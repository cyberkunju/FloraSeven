# FloraSeven Deployment Guide

This guide provides detailed instructions for deploying the FloraSeven system, including the mobile application, server components, and hardware setup.

## Overview

Deploying the FloraSeven system involves three main components:

1. **Hardware Setup**: Assembling and configuring the Plant Node and Hub Node
2. **Server Deployment**: Setting up the server on a laptop or desktop computer
3. **Mobile Application Deployment**: Building and installing the Android application

## Hardware Deployment

### Components Required

#### Plant Node

- ESP32 WROOM Development Board
- DS18B20 Waterproof Temperature Sensor
- BH1750 Light Sensor Module
- Capacitive Soil Moisture Sensor V2.0
- DIY EC Probe with LM358 Amplifier
- 18650 Battery with Holder
- TP4056 Charging Module
- 3.3V Voltage Regulator
- Waterproof Enclosure
- Connecting Wires
- Resistors and Capacitors (as per schematic)

#### Hub Node

- ESP32-CAM Module
- Arduino R4 Minima
- ML8511 UV Sensor
- Crowtail pH Sensor
- Mini Submersible Pump (3-6V)
- MOSFET (e.g., IRF520)
- 18650 Battery with Holder
- TP4056 Charging Module
- 3.3V Voltage Regulator
- Waterproof Enclosure
- Connecting Wires
- Silicone Tubing

### Plant Node Assembly

1. **Prepare the Circuit Board**:
   - Use a prototype board or PCB for component mounting
   - Follow the schematic for connections

2. **Connect the Power Circuit**:
   - Connect the 18650 battery to the TP4056 module
   - Connect the TP4056 output to the 3.3V regulator
   - Connect the regulator output to the ESP32 VIN and GND

3. **Connect the Sensors**:
   - **DS18B20**:
     - Connect VCC to 3.3V
     - Connect GND to ground
     - Connect DATA to GPIO4 with a 4.7kΩ pull-up resistor to 3.3V

   - **BH1750**:
     - Connect VCC to 3.3V
     - Connect GND to ground
     - Connect SDA to GPIO21
     - Connect SCL to GPIO22

   - **Soil Moisture Sensor**:
     - Connect VCC to 3.3V
     - Connect GND to ground
     - Connect OUT to GPIO34

   - **EC Probe Circuit**:
     - Build the EC probe circuit with LM358 as per schematic
     - Connect the excitation signal to GPIO25
     - Connect the output to GPIO32

4. **Assemble the Enclosure**:
   - Place the circuit board in the waterproof enclosure
   - Route sensor cables through cable glands
   - Ensure the battery is securely mounted
   - Seal all openings with silicone or appropriate sealant

### Hub Node Assembly

1. **Prepare the Circuit Boards**:
   - Mount the ESP32-CAM on a suitable adapter board
   - Mount the Arduino R4 Minima securely

2. **Connect the Power Circuit**:
   - Connect the 18650 battery to the TP4056 module
   - Connect the TP4056 output to the 3.3V regulator
   - Connect the regulator output to both the ESP32-CAM and Arduino R4 Minima

3. **Connect the I2C Interface**:
   - Connect GPIO14 of ESP32-CAM to SDA of Arduino R4 Minima
   - Connect GPIO15 of ESP32-CAM to SCL of Arduino R4 Minima
   - Add 4.7kΩ pull-up resistors to both SDA and SCL lines

4. **Connect the Sensors and Actuators**:
   - **pH Sensor**:
     - Connect to A0 of Arduino R4 Minima

   - **UV Sensor**:
     - Connect VCC to 3.3V
     - Connect GND to ground
     - Connect OUT to A1 of Arduino R4 Minima

   - **Water Pump**:
     - Connect the pump to the MOSFET circuit
     - Connect the MOSFET gate to D7 of Arduino R4 Minima
     - Connect the pump power to the battery (not through the regulator)

5. **Assemble the Enclosure**:
   - Place the circuit boards in the waterproof enclosure
   - Ensure the camera has a clear view through a transparent window
   - Route sensor cables and pump tubing through appropriate openings
   - Seal all openings with silicone or appropriate sealant

### Firmware Upload

#### Plant Node Firmware

1. **Connect the ESP32 to your computer**:
   - Use a USB-to-Serial adapter
   - Connect RX, TX, GND, and 3.3V
   - Connect GPIO0 to GND during reset to enter download mode

2. **Configure the Firmware**:
   - Open `Esp32.cpp` in Arduino IDE
   - Update WiFi credentials:
     ```cpp
     const char* ssid = "your_wifi_ssid";
     const char* password = "your_wifi_password";
     ```
   - Update MQTT broker address:
     ```cpp
     const char* mqtt_server = "your_server_ip";
     ```
   - Adjust sleep interval if needed:
     ```cpp
     #define TIME_TO_SLEEP 30 // Time in seconds
     ```

