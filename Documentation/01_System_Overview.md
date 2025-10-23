# FloraSeven System Overview

FloraSeven is a comprehensive smart plant monitoring system designed to help users maintain optimal growing conditions for their plants. The system combines hardware sensors, a central server, and a mobile application to provide real-time monitoring and control capabilities.

## System Components

The FloraSeven system consists of three main components:

1. **Hardware Components**
   - Plant Node (ESP32 WROOM)
   - Hub Node (ESP32-CAM with Arduino R4 Minima)
   - Sensors (moisture, temperature, light, UV, pH, EC)
   - Actuators (water pump)

2. **Server Components**
   - MQTT Broker
   - REST API Server
   - Database
   - AI Image Analysis Service
   - Visualization Service

3. **Mobile Application**
   - Flutter-based Android application
   - User interface for monitoring and control
   - Plant management features
   - Visualization of sensor data

## Key Features

### Sensor Monitoring
- Soil moisture monitoring
- Soil temperature monitoring
- Light level monitoring
- UV level monitoring
- pH level monitoring
- Electrical conductivity (EC) monitoring

### Automated Control
- Automatic watering based on moisture thresholds
- Manual watering control
- Configurable thresholds for all sensors

### Plant Health Analysis
- Visual plant health analysis using AI
- Sensor condition index
- Historical data visualization
- Trend analysis

### User Interface
- Dashboard with current plant status
- Detailed plant view with all sensor readings
- Settings for configuring thresholds and system behavior
- Plant collection management

## System Architecture

The FloraSeven system follows a distributed architecture with the following data flow:

1. **Sensor Data Collection**
   - Plant Node collects soil moisture, temperature, light, and EC data
   - Hub Node collects pH and UV data
   - Both nodes send data to the server via MQTT

2. **Data Processing**
   - Server processes incoming sensor data
   - Server stores data in the database
   - Server analyzes plant images using AI

3. **User Interaction**
   - Mobile app communicates with the server via REST API
   - User views sensor data and plant health information
   - User controls watering and configures thresholds

4. **Automated Actions**
   - Server monitors sensor data against thresholds
   - Server triggers automated watering when needed
   - Server sends notifications to the mobile app

## Technical Specifications

### Hardware
- ESP32 WROOM for Plant Node
- ESP32-CAM for Hub Node camera
- Arduino R4 Minima for Hub Node control
- DS18B20 temperature sensor
- BH1750 light sensor
- ML8511 UV sensor
- Capacitive Soil Moisture V2.0 sensor
- Crowtail pH sensor
- DIY EC probe with LM358 amplifier
- 3-6V mini submersible pump

### Software
- ESP32 firmware in C++
- Arduino R4 Minima firmware in C++
- Server in Python with Flask
- Mobile app in Flutter/Dart
- TensorFlow for AI image classification (binary healthy/wilted)

### Communication
- MQTT for device-to-server communication
- REST API for app-to-server communication
- I²C for internal Hub Node communication

### Power
- 18650 batteries for Plant Node and Hub Node
- 1-3 day battery life
- USB connection for firmware updates

## System Limitations

- Battery life limited to 1-3 days
- Requires WiFi connectivity
- Limited to Android mobile devices
- Requires laptop server for full functionality
- No cloud backup or synchronization
- Single plant monitoring per system

## Future Enhancements

- Automatic plant identification
- User accounts and cloud services
- Advanced analytics and recommendations
- Complex notification system
- Scheduling features
- Additional actuators (fans, lights)
- Offline mode
- Bluetooth setup
- iOS support

For more detailed information about each component, please refer to the respective documentation sections.
