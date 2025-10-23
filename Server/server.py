"""
Main Flask application for the FloraSeven server.

This module provides the REST API endpoints for the Flutter mobile app
to interact with the system.

Features:
- RESTful API for mobile app communication
- Authentication and authorization
- File upload for plant images
- Command interface for hardware control
- Visualization endpoints for charts and dashboards
- Connection monitoring and status reporting
- Notification system
"""
import os
import logging
import threading
import time
import traceback
import uuid
from datetime import datetime
from functools import wraps

from flask import Flask, request, jsonify, send_from_directory, session, g, Response
from flask_cors import CORS
from werkzeug.utils import secure_filename

import config
import database
# Use real MQTT client
import mqtt_client
# import mock_mqtt as mqtt_client
import ai_service
import logic
import auth
import monitoring
import visualization
import connection_status
import connection_monitor

# Set up logging based on configuration
logger = logging.getLogger(__name__)

# Helper functions for API responses
def api_response(data=None, message=None, success=True, status_code=200, error=None):
    """
    Create a standardized API response.

    Args:
        data: Response data
        message (str, optional): Response message
        success (bool): Whether the request was successful
        status_code (int): HTTP status code
        error (str, optional): Error message

    Returns:
        Response: Flask response object
    """
    response_data = {
        'success': success,
        'timestamp': datetime.now().isoformat(),
        'request_id': getattr(g, 'request_id', str(uuid.uuid4()))
    }

    if data is not None:
        response_data['data'] = data

    if message:
        response_data['message'] = message

    if error:
        response_data['error'] = error

    return jsonify(response_data), status_code

def handle_api_exception(e, default_message="An unexpected error occurred"):
    """
    Handle exceptions in API endpoints.

    Args:
        e (Exception): The exception
        default_message (str): Default error message

    Returns:
        Response: Error response
    """
    logger.error(f"API Error: {str(e)}", exc_info=True)

    # Get detailed error information for logging
    error_details = {
        'error_type': type(e).__name__,
        'error_message': str(e),
        'traceback': traceback.format_exc()
    }

    # Log detailed error
    logger.error(f"Detailed error: {error_details}")

    # Return user-friendly error
    return api_response(
        success=False,
        message=default_message,
        error=str(e),
        status_code=500
    )

# Create Flask app
app = Flask(__name__)

# Request ID middleware
@app.before_request
def before_request():
    """Generate a unique request ID for each request."""
    g.request_id = str(uuid.uuid4())
    g.start_time = time.time()

@app.after_request
def after_request(response):
    """Add request ID and processing time to response headers."""
    response.headers['X-Request-ID'] = getattr(g, 'request_id', 'unknown')

    # Calculate processing time
    if hasattr(g, 'start_time'):
        processing_time = time.time() - g.start_time
        response.headers['X-Processing-Time'] = str(processing_time)

    return response

# Configure CORS
if hasattr(config, 'CORS_ORIGINS') and config.CORS_ORIGINS != '*':
    CORS(app, resources={r"/api/*": {"origins": config.CORS_ORIGINS}})
else:
    CORS(app)  # Enable CORS for all routes

# Configure app
app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_LENGTH
app.secret_key = config.SECRET_KEY
app.config['SESSION_COOKIE_SECURE'] = not config.DEBUG  # Secure cookies in production
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access to cookies
app.config['PERMANENT_SESSION_LIFETIME'] = config.SESSION_TIMEOUT  # Session timeout
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = config.DEBUG  # Pretty JSON in debug mode

# Configure rate limiting if enabled
if hasattr(config, 'RATE_LIMIT_ENABLED') and config.RATE_LIMIT_ENABLED:
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address

    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=[config.RATE_LIMIT]
    )

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize database
database.init_db()

# Start MQTT client in a separate thread
def start_mqtt_client():
    """Start the MQTT client in a separate thread."""
    try:
        if not mqtt_client.mqtt_client.start():
            logger.error("Failed to start MQTT client")
    except Exception as e:
        logger.error(f"Error starting MQTT client: {e}", exc_info=True)

mqtt_thread = threading.Thread(target=start_mqtt_client)
mqtt_thread.daemon = True
mqtt_thread.start()

# Start monitoring in a separate thread
def start_monitoring():
    """Start the monitoring system in a separate thread."""
    try:
        if not monitoring.monitor.start():
            logger.warning("Failed to start monitoring system")
    except Exception as e:
        logger.error(f"Error starting monitoring system: {e}", exc_info=True)

