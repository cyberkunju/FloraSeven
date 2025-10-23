# FloraSeven v1.0 - Project Overview

## Introduction

FloraSeven is an intelligent plant care system that uses IoT sensors and AI-driven visual analysis to monitor and care for sensitive plants. The system consists of hardware nodes (Plant Node and Hub Node) that collect sensor data and capture images, a laptop server backend that processes the data and runs AI analysis, and a Flutter mobile app for user interaction.

This document provides an overview of the FloraSeven v1.0 prototype, focusing on the laptop server backend component.

## System Components

### Hardware Nodes

1. **Plant Node (ESP32 WROOM)**
   - Collects sensor data including:
     - Soil moisture
     - Soil temperature
     - Light levels (lux)
     - UV levels at plant
     - Electrical conductivity (EC) raw readings
   - Transmits data to the laptop server via MQTT

2. **Hub Node (ESP32-CAM + R4 Minima)**
   - Equipped with a camera for capturing plant images
   - Collects additional sensor data:
     - Water pH
     - Ambient UV levels
   - Controls the water pump
   - Transmits data to the laptop server via MQTT
   - Uploads images to the laptop server via HTTP

### Laptop Server Backend

The laptop server backend is the central coordination point for the FloraSeven system. It:

- Receives real-time sensor data from hardware nodes via MQTT
- Receives plant images from the Hub Node via HTTP
- Processes incoming data and stores it in a SQLite database
- Runs a TensorFlow model to assess visual plant health from images
- Calculates plant health indicators based on sensor readings and AI analysis
- Provides a REST API for the Flutter mobile app
- Relays commands from the app to the hardware nodes via MQTT

### Flutter Mobile App

The Flutter mobile app provides the user interface for the FloraSeven system. It:

- Displays plant health status, sensor readings, and images
- Allows users to set thresholds for various parameters
- Enables manual control of the water pump
- Communicates with the laptop server via REST API

## Data Flow

1. Hardware nodes collect sensor data and transmit it to the laptop server via MQTT
2. Hub Node captures images and uploads them to the laptop server via HTTP
3. Laptop server processes the data, runs AI analysis, and stores results in the database
4. Flutter app requests data from the laptop server via REST API
5. User sends commands via the app, which are relayed to hardware nodes via MQTT

## Project Scope

The FloraSeven v1.0 prototype is designed to run locally on a development laptop within the same Wi-Fi network as the hardware nodes and mobile app. It simulates the core functions of a future cloud backend.

The prototype focuses on:
- Reliable data collection and storage
- Accurate plant health assessment
- Responsive user interface
- Basic automation of plant care tasks

Future versions may include cloud integration, support for multiple plants, advanced AI features, and more sophisticated automation.
