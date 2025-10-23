"""
Test script to verify that the environment is set up correctly.

This script checks that all required libraries are installed and
the GPU is available (if applicable).
"""

import os
import sys
import importlib
import platform
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("test_environment")

def check_library(library_name):
    """Check if a library is installed and get its version."""
    try:
        # Special case for Pillow which is imported as PIL
        if library_name == 'pillow':
            lib = importlib.import_module('PIL')
            version = getattr(lib, '__version__', 'unknown')
        # Special case for opencv-python which is imported as cv2
        elif library_name == 'opencv-python':
            lib = importlib.import_module('cv2')
            version = getattr(lib, '__version__', 'unknown')
        # Special case for scikit-learn which is imported as sklearn
        elif library_name == 'scikit-learn':
            lib = importlib.import_module('sklearn')
            version = getattr(lib, '__version__', 'unknown')
        # Special case for kaggle to avoid authentication error
        elif library_name == 'kaggle':
            try:
                lib = importlib.import_module('kaggle')
                # Don't call authenticate() which requires credentials
                version = getattr(lib, '__version__', 'unknown')
            except Exception as e:
                logger.info(f"✓ kaggle is installed but encountered an error: {e}")
                return True
        else:
            lib = importlib.import_module(library_name)
            version = getattr(lib, '__version__', 'unknown')

        logger.info(f"✓ {library_name} is installed (version: {version})")
        return True
    except ImportError:
        logger.error(f"✗ {library_name} is NOT installed")
        return False

def check_tensorflow_gpu():
    """Check if TensorFlow can access the GPU."""
    try:
        import tensorflow as tf
        gpus = tf.config.list_physical_devices('GPU')
        if gpus:
            logger.info(f"✓ TensorFlow can access {len(gpus)} GPU(s)")
            for gpu in gpus:
                logger.info(f"  - {gpu.name}")

            # Try to allocate memory on the GPU
            try:
                tf.config.experimental.set_memory_growth(gpus[0], True)
                logger.info("✓ Successfully configured GPU memory growth")
            except RuntimeError as e:
                logger.warning(f"! Could not configure GPU memory growth: {e}")

            return True
        else:
            logger.warning("! No GPU available for TensorFlow")
            logger.info("  TensorFlow will run on CPU")
            return False
    except Exception as e:
        logger.error(f"✗ Error checking TensorFlow GPU: {e}")
        return False

def check_environment():
    """Check the Python environment and required libraries."""
    # Check Python version
    python_version = platform.python_version()
    if python_version >= '3.8':
        logger.info(f"✓ Python version is {python_version}")
    else:
        logger.warning(f"! Python version is {python_version}, recommended: 3.8 or higher")

    # Check operating system
    os_info = platform.platform()
    logger.info(f"✓ Operating system: {os_info}")

    # Check required libraries
    required_libraries = [
        'tensorflow',
        'numpy',
        'pillow',
        'opencv-python',
        'scikit-learn',
        'matplotlib',
        'seaborn',
        'pandas',
        'tqdm',
        'kaggle'
    ]

    all_installed = True
    for lib in required_libraries:
        if not check_library(lib):
            all_installed = False

    # Check TensorFlow GPU
    has_gpu = check_tensorflow_gpu()

    # Check Kaggle API credentials
    kaggle_cred_path = os.path.join(os.path.expanduser('~'), '.kaggle', 'kaggle.json')
    if os.path.exists(kaggle_cred_path):
        logger.info("✓ Kaggle API credentials found")
    else:
        logger.warning("! Kaggle API credentials not found at ~/.kaggle/kaggle.json")
        logger.info("  You will need to set up Kaggle credentials to download datasets")
        logger.info("  This is not a critical error for testing the environment")

        # Create directory for kaggle credentials
        os.makedirs(os.path.join(os.path.expanduser('~'), '.kaggle'), exist_ok=True)

        # Create a placeholder kaggle.json file with instructions
        placeholder_content = {
            "username": "YOUR-KAGGLE-USERNAME",
            "key": "YOUR-KAGGLE-API-KEY"
        }

        # Don't actually write the file, just show instructions
        logger.info("  To set up Kaggle credentials:")
        logger.info("  1. Go to https://www.kaggle.com/account")
        logger.info("  2. Click 'Create New API Token' to download kaggle.json")
        logger.info("  3. Place this file in ~/.kaggle/ directory")

    # Overall status
    if all_installed:
        logger.info("✓ All required libraries are installed")
    else:
        logger.error("✗ Some required libraries are missing")

    # Return True if all libraries are installed, regardless of GPU or Kaggle credentials
    return all_installed

if __name__ == "__main__":
    logger.info("Testing FloraSeven AI environment...")

    if check_environment():
        logger.info("✓ Environment check passed")
        sys.exit(0)
    else:
        logger.warning("! Environment check completed with warnings")
        sys.exit(1)
