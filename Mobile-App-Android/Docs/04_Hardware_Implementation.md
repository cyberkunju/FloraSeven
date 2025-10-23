# Hardware Implementation

This document provides detailed information about the hardware component of the IoT Plant Monitoring and Watering System, including the ESP32 setup, sensor connections, and firmware details.

## Hardware Components

### Required Components

1. **ESP32 Development Board**
   - Recommended: ESP32-WROOM-32 or ESP32-CAM
   - Features needed: Wi-Fi, sufficient GPIO pins, ADC support

2. **Soil Moisture Sensor**
   - Recommended: Capacitive soil moisture sensor (more durable than resistive)
   - Operating voltage: 3.3V-5V
   - Interface: Analog output

3. **Water Pump**
   - Type: 5V DC mini submersible pump
   - Flow rate: 100-200L/H
   - Current: ~130-220mA

4. **Relay Module**
   - Type: 5V relay module (1 channel)
   - Used to control the water pump

5. **Power Supply**
   - 5V/2A power adapter for ESP32 and pump
   - Alternative: 18650 battery with charging circuit

6. **Additional Components**
   - Jumper wires
   - Breadboard or PCB
   - Water tubes (3-5mm diameter)
   - Water container
   - Project enclosure (waterproof recommended)

### Optional Components

1. **DHT22/DHT11 Sensor**
   - For measuring ambient temperature and humidity

2. **OLED Display**
   - For displaying system status without the mobile app
   - Recommended: 0.96" 128x64 I2C OLED

3. **Status LEDs**
   - For visual indication of system status

## Hardware Setup

### Wiring Diagram

![Wiring Diagram](./images/wiring_diagram.png)

### Pin Connections

#### ESP32 to Soil Moisture Sensor

| ESP32 Pin | Moisture Sensor Pin |
|-----------|---------------------|
| 3.3V      | VCC                 |
| GND       | GND                 |
| GPIO34    | AO (Analog Output)  |

#### ESP32 to Relay Module

| ESP32 Pin | Relay Module Pin |
|-----------|------------------|
| 5V        | VCC              |
| GND       | GND              |
| GPIO26    | IN (Signal)      |

#### Relay Module to Water Pump

| Relay Module | Water Pump | Power Supply |
|--------------|------------|--------------|
| COM          | -          | -            |
| NO           | Red wire   | -            |
| -            | Black wire | GND          |
| -            | -          | 5V           |

#### Optional: ESP32 to DHT22 Sensor

| ESP32 Pin | DHT22 Pin |
|-----------|-----------|
| 3.3V      | VCC       |
| GND       | GND       |
| GPIO17    | DATA      |

#### Optional: ESP32 to OLED Display

| ESP32 Pin | OLED Display Pin |
|-----------|------------------|
| 3.3V      | VCC              |
| GND       | GND              |
| GPIO21    | SDA              |
| GPIO22    | SCL              |

### Assembly Instructions

1. **Prepare the Components**
   - Ensure the ESP32 is flashed with the firmware
   - Test each component individually before assembly

2. **Connect the Soil Moisture Sensor**
   - Insert the sensor into the soil
   - Connect the wires according to the pin connections table

3. **Connect the Relay and Water Pump**
   - Mount the relay module in a dry location
   - Connect the relay to the ESP32
   - Connect the water pump to the relay and power supply
   - Place the pump's tube in the water container
   - Position the output tube near the plant

4. **Connect Optional Components**
   - If using DHT22, connect according to the pin connections table
   - If using OLED display, connect according to the pin connections table

5. **Power the System**
   - Connect the power supply
   - Verify all connections are secure
   - Power on the system

6. **Waterproof Considerations**
   - Keep the electronics away from water
   - Use a waterproof enclosure for outdoor use
   - Consider using heat shrink tubing for wire connections

## Firmware

### Overview

The ESP32 firmware is written in C++ using the Arduino framework. It handles:

1. Wi-Fi connectivity
2. Web server for API endpoints
3. mDNS for service discovery
4. Sensor reading and processing
5. Water pump control
6. Auto-watering logic

### Dependencies

The firmware requires the following libraries:

1. **WiFi.h** - For Wi-Fi connectivity
2. **ESPmDNS.h** - For mDNS service advertising
3. **WebServer.h** - For handling HTTP requests
4. **ArduinoJson.h** - For JSON parsing and generation
5. **EEPROM.h** - For persistent storage

### Firmware Structure

