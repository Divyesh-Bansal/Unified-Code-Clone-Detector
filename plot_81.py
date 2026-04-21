import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc

# ---------------------------------------------------------
# 1. Reconstruct the Dataset
# ---------------------------------------------------------

# Known Positive Scores (Your 15 True Positives >= 50%)
pos_scores_known = [
    100.0, 98.95, 98.57, 98.21, 91.15, 91.13, 86.61, 
    83.20, 82.71, 79.69, 77.71, 74.07, 65.72, 65.71, 53.18
]

# Unknown Positive Scores (Your 4 False Negatives < 50%)
# Simulated just below the 50% threshold
np.random.seed(42)
pos_scores_unknown = [48.5, 45.2, 42.1, 38.0]
pos_scores = pos_scores_known + pos_scores_unknown

# Known Negative Scores (Your 1 False Positive >= 50%)
neg_scores_known = [50.71]

# Unknown Negative Scores (The 3,220 True Negatives < 50%)
# Simulated as a normal distribution of baseline noise (15% avg)
neg_scores_unknown = np.random.normal(loc=15, scale=10, size=3220)
neg_scores_unknown = np.clip(neg_scores_unknown, 0, 49.9).tolist()
neg_scores = neg_scores_known + neg_scores_unknown

# Combine to create the full dataset arrays
y_true = [1] * len(pos_scores) + [0] * len(neg_scores)
y_score = pos_scores + neg_scores

# Normalize scores to 0.0 - 1.0 for standard metric functions
y_score_norm = [s / 100.0 for s in y_score]

# ---------------------------------------------------------
# 2. Calculate and Plot ROC
# ---------------------------------------------------------

# Calculate False Positive Rate, True Positive Rate, and Area Under Curve
fpr, tpr, thresholds_roc = roc_curve(y_true, y_score_norm)
roc_auc = auc(fpr, tpr)

# Initialize the plot
plt.figure(figsize=(8, 6))

# Plot the ROC curve
plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (AUC = {roc_auc:.4f})')

# Plot the 50/50 baseline guess (diagonal line)
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')

# Formatting
plt.xlim([-0.01, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate (FPR)', fontsize=12)
plt.ylabel('True Positive Rate (TPR) / Recall', fontsize=12)
plt.title('ROC Curve - Hybrid Clone Detector (81 Files)', fontsize=14)
plt.legend(loc="lower right", fontsize=12)
plt.grid(True, alpha=0.3)

# Save and show
plt.savefig('roc_curve_81.png', dpi=150, bbox_inches='tight')
plt.show()