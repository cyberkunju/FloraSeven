"""
Main script for FloraSeven AI plant health classification model.

This script orchestrates the entire pipeline from data download to model training
and evaluation.
"""

import os
import argparse
import logging
import sys
import json
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("floraseven_ai.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("main")

def run_pipeline(args):
    """
    Run the complete pipeline or specific components based on arguments.

    Args:
        args: Command line arguments
    """
    # Record start time
    start_time = datetime.now()
    logger.info(f"Starting FloraSeven AI pipeline at {start_time}")

    # Create project status file
    status = {
        'pipeline_start_time': start_time.strftime("%Y-%m-%d %H:%M:%S"),
        'steps': {}
    }

    # Define base directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    try:
        # Step 1: Download datasets
        if args.download_data or args.all:
            logger.info("Step 1: Downloading datasets")
            status['steps']['download_data'] = {'status': 'running', 'start_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

            try:
                from download_datasets import download_datasets, organize_datasets
                download_datasets()
                organize_datasets()

                status['steps']['download_data']['status'] = 'completed'
                status['steps']['download_data']['end_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                logger.info("Dataset download and organization completed")
            except Exception as e:
                logger.warning(f"Dataset download failed: {e}")
                logger.info("Skipping download step and using existing data")

                # Try to run organize_only.py instead
                try:
                    import importlib.util
                    spec = importlib.util.spec_from_file_location("organize_only", os.path.join(base_dir, 'src', 'organize_only.py'))
                    organize_only = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(organize_only)

                    # Run organize_datasets function
                    organize_only.organize_datasets()

                    status['steps']['download_data']['status'] = 'completed'
                    status['steps']['download_data']['end_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    status['steps']['download_data']['note'] = 'Used existing data instead of downloading'
                    logger.info("Used existing data instead of downloading")
                except Exception as e2:
                    logger.warning(f"Failed to organize existing data: {e2}")
                    status['steps']['download_data']['status'] = 'skipped'
                    status['steps']['download_data']['end_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    status['steps']['download_data']['error'] = str(e2)

        # Step 1.5: Balance dataset
        if args.balance_dataset or args.all:
            logger.info("Step 1.5: Creating balanced dataset")
            status['steps']['balance_dataset'] = {'status': 'running', 'start_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

            try:
                from balance_dataset import main as balance_dataset
                balance_dataset()

                status['steps']['balance_dataset']['status'] = 'completed'
                status['steps']['balance_dataset']['end_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                logger.info("Balanced dataset creation completed")
            except Exception as e:
                logger.error(f"Balanced dataset creation failed: {e}")
                status['steps']['balance_dataset']['status'] = 'failed'
                status['steps']['balance_dataset']['end_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                status['steps']['balance_dataset']['error'] = str(e)
                raise e

        # Step 2: Preprocess data
        if args.preprocess_data or args.all:
            logger.info("Step 2: Preprocessing data")
            status['steps']['preprocess_data'] = {'status': 'running', 'start_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

            from data_preprocessing import main as preprocess_data
            train_generator, validation_generator, test_generator, class_weights = preprocess_data()

            status['steps']['preprocess_data']['status'] = 'completed'
            status['steps']['preprocess_data']['end_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logger.info("Data preprocessing completed")

        # Step 3: Train model
        if args.train_model or args.all:
            logger.info("Step 3: Training model")
            status['steps']['train_model'] = {'status': 'running', 'start_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

            from train import main as train_model
            model, evaluation_results = train_model()

            status['steps']['train_model']['status'] = 'completed'
            status['steps']['train_model']['end_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            status['steps']['train_model']['evaluation_results'] = evaluation_results
            logger.info("Model training completed")

        # Step 4: Test prediction
        if args.test_prediction or args.all:
            logger.info("Step 4: Testing prediction functionality")
            status['steps']['test_prediction'] = {'status': 'running', 'start_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

            # Check if test images exist
            test_dir = os.path.join(base_dir, 'data', 'processed', 'test')
            if os.path.exists(test_dir):
                from predict import batch_predict

                # Get a few test images from each category
                test_images = []
                for category in ['healthy', 'wilting', 'discolored']:
                    category_dir = os.path.join(test_dir, category)
                    if os.path.exists(category_dir):
                        image_files = [f for f in os.listdir(category_dir)
                                      if os.path.isfile(os.path.join(category_dir, f)) and
                                      f.lower().endswith(('.png', '.jpg', '.jpeg'))]
                        # Take up to 3 images from each category
                        for filename in image_files[:3]:
                            test_images.append(os.path.join(category_dir, filename))

                if test_images:
                    # Create a test directory
                    test_output_dir = os.path.join(base_dir, 'test_predictions')
                    os.makedirs(test_output_dir, exist_ok=True)

                    # Copy test images to test directory
                    import shutil
                    for image_path in test_images:
                        shutil.copy2(image_path, test_output_dir)

                    # Run batch prediction
                    prediction_results = batch_predict(
                        test_output_dir,
                        os.path.join(test_output_dir, 'prediction_results.json')
                    )

                    status['steps']['test_prediction']['results'] = prediction_results
                else:
                    logger.warning("No test images found")
                    status['steps']['test_prediction']['warning'] = "No test images found"
            else:
                logger.warning("Test directory not found")
                status['steps']['test_prediction']['warning'] = "Test directory not found"

            status['steps']['test_prediction']['status'] = 'completed'
            status['steps']['test_prediction']['end_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logger.info("Prediction testing completed")

        # Record end time
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        status['pipeline_end_time'] = end_time.strftime("%Y-%m-%d %H:%M:%S")
        status['duration_seconds'] = duration

        logger.info(f"FloraSeven AI pipeline completed in {duration:.2f} seconds")

        # Save status to file
        status_file = os.path.join(base_dir, 'pipeline_status.json')
        with open(status_file, 'w') as f:
            json.dump(status, f, indent=4)
        logger.info(f"Pipeline status saved to {status_file}")

        return True

    except Exception as e:
        logger.error(f"Pipeline failed: {e}")

        # Update status with error
        status['error'] = str(e)
        status['pipeline_end_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Save status to file
        status_file = os.path.join(base_dir, 'pipeline_status.json')
        with open(status_file, 'w') as f:
            json.dump(status, f, indent=4)
        logger.info(f"Pipeline status with error saved to {status_file}")

        return False

def main():
    """Parse command line arguments and run the pipeline."""
    parser = argparse.ArgumentParser(description='FloraSeven AI Plant Health Classification Pipeline')

    parser.add_argument('--all', action='store_true', help='Run the complete pipeline')
    parser.add_argument('--download-data', action='store_true', help='Download and organize datasets')
    parser.add_argument('--balance-dataset', action='store_true', help='Create a balanced dataset from raw data')
    parser.add_argument('--preprocess-data', action='store_true', help='Preprocess data')
    parser.add_argument('--train-model', action='store_true', help='Train the model')
    parser.add_argument('--test-prediction', action='store_true', help='Test prediction functionality')

    args = parser.parse_args()

    # If no arguments provided, show help
    if not any(vars(args).values()):
        parser.print_help()
        return

    # Run the pipeline
    success = run_pipeline(args)

    if success:
        logger.info("Pipeline completed successfully")
    else:
        logger.error("Pipeline failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
