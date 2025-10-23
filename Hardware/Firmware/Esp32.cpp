#include <WiFi.h>
#include <PubSubClient.h> // MQTT Library
#include <Wire.h>         // I2C for BH1750
#include <BH1750.h>       // BH1750 Library
#include <OneWire.h>      // OneWire for DS18B20
#include <DallasTemperature.h> // DS18B20 Library
#include <ArduinoJson.h>  // JSON Handling

// --- WiFi Credentials ---
const char* ssid = "xperia";         // Your WiFi SSID
const char* password = "11222211"; // Your WiFi Password

// --- MQTT Broker Settings ---
const char* mqtt_server = "192.168.179.176"; // Your Laptop's IP Address
const int mqtt_port = 1883;                 // Default MQTT port
const char* mqtt_client_id = "floraSevenPlantNode1"; // Unique client ID for MQTT Broker

// --- MQTT Topics ---
const char* mqtt_topic_data = "floraSeven/plant/node1/data"; // Where this node publishes data
// const char* mqtt_topic_cmd_read = "floraSeven/command/plant/node1/readNow"; // Optional: Subscribe to force read

// --- Pin Definitions (Update these based on your actual ESP32 wiring) ---
// I2C Pins (Default for most ESP32 Dev Boards)
const int I2C_SDA_PIN = 21;
const int I2C_SCL_PIN = 22;
// OneWire Pin
const int TEMP_SENSOR_PIN = 4;  // GPIO4 for DS18B20 Data
// Analog Pins (Use ADC1 pins - GPIO 32-39)
const int MOISTURE_PIN = 34;    // GPIO34 (ADC1_CH6) for Soil Moisture Sensor Output
const int UV_PIN = 35;          // GPIO35 (ADC1_CH7) for ML8511 UV Sensor Output
const int EC_VOLTAGE_PIN = 32;  // GPIO32 (ADC1_CH4) for Conditioned EC Voltage Output
// PWM Pin (For EC Excitation - Output)
const int EC_PROBE_PWM_PIN = 25;// GPIO25 (Example)

// --- PWM Configuration ---
const int PWM_CHANNEL = 0;      // ESP32 LEDC Channel 0
const int PWM_FREQ = 5000;      // 5 kHz frequency for EC excitation
const int PWM_RESOLUTION = 8;   // 8-bit resolution (0-255)
const int PWM_DUTY_CYCLE = 128; // 50% duty cycle for balanced square wave

// --- EC Calculation & Compensation ---
// ** IMPORTANT: Calibrate these values based on your EC circuit tests! **
float ec_voltage_at_zero_ec = 0.15; // Placeholder: Voltage reading in Distilled Water
float ec_voltage_at_known_ec = 1.85; // Placeholder: Voltage reading in standard solution
float known_ec_value_ms_cm = 1.413;  // EC of standard solution (e.g., 1.413 mS/cm)
float temp_coefficient = 0.019;     // Temp coefficient (~1.9% per degree C)

// --- Sensor Objects ---
BH1750 lightMeter;
OneWire oneWire(TEMP_SENSOR_PIN);
DallasTemperature tempSensors(&oneWire);

// --- WiFi & MQTT Clients ---
WiFiClient espClient;
PubSubClient mqttClient(espClient);

// --- Deep Sleep Configuration ---
#define uS_TO_S_FACTOR 1000000ULL  // Conversion factor for micro seconds to seconds (use ULL for large numbers)
#define TIME_TO_SLEEP  30          // Time ESP32 will sleep (in seconds)

