"""
Prediction script for FloraSeven AI plant health classification.

This script provides functions for making predictions on new plant images,
including the predict_visual_health() function that will be used by the backend.
"""

import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import matplotlib.pyplot as plt
import cv2
import logging
import sys
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("prediction.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("prediction")

# Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, 'models')

# Image parameters
IMG_SIZE = 224  # MobileNetV2/EfficientNetB0 input size
CONFIDENCE_THRESHOLD = 0.6  # Threshold for "Uncertain" classification

# Class mapping
CLASS_MAPPING = {
    0: 'healthy',
    1: 'wilting',
    2: 'discolored'
}

def load_trained_model(model_path=None):
    """
    Load the trained model.

    Args:
        model_path: Path to the model file. If None, use the latest fine-tuned model.

    Returns:
        model: Loaded Keras model
    """
    if model_path is None:
        # Find the latest fine-tuned model
        model_files = [f for f in os.listdir(MODELS_DIR) if f.endswith('.h5') and 'fine_tuned' in f]
        if not model_files:
            raise FileNotFoundError("No fine-tuned model found in models directory")

        # Sort by modification time (newest first)
        model_files.sort(key=lambda x: os.path.getmtime(os.path.join(MODELS_DIR, x)), reverse=True)
        model_path = os.path.join(MODELS_DIR, model_files[0])

    logger.info(f"Loading model from {model_path}")
    model = load_model(model_path)
    return model

def preprocess_image(image_path):
    """
    Preprocess an image for prediction.

    Args:
        image_path: Path to the image file

    Returns:
        preprocessed_img: Preprocessed image as a numpy array
    """
    # Check if image exists
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    # Check image quality
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not read image: {image_path}")

    # Check for blur
    laplacian_var = cv2.Laplacian(img, cv2.CV_64F).var()
    if laplacian_var < 100:  # Threshold for blur detection
        logger.warning(f"Image may be blurry: {image_path}, Laplacian variance: {laplacian_var}")

    # Load and resize image
    img = load_img(image_path, target_size=(IMG_SIZE, IMG_SIZE))

    # Convert to array and normalize
    img_array = img_to_array(img)
    preprocessed_img = np.expand_dims(img_array, axis=0) / 255.0

    return preprocessed_img

def generate_cam(model, preprocessed_img, class_idx):
    """
    Generate Class Activation Map (CAM) to visualize which regions influenced the prediction.

    Args:
        model: Trained Keras model
        preprocessed_img: Preprocessed image as a numpy array
        class_idx: Index of the predicted class

    Returns:
        cam_image: Class activation map as a numpy array
    """
    try:
        # Get the last convolutional layer
        last_conv_layer = None
        for layer in reversed(model.layers):
            if isinstance(layer, tf.keras.layers.Conv2D):
                last_conv_layer = layer.name
                break

        if last_conv_layer is None:
            logger.warning("Could not find convolutional layer for CAM generation")
            return None

        # Create a model that outputs the last conv layer activations and the final predictions
        grad_model = tf.keras.models.Model(
            inputs=[model.inputs],
            outputs=[model.get_layer(last_conv_layer).output, model.output]
        )

        # Compute gradients
        with tf.GradientTape() as tape:
            conv_outputs, predictions = grad_model(preprocessed_img)
            loss = predictions[:, class_idx]

        # Extract gradients
        grads = tape.gradient(loss, conv_outputs)

        # Global average pooling
        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

        # Weight the channels by the gradients
        conv_outputs = conv_outputs[0]
        heatmap = tf.reduce_sum(tf.multiply(pooled_grads, conv_outputs), axis=-1)

        # Normalize heatmap
        heatmap = tf.maximum(heatmap, 0) / tf.math.reduce_max(heatmap)
        heatmap = heatmap.numpy()

        # Resize heatmap to original image size
        heatmap = cv2.resize(heatmap, (IMG_SIZE, IMG_SIZE))

        # Convert heatmap to RGB
        heatmap = np.uint8(255 * heatmap)
        heatmap = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)

        # Superimpose heatmap on original image
        original_img = (preprocessed_img[0] * 255).astype(np.uint8)
        cam_image = cv2.addWeighted(original_img, 0.7, heatmap, 0.3, 0)

        return cam_image

    except Exception as e:
        logger.error(f"Error generating CAM: {e}")
        return None

