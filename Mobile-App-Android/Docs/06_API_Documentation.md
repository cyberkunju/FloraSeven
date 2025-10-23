# API Documentation

This document provides detailed information about the API endpoints used in the IoT Plant Monitoring and Watering System. These endpoints are implemented by both the ESP32 hardware and the Python demo server, ensuring consistent behavior across both implementations.

## API Overview

The system uses a RESTful API over HTTP for communication between the mobile application and the server (either the ESP32 hardware or the demo server). The API provides endpoints for:

1. Retrieving plant status
2. Triggering watering
3. Configuring auto-watering settings

## Base URL

The base URL for API requests depends on the server's IP address and port:

- **Hardware Implementation**: `http://<esp32-ip-address>/api`
- **Demo Server**: `http://<server-ip-address>:8080/api`

The mobile application discovers the server using mDNS, so users don't need to manually enter the IP address.

## Authentication

The current API implementation does not include authentication. This is suitable for home networks but should be enhanced with proper authentication if deployed in more sensitive environments.

## API Endpoints

### 1. Get Plant Status

Retrieves the current status of the plant, including moisture level and system information.

**Endpoint**: `/api/status`

**Method**: GET

**Request Parameters**: None

**Response Format**:
```json
{
  "moisturePercent": 45,
  "isWatering": false,
  "autoWateringEnabled": true,
  "lastUpdated": 1617293456789,
  "isConnected": true,
  "systemStatus": "OK"
}
```

**Response Fields**:
- `moisturePercent` (integer): Current soil moisture level as a percentage (0-100%)
- `isWatering` (boolean): Whether watering is currently in progress
- `autoWateringEnabled` (boolean): Whether auto-watering is enabled
- `lastUpdated` (integer): Timestamp of the last update in milliseconds since epoch
- `isConnected` (boolean): Whether the system is connected and operational
- `systemStatus` (string): System status message ("OK", "ERROR", etc.)

**Status Codes**:
- 200: Success
- 500: Server error

**Example Request**:
```bash
curl -X GET http://192.168.1.100:8080/api/status
```

**Example Response**:
```json
{
  "moisturePercent": 45,
  "isWatering": false,
  "autoWateringEnabled": true,
  "lastUpdated": 1617293456789,
  "isConnected": true,
  "systemStatus": "OK"
}
```

### 2. Trigger Watering

Triggers the water pump to water the plant.

**Endpoint**: `/api/water`

**Method**: POST

**Request Parameters**: None

**Request Body**: None

**Response Format**:
```json
{
  "success": true
}
```

**Response Fields**:
- `success` (boolean): Whether the watering was successfully triggered

**Status Codes**:
- 200: Success
- 400: Bad request (e.g., watering already in progress)
- 500: Server error

**Example Request**:
```bash
curl -X POST http://192.168.1.100:8080/api/water
```

**Example Response**:
```json
{
  "success": true
}
```

### 3. Configure Auto-Watering

Enables or disables the auto-watering feature.

**Endpoint**: `/api/auto_watering`

**Method**: POST

**Request Body**:
```json
{
  "enabled": true
}
```

**Request Fields**:
- `enabled` (boolean): Whether to enable (true) or disable (false) auto-watering

**Response Format**:
```json
{
  "success": true
}
```

**Response Fields**:
- `success` (boolean): Whether the auto-watering setting was successfully updated

**Status Codes**:
- 200: Success
- 400: Bad request (e.g., missing or invalid parameters)
- 500: Server error

**Example Request**:
```bash
curl -X POST -H "Content-Type: application/json" -d '{"enabled": true}' http://192.168.1.100:8080/api/auto_watering
```

**Example Response**:
```json
{
  "success": true
}
```

## Error Handling

The API uses standard HTTP status codes to indicate success or failure. In case of an error, the response body will contain an error message:

```json
{
  "error": "Error message describing what went wrong"
}
```

Common error scenarios include:

1. **Server Unreachable**: The mobile app cannot connect to the server
2. **Watering Already in Progress**: Attempting to trigger watering when it's already active
3. **Invalid Parameters**: Missing or invalid parameters in the request
4. **Server Error**: Internal error in the server

## Rate Limiting

The current implementation does not include rate limiting. However, the mobile application should implement reasonable polling intervals (e.g., 5 seconds) to avoid overwhelming the server, especially when running on the ESP32 hardware.

## Versioning

The current API does not include versioning in the URL path. Future versions of the API should consider adding versioning (e.g., `/api/v1/status`) to ensure backward compatibility.

## API Implementation Details

### ESP32 Hardware Implementation

The ESP32 hardware implements the API using the Arduino WebServer library. The implementation can be found in the `web_server.h` file in the firmware directory.

Key aspects of the implementation:

1. **JSON Serialization**: Uses the ArduinoJson library for parsing and generating JSON
2. **Concurrency**: Handles requests in the main loop, which may limit concurrent requests
3. **Error Handling**: Provides basic error handling with appropriate HTTP status codes

### Demo Server Implementation

The demo server implements the API using Flask, a Python web framework. The implementation can be found in the `server.py` file in the demo_server directory.

Key aspects of the implementation:

1. **JSON Serialization**: Uses Flask's built-in JSON handling
2. **Simulation**: Simulates plant behavior, including moisture changes and watering effects
3. **Concurrency**: Uses Flask's development server, which has limited concurrency

## Testing the API

You can test the API using various tools:

### Using curl

```bash
# Get status
curl -X GET http://192.168.1.100:8080/api/status

# Trigger watering
curl -X POST http://192.168.1.100:8080/api/water

# Enable auto-watering
curl -X POST -H "Content-Type: application/json" -d '{"enabled": true}' http://192.168.1.100:8080/api/auto_watering
```

### Using Postman

1. Create a new request
2. Set the request method (GET or POST)
3. Enter the URL (e.g., `http://192.168.1.100:8080/api/status`)
4. For POST requests with a body, select "Body" > "raw" > "JSON" and enter the JSON payload
5. Click "Send"

### Using the Mobile App

The mobile application provides a user-friendly interface for interacting with the API. You can:

1. View the current status on the plant detail screen
2. Trigger watering using the "Water Now" button
3. Enable/disable auto-watering using the toggle switch

## Future API Enhancements

Potential enhancements for future versions of the API:

1. **Authentication**: Add token-based authentication for secure access
2. **HTTPS Support**: Add encryption for secure communication
3. **Watering History**: Add endpoints to retrieve watering history
4. **Configuration**: Add endpoints to configure system parameters (e.g., watering duration)
5. **Multiple Plants**: Extend the API to support multiple plants with unique identifiers
6. **Webhooks**: Add support for webhooks to notify external systems of events
7. **GraphQL**: Consider implementing a GraphQL API for more flexible queries
