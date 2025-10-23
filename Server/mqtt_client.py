"""
MQTT client module for the FloraSeven server.

This module provides a client for communicating with the hardware nodes
via MQTT. It handles connecting to the broker, subscribing to topics,
processing incoming messages, and publishing commands.

Features:
- Automatic reconnection with exponential backoff
- Message queuing during disconnections
- TLS/SSL support for secure connections
- Authentication support
- Detailed logging and error handling
- Last Will and Testament for proper status tracking
"""
import json
import logging
import threading
import time
import queue
import ssl
from datetime import datetime

import paho.mqtt.client as mqtt

import config
import database
import connection_status

# Set up logging
logger = logging.getLogger(__name__)

class MQTTClient:
    """MQTT client for the FloraSeven server."""

    def __init__(self):
        """Initialize the MQTT client."""
        # Create MQTT client with clean session
        self.client = mqtt.Client(client_id=config.MQTT_CLIENT_ID, clean_session=True)

        # Set up callbacks
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        self.client.on_publish = self.on_publish
        self.client.on_subscribe = self.on_subscribe
        self.client.on_log = self.on_log

        # Connection state
        self.connected = False
        self.reconnect_delay = config.MQTT_RECONNECT_DELAY_MIN
        self.max_reconnect_delay = config.MQTT_RECONNECT_DELAY_MAX

        # Message queue for storing messages during disconnection
        self.message_queue = queue.Queue()
        self.queue_lock = threading.Lock()
        self.queue_processor_running = False

        # Reconnection thread
        self.reconnect_thread = None
        self.reconnect_thread_running = False

        # Statistics
        self.stats = {
            'messages_received': 0,
            'messages_sent': 0,
            'connection_attempts': 0,
            'successful_connections': 0,
            'disconnections': 0,
            'last_connected': None,
            'last_disconnected': None,
            'uptime': 0,
            'start_time': time.time()
        }

        # Enable logging
        self.client.enable_logger(logger)

        # Set up TLS if enabled
        if config.MQTT_USE_TLS:
            self.client.tls_set(
                ca_certs=None,  # Use default CA certs
                certfile=None,
                keyfile=None,
                cert_reqs=ssl.CERT_REQUIRED,
                tls_version=ssl.PROTOCOL_TLS,
                ciphers=None
            )

        # Set up authentication if provided
        if config.MQTT_USERNAME and config.MQTT_PASSWORD:
            self.client.username_pw_set(config.MQTT_USERNAME, config.MQTT_PASSWORD)

    def start(self):
        """
        Start the MQTT client in a separate thread.

        Returns:
            bool: True if the client was started successfully, False otherwise
        """
        try:
            # Connect to the broker
            logger.info(f"Connecting to MQTT broker at {config.MQTT_BROKER}:{config.MQTT_PORT}")

            # Update statistics
            self.stats['connection_attempts'] += 1

            # Set up will message (last will and testament)
            self.client.will_set(
                config.MQTT_TOPIC_SERVER_STATUS,
                payload="offline",
                qos=config.MQTT_QOS,
                retain=True
            )

            # Start the MQTT loop in a separate thread
            self.client.loop_start()

            # Connect with clean session
            self.client.connect_async(
                config.MQTT_BROKER,
                config.MQTT_PORT,
                config.MQTT_KEEPALIVE
            )

            # Wait for connection to be established
            timeout = 15  # seconds
            start_time = time.time()
            while not self.connected and time.time() - start_time < timeout:
                time.sleep(0.1)

            if not self.connected:
                logger.error("Failed to connect to MQTT broker within timeout")
                # Don't stop the loop - it will handle reconnection

                # Start reconnection thread
                self._start_reconnection_thread()

                # Start message queue processor
                self._start_queue_processor()

                return False

            # Publish online status
            self.client.publish(
                config.MQTT_TOPIC_SERVER_STATUS,
                payload="online",
                qos=config.MQTT_QOS,
                retain=True
            )

            # Start message queue processor
            self._start_queue_processor()

            # Register with connection status module
            connection_status.record_component_activity('mqtt_client')

            logger.info("MQTT client started successfully")
            return True

        except Exception as e:
            logger.error(f"Error starting MQTT client: {e}", exc_info=True)

            # Start reconnection thread
            self._start_reconnection_thread()

            # Start message queue processor
            self._start_queue_processor()

            return False

    def _start_reconnection_thread(self):
        """Start a thread to handle reconnection attempts."""
        if self.reconnect_thread_running:
            return

        self.reconnect_thread_running = True
        self.reconnect_thread = threading.Thread(target=self._reconnection_loop)
        self.reconnect_thread.daemon = True
        self.reconnect_thread.start()
        logger.info("MQTT reconnection thread started")

    def _reconnection_loop(self):
        """Loop to handle reconnection attempts with exponential backoff."""
        while self.reconnect_thread_running:
            if not self.connected:
                try:
                    logger.info(f"Attempting to reconnect to MQTT broker (delay: {self.reconnect_delay}s)")
                    self.stats['connection_attempts'] += 1

                    # Try to reconnect
                    self.client.reconnect()

                    # If we get here, reconnection was successful
                    logger.info("Reconnected to MQTT broker")

                    # Reset reconnect delay
                    self.reconnect_delay = config.MQTT_RECONNECT_DELAY_MIN

                except Exception as e:
                    logger.error(f"Failed to reconnect to MQTT broker: {e}")

                    # Implement exponential backoff
                    time.sleep(self.reconnect_delay)
                    self.reconnect_delay = min(self.reconnect_delay * 2, self.max_reconnect_delay)

            # Sleep before next check
            time.sleep(5)

    def _start_queue_processor(self):
        """Start a thread to process the message queue."""
        if self.queue_processor_running:
            return

        self.queue_processor_running = True
        queue_thread = threading.Thread(target=self._process_message_queue)
        queue_thread.daemon = True
        queue_thread.start()
        logger.info("MQTT message queue processor started")

    def _process_message_queue(self):
        """Process messages in the queue when connected."""
        while self.queue_processor_running:
            if self.connected and not self.message_queue.empty():
                try:
                    with self.queue_lock:
                        if not self.message_queue.empty():
                            # Get the next message from the queue
                            message = self.message_queue.get()
                            topic = message['topic']
                            payload = message['payload']
                            qos = message.get('qos', config.MQTT_QOS)
                            retain = message.get('retain', False)

                            # Publish the message
                            result = self.client.publish(topic, payload, qos, retain)

                            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                                logger.debug(f"Published queued message to {topic}")
                                self.stats['messages_sent'] += 1
                            else:
                                logger.warning(f"Failed to publish queued message to {topic}: {result.rc}")
                                # Put the message back in the queue
                                self.message_queue.put(message)

                            # Mark the task as done
                            self.message_queue.task_done()
                except Exception as e:
                    logger.error(f"Error processing message queue: {e}")

            # Sleep to avoid busy waiting
            time.sleep(0.1)

    def stop(self):
        """
        Stop the MQTT client.

        Returns:
            bool: True if the client was stopped successfully, False otherwise
        """
        try:
            # Publish offline status before disconnecting
            try:
                self.client.publish(
                    config.MQTT_TOPIC_SERVER_STATUS,
                    payload="offline",
                    qos=config.MQTT_QOS,
                    retain=True
                )
            except Exception as e:
                logger.warning(f"Failed to publish offline status: {e}")

            # Stop reconnection thread
            self.reconnect_thread_running = False
            if self.reconnect_thread:
                self.reconnect_thread.join(timeout=1.0)
                self.reconnect_thread = None

            # Stop queue processor
            self.queue_processor_running = False

            # Disconnect and stop the loop
            self.client.disconnect()
            self.client.loop_stop()

            # Update state
            self.connected = False
            self.stats['last_disconnected'] = datetime.now().isoformat()

            logger.info("MQTT client stopped")
            return True

        except Exception as e:
            logger.error(f"Error stopping MQTT client: {e}", exc_info=True)
            return False

    def on_connect(self, client, userdata, flags, rc):
        """
        Callback for when the client connects to the broker.

        Args:
            client: MQTT client instance
            userdata: User data
            flags: Connection flags
            rc: Connection result code
        """
        if rc == 0:
            self.connected = True

            # Update statistics
            self.stats['successful_connections'] += 1
            self.stats['last_connected'] = datetime.now().isoformat()

            logger.info("Connected to MQTT broker")

            # Subscribe to topics
            self.subscribe_to_topics()

            # Reset reconnect delay
            self.reconnect_delay = config.MQTT_RECONNECT_DELAY_MIN

            # Publish online status
            self.client.publish(
                config.MQTT_TOPIC_SERVER_STATUS,
                payload="online",
                qos=config.MQTT_QOS,
                retain=True
            )

            # Register with connection status module
            connection_status.record_component_activity('mqtt_client')
        else:
            self.connected = False
            error_message = "Unknown error"
            if rc == 1:
                error_message = "Connection refused - incorrect protocol version"
            elif rc == 2:
                error_message = "Connection refused - invalid client identifier"
            elif rc == 3:
                error_message = "Connection refused - server unavailable"
            elif rc == 4:
                error_message = "Connection refused - bad username or password"
            elif rc == 5:
                error_message = "Connection refused - not authorized"
            logger.error(f"Failed to connect to MQTT broker: {error_message} (code {rc})")

    def on_disconnect(self, client, userdata, rc):
        """
        Callback for when the client disconnects from the broker.

        Args:
            client: MQTT client instance
            userdata: User data
            rc: Disconnection result code
        """
        # Update state
        self.connected = False
        self.stats['disconnections'] += 1
        self.stats['last_disconnected'] = datetime.now().isoformat()

        if rc != 0:
            logger.warning(f"Unexpected disconnection from MQTT broker with result code {rc}")

            # The client will automatically attempt to reconnect
            # We don't need to call reconnect() here as the loop_start() will handle it
        else:
            logger.info("Disconnected from MQTT broker")

    def on_publish(self, client, userdata, mid):
        """
        Callback for when a message is published.

        Args:
            client: MQTT client instance
            userdata: User data
            mid: Message ID
        """
        # Update statistics
        self.stats['messages_sent'] += 1

    def on_subscribe(self, client, userdata, mid, granted_qos):
        """
        Callback for when the client subscribes to a topic.

        Args:
            client: MQTT client instance
            userdata: User data
            mid: Message ID
            granted_qos: Granted QoS level
        """
        logger.debug(f"Subscribed to topic with message ID {mid}, QoS {granted_qos}")

    def on_log(self, client, userdata, level, buf):
        """
        Callback for logging.

        Args:
            client: MQTT client instance
            userdata: User data
            level: Log level
            buf: Log message
        """
        # Map Paho log levels to Python logging levels
        if level == mqtt.MQTT_LOG_INFO:
            logger.debug(f"MQTT Log: {buf}")
        elif level == mqtt.MQTT_LOG_NOTICE:
            logger.info(f"MQTT Log: {buf}")
        elif level == mqtt.MQTT_LOG_WARNING:
            logger.warning(f"MQTT Log: {buf}")
        elif level == mqtt.MQTT_LOG_ERR:
            logger.error(f"MQTT Log: {buf}")
        elif level == mqtt.MQTT_LOG_DEBUG:
            logger.debug(f"MQTT Log: {buf}")

    def on_message(self, client, userdata, msg):
        """
        Callback for when a message is received from the broker.

        Args:
            client: MQTT client instance
            userdata: User data
            msg: MQTT message
        """
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')

            # Update statistics
            self.stats['messages_received'] += 1

            # Register activity with connection status module
            connection_status.record_component_activity('mqtt_client')

            logger.debug(f"Received message on topic {topic}: {payload}")

            # Process message based on topic pattern matching
            if topic.startswith('floraSeven/plant/') and topic.endswith('/data'):
                self._handle_plant_data(payload, topic)
            elif topic.startswith('floraSeven/hub/') and topic.endswith('/status'):
                self._handle_hub_status(payload, topic)
            elif topic.startswith('floraSeven/hub/') and topic.endswith('/cam/image_status'):
                self._handle_image_status(payload, topic)
            else:
                logger.warning(f"Received message on unknown topic: {topic}")

        except UnicodeDecodeError:
            logger.error(f"Failed to decode message payload on topic {msg.topic}")
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in message payload on topic {msg.topic}")
        except Exception as e:
            logger.error(f"Error processing MQTT message: {e}", exc_info=True)

    def subscribe_to_topics(self):
        """Subscribe to MQTT topics."""
        try:
            # Create a list of topics to subscribe to with their QoS levels
            topics = [
                (config.MQTT_TOPIC_PLANT_DATA, config.MQTT_QOS),
                (config.MQTT_TOPIC_HUB_STATUS, config.MQTT_QOS),
                (config.MQTT_TOPIC_HUB_IMAGE_STATUS, config.MQTT_QOS)
            ]

            # Subscribe to all topics at once
            result, _ = self.client.subscribe(topics)

            if result == mqtt.MQTT_ERR_SUCCESS:
                for topic, qos in topics:
                    logger.info(f"Subscribed to {topic} with QoS {qos}")
            else:
                logger.error(f"Failed to subscribe to topics: {result}")

        except Exception as e:
            logger.error(f"Error subscribing to MQTT topics: {e}", exc_info=True)

    def _handle_plant_data(self, payload, topic):
        """
        Handle Plant Node data message.

        Args:
            payload (str): JSON payload
            topic (str): MQTT topic
        """
        try:
            # Extract node ID from topic
            # Format: floraSeven/plant/{nodeId}/data
            parts = topic.split('/')
            if len(parts) >= 3:
                node_id_from_topic = parts[2]
            else:
                node_id_from_topic = "unknown"

            # Parse JSON payload
            data = json.loads(payload)

            # Validate required fields
            required_fields = ['timestamp', 'nodeId', 'temp_soil_c', 'moisture_raw', 'light_lux']
            if not all(field in data for field in required_fields):
                logger.warning(f"Plant data missing required fields: {payload}")
                return

            # Get data from payload
            timestamp = data['timestamp']
            node_id = data.get('nodeId', node_id_from_topic)

            # Convert timestamp to ISO format if it's a Unix timestamp
            if isinstance(timestamp, (int, float)):
                timestamp = datetime.fromtimestamp(timestamp).isoformat()

            # Log each sensor reading to the database using the with_connection decorator
            database.log_sensor_reading(timestamp, node_id, 'temp_soil', data['temp_soil_c'])
            database.log_sensor_reading(timestamp, node_id, 'moisture', data['moisture_raw'])
            database.log_sensor_reading(timestamp, node_id, 'light_lux', data['light_lux'])

            # Log EC data if available
            if 'ec_voltage_rms' in data:
                database.log_sensor_reading(timestamp, node_id, 'ec_raw', data['ec_voltage_rms'])

            # Log EC compensated data if available
            if 'ec_comp_mS_cm' in data:
                database.log_sensor_reading(timestamp, node_id, 'ec_compensated', data['ec_comp_mS_cm'])

            # Update connection status for this node
            connection_status.record_component_activity(f'plant_node_{node_id}')

            logger.info(f"Processed plant data from {node_id}")

        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in plant data payload: {payload}")
        except Exception as e:
            logger.error(f"Error handling plant data: {e}", exc_info=True)

    def _handle_hub_status(self, payload, topic):
        """
        Handle Hub Node status message.

        Args:
            payload (str): JSON payload
            topic (str): MQTT topic
        """
        try:
            # Extract node ID from topic
            # Format: floraSeven/hub/{nodeId}/status
            parts = topic.split('/')
            if len(parts) >= 3:
                node_id_from_topic = parts[2]
            else:
                node_id_from_topic = "unknown"

            # Parse JSON payload
            data = json.loads(payload)

            # Check if this is an ACK message
            if 'status' in data and data['status'] == 'ACK':
                if 'command_received' in data:
                    logger.info(f"Hub {node_id_from_topic} acknowledged command: {data['command_received']}")

                # Update connection status for this node
                connection_status.record_component_activity(f'hub_node_{node_id_from_topic}')
                return

            # Check if this is an INFO or ERROR message
            if 'status' in data and data['status'] in ['INFO', 'ERROR']:
                if 'message' in data:
                    log_level = logging.INFO if data['status'] == 'INFO' else logging.ERROR
                    logger.log(log_level, f"Hub {node_id_from_topic}: {data['message']}")

                # Update connection status for this node
                connection_status.record_component_activity(f'hub_node_{node_id_from_topic}')
                return

            # Validate required fields for sensor data
            required_fields = ['timestamp', 'nodeId', 'ph_water', 'uv_ambient', 'pump_active']
            if not all(field in data for field in required_fields):
                logger.warning(f"Hub status missing required fields: {payload}")
                return

            # Get data from payload
            timestamp = data['timestamp']
            node_id = data.get('nodeId', node_id_from_topic)

            # Convert timestamp to ISO format if it's a Unix timestamp
            if isinstance(timestamp, (int, float)):
                timestamp = datetime.fromtimestamp(timestamp).isoformat()

            # Log each sensor reading to the database using the with_connection decorator
            database.log_sensor_reading(timestamp, node_id, 'ph_water', data['ph_water'])
            database.log_sensor_reading(timestamp, node_id, 'uv_ambient', data['uv_ambient'])
            database.log_sensor_reading(timestamp, node_id, 'pump_state', 1 if data['pump_active'] else 0)

            # Log ambient temperature and humidity if available
            if 'temp_ambient' in data:
                database.log_sensor_reading(timestamp, node_id, 'temp_ambient', data['temp_ambient'])
            if 'humidity' in data:
                database.log_sensor_reading(timestamp, node_id, 'humidity', data['humidity'])

            # Update connection status for this node
            connection_status.record_component_activity(f'hub_node_{node_id}')

            logger.info(f"Processed hub status from {node_id}")

        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in hub status payload: {payload}")
        except Exception as e:
            logger.error(f"Error handling hub status: {e}", exc_info=True)

    def _handle_image_status(self, payload, topic):
        """
        Handle Hub Node image status message.

        Args:
            payload (str): JSON payload
            topic (str): MQTT topic
        """
        try:
            # Extract node ID from topic
            # Format: floraSeven/hub/{nodeId}/cam/image_status
            parts = topic.split('/')
            if len(parts) >= 3:
                node_id_from_topic = parts[2]
            else:
                node_id_from_topic = "unknown"

            # Parse JSON payload
            data = json.loads(payload)

            # Get node ID from payload or topic
            node_id = data.get('nodeId', node_id_from_topic)

            # Update connection status for camera
            connection_status.record_component_activity(f'camera_{node_id}')

            # Check if this is a status update
            if 'status' in data:
                status = data['status']

                if status == 'uploading':
                    logger.info(f"Camera {node_id} is uploading an image (size: {data.get('image_size', 'unknown')} bytes)")
                    return

                elif status == 'uploaded':
                    logger.info(f"Camera {node_id} successfully uploaded an image")
                    return

                elif status == 'failed':
                    error = data.get('error', 'Unknown error')
                    logger.warning(f"Camera {node_id} failed to upload an image: {error}")
                    return

            # Validate required fields
            required_fields = ['timestamp', 'success']
            if not all(field in data for field in required_fields):
                logger.warning(f"Image status missing required fields: {payload}")
                return

            if data['success']:
                if 'filename' not in data:
                    logger.warning(f"Image status missing filename: {payload}")
                    return

                logger.info(f"Image uploaded successfully: {data['filename']}")
            else:
                error = data.get('error', 'Unknown error')
                logger.warning(f"Image upload failed: {error}")

        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in image status payload: {payload}")
        except Exception as e:
            logger.error(f"Error handling image status: {e}", exc_info=True)

    def send_water_command(self, state, duration_sec=None, node_id="hub1"):
        """
        Send a command to control the water pump.

        Args:
            state (str): "ON" or "OFF"
            duration_sec (int, optional): Duration in seconds (only required when state is "ON")
            node_id (str, optional): ID of the hub node to send the command to

        Returns:
            bool: True if the command was sent successfully, False otherwise
        """
        try:
            # Validate state
            if state not in ["ON", "OFF"]:
                logger.error(f"Invalid water command state: {state}")
                return False

            # Check connection status
            if not self.connected:
                logger.warning("MQTT client not connected. Queuing water command for later delivery.")

                # Queue the command for later
                with self.queue_lock:
                    payload = {"state": state}

                    if state == "ON":
                        if duration_sec is None:
                            duration_sec = config.DEFAULT_PUMP_DURATION

                        # Limit duration to maximum allowed
                        if duration_sec > config.MAX_PUMP_DURATION:
                            duration_sec = config.MAX_PUMP_DURATION
                            logger.warning(f"Pump duration limited to maximum of {config.MAX_PUMP_DURATION} seconds")

                        payload["duration_sec"] = duration_sec

                    # Add timestamp and message ID
                    payload["timestamp"] = datetime.now().isoformat()
                    payload["message_id"] = f"pump_{int(time.time())}"

                    # Queue the message
                    topic = config.MQTT_TOPIC_COMMAND_PUMP.replace('+', node_id)
                    self.message_queue.put({
                        'topic': topic,
                        'payload': json.dumps(payload),
                        'qos': config.MQTT_QOS,
                        'retain': False
                    })

                    logger.info(f"Queued water pump command for later delivery: {payload}")

                return False

            # Prepare command payload
            payload = {"state": state}

            if state == "ON":
                if duration_sec is None:
                    duration_sec = config.DEFAULT_PUMP_DURATION

                # Limit duration to maximum allowed
                if duration_sec > config.MAX_PUMP_DURATION:
                    duration_sec = config.MAX_PUMP_DURATION
                    logger.warning(f"Pump duration limited to maximum of {config.MAX_PUMP_DURATION} seconds")

                payload["duration_sec"] = duration_sec

            # Add timestamp and message ID
            payload["timestamp"] = datetime.now().isoformat()
            payload["message_id"] = f"pump_{int(time.time())}"

            # Replace wildcard with specific node ID
            topic = config.MQTT_TOPIC_COMMAND_PUMP.replace('+', node_id)

            # Publish the command
            result = self.client.publish(
                topic,
                json.dumps(payload),
                qos=config.MQTT_QOS
            )

            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"Water command sent to {node_id}: {payload}")
                self.stats['messages_sent'] += 1
                return True
            else:
                logger.error(f"Failed to send water command: {result}")
                return False

        except Exception as e:
            logger.error(f"Error sending water command: {e}", exc_info=True)
            return False

    def send_capture_image_command(self, resolution=None, flash=None, node_id="hub1"):
        """
        Send a command to capture an image.

        Args:
            resolution (str, optional): Image resolution (e.g., "high", "medium", "low")
            flash (bool, optional): Whether to use flash
            node_id (str, optional): ID of the hub node to send the command to

        Returns:
            bool: True if the command was sent successfully, False otherwise
        """
        try:
            # Check connection status
            if not self.connected:
                logger.warning("MQTT client not connected. Queuing capture image command for later delivery.")

                # Queue the command for later
                with self.queue_lock:
                    payload = {}

                    if resolution is not None:
                        payload["resolution"] = resolution

                    if flash is not None:
                        payload["flash"] = flash

                    # Add timestamp and message ID
                    payload["timestamp"] = datetime.now().isoformat()
                    payload["message_id"] = f"capture_{int(time.time())}"

                    # Queue the message
                    topic = config.MQTT_TOPIC_COMMAND_CAPTURE_IMAGE.replace('+', node_id)
                    self.message_queue.put({
                        'topic': topic,
                        'payload': json.dumps(payload),
                        'qos': config.MQTT_QOS,
                        'retain': False
                    })

                    logger.info(f"Queued capture image command for later delivery")

                return False

            # Prepare command payload
            payload = {}

            if resolution is not None:
                payload["resolution"] = resolution

            if flash is not None:
                payload["flash"] = flash

            # Add timestamp and message ID
            payload["timestamp"] = datetime.now().isoformat()
            payload["message_id"] = f"capture_{int(time.time())}"

            # Replace wildcard with specific node ID
            topic = config.MQTT_TOPIC_COMMAND_CAPTURE_IMAGE.replace('+', node_id)

            # Publish the command
            result = self.client.publish(
                topic,
                json.dumps(payload),
                qos=config.MQTT_QOS
            )

            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"Capture image command sent to {node_id}: {payload}")
                self.stats['messages_sent'] += 1
                return True
            else:
                logger.error(f"Failed to send capture image command: {result}")
                return False

        except Exception as e:
            logger.error(f"Error sending capture image command: {e}", exc_info=True)
            return False

    def send_read_now_command(self, node_id="node1"):
        """
        Send a command to force a sensor reading.

        Args:
            node_id (str, optional): ID of the plant node to send the command to

        Returns:
            bool: True if the command was sent successfully, False otherwise
        """
        try:
            # Check connection status
            if not self.connected:
                logger.warning("MQTT client not connected. Queuing read now command for later delivery.")

                # Queue the command for later
                with self.queue_lock:
                    payload = {
                        "timestamp": datetime.now().isoformat(),
                        "message_id": f"read_{int(time.time())}"
                    }

                    # Queue the message
                    topic = config.MQTT_TOPIC_COMMAND_READ_NOW.replace('+', node_id)
                    self.message_queue.put({
                        'topic': topic,
                        'payload': json.dumps(payload),
                        'qos': config.MQTT_QOS,
                        'retain': False
                    })

                    logger.info(f"Queued read now command for later delivery")

                return False

            # Prepare command payload with timestamp and message ID
            payload = {
                "timestamp": datetime.now().isoformat(),
                "message_id": f"read_{int(time.time())}"
            }

            # Replace wildcard with specific node ID
            topic = config.MQTT_TOPIC_COMMAND_READ_NOW.replace('+', node_id)

            # Publish the command
            result = self.client.publish(
                topic,
                json.dumps(payload),
                qos=config.MQTT_QOS
            )

            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"Read now command sent to {node_id}")
                self.stats['messages_sent'] += 1
                return True
            else:
                logger.error(f"Failed to send read now command: {result}")
                return False

        except Exception as e:
            logger.error(f"Error sending read now command: {e}", exc_info=True)
            return False

    def get_status(self):
        """
        Get the current status of the MQTT client.

        Returns:
            dict: Status information
        """
        # Calculate uptime
        if self.stats['last_connected']:
            try:
                # If last_connected is an ISO string, parse it
                if isinstance(self.stats['last_connected'], str):
                    last_connected = datetime.fromisoformat(self.stats['last_connected'].replace('Z', '+00:00'))
                    self.stats['uptime'] = (datetime.now() - last_connected).total_seconds()
                else:
                    self.stats['uptime'] = time.time() - self.stats['start_time']
            except Exception:
                self.stats['uptime'] = 0

        # Return status
        return {
            'connected': self.connected,
            'broker': f"{config.MQTT_BROKER}:{config.MQTT_PORT}",
            'client_id': config.MQTT_CLIENT_ID,
            'messages_received': self.stats['messages_received'],
            'messages_sent': self.stats['messages_sent'],
            'connection_attempts': self.stats['connection_attempts'],
            'successful_connections': self.stats['successful_connections'],
            'disconnections': self.stats['disconnections'],
            'last_connected': self.stats['last_connected'],
            'last_disconnected': self.stats['last_disconnected'],
            'uptime_seconds': self.stats['uptime'],
            'queued_messages': self.message_queue.qsize(),
            'reconnect_delay': self.reconnect_delay
        }

# Create a singleton instance
mqtt_client = MQTTClient()
