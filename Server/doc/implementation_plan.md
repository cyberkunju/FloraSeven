# FloraSeven v1.0 - Implementation Plan

## Overview

This document outlines the detailed implementation plan for the FloraSeven v1.0 laptop server backend. The implementation is divided into several phases, each focusing on specific components of the system.

## Phase 1: Project Setup

### 1.1 Directory Structure

Create the following directory structure:

```
floraseven_server/
├── venv/                  # Virtual environment
├── images/                # Directory to store uploaded plant images
├── data/                  # Directory for database and logs
├── server.py              # Main Flask application
├── mqtt_client.py         # MQTT client implementation
├── database.py            # SQLite database functions
├── ai_service.py          # AI model integration
├── logic.py               # Business logic functions
├── config.py              # Configuration variables
├── requirements.txt       # Python dependencies
└── .env                   # Environment variables (optional)
```

### 1.2 Environment Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```

2. Install required dependencies:
   ```bash
   pip install flask flask-cors paho-mqtt tensorflow pillow python-dotenv
   pip freeze > requirements.txt
   ```

3. Install and configure Mosquitto MQTT broker:
   - Download and install from mosquitto.org
   - Ensure it's running on port 1883
   - Test with mosquitto_pub and mosquitto_sub

### 1.3 Configuration

Create `config.py` with the following settings:

- MQTT broker address and port
- MQTT topics
- Database file path
- Image storage directory
- API port
- AI model path
- Logging configuration

## Phase 2: Core Components Development

### 2.1 Database Module (database.py)

Implement the following functions:

1. `init_db()`: Initialize the SQLite database with the following schema:
   - SensorLog table:
     - timestamp (TEXT ISO8601 or INTEGER Unix Epoch, PRIMARY KEY or INDEXED)
     - node_id (TEXT - e.g., 'plantNode1', 'hubNode')
     - sensor_type (TEXT - e.g., 'moisture', 'temp_soil', 'light_lux', 'uv_plant', 'ec_raw', 'ph_water', 'uv_ambient')
     - value (REAL)
   - ImageLog table:
     - timestamp (TEXT ISO8601 or INTEGER Unix Epoch, PRIMARY KEY)
     - image_filename (TEXT - e.g., 'plant_image_20250415103005.jpg')
     - health_label (TEXT - e.g., 'Healthy', 'Wilted')
     - health_score (INTEGER - 0-100)
     - confidence (REAL - 0.0-1.0)
   - Thresholds table:
     - parameter_name (TEXT, PRIMARY KEY - e.g., 'moistureMin', 'moistureMax', 'tempSoilMin'...)
     - value (REAL)

2. `log_sensor_reading(timestamp, node_id, sensor_type, value)`: Insert a sensor reading into the SensorLog table

3. `log_image_analysis(timestamp, filename, health_label, health_score, confidence)`: Insert image analysis results into the ImageLog table

4. `get_latest_sensor_reading(node_id, sensor_type)`: Get the latest reading for a specific sensor

5. `get_latest_status_data()`: Get the latest readings for all sensors

6. `get_thresholds()`: Get all threshold values

7. `update_thresholds(thresholds_dict)`: Update threshold values

8. `get_latest_image_data()`: Get data for the most recent image analysis

### 2.2 MQTT Client Module (mqtt_client.py)

Implement the following:

1. MQTT client class with:
   - Connection to broker
   - Subscription to topics
   - Callback functions:
     - `on_connect`: Subscribe to topics when connected
     - `on_message`: Handle incoming messages
     - `on_disconnect`: Handle disconnections and reconnect
   - Command publishing function

2. Message handling for different topics:
   - Parse JSON payloads
   - Extract sensor readings
   - Log data to database
   - Trigger appropriate actions

3. Command publishing function:
   - Format command payloads
   - Publish to appropriate topics

4. Run the client in a separate thread

### 2.3 AI Service Module (ai_service.py)

Implement the following:

1. Model loading function:
   - Load the TensorFlow SavedModel from `FloraSeven_AI/models/model1_whole_plant_health/`
   - Load class indices from `FloraSeven_AI/models/model1_whole_plant_health_class_indices.json`

