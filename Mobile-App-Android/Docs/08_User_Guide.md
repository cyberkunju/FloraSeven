# User Guide

This document provides a comprehensive guide for users of the IoT Plant Monitoring and Watering System, explaining how to set up, use, and maintain the system.

## Getting Started

### System Requirements

#### Mobile Application

- Android 6.0 (Marshmallow) or higher
- iOS 12.0 or higher (if iOS version is available)
- Bluetooth 4.0+ (for future Bluetooth connectivity features)
- Wi-Fi connectivity

#### Hardware

- Power source (wall outlet or battery)
- Wi-Fi network
- Plant pot with drainage
- Water reservoir

### Installation

#### Mobile Application

1. **Download the App**
   - Android: Download from Google Play Store or use the provided APK file
   - iOS: Download from Apple App Store (if available)

2. **Install the App**
   - Android: Open the APK file and follow the installation prompts
   - iOS: The app will install automatically after downloading

#### Hardware Setup (if using physical hardware)

1. **Assemble the Hardware**
   - Follow the assembly instructions in the [Hardware Implementation](./04_Hardware_Implementation.md) document
   - Ensure all connections are secure

2. **Position the Components**
   - Insert the moisture sensor into the soil (about 2-3 inches deep)
   - Position the water tube near the plant's base
   - Place the water reservoir in a stable position
   - Secure the electronics in a safe, dry location

3. **Connect to Power**
   - Plug the power adapter into a wall outlet
   - Connect the power adapter to the ESP32

4. **Configure Wi-Fi**
   - The ESP32 will create a temporary Wi-Fi access point named "PlantMonitor-Setup"
   - Connect to this network using your smartphone
   - Open a web browser and navigate to `192.168.4.1`
   - Enter your home Wi-Fi credentials
   - The ESP32 will restart and connect to your home Wi-Fi

### Initial Setup

1. **Launch the App**
   - Open the app on your smartphone
   - You'll be presented with the splash screen followed by the mode selection screen

2. **Select Mode**
   - Choose "Demo Mode" to use the demo server (no hardware required)
   - Choose "Hardware Mode" to connect to the physical hardware

3. **Server Discovery**
   - The app will automatically search for available servers on your local network
   - Select the discovered server from the list
   - If no server is found, ensure the server (or hardware) is powered on and connected to the same network

4. **Add Your First Plant**
   - Tap the "+" button to add a new plant
   - Enter the plant name, species, and other details
   - Optionally, add a photo of your plant
   - Set the moisture thresholds based on your plant's needs
   - Tap "Save" to add the plant to your collection

## Using the Application

### Home Screen

The home screen displays your plant collection with status indicators:

- **Plant Cards**: Each card shows a plant with its name, image, and current moisture level
- **Status Indicators**: Color-coded indicators show the plant's status:
  - Green: Moisture level is good
  - Yellow: Moisture level is getting low
  - Red: Moisture level is critically low
- **Navigation**: Access other screens using the bottom navigation bar

### Plant Detail Screen

Tap on a plant card to view detailed information:

#### Status Section

- **Moisture Level**: Current soil moisture percentage
- **Last Updated**: When the moisture level was last measured
- **Connection Status**: Whether the system is connected to the plant

#### Controls

- **Water Now Button**: Tap to trigger watering immediately
  - The button has a 30-second cooldown to prevent overwatering
  - During cooldown, the button shows the remaining time
- **Auto-Watering Toggle**: Enable or disable automatic watering based on moisture thresholds

#### Settings

- **Moisture Thresholds**: Configure the low and high moisture thresholds
- **Plant Information**: View and edit plant details
- **Watering History**: View a log of recent watering events

### Adding and Managing Plants

#### Adding a New Plant

1. Tap the "+" button on the home screen
2. Fill in the plant details:
   - **Name**: A name for your plant
   - **Species**: The plant species (optional)
   - **Image**: Add a photo of your plant (optional)
   - **Moisture Thresholds**: Set the low and high moisture thresholds
   - **Auto-Watering**: Enable or disable automatic watering
3. Tap "Save" to add the plant

#### Editing a Plant

1. Go to the plant detail screen
2. Tap the "Edit" button (pencil icon)
3. Modify the plant details
4. Tap "Save" to update the plant

#### Removing a Plant

1. Go to the plant detail screen
2. Tap the "More" button (three dots)
3. Select "Delete Plant"
4. Confirm the deletion

### Settings Screen

Access the settings screen from the bottom navigation bar:

- **Theme**: Switch between light and dark themes
- **Notifications**: Configure notification preferences
- **Server Connection**: View and manage server connections
- **About**: View app version and information

## Features

### Real-time Monitoring

The system continuously monitors the soil moisture level and displays it in the app. The moisture level is updated every few seconds when the app is open.

### Manual Watering

You can trigger watering manually by tapping the "Water Now" button on the plant detail screen. The water pump will activate for a preset duration (typically 5 seconds).

The button has a 30-second cooldown period to prevent overwatering. During this period, the button will be disabled and will show the remaining cooldown time.

### Automatic Watering

When auto-watering is enabled, the system will automatically water the plant when the moisture level falls below the low threshold. The system includes safeguards to prevent overwatering:

- Minimum interval between watering events (typically 1 hour)
- Maximum watering duration
- Moisture level checks after watering

### Notifications

The app provides notifications for important events:

- **Low Moisture**: When the moisture level falls below the low threshold
- **Critical Moisture**: When the moisture level is critically low
- **Auto-Watering**: When automatic watering is triggered
- **System Alerts**: For system issues or errors

### Server Discovery

The app automatically discovers servers on your local network using mDNS (multicast DNS). This eliminates the need to manually enter IP addresses.

### Offline Mode

