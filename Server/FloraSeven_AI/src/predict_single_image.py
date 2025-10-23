"""
Script to test Model 1 (Whole Plant Health) on a single image.

This script will:
1. Load the trained Model 1
2. Run a prediction on a single image
3. Display the image with the prediction result
"""

import os
import sys
import json
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.models import load_model

# Define constants
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, 'models')
MODEL_NAME = 'model1_whole_plant_health'
IMG_SIZE = 224

def load_trained_model():
    """Load the trained model."""
    model_path = os.path.join(MODELS_DIR, MODEL_NAME)
    model = load_model(model_path)
    
    # Load class indices
    class_indices_path = os.path.join(MODELS_DIR, f"{MODEL_NAME}_class_indices.json")
    with open(class_indices_path, 'r') as f:
        class_indices = json.load(f)
    
    # Invert the dictionary to map indices to class names
    idx_to_class = {v: k for k, v in class_indices.items()}
    
    return model, idx_to_class

def predict_image(model, image_path, idx_to_class):
    """Make a prediction on a single image."""
    # Load and preprocess the image
    img = load_img(image_path, target_size=(IMG_SIZE, IMG_SIZE))
    img_array = img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    
    # Make prediction
    prediction = model.predict(img_array)[0][0]
    predicted_class = 1 if prediction > 0.5 else 0
    predicted_class_name = idx_to_class[predicted_class]
    confidence = prediction if predicted_class == 1 else 1 - prediction
    
    return img, predicted_class_name, confidence

def display_prediction(img, predicted_class, confidence):
    """Display the image with the prediction result."""
    plt.figure(figsize=(8, 8))
    plt.imshow(img)
    plt.title(f"Prediction: {predicted_class.capitalize()}\nConfidence: {confidence:.2f}", fontsize=16)
    plt.axis('off')
    plt.tight_layout()
    plt.show()
    
    # Save the visualization
    output_dir = os.path.join(BASE_DIR, 'results')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "single_prediction_result.png")
    plt.savefig(output_path)
    print(f"Prediction visualization saved to: {output_path}")

def main():
    """Main function to test Model 1 on a single image."""
    # Check if image path is provided
    if len(sys.argv) < 2:
        print("Usage: python predict_single_image.py <image_path>")
        return
    
    image_path = sys.argv[1]
    if not os.path.exists(image_path):
        print(f"Error: Image not found at {image_path}")
        return
    
    print(f"Loading trained model...")
    model, idx_to_class = load_trained_model()
    
    print(f"Making prediction on {image_path}...")
    img, predicted_class, confidence = predict_image(model, image_path, idx_to_class)
    
    print(f"Prediction: {predicted_class.capitalize()}")
    print(f"Confidence: {confidence:.4f}")
    
    display_prediction(img, predicted_class, confidence)

if __name__ == "__main__":
    main()
