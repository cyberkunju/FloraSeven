# FloraSeven v1.0 - Database Schema

## Overview

The FloraSeven laptop server backend uses SQLite for data storage. This document specifies the database schema, including tables, fields, and relationships.

## Database File

The SQLite database file is located at:
```
data/floraseven_data.db
```

## Tables

The database consists of three main tables:
1. SensorLog - Stores sensor readings
2. ImageLog - Stores image analysis results
3. Thresholds - Stores threshold settings

### SensorLog Table

The SensorLog table stores all sensor readings from both the Plant Node and Hub Node.

#### Schema

```sql
CREATE TABLE IF NOT EXISTS SensorLog (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    node_id TEXT NOT NULL,
    sensor_type TEXT NOT NULL,
    value REAL NOT NULL,
    UNIQUE(timestamp, node_id, sensor_type)
);

-- Index for faster queries on timestamp
CREATE INDEX IF NOT EXISTS idx_sensorlog_timestamp ON SensorLog(timestamp);
-- Index for faster queries on node_id and sensor_type
CREATE INDEX IF NOT EXISTS idx_sensorlog_node_sensor ON SensorLog(node_id, sensor_type);
```

#### Fields

- `id`: Unique identifier (auto-incrementing integer)
- `timestamp`: ISO8601 timestamp of the reading (TEXT)
- `node_id`: Identifier for the node (e.g., "plantNode1", "hubNode")
- `sensor_type`: Type of sensor (e.g., "moisture", "temp_soil", "light_lux", "uv_plant", "ec_raw", "ph_water", "uv_ambient")
- `value`: Sensor reading value (REAL)

#### Example Data

| id | timestamp | node_id | sensor_type | value |
|----|-----------|---------|-------------|-------|
| 1 | 2025-04-15T10:30:05Z | plantNode1 | moisture | 62.1 |
| 2 | 2025-04-15T10:30:05Z | plantNode1 | temp_soil | 23.5 |
| 3 | 2025-04-15T10:30:05Z | plantNode1 | light_lux | 18000 |
| 4 | 2025-04-15T10:30:05Z | plantNode1 | ec_raw | 1150 |
| 5 | 2025-04-15T10:30:10Z | hubNode | ph_water | 6.7 |
| 6 | 2025-04-15T10:30:10Z | hubNode | uv_ambient | 0.9 |
| 7 | 2025-04-15T10:30:10Z | hubNode | pump_state | 0 |

### ImageLog Table

The ImageLog table stores information about plant images and their analysis results.

#### Schema

```sql
CREATE TABLE IF NOT EXISTS ImageLog (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    image_filename TEXT NOT NULL,
    health_label TEXT NOT NULL,
    health_score INTEGER NOT NULL,
    confidence REAL NOT NULL,
    UNIQUE(image_filename)
);

-- Index for faster queries on timestamp
CREATE INDEX IF NOT EXISTS idx_imagelog_timestamp ON ImageLog(timestamp);
```

#### Fields

- `id`: Unique identifier (auto-incrementing integer)
- `timestamp`: ISO8601 timestamp of the image capture (TEXT)
- `image_filename`: Name of the image file (TEXT)
- `health_label`: Health classification from AI analysis (e.g., "healthy", "wilting")
- `health_score`: Health score from 0-100 (INTEGER)
- `confidence`: Confidence of the classification from 0-1 (REAL)

#### Example Data

| id | timestamp | image_filename | health_label | health_score | confidence |
|----|-----------|----------------|--------------|--------------|------------|
| 1 | 2025-04-15T10:35:00Z | plant_image_20250415103500.jpg | healthy | 85 | 0.85 |
| 2 | 2025-04-15T11:35:00Z | plant_image_20250415113500.jpg | healthy | 82 | 0.82 |
| 3 | 2025-04-15T12:35:00Z | plant_image_20250415123500.jpg | wilting | 45 | 0.78 |

### Thresholds Table

The Thresholds table stores the minimum and maximum acceptable values for various parameters.

#### Schema

```sql
CREATE TABLE IF NOT EXISTS Thresholds (
    parameter_name TEXT PRIMARY KEY,
    min_value REAL NOT NULL,
    max_value REAL NOT NULL
);
```

#### Fields

- `parameter_name`: Name of the parameter (TEXT, PRIMARY KEY)
- `min_value`: Minimum acceptable value (REAL)
- `max_value`: Maximum acceptable value (REAL)

#### Example Data

| parameter_name | min_value | max_value |
|----------------|-----------|-----------|
| moisture | 40.0 | 70.0 |
| temp_soil | 18.0 | 28.0 |
| light_lux | 5000.0 | 30000.0 |
| ph_water | 6.0 | 7.5 |
| uv_ambient | 0.0 | 2.0 |
| ec_raw | 800.0 | 1500.0 |

## Database Initialization

The database is initialized with the following SQL script:

