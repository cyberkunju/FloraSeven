#include <Wire.h> // Include the I2C library

// --- Pin Definitions ---
const int PUMP_PIN = 7;       // Digital pin connected to MOSFET Signal pin
const int PH_SENSOR_PIN = A0;   // Analog pin placeholder for pH Sensor SIG wire
const int UV_SENSOR_PIN = A1;   // Analog pin placeholder for ML8511 OUT pin

// --- I2C Configuration ---
const int I2C_SLAVE_ADDRESS = 0x08; // Our unique address on the I2C bus

// --- I2C Command Definitions (Matching ESP32-CAM Master) ---
#define CMD_PUMP_OFF 0x00
#define CMD_PUMP_ON 0x01
// Define commands for data requests if needed later
#define CMD_REQ_PH 0x10
#define CMD_REQ_UV 0x11
// Add more as needed...

// --- Global Variables ---
volatile byte receivedCommand = 0xFF; // Holds the last command received via I2C (init to invalid)
volatile bool newCommandReceived = false; // Flag set by I2C ISR

// Placeholder variables for sensor readings
// Using float allows for future calibrated values
float currentPHValue = -1.0; // Use -1.0 to indicate error or not read yet
float currentUVValue = -1.0; // Use -1.0 to indicate error or not read yet

// Variable to store which data master requested
volatile byte dataRequestCommand = 0x00;


//=============================================================================
// SETUP FUNCTION - Runs once on power-up/reset
//=============================================================================
void setup() {
  Serial.begin(115200);          // Start serial communication at 115200 baud
  while (!Serial) { delay(10); } // Wait for Serial Monitor to open if needed

  Serial.println("--- FloraSeven Hub: R4 Minima v1.2 Initializing ---");
  Serial.println("Role: I2C Slave, Pump Controller, Sensor Reader (pH/UV Placeholders)");

  // Initialize Pump Pin
  pinMode(PUMP_PIN, OUTPUT);
  digitalWrite(PUMP_PIN, LOW); // Ensure pump is OFF initially
  Serial.println("Pump Pin D7 Initialized as OUTPUT LOW.");

  // Initialize Sensor Pins (Even if not read yet, set as inputs)
  pinMode(PH_SENSOR_PIN, INPUT);
  pinMode(UV_SENSOR_PIN, INPUT);
  Serial.println("Sensor pins A0 (pH), A1 (UV) initialized as INPUT.");


  // Initialize I2C Communication as Slave
  Wire.begin(I2C_SLAVE_ADDRESS);  // Join I2C bus with address 0x08
  Wire.onReceive(receiveEvent);   // Register function to call when data received
  Wire.onRequest(requestEvent);   // Register function to call when master requests data
  Serial.print("I2C Initialized as Slave Address: 0x");
  Serial.println(I2C_SLAVE_ADDRESS, HEX);

  Serial.println("Setup Complete. Reading sensors & waiting for commands...");
  Serial.println("--------------------------------------------");
}

