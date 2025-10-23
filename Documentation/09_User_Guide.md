# FloraSeven User Guide

Welcome to the FloraSeven smart plant monitoring system! This guide will help you get started with your FloraSeven system and make the most of its features.

## Introduction

FloraSeven is a comprehensive smart plant monitoring system that helps you keep your plants healthy by monitoring soil moisture, temperature, light, and other environmental factors. The system includes hardware sensors, a central server, and a mobile application that work together to provide real-time monitoring and control capabilities.

## System Components

Your FloraSeven system consists of the following components:

1. **Plant Node**: A small device with sensors that monitors soil moisture, temperature, light, and electrical conductivity (EC).

2. **Hub Node**: A device with a camera and additional sensors that monitors pH and UV levels, and controls the water pump.

3. **Server**: Software running on a laptop or desktop computer that processes data from the hardware nodes and provides an API for the mobile application.

4. **Mobile Application**: An Android app that allows you to monitor your plant's health, control watering, and configure system settings.

## Getting Started

### Hardware Setup

1. **Plant Node Placement**:
   - Insert the soil moisture sensor into the soil, about halfway between the center and edge of the pot
   - Ensure the temperature sensor is in contact with the soil
   - Position the light sensor to measure ambient light reaching the plant
   - Keep the enclosure away from direct water exposure

2. **Hub Node Placement**:
   - Position the camera to have a clear view of the plant
   - Place the pH sensor in the water reservoir or soil as needed
   - Position the UV sensor to measure ambient UV light
   - Place the water pump in the water reservoir
   - Route the water tube to the base of the plant

3. **Power On**:
   - Ensure both nodes have charged batteries
   - Turn on both nodes using their power switches
   - The nodes will automatically connect to your WiFi network and the server

### Mobile App Installation

1. **Download the App**:
   - Install the FloraSeven app on your Android device
   - You can get the APK file from the project repository or from your system administrator

2. **First Launch**:
   - Launch the FloraSeven app
   - You'll see the splash screen with the FloraSeven logo
   - After a few seconds, you'll be prompted to enter the server address

3. **Server Connection**:
   - Enter the IP address and port of your server (e.g., `192.168.1.100:5000`)
   - Tap "Connect"
   - If the connection is successful, you'll be taken to the login screen

4. **Login**:
   - Enter your username and password
   - Tap "Login"
   - If authentication is successful, you'll be taken to the dashboard

## Using the Mobile App

### Dashboard

The dashboard is the main screen of the app and provides an overview of your plant's status.

![Dashboard](images/dashboard.png)

1. **Moisture Level**: Shows the current soil moisture level with a visual indicator
2. **Temperature**: Shows the current soil temperature
3. **Light Level**: Shows the current light level
4. **Last Watered**: Shows when the plant was last watered
5. **Plant Health**: Shows the overall health status of the plant
6. **Quick Water Button**: Tap to manually water the plant
7. **Navigation**: Use the bottom navigation bar to access other screens

### Plant Detail

The plant detail screen provides comprehensive information about your plant.

![Plant Detail](images/plant_detail.png)

1. **Plant Image**: Shows the latest image of your plant
2. **Sensor Readings**: Shows all sensor readings (moisture, temperature, light, pH, EC, UV)
3. **Health Analysis**: Shows the results of the AI-based health analysis
4. **Historical Data**: Shows charts of historical sensor data
5. **Manual Watering**: Controls for manually watering the plant
6. **Threshold Settings**: Access to threshold configuration

### Settings

The settings screen allows you to configure various system parameters.

![Settings](images/settings.png)

1. **Server Connection**: Configure the server connection settings
2. **Notification Preferences**: Configure notification settings
3. **Threshold Configuration**: Configure sensor thresholds
4. **System Information**: View system information
5. **User Account**: Manage your user account
6. **About**: View information about the FloraSeven system

## Features

### Sensor Monitoring

FloraSeven continuously monitors several environmental factors:

