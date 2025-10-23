"""
Data visualization module for the FloraSeven server.

This module provides functions for generating charts and visualizations.
"""
import os
import logging
import io
import base64
from datetime import datetime, timedelta

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

import database

# Set up logging
logger = logging.getLogger(__name__)

def generate_sensor_chart(node_id, sensor_type, hours=24):
    """
    Generate a chart for a specific sensor.
    
    Args:
        node_id (str): Identifier for the node
        sensor_type (str): Type of sensor
        hours (int): Number of hours of data to include
        
    Returns:
        str: Base64-encoded PNG image
    """
    try:
        # Calculate start time
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        # Get sensor history
        history = database.get_sensor_history(
            node_id, 
            sensor_type,
            start_time=start_time.isoformat(),
            end_time=end_time.isoformat(),
            limit=1000
        )
        
        if not history:
            logger.warning(f"No data found for {node_id} {sensor_type}")
            return None
        
        # Extract data
        timestamps = [datetime.fromisoformat(item['timestamp']) for item in history]
        values = [item['value'] for item in history]
        
        # Create figure
        plt.figure(figsize=(10, 6))
        plt.plot(timestamps, values, 'b-')
        plt.title(f"{sensor_type.replace('_', ' ').title()} ({node_id})")
        plt.xlabel('Time')
        plt.ylabel(sensor_type.replace('_', ' ').title())
        
        # Format x-axis
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=2))
        plt.gcf().autofmt_xdate()
        
        # Add grid
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # Get thresholds
        thresholds = database.get_thresholds().get(sensor_type)
        if thresholds:
            # Add threshold lines
            plt.axhline(y=thresholds['min'], color='r', linestyle='--', alpha=0.7, label=f"Min ({thresholds['min']})")
            plt.axhline(y=thresholds['max'], color='r', linestyle='--', alpha=0.7, label=f"Max ({thresholds['max']})")
            
            # Add warning threshold lines
            warning_min = thresholds['min'] + (thresholds['max'] - thresholds['min']) * 0.1
            warning_max = thresholds['max'] - (thresholds['max'] - thresholds['min']) * 0.1
            plt.axhline(y=warning_min, color='y', linestyle='--', alpha=0.7, label=f"Warning Min ({warning_min:.1f})")
            plt.axhline(y=warning_max, color='y', linestyle='--', alpha=0.7, label=f"Warning Max ({warning_max:.1f})")
            
            # Add legend
            plt.legend()
        
        # Save to buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        plt.close()
        
        # Convert to base64
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        
        return img_base64
    
    except Exception as e:
        logger.error(f"Error generating sensor chart: {e}")
        return None

def generate_health_history_chart(days=7):
    """
    Generate a chart showing plant health history.
    
    Args:
        days (int): Number of days of data to include
        
    Returns:
        str: Base64-encoded PNG image
    """
    try:
        # Calculate start time
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        
        # Get image history
        history = database.get_image_history(
            start_time=start_time.isoformat(),
            end_time=end_time.isoformat(),
            limit=100
        )
        
        if not history:
            logger.warning("No image history found")
            return None
        
        # Extract data
        timestamps = [datetime.fromisoformat(item['timestamp']) for item in history]
        health_scores = [item['health_score'] for item in history]
        
        # Create figure
        plt.figure(figsize=(10, 6))
        plt.plot(timestamps, health_scores, 'g-o')
        plt.title(f"Plant Health History (Last {days} Days)")
        plt.xlabel('Date')
        plt.ylabel('Health Score (0-100)')
        
        # Format x-axis
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1))
        plt.gcf().autofmt_xdate()
        
        # Set y-axis limits
        plt.ylim(0, 100)
        
        # Add grid
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # Add health zones
        plt.axhspan(0, 40, alpha=0.2, color='red', label='Critical')
        plt.axhspan(40, 70, alpha=0.2, color='yellow', label='Warning')
        plt.axhspan(70, 100, alpha=0.2, color='green', label='Healthy')
        
        # Add legend
        plt.legend()
        
        # Save to buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        plt.close()
        
        # Convert to base64
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        
        return img_base64
    
    except Exception as e:
        logger.error(f"Error generating health history chart: {e}")
        return None

def generate_dashboard():
    """
    Generate a dashboard with multiple charts.
    
    Returns:
        dict: Dictionary with base64-encoded charts
    """
    try:
        dashboard = {
            'moisture_chart': generate_sensor_chart('plantNode1', 'moisture', hours=24),
            'temperature_chart': generate_sensor_chart('plantNode1', 'temp_soil', hours=24),
            'light_chart': generate_sensor_chart('plantNode1', 'light_lux', hours=24),
            'ec_chart': generate_sensor_chart('plantNode1', 'ec_raw', hours=24),
            'ph_chart': generate_sensor_chart('hubNode', 'ph_water', hours=24),
            'uv_chart': generate_sensor_chart('hubNode', 'uv_ambient', hours=24),
            'health_chart': generate_health_history_chart(days=7)
        }
        
        return dashboard
    
    except Exception as e:
        logger.error(f"Error generating dashboard: {e}")
        return {}
