"""
Authentication module for the FloraSeven server.

This module provides functions for authenticating API requests.
"""
import logging
import functools
from flask import request, jsonify
import config

# Set up logging
logger = logging.getLogger(__name__)

def check_auth(username, password):
    """
    Check if the provided username and password are valid.
    
    Args:
        username (str): Username
        password (str): Password
        
    Returns:
        bool: True if authentication is successful, False otherwise
    """
    return username == config.API_USERNAME and password == config.API_PASSWORD

def authenticate():
    """
    Send a 401 response that enables basic auth.
    
    Returns:
        Response: 401 response with WWW-Authenticate header
    """
    return jsonify({'error': 'Authentication required'}), 401, {
        'WWW-Authenticate': 'Basic realm="FloraSeven API"'
    }

def requires_auth(f):
    """
    Decorator for routes that require authentication.
    
    Args:
        f: Function to decorate
        
    Returns:
        Function: Decorated function
    """
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if not config.ENABLE_AUTH:
            return f(*args, **kwargs)
            
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            logger.warning(f"Authentication failed for {request.remote_addr}")
            return authenticate()
        return f(*args, **kwargs)
    return decorated