monitoring_thread = threading.Thread(target=start_monitoring)
monitoring_thread.daemon = True
monitoring_thread.start()

# Start connection monitoring in a separate thread
def start_connection_monitoring():
    """Start the connection monitoring system in a separate thread."""
    try:
        if not connection_monitor.connection_monitor.start():
            logger.warning("Failed to start connection monitoring system")
    except Exception as e:
        logger.error(f"Error starting connection monitoring: {e}", exc_info=True)

connection_monitoring_thread = threading.Thread(target=start_connection_monitoring)
connection_monitoring_thread.daemon = True
connection_monitoring_thread.start()

# Initialize connection status module
try:
    connection_status.initialize()
except Exception as e:
    logger.error(f"Error initializing connection status module: {e}", exc_info=True)

@app.route('/api/v1/status', methods=['GET'])
@auth.requires_auth
def get_status():
    """
    Get the latest system status.

    Returns:
        JSON: System status with sensor readings, connection status, and system health
    """
    try:
        # Get complete status from logic module
        status = logic.get_complete_status()

        # Add request timestamp
        status['timestamp'] = datetime.now().isoformat()

        # Add server info
        status['server'] = {
            'version': '1.0.0',
            'uptime': time.time() - getattr(connection_status, '_server_start_time', time.time())
        }

        # Add MQTT client status if available
        try:
            status['mqtt'] = mqtt_client.mqtt_client.get_status()
        except Exception as mqtt_error:
            logger.warning(f"Could not get MQTT status: {mqtt_error}")
            status['mqtt'] = {'connected': False, 'error': str(mqtt_error)}

        return api_response(
            data=status,
            message="System status retrieved successfully"
        )

    except Exception as e:
        return handle_api_exception(e, "Failed to retrieve system status")

@app.route('/api/v1/image/latest', methods=['GET'])
@auth.requires_auth
def get_latest_image():
    """
    Get the latest plant image.

    Returns:
        File: Image file or JSON error response
    """
    try:
        # Check if metadata only is requested
        metadata_only = request.args.get('metadata', 'false').lower() == 'true'

        # Get image data from database
        image_data = database.get_latest_image_data(database.get_db_connection())

        if image_data and image_data.get('latest_image'):
            filename = image_data['latest_image']
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            # Check if file exists
            if not os.path.exists(filepath):
                logger.warning(f"Image file not found: {filepath}")
                return api_response(
                    success=False,
                    message="Image file not found on server",
                    error="File not found",
                    status_code=404
                )

            # If metadata only is requested, return metadata
            if metadata_only:
                # Add file info
                try:
                    file_size = os.path.getsize(filepath)
                    file_modified = datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat()
                    image_data['file_info'] = {
                        'size': file_size,
                        'modified': file_modified,
                        'path': filename
                    }
                except Exception as file_error:
                    logger.warning(f"Error getting file info: {file_error}")

                return api_response(
                    data=image_data,
                    message="Image metadata retrieved successfully"
                )

            # Otherwise return the actual image file
            return send_from_directory(
                app.config['UPLOAD_FOLDER'],
                filename,
                as_attachment=request.args.get('download', 'false').lower() == 'true'
            )
        else:
            return api_response(
                success=False,
                message="No image found",
                error="No image data available",
                status_code=404
            )

    except Exception as e:
        return handle_api_exception(e, "Failed to retrieve latest image")

