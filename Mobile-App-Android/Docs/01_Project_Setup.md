# Project Setup

This document provides detailed instructions for setting up the IoT Plant Monitoring and Watering System development environment.



lib/
├── main.dart                   # Application entry point
├── models/                     # Data models
│   ├── plant.dart              # Plant model
│   ├── plant_status.dart       # Plant status model
│   └── server_info.dart        # Server information model
├── providers/                  # State management
│   ├── providers.dart          # Provider exports
│   ├── plant_provider.dart     # Plant collection management
│   ├── plant_status_provider.dart # Real-time status management
│   ├── server_discovery_provider.dart # Server discovery
│   └── theme_provider.dart     # Theme management
├── screens/                    # UI screens
│   ├── add_edit_plant_screen.dart # Add/Edit plant screen
│   ├── plant_collection_screen.dart # Home screen with plant list
│   ├── new_splash_screen.dart  # Splash screen
│   ├── plant_detail_screen.dart # Plant details and controls
│   └── settings_screen.dart    # App settings
├── services/                   # Business logic
│   ├── api_service.dart        # API communication
│   ├── notification_service.dart # Notification management
│   └── discovery_service.dart  # mDNS discovery
└── utils/                      # Utilities
    ├── app_constants.dart      # Constants and theme
    ├── app_logger.dart         # Logging configuration
    └── extensions.dart         # Extension methods


    
## Prerequisites

### Software Requirements

1. **Flutter SDK** (version 3.16.0 or higher)
   - [Flutter Installation Guide](https://flutter.dev/docs/get-started/install)
   - Run `flutter doctor` to verify installation

2. **Android Studio** (for Android development)
   - [Android Studio Installation](https://developer.android.com/studio)
   - Required plugins:
     - Flutter plugin
     - Dart plugin

3. **Visual Studio Code** (optional but recommended)
   - [VS Code Installation](https://code.visualstudio.com/)
   - Recommended extensions:
     - Flutter
     - Dart
     - Material Icon Theme
     - Better Comments

4. **Python** (version 3.8 or higher, for demo server)
   - [Python Installation](https://www.python.org/downloads/)
   - Required packages:
     - Flask
     - zeroconf
     - requests

5. **Git** (for version control)
   - [Git Installation](https://git-scm.com/downloads)

### Hardware Requirements (for physical implementation)

1. **ESP32-CAM** or **ESP32** microcontroller
2. **Moisture Sensor** (capacitive soil moisture sensor recommended)
3. **Water Pump** (5V DC mini water pump)
4. **Relay Module** (for controlling the water pump)
5. **Power Supply** (5V for ESP32 and pump)
6. **Jumper Wires**
7. **Breadboard** (for prototyping)
8. **USB to UART Converter** (for programming ESP32)

## Project Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/iot_waterpump.git
cd iot_waterpump
```

### 2. Flutter Setup

1. Install Flutter dependencies:

```bash
flutter pub get
```

2. Verify Flutter setup:

```bash
flutter doctor
```

3. Check for any issues with the Flutter project:

```bash
flutter analyze
```

### 3. Demo Server Setup

1. Navigate to the demo server directory:

```bash
cd demo_server
```

2. Install Python dependencies:

```bash
pip install -r requirements.txt
```

3. Start the demo server:

```bash
python server.py
```

The server will start on port 8080 and will be accessible at `http://localhost:8080`.

### 4. Hardware Setup (for physical implementation)

For detailed hardware setup instructions, refer to the [Hardware Implementation](./04_Hardware_Implementation.md) document.

### 5. Running the Application

#### Using Demo Mode

1. Start the demo server as described above.
2. Run the Flutter application:

```bash
cd ..  # Return to the project root
flutter run
```

3. When the app starts, select "Demo Mode" on the startup screen.

#### Using Physical Hardware

1. Set up the hardware as described in the Hardware Implementation document.
2. Upload the firmware to the ESP32 (see the Hardware Implementation document).
3. Run the Flutter application:

```bash
flutter run
```

4. When the app starts, select "Hardware Mode" on the startup screen.

## Folder Structure

```
iot_waterpump/
├── android/                  # Android-specific files
├── assets/                   # App assets (images, animations)
├── build/                    # Build output
├── demo_server/              # Python demo server
│   ├── server.py             # Server implementation
│   └── requirements.txt      # Python dependencies
├── Docs/                     # Documentation
├── firmware/                 # ESP32 firmware
│   ├── iot_waterpump/        # Arduino project
│   └── libraries/            # Required libraries
├── ios/                      # iOS-specific files
├── lib/                      # Flutter application code
│   ├── models/               # Data models
│   ├── providers/            # State management
│   ├── screens/              # UI screens
│   ├── services/             # Business logic
│   ├── utils/                # Utilities
│   └── main.dart             # Application entry point
├── test/                     # Test files
├── pubspec.yaml              # Flutter dependencies
└── README.md                 # Project overview
```

## Troubleshooting

For common setup issues and their solutions, refer to the [Troubleshooting](./09_Troubleshooting.md) document.
