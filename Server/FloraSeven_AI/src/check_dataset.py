"""
Script to check the dataset structure and verify that we have enough images for training.
"""

import os
import sys
import logging
import matplotlib.pyplot as plt
import random
from PIL import Image

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("check_dataset.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("check_dataset")

# Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DATA_DIR = os.path.join(BASE_DIR, 'data', 'processed')

def check_dataset_structure():
    """Check the dataset structure and count images in each category."""
    logger.info("Checking dataset structure...")
    
    # Check if processed data directory exists
    if not os.path.exists(PROCESSED_DATA_DIR):
        logger.error(f"Processed data directory not found: {PROCESSED_DATA_DIR}")
        logger.info("Please run download_datasets.py or organize_only.py first")
        return False
    
    # Check each category
    categories = ['healthy', 'wilting', 'discolored']
    category_counts = {}
    
    for category in categories:
        category_dir = os.path.join(PROCESSED_DATA_DIR, category)
        
        if not os.path.exists(category_dir):
            logger.error(f"Category directory not found: {category_dir}")
            continue
        
        # Count images
        image_files = [f for f in os.listdir(category_dir) 
                      if os.path.isfile(os.path.join(category_dir, f)) and 
                      f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        
        category_counts[category] = len(image_files)
        
        logger.info(f"Category '{category}': {len(image_files)} images")
        
        # Check if we have enough images
        if len(image_files) < 10:
            logger.warning(f"Category '{category}' has very few images ({len(image_files)}). Model training may not be effective.")
        elif len(image_files) < 50:
            logger.warning(f"Category '{category}' has relatively few images ({len(image_files)}). Consider adding more for better results.")
        else:
            logger.info(f"Category '{category}' has a good number of images ({len(image_files)}).")
    
    # Check if we have a balanced dataset
    if len(category_counts) == 3:
        min_count = min(category_counts.values())
        max_count = max(category_counts.values())
        
        if max_count > min_count * 3:
            logger.warning(f"Dataset is imbalanced. Max count ({max_count}) is more than 3x min count ({min_count}).")
            logger.info("Consider using class weights or balancing the dataset.")
        else:
            logger.info("Dataset is relatively balanced.")
    
    return True

def visualize_samples():
    """Visualize random samples from each category."""
    logger.info("Visualizing random samples from each category...")
    
    categories = ['healthy', 'wilting', 'discolored']
    plt.figure(figsize=(15, 5))
    
    for i, category in enumerate(categories):
        category_dir = os.path.join(PROCESSED_DATA_DIR, category)
        
        if not os.path.exists(category_dir):
            logger.error(f"Category directory not found: {category_dir}")
            continue
        
        # Get all image files
        image_files = [f for f in os.listdir(category_dir) 
                      if os.path.isfile(os.path.join(category_dir, f)) and 
                      f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        
        if not image_files:
            logger.warning(f"No images found in {category_dir}")
            continue
        
        # Select a random image
        random_image = random.choice(image_files)
        image_path = os.path.join(category_dir, random_image)
        
        # Display the image
        plt.subplot(1, 3, i+1)
        img = Image.open(image_path)
        plt.imshow(img)
        plt.title(f"{category} ({len(image_files)} images)")
        plt.axis('off')
    
    plt.tight_layout()
    plt.savefig(os.path.join(BASE_DIR, 'sample_images.png'))
    logger.info(f"Sample visualization saved to {os.path.join(BASE_DIR, 'sample_images.png')}")

if __name__ == "__main__":
    logger.info("Starting dataset check")
    if check_dataset_structure():
        visualize_samples()
        logger.info("Dataset check complete")
    else:
        logger.error("Dataset check failed")
