# FloraSeven v1.0 - MQTT Protocol Specification

## Overview

The FloraSeven system uses MQTT (Message Queuing Telemetry Transport) for communication between the hardware nodes (Plant Node and Hub Node) and the laptop server backend. This document specifies the MQTT protocol used in the FloraSeven v1.0 prototype.

## MQTT Broker Configuration

- **Broker**: Mosquitto
- **Address**: localhost (127.0.0.1)
- **Port**: 1883 (default, unencrypted)
- **QoS**: 1 (At least once delivery)
- **Retain**: False (unless otherwise specified)

## Topic Structure

The FloraSeven MQTT topics follow a hierarchical structure:

```
floraSeven/[node_type]/[node_id]/[data_type]
floraSeven/command/[node_type]/[node_id]/[command_type]
```

Where:
- `node_type`: Either "plant" or "hub"
- `node_id`: Identifier for the specific node (e.g., "node1")
- `data_type`: Type of data being transmitted (e.g., "data", "status")
- `command_type`: Type of command being sent (e.g., "pump", "captureImage")

## Data Topics

### Plant Node Data

**Topic**: `floraSeven/plant/node1/data`

**Payload**: JSON object with the following fields:
- `timestamp`: ISO8601 timestamp (e.g., "2025-04-15T10:30:05Z")
- `nodeId`: Identifier for the node (e.g., "plantNode1")
- `moisture`: Soil moisture percentage (0-100)
- `temp_soil`: Soil temperature in Celsius
- `light_lux`: Light level in lux
- `ec_raw`: Electrical conductivity raw reading (relative value, higher = higher conductivity)

**Example**:
```json
{
  "timestamp": "2025-04-15T10:30:05Z",
  "nodeId": "plantNode1",
  "moisture": 62.1,
  "temp_soil": 23.5,
  "light_lux": 18000,
  "ec_raw": 1150
}
```

**Frequency**: Every 30 seconds

### Hub Node Status

**Topic**: `floraSeven/hub/status`

**Payload**: JSON object with the following fields:
- `timestamp`: ISO8601 timestamp (e.g., "2025-04-15T10:30:10Z")
- `nodeId`: Identifier for the node (e.g., "hubNode")
- `ph_water`: Water pH level
- `uv_ambient`: Ambient UV level
- `pump_active`: Boolean indicating if the pump is active

**Example**:
```json
{
  "timestamp": "2025-04-15T10:30:10Z",
  "nodeId": "hubNode",
  "ph_water": 6.7,
  "uv_ambient": 0.9,
  "pump_active": false
}
```

**Frequency**: Every 30 seconds

### Hub Node Image Status

**Topic**: `floraSeven/hub/cam/image_status`

**Payload**: JSON object with the following fields:
- `timestamp`: ISO8601 timestamp
- `success`: Boolean indicating if the image was successfully uploaded
- `filename`: Name of the uploaded image file
- `error`: Error message (only present if success is false)

**Example**:
```json
{
  "timestamp": "2025-04-15T10:35:00Z",
  "success": true,
  "filename": "plant_image_20250415103500.jpg"
}
```

**Frequency**: After each image capture and upload attempt

## Command Topics

### Water Pump Control

**Topic**: `floraSeven/command/hub/pump`

**Payload**: JSON object with the following fields:
- `state`: "ON" or "OFF"
- `duration_sec`: Duration in seconds (optional when state is "ON", default is 3 seconds)

**Example**:
```json
{
  "state": "ON",
  "duration_sec": 5
}
```

**Alternative Simple Payload**: Simple string "ON" or "OFF"

**Direction**: From laptop server to Hub Node

### Image Capture Command

**Topic**: `floraSeven/command/hub/captureImage`

**Payload**: JSON object with optional parameters:
- `resolution`: Image resolution (optional, e.g., "high", "medium", "low")
- `flash`: Boolean indicating if flash should be used (optional)

**Example**:
```json
{
  "resolution": "high",
  "flash": false
}
```

**Alternative Simple Payload**: Empty payload or empty JSON object `{}`

**Direction**: From laptop server to Hub Node

### Force Sensor Reading

**Topic**: `floraSeven/command/plant/node1/readNow`

**Payload**: Empty payload or empty JSON object `{}`

**Direction**: From laptop server to Plant Node

## Message Handling

### Server-side Handling

The laptop server backend should:

1. Connect to the Mosquitto broker on startup
2. Subscribe to all data topics
3. Implement the following callback functions:
   - `on_connect`: Subscribe to topics when connected
   - `on_message`: Process incoming messages
   - `on_disconnect`: Handle disconnections and reconnect

### Message Processing

For each incoming message, the server should:

1. Decode the payload from UTF-8
2. Parse the JSON
3. Validate the message structure
4. Extract the data
5. Store the data in the database
6. Update the system state
7. Trigger any necessary actions

### Command Publishing

To send commands to hardware nodes, the server should:

1. Format the command payload as JSON
2. Publish to the appropriate topic
3. Use QoS 1 to ensure delivery
4. Log the command for debugging

## Error Handling

### Connection Errors

If the connection to the MQTT broker is lost, the server should:

1. Log the disconnection
2. Attempt to reconnect with exponential backoff
3. Resubscribe to topics upon reconnection

### Message Parsing Errors

If a message cannot be parsed, the server should:

1. Log the error with the raw message
2. Discard the message
3. Continue processing other messages

### Command Delivery Errors

If a command cannot be delivered, the server should:

1. Log the error
2. Retry the command (if appropriate)
3. Notify the user via the API

## Security Considerations

For the v1.0 prototype running on a local network, security is minimal:

- No authentication is required for MQTT connections
- No encryption is used for MQTT messages
- The system relies on network-level security (local Wi-Fi)

Future versions should implement:

- TLS encryption for MQTT (port 8883)
- Username/password authentication
- Access control lists (ACLs) for topics
- Possibly client certificate authentication

## Testing

To test MQTT communication:

1. Use Mosquitto command-line tools:
   ```bash
   # Subscribe to all topics
   mosquitto_sub -t "floraSeven/#" -v

   # Publish test data
   mosquitto_pub -t "floraSeven/plant/node1/data" -m '{"timestamp":"2025-04-15T10:30:05Z","nodeId":"plantNode1","moisture":62.1,"temp_soil":23.5,"light_lux":18000,"ec_raw":1150}'
   ```

2. Use MQTT Explorer for visual monitoring of topics and messages

3. Implement a test script to simulate hardware nodes:
   ```python
   import paho.mqtt.client as mqtt
   import json
   import time
   from datetime import datetime

   # Connect to broker
   client = mqtt.Client()
   client.connect("localhost", 1883, 60)

   # Simulate Plant Node data
   while True:
       payload = {
           "timestamp": datetime.now().isoformat(),
           "nodeId": "plantNode1",
           "moisture": 62.1,
           "temp_soil": 23.5,
           "light_lux": 18000,
           "ec_raw": 1150
       }
       client.publish("floraSeven/plant/node1/data", json.dumps(payload))
       time.sleep(5)  # Send every 5 seconds for testing
   ```
