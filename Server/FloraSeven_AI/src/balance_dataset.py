"""
Script to create a balanced dataset from the raw data.

This script will:
1. Create a balanced dataset with equal numbers of healthy, wilting, and discolored plants
2. Split the dataset into train, validation, and test sets
3. Save the balanced dataset to the processed directory
"""

import os
import shutil
import random
import logging
from tqdm import tqdm
import numpy as np
from sklearn.model_selection import train_test_split
import tensorflow as tf

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("balance_dataset")

# Define constants
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOWNLOADED_DIR = os.path.join(BASE_DIR, 'data', 'Downloaded')
PROCESSED_DIR = os.path.join(BASE_DIR, 'data', 'processed')
TRAIN_DIR = os.path.join(PROCESSED_DIR, 'train')
VALIDATION_DIR = os.path.join(PROCESSED_DIR, 'validation')
TEST_DIR = os.path.join(PROCESSED_DIR, 'test')

# Target number of images per class
# We'll aim for 2000 images per class to have a balanced dataset
TARGET_IMAGES_PER_CLASS = 2000

def create_directories():
    """Create necessary directories if they don't exist."""
    for directory in [PROCESSED_DIR, TRAIN_DIR, VALIDATION_DIR, TEST_DIR]:
        os.makedirs(directory, exist_ok=True)
        
    # Create class directories in each split
    for split_dir in [TRAIN_DIR, VALIDATION_DIR, TEST_DIR]:
        for class_name in ['healthy', 'wilting', 'discolored']:
            os.makedirs(os.path.join(split_dir, class_name), exist_ok=True)

