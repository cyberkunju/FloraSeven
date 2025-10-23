"""
Script to organize existing datasets without downloading.

This script assumes the datasets have been manually downloaded and placed in the
appropriate directories.
"""

import os
import sys
import logging
import shutil

# Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA_DIR = os.path.join(BASE_DIR, 'data', 'raw')
PROCESSED_DATA_DIR = os.path.join(BASE_DIR, 'data', 'processed')

# Create directories if they don't exist
os.makedirs(RAW_DATA_DIR, exist_ok=True)
os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

# Create category directories in processed data folder
for category in ['healthy', 'wilting', 'discolored']:
    os.makedirs(os.path.join(PROCESSED_DATA_DIR, category), exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("organize_datasets.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("organize_only")

def organize_datasets():
    """Organize downloaded datasets into processed categories."""
    logger.info("Organizing datasets into categories...")

    # 1. Process Houseplant Images
    houseplant_dir = os.path.join(RAW_DATA_DIR, "houseplant_images")

    # Map directories to categories
    category_mapping = {
        "healthy": "healthy",
        "wilted": "wilting"
    }

    # Copy files to appropriate category folders
    for source_category, target_category in category_mapping.items():
        source_dir = os.path.join(houseplant_dir, source_category)
        target_dir = os.path.join(PROCESSED_DATA_DIR, target_category)

        if os.path.exists(source_dir):
            logger.info(f"Processing {source_dir} -> {target_dir}")
            for filename in os.listdir(source_dir):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    source_file = os.path.join(source_dir, filename)
                    target_file = os.path.join(target_dir, f"houseplant_{filename}")
                    shutil.copy2(source_file, target_file)
        else:
            logger.warning(f"Source directory not found: {source_dir}")

    # 2. Process Plant Diseases Dataset
    plant_diseases_dir = os.path.join(RAW_DATA_DIR, "plant_diseases")
    train_dir = os.path.join(plant_diseases_dir, "New Plant Diseases Dataset(Augmented)", "New Plant Diseases Dataset(Augmented)", "train")

    if os.path.exists(train_dir):
        # Copy healthy plants to healthy category
        healthy_dir = os.path.join(train_dir, "healthy")
        target_healthy_dir = os.path.join(PROCESSED_DATA_DIR, "healthy")

        if os.path.exists(healthy_dir):
            logger.info(f"Processing healthy plants from diseases dataset -> {target_healthy_dir}")
            for plant_type in os.listdir(healthy_dir):
                plant_dir = os.path.join(healthy_dir, plant_type)
                if os.path.isdir(plant_dir):
                    for filename in os.listdir(plant_dir):
                        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                            source_file = os.path.join(plant_dir, filename)
                            target_file = os.path.join(target_healthy_dir, f"disease_dataset_healthy_{plant_type}_{filename}")
                            shutil.copy2(source_file, target_file)

        # Copy diseased plants to discolored category
        for category in os.listdir(train_dir):
            if category != "healthy" and os.path.isdir(os.path.join(train_dir, category)):
                category_dir = os.path.join(train_dir, category)
                target_discolored_dir = os.path.join(PROCESSED_DATA_DIR, "discolored")

                logger.info(f"Processing {category} -> {target_discolored_dir}")
                for plant_type in os.listdir(category_dir):
                    plant_dir = os.path.join(category_dir, plant_type)
                    if os.path.isdir(plant_dir):
                        for filename in os.listdir(plant_dir):
                            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                                source_file = os.path.join(plant_dir, filename)
                                target_file = os.path.join(target_discolored_dir, f"disease_dataset_{category}_{plant_type}_{filename}")
                                shutil.copy2(source_file, target_file)
    else:
        logger.warning(f"Plant diseases train directory not found: {train_dir}")
        # Check for sample images instead
        for category in ["healthy", "discolored"]:
            source_dir = os.path.join(plant_diseases_dir, category)
            target_dir = os.path.join(PROCESSED_DATA_DIR, category)

            if os.path.exists(source_dir):
                logger.info(f"Processing sample images from {source_dir} -> {target_dir}")
                for filename in os.listdir(source_dir):
                    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                        source_file = os.path.join(source_dir, filename)
                        target_file = os.path.join(target_dir, f"sample_disease_{filename}")
                        shutil.copy2(source_file, target_file)

    # 3. Process sample images directory if it exists
    sample_dir = os.path.join(BASE_DIR, 'sample_images')
    if os.path.exists(sample_dir):
        logger.info(f"Processing sample images from {sample_dir}")
        for filename in os.listdir(sample_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                # Determine category from filename
                if 'healthy' in filename.lower():
                    category = 'healthy'
                elif 'wilt' in filename.lower():
                    category = 'wilting'
                elif 'discolor' in filename.lower() or 'yellow' in filename.lower():
                    category = 'discolored'
                else:
                    # Default to healthy if can't determine
                    category = 'healthy'

                source_file = os.path.join(sample_dir, filename)
                target_file = os.path.join(PROCESSED_DATA_DIR, category, f"sample_{filename}")
                try:
                    shutil.copy2(source_file, target_file)
                    logger.info(f"Copied {filename} to {category} category")
                except Exception as e:
                    logger.error(f"Error copying {filename}: {e}")

    # Count files in each category
    for category in ['healthy', 'wilting', 'discolored']:
        category_dir = os.path.join(PROCESSED_DATA_DIR, category)
        file_count = len([f for f in os.listdir(category_dir) if os.path.isfile(os.path.join(category_dir, f))])
        logger.info(f"Category '{category}' contains {file_count} images")

if __name__ == "__main__":
    logger.info("Starting dataset organization process")
    organize_datasets()
    logger.info("Dataset organization complete")
