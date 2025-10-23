# FloraSeven v1.0 - API Specification

## Overview

The FloraSeven laptop server backend provides a REST API for the Flutter mobile app to interact with the system. This document specifies the API endpoints, request/response formats, and error handling. The API is implemented using Flask, a Python web framework.

## Base URL

```
http://<laptop-ip-address>:5000
```

Where `<laptop-ip-address>` is the IP address of the laptop running the server on the local network.

## Authentication

The API supports Basic Authentication. To access protected endpoints, include an Authorization header with your request:

```
Authorization: Basic <base64-encoded-credentials>
```

Where `<base64-encoded-credentials>` is the Base64 encoding of `username:password`.

Authentication can be enabled or disabled via the `ENABLE_AUTH` environment variable. When disabled, all endpoints are accessible without authentication.

## API Endpoints

### 1. Get System Status

**Endpoint**: `GET /api/v1/status`

**Description**: Get the latest system status, including sensor readings, thresholds, visual health assessment, condition index, and overall health.

**Request**: No parameters required.

**Response**:
```json
{
  "timestamp": "2025-04-15T10:45:30Z",
  "sensor_data": {
    "plant": {
      "moisture": 62.1,
      "temp_soil": 23.5,
      "light_lux": 18000,
      "ec_raw": 1150
    },
    "hub": {
      "ph_water": 6.7,
      "uv_ambient": 0.9,
      "pump_active": false
    }
  },
  "thresholds": {
    "moisture": {
      "min": 40.0,
      "max": 70.0
    },
    "temp_soil": {
      "min": 18.0,
      "max": 28.0
    },
    "light_lux": {
      "min": 5000.0,
      "max": 30000.0
    },
    "ph_water": {
      "min": 6.0,
      "max": 7.5
    }
  },
  "visual_health": {
    "latest_image": "plant_image_20250415103500.jpg",
    "health_label": "healthy",
    "health_score": 85,
    "confidence": 0.85,
    "timestamp": "2025-04-15T10:35:00Z"
  },
  "condition_index": {
    "moisture": {
      "status": "optimal",
      "value": 62.1,
      "min": 40.0,
      "max": 70.0
    },
    "temp_soil": {
      "status": "optimal",
      "value": 23.5,
      "min": 18.0,
      "max": 28.0
    },
    "light_lux": {
      "status": "optimal",
      "value": 18000,
      "min": 5000.0,
      "max": 30000.0
    },
    "ph_water": {
      "status": "optimal",
      "value": 6.7,
      "min": 6.0,
      "max": 7.5
    }
  },
  "overall_health": {
    "status": "healthy",
    "score": 90,
    "suggestions": [
      "Plant is healthy and all parameters are within optimal ranges."
    ]
  }
}
```

**Status Codes**:
- 200: Success
- 500: Server error

### 2. Get Latest Image

**Endpoint**: `GET /api/v1/image/latest`

**Description**: Get the latest plant image captured by the Hub Node.

**Request**: No parameters required.

**Response**: The image file (JPEG format) with appropriate content type.

**Status Codes**:
- 200: Success
- 404: No image found
- 500: Server error

### 3. Upload Image

**Endpoint**: `POST /api/v1/upload_image`

**Description**: Upload a plant image from the Hub Node for analysis.

**Request**:
- Content-Type: `multipart/form-data`
- Body: Form with a file field named "file" containing the image

**Response**:
```json
{
  "success": true,
  "filename": "plant_image_20250415103500.jpg",
  "analysis": {
    "health_label": "healthy",
    "health_score": 85,
    "confidence": 0.85
  }
}
```

**Status Codes**:
- 200: Success
- 400: Bad request (missing file, invalid format)
- 500: Server error

### 4. Get Thresholds

**Endpoint**: `GET /api/v1/settings/thresholds`

**Description**: Get the current threshold settings for all parameters.

**Request**: No parameters required.

**Response**:
```json
{
  "moisture": {
    "min": 40.0,
    "max": 70.0
  },
  "temp_soil": {
    "min": 18.0,
    "max": 28.0
  },
  "light_lux": {
    "min": 5000.0,
    "max": 30000.0
  },
  "ph_water": {
    "min": 6.0,
    "max": 7.5
  }
}
```

**Status Codes**:
- 200: Success
- 500: Server error

### 5. Update Thresholds

**Endpoint**: `POST /api/v1/settings/thresholds`

**Description**: Update the threshold settings for one or more parameters.

**Request**:
- Content-Type: `application/json`
- Body: JSON object with parameter thresholds to update

