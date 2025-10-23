# FloraSeven AI: Plant Health Classification

This repository contains the AI component of the FloraSeven project, which classifies plant health based on images captured by the ESP32-CAM.

## Overview

The FloraSeven AI model uses transfer learning with MobileNetV2/EfficientNetLite to classify plant images into three categories:
- **Healthy**: Plants with vibrant, turgid leaves and appropriate coloration
- **Wilting**: Plants with limp or drooping leaves, indicating water stress
- **Discolored/Stressed**: Plants with yellowing, browning, or other signs of stress

The model also provides a confidence score (0-100) representing the certainty of the classification.

## Project Structure

```
FloraSeven_AI/
├── data/
│   ├── raw/                  # Raw downloaded datasets
│   └── processed/            # Processed and organized images
│       ├── healthy/
│       ├── wilting/
│       ├── discolored/
│       ├── train/            # Training split
│       ├── validation/       # Validation split
│       └── test/             # Test split
├── models/                   # Saved models and evaluation results
├── notebooks/                # Jupyter notebooks for exploration
├── src/                      # Source code
│   ├── download_datasets.py  # Dataset download and organization
│   ├── data_preprocessing.py # Data preprocessing and augmentation
│   ├── model.py              # Model architecture definition
│   ├── train.py              # Model training and evaluation
│   ├── predict.py            # Prediction functionality
│   └── main.py               # Main script to run the pipeline
├── logs/                     # TensorBoard logs
├── venv/                     # Python virtual environment
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Kaggle API credentials (for downloading datasets)

### Installation

1. Clone this repository:
   ```
   git clone <repository-url>
   cd FloraSeven_AI
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv

   # On Windows
   venv\Scripts\activate

   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up Kaggle API credentials:
   - Go to your Kaggle account settings (https://www.kaggle.com/account)
   - Click "Create New API Token" to download `kaggle.json`
   - Place this file in `~/.kaggle/` on Linux/macOS or `C:\Users\<Windows-username>\.kaggle\` on Windows

## Usage

### Running the Complete Pipeline

To run the complete pipeline from data download to model training and evaluation:

```
python src/main.py --all
```

### Running Individual Steps

You can also run individual steps of the pipeline:

1. Download and organize datasets:
   ```
   python src/main.py --download-data
   ```

2. Preprocess data (split into train/validation/test sets):
   ```
   python src/main.py --preprocess-data
   ```

3. Train the model:
   ```
   python src/main.py --train-model
   ```

4. Test prediction functionality:
   ```
   python src/main.py --test-prediction
   ```

### Making Predictions

To predict the health of a plant from an image:

```
python src/predict.py --image path/to/image.jpg
```

To generate a Class Activation Map (CAM) visualization:

```
python src/predict.py --image path/to/image.jpg --visualize
```

To make predictions on all images in a directory:

```
python src/predict.py --dir path/to/images/ --output results.json
```

## Integration with FloraSeven Backend

The `predict_visual_health()` function in `src/predict.py` is designed to be imported and used by the FloraSeven backend:

```python
from FloraSeven_AI.src.predict import predict_visual_health

# Make a prediction
result = predict_visual_health('path/to/image.jpg')

# Access the results
health_label = result['health_label']  # 'healthy', 'wilting', 'discolored', or 'uncertain'
health_score = result['health_score']  # 0-100 confidence score
```

## Model Training Details

- **Base Model**: MobileNetV2 (pre-trained on ImageNet)
- **Training Strategy**: Two-phase approach
  1. Initial training with frozen base model
  2. Fine-tuning with top layers unfrozen
- **Data Augmentation**: Rotation, shift, shear, zoom, flip
- **Callbacks**: EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
- **Evaluation Metrics**: Accuracy, Precision, Recall, F1-Score, Confusion Matrix

## Project Status

The current status of the project can be found in `pipeline_status.json`, which is updated after each pipeline run.

## Future Enhancements

- Increase dataset size with ESP32-CAM specific images
- Add more specific health categories
- Implement object detection to locate issues on the plant
- Deploy to edge devices using TensorFlow Lite
- Implement active learning for continuous improvement

## License

[Specify your license here]

## Datasets

The model is trained on the following datasets:

1. **Healthy and Wilted Houseplant Images** (from Kaggle)
   - Dataset ID: `russellchan/healthy-and-wilted-houseplant-images`
   - Contains images specifically of houseplants in healthy and wilted states
   - Used for "healthy" and "wilting" categories

2. **New Plant Diseases Dataset** (from Kaggle)
   - Dataset ID: `vipoooool/new-plant-diseases-dataset`
   - Contains a large collection of plant disease images
   - Used for "discolored" category and additional disease patterns

3. **PlantVillage Dataset** (from Kaggle)
   - Dataset ID: `tushar5harma/plant-village-dataset-updated`
   - Contains 54,303 images of healthy and unhealthy plant leaves
   - Comprehensive coverage of plant health conditions across 38 categories

## Acknowledgments

- The model uses datasets from Kaggle
- Transfer learning with pre-trained models from TensorFlow/Keras
- PlantVillage dataset from Penn State University
