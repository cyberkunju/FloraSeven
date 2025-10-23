# FloraSeven Hardware Components

This directory contains all hardware-related files for the FloraSeven smart plant monitoring system.

## 📁 Directory Structure

```
Hardware/
├── Firmware/              # Microcontroller firmware
│   ├── Esp32.cpp         # Plant Node (ESP32 WROOM)
│   ├── Esp32Cam.cpp      # Hub Node Camera (ESP32-CAM)
│   └── ArduinoR4Minima.cpp  # Hub Node Controller (Arduino R4)
├── Schematics/           # Circuit diagrams (if available)
├── PCB/                  # PCB design files (if available)
└── README.md            # This file
```

## 🔧 Hardware Components

### Plant Node (ESP32 WROOM)
**Purpose**: Remote sensor node for plant monitoring

**Components**:
- ESP32 WROOM development board
- DS18B20 temperature sensor
- BH1750 light sensor
- Capacitive soil moisture sensor
- DIY EC probe
- 18650 Li-ion battery + charging module

**Features**:
- Deep sleep power management (30-second cycles)
- WiFi connectivity
- MQTT communication
- Battery life: 1-3 days

### Hub Node (ESP32-CAM + Arduino R4 Minima)
**Purpose**: Central control unit with camera and pump control

**Components**:
- ESP32-CAM module (OV2640 camera)
- Arduino R4 Minima
- Crowtail pH sensor
- ML8511 UV sensor
- Mini submersible water pump
- MOSFET driver circuit
- Power supply (5V/2A recommended)

**Features**:
- Plant imaging (800×600 JPEG)
- I2C communication between microcontrollers
- HTTP image upload
- MQTT command reception
- Pump control

## 📋 Bill of Materials (BOM)

### Plant Node
| Component | Quantity | Notes |
|-----------|----------|-------|
| ESP32 WROOM | 1 | 38-pin development board |
| DS18B20 | 1 | Waterproof version recommended |
| BH1750 | 1 | I2C light sensor |
| Capacitive Moisture Sensor | 1 | Corrosion-resistant |
| EC Probe | 1 | DIY or commercial |
| 18650 Battery | 1 | 2500mAh or higher |
| TP4056 Charging Module | 1 | With protection |
| Resistors | Various | Pull-up resistors |
| Wires & Connectors | - | Dupont wires |

### Hub Node
| Component | Quantity | Notes |
|-----------|----------|-------|
| ESP32-CAM | 1 | With OV2640 camera |
| Arduino R4 Minima | 1 | - |
| Crowtail pH Sensor | 1 | Analog output |
| ML8511 UV Sensor | 1 | Analog output |
| Mini Water Pump | 1 | 3-6V DC |
| MOSFET (IRF520) | 1 | For pump control |
| Diode (1N4007) | 1 | Flyback protection |
| 5V Power Supply | 1 | 2A minimum |
| Wires & Connectors | - | - |

**Estimated Total Cost**: $80-120 USD

## 🔌 Pin Connections

### Plant Node (ESP32 WROOM)

```
DS18B20 Temperature:
  - VCC → 3.3V
  - GND → GND
  - DATA → GPIO4 (with 4.7kΩ pull-up to 3.3V)

BH1750 Light Sensor:
  - VCC → 3.3V
  - GND → GND
  - SDA → GPIO21
  - SCL → GPIO22

Capacitive Moisture Sensor:
  - VCC → 3.3V
  - GND → GND
  - AOUT → GPIO34 (ADC1_CH6)

EC Probe:
  - Excitation → GPIO25 (PWM output)
  - Signal → GPIO32 (ADC1_CH4)
  - GND → GND
```

### Hub Node (ESP32-CAM)

```
Camera: Built-in OV2640 (no external connections needed)

I2C to Arduino R4:
  - SDA → GPIO14
  - SCL → GPIO15
  - GND → GND (common ground)
```

### Hub Node (Arduino R4 Minima)

```
I2C from ESP32-CAM:
  - SDA → A4
  - SCL → A5
  - GND → GND (common ground)

pH Sensor:
  - VCC → 5V
  - GND → GND
  - AOUT → A0

UV Sensor (ML8511):
  - VCC → 3.3V
  - GND → GND
  - OUT → A1
  - EN → 3.3V

Water Pump (via MOSFET):
  - Pump + → 5V (through MOSFET drain)
  - Pump - → GND
  - MOSFET Gate → D7
  - MOSFET Source → GND
  - Diode across pump (cathode to +)
```

## 🔨 Assembly Instructions

### Plant Node Assembly

1. **Prepare the ESP32 board**
   - Solder headers if needed
   - Test basic functionality

2. **Connect sensors**
   - Wire DS18B20 with pull-up resistor
   - Connect BH1750 via I2C
   - Connect moisture sensor to ADC pin
   - Wire EC probe with PWM excitation