- **Soil Moisture**: Measures the water content in the soil
- **Soil Temperature**: Measures the temperature of the soil
- **Light Level**: Measures the ambient light reaching the plant
- **pH Level**: Measures the acidity or alkalinity of the soil or water
- **Electrical Conductivity (EC)**: Measures the nutrient concentration in the soil
- **UV Level**: Measures the ultraviolet light reaching the plant

All sensor readings are displayed in the app and updated regularly.

### Automated Watering

FloraSeven can automatically water your plant based on soil moisture thresholds:

1. **Threshold Configuration**:
   - Go to Settings > Threshold Configuration
   - Set the minimum and maximum moisture thresholds
   - Tap "Save"

2. **Automatic Watering**:
   - When soil moisture falls below the minimum threshold, the system will automatically water the plant
   - Watering continues until the moisture level reaches the maximum threshold
   - You'll receive a notification when watering starts and completes

### Manual Watering

You can manually water your plant at any time:

1. **Quick Water**:
   - Tap the "Water Now" button on the dashboard
   - The pump will run for a default duration (5 seconds)

2. **Custom Watering**:
   - Go to the Plant Detail screen
   - Tap "Manual Watering"
   - Set the desired duration
   - Tap "Start Watering"
   - Tap "Stop Watering" at any time to stop

### Plant Health Analysis

FloraSeven uses AI to analyze your plant's health:

1. **Visual Analysis**:
   - The system captures images of your plant
   - AI analyzes the images for signs of health issues
   - Results are displayed in the Plant Detail screen

2. **Sensor Condition Index**:
   - The system analyzes sensor readings
   - Compares readings to optimal ranges
   - Generates an overall health score
   - Identifies potential issues

### Notifications

FloraSeven sends notifications about important events:

- **Low Moisture**: When soil moisture falls below the minimum threshold
- **High Temperature**: When soil temperature exceeds the maximum threshold
- **Low Light**: When light level falls below the minimum threshold
- **Watering Events**: When automatic or manual watering starts and completes
- **Health Issues**: When potential health issues are detected

To configure notifications:
1. Go to Settings > Notification Preferences
2. Enable or disable specific notification types
3. Tap "Save"

## Maintenance

### Battery Charging

Both the Plant Node and Hub Node run on rechargeable batteries:

1. **Checking Battery Level**:
   - Battery levels are displayed in the app
   - You'll receive a notification when battery levels are low

2. **Charging**:
   - Connect the micro USB cable to the charging port on the node
   - Connect the other end to a USB power source
   - The charging indicator will light up
   - Charging takes approximately 3-4 hours
   - Disconnect when charging is complete

### Sensor Maintenance

To ensure accurate readings, maintain your sensors regularly:

1. **Soil Moisture Sensor**:
   - Gently clean the sensor with a soft cloth if dirty
   - Avoid bending or damaging the sensor
   - Reposition if necessary for better readings

2. **pH Sensor**:
   - Calibrate monthly using pH 4.0 and 7.0 buffer solutions
   - Store the sensor in a storage solution when not in use
   - Replace the sensor if readings become erratic

3. **EC Sensor**:
   - Calibrate monthly using a standard solution
   - Clean the probes if necessary
   - Replace if readings become unreliable

### Water Pump Maintenance

To keep the water pump working properly:

1. **Regular Cleaning**:
   - Clean the pump intake if it becomes clogged
   - Run clean water through the pump periodically
   - Check the tubing for blockages

2. **Water Reservoir**:
   - Refill the water reservoir as needed
   - Clean the reservoir monthly to prevent algae growth
   - Use clean water to prevent pump damage

## Troubleshooting

### Connection Issues

If the app cannot connect to the server:

1. **Check Server Status**:
   - Verify that the server is running
   - Check that the server computer is powered on and connected to the network

2. **Check Network Connection**:
   - Ensure your mobile device is connected to the same WiFi network as the server
   - Try connecting to other devices on the network to verify connectivity

3. **Verify Server Address**:
   - Go to Settings > Server Connection
   - Verify that the server address is correct
   - Try using the IP address instead of hostname

4. **Restart Components**:
   - Restart the mobile app
   - Restart the server
   - Restart the hardware nodes

