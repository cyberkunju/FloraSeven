# Demo Server

This document provides detailed information about the Python-based demo server component of the IoT Plant Monitoring and Watering System. The demo server simulates the hardware component for development and testing purposes.

## Overview

The demo server is a Python application that mimics the behavior of the ESP32 hardware. It provides the same API endpoints and uses mDNS for service discovery, allowing the mobile app to interact with it just like it would with the actual hardware.

## Features

- **API Endpoints**: Implements the same API endpoints as the ESP32 hardware
- **mDNS Service**: Advertises itself on the local network for automatic discovery
- **Moisture Simulation**: Simulates changing moisture levels based on watering events
- **Auto-Watering Logic**: Implements the same auto-watering logic as the hardware
- **Logging**: Provides detailed logs of all operations

## Technical Details

### Dependencies

The demo server requires the following Python packages:

```
Flask==2.0.1
zeroconf==0.38.4
requests==2.26.0
```

These dependencies are listed in the `requirements.txt` file.

### Project Structure

```
demo_server/
├── server.py              # Main server implementation
├── requirements.txt       # Python dependencies
├── start_server.bat       # Windows batch file to start the server
├── start_server.sh        # Linux/Mac shell script to start the server
└── README.md              # Server documentation
```

### Server Implementation

The demo server is implemented in `server.py`. Here's a breakdown of its key components:

#### Imports and Configuration

```python
import time
import json
import random
import threading
import socket
from flask import Flask, jsonify, request
from zeroconf import ServiceInfo, Zeroconf

# Configuration
HOST = '0.0.0.0'  # Listen on all interfaces
PORT = 8080
SERVICE_TYPE = '_plantmonitor._tcp.local.'
SERVICE_NAME = 'ESP32PlantMonitor'
```

#### Plant State Simulation

```python
# Simulated plant state
plant_state = {
    'moisture_percent': 50,
    'is_watering': False,
    'auto_watering_enabled': False,
    'last_updated': time.time(),
    'is_connected': True,
    'system_status': 'OK'
}

# Moisture simulation parameters
MOISTURE_DECREASE_RATE = 0.5  # % per minute
MOISTURE_INCREASE_RATE = 15   # % per watering
WATERING_DURATION = 5         # seconds
AUTO_WATERING_THRESHOLD = 30  # %
```

#### Moisture Simulation Thread

```python
def simulate_moisture():
    """Simulate moisture changes over time."""
    global plant_state
    
    while True:
        # Decrease moisture over time (if not watering)
        if not plant_state['is_watering']:
            # Calculate time since last update
            current_time = time.time()
            elapsed_minutes = (current_time - plant_state['last_updated']) / 60
            
            # Decrease moisture based on elapsed time
            decrease = MOISTURE_DECREASE_RATE * elapsed_minutes
            plant_state['moisture_percent'] = max(0, plant_state['moisture_percent'] - decrease)
            plant_state['last_updated'] = current_time
            
            # Check for auto-watering
            if (plant_state['auto_watering_enabled'] and 
                plant_state['moisture_percent'] < AUTO_WATERING_THRESHOLD):
                trigger_watering()
                print(f"Auto-watering triggered. Moisture: {plant_state['moisture_percent']:.1f}%")
        
        # Small random variation for realism
        plant_state['moisture_percent'] += random.uniform(-0.5, 0.5)
        plant_state['moisture_percent'] = max(0, min(100, plant_state['moisture_percent']))
        
        # Sleep for a short time
        time.sleep(5)
```

#### Watering Simulation

```python
def trigger_watering():
    """Simulate watering the plant."""
    global plant_state
    
    if plant_state['is_watering']:
        return False
    
    plant_state['is_watering'] = True
    
    # Start a thread to handle the watering process
    threading.Thread(target=watering_process, daemon=True).start()
    
    return True

def watering_process():
    """Simulate the watering process."""
    global plant_state
    
    # Wait for the watering duration
    time.sleep(WATERING_DURATION)
    
    # Increase moisture level
    plant_state['moisture_percent'] += MOISTURE_INCREASE_RATE
    plant_state['moisture_percent'] = min(100, plant_state['moisture_percent'])
    
    # Update state
    plant_state['is_watering'] = False
    plant_state['last_updated'] = time.time()
    
    print(f"Watering completed. New moisture: {plant_state['moisture_percent']:.1f}%")
```

