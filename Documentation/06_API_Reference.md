# FloraSeven API Reference

This document provides a comprehensive reference for the FloraSeven REST API, which is used by the mobile application to communicate with the server.

## API Overview

The FloraSeven API is a RESTful API that follows standard HTTP conventions:

- Uses JSON for request and response bodies
- Uses standard HTTP methods (GET, POST, PUT, DELETE)
- Uses standard HTTP status codes
- Requires authentication for most endpoints
- Provides detailed error responses

## Base URL

All API endpoints are relative to the base URL:

```
http://<server-ip>:5000/api/v1
```

Where `<server-ip>` is the IP address of the server running the FloraSeven server application.

## Authentication

Most API endpoints require authentication. The FloraSeven API uses session-based authentication.

### Login

```
POST /login
```

Authenticates a user and creates a session.

#### Request Body

```json
{
  "username": "admin",
  "password": "password"
}
```

#### Response

```json
{
  "success": true,
  "message": "Login successful",
  "username": "admin"
}
```

#### Status Codes

- `200 OK`: Login successful
- `401 Unauthorized`: Invalid credentials
- `400 Bad Request`: Missing username or password

### Logout

```
POST /logout
```

Invalidates the current session.

#### Response

```json
{
  "success": true,
  "message": "Logout successful"
}
```

#### Status Codes

- `200 OK`: Logout successful
- `500 Internal Server Error`: Error processing logout

## System Status

### Get System Status

```
GET /status
```

Returns the current system status, including sensor data, plant health, and hardware status.

#### Response

```json
{
  "timestamp": "2025-04-16T12:34:56.789Z",
  "plantNode": {
    "moisture": 45.2,
    "temperatureSoil": 22.5,
    "lightLux": 1250,
    "ecConductivity": 1.2
  },
  "hubNode": {
    "phWater": 6.8,
    "uvAmbient": 0.5
  },
  "health": {
    "overallScore": 85,
    "status": "Good",
    "issues": []
  },
  "latestImage": {
    "url": "/api/v1/image/latest",
    "timestamp": "2025-04-16T12:30:00.000Z"
  },
  "pumpStatus": {
    "active": false,
    "lastActivated": "2025-04-16T10:15:00.000Z"
  },
  "power": {
    "plantNodeBattery": 85,
    "hubNodeBattery": 90
  },
  "autoWateringEnabled": true
}
```

#### Status Codes

- `200 OK`: Status retrieved successfully
- `500 Internal Server Error`: Error retrieving status

## Images

### Get Latest Image

```
GET /image/latest
```

Returns the latest plant image.

#### Response

The response is the image file (JPEG format).

#### Status Codes

- `200 OK`: Image retrieved successfully
- `404 Not Found`: No image found
- `500 Internal Server Error`: Error retrieving image

### Upload Image

```
POST /upload_image
```

Uploads a plant image for analysis.

#### Request

The request should be a multipart form with a file field named `file` containing the image.

#### Response

```json
{
  "success": true,
  "filename": "plant_image_20250416123456.jpg",
  "analysis": {
    "health_label": "Healthy",
    "health_score": 85,
    "confidence": 0.92,
    "issues_detected": []
  }
}
```

#### Status Codes

- `200 OK`: Image uploaded and analyzed successfully
- `400 Bad Request`: No file or invalid file
- `500 Internal Server Error`: Error processing image

## Settings

### Get Thresholds

```
GET /settings/thresholds
```

Returns the current threshold settings for all sensors.

#### Response

```json
{
  "moisture": {
    "min": 30,
    "max": 70,
    "unit": "%"
  },
  "temperature": {
    "min": 18,
    "max": 28,
    "unit": "°C"
  },
  "light": {
    "min": 500,
    "max": 10000,
    "unit": "lux"
  },
  "ph": {
    "min": 6.0,
    "max": 7.5,
    "unit": "pH"
  },
  "ec": {
    "min": 0.8,
    "max": 1.5,
    "unit": "mS/cm"
  }
}
```

#### Status Codes

- `200 OK`: Thresholds retrieved successfully
- `500 Internal Server Error`: Error retrieving thresholds

### Update Thresholds

```
POST /settings/thresholds
```

Updates the threshold settings for sensors.

#### Request Body

```json
{
  "moisture": {
    "min": 35,
    "max": 65
  },
  "temperature": {
    "min": 20,
    "max": 26
  }
}
```

Note: You can update any subset of thresholds.

#### Response

```json
{
  "success": true,
  "message": "Thresholds updated successfully",
  "updated_parameters": ["moisture", "temperature"]
}
```

#### Status Codes

- `200 OK`: Thresholds updated successfully
- `400 Bad Request`: Invalid threshold values
- `500 Internal Server Error`: Error updating thresholds

## Commands

### Water Command

```
POST /command/water
```

Sends a command to control the water pump.

#### Request Body

```json
{
  "state": "ON",
  "duration_sec": 5
}
```

or

```json
{
  "state": "OFF"
}
```

