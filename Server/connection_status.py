"""
Connection status monitoring module for the FloraSeven server.

This module tracks the connection status of all system components
and provides functions to check if components are online, offline,
or in a warning/error state.

Features:
- Real-time component status tracking
- Automatic notification of status changes
- Persistent status storage
- Email alerts for critical issues
- Integration with the database for historical tracking
- Support for multiple component types (hardware, sensors, services)
"""
import logging
import threading
import time
import json
import os
import uuid
from datetime import datetime, timedelta

import config
import database

# Set up logging
logger = logging.getLogger(__name__)

# Connection states
CONNECTION_STATE_ONLINE = "online"
CONNECTION_STATE_WARNING = "warning"
CONNECTION_STATE_ERROR = "error"
CONNECTION_STATE_CRITICAL = "critical"
CONNECTION_STATE_UNKNOWN = "unknown"

# Dictionary to store the last activity timestamp for each component
_component_last_activity = {}
_component_status = {}
_lock = threading.Lock()

# Dictionary to store notification timestamps to prevent spam
_last_notification = {}

# Component metadata for better display
_component_metadata = {
    "server": {
        "name": "FloraSeven Server",
        "type": "server",
        "description": "Main server application"
    },
    "mqtt_client": {
        "name": "MQTT Client",
        "type": "service",
        "description": "MQTT messaging service"
    },
    "plant_node_node1": {
        "name": "Plant Node 1",
        "type": "hardware",
        "description": "ESP32 WROOM with sensors"
    },
    "hub_node_hub1": {
        "name": "Hub Node 1",
        "type": "hardware",
        "description": "ESP32-CAM with R4 Minima"
    },
    "camera_hub1": {
        "name": "Camera (Hub 1)",
        "type": "sensor",
        "description": "ESP32-CAM camera module"
    }
}

# Sensor metadata
_sensor_metadata = {
    "moisture": {
        "name": "Soil Moisture",
        "unit": "%",
        "description": "Capacitive Soil Moisture Sensor V2.0"
    },
    "temp_soil": {
        "name": "Soil Temperature",
        "unit": "°C",
        "description": "DS18B20 Temperature Sensor"
    },
    "light_lux": {
        "name": "Light Intensity",
        "unit": "lux",
        "description": "BH1750 Light Sensor"
    },
    "ec_raw": {
        "name": "Electrical Conductivity",
        "unit": "µS/cm",
        "description": "DIY EC Probe with LM358"
    },
    "ph_water": {
        "name": "Water pH",
        "unit": "pH",
        "description": "Crowtail pH Sensor"
    },
    "uv_ambient": {
        "name": "UV Index",
        "unit": "",
        "description": "ML8511 UV Sensor"
    },
    "temp_ambient": {
        "name": "Ambient Temperature",
        "unit": "°C",
        "description": "DHT22 Temperature Sensor"
    },
    "humidity": {
        "name": "Ambient Humidity",
        "unit": "%",
        "description": "DHT22 Humidity Sensor"
    }
}

def record_component_activity(component_id):
    """
    Record activity for a component.

    Args:
        component_id (str): Unique identifier for the component
    """
    with _lock:
        now = datetime.now()
        _component_last_activity[component_id] = now

        # Update status
        _component_status[component_id] = {
            'status': CONNECTION_STATE_ONLINE,
            'last_activity': now.isoformat(),
            'message': 'Component is online'
        }

        # Add metadata if available
        if component_id in _component_metadata:
            _component_status[component_id].update({
                'name': _component_metadata[component_id]['name'],
                'type': _component_metadata[component_id]['type'],
                'description': _component_metadata[component_id]['description']
            })

        logger.debug(f"Recorded activity for component {component_id}")

