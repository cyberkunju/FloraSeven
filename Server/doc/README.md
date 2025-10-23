# FloraSeven v1.0 - Documentation

## Overview

This folder contains comprehensive documentation for the FloraSeven v1.0 laptop server backend. FloraSeven is an intelligent plant care system that uses IoT sensors and AI-driven visual analysis to monitor and care for sensitive plants.

## Documentation Files

- [Project Overview](project_overview.md) - Overview of the FloraSeven project
- [Architecture](architecture.md) - System architecture and components
- [Implementation Plan](implementation_plan.md) - Detailed implementation plan
- [AI Integration](ai_integration.md) - AI model integration details
- [MQTT Protocol](mqtt_protocol.md) - MQTT protocol details
- [API Specification](api_specification.md) - API endpoints specification
- [Database Schema](database_schema.md) - Database schema design
- [Glossary](glossary.md) - Definitions of key terms and concepts

## System Components

The FloraSeven system consists of three main components:

1. **Hardware Nodes**:
   - Plant Node (ESP32 WROOM) - Collects sensor data from the plant
   - Hub Node (ESP32-CAM + R4 Minima) - Captures images and controls the water pump

2. **Laptop Server Backend**:
   - Receives sensor data via MQTT
   - Processes plant images with AI
   - Provides a REST API for the mobile app
   - Sends commands to hardware nodes

3. **Flutter Mobile App**:
   - Displays plant health status and sensor data
   - Allows user to control the system
   - Communicates with the server via REST API

## Implementation Status

This documentation represents the planning phase of the FloraSeven v1.0 laptop server backend. The implementation will follow the detailed plan outlined in these documents.

## Next Steps

1. Set up the project structure and environment
2. Implement the core components:
   - Database module
   - MQTT client
   - AI service
   - Business logic
   - Flask API
3. Test the system with hardware nodes
4. Deploy the server on the target laptop

## Contact

For questions or feedback about this documentation, please contact the project team.
