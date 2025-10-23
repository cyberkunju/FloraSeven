"""
Script to prepare the dataset for Model 1 (Whole Plant Health).

This script will:
1. Take all 452 healthy images from the Houseplant dataset
2. Take all 452 wilting images from the Houseplant dataset
3. Split them into train, validation, and test sets
4. Copy the images to the processed directory
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
logger = logging.getLogger("prepare_model1_dataset")

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

def collect_images():
    """
    Collect all healthy and wilting images from the Houseplant dataset.
    
    Returns:
        dict: Dictionary with keys 'healthy', 'wilting' and values as lists of image paths
    """
    images = {
        'healthy': [],
        'wilting': []
    }
    
    # Houseplant healthy images
    houseplant_healthy_dir = os.path.join(DOWNLOADED_DIR, 'Healthy and Wilted Houseplant Images', 
                                         'houseplant_images', 'healthy')
    if os.path.exists(houseplant_healthy_dir):
        for filename in os.listdir(houseplant_healthy_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                images['healthy'].append(os.path.join(houseplant_healthy_dir, filename))
    
    # Houseplant wilted images
    houseplant_wilted_dir = os.path.join(DOWNLOADED_DIR, 'Healthy and Wilted Houseplant Images', 
                                        'houseplant_images', 'wilted')
    if os.path.exists(houseplant_wilted_dir):
        for filename in os.listdir(houseplant_wilted_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                images['wilting'].append(os.path.join(houseplant_wilted_dir, filename))
    
    # Log the counts
    for category, paths in images.items():
        logger.info(f"Collected {len(paths)} {category} images")
    
    return images

def split_and_copy_images(images):
    """
    Split images into train, validation, and test sets and copy to appropriate directories.
    
    Args:
        images: Dictionary with keys 'healthy', 'wilting' and values as lists of image paths
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

def main():
    """Main function to prepare the dataset for Model 1."""
    logger.info("Starting dataset preparation for Model 1 (Whole Plant Health)")
    
    # Collect images
    images = collect_images()
    
    # Split and copy images
    split_and_copy_images(images)
    
    logger.info("Dataset preparation for Model 1 completed")
    
    # Print final counts
    for split_dir, split_name in [(TRAIN_DIR, 'Train'), 
                                 (VALIDATION_DIR, 'Validation'), 
                                 (TEST_DIR, 'Test')]:
        logger.info(f"\n{split_name} set:")
        for class_name in ['healthy', 'wilting']:
            class_dir = os.path.join(split_dir, class_name)
            count = len([f for f in os.listdir(class_dir) 
                        if os.path.isfile(os.path.join(class_dir, f))])
            logger.info(f"  {class_name}: {count} images")

if __name__ == "__main__":
    main()
