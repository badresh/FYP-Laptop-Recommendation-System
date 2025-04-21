import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import precision_recall_curve, confusion_matrix, mean_squared_error, roc_curve, auc, accuracy_score
import numpy as np

def evaluate_model(y_true, y_pred, y_scores):
    # Calculate metrics
    precision, recall, _ = precision_recall_curve(y_true, y_scores)
    fpr, tpr, _ = roc_curve(y_true, y_scores)
    roc_auc = auc(fpr, tpr)
    accuracy = accuracy_score(y_true, y_pred)
    mse_val = mean_squared_error(y_true, y_pred)
    
    # Precision-Recall Curve
    plt.figure()
    plt.plot(recall, precision, marker='.')
    plt.title('Precision-Recall Curve')
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.show()

    # ROC Curve
    plt.figure()
    plt.plot(fpr, tpr, marker='.', label=f"ROC curve (area = {roc_auc:.2f})")
    plt.title("Receiver Operating Characteristic")
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.legend(loc="lower right")
    plt.show()

    # Performance Metrics
    print(f"Precision: {np.mean(precision):.2f}")
    print(f"Recall: {np.mean(recall):.2f}")
    print(f"Accuracy: {accuracy:.2f}")
    print(f"MSE: {mse_val:.2f}")

    # Confusion Matrix
    cm = confusion_matrix(y_true, y_pred)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.title('Confusion Matrix')
    plt.xlabel('Predicted')
    plt.ylabel('True')
    plt.show()

    # Accuracy Graph
    iterations = list(range(1, len(y_true) + 1))
    accuracies = [accuracy for _ in range(len(y_true))]  # Example: generate a list or fetch from data
    plt.figure()
    plt.plot(iterations, accuracies, marker='x', linestyle='-')
    plt.title('Accuracy Over Iterations')
    plt.xlabel('Iterations')
    plt.ylabel('Accuracy')
    plt.show()

    # Precision Graph
    precision_values = precision[:-1]  # Drop the last precision (usually insignificant)
    plt.figure()
    plt.plot(iterations[:len(precision_values)], precision_values, marker='o', linestyle='-')
    plt.title('Precision Over Iterations')
    plt.xlabel('Iterations')
    plt.ylabel('Precision')
    plt.show()

if __name__ == "__main__":
    # Sample data setup (Make sure to use your real data here)
    y_true = [0, 1, 0, 1, 1, 0, 1, 0]
    y_pred = [0, 1, 0, 0, 1, 0, 1, 1]
    y_scores = [0.1, 0.9, 0.2, 0.4, 0.85, 0.1, 0.75, 0.3]

    evaluate_model(y_true, y_pred, y_scores)








# import matplotlib.pyplot as plt
# import seaborn as sns
# from sklearn.metrics import (
#     precision_recall_curve, confusion_matrix, mean_squared_error,
#     roc_curve, auc, accuracy_score, precision_score, recall_score
# )
# import numpy as np

# def evaluate_model(y_true, y_pred, y_scores):
#     # Calculate metrics
#     precision_curve, recall_curve, _ = precision_recall_curve(y_true, y_scores)
#     fpr, tpr, _ = roc_curve(y_true, y_scores)
#     roc_auc = auc(fpr, tpr)
    
#     precision_val = precision_score(y_true, y_pred)
#     recall_val = recall_score(y_true, y_pred)
#     accuracy = accuracy_score(y_true, y_pred)
#     mse_val = mean_squared_error(y_true, y_pred)

#     # Precision-Recall Curve
#     plt.figure()
#     plt.plot(recall_curve, precision_curve, marker='.')
#     plt.title('Precision-Recall Curve')
#     plt.xlabel('Recall')
#     plt.ylabel('Precision')
#     plt.grid()
#     plt.show()

#     # ROC Curve
#     plt.figure()
#     plt.plot(fpr, tpr, marker='.', label=f"ROC AUC = {roc_auc:.2f}")
#     plt.title("ROC Curve")
#     plt.xlabel('False Positive Rate')
#     plt.ylabel('True Positive Rate')
#     plt.legend()
#     plt.grid()
#     plt.show()

#     # Performance Metrics
#     print(f"Precision Score: {precision_val:.2f}")
#     print(f"Recall Score: {recall_val:.2f}")
#     print(f"Accuracy: {accuracy:.2f}")
#     print(f"Mean Squared Error: {mse_val:.2f}")

#     # Confusion Matrix
#     cm = confusion_matrix(y_true, y_pred)
#     sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
#     plt.title('Confusion Matrix')
#     plt.xlabel('Predicted')
#     plt.ylabel('Actual')
#     plt.show()

# if __name__ == "__main__":
#     # Sample data
#     y_true = [0, 1, 0, 1, 1, 0, 1, 0]
#     y_pred = [0, 1, 0, 0, 1, 0, 1, 1]
#     y_scores = [0.1, 0.9, 0.2, 0.4, 0.85, 0.1, 0.75, 0.3]

