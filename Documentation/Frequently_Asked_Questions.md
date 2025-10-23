# FloraSeven Frequently Asked Questions

This document provides answers to common questions about the FloraSeven smart plant monitoring system.

## General Questions

### What is FloraSeven?

FloraSeven is a comprehensive smart plant monitoring system that helps you keep your plants healthy by monitoring soil moisture, temperature, light, and other environmental factors. The system includes hardware sensors, a central server, and a mobile application that work together to provide real-time monitoring and control capabilities.

### What problems does FloraSeven solve?

FloraSeven addresses several common plant care challenges:
- Inconsistent watering (too much or too little)
- Difficulty monitoring environmental conditions
- Lack of awareness about plant health issues
- Uncertainty about optimal growing conditions
- Forgetting to water plants when needed

### What makes FloraSeven different from other plant monitoring systems?

FloraSeven offers several unique advantages:
- Comprehensive sensor suite (moisture, temperature, light, pH, EC, UV)
- AI-powered plant health analysis
- Integrated watering system
- Open architecture for customization and expansion
- Detailed documentation for users and developers

### Is FloraSeven suitable for beginners?

Yes, FloraSeven is designed to be user-friendly for beginners while offering advanced features for experienced plant enthusiasts. The mobile application provides an intuitive interface, and the system comes with default settings that work well for most common houseplants.

### Can FloraSeven be used outdoors?

The current version of FloraSeven is primarily designed for indoor use. While the hardware components are in waterproof enclosures, extended outdoor exposure is not recommended. Future versions may include enhanced outdoor capabilities.

## Hardware Questions

### What hardware components are included in the FloraSeven system?

The FloraSeven system consists of two main hardware nodes:
1. **Plant Node**: ESP32 WROOM-based node with soil moisture, temperature, light, and EC sensors
2. **Hub Node**: Combination of ESP32-CAM and Arduino R4 Minima with camera, pH sensor, UV sensor, and water pump control

### How long do the batteries last?

The batteries typically last 1-3 days depending on usage patterns, sensor reading frequency, and environmental conditions. Future versions plan to include solar charging for extended battery life.

### How accurate are the sensors?

The sensors provide reasonably accurate readings suitable for hobby gardening:
- Temperature: ±0.5°C accuracy
- Light: ±20% accuracy
- Moisture: Relative readings with good consistency
- pH: ±0.1 pH after calibration
- EC: Relative readings requiring calibration

For scientific or commercial applications, professional-grade sensors may be more appropriate.

### How much water does the pump dispense?

The default watering duration of 5 seconds dispenses approximately 50-100ml of water, depending on the specific pump and tubing configuration. This can be adjusted in the mobile application settings.

### Can I add more sensors?

The current version supports a fixed set of sensors. Future versions will include support for additional sensors and a wireless sensor network for monitoring multiple plants.

### How do I assemble the hardware?

Detailed assembly instructions are provided in the [Hardware Components](05_Hardware_Components.md) and [Deployment Guide](08_Deployment_Guide.md) documents. The assembly requires basic electronics knowledge and soldering skills.

## Server Questions

### What are the server requirements?

The server can run on a laptop or desktop computer with:
- Windows, macOS, or Linux operating system
- Python 3.9 or higher
- 2GB RAM minimum (4GB recommended)
- 1GB free disk space
- Network connectivity to hardware nodes and mobile device

### Does the server need to run continuously?

Yes, the server needs to run continuously to receive sensor data from the hardware nodes, process it, and make it available to the mobile application. If the server is shut down, data collection will be interrupted.

### Can the server run on a Raspberry Pi?

While not officially supported in the current version, the server should be able to run on a Raspberry Pi 4 with at least 2GB RAM. Future versions will include optimized support for Raspberry Pi and similar single-board computers.

### Is cloud deployment supported?

The current version is designed for local deployment. Cloud deployment is planned for future versions, which will enable remote access and monitoring from anywhere.

### How much data does the server store?

The server stores sensor data indefinitely by default. For a single plant with readings every 30 seconds, this amounts to approximately 1MB of data per month. Storage settings can be adjusted in the server configuration.

## Mobile Application Questions

### Which mobile platforms are supported?

The current version supports Android devices only. iOS support is planned for future versions.

### Can multiple users access the system?

The current version is designed for single-user access. Multi-user support with user accounts and permissions is planned for future versions.

### Can I monitor multiple plants?

The current version is designed for monitoring a single plant. Multi-plant support is a high-priority enhancement planned for future versions.

### Does the app work offline?

The app includes limited offline functionality, allowing you to view cached data when the server is unavailable. Full offline support with synchronization is planned for future versions.

### How do notifications work?

The app uses system-level Android notifications to alert you about important events such as low moisture, high temperature, or completed watering. Notification preferences can be configured in the app settings.

### Can I schedule watering?

The current version waters based on moisture thresholds rather than schedules. Scheduled watering is planned for future versions.

## System Integration Questions