//=============================================================================
// SETUP FUNCTION
//=============================================================================
void setup() {
  Serial.begin(115200);
  while (!Serial) { delay(10); }
  Serial.println();
  Serial.println("--- FloraSeven Plant Node v1.0 Initializing ---");

  // --- Initialize Sensors ---
  // I2C for BH1750
  Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN); // Initialize I2C
  if (lightMeter.begin(BH1750::CONTINUOUS_HIGH_RES_MODE)) {
    Serial.println(F("BH1750 Light Sensor Initialized."));
  } else {
    Serial.println(F("!!! Error initializing BH1750! Check wiring. !!!"));
  }

  // OneWire for DS18B20
  tempSensors.begin();
  Serial.println("DS18B20 Temperature Sensor Initialized.");

  // Analog Pins (No special setup needed, default is INPUT)
  Serial.println("Analog pins configured for Moisture, UV, EC.");

  // --- Setup PWM for EC Excitation ---
  Serial.print("Setting up PWM on Pin "); Serial.print(EC_PROBE_PWM_PIN);
  Serial.print(" ("); Serial.print(PWM_FREQ); Serial.println(" Hz)...");
  ledcSetup(PWM_CHANNEL, PWM_FREQ, PWM_RESOLUTION);
  ledcAttachPin(EC_PROBE_PWM_PIN, PWM_CHANNEL);
  ledcWrite(PWM_CHANNEL, PWM_DUTY_CYCLE); // Start PWM signal

  // --- Connect to WiFi & MQTT ---
  setupWiFi();
  mqttClient.setServer(mqtt_server, mqtt_port);
  // mqttClient.setCallback(mqttCallback); // Add if subscribing to commands later

  Serial.println("Setup Complete. Entering main loop...");
  Serial.println("--------------------------------------------");
}

//=============================================================================
// LOOP FUNCTION
//=============================================================================
void loop() {
  // Reconnect if necessary (only if not using deep sleep)
  // if (!mqttClient.connected()) {
  //   reconnectMQTT();
  // }
  // mqttClient.loop(); // Process MQTT messages (only if not using deep sleep)


  // --- Perform Reading and Publishing ---
  readAndPublishData();

  // --- Enter Deep Sleep ---
  Serial.print("Entering Deep Sleep for "); Serial.print(TIME_TO_SLEEP); Serial.println(" seconds...");
  Serial.flush(); // Ensure serial messages are sent before sleeping
  esp_sleep_enable_timer_wakeup(TIME_TO_SLEEP * uS_TO_S_FACTOR);
  esp_deep_sleep_start();

  // Code below this point will not execute until wake-up reset
}

//=============================================================================
// WIFI & MQTT FUNCTIONS
//=============================================================================
void setupWiFi() {
  delay(10);
  Serial.print("Connecting to WiFi SSID: "); Serial.println(ssid);
  WiFi.mode(WIFI_STA); // Set WiFi to station mode
  WiFi.begin(ssid, password);
  int retries = 0;
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    retries++;
    if (retries > 30) {
      Serial.println("\n!!! WiFi Connection Failed! Entering deep sleep and retrying later... !!!");
      esp_sleep_enable_timer_wakeup(TIME_TO_SLEEP * uS_TO_S_FACTOR); // Sleep even if WiFi fails
      esp_deep_sleep_start();
    }
  }
  Serial.println("\nWiFi connected");
  Serial.print("IP address: "); Serial.println(WiFi.localIP());
}

void reconnectMQTT() {
  int retries = 0;
  while (!mqttClient.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (mqttClient.connect(mqtt_client_id)) {
      Serial.println("connected");
      // Subscribe here if needed
      // mqttClient.subscribe(mqtt_topic_cmd_read);
    } else {
      Serial.print("failed, rc="); Serial.print(mqttClient.state()); Serial.println(" try again in 5 seconds");
      delay(5000);
       retries++;
       if (retries > 5) {
          Serial.println("!!! Could not connect to MQTT Broker. Will retry after sleep. !!!");
          return; // Exit attempt, will try again after sleep
       }
    }
  }
}

