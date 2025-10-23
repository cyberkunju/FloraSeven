"""
Configuration settings for the FloraSeven server.

This module provides configuration settings for the FloraSeven server,
with sensible defaults for production use. Settings can be overridden
using environment variables or a .env file.
"""
import os
import time
import secrets
import logging
import logging.handlers
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ======================================================================
# Flask settings
# ======================================================================
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'  # Default to False for production
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 5000))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'images')
MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16 MB max upload size
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}  # Allowed file extensions for uploads

# ======================================================================
# Database settings
# ======================================================================
DATA_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)  # Ensure data directory exists
DATABASE_PATH = os.path.join(DATA_DIR, 'floraseven_data.db')
DATABASE_BACKUP_DIR = os.path.join(DATA_DIR, 'backups')
os.makedirs(DATABASE_BACKUP_DIR, exist_ok=True)  # Ensure backup directory exists
DATABASE_BACKUP_INTERVAL = int(os.getenv('DATABASE_BACKUP_INTERVAL', 86400))  # 24 hours in seconds
DATABASE_MAX_BACKUPS = int(os.getenv('DATABASE_MAX_BACKUPS', 7))  # Keep 7 days of backups

# Data retention settings
SENSOR_DATA_RETENTION_DAYS = int(os.getenv('SENSOR_DATA_RETENTION_DAYS', 90))  # Keep 90 days of sensor data
CONNECTION_DATA_RETENTION_DAYS = int(os.getenv('CONNECTION_DATA_RETENTION_DAYS', 30))  # Keep 30 days of connection data
NOTIFICATION_RETENTION_DAYS = int(os.getenv('NOTIFICATION_RETENTION_DAYS', 30))  # Keep 30 days of notifications

# ======================================================================
# MQTT settings
# ======================================================================
MQTT_BROKER = os.getenv('MQTT_BROKER', 'localhost')
MQTT_PORT = int(os.getenv('MQTT_PORT', 1883))
MQTT_KEEPALIVE = int(os.getenv('MQTT_KEEPALIVE', 60))
MQTT_CLIENT_ID = os.getenv('MQTT_CLIENT_ID', f'floraseven_server_{int(time.time())}')
MQTT_USERNAME = os.getenv('MQTT_USERNAME', '')
MQTT_PASSWORD = os.getenv('MQTT_PASSWORD', '')
MQTT_USE_TLS = os.getenv('MQTT_USE_TLS', 'False').lower() == 'true'
MQTT_RECONNECT_DELAY_MIN = int(os.getenv('MQTT_RECONNECT_DELAY_MIN', 1))  # 1 second
MQTT_RECONNECT_DELAY_MAX = int(os.getenv('MQTT_RECONNECT_DELAY_MAX', 60))  # 60 seconds
MQTT_QOS = int(os.getenv('MQTT_QOS', 1))  # QoS 1 by default (at least once delivery)

# MQTT topics
MQTT_TOPIC_PLANT_DATA = os.getenv('MQTT_TOPIC_PLANT_DATA', 'floraSeven/plant/+/data')  # + is a wildcard for node ID
MQTT_TOPIC_HUB_STATUS = os.getenv('MQTT_TOPIC_HUB_STATUS', 'floraSeven/hub/+/status')
MQTT_TOPIC_HUB_IMAGE_STATUS = os.getenv('MQTT_TOPIC_HUB_IMAGE_STATUS', 'floraSeven/hub/+/cam/image_status')
MQTT_TOPIC_COMMAND_PUMP = os.getenv('MQTT_TOPIC_COMMAND_PUMP', 'floraSeven/command/hub/pump')
MQTT_TOPIC_COMMAND_CAPTURE_IMAGE = os.getenv('MQTT_TOPIC_COMMAND_CAPTURE_IMAGE', 'floraSeven/command/hub/captureImage')
MQTT_TOPIC_COMMAND_READ_NOW = os.getenv('MQTT_TOPIC_COMMAND_READ_NOW', 'floraSeven/command/plant/+/readNow')
MQTT_TOPIC_SERVER_STATUS = os.getenv('MQTT_TOPIC_SERVER_STATUS', 'floraSeven/server/status')

# ======================================================================
# AI model settings
# ======================================================================
AI_MODEL_DIR = os.path.join(BASE_DIR, 'FloraSeven_AI', 'models', 'model1_whole_plant_health')
AI_CLASS_INDICES_FILE = os.path.join(BASE_DIR, 'FloraSeven_AI', 'models', 'model1_whole_plant_health_class_indices.json')
AI_MODEL_ENABLED = os.getenv('AI_MODEL_ENABLED', 'True').lower() == 'true'
AI_MODEL_CONFIDENCE_THRESHOLD = float(os.getenv('AI_MODEL_CONFIDENCE_THRESHOLD', 0.7))  # Minimum confidence to accept prediction

# ======================================================================
# Default thresholds
# ======================================================================
DEFAULT_THRESHOLDS = {
    'moisture': {'min': float(os.getenv('DEFAULT_MOISTURE_MIN', 40.0)), 'max': float(os.getenv('DEFAULT_MOISTURE_MAX', 70.0))},
    'temp_soil': {'min': float(os.getenv('DEFAULT_TEMP_SOIL_MIN', 18.0)), 'max': float(os.getenv('DEFAULT_TEMP_SOIL_MAX', 28.0))},
    'light_lux': {'min': float(os.getenv('DEFAULT_LIGHT_LUX_MIN', 5000.0)), 'max': float(os.getenv('DEFAULT_LIGHT_LUX_MAX', 30000.0))},
    'ph_water': {'min': float(os.getenv('DEFAULT_PH_WATER_MIN', 6.0)), 'max': float(os.getenv('DEFAULT_PH_WATER_MAX', 7.5))},
    'uv_ambient': {'min': float(os.getenv('DEFAULT_UV_AMBIENT_MIN', 0.0)), 'max': float(os.getenv('DEFAULT_UV_AMBIENT_MAX', 2.0))},
    'ec_raw': {'min': float(os.getenv('DEFAULT_EC_RAW_MIN', 800.0)), 'max': float(os.getenv('DEFAULT_EC_RAW_MAX', 1500.0))}
}

