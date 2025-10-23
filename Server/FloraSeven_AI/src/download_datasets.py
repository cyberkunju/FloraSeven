"""
Dataset downloader for FloraSeven AI model.

This script downloads and organizes the datasets needed for training the
FloraSeven plant health classification model.
"""

import os
import sys
import zipfile
import shutil
import requests
from tqdm import tqdm
import kaggle
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("dataset_download.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("dataset_downloader")

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

def download_file(url, destination):
    """Download a file from a URL to a destination path with progress bar."""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024  # 1 Kibibyte

        logger.info(f"Downloading {url} to {destination}")

        with open(destination, 'wb') as file, tqdm(
                desc=os.path.basename(destination),
                total=total_size,
                unit='iB',
                unit_scale=True,
                unit_divisor=1024,
        ) as bar:
            for data in response.iter_content(block_size):
                size = file.write(data)
                bar.update(size)

        return True
    except Exception as e:
        logger.error(f"Error downloading {url}: {e}")
        return False

def download_kaggle_dataset(dataset, path):
    """Download a dataset from Kaggle."""
    try:
        logger.info(f"Downloading Kaggle dataset: {dataset}")
        # Check if Kaggle credentials are set
        if not os.environ.get('KAGGLE_USERNAME') or not os.environ.get('KAGGLE_KEY'):
            logger.warning("Kaggle credentials not found in environment variables")
            logger.info("Setting Kaggle credentials from kaggle.json if available")

            # Try to load from kaggle.json in current directory
            if os.path.exists('kaggle.json'):
                import json
                with open('kaggle.json', 'r') as f:
                    creds = json.load(f)
                    os.environ['KAGGLE_USERNAME'] = creds.get('username')
                    os.environ['KAGGLE_KEY'] = creds.get('key')
                logger.info("Loaded Kaggle credentials from kaggle.json in current directory")
            else:
                logger.warning("kaggle.json not found in current directory")

        # Verify credentials are set
        if not os.environ.get('KAGGLE_USERNAME') or not os.environ.get('KAGGLE_KEY'):
            logger.error("Kaggle credentials not set. Cannot download dataset.")
            return False

        # Try to download the dataset
        logger.info(f"Attempting to download {dataset} using Kaggle API")
        kaggle.api.dataset_download_files(dataset, path=path, unzip=True)
        logger.info(f"Successfully downloaded {dataset}")
        return True
    except Exception as e:
        logger.error(f"Error downloading Kaggle dataset {dataset}: {e}")
        logger.info("Attempting alternative download methods...")
        return False

def extract_zip(zip_path, extract_to):
    """Extract a zip file to a directory."""
    try:
        logger.info(f"Extracting {zip_path} to {extract_to}")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        return True
    except Exception as e:
        logger.error(f"Error extracting {zip_path}: {e}")
        return False

def download_alternative_dataset(dataset_name, direct_url, path):
    """Download dataset from a direct URL as an alternative to Kaggle."""
    try:
        # Create a zip file path
        zip_path = os.path.join(path, f"{dataset_name}.zip")

        # Download the zip file
        logger.info(f"Downloading {dataset_name} from direct URL: {direct_url}")
        if download_file(direct_url, zip_path):
            # Extract the zip file
            if extract_zip(zip_path, path):
                logger.info(f"Successfully downloaded and extracted {dataset_name} from direct URL")
                # Remove the zip file after extraction
                os.remove(zip_path)
                return True
            else:
                logger.error(f"Failed to extract {dataset_name} from {zip_path}")
                return False
        else:
            logger.error(f"Failed to download {dataset_name} from direct URL")
            return False
    except Exception as e:
        logger.error(f"Error in alternative download for {dataset_name}: {e}")
        return False

def download_sample_dataset(category, path):
    """Download a small sample dataset for a specific category."""
    try:
        # Sample image URLs for each category
        sample_images = {
            "healthy": [
                "https://images.pexels.com/photos/1084199/pexels-photo-1084199.jpeg",
                "https://images.pexels.com/photos/3511755/pexels-photo-3511755.jpeg",
                "https://images.pexels.com/photos/3097770/pexels-photo-3097770.jpeg"
            ],
            "wilting": [
                "https://images.pexels.com/photos/7728689/pexels-photo-7728689.jpeg",
                "https://images.pexels.com/photos/7728690/pexels-photo-7728690.jpeg",
                "https://images.pexels.com/photos/7728691/pexels-photo-7728691.jpeg"
            ],
            "discolored": [
                "https://images.pexels.com/photos/7728683/pexels-photo-7728683.jpeg",
                "https://images.pexels.com/photos/7728684/pexels-photo-7728684.jpeg",
                "https://images.pexels.com/photos/7728685/pexels-photo-7728685.jpeg"
            ]
        }

        # Create category directory
        category_dir = os.path.join(path, category)
        os.makedirs(category_dir, exist_ok=True)

        # Download sample images for the category
        success_count = 0
        for i, url in enumerate(sample_images.get(category, [])):
            filename = f"sample_{category}_{i+1}.jpg"
            destination = os.path.join(category_dir, filename)
            if download_file(url, destination):
                success_count += 1

        logger.info(f"Downloaded {success_count}/{len(sample_images.get(category, []))} sample images for {category}")
        return success_count > 0
    except Exception as e:
        logger.error(f"Error downloading sample dataset for {category}: {e}")
        return False

def download_datasets():
    """Download all required datasets."""
    # 1. Healthy and Wilted Houseplant Images (Kaggle)
    houseplant_dataset = "russellchan/healthy-and-wilted-houseplant-images"
    houseplant_dir = os.path.join(RAW_DATA_DIR, "houseplant_images")
    os.makedirs(houseplant_dir, exist_ok=True)

    logger.info("Downloading Healthy and Wilted Houseplant Images dataset...")
    if download_kaggle_dataset(houseplant_dataset, houseplant_dir):
        logger.info("Successfully downloaded Houseplant dataset")
    else:
        logger.warning("Failed to download Houseplant dataset from Kaggle, trying alternative method...")
        # Alternative: Download sample images directly
        if download_sample_dataset("healthy", houseplant_dir) and download_sample_dataset("wilting", houseplant_dir):
            logger.info("Successfully downloaded sample houseplant images as alternative")
        else:
            logger.error("Failed to download houseplant dataset using all methods")

    # 2. New Plant Diseases Dataset (Kaggle)
    plant_diseases_dataset = "vipoooool/new-plant-diseases-dataset"
    plant_diseases_dir = os.path.join(RAW_DATA_DIR, "plant_diseases")
    os.makedirs(plant_diseases_dir, exist_ok=True)

    logger.info("Downloading New Plant Diseases Dataset...")
    if download_kaggle_dataset(plant_diseases_dataset, plant_diseases_dir):
        logger.info("Successfully downloaded Plant Diseases dataset")
    else:
        logger.warning("Failed to download Plant Diseases dataset from Kaggle, trying alternative method...")
        # Alternative: Download sample images directly
        if download_sample_dataset("discolored", plant_diseases_dir):
            logger.info("Successfully downloaded sample plant disease images as alternative")
        else:
            logger.error("Failed to download plant diseases dataset using all methods")

    # 3. PlantVillage Dataset (Kaggle) - Replacing the Hugging Face dataset
    plantvillage_dataset = "tushar5harma/plant-village-dataset-updated"
    plantvillage_dir = os.path.join(RAW_DATA_DIR, "plantvillage")
    os.makedirs(plantvillage_dir, exist_ok=True)

    logger.info("Downloading PlantVillage Dataset...")
    if download_kaggle_dataset(plantvillage_dataset, plantvillage_dir):
        logger.info("Successfully downloaded PlantVillage dataset")
    else:
        logger.warning("Failed to download PlantVillage dataset from Kaggle, trying alternative method...")
        # Alternative: Download sample images directly
        logger.info("Using sample images as an alternative")

        # Create a directory for alternative samples
        alternative_dir = os.path.join(RAW_DATA_DIR, "plantvillage_alternative")
        os.makedirs(alternative_dir, exist_ok=True)

        # Download sample images for all categories
        for category in ["healthy", "wilting", "discolored"]:
            download_sample_dataset(category, alternative_dir)

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

    # 3. Process PlantVillage Dataset
    plantvillage_dir = os.path.join(RAW_DATA_DIR, "plantvillage")
    if os.path.exists(plantvillage_dir):
        logger.info(f"Processing PlantVillage dataset from {plantvillage_dir}")

        # Map PlantVillage categories to our categories
        # PlantVillage has categories like 'Apple___healthy', 'Tomato___Late_blight', etc.
        for item in os.listdir(plantvillage_dir):
            item_path = os.path.join(plantvillage_dir, item)

            # Skip non-directories
            if not os.path.isdir(item_path):
                continue

            # Determine target category based on folder name
            if "healthy" in item.lower():
                target_category = "healthy"
            elif "wilted" in item.lower() or "wilting" in item.lower():
                target_category = "wilting"
            else:
                # All disease categories go to discolored
                target_category = "discolored"

            target_dir = os.path.join(PROCESSED_DATA_DIR, target_category)
            logger.info(f"Processing {item} -> {target_category}")

            # Copy images to target directory
            for filename in os.listdir(item_path):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    source_file = os.path.join(item_path, filename)
                    target_file = os.path.join(target_dir, f"plantvillage_{item}_{filename}")
                    try:
                        shutil.copy2(source_file, target_file)
                    except Exception as e:
                        logger.error(f"Error copying {filename}: {e}")
    else:
        logger.warning(f"PlantVillage directory not found: {plantvillage_dir}")

        # Check for alternative samples
        alternative_dir = os.path.join(RAW_DATA_DIR, "plantvillage_alternative")
        if os.path.exists(alternative_dir):
            for category in ["healthy", "wilting", "discolored"]:
                source_dir = os.path.join(alternative_dir, category)
                target_dir = os.path.join(PROCESSED_DATA_DIR, category)

                if os.path.exists(source_dir):
                    logger.info(f"Processing alternative samples from {source_dir} -> {target_dir}")
                    for filename in os.listdir(source_dir):
                        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                            source_file = os.path.join(source_dir, filename)
                            target_file = os.path.join(target_dir, f"plantvillage_alt_{filename}")
                            shutil.copy2(source_file, target_file)

    # Count files in each category
    for category in ['healthy', 'wilting', 'discolored']:
        category_dir = os.path.join(PROCESSED_DATA_DIR, category)
        file_count = len([f for f in os.listdir(category_dir) if os.path.isfile(os.path.join(category_dir, f))])
        logger.info(f"Category '{category}' contains {file_count} images")

        # Check if we have enough images
        if file_count < 10:
            logger.warning(f"Category '{category}' has very few images ({file_count}). Model training may not be effective.")
            # Try to download more sample images if needed
            if file_count < 5:
                logger.info(f"Attempting to download additional sample images for '{category}'")
                download_sample_dataset(category, os.path.join(RAW_DATA_DIR, "additional_samples"))
                # Copy these to processed directory
                source_dir = os.path.join(RAW_DATA_DIR, "additional_samples", category)
                if os.path.exists(source_dir):
                    for filename in os.listdir(source_dir):
                        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                            source_file = os.path.join(source_dir, filename)
                            target_file = os.path.join(category_dir, f"additional_{filename}")
                            shutil.copy2(source_file, target_file)

                    # Recount files
                    file_count = len([f for f in os.listdir(category_dir) if os.path.isfile(os.path.join(category_dir, f))])
                    logger.info(f"Category '{category}' now contains {file_count} images after adding samples")

if __name__ == "__main__":
    logger.info("Starting dataset download and organization process")
    download_datasets()
    organize_datasets()
    logger.info("Dataset download and organization complete")