//=============================================================================
// SENSOR READING & DATA PUBLISHING
//=============================================================================
void readAndPublishData() {
  // --- Ensure MQTT is Connected ---
  // If waking from sleep, need to connect each time
  if (!mqttClient.connected()) {
    reconnectMQTT();
    // If still not connected after retries, skip publishing and go back to sleep
    if (!mqttClient.connected()){
        Serial.println("MQTT connection failed, skipping publish cycle.");
        return;
    }
  }

  // --- Read Temperature ---
  tempSensors.requestTemperatures();
  float temperatureC = tempSensors.getTempCByIndex(0);
  if(temperatureC == DEVICE_DISCONNECTED_C || temperatureC < -50 || temperatureC > 120) { // Basic sanity check
    Serial.println("Error: Could not read valid temperature data");
    temperatureC = -99.0; // Indicate error
  }

  // --- Read Light ---
  float lightLux = lightMeter.readLightLevel();
  if(lightLux < 0) {
      Serial.println("Error: Could not read light data");
      // Try to reinitialize BH1750?
      // lightMeter.begin(BH1750::CONTINUOUS_HIGH_RES_MODE);
      lightLux = -1.0; // Indicate error
  }

  // --- Read Moisture ---
  int moistureRaw = averageAnalogRead(MOISTURE_PIN);
  // Convert raw value to percentage or calibrated value if needed
  // float moisturePercent = map(moistureRaw, DRY_ADC_VAL, WET_ADC_VAL, 0, 100);

  // --- Read UV ---
  int uvRaw = averageAnalogRead(UV_PIN);
  float uvVoltage = uvRaw * (3.3 / 4095.0);
  // Apply calibration later if needed: mapfloat(uvVoltage, ...)
  float uvIndex = uvVoltage; // Send raw voltage for now, server can interpret later

  // --- Read EC Voltage ---
  int ecAdcRaw = averageAnalogRead(EC_VOLTAGE_PIN);
  float ecVoltage = ecAdcRaw * (3.3 / 4095.0);

  // --- Calculate Compensated EC (Using placeholders - Requires Calibration!) ---
  float ec_measured = 0.0;
   if (abs(ec_voltage_at_known_ec - ec_voltage_at_zero_ec) > 0.01) { // Avoid division by zero
      if (ecVoltage > ec_voltage_at_zero_ec) {
          ec_measured = known_ec_value_ms_cm * (ecVoltage - ec_voltage_at_zero_ec) / (ec_voltage_at_known_ec - ec_voltage_at_zero_ec);
          if (ec_measured < 0) ec_measured = 0;
      } else {
          ec_measured = 0.0;
      }
   }

  float ec_compensated = ec_measured; // Start with measured value
  if (temperatureC > -50.0 && abs(1.0 + temp_coefficient * (temperatureC - 25.0)) > 0.01) { // Check valid temp & avoid division by zero
    ec_compensated = ec_measured / (1.0 + temp_coefficient * (temperatureC - 25.0));
  } else {
      ec_compensated = ec_measured; // Use uncompensated if temp is invalid
      Serial.println("Warning: Using uncompensated EC due to invalid temperature.");
  }


  // --- Format Data as JSON ---
  // Increase JSON doc size if needed
  StaticJsonDocument<384> doc;

  // Server handles timestamp
  doc["temp_soil_c"] = round(temperatureC * 10.0) / 10.0; // 1 decimal place
  doc["moisture_raw"] = moistureRaw;
  doc["light_lux"] = round(lightLux);
  doc["uv_voltage"] = round(uvIndex * 100.0) / 100.0; // Send voltage, rounded to 2 decimals
  doc["ec_voltage"] = round(ecVoltage * 1000.0) / 1000.0; // Send voltage, rounded to 3 decimals
  // doc["ec_comp_ms_cm"] = round(ec_compensated * 100.0) / 100.0; // Optional: Send calculated EC too

  char jsonBuffer[384];
  serializeJson(doc, jsonBuffer);

  // --- Publish to MQTT ---
  Serial.print("Publishing to MQTT: ");
  Serial.println(jsonBuffer);
  if (!mqttClient.publish(mqtt_topic_data, jsonBuffer)) {
      Serial.println("!!! MQTT Publish Failed !!!");
      // Handle failure? Retry?
  } else {
      Serial.println("  Publish successful.");
  }
}


//=============================================================================
// HELPER FUNCTION - Average Analog Read
//=============================================================================
int averageAnalogRead(int pinToRead) {
  byte numberOfReadings = 8;
  unsigned long runningValue = 0;
  for (int x = 0; x < numberOfReadings; x++) {
    runningValue += analogRead(pinToRead);
    delay(1); // Small delay helps ADC
  }
  runningValue /= numberOfReadings;
  return (int)runningValue;
}