@app.route('/api/v1/upload_image', methods=['POST'])
@auth.requires_auth
def upload_image():
    """
    Upload a plant image for analysis.

    Returns:
        JSON: Upload result with analysis data
    """
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return api_response(
                success=False,
                message="No file provided",
                error="No file part in the request",
                status_code=400
            )

        file = request.files['file']

        # Check if file is empty
        if file.filename == '':
            return api_response(
                success=False,
                message="Empty file provided",
                error="No selected file",
                status_code=400
            )

        # Check file extension
        allowed_extensions = {'jpg', 'jpeg', 'png'}
        if not '.' in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
            return api_response(
                success=False,
                message="Invalid file type",
                error=f"File must be one of: {', '.join(allowed_extensions)}",
                status_code=400
            )

        # Generate unique filename with secure filename to prevent path traversal
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        original_filename = secure_filename(file.filename)
        filename = f"plant_image_{timestamp}_{original_filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # Save file
        file.save(filepath)
        logger.info(f"Image uploaded: {filepath}")

        # Analyze image
        if ai_service.ai_service is not None:
            try:
                # Analyze the image
                result = ai_service.ai_service.analyze_image(filepath)

                # Get database connection
                conn = database.get_db_connection()

                # Log results to database
                database.log_image_analysis(
                    conn,
                    timestamp=datetime.now().isoformat(),
                    image_filename=filename,
                    health_label=result['health_label'],
                    health_score=result['health_score'],
                    confidence=result['confidence']
                )

                # Add file info to result
                file_size = os.path.getsize(filepath)
                result['file_info'] = {
                    'filename': filename,
                    'size': file_size,
                    'original_name': original_filename
                }

                return api_response(
                    data={
                        'filename': filename,
                        'analysis': result
                    },
                    message="Image uploaded and analyzed successfully"
                )
            except Exception as analysis_error:
                logger.error(f"Error analyzing image: {analysis_error}", exc_info=True)

                # Still return success for the upload, but with analysis error
                return api_response(
                    data={
                        'filename': filename,
                        'analysis_error': str(analysis_error)
                    },
                    message="Image uploaded but analysis failed",
                    success=True,
                    error="Analysis failed but upload succeeded"
                )
        else:
            # AI service not available, but upload succeeded
            return api_response(
                data={'filename': filename},
                message="Image uploaded successfully but AI service is not available",
                success=True,
                error="AI service not available"
            )

    except Exception as e:
        return handle_api_exception(e, "Failed to process image upload")

@app.route('/api/v1/settings/thresholds', methods=['GET'])
@auth.requires_auth
def get_thresholds():
    """
    Get the current threshold settings.

    Returns:
        JSON: Threshold settings for all parameters
    """
    try:
        # Get database connection
        conn = database.get_db_connection()

        # Get thresholds from database
        thresholds = database.get_thresholds(conn)

        # Add default thresholds for any missing parameters
        for param, values in config.DEFAULT_THRESHOLDS.items():
            if param not in thresholds:
                thresholds[param] = values

        # Add metadata
        result = {
            'thresholds': thresholds,
            'default_thresholds': config.DEFAULT_THRESHOLDS,
            'parameters': list(thresholds.keys())
        }

        return api_response(
            data=result,
            message="Threshold settings retrieved successfully"
        )

    except Exception as e:
        return handle_api_exception(e, "Failed to retrieve threshold settings")

@app.route('/api/v1/settings/thresholds', methods=['POST'])
@auth.requires_auth
def update_thresholds():
    """
    Update threshold settings.

    Returns:
        JSON: Update result with list of updated parameters
    """
    try:
        # Get thresholds from request
        thresholds = request.json

        if not thresholds:
            return api_response(
                success=False,
                message="No thresholds provided",
                error="Request body is empty or not valid JSON",
                status_code=400
            )

        # Validate thresholds
        validation_errors = []
        for param, values in thresholds.items():
            if not isinstance(values, dict):
                validation_errors.append(f"Parameter '{param}' must have min and max values as an object")
                continue

            if 'min' not in values or 'max' not in values:
                validation_errors.append(f"Missing min or max value for '{param}'")
                continue

            try:
                min_val = float(values['min'])
                max_val = float(values['max'])

                if min_val >= max_val:
                    validation_errors.append(f"Min value must be less than max value for '{param}'")
            except (ValueError, TypeError):
                validation_errors.append(f"Min and max values for '{param}' must be numbers")

        if validation_errors:
            return api_response(
                success=False,
                message="Validation failed",
                error=validation_errors,
                status_code=400
            )

        # Get database connection
        conn = database.get_db_connection()

        # Update thresholds
        updated_params = database.update_thresholds(conn, thresholds)

        # Get the updated thresholds
        updated_thresholds = {}
        all_thresholds = database.get_thresholds(conn)
        for param in updated_params:
            if param in all_thresholds:
                updated_thresholds[param] = all_thresholds[param]

        return api_response(
            data={
                'updated_parameters': updated_params,
                'updated_thresholds': updated_thresholds
            },
            message=f"Thresholds updated successfully for {len(updated_params)} parameter(s)"
        )

    except Exception as e:
        return handle_api_exception(e, "Failed to update threshold settings")

