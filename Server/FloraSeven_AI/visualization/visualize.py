"""
Visualization utilities for FloraSeven AI model.
"""

import matplotlib.pyplot as plt
import numpy as np
import os
import tensorflow as tf
from sklearn.metrics import confusion_matrix, classification_report, roc_curve, auc, precision_recall_curve
import seaborn as sns
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union, Any
import itertools

def plot_training_history(history: Dict[str, List[float]], save_path: Optional[str] = None) -> None:
    """
    Plot training history.
    
    Args:
        history: Training history dictionary
        save_path: Path to save the plot (if None, plot is displayed)
    """
    plt.figure(figsize=(15, 10))
    
    # Plot accuracy
    plt.subplot(2, 2, 1)
    plt.plot(history['accuracy'], label='Training Accuracy')
    plt.plot(history['val_accuracy'], label='Validation Accuracy')
    plt.title('Model Accuracy')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.legend()
    plt.grid(True)
    
    # Plot loss
    plt.subplot(2, 2, 2)
    plt.plot(history['loss'], label='Training Loss')
    plt.plot(history['val_loss'], label='Validation Loss')
    plt.title('Model Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.grid(True)
    
    # Plot AUC if available
    if 'auc' in history and 'val_auc' in history:
        plt.subplot(2, 2, 3)
        plt.plot(history['auc'], label='Training AUC')
        plt.plot(history['val_auc'], label='Validation AUC')
        plt.title('Model AUC')
        plt.xlabel('Epoch')
        plt.ylabel('AUC')
        plt.legend()
        plt.grid(True)
    
    # Plot learning rate if available
    if 'lr' in history:
        plt.subplot(2, 2, 4)
        plt.semilogy(history['lr'], label='Learning Rate')
        plt.title('Learning Rate')
        plt.xlabel('Epoch')
        plt.ylabel('Learning Rate (log scale)')
        plt.legend()
        plt.grid(True)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path)
        print(f"Training history plot saved to {save_path}")
    else:
        plt.show()
    
    plt.close()

def plot_confusion_matrix(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    class_names: List[str],
    save_path: Optional[str] = None,
    normalize: bool = True,
    title: str = 'Confusion Matrix'
) -> None:
    """
    Plot confusion matrix.
    
    Args:
        y_true: True labels
        y_pred: Predicted labels
        class_names: List of class names
        save_path: Path to save the plot (if None, plot is displayed)
        normalize: Whether to normalize the confusion matrix
        title: Plot title
    """
    # Compute confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    
    # Normalize if requested
    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        fmt = '.2f'
    else:
        fmt = 'd'
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(
        cm,
        annot=True,
        fmt=fmt,
        cmap='Blues',
        xticklabels=class_names,
        yticklabels=class_names
    )
    plt.title(title)
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path)
        print(f"Confusion matrix plot saved to {save_path}")
    else:
        plt.show()
    
    plt.close()

def plot_roc_curve(
    y_true: np.ndarray,
    y_score: np.ndarray,
    class_names: List[str],
    save_path: Optional[str] = None,
    title: str = 'ROC Curve'
) -> None:
    """
    Plot ROC curve.
    
    Args:
        y_true: True labels (one-hot encoded for multi-class)
        y_score: Predicted probabilities
        class_names: List of class names
        save_path: Path to save the plot (if None, plot is displayed)
        title: Plot title
    """
    plt.figure(figsize=(10, 8))
    
    # For binary classification
    if len(class_names) == 2:
        fpr, tpr, _ = roc_curve(y_true, y_score)
        roc_auc = auc(fpr, tpr)
        
        plt.plot(fpr, tpr, lw=2, label=f'ROC curve (AUC = {roc_auc:.2f})')
        plt.plot([0, 1], [0, 1], 'k--', lw=2)
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title(title)
        plt.legend(loc="lower right")
    
    # For multi-class classification
    else:
        # Convert one-hot encoded y_true to class indices
        if y_true.shape[1] > 1:  # one-hot encoded
            y_true_indices = np.argmax(y_true, axis=1)
        else:
            y_true_indices = y_true
        
        # Compute ROC curve and ROC area for each class
        fpr = {}
        tpr = {}
        roc_auc = {}
        
        for i, class_name in enumerate(class_names):
            # Create binary labels for current class (one-vs-rest)
            y_true_binary = (y_true_indices == i).astype(int)
            
            # Get scores for current class
            y_score_class = y_score[:, i]
            
            # Compute ROC curve
            fpr[i], tpr[i], _ = roc_curve(y_true_binary, y_score_class)
            roc_auc[i] = auc(fpr[i], tpr[i])
            
            # Plot ROC curve for current class
            plt.plot(
                fpr[i],
                tpr[i],
                lw=2,
                label=f'{class_name} (AUC = {roc_auc[i]:.2f})'
            )
        
        plt.plot([0, 1], [0, 1], 'k--', lw=2)
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title(title)
        plt.legend(loc="lower right")
    
    plt.grid(True)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path)
        print(f"ROC curve plot saved to {save_path}")
    else:
        plt.show()
    
    plt.close()

