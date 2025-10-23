"""
Script to predict plant health from any image.

This script will:
1. Load the trained Model 1
2. Take an image path as input
3. Preprocess the image
4. Make a prediction
5. Display the image with the prediction result
"""

import os
import sys
import json
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
from PIL import Image
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
    """Make a prediction on an image."""
    try:
        # Try to open the image to check if it's valid
        img = Image.open(image_path)
        img = img.convert('RGB')  # Convert to RGB if it's not already

        # Resize and preprocess the image
        img = img.resize((IMG_SIZE, IMG_SIZE))
        img_array = np.array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        # Make prediction
        prediction = model.predict(img_array, verbose=0)[0][0]
        print(f"Raw prediction value: {prediction}")

        # In our model:
        # - Values close to 0 mean "healthy" with high confidence
        # - Values close to 1 mean "wilting" with high confidence
        predicted_class = 1 if prediction > 0.5 else 0
        predicted_class_name = idx_to_class[predicted_class]

        # Confidence is how certain the model is about its prediction
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

        return img, predicted_class_name, confidence, health_score

    except Exception as e:
        print(f"Error processing image: {e}")
        return None, None, None, None

def display_prediction(img, predicted_class, confidence, health_score, save_path=None):
    """Display the image with the prediction result."""
    plt.figure(figsize=(10, 8))
    plt.imshow(img)

    # Set title color based on health score
    if health_score >= 70:
        title_color = 'green'
    elif health_score >= 40:
        title_color = 'orange'
    else:
        title_color = 'red'

    # Format confidence as percentage
    confidence_pct = confidence * 100
    plt.title(f"Prediction: {predicted_class.capitalize()}\nConfidence: {confidence_pct:.1f}%\nHealth Score: {health_score}/100",
              fontsize=16, color=title_color)
    plt.axis('off')
    plt.tight_layout()

    # Save the visualization if a path is provided
    if save_path:
        plt.savefig(save_path)
        print(f"Prediction visualization saved to: {save_path}")

    plt.show()

def main():
    """Main function to predict plant health from any image."""
    # Check if image path is provided
    if len(sys.argv) < 2:
        print("Usage: python predict_any_image.py <image_path>")
        return

    image_path = sys.argv[1]
    if not os.path.exists(image_path):
        print(f"Error: Image not found at {image_path}")
        return

    print(f"Loading trained model...")
    model, idx_to_class = load_trained_model()

    print(f"Making prediction on {image_path}...")
    img, predicted_class, confidence, health_score = predict_image(model, image_path, idx_to_class)

    if img is not None:
        print(f"Prediction: {predicted_class.capitalize()}")
        print(f"Confidence: {confidence:.4f}")
        print(f"Health Score: {health_score}/100")

        # Create output directory if it doesn't exist
        output_dir = os.path.join(BASE_DIR, 'results')
        os.makedirs(output_dir, exist_ok=True)

        # Generate output filename based on input filename
        input_filename = os.path.basename(image_path)
        output_filename = f"prediction_{input_filename}"
        output_path = os.path.join(output_dir, output_filename)

        display_prediction(img, predicted_class, confidence, health_score, save_path=output_path)
    else:
        print("Failed to process the image.")

if __name__ == "__main__":
    main()
