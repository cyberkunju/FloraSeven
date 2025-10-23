"""
Unit tests for the FloraSeven logic module.

This module contains tests for the business logic functions.
"""
import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logic

class TestLogic(unittest.TestCase):
    """Test cases for the FloraSeven logic module."""

    def test_calculate_parameter_status(self):
        """Test the _calculate_parameter_status function."""
        # Test optimal value
        status = logic._calculate_parameter_status(50.0, 40.0, 70.0)
        self.assertEqual(status, "optimal")

        # Test warning value (low)
        status = logic._calculate_parameter_status(42.0, 40.0, 70.0)
        self.assertEqual(status, "warning")

        # Test warning value (high)
        status = logic._calculate_parameter_status(68.0, 40.0, 70.0)
        self.assertEqual(status, "warning")

        # Test critical value (low)
        status = logic._calculate_parameter_status(35.0, 40.0, 70.0)
        self.assertEqual(status, "critical")

        # Test critical value (high)
        status = logic._calculate_parameter_status(75.0, 40.0, 70.0)
        self.assertEqual(status, "critical")

    def test_calculate_condition_index(self):
        """Test the calculate_condition_index function."""
        # Set up test data
        sensor_data = {
            'plant': {
                'moisture': 60.0,
                'temp_soil': 25.0,
                'light_lux': 15000.0,
                'ec_raw': 1000.0
            },
            'hub': {
                'ph_water': 6.5,
                'uv_ambient': 1.0
            }
        }

        thresholds = {
            'moisture': {'min': 40.0, 'max': 70.0},
            'temp_soil': {'min': 18.0, 'max': 28.0},
            'light_lux': {'min': 5000.0, 'max': 30000.0},
            'ph_water': {'min': 6.0, 'max': 7.5},
            'uv_ambient': {'min': 0.0, 'max': 2.0},
            'ec_raw': {'min': 800.0, 'max': 1500.0}
        }

        # Calculate condition index
        condition_index = logic.calculate_condition_index(sensor_data, thresholds)

        # Check results
        self.assertEqual(condition_index['moisture']['status'], "optimal")
        self.assertEqual(condition_index['temp_soil']['status'], "optimal")
        self.assertEqual(condition_index['light_lux']['status'], "optimal")
        self.assertEqual(condition_index['ph_water']['status'], "optimal")
        self.assertEqual(condition_index['uv_ambient']['status'], "optimal")
        self.assertEqual(condition_index['ec_raw']['status'], "optimal")

    def test_calculate_overall_health(self):
        """Test the calculate_overall_health function."""
        # Set up test data
        condition_index = {
            'moisture': {'status': 'optimal', 'value': 60.0, 'min': 40.0, 'max': 70.0},
            'temp_soil': {'status': 'optimal', 'value': 25.0, 'min': 18.0, 'max': 28.0},
            'light_lux': {'status': 'optimal', 'value': 15000.0, 'min': 5000.0, 'max': 30000.0},
            'ph_water': {'status': 'optimal', 'value': 6.5, 'min': 6.0, 'max': 7.5},
            'uv_ambient': {'status': 'optimal', 'value': 1.0, 'min': 0.0, 'max': 2.0},
            'ec_raw': {'status': 'optimal', 'value': 1000.0, 'min': 800.0, 'max': 1500.0}
        }

        visual_health = {
            'health_label': 'healthy',
            'health_score': 85,
            'confidence': 0.85
        }

        # Calculate overall health
        overall_health = logic.calculate_overall_health(condition_index, visual_health)

        # Check results
        self.assertEqual(overall_health['status'], "healthy")
        self.assertGreaterEqual(overall_health['score'], 85)
        self.assertGreaterEqual(len(overall_health['suggestions']), 1)

    def test_generate_suggestions(self):
        """Test the generate_suggestions function."""
        # Test with all optimal parameters
        condition_index = {
            'moisture': {'status': 'optimal', 'value': 60.0, 'min': 40.0, 'max': 70.0},
            'temp_soil': {'status': 'optimal', 'value': 25.0, 'min': 18.0, 'max': 28.0}
        }

        visual_health = {
            'health_label': 'healthy',
            'health_score': 85
        }

        suggestions = logic.generate_suggestions(condition_index, visual_health)
        self.assertEqual(len(suggestions), 1)
        self.assertIn("healthy", suggestions[0].lower())

        # Test with low moisture
        condition_index = {
            'moisture': {'status': 'critical', 'value': 35.0, 'min': 40.0, 'max': 70.0},
            'temp_soil': {'status': 'optimal', 'value': 25.0, 'min': 18.0, 'max': 28.0}
        }

        suggestions = logic.generate_suggestions(condition_index, visual_health)
        self.assertGreaterEqual(len(suggestions), 1)
        # Check if any suggestion mentions moisture and water
        moisture_suggestion = False
        for suggestion in suggestions:
            if "moisture" in suggestion.lower() and "water" in suggestion.lower():
                moisture_suggestion = True
                break
        self.assertTrue(moisture_suggestion, "No suggestion about low moisture found")

        # Test with wilting plant
        visual_health = {
            'health_label': 'wilting',
            'health_score': 40
        }

        suggestions = logic.generate_suggestions(condition_index, visual_health)
        self.assertGreaterEqual(len(suggestions), 2)  # At least 2 suggestions
        self.assertTrue(any("wilting" in s.lower() for s in suggestions))

    def test_get_complete_status(self):
        """Test the get_complete_status function."""
        # Mock the database functions
        with patch('database.get_latest_status_data') as mock_get_status, \
             patch('database.get_thresholds') as mock_get_thresholds, \
             patch('database.get_latest_image_data') as mock_get_image:

            # Set up mock return values
            mock_get_status.return_value = {
                'plant': {'moisture': 60.0},
                'hub': {'ph_water': 6.5}
            }

            mock_get_thresholds.return_value = {
                'moisture': {'min': 40.0, 'max': 70.0},
                'ph_water': {'min': 6.0, 'max': 7.5}
            }

            mock_get_image.return_value = {
                'health_label': 'healthy',
                'health_score': 85
            }

            # Get complete status
            status = logic.get_complete_status()

            # Check results
            self.assertIn('timestamp', status)
            self.assertIn('sensor_data', status)
            self.assertIn('thresholds', status)
            self.assertIn('visual_health', status)
            self.assertIn('condition_index', status)
            self.assertIn('overall_health', status)
            self.assertIn('sensor_status', status)

            # Check sensor status
            self.assertEqual(status['sensor_status']['ph_water']['status'], 'mock')
            self.assertEqual(status['sensor_status']['uv_ambient']['status'], 'mock')

if __name__ == '__main__':
    unittest.main()
