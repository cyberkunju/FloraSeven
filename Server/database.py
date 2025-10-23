"""
Database module for the FloraSeven server.

This module provides functions for interacting with the SQLite database,
including initializing the database schema, logging sensor readings and
image analysis results, and retrieving data.

Features:
- Automatic database initialization
- Connection pooling for better performance
- Automatic database backups
- Data pruning to prevent database bloat
- Optimized queries with proper indexing
- Thread-safe operations
"""
import os
import sqlite3
import logging
import threading
import shutil
import time
from datetime import datetime, timedelta
import json
from functools import wraps

import config

# Set up logging
logger = logging.getLogger(__name__)

# Connection pool
_connection_pool = {}
_connection_pool_lock = threading.Lock()
_last_connection_time = {}

# Maximum number of connections in the pool
MAX_POOL_SIZE = 5

# Maximum idle time for a connection (in seconds)
MAX_IDLE_TIME = 60

def dict_factory(cursor, row):
    """
    Convert SQLite row to dictionary.

    Args:
        cursor: SQLite cursor
        row: SQLite row

    Returns:
        dict: Dictionary representation of the row
    """
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}

def get_db_connection():
    """
    Get a connection to the SQLite database from the connection pool.

    This function implements a simple connection pooling mechanism to
    improve performance by reusing database connections.

    Returns:
        sqlite3.Connection: Database connection object
    """
    thread_id = threading.get_ident()

    with _connection_pool_lock:
        # Clean up idle connections
        _cleanup_idle_connections()

        # Check if we already have a connection for this thread
        if thread_id in _connection_pool:
            conn = _connection_pool[thread_id]
            _last_connection_time[thread_id] = time.time()
            return conn

        # Check if we've reached the maximum pool size
        if len(_connection_pool) >= MAX_POOL_SIZE:
            # Find the oldest connection and close it
            oldest_thread = min(_last_connection_time, key=_last_connection_time.get)
            _connection_pool[oldest_thread].close()
            del _connection_pool[oldest_thread]
            del _last_connection_time[oldest_thread]

        # Create a new connection
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(config.DATABASE_PATH), exist_ok=True)

            # Create the connection
            conn = sqlite3.connect(config.DATABASE_PATH,
                                  detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
                                  timeout=30.0)

            # Enable foreign keys
            conn.execute("PRAGMA foreign_keys = ON")

            # Set row factory
            conn.row_factory = sqlite3.Row

            # Add to pool
            _connection_pool[thread_id] = conn
            _last_connection_time[thread_id] = time.time()

            return conn

        except sqlite3.Error as e:
            logger.error(f"Error creating database connection: {e}")
            raise

def _cleanup_idle_connections():
    """Clean up idle connections from the connection pool."""
    current_time = time.time()
    idle_threads = []

    for thread_id, last_time in _last_connection_time.items():
        if current_time - last_time > MAX_IDLE_TIME:
            idle_threads.append(thread_id)

    for thread_id in idle_threads:
        try:
            _connection_pool[thread_id].close()
            del _connection_pool[thread_id]
            del _last_connection_time[thread_id]
            logger.debug(f"Closed idle database connection for thread {thread_id}")
        except Exception as e:
            logger.warning(f"Error closing idle connection: {e}")

def close_db_connections():
    """Close all database connections in the pool."""
    with _connection_pool_lock:
        for thread_id, conn in list(_connection_pool.items()):
            try:
                conn.close()
                logger.debug(f"Closed database connection for thread {thread_id}")
            except Exception as e:
                logger.warning(f"Error closing connection: {e}")

        _connection_pool.clear()
        _last_connection_time.clear()

def with_connection(func):
    """
    Decorator to automatically handle database connections.

    This decorator wraps a function to automatically get a database connection,
    handle transactions, and properly handle errors.

    Args:
        func: The function to wrap

    Returns:
        The wrapped function
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        conn = None
        try:
            conn = get_db_connection()
            return func(conn, *args, **kwargs)
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error in {func.__name__}: {e}")
            raise
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Error in {func.__name__}: {e}")
            raise

    return wrapper

def backup_database():
    """
    Create a backup of the database.

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Check if database exists
        if not os.path.exists(config.DATABASE_PATH):
            logger.warning("Cannot backup database: file does not exist")
            return False

        # Create backup directory if it doesn't exist
        os.makedirs(config.DATABASE_BACKUP_DIR, exist_ok=True)

        # Create backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(config.DATABASE_BACKUP_DIR, f"floraseven_data_{timestamp}.db")

        # Close all connections before backup
        close_db_connections()

        # Copy the database file
        shutil.copy2(config.DATABASE_PATH, backup_path)

        logger.info(f"Database backup created: {backup_path}")

        # Reopen a connection to ensure the pool is not empty
        try:
            get_db_connection()
            logger.debug("Reopened database connection after backup")
        except Exception as e:
            logger.warning(f"Failed to reopen database connection after backup: {e}")

        # Clean up old backups
        _cleanup_old_backups()

        return True

    except Exception as e:
        logger.error(f"Error backing up database: {e}", exc_info=True)
        return False

