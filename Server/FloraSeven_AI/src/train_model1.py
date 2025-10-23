"""
Script to train Model 1 (Whole Plant Health) for the FloraSeven AI system.

This model will classify plants as either healthy or wilting based on the overall plant structure.
It uses transfer learning with MobileNetV2 as the base model.
"""

import os
import time
import json
import logging
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau, TensorBoard

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("train_model1")

# Define constants
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, 'data', 'processed')
TRAIN_DIR = os.path.join(PROCESSED_DIR, 'train')
VALIDATION_DIR = os.path.join(PROCESSED_DIR, 'validation')
TEST_DIR = os.path.join(PROCESSED_DIR, 'test')
MODELS_DIR = os.path.join(BASE_DIR, 'models')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')

# Create directories if they don't exist
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# Model parameters
IMG_SIZE = 224
BATCH_SIZE = 32
EPOCHS = 50
LEARNING_RATE = 1e-4
MODEL_NAME = 'model1_whole_plant_health'

def check_gpu():
    """Check if GPU is available and configure TensorFlow accordingly."""
    gpus = tf.config.list_physical_devices('GPU')
    if gpus:
        try:
            # Currently, memory growth needs to be the same across GPUs
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
            logical_gpus = tf.config.list_logical_devices('GPU')
            logger.info(f"Physical GPUs: {len(gpus)}, Logical GPUs: {len(logical_gpus)}")
            return True
        except RuntimeError as e:
            # Memory growth must be set before GPUs have been initialized
            logger.warning(f"GPU configuration error: {e}")
            return False
    else:
        logger.warning("No GPU found. Training will proceed on CPU (this will be slow).")
        return False

def create_data_generators():
    """Create data generators for training, validation, and testing."""
    # Data augmentation for training
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest'
    )
    
    # Only rescaling for validation and test
    valid_datagen = ImageDataGenerator(rescale=1./255)
    test_datagen = ImageDataGenerator(rescale=1./255)
    
    # Create generators
    train_generator = train_datagen.flow_from_directory(
        TRAIN_DIR,
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        class_mode='binary',
        shuffle=True
    )
    
    validation_generator = valid_datagen.flow_from_directory(
        VALIDATION_DIR,
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        class_mode='binary',
        shuffle=False
    )
    
    test_generator = test_datagen.flow_from_directory(
        TEST_DIR,
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        class_mode='binary',
        shuffle=False
    )
    
    return train_generator, validation_generator, test_generator

def create_model():
    """Create the Model 1 architecture using transfer learning with MobileNetV2."""
    # Load the pre-trained MobileNetV2 model without the top classification layer
    base_model = MobileNetV2(
        weights='imagenet',
        include_top=False,
        input_shape=(IMG_SIZE, IMG_SIZE, 3)
    )
    
    # Freeze the base model layers
    base_model.trainable = False
    
    # Add custom classification head
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(128, activation='relu')(x)
    x = Dropout(0.5)(x)
    predictions = Dense(1, activation='sigmoid')(x)  # Binary classification: healthy vs wilting
    
    # Create the final model
    model = Model(inputs=base_model.input, outputs=predictions)
    
    # Compile the model
    model.compile(
        optimizer=Adam(learning_rate=LEARNING_RATE),
        loss='binary_crossentropy',
        metrics=['accuracy', tf.keras.metrics.Precision(), tf.keras.metrics.Recall()]
    )
    
    return model, base_model

def create_callbacks():
    """Create callbacks for training."""
    # Model checkpoint to save the best model
    checkpoint_path = os.path.join(MODELS_DIR, f"{MODEL_NAME}_best.h5")
    checkpoint = ModelCheckpoint(
        checkpoint_path,
        monitor='val_accuracy',
        verbose=1,
        save_best_only=True,
        mode='max'
    )
    
    # Early stopping to prevent overfitting
    early_stopping = EarlyStopping(
        monitor='val_loss',
        patience=10,
        verbose=1,
        restore_best_weights=True
    )
    
    # Reduce learning rate when a metric has stopped improving
    reduce_lr = ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.2,
        patience=5,
        min_lr=1e-6,
        verbose=1
    )
    
    # TensorBoard for visualization
    log_dir = os.path.join(LOGS_DIR, f"{MODEL_NAME}_{int(time.time())}")
    tensorboard = TensorBoard(
        log_dir=log_dir,
        histogram_freq=1,
        write_graph=True
    )
    
    return [checkpoint, early_stopping, reduce_lr, tensorboard]

