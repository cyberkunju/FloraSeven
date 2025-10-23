"""
Model architecture for FloraSeven AI plant health classification.

This script defines the model architecture using transfer learning
with MobileNetV2 or EfficientNetLite as the base model.
"""

import os
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2, EfficientNetB0
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout, Input
from tensorflow.keras.optimizers import Adam
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("model.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("model")

# Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, 'models')

# Create models directory if it doesn't exist
os.makedirs(MODELS_DIR, exist_ok=True)

# Image parameters
IMG_SIZE = 224  # Standard input size for MobileNetV2/EfficientNetB0
NUM_CLASSES = 3  # healthy, wilting, discolored

def create_model(base_model_name='MobileNetV2', learning_rate=0.001):
    """
    Create a transfer learning model for plant health classification.

    Args:
        base_model_name: Name of the base model to use ('MobileNetV2' or 'EfficientNetB0')
        learning_rate: Initial learning rate for the Adam optimizer

    Returns:
        model: Compiled Keras model
    """
    logger.info(f"Creating model with {base_model_name} as base")

    # Define input shape
    input_shape = (IMG_SIZE, IMG_SIZE, 3)

    # Create input layer
    inputs = Input(shape=input_shape)

    # Load pre-trained base model without top layers
    if base_model_name == 'MobileNetV2':
        base_model = MobileNetV2(
            input_shape=input_shape,
            include_top=False,
            weights='imagenet'
        )
    elif base_model_name == 'EfficientNetB0':
        base_model = EfficientNetB0(
            input_shape=input_shape,
            include_top=False,
            weights='imagenet'
        )
    else:
        raise ValueError(f"Unsupported base model: {base_model_name}")

    # Freeze the base model layers
    base_model.trainable = False

    # Add custom top layers with improved architecture
    x = base_model(inputs, training=False)
    x = GlobalAveragePooling2D()(x)

    # Add batch normalization for better training stability
    x = tf.keras.layers.BatchNormalization()(x)

    # First dense layer with more units
    x = Dense(512, activation='relu')(x)
    x = tf.keras.layers.BatchNormalization()(x)
    x = Dropout(0.4)(x)

    # Second dense layer
    x = Dense(256, activation='relu')(x)
    x = tf.keras.layers.BatchNormalization()(x)
    x = Dropout(0.3)(x)

    # Third dense layer
    x = Dense(128, activation='relu')(x)
    x = tf.keras.layers.BatchNormalization()(x)
    x = Dropout(0.2)(x)

    # Output layer with softmax activation
    outputs = Dense(NUM_CLASSES, activation='softmax')(x)

    # Create the model
    model = Model(inputs=inputs, outputs=outputs)

    # Compile the model
    model.compile(
        optimizer=Adam(learning_rate=learning_rate),
        loss='categorical_crossentropy',
        metrics=['accuracy', tf.keras.metrics.Precision(), tf.keras.metrics.Recall()]
    )

    logger.info(f"Model created with {base_model_name} base")
    logger.info(f"Total parameters: {model.count_params():,}")
    logger.info(f"Trainable parameters: {sum(w.numpy().size for w in model.trainable_weights):,}")

    return model

def unfreeze_top_layers(model, num_layers=30):
    """
    Unfreeze the top layers of the base model for fine-tuning.

    Args:
        model: The Keras model
        num_layers: Number of top layers to unfreeze

    Returns:
        model: Updated model with unfrozen top layers
    """
    # Find the base model within the larger model
    if hasattr(model.layers[1], 'layers'):
        base_model = model.layers[1]

        # Unfreeze the top layers
        base_model.trainable = True

        # Freeze all layers except the top num_layers
        for layer in base_model.layers[:-num_layers]:
            layer.trainable = False

        logger.info(f"Unfroze top {num_layers} layers of base model for fine-tuning")
        logger.info(f"Trainable parameters after unfreezing: {sum(w.numpy().size for w in model.trainable_weights):,}")
    else:
        logger.warning("Could not identify base model for unfreezing")

    return model

def save_model_architecture(model, filename='model_architecture.png'):
    """
    Save a visualization of the model architecture.

    Args:
        model: The Keras model
        filename: Name of the output file
    """
    try:
        tf.keras.utils.plot_model(
            model,
            to_file=os.path.join(MODELS_DIR, filename),
            show_shapes=True,
            show_layer_names=True
        )
        logger.info(f"Model architecture saved to {os.path.join(MODELS_DIR, filename)}")
    except Exception as e:
        logger.error(f"Failed to save model architecture: {e}")

def main():
    """Main function to create and visualize the model."""
    # Create model
    model = create_model()

    # Print model summary
    model.summary()

    # Save model architecture visualization
    save_model_architecture(model)

    return model

if __name__ == "__main__":
    main()