#     evaluate_model(y_true, y_pred, y_scores)




# import matplotlib.pyplot as plt
# import seaborn as sns
# from sklearn.metrics import (
#     precision_recall_curve, confusion_matrix, 
#     mean_squared_error, roc_curve, auc, 
#     accuracy_score, precision_score, recall_score,
#     f1_score, classification_report
# )
# import numpy as np

# def evaluate_model_performance(y_true, y_pred, y_scores):
#     """
#     Comprehensive model evaluation with additional metrics and visualizations
#     """
#     # Calculate all metrics
#     accuracy = accuracy_score(y_true, y_pred)
#     precision = precision_score(y_true, y_pred)
#     recall = recall_score(y_true, y_pred)
#     f1 = f1_score(y_true, y_pred)
    
#     # Calculate curves for plotting
#     precision_curve, recall_curve, _ = precision_recall_curve(y_true, y_scores)
#     fpr, tpr, _ = roc_curve(y_true, y_scores)
#     roc_auc = auc(fpr, tpr)

#     # Print detailed metrics
#     print("\n=== Model Performance Metrics ===")
#     print(f"Accuracy: {accuracy:.4f}")
#     print(f"Precision: {precision:.4f}")
#     print(f"Recall: {recall:.4f}")
#     print(f"F1 Score: {f1:.4f}")
#     print(f"ROC AUC: {roc_auc:.4f}")
    
#     # Print detailed classification report
#     print("\n=== Classification Report ===")
#     print(classification_report(y_true, y_pred))

#     # Create subplots for all visualizations
#     plt.style.use('seaborn')
#     fig, axes = plt.subplots(2, 2, figsize=(15, 12))
#     fig.suptitle('Model Performance Metrics Visualization', fontsize=16)

#     # 1. Confusion Matrix
#     sns.heatmap(confusion_matrix(y_true, y_pred), 
#                 annot=True, fmt='d', cmap='Blues',
#                 ax=axes[0,0])
#     axes[0,0].set_title('Confusion Matrix')
#     axes[0,0].set_xlabel('Predicted')
#     axes[0,0].set_ylabel('True')

#     # 2. ROC Curve
#     axes[0,1].plot(fpr, tpr, color='darkorange', lw=2,
#                    label=f'ROC curve (AUC = {roc_auc:.2f})')
#     axes[0,1].plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
#     axes[0,1].set_title('Receiver Operating Characteristic (ROC)')
#     axes[0,1].set_xlabel('False Positive Rate')
#     axes[0,1].set_ylabel('True Positive Rate')
#     axes[0,1].legend(loc="lower right")

#     # 3. Precision-Recall Curve
#     axes[1,0].plot(recall_curve, precision_curve, color='blue', lw=2)
#     axes[1,0].set_title('Precision-Recall Curve')
#     axes[1,0].set_xlabel('Recall')
#     axes[1,0].set_ylabel('Precision')
#     axes[1,0].set_ylim([0.0, 1.05])

#     # 4. Metrics Comparison
#     metrics = ['Accuracy', 'Precision', 'Recall', 'F1 Score']
#     values = [accuracy, precision, recall, f1]
#     axes[1,1].bar(metrics, values, color=['blue', 'green', 'red', 'purple'])
#     axes[1,1].set_title('Performance Metrics Comparison')
#     axes[1,1].set_ylim([0, 1])
#     for i, v in enumerate(values):
#         axes[1,1].text(i, v + 0.01, f'{v:.3f}', ha='center')

#     plt.tight_layout()
#     plt.show()

#     # Additional visualization: Performance over iterations
#     plt.figure(figsize=(10, 5))
#     iterations = range(1, len(y_true) + 1)
#     metrics_over_time = {
#         'Accuracy': [accuracy] * len(iterations),
#         'Precision': [precision] * len(iterations),
#         'Recall': [recall] * len(iterations)
#     }
    
#     for metric, values in metrics_over_time.items():
#         plt.plot(iterations, values, marker='o', label=metric)
    
#     plt.title('Performance Metrics Over Iterations')
#     plt.xlabel('Iterations')
#     plt.ylabel('Score')
#     plt.legend()
#     plt.grid(True)
#     plt.show()

# if __name__ == "__main__":
#     # Example usage with sample data
#     # Replace these with your actual data
#     y_true = np.array([0, 1, 0, 1, 1, 0, 1, 0, 1, 1])
#     y_pred = np.array([0, 1, 0, 0, 1, 0, 1, 1, 1, 1])
#     y_scores = np.array([0.1, 0.9, 0.2, 0.4, 0.85, 0.1, 0.75, 0.6, 0.95, 0.83])

#     evaluate_model_performance(y_true, y_pred, y_scores)