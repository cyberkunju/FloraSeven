"""
Training script for FloraSeven AI plant health classification model.

This script handles the training process, including callbacks setup,
model training, fine-tuning, and evaluation.
"""

import os
import tensorflow as tf
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau, TensorBoard
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import confusion_matrix, classification_report
import seaborn as sns
import logging
import sys
import datetime
import json

# Import local modules
from data_preprocessing import main as prepare_data
from model import create_model, unfreeze_top_layers, save_model_architecture

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("training.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("training")

# Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, 'models')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')

# Create directories if they don't exist
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# Training parameters
EPOCHS_INITIAL = 20
EPOCHS_FINE_TUNING = 10
BATCH_SIZE = 32
LEARNING_RATE_INITIAL = 0.001
LEARNING_RATE_FINE_TUNING = 0.0001

def setup_callbacks(model_name):
    """
    Set up training callbacks.

    Args:
        model_name: Name of the model for saving checkpoints

    Returns:
        callbacks: List of Keras callbacks
    """
    logger.info("Setting up training callbacks")

    # Create a timestamp for unique model naming
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    model_filename = f"{model_name}_{timestamp}"

    # ModelCheckpoint: Save the best model based on validation accuracy
    checkpoint_path = os.path.join(MODELS_DIR, f"{model_filename}_best.h5")
    checkpoint = ModelCheckpoint(
        checkpoint_path,
        monitor='val_accuracy',
        verbose=1,
        save_best_only=True,
        mode='max'
    )

    # EarlyStopping: Stop training when validation loss doesn't improve
    early_stopping = EarlyStopping(
        monitor='val_loss',
        patience=5,
        verbose=1,
        restore_best_weights=True
    )

    # ReduceLROnPlateau: Reduce learning rate when metrics plateau
    reduce_lr = ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.2,
        patience=3,
        verbose=1,
        min_lr=1e-6
    )

    # TensorBoard: Visualize training progress
    log_dir = os.path.join(LOGS_DIR, f"{model_filename}")
    tensorboard = TensorBoard(
        log_dir=log_dir,
        histogram_freq=1,
        write_graph=True,
        update_freq='epoch'
    )

    return [checkpoint, early_stopping, reduce_lr, tensorboard]

def train_model(train_generator, validation_generator, class_weights, base_model_name='MobileNetV2'):
    """
    Train the model with initial frozen base and then fine-tune.

    Args:
        train_generator: Generator for training data
        validation_generator: Generator for validation data
        class_weights: Dictionary of class weights to handle class imbalance
        base_model_name: Name of the base model to use

    Returns:
        model: Trained Keras model
        history_initial: Training history for initial phase
        history_fine_tuning: Training history for fine-tuning phase
    """
    # Create model
    model = create_model(base_model_name=base_model_name, learning_rate=LEARNING_RATE_INITIAL)

    # Save model architecture visualization
    save_model_architecture(model, f"{base_model_name}_architecture.png")

    # Set up callbacks
    callbacks = setup_callbacks(base_model_name)

    # Calculate steps per epoch
    steps_per_epoch = train_generator.samples // BATCH_SIZE
    validation_steps = validation_generator.samples // BATCH_SIZE

    # Ensure at least one step
    steps_per_epoch = max(1, steps_per_epoch)
    validation_steps = max(1, validation_steps)

    logger.info(f"Starting initial training phase with frozen base model")
    logger.info(f"Training on {train_generator.samples} samples, validating on {validation_generator.samples} samples")
    logger.info(f"Using class weights: {class_weights}")

    # Initial training phase with frozen base model
    history_initial = model.fit(
        train_generator,
        steps_per_epoch=steps_per_epoch,
        epochs=EPOCHS_INITIAL,
        validation_data=validation_generator,
        validation_steps=validation_steps,
        callbacks=callbacks,
        class_weight=class_weights,  # Add class weights
        verbose=1
    )

    # Save initial model
    initial_model_path = os.path.join(MODELS_DIR, f"{base_model_name}_initial.h5")
    model.save(initial_model_path)
    logger.info(f"Initial model saved to {initial_model_path}")

    # Fine-tuning phase: unfreeze top layers and train with lower learning rate
    logger.info("Starting fine-tuning phase with unfrozen top layers")

    # Unfreeze top layers
    model = unfreeze_top_layers(model, num_layers=50)  # Increased number of unfrozen layers

    # Recompile model with lower learning rate
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=LEARNING_RATE_FINE_TUNING),
        loss='categorical_crossentropy',
        metrics=['accuracy', tf.keras.metrics.Precision(), tf.keras.metrics.Recall()]
    )

    # Update callbacks for fine-tuning phase
    callbacks = setup_callbacks(f"{base_model_name}_fine_tuned")

    # Fine-tuning
    history_fine_tuning = model.fit(
        train_generator,
        steps_per_epoch=steps_per_epoch,
        epochs=EPOCHS_FINE_TUNING,
        validation_data=validation_generator,
        validation_steps=validation_steps,
        callbacks=callbacks,
        class_weight=class_weights,  # Add class weights
        verbose=1
    )

    # Save fine-tuned model
    fine_tuned_model_path = os.path.join(MODELS_DIR, f"{base_model_name}_fine_tuned.h5")
    model.save(fine_tuned_model_path)
    logger.info(f"Fine-tuned model saved to {fine_tuned_model_path}")

    return model, history_initial, history_fine_tuning