```json
{
  "moisture": {
    "min": 45.0,
    "max": 75.0
  },
  "ph_water": {
    "min": 6.2,
    "max": 7.2
  }
}
```

**Response**:
```json
{
  "success": true,
  "message": "Thresholds updated successfully",
  "updated_parameters": ["moisture", "ph_water"]
}
```

**Status Codes**:
- 200: Success
- 400: Bad request (invalid parameters or values)
- 500: Server error

### 6. Send Capture Image Command

**Endpoint**: `POST /api/v1/command/capture_image`

**Description**: Send a command to capture an image using the ESP32-CAM.

**Request**:
- Content-Type: `application/json`
- Body: JSON object with command parameters

```json
{
  "resolution": "high",  // Optional, default is medium
  "flash": false         // Optional, default is false
}
```

**Response**:
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

**Status Codes**:
- 200: Success
- 400: Bad request (invalid parameters)
- 500: Server error

### 7. Send Read Now Command

**Endpoint**: `POST /api/v1/command/read_now`

**Description**: Send a command to force a sensor reading from the Plant Node.

**Request**:
- Content-Type: `application/json`
- Body: Empty JSON object `{}`

**Response**:
```json
{
  "success": true,
  "message": "Read now command sent successfully"
}
```

**Status Codes**:
- 200: Success
- 500: Server error

### 8. Login

**Endpoint**: `POST /api/v1/login`

**Description**: Login to get an authentication token.

**Request**:
- Content-Type: `application/json`
- Body: JSON object with credentials

```json
{
  "username": "admin",
  "password": "floraseven"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Login successful",
  "username": "admin"
}
```

**Status Codes**:
- 200: Success
- 400: Bad request (missing username or password)
- 401: Unauthorized (invalid credentials)
- 500: Server error

### 9. Logout

**Endpoint**: `POST /api/v1/logout`

**Description**: Logout to invalidate the authentication token.

**Request**: No parameters required.

**Response**:
```json
{
  "success": true,
  "message": "Logout successful"
}
```

**Status Codes**:
- 200: Success
- 500: Server error

### 10. Get Sensor Chart

**Endpoint**: `GET /api/v1/visualization/sensor/<node_id>/<sensor_type>`

**Description**: Get a chart for a specific sensor.

**Parameters**:
- `node_id`: Identifier for the node (e.g., `plantNode1`, `hubNode`)
- `sensor_type`: Type of sensor (e.g., `moisture`, `temp_soil`, `light_lux`, `ec_raw`, `ph_water`, `uv_ambient`)
- `hours` (query parameter): Number of hours of data to include (default: 24)

**Response**:
```json
{
  "success": true,
  "chart_data": "base64-encoded-png-image"
}
```

**Status Codes**:
- 200: Success
- 500: Server error

### 11. Get Health Chart

**Endpoint**: `GET /api/v1/visualization/health`

**Description**: Get a chart showing plant health history.

**Parameters**:
- `days` (query parameter): Number of days of data to include (default: 7)

**Response**:
```json
{
  "success": true,
  "chart_data": "base64-encoded-png-image"
}
```

**Status Codes**:
- 200: Success
- 500: Server error

### 12. Get Dashboard

**Endpoint**: `GET /api/v1/visualization/dashboard`

**Description**: Get a dashboard with multiple charts.

**Response**:
```json
{
  "success": true,
  "dashboard": {
    "moisture_chart": "base64-encoded-png-image",
    "temperature_chart": "base64-encoded-png-image",
    "light_chart": "base64-encoded-png-image",
    "ec_chart": "base64-encoded-png-image",
    "ph_chart": "base64-encoded-png-image",
    "uv_chart": "base64-encoded-png-image",
    "health_chart": "base64-encoded-png-image"
  }
}
```

**Status Codes**:
- 200: Success
- 500: Server error

### 13. Send Water Command

**Endpoint**: `POST /api/v1/command/water`

**Description**: Send a command to control the water pump.

**Request**:
- Content-Type: `application/json`
- Body: JSON object with command parameters

```json
{
  "state": "ON",
  "duration_sec": 5  // Optional when state is "ON", default is 3 seconds
}
```

Note: If `duration_sec` is not provided when `state` is "ON", a default duration of 3 seconds will be used.

**Response**:
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

**Status Codes**:
- 200: Success
- 400: Bad request (invalid parameters)
- 500: Server error

## Data Models

### Sensor Data

