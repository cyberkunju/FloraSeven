"""
Connection monitoring module for the FloraSeven server.

This module provides comprehensive monitoring of all system components,
including hardware nodes, sensors, and communication channels.
"""
import logging
import time
import threading
from datetime import datetime, timedelta
import json
import os
from typing import Dict, List, Optional, Any, Callable

import config
import database
import mqtt_client
from connection_status import (
    CONNECTION_STATE_ONLINE,
    CONNECTION_STATE_WARNING,
    CONNECTION_STATE_ERROR,
    CONNECTION_STATE_CRITICAL,
    CONNECTION_STATE_UNKNOWN,
    record_component_activity,
    get_connection_status
)

# Set up logging
logger = logging.getLogger(__name__)

# Component types
COMPONENT_TYPE_HUB = "hub"
COMPONENT_TYPE_PLANT_NODE = "plant_node"
COMPONENT_TYPE_CAMERA = "camera"
COMPONENT_TYPE_SENSOR = "sensor"

# Monitoring states
MONITOR_STATE_ACTIVE = "active"
MONITOR_STATE_PAUSED = "paused"
MONITOR_STATE_STOPPED = "stopped"

# Import timeouts from config
from config import TIMEOUT_WARNING, TIMEOUT_ERROR, TIMEOUT_CRITICAL

# History retention period (in days)
HISTORY_RETENTION_DAYS = 7