3. **Upload the Firmware**:
   - Select "ESP32 Dev Module" from the Boards menu
   - Select the appropriate COM port
   - Click Upload
   - Remove the GPIO0 to GND connection after upload

4. **Verify Operation**:
   - Open Serial Monitor (115200 baud)
   - Reset the ESP32
   - Verify that it connects to WiFi and MQTT
   - Verify that sensor readings are displayed
   - Verify that it enters deep sleep mode

#### Hub Node Firmware

1. **ESP32-CAM Firmware**:
   - Connect the ESP32-CAM to your computer using a USB-to-Serial adapter
   - Connect GPIO0 to GND during reset to enter download mode
   - Open `Esp32Cam.cpp` in Arduino IDE
   - Update WiFi and MQTT settings:
     ```cpp
     const char* ssid = "your_wifi_ssid";
     const char* password = "your_wifi_password";
     const char* mqtt_server = "your_server_ip";
     ```
   - Update server URL:
     ```cpp
     const char* server_image_upload_url = "http://your_server_ip:5000/api/v1/upload_image";
     ```
   - Select "AI Thinker ESP32-CAM" from the Boards menu
   - Upload the firmware
   - Remove the GPIO0 to GND connection after upload

2. **Arduino R4 Minima Firmware**:
   - Connect the Arduino R4 Minima to your computer via USB
   - Open `ArduinoR4Minima.cpp` in Arduino IDE
   - Select "Arduino Uno R4 Minima" from the Boards menu
   - Upload the firmware

### Hardware Testing

1. **Power Test**:
   - Power both nodes with batteries
   - Verify that they boot up correctly
   - Check power consumption during active and sleep modes

2. **Sensor Test**:
   - Verify that all sensors are reading correctly
   - Test in different conditions to ensure proper operation
   - Calibrate sensors if necessary

3. **Communication Test**:
   - Verify that both nodes connect to WiFi
   - Verify MQTT communication with the server
   - Verify I2C communication between ESP32-CAM and Arduino R4 Minima

4. **Actuator Test**:
   - Test the water pump operation
   - Verify that commands from the server control the pump
   - Check water flow and pressure

5. **Camera Test**:
   - Verify that the camera captures images
   - Verify that images are uploaded to the server
   - Check image quality and resolution

## Server Deployment

### Prerequisites

- Computer running Windows, macOS, or Linux
- Python 3.9 or higher
- MQTT broker (e.g., Mosquitto)
- Network connectivity to hardware nodes
- Sufficient storage for database and images

### Installation

1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd Server
   ```

2. **Create Virtual Environment**:
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment**:
   - Create a `.env` file based on `.env.example`
   - Set the following variables:
     ```
     HOST=0.0.0.0
     PORT=5000
     DEBUG=False
     SECRET_KEY=your_secret_key
     UPLOAD_FOLDER=images
     MAX_CONTENT_LENGTH=16777216
     MQTT_BROKER=localhost
     MQTT_PORT=1883
     MQTT_CLIENT_ID=floraseven_server
     MQTT_USERNAME=
     MQTT_PASSWORD=
     ```

5. **Initialize Database**:
   - The database will be automatically initialized on first run
   - Alternatively, run:
     ```bash
     python -c "import database; database.init_db()"
     ```

6. **Install MQTT Broker**:
   - **Windows**:
     - Download and install Mosquitto from [mosquitto.org](https://mosquitto.org/download/)
     - Create a configuration file `mosquitto.conf`:
       ```
       listener 1883
       allow_anonymous true
       ```
     - Start Mosquitto:
       ```
       mosquitto -c mosquitto.conf
       ```

   - **macOS**:
     ```bash
     brew install mosquitto
     mosquitto -c /usr/local/etc/mosquitto/mosquitto.conf
     ```

   - **Linux**:
     ```bash
     sudo apt-get install mosquitto
     sudo systemctl start mosquitto
     ```

### Running the Server

1. **Start the Server**:
   ```bash
   python server.py
   ```

2. **Verify Operation**:
   - The server should start and display:
     ```
     Starting FloraSeven server on 0.0.0.0:5000
     ```
   - Open a web browser and navigate to `http://localhost:5000/api/v1/status`
   - You should see a JSON response (may require authentication)

### Server Configuration

#### MQTT Configuration

- Edit the `.env` file to set MQTT broker details:
  ```
  MQTT_BROKER=your_mqtt_broker_ip
  MQTT_PORT=1883
  MQTT_CLIENT_ID=floraseven_server
  MQTT_USERNAME=your_username  # If authentication is enabled
  MQTT_PASSWORD=your_password  # If authentication is enabled
  ```