#### Flask API Endpoints

```python
app = Flask(__name__)

@app.route('/api/status', methods=['GET'])
def get_status():
    """Return the current plant status."""
    return jsonify({
        'moisturePercent': int(plant_state['moisture_percent']),
        'isWatering': plant_state['is_watering'],
        'autoWateringEnabled': plant_state['auto_watering_enabled'],
        'lastUpdated': int(plant_state['last_updated'] * 1000),  # Convert to milliseconds
        'isConnected': plant_state['is_connected'],
        'systemStatus': plant_state['system_status']
    })

@app.route('/api/water', methods=['POST'])
def water_plant():
    """Trigger watering."""
    success = trigger_watering()
    return jsonify({'success': success})

@app.route('/api/auto_watering', methods=['POST'])
def set_auto_watering():
    """Enable or disable auto-watering."""
    try:
        data = request.get_json()
        if 'enabled' in data:
            plant_state['auto_watering_enabled'] = bool(data['enabled'])
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Missing enabled parameter'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400
```

#### mDNS Service Registration

```python
def register_mdns_service():
    """Register the mDNS service for discovery."""
    # Get local IP address
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    local_ip = s.getsockname()[0]
    s.close()
    
    # Create zeroconf service info
    service_info = ServiceInfo(
        SERVICE_TYPE,
        f"{SERVICE_NAME}.{SERVICE_TYPE}",
        addresses=[socket.inet_aton(local_ip)],
        port=PORT,
        properties={'path': '/'}
    )
    
    # Register service
    zeroconf = Zeroconf()
    zeroconf.register_service(service_info)
    
    print(f"Registered mDNS service: {SERVICE_NAME}.{SERVICE_TYPE}")
    
    return zeroconf, service_info
```

#### Main Function

```python
def main():
    """Main function to start the server."""
    # Start moisture simulation thread
    threading.Thread(target=simulate_moisture, daemon=True).start()
    
    # Register mDNS service
    zeroconf, service_info = register_mdns_service()
    
    try:
        # Print server information
        local_ip = socket.gethostbyname(socket.gethostname())
        print("\n=== ESP32-CAM Demo Server ===")
        print(f"Server running at: http://{local_ip}:{PORT}")
        print("API Endpoints:")
        print(f"  GET  http://{local_ip}:{PORT}/api/status")
        print(f"  POST http://{local_ip}:{PORT}/api/water")
        print(f"  POST http://{local_ip}:{PORT}/api/auto_watering")
        print("\nThe app will automatically discover this server on your local network")
        print("=== Press Ctrl+C to stop the server ===\n")
        
        # Start Flask app
        app.run(host=HOST, port=PORT, debug=True)
    
    except KeyboardInterrupt:
        print("\nShutting down server...")
    finally:
        # Unregister mDNS service
        zeroconf.unregister_service(service_info)
        zeroconf.close()

if __name__ == '__main__':
    main()
```

## Setup and Usage

### Installation