def _cleanup_old_backups():
    """Clean up old database backups, keeping only the most recent ones."""
    try:
        # Get all backup files
        backup_files = []
        for filename in os.listdir(config.DATABASE_BACKUP_DIR):
            if filename.startswith("floraseven_data_") and filename.endswith(".db"):
                file_path = os.path.join(config.DATABASE_BACKUP_DIR, filename)
                backup_files.append((file_path, os.path.getmtime(file_path)))

        # Sort by modification time (newest first)
        backup_files.sort(key=lambda x: x[1], reverse=True)

        # Keep only the most recent backups
        if len(backup_files) > config.DATABASE_MAX_BACKUPS:
            for file_path, _ in backup_files[config.DATABASE_MAX_BACKUPS:]:
                os.remove(file_path)
                logger.debug(f"Removed old database backup: {file_path}")

    except Exception as e:
        logger.error(f"Error cleaning up old backups: {e}")

def optimize_database():
    """
    Optimize the database by running VACUUM and ANALYZE.

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        conn = get_db_connection()

        # Run VACUUM to rebuild the database file
        conn.execute("VACUUM")

        # Run ANALYZE to update statistics
        conn.execute("ANALYZE")

        conn.close()

        logger.info("Database optimized")
        return True

    except Exception as e:
        logger.error(f"Error optimizing database: {e}")
        return False

def init_db():
    """
    Initialize the SQLite database with the required schema.

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(config.DATABASE_PATH), exist_ok=True)

        # Connect to database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Enable WAL mode for better concurrency
        cursor.execute("PRAGMA journal_mode = WAL")

        # Set synchronous mode to NORMAL for better performance
        cursor.execute("PRAGMA synchronous = NORMAL")

        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON")

        # Create SensorLog table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS SensorLog (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            node_id TEXT NOT NULL,
            sensor_type TEXT NOT NULL,
            value REAL NOT NULL,
            created_at TEXT DEFAULT (datetime('now')),
            UNIQUE(timestamp, node_id, sensor_type)
        )
        ''')

        # Create indices for SensorLog
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sensorlog_timestamp ON SensorLog(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sensorlog_node_sensor ON SensorLog(node_id, sensor_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sensorlog_node_timestamp ON SensorLog(node_id, timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sensorlog_sensor_timestamp ON SensorLog(sensor_type, timestamp)')

        # Create ImageLog table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS ImageLog (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            image_filename TEXT NOT NULL,
            health_label TEXT NOT NULL,
            health_score INTEGER NOT NULL,
            confidence REAL NOT NULL,
            created_at TEXT DEFAULT (datetime('now')),
            UNIQUE(image_filename)
        )
        ''')

        # Create indices for ImageLog
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_imagelog_timestamp ON ImageLog(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_imagelog_health ON ImageLog(health_label, health_score)')

        # Create Thresholds table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Thresholds (
            parameter_name TEXT PRIMARY KEY,
            min_value REAL NOT NULL,
            max_value REAL NOT NULL,
            updated_at TEXT DEFAULT (datetime('now'))
        )
        ''')

        # Create ConnectionStatus table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS ConnectionStatus (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            status_data TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        )
        ''')

        # Create index for ConnectionStatus
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_connectionstatus_timestamp ON ConnectionStatus(timestamp)')

        # Create ConnectionEvents table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS ConnectionEvents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            component_id TEXT NOT NULL,
            component_name TEXT NOT NULL,
            component_type TEXT NOT NULL,
            previous_state TEXT NOT NULL,
            new_state TEXT NOT NULL,
            message TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        )
        ''')

        # Create indices for ConnectionEvents
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_connectionevents_timestamp ON ConnectionEvents(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_connectionevents_component ON ConnectionEvents(component_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_connectionevents_state ON ConnectionEvents(new_state)')

        # Create Notifications table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            component_id TEXT NOT NULL,
            severity TEXT NOT NULL,
            message TEXT NOT NULL,
            read INTEGER DEFAULT 0,
            action_taken INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now'))
        )
        ''')

        # Create indices for Notifications
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_notifications_timestamp ON Notifications(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_notifications_read ON Notifications(read)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_notifications_component_severity ON Notifications(component_id, severity)')

        # Create SystemStats table for tracking system performance
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS SystemStats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            stat_type TEXT NOT NULL,
            stat_value REAL NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        )
        ''')

        # Create indices for SystemStats
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_systemstats_timestamp ON SystemStats(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_systemstats_type ON SystemStats(stat_type)')

        # Create WateringEvents table for tracking watering events
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS WateringEvents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            duration_sec INTEGER NOT NULL,
            triggered_by TEXT NOT NULL,
            moisture_before REAL,
            moisture_after REAL,
            created_at TEXT DEFAULT (datetime('now'))
        )
        ''')

        # Create indices for WateringEvents
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_wateringevents_timestamp ON WateringEvents(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_wateringevents_triggered_by ON WateringEvents(triggered_by)')

        # Insert default thresholds if they don't exist
        for param, values in config.DEFAULT_THRESHOLDS.items():
            cursor.execute('''
            INSERT OR IGNORE INTO Thresholds (parameter_name, min_value, max_value)
            VALUES (?, ?, ?)
            ''', (param, values['min'], values['max']))

        conn.commit()

        # Optimize the database
        cursor.execute("ANALYZE")

        conn.close()

        logger.info("Database initialized successfully")

        # Create initial backup
        backup_database()

        return True

    except Exception as e:
        logger.error(f"Error initializing database: {e}", exc_info=True)
        return False

@with_connection
def log_sensor_reading(conn, timestamp, node_id, sensor_type, value):
    """
    Log a sensor reading to the database.

    Args:
        conn: Database connection
        timestamp (str): ISO8601 timestamp
        node_id (str): Identifier for the node
        sensor_type (str): Type of sensor
        value (float): Sensor reading value

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        cursor = conn.cursor()

        # Check if record already exists
        cursor.execute('''
        SELECT id FROM SensorLog
        WHERE timestamp = ? AND node_id = ? AND sensor_type = ?
        ''', (timestamp, node_id, sensor_type))

        existing_record = cursor.fetchone()

        if existing_record:
            # Update existing record
            cursor.execute('''
            UPDATE SensorLog
            SET value = ?
            WHERE timestamp = ? AND node_id = ? AND sensor_type = ?
            ''', (value, timestamp, node_id, sensor_type))
        else:
            # Insert new record
            cursor.execute('''
            INSERT INTO SensorLog (timestamp, node_id, sensor_type, value)
            VALUES (?, ?, ?, ?)
            ''', (timestamp, node_id, sensor_type, value))

        conn.commit()

        logger.debug(f"Logged sensor reading: {node_id} {sensor_type} = {value}")
        return True

    except sqlite3.Error as e:
        logger.error(f"Database error logging sensor reading: {e}")
        return False
    except Exception as e:
        logger.error(f"Error logging sensor reading: {e}", exc_info=True)
        return False

@with_connection
def log_image_analysis(conn, timestamp, image_filename, health_label, health_score, confidence):
    """
    Log image analysis results to the database.

    Args:
        conn: Database connection
        timestamp (str): ISO8601 timestamp
        image_filename (str): Name of the image file
        health_label (str): Health classification
        health_score (int): Health score (0-100)
        confidence (float): Confidence of the classification (0-1)

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        cursor = conn.cursor()

        # Check if record already exists
        cursor.execute('''
        SELECT id FROM ImageLog
        WHERE image_filename = ?
        ''', (image_filename,))

        existing_record = cursor.fetchone()

        if existing_record:
            # Update existing record
            cursor.execute('''
            UPDATE ImageLog
            SET timestamp = ?, health_label = ?, health_score = ?, confidence = ?
            WHERE image_filename = ?
            ''', (timestamp, health_label, health_score, confidence, image_filename))
        else:
            # Insert new record
            cursor.execute('''
            INSERT INTO ImageLog (timestamp, image_filename, health_label, health_score, confidence)
            VALUES (?, ?, ?, ?, ?)
            ''', (timestamp, image_filename, health_label, health_score, confidence))

        conn.commit()

        logger.info(f"Logged image analysis: {image_filename}, {health_label}, score={health_score}, confidence={confidence:.2f}")
        return True

    except sqlite3.Error as e:
        logger.error(f"Database error logging image analysis: {e}")
        return False
    except Exception as e:
        logger.error(f"Error logging image analysis: {e}", exc_info=True)
        return False

@with_connection
def get_latest_sensor_reading(conn, node_id, sensor_type):
    """
    Get the latest reading for a specific sensor.

    Args:
        conn: Database connection
        node_id (str): Identifier for the node
        sensor_type (str): Type of sensor

    Returns:
        dict: Sensor reading data or None if not found
    """
    try:
        # Set row factory for this connection
        original_row_factory = conn.row_factory
        conn.row_factory = dict_factory
        cursor = conn.cursor()

        cursor.execute('''
        SELECT timestamp, node_id, sensor_type, value
        FROM SensorLog
        WHERE node_id = ? AND sensor_type = ?
        ORDER BY timestamp DESC
        LIMIT 1
        ''', (node_id, sensor_type))

        result = cursor.fetchone()

        # Restore original row factory
        conn.row_factory = original_row_factory

        return result

    except sqlite3.Error as e:
        logger.error(f"Database error getting latest sensor reading: {e}")
        return None
    except Exception as e:
        logger.error(f"Error getting latest sensor reading: {e}", exc_info=True)
        return None

@with_connection
def get_latest_status_data(conn):
    """
    Get the latest readings for all sensors.

    Args:
        conn: Database connection

    Returns:
        dict: Dictionary with latest sensor data
    """
    try:
        # Set row factory for this connection
        original_row_factory = conn.row_factory
        conn.row_factory = dict_factory
        cursor = conn.cursor()

        # Get all latest sensor readings in a single query for better performance
        cursor.execute('''
        WITH LatestReadings AS (
            SELECT
                node_id,
                sensor_type,
                value,
                ROW_NUMBER() OVER (PARTITION BY node_id, sensor_type ORDER BY timestamp DESC) as rn
            FROM SensorLog
            WHERE (node_id = 'plantNode1' AND sensor_type IN ('moisture', 'temp_soil', 'light_lux', 'ec_raw'))
               OR (node_id = 'hubNode' AND sensor_type IN ('ph_water', 'uv_ambient', 'pump_state'))
        )
        SELECT node_id, sensor_type, value
        FROM LatestReadings
        WHERE rn = 1
        ''')

        results = cursor.fetchall()

        # Restore original row factory
        conn.row_factory = original_row_factory

        # Process results
        plant_data = {}
        hub_data = {}

        for row in results:
            if row['node_id'] == 'plantNode1':
                plant_data[row['sensor_type']] = row['value']
            elif row['node_id'] == 'hubNode':
                # Convert pump_state to boolean
                if row['sensor_type'] == 'pump_state':
                    hub_data['pump_active'] = bool(row['value'])
                else:
                    hub_data[row['sensor_type']] = row['value']

        # Add timestamps
        status_data = {
            'plant': plant_data,
            'hub': hub_data,
            'timestamp': datetime.now().isoformat(),
            'is_offline_data': False
        }

        return status_data

    except sqlite3.Error as e:
        logger.error(f"Database error getting latest status data: {e}")
        return {
            'plant': {},
            'hub': {},
            'timestamp': datetime.now().isoformat(),
            'is_offline_data': True,
            'error': str(e)
        }
    except Exception as e:
        logger.error(f"Error getting latest status data: {e}", exc_info=True)
        return {
            'plant': {},
            'hub': {},
            'timestamp': datetime.now().isoformat(),
            'is_offline_data': True,
            'error': str(e)
        }

@with_connection
def get_sensor_history(conn, node_id, sensor_type, start_time=None, end_time=None, limit=100, interval=None):
    """
    Get historical sensor readings.

    Args:
        conn: Database connection
        node_id (str): Identifier for the node
        sensor_type (str): Type of sensor
        start_time (str, optional): ISO8601 start timestamp
        end_time (str, optional): ISO8601 end timestamp
        limit (int, optional): Maximum number of readings to return
        interval (str, optional): Time interval for aggregation ('hour', 'day', 'week', 'month')

    Returns:
        list: List of sensor readings
    """
    try:
        # Set row factory for this connection
        original_row_factory = conn.row_factory
        conn.row_factory = dict_factory
        cursor = conn.cursor()

        # If interval is specified, use aggregation
        if interval:
            # Define the time function based on the interval
            if interval == 'hour':
                time_function = "strftime('%Y-%m-%d %H:00:00', timestamp)"
            elif interval == 'day':
                time_function = "strftime('%Y-%m-%d 00:00:00', timestamp)"
            elif interval == 'week':
                time_function = "strftime('%Y-%W', timestamp)"  # Year-Week format
            elif interval == 'month':
                time_function = "strftime('%Y-%m-01', timestamp)"
            else:
                # Invalid interval, fall back to no aggregation
                interval = None

        if interval:
            # Query with aggregation
            query = f'''
            SELECT
                {time_function} as period,
                node_id,
                sensor_type,
                AVG(value) as avg_value,
                MIN(value) as min_value,
                MAX(value) as max_value,
                COUNT(*) as reading_count
            FROM SensorLog
            WHERE node_id = ? AND sensor_type = ?
            '''
        else:
            # Query without aggregation
            query = '''
            SELECT timestamp, node_id, sensor_type, value
            FROM SensorLog
            WHERE node_id = ? AND sensor_type = ?
            '''

        params = [node_id, sensor_type]

        if start_time:
            query += ' AND timestamp >= ?'
            params.append(start_time)

        if end_time:
            query += ' AND timestamp <= ?'
            params.append(end_time)

        if interval:
            query += ' GROUP BY period ORDER BY period DESC LIMIT ?'
        else:
            query += ' ORDER BY timestamp DESC LIMIT ?'

        params.append(limit)

        cursor.execute(query, params)
        results = cursor.fetchall()

        # Restore original row factory
        conn.row_factory = original_row_factory

        return results

    except sqlite3.Error as e:
        logger.error(f"Database error getting sensor history: {e}")
        return []
    except Exception as e:
        logger.error(f"Error getting sensor history: {e}", exc_info=True)
        return []

@with_connection
def get_latest_image_data(conn):
    """
    Get data for the most recent image analysis.

    Args:
        conn: Database connection

    Returns:
        dict: Image analysis data or None if not found
    """
    try:
        # Set row factory for this connection
        original_row_factory = conn.row_factory
        conn.row_factory = dict_factory
        cursor = conn.cursor()

        cursor.execute('''
        SELECT timestamp, image_filename, health_label, health_score, confidence
        FROM ImageLog
        ORDER BY timestamp DESC
        LIMIT 1
        ''')

        result = cursor.fetchone()

        # Restore original row factory
        conn.row_factory = original_row_factory

        if result:
            return {
                'latest_image': result['image_filename'],
                'health_label': result['health_label'],
                'health_score': result['health_score'],
                'confidence': result['confidence'],
                'timestamp': result['timestamp'],
                'is_offline_data': False
            }
        else:
            return {
                'latest_image': None,
                'health_label': 'unknown',
                'health_score': 0,
                'confidence': 0,
                'timestamp': datetime.now().isoformat(),
                'is_offline_data': True,
                'error': 'No image data available'
            }

    except sqlite3.Error as e:
        logger.error(f"Database error getting latest image data: {e}")
        return {
            'latest_image': None,
            'health_label': 'unknown',
            'health_score': 0,
            'confidence': 0,
            'timestamp': datetime.now().isoformat(),
            'is_offline_data': True,
            'error': str(e)
        }
    except Exception as e:
        logger.error(f"Error getting latest image data: {e}", exc_info=True)
        return {
            'latest_image': None,
            'health_label': 'unknown',
            'health_score': 0,
            'confidence': 0,
            'timestamp': datetime.now().isoformat(),
            'is_offline_data': True,
            'error': str(e)
        }

@with_connection
def get_image_history(conn, start_time=None, end_time=None, limit=20, health_label=None):
    """
    Get historical image analysis results.

    Args:
        conn: Database connection
        start_time (str, optional): ISO8601 start timestamp
        end_time (str, optional): ISO8601 end timestamp
        limit (int, optional): Maximum number of results to return
        health_label (str, optional): Filter by health label

    Returns:
        list: List of image analysis results
    """
    try:
        # Set row factory for this connection
        original_row_factory = conn.row_factory
        conn.row_factory = dict_factory
        cursor = conn.cursor()

        query = '''
        SELECT timestamp, image_filename, health_label, health_score, confidence
        FROM ImageLog
        '''
        params = []
        where_clauses = []

        if start_time:
            where_clauses.append('timestamp >= ?')
            params.append(start_time)

        if end_time:
            where_clauses.append('timestamp <= ?')
            params.append(end_time)

        if health_label:
            where_clauses.append('health_label = ?')
            params.append(health_label)

        if where_clauses:
            query += ' WHERE ' + ' AND '.join(where_clauses)

        query += ' ORDER BY timestamp DESC LIMIT ?'
        params.append(limit)

        cursor.execute(query, params)
        results = cursor.fetchall()

        # Restore original row factory
        conn.row_factory = original_row_factory

        return results

    except sqlite3.Error as e:
        logger.error(f"Database error getting image history: {e}")
        return []
    except Exception as e:
        logger.error(f"Error getting image history: {e}", exc_info=True)
        return []

@with_connection
def get_thresholds(conn):
    """
    Get all threshold values.

    Args:
        conn: Database connection

    Returns:
        dict: Dictionary with parameter thresholds
    """
    try:
        # Set row factory for this connection
        original_row_factory = conn.row_factory
        conn.row_factory = dict_factory
        cursor = conn.cursor()

        cursor.execute('''
        SELECT parameter_name, min_value, max_value
        FROM Thresholds
        ''')

        results = cursor.fetchall()

        # Restore original row factory
        conn.row_factory = original_row_factory

        thresholds = {}
        for row in results:
            thresholds[row['parameter_name']] = {
                'min': row['min_value'],
                'max': row['max_value']
            }

        return thresholds

    except sqlite3.Error as e:
        logger.error(f"Database error getting thresholds: {e}")
        # Return default thresholds if there's an error
        return config.DEFAULT_THRESHOLDS
    except Exception as e:
        logger.error(f"Error getting thresholds: {e}", exc_info=True)
        # Return default thresholds if there's an error
        return config.DEFAULT_THRESHOLDS

@with_connection
def update_thresholds(conn, thresholds_dict):
    """
    Update threshold values.

    Args:
        conn: Database connection
        thresholds_dict (dict): Dictionary with parameters to update
            Format: {
                'parameter_name': {
                    'min': min_value,
                    'max': max_value
                },
                ...
            }

    Returns:
        list: List of parameters that were updated
    """
    try:
        cursor = conn.cursor()
        updated_params = []

        for param, values in thresholds_dict.items():
            if 'min' in values and 'max' in values:
                # Validate values
                min_value = float(values['min'])
                max_value = float(values['max'])

                # Ensure min is less than max
                if min_value >= max_value:
                    logger.warning(f"Invalid threshold values for {param}: min ({min_value}) must be less than max ({max_value})")
                    continue

                # Check if parameter exists
                cursor.execute('''
                SELECT COUNT(*) FROM Thresholds WHERE parameter_name = ?
                ''', (param,))

                if cursor.fetchone()[0] > 0:
                    # Update existing parameter
                    cursor.execute('''
                    UPDATE Thresholds
                    SET min_value = ?, max_value = ?, updated_at = datetime('now')
                    WHERE parameter_name = ?
                    ''', (min_value, max_value, param))
                else:
                    # Insert new parameter
                    cursor.execute('''
                    INSERT INTO Thresholds (parameter_name, min_value, max_value)
                    VALUES (?, ?, ?)
                    ''', (param, min_value, max_value))

                updated_params.append(param)

        conn.commit()

        if updated_params:
            logger.info(f"Updated thresholds for: {', '.join(updated_params)}")

        return updated_params

    except sqlite3.Error as e:
        logger.error(f"Database error updating thresholds: {e}")
        return []
    except Exception as e:
        logger.error(f"Error updating thresholds: {e}", exc_info=True)
        return []

@with_connection
def store_connection_status(conn, status_data):
    """
    Store a snapshot of the connection status.

    Args:
        conn: Database connection
        status_data (dict): Connection status data

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        cursor = conn.cursor()

        # Convert dict to JSON string
        status_json = json.dumps(status_data)

        cursor.execute('''
        INSERT INTO ConnectionStatus (timestamp, status_data)
        VALUES (?, ?)
        ''', (datetime.now().isoformat(), status_json))

        conn.commit()

        logger.debug("Stored connection status snapshot")
        return True

    except Exception as e:
        logger.error(f"Error storing connection status: {e}")
        return False

@with_connection
def get_connection_status_history(conn, start_time=None, end_time=None, limit=20):
    """
    Get historical connection status snapshots.

    Args:
        conn: Database connection
        start_time (str, optional): ISO8601 start timestamp
        end_time (str, optional): ISO8601 end timestamp
        limit (int, optional): Maximum number of snapshots to return

    Returns:
        list: List of connection status snapshots
    """
    try:
        # Set row factory for this connection
        original_row_factory = conn.row_factory
        conn.row_factory = dict_factory
        cursor = conn.cursor()

        query = '''
        SELECT id, timestamp, status_data
        FROM ConnectionStatus
        '''
        params = []

        if start_time:
            query += ' WHERE timestamp >= ?'
            params.append(start_time)

            if end_time:
                query += ' AND timestamp <= ?'
                params.append(end_time)
        elif end_time:
            query += ' WHERE timestamp <= ?'
            params.append(end_time)

        query += ' ORDER BY timestamp DESC LIMIT ?'
        params.append(limit)

        cursor.execute(query, params)

        results = cursor.fetchall()

        # Restore original row factory
        conn.row_factory = original_row_factory

        # Parse JSON data
        for result in results:
            result['status_data'] = json.loads(result['status_data'])

        return results

    except Exception as e:
        logger.error(f"Error getting connection status history: {e}")
        return []

@with_connection
def log_connection_event(conn, component_id, component_name, component_type, previous_state, new_state, message=None):
    """
    Log a connection state change event.

    Args:
        conn: Database connection
        component_id (str): Component identifier
        component_name (str): Human-readable component name
        component_type (str): Type of component
        previous_state (str): Previous connection state
        new_state (str): New connection state
        message (str, optional): Additional message

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        cursor = conn.cursor()

        cursor.execute('''
        INSERT INTO ConnectionEvents (timestamp, component_id, component_name, component_type,
                                     previous_state, new_state, message)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (datetime.now().isoformat(), component_id, component_name, component_type,
             previous_state, new_state, message))

        conn.commit()

        logger.debug(f"Logged connection event: {component_id} {previous_state} -> {new_state}")
        return True

    except Exception as e:
        logger.error(f"Error logging connection event: {e}")
        return False

@with_connection
def get_connection_events(conn, component_id=None, start_time=None, end_time=None, limit=50):
    """
    Get connection state change events.

    Args:
        conn: Database connection
        component_id (str, optional): Filter by component ID
        start_time (str, optional): ISO8601 start timestamp
        end_time (str, optional): ISO8601 end timestamp
        limit (int, optional): Maximum number of events to return

    Returns:
        list: List of connection events
    """
    try:
        # Set row factory for this connection
        original_row_factory = conn.row_factory
        conn.row_factory = dict_factory
        cursor = conn.cursor()

        query = '''
        SELECT id, timestamp, component_id, component_name, component_type,
               previous_state, new_state, message
        FROM ConnectionEvents
        '''
        params = []

        # Build WHERE clause
        where_clauses = []

        if component_id:
            where_clauses.append('component_id = ?')
            params.append(component_id)

        if start_time:
            where_clauses.append('timestamp >= ?')
            params.append(start_time)

        if end_time:
            where_clauses.append('timestamp <= ?')
            params.append(end_time)

        if where_clauses:
            query += ' WHERE ' + ' AND '.join(where_clauses)

        query += ' ORDER BY timestamp DESC LIMIT ?'
        params.append(limit)

        cursor.execute(query, params)

        results = cursor.fetchall()

        # Restore original row factory
        conn.row_factory = original_row_factory

        return results

    except Exception as e:
        logger.error(f"Error getting connection events: {e}")
        return []

def add_notification(component_id, severity, message, timestamp=None):
    """
    Add a notification to the database.

    Args:
        component_id (str): Component identifier
        severity (str): Notification severity (info, warning, error)
        message (str): Notification message
        timestamp (datetime, optional): Notification timestamp

    Returns:
        int: Notification ID if successful, None otherwise
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        if timestamp is None:
            timestamp = datetime.now()

        cursor.execute('''
        INSERT INTO Notifications (timestamp, component_id, severity, message)
        VALUES (?, ?, ?, ?)
        ''', (timestamp.isoformat(), component_id, severity, message))

        notification_id = cursor.lastrowid

        conn.commit()
        conn.close()

        logger.debug(f"Added notification: {severity} - {message}")
        return notification_id

    except Exception as e:
        logger.error(f"Error adding notification: {e}")
        return None

def get_notifications(read=None, component_id=None, severity=None, start_time=None, end_time=None, limit=50):
    """
    Get notifications from the database.

    Args:
        read (bool, optional): Filter by read status
        component_id (str, optional): Filter by component ID
        severity (str, optional): Filter by severity
        start_time (str, optional): ISO8601 start timestamp
        end_time (str, optional): ISO8601 end timestamp
        limit (int, optional): Maximum number of notifications to return

    Returns:
        list: List of notifications
    """
    try:
        conn = get_db_connection()
        conn.row_factory = dict_factory
        cursor = conn.cursor()

        query = '''
        SELECT id, timestamp, component_id, severity, message, read, action_taken
        FROM Notifications
        '''
        params = []

        # Build WHERE clause
        where_clauses = []

        if read is not None:
            where_clauses.append('read = ?')
            params.append(1 if read else 0)

        if component_id:
            where_clauses.append('component_id = ?')
            params.append(component_id)

        if severity:
            where_clauses.append('severity = ?')
            params.append(severity)

        if start_time:
            where_clauses.append('timestamp >= ?')
            params.append(start_time)

        if end_time:
            where_clauses.append('timestamp <= ?')
            params.append(end_time)

        if where_clauses:
            query += ' WHERE ' + ' AND '.join(where_clauses)

        query += ' ORDER BY timestamp DESC LIMIT ?'
        params.append(limit)

        cursor.execute(query, params)

        results = cursor.fetchall()
        conn.close()

        return results

    except Exception as e:
        logger.error(f"Error getting notifications: {e}")
        return []

def mark_notification_read(notification_id, read=True):
    """
    Mark a notification as read or unread.

    Args:
        notification_id (int): Notification ID
        read (bool, optional): Read status

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
        UPDATE Notifications
        SET read = ?
        WHERE id = ?
        ''', (1 if read else 0, notification_id))

        conn.commit()
        conn.close()

        logger.debug(f"Marked notification {notification_id} as {'read' if read else 'unread'}")
        return True

    except Exception as e:
        logger.error(f"Error marking notification as read: {e}")
        return False

def mark_notification_action_taken(notification_id, action_taken=True):
    """
    Mark a notification as having action taken.

    Args:
        notification_id (int): Notification ID
        action_taken (bool, optional): Action taken status

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
        UPDATE Notifications
        SET action_taken = ?
        WHERE id = ?
        ''', (1 if action_taken else 0, notification_id))

        conn.commit()
        conn.close()

        logger.debug(f"Marked notification {notification_id} as {'action taken' if action_taken else 'no action taken'}")
        return True

    except Exception as e:
        logger.error(f"Error marking notification action taken: {e}")
        return False

def clear_old_notifications(days=30):
    """
    Clear notifications older than the specified number of days.

    Args:
        days (int, optional): Number of days to keep

    Returns:
        int: Number of notifications cleared
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

        cursor.execute('''
        DELETE FROM Notifications
        WHERE timestamp < ?
        ''', (cutoff_date,))

        deleted_count = cursor.rowcount

        conn.commit()
        conn.close()

        logger.info(f"Cleared {deleted_count} notifications older than {days} days")
        return deleted_count

    except Exception as e:
        logger.error(f"Error clearing old notifications: {e}")
        return 0

def prune_sensor_data(days=90):
    """
    Prune sensor data older than the specified number of days.

    Args:
        days (int, optional): Number of days to keep

    Returns:
        int: Number of records pruned
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

        # First, count how many records will be deleted
        cursor.execute('''
        SELECT COUNT(*) FROM SensorLog
        WHERE timestamp < ?
        ''', (cutoff_date,))

        count = cursor.fetchone()[0]

        if count > 0:
            # Delete the old records
            cursor.execute('''
            DELETE FROM SensorLog
            WHERE timestamp < ?
            ''', (cutoff_date,))

            conn.commit()

            logger.info(f"Pruned {count} sensor readings older than {days} days")

            # Optimize the database after a large deletion
            if count > 1000:
                conn.execute("VACUUM")
                logger.info("Optimized database after pruning")

        conn.close()
        return count

    except Exception as e:
        logger.error(f"Error pruning sensor data: {e}", exc_info=True)
        return 0

def prune_connection_data(days=30):
    """
    Prune connection status and events data older than the specified number of days.

    Args:
        days (int, optional): Number of days to keep

    Returns:
        dict: Number of records pruned by table
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

        pruned = {}

        # Prune ConnectionStatus
        cursor.execute('''
        SELECT COUNT(*) FROM ConnectionStatus
        WHERE timestamp < ?
        ''', (cutoff_date,))

        count = cursor.fetchone()[0]

        if count > 0:
            cursor.execute('''
            DELETE FROM ConnectionStatus
            WHERE timestamp < ?
            ''', (cutoff_date,))

            pruned['connection_status'] = count

        # Prune ConnectionEvents
        cursor.execute('''
        SELECT COUNT(*) FROM ConnectionEvents
        WHERE timestamp < ?
        ''', (cutoff_date,))

        count = cursor.fetchone()[0]

        if count > 0:
            cursor.execute('''
            DELETE FROM ConnectionEvents
            WHERE timestamp < ?
            ''', (cutoff_date,))

            pruned['connection_events'] = count

        conn.commit()

        # Optimize if we deleted a lot of data
        if sum(pruned.values()) > 1000:
            conn.execute("VACUUM")
            logger.info("Optimized database after pruning connection data")

        conn.close()

        if pruned:
            logger.info(f"Pruned connection data older than {days} days: {pruned}")

        return pruned

    except Exception as e:
        logger.error(f"Error pruning connection data: {e}", exc_info=True)
        return {}

def prune_all_data():
    """
    Prune all old data from the database based on configured retention periods.

    Returns:
        dict: Summary of pruned data
    """
    summary = {}

    # Prune sensor data (90 days by default)
    sensor_days = getattr(config, 'SENSOR_DATA_RETENTION_DAYS', 90)
    summary['sensor_data'] = prune_sensor_data(days=sensor_days)

    # Prune connection data (30 days by default)
    connection_days = getattr(config, 'CONNECTION_DATA_RETENTION_DAYS', 30)
    summary['connection_data'] = prune_connection_data(days=connection_days)

    # Prune notifications (30 days by default)
    notification_days = getattr(config, 'NOTIFICATION_RETENTION_DAYS', 30)
    summary['notifications'] = clear_old_notifications(days=notification_days)

    # Optimize the database
    optimize_database()

    return summary

@with_connection
def log_watering_event(conn, timestamp, duration_sec, triggered_by, moisture_before=None, moisture_after=None):
    """
    Log a watering event to the database.

    Args:
        conn: Database connection
        timestamp (str): ISO8601 timestamp
        duration_sec (int): Duration of watering in seconds
        triggered_by (str): What triggered the watering ('manual', 'auto', 'schedule')
        moisture_before (float, optional): Moisture level before watering
        moisture_after (float, optional): Moisture level after watering

    Returns:
        int: ID of the new watering event record, or None if failed
    """
    try:
        cursor = conn.cursor()

        cursor.execute('''
        INSERT INTO WateringEvents (timestamp, duration_sec, triggered_by, moisture_before, moisture_after)
        VALUES (?, ?, ?, ?, ?)
        ''', (timestamp, duration_sec, triggered_by, moisture_before, moisture_after))

        event_id = cursor.lastrowid
        conn.commit()

        logger.info(f"Logged watering event: {triggered_by}, duration={duration_sec}s")
        return event_id

    except sqlite3.Error as e:
        logger.error(f"Database error logging watering event: {e}")
        return None
    except Exception as e:
        logger.error(f"Error logging watering event: {e}", exc_info=True)
        return None

@with_connection
def get_watering_history(conn, start_time=None, end_time=None, limit=20):
    """
    Get watering event history.

    Args:
        conn: Database connection
        start_time (str, optional): ISO8601 start timestamp
        end_time (str, optional): ISO8601 end timestamp
        limit (int, optional): Maximum number of events to return

    Returns:
        list: List of watering events
    """
    try:
        # Set row factory for this connection
        original_row_factory = conn.row_factory
        conn.row_factory = dict_factory
        cursor = conn.cursor()

        query = '''
        SELECT id, timestamp, duration_sec, triggered_by, moisture_before, moisture_after
        FROM WateringEvents
        '''
        params = []
        where_clauses = []

        if start_time:
            where_clauses.append('timestamp >= ?')
            params.append(start_time)

        if end_time:
            where_clauses.append('timestamp <= ?')
            params.append(end_time)

        if where_clauses:
            query += ' WHERE ' + ' AND '.join(where_clauses)

        query += ' ORDER BY timestamp DESC LIMIT ?'
        params.append(limit)

        cursor.execute(query, params)
        results = cursor.fetchall()

        # Restore original row factory
        conn.row_factory = original_row_factory

        return results

    except sqlite3.Error as e:
        logger.error(f"Database error getting watering history: {e}")
        return []
    except Exception as e:
        logger.error(f"Error getting watering history: {e}", exc_info=True)
        return []

@with_connection
def add_notification(conn, component_id, severity, message, timestamp=None):
    """
    Add a notification to the database.

    Args:
        conn: Database connection
        component_id (str): ID of the component that triggered the notification
        severity (str): Severity level ('info', 'warning', 'error', 'critical')
        message (str): Notification message
        timestamp (datetime, optional): Timestamp for the notification (defaults to now)

    Returns:
        int: ID of the new notification, or None if failed
    """
    try:
        cursor = conn.cursor()

        # Use current time if timestamp not provided
        if timestamp is None:
            timestamp = datetime.now()

        # Convert timestamp to ISO format if it's a datetime object
        if isinstance(timestamp, datetime):
            timestamp = timestamp.isoformat()

        # Insert notification
        cursor.execute('''
        INSERT INTO Notifications (timestamp, component_id, severity, message, read, action_taken)
        VALUES (?, ?, ?, ?, 0, 0)
        ''', (timestamp, component_id, severity, message))

        notification_id = cursor.lastrowid
        conn.commit()

        logger.info(f"Added notification: {severity} - {message}")
        return notification_id

    except sqlite3.Error as e:
        logger.error(f"Database error adding notification: {e}")
        return None
    except Exception as e:
        logger.error(f"Error adding notification: {e}", exc_info=True)
        return None

@with_connection
def store_connection_status(conn, status_data):
    """
    Store connection status data in the database.

    Args:
        conn: Database connection
        status_data (dict): Connection status data

    Returns:
        int: ID of the new status record, or None if failed
    """
    try:
        cursor = conn.cursor()

        # Convert status data to JSON
        status_json = json.dumps(status_data)

        # Get timestamp from status data or use current time
        timestamp = status_data.get('timestamp', datetime.now().isoformat())

        # Insert status
        cursor.execute('''
        INSERT INTO ConnectionStatus (timestamp, status_data)
        VALUES (?, ?)
        ''', (timestamp, status_json))

        status_id = cursor.lastrowid
        conn.commit()

        logger.debug(f"Stored connection status snapshot (ID: {status_id})")
        return status_id

    except sqlite3.Error as e:
        logger.error(f"Database error storing connection status: {e}")
        return None
    except Exception as e:
        logger.error(f"Error storing connection status: {e}", exc_info=True)
        return None

def schedule_maintenance():
    """
    Schedule database maintenance tasks to run periodically.
    """
    def maintenance_loop():
        while True:
            try:
                # Wait until 3 AM
                now = datetime.now()
                target_time = now.replace(hour=3, minute=0, second=0, microsecond=0)
                if now >= target_time:
                    target_time = target_time + timedelta(days=1)

                sleep_seconds = (target_time - now).total_seconds()
                time.sleep(sleep_seconds)

                # Perform maintenance
                logger.info("Starting scheduled database maintenance")

                # Backup the database
                backup_database()

                # Prune old data
                prune_all_data()

                logger.info("Scheduled database maintenance completed")

            except Exception as e:
                logger.error(f"Error in database maintenance: {e}", exc_info=True)
                time.sleep(3600)  # Wait an hour and try again

    # Start the maintenance thread
    maintenance_thread = threading.Thread(target=maintenance_loop)
    maintenance_thread.daemon = True
    maintenance_thread.start()
    logger.info("Database maintenance scheduler started")

    return maintenance_thread

# Initialize the database when the module is imported
if __name__ != "__main__":
    init_db()

    # Schedule maintenance tasks
    _maintenance_thread = schedule_maintenance()