# Default water pump settings
DEFAULT_PUMP_DURATION = int(os.getenv('DEFAULT_PUMP_DURATION', 3))  # seconds
MAX_PUMP_DURATION = int(os.getenv('MAX_PUMP_DURATION', 120))  # seconds
MIN_PUMP_INTERVAL = int(os.getenv('MIN_PUMP_INTERVAL', 300))  # 5 minutes between watering events

# ======================================================================
# Security settings
# ======================================================================
API_USERNAME = os.getenv('API_USERNAME', 'admin')
API_PASSWORD = os.getenv('API_PASSWORD', 'floraseven')
ENABLE_AUTH = os.getenv('ENABLE_AUTH', 'True').lower() == 'true'  # Default to True for production
SECRET_KEY = os.getenv('SECRET_KEY', secrets.token_hex(32))  # Generate a secure random key if not provided
SESSION_TIMEOUT = int(os.getenv('SESSION_TIMEOUT', 3600))  # 1 hour
CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')  # Default to allow all origins

# Rate limiting
RATE_LIMIT_ENABLED = os.getenv('RATE_LIMIT_ENABLED', 'True').lower() == 'true'
RATE_LIMIT = os.getenv('RATE_LIMIT', '100/minute')  # Default rate limit

# Login rate limiting
LOGIN_RATE_LIMIT_ENABLED = os.getenv('LOGIN_RATE_LIMIT_ENABLED', 'True').lower() == 'true'
LOGIN_MAX_ATTEMPTS = int(os.getenv('LOGIN_MAX_ATTEMPTS', 5))  # Max failed login attempts
LOGIN_ATTEMPT_WINDOW = int(os.getenv('LOGIN_ATTEMPT_WINDOW', 300))  # 5 minutes window for login attempts

# Maximum watering duration
MAX_WATERING_DURATION = int(os.getenv('MAX_WATERING_DURATION', 120))  # 120 seconds max watering duration

# ======================================================================
# Connection monitoring settings
# ======================================================================
CONNECTION_CHECK_INTERVAL = int(os.getenv('CONNECTION_CHECK_INTERVAL', 60))  # Check every 60 seconds
CONNECTION_NOTIFICATION_COOLDOWN = int(os.getenv('CONNECTION_NOTIFICATION_COOLDOWN', 300))  # 5 minutes between notifications
TIMEOUT_WARNING = int(os.getenv('TIMEOUT_WARNING', 300))  # 5 minutes
TIMEOUT_ERROR = int(os.getenv('TIMEOUT_ERROR', 600))  # 10 minutes
TIMEOUT_CRITICAL = int(os.getenv('TIMEOUT_CRITICAL', 1800))  # 30 minutes

# ======================================================================
# Logging settings
# ======================================================================
LOG_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)  # Ensure log directory exists
LOG_FILE = os.path.join(LOG_DIR, 'floraseven.log')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
LOG_FORMAT = os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
LOG_MAX_SIZE = int(os.getenv('LOG_MAX_SIZE', 10 * 1024 * 1024))  # 10 MB
LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', 5))  # Keep 5 backup files

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[
        logging.handlers.RotatingFileHandler(
            LOG_FILE,
            maxBytes=LOG_MAX_SIZE,
            backupCount=LOG_BACKUP_COUNT
        ),
        logging.StreamHandler()  # Also log to console
    ]
)

# ======================================================================
# Email notification settings
# ======================================================================
SMTP_SERVER = os.getenv('SMTP_SERVER', '')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
ALERT_FROM = os.getenv('ALERT_FROM', '')
ALERT_RECIPIENTS = os.getenv('ALERT_RECIPIENTS', '').split(',') if os.getenv('ALERT_RECIPIENTS') else []
ENABLE_EMAIL_ALERTS = bool(SMTP_SERVER and SMTP_USERNAME and SMTP_PASSWORD and ALERT_FROM and ALERT_RECIPIENTS)

# ======================================================================
# mDNS service discovery settings
# ======================================================================
MDNS_ENABLED = os.getenv('MDNS_ENABLED', 'True').lower() == 'true'
MDNS_SERVICE_TYPE = os.getenv('MDNS_SERVICE_TYPE', '_floraseven._tcp.local.')
MDNS_SERVICE_NAME = os.getenv('MDNS_SERVICE_NAME', 'FloraSeven Plant Monitor')
MDNS_SERVICE_PORT = int(os.getenv('MDNS_SERVICE_PORT', PORT))

# ======================================================================
# Performance settings
# ======================================================================
WORKER_THREADS = int(os.getenv('WORKER_THREADS', 4))  # Number of worker threads for processing
CACHE_ENABLED = os.getenv('CACHE_ENABLED', 'True').lower() == 'true'
CACHE_TIMEOUT = int(os.getenv('CACHE_TIMEOUT', 60))  # 60 seconds cache timeout