### Does FloraSeven integrate with smart home platforms?

The current version does not include smart home integration. Integration with platforms like Google Home, Amazon Alexa, and Apple HomeKit is planned for future versions.

### Can FloraSeven connect to weather services?

The current version does not include weather service integration. This feature is planned for future versions to enable adaptive watering based on local weather conditions.

### Can I export data from FloraSeven?

The current version has limited data export capabilities. Comprehensive data export and import features are planned for future versions.

### Can FloraSeven be integrated with existing irrigation systems?

The current version is designed as a standalone system. Integration with larger irrigation systems is planned for future versions.

## Maintenance Questions

### How often do I need to calibrate the sensors?

It is recommended to calibrate the pH and EC sensors monthly for optimal accuracy. The moisture, temperature, light, and UV sensors do not require regular calibration.

### How do I update the firmware?

Firmware updates require connecting the hardware nodes to a computer via USB and using the Arduino IDE to upload the new firmware. Future versions will include over-the-air update capabilities.

### How do I update the mobile application?

The mobile application can be updated by installing the new APK file on your Android device. Future versions will be available through the Google Play Store for easier updates.

### How do I update the server software?

Server updates involve downloading the new server code and restarting the server application. Detailed update instructions are provided with each release.

### What regular maintenance is required?

Regular maintenance includes:
- Recharging batteries (every 1-3 days)
- Refilling the water reservoir as needed
- Cleaning sensors periodically
- Calibrating pH and EC sensors monthly
- Checking and cleaning the water pump and tubing

## Troubleshooting Questions

### What should I do if the sensors show incorrect readings?

1. Check sensor connections and placement
2. Verify battery levels
3. Calibrate sensors if applicable
4. Restart the hardware nodes
5. Consult the [Troubleshooting Guide](10_Troubleshooting.md) for specific sensor issues

### What should I do if the pump doesn't work?

1. Check pump connections
2. Verify water level in the reservoir
3. Check for blockages in the tubing
4. Test manual watering from the app
5. Restart the Hub Node
6. Consult the [Troubleshooting Guide](10_Troubleshooting.md) for detailed steps

### What should I do if the app cannot connect to the server?

1. Verify that the server is running
2. Check that your mobile device is on the same network as the server
3. Verify the server address in the app settings
4. Restart the app and server
5. Consult the [Troubleshooting Guide](10_Troubleshooting.md) for connectivity issues

### What should I do if the hardware nodes don't connect to WiFi?

1. Verify WiFi credentials in the firmware
2. Check WiFi signal strength at node locations
3. Restart the nodes
4. Reset the WiFi router
5. Consult the [Troubleshooting Guide](10_Troubleshooting.md) for detailed steps

### Where can I get help if I have more questions?

If you have questions not covered in the documentation, please:
1. Check the [Troubleshooting Guide](10_Troubleshooting.md) for common issues
2. Consult the [User Guide](09_User_Guide.md) for general usage information
3. Review the [Technical Documentation](FloraSeven_Technical_Documentation.md) for detailed technical information
4. Contact the FloraSeven development team for additional support

## Development Questions

### Is FloraSeven open source?

Yes, FloraSeven is released under the MIT License, allowing for modification and customization.

### Can I contribute to the FloraSeven project?

Yes, contributions are welcome! Please refer to the [Development Guide](07_Development_Guide.md) for information on setting up your development environment and the contribution process.

### Can I customize the hardware?

Yes, the hardware design is modular and can be customized. The [Hardware Components](05_Hardware_Components.md) document provides detailed information about the hardware architecture and components.

### Can I customize the mobile application?

Yes, the mobile application is built with Flutter and can be customized. The [Mobile Application](03_Mobile_Application.md) document provides information about the application architecture and components.

### Can I customize the server?

Yes, the server is built with Python/Flask and can be customized. The [Server Components](04_Server_Components.md) document provides information about the server architecture and components.

## Future Plans

### What enhancements are planned for future versions?

Major planned enhancements include:
- Multi-plant support
- User accounts and cloud synchronization
- iOS support
- Advanced analytics and recommendations
- Scheduling system
- Additional actuators (lights, fans)
- Solar power integration
- Wireless sensor network
- Enhanced sensor suite

For a complete list, see the [Future Enhancements](11_Future_Enhancements.md) document.

### When will these enhancements be available?

The enhancements are planned for implementation in phases over the next 24+ months. The [Current vs. Future Features](Current_vs_Future_Features.md) document provides a detailed timeline.

### Can I request new features?

Yes, feature requests are welcome and will be considered for inclusion in future versions. Please contact the FloraSeven development team with your suggestions.

### Will there be a commercial version of FloraSeven?

There are currently no plans for a commercial version. FloraSeven is designed as an open-source project for hobbyists, educators, and researchers.

### Will FloraSeven support commercial agriculture?

The current focus is on home gardening and small-scale plant care. Extensions for commercial agriculture may be considered in the future but are not currently on the roadmap.