def evaluate_model(model, test_generator):
    """
    Evaluate the trained model on the test set.

    Args:
        model: Trained Keras model
        test_generator: Generator for test data

    Returns:
        evaluation_results: Dictionary with evaluation metrics
    """
    logger.info("Evaluating model on test set")

    # Evaluate model
    test_loss, test_accuracy, test_precision, test_recall = model.evaluate(test_generator)

    logger.info(f"Test accuracy: {test_accuracy:.4f}")
    logger.info(f"Test precision: {test_precision:.4f}")
    logger.info(f"Test recall: {test_recall:.4f}")

    # Calculate F1 score
    f1_score = 2 * (test_precision * test_recall) / (test_precision + test_recall + 1e-10)
    logger.info(f"Test F1 score: {f1_score:.4f}")

    # Get predictions
    test_generator.reset()
    y_pred_prob = model.predict(test_generator)
    y_pred = np.argmax(y_pred_prob, axis=1)

    # Get true labels
    y_true = test_generator.classes[:len(y_pred)]

    # Generate confusion matrix
    cm = confusion_matrix(y_true, y_pred)

    # Get class names
    class_names = list(test_generator.class_indices.keys())

    # Plot confusion matrix
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=class_names, yticklabels=class_names)
    plt.xlabel('Predicted')
    plt.ylabel('True')
    plt.title('Confusion Matrix')
    confusion_matrix_path = os.path.join(MODELS_DIR, 'confusion_matrix.png')
    plt.savefig(confusion_matrix_path)
    logger.info(f"Confusion matrix saved to {confusion_matrix_path}")

    # Generate classification report
    report = classification_report(y_true, y_pred, target_names=class_names, output_dict=True)
    logger.info("Classification Report:")
    for class_name in class_names:
        logger.info(f"{class_name}: Precision={report[class_name]['precision']:.4f}, "
                   f"Recall={report[class_name]['recall']:.4f}, "
                   f"F1-Score={report[class_name]['f1-score']:.4f}")

    # Save classification report
    report_path = os.path.join(MODELS_DIR, 'classification_report.json')
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=4)
    logger.info(f"Classification report saved to {report_path}")

    # Create evaluation results dictionary
    evaluation_results = {
        'accuracy': float(test_accuracy),
        'precision': float(test_precision),
        'recall': float(test_recall),
        'f1_score': float(f1_score),
        'confusion_matrix': cm.tolist(),
        'classification_report': report
    }

    # Save evaluation results
    results_path = os.path.join(MODELS_DIR, 'evaluation_results.json')
    with open(results_path, 'w') as f:
        json.dump(evaluation_results, f, indent=4)
    logger.info(f"Evaluation results saved to {results_path}")

    return evaluation_results

def plot_training_history(history_initial, history_fine_tuning):
    """
    Plot training and validation metrics.

    Args:
        history_initial: Training history for initial phase
        history_fine_tuning: Training history for fine-tuning phase
    """
    # Combine histories
    combined_acc = history_initial.history['accuracy'] + history_fine_tuning.history['accuracy']
    combined_val_acc = history_initial.history['val_accuracy'] + history_fine_tuning.history['val_accuracy']
    combined_loss = history_initial.history['loss'] + history_fine_tuning.history['loss']
    combined_val_loss = history_initial.history['val_loss'] + history_fine_tuning.history['val_loss']

    # Create epoch numbers
    epochs_initial = range(1, len(history_initial.history['accuracy']) + 1)
    epochs_fine_tuning = range(len(history_initial.history['accuracy']) + 1,
                              len(history_initial.history['accuracy']) + len(history_fine_tuning.history['accuracy']) + 1)
    epochs_combined = range(1, len(combined_acc) + 1)

    # Plot accuracy
    plt.figure(figsize=(12, 5))

    plt.subplot(1, 2, 1)
    plt.plot(epochs_combined, combined_acc, 'b-', label='Training Accuracy')
    plt.plot(epochs_combined, combined_val_acc, 'r-', label='Validation Accuracy')
    plt.axvline(x=len(epochs_initial) + 0.5, color='g', linestyle='--', label='Start Fine-tuning')
    plt.title('Training and Validation Accuracy')
    plt.xlabel('Epochs')
    plt.ylabel('Accuracy')
    plt.legend()

    # Plot loss
    plt.subplot(1, 2, 2)
    plt.plot(epochs_combined, combined_loss, 'b-', label='Training Loss')
    plt.plot(epochs_combined, combined_val_loss, 'r-', label='Validation Loss')
    plt.axvline(x=len(epochs_initial) + 0.5, color='g', linestyle='--', label='Start Fine-tuning')
    plt.title('Training and Validation Loss')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend()

    plt.tight_layout()
    history_plot_path = os.path.join(MODELS_DIR, 'training_history.png')
    plt.savefig(history_plot_path)
    logger.info(f"Training history plot saved to {history_plot_path}")

def main():
    """Main function to run the training pipeline."""
    logger.info("Starting FloraSeven AI model training")

    # Prepare data
    logger.info("Preparing data...")
    train_generator, validation_generator, test_generator, class_weights = prepare_data()

    # Train model
    logger.info("Training model...")
    model, history_initial, history_fine_tuning = train_model(
        train_generator,
        validation_generator,
        class_weights,
        base_model_name='MobileNetV2'
    )

    # Plot training history
    logger.info("Plotting training history...")
    plot_training_history(history_initial, history_fine_tuning)

    # Evaluate model
    logger.info("Evaluating model...")
    evaluation_results = evaluate_model(model, test_generator)

    logger.info("Training pipeline completed successfully")

    return model, evaluation_results

if __name__ == "__main__":
    main()