3. **Add power management**
   - Connect TP4056 charging module
   - Wire 18650 battery holder
   - Add power switch (optional)

4. **Test connections**
   - Upload test firmware
   - Verify sensor readings
   - Check power consumption

5. **Enclosure**
   - Use waterproof enclosure
   - Ensure sensor probes are accessible
   - Add ventilation for temperature sensor

### Hub Node Assembly

1. **Prepare ESP32-CAM**
   - Install camera module
   - Test camera functionality
   - Add external antenna (optional)

2. **Prepare Arduino R4 Minima**
   - Test basic functionality
   - Verify I2C communication

3. **Connect I2C between boards**
   - Wire SDA and SCL
   - Ensure common ground
   - Add pull-up resistors (4.7kΩ)

4. **Connect sensors to Arduino**
   - Wire pH sensor to A0
   - Wire UV sensor to A1
   - Test sensor readings

5. **Add pump control circuit**
   - Build MOSFET driver circuit
   - Add flyback diode
   - Connect pump
   - Test pump operation

6. **Power supply**
   - Use 5V/2A power adapter
   - Ensure stable voltage
   - Add capacitors for filtering

## 📤 Firmware Upload

### ESP32 WROOM (Plant Node)

1. Open `Firmware/Esp32.cpp` in Arduino IDE
2. Install required libraries:
   - OneWire
   - DallasTemperature
   - BH1750
   - WiFi
   - PubSubClient (MQTT)
3. Configure WiFi and MQTT settings
4. Select board: "ESP32 Dev Module"
5. Upload firmware

### ESP32-CAM (Hub Node)

1. Open `Firmware/Esp32Cam.cpp` in Arduino IDE
2. Install required libraries:
   - WiFi
   - PubSubClient (MQTT)
   - HTTPClient
   - Wire (I2C)
   - esp_camera
3. Configure WiFi, MQTT, and server URL
4. Select board: "AI Thinker ESP32-CAM"
5. Connect FTDI programmer (GPIO0 to GND for programming mode)
6. Upload firmware

### Arduino R4 Minima (Hub Node)

1. Open `Firmware/ArduinoR4Minima.cpp` in Arduino IDE
2. Install required libraries:
   - Wire (I2C)
3. Select board: "Arduino UNO R4 Minima"
4. Upload firmware

## 🔍 Testing & Calibration

### Sensor Calibration

**Moisture Sensor**:
1. Measure ADC value in air (dry)
2. Measure ADC value in water (wet)
3. Update calibration constants in firmware

**EC Probe**:
1. Measure voltage in distilled water (0 mS/cm)
2. Measure voltage in calibration solution (1.413 mS/cm)
3. Update calibration constants

**pH Sensor**:
1. Calibrate with pH 4.0 buffer
2. Calibrate with pH 7.0 buffer
3. Update calibration constants

### Power Consumption Testing

**Plant Node**:
- Active mode: ~160mA
- Deep sleep: ~10µA
- Average: ~23mA (30s cycle)
- Expected battery life: 1-3 days (2500mAh)

**Hub Node**:
- Idle: ~200mA
- Camera active: ~300mA
- Pump active: +500mA
- Requires continuous power supply

## 🛠️ Troubleshooting

### Plant Node Issues

**ESP32 won't wake from deep sleep**:
- Check GPIO0 is not pulled low
- Verify power supply voltage
- Test with shorter sleep duration

**Sensor readings incorrect**:
- Check wiring and connections
- Verify sensor power supply
- Recalibrate sensors
- Check for interference

**WiFi connection fails**:
- Verify SSID and password
- Check WiFi signal strength
- Reduce power consumption during connection
- Add external antenna

### Hub Node Issues

**Camera not working**:
- Check camera ribbon cable
- Verify camera power supply
- Test with example sketch
- Check GPIO pin conflicts

**I2C communication fails**:
- Verify SDA/SCL connections
- Check pull-up resistors
- Test with I2C scanner
- Ensure common ground

**Pump not responding**:
- Check MOSFET connections
- Verify pump power supply
- Test MOSFET with multimeter
- Check flyback diode orientation

## 📚 Additional Resources

- [ESP32 Documentation](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/)
- [Arduino R4 Minima Guide](https://docs.arduino.cc/hardware/uno-r4-minima)
- [Sensor Datasheets](../Documentation/)
- [Circuit Diagrams](./Schematics/)

## 🔐 Safety Considerations

- Use proper insulation for all connections
- Ensure waterproofing for outdoor sensors
- Add fuses for overcurrent protection
- Use appropriate wire gauge for pump
- Keep electronics away from water
- Follow battery safety guidelines
- Disconnect power when working on circuits

## 📝 Notes

- All firmware files use Arduino framework
- Deep sleep reduces power consumption significantly
- I2C communication requires common ground
- Camera uses significant power when active
- Pump requires flyback diode for protection
- Sensors should be calibrated regularly

---

For more detailed information, see the main [Documentation](../Documentation/) directory.
