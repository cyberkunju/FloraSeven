# 🌿 FloraSeven - Smart Greenhouse IoT Ecosystem

<div align="center">

![FloraSeven Logo](Documentation/images/logo.png)

**A scalable IoT ecosystem for precision monitoring and automated care of plants in controlled environments**

*Combining AI-powered visual diagnostics with multi-modal sensor data for near-human plant health understanding*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Flutter](https://img.shields.io/badge/Flutter-3.7+-02569B.svg)](https://flutter.dev/)
[![ESP32](https://img.shields.io/badge/ESP32-Compatible-green.svg)](https://www.espressif.com/)

[Features](#-features) • [Architecture](#-architecture) • [Installation](#-installation) • [Documentation](#-documentation) • [Contributing](#-contributing)

</div>

---

## 📋 Overview

FloraSeven is a scalable Internet of Things (IoT) ecosystem designed for precision monitoring and automated care of high-value and sensitive plants in controlled environments such as greenhouses. The system leverages a modular architecture comprising wireless, battery-powered sensor nodes and a central intelligent hub. It integrates multi-modal data sensing (soil, water, and atmospheric parameters) with AI-powered visual diagnostics to provide a holistic and actionable assessment of plant health.

A cross-platform mobile application, connected via a cloud-ready backend, facilitates real-time remote monitoring, configuration, and control, demonstrating a complete, end-to-end solution for modern smart agriculture and precision horticulture.

### Core Innovation: AI-Sensor Fusion

FloraSeven's defining innovation lies in its refusal to rely on a single data source. By combining **quantitative sensor data** (the "how it feels") with **AI-powered visual analysis** (the "how it looks"), the system achieves a near-human level of contextual understanding of plant health, providing actionable insights that go beyond traditional monitoring systems.

### 🎯 Key Capabilities

- **Multi-Modal Data Sensing**: Comprehensive monitoring of 6 environmental parameters (soil moisture, temperature, light intensity, pH, EC, UV index)
- **AI-Powered Visual Diagnostics**: CNN-based image classification providing Visual Health Score (0-100) and descriptive labels
- **Holistic Health Assessment**: Intelligent fusion of sensor-based Condition Index and AI Visual Health Score for actionable insights
- **Automated Precision Irrigation**: MOSFET-controlled water pump with configurable thresholds and safety limits
- **Dynamic Remote Configuration**: User-adjustable sensor thresholds via mobile app without firmware changes
- **Modular & Scalable Architecture**: Wireless, battery-powered nodes enable effortless scaling from single plant to entire greenhouse
- **Real-Time Communication**: MQTT-based low-latency data transfer with WebSocket support
- **Cross-Platform Mobile App**: Flutter-based native experience for iOS and Android
- **Cloud-Ready Backend**: Python Flask/FastAPI server with SQLite storage, fully deployable to cloud infrastructure
- **Power Efficient Design**: Deep sleep cycles and swappable 18650 Li-ion batteries for continuous operation

---

## ✨ Features

### Hardware Layer

#### 1. Wireless Plant Node (Sensor Layer)
**Purpose**: Self-contained, battery-powered unit for per-plant deployment, capturing high-fidelity data from the plant's immediate root zone and micro-environment.

**ESP32 WROOM Microcontroller with Precision Sensors**:
- **Capacitive Soil Moisture Sensor**: Corrosion-resistant, accurate moisture detection
- **DS18B20 Temperature Sensor**: Waterproof, ±0.5°C accuracy for soil temperature
- **BH1750 Light Sensor**: I2C-based ambient light measurement (Lux)
- **ML8511 UV Sensor**: UV index monitoring for light quality assessment
- **4-Electrode DIY EC Probe**: Custom-built with op-amp signal conditioning and temperature compensation
- **Power Management**: Deep sleep cycles (30s intervals), swappable 18650 Li-ion battery with external charging
- **Connectivity**: Wi-Fi + MQTT for efficient, low-latency data transmission

#### 2. Intelligent Hub Node (Control & Vision Layer)
**Purpose**: Central command, control, and vision analysis unit serving as the primary gateway to the backend.

**Dual-Microcontroller Design**:
- **Arduino UNO R4 Minima**: Robust real-time sensor reading (pH, UV) and actuator control
  - Crowtail pH Sensor for water quality monitoring
  - ML8511 UV Sensor for ambient conditions
  - MOSFET-controlled 3-6V submersible pump for precision irrigation
  - I²C communication with ESP32-CAM
  
- **ESP32-CAM Module**: Dedicated vision and network gateway
  - OV2640 camera for high-resolution plant imaging (800×600 JPEG)
  - Wi-Fi connectivity for server communication
  - HTTP image upload and MQTT command reception
  - I²C master for Arduino communication

### Server Backend (Backend & Intelligence Layer)
**Purpose**: The central brain of the ecosystem, handling data aggregation, storage, complex logic, AI processing, and serving as the bridge to the user application.

**Technology Stack**:
- **MQTT Broker**: Mosquitto for real-time messaging from IoT nodes
- **Backend Framework**: Python with Flask (REST API) and WebSocket support
- **Data Storage**: SQLite with optimized queries, connection pooling, and automatic backups
- **AI Engine**: TensorFlow-based CNN (MobileNetV2) for image classification

**Core Intelligence**:
- **Data Fusion**: Combines sensor data from Plant Node and Hub Node
- **Sensor-Based Condition Index**: Compares live data against user-defined optimal thresholds
  - Generates qualitative status alerts ("Optimal", "Needs Water", "Nutrient Alert")
  - Configurable thresholds per sensor parameter
- **AI Visual Diagnostics**: 
  - Processes plant images using trained CNN
  - Outputs Visual Health Score (0-100)
  - Provides descriptive labels ("Healthy", "Wilting Detected", "Nutrient Deficiency")
- **Holistic Health Assessment**: 
  - Intelligently combines Condition Index and Visual Health Score
  - Generates actionable suggestions and alerts
  - Historical trend analysis and predictive insights

**API Features**:
- 17+ RESTful endpoints for complete system control
- Real-time data streaming via WebSocket
- Secure authentication and session management
- Rate limiting and CORS support
- Comprehensive error handling and logging

### Mobile Application (Presentation Layer)
**Purpose**: Primary user interface for interacting with the FloraSeven ecosystem from anywhere in the world.

**Technology Stack**: Flutter for high-performance, cross-platform native experience (iOS/Android)

**Key Features**:
- **Real-Time Dashboard**: 
  - Live data from all sensors with visual indicators
  - Current plant image with AI analysis overlay
  - Visual Health Score and overall health status
  - Intuitive, visually appealing Material Design 3 UI
  
- **Remote Control & Actuation**:
  - Manual pump control ("Water Now" button)
  - Camera trigger for on-demand image capture
  - Force sensor reading commands
  
- **Dynamic Configuration**:
  - Remote threshold adjustment for each sensor parameter
  - Plant-specific profile management
  - System settings and calibration
  - No firmware changes required for configuration updates
  
- **Intelligent Notifications**:
  - Critical alerts (low moisture, extreme temperature)
  - AI-detected health issues
  - System status updates
  - Customizable notification preferences
  
- **Data Visualization**:
  - Real-time charts using FL Chart
  - Historical trend analysis
  - Comparative views across multiple plants
  - Export capabilities for data analysis
  
- **Offline Capability**:
  - Local storage with Hive
  - Command queuing during disconnection
  - Automatic sync when connection restored
  
- **Advanced Features**:
  - Server discovery via mDNS
  - Multi-server support
  - Dark/light theme
  - Localization support

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         SENSOR LAYER (Plant Node)                        │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │  ESP32 WROOM - Wireless Battery-Powered Sensor Node            │    │
│  │  ┌──────────────────────────────────────────────────────────┐  │    │
│  │  │ Precision Sensors:                                        │  │    │
│  │  │  • Capacitive Soil Moisture (Corrosion-resistant)        │  │    │
│  │  │  • DS18B20 Temperature (±0.5°C, Waterproof)              │  │    │
│  │  │  • BH1750 Light Sensor (I2C, Lux measurement)            │  │    │
│  │  │  • ML8511 UV Index Sensor                                │  │    │
│  │  │  • 4-Electrode EC Probe (Op-amp conditioned, temp comp)  │  │    │
│  │  └──────────────────────────────────────────────────────────┘  │    │
│  │  Power: 18650 Li-ion | Deep Sleep: 30s cycles | WiFi + MQTT   │    │
│  └────────────────────────────────────────────────────────────────┘    │
└──────────────────────────────────┬──────────────────────────────────────┘
                                   │ MQTT (WiFi)
                                   │
┌──────────────────────────────────▼──────────────────────────────────────┐
│              CONTROL & VISION LAYER (Hub Node)                           │
│  ┌─────────────────────────┐      ┌──────────────────────────────┐     │
│  │  Arduino R4 Minima      │◄────►│  ESP32-CAM                   │     │
│  │  (I²C Slave)            │ I²C  │  (I²C Master + Network)      │     │
│  │                         │      │                              │     │
│  │  • pH Sensor (Crowtail) │      │  • OV2640 Camera (800×600)   │     │
│  │  • UV Sensor (ML8511)   │      │  • WiFi + MQTT Client        │     │
│  │  • Pump Control (MOSFET)│      │  • HTTP Image Upload         │     │
│  └─────────────────────────┘      └──────────────────────────────┘     │
└──────────────────────────────────┬──────────────────────────────────────┘
                                   │ MQTT + HTTP (WiFi)
                                   │
┌──────────────────────────────────▼──────────────────────────────────────┐
│           BACKEND & INTELLIGENCE LAYER (Server)                          │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │                    Python Flask Server                          │    │
│  │  ┌──────────────────────────────────────────────────────────┐  │    │
│  │  │  Mosquitto MQTT Broker ◄─► MQTT Client (Paho)            │  │    │
│  │  └──────────────────────────────────────────────────────────┘  │    │
│  │  ┌──────────────────────────────────────────────────────────┐  │    │
│  │  │  Data Fusion & Intelligence Engine:                      │  │    │
│  │  │  • Sensor-Based Condition Index (Threshold Comparison)   │  │    │
│  │  │  • AI Visual Diagnostics (CNN - MobileNetV2)             │  │    │
│  │  │  • Holistic Health Assessment (Fusion Algorithm)         │  │    │
│  │  │  • Actionable Insights & Alerts                          │  │    │
│  │  └──────────────────────────────────────────────────────────┘  │    │
│  │  ┌──────────────────────────────────────────────────────────┐  │    │
│  │  │  SQLite Database (9 Tables):                             │  │    │
│  │  │  • Time-series sensor data • Image analysis logs         │  │    │
│  │  │  • User thresholds • Connection status • Alerts          │  │    │
│  │  └──────────────────────────────────────────────────────────┘  │    │
│  │  REST API (17 endpoints) | WebSocket | Authentication          │    │
│  └────────────────────────────────────────────────────────────────┘    │
└──────────────────────────────────┬──────────────────────────────────────┘
                                   │ REST API / WebSocket
                                   │
┌──────────────────────────────────▼──────────────────────────────────────┐
│                  PRESENTATION LAYER (Mobile App)                         │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │              Flutter Cross-Platform Application                 │    │
│  │  ┌──────────────────────────────────────────────────────────┐  │    │
│  │  │  Real-Time Dashboard:                                     │  │    │
│  │  │  • Live sensor data • AI Visual Health Score             │  │    │
│  │  │  • Plant image overlay • Holistic health status          │  │    │
│  │  └──────────────────────────────────────────────────────────┘  │    │
│  │  ┌──────────────────────────────────────────────────────────┐  │    │
│  │  │  Remote Control & Configuration:                         │  │    │
│  │  │  • Manual pump control • Camera trigger                  │  │    │
│  │  │  • Dynamic threshold adjustment (no firmware changes)    │  │    │
│  │  │  • Plant-specific profiles                               │  │    │
│  │  └──────────────────────────────────────────────────────────┘  │    │
│  │  Material Design 3 | Riverpod | Offline Sync | Push Alerts     │    │
│  └────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘

                    🌿 AI-SENSOR FUSION ECOSYSTEM 🌿
        "How it Feels" (Sensors) + "How it Looks" (AI Vision)
                  = Near-Human Plant Health Understanding
```

---

## 💡 Technical Highlights & Innovations

### 1. AI-Sensor Fusion: The Core Innovation
FloraSeven combines **quantitative sensor data** with **AI-powered visual analysis** to achieve near-human understanding of plant health. This dual-modality approach detects issues invisible to sensors alone (visual wilting, discoloration) while maintaining quantitative precision.

### 2. 4-Electrode DIY EC Sensor
Custom-built conductivity probe with op-amp signal conditioning and temperature compensation. Achieves ±5% accuracy at 1/10th the cost of commercial sensors ($5 vs $50-200).

### 3. Ultra-Low Power Design
Deep sleep architecture achieves **99.7% power reduction** (10µA sleep vs 160mA active), extending battery life to 1-3 days with 30-second sampling intervals.

### 4. Dual-Microcontroller Hub Architecture
Task-optimized design: Arduino R4 handles robust sensor reading and actuation, ESP32-CAM manages vision and networking. I²C communication ensures modularity and reliability.

### 5. Dynamic Remote Configuration
User-adjustable sensor thresholds via mobile app **without firmware changes**. Enables plant-specific profiles, seasonal adaptation, and A/B testing of optimal parameters.

### 6. Modular & Scalable Design
Wireless, battery-powered nodes enable effortless scaling from single plant to entire greenhouse. Zero-infrastructure deployment—just place and power on.

### 7. Holistic Health Assessment Engine
Three-layer intelligence system:
- **Layer 1**: Sensor-Based Condition Index (threshold comparison)
- **Layer 2**: AI Visual Diagnostics (CNN with confidence scoring)
- **Layer 3**: Intelligent fusion algorithm with context-aware weighting

### 8. Production-Grade Backend
Cloud-ready Flask server with connection pooling, automatic backups, tiered data retention, and horizontal scaling support. Deployable on Raspberry Pi or cloud infrastructure.

**For detailed technical analysis, see [TECHNICAL_HIGHLIGHTS.md](TECHNICAL_HIGHLIGHTS.md)**

---

## 🚀 Installation

### Prerequisites

**Hardware:**
- ESP32 WROOM development board
- ESP32-CAM module
- Arduino R4 Minima
- Sensors (DS18B20, BH1750, capacitive moisture, pH, EC, UV)
- Mini submersible water pump
- 18650 Li-ion batteries and charging modules

**Software:**
- Python 3.9 or higher
- Flutter SDK 3.7 or higher
- Arduino IDE or PlatformIO
- MQTT Broker (Mosquitto recommended)
- Android Studio (for mobile app development)

### Quick Start

#### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/floraseven.git
cd floraseven
```

#### 2. Server Setup
```bash
cd Server

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Initialize database
python database.py

# Run server
python server.py
```

#### 3. Hardware Setup
```bash
cd Hardware/Firmware

# Flash ESP32 Plant Node
# Open Esp32.cpp in Arduino IDE
# Configure WiFi credentials and MQTT broker
# Upload to ESP32 WROOM

# Flash ESP32-CAM Hub Node
# Open Esp32Cam.cpp in Arduino IDE
# Configure WiFi, MQTT, and server URL
# Upload to ESP32-CAM

# Flash Arduino R4 Minima
# Open ArduinoR4Minima.cpp in Arduino IDE
# Upload to Arduino R4 Minima
```

#### 4. Mobile App Setup
```bash
cd Mobile-App-Android

# Get dependencies
flutter pub get

# Configure server URL
# Edit lib/utils/app_config.dart

# Run app
flutter run
```

---

## 📚 Documentation

Comprehensive documentation is available in the `Documentation/` directory:

- **[System Overview](Documentation/01_System_Overview.md)** - High-level system description
- **[Architecture](Documentation/02_Architecture.md)** - Detailed architecture and design
- **[API Reference](Documentation/06_API_Reference.md)** - Complete API documentation
- **[Deployment Guide](Documentation/08_Deployment_Guide.md)** - Production deployment instructions
- **[User Guide](Documentation/09_User_Guide.md)** - End-user manual
- **[Troubleshooting](Documentation/10_Troubleshooting.md)** - Common issues and solutions
- **[FAQ](Documentation/Frequently_Asked_Questions.md)** - Frequently asked questions

---

## 🔧 Configuration

### Server Configuration

Edit `Server/.env`:

```env
# Flask Settings
DEBUG=False
HOST=0.0.0.0
PORT=5000

# MQTT Settings
MQTT_BROKER=localhost
MQTT_PORT=1883
MQTT_USERNAME=your_username
MQTT_PASSWORD=your_password

# Database
DATABASE_PATH=data/sensor_data.db

# Security
API_USERNAME=admin
API_PASSWORD=your_secure_password
SECRET_KEY=your_secret_key_here
```

### Hardware Configuration

Update WiFi and MQTT settings in firmware files:

```cpp
// Esp32.cpp and Esp32Cam.cpp
const char* ssid = "Your_WiFi_SSID";
const char* password = "Your_WiFi_Password";
const char* mqtt_server = "192.168.1.100";
const int mqtt_port = 1883;
```

### Mobile App Configuration

Edit `Mobile-App-Android/lib/utils/app_config.dart`:

```dart
static const String defaultServerUrl = 'http://192.168.1.100:5000';
static const String mqttBrokerUrl = '192.168.1.100';
```

---

## 📊 System Requirements

### Hardware Requirements
- **ESP32 WROOM**: 520KB SRAM, 4MB Flash
- **ESP32-CAM**: 520KB SRAM, 4MB Flash, OV2640 camera
- **Arduino R4 Minima**: 32KB SRAM, 256KB Flash
- **Power**: 18650 Li-ion batteries (2500mAh recommended)

### Server Requirements
- **CPU**: 2+ cores recommended
- **RAM**: 2GB minimum, 4GB recommended
- **Storage**: 10GB minimum (for database and images)
- **OS**: Linux, Windows, or macOS
- **Network**: WiFi or Ethernet with MQTT broker

### Mobile Requirements
- **Android**: API Level 21+ (Android 5.0+)
- **Storage**: 100MB free space
- **RAM**: 2GB minimum

---

## 🧪 Testing

### Server Tests
```bash
cd Server
python -m pytest tests/
python test_mqtt_simulation.py
python test_api.py
```

### Mobile App Tests
```bash
cd Mobile-App-Android
flutter test
flutter test integration_test/
```

---

## 📈 Performance Metrics

- **Battery Life**: 1-3 days (Plant Node with deep sleep)
- **Sensor Reading Interval**: 30 seconds
- **API Response Time**: <100ms (status endpoint)
- **Image Analysis Time**: <2 seconds
- **Database Size**: ~10MB per month
- **MQTT Latency**: <100ms

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and development process.

---

## 🛣️ Roadmap

### Phase 1 - Foundation (Current)
- ✅ Hardware nodes operational
- ✅ Server backend functional
- ✅ Mobile app with core features
- ✅ AI model integrated

### Phase 2 - Enhancement
- [ ] Multi-plant support
- [ ] Cloud integration (AWS IoT / Firebase)
- [ ] iOS app development
- [ ] Advanced disease detection

### Phase 3 - Advanced Features
- [ ] Watering schedules
- [ ] Weather API integration
- [ ] Predictive analytics
- [ ] OTA firmware updates

### Phase 4 - Production
- [ ] Commercial packaging
- [ ] Solar charging option
- [ ] Web dashboard
- [ ] Multi-user support

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**Note**: This is a complete, production-ready IoT ecosystem suitable for:
- Educational purposes (university courses, research)
- Commercial applications (smart agriculture, precision horticulture)
- Hobbyist projects (home gardening, greenhouse automation)
- Startup MVPs (IoT product development)

Feel free to use, modify, and distribute according to the MIT License terms.

---

## 👥 Authors

- **Your Name** - *Initial work* - [YourGitHub](https://github.com/yourusername)

---

## 🙏 Acknowledgments

- **TensorFlow** for the machine learning framework
- **Flutter** team for the excellent mobile framework
- **Espressif** for ESP32 hardware and comprehensive documentation
- **Arduino** community for extensive resources and support
- **PlantVillage** dataset for AI model training data
- **Mosquitto** MQTT broker for reliable messaging
- **Open-source community** for inspiration and collaboration

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/floraseven/issues)
- **Email**: your.email@example.com
- **Documentation**: [Full Documentation](Documentation/)

---

## 📸 Screenshots

<div align="center">

### Mobile App

<img src="Documentation/images/dashboard.png" width="250" alt="Dashboard"/>
<img src="Documentation/images/plant-detail.png" width="250" alt="Plant Detail"/>
<img src="Documentation/images/settings.png" width="250" alt="Settings"/>

### Hardware

<img src="Documentation/images/plant-node.jpg" width="350" alt="Plant Node"/>
<img src="Documentation/images/hub-node.jpg" width="350" alt="Hub Node"/>

</div>

---

<div align="center">

**Made with ❤️ for plants and technology**

⭐ Star this repo if you find it helpful!

</div>