class ConnectionMonitor:
    """Connection monitoring service for FloraSeven."""

    def __init__(self):
        """Initialize the connection monitor."""
        self._state = MONITOR_STATE_STOPPED
        self._thread = None
        self._lock = threading.Lock()
        self._check_interval = 60  # Check every 60 seconds
        self._component_registry = {}
        self._event_history = []
        self._event_callbacks = []
        self._last_notification_time = {}
        self._notification_cooldown = 300  # 5 minutes between notifications for same component

        # Load configuration
        self._load_configuration()

        # Initialize component registry
        self._initialize_registry()

        logger.info("Connection monitor initialized")

    def _load_configuration(self):
        """Load monitoring configuration from config file."""
        try:
            # Load from config module
            self._check_interval = getattr(config, 'CONNECTION_CHECK_INTERVAL', 60)
            self._notification_cooldown = getattr(config, 'CONNECTION_NOTIFICATION_COOLDOWN', 300)

            # Use the imported timeouts from config
            self._timeout_warning = TIMEOUT_WARNING
            self._timeout_error = TIMEOUT_ERROR
            self._timeout_critical = TIMEOUT_CRITICAL

            logger.info(f"Loaded connection monitor configuration: check_interval={self._check_interval}s")
        except Exception as e:
            logger.warning(f"Failed to load connection monitor configuration: {e}")
            # Use defaults

    def _initialize_registry(self):
        """Initialize the component registry with expected components."""
        # Main components
        self._register_component("main_hub", COMPONENT_TYPE_HUB, "Main Hub",
                                critical=True, expected_interval=60)
        self._register_component("plant_node", COMPONENT_TYPE_PLANT_NODE, "Plant Node",
                                critical=True, expected_interval=60)
        self._register_component("camera", COMPONENT_TYPE_CAMERA, "Camera",
                                critical=False, expected_interval=300)

        # Sensors
        self._register_component("moisture", COMPONENT_TYPE_SENSOR, "Moisture Sensor",
                                critical=True, expected_interval=60, parent="plant_node")
        self._register_component("temperature", COMPONENT_TYPE_SENSOR, "Temperature Sensor",
                                critical=False, expected_interval=60, parent="plant_node")
        self._register_component("light", COMPONENT_TYPE_SENSOR, "Light Sensor",
                                critical=False, expected_interval=60, parent="plant_node")
        self._register_component("ec", COMPONENT_TYPE_SENSOR, "EC Sensor",
                                critical=False, expected_interval=60, parent="plant_node")
        self._register_component("ph", COMPONENT_TYPE_SENSOR, "pH Sensor",
                                critical=False, expected_interval=60, parent="main_hub")
        self._register_component("uv", COMPONENT_TYPE_SENSOR, "UV Sensor",
                                critical=False, expected_interval=60, parent="main_hub")

    def _register_component(self, component_id: str, component_type: str, display_name: str,
                           critical: bool = False, expected_interval: int = 60,
                           parent: Optional[str] = None):
        """
        Register a component for monitoring.

        Args:
            component_id: Unique identifier for the component
            component_type: Type of component (hub, plant_node, camera, sensor)
            display_name: Human-readable name for the component
            critical: Whether this component is critical for system operation
            expected_interval: Expected interval between updates in seconds
            parent: Parent component ID if this is a sub-component
        """
        self._component_registry[component_id] = {
            "id": component_id,
            "type": component_type,
            "name": display_name,
            "critical": critical,
            "expected_interval": expected_interval,
            "parent": parent,
            "last_seen": None,
            "state": CONNECTION_STATE_UNKNOWN,
            "message": "Not yet connected",
            "consecutive_failures": 0,
            "uptime_percentage": 0.0,
            "connection_history": []
        }

        logger.debug(f"Registered component: {component_id} ({display_name})")

    def start(self):
        """Start the connection monitoring thread."""
        with self._lock:
            if self._state != MONITOR_STATE_STOPPED:
                logger.warning("Connection monitor is already running")
                return False

            self._state = MONITOR_STATE_ACTIVE
            self._thread = threading.Thread(target=self._monitoring_loop)
            self._thread.daemon = True
            self._thread.start()

            logger.info("Connection monitor started")
            return True

    def stop(self):
        """Stop the connection monitoring thread."""
        with self._lock:
            if self._state == MONITOR_STATE_STOPPED:
                logger.warning("Connection monitor is not running")
                return False

            self._state = MONITOR_STATE_STOPPED
            self._thread = None

            logger.info("Connection monitor stopped")
            return True

    def pause(self):
        """Pause the connection monitoring."""
        with self._lock:
            if self._state != MONITOR_STATE_ACTIVE:
                logger.warning("Connection monitor is not active")
                return False

            self._state = MONITOR_STATE_PAUSED
            logger.info("Connection monitor paused")
            return True

    def resume(self):
        """Resume the connection monitoring."""
        with self._lock:
            if self._state != MONITOR_STATE_PAUSED:
                logger.warning("Connection monitor is not paused")
                return False

            self._state = MONITOR_STATE_ACTIVE
            logger.info("Connection monitor resumed")
            return True

    def _monitoring_loop(self):
        """Main monitoring loop."""
        logger.info("Connection monitoring loop started")

        while self._state != MONITOR_STATE_STOPPED:
            try:
                if self._state == MONITOR_STATE_ACTIVE:
                    self._check_all_components()

                # Sleep for the check interval
                time.sleep(self._check_interval)

            except Exception as e:
                logger.error(f"Error in connection monitoring loop: {e}")
                # Continue the loop despite errors

    def _check_all_components(self):
        """Check the status of all registered components."""
        logger.debug("Checking all component connections")

        now = datetime.now()
        status_changed = False

        with self._lock:
            # Get the current connection status from the connection_status module
            current_status = get_connection_status()

            # Update our registry with the current status
            for component_id, component in self._component_registry.items():
                previous_state = component["state"]

                # Update from connection_status module
                if component["type"] == COMPONENT_TYPE_SENSOR:
                    if component_id in current_status.get("sensors", {}):
                        status_data = current_status["sensors"][component_id]
                        self._update_component_status(component_id, status_data)
                else:
                    if component_id in current_status:
                        status_data = current_status[component_id]
                        self._update_component_status(component_id, status_data)

                # Check for state changes
                if component["state"] != previous_state:
                    status_changed = True
                    self._handle_state_change(component_id, previous_state, component["state"])

            # Calculate derived metrics
            self._calculate_metrics()

            # Clean up old history
            self._clean_history()

        # If status changed, store in database
        if status_changed:
            self._store_status_snapshot()

    def _update_component_status(self, component_id: str, status_data: Dict[str, Any]):
        """
        Update a component's status from connection_status data.

        Args:
            component_id: The component ID
            status_data: Status data from connection_status module
        """
        component = self._component_registry[component_id]

        # Update state
        component["state"] = status_data.get("state", CONNECTION_STATE_UNKNOWN)

        # Update message if present
        if "message" in status_data:
            component["message"] = status_data["message"]

        # Update last_seen if present
        if "last_connected" in status_data:
            try:
                component["last_seen"] = datetime.fromisoformat(status_data["last_connected"])
            except (ValueError, TypeError):
                # If the date format is invalid, use current time
                component["last_seen"] = datetime.now()

        # Update consecutive failures
        if component["state"] == CONNECTION_STATE_ONLINE:
            component["consecutive_failures"] = 0
        elif component["state"] in (CONNECTION_STATE_WARNING, CONNECTION_STATE_ERROR, CONNECTION_STATE_CRITICAL):
            component["consecutive_failures"] += 1

    def _handle_state_change(self, component_id: str, previous_state: str, new_state: str):
        """
        Handle a component state change.

        Args:
            component_id: The component ID
            previous_state: The previous connection state
            new_state: The new connection state
        """
        component = self._component_registry[component_id]
        now = datetime.now()

        # Create an event record
        event = {
            "component_id": component_id,
            "component_name": component["name"],
            "component_type": component["type"],
            "previous_state": previous_state,
            "new_state": new_state,
            "timestamp": now.isoformat(),
            "message": component["message"]
        }

        # Add to history
        self._event_history.append(event)

        # Log the event
        if new_state == CONNECTION_STATE_ONLINE and previous_state != CONNECTION_STATE_UNKNOWN:
            logger.info(f"Component reconnected: {component['name']} ({component_id})")
        elif new_state == CONNECTION_STATE_WARNING:
            logger.warning(f"Component connection degraded: {component['name']} ({component_id})")
        elif new_state == CONNECTION_STATE_ERROR or new_state == CONNECTION_STATE_CRITICAL:
            logger.error(f"Component disconnected: {component['name']} ({component_id})")

        # Add to component history
        component["connection_history"].append({
            "state": new_state,
            "timestamp": now.isoformat(),
            "message": component["message"]
        })

        # Trigger callbacks
        self._trigger_event_callbacks(event)

        # Check if we should send a notification
        self._check_notification_needed(component_id, previous_state, new_state)

    def _check_notification_needed(self, component_id: str, previous_state: str, new_state: str):
        """
        Check if a notification should be sent for this state change.

        Args:
            component_id: The component ID
            previous_state: The previous connection state
            new_state: The new connection state
        """
        component = self._component_registry[component_id]
        now = datetime.now()

        # Skip if in cooldown period
        if component_id in self._last_notification_time:
            time_since_last = (now - self._last_notification_time[component_id]).total_seconds()
            if time_since_last < self._notification_cooldown:
                logger.debug(f"Skipping notification for {component_id} (in cooldown period)")
                return

        # Determine if notification is needed
        send_notification = False
        severity = "info"

        if new_state == CONNECTION_STATE_ONLINE and previous_state in (CONNECTION_STATE_WARNING, CONNECTION_STATE_ERROR, CONNECTION_STATE_CRITICAL):
            # Component reconnected
            send_notification = True
            severity = "info"
            message = f"{component['name']} has reconnected"

        elif new_state == CONNECTION_STATE_WARNING and component["critical"]:
            # Critical component degraded
            send_notification = True
            severity = "warning"
            message = f"{component['name']} connection is degraded: {component['message']}"

        elif new_state in (CONNECTION_STATE_ERROR, CONNECTION_STATE_CRITICAL):
            # Any component disconnected
            send_notification = True
            severity = "error" if component["critical"] else "warning"
            message = f"{component['name']} has disconnected: {component['message']}"

        # Send notification if needed
        if send_notification:
            self._send_notification(component_id, severity, message)
            self._last_notification_time[component_id] = now

    def _send_notification(self, component_id: str, severity: str, message: str):
        """
        Send a notification about a component status change.

        Args:
            component_id: The component ID
            severity: Notification severity (info, warning, error)
            message: Notification message
        """
        # Log the notification
        if severity == "info":
            logger.info(f"NOTIFICATION: {message}")
        elif severity == "warning":
            logger.warning(f"NOTIFICATION: {message}")
        else:
            logger.error(f"NOTIFICATION: {message}")

        # Store in database for the mobile app to retrieve
        try:
            database.add_notification(
                component_id=component_id,
                severity=severity,
                message=message,
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"Failed to store notification in database: {e}")

    def _calculate_metrics(self):
        """Calculate derived metrics for all components."""
        now = datetime.now()

        for component_id, component in self._component_registry.items():
            # Skip if no history
            if not component["connection_history"]:
                continue

            # Calculate uptime percentage over the last 24 hours
            connected_time = 0
            total_time = 0

            # Get history from the last 24 hours
            history = [
                h for h in component["connection_history"]
                if datetime.fromisoformat(h["timestamp"]) > now - timedelta(hours=24)
            ]

            if history:
                # Sort by timestamp
                history.sort(key=lambda h: h["timestamp"])

                # Calculate connected time
                for i in range(len(history)):
                    state = history[i]["state"]
                    start_time = datetime.fromisoformat(history[i]["timestamp"])

                    # End time is either the next event or now
                    end_time = now
                    if i < len(history) - 1:
                        end_time = datetime.fromisoformat(history[i+1]["timestamp"])

                    # Calculate duration
                    duration = (end_time - start_time).total_seconds()
                    total_time += duration

                    # Add to connected time if state is ONLINE
                    if state == CONNECTION_STATE_ONLINE:
                        connected_time += duration

                # Calculate percentage
                if total_time > 0:
                    component["uptime_percentage"] = (connected_time / total_time) * 100

            # Limit history size
            if len(component["connection_history"]) > 100:
                component["connection_history"] = component["connection_history"][-100:]

    def _clean_history(self):
        """Clean up old history entries."""
        now = datetime.now()
        cutoff = now - timedelta(days=HISTORY_RETENTION_DAYS)

        # Clean event history
        self._event_history = [
            e for e in self._event_history
            if datetime.fromisoformat(e["timestamp"]) > cutoff
        ]

    def _store_status_snapshot(self):
        """Store a snapshot of the current status in the database."""
        try:
            # Convert to serializable format
            status = {
                "timestamp": datetime.now().isoformat(),
                "components": {}
            }

            for component_id, component in self._component_registry.items():
                status["components"][component_id] = {
                    "id": component_id,
                    "name": component["name"],
                    "type": component["type"],
                    "state": component["state"],
                    "message": component["message"],
                    "last_seen": component["last_seen"].isoformat() if component["last_seen"] else None,
                    "uptime_percentage": component["uptime_percentage"],
                    "critical": component["critical"]
                }

            # Get database connection and store status
            conn = database.get_db_connection()
            database.store_connection_status(conn, status)

        except Exception as e:
            logger.error(f"Failed to store status snapshot: {e}")

    def register_event_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """
        Register a callback function for connection events.

        Args:
            callback: Function to call when a connection event occurs
        """
        with self._lock:
            self._event_callbacks.append(callback)

    def _trigger_event_callbacks(self, event: Dict[str, Any]):
        """
        Trigger all registered event callbacks.

        Args:
            event: The event data
        """
        for callback in self._event_callbacks:
            try:
                callback(event)
            except Exception as e:
                logger.error(f"Error in connection event callback: {e}")

    def get_component_status(self, component_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the status of a specific component.

        Args:
            component_id: The component ID

        Returns:
            The component status or None if not found
        """
        with self._lock:
            if component_id in self._component_registry:
                component = self._component_registry[component_id]
                return {
                    "id": component_id,
                    "name": component["name"],
                    "type": component["type"],
                    "state": component["state"],
                    "message": component["message"],
                    "last_seen": component["last_seen"].isoformat() if component["last_seen"] else None,
                    "uptime_percentage": component["uptime_percentage"],
                    "critical": component["critical"],
                    "consecutive_failures": component["consecutive_failures"]
                }
            return None

    def get_all_component_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Get the status of all components.

        Returns:
            Dictionary of component statuses
        """
        with self._lock:
            result = {}
            for component_id, component in self._component_registry.items():
                result[component_id] = {
                    "id": component_id,
                    "name": component["name"],
                    "type": component["type"],
                    "state": component["state"],
                    "message": component["message"],
                    "last_seen": component["last_seen"].isoformat() if component["last_seen"] else None,
                    "uptime_percentage": component["uptime_percentage"],
                    "critical": component["critical"],
                    "consecutive_failures": component["consecutive_failures"]
                }
            return result

    def get_recent_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get recent connection events.

        Args:
            limit: Maximum number of events to return

        Returns:
            List of recent events
        """
        with self._lock:
            # Sort by timestamp (newest first)
            sorted_events = sorted(
                self._event_history,
                key=lambda e: e["timestamp"],
                reverse=True
            )

            # Return limited number
            return sorted_events[:limit]

    def record_activity(self, component_id: str):
        """
        Record activity for a component.

        Args:
            component_id: The component ID
        """
        # Use the existing record_component_activity function
        if component_id in self._component_registry:
            component_type = self._component_registry[component_id]["type"]

            if component_type == COMPONENT_TYPE_SENSOR:
                record_component_activity("sensors", component_id)
            else:
                record_component_activity(component_id)

    def get_system_health_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the overall system health.

        Returns:
            System health summary
        """
        with self._lock:
            total_components = len(self._component_registry)
            connected_components = sum(1 for c in self._component_registry.values()
                                     if c["state"] == CONNECTION_STATE_ONLINE)
            warning_components = sum(1 for c in self._component_registry.values()
                                    if c["state"] == CONNECTION_STATE_WARNING)
            error_components = sum(1 for c in self._component_registry.values()
                                 if c["state"] == CONNECTION_STATE_ERROR)
            critical_components_count = sum(1 for c in self._component_registry.values()
                                         if c["state"] == CONNECTION_STATE_CRITICAL)
            unknown_components = sum(1 for c in self._component_registry.values()
                                   if c["state"] == CONNECTION_STATE_UNKNOWN)

            # Check critical components
            critical_components = [c for c in self._component_registry.values() if c["critical"]]
            critical_disconnected = sum(1 for c in critical_components
                                      if c["state"] in (CONNECTION_STATE_ERROR, CONNECTION_STATE_CRITICAL))

            # Determine overall health
            if critical_disconnected > 0 or critical_components_count > 0:
                overall_health = "critical"
            elif error_components > 0:
                overall_health = "error"
            elif warning_components > 0:
                overall_health = "warning"
            elif unknown_components == total_components:
                overall_health = "unknown"
            else:
                overall_health = "healthy"

            # Calculate average uptime
            uptime_values = [c["uptime_percentage"] for c in self._component_registry.values()
                           if c["uptime_percentage"] > 0]
            average_uptime = sum(uptime_values) / len(uptime_values) if uptime_values else 0

            return {
                "timestamp": datetime.now().isoformat(),
                "overall_health": overall_health,
                "total_components": total_components,
                "connected_components": connected_components,
                "warning_components": warning_components,
                "error_components": error_components,
                "critical_components_count": critical_components_count,
                "unknown_components": unknown_components,
                "critical_components": len(critical_components),
                "critical_disconnected": critical_disconnected,
                "average_uptime": average_uptime
            }

# Create a singleton instance
connection_monitor = ConnectionMonitor()
