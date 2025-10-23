// FloraSeven Hub - ESP32-CAM Firmware v1.2 (Final for Initial Test)
// Role: I2C Master, Camera Interface, WiFi/MQTT Client

#include <WiFi.h>
#include <WiFiClient.h>
#include <PubSubClient.h> // MQTT Library
#include <HTTPClient.h>   // For sending image via HTTP POST
#include "esp_camera.h"   // ESP32 Camera Driver
#include <Wire.h>         // I2C Library
#include <ArduinoJson.h>  // JSON Handling

// --- WiFi Credentials ---
const char* ssid = "xperia";         // Your WiFi SSID
const char* password = "11222211"; // Your WiFi Password

// --- MQTT Broker Settings ---
const char* mqtt_server = "192.168.179.176"; // Your Laptop's IP Address
const int mqtt_port = 1883;                 // Default MQTT port
const char* mqtt_client_id = "floraSevenHubNode"; // Unique client ID for MQTT Broker

// --- MQTT Topics ---
// Subscriptions (Commands FROM Server)
const char* mqtt_topic_cmd_pump = "floraSeven/command/hub/pump";
const char* mqtt_topic_cmd_capture = "floraSeven/command/hub/captureImage";
// Publications (Data TO Server)
const char* mqtt_topic_status = "floraSeven/hub/status";
const char* mqtt_topic_image_meta = "floraSeven/hub/cam/image_status"; // Metadata after upload

// --- Server API Endpoint ---
const char* server_image_upload_url = "http://192.168.179.176:5000/api/v1/upload_image"; // Confirmed IP & Port

// --- I2C Configuration ---
#define R4_MINIMA_I2C_ADDR 0x08 // R4 Minima Slave Address
#define I2C_SDA_PIN 14          // GPIO pin for I2C SDA on ESP32-CAM Header
#define I2C_SCL_PIN 15          // GPIO pin for I2C SCL on ESP32-CAM Header

// --- I2C Command Bytes (Matching R4 Minima) ---
#define CMD_PUMP_OFF 0x00
#define CMD_PUMP_ON 0x01
// Add commands later if needed to request pH/UV data, e.g.:
// #define CMD_REQ_PH 0x10
// #define CMD_REQ_UV 0x11

// --- Camera Pin Definition (AI-Thinker Model - Standard) ---
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26 // Internal Camera I2C Data
#define SIOC_GPIO_NUM     27 // Internal Camera I2C Clock
#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

// --- Global Variables ---
WiFiClient espClient;
PubSubClient mqttClient(espClient);
bool pumpState = false; // Track the last commanded pump state (false = OFF, true = ON)
unsigned long lastStatusPublishTime = 0;
const unsigned long intervalStatusPublish = 60000; // Publish status every 60 seconds

//=============================================================================
// SETUP FUNCTION
//=============================================================================
void setup() {
  Serial.begin(115200);
  Serial.setDebugOutput(true); // Enable detailed debug output
  Serial.println();
  Serial.println("--- FloraSeven Hub: ESP32-CAM v1.2 Final Initializing ---");

  // Initialize I2C as Master using EXTERNAL pins 14, 15
  bool i2c_ok = Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN);
  if (i2c_ok) {
     Serial.print("External I2C Master Initialized. SDA = "); Serial.print(I2C_SDA_PIN);
     Serial.print(", SCL = "); Serial.println(I2C_SCL_PIN);
  } else {
     Serial.println("!!! Failed to Initialize External I2C Master !!! Check Pins / Pullups?");
     // Consider halting or indicating error
  }

  // Initialize Camera
  if(!setupCamera()){
    Serial.println("!!! Camera Init Failed! Restarting... !!!");
    delay(1000);
    ESP.restart();
  }
  Serial.println("Camera Initialized Successfully.");

  // Connect to WiFi
  setupWiFi();

  // Configure MQTT
  mqttClient.setServer(mqtt_server, mqtt_port);
  mqttClient.setCallback(mqttCallback); // Set the function to handle incoming messages

  Serial.println("Setup Complete. Connecting to MQTT...");
  Serial.println("--------------------------------------------");
}

//=============================================================================
// LOOP FUNCTION
//=============================================================================
void loop() {
  // Reconnect to MQTT if connection lost
  if (!mqttClient.connected()) {
    reconnectMQTT();
  }
  // Allow MQTT client to process incoming messages and maintain connection
  mqttClient.loop();

  // --- Publish Hub Status Periodically ---
  if (millis() - lastStatusPublishTime > intervalStatusPublish) {
    publishHubStatus();
    lastStatusPublishTime = millis();
  }

  // Keep the loop running, MQTT processing happens in the background via client.loop()
   delay(10); // Small delay to prevent watchdog timer issues if loop is too empty
}

