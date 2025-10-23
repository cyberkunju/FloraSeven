"""
Business logic module for the FloraSeven server.

This module provides functions for calculating plant health indices,
generating suggestions, and coordinating between other components.
"""
import logging
from datetime import datetime

import database

# Set up logging
logger = logging.getLogger(__name__)

def calculate_condition_index(sensor_data, thresholds):
    """
    Calculate the condition index based on sensor readings and thresholds.

    Args:
        sensor_data (dict): Dictionary with latest sensor data
        thresholds (dict): Dictionary with parameter thresholds

    Returns:
        dict: Condition index with status for each parameter
    """
    condition_index = {}

    # Process plant node sensors
    plant_data = sensor_data.get('plant', {})
    for param in ['moisture', 'temp_soil', 'light_lux', 'ec_raw']:
        if param in plant_data and param in thresholds:
            value = plant_data[param]
            min_val = thresholds[param]['min']
            max_val = thresholds[param]['max']

            # Calculate status
            status = _calculate_parameter_status(value, min_val, max_val)

            condition_index[param] = {
                'status': status,
                'value': value,
                'min': min_val,
                'max': max_val
            }

    # Process hub node sensors
    hub_data = sensor_data.get('hub', {})
    for param in ['ph_water', 'uv_ambient']:
        if param in hub_data and param in thresholds:
            value = hub_data[param]
            min_val = thresholds[param]['min']
            max_val = thresholds[param]['max']

            # Calculate status
            status = _calculate_parameter_status(value, min_val, max_val)

            condition_index[param] = {
                'status': status,
                'value': value,
                'min': min_val,
                'max': max_val
            }

    return condition_index

def _calculate_parameter_status(value, min_val, max_val):
    """
    Calculate the status of a parameter based on its value and thresholds.

    Args:
        value (float): Parameter value
        min_val (float): Minimum threshold
        max_val (float): Maximum threshold

    Returns:
        str: Status ("optimal", "warning", or "critical")
    """
    # Calculate warning thresholds (±10% of optimal range)
    warning_min = min_val + (max_val - min_val) * 0.1
    warning_max = max_val - (max_val - min_val) * 0.1

    if value < min_val or value > max_val:
        return "critical"
    elif value < warning_min or value > warning_max:
        return "warning"
    else:
        return "optimal"

def calculate_overall_health(condition_index, visual_health):
    """
    Calculate the overall health based on condition index and visual health.

    Args:
        condition_index (dict): Condition index with status for each parameter
        visual_health (dict): Visual health assessment from AI

    Returns:
        dict: Overall health status and score
    """
    # Default values
    status = "healthy"
    score = 100
    suggestions = []

    # Check if visual_health is available
    if visual_health is None:
        visual_health = {
            'health_label': 'unknown',
            'health_score': 50,
            'confidence': 0.5
        }

    # Determine status based on condition index and visual health
    has_critical = False
    has_warning = False

    for param, data in condition_index.items():
        if data['status'] == "critical":
            has_critical = True
        elif data['status'] == "warning":
            has_warning = True

    # Visual health affects overall status
    visual_label = visual_health.get('health_label', 'unknown')
    visual_score = visual_health.get('health_score', 50)

    if visual_label == "wilting" or has_critical:
        status = "critical"
    elif visual_score < 70 or has_warning:
        status = "needs_attention"
    else:
        status = "healthy"

    # Calculate overall score
    # 60% from visual health, 40% from condition index
    if visual_score is not None:
        visual_component = visual_score * 0.6
    else:
        visual_component = 50 * 0.6

    # Calculate average normalized score from condition index
    sensor_scores = []
    for param, data in condition_index.items():
        if data['status'] == "optimal":
            sensor_scores.append(100)
        elif data['status'] == "warning":
            sensor_scores.append(50)
        else:  # critical
            sensor_scores.append(0)

    if sensor_scores:
        sensor_component = (sum(sensor_scores) / len(sensor_scores)) * 0.4
    else:
        sensor_component = 50 * 0.4

    # Combine components
    score = int(visual_component + sensor_component)

    # Generate suggestions
    suggestions = generate_suggestions(condition_index, visual_health)

    return {
        'status': status,
        'score': score,
        'suggestions': suggestions
    }