def plot_precision_recall_curve(
    y_true: np.ndarray,
    y_score: np.ndarray,
    class_names: List[str],
    save_path: Optional[str] = None,
    title: str = 'Precision-Recall Curve'
) -> None:
    """
    Plot precision-recall curve.
    
    Args:
        y_true: True labels (one-hot encoded for multi-class)
        y_score: Predicted probabilities
        class_names: List of class names
        save_path: Path to save the plot (if None, plot is displayed)
        title: Plot title
    """
    plt.figure(figsize=(10, 8))
    
    # For binary classification
    if len(class_names) == 2:
        precision, recall, _ = precision_recall_curve(y_true, y_score)
        pr_auc = auc(recall, precision)
        
        plt.plot(recall, precision, lw=2, label=f'PR curve (AUC = {pr_auc:.2f})')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.title(title)
        plt.legend(loc="lower left")
    
    # For multi-class classification
    else:
        # Convert one-hot encoded y_true to class indices
        if y_true.shape[1] > 1:  # one-hot encoded
            y_true_indices = np.argmax(y_true, axis=1)
        else:
            y_true_indices = y_true
        
        # Compute precision-recall curve for each class
        precision = {}
        recall = {}
        pr_auc = {}
        
        for i, class_name in enumerate(class_names):
            # Create binary labels for current class (one-vs-rest)
            y_true_binary = (y_true_indices == i).astype(int)
            
            # Get scores for current class
            y_score_class = y_score[:, i]
            
            # Compute precision-recall curve
            precision[i], recall[i], _ = precision_recall_curve(y_true_binary, y_score_class)
            pr_auc[i] = auc(recall[i], precision[i])
            
            # Plot precision-recall curve for current class
            plt.plot(
                recall[i],
                precision[i],
                lw=2,
                label=f'{class_name} (AUC = {pr_auc[i]:.2f})'
            )
        
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.title(title)
        plt.legend(loc="lower left")
    
    plt.grid(True)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path)
        print(f"Precision-recall curve plot saved to {save_path}")
    else:
        plt.show()
    
    plt.close()

