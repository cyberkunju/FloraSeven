# FloraSeven v1.0 - AI Integration

## Overview

The FloraSeven system incorporates AI-driven visual analysis to assess plant health from images captured by the Hub Node's camera. ThisW document details the AI model, its integration into the server backend, and the prediction workflow.

## AI Model Details

### Model Information

- **Model Type**: TensorFlow SavedModel (not TensorFlow Lite)
- **Location**: `FloraSeven_AI/models/model1_whole_plant_health/`
- **Classification Type**: Binary classification ("Healthy" or "Wilted")
- **Class Indices**: Defined in `FloraSeven_AI/models/model1_whole_plant_health_class_indices.json`
- **Input Size**: 224x224 pixels, RGB (3 channels)
- **Framework**: TensorFlow (version ≥ 2.8.0)

### Class Indices

The class indices JSON file maps the model's output indices to human-readable labels:

```json
{"healthy": 0, "wilting": 1}
```

This indicates that:
- Output index 0 corresponds to "healthy"
- Output index 1 corresponds to "wilting"

## Existing Code Analysis

### predict_visual_health.py (Primary Implementation)

The `FloraSeven_AI/src/predict_visual_health.py` file contains the primary implementation for plant health prediction that should be used in the server backend:

```python
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
    """
    # Implementation details...
```

This function:
1. Loads the model if not already loaded
2. Preprocesses the input image
3. Runs inference to get a prediction
4. Interprets the prediction to determine the health label
5. Calculates a confidence score and health score
6. Returns the results as a dictionary

### predict.py (Alternative Implementation - Not Used)

The `FloraSeven_AI/src/predict.py` file contains a more complex implementation with additional features, but it has some missing functions and is not recommended for use in the server backend:

```python
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
    # Implementation details...
```

This implementation includes:
- Image quality assessment (blur detection)
- Class activation mapping (CAM) visualization
- More detailed prediction results
- Error handling

However, it references two functions that are not defined in the file:
- `calculate_laplacian_variance()`
- `is_blurry()`

### utils/predict.py (Alternative Implementation - Not Used)

The `FloraSeven_AI/utils/predict.py` file contains a `PlantHealthPredictor` class with similar functionality, but we'll use the simpler `predict_visual_health.py` implementation for the server backend:

```python
class PlantHealthPredictor:
    """Plant health prediction class for FloraSeven backend."""

    def __init__(self, model_path, class_names=None, image_size=(224, 224), use_grad_cam=True):
        # Initialization...

    def predict_visual_health(self, image_path):
        """
        Predict the visual health of a plant from an image.
        This is the main function to be used by the FloraSeven backend.
        """
        # Implementation details...
```

This class provides:
- Model loading and caching
- Image preprocessing
- Prediction with confidence scores
- Grad-CAM visualization (optional)

## Integration Approach

Based on the analysis of existing code, we will implement the AI service as follows. We'll primarily use the `predict_visual_health.py` implementation, with a fallback to our own implementation if needed:

### 1. AI Service Module (ai_service.py)

