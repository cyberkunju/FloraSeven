"""
Script to test Model 1 (Whole Plant Health) on test images.

This script will:
1. Load the trained Model 1
2. Run predictions on the test set
3. Visualize some sample predictions with their ground truth
4. Calculate and display performance metrics
"""

import os
import json
import random
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.models import load_model
from sklearn.metrics import confusion_matrix, classification_report

# Define constants
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, 'data', 'processed')
TEST_DIR = os.path.join(PROCESSED_DIR, 'test')
MODELS_DIR = os.path.join(BASE_DIR, 'models')
MODEL_NAME = 'model1_whole_plant_health'
IMG_SIZE = 224
NUM_SAMPLES_TO_VISUALIZE = 10

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

def load_test_images():
    """Load test images and their labels."""
    images = []
    labels = []
    file_paths = []
    
    # Load healthy images
    healthy_dir = os.path.join(TEST_DIR, 'healthy')
    for filename in os.listdir(healthy_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            file_path = os.path.join(healthy_dir, filename)
            img = load_img(file_path, target_size=(IMG_SIZE, IMG_SIZE))
            img_array = img_to_array(img) / 255.0
            images.append(img_array)
            labels.append(0)  # 0 for healthy
            file_paths.append(file_path)
    
    # Load wilting images
    wilting_dir = os.path.join(TEST_DIR, 'wilting')
    for filename in os.listdir(wilting_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            file_path = os.path.join(wilting_dir, filename)
            img = load_img(file_path, target_size=(IMG_SIZE, IMG_SIZE))
            img_array = img_to_array(img) / 255.0
            images.append(img_array)
            labels.append(1)  # 1 for wilting
            file_paths.append(file_path)
    
    return np.array(images), np.array(labels), file_paths

def predict_and_evaluate(model, images, labels, idx_to_class):
    """Make predictions and evaluate the model."""
    # Make predictions
    predictions = model.predict(images)
    predicted_classes = (predictions > 0.5).astype(int).flatten()
    
    # Calculate metrics
    cm = confusion_matrix(labels, predicted_classes)
    report = classification_report(labels, predicted_classes, 
                                  target_names=list(idx_to_class.values()),
                                  output_dict=True)
    
    # Print results
    print("\nConfusion Matrix:")
    print(cm)
    print("\nClassification Report:")
    for class_name, metrics in report.items():
        if class_name in ['healthy', 'wilting']:
            print(f"{class_name.capitalize()}:")
            print(f"  Precision: {metrics['precision']:.4f}")
            print(f"  Recall: {metrics['recall']:.4f}")
            print(f"  F1-score: {metrics['f1-score']:.4f}")
    
    print(f"\nAccuracy: {report['accuracy']:.4f}")
    
    return predictions, predicted_classes, cm, report

def visualize_predictions(images, labels, predictions, predicted_classes, file_paths, idx_to_class):
    """Visualize sample predictions."""
    # Combine data for random sampling
    data = list(zip(images, labels, predictions, predicted_classes, file_paths))
    
    # Randomly sample images to visualize
    num_samples = min(NUM_SAMPLES_TO_VISUALIZE, len(data))
    samples = random.sample(data, num_samples)
    
    # Create a figure
    plt.figure(figsize=(15, 12))
    
    # Plot each sample
    for i, (img, label, pred_prob, pred_class, file_path) in enumerate(samples):
        plt.subplot(3, 4, i + 1)
        plt.imshow(img)
        
        # Get class names
        true_class = idx_to_class[label]
        predicted_class = idx_to_class[pred_class]
        
        # Set title color based on correctness
        title_color = 'green' if label == pred_class else 'red'
        
        # Create title with prediction probability
        title = f"True: {true_class}\nPred: {predicted_class} ({pred_prob[0]:.2f})"
        plt.title(title, color=title_color)
        plt.axis('off')
    
    plt.tight_layout()
    
    # Save the visualization
    output_path = os.path.join(BASE_DIR, 'results', f"{MODEL_NAME}_test_results.png")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path)
    print(f"\nTest results visualization saved to: {output_path}")
    
    # Show the plot
    plt.show()

def main():
    """Main function to test Model 1."""
    print("Loading trained model...")
    model, idx_to_class = load_trained_model()
    
    print("Loading test images...")
    images, labels, file_paths = load_test_images()
    print(f"Loaded {len(images)} test images")
    
    print("Making predictions...")
    predictions, predicted_classes, cm, report = predict_and_evaluate(model, images, labels, idx_to_class)
    
    print("Visualizing predictions...")
    visualize_predictions(images, labels, predictions, predicted_classes, file_paths, idx_to_class)
    
    print("\nTesting completed!")

if __name__ == "__main__":
    main()