#### Authentication Configuration

- Edit `auth.py` to configure users:
  ```python
  USERS = {
      "admin": {
          "password": "password",  # Change this!
          "role": "admin"
      }
  }
  ```
- For production, consider implementing a more secure authentication system

#### Threshold Configuration

- Default thresholds are set in `database.py`
- These can be modified through the API or directly in the database

### Production Deployment

For a more robust production deployment, consider the following:

1. **Use a WSGI Server**:
   ```bash
   pip install gunicorn  # On Linux/macOS
   gunicorn -w 4 -b 0.0.0.0:5000 server:app
   ```

2. **Use a Process Manager**:
   - Install Supervisor:
     ```bash
     pip install supervisor
     ```
   - Create a configuration file `supervisord.conf`:
     ```
     [program:floraseven]
     command=/path/to/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 server:app
     directory=/path/to/Server
     user=username
     autostart=true
     autorestart=true
     redirect_stderr=true
     stdout_logfile=/path/to/Server/logs/supervisor.log
     ```
   - Start Supervisor:
     ```bash
     supervisord -c supervisord.conf
     ```

3. **Use a Reverse Proxy**:
   - Install Nginx
   - Configure Nginx to proxy requests to the Flask application
   - Enable HTTPS with Let's Encrypt

## Mobile Application Deployment

### Prerequisites

- Flutter SDK 3.x
- Android SDK
- Android device or emulator
- USB debugging enabled on Android device (for development)

### Building the Application