def plot_sample_predictions(
    model: tf.keras.Model,
    test_dataset: tf.data.Dataset,
    class_names: List[str],
    num_samples: int = 10,
    save_path: Optional[str] = None
) -> None:
    """
    Plot sample predictions.
    
    Args:
        model: Trained model
        test_dataset: Test dataset
        class_names: List of class names
        num_samples: Number of samples to plot
        save_path: Path to save the plot (if None, plot is displayed)
    """
    # Get a batch of test images
    for images, labels in test_dataset.take(1):
        # Get predictions
        predictions = model.predict(images)
        
        # Plot images with predictions
        plt.figure(figsize=(20, 4 * min(num_samples, len(images))))
        
        for i in range(min(num_samples, len(images))):
            plt.subplot(min(num_samples, len(images)), 5, i * 5 + 1)
            plt.imshow(images[i])
            plt.axis('off')
            
            # Get true label
            true_label = np.argmax(labels[i])
            
            # Get predicted label and confidence
            if len(class_names) == 2:
                # Binary classification
                pred_label = 1 if predictions[i] >= 0.5 else 0
                confidence = float(predictions[i]) if pred_label == 1 else 1 - float(predictions[i])
            else:
                # Multi-class classification
                pred_label = np.argmax(predictions[i])
                confidence = float(predictions[i][pred_label])
            
            # Set title color based on correctness
            title_color = 'green' if pred_label == true_label else 'red'
            
            plt.title(
                f"True: {class_names[true_label]}\nPred: {class_names[pred_label]} ({confidence:.2f})",
                color=title_color
            )
            
            # Plot class probabilities
            plt.subplot(min(num_samples, len(images)), 5, i * 5 + 2)
            if len(class_names) == 2:
                # Binary classification
                probs = [1 - float(predictions[i]), float(predictions[i])]
                plt.bar(class_names, probs, color=['blue', 'orange'])
            else:
                # Multi-class classification
                plt.bar(class_names, predictions[i])
            
            plt.title('Class Probabilities')
            plt.xticks(rotation=45, ha='right')
            
            # Plot feature importance (Grad-CAM) if available
            try:
                # Create a model that outputs both the predictions and the last conv layer activations
                last_conv_layer = None
                for layer in reversed(model.layers):
                    if isinstance(layer, tf.keras.layers.Conv2D):
                        last_conv_layer = layer
                        break
                
                if last_conv_layer is not None:
                    grad_model = tf.keras.models.Model(
                        inputs=[model.inputs],
                        outputs=[model.output, last_conv_layer.output]
                    )
                    
                    # Compute gradients
                    with tf.GradientTape() as tape:
                        preds, conv_outputs = grad_model(np.expand_dims(images[i], axis=0))
                        if len(class_names) == 2:
                            # Binary classification
                            class_idx = 0 if preds[0][0] < 0.5 else 1
                            loss = 1 - preds[0][0] if class_idx == 0 else preds[0][0]
                        else:
                            # Multi-class classification
                            class_idx = tf.argmax(preds[0])
                            loss = preds[0, class_idx]
                    
                    # Extract gradients
                    grads = tape.gradient(loss, conv_outputs)
                    
                    # Global average pooling
                    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
                    
                    # Weight the channels by the gradients
                    conv_outputs = conv_outputs[0]
                    heatmap = tf.reduce_sum(tf.multiply(pooled_grads, conv_outputs), axis=-1)
                    
                    # Normalize the heatmap
                    heatmap = tf.maximum(heatmap, 0) / tf.math.reduce_max(heatmap)
                    heatmap = heatmap.numpy()
                    
                    # Resize the heatmap to the original image size
                    import cv2
                    heatmap = cv2.resize(heatmap, (images[i].shape[1], images[i].shape[0]))
                    
                    # Convert heatmap to RGB
                    heatmap = np.uint8(255 * heatmap)
                    heatmap = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
                    
                    # Convert image to RGB
                    img = (images[i].numpy() * 255).astype(np.uint8)
                    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                    
                    # Superimpose the heatmap on the original image
                    superimposed_img = heatmap * 0.4 + img
                    superimposed_img = np.clip(superimposed_img, 0, 255).astype('uint8')
                    
                    # Convert back to RGB for matplotlib
                    superimposed_img = cv2.cvtColor(superimposed_img, cv2.COLOR_BGR2RGB)
                    
                    # Plot the Grad-CAM
                    plt.subplot(min(num_samples, len(images)), 5, i * 5 + 3)
                    plt.imshow(superimposed_img)
                    plt.title('Grad-CAM')
                    plt.axis('off')
            except Exception as e:
                print(f"Error generating Grad-CAM: {e}")
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path)
        print(f"Sample predictions plot saved to {save_path}")
    else:
        plt.show()
    
    plt.close()

