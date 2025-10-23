# Building and Deployment

This document provides detailed instructions for building and deploying the IoT Plant Monitoring and Watering System, including the mobile application, demo server, and hardware components.

## Mobile Application

### Building for Development

#### Prerequisites

- Flutter SDK (version 3.16.0 or higher)
- Android Studio or Visual Studio Code with Flutter plugins
- Android SDK (for Android builds)
- Xcode (for iOS builds, macOS only)
- Git

#### Steps

1. **Clone the Repository**

```bash
git clone https://github.com/yourusername/iot_waterpump.git
cd iot_waterpump
```

2. **Install Dependencies**

```bash
flutter pub get
```

3. **Run in Development Mode**

For Android:
```bash
flutter run
```

For iOS (macOS only):
```bash
flutter run -d ios
```

This will build the app in debug mode and install it on a connected device or emulator.

### Building for Production

#### Android APK

To build a release APK:

```bash
flutter build apk
```

The APK will be located at `build/app/outputs/flutter-apk/app-release.apk`.

#### Android App Bundle (AAB)

For Google Play Store deployment:

```bash
flutter build appbundle
```

The AAB will be located at `build/app/outputs/bundle/release/app-release.aab`.

#### iOS IPA (macOS only)

For iOS App Store deployment:

1. Update the version in `pubspec.yaml`
2. Build the iOS release:

```bash
flutter build ios
```

3. Open the Xcode workspace:

```bash
open ios/Runner.xcworkspace
```

4. In Xcode, select `Product > Archive` to create an archive
5. Use the Xcode Organizer to upload the archive to the App Store

### Custom Build Configurations

#### Flavor-Specific Builds

The project supports different build flavors:

- **Development**: For development and testing
- **Production**: For production deployment

To build a specific flavor:

```bash
flutter build apk --flavor development
flutter build apk --flavor production
```

#### Environment-Specific Configuration

Environment-specific configuration is managed in `lib/utils/app_constants.dart`. You can modify this file to change:

- API endpoints
- Feature flags
- Default settings

### Automated Builds

#### Using GitHub Actions

The repository includes GitHub Actions workflows for automated builds:

1. **CI Workflow**: Runs on every pull request to verify the build
2. **Release Workflow**: Builds and publishes releases when a tag is pushed

The workflows are defined in `.github/workflows/`.

#### Using Fastlane

For more advanced CI/CD, you can use Fastlane:

1. Install Fastlane:

```bash
gem install fastlane
```

2. Initialize Fastlane in the project:

```bash
cd android
fastlane init
```

3. Configure Fastlane for your specific needs (see `android/fastlane/Fastfile`)

## Demo Server

### Deployment Options

#### Local Deployment

For local development and testing:

1. Navigate to the demo server directory:

```bash
cd demo_server
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the server:

```bash
python server.py
```

The server will start on port 8080 and will be accessible at `http://localhost:8080`.

#### Docker Deployment

For containerized deployment:

1. Build the Docker image:

```bash
docker build -t iot-waterpump-demo-server .
```

2. Run the container:

```bash
docker run -p 8080:8080 iot-waterpump-demo-server
```

#### Cloud Deployment

For cloud deployment (e.g., AWS, Google Cloud, Azure):

1. Create a virtual machine instance
2. Install Python and dependencies
3. Configure firewall to allow traffic on port 8080
4. Run the server as a service

Example systemd service file (`/etc/systemd/system/iot-waterpump-demo.service`):

```
[Unit]
Description=IoT Waterpump Demo Server
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/iot_waterpump/demo_server
ExecStart=/usr/bin/python3 server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl enable iot-waterpump-demo
sudo systemctl start iot-waterpump-demo
```

### Configuration

The demo server can be configured by modifying the following parameters in `server.py`:

```python
# Server configuration
HOST = '0.0.0.0'  # Listen on all interfaces
PORT = 8080
SERVICE_TYPE = '_plantmonitor._tcp.local.'
SERVICE_NAME = 'ESP32PlantMonitor'

# Simulation parameters
MOISTURE_DECREASE_RATE = 0.5  # % per minute
MOISTURE_INCREASE_RATE = 15   # % per watering
WATERING_DURATION = 5         # seconds
AUTO_WATERING_THRESHOLD = 30  # %
```

## Hardware Deployment

### Firmware Deployment

#### Prerequisites

- Arduino IDE (version 1.8.0 or higher)
- ESP32 board support package
- Required libraries (ArduinoJson, etc.)
- USB to UART adapter (for ESP32 without built-in USB)

#### Steps

1. **Connect the ESP32**

Connect the ESP32 to your computer using a USB cable or USB to UART adapter.

2. **Configure Arduino IDE**

- Open Arduino IDE
- Go to `File > Preferences`
- Add `https://dl.espressif.com/dl/package_esp32_index.json` to Additional Board Manager URLs
- Go to `Tools > Board > Boards Manager`
- Search for ESP32 and install
- Go to `Tools > Board` and select your ESP32 board
- Go to `Tools > Port` and select the port connected to your ESP32

3. **Install Required Libraries**

