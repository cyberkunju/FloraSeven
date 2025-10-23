"""
Prediction utilities for FloraSeven AI model.
"""

import tensorflow as tf
import numpy as np
import os
import cv2
from typing import Dict, Any, Optional, Union, List, Tuple
import json
import time

class PlantHealthPredictor:
    """Plant health prediction class for FloraSeven backend."""
    
    def __init__(
        self,
        model_path: str,
        class_names: Optional[List[str]] = None,
        image_size: Tuple[int, int] = (224, 224),
        use_grad_cam: bool = True
    ):
        """
        Initialize the plant health predictor.
        
        Args:
            model_path: Path to the saved model
            class_names: List of class names (if None, tries to load from model directory)
            image_size: Input image size (height, width)
            use_grad_cam: Whether to generate Grad-CAM visualizations
        """
        self.model_path = model_path
        self.image_size = image_size
        self.use_grad_cam = use_grad_cam
        
        # Load model
        self.model = self._load_model()
        
        # Load class names
        self.class_names = class_names
        if self.class_names is None:
            self.class_names = self._load_class_names()
        
        # Initialize last conv layer for Grad-CAM
        self.last_conv_layer = None
        if self.use_grad_cam:
            self._initialize_grad_cam()
    
    def _load_model(self) -> tf.keras.Model:
        """
        Load the saved model.
        
        Returns:
            Loaded Keras model
        """
        print(f"Loading model from {self.model_path}")
        try:
            model = tf.keras.models.load_model(self.model_path)
            print("Model loaded successfully")
            return model
        except Exception as e:
            print(f"Error loading model: {e}")
            raise
    
    def _load_class_names(self) -> List[str]:
        """
        Load class names from model directory.
        
        Returns:
            List of class names
        """
        # Try to find a class_names.json file in the model directory
        model_dir = os.path.dirname(self.model_path)
        class_names_path = os.path.join(model_dir, 'class_names.json')
        
        if os.path.exists(class_names_path):
            with open(class_names_path, 'r') as f:
                class_names = json.load(f)
            print(f"Loaded class names: {class_names}")
            return class_names
        
        # If not found, use default class names
        default_class_names = ['healthy', 'wilted']
        print(f"Using default class names: {default_class_names}")
        return default_class_names
    
    def _initialize_grad_cam(self) -> None:
        """Initialize Grad-CAM by finding the last convolutional layer."""
        for layer in reversed(self.model.layers):
            if isinstance(layer, tf.keras.layers.Conv2D):
                self.last_conv_layer = layer
                print(f"Found last convolutional layer for Grad-CAM: {layer.name}")
                break
        
        if self.last_conv_layer is None:
            print("Warning: No convolutional layer found for Grad-CAM")
            self.use_grad_cam = False
    
    def _preprocess_image(self, image_path: str) -> np.ndarray:
        """
        Preprocess an image for prediction.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Preprocessed image array
        """
        # Load image
        img = tf.keras.preprocessing.image.load_img(
            image_path,
            target_size=self.image_size
        )
        
        # Convert to array and normalize
        img_array = tf.keras.preprocessing.image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0) / 255.0
        
        return img_array
    
    def _generate_grad_cam(
        self,
        image_path: str,
        preprocessed_img: np.ndarray,
        output_path: Optional[str] = None
    ) -> Optional[str]:
        """
        Generate Grad-CAM visualization.
        
        Args:
            image_path: Path to the original image
            preprocessed_img: Preprocessed image array
            output_path: Path to save the visualization (if None, a path is generated)
            
        Returns:
            Path to the saved visualization, or None if generation failed
        """
        if not self.use_grad_cam or self.last_conv_layer is None:
            return None
        
        try:
            # Create a model that outputs both the predictions and the last conv layer activations
            grad_model = tf.keras.models.Model(
                inputs=[self.model.inputs],
                outputs=[self.model.output, self.last_conv_layer.output]
            )
            
            # Compute gradients
            with tf.GradientTape() as tape:
                preds, conv_outputs = grad_model(preprocessed_img)
                if len(self.class_names) == 2:
                    # Binary classification
                    class_idx = 0 if preds[0][0] < 0.5 else 1
                    loss = 1 - preds[0][0] if class_idx == 0 else preds[0][0]
                else:
                    # Multi-class classification
                    class_idx = tf.argmax(preds[0])
                    loss = preds[0, class_idx]
            
            # Extract gradients
            grads = tape.gradient(loss, conv_outputs)
            
            # Global average pooling
            pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
            
            # Weight the channels by the gradients
            conv_outputs = conv_outputs[0]
            heatmap = tf.reduce_sum(tf.multiply(pooled_grads, conv_outputs), axis=-1)
            
            # Normalize the heatmap
            heatmap = tf.maximum(heatmap, 0) / tf.math.reduce_max(heatmap)
            heatmap = heatmap.numpy()
            
            # Load the original image
            img = cv2.imread(image_path)
            
            # Resize the heatmap to the original image size
            heatmap = cv2.resize(heatmap, (img.shape[1], img.shape[0]))
            
            # Convert heatmap to RGB
            heatmap = np.uint8(255 * heatmap)
            heatmap = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
            
            # Superimpose the heatmap on the original image
            superimposed_img = heatmap * 0.4 + img
            superimposed_img = np.clip(superimposed_img, 0, 255).astype('uint8')
            
            # Generate output path if not provided
            if output_path is None:
                output_dir = os.path.dirname(image_path)
                base_name = os.path.basename(image_path)
                name, ext = os.path.splitext(base_name)
                output_path = os.path.join(output_dir, f"{name}_gradcam{ext}")
            
            # Save the visualization
            cv2.imwrite(output_path, superimposed_img)
            
            return output_path
        except Exception as e:
            print(f"Error generating Grad-CAM: {e}")
            return None
    
    def predict(self, image_path: str, generate_grad_cam: bool = True) -> Dict[str, Any]:
        """
        Predict the health of a plant from an image.
        
        Args:
            image_path: Path to the image file
            generate_grad_cam: Whether to generate Grad-CAM visualization
            
        Returns:
            Dictionary with prediction results
        """
        # Check if image exists
        if not os.path.exists(image_path):
            return {
                'error': f"Image not found: {image_path}",
                'success': False
            }
        
        try:
            # Start timing
            start_time = time.time()
            
            # Preprocess image
            preprocessed_img = self._preprocess_image(image_path)
            
            # Make prediction
            prediction = self.model.predict(preprocessed_img)[0]
            
            # Process prediction based on number of classes
            if len(self.class_names) == 2:
                # Binary classification
                confidence = float(prediction[0]) if isinstance(prediction, np.ndarray) else float(prediction)
                label = self.class_names[1] if confidence >= 0.5 else self.class_names[0]
                confidence = confidence if label == self.class_names[1] else 1 - confidence
                
                # Calculate health score (0-100)
                if label == 'healthy':
                    health_score = int(confidence * 100)
                else:
                    health_score = int((1 - confidence) * 100)
                
                # Get class probabilities
                class_probs = {
                    self.class_names[0]: float(1 - confidence),
                    self.class_names[1]: float(confidence)
                }
            else:
                # Multi-class classification
                label_idx = np.argmax(prediction)
                confidence = float(prediction[label_idx])
                label = self.class_names[label_idx]
                
                # Calculate health score based on class
                if label == 'healthy':
                    health_score = int(confidence * 100)
                else:
                    health_score = int((1 - confidence) * 50)  # Scale to 0-50 for non-healthy classes
                
                # Get class probabilities
                class_probs = {
                    class_name: float(prediction[i])
                    for i, class_name in enumerate(self.class_names)
                }
            
            # Generate Grad-CAM visualization if requested
            grad_cam_path = None
            if generate_grad_cam and self.use_grad_cam:
                grad_cam_path = self._generate_grad_cam(image_path, preprocessed_img)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            return {
                'success': True,
                'label': label,
                'confidence': confidence,
                'health_score': health_score,
                'class_probabilities': class_probs,
                'grad_cam_path': grad_cam_path,
                'processing_time': processing_time
            }
        except Exception as e:
            return {
                'error': str(e),
                'success': False
            }
    
    def predict_visual_health(self, image_path: str) -> Dict[str, Any]:
        """
        Predict the visual health of a plant from an image.
        This is the main function to be used by the FloraSeven backend.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary with prediction results
        """
        result = self.predict(image_path)
        
        if not result.get('success', False):
            return {
                'error': result.get('error', 'Unknown error'),
                'health_label': 'unknown',
                'health_score': 0,
                'confidence': 0
            }
        
        return {
            'health_label': result['label'],
            'health_score': result['health_score'],
            'confidence': result['confidence'],
            'visualization_path': result.get('grad_cam_path')
        }
