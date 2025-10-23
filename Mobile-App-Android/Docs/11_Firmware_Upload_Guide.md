# Firmware Upload Guide

This document provides detailed, step-by-step instructions for uploading the IoT Plant Monitoring and Watering System firmware to your ESP32 hardware. Following these instructions will ensure your hardware functions correctly with the mobile application.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Hardware Preparation](#hardware-preparation)
3. [Development Environment Setup](#development-environment-setup)
4. [Firmware Configuration](#firmware-configuration)
5. [Upload Process](#upload-process)
6. [Verification](#verification)
7. [Troubleshooting](#troubleshooting)
8. [Advanced Configuration](#advanced-configuration)
9. [Firmware Update Process](#firmware-update-process)
10. [Firmware Recovery](#firmware-recovery)

## Prerequisites

### Required Hardware

- **ESP32 Development Board** (ESP32-WROOM-32, ESP32-CAM, or similar)
- **USB to UART Adapter** (if your ESP32 doesn't have built-in USB)
- **USB Cable** (compatible with your ESP32 board or adapter)
- **Computer** with Windows, macOS, or Linux
- **Moisture Sensor** (capacitive soil moisture sensor)
- **Relay Module** (5V relay for controlling the water pump)
- **Water Pump** (5V DC mini submersible pump)
- **Power Supply** (5V/2A for ESP32 and pump)
- **Jumper Wires** (for connections)

### Required Software

- **Arduino IDE** (version 1.8.0 or higher)
- **ESP32 Board Support Package**
- **Required Libraries**:
  - ArduinoJson (version 6.x)
  - WiFi (included with ESP32 board package)
  - ESPmDNS (included with ESP32 board package)
  - WebServer (included with ESP32 board package)
  - EEPROM (included with ESP32 board package)

### Knowledge Requirements

- Basic understanding of Arduino programming
- Familiarity with electronic components and wiring
- Basic troubleshooting skills

## Hardware Preparation

Before uploading the firmware, ensure your hardware is properly assembled and connected:

### Wiring Connections

Follow this wiring diagram to connect your components:

```
ESP32 Pin    |    Component
-------------|-----------------
GPIO34       |    Moisture Sensor (AO - Analog Output)
3.3V         |    Moisture Sensor (VCC)
GND          |    Moisture Sensor (GND)
GPIO26       |    Relay Module (IN - Signal)
5V           |    Relay Module (VCC)
GND          |    Relay Module (GND)
```

The relay module should be connected to the water pump as follows:

```
Relay Module    |    Connection
----------------|------------------
COM             |    Not connected
NO (Normally Open) |    Water Pump (+)
                |    Water Pump (-) connects to GND
```

### Power Considerations

- During firmware upload, the ESP32 will be powered via USB
- For normal operation, use a 5V/2A power supply
- Ensure the power supply can handle the current draw of both the ESP32 and the water pump
- Consider using a separate power supply for the water pump if it draws significant current

## Development Environment Setup

### Installing Arduino IDE

1. **Download Arduino IDE**:
   - Go to [arduino.cc/en/software](https://arduino.cc/en/software)
   - Download the version for your operating system
   - Install following the on-screen instructions

2. **Configure Arduino IDE**:
   - Launch Arduino IDE
   - Go to File > Preferences
   - In "Additional Board Manager URLs", add:
     ```
     https://dl.espressif.com/dl/package_esp32_index.json
     ```
   - Click "OK" to save

### Installing ESP32 Board Support

1. **Open Boards Manager**:
   - Go to Tools > Board > Boards Manager

2. **Install ESP32 Package**:
   - Search for "ESP32"
   - Find "ESP32 by Espressif Systems"
   - Click "Install" (this may take several minutes)
   - Click "Close" when complete

### Installing Required Libraries

1. **Open Library Manager**:
   - Go to Tools > Manage Libraries

2. **Install ArduinoJson**:
   - Search for "ArduinoJson"
   - Find "ArduinoJson by Benoit Blanchon"
   - Select version 6.x (latest stable)
   - Click "Install"

3. **Verify Built-in Libraries**:
   - The following libraries should be included with the ESP32 board package:
     - WiFi
     - ESPmDNS
     - WebServer
     - EEPROM
   - If any are missing, search and install them from the Library Manager

## Firmware Configuration

### Accessing the Firmware Files

1. **Navigate to Firmware Directory**:
   - Open the project folder: `iot_waterpump`
   - Navigate to the firmware directory: `firmware/iot_waterpump`

2. **Open the Main Sketch**:
   - Double-click `iot_waterpump.ino` to open it in Arduino IDE
   - This should open all related files in tabs

### Configuring WiFi Settings

Locate the WiFi configuration section in `config.h` or at the top of the main sketch:

```cpp
// WiFi credentials
#define WIFI_SSID "YourWiFiName"        // Replace with your WiFi network name
#define WIFI_PASSWORD "YourWiFiPassword" // Replace with your WiFi password
```

Replace the placeholder values with your actual WiFi credentials:
- `YourWiFiName` with your WiFi network name (SSID)
- `YourWiFiPassword` with your WiFi password

### Configuring Pin Assignments

If your hardware connections differ from the default, update the pin definitions:

```cpp
// Pin definitions
#define MOISTURE_SENSOR_PIN 34  // Analog pin connected to moisture sensor
#define PUMP_RELAY_PIN 26       // Digital pin connected to relay control
```

Modify these values to match your actual hardware connections.

### Configuring Moisture Sensor Calibration

For accurate moisture readings, calibrate the sensor values:

```cpp
// Moisture sensor calibration
#define MOISTURE_DRY_VALUE 3000  // Sensor reading in completely dry soil
#define MOISTURE_WET_VALUE 1000  // Sensor reading in water
```

To determine these values for your specific sensor:
1. Place the sensor in completely dry soil or air and note the reading
2. Place the sensor in water (not fully submerged) and note the reading
3. Update the values accordingly

### Configuring Watering Parameters

Adjust the watering parameters based on your plant's needs:

```cpp
// Watering parameters
#define MANUAL_WATERING_DURATION 5000    // Duration in ms for manual watering (5 seconds)
#define AUTO_WATERING_DURATION 3000      // Duration in ms for auto watering (3 seconds)
#define MIN_WATERING_INTERVAL 3600000    // Minimum time between auto waterings (1 hour)
```

Modify these values based on:
- Your plant's water requirements
- Your pump's flow rate
- Your pot size

### Configuring mDNS Service

The mDNS service name allows the mobile app to discover your device:

```cpp
// mDNS service configuration
#define MDNS_SERVICE_NAME "ESP32PlantMonitor"  // Name for mDNS advertising
#define MDNS_SERVICE_TYPE "_plantmonitor._tcp" // Service type for mDNS
```

Keep these default values unless you have a specific reason to change them, as the mobile app is configured to look for these service names.

## Upload Process

### Connecting the ESP32

1. **Connect ESP32 to Computer**:
   - Connect your ESP32 to your computer using a USB cable
   - If using an ESP32 without built-in USB, connect via a USB to UART adapter:
     - Connect GND to GND
     - Connect TX to RX
     - Connect RX to TX
     - Connect 3.3V to 3.3V (or 5V to 5V, depending on your board)

2. **Identify the COM Port**:
   - Windows: Check Device Manager > Ports (COM & LPT)
   - macOS: In Arduino IDE, look under Tools > Port for /dev/cu.SLAB_USBtoUART or similar
   - Linux: In Arduino IDE, look under Tools > Port for /dev/ttyUSB0 or similar

### Configuring Upload Settings

1. **Select the Board**:
   - Go to Tools > Board > ESP32 Arduino
   - Select your specific ESP32 board model (e.g., "ESP32 Dev Module", "ESP32-CAM", etc.)

2. **Select the Port**:
   - Go to Tools > Port
   - Select the COM port that corresponds to your ESP32

3. **Configure Flash Settings** (if needed):
   - Go to Tools > Flash Mode and select "DIO" or "QIO" (typically DIO)
   - Go to Tools > Flash Frequency and select "80MHz"
   - Go to Tools > Flash Size and select appropriate size (typically "4MB")
   - Go to Tools > Partition Scheme and select "Default"
   - Go to Tools > Upload Speed and select "921600"

### Uploading the Firmware

1. **Verify the Code**:
   - Click the Verify button (checkmark icon) or press Ctrl+R
   - Wait for compilation to complete
   - Fix any errors that appear in the output window

2. **Prepare the ESP32 for Upload** (if needed):
   - Some ESP32 boards require you to press and hold the BOOT button
   - If using ESP32-CAM, you may need to connect GPIO0 to GND during power-up

3. **Upload the Firmware**:
   - Click the Upload button (right arrow icon) or press Ctrl+U
   - Wait for the "Connecting..." message
   - If required, press and hold the BOOT button until you see upload progress
   - Wait for the upload to complete
   - You should see "Done uploading" in the status bar when finished

4. **Reset the ESP32**:
   - Press the RESET button on the ESP32 (if available)
   - Or disconnect and reconnect the USB cable

## Verification

### Monitoring Serial Output

1. **Open Serial Monitor**:
   - Click the Serial Monitor button or go to Tools > Serial Monitor
   - Set the baud rate to 115200
   - Set line ending to "Both NL & CR"

2. **Check Initialization Messages**:
   - You should see boot messages from the ESP32
   - Look for "Connecting to WiFi..."
   - Verify successful connection: "Connected to WiFi. IP address: xxx.xxx.xxx.xxx"
   - Confirm server startup: "HTTP server started"
   - Verify mDNS advertisement: "mDNS responder started"

### Testing Basic Functionality

1. **Test WiFi Connection**:
   - Verify the ESP32 connects to your WiFi network
   - Note the IP address displayed in the Serial Monitor

2. **Test Web Server**:
   - Open a web browser on your computer
   - Navigate to the IP address displayed (e.g., http://192.168.1.100)
   - You should see a response (may be a 404 page, but confirms server is running)

3. **Test API Endpoints**:
   - Use a tool like curl or Postman to test the API endpoints:
     - GET http://[ESP32-IP]/api/status
     - POST http://[ESP32-IP]/api/water
     - POST http://[ESP32-IP]/api/auto_watering with body {"enabled": true}

### Testing with Mobile App

1. **Launch the Mobile App**:
   - Open the IoT Plant Monitoring and Watering System app on your device
   - Select "Hardware Mode" at startup

2. **Verify Discovery**:
   - The app should automatically discover your ESP32 via mDNS
   - Select your device from the list if multiple are found

3. **Check Functionality**:
   - Verify moisture readings are displayed
   - Test the "Water Now" button
   - Test enabling/disabling auto-watering
   - Confirm the 30-second cooldown timer works after watering

## Troubleshooting

### Upload Issues

| Issue | Possible Causes | Solutions |
|-------|----------------|-----------|
| "Failed to connect to ESP32" | ESP32 not in bootloader mode | Press and hold BOOT button during upload |
| | Incorrect COM port | Select the correct port in Tools > Port |
| | USB driver issues | Reinstall USB drivers |
| "Timed out waiting for packet header" | Connection issues | Press RESET button and try again |
| | Faulty USB cable | Try a different USB cable |
| "Error compiling" | Syntax errors | Check error message and fix code |
| | Missing libraries | Install required libraries |
| Upload succeeds but ESP32 doesn't run | Flash issues | Try different Flash Mode or Partition Scheme |
| | Power issues | Ensure stable power supply |

### WiFi Connection Issues

| Issue | Possible Causes | Solutions |
|-------|----------------|-----------|
| "Failed to connect to WiFi" | Incorrect credentials | Verify SSID and password |
| | WiFi network issues | Check if other devices can connect |
| | 5GHz network | Use 2.4GHz network (ESP32 may not support 5GHz) |
| | Signal strength | Move ESP32 closer to router |
| Frequent disconnections | Power issues | Use a stable power supply |
| | Interference | Change WiFi channel |
| | ESP32 overheating | Improve ventilation |

### Sensor and Actuator Issues

| Issue | Possible Causes | Solutions |
|-------|----------------|-----------|
| Incorrect moisture readings | Calibration issues | Recalibrate sensor values |
| | Wiring issues | Check connections |
| | Faulty sensor | Replace sensor |
| Pump doesn't activate | Relay wiring | Check relay connections |
| | Incorrect pin assignment | Verify PUMP_RELAY_PIN value |
| | Relay module issues | Test relay with simple sketch |
| | Insufficient power | Use adequate power supply |

### Mobile App Connection Issues

| Issue | Possible Causes | Solutions |
|-------|----------------|-----------|
| App doesn't discover ESP32 | mDNS issues | Check if both devices are on same network |
| | Firewall blocking mDNS | Check firewall settings |
| | ESP32 not advertising | Verify mDNS setup in firmware |
| Connection drops | Network issues | Check WiFi stability |
| | ESP32 restarting | Check power supply and logs |
| | Memory leaks | Update to latest firmware |

## Advanced Configuration

### Customizing Server Settings

To change the web server port (default is 80):

```cpp
// Web server configuration
#define WEB_SERVER_PORT 8080  // Change to your preferred port
```

Note: If you change the port, you'll need to specify it in the mobile app when connecting manually.

### Enabling Debug Logging

For more detailed logging:

```cpp
// Debug configuration
#define DEBUG_ENABLED true  // Set to false to disable debug messages
```

This will output additional debug information to the Serial Monitor.

### Adjusting Auto-Watering Logic

To customize the auto-watering behavior:

```cpp
// Auto-watering configuration
#define MOISTURE_THRESHOLD_LOW 30  // Percentage below which to trigger watering
#define MOISTURE_THRESHOLD_HIGH 70 // Target percentage after watering
#define AUTO_WATERING_CHECK_INTERVAL 60000 // Check interval in ms (1 minute)
```

Adjust these values based on your specific plant's needs.

### Power Saving Configuration

To enable power-saving features:

```cpp
// Power saving configuration
#define ENABLE_DEEP_SLEEP true       // Enable deep sleep between readings
#define DEEP_SLEEP_DURATION 300000   // Sleep duration in ms (5 minutes)
```

Note: Deep sleep will disconnect WiFi, so use this only if power consumption is critical.

## Firmware Update Process

### Over-the-Air (OTA) Updates

If your firmware includes OTA update capability:

1. **Prepare the New Firmware**:
   - Make your changes to the code
   - Compile the new firmware
   - Generate the binary file: Sketch > Export Compiled Binary

2. **Upload via OTA**:
   - In Arduino IDE, go to Tools > Port
   - Select your ESP32's network port (should appear as an IP address)
   - Click Upload to send the firmware over WiFi

### Manual Update Process

For standard updates:

1. **Connect ESP32 to Computer**:
   - Connect via USB as described in the Upload Process section

2. **Upload New Firmware**:
   - Make your changes to the code
   - Follow the standard upload process

3. **Verify Update**:
   - Check the Serial Monitor for the new version number
   - Test new functionality

## Firmware Recovery

If your ESP32 becomes unresponsive or enters a boot loop:

### Hard Reset Procedure

1. **Enter Recovery Mode**:
   - Disconnect power
   - Press and hold the BOOT button
   - Reconnect power while holding BOOT
   - Release BOOT after 3 seconds

2. **Flash Default Firmware**:
   - In Arduino IDE, go to Tools > Erase Flash > All Flash Contents
   - Click Upload to flash the original firmware

### Using ESP Flash Tool

For advanced recovery:

1. **Download ESP Flash Tool**:
   - Get the ESP Flash Download Tool from Espressif's website

2. **Configure Flash Tool**:
   - Select your ESP32 chip type
   - Load the firmware.bin file
   - Set correct flash address (typically 0x0)
   - Configure flash parameters

3. **Flash the Firmware**:
   - Connect ESP32 in bootloader mode
   - Click Start to flash the firmware

## Conclusion

Following this guide should result in a successfully programmed ESP32 that works seamlessly with the IoT Plant Monitoring and Watering System mobile application. The firmware provides all the functionality needed to monitor soil moisture and control watering automatically or manually.

For additional help or to report issues, please refer to the project's GitHub repository or contact the development team.

---

## Appendix: Serial Monitor Output Reference

Below is an example of the expected Serial Monitor output during normal startup:

```
ESP32 Plant Monitoring and Watering System
Firmware Version: 1.0.0
Initializing...
Connecting to WiFi...
Connected to WiFi
IP address: 192.168.1.100
HTTP server started
mDNS responder started
Service advertised: ESP32PlantMonitor._plantmonitor._tcp.local.
System ready!

Moisture sensor reading: 2048
Moisture percentage: 45%
Auto-watering: Disabled
```

This output confirms that the ESP32 has:
1. Successfully booted
2. Connected to WiFi
3. Started the web server
4. Advertised itself via mDNS
5. Started reading from the moisture sensor

## Appendix: Common ESP32 Board Pinouts

### ESP32 DevKit V1

```
GPIO34 - ADC (Input only) - Connect to moisture sensor
GPIO26 - Digital output - Connect to relay
```

### ESP32-CAM

```
GPIO33 - ADC - Connect to moisture sensor
GPIO2  - Digital output - Connect to relay
```

Note: ESP32-CAM requires an external USB-to-UART adapter for programming.

### ESP32-S2

```
GPIO7  - ADC - Connect to moisture sensor
GPIO6  - Digital output - Connect to relay
```

Adjust pin definitions in the firmware according to your specific board.
