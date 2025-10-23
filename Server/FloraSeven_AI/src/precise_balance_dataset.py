"""
Script to create a precisely balanced dataset from the raw data according to exact specifications.

This script will:
1. Create a balanced dataset with exactly:
   - 425 healthy images (325 from Houseplant + 100 from Plant Village)
   - 452 wilting images (all from Houseplant)
   - 452 discolored images (from Plant Village Early Blight)
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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("precise_balance_dataset")

# Define constants
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOWNLOADED_DIR = os.path.join(BASE_DIR, 'data', 'Downloaded')
PROCESSED_DIR = os.path.join(BASE_DIR, 'data', 'processed')
TRAIN_DIR = os.path.join(PROCESSED_DIR, 'train')
VALIDATION_DIR = os.path.join(PROCESSED_DIR, 'validation')
TEST_DIR = os.path.join(PROCESSED_DIR, 'test')

# Define train/validation/test split ratios
TRAIN_RATIO = 0.7
VALIDATION_RATIO = 0.15
TEST_RATIO = 0.15

def create_directories():
    """Create necessary directories if they don't exist."""
    for directory in [PROCESSED_DIR, TRAIN_DIR, VALIDATION_DIR, TEST_DIR]:
        os.makedirs(directory, exist_ok=True)
        
    # Create class directories in each split
    for split_dir in [TRAIN_DIR, VALIDATION_DIR, TEST_DIR]:
        for class_name in ['healthy', 'wilting', 'discolored']:
            os.makedirs(os.path.join(split_dir, class_name), exist_ok=True)

def collect_precise_images():
    """
    Collect images from various sources according to exact specifications.
    
    Returns:
        dict: Dictionary with keys 'healthy', 'wilting', 'discolored' and values as lists of image paths
    """
    images = {
        'healthy': [],
        'wilting': [],
        'discolored': []
    }
    
    # 1. Houseplant healthy images - exactly 325
    houseplant_healthy_dir = os.path.join(DOWNLOADED_DIR, 'Healthy and Wilted Houseplant Images', 
                                         'houseplant_images', 'healthy')
    if os.path.exists(houseplant_healthy_dir):
        houseplant_healthy_images = [os.path.join(houseplant_healthy_dir, f) for f in os.listdir(houseplant_healthy_dir)
                                    if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        # Take exactly 325 images
        images['healthy'].extend(random.sample(houseplant_healthy_images, 325))
    
    # 2. Plant Village healthy images - exactly 100
    tomato_healthy_dir = os.path.join(DOWNLOADED_DIR, 'Plant Village Dataset (Updated)', 
                                     'Tomato', 'Train', 'Healthy')
    if os.path.exists(tomato_healthy_dir):
        tomato_healthy_images = [os.path.join(tomato_healthy_dir, f) for f in os.listdir(tomato_healthy_dir)
                                if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        # Take exactly 100 images
        images['healthy'].extend(random.sample(tomato_healthy_images, 100))
    
    # 3. Houseplant wilted images - all 452
    houseplant_wilted_dir = os.path.join(DOWNLOADED_DIR, 'Healthy and Wilted Houseplant Images', 
                                        'houseplant_images', 'wilted')
    if os.path.exists(houseplant_wilted_dir):
        for filename in os.listdir(houseplant_wilted_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                images['wilting'].append(os.path.join(houseplant_wilted_dir, filename))
    
    # 4. Plant Village diseased images - exactly 452
    tomato_early_blight_dir = os.path.join(DOWNLOADED_DIR, 'Plant Village Dataset (Updated)', 
                                          'Tomato', 'Train', 'Early Blight')
    if os.path.exists(tomato_early_blight_dir):
        tomato_early_blight_images = [os.path.join(tomato_early_blight_dir, f) for f in os.listdir(tomato_early_blight_dir)
                                     if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        # Take exactly 452 images
        images['discolored'].extend(random.sample(tomato_early_blight_images, 452))
    
    # Log the counts
    for category, paths in images.items():
        logger.info(f"Collected {len(paths)} {category} images")
    
    return images

def split_and_copy_images(images):
    """
    Split images into train, validation, and test sets and copy to appropriate directories.
    
    Args:
        images: Dictionary with image lists
    """
    for category, paths in images.items():
        # First split: separate train set
        train_paths, temp_paths = train_test_split(
            paths, train_size=TRAIN_RATIO, random_state=42
        )
        
        # Second split: separate validation and test sets
        val_paths, test_paths = train_test_split(
            temp_paths, train_size=VALIDATION_RATIO/(VALIDATION_RATIO + TEST_RATIO), random_state=42
        )
        
        logger.info(f"Class '{category}': {len(train_paths)} train, {len(val_paths)} validation, {len(test_paths)} test")
        
        # Copy files to respective directories
        for paths_list, target_dir in [(train_paths, TRAIN_DIR), 
                                     (val_paths, VALIDATION_DIR), 
                                     (test_paths, TEST_DIR)]:
            target_class_dir = os.path.join(target_dir, category)
            
            for src_path in tqdm(paths_list, desc=f"Copying {category} to {os.path.basename(target_dir)}"):
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
    """Main function to create a precisely balanced dataset."""
    logger.info("Starting precise balanced dataset creation")
    
    # Create necessary directories
    create_directories()
    
    # Clean processed directory
    clean_processed_directory()
    
    # Collect images according to exact specifications
    images = collect_precise_images()
    
    # Split and copy images
    split_and_copy_images(images)
    
    logger.info("Precise balanced dataset creation completed")
    
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
