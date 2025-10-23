"""
Unit tests for the FloraSeven server.

This module contains tests for the Flask API endpoints.
"""
import os
import sys
import unittest
import json
import base64
from datetime import datetime
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import server
import config

class TestServerAPI(unittest.TestCase):
    """Test cases for the FloraSeven server API."""
    
    def setUp(self):
        """Set up test client and disable authentication."""
        self.app = server.app.test_client()
        self.app.testing = True
        # Disable authentication for testing
        self.auth_patcher = patch('auth.requires_auth', lambda f: f)
        self.auth_patcher.start()
        
    def tearDown(self):
        """Clean up after tests."""
        self.auth_patcher.stop()
    
    def test_get_status(self):
        """Test the status endpoint."""
        # Mock the logic.get_complete_status function
        with patch('logic.get_complete_status') as mock_get_status:
            # Set up mock return value
            mock_get_status.return_value = {
                'timestamp': datetime.now().isoformat(),
                'sensor_data': {
                    'plant': {'moisture': 60.0},
                    'hub': {'ph_water': 7.0}
                },
                'thresholds': {'moisture': {'min': 40.0, 'max': 70.0}},
                'visual_health': {'health_label': 'healthy', 'health_score': 85},
                'condition_index': {'moisture': {'status': 'optimal'}},
                'overall_health': {'status': 'healthy', 'score': 90}
            }
            
            # Make request
            response = self.app.get('/api/v1/status')
            
            # Check response
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertIn('sensor_data', data)
            self.assertIn('thresholds', data)
            self.assertIn('visual_health', data)
            self.assertIn('condition_index', data)
            self.assertIn('overall_health', data)
    
    def test_get_thresholds(self):
        """Test the get thresholds endpoint."""
        # Mock the database.get_thresholds function
        with patch('database.get_thresholds') as mock_get_thresholds:
            # Set up mock return value
            mock_get_thresholds.return_value = {
                'moisture': {'min': 40.0, 'max': 70.0},
                'temp_soil': {'min': 18.0, 'max': 28.0}
            }
            
            # Make request
            response = self.app.get('/api/v1/settings/thresholds')
            
            # Check response
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertIn('moisture', data)
            self.assertIn('temp_soil', data)
    
    def test_update_thresholds(self):
        """Test the update thresholds endpoint."""
        # Mock the database.update_thresholds function
        with patch('database.update_thresholds') as mock_update_thresholds:
            # Set up mock return value
            mock_update_thresholds.return_value = ['moisture']
            
            # Make request
            response = self.app.post(
                '/api/v1/settings/thresholds',
                json={'moisture': {'min': 45.0, 'max': 75.0}}
            )
            
            # Check response
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertIn('updated_parameters', data)
            self.assertEqual(data['updated_parameters'], ['moisture'])
    
    def test_send_water_command(self):
        """Test the water command endpoint."""
        # Mock the mqtt_client.send_water_command function
        with patch.object(server.mqtt_client.mqtt_client, 'send_water_command') as mock_send_command:
            # Set up mock return value
            mock_send_command.return_value = True
            
            # Make request
            response = self.app.post(
                '/api/v1/command/water',
                json={'state': 'ON', 'duration_sec': 5}
            )
            
            # Check response
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertEqual(data['command']['state'], 'ON')
            self.assertEqual(data['command']['duration_sec'], 5)
            
            # Check that the command was sent with the correct parameters
            mock_send_command.assert_called_once_with('ON', 5)
    
    def test_send_capture_image_command(self):
        """Test the capture image command endpoint."""
        # Mock the mqtt_client.send_capture_image_command function
        with patch.object(server.mqtt_client.mqtt_client, 'send_capture_image_command') as mock_send_command:
            # Set up mock return value
            mock_send_command.return_value = True
            
            # Make request
            response = self.app.post(
                '/api/v1/command/capture_image',
                json={'resolution': 'high', 'flash': False}
            )
            
            # Check response
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertEqual(data['command']['resolution'], 'high')
            self.assertEqual(data['command']['flash'], False)
            
            # Check that the command was sent with the correct parameters
            mock_send_command.assert_called_once_with('high', False)
    
    def test_send_read_now_command(self):
        """Test the read now command endpoint."""
        # Mock the mqtt_client.send_read_now_command function
        with patch.object(server.mqtt_client.mqtt_client, 'send_read_now_command') as mock_send_command:
            # Set up mock return value
            mock_send_command.return_value = True
            
            # Make request
            response = self.app.post('/api/v1/command/read_now')
            
            # Check response
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            
            # Check that the command was sent
            mock_send_command.assert_called_once()
    
    def test_login(self):
        """Test the login endpoint."""
        # Mock the auth.check_auth function
        with patch('auth.check_auth') as mock_check_auth:
            # Set up mock return value
            mock_check_auth.return_value = True
            
            # Make request
            response = self.app.post(
                '/api/v1/login',
                json={'username': 'admin', 'password': 'floraseven'}
            )
            
            # Check response
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertEqual(data['username'], 'admin')
            
            # Check that the auth function was called with the correct parameters
            mock_check_auth.assert_called_once_with('admin', 'floraseven')
    
    def test_login_invalid_credentials(self):
        """Test the login endpoint with invalid credentials."""
        # Mock the auth.check_auth function
        with patch('auth.check_auth') as mock_check_auth:
            # Set up mock return value
            mock_check_auth.return_value = False
            
            # Make request
            response = self.app.post(
                '/api/v1/login',
                json={'username': 'admin', 'password': 'wrong'}
            )
            
            # Check response
            self.assertEqual(response.status_code, 401)
            data = json.loads(response.data)
            self.assertFalse(data['success'])
            self.assertIn('error', data)
            
            # Check that the auth function was called with the correct parameters
            mock_check_auth.assert_called_once_with('admin', 'wrong')
    
    def test_logout(self):
        """Test the logout endpoint."""
        # Make request
        response = self.app.post('/api/v1/logout')
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])

if __name__ == '__main__':
    unittest.main()