@app.route('/api/v1/command/water', methods=['POST'])
@auth.requires_auth
def send_water_command():
    """
    Send a command to control the water pump.

    Returns:
        JSON: Command result with status and command details
    """
    try:
        # Get command from request
        command = request.json

        if not command:
            return api_response(
                success=False,
                message="No command provided",
                error="Request body is empty or not valid JSON",
                status_code=400
            )

        # Validate command
        if 'state' not in command:
            return api_response(
                success=False,
                message="Missing state parameter",
                error="The 'state' parameter is required",
                status_code=400
            )

        state = command['state'].upper()
        if state not in ['ON', 'OFF']:
            return api_response(
                success=False,
                message="Invalid state parameter",
                error="State must be 'ON' or 'OFF'",
                status_code=400
            )

        duration_sec = None
        if state == 'ON' and 'duration_sec' in command:
            try:
                duration_sec = int(command['duration_sec'])
                if duration_sec <= 0:
                    return api_response(
                        success=False,
                        message="Invalid duration",
                        error="Duration must be a positive integer",
                        status_code=400
                    )
                elif duration_sec > config.MAX_WATERING_DURATION:
                    return api_response(
                        success=False,
                        message="Duration too long",
                        error=f"Maximum watering duration is {config.MAX_WATERING_DURATION} seconds",
                        status_code=400
                    )
            except ValueError:
                return api_response(
                    success=False,
                    message="Invalid duration format",
                    error="Duration must be a positive integer",
                    status_code=400
                )

        # Get current moisture level before watering
        moisture_before = None
        try:
            conn = database.get_db_connection()
            moisture_reading = database.get_latest_sensor_reading(conn, 'plantNode1', 'moisture')
            if moisture_reading:
                moisture_before = moisture_reading['value']
        except Exception as db_error:
            logger.warning(f"Could not get moisture reading before watering: {db_error}")

        # Send command
        command_result = mqtt_client.mqtt_client.send_water_command(state, duration_sec)

        if command_result:
            # Log watering event if turning on
            if state == 'ON':
                try:
                    # Create a watering event entry
                    watering_event = {
                        'timestamp': datetime.now().isoformat(),
                        'duration_sec': duration_sec or 0,
                        'triggered_by': 'manual',
                        'moisture_before': moisture_before
                    }

                    # Store in database if we have a watering events table
                    if hasattr(database, 'log_watering_event'):
                        database.log_watering_event(conn, **watering_event)
                except Exception as log_error:
                    logger.warning(f"Could not log watering event: {log_error}")

            return api_response(
                data={
                    'command': {
                        'state': state,
                        'duration_sec': duration_sec if state == 'ON' else None,
                        'moisture_before': moisture_before
                    }
                },
                message=f"Water pump turned {state.lower()}" +
                        (f" for {duration_sec} seconds" if state == 'ON' and duration_sec else "")
            )
        else:
            return api_response(
                success=False,
                message="Failed to send water command",
                error="MQTT command failed",
                status_code=500
            )

    except Exception as e:
        return handle_api_exception(e, "Failed to send water command")

@app.route('/api/v1/command/capture_image', methods=['POST'])
@auth.requires_auth
def send_capture_image_command():
    """
    Send a command to capture an image.

    Returns:
        JSON: Command result with status and command details
    """
    try:
        # Get command from request
        command = request.json or {}

        # Extract and validate parameters
        resolution = command.get('resolution')
        if resolution and not isinstance(resolution, str):
            return api_response(
                success=False,
                message="Invalid resolution parameter",
                error="Resolution must be a string (e.g., '640x480')",
                status_code=400
            )

        flash = command.get('flash', False)
        if not isinstance(flash, bool):
            # Try to convert to boolean if it's a string
            if isinstance(flash, str):
                flash = flash.lower() == 'true'
            else:
                return api_response(
                    success=False,
                    message="Invalid flash parameter",
                    error="Flash must be a boolean value",
                    status_code=400
                )

        # Add additional parameters
        quality = command.get('quality')
        if quality is not None:
            try:
                quality = int(quality)
                if quality < 0 or quality > 100:
                    return api_response(
                        success=False,
                        message="Invalid quality parameter",
                        error="Quality must be an integer between 0 and 100",
                        status_code=400
                    )
            except (ValueError, TypeError):
                return api_response(
                    success=False,
                    message="Invalid quality format",
                    error="Quality must be an integer between 0 and 100",
                    status_code=400
                )

        # Send command
        command_result = mqtt_client.mqtt_client.send_capture_image_command(
            resolution=resolution,
            flash=flash,
            quality=quality
        )

        if command_result:
            return api_response(
                data={
                    'command': {
                        'resolution': resolution,
                        'flash': flash,
                        'quality': quality
                    },
                    'estimated_time': 5  # Estimated time in seconds for the image to be captured
                },
                message="Capture image command sent successfully"
            )
        else:
            return api_response(
                success=False,
                message="Failed to send capture image command",
                error="MQTT command failed",
                status_code=500
            )

    except Exception as e:
        return handle_api_exception(e, "Failed to send capture image command")