```python
import os
import sys
import logging
import tensorflow as tf
from tensorflow.keras.models import load_model
import numpy as np
import json

# Add FloraSeven_AI to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'FloraSeven_AI'))

# Try to import the predict_visual_health function
try:
    from src.predict_visual_health import predict_visual_health
except ImportError:
    # Fallback to our own implementation
    predict_visual_health = None

class AIService:
    def __init__(self, model_dir, class_indices_file):
        self.model_dir = model_dir
        self.class_indices_file = class_indices_file
        self.model = None
        self.class_indices = None
        self.logger = logging.getLogger("ai_service")

        # Load model and class indices
        self._load_model()
        self._load_class_indices()

    def _load_model(self):
        """Load the TensorFlow model."""
        try:
            self.logger.info(f"Loading model from {self.model_dir}")
            self.model = load_model(self.model_dir)
            self.logger.info("Model loaded successfully")
        except Exception as e:
            self.logger.error(f"Error loading model: {e}")
            raise

    def _load_class_indices(self):
        """Load class indices from JSON file."""
        try:
            self.logger.info(f"Loading class indices from {self.class_indices_file}")
            with open(self.class_indices_file, 'r') as f:
                self.class_indices = json.load(f)
            self.logger.info(f"Class indices loaded: {self.class_indices}")

            # Invert the dictionary to map indices to class names
            self.idx_to_class = {v: k for k, v in self.class_indices.items()}
        except Exception as e:
            self.logger.error(f"Error loading class indices: {e}")
            raise

    def analyze_image(self, image_path):
        """
        Analyze a plant image to determine its health.

        Args:
            image_path: Path to the image file

        Returns:
            dict: Dictionary containing prediction results
        """
        self.logger.info(f"Analyzing image: {image_path}")

        # Check if image exists
        if not os.path.exists(image_path):
            self.logger.error(f"Image not found: {image_path}")
            return {
                'health_label': 'error',
                'health_score': 0,
                'confidence': 0.0,
                'error': f"Image not found: {image_path}"
            }

        try:
            # If the imported predict_visual_health function is available, use it
            if predict_visual_health is not None:
                self.logger.info("Using imported predict_visual_health function")
                result = predict_visual_health(image_path=image_path)
                return result

            # Otherwise, use our own implementation
            self.logger.info("Using internal implementation for prediction")
            return self._predict_visual_health(image_path)

        except Exception as e:
            self.logger.error(f"Error analyzing image: {e}")
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
            image_path: Path to the image file

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
        prediction = self.model.predict(img_array)[0]

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

        self.logger.info(f"Prediction: {predicted_label}, Score: {health_score}, Confidence: {confidence:.4f}")

        return {
            'health_label': predicted_label,
            'health_score': health_score,
            'confidence': confidence
        }
```

### 2. Integration in server.py

```python
# Initialize AI service
ai_service = AIService(
    model_dir=os.path.join(BASE_DIR, 'FloraSeven_AI', 'models', 'model1_whole_plant_health'),
    class_indices_file=os.path.join(BASE_DIR, 'FloraSeven_AI', 'models', 'model1_whole_plant_health_class_indices.json')
)

# API endpoint for image upload and analysis
@app.route('/api/v1/upload_image', methods=['POST'])
def upload_image():
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        file = request.files['file']

        # Check if file is empty
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        filename = f"plant_image_{timestamp}.jpg"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # Save file
        file.save(filepath)

        # Analyze image
        result = ai_service.analyze_image(filepath)

        # Log results to database
        db.log_image_analysis(
            timestamp=datetime.now().isoformat(),
            filename=filename,
            health_label=result['health_label'],
            health_score=result['health_score'],
            confidence=result['confidence']
        )

        return jsonify({
            'success': True,
            'filename': filename,
            'analysis': result
        })

    except Exception as e:
        app.logger.error(f"Error processing image upload: {e}")
        return jsonify({'error': str(e)}), 500
```

## Prediction Workflow

The complete prediction workflow is as follows:

1. **Image Capture**:
   - Hub Node captures an image using its camera
   - Image is uploaded to the server via HTTP POST to `/api/v1/upload_image`

2. **Image Processing**:
   - Server receives the image and saves it to the `images/` directory
   - AI service loads the image and preprocesses it (resize to 224x224, normalize)

3. **Model Inference**:
   - AI service runs the preprocessed image through the TensorFlow model
   - Model outputs a prediction (probability of wilting)

4. **Result Interpretation**:
   - AI service interprets the prediction to determine the health label
   - Confidence score is calculated
   - Health score (0-100) is calculated based on the label and confidence

5. **Result Storage**:
   - Prediction results are stored in the database
   - Image filename is linked to the results

6. **Result Access**:
   - Flutter app requests latest status via `/api/v1/status`
   - Server includes visual health assessment in the response
   - Flutter app displays the results to the user

## Error Handling

The AI service includes robust error handling:

- **Model Loading Errors**: Logged and propagated to prevent server startup with a broken model
- **Missing Image**: Returns an error result with appropriate message
- **Prediction Errors**: Caught and logged, returns an error result
- **Import Errors**: Falls back to internal implementation if the imported function is not available

## Future Improvements

Potential improvements for future versions:

1. **Multi-class Classification**: Extend to more health conditions beyond binary healthy/wilted
2. **Confidence Thresholds**: Implement "uncertain" classification for low-confidence predictions
3. **Image Quality Assessment**: Add blur detection and other quality checks
4. **Visualization**: Implement Grad-CAM or similar techniques to highlight areas of concern
5. **Model Versioning**: Support multiple models and version tracking
6. **Online Learning**: Implement feedback mechanism to improve model over time
