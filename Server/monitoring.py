"""
Monitoring module for the FloraSeven server.

This module provides functions for monitoring the server and sending alerts.
"""
import os
import logging
import threading
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

import config
import database

# Set up logging
logger = logging.getLogger(__name__)

class ServerMonitor:
    """Server monitoring class."""
    
    def __init__(self):
        """Initialize the server monitor."""
        self.running = False
        self.thread = None
        self.check_interval = 300  # 5 minutes
        self.alert_recipients = []
        self.last_alert_time = {}  # Track when alerts were last sent
        self.alert_cooldown = 3600  # 1 hour cooldown between alerts
        
        # Load alert settings from environment variables
        self.smtp_server = os.getenv('SMTP_SERVER')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.alert_from = os.getenv('ALERT_FROM')
        
        # Parse alert recipients
        recipients = os.getenv('ALERT_RECIPIENTS')
        if recipients:
            self.alert_recipients = [r.strip() for r in recipients.split(',')]
        
        # Enable monitoring if SMTP settings are configured
        self.enabled = bool(self.smtp_server and self.smtp_username and 
                           self.smtp_password and self.alert_from and 
                           self.alert_recipients)
        
        if not self.enabled:
            logger.warning("Monitoring alerts disabled: SMTP settings not configured")
    
    def start(self):
        """Start the monitoring thread."""
        if not self.enabled:
            logger.warning("Monitoring alerts disabled: SMTP settings not configured")
            return False
        
        if self.running:
            logger.warning("Monitoring thread already running")
            return False
        
        self.running = True
        self.thread = threading.Thread(target=self._monitoring_loop)
        self.thread.daemon = True
        self.thread.start()
        
        logger.info("Monitoring thread started")
        return True
    
    def stop(self):
        """Stop the monitoring thread."""
        if not self.running:
            logger.warning("Monitoring thread not running")
            return False
        
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
            self.thread = None
        
        logger.info("Monitoring thread stopped")
        return True
    
    def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.running:
            try:
                self._check_system_health()
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
            
            # Sleep for the check interval
            time.sleep(self.check_interval)
    
    def _check_system_health(self):
        """Check the health of the system."""
        # Check for sensor data freshness
        self._check_sensor_data_freshness()
        
        # Check for critical sensor values
        self._check_critical_sensor_values()
        
        # Check for database size
        self._check_database_size()
    
    def _check_sensor_data_freshness(self):
        """Check if sensor data is being received regularly."""
        try:
            # Get latest sensor readings
            plant_data = database.get_latest_status_data().get('plant', {})
            hub_data = database.get_latest_status_data().get('hub', {})
            
            # Check if we have any data
            if not plant_data and not hub_data:
                self._send_alert(
                    "No sensor data",
                    "No sensor data has been received from either the Plant Node or Hub Node."
                )
                return
            
            # Check Plant Node data freshness
            if plant_data:
                # Get the latest reading timestamp
                latest_reading = database.get_latest_sensor_reading('plantNode1', 'moisture')
                if latest_reading:
                    timestamp = datetime.fromisoformat(latest_reading['timestamp'])
                    now = datetime.now()
                    
                    # Alert if data is more than 10 minutes old
                    if now - timestamp > timedelta(minutes=10):
                        self._send_alert(
                            "Plant Node data stale",
                            f"No new data received from Plant Node in {(now - timestamp).seconds // 60} minutes."
                        )
            
            # Check Hub Node data freshness
            if hub_data:
                # Get the latest reading timestamp
                latest_reading = database.get_latest_sensor_reading('hubNode', 'ph_water')
                if latest_reading:
                    timestamp = datetime.fromisoformat(latest_reading['timestamp'])
                    now = datetime.now()
                    
                    # Alert if data is more than 10 minutes old
                    if now - timestamp > timedelta(minutes=10):
                        self._send_alert(
                            "Hub Node data stale",
                            f"No new data received from Hub Node in {(now - timestamp).seconds // 60} minutes."
                        )
        
        except Exception as e:
            logger.error(f"Error checking sensor data freshness: {e}")
    
    def _check_critical_sensor_values(self):
        """Check for critical sensor values."""
        try:
            # Get latest sensor data and thresholds
            sensor_data = database.get_latest_status_data()
            thresholds = database.get_thresholds()
            
            # Check plant node sensors
            plant_data = sensor_data.get('plant', {})
            for param in ['moisture', 'temp_soil', 'light_lux', 'ec_raw']:
                if param in plant_data and param in thresholds:
                    value = plant_data[param]
                    min_val = thresholds[param]['min']
                    max_val = thresholds[param]['max']
                    
                    # Check if value is critical
                    if value < min_val:
                        self._send_alert(
                            f"Critical {param} value",
                            f"{param} is critically low: {value} (minimum: {min_val})"
                        )
                    elif value > max_val:
                        self._send_alert(
                            f"Critical {param} value",
                            f"{param} is critically high: {value} (maximum: {max_val})"
                        )
            
            # Check hub node sensors
            hub_data = sensor_data.get('hub', {})
            for param in ['ph_water', 'uv_ambient']:
                if param in hub_data and param in thresholds:
                    value = hub_data[param]
                    min_val = thresholds[param]['min']
                    max_val = thresholds[param]['max']
                    
                    # Check if value is critical
                    if value < min_val:
                        self._send_alert(
                            f"Critical {param} value",
                            f"{param} is critically low: {value} (minimum: {min_val})"
                        )
                    elif value > max_val:
                        self._send_alert(
                            f"Critical {param} value",
                            f"{param} is critically high: {value} (maximum: {max_val})"
                        )
        
        except Exception as e:
            logger.error(f"Error checking critical sensor values: {e}")
    
    def _check_database_size(self):
        """Check the size of the database file."""
        try:
            # Get database file size
            db_path = config.DATABASE_PATH
            if os.path.exists(db_path):
                size_mb = os.path.getsize(db_path) / (1024 * 1024)
                
                # Alert if database is larger than 100 MB
                if size_mb > 100:
                    self._send_alert(
                        "Database size warning",
                        f"Database file size is {size_mb:.2f} MB, which may affect performance."
                    )
        
        except Exception as e:
            logger.error(f"Error checking database size: {e}")
    
    def _send_alert(self, subject, message):
        """
        Send an alert email.
        
        Args:
            subject (str): Alert subject
            message (str): Alert message
        """
        # Check if we're in the cooldown period for this alert
        now = datetime.now()
        if subject in self.last_alert_time:
            time_since_last = (now - self.last_alert_time[subject]).total_seconds()
            if time_since_last < self.alert_cooldown:
                logger.info(f"Skipping alert '{subject}' (in cooldown period)")
                return
        
        # Update last alert time
        self.last_alert_time[subject] = now
        
        # Log the alert
        logger.warning(f"ALERT: {subject} - {message}")
        
        # Skip sending email if SMTP is not configured
        if not self.enabled:
            return
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.alert_from
            msg['To'] = ', '.join(self.alert_recipients)
            msg['Subject'] = f"FloraSeven Alert: {subject}"
            
            # Add timestamp and server info to message
            body = f"{message}\n\nTimestamp: {now.isoformat()}\nServer: {os.uname().nodename}"
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Sent alert email: {subject}")
        
        except Exception as e:
            logger.error(f"Error sending alert email: {e}")

# Create a singleton instance
monitor = ServerMonitor()
