# FloraSeven Server

FloraSeven is an intelligent plant care system that uses IoT sensors and AI-driven visual analysis to monitor and care for sensitive plants. This repository contains the server backend for the FloraSeven v1.0 prototype.

## System Overview

The FloraSeven system consists of three main components:

1. **Hardware Nodes**:
   - Plant Node (ESP32 WROOM) - Collects sensor data from the plant
   - Hub Node (ESP32-CAM + R4 Minima) - Captures images and controls the water pump

2. **Laptop Server Backend** (this repository):
   - Receives sensor data via MQTT
   - Processes plant images with AI
   - Provides a REST API for the mobile app
   - Sends commands to hardware nodes

3. **Flutter Mobile App**:
   - Displays plant health status and sensor data
   - Allows user to control the system
   - Communicates with the server via REST API

## Prerequisites

- Python 3.9 or 3.10
- Mosquitto MQTT broker
- TensorFlow model (provided in FloraSeven_AI/models)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/floraseven-server.git
   cd floraseven-server
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Install and start Mosquitto MQTT broker:
   - Download from [mosquitto.org](https://mosquitto.org/download/)
   - Start the broker:
     ```
     mosquitto -v
     ```

## Configuration

Configuration settings are stored in `config.py` and can be overridden using environment variables or a `.env` file.

Key configuration options:
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 5000)
- `MQTT_BROKER`: MQTT broker address (default: localhost)
- `MQTT_PORT`: MQTT broker port (default: 1883)

## Running the Server

Start the server:
```
python server.py
```

The server will:
1. Initialize the SQLite database
2. Connect to the MQTT broker
3. Start the Flask web server
4. Begin listening for sensor data and API requests

## API Endpoints

The server provides the following REST API endpoints:

- `GET /api/v1/status` - Get the latest system status
- `GET /api/v1/image/latest` - Get the latest plant image
- `POST /api/v1/upload_image` - Upload a plant image for analysis
- `GET /api/v1/settings/thresholds` - Get current thresholds
- `POST /api/v1/settings/thresholds` - Update thresholds
- `POST /api/v1/command/water` - Send water pump command
- `POST /api/v1/command/capture_image` - Send image capture command
- `POST /api/v1/command/read_now` - Send force reading command

See the [API documentation](doc/api_specification.md) for details.

## Testing

### MQTT Simulation

To test the server with simulated sensor data:
```
python test_mqtt_simulation.py
```

This script will publish simulated Plant Node and Hub Node data to the MQTT broker.

### API Testing

To test the API endpoints:
```
python test_api.py
```

This script will send requests to all API endpoints and verify the responses.

## Project Structure

- `server.py` - Main Flask application
- `mqtt_client.py` - MQTT client for communication with hardware nodes
- `database.py` - SQLite database functions
- `ai_service.py` - AI model integration
- `logic.py` - Business logic functions
- `config.py` - Configuration variables
- `images/` - Directory for uploaded plant images
- `data/` - Directory for database and logs
- `FloraSeven_AI/` - AI model and prediction code
- `doc/` - Documentation

## Documentation

Detailed documentation is available in the `doc/` directory:

- [Project Overview](doc/project_overview.md)
- [Architecture](doc/architecture.md)
- [Implementation Plan](doc/implementation_plan.md)
- [AI Integration](doc/ai_integration.md)
- [MQTT Protocol](doc/mqtt_protocol.md)
- [API Specification](doc/api_specification.md)
- [Database Schema](doc/database_schema.md)
- [Glossary](doc/glossary.md)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