//=============================================================================
// WIFI SETUP
//=============================================================================
void setupWiFi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to WiFi SSID: "); Serial.println(ssid);
  WiFi.begin(ssid, password);
  int retries = 0;
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    retries++;
    if (retries > 30) { // Increased timeout (15 seconds)
        Serial.println("\n!!! Failed to connect to WiFi! Please check SSID/Password/Signal. Restarting... !!!");
        delay(1000);
        ESP.restart();
    }
  }
  Serial.println("\nWiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

//=============================================================================
// MQTT SETUP & CALLBACK
//=============================================================================
void reconnectMQTT() {
  int retries = 0;
  while (!mqttClient.connected()) {
    Serial.print("Attempting MQTT connection to "); Serial.print(mqtt_server); Serial.print("...");
    // Attempt to connect
    if (mqttClient.connect(mqtt_client_id)) {
      Serial.println("connected");
      // Subscribe to command topics upon successful connection
      if(mqttClient.subscribe(mqtt_topic_cmd_pump)){
          Serial.print("Subscribed to: "); Serial.println(mqtt_topic_cmd_pump);
      } else {
          Serial.println("!!! Failed to subscribe to pump topic !!!");
      }
       if(mqttClient.subscribe(mqtt_topic_cmd_capture)){
          Serial.print("Subscribed to: "); Serial.println(mqtt_topic_cmd_capture);
      } else {
           Serial.println("!!! Failed to subscribe to capture topic !!!");
      }
    } else {
      Serial.print("failed, rc=");
      Serial.print(mqttClient.state()); // Print the error code
      Serial.println(" try again in 5 seconds");
      delay(5000); // Wait 5 seconds before retrying
      retries++;
       if (retries > 5) { // Stop trying after ~30 seconds
          Serial.println("!!! Could not connect to MQTT Broker after multiple attempts. Check IP/Broker Status. !!!");
          // Consider alternative action like restarting WiFi or ESP
          return; // Exit reconnect attempt for now
       }
    }
  }
}

// MQTT Callback function - Handles incoming messages
void mqttCallback(char* topic, byte* payload, unsigned int length) {
  Serial.print("MQTT Message arrived [");
  Serial.print(topic);
  Serial.print("] ");

  // Create a String from the payload
  payload[length] = '\0'; // Null-terminate the payload C-string
  String message = (char*)payload;
  Serial.println(message);

  // --- Process commands based on topic ---
  if (strcmp(topic, mqtt_topic_cmd_pump) == 0) {
    processPumpCommand(message);
  } else if (strcmp(topic, mqtt_topic_cmd_capture) == 0) {
    processCaptureCommand(message);
  } else {
    Serial.println("  -> Unknown topic received.");
  }
}

//=============================================================================
// COMMAND PROCESSING
//=============================================================================

void processPumpCommand(String message) {
  StaticJsonDocument<64> doc;
  DeserializationError error = deserializeJson(doc, message);

  if (error) {
    Serial.print("deserializeJson() failed for pump command: ");
    Serial.println(error.c_str());
    return;
  }

  // Use doc.containsKey() for safer access
  if (!doc.containsKey("state")) {
     Serial.println("  Invalid pump command format: missing 'state'.");
     return;
  }
  const char* state = doc["state"];

  if (strcmp(state, "ON") == 0) {
    Serial.println("  Received Pump ON command. Sending via I2C...");
    sendCommandToR4(CMD_PUMP_ON);
    pumpState = true; // Update local tracking
  } else if (strcmp(state, "OFF") == 0) {
    Serial.println("  Received Pump OFF command. Sending via I2C...");
    sendCommandToR4(CMD_PUMP_OFF);
    pumpState = false; // Update local tracking
  } else {
    Serial.print("  Unknown pump state received: "); Serial.println(state);
  }
  // Immediately publish updated status after processing command
  publishHubStatus();
}

void processCaptureCommand(String message) {
    Serial.println("Received Capture Image command. Processing...");
    // We are ignoring payload for now, just trigger capture
    captureAndSendImage(); // Call the function to handle capture & upload
}


//=============================================================================
// I2C COMMUNICATION WITH R4 MINIMA
//=============================================================================
void sendCommandToR4(byte command) {
  Wire.beginTransmission(R4_MINIMA_I2C_ADDR);
  Wire.write(command);
  byte error = Wire.endTransmission();

  if (error == 0) {
    Serial.print("  I2C command 0x"); Serial.print(command, HEX); Serial.println(" sent successfully.");
  } else {
    Serial.print("  !!! Error sending I2C command to R4. Error code: "); Serial.println(error);
    // Consider logging this error or adding retry logic if critical
  }
}

// --- Function to Request Data from R4 (Placeholder - Implement when R4 Slave code supports it) ---
float requestFloatFromR4(byte requestCommand) {
  Serial.print("Requesting data via I2C, command: 0x"); Serial.println(requestCommand, HEX);
  Wire.beginTransmission(R4_MINIMA_I2C_ADDR);
  Wire.write(requestCommand); // Tell slave what data we want
  byte error = Wire.endTransmission();
  if (error != 0) {
    Serial.print("  !!! Error sending request command. Error code: "); Serial.println(error);
    return -1.0; // Indicate error
  }

  delay(50); // Give slave time to process request and prepare data

  int bytesToRequest = sizeof(float); // Example: Expecting a float value back
  int bytesReceived = Wire.requestFrom((uint8_t)R4_MINIMA_I2C_ADDR, (size_t)bytesToRequest);

  if (bytesReceived == bytesToRequest) {
    byte buffer[bytesToRequest];
    Wire.readBytes(buffer, bytesToRequest);
    float value;
    memcpy(&value, buffer, bytesToRequest); // Copy bytes into float variable
    Serial.print("  Received float value: "); Serial.println(value);
    return value;
  } else {
    Serial.print("  !!! Error receiving data from R4. Expected "); Serial.print(bytesToRequest);
    Serial.print(" bytes, got "); Serial.println(bytesReceived);
    // You might want to flush the buffer if partial data was received
    // while(Wire.available()) { Wire.read(); }
    return -1.0; // Indicate error
  }
}

//=============================================================================
// HUB STATUS PUBLISH
//=============================================================================
void publishHubStatus() {
  Serial.println("Publishing Hub Status...");

  // --- Request pH and UV from R4 Minima via I2C ---
  // ** PLACEHOLDER - Implement request logic when R4 slave code supports it **
  // Example:
  // float phWater = requestFloatFromR4(CMD_REQ_PH); // Need to define CMD_REQ_PH = 0x10
  // float uvAmbient = requestFloatFromR4(CMD_REQ_UV); // Need to define CMD_REQ_UV = 0x11
  float phWater = -1.0; // Placeholder until I2C request implemented
  float uvAmbient = -1.0; // Placeholder until I2C request implemented

  const char* phStatus = (phWater < -0.5) ? "error" : "active"; // Use -0.5 to allow for 0.0 readings
  const char* uvStatus = (uvAmbient < -0.5) ? "error" : "active";

  // --- Create JSON Document ---
  StaticJsonDocument<384> doc; // Increased size slightly for status object

  // Add placeholder values or actual requested values
  if (phWater >= -0.5) doc["ph_water"] = round(phWater * 10.0) / 10.0; else doc["ph_water"] = nullptr;
  if (uvAmbient >= -0.5) doc["uv_ambient"] = round(uvAmbient * 10.0) / 10.0; else doc["uv_ambient"] = nullptr;

  doc["pump_active"] = pumpState; // Use the tracked state

  JsonObject sensor_status = doc.createNestedObject("sensor_status");
  sensor_status["ph_water"] = phStatus;
  sensor_status["uv_ambient"] = uvStatus;

  // (Optional) Add last command info for debugging
  // JsonObject last_command = doc.createNestedObject("last_command");
  // last_command["type"] = "pump";
  // last_command["state"] = pumpState ? "ON" : "OFF";

  // --- Serialize and Publish ---
  char buffer[384];
  size_t n = serializeJson(doc, buffer);

  if (mqttClient.publish(mqtt_topic_status, buffer, n)) {
      Serial.print("  Published Hub Status: "); Serial.println(buffer);
  } else {
      Serial.println("  !!! Failed to publish Hub Status !!!");
  }
}


//=============================================================================
// CAMERA SETUP & CAPTURE/SEND
//=============================================================================

bool setupCamera(){
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM; // Internal camera config I2C
  config.pin_sscb_scl = SIOC_GPIO_NUM; // Internal camera config I2C
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG; // Output JPEG

  // Frame size setting
  config.frame_size = FRAMESIZE_SVGA; // 800x600 - Good balance
  config.jpeg_quality = 12; // 0-63 (lower num = higher quality, larger file)
  config.fb_count = 1;      // Number of frame buffers (1 is okay for single captures)
  #if defined(CAMERA_MODEL_ESP_EYE) || defined(CAMERA_MODEL_TTGO_T_JOURNAL)
    config.fb_location = CAMERA_FB_IN_PSRAM;
    config.grab_mode = CAMERA_GRAB_LATEST;
    Serial.println("PSRAM Found - Using PSRAM for Frame Buffer");
  #else
    // Use DRAM if PSRAM not detected - might fail for larger framesizes
    config.fb_location = CAMERA_FB_IN_DRAM;
    config.grab_mode = CAMERA_GRAB_WHEN_EMPTY; // Default for DRAM
     Serial.println("PSRAM Not Detected - Using DRAM (May limit resolution)");
     // If using DRAM, might need smaller frame size like VGA or CIF
     // config.frame_size = FRAMESIZE_VGA; // 640x480 as fallback?
  #endif


  // Initialize Camera
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x\n", err);
    return false;
  }
  Serial.println("Camera driver initialized.");

  // Optional sensor settings
  sensor_t * s = esp_camera_sensor_get();
  if (s != NULL) {
     // Settings often needed for OV2640/OV3660
     s->set_vflip(s, 0);       // 0 = disable vertical flip
     s->set_hmirror(s, 0);     // 0 = disable horizontal mirror
     s->set_brightness(s, 0);  // -2 to 2
     s->set_contrast(s, 0);    // -2 to 2
     s->set_saturation(s, 0);  // -2 to 2
  } else {
     Serial.println("Warning: Could not get camera sensor handle.");
  }

  return true;
}