def predict_visual_health(image_path, model_path=None, generate_visualization=False):
    """
    Predict the visual health of a plant from an image.

    Args:
        image_path: Path to the image file
        model_path: Path to the model file (optional)
        generate_visualization: Whether to generate and return CAM visualization

    Returns:
        result: Dictionary containing prediction results
    """
    try:
        # Load model
        model = load_trained_model(model_path)

        # Check if image exists
        if not os.path.exists(image_path):
            logger.error(f"Image not found: {image_path}")
            return {
                'health_label': 'error',
                'health_score': 0,
                'confidence': 0.0,
                'error': f"Image not found: {image_path}"
            }

        # Check if image is blurry
        laplacian_var = calculate_laplacian_variance(image_path)
        if is_blurry(image_path):
            logger.warning(f"Image may be blurry: {image_path}, Laplacian variance: {laplacian_var}")

        # Preprocess image
        preprocessed_img = preprocess_image(image_path)

        # Make prediction
        prediction = model.predict(preprocessed_img)[0]

        # Get predicted class and confidence
        predicted_class_idx = np.argmax(prediction)
        confidence = float(prediction[predicted_class_idx])
        predicted_label = CLASS_MAPPING[predicted_class_idx]

        # Increased confidence threshold for better certainty
        enhanced_threshold = 0.65

        # Check confidence threshold
        if confidence < CONFIDENCE_THRESHOLD:
            health_label = "uncertain"
            logger.info(f"Low confidence prediction ({confidence:.4f}) for {image_path}, marking as uncertain")
        else:
            health_label = predicted_label

        # Special case for healthy plants - if predicted as wilting or discolored with moderate confidence,
        # and the image is not blurry, consider it as uncertain
        if predicted_label in ['wilting', 'discolored'] and confidence < enhanced_threshold and laplacian_var > 100:
            health_label = "uncertain"
            logger.info(f"Moderate confidence prediction ({confidence:.4f}) with good image quality, marking as uncertain")

        # Convert confidence to health score (0-100)
        health_score = int(confidence * 100)

        # Create result dictionary
        result = {
            'health_label': health_label,
            'health_score': health_score,
            'confidence': confidence,
            'raw_predictions': {CLASS_MAPPING[i]: float(prediction[i]) for i in range(len(prediction))},
            'image_quality': {
                'laplacian_variance': laplacian_var,
                'is_blurry': is_blurry(image_path)
            }
        }

        # Generate CAM visualization if requested
        if generate_visualization:
            cam_image = generate_cam(model, preprocessed_img, predicted_class_idx)
            if cam_image is not None:
                # Save visualization
                visualization_path = os.path.join(os.path.dirname(image_path),
                                                 f"{os.path.splitext(os.path.basename(image_path))[0]}_cam.jpg")
                cv2.imwrite(visualization_path, cam_image)
                result['visualization_path'] = visualization_path

        logger.info(f"Prediction for {os.path.basename(image_path)}: {health_label} (score: {health_score}, confidence: {confidence:.4f})")
        return result

    except Exception as e:
        logger.error(f"Error predicting visual health: {e}")
        return {
            'health_label': 'error',
            'health_score': 0,
            'confidence': 0.0,
            'error': str(e)
        }

def batch_predict(image_dir, output_file=None, visualize=False):
    """
    Make predictions on all images in a directory.

    Args:
        image_dir: Directory containing images
        output_file: Path to save results (optional)
        visualize: Whether to generate CAM visualizations

    Returns:
        results: Dictionary mapping image filenames to prediction results
    """
    # Check if directory exists
    if not os.path.exists(image_dir):
        raise FileNotFoundError(f"Directory not found: {image_dir}")

    # Get all image files
    image_files = [f for f in os.listdir(image_dir)
                  if os.path.isfile(os.path.join(image_dir, f)) and
                  f.lower().endswith(('.png', '.jpg', '.jpeg'))]

    if not image_files:
        logger.warning(f"No images found in {image_dir}")
        return {}

    logger.info(f"Found {len(image_files)} images in {image_dir}")

    # Make predictions using the improved predict_visual_health function
    results = {}
    for filename in image_files:
        image_path = os.path.join(image_dir, filename)
        result = predict_visual_health(image_path, generate_visualization=visualize)
        results[filename] = result

    # Save results if output file specified
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=4)
        logger.info(f"Batch prediction results saved to {output_file}")

    # Print summary statistics
    health_counts = {}
    for result in results.values():
        label = result['health_label']
        health_counts[label] = health_counts.get(label, 0) + 1

    logger.info("Prediction summary:")
    for label, count in health_counts.items():
        percentage = (count / len(results)) * 100
        logger.info(f"  {label}: {count} images ({percentage:.1f}%)")

    return results

def main():
    """Main function for demonstration."""
    import argparse

    parser = argparse.ArgumentParser(description='Predict plant visual health')
    parser.add_argument('--image', type=str, help='Path to image file')
    parser.add_argument('--dir', type=str, help='Path to directory of images')
    parser.add_argument('--model', type=str, help='Path to model file (optional)')
    parser.add_argument('--visualize', action='store_true', help='Generate CAM visualization')
    parser.add_argument('--output', type=str, help='Output file for batch predictions')

    args = parser.parse_args()

    if args.image:
        # Single image prediction
        result = predict_visual_health(args.image, args.model, args.visualize)
        print(json.dumps(result, indent=4))

    elif args.dir:
        # Batch prediction
        results = batch_predict(args.dir, args.output, args.visualize)
        if not args.output:
            print(json.dumps(results, indent=4))

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