#### Response

```json
{
  "success": true,
  "message": "Water command sent successfully",
  "command": {
    "state": "ON",
    "duration_sec": 5
  }
}
```

#### Status Codes

- `200 OK`: Command sent successfully
- `400 Bad Request`: Invalid command parameters
- `500 Internal Server Error`: Error sending command

### Capture Image Command

```
POST /command/capture_image
```

Sends a command to capture a new plant image.

#### Request Body

```json
{
  "resolution": "high",
  "flash": false
}
```

Both parameters are optional.

#### Response

```json
{
  "success": true,
  "message": "Capture image command sent successfully",
  "command": {
    "resolution": "high",
    "flash": false
  }
}
```

#### Status Codes

- `200 OK`: Command sent successfully
- `500 Internal Server Error`: Error sending command

### Read Now Command

```
POST /command/read_now
```

Sends a command to force an immediate sensor reading.

#### Request Body

Empty or `{}`.

#### Response

```json
{
  "success": true,
  "message": "Read now command sent successfully"
}
```

#### Status Codes

- `200 OK`: Command sent successfully
- `500 Internal Server Error`: Error sending command

## Visualization

### Sensor Chart

```
GET /visualization/sensor/<node_id>/<sensor_type>
```

Returns chart data for a specific sensor.

#### Parameters

- `node_id`: Identifier for the node (e.g., `plant`, `hub`)
- `sensor_type`: Type of sensor (e.g., `moisture`, `temperature`, `light`, `ph`, `ec`, `uv`)

#### Query Parameters

- `hours`: Number of hours of data to include (default: 24)

#### Response

```json
{
  "success": true,
  "chart_data": {
    "title": "Soil Moisture (Last 24 Hours)",
    "x_label": "Time",
    "y_label": "Moisture (%)",
    "data": [
      {
        "x": "2025-04-16T00:00:00Z",
        "y": 45.2
      },
      {
        "x": "2025-04-16T01:00:00Z",
        "y": 44.8
      },
      // ... more data points
    ],
    "thresholds": {
      "min": 30,
      "max": 70
    }
  }
}
```

#### Status Codes

- `200 OK`: Chart data retrieved successfully
- `500 Internal Server Error`: Error generating chart

### Health Chart

```
GET /visualization/health
```

Returns chart data showing plant health history.

#### Query Parameters

- `days`: Number of days of data to include (default: 7)

#### Response

```json
{
  "success": true,
  "chart_data": {
    "title": "Plant Health History (Last 7 Days)",
    "x_label": "Date",
    "y_label": "Health Score",
    "data": [
      {
        "x": "2025-04-10",
        "y": 82
      },
      {
        "x": "2025-04-11",
        "y": 85
      },
      // ... more data points
    ]
  }
}
```

#### Status Codes

- `200 OK`: Chart data retrieved successfully
- `500 Internal Server Error`: Error generating chart

### Dashboard

```
GET /visualization/dashboard
```

Returns a dashboard with multiple charts.

#### Response

```json
{
  "success": true,
  "dashboard": {
    "moisture_chart": {
      // ... chart data
    },
    "temperature_chart": {
      // ... chart data
    },
    "light_chart": {
      // ... chart data
    },
    "health_chart": {
      // ... chart data
    }
  }
}
```

#### Status Codes

- `200 OK`: Dashboard data retrieved successfully
- `500 Internal Server Error`: Error generating dashboard

## Error Handling

All API endpoints return appropriate HTTP status codes and error messages in case of failure.

### Error Response Format

```json
{
  "error": "Error message describing the problem"
}
```

### Common Error Codes

- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication required
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server-side error

## MQTT Topics

While not part of the REST API, the following MQTT topics are used for communication between the server and hardware nodes:

### Subscriptions (Server subscribes to)

- `floraSeven/plant/node1/data`: Plant Node sensor data
- `floraSeven/hub/status`: Hub Node status
- `floraSeven/hub/cam/image_status`: Image metadata after upload

### Publications (Server publishes to)

- `floraSeven/command/hub/pump`: Pump control commands
- `floraSeven/command/hub/captureImage`: Image capture commands
- `floraSeven/command/plant/node1/readNow`: Force read commands

## API Versioning

The API is versioned using the URL path (`/api/v1/`). Future versions will use different version identifiers (e.g., `/api/v2/`).

## Rate Limiting

Currently, there is no rate limiting implemented for the API. However, clients should avoid making excessive requests to prevent server overload.

## Pagination

Currently, there is no pagination implemented for the API. All data is returned in a single response.

## Caching

The server does not implement caching headers. Clients should implement their own caching strategies if needed.

## Cross-Origin Resource Sharing (CORS)

The server implements CORS to allow cross-origin requests from any origin. This is suitable for development but may be restricted in production.

## API Changes and Deprecation

API changes and deprecations will be communicated through version changes. The current API version is v1.

## API Testing

The server includes a test suite for API endpoints. Clients can also use tools like Postman or curl to test the API manually.