// Function to capture image and send via HTTP POST
void captureAndSendImage(){
  Serial.println("Capturing image...");
  camera_fb_t * fb = NULL; // Frame buffer pointer

  // Capture frame
  fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("!!! Camera capture failed - Frame buffer is NULL !!!");
    return;
  }
   if(fb->format != PIXFORMAT_JPEG){
    Serial.println("!!! Non-JPEG format not supported for upload in this example !!!");
    esp_camera_fb_return(fb); // MUST return buffer even if not used
    return;
  }

  Serial.printf("  Picture taken! Size: %u bytes, Format: JPEG, W: %d, H: %d\n",
                fb->len, fb->width, fb->height);

  // --- Send Image via HTTP POST ---
  HTTPClient http;
  WiFiClient client; // Need a WiFiClient for HTTPClient

  Serial.print("Connecting to Server for Image Upload: "); Serial.println(server_image_upload_url);

  if (http.begin(client, server_image_upload_url)) { // Specify URL
      http.addHeader("Content-Type", "image/jpeg"); // Let server know it's JPEG

      Serial.println("  Sending HTTP POST request with image data...");
      // Send the request with the image buffer and length
      int httpCode = http.POST(fb->buf, fb->len);

      // Check the result
      if (httpCode > 0) {
          Serial.printf("  HTTP POST successful, response code: %d\n", httpCode);
          String payload = http.getString(); // Get response payload from server
          Serial.print("  Server Response: "); Serial.println(payload);

          // --- Publish MQTT Metadata AFTER successful upload ---
          StaticJsonDocument<256> imgDoc;
          imgDoc["status"] = "uploaded";
          imgDoc["filename"] = "capture.jpg"; // Server likely renames based on timestamp
          imgDoc["resolution"] = String(fb->width) + "x" + String(fb->height);
          imgDoc["size_bytes"] = fb->len;
          imgDoc["upload_method"] = "http_post";

          char metaBuffer[256];
          size_t n = serializeJson(imgDoc, metaBuffer);
          if(mqttClient.publish(mqtt_topic_image_meta, metaBuffer, n)){
              Serial.println("  Published image metadata to MQTT.");
          } else {
              Serial.println("  !!! Failed to publish image metadata to MQTT !!!");
          }

      } else {
          Serial.printf("  !!! HTTP POST failed, error: %s (Code: %d) !!!\n", http.errorToString(httpCode).c_str(), httpCode);
      }
      http.end(); // Free resources
  } else {
      Serial.printf("  !!! Unable to connect to server [%s] !!!\n", server_image_upload_url);
  }

  // --- IMPORTANT: Return the frame buffer to be reused ---
  esp_camera_fb_return(fb);
  Serial.println("Frame buffer returned.");
}