@app.route('/api/v1/command/read_now', methods=['POST'])
@auth.requires_auth
def send_read_now_command():
    """
    Send a command to force a sensor reading.

    Returns:
        JSON: Command result with status and details
    """
    try:
        # Get optional parameters
        params = request.json or {}

        # Extract specific sensors to read if provided
        sensors = params.get('sensors')
        if sensors and not isinstance(sensors, list):
            return api_response(
                success=False,
                message="Invalid sensors parameter",
                error="Sensors must be a list of sensor types",
                status_code=400
            )

        # Extract node ID if provided
        node_id = params.get('node_id')

        # Send command
        command_result = mqtt_client.mqtt_client.send_read_now_command(
            node_id=node_id,
            sensors=sensors
        )

        if command_result:
            return api_response(
                data={
                    'command': {
                        'node_id': node_id,
                        'sensors': sensors
                    },
                    'estimated_time': 2  # Estimated time in seconds for readings to be available
                },
                message="Read now command sent successfully"
            )
        else:
            return api_response(
                success=False,
                message="Failed to send read now command",
                error="MQTT command failed",
                status_code=500
            )

    except Exception as e:
        return handle_api_exception(e, "Failed to send read now command")

@app.errorhandler(400)
def bad_request(error):
    """Handle 400 Bad Request errors."""
    return api_response(
        success=False,
        message="Bad request",
        error=str(error),
        status_code=400
    )

@app.errorhandler(404)
def not_found(error):
    """Handle 404 Not Found errors."""
    return api_response(
        success=False,
        message="Resource not found",
        error=str(error),
        status_code=404
    )

@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 Method Not Allowed errors."""
    return api_response(
        success=False,
        message="Method not allowed",
        error=str(error),
        status_code=405
    )

@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle 413 Request Entity Too Large errors."""
    return api_response(
        success=False,
        message="Request entity too large",
        error=f"The file exceeds the maximum allowed size of {config.MAX_CONTENT_LENGTH / (1024 * 1024):.1f} MB",
        status_code=413
    )

@app.route('/api/v1/login', methods=['POST'])
def login():
    """
    Login endpoint to get an authentication token.

    Returns:
        JSON: Login result with session information
    """
    try:
        # Get credentials from request
        data = request.json

        if not data:
            return api_response(
                success=False,
                message="No credentials provided",
                error="Request body is empty or not valid JSON",
                status_code=400
            )

        if 'username' not in data or 'password' not in data:
            return api_response(
                success=False,
                message="Missing credentials",
                error="Both username and password are required",
                status_code=400
            )

        username = data['username']
        password = data['password']

        # Rate limit login attempts
        if hasattr(config, 'LOGIN_RATE_LIMIT_ENABLED') and config.LOGIN_RATE_LIMIT_ENABLED:
            # Check if we're tracking login attempts
            if not hasattr(login, 'attempts'):
                login.attempts = {}

            # Get client IP
            client_ip = request.remote_addr

            # Check if this IP has too many recent failed attempts
            current_time = time.time()
            if client_ip in login.attempts:
                attempts = login.attempts[client_ip]
                # Remove old attempts
                attempts = [a for a in attempts if current_time - a < config.LOGIN_ATTEMPT_WINDOW]

                # Check if too many attempts
                if len(attempts) >= config.LOGIN_MAX_ATTEMPTS:
                    logger.warning(f"Too many login attempts from {client_ip}")
                    return api_response(
                        success=False,
                        message="Too many login attempts",
                        error="Please try again later",
                        status_code=429
                    )

                login.attempts[client_ip] = attempts
            else:
                login.attempts[client_ip] = []

        # Check credentials
        if auth.check_auth(username, password):
            # Set session variables
            session.permanent = True
            session['logged_in'] = True
            session['username'] = username
            session['login_time'] = datetime.now().isoformat()

            # Clear failed login attempts for this IP if we're tracking
            if hasattr(login, 'attempts') and request.remote_addr in login.attempts:
                login.attempts[request.remote_addr] = []

            return api_response(
                data={
                    'username': username,
                    'session_expires': (datetime.now() + config.SESSION_TIMEOUT).isoformat()
                    if hasattr(config, 'SESSION_TIMEOUT') else None
                },
                message="Login successful"
            )
        else:
            # Track failed login attempt
            if hasattr(config, 'LOGIN_RATE_LIMIT_ENABLED') and config.LOGIN_RATE_LIMIT_ENABLED:
                client_ip = request.remote_addr
                login.attempts[client_ip].append(time.time())

            logger.warning(f"Failed login attempt for user: {username}")
            return api_response(
                success=False,
                message="Login failed",
                error="Invalid username or password",
                status_code=401
            )

    except Exception as e:
        return handle_api_exception(e, "Login failed due to an unexpected error")