- Go to `Tools > Manage Libraries`
- Install the following libraries:
  - ArduinoJson
  - WiFi
  - ESPmDNS
  - WebServer
  - EEPROM

4. **Configure the Firmware**

Open `firmware/iot_waterpump/config.h` and update the following parameters:

```cpp
// WiFi credentials
#define WIFI_SSID "YourWiFiSSID"
#define WIFI_PASSWORD "YourWiFiPassword"

// Pin configuration
#define MOISTURE_SENSOR_PIN 34
#define PUMP_RELAY_PIN 26

// Moisture sensor calibration
#define MOISTURE_DRY_VALUE 3000
#define MOISTURE_WET_VALUE 1000

// Watering parameters
#define MANUAL_WATERING_DURATION 5000  // 5 seconds
#define AUTO_WATERING_DURATION 3000    // 3 seconds
#define MIN_WATERING_INTERVAL 3600000  // 1 hour
```

5. **Upload the Firmware**

- Open `firmware/iot_waterpump/iot_waterpump.ino` in Arduino IDE
- Click `Upload` or press `Ctrl+U`
- Wait for the upload to complete
- Open the Serial Monitor (`Ctrl+Shift+M`) to verify the ESP32 is working correctly

### Hardware Assembly

Follow these steps to assemble the hardware:

1. **Prepare the Components**

Gather all the required components:
- ESP32 development board
- Soil moisture sensor
- Water pump
- Relay module
- Power supply
- Jumper wires
- Breadboard or PCB
- Water tubes
- Water container

2. **Connect the Components**

Follow the wiring diagram in the [Hardware Implementation](./04_Hardware_Implementation.md) document.

3. **Test the System**

- Power on the system
- Verify the ESP32 connects to WiFi
- Check the moisture sensor readings
- Test the water pump

4. **Install in the Plant Pot**

- Insert the moisture sensor into the soil
- Position the water tube near the plant
- Place the water container in a stable position
- Secure all components to prevent water damage

### Enclosure

For a more polished deployment, consider creating an enclosure:

1. **3D Printed Enclosure**

The `hardware/enclosure` directory contains STL files for a 3D printed enclosure. Print the following parts:
- `base.stl`: Base of the enclosure
- `lid.stl`: Lid of the enclosure
- `sensor_holder.stl`: Holder for the moisture sensor

2. **Commercial Enclosure**

Alternatively, use a commercial waterproof enclosure:
- Recommended size: 100mm x 80mm x 50mm
- Drill holes for:
  - Power cable
  - Water tube
  - Moisture sensor cable
- Use cable glands to maintain water resistance

## Continuous Integration/Continuous Deployment (CI/CD)

### GitHub Actions Workflow

The repository includes GitHub Actions workflows for CI/CD:

#### Mobile App CI

`.github/workflows/flutter-ci.yml`:
```yaml
name: Flutter CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: subosito/flutter-action@v1
        with:
          flutter-version: '3.16.0'
      - run: flutter pub get
      - run: flutter analyze
      - run: flutter test
      - run: flutter build apk
      - uses: actions/upload-artifact@v2
        with:
          name: release-apk
          path: build/app/outputs/flutter-apk/app-release.apk
```

#### Demo Server CI

`.github/workflows/python-ci.yml`:
```yaml
name: Python CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.8'
      - run: |
          cd demo_server
          pip install -r requirements.txt
          python -m pytest
```

### Release Process

To create a new release:

1. Update version in `pubspec.yaml`
2. Create a new tag:

```bash
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

3. The GitHub Actions workflow will automatically build and publish the release

## Deployment Checklist

Before deploying to production, ensure:

1. **Mobile App**
   - Version number is updated in `pubspec.yaml`
   - All tests pass
   - App icon and splash screen are properly configured
   - App permissions are correctly set in `AndroidManifest.xml` and `Info.plist`

2. **Demo Server**
   - All dependencies are listed in `requirements.txt`
   - Server configuration is appropriate for the deployment environment
   - Logging is properly configured

3. **Hardware**
   - Firmware is configured with correct WiFi credentials
   - Moisture sensor is calibrated
   - Water pump is tested and working
   - All connections are secure and protected from water

## Troubleshooting Deployment Issues

### Mobile App

1. **Build Failures**
   - Check Flutter version compatibility
   - Ensure all dependencies are compatible
   - Run `flutter clean` and try again

2. **Runtime Errors**
   - Check logs using `flutter logs`
   - Verify API endpoints are accessible
   - Check network permissions

### Demo Server

1. **Server Won't Start**
   - Check Python version compatibility
   - Verify all dependencies are installed
   - Check port availability

2. **mDNS Discovery Issues**
   - Verify firewall settings
   - Check network configuration
   - Try running with administrator privileges

### Hardware

1. **ESP32 Won't Connect to WiFi**
   - Verify WiFi credentials
   - Check WiFi signal strength
   - Try a different WiFi network

2. **Moisture Sensor Readings Incorrect**
   - Recalibrate the sensor
   - Check wiring connections
   - Try a different sensor

3. **Water Pump Not Working**
   - Check relay connections
   - Verify pump is receiving power
   - Test pump directly with power supply
