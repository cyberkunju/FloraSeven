# FloraSeven Architecture

This document describes the architecture of the FloraSeven system, including the hardware components, server components, and mobile application.

## System Architecture Overview

The FloraSeven system follows a three-tier architecture:

1. **Hardware Tier**: Physical devices and sensors that collect data and control actuators
2. **Server Tier**: Central processing and storage system that manages data and business logic
3. **Client Tier**: Mobile application that provides the user interface

![FloraSeven Architecture](images/architecture_diagram.png)

## Hardware Architecture

The hardware tier consists of two main nodes:

### Plant Node (ESP32 WROOM)

The Plant Node is responsible for collecting data from sensors directly in contact with the plant and soil.

**Components:**
- ESP32 WROOM microcontroller
- DS18B20 temperature sensor
- BH1750 light sensor
- Capacitive Soil Moisture V2.0 sensor
- DIY EC probe with LM358 amplifier
- 18650 battery with power management

**Responsibilities:**
- Collect sensor data (moisture, temperature, light, EC)
- Send data to the server via MQTT
- Enter deep sleep mode to conserve battery
- Wake up periodically to take readings

**Technical Details:**
- Uses I2C for BH1750 light sensor
- Uses OneWire for DS18B20 temperature sensor
- Uses ADC for moisture and EC sensors
- Uses PWM for EC probe excitation
- Connects to WiFi and MQTT broker
- Deep sleep between readings (30 seconds by default)

### Hub Node (ESP32-CAM + Arduino R4 Minima)

The Hub Node is responsible for capturing images of the plant and collecting additional environmental data.

**Components:**
- ESP32-CAM microcontroller with camera
- Arduino R4 Minima microcontroller
- ML8511 UV sensor
- Crowtail pH sensor
- Mini submersible pump
- 18650 battery with power management

**Responsibilities:**
- Capture plant images
- Collect sensor data (pH, UV)
- Control water pump
- Send data and images to the server
- Receive commands from the server

**Technical Details:**
- ESP32-CAM acts as I2C master
- Arduino R4 Minima acts as I2C slave
- ESP32-CAM handles WiFi and MQTT communication
- ESP32-CAM captures and uploads images via HTTP
- Arduino R4 Minima controls the pump and reads sensors
- Communication between ESP32-CAM and R4 Minima via I2C

## Server Architecture

The server tier is the central processing and storage system for the FloraSeven platform.

### Components

**Core Services:**
- MQTT Broker: Handles communication with hardware nodes
- Flask Web Server: Provides REST API for mobile application
- SQLite Database: Stores sensor data, settings, and image metadata
- AI Service: Analyzes plant images for health assessment

**Supporting Services:**
- Logic Service: Implements business logic and data processing
- Monitoring Service: Monitors sensor data and triggers alerts
- Visualization Service: Generates charts and visualizations
- Authentication Service: Handles user authentication

### Data Flow

1. **Sensor Data Flow:**
   - Hardware nodes publish sensor data to MQTT topics
   - MQTT client in server receives data
   - Logic service processes and validates data
   - Database service stores data
   - Monitoring service checks thresholds and triggers actions

2. **Image Data Flow:**
   - Hub Node captures image
   - Hub Node uploads image via HTTP POST
   - Server stores image
   - AI service analyzes image
   - Database stores analysis results

3. **Command Flow:**
   - Mobile app sends command via REST API
   - Server processes command
   - Server publishes command to MQTT topic
   - Hardware node receives and executes command

### Database Schema

The server uses SQLite with the following main tables:

- **sensor_data**: Stores all sensor readings with timestamps
- **thresholds**: Stores threshold settings for each sensor
- **images**: Stores metadata for captured images
- **image_analysis**: Stores results of AI analysis
- **system_status**: Stores overall system status
- **users**: Stores user authentication information

## Mobile Application Architecture

The mobile application follows a clean architecture pattern with separation of concerns.

### Layers

1. **Presentation Layer**
   - Screens: UI components and layouts
   - Widgets: Reusable UI components
   - View Models: Manage UI state and business logic

2. **Application Layer**
   - Providers: State management using Riverpod
   - Use Cases: Implement application-specific business rules

3. **Domain Layer**
   - Models: Business entities and value objects
   - Repositories: Abstract data access interfaces

4. **Data Layer**
   - Services: Implement data access and external APIs
   - Repositories: Concrete implementations of domain repositories
   - Data Sources: Local and remote data sources

### State Management

The application uses Riverpod for state management with the following key providers:

- **AuthProvider**: Manages authentication state
- **PlantDataProvider**: Manages plant data state
- **ThresholdsProvider**: Manages threshold settings
- **ConnectionProvider**: Manages server connection state
- **NotificationProvider**: Manages notification state

### Navigation

The application uses Flutter's built-in navigation system with the following main routes:

- `/`: Splash screen
- `/login`: Login screen
- `/dashboard`: Main dashboard screen
- `/plant_detail`: Detailed plant view
- `/settings`: Settings screen

## Communication Protocols

### MQTT Protocol

MQTT is used for communication between hardware nodes and the server.

**Topics:**
- `floraSeven/plant/node1/data`: Plant Node sensor data
- `floraSeven/hub/status`: Hub Node status
- `floraSeven/hub/cam/image_status`: Image metadata
- `floraSeven/command/hub/pump`: Pump control commands
- `floraSeven/command/hub/captureImage`: Image capture commands
- `floraSeven/command/plant/node1/readNow`: Force read commands

### REST API

REST API is used for communication between the mobile application and the server.

**Endpoints:**
- `/api/v1/status`: Get system status
- `/api/v1/image/latest`: Get latest image
- `/api/v1/upload_image`: Upload image
- `/api/v1/settings/thresholds`: Get/update thresholds
- `/api/v1/command/water`: Send water command
- `/api/v1/command/capture_image`: Send capture image command
- `/api/v1/command/read_now`: Send read now command
- `/api/v1/login`: User login
- `/api/v1/logout`: User logout
- `/api/v1/visualization/*`: Get visualization data

### I2C Protocol

I2C is used for communication between the ESP32-CAM and Arduino R4 Minima in the Hub Node.

**Commands:**
- `0x00`: Turn pump off
- `0x01`: Turn pump on
- `0x10`: Request pH data
- `0x11`: Request UV data

## Security Considerations

- Authentication is required for all API endpoints
- MQTT communication uses client IDs for basic authentication
- Passwords are stored with hashing
- API endpoints validate input data
- Error handling prevents information disclosure

## Deployment Architecture

The FloraSeven system is designed for local deployment with the following components:

1. **Hardware Nodes**: Deployed near the plant being monitored
2. **Server**: Deployed on a laptop or desktop computer
3. **Mobile Application**: Deployed on Android devices

All components must be on the same local network for communication.

## Scalability and Performance

The current architecture has the following scalability and performance characteristics:

- **Hardware Nodes**: Limited to one Plant Node and one Hub Node per system
- **Server**: Can handle multiple hardware nodes but optimized for single-plant monitoring
- **Database**: SQLite is suitable for single-user, single-plant scenarios
- **Mobile Application**: Designed for single-user access

Future versions may enhance scalability through cloud integration and multi-user support.