@app.route('/api/v1/logout', methods=['POST'])
def logout():
    """
    Logout endpoint to invalidate the authentication token.

    Returns:
        JSON: Logout result with status
    """
    try:
        # Get username before clearing session
        username = session.get('username', 'unknown')

        # Clear session
        session.clear()

        # Log the logout
        logger.info(f"User logged out: {username}")

        return api_response(
            message="Logout successful"
        )

    except Exception as e:
        return handle_api_exception(e, "Logout failed due to an unexpected error")

@app.route('/api/v1/visualization/sensor/<node_id>/<sensor_type>', methods=['GET'])
@auth.requires_auth
def get_sensor_chart(node_id, sensor_type):
    """
    Get a chart for a specific sensor.

    Args:
        node_id (str): Identifier for the node
        sensor_type (str): Type of sensor

    Returns:
        JSON: Chart data
    """
    try:
        # Get hours parameter
        hours = request.args.get('hours', default=24, type=int)

        # Generate chart
        chart_data = visualization.generate_sensor_chart(node_id, sensor_type, hours=hours)

        if chart_data:
            return jsonify({
                'success': True,
                'chart_data': chart_data
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to generate chart'
            }), 500

    except Exception as e:
        logger.error(f"Error generating sensor chart: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/visualization/health', methods=['GET'])
@auth.requires_auth
def get_health_chart():
    """
    Get a chart showing plant health history.

    Returns:
        JSON: Chart data
    """
    try:
        # Get days parameter
        days = request.args.get('days', default=7, type=int)

        # Generate chart
        chart_data = visualization.generate_health_history_chart(days=days)

        if chart_data:
            return jsonify({
                'success': True,
                'chart_data': chart_data
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to generate chart'
            }), 500

    except Exception as e:
        logger.error(f"Error generating health chart: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/visualization/dashboard', methods=['GET'])
@auth.requires_auth
def get_dashboard():
    """
    Get a dashboard with multiple charts.

    Returns:
        JSON: Dashboard data
    """
    try:
        # Generate dashboard
        dashboard = visualization.generate_dashboard()

        return jsonify({
            'success': True,
            'dashboard': dashboard
        })

    except Exception as e:
        logger.error(f"Error generating dashboard: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/connection/status', methods=['GET'])
@auth.requires_auth
def get_connection_status():
    """
    Get the connection status of all system components.

    Returns:
        JSON: Connection status of all components
    """
    try:
        # Get enhanced status from connection monitor if available
        try:
            status = connection_monitor.connection_monitor.get_all_component_status()
            return jsonify(status)
        except Exception:
            # Fall back to basic connection status
            status = connection_status.get_connection_status()
            return jsonify(status)

    except Exception as e:
        logger.error(f"Error getting connection status: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/connection/health', methods=['GET'])
@auth.requires_auth
def get_connection_health():
    """
    Get a summary of the overall system health.

    Returns:
        JSON: System health summary
    """
    try:
        health = connection_monitor.connection_monitor.get_system_health_summary()
        return jsonify(health)

    except Exception as e:
        logger.error(f"Error getting system health: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/connection/events', methods=['GET'])
@auth.requires_auth
def get_connection_events():
    """
    Get recent connection events.

    Returns:
        JSON: List of connection events
    """
    try:
        # Get query parameters
        component_id = request.args.get('component_id')
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        limit = request.args.get('limit', default=50, type=int)

        # Get events from database
        events = database.get_connection_events(
            component_id=component_id,
            start_time=start_time,
            end_time=end_time,
            limit=limit
        )

        return jsonify({
            'success': True,
            'events': events
        })

    except Exception as e:
        logger.error(f"Error getting connection events: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/connection/history', methods=['GET'])
@auth.requires_auth
def get_connection_history():
    """
    Get historical connection status snapshots.

    Returns:
        JSON: List of connection status snapshots
    """
    try:
        # Get query parameters
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        limit = request.args.get('limit', default=20, type=int)

        # Get history from database
        history = database.get_connection_status_history(
            start_time=start_time,
            end_time=end_time,
            limit=limit
        )

        return jsonify({
            'success': True,
            'history': history
        })

    except Exception as e:
        logger.error(f"Error getting connection history: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/notifications', methods=['GET'])
@auth.requires_auth
def get_notifications():
    """
    Get notifications.

    Returns:
        JSON: List of notifications
    """
    try:
        # Get query parameters
        read = request.args.get('read')
        if read is not None:
            read = read.lower() == 'true'

        component_id = request.args.get('component_id')
        severity = request.args.get('severity')
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        limit = request.args.get('limit', default=50, type=int)

        # Get notifications from database
        notifications = database.get_notifications(
            read=read,
            component_id=component_id,
            severity=severity,
            start_time=start_time,
            end_time=end_time,
            limit=limit
        )

        return jsonify({
            'success': True,
            'notifications': notifications
        })

    except Exception as e:
        logger.error(f"Error getting notifications: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/notifications/<int:notification_id>/read', methods=['POST'])
@auth.requires_auth
def mark_notification_read(notification_id):
    """
    Mark a notification as read.

    Args:
        notification_id (int): Notification ID

    Returns:
        JSON: Operation result
    """
    try:
        # Get read status from request
        data = request.json or {}
        read = data.get('read', True)

        # Mark notification as read
        success = database.mark_notification_read(notification_id, read)

        if success:
            return jsonify({
                'success': True,
                'message': f'Notification {notification_id} marked as {"read" if read else "unread"}'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to mark notification'
            }), 500

    except Exception as e:
        logger.error(f"Error marking notification as read: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/notifications/<int:notification_id>/action', methods=['POST'])
@auth.requires_auth
def mark_notification_action(notification_id):
    """
    Mark a notification as having action taken.

    Args:
        notification_id (int): Notification ID

    Returns:
        JSON: Operation result
    """
    try:
        # Get action status from request
        data = request.json or {}
        action_taken = data.get('action_taken', True)

        # Mark notification action
        success = database.mark_notification_action_taken(notification_id, action_taken)

        if success:
            return jsonify({
                'success': True,
                'message': f'Notification {notification_id} marked as {"action taken" if action_taken else "no action taken"}'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to mark notification action'
            }), 500

    except Exception as e:
        logger.error(f"Error marking notification action: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/notifications/clear', methods=['POST'])
@auth.requires_auth
def clear_notifications():
    """
    Clear old notifications.

    Returns:
        JSON: Operation result
    """
    try:
        # Get days parameter from request
        data = request.json or {}
        days = data.get('days', 30)

        # Clear old notifications
        deleted_count = database.clear_old_notifications(days)

        return jsonify({
            'success': True,
            'message': f'Cleared {deleted_count} notifications older than {days} days'
        })

    except Exception as e:
        logger.error(f"Error clearing notifications: {e}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(429)
def too_many_requests(error):
    """Handle 429 Too Many Requests errors."""
    return api_response(
        success=False,
        message="Too many requests",
        error="Rate limit exceeded. Please try again later.",
        status_code=429
    )

@app.errorhandler(500)
def server_error(error):
    """Handle 500 Internal Server Error errors."""
    logger.error(f"Internal server error: {error}", exc_info=True)
    return api_response(
        success=False,
        message="Internal server error",
        error="The server encountered an unexpected condition that prevented it from fulfilling the request",
        status_code=500
    )

@app.route('/api/v1/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for monitoring systems.

    Returns:
        JSON: Health status of the server
    """
    try:
        # Check database connection
        db_ok = False
        try:
            conn = database.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            db_ok = cursor.fetchone() is not None
        except Exception as db_error:
            logger.warning(f"Database health check failed: {db_error}")

        # Check MQTT connection
        mqtt_ok = mqtt_client.mqtt_client.is_connected()

        # Check disk space
        disk_ok = True
        disk_space = {}
        try:
            import shutil
            total, used, free = shutil.disk_usage("/")
            disk_space = {
                "total_gb": total / (1024**3),
                "used_gb": used / (1024**3),
                "free_gb": free / (1024**3),
                "percent_used": (used / total) * 100
            }
            disk_ok = disk_space["percent_used"] < 90  # Less than 90% used
        except Exception as disk_error:
            logger.warning(f"Disk space check failed: {disk_error}")

        # Overall health status
        all_ok = db_ok and mqtt_ok and disk_ok

        return api_response(
            data={
                "status": "healthy" if all_ok else "unhealthy",
                "database": {
                    "connected": db_ok
                },
                "mqtt": {
                    "connected": mqtt_ok
                },
                "disk": disk_space,
                "uptime_seconds": time.time() - getattr(connection_status, '_server_start_time', time.time())
            },
            message="Health check completed"
        )
    except Exception as e:
        return handle_api_exception(e, "Health check failed")

@app.route('/api/v1/system/info', methods=['GET'])
@auth.requires_auth
def system_info():
    """
    Get system information.

    Returns:
        JSON: System information including versions, uptime, etc.
    """
    try:
        import platform
        import sys

        # Get Python packages
        packages = {}
        try:
            import pkg_resources
            for pkg in pkg_resources.working_set:
                packages[pkg.key] = pkg.version
        except Exception as pkg_error:
            logger.warning(f"Could not get package information: {pkg_error}")

        return api_response(
            data={
                "server": {
                    "version": "1.0.0",
                    "uptime_seconds": time.time() - getattr(connection_status, '_server_start_time', time.time()),
                    "start_time": getattr(connection_status, '_server_start_time_iso', datetime.now().isoformat())
                },
                "system": {
                    "platform": platform.platform(),
                    "python_version": sys.version,
                    "hostname": platform.node()
                },
                "packages": packages
            },
            message="System information retrieved successfully"
        )
    except Exception as e:
        return handle_api_exception(e, "Failed to retrieve system information")

@app.route('/api/v1/watering/history', methods=['GET'])
@auth.requires_auth
def get_watering_history():
    """
    Get watering event history.

    Returns:
        JSON: List of watering events
    """
    try:
        # Get query parameters
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        limit = request.args.get('limit', default=20, type=int)

        # Get watering history from database
        conn = database.get_db_connection()
        history = database.get_watering_history(
            conn,
            start_time=start_time,
            end_time=end_time,
            limit=limit
        )

        # Calculate statistics
        stats = {}
        if history:
            total_duration = sum(event['duration_sec'] for event in history if event['duration_sec'])
            avg_duration = total_duration / len(history) if history else 0
            manual_count = sum(1 for event in history if event['triggered_by'] == 'manual')
            auto_count = sum(1 for event in history if event['triggered_by'] == 'auto')

            stats = {
                'total_events': len(history),
                'total_duration_sec': total_duration,
                'avg_duration_sec': avg_duration,
                'manual_count': manual_count,
                'auto_count': auto_count
            }

        return api_response(
            data={
                'history': history,
                'stats': stats
            },
            message=f"Retrieved {len(history)} watering events"
        )

    except Exception as e:
        return handle_api_exception(e, "Failed to retrieve watering history")

@app.route('/api/v1/system/database', methods=['POST'])
@auth.requires_auth
def database_maintenance():
    """
    Perform database maintenance operations.

    Returns:
        JSON: Result of the maintenance operation
    """
    try:
        operation = request.json.get('operation', '').lower() if request.json else ''

        if not operation:
            return api_response(
                success=False,
                message="No operation specified",
                error="The 'operation' parameter is required",
                status_code=400
            )

        if operation == 'optimize':
            result = database.optimize_database()
            return api_response(
                data={"optimized": result},
                message="Database optimization completed"
            )
        elif operation == 'backup':
            result = database.backup_database()
            return api_response(
                data={"backup_created": result},
                message="Database backup completed"
            )
        elif operation == 'prune':
            days = request.json.get('days', None)
            if days is not None:
                try:
                    days = int(days)
                    if days <= 0:
                        return api_response(
                            success=False,
                            message="Invalid days parameter",
                            error="Days must be a positive integer",
                            status_code=400
                        )
                except (ValueError, TypeError):
                    return api_response(
                        success=False,
                        message="Invalid days format",
                        error="Days must be a positive integer",
                        status_code=400
                    )

            result = database.prune_all_data()
            return api_response(
                data={"pruned": result},
                message="Database pruning completed"
            )
        else:
            return api_response(
                success=False,
                message="Invalid operation",
                error=f"Operation '{operation}' is not supported. Valid operations are: optimize, backup, prune",
                status_code=400
            )

    except Exception as e:
        return handle_api_exception(e, "Database maintenance failed")

if __name__ == '__main__':
    # Configure logging
    logging_level = getattr(logging, config.LOG_LEVEL.upper(), logging.INFO)
    logging.basicConfig(
        level=logging_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(os.path.join('data', 'floraseven_server.log'))
        ]
    )

    # Store server start time
    connection_status._server_start_time = time.time()
    connection_status._server_start_time_iso = datetime.now().isoformat()

    # Log startup
    logger.info(f"Starting FloraSeven server v1.0.0 on {config.HOST}:{config.PORT}")
    logger.info(f"Debug mode: {config.DEBUG}")
    logger.info(f"Log level: {config.LOG_LEVEL}")

    # Run the app
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG,
        threaded=True
    )
