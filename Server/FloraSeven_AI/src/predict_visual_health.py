"""
Module to predict plant visual health for the FloraSeven backend.

This module provides a function to predict the visual health of a plant
from an image captured by the ESP32-CAM.
"""

import os
import json
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.models import load_model

# Define constants
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, 'models')
MODEL_NAME = 'model1_whole_plant_health'
IMG_SIZE = 224

# Global variables to cache the model and class indices
_model = None
_idx_to_class = None

def _load_model_if_needed():
    """Load the model if it hasn't been loaded yet."""
    global _model, _idx_to_class

    if _model is None:
        # Load the model
        model_path = os.path.join(MODELS_DIR, MODEL_NAME)
        _model = load_model(model_path)

        # Load class indices
        class_indices_path = os.path.join(MODELS_DIR, f"{MODEL_NAME}_class_indices.json")
        with open(class_indices_path, 'r') as f:
            class_indices = json.load(f)

        # Invert the dictionary to map indices to class names
        _idx_to_class = {v: k for k, v in class_indices.items()}

def predict_visual_health(image_path=None, image_array=None):
    """
    Predict the visual health of a plant from an image.

    Args:
        image_path (str, optional): Path to the image file.
        image_array (numpy.ndarray, optional): Image as a numpy array.
            If both image_path and image_array are provided, image_path takes precedence.

    Returns:
        dict: A dictionary containing the prediction results:
            - health_label (str): 'healthy' or 'wilting'
            - confidence (float): Confidence score (0-1)
            - health_score (int): Health score (0-100)

    Raises:
        ValueError: If neither image_path nor image_array is provided.
        FileNotFoundError: If the image file does not exist.
    """
    # Load the model if needed
    _load_model_if_needed()

    # Check input
    if image_path is None and image_array is None:
        raise ValueError("Either image_path or image_array must be provided")

    # Preprocess the image
    if image_path is not None:
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found at {image_path}")

        img = load_img(image_path, target_size=(IMG_SIZE, IMG_SIZE))
        img_array = img_to_array(img)
    else:
        # Resize the image if needed
        if image_array.shape[0] != IMG_SIZE or image_array.shape[1] != IMG_SIZE:
            img_array = tf.image.resize(image_array, (IMG_SIZE, IMG_SIZE)).numpy()
        else:
            img_array = image_array.copy()

    # Normalize the image
    img_array = img_array / 255.0

    # Add batch dimension
    img_array = np.expand_dims(img_array, axis=0)

    # Make prediction
    prediction = _model.predict(img_array, verbose=0)[0][0]
    predicted_class = 1 if prediction > 0.5 else 0
    predicted_class_name = _idx_to_class[predicted_class]
    confidence = prediction if predicted_class == 1 else 1 - prediction

    # Calculate health score (0-100)
    # Higher health score = healthier plant
    if predicted_class_name == 'wilting':
        # For wilting plants, health score is inverse of prediction
        health_score = int((1 - prediction) * 100)
    else:  # healthy
        # For healthy plants, health score is inverse of prediction
        # (since values close to 0 mean healthy with high confidence)
        health_score = int((1 - prediction) * 100)

    # Return results
    return {
        'health_label': predicted_class_name,
        'confidence': float(confidence),
        'health_score': health_score
    }

# Example usage
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python predict_visual_health.py <image_path>")
        sys.exit(1)

    image_path = sys.argv[1]
    result = predict_visual_health(image_path=image_path)

    print(f"Health Label: {result['health_label']}")
    print(f"Confidence: {result['confidence']:.4f}")
    print(f"Health Score: {result['health_score']}/100")