def plot_classification_report(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    class_names: List[str],
    save_path: Optional[str] = None,
    title: str = 'Classification Report'
) -> None:
    """
    Plot classification report as a heatmap.
    
    Args:
        y_true: True labels
        y_pred: Predicted labels
        class_names: List of class names
        save_path: Path to save the plot (if None, plot is displayed)
        title: Plot title
    """
    # Generate classification report
    report = classification_report(
        y_true,
        y_pred,
        target_names=class_names,
        output_dict=True
    )
    
    # Convert to DataFrame
    df = pd.DataFrame(report).transpose()
    
    # Remove support column for visualization
    if 'support' in df.columns:
        support = df['support']
        df = df.drop('support', axis=1)
    else:
        support = None
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(df, annot=True, cmap='Blues', fmt='.2f')
    plt.title(title)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path)
        print(f"Classification report plot saved to {save_path}")
    else:
        plt.show()
    
    plt.close()
    
    # Print support information
    if support is not None:
        print("Support (number of samples per class):")
        for i, class_name in enumerate(class_names):
            if class_name in support.index:
                print(f"  {class_name}: {int(support[class_name])}")

def visualize_model_evaluation(
    model: tf.keras.Model,
    test_dataset: tf.data.Dataset,
    class_names: List[str],
    history: Dict[str, List[float]],
    output_dir: str
) -> None:
    """
    Generate comprehensive model evaluation visualizations.
    
    Args:
        model: Trained model
        test_dataset: Test dataset
        class_names: List of class names
        history: Training history
        output_dir: Directory to save visualizations
    """
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Plot training history
    plot_training_history(
        history,
        save_path=os.path.join(output_dir, 'training_history.png')
    )
    
    # Get predictions on test dataset
    y_true = []
    y_pred = []
    y_score = []
    
    for images, labels in test_dataset:
        predictions = model.predict(images)
        
        # Convert one-hot encoded labels to class indices
        if len(labels.shape) > 1 and labels.shape[1] > 1:
            labels = np.argmax(labels, axis=1)
        
        # Convert predictions to class indices and scores
        if len(class_names) == 2:
            # Binary classification
            pred_indices = (predictions >= 0.5).astype(int).flatten()
            pred_scores = predictions.flatten()
        else:
            # Multi-class classification
            pred_indices = np.argmax(predictions, axis=1)
            pred_scores = predictions
        
        y_true.extend(labels)
        y_pred.extend(pred_indices)
        y_score.extend(pred_scores)
    
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    y_score = np.array(y_score)
    
    # Plot confusion matrix
    plot_confusion_matrix(
        y_true,
        y_pred,
        class_names,
        save_path=os.path.join(output_dir, 'confusion_matrix.png')
    )
    
    # Plot ROC curve
    if len(class_names) == 2:
        # Binary classification
        plot_roc_curve(
            y_true,
            y_score,
            class_names,
            save_path=os.path.join(output_dir, 'roc_curve.png')
        )
        
        # Plot precision-recall curve
        plot_precision_recall_curve(
            y_true,
            y_score,
            class_names,
            save_path=os.path.join(output_dir, 'precision_recall_curve.png')
        )
    else:
        # Multi-class classification
        # Convert class indices to one-hot encoding for ROC curve
        y_true_onehot = tf.keras.utils.to_categorical(y_true, num_classes=len(class_names))
        
        plot_roc_curve(
            y_true_onehot,
            y_score,
            class_names,
            save_path=os.path.join(output_dir, 'roc_curve.png')
        )
        
        # Plot precision-recall curve
        plot_precision_recall_curve(
            y_true_onehot,
            y_score,
            class_names,
            save_path=os.path.join(output_dir, 'precision_recall_curve.png')
        )
    
    # Plot classification report
    plot_classification_report(
        y_true,
        y_pred,
        class_names,
        save_path=os.path.join(output_dir, 'classification_report.png')
    )
    
    # Plot sample predictions
    plot_sample_predictions(
        model,
        test_dataset,
        class_names,
        num_samples=10,
        save_path=os.path.join(output_dir, 'sample_predictions.png')
    )
    
    print(f"Model evaluation visualizations saved to {output_dir}")
