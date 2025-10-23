# FloraSeven v1.0 - Glossary

This document defines key terms and concepts used throughout the FloraSeven documentation.

## Hardware Terms

### Plant Node
An ESP32 WROOM-based device that collects sensor data from the plant, including soil moisture, soil temperature, light levels, and electrical conductivity. It communicates with the laptop server via MQTT.

### Hub Node
An ESP32-CAM and R4 Minima-based device that captures plant images, measures water pH and ambient UV levels, and controls the water pump. It communicates with the laptop server via MQTT and HTTP.

### Sensors
- **Soil Moisture Sensor**: Measures the volumetric water content in soil (0-100%)
- **Soil Temperature Sensor**: Measures the temperature of the soil in Celsius
- **Light Sensor**: Measures ambient light levels in lux
- **UV Sensor**: Measures ultraviolet light levels
- **EC Sensor**: Measures electrical conductivity, which correlates with nutrient levels
- **pH Sensor**: Measures the acidity/alkalinity of water

## Software Terms

### MQTT
Message Queuing Telemetry Transport, a lightweight messaging protocol for IoT devices. Used for communication between the hardware nodes and the laptop server.

### MQTT Broker
A server that receives all messages from clients and routes them to the appropriate destination clients. In FloraSeven, Mosquitto is used as the MQTT broker.

### MQTT Topic
A string that the broker uses to filter messages for each connected client. FloraSeven uses a hierarchical topic structure (e.g., `floraSeven/plant/node1/data`).

### REST API
Representational State Transfer Application Programming Interface. A set of HTTP endpoints that the Flutter mobile app uses to communicate with the laptop server.

### Flask
A lightweight Python web framework used to implement the REST API in the FloraSeven server backend.

### SQLite
A file-based relational database used to store sensor readings, image analysis results, and threshold settings.

### TensorFlow
An open-source machine learning framework used for the plant health analysis model.

## Plant Health Terms

### Condition Index
A measure of plant health based on sensor readings compared to defined thresholds. Each parameter (moisture, temperature, etc.) is assigned a status of "optimal", "warning", or "critical".

### Visual Health
An assessment of plant health based on AI analysis of plant images. Includes a health label ("healthy" or "wilted"), a confidence score, and a health score (0-100).

### Overall Health
A comprehensive assessment of plant health that combines the Condition Index and Visual Health. Includes a status ("healthy", "needs_attention", or "critical"), a score (0-100), and suggestions for care.

### Health Score
A numerical value from 0 to 100 representing the health of the plant, with higher values indicating better health.

### Thresholds
Minimum and maximum acceptable values for various parameters (moisture, temperature, etc.). Used to determine the status of each parameter in the Condition Index.

## Data Terms

### Sensor Reading
A single measurement from a sensor, including the timestamp, node ID, sensor type, and value.

### Image Analysis
The result of AI processing on a plant image, including the health label, health score, and confidence.

### Timestamp
A string representing a specific point in time, formatted according to ISO 8601 (e.g., "2025-04-15T10:30:05Z").

## Communication Terms

### Command
A message sent from the laptop server to a hardware node to perform an action, such as activating the water pump or capturing an image.

### Status
Information about the current state of the system, including sensor readings, thresholds, visual health assessment, condition index, and overall health.

### Suggestion
A recommendation for plant care based on the current condition index and visual health assessment.