```
firmware/
├── iot_waterpump/
│   ├── iot_waterpump.ino       # Main sketch file
│   ├── config.h                # Configuration parameters
│   ├── wifi_manager.h          # Wi-Fi connection management
│   ├── web_server.h            # Web server and API endpoints
│   ├── sensor_manager.h        # Sensor reading and processing
│   ├── pump_controller.h       # Water pump control
│   └── auto_watering.h         # Auto-watering logic
└── libraries/                  # Required libraries
```

### Key Functions

#### Main Setup and Loop

```cpp
void setup() {
  Serial.begin(115200);
  
  // Initialize EEPROM for settings storage
  EEPROM.begin(512);
  
  // Load settings from EEPROM
  loadSettings();
  
  // Initialize GPIO pins
  initializePins();
  
  // Connect to Wi-Fi
  connectToWiFi();
  
  // Start mDNS service
  startMDNS();
  
  // Setup web server routes
  setupWebServer();
  
  // Start the web server
  server.begin();
  
  Serial.println("System initialized and ready");
}

void loop() {
  // Handle web server clients
  server.handleClient();
  
  // Read sensor data
  readSensors();
  
  // Check if auto-watering should be triggered
  if (autoWateringEnabled) {
    checkAutoWatering();
  }
  
  // Small delay to prevent CPU hogging
  delay(100);
}
```

#### Sensor Reading

```cpp
void readSensors() {
  // Read moisture sensor
  int rawMoisture = analogRead(MOISTURE_SENSOR_PIN);
  
  // Convert raw value to percentage (0-100%)
  // Note: The sensor gives lower values for higher moisture
  int moisturePercent = map(rawMoisture, MOISTURE_DRY_VALUE, MOISTURE_WET_VALUE, 0, 100);
  
  // Constrain to valid range
  moisturePercent = constrain(moisturePercent, 0, 100);
  
  // Update global variable
  currentMoisturePercent = moisturePercent;
  
  // Optional: Read temperature and humidity if DHT sensor is connected
  if (DHT_ENABLED) {
    readDHTSensor();
  }
  
  // Log sensor data periodically
  static unsigned long lastLogTime = 0;
  if (millis() - lastLogTime > LOG_INTERVAL) {
    Serial.print("Moisture: ");
    Serial.print(currentMoisturePercent);
    Serial.println("%");
    
    lastLogTime = millis();
  }
}
```

#### Water Pump Control

```cpp
void activateWaterPump(unsigned long duration) {
  // Check if pump is already running
  if (isPumpRunning) {
    Serial.println("Pump is already running");
    return;
  }
  
  // Activate the pump
  digitalWrite(PUMP_RELAY_PIN, HIGH);
  isPumpRunning = true;
  pumpStartTime = millis();
  pumpDuration = duration;
  
  Serial.print("Pump activated for ");
  Serial.print(duration / 1000);
  Serial.println(" seconds");
}

void checkPumpStatus() {
  // Check if pump is running and should be turned off
  if (isPumpRunning && (millis() - pumpStartTime >= pumpDuration)) {
    digitalWrite(PUMP_RELAY_PIN, LOW);
    isPumpRunning = false;
    
    Serial.println("Pump deactivated");
    
    // Update last watered timestamp
    lastWateredTime = millis();
  }
}
```

#### Auto-Watering Logic

```cpp
void checkAutoWatering() {
  // Only check if auto-watering is enabled and pump is not running
  if (!autoWateringEnabled || isPumpRunning) {
    return;
  }
  
  // Check if moisture is below threshold
  if (currentMoisturePercent < moistureThresholdLow) {
    // Check if enough time has passed since last watering
    if (millis() - lastWateredTime > MIN_WATERING_INTERVAL) {
      Serial.println("Auto-watering triggered");
      activateWaterPump(AUTO_WATERING_DURATION);
    }
  }
}
```

#### Web Server API Endpoints

```cpp
void setupWebServer() {
  // Status endpoint
  server.on("/api/status", HTTP_GET, []() {
    DynamicJsonDocument doc(256);
    
    doc["moisturePercent"] = currentMoisturePercent;
    doc["isWatering"] = isPumpRunning;
    doc["autoWateringEnabled"] = autoWateringEnabled;
    doc["lastUpdated"] = millis();
    doc["isConnected"] = true;
    doc["systemStatus"] = "OK";
    
    String response;
    serializeJson(doc, response);
    
    server.send(200, "application/json", response);
  });
  
  // Water endpoint
  server.on("/api/water", HTTP_POST, []() {
    activateWaterPump(MANUAL_WATERING_DURATION);
    
    server.send(200, "application/json", "{\"success\": true}");
  });
  
  // Auto-watering toggle endpoint
  server.on("/api/auto_watering", HTTP_POST, []() {
    // Parse request body
    if (server.hasArg("plain")) {
      DynamicJsonDocument doc(64);
      deserializeJson(doc, server.arg("plain"));
      
      if (doc.containsKey("enabled")) {
        autoWateringEnabled = doc["enabled"].as<bool>();
        
        // Save setting to EEPROM
        saveSettings();
        
        server.send(200, "application/json", "{\"success\": true}");
      } else {
        server.send(400, "application/json", "{\"error\": \"Missing 'enabled' parameter\"}");
      }
    } else {
      server.send(400, "application/json", "{\"error\": \"Missing request body\"}");
    }
  });
  
  // Not found handler
  server.onNotFound([]() {
    server.send(404, "application/json", "{\"error\": \"Not found\"}");
  });
}
```