def collect_healthy_images():
    """
    Collect healthy plant images from various sources.
    
    Returns:
        list: Paths to healthy plant images
    """
    healthy_images = []
    
    # 1. Houseplant healthy images
    houseplant_healthy_dir = os.path.join(DOWNLOADED_DIR, 'Healthy and Wilted Houseplant Images', 
                                         'houseplant_images', 'healthy')
    if os.path.exists(houseplant_healthy_dir):
        for filename in os.listdir(houseplant_healthy_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                healthy_images.append(os.path.join(houseplant_healthy_dir, filename))
    
    # 2. Plant Village healthy images (sample from different plants)
    plant_village_dir = os.path.join(DOWNLOADED_DIR, 'Plant Village Dataset (Updated)')
    plant_types = ['Tomato', 'Apple', 'Potato', 'Corn (Maize)', 'Grape']
    
    for plant_type in plant_types:
        healthy_dir = os.path.join(plant_village_dir, plant_type, 'Train', 'Healthy')
        if os.path.exists(healthy_dir):
            # Calculate how many images to take from each plant type
            remaining = TARGET_IMAGES_PER_CLASS - len(healthy_images)
            if remaining <= 0:
                break
                
            # Get all healthy images for this plant type
            plant_healthy_images = [os.path.join(healthy_dir, f) for f in os.listdir(healthy_dir)
                                   if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            
            # Take a random sample (or all if there are fewer than needed)
            sample_size = min(len(plant_healthy_images), remaining)
            healthy_images.extend(random.sample(plant_healthy_images, sample_size))
    
    logger.info(f"Collected {len(healthy_images)} healthy plant images")
    return healthy_images

def collect_wilting_images():
    """
    Collect wilting plant images from various sources.
    
    Returns:
        list: Paths to wilting plant images
    """
    wilting_images = []
    
    # 1. Houseplant wilted images
    houseplant_wilted_dir = os.path.join(DOWNLOADED_DIR, 'Healthy and Wilted Houseplant Images', 
                                        'houseplant_images', 'wilted')
    if os.path.exists(houseplant_wilted_dir):
        for filename in os.listdir(houseplant_wilted_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                wilting_images.append(os.path.join(houseplant_wilted_dir, filename))
    
    # If we need more wilting images, we can augment the existing ones
    if len(wilting_images) < TARGET_IMAGES_PER_CLASS:
        logger.info(f"Only found {len(wilting_images)} wilting images, will augment to reach target")
        
        # Create augmentation pipeline
        datagen = tf.keras.preprocessing.image.ImageDataGenerator(
            rotation_range=40,
            width_shift_range=0.2,
            height_shift_range=0.2,
            shear_range=0.2,
            zoom_range=0.2,
            horizontal_flip=True,
            fill_mode='nearest'
        )
        
        # Create a temporary directory for augmented images
        temp_dir = os.path.join(PROCESSED_DIR, 'temp_augmented_wilting')
        os.makedirs(temp_dir, exist_ok=True)
        
        # Augment images until we reach the target
        original_count = len(wilting_images)
        augmentation_factor = min(5, TARGET_IMAGES_PER_CLASS // original_count + 1)
        
        for i, image_path in enumerate(tqdm(wilting_images, desc="Augmenting wilting images")):
            try:
                # Load image
                img = tf.keras.preprocessing.image.load_img(image_path)
                x = tf.keras.preprocessing.image.img_to_array(img)
                x = x.reshape((1,) + x.shape)
                
                # Generate augmented images
                aug_iter = datagen.flow(x, batch_size=1, save_to_dir=temp_dir,
                                      save_prefix=f'aug_{i}', save_format='jpg')
                
                # Generate 'augmentation_factor' augmented images for each original
                for _ in range(augmentation_factor):
                    next(aug_iter)
            except Exception as e:
                logger.warning(f"Error augmenting image {image_path}: {e}")
        
        # Add augmented images to the list
        for filename in os.listdir(temp_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                wilting_images.append(os.path.join(temp_dir, filename))
        
        logger.info(f"After augmentation: {len(wilting_images)} wilting plant images")
    
    # If we have more than needed, randomly sample
    if len(wilting_images) > TARGET_IMAGES_PER_CLASS:
        wilting_images = random.sample(wilting_images, TARGET_IMAGES_PER_CLASS)
    
    logger.info(f"Collected {len(wilting_images)} wilting plant images")
    return wilting_images

def collect_discolored_images():
    """
    Collect discolored plant images from various sources.
    
    Returns:
        list: Paths to discolored plant images
    """
    discolored_images = []
    
    # Plant Village diseased images (sample from different plants and diseases)
    plant_village_dir = os.path.join(DOWNLOADED_DIR, 'Plant Village Dataset (Updated)')
    plant_types = ['Tomato', 'Apple', 'Potato', 'Corn (Maize)', 'Grape']
    
    for plant_type in plant_types:
        plant_dir = os.path.join(plant_village_dir, plant_type, 'Train')
        if os.path.exists(plant_dir):
            # Get all disease folders (excluding 'Healthy')
            disease_folders = [d for d in os.listdir(plant_dir) 
                              if os.path.isdir(os.path.join(plant_dir, d)) and d != 'Healthy']
            
            # Calculate how many images to take from each disease
            remaining = TARGET_IMAGES_PER_CLASS - len(discolored_images)
            if remaining <= 0:
                break
                
            # Distribute remaining images evenly among diseases
            images_per_disease = remaining // (len(disease_folders) * len(plant_types)) + 1
            
            # Collect images from each disease
            for disease in disease_folders:
                disease_dir = os.path.join(plant_dir, disease)
                disease_images = [os.path.join(disease_dir, f) for f in os.listdir(disease_dir)
                                 if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
                
                # Take a random sample
                sample_size = min(len(disease_images), images_per_disease)
                discolored_images.extend(random.sample(disease_images, sample_size))
                
                # Check if we've reached the target
                if len(discolored_images) >= TARGET_IMAGES_PER_CLASS:
                    break
    
    # If we have more than needed, randomly sample
    if len(discolored_images) > TARGET_IMAGES_PER_CLASS:
        discolored_images = random.sample(discolored_images, TARGET_IMAGES_PER_CLASS)
    
    logger.info(f"Collected {len(discolored_images)} discolored plant images")
    return discolored_images

def split_and_copy_images(image_paths, class_name, test_size=0.15, validation_size=0.15):
    """
    Split images into train, validation, and test sets and copy to appropriate directories.
    
    Args:
        image_paths: List of image paths
        class_name: Class name (healthy, wilting, discolored)
        test_size: Proportion of images to use for testing
        validation_size: Proportion of images to use for validation
    """
    # First split: separate test set
    train_val_paths, test_paths = train_test_split(
        image_paths, test_size=test_size, random_state=42
    )
    
    # Second split: separate validation set from remaining training set
    # Adjust validation_size to get the right proportion from the remaining data
    adjusted_val_size = validation_size / (1 - test_size)
    train_paths, val_paths = train_test_split(
        train_val_paths, test_size=adjusted_val_size, random_state=42
    )
    
    logger.info(f"Class '{class_name}': {len(train_paths)} train, {len(val_paths)} validation, {len(test_paths)} test")
    
    # Copy files to respective directories
    for paths, target_dir in [(train_paths, TRAIN_DIR), 
                             (val_paths, VALIDATION_DIR), 
                             (test_paths, TEST_DIR)]:
        target_class_dir = os.path.join(target_dir, class_name)
        
        for src_path in tqdm(paths, desc=f"Copying {class_name} to {os.path.basename(target_dir)}"):
            # Generate a unique filename to avoid conflicts
            filename = os.path.basename(src_path)
            base, ext = os.path.splitext(filename)
            unique_filename = f"{base}_{random.randint(1000, 9999)}{ext}"
            dst_path = os.path.join(target_class_dir, unique_filename)
            
            # Copy the file
            try:
                shutil.copy2(src_path, dst_path)
            except Exception as e:
                logger.warning(f"Error copying {src_path} to {dst_path}: {e}")

def clean_processed_directory():
    """Clean the processed directory before creating a new balanced dataset."""
    # Remove class directories in each split
    for split_dir in [TRAIN_DIR, VALIDATION_DIR, TEST_DIR]:
        for class_name in ['healthy', 'wilting', 'discolored']:
            class_dir = os.path.join(split_dir, class_name)
            if os.path.exists(class_dir):
                logger.info(f"Cleaning {class_dir}")
                for filename in os.listdir(class_dir):
                    file_path = os.path.join(class_dir, filename)
                    if os.path.isfile(file_path):
                        os.remove(file_path)

def main():
    """Main function to create a balanced dataset."""
    logger.info("Starting balanced dataset creation")
    
    # Create necessary directories
    create_directories()
    
    # Clean processed directory
    clean_processed_directory()
    
    # Collect images for each class
    healthy_images = collect_healthy_images()
    wilting_images = collect_wilting_images()
    discolored_images = collect_discolored_images()
    
    # Split and copy images
    split_and_copy_images(healthy_images, 'healthy')
    split_and_copy_images(wilting_images, 'wilting')
    split_and_copy_images(discolored_images, 'discolored')
    
    # Clean up temporary directory if it exists
    temp_dir = os.path.join(PROCESSED_DIR, 'temp_augmented_wilting')
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    
    logger.info("Balanced dataset creation completed")
    
    # Print final counts
    for split_dir, split_name in [(TRAIN_DIR, 'Train'), 
                                 (VALIDATION_DIR, 'Validation'), 
                                 (TEST_DIR, 'Test')]:
        logger.info(f"\n{split_name} set:")
        for class_name in ['healthy', 'wilting', 'discolored']:
            class_dir = os.path.join(split_dir, class_name)
            count = len([f for f in os.listdir(class_dir) 
                        if os.path.isfile(os.path.join(class_dir, f))])
            logger.info(f"  {class_name}: {count} images")

if __name__ == "__main__":
    main()