def generate_suggestions(condition_index, visual_health):
    """
    Generate care suggestions based on condition index and visual health.

    Args:
        condition_index (dict): Condition index with status for each parameter
        visual_health (dict): Visual health assessment from AI

    Returns:
        list: List of suggestion strings
    """
    suggestions = []

    # Check if all parameters are optimal
    all_optimal = True
    for param, data in condition_index.items():
        if data['status'] != "optimal":
            all_optimal = False

    if all_optimal and visual_health.get('health_label') == 'healthy':
        suggestions.append("Plant is healthy and all parameters are within optimal ranges.")
        return suggestions

    # Generate specific suggestions based on parameters
    for param, data in condition_index.items():
        if data['status'] == "critical" or data['status'] == "warning":
            if param == "moisture":
                if data['value'] < data['min']:
                    suggestions.append("Soil moisture is too low. Water the plant.")
                else:
                    suggestions.append("Soil moisture is too high. Allow soil to dry before watering again.")

            elif param == "temp_soil":
                if data['value'] < data['min']:
                    suggestions.append("Soil temperature is too low. Move plant to a warmer location.")
                else:
                    suggestions.append("Soil temperature is too high. Move plant to a cooler location.")

            elif param == "light_lux":
                if data['value'] < data['min']:
                    suggestions.append("Light level is too low. Move plant to a brighter location.")
                else:
                    suggestions.append("Light level is too high. Provide some shade or move to a less bright location.")

            elif param == "ph_water":
                if data['value'] < data['min']:
                    suggestions.append("Water pH is too low (acidic). Adjust water pH or use pH-balanced water.")
                else:
                    suggestions.append("Water pH is too high (alkaline). Adjust water pH or use pH-balanced water.")

            elif param == "ec_raw":
                if data['value'] < data['min']:
                    suggestions.append("Nutrient level (EC) is too low. Consider adding fertilizer.")
                else:
                    suggestions.append("Nutrient level (EC) is too high. Flush soil with clean water.")

    # Add suggestions based on visual health
    if visual_health.get('health_label') == 'wilting':
        suggestions.append("Plant appears to be wilting based on visual analysis. Check water levels and environmental conditions.")

    # If no specific suggestions were generated, add a general one
    if not suggestions:
        suggestions.append("Some parameters are outside optimal ranges. Monitor plant closely.")

    return suggestions

def get_complete_status():
    """
    Get the complete system status, including sensor data, thresholds,
    visual health, condition index, and overall health.

    Returns:
        dict: Complete system status
    """
    try:
        # Get latest sensor data
        sensor_data = database.get_latest_status_data()

        # Get thresholds
        thresholds = database.get_thresholds()

        # Get latest visual health assessment
        visual_health = database.get_latest_image_data()

        # Calculate condition index
        condition_index = calculate_condition_index(sensor_data, thresholds)

        # Calculate overall health
        overall_health = calculate_overall_health(condition_index, visual_health)

        # Add sensor status information (which sensors are providing mock data)
        sensor_status = {
            'ph_water': {
                'status': 'mock',
                'message': 'Sensor under repair - showing mock data'
            },
            'uv_ambient': {
                'status': 'mock',
                'message': 'Sensor under repair - showing mock data'
            }
        }

        # Combine all data
        status = {
            'timestamp': datetime.now().isoformat(),
            'sensor_data': sensor_data,
            'thresholds': thresholds,
            'visual_health': visual_health,
            'condition_index': condition_index,
            'overall_health': overall_health,
            'sensor_status': sensor_status
        }

        return status

    except Exception as e:
        logger.error(f"Error getting complete status: {e}")
        return {
            'error': str(e)
        }
