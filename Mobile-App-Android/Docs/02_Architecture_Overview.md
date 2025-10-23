# Architecture Overview

This document provides a comprehensive overview of the IoT Plant Monitoring and Watering System architecture, explaining how the different components interact with each other.

## System Architecture

The system follows a client-server architecture with three main components:

1. **Mobile Application (Client)** - Flutter-based mobile app
2. **Hardware Component (Server)** - ESP32-based system with sensors and actuators
3. **Demo Server** - Python-based server that simulates the hardware

![System Architecture Diagram](./images/system_architecture.png)

## Component Interaction

### Communication Flow

1. The ESP32 hardware (or demo server) exposes a RESTful API over HTTP
2. The mobile app discovers the server using mDNS (multicast DNS)
3. The mobile app communicates with the server to:
   - Retrieve plant status (moisture levels, system status)
   - Trigger watering actions
   - Configure auto-watering settings

### Data Flow

1. **Sensor Data Collection**:
   - Moisture sensors collect data from the soil
   - ESP32 processes and stores this data
   - Data is made available through the API

2. **Control Commands**:
   - User initiates commands through the mobile app
   - Commands are sent to the ESP32 via HTTP requests
   - ESP32 executes the commands (e.g., activating the water pump)

3. **Status Updates**:
   - ESP32 continuously updates its internal state
   - Mobile app polls for updates or receives push notifications
   - UI reflects the current system state

## Mobile Application Architecture

The mobile application follows the Provider pattern for state management and is structured as follows:

### Layers

1. **Presentation Layer** (UI)
   - Screens and widgets
   - User interaction handling

2. **Business Logic Layer**
   - Providers for state management
   - Services for business logic

3. **Data Layer**
   - Models for data representation
   - Repositories for data access

### Key Components

1. **Providers**
   - `PlantProvider` - Manages plant collection
   - `PlantStatusProvider` - Handles real-time plant status
   - `ServerDiscoveryProvider` - Manages server discovery
   - `ThemeProvider` - Handles app theme settings

2. **Services**
   - `ApiService` - Handles API communication
   - `NotificationService` - Manages notifications
   - `ServerDiscoveryService` - Discovers servers on the network

3. **Models**
   - `Plant` - Represents a plant with its settings
   - `PlantStatus` - Represents the current status of a plant
   - `ServerInfo` - Contains server connection information

## Hardware Architecture

### Components

1. **ESP32 Microcontroller**
   - Processes sensor data
   - Controls the water pump
   - Hosts the web server
   - Manages Wi-Fi connectivity

2. **Sensors**
   - Soil moisture sensor
   - Optional: temperature and humidity sensors

3. **Actuators**
   - Water pump (controlled via relay)
   - Optional: LED indicators

### Firmware Structure

The ESP32 firmware is organized into the following modules:

1. **Main Module** - System initialization and main loop
2. **Sensor Module** - Reading and processing sensor data
3. **Pump Control Module** - Managing the water pump
4. **Web Server Module** - Handling HTTP requests
5. **WiFi Module** - Managing network connectivity
6. **mDNS Module** - Advertising the service on the network

## Demo Server Architecture

The demo server is a Python-based application that simulates the hardware component for development and testing purposes.

### Components

1. **Flask Web Server** - Handles HTTP requests
2. **mDNS Service** - Advertises the server on the network
3. **Simulation Logic** - Simulates plant moisture levels and watering effects

### Endpoints

The demo server exposes the same API endpoints as the hardware component:

1. `GET /api/status` - Returns the current plant status
2. `POST /api/water` - Triggers watering
3. `POST /api/auto_watering` - Toggles auto-watering mode

## Security Considerations

1. **Local Network Only** - The system is designed to operate on a local network only
2. **No Sensitive Data** - The system does not collect or store sensitive user data
3. **Future Enhancements** - Plans for adding authentication and encryption

## Scalability

The current architecture supports:

1. **Multiple Plants** - The mobile app can manage multiple plants
2. **Multiple Servers** - The app can discover and connect to multiple ESP32 devices
3. **Future Expansion** - The modular design allows for adding new features and sensors
