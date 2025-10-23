# FloraSeven - Smart Plant Monitoring System

FloraSeven is a comprehensive IoT system for monitoring plant soil moisture and controlling watering using an ESP32-CAM microcontroller and a Flutter mobile application for Android. The system includes both a hardware implementation and a demo mode for testing without physical hardware.

## System Components

### Hardware
- ESP32-CAM microcontroller
- Arduino UNO R3 (for programming the ESP32-CAM)
- Resistive Soil Moisture Sensor
- 5V Relay Module
- Water Pump
- Breadboard and jumper wires
- Power supply (5V)

### Software
- ESP32-CAM Firmware (C++ with Arduino framework)
- Flutter Mobile App (Dart)

## Project Structure

- `firmware/` - ESP32-CAM firmware code (C++ with Arduino framework)
- `demo_server/` - Python server for demo mode
  - `server.py` - Main server implementation
  - `config.py` - Server configuration
  - `requirements.txt` - Python dependencies
- `lib/` - Flutter mobile application code
  - `models/` - Data models for plants and system status
  - `providers/` - Riverpod state management
  - `services/` - API communication and notification handling
  - `screens/` - UI screens and components
  - `utils/` - Utility classes, constants, and configuration

## Known Issues and Fixes

### Flutter Local Notifications Package Issue

When building the app with Flutter 3.24 or newer, you may encounter the following error:

```
error: reference to bigLargeIcon is ambiguous
bigPictureStyle.bigLargeIcon(null);
                     ^
both method bigLargeIcon(Bitmap) in BigPictureStyle and method bigLargeIcon(Icon) in BigPictureStyle match
```

To fix this issue, run one of the provided patch scripts before building the app:

- Windows: `./apply_notification_patch.ps1`
- Linux/Mac: `./apply_notification_patch.sh`

These scripts will automatically patch the flutter_local_notifications package in your Flutter cache. For more details, see the README in `android/app/src/main/java/com/dexterous/flutterlocalnotifications/`.

### Java Compatibility Warnings

When building the app, you might see warnings about obsolete Java 8 compatibility:

```
warning: [options] source value 8 is obsolete and will be removed in a future release
warning: [options] target value 8 is obsolete and will be removed in a future release
```

To fix these warnings, run the provided script:

- Windows: `./fix_java_compatibility.ps1`
- Linux/Mac: `./fix_java_compatibility.sh`

These scripts update the Java compatibility level to Java 11 in all relevant Gradle files in your Flutter cache.

## Getting Started

### Demo Mode (No Hardware Required)

1. Start the demo server:
   - Navigate to the `demo_server` folder
   - Double-click `start_server.bat` or run `python server.py`
   - Note the IP address displayed in the console

2. Run the Flutter app:
   - Make sure Flutter SDK is installed
   - Run `flutter pub get` to install dependencies
   - Run `flutter run` to build and install the app
   - In the app settings, enter the IP address from the demo server
   - Ensure "Demo Mode" is enabled in settings

### Hardware Mode

#### Setting Up the Hardware

1. Follow the wiring instructions in `firmware/PROGRAMMING_GUIDE.md` to connect:
   - ESP32-CAM to Arduino UNO for programming
   - Soil moisture sensor to ESP32-CAM
   - Relay module to ESP32-CAM
   - Water pump to relay module

### Programming the ESP32-CAM

1. Install PlatformIO in VS Code
2. Open the `firmware` folder in VS Code
3. Edit `include/config.h` to set your WiFi credentials
4. Connect the Arduino UNO to your computer
5. Follow the programming instructions in `firmware/PROGRAMMING_GUIDE.md`

### Building and Installing the Flutter App

1. Make sure Flutter SDK is installed
2. Run `flutter pub get` to install dependencies
3. Connect your Android device
4. Run `flutter run` to build and install the app

## Usage

### Demo Mode

1. Start the demo server (see instructions above)
2. Launch the Flutter app on your Android device
3. Go to Settings and ensure "Demo Mode" is enabled
4. Enter the IP address displayed by the demo server
5. Return to the main screen to view simulated moisture data and control the virtual watering system

### Hardware Mode

1. Power on the ESP32-CAM
2. Note the IP address displayed in the serial monitor
3. Launch the Flutter app on your Android device
4. Go to Settings and disable "Demo Mode" to switch to Hardware Mode
5. Enter the ESP32-CAM's IP address in the app settings
6. Return to the main screen to view real moisture data and control the actual watering system

## Features

- Real-time soil moisture monitoring
- Manual watering control
- Automatic watering based on moisture thresholds
- System status monitoring (WiFi signal, uptime)
- User-friendly mobile interface
- Demo mode for testing without hardware
- White theme with elegant UI styling
- Responsive design
- System notifications for critical events

## Demo Server

The demo server simulates the ESP32-CAM's behavior:

- Generates realistic moisture data that decreases over time
- Responds to watering commands by increasing moisture levels
- Implements automatic watering when moisture falls below threshold
- Provides the same API endpoints as the actual hardware

See `demo_server/README.md` for more details.