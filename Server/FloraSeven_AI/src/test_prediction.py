"""
Test script for prediction functionality.

This script tests the prediction functionality using the sample images.
Since we don't have a trained model yet, it will create a dummy model for testing.
"""

import os
import sys
import tensorflow as tf
import numpy as np
import logging
import json
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras.models import Model

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("test_prediction")

# Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLE_DIR = os.path.join(BASE_DIR, 'sample_images')
MODELS_DIR = os.path.join(BASE_DIR, 'models')

# Create models directory if it doesn't exist
os.makedirs(MODELS_DIR, exist_ok=True)

# Constants
IMG_SIZE = 224
NUM_CLASSES = 3
CLASS_MAPPING = {
    0: 'healthy',
    1: 'wilting',
    2: 'discolored'
}

def create_dummy_model():
    """
    Create a dummy model for testing prediction functionality.

    Returns:
        model: A simple MobileNetV2-based model
    """
    logger.info("Creating dummy model for testing")

    # Create a base model
    base_model = MobileNetV2(
        input_shape=(IMG_SIZE, IMG_SIZE, 3),
        include_top=False,
        weights='imagenet'
    )

    # Freeze the base model
    base_model.trainable = False

    # Add custom layers
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(128, activation='relu')(x)
    predictions = Dense(NUM_CLASSES, activation='softmax')(x)

    # Create the model
    model = Model(inputs=base_model.input, outputs=predictions)

    # Compile the model
    model.compile(
        optimizer='adam',
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )

    # Save the model
    model_path = os.path.join(MODELS_DIR, 'dummy_model.h5')
    model.save(model_path)
    logger.info(f"Dummy model saved to {model_path}")

    return model

def test_prediction():
    """
    Test the prediction functionality using the sample images.
    """
    # Import the predict_visual_health function
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from predict import predict_visual_health

    # Check if sample images exist
    if not os.path.exists(SAMPLE_DIR):
        logger.error(f"Sample directory not found: {SAMPLE_DIR}")
        logger.info("Please run download_sample_images.py first")
        return False

    sample_images = [f for f in os.listdir(SAMPLE_DIR)
                    if os.path.isfile(os.path.join(SAMPLE_DIR, f)) and
                    f.lower().endswith(('.png', '.jpg', '.jpeg'))]

    if not sample_images:
        logger.error("No sample images found")
        logger.info("Please run download_sample_images.py first")
        return False

    # Use the trained model if it exists
    model_path = os.path.join(MODELS_DIR, 'MobileNetV2_fine_tuned.h5')
    if not os.path.exists(model_path):
        # Fall back to dummy model if trained model doesn't exist
        model_path = os.path.join(MODELS_DIR, 'dummy_model.h5')
        if not os.path.exists(model_path):
            create_dummy_model()

    logger.info(f"Using model: {model_path}")

    # Test prediction on each sample image
    logger.info("Testing prediction on sample images")

    results = {}
    for image_file in sample_images:
        image_path = os.path.join(SAMPLE_DIR, image_file)
        logger.info(f"Predicting {image_file}")

        # Make prediction
        result = predict_visual_health(image_path, model_path, generate_visualization=True)

        # Store result
        results[image_file] = result

        # Log result
        logger.info(f"Prediction for {image_file}: {result['health_label']} (score: {result['health_score']})")

    # Save results
    results_path = os.path.join(SAMPLE_DIR, 'prediction_results.json')
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=4)
    logger.info(f"Prediction results saved to {results_path}")

    return True

if __name__ == "__main__":
    logger.info("Starting prediction test")
    if test_prediction():
        logger.info("Prediction test completed successfully")
    else:
        logger.error("Prediction test failed")