```json
{
  "plant": {
    "moisture": 62.1,       // Soil moisture percentage (0-100)
    "temp_soil": 23.5,      // Soil temperature in Celsius
    "light_lux": 18000,     // Light level in lux
    "ec_raw": 1150          // Electrical conductivity raw reading (relative value)
  },
  "hub": {
    "ph_water": 6.7,        // Water pH level
    "uv_ambient": 0.9,      // Ambient UV level
    "pump_active": false    // Whether the pump is active
  }
}
```

### Thresholds

```json
{
  "moisture": {
    "min": 40.0,            // Minimum acceptable value
    "max": 70.0             // Maximum acceptable value
  },
  "temp_soil": {
    "min": 18.0,
    "max": 28.0
  },
  "light_lux": {
    "min": 5000.0,
    "max": 30000.0
  },
  "ph_water": {
    "min": 6.0,
    "max": 7.5
  }
}
```

### Visual Health

```json
{
  "latest_image": "plant_image_20250415103500.jpg",  // Filename of the latest image
  "health_label": "healthy",                        // Health classification
  "health_score": 85,                               // Health score (0-100)
  "confidence": 0.85,                               // Confidence of the classification (0-1)
  "timestamp": "2025-04-15T10:35:00Z"               // When the image was captured
}
```

### Condition Index

```json
{
  "moisture": {
    "status": "optimal",    // "optimal", "warning", or "critical"
    "value": 62.1,          // Current value
    "min": 40.0,            // Minimum threshold
    "max": 70.0             // Maximum threshold
  },
  // Other parameters follow the same structure
}
```

### Overall Health

```json
{
  "status": "healthy",      // "healthy", "needs_attention", or "critical"
  "score": 90,              // Overall health score (0-100)
  "suggestions": [          // Array of suggestion strings
    "Plant is healthy and all parameters are within optimal ranges."
  ]
}
```

## Error Handling

All API endpoints return errors in a consistent format:

```json
{
  "error": "Error message describing what went wrong",
  "code": "ERROR_CODE"      // Optional error code
}
```

Common error codes:
- `INVALID_REQUEST`: Request format or parameters are invalid
- `RESOURCE_NOT_FOUND`: Requested resource does not exist
- `INTERNAL_ERROR`: Server encountered an unexpected error
- `DATABASE_ERROR`: Error accessing or writing to the database
- `MQTT_CONNECTION_ERROR`: Error connecting to the MQTT broker
- `MQTT_PUBLISH_FAILED`: Failed to publish message to MQTT topic
- `AI_MODEL_ERROR`: Error loading or using the AI model
- `AI_ANALYSIS_ERROR`: Error analyzing an image
- `IMAGE_PROCESSING_ERROR`: Error processing or saving an image
- `INVALID_THRESHOLD`: Threshold value is outside acceptable range

## Rate Limiting

For the v1.0 prototype, no rate limiting is implemented. The API can be called as frequently as needed.

## Versioning

The API is versioned in the URL path (`/api/v1/`). Future versions will use `/api/v2/`, etc.

## Testing

The API can be tested using:

1. **Postman/Insomnia**: For manual testing of endpoints
2. **curl**: For command-line testing

Example curl commands:

```bash
# Get system status
curl -X GET http://localhost:5000/api/v1/status

# Get latest image
curl -X GET http://localhost:5000/api/v1/image/latest --output latest_image.jpg

# Upload image
curl -X POST http://localhost:5000/api/v1/upload_image -F "file=@test_image.jpg"

# Get thresholds
curl -X GET http://localhost:5000/api/v1/settings/thresholds

# Update thresholds
curl -X POST http://localhost:5000/api/v1/settings/thresholds \
  -H "Content-Type: application/json" \
  -d '{"moisture":{"min":45.0,"max":75.0}}'

# Send water command
curl -X POST http://localhost:5000/api/v1/command/water \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic YWRtaW46ZmxvcmFzZXZlbg==" \
  -d '{"state":"ON","duration_sec":5}'

# Login
curl -X POST http://localhost:5000/api/v1/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"floraseven"}'

# Get sensor chart
curl -X GET http://localhost:5000/api/v1/visualization/sensor/plantNode1/moisture?hours=24 \
  -H "Authorization: Basic YWRtaW46ZmxvcmFzZXZlbg=="

# Get health chart
curl -X GET http://localhost:5000/api/v1/visualization/health?days=7 \
  -H "Authorization: Basic YWRtaW46ZmxvcmFzZXZlbg=="

# Get dashboard
curl -X GET http://localhost:5000/api/v1/visualization/dashboard \
  -H "Authorization: Basic YWRtaW46ZmxvcmFzZXZlbg=="
```
