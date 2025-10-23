"""
Data loading and preprocessing utilities for FloraSeven AI model.
"""

import os
import re
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from typing import Tuple, Dict, List, Optional, Union
import pandas as pd
import glob
import shutil
from tqdm import tqdm

# Constants
IMAGE_SIZE = (224, 224)  # Standard input size for most models
BATCH_SIZE = 32
AUTOTUNE = tf.data.AUTOTUNE

class FloraSevenDataLoader:
    """Data loader for FloraSeven plant health classification model."""
    
    def __init__(
        self, 
        data_dir: str,
        processed_dir: str = None,
        image_size: Tuple[int, int] = IMAGE_SIZE,
        batch_size: int = BATCH_SIZE,
        validation_split: float = 0.15,
        test_split: float = 0.15,
        seed: int = 42,
        augmentation: bool = True
    ):
        """
        Initialize the data loader.
        
        Args:
            data_dir: Directory containing the raw image data
            processed_dir: Directory to store processed data (if None, uses data_dir/processed)
            image_size: Target image size (height, width)
            batch_size: Batch size for training
            validation_split: Fraction of data to use for validation
            test_split: Fraction of data to use for testing
            seed: Random seed for reproducibility
            augmentation: Whether to use data augmentation
        """
        self.data_dir = data_dir
        self.processed_dir = processed_dir or os.path.join(data_dir, 'processed')
        self.image_size = image_size
        self.batch_size = batch_size
        self.validation_split = validation_split
        self.test_split = test_split
        self.seed = seed
        self.augmentation = augmentation
        
        # Create processed directory if it doesn't exist
        os.makedirs(self.processed_dir, exist_ok=True)
        
        # Create train/val/test directories
        self.train_dir = os.path.join(self.processed_dir, 'train')
        self.val_dir = os.path.join(self.processed_dir, 'validation')
        self.test_dir = os.path.join(self.processed_dir, 'test')
        
        # Class mapping
        self.class_names = ['healthy', 'wilted']
        self.class_to_idx = {cls: i for i, cls in enumerate(self.class_names)}
        
        # Dataset statistics
        self.stats = {}
    
    def _extract_health_score(self, filename: str) -> int:
        """Extract health score from filename."""
        match = re.search(r'(\d+)pct_health', filename)
        if match:
            return int(match.group(1))
        return 0
    
    def _extract_plant_type(self, filename: str) -> str:
        """Extract plant type from filename."""
        if 'healthy_plant_' in filename:
            match = re.search(r'healthy_plant_([a-zA-Z_]+)_\d+pct', filename)
        else:
            match = re.search(r'wilted_plant_([a-zA-Z_]+)_\d+pct', filename)
            
        if match:
            return match.group(1).replace('_', ' ')
        return 'unknown'
    
    def organize_data(self, sdxl_dir: str = None, threshold: int = 50) -> None:
        """
        Organize data into train/validation/test splits with proper class directories.
        
        Args:
            sdxl_dir: Directory containing SDXL-generated images
            threshold: Health score threshold to classify as healthy/wilted
        """
        print("Organizing data into train/validation/test splits...")
        
        # Create class directories
        for split_dir in [self.train_dir, self.val_dir, self.test_dir]:
            for class_name in self.class_names:
                os.makedirs(os.path.join(split_dir, class_name), exist_ok=True)
        
        # Collect all image files
        image_files = []
        
        # If SDXL directory is provided, use those images
        if sdxl_dir and os.path.exists(sdxl_dir):
            healthy_dir = os.path.join(sdxl_dir, 'healthy')
            wilted_dir = os.path.join(sdxl_dir, 'wilted')
            
            if os.path.exists(healthy_dir):
                healthy_files = glob.glob(os.path.join(healthy_dir, '*.png'))
                for file in healthy_files:
                    health_score = self._extract_health_score(os.path.basename(file))
                    plant_type = self._extract_plant_type(os.path.basename(file))
                    image_files.append({
                        'path': file,
                        'health_score': health_score,
                        'plant_type': plant_type,
                        'class': 'healthy' if health_score >= threshold else 'wilted'
                    })
            
            if os.path.exists(wilted_dir):
                wilted_files = glob.glob(os.path.join(wilted_dir, '*.png'))
                for file in wilted_files:
                    health_score = self._extract_health_score(os.path.basename(file))
                    plant_type = self._extract_plant_type(os.path.basename(file))
                    image_files.append({
                        'path': file,
                        'health_score': health_score,
                        'plant_type': plant_type,
                        'class': 'healthy' if health_score >= threshold else 'wilted'
                    })
        
        # Also check the data_dir for any additional images
        for class_name in self.class_names:
            class_dir = os.path.join(self.data_dir, class_name)
            if os.path.exists(class_dir):
                class_files = glob.glob(os.path.join(class_dir, '*.jpg')) + \
                             glob.glob(os.path.join(class_dir, '*.png')) + \
                             glob.glob(os.path.join(class_dir, '*.jpeg'))
                
                for file in class_files:
                    # For non-SDXL images, we use the directory name as the class
                    image_files.append({
                        'path': file,
                        'health_score': 100 if class_name == 'healthy' else 0,
                        'plant_type': 'unknown',
                        'class': class_name
                    })
        
        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(image_files)
        
        # Print dataset statistics
        print(f"Total images: {len(df)}")
        print(f"Class distribution: {df['class'].value_counts().to_dict()}")
        print(f"Plant types: {df['plant_type'].value_counts().to_dict()}")
        
        # Store statistics
        self.stats['total_images'] = len(df)
        self.stats['class_distribution'] = df['class'].value_counts().to_dict()
        self.stats['plant_types'] = df['plant_type'].value_counts().to_dict()
        self.stats['health_score_mean'] = df['health_score'].mean()
        self.stats['health_score_std'] = df['health_score'].std()
        
        # Split into train, validation, and test sets
        # First split off the test set
        train_val_df, test_df = train_test_split(
            df, 
            test_size=self.test_split,
            stratify=df['class'],
            random_state=self.seed
        )
        
        # Then split the remaining data into train and validation
        train_df, val_df = train_test_split(
            train_val_df,
            test_size=self.validation_split / (1 - self.test_split),
            stratify=train_val_df['class'],
            random_state=self.seed
        )
        
        print(f"Train set: {len(train_df)} images")
        print(f"Validation set: {len(val_df)} images")
        print(f"Test set: {len(test_df)} images")
        
        # Store split statistics
        self.stats['train_size'] = len(train_df)
        self.stats['val_size'] = len(val_df)
        self.stats['test_size'] = len(test_df)
        
        # Copy files to their respective directories
        for split_name, split_df, split_dir in [
            ('train', train_df, self.train_dir),
            ('validation', val_df, self.val_dir),
            ('test', test_df, self.test_dir)
        ]:
            print(f"Copying {split_name} files...")
            for _, row in tqdm(split_df.iterrows(), total=len(split_df)):
                src_path = row['path']
                dst_dir = os.path.join(split_dir, row['class'])
                dst_path = os.path.join(dst_dir, os.path.basename(src_path))
                
                # Copy the file
                shutil.copy2(src_path, dst_path)
        
        print("Data organization complete!")
    
    def create_datasets(self) -> Tuple[tf.data.Dataset, tf.data.Dataset, tf.data.Dataset]:
        """
        Create TensorFlow datasets for training, validation, and testing.
        
        Returns:
            Tuple of (train_ds, val_ds, test_ds)
        """
        print("Creating TensorFlow datasets...")
        
        # Define preprocessing function
        def preprocess_image(image):
            image = tf.image.resize(image, self.image_size)
            image = tf.cast(image, tf.float32) / 255.0  # Normalize to [0,1]
            return image
        
        # Create data generators with augmentation for training
        if self.augmentation:
            train_datagen = ImageDataGenerator(
                preprocessing_function=preprocess_image,
                rotation_range=20,
                width_shift_range=0.2,
                height_shift_range=0.2,
                shear_range=0.2,
                zoom_range=0.2,
                horizontal_flip=True,
                fill_mode='nearest'
            )
        else:
            train_datagen = ImageDataGenerator(
                preprocessing_function=preprocess_image
            )
        
        # No augmentation for validation and test
        val_datagen = ImageDataGenerator(
            preprocessing_function=preprocess_image
        )
        
        test_datagen = ImageDataGenerator(
            preprocessing_function=preprocess_image
        )
        
        # Create generators
        train_generator = train_datagen.flow_from_directory(
            self.train_dir,
            target_size=self.image_size,
            batch_size=self.batch_size,
            class_mode='categorical',
            shuffle=True,
            seed=self.seed
        )
        
        val_generator = val_datagen.flow_from_directory(
            self.val_dir,
            target_size=self.image_size,
            batch_size=self.batch_size,
            class_mode='categorical',
            shuffle=False
        )
        
        test_generator = test_datagen.flow_from_directory(
            self.test_dir,
            target_size=self.image_size,
            batch_size=self.batch_size,
            class_mode='categorical',
            shuffle=False
        )
        
        # Update class names from the generator
        self.class_names = list(train_generator.class_indices.keys())
        self.class_to_idx = train_generator.class_indices
        
        # Convert to tf.data.Dataset for better performance
        def generator_to_dataset(generator):
            return tf.data.Dataset.from_generator(
                lambda: generator,
                output_signature=(
                    tf.TensorSpec(shape=(None, *self.image_size, 3), dtype=tf.float32),
                    tf.TensorSpec(shape=(None, len(self.class_names)), dtype=tf.float32)
                )
            ).prefetch(AUTOTUNE)
        
        train_ds = generator_to_dataset(train_generator)
        val_ds = generator_to_dataset(val_generator)
        test_ds = generator_to_dataset(test_generator)
        
        # Store steps per epoch
        self.steps_per_epoch = train_generator.samples // self.batch_size
        self.validation_steps = val_generator.samples // self.batch_size
        self.test_steps = test_generator.samples // self.batch_size
        
        print(f"Created datasets with {len(self.class_names)} classes: {self.class_names}")
        return train_ds, val_ds, test_ds
    
    def visualize_samples(self, num_samples: int = 5) -> None:
        """
        Visualize sample images from each class in the training set.
        
        Args:
            num_samples: Number of samples to visualize per class
        """
        plt.figure(figsize=(15, 5 * len(self.class_names)))
        
        for i, class_name in enumerate(self.class_names):
            class_dir = os.path.join(self.train_dir, class_name)
            image_paths = glob.glob(os.path.join(class_dir, '*'))[:num_samples]
            
            for j, image_path in enumerate(image_paths):
                img = tf.keras.preprocessing.image.load_img(image_path, target_size=self.image_size)
                img_array = tf.keras.preprocessing.image.img_to_array(img) / 255.0
                
                plt.subplot(len(self.class_names), num_samples, i * num_samples + j + 1)
                plt.imshow(img_array)
                plt.title(f"{class_name}: {os.path.basename(image_path)}")
                plt.axis('off')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.processed_dir, 'sample_images.png'))
        plt.close()
        print(f"Sample visualization saved to {os.path.join(self.processed_dir, 'sample_images.png')}")
    
    def get_class_weights(self) -> Dict[int, float]:
        """
        Calculate class weights for imbalanced datasets.
        
        Returns:
            Dictionary mapping class indices to weights
        """
        if not self.stats or 'class_distribution' not in self.stats:
            print("Warning: Class distribution not available. Run organize_data first.")
            return {i: 1.0 for i in range(len(self.class_names))}
        
        # Get class distribution
        class_counts = self.stats['class_distribution']
        total_samples = sum(class_counts.values())
        
        # Calculate weights: inversely proportional to class frequency
        weights = {}
        for class_name, count in class_counts.items():
            class_idx = self.class_to_idx.get(class_name, 0)
            weights[class_idx] = total_samples / (len(class_counts) * count)
        
        print(f"Class weights: {weights}")
        return weights