def train_model(model, train_generator, validation_generator, callbacks):
    """Train the model."""
    # Calculate steps per epoch
    steps_per_epoch = train_generator.samples // train_generator.batch_size
    validation_steps = validation_generator.samples // validation_generator.batch_size
    
    # Ensure at least one step
    steps_per_epoch = max(1, steps_per_epoch)
    validation_steps = max(1, validation_steps)
    
    # Train the model
    history = model.fit(
        train_generator,
        steps_per_epoch=steps_per_epoch,
        epochs=EPOCHS,
        validation_data=validation_generator,
        validation_steps=validation_steps,
        callbacks=callbacks,
        verbose=1
    )
    
    return history

def evaluate_model(model, test_generator):
    """Evaluate the model on the test set."""
    # Calculate steps
    steps = test_generator.samples // test_generator.batch_size
    steps = max(1, steps)
    
    # Evaluate the model
    results = model.evaluate(test_generator, steps=steps, verbose=1)
    
    # Log results
    metrics = ['loss', 'accuracy', 'precision', 'recall']
    for metric, value in zip(metrics, results):
        logger.info(f"Test {metric}: {value:.4f}")
    
    return dict(zip(metrics, results))

def fine_tune_model(model, base_model, train_generator, validation_generator, callbacks):
    """Fine-tune the model by unfreezing some layers of the base model."""
    # Unfreeze the top layers of the base model
    base_model.trainable = True
    
    # Freeze all the layers except the last 4 blocks (out of 16 blocks in MobileNetV2)
    for layer in base_model.layers[:-54]:  # MobileNetV2 has 154 layers, so this unfreezes ~1/3
        layer.trainable = False
    
    # Recompile the model with a lower learning rate
    model.compile(
        optimizer=Adam(learning_rate=LEARNING_RATE / 10),
        loss='binary_crossentropy',
        metrics=['accuracy', tf.keras.metrics.Precision(), tf.keras.metrics.Recall()]
    )
    
    # Calculate steps per epoch
    steps_per_epoch = train_generator.samples // train_generator.batch_size
    validation_steps = validation_generator.samples // validation_generator.batch_size
    
    # Ensure at least one step
    steps_per_epoch = max(1, steps_per_epoch)
    validation_steps = max(1, validation_steps)
    
    # Fine-tune the model
    history = model.fit(
        train_generator,
        steps_per_epoch=steps_per_epoch,
        epochs=EPOCHS // 2,  # Fewer epochs for fine-tuning
        validation_data=validation_generator,
        validation_steps=validation_steps,
        callbacks=callbacks,
        verbose=1
    )
    
    return history

def save_model_for_inference(model):
    """Save the model in TensorFlow SavedModel format for inference."""
    # Save the model
    model_path = os.path.join(MODELS_DIR, MODEL_NAME)
    model.save(model_path)
    logger.info(f"Model saved to {model_path}")
    
    # Save a TFLite version for potential edge deployment
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    tflite_model = converter.convert()
    
    tflite_path = os.path.join(MODELS_DIR, f"{MODEL_NAME}.tflite")
    with open(tflite_path, 'wb') as f:
        f.write(tflite_model)
    logger.info(f"TFLite model saved to {tflite_path}")
    
    # Save class indices
    class_indices_path = os.path.join(MODELS_DIR, f"{MODEL_NAME}_class_indices.json")
    with open(class_indices_path, 'w') as f:
        json.dump({'healthy': 0, 'wilting': 1}, f)
    logger.info(f"Class indices saved to {class_indices_path}")

def main():
    """Main function to train Model 1."""
    logger.info("Starting training for Model 1 (Whole Plant Health)")
    
    # Check GPU availability
    has_gpu = check_gpu()
    logger.info(f"Training with GPU: {has_gpu}")
    
    # Create data generators
    train_generator, validation_generator, test_generator = create_data_generators()
    logger.info(f"Training samples: {train_generator.samples}")
    logger.info(f"Validation samples: {validation_generator.samples}")
    logger.info(f"Test samples: {test_generator.samples}")
    
    # Create model
    model, base_model = create_model()
    model.summary(print_fn=logger.info)
    
    # Create callbacks
    callbacks = create_callbacks()
    
    # Train the model
    logger.info("Starting initial training phase...")
    history = train_model(model, train_generator, validation_generator, callbacks)
    
    # Evaluate the model
    logger.info("Evaluating model after initial training...")
    initial_results = evaluate_model(model, test_generator)
    
    # Fine-tune the model
    logger.info("Starting fine-tuning phase...")
    fine_tune_history = fine_tune_model(model, base_model, train_generator, validation_generator, callbacks)
    
    # Evaluate the fine-tuned model
    logger.info("Evaluating model after fine-tuning...")
    final_results = evaluate_model(model, test_generator)
    
    # Save the model for inference
    save_model_for_inference(model)
    
    logger.info("Model 1 training completed successfully!")
    logger.info(f"Initial test accuracy: {initial_results['accuracy']:.4f}")
    logger.info(f"Final test accuracy: {final_results['accuracy']:.4f}")

if __name__ == "__main__":
    main()