The app stores plant information locally, allowing you to view plant details even when not connected to the server. However, real-time monitoring and watering controls require a server connection.

## Maintenance

### Hardware Maintenance

#### Moisture Sensor

- **Cleaning**: Remove the sensor from the soil every 2-3 months and gently clean it with a soft cloth
- **Calibration**: Recalibrate the sensor if readings seem inaccurate (see [Hardware Implementation](./04_Hardware_Implementation.md))
- **Replacement**: Replace the sensor if it shows signs of corrosion or damage

#### Water Pump

- **Cleaning**: Clean the pump and tubes every 3-6 months to prevent clogging
- **Water Quality**: Use clean water to prevent mineral buildup
- **Inspection**: Regularly check for leaks or damage

#### Water Reservoir

- **Refilling**: Check the water level regularly and refill as needed
- **Cleaning**: Clean the reservoir monthly to prevent algae growth
- **Positioning**: Ensure the reservoir is positioned to prevent accidental spills

### Software Maintenance

#### Mobile Application

- **Updates**: Keep the app updated to the latest version
- **Cache Clearing**: Occasionally clear the app cache in your device settings
- **Backup**: Use the export feature to backup your plant data

#### Firmware (if using physical hardware)

- **Updates**: Check for firmware updates periodically
- **Restart**: Restart the ESP32 occasionally to ensure optimal performance

## Troubleshooting

### Mobile Application Issues

#### App Crashes

1. Ensure your device meets the minimum requirements
2. Update the app to the latest version
3. Clear the app cache
4. Reinstall the app if problems persist

#### Connection Issues

1. Verify both your device and the server are on the same Wi-Fi network
2. Check if the server is running
3. Restart the server
4. Try manually entering the server IP address

#### Notification Problems

1. Check notification permissions in your device settings
2. Verify notification settings in the app
3. Restart the app

### Hardware Issues

#### Moisture Sensor Readings Inaccurate

1. Check sensor placement in the soil
2. Clean the sensor
3. Recalibrate the sensor
4. Replace the sensor if necessary

#### Water Pump Not Working

1. Check power connections
2. Verify the pump is not clogged
3. Test the pump directly with power
4. Check the relay functionality

#### Wi-Fi Connection Problems

1. Verify Wi-Fi credentials
2. Check Wi-Fi signal strength at the ESP32 location
3. Restart the ESP32
4. Reset and reconfigure Wi-Fi settings

### Demo Server Issues

#### Server Not Starting

1. Check if the required Python packages are installed
2. Verify the port is not in use by another application
3. Check firewall settings
4. Run the server with administrator privileges

#### Server Not Discoverable

1. Ensure your device and the server are on the same network
2. Check if mDNS is blocked by your network
3. Try using the server's IP address directly

## Best Practices

### Plant Care

- **Plant Selection**: Choose plants suitable for automated watering
- **Soil Type**: Use well-draining soil appropriate for your plant
- **Pot Size**: Ensure the pot has adequate drainage
- **Sensor Placement**: Position the moisture sensor away from the edges of the pot

### System Usage

- **Moisture Thresholds**: Set appropriate thresholds based on your plant's needs
- **Manual Checks**: Periodically check the soil moisture manually to verify sensor accuracy
- **Gradual Adjustment**: Start with conservative watering settings and adjust as needed
- **Regular Monitoring**: Check the app regularly to ensure the system is functioning properly

### Water Conservation

- **Optimal Watering**: Set thresholds to water only when necessary
- **Drip Irrigation**: Position the water tube to minimize runoff
- **Water Collection**: Consider using collected rainwater
- **Leak Prevention**: Regularly check for leaks in the system

## FAQ

### General Questions

**Q: Can I use the system for multiple plants?**
A: The current hardware setup supports one plant per ESP32. However, you can manage multiple plants in the app by setting up multiple ESP32 devices.

**Q: Does the system work with all types of plants?**
A: The system works best with plants that have consistent watering needs. It may not be suitable for plants with very specific or changing watering requirements.

**Q: Can I use the system outdoors?**
A: The system is designed primarily for indoor use. For outdoor use, you would need to weatherproof the electronics and consider power supply options.

### Mobile App Questions

**Q: Can I use the app without the hardware?**
A: Yes, you can use the app in "Demo Mode" which simulates the hardware behavior.

**Q: Is the app available for iOS?**
A: Currently, the app is available for Android. iOS support may be added in future versions.

**Q: Can multiple users control the same plant?**
A: The current version does not support multi-user access. This feature may be added in future versions.

### Hardware Questions

**Q: How long does the water pump run when triggered?**
A: By default, the pump runs for 5 seconds when manually triggered and 3 seconds when automatically triggered. These durations can be adjusted in the firmware.

**Q: How often does the system check the moisture level?**
A: The system checks the moisture level continuously, with readings taken approximately every 5 seconds.

**Q: Can I use a different type of moisture sensor?**
A: Yes, but you may need to modify the firmware to accommodate different sensor characteristics.

## Support

For additional support:

- **GitHub Issues**: Report bugs or request features on the project's GitHub repository
- **Documentation**: Refer to the other documents in the Docs folder for detailed information
- **Community Forum**: Join the community forum (if available) to connect with other users

## Glossary

- **Moisture Level**: The amount of water in the soil, expressed as a percentage
- **Moisture Threshold**: The moisture level at which the system takes action (e.g., triggering watering)
- **Auto-Watering**: Automatic watering based on moisture thresholds
- **ESP32**: The microcontroller used in the hardware component
- **mDNS**: Multicast DNS, a protocol that allows for service discovery on a local network
- **Demo Mode**: A mode that simulates the hardware behavior for testing or demonstration purposes
- **Hardware Mode**: A mode that connects to the physical ESP32 hardware