1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd iot_waterpump
   ```

2. **Install Dependencies**:
   ```bash
   flutter pub get
   ```

3. **Configure Server Connection**:
   - Edit `lib/utils/app_config.dart`:
     ```dart
     static const String apiBaseUrl = 'http://your_server_ip:5000/api/v1';
     ```

4. **Build Debug APK**:
   ```bash
   flutter build apk --debug
   ```

5. **Build Release APK**:
   ```bash
   flutter build apk --release
   ```
   The APK will be located at `build/app/outputs/flutter-apk/app-release.apk`

### Installing on Android Device

#### Using Flutter

1. Connect your Android device via USB
2. Enable USB debugging on your device
3. Run:
   ```bash
   flutter install
   ```

#### Manual Installation

1. Transfer the APK to your Android device
2. On your device, navigate to the APK file
3. Tap the APK file to install
4. You may need to enable installation from unknown sources in your device settings

### Running the Application

1. Launch the FloraSeven app on your device
2. On first launch, you'll be prompted to enter the server address
3. Enter the IP address and port of your server (e.g., `192.168.1.100:5000`)
4. Log in with the credentials configured in the server

## System Integration

### Network Configuration

1. **WiFi Network**:
   - Ensure all devices (hardware nodes, server, mobile device) are on the same WiFi network
   - The network should have good coverage in the area where the hardware nodes are deployed
   - The network should be stable and reliable

2. **IP Addressing**:
   - The server should have a static IP address
   - Update the firmware and mobile app with this IP address
   - Alternatively, use mDNS for service discovery (future enhancement)

3. **Firewall Configuration**:
   - Ensure the following ports are open on the server:
     - 5000/TCP for the REST API
     - 1883/TCP for MQTT

### Hardware Placement

1. **Plant Node**:
   - Place the soil moisture sensor in the soil, about halfway between the center and edge of the pot
   - Ensure the temperature sensor is in contact with the soil
   - Position the light sensor to measure ambient light reaching the plant
   - Keep the enclosure away from direct water exposure

2. **Hub Node**:
   - Position the camera to have a clear view of the plant
   - Place the pH sensor in the water reservoir or soil as needed
   - Position the UV sensor to measure ambient UV light
   - Place the water pump in the water reservoir
   - Route the water tube to the base of the plant

### Initial System Setup

1. **Server Setup**:
   - Start the server
   - Verify that it's running and accessible

2. **Hardware Setup**:
   - Power on the Plant Node and Hub Node
   - Verify that they connect to WiFi and MQTT
   - Check the server logs for connection messages

3. **Mobile App Setup**:
   - Install and launch the mobile app
   - Configure the server connection
   - Log in with the configured credentials
   - Verify that the dashboard shows sensor data

4. **System Testing**:
   - Test manual watering functionality
   - Verify that sensor readings are updated
   - Test image capture functionality
   - Verify that notifications work correctly

## Maintenance

### Regular Maintenance

1. **Battery Charging**:
   - Check battery levels regularly
   - Recharge batteries when they reach 20% capacity
   - Consider implementing a battery level monitoring system

2. **Sensor Calibration**:
   - Calibrate the pH sensor monthly
   - Calibrate the EC sensor monthly
   - Check soil moisture sensor readings against known wet and dry conditions

3. **Water Reservoir**:
   - Refill the water reservoir as needed
   - Clean the reservoir monthly to prevent algae growth
   - Check the water pump and tubing for blockages

4. **Software Updates**:
   - Check for firmware updates
   - Update the mobile application when new versions are available
   - Update the server software when new versions are available

### Troubleshooting

#### Hardware Issues

1. **Node Not Connecting**:
   - Check battery level
   - Verify WiFi credentials
   - Check WiFi signal strength
   - Reset the node and observe serial output

2. **Sensor Reading Errors**:
   - Check sensor connections
   - Verify power supply
   - Calibrate sensors if needed
   - Replace sensors if faulty

3. **Pump Not Working**:
   - Check pump connections
   - Verify MOSFET operation
   - Check for blockages in tubing
   - Verify that commands are being received

#### Server Issues

1. **Server Not Starting**:
   - Check for error messages
   - Verify Python environment
   - Check for port conflicts
   - Verify dependencies are installed

2. **MQTT Connection Issues**:
   - Verify MQTT broker is running
   - Check broker address and port
   - Check for authentication issues
   - Monitor MQTT messages using a client like MQTT Explorer

3. **API Errors**:
   - Check server logs for error messages
   - Verify database connectivity
   - Check for disk space issues
   - Restart the server if needed

#### Mobile App Issues

1. **Connection Errors**:
   - Verify server address
   - Check network connectivity
   - Verify that the server is running
   - Check for firewall issues

2. **Authentication Errors**:
   - Verify credentials
   - Check server authentication configuration
   - Clear app data and try again

3. **UI Issues**:
   - Restart the app
   - Clear app cache
   - Reinstall the app if needed

## Backup and Recovery

### Server Backup

1. **Database Backup**:
   - Regularly backup the SQLite database:
     ```bash
     cp data/floraseven_data.db data/floraseven_data.db.backup
     ```

2. **Image Backup**:
   - Backup the images directory:
     ```bash
     cp -r images images_backup
     ```

3. **Configuration Backup**:
   - Backup the `.env` file and any custom configurations

### Recovery Procedures

1. **Database Recovery**:
   - Stop the server
   - Replace the database with the backup:
     ```bash
     cp data/floraseven_data.db.backup data/floraseven_data.db
     ```
   - Restart the server

2. **Server Reinstallation**:
   - Clone the repository
   - Install dependencies
   - Restore the database and images from backup
   - Restore configuration files
   - Start the server

3. **Hardware Recovery**:
   - Reflash firmware if needed
   - Replace faulty components
   - Reconfigure WiFi and MQTT settings
   - Test functionality

## Security Considerations

### Network Security

1. **WiFi Security**:
   - Use WPA2 or WPA3 encryption
   - Use a strong password
   - Consider using a separate network for IoT devices

2. **MQTT Security**:
   - Enable MQTT authentication
   - Use TLS for MQTT if possible
   - Restrict MQTT access to local network

3. **API Security**:
   - Implement proper authentication
   - Use HTTPS for API communication (in production)
   - Implement rate limiting

### Physical Security

1. **Hardware Protection**:
   - Use waterproof enclosures
   - Secure mounting to prevent tampering
   - Consider tamper-evident seals

2. **Server Protection**:
   - Keep the server in a secure location
   - Implement physical access controls
   - Use disk encryption if sensitive data is stored

### Data Security

1. **User Data**:
   - Minimize collection of personal data
   - Encrypt sensitive data
   - Implement proper access controls

2. **Credentials**:
   - Use strong passwords
   - Store passwords securely (hashed and salted)
   - Rotate credentials periodically

## Scaling Considerations

The current FloraSeven system is designed for monitoring a single plant. For larger deployments, consider the following:

1. **Multiple Plant Nodes**:
   - Modify the MQTT topics to include unique identifiers
   - Update the server to handle multiple nodes
   - Enhance the mobile app to display multiple plants

2. **Distributed Server**:
   - Consider moving to a cloud-based server
   - Implement a more scalable database (e.g., PostgreSQL)
   - Use a dedicated MQTT broker service

3. **Enhanced Mobile App**:
   - Implement user accounts
   - Add plant management features
   - Enhance visualization for multiple plants

## Conclusion

This deployment guide provides comprehensive instructions for setting up the FloraSeven system. By following these steps, you should be able to deploy a fully functional plant monitoring system with sensor data collection, automated watering, and mobile app control.

For further assistance, refer to the troubleshooting section or contact the development team.