### Flashing the Firmware

To flash the firmware to the ESP32:

1. **Install Arduino IDE**
   - Download and install from [arduino.cc](https://www.arduino.cc/en/software)

2. **Install ESP32 Board Support**
   - Open Arduino IDE
   - Go to File > Preferences
   - Add `https://dl.espressif.com/dl/package_esp32_index.json` to Additional Board Manager URLs
   - Go to Tools > Board > Boards Manager
   - Search for ESP32 and install

3. **Install Required Libraries**
   - Go to Tools > Manage Libraries
   - Install the following libraries:
     - ArduinoJson
     - DHT sensor library (if using DHT sensor)
     - Adafruit SSD1306 (if using OLED display)

4. **Configure Board Settings**
   - Select the appropriate board from Tools > Board
   - Set the correct port from Tools > Port

5. **Upload the Firmware**
   - Open the `iot_waterpump.ino` file
   - Click the Upload button or press Ctrl+U

## Calibration

### Moisture Sensor Calibration

The moisture sensor needs to be calibrated for accurate readings:

1. **Dry Calibration**
   - Remove the sensor from soil and ensure it's completely dry
   - Note the raw analog reading (this is your `MOISTURE_DRY_VALUE`)

2. **Wet Calibration**
   - Place the sensor in water (not fully submerged)
   - Note the raw analog reading (this is your `MOISTURE_WET_VALUE`)

3. **Update Firmware Constants**
   - Update the `MOISTURE_DRY_VALUE` and `MOISTURE_WET_VALUE` in `config.h`
   - Reflash the firmware

### Water Pump Calibration

To calibrate the water pump duration:

1. **Measure Water Flow Rate**
   - Activate the pump for 10 seconds
   - Measure the amount of water dispensed
   - Calculate the flow rate (ml/second)

2. **Determine Optimal Watering Duration**
   - Based on plant type and pot size, determine the required water amount
   - Calculate the duration needed to dispense this amount
   - Update the `MANUAL_WATERING_DURATION` and `AUTO_WATERING_DURATION` in `config.h`

## Troubleshooting

### Common Issues

1. **Moisture Sensor Readings Inconsistent**
   - Check connections
   - Recalibrate the sensor
   - Try a different sensor (they can degrade over time)

2. **Pump Not Activating**
   - Check relay connections
   - Verify relay is receiving the signal (LED on relay should light up)
   - Test pump directly with power supply

3. **ESP32 Not Connecting to Wi-Fi**
   - Verify Wi-Fi credentials
   - Check Wi-Fi signal strength at device location
   - Try resetting the ESP32

4. **System Restarting Unexpectedly**
   - Check power supply (insufficient current can cause restarts)
   - Add a capacitor across power lines to stabilize
   - Check for memory leaks in firmware

### Maintenance

1. **Regular Checks**
   - Clean the moisture sensor every 2-3 months
   - Check water tubes for blockages
   - Verify pump operation

2. **Firmware Updates**
   - Check for firmware updates periodically
   - Update using the same flashing procedure

## Power Consumption

The system's power consumption varies depending on the state:

| State                | Approximate Current Draw |
|----------------------|--------------------------|
| Idle (Wi-Fi active)  | 80-120mA                |
| Sensing only         | 100-140mA               |
| Pump active          | 200-350mA               |

For battery-powered operation, consider:
- Using deep sleep modes
- Reducing Wi-Fi transmission frequency
- Using a larger capacity battery (2000mAh+)

## Safety Considerations

1. **Electrical Safety**
   - Keep all electrical components away from water
   - Use appropriate fuses or current limiters
   - Consider using optoisolators for additional safety

2. **Water Safety**
   - Ensure water containment is secure
   - Use check valves to prevent backflow
   - Position electronics above water level

3. **Plant Safety**
   - Implement safeguards against overwatering
   - Set reasonable limits on pump activation frequency
   - Consider adding a water level sensor to prevent pump dry running
