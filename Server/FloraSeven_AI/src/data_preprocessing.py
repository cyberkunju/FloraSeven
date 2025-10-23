"""
Data preprocessing for FloraSeven AI model.

This script handles preprocessing of the plant images for the FloraSeven
plant health classification model, including resizing, normalization,
and data splitting.
"""

import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import logging
import sys
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("preprocessing.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("data_preprocessing")

# Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DATA_DIR = os.path.join(BASE_DIR, 'data', 'processed')
TRAIN_DIR = os.path.join(PROCESSED_DATA_DIR, 'train')
VALIDATION_DIR = os.path.join(PROCESSED_DATA_DIR, 'validation')
TEST_DIR = os.path.join(PROCESSED_DATA_DIR, 'test')

# Create directories if they don't exist
for directory in [TRAIN_DIR, VALIDATION_DIR, TEST_DIR]:
    os.makedirs(directory, exist_ok=True)
    for category in ['healthy', 'wilting', 'discolored']:
        os.makedirs(os.path.join(directory, category), exist_ok=True)

# Image parameters
IMG_SIZE = 224  # MobileNetV2 input size
BATCH_SIZE = 32

def split_dataset(test_size=0.15, validation_size=0.15, random_state=42):
    """
    Split the dataset into train, validation, and test sets.

    Args:
        test_size: Proportion of the dataset to include in the test split
        validation_size: Proportion of the dataset to include in the validation split
        random_state: Random seed for reproducibility
    """
    logger.info("Splitting dataset into train, validation, and test sets")

    # Process each category
    for category in ['healthy', 'wilting', 'discolored']:
        category_dir = os.path.join(PROCESSED_DATA_DIR, category)

        if not os.path.exists(category_dir):
            logger.warning(f"Category directory not found: {category_dir}")
            continue

        # Get all image files
        image_files = [f for f in os.listdir(category_dir)
                      if os.path.isfile(os.path.join(category_dir, f)) and
                      f.lower().endswith(('.png', '.jpg', '.jpeg'))]

        if not image_files:
            logger.warning(f"No images found in {category_dir}")
            continue

        logger.info(f"Found {len(image_files)} images in category '{category}'")

        # First split: separate test set
        train_val_files, test_files = train_test_split(
            image_files,
            test_size=test_size,
            random_state=random_state
        )

        # Second split: separate validation set from remaining training set
        # Adjust validation_size to get the right proportion from the remaining data
        adjusted_val_size = validation_size / (1 - test_size)
        train_files, val_files = train_test_split(
            train_val_files,
            test_size=adjusted_val_size,
            random_state=random_state
        )

        logger.info(f"Category '{category}': {len(train_files)} train, {len(val_files)} validation, {len(test_files)} test")

        # Copy files to respective directories
        for file_list, target_subdir in [(train_files, TRAIN_DIR),
                                        (val_files, VALIDATION_DIR),
                                        (test_files, TEST_DIR)]:
            target_dir = os.path.join(target_subdir, category)

            for filename in tqdm(file_list, desc=f"Copying {category} to {os.path.basename(target_subdir)}"):
                source_file = os.path.join(category_dir, filename)
                target_file = os.path.join(target_dir, filename)

                # Use tf.io.read_file and tf.io.write_file for better performance
                img_content = tf.io.read_file(source_file)
                tf.io.write_file(target_file, img_content)

def create_data_generators():
    """
    Create data generators for training, validation, and testing.

    Returns:
        train_generator: Generator for training data
        validation_generator: Generator for validation data
        test_generator: Generator for test data
        class_weights: Dictionary of class weights to handle class imbalance
    """
    logger.info("Creating data generators with augmentation for training")

    # Training data generator with enhanced augmentation
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=30,  # Increased rotation range
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.3,  # Increased zoom range
        horizontal_flip=True,
        vertical_flip=True,  # Added vertical flip
        brightness_range=[0.8, 1.2],  # Added brightness variation
        fill_mode='nearest'
    )

    # Validation and test data generators (no augmentation, just rescaling)
    valid_test_datagen = ImageDataGenerator(rescale=1./255)

    # Create generators
    train_generator = train_datagen.flow_from_directory(
        TRAIN_DIR,
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        shuffle=True
    )

    validation_generator = valid_test_datagen.flow_from_directory(
        VALIDATION_DIR,
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        shuffle=False
    )

    test_generator = valid_test_datagen.flow_from_directory(
        TEST_DIR,
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        shuffle=False
    )

    logger.info(f"Class indices: {train_generator.class_indices}")

    # Calculate class weights to handle class imbalance
    # Count samples in each class
    class_counts = {}
    for category in ['healthy', 'wilting', 'discolored']:
        class_dir = os.path.join(TRAIN_DIR, category)
        if os.path.exists(class_dir):
            class_counts[category] = len([f for f in os.listdir(class_dir)
                                        if os.path.isfile(os.path.join(class_dir, f)) and
                                        f.lower().endswith(('.png', '.jpg', '.jpeg'))])
        else:
            class_counts[category] = 0

    logger.info(f"Class counts: {class_counts}")

    # Calculate class weights (inversely proportional to class frequency)
    total_samples = sum(class_counts.values())
    class_weights = {}
    for i, (category, count) in enumerate(class_counts.items()):
        if count > 0:
            # Use sklearn formula: n_samples / (n_classes * np.bincount(y))
            class_weights[i] = total_samples / (len(class_counts) * count)
        else:
            class_weights[i] = 1.0

    logger.info(f"Class weights: {class_weights}")

    return train_generator, validation_generator, test_generator, class_weights

def visualize_augmentation(train_generator, num_samples=5):
    """
    Visualize augmented training samples.

    Args:
        train_generator: Training data generator
        num_samples: Number of samples to visualize
    """
    logger.info("Visualizing augmented samples")

    # Get a batch of training data
    images, labels = next(train_generator)

    # Create a figure to display the images
    plt.figure(figsize=(15, 5))

    for i in range(min(num_samples, len(images))):
        plt.subplot(1, num_samples, i+1)
        plt.imshow(images[i])

        # Get the class name from the label
        class_idx = np.argmax(labels[i])
        class_name = list(train_generator.class_indices.keys())[class_idx]

        plt.title(class_name)
        plt.axis('off')

    plt.tight_layout()
    plt.savefig(os.path.join(BASE_DIR, 'augmentation_samples.png'))
    logger.info(f"Saved augmentation visualization to {os.path.join(BASE_DIR, 'augmentation_samples.png')}")

def main():
    """Main function to run the preprocessing pipeline."""
    logger.info("Starting data preprocessing")

    # Split the dataset
    split_dataset()

    # Create data generators and calculate class weights
    train_generator, validation_generator, test_generator, class_weights = create_data_generators()

    # Visualize augmentation
    visualize_augmentation(train_generator)

    logger.info("Data preprocessing complete")

    # Return generators and class weights for use in training
    return train_generator, validation_generator, test_generator, class_weights

if __name__ == "__main__":
    main()