def get_component_status(component_id):
    """
    Get the status of a component.

    Args:
        component_id (str): Unique identifier for the component

    Returns:
        dict: Status information for the component
    """
    with _lock:
        if component_id not in _component_last_activity:
            return {
                'status': CONNECTION_STATE_UNKNOWN,
                'last_activity': None,
                'message': 'No activity recorded for this component'
            }

        last_activity = _component_last_activity[component_id]
        now = datetime.now()
        time_since_last_activity = (now - last_activity).total_seconds()

        # Determine status based on time since last activity
        if time_since_last_activity < config.TIMEOUT_WARNING:
            status = CONNECTION_STATE_ONLINE
            message = 'Component is online'
        elif time_since_last_activity < config.TIMEOUT_ERROR:
            status = CONNECTION_STATE_WARNING
            message = f'Component has not reported in {int(time_since_last_activity)} seconds'
        elif time_since_last_activity < config.TIMEOUT_CRITICAL:
            status = CONNECTION_STATE_ERROR
            message = f'Component may be offline (last activity: {int(time_since_last_activity)} seconds ago)'
        else:
            status = CONNECTION_STATE_CRITICAL
            message = f'Component is offline (last activity: {int(time_since_last_activity)} seconds ago)'

        result = {
            'status': status,
            'last_activity': last_activity.isoformat(),
            'time_since_last_activity': time_since_last_activity,
            'message': message
        }

        # Add metadata if available
        if component_id in _component_metadata:
            result.update({
                'name': _component_metadata[component_id]['name'],
                'type': _component_metadata[component_id]['type'],
                'description': _component_metadata[component_id]['description']
            })

        return result

def get_all_component_status():
    """
    Get the status of all components.

    Returns:
        dict: Status information for all components
    """
    with _lock:
        result = {}
        for component_id in _component_last_activity:
            result[component_id] = get_component_status(component_id)
        return result

