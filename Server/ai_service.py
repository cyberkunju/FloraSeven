"""
AI service module for the FloraSeven server.

This module provides functions for analyzing plant images using the
TensorFlow model to determine plant health.
"""
import os
import sys
import json
import logging
from datetime import datetime

import numpy as np
import tensorflow as tf
from tensorflow import keras
from PIL import Image

import config

# Set up logging
logger = logging.getLogger(__name__)

# Add FloraSeven_AI to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'FloraSeven_AI'))

# Try to import the predict_visual_health function
try:
    # Use the Keras 3 compatible version
    from src.predict_visual_health_keras3 import predict_visual_health as imported_predict_visual_health
    logger.info("Successfully imported predict_visual_health_keras3 from FloraSeven_AI")
except ImportError as e:
    logger.warning(f"Could not import predict_visual_health_keras3 from FloraSeven_AI: {e}")
    imported_predict_visual_health = None

class AIService:
    """AI service for plant health analysis."""

    def __init__(self, model_dir, class_indices_file):
        """
        Initialize the AI service.

        Args:
            model_dir (str): Path to the TensorFlow model directory
            class_indices_file (str): Path to the class indices JSON file
        """
        self.model_dir = model_dir
        self.class_indices_file = class_indices_file
        self.model = None
        self.class_indices = None

        # Load model and class indices
        self._load_model()
        self._load_class_indices()

    def _load_model(self):
        """Load the TensorFlow model."""
        try:
            logger.info(f"Loading model from {self.model_dir}")
            # Use TFSMLayer for TensorFlow SavedModel format
            self.model = keras.Sequential([
                keras.layers.TFSMLayer(self.model_dir, call_endpoint='serving_default')
            ])
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise

    def _load_class_indices(self):
        """Load class indices from JSON file."""
        try:
            logger.info(f"Loading class indices from {self.class_indices_file}")
            with open(self.class_indices_file, 'r') as f:
                self.class_indices = json.load(f)
            logger.info(f"Class indices loaded: {self.class_indices}")

            # Invert the dictionary to map indices to class names
            self.idx_to_class = {v: k for k, v in self.class_indices.items()}
        except Exception as e:
            logger.error(f"Error loading class indices: {e}")
            raise

    def analyze_image(self, image_path):
        """
        Analyze a plant image to determine its health.

        Args:
            image_path (str): Path to the image file

        Returns:
            dict: Dictionary containing prediction results
        """
        logger.info(f"Analyzing image: {image_path}")

        # Check if image exists
        if not os.path.exists(image_path):
            logger.error(f"Image not found: {image_path}")
            return {
                'health_label': 'error',
                'health_score': 0,
                'confidence': 0.0,
                'error': f"Image not found: {image_path}"
            }

        try:
            # If the imported predict_visual_health function is available, use it
            if imported_predict_visual_health is not None:
                logger.info("Using imported predict_visual_health function")
                result = imported_predict_visual_health(image_path=image_path)
                return result

            # Otherwise, use our own implementation
            logger.info("Using internal implementation for prediction")
            return self._predict_visual_health(image_path)

        except Exception as e:
            logger.error(f"Error analyzing image: {e}")
            return {
                'health_label': 'error',
                'health_score': 0,
                'confidence': 0.0,
                'error': str(e)
            }

    def _predict_visual_health(self, image_path):
        """
        Internal implementation of visual health prediction.

        Args:
            image_path (str): Path to the image file

        Returns:
            dict: Dictionary containing prediction results
        """
        # Load and preprocess image
        # Note: This preprocessing must match exactly what was used during model training
        # The model expects images resized to 224x224 pixels and normalized to [0,1] range
        img = tf.keras.preprocessing.image.load_img(
            image_path,
            target_size=(224, 224)
        )
        img_array = tf.keras.preprocessing.image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0) / 255.0  # Normalize to [0,1] range

        # Make prediction
        # TFSMLayer returns a dictionary with the output tensor
        prediction_dict = self.model(img_array)

        # Get the prediction tensor from the dictionary
        # The key might be different based on your model's output layer name
        # Common names are 'output', 'predictions', or the name of the last layer
        output_key = list(prediction_dict.keys())[0]  # Get the first key
        prediction = prediction_dict[output_key].numpy()[0]  # Convert to numpy and get first item

        # Process prediction based on model type
        if isinstance(prediction, np.ndarray) and len(prediction) > 1:
            # Multi-class classification
            predicted_class_idx = np.argmax(prediction)
            confidence = float(prediction[predicted_class_idx])
            predicted_label = self.idx_to_class[predicted_class_idx]
        else:
            # Binary classification with single output
            # For our model, output closer to 1 means "wilting" (index 1)
            # Output closer to 0 means "healthy" (index 0)
            confidence = float(prediction[0]) if isinstance(prediction, np.ndarray) else float(prediction)
            predicted_label = self.idx_to_class[1] if confidence >= 0.5 else self.idx_to_class[0]
            # Ensure confidence is always relative to the predicted class
            confidence = confidence if predicted_label == self.idx_to_class[1] else 1 - confidence

        # Calculate health score (0-100)
        if predicted_label == 'healthy':
            health_score = int(confidence * 100)
        else:
            health_score = int((1 - confidence) * 100)

        logger.info(f"Prediction: {predicted_label}, Score: {health_score}, Confidence: {confidence:.4f}")

        return {
            'health_label': predicted_label,
            'health_score': health_score,
            'confidence': confidence
        }

# Initialize the AI service
try:
    ai_service = AIService(
        model_dir=config.AI_MODEL_DIR,
        class_indices_file=config.AI_CLASS_INDICES_FILE
    )
    logger.info("AI service initialized successfully")
except Exception as e:
    logger.error(f"Error initializing AI service: {e}")
    ai_service = None