```sql
-- Create SensorLog table
CREATE TABLE IF NOT EXISTS SensorLog (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    node_id TEXT NOT NULL,
    sensor_type TEXT NOT NULL,
    value REAL NOT NULL,
    UNIQUE(timestamp, node_id, sensor_type)
);

-- Create indices for SensorLog
CREATE INDEX IF NOT EXISTS idx_sensorlog_timestamp ON SensorLog(timestamp);
CREATE INDEX IF NOT EXISTS idx_sensorlog_node_sensor ON SensorLog(node_id, sensor_type);

-- Create ImageLog table
CREATE TABLE IF NOT EXISTS ImageLog (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    image_filename TEXT NOT NULL,
    health_label TEXT NOT NULL,
    health_score INTEGER NOT NULL,
    confidence REAL NOT NULL,
    UNIQUE(image_filename)
);

-- Create index for ImageLog
CREATE INDEX IF NOT EXISTS idx_imagelog_timestamp ON ImageLog(timestamp);

-- Create Thresholds table
CREATE TABLE IF NOT EXISTS Thresholds (
    parameter_name TEXT PRIMARY KEY,
    min_value REAL NOT NULL,
    max_value REAL NOT NULL
);

-- Insert default thresholds
INSERT OR IGNORE INTO Thresholds (parameter_name, min_value, max_value) VALUES
    ('moisture', 40.0, 70.0),
    ('temp_soil', 18.0, 28.0),
    ('light_lux', 5000.0, 30000.0),
    ('ph_water', 6.0, 7.5),
    ('uv_ambient', 0.0, 2.0),
    ('ec_raw', 800.0, 1500.0);
```

## Database Functions

The `database.py` module provides the following functions for interacting with the database:

### Initialization

```python
def init_db():
    """Initialize the SQLite database with the required schema."""
    # Implementation details...
```

### Sensor Data

```python
def log_sensor_reading(timestamp, node_id, sensor_type, value):
    """
    Log a sensor reading to the database.

    Args:
        timestamp (str): ISO8601 timestamp
        node_id (str): Identifier for the node
        sensor_type (str): Type of sensor
        value (float): Sensor reading value

    Returns:
        bool: True if successful, False otherwise
    """
    # Implementation details...

def get_latest_sensor_reading(node_id, sensor_type):
    """
    Get the latest reading for a specific sensor.

    Args:
        node_id (str): Identifier for the node
        sensor_type (str): Type of sensor

    Returns:
        dict: Sensor reading data or None if not found
    """
    # Implementation details...

def get_latest_status_data():
    """
    Get the latest readings for all sensors.

    Returns:
        dict: Dictionary with latest sensor data
    """
    # Implementation details...

def get_sensor_history(node_id, sensor_type, start_time=None, end_time=None, limit=100):
    """
    Get historical sensor readings.

    Args:
        node_id (str): Identifier for the node
        sensor_type (str): Type of sensor
        start_time (str, optional): ISO8601 start timestamp
        end_time (str, optional): ISO8601 end timestamp
        limit (int, optional): Maximum number of readings to return

    Returns:
        list: List of sensor readings
    """
    # Implementation details...
```

### Image Data

```python
def log_image_analysis(timestamp, image_filename, health_label, health_score, confidence):
    """
    Log image analysis results to the database.

    Args:
        timestamp (str): ISO8601 timestamp
        image_filename (str): Name of the image file
        health_label (str): Health classification
        health_score (int): Health score (0-100)
        confidence (float): Confidence of the classification (0-1)

    Returns:
        bool: True if successful, False otherwise
    """
    # Implementation details...

def get_latest_image_data():
    """
    Get data for the most recent image analysis.

    Returns:
        dict: Image analysis data or None if not found
    """
    # Implementation details...

def get_image_history(start_time=None, end_time=None, limit=20):
    """
    Get historical image analysis results.

    Args:
        start_time (str, optional): ISO8601 start timestamp
        end_time (str, optional): ISO8601 end timestamp
        limit (int, optional): Maximum number of results to return

    Returns:
        list: List of image analysis results
    """
    # Implementation details...
```

### Thresholds

```python
def get_thresholds():
    """
    Get all threshold values.

    Returns:
        dict: Dictionary with parameter thresholds
    """
    # Implementation details...

def update_thresholds(thresholds_dict):
    """
    Update threshold values.

    Args:
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
    # Implementation details...
```

## Data Retention

For the v1.0 prototype, there is no automatic data pruning or archiving. All data is retained indefinitely in the SQLite database.

Future versions may implement:
- Automatic pruning of old sensor data
- Data aggregation for historical analysis
- Data export functionality

## Backup

The SQLite database file should be backed up regularly to prevent data loss. A simple file copy is sufficient for backup purposes.

Example backup script:
```bash
#!/bin/bash
# Backup the FloraSeven database
TIMESTAMP=$(date +%Y%m%d%H%M%S)
cp data/floraseven_data.db data/backups/floraseven_data_$TIMESTAMP.db
```
