"""
Script to generate augmented samples from existing images.

This script uses data augmentation techniques to generate additional training samples
from the existing images in the dataset.
"""

import os
import sys
import logging
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator, load_img, img_to_array, array_to_img
import matplotlib.pyplot as plt
from PIL import Image

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("augmentation.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("augmentation")

# Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DATA_DIR = os.path.join(BASE_DIR, 'data', 'processed')

# Define augmentation parameters
def get_augmentation_generator():
    """Get an image data generator with augmentation parameters."""
    return ImageDataGenerator(
        rotation_range=40,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest'
    )

def generate_augmented_samples(category, num_samples=20):
    """
    Generate augmented samples for a category.
    
    Args:
        category: Category name ('healthy', 'wilting', 'discolored')
        num_samples: Number of augmented samples to generate per original image
    """
    category_dir = os.path.join(PROCESSED_DATA_DIR, category)
    
    if not os.path.exists(category_dir):
        logger.error(f"Category directory not found: {category_dir}")
        return False
    
    # Get all image files
    image_files = [f for f in os.listdir(category_dir) 
                  if os.path.isfile(os.path.join(category_dir, f)) and 
                  f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    if not image_files:
        logger.warning(f"No images found in {category_dir}")
        return False
    
    logger.info(f"Generating {num_samples} augmented samples per image for category '{category}'")
    
    # Create augmentation generator
    datagen = get_augmentation_generator()
    
    # Generate augmented samples for each image
    for i, filename in enumerate(image_files):
        # Skip if filename contains 'augmented' to avoid re-augmenting
        if 'augmented' in filename.lower():
            continue
            
        image_path = os.path.join(category_dir, filename)
        
        try:
            # Load image
            img = load_img(image_path, target_size=(224, 224))
            x = img_to_array(img)
            x = x.reshape((1,) + x.shape)
            
            # Generate augmented samples
            j = 0
            for batch in datagen.flow(x, batch_size=1):
                # Save augmented image
                aug_img = array_to_img(batch[0])
                base_filename = os.path.splitext(filename)[0]
                aug_filename = f"{base_filename}_augmented_{j+1}.jpg"
                aug_path = os.path.join(category_dir, aug_filename)
                aug_img.save(aug_path)
                
                j += 1
                if j >= num_samples:
                    break
            
            logger.info(f"Generated {j} augmented samples for {filename}")
        
        except Exception as e:
            logger.error(f"Error generating augmented samples for {filename}: {e}")
    
    # Count files after augmentation
    new_count = len([f for f in os.listdir(category_dir) 
                    if os.path.isfile(os.path.join(category_dir, f)) and 
                    f.lower().endswith(('.png', '.jpg', '.jpeg'))])
    
    logger.info(f"Category '{category}' now contains {new_count} images after augmentation")
    
    return True

def visualize_augmentation_samples():
    """Visualize original and augmented samples for each category."""
    categories = ['healthy', 'wilting', 'discolored']
    plt.figure(figsize=(15, 15))
    
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
        
        # Find an original image and its augmented versions
        original_files = [f for f in image_files if 'augmented' not in f]
        if not original_files:
            logger.warning(f"No original images found in {category_dir}")
            continue
        
        original_file = original_files[0]
        base_filename = os.path.splitext(original_file)[0]
        augmented_files = [f for f in image_files if f.startswith(base_filename) and 'augmented' in f]
        
        # Display original image
        plt.subplot(3, 5, i*5+1)
        img = Image.open(os.path.join(category_dir, original_file))
        plt.imshow(img)
        plt.title(f"{category} (original)")
        plt.axis('off')
        
        # Display augmented images
        for j, aug_file in enumerate(augmented_files[:4]):
            plt.subplot(3, 5, i*5+j+2)
            img = Image.open(os.path.join(category_dir, aug_file))
            plt.imshow(img)
            plt.title(f"{category} (augmented {j+1})")
            plt.axis('off')
    
    plt.tight_layout()
    plt.savefig(os.path.join(BASE_DIR, 'augmentation_samples.png'))
    logger.info(f"Augmentation visualization saved to {os.path.join(BASE_DIR, 'augmentation_samples.png')}")

if __name__ == "__main__":
    logger.info("Starting augmented sample generation")
    
    # Generate augmented samples for each category
    for category in ['healthy', 'wilting', 'discolored']:
        generate_augmented_samples(category, num_samples=20)
    
    # Visualize augmentation samples
    visualize_augmentation_samples()
    
    logger.info("Augmented sample generation complete")
