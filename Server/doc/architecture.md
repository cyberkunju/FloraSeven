# FloraSeven v1.0 - System Architecture

## Overview

The FloraSeven system follows a distributed architecture with three main components:
1. Hardware nodes (Plant Node and Hub Node)
2. Laptop server backend
3. Flutter mobile app

This document focuses on the architecture of the laptop server backend, which serves as the central coordination point for the system.

## Laptop Server Backend Architecture

The laptop server backend follows a modular architecture with several key components:

```
┌─────────────────────────────────────────────────────────────────┐
│                     Laptop Server Backend                        │
│                                                                 │
│  ┌───────────┐    ┌───────────┐    ┌───────────┐    ┌────────┐  │
│  │   Flask   │    │   MQTT    │    │    AI     │    │Database│  │
│  │   API     │◄──►│  Client   │◄──►│  Service  │◄──►│ (SQLite)│  │
│  └───────────┘    └───────────┘    └───────────┘    └────────┘  │
│        ▲                 ▲               ▲               ▲      │
│        │                 │               │               │      │
│        └────────────────┐│┌─────────────┘               │      │
│                         ││                              │      │
│                     ┌───▼▼───┐                          │      │
│                     │Business│                          │      │
│                     │ Logic  │◄─────────────────────────┘      │
│                     └────────┘                                 │
└─────────────────────────────────────────────────────────────────┘
        ▲                 ▲                      ▲
        │                 │                      │
┌───────▼────────┐ ┌─────▼───────┐      ┌───────▼────────┐
│  Flutter App   │ │  Plant Node  │      │   Hub Node     │
│  (REST API)    │ │   (MQTT)     │      │ (MQTT & HTTP)  │
└────────────────┘ └─────────────┘      └────────────────┘
```

### Core Components

#### 1. Flask API (server.py)

The Flask API provides HTTP endpoints for the Flutter mobile app to interact with the system. It:
- Handles incoming HTTP requests
- Validates request data
- Calls appropriate business logic functions
- Returns formatted responses
- Serves static files (images)

Key endpoints include:
- GET /api/v1/status - Get latest system status
- GET /api/v1/image/latest - Get the latest plant image
- POST /api/v1/upload_image - Receive uploaded images from Hub Node
- GET /api/v1/settings/thresholds - Get current thresholds
- POST /api/v1/settings/thresholds - Update thresholds
- POST /api/v1/command/water - Send water pump command

#### 2. MQTT Client (mqtt_client.py)

The MQTT client handles communication with the hardware nodes via the MQTT protocol. It:
- Connects to the Mosquitto broker running on the laptop
- Subscribes to topics for receiving sensor data
- Publishes commands to hardware nodes
- Parses incoming JSON messages
- Updates the database with new sensor readings

Key topics include:
- floraSeven/plant/node1/data - Plant Node sensor readings
- floraSeven/hub/status - Hub Node status/sensor readings
- floraSeven/hub/cam/image_status - Image upload notifications
- floraSeven/command/hub/pump - Water pump control commands
- floraSeven/command/hub/captureImage - Image capture commands

#### 3. AI Service (ai_service.py)

The AI service handles the visual analysis of plant images. It:
- Loads the TensorFlow model
- Preprocesses images for analysis
- Runs inference to assess plant health
- Returns health labels and confidence scores

The AI model is a binary classifier that determines if a plant is "Healthy" or "Wilted".

#### 4. Database Module (database.py)

The database module handles data persistence using SQLite. It:
- Initializes the database schema
- Provides functions for CRUD operations
- Logs sensor readings and image analysis results
- Stores and retrieves threshold settings

Key tables include:
- SensorLog - Stores sensor readings with timestamps
- ImageLog - Stores image analysis results
- Thresholds - Stores threshold settings for various parameters

#### 5. Business Logic (logic.py)

The business logic module contains the core application logic. It:
- Calculates the Condition Index based on sensor readings and thresholds
- Determines Overall Health based on sensor data and visual analysis
- Generates suggestions for plant care
- Coordinates between other components

##### Health Calculation Logic

**Condition Index Calculation**:
- For each sensor reading (moisture, temperature, light, etc.):
  - Compare the current value against the min/max thresholds
  - Assign a status: "optimal" if within thresholds, "warning" if near thresholds (±10%), "critical" if outside thresholds
  - Store the status, current value, and thresholds in the condition index

**Overall Health Calculation**:
- Combines the Condition Index and Visual Health assessment using the following rules:
  - If any sensor has a "critical" status OR visual health label is "wilted", Overall Status = "critical"
  - If any sensor has a "warning" status OR visual health score < 70, Overall Status = "needs_attention"
  - Otherwise, Overall Status = "healthy"
- Overall Health Score calculation:
  - 60% weight from Visual Health score
  - 40% weight from average of normalized sensor scores
  - Sensor scores are normalized to 0-100 scale based on distance from optimal range

**Suggestion Generation**:
- Based on specific conditions in the Condition Index and Visual Health
- Examples:
  - If moisture is "critical" (low) and visual health is "wilted", suggest "Water plant immediately"
  - If light is "warning" (low), suggest "Consider moving plant to a brighter location"
  - If all parameters are optimal, suggest "Plant is healthy, maintain current care routine"

## Communication Flow

1. **Sensor Data Flow**:
   - Hardware nodes publish sensor data to MQTT topics
   - MQTT client receives data and parses JSON
   - Data is stored in the SQLite database
   - Business logic calculates health indices
   - Flutter app requests latest status via REST API

2. **Image Analysis Flow**:
   - Hub Node captures image and uploads via HTTP POST
   - Flask API receives image and saves to disk
   - AI service analyzes image and returns health assessment
   - Results are stored in the database
   - Flutter app requests latest image and analysis via REST API

3. **Command Flow**:
   - Flutter app sends command via REST API
   - Flask API validates command
   - MQTT client publishes command to appropriate topic
   - Hardware node receives command and executes action

## Dependencies

- **Python 3.9/3.10**: Base programming language
- **Flask**: Web framework for REST API
- **Flask-CORS**: Cross-origin resource sharing support
- **Paho-MQTT**: MQTT client library
- **TensorFlow**: AI model runtime
- **SQLite**: Embedded database
- **Pillow**: Image processing
- **Mosquitto**: MQTT broker (runs as a separate process)

## Deployment

The laptop server backend runs locally on a development laptop with:
- Mosquitto MQTT broker running on port 1883
- Flask server running on port 5000
- SQLite database file stored locally
- Images stored in a local directory

All components run within a single Python process, with the MQTT client running in a separate thread.
