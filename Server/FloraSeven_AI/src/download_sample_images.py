"""
Download sample plant images for testing.

This script downloads a few sample plant images for testing the prediction functionality
without requiring the full dataset download.
"""

import os
import requests
from tqdm import tqdm
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("download_samples")

# Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLE_DIR = os.path.join(BASE_DIR, 'sample_images')

# Create sample directory if it doesn't exist
os.makedirs(SAMPLE_DIR, exist_ok=True)

# Sample image URLs
SAMPLE_IMAGES = [
    {
        "url": "https://images.pexels.com/photos/1084199/pexels-photo-1084199.jpeg",
        "filename": "healthy_plant_sample.jpg",
        "category": "healthy"
    },
    {
        "url": "https://images.pexels.com/photos/7728689/pexels-photo-7728689.jpeg",
        "filename": "wilted_plant_sample.jpg",
        "category": "wilting"
    },
    {
        "url": "https://images.pexels.com/photos/7728683/pexels-photo-7728683.jpeg",
        "filename": "discolored_plant_sample.jpg",
        "category": "discolored"
    }
]

def download_file(url, destination):
    """Download a file from a URL to a destination path with progress bar."""
    try:
        # Add User-Agent header to comply with Wikimedia's policy
        headers = {
            'User-Agent': 'FloraSeven/1.0 (https://github.com/yourusername/floraseven; your.email@example.com) Python/3.9'
        }
        response = requests.get(url, stream=True, headers=headers)
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

def download_sample_images():
    """Download sample images for testing."""
    logger.info(f"Downloading {len(SAMPLE_IMAGES)} sample images to {SAMPLE_DIR}")

    success_count = 0
    for image in SAMPLE_IMAGES:
        destination = os.path.join(SAMPLE_DIR, image["filename"])
        if download_file(image["url"], destination):
            success_count += 1

    logger.info(f"Successfully downloaded {success_count}/{len(SAMPLE_IMAGES)} sample images")

    return success_count == len(SAMPLE_IMAGES)

if __name__ == "__main__":
    logger.info("Starting sample image download")
    if download_sample_images():
        logger.info("Sample image download completed successfully")
    else:
        logger.warning("Sample image download completed with errors")