def check_components():
    """
    Check the status of all components and log warnings/errors.
    Also records status changes in the database for historical tracking.
    """
    with _lock:
        now = datetime.now()
        status_changes = []

        for component_id, last_activity in _component_last_activity.items():
            time_since_last_activity = (now - last_activity).total_seconds()

            # Get component metadata
            component_name = component_id
            component_type = "unknown"
            if component_id in _component_metadata:
                component_name = _component_metadata[component_id]['name']
                component_type = _component_metadata[component_id]['type']

            # Skip if we've recently notified about this component
            if component_id in _last_notification:
                time_since_notification = (now - _last_notification[component_id]).total_seconds()
                if time_since_notification < config.CONNECTION_NOTIFICATION_COOLDOWN:
                    continue

            # Get previous state
            previous_state = CONNECTION_STATE_UNKNOWN
            if component_id in _component_status:
                previous_state = _component_status[component_id].get('status', CONNECTION_STATE_UNKNOWN)

            # Check for warning/error conditions
            new_state = None
            message = None

            if time_since_last_activity >= config.TIMEOUT_CRITICAL:
                new_state = CONNECTION_STATE_CRITICAL
                message = f'Component is offline (last activity: {int(time_since_last_activity)} seconds ago)'
                logger.error(f"Component {component_id} is offline (last activity: {int(time_since_last_activity)} seconds ago)")

            elif time_since_last_activity >= config.TIMEOUT_ERROR:
                new_state = CONNECTION_STATE_ERROR
                message = f'Component may be offline (last activity: {int(time_since_last_activity)} seconds ago)'
                logger.error(f"Component {component_id} may be offline (last activity: {int(time_since_last_activity)} seconds ago)")

            elif time_since_last_activity >= config.TIMEOUT_WARNING:
                new_state = CONNECTION_STATE_WARNING
                message = f'Component has not reported in {int(time_since_last_activity)} seconds'
                logger.warning(f"Component {component_id} has not reported in {int(time_since_last_activity)} seconds")

            # If state changed, update status and record the change
            if new_state and new_state != previous_state:
                _last_notification[component_id] = now
                _component_status[component_id] = {
                    'status': new_state,
                    'last_activity': last_activity.isoformat(),
                    'message': message
                }

                # Add metadata if available
                if component_id in _component_metadata:
                    _component_status[component_id].update({
                        'name': _component_metadata[component_id]['name'],
                        'type': _component_metadata[component_id]['type'],
                        'description': _component_metadata[component_id]['description']
                    })

                # Record status change for database logging
                status_changes.append({
                    'component_id': component_id,
                    'component_name': component_name,
                    'component_type': component_type,
                    'previous_state': previous_state,
                    'new_state': new_state,
                    'message': message,
                    'timestamp': now.isoformat()
                })

                # Send email notification if enabled
                if new_state in [CONNECTION_STATE_ERROR, CONNECTION_STATE_CRITICAL] and \
                   hasattr(config, 'ENABLE_EMAIL_ALERTS') and config.ENABLE_EMAIL_ALERTS:
                    _send_email_alert(component_id, new_state, time_since_last_activity)

        # Log status changes to database
        if status_changes:
            try:
                # Get database connection
                conn = database.get_db_connection()

                # Log each status change
                for change in status_changes:
                    try:
                        cursor = conn.cursor()
                        cursor.execute('''
                        INSERT INTO ConnectionEvents
                        (timestamp, component_id, component_name, component_type, previous_state, new_state, message)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            change['timestamp'],
                            change['component_id'],
                            change['component_name'],
                            change['component_type'],
                            change['previous_state'],
                            change['new_state'],
                            change['message']
                        ))
                        conn.commit()

                        # Create notification for critical and error states
                        if change['new_state'] in [CONNECTION_STATE_ERROR, CONNECTION_STATE_CRITICAL]:
                            severity = "critical" if change['new_state'] == CONNECTION_STATE_CRITICAL else "error"
                            cursor.execute('''
                            INSERT INTO Notifications
                            (timestamp, component_id, severity, message, read, action_taken)
                            VALUES (?, ?, ?, ?, 0, 0)
                            ''', (
                                change['timestamp'],
                                change['component_id'],
                                severity,
                                f"{change['component_name']} is {change['new_state']}: {change['message']}"
                            ))
                            conn.commit()

                    except Exception as e:
                        logger.error(f"Error logging connection event: {e}", exc_info=True)

            except Exception as e:
                logger.error(f"Error getting database connection: {e}", exc_info=True)

def _send_email_alert(component_id, severity, time_since_last_activity):
    """
    Send an email alert about a component status change.

    Args:
        component_id (str): Unique identifier for the component
        severity (str): Severity level ('warning', 'error', 'critical')
        time_since_last_activity (float): Time since last activity in seconds
    """
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        # Create message
        msg = MIMEMultipart()
        msg['From'] = config.ALERT_FROM
        msg['To'] = ', '.join(config.ALERT_RECIPIENTS)
        msg['Subject'] = f"FloraSeven {severity.upper()} Alert: Component {component_id} Status Change"

        # Create message body
        body = f"""
        <html>
        <body>
            <h2>FloraSeven Component Status Alert</h2>
            <p>This is an automated alert from your FloraSeven plant monitoring system.</p>
            <p><strong>Component:</strong> {component_id}</p>
            <p><strong>Status:</strong> {severity.upper()}</p>
            <p><strong>Last Activity:</strong> {int(time_since_last_activity)} seconds ago</p>
            <p><strong>Timestamp:</strong> {datetime.now().isoformat()}</p>
            <hr>
            <p>Please check your FloraSeven system for more details.</p>
        </body>
        </html>
        """

        msg.attach(MIMEText(body, 'html'))

        # Connect to SMTP server and send message
        with smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT) as server:
            server.starttls()
            server.login(config.SMTP_USERNAME, config.SMTP_PASSWORD)
            server.send_message(msg)

        logger.info(f"Sent email alert for component {component_id}")

    except Exception as e:
        logger.error(f"Failed to send email alert: {e}", exc_info=True)

def start_monitoring():
    """
    Start the connection monitoring thread.
    """
    def monitor_loop():
        while True:
            try:
                check_components()
            except Exception as e:
                logger.error(f"Error in connection monitoring: {e}", exc_info=True)

            # Sleep until next check
            time.sleep(config.CONNECTION_CHECK_INTERVAL)

    # Start the monitoring thread
    monitor_thread = threading.Thread(target=monitor_loop)
    monitor_thread.daemon = True
    monitor_thread.start()
    logger.info("Connection monitoring started")

    return monitor_thread

def save_status_to_file():
    """
    Save the current status to a JSON file and database.
    """
    try:
        status_file = os.path.join(config.BASE_DIR, 'data', 'component_status.json')

        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(status_file), exist_ok=True)

        # Get current status
        status = get_all_component_status()

        # Add timestamp and metadata
        timestamp = datetime.now().isoformat()
        status['_meta'] = {
            'timestamp': timestamp,
            'server_uptime': time.time() - _server_start_time,
            'status_id': str(uuid.uuid4())
        }

        # Write to file
        with open(status_file, 'w') as f:
            json.dump(status, f, indent=2)

        # Save to database
        try:
            # Get database connection
            conn = database.get_db_connection()
            cursor = conn.cursor()

            # Convert status to JSON string
            status_json = json.dumps(status)

            # Insert into database
            cursor.execute('''
            INSERT INTO ConnectionStatus (timestamp, status_data)
            VALUES (?, ?)
            ''', (timestamp, status_json))

            conn.commit()

        except Exception as db_error:
            logger.error(f"Failed to save status to database: {db_error}", exc_info=True)

        logger.debug("Saved component status to file and database")

    except Exception as e:
        logger.error(f"Failed to save status to file: {e}", exc_info=True)

def load_status_from_file():
    """
    Load the status from a JSON file.
    """
    try:
        status_file = os.path.join(config.BASE_DIR, 'data', 'component_status.json')

        if not os.path.exists(status_file):
            logger.info("No status file found, starting with empty status")
            return

        with open(status_file, 'r') as f:
            status = json.load(f)

        # Remove meta information
        if '_meta' in status:
            del status['_meta']

        # Update component status
        with _lock:
            for component_id, component_status in status.items():
                if 'last_activity' in component_status and component_status['last_activity']:
                    try:
                        last_activity = datetime.fromisoformat(component_status['last_activity'].replace('Z', '+00:00'))
                        _component_last_activity[component_id] = last_activity
                        _component_status[component_id] = component_status
                    except Exception:
                        pass

        logger.info(f"Loaded status for {len(status)} components from file")

    except Exception as e:
        logger.error(f"Failed to load status from file: {e}", exc_info=True)

def initialize():
    """
    Initialize the connection status module.

    This function sets up the connection status monitoring system, including:
    - Loading previous status from file
    - Recording initial server activity
    - Starting the monitoring thread
    - Starting the status save thread

    Returns:
        threading.Thread: The monitoring thread
    """
    try:
        logger.info("Initializing connection status module")

        # Store server start time
        global _server_start_time
        _server_start_time = time.time()

        # Try to load status from file
        try:
            load_status_from_file()
        except Exception as e:
            logger.warning(f"Could not load status from file, starting with empty status: {e}")

        # Record initial activity for the server
        try:
            record_component_activity('server')
        except Exception as e:
            logger.warning(f"Could not record initial server activity: {e}")

        # Start the monitoring thread
        try:
            monitor_thread = start_monitoring()
        except Exception as e:
            logger.error(f"Failed to start monitoring thread: {e}", exc_info=True)
            monitor_thread = None

        # Start a thread to periodically save status to file and database
        def _status_save_loop():
            while True:
                try:
                    save_status_to_file()
                except Exception as e:
                    logger.error(f"Error saving status: {e}", exc_info=True)

                # Sleep for a while
                time.sleep(300)  # Save every 5 minutes

        try:
            save_thread = threading.Thread(target=_status_save_loop)
            save_thread.daemon = True
            save_thread.start()
            logger.info("Status save thread started")
        except Exception as e:
            logger.error(f"Failed to start status save thread: {e}", exc_info=True)

        logger.info("Connection status module initialized successfully")

        return monitor_thread

    except Exception as e:
        logger.error(f"Failed to initialize connection status module: {e}", exc_info=True)
        return None

# Record server start time if not already set
if '_server_start_time' not in globals():
    _server_start_time = time.time()

# Module-level initialization will be handled by the initialize() function
# when called by the main application