1. **Install Python**
   - Download and install Python 3.8 or higher from [python.org](https://www.python.org/downloads/)
   - Ensure Python is added to your PATH

2. **Install Dependencies**
   - Navigate to the demo_server directory
   - Run: `pip install -r requirements.txt`

### Starting the Server

#### Windows

1. **Using the Batch File**
   - Double-click `start_server.bat`
   - Or run from command prompt: `start_server.bat`

2. **Using Python Directly**
   - Open command prompt
   - Navigate to the demo_server directory
   - Run: `python server.py`

#### Linux/Mac

1. **Using the Shell Script**
   - Make the script executable: `chmod +x start_server.sh`
   - Run: `./start_server.sh`

2. **Using Python Directly**
   - Open terminal
   - Navigate to the demo_server directory
   - Run: `python3 server.py`

### Verifying the Server

Once the server is running, you should see output similar to:

```
Registered mDNS service: ESP32PlantMonitor._plantmonitor._tcp.local.

=== ESP32-CAM Demo Server ===
Server running at: http://192.168.1.100:8080
API Endpoints:
  GET  http://192.168.1.100:8080/api/status
  POST http://192.168.1.100:8080/api/water
  POST http://192.168.1.100:8080/api/auto_watering

The app will automatically discover this server on your local network
=== Press Ctrl+C to stop the server ===

 * Serving Flask app 'server' (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: on
 * Running on all addresses.
   WARNING: This is a development server. Do not use it in a production deployment.
 * Running on http://192.168.1.100:8080/ (Press CTRL+C to quit)
```

### Testing the API

You can test the API endpoints using curl or a tool like Postman:

#### Get Status

```bash
curl http://localhost:8080/api/status
```

Expected response:
```json
{
  "autoWateringEnabled": false,
  "isConnected": true,
  "isWatering": false,
  "lastUpdated": 1617293456789,
  "moisturePercent": 45,
  "systemStatus": "OK"
}
```

#### Trigger Watering

```bash
curl -X POST http://localhost:8080/api/water
```

Expected response:
```json
{
  "success": true
}
```

#### Set Auto-Watering

```bash
curl -X POST -H "Content-Type: application/json" -d '{"enabled": true}' http://localhost:8080/api/auto_watering
```

Expected response:
```json
{
  "success": true
}
```

## Customization

You can customize the demo server behavior by modifying the following parameters in `server.py`:

```python
# Moisture simulation parameters
MOISTURE_DECREASE_RATE = 0.5  # % per minute
MOISTURE_INCREASE_RATE = 15   # % per watering
WATERING_DURATION = 5         # seconds
AUTO_WATERING_THRESHOLD = 30  # %
```

- **MOISTURE_DECREASE_RATE**: How quickly the moisture level decreases over time
- **MOISTURE_INCREASE_RATE**: How much the moisture level increases after watering
- **WATERING_DURATION**: How long the watering process takes
- **AUTO_WATERING_THRESHOLD**: Moisture level below which auto-watering is triggered

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   - Error: `OSError: [Errno 98] Address already in use`
   - Solution: Change the PORT value in `server.py` or stop the process using the current port

2. **mDNS Registration Failure**
   - Error: `Error registering service`
   - Solution: Check firewall settings or try running with administrator privileges

3. **Network Discovery Issues**
   - Problem: Mobile app cannot discover the server
   - Solution: Ensure both devices are on the same network and check firewall settings

4. **Python Dependencies**
   - Error: `ModuleNotFoundError: No module named 'flask'`
   - Solution: Run `pip install -r requirements.txt` to install required packages

### Logs and Debugging

The demo server outputs logs to the console, including:
- Server startup information
- API endpoint access
- Watering events
- Auto-watering triggers
- Moisture level changes

For more detailed debugging, you can modify the Flask debug level in `server.py`:

```python
app.run(host=HOST, port=PORT, debug=True)  # Set debug=False to reduce log verbosity
```

## Security Considerations

The demo server is intended for development and testing purposes only. It lacks several security features that would be necessary for a production environment:

1. **No Authentication**: The API endpoints have no authentication
2. **No Encryption**: Communication is not encrypted (no HTTPS)
3. **Debug Mode**: Flask runs in debug mode, which can expose system information

**Do not** expose this server to the public internet or use it in a production environment.

## Performance Considerations

The demo server is designed for local development and testing. It has some limitations:

1. **Single-Threaded**: Flask's development server is single-threaded by default
2. **Limited Concurrency**: May not handle multiple simultaneous connections well
3. **Resource Usage**: The moisture simulation thread runs continuously

For testing with multiple clients, consider using a production WSGI server like Gunicorn or uWSGI.