2. Image preprocessing function:
   - Load image using Pillow
   - Resize to required dimensions (224x224)
   - Normalize pixel values

3. Prediction function:
   - Preprocess image
   - Run inference using the model
   - Interpret results using class indices
   - Calculate confidence and health score
   - Return prediction results

4. Integration with `predict_visual_health.py` from the FloraSeven_AI module

### 2.4 Business Logic Module (logic.py)

Implement the following functions:

1. `calculate_condition_index(latest_data, thresholds)`:
   - Compare sensor readings against thresholds
   - Determine status for each parameter (Optimal, Warning, Critical)
   - Return condition index dictionary

2. `calculate_overall_health(condition_index, visual_health)`:
   - Combine condition index and visual health assessment
   - Apply rules to determine overall health status
   - Return overall health status and score

3. `generate_suggestions(condition_index, visual_health)`:
   - Apply rules to generate care suggestions
   - Return list of suggestions

### 2.5 Flask Application (server.py)

Implement the following:

1. Flask app initialization:
   - Create Flask app
   - Configure CORS
   - Initialize components (database, MQTT client, AI service)

2. API routes:
   - GET /api/v1/status:
     - Get latest sensor data
     - Get latest visual health assessment
     - Calculate condition index and overall health
     - Return comprehensive status response
   - GET /api/v1/image/latest:
     - Get latest image filename
     - Return image file
   - POST /api/v1/upload_image:
     - Receive and save uploaded image
     - Trigger AI analysis
     - Store results in database
     - Return success/failure response
   - GET /api/v1/settings/thresholds:
     - Get current thresholds from database
     - Return thresholds response
   - POST /api/v1/settings/thresholds:
     - Validate incoming thresholds
     - Update thresholds in database
     - Return success/failure response
   - POST /api/v1/command/water:
     - Validate water command
     - Publish command via MQTT
     - Return command acknowledgement

3. Error handling:
   - Implement try-except blocks
   - Return appropriate HTTP status codes
   - Log errors

4. Run the Flask app with:
   ```python
   if __name__ == "__main__":
       app.run(host="0.0.0.0", port=5000, debug=True)
   ```

## Phase 3: Testing & Integration

### 3.1 Component Testing

1. Database testing:
   - Test database initialization
   - Test CRUD operations
   - Verify data integrity

2. MQTT client testing:
   - Test connection to broker
   - Test subscription to topics
   - Test message handling
   - Test command publishing

3. AI service testing:
   - Test model loading
   - Test image preprocessing
   - Test prediction function
   - Verify prediction results

4. Business logic testing:
   - Test condition index calculation
   - Test overall health calculation
   - Test suggestion generation

5. API testing:
   - Test each endpoint with Postman/Insomnia
   - Verify response formats
   - Test error handling

### 3.2 Integration Testing

1. End-to-end testing:
   - Test data flow from MQTT to database to API
   - Test image upload and analysis flow
   - Test command flow from API to MQTT

2. Hardware integration testing:
   - Test with real Plant Node
   - Test with real Hub Node
   - Verify data reception and command execution

3. Flutter app integration testing:
   - Test app connection to server
   - Test data display in app
   - Test command sending from app

### 3.3 Performance Testing

1. Test system under load:
   - Simulate multiple sensor readings
   - Measure response times
   - Identify bottlenecks

2. Test reliability:
   - Run system for extended periods
   - Monitor for memory leaks
   - Test recovery from failures

## Phase 4: Documentation & Deployment

### 4.1 Code Documentation

1. Add docstrings to all functions
2. Add comments for complex logic
3. Create README.md with setup and usage instructions

### 4.2 User Documentation

1. Create setup guide
2. Create usage guide
3. Create troubleshooting guide

### 4.3 Deployment

1. Prepare deployment script
2. Create startup instructions
3. Test deployment on target laptop

## Timeline

- Phase 1 (Project Setup): 1 day
- Phase 2 (Core Components Development): 3-5 days
- Phase 3 (Testing & Integration): 2-3 days
- Phase 4 (Documentation & Deployment): 1-2 days

Total estimated time: 7-11 days
