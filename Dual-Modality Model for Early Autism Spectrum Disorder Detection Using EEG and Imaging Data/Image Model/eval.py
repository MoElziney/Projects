import torch
import torch.nn as nn
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

from datasets import AutismDatasetModule
from train import ViTASDLM

from pytorch_lightning import LightningModule
from pytorch_lightning.cli import LightningCLI
from pytorch_lightning.utilities.types import STEP_OUTPUT, EPOCH_OUTPUT

# Added Precision, Recall, and F1Score to the imports
from torchmetrics import Accuracy, ConfusionMatrix, AUROC, Precision, Recall, F1Score
from torch.optim import Optimizer

from timm.data import Mixup
from timm.models import create_model
from timm.optim import create_optimizer_v2
from timm.scheduler import create_scheduler
from timm.scheduler.scheduler import Scheduler

from pathlib import Path
from typing import Optional

# Initialize all metrics
num_classes = 2
task_type = "binary"

auroc = AUROC(task=task_type, num_classes=num_classes)
accuracy = Accuracy(task=task_type, num_classes=num_classes)
precision = Precision(task=task_type, num_classes=num_classes, average='macro')
recall = Recall(task=task_type, num_classes=num_classes, average='macro')
f1_score = F1Score(task=task_type, num_classes=num_classes, average='macro')

# Ensure you fill in the checkpoint and hparams paths before running
model = ViTASDLM.load_from_checkpoint(
    checkpoint_path="",
    hparams_file="",
    map_location=None,
)

def get_predictions(model):
    softmax = nn.Softmax(dim=1)
    dataset_module = AutismDatasetModule()
    model.eval()

    predictions = []
    labels = []

    # Added torch.no_grad() to save memory and speed up evaluation
    with torch.no_grad():
        for data, label in iter(dataset_module.test_dataloader()):
            prediction = model(data)
            predictions.append(softmax(prediction))
            labels.append(label)

    predictions = torch.cat(predictions)
    labels = torch.cat(labels)
    true_predictions = [max(a,b) for a,b in predictions.tolist()]
    
    return predictions, labels, true_predictions

in_preds, in_labels, in_true_preds = get_predictions(model)

# Calculate and print all final metrics
# Using .item() extracts the float value from the PyTorch tensor for cleaner printing
print(f"Testing AUROC:     {auroc(in_preds, in_labels).item():.4f}")
print(f"Testing Accuracy:  {accuracy(in_preds, in_labels).item():.4f}")
print(f"Testing Precision: {precision(in_preds, in_labels).item():.4f}")
print(f"Testing Recall:    {recall(in_preds, in_labels).item():.4f}")
print(f"Testing F1-Score:  {f1_score(in_preds, in_labels).item():.4f}")