### Sensor Reading Issues

If sensor readings are incorrect or missing:

1. **Check Sensor Connections**:
   - Verify that sensors are properly connected
   - Check for damaged cables or connectors

2. **Check Battery Levels**:
   - Low battery can cause erratic sensor readings
   - Charge the batteries if levels are low

3. **Recalibrate Sensors**:
   - Recalibrate pH and EC sensors
   - Verify soil moisture sensor readings with manual testing

4. **Restart Nodes**:
   - Power cycle the Plant Node and Hub Node
   - Wait for them to reconnect to the network

### Watering Issues

If the watering system is not working properly:

1. **Check Pump Connection**:
   - Verify that the pump is properly connected
   - Check for damaged cables or connectors

2. **Check Water Level**:
   - Ensure the water reservoir has sufficient water
   - Check that the pump intake is submerged

3. **Check Tubing**:
   - Verify that the tubing is not kinked or blocked
   - Check for leaks in the tubing

4. **Test Manual Watering**:
   - Try manual watering to verify pump operation
   - If manual watering works but automatic doesn't, check threshold settings

### App Issues

If the mobile app is not working properly:

1. **Force Close and Restart**:
   - Force close the app
   - Restart the app

2. **Clear Cache**:
   - Go to Android Settings > Apps > FloraSeven
   - Tap "Storage"
   - Tap "Clear Cache"

3. **Reinstall App**:
   - Uninstall the app
   - Reinstall from the APK file

4. **Check for Updates**:
   - Ask your system administrator if there are app updates available

## Frequently Asked Questions

### General Questions

**Q: How often does FloraSeven take sensor readings?**
A: The Plant Node takes readings every 30 seconds by default. The Hub Node continuously monitors and reports status every minute.

**Q: How long do the batteries last?**
A: The batteries typically last 1-3 days depending on usage. More frequent readings and watering will reduce battery life.

**Q: Can I use FloraSeven outdoors?**
A: FloraSeven is designed primarily for indoor use. While the hardware is in waterproof enclosures, extended outdoor exposure is not recommended.

**Q: Can I monitor multiple plants?**
A: The current version of FloraSeven is designed for monitoring a single plant. Future versions may support multiple plants.

### Sensor Questions

**Q: What is the optimal moisture range for my plant?**
A: This depends on the type of plant. Generally, 30-70% is a good range for most houseplants. Research your specific plant's needs and adjust thresholds accordingly.

**Q: What does the EC reading mean?**
A: EC (Electrical Conductivity) measures the concentration of dissolved salts and nutrients in the soil. Higher EC indicates more nutrients, but too high can indicate over-fertilization.

**Q: How accurate are the sensor readings?**
A: The sensors provide reasonably accurate readings for hobby gardening. For scientific or commercial applications, professional-grade sensors may be more appropriate.

### Watering Questions

**Q: How much water is dispensed during watering?**
A: The default watering duration of 5 seconds dispenses approximately 50-100ml of water, depending on the pump and tubing configuration.

**Q: Can I schedule watering at specific times?**
A: The current version waters based on moisture thresholds, not schedules. Scheduled watering may be added in future versions.

**Q: What happens if the water reservoir is empty?**
A: The pump will run but no water will be dispensed. The system does not currently detect an empty reservoir.

### App Questions

**Q: Can I use the app on iOS?**
A: The current version of the app is for Android only. iOS support may be added in future versions.

**Q: Can I access FloraSeven remotely?**
A: The current version requires the app to be on the same network as the server. Remote access may be added in future versions.

**Q: Can multiple people use the app?**
A: Yes, multiple people can use the app if they have the server address and login credentials.

## Support

If you encounter issues not covered in this guide, please contact your system administrator or the FloraSeven development team for assistance.

## Future Enhancements

The FloraSeven team is continuously working to improve the system. Planned enhancements include:

- Automatic plant identification
- User accounts and cloud services
- Advanced analytics and recommendations
- Complex notification system
- Scheduling features
- Additional actuators (fans, lights)
- Offline mode
- Bluetooth setup
- iOS support

Stay tuned for updates!