//=============================================================================
// LOOP FUNCTION - Runs repeatedly
//=============================================================================
void loop() {
  // --- Read Local Sensors (Using Placeholders for now) ---
  // When sensors are working, uncomment the actual read lines
  // int phRaw = analogRead(PH_SENSOR_PIN);
  // int uvRaw = analogRead(UV_SENSOR_PIN);
  // currentPHValue = convertRawToPH(phRaw); // Implement conversion later
  // currentUVValue = convertRawToUV(uvRaw); // Implement conversion later

  // Using placeholder values until sensors are fixed/implemented
  currentPHValue = 7.0; // Example placeholder
  currentUVValue = 0.5; // Example placeholder
  int phRaw = -1; // Indicate raw read is disabled
  int uvRaw = -1; // Indicate raw read is disabled

  // Print current status (optional for debugging)
  Serial.print("Status -> pH: "); Serial.print(currentPHValue);
  Serial.print(" | UV: "); Serial.print(currentUVValue);
  Serial.print(" | Pump State: "); Serial.println(digitalRead(PUMP_PIN) == HIGH ? "ON" : "OFF");
  // Serial.print(" | Raw -> pH: "); Serial.print(phRaw);
  // Serial.print(" | UV: "); Serial.println(uvRaw);


  // --- Process Received I2C Command ---
  if (newCommandReceived) {
    byte commandToProcess = receivedCommand; // Copy command locally
    newCommandReceived = false; // Reset the flag

    Serial.print("Processing I2C Command: 0x");
    Serial.println(commandToProcess, HEX);

    switch(commandToProcess) {
      case CMD_PUMP_ON:
        Serial.println("  Action: Turning Pump ON");
        digitalWrite(PUMP_PIN, HIGH); // Turn pump ON and leave it ON
        break; // Exit switch statement

      case CMD_PUMP_OFF:
        Serial.println("  Action: Turning Pump OFF");
        digitalWrite(PUMP_PIN, LOW); // Turn pump OFF
        break;

      // --- Add cases here to handle data requests ---
      case CMD_REQ_PH:
        Serial.println("  Info: Master requested pH data.");
        dataRequestCommand = CMD_REQ_PH; // Set flag for onRequest handler
        break;

      case CMD_REQ_UV:
         Serial.println("  Info: Master requested UV data.");
         dataRequestCommand = CMD_REQ_UV; // Set flag for onRequest handler
         break;

      // Add more commands later...

      default:
        Serial.println("  Action: Unknown command received.");
        break;
    }
    // Reset command after processing (optional, helps avoid re-processing if loop is fast)
    // receivedCommand = 0xFF; // Reset to invalid command
  }

  delay(1000); // Main loop delay - reads sensors/checks flag every second
}

//=============================================================================
// I2C Receive Event Handler (Called by hardware interrupt - KEEP IT FAST)
//=============================================================================
void receiveEvent(int howManyBytes) {
  // Only process if exactly one byte was sent (our simple command protocol)
  if (Wire.available() == 1) {
    receivedCommand = Wire.read(); // Read the command byte
    newCommandReceived = true;     // Set flag for the main loop to process
    // Avoid Serial.print() or long delays inside ISRs like this
  } else {
    // Discard extra bytes if more than one received unexpectedly
    Serial.print("Warning: Received "); Serial.print(howManyBytes); Serial.println(" bytes via I2C, expected 1. Flushing buffer.");
    while(Wire.available() > 0) {
      Wire.read(); // Read and discard extra bytes
    }
  }
}

//=============================================================================
// I2C Request Event Handler (Called by hardware interrupt when Master requests data)
//=============================================================================
void requestEvent() {
  // This function needs to send back data based on the *last* request command received
  Serial.print("I2C Request Event Triggered. Responding to command: 0x");
  Serial.println(dataRequestCommand, HEX);

  // Prepare data buffer (using float requires sending 4 bytes)
  byte buffer[sizeof(float)];
  float valueToSend = -1.0; // Default error value

  switch(dataRequestCommand) {
    case CMD_REQ_PH:
      valueToSend = currentPHValue;
      Serial.print("  Sending pH value: "); Serial.println(valueToSend);
      break;
    case CMD_REQ_UV:
      valueToSend = currentUVValue;
       Serial.print("  Sending UV value: "); Serial.println(valueToSend);
      break;
    // Add cases for other data requests later...
    default:
      Serial.println("  Unknown data request command or no request pending.");
      valueToSend = -99.99; // Send specific error code?
      break;
  }

  // Copy the float value into the byte buffer
  memcpy(buffer, &valueToSend, sizeof(float));

  // Send the byte buffer back to the master
  Wire.write(buffer, sizeof(float));

  // Optional: Reset the request command after fulfilling it
  dataRequestCommand = 0x00;
}

//=============================================================================
// Placeholder Functions for Sensor Conversion (Implement Later)
//=============================================================================
/*
float convertRawToPH(int rawADC) {
  // Add calibration logic here
  // float voltage = rawADC * (5.0 / 1023.0); // If using 10-bit ADC mode on R4
  float voltage = rawADC * (3.3 / 4095.0); // If using 12-bit default
  // Apply linear mapping (y=mx+c) based on pH 4 & 7 buffer calibration
  return 7.0; // Placeholder
}

float convertRawToUV(int rawADC) {
  // Add calibration logic here
  // float voltage = rawADC * (3.3 / 4095.0); // R4 12-bit default
  // Apply mapfloat() using YOUR calibrated voltages
  return 0.0; // Placeholder
}
*/