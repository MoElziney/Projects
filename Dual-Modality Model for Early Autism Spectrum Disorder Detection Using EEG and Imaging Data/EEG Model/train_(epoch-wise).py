import os
import glob
import random  
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix, roc_curve, auc
import matplotlib.pyplot as plt
import warnings
import functools
from model import SpectrogramResNet

warnings.filterwarnings('ignore')

# --- Configuration ---
PROCESSED_DIR = "D:/ds006780-download/processed_data_v2"
BATCH_SIZE = 32
EPOCHS = 10 
LEARNING_RATE = 1e-4 
WEIGHT_DECAY = 1e-4 
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def calculate_metrics(labels, preds, probs):
    try:
        acc = accuracy_score(labels, preds)
        prec = precision_score(labels, preds, zero_division=0)
        rec = recall_score(labels, preds, zero_division=0)
        f1 = f1_score(labels, preds, zero_division=0)
        auc_val = roc_auc_score(labels, probs)
    except ValueError: 
        acc = accuracy_score(labels, preds)
        prec, rec, f1, auc_val = 0.0, 0.0, 0.0, 0.0
    return acc, prec, rec, f1, auc_val

def print_metrics(phase, loss, acc, prec, rec, f1, auc_val):
    print(f"  {phase} -> Loss: {loss:.4f} | Acc: {acc:.4f} | Prec: {prec:.4f} | Rec: {rec:.4f} | F1: {f1:.4f} | AUC: {auc_val:.4f}")


@functools.lru_cache(maxsize=128)
def load_cached_file(path):
    return np.load(path, allow_pickle=True).item()

class GlobalLeakageDataset(Dataset):
    def __init__(self, samples_list):
        self.samples = samples_list

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        path, epoch_idx, label = self.samples[idx]
        
        data_dict = load_cached_file(path)
        x = data_dict['data'][epoch_idx]
        
        return torch.tensor(x, dtype=torch.float32), torch.tensor([label], dtype=torch.float32)

# ==========================================
# TRAINING LOOP
# ==========================================
def run_epoch(model, dataloader, criterion, optimizer, scaler, is_train=True):
    if is_train:
        model.train()
    else:
        model.eval()
        
    running_loss = 0.0
    all_preds, all_probs, all_labels = [], [], []

    with torch.set_grad_enabled(is_train):
        for x, y in dataloader:
            x = x.to(DEVICE, non_blocking=True)
            y = y.to(DEVICE, non_blocking=True)
            
            if is_train: 
                optimizer.zero_grad()
            
            # 1. Run the forward pass in 16-bit mixed precision for speed
            with torch.amp.autocast('cuda', enabled=(DEVICE.type == 'cuda')):
                outputs = model(x)
            
            # 2. Step OUTSIDE the autocast block and force 32-bit float for safe BCELoss math
            loss = criterion(outputs.float(), y.float())
            
            if is_train:
                # 3. Use the scaler to safely backpropagate the gradients
                scaler.scale(loss).backward()
                scaler.step(optimizer)
                scaler.update()
            
            running_loss += loss.item() * x.size(0)
            
            probs = outputs.detach().float()
            preds = (probs > 0.5).float()
            
            all_probs.extend(probs.view(-1).cpu().numpy())
            all_preds.extend(preds.view(-1).cpu().numpy())
            all_labels.extend(y.view(-1).cpu().numpy())
            
    epoch_loss = running_loss / len(dataloader.dataset) if len(dataloader.dataset) > 0 else 0.0
    
    if len(all_labels) == 0:
        return epoch_loss, 0.0, 0.0, 0.0, 0.0, 0.0
        
    acc, prec, rec, f1, auc_metric = calculate_metrics(all_labels, all_preds, all_probs)
    return epoch_loss, acc, prec, rec, f1, auc_metric

# ==========================================
# MAIN EXECUTION
# ==========================================
def main():
    print(f"Using device: {DEVICE}")
    
   
    seed = 42
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed) 
        
    # Force deterministic algorithms for CuDNN to prevent varying results
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
   

    all_files = sorted(glob.glob(os.path.join(PROCESSED_DIR, "*_spec.npy")))
    
    
    if not all_files:
        print(f"No .npy files found in {PROCESSED_DIR}. Run preprocess_v2.py first.")
        return

    # SUBSET THE FILES TO REDUCE TOTAL EEG EPOCHS FOR A FASTER DEMO
    # Since all_files is now sorted, this random subset will be identical across runs
    np.random.shuffle(all_files)
    all_files = all_files[:150]

    print(f"Found {len(all_files)} files (subset for faster demonstration).")
    print("WARNING: EXECUTING FLAWED EPOCH-WISE SPLIT (SUBJECT IDENTITY LEAKAGE)\n")
    
    print("Extracting global epoch index from files (this will take a few seconds)...")
    all_samples = []
    
    for path in all_files:
        try:
            data_dict = np.load(path, allow_pickle=True).item()
            num_epochs = data_dict['data'].shape[0]
            label = data_dict['label']
            for i in range(num_epochs):
                all_samples.append((path, i, label))
        except Exception as e:
            print(f"Error loading {path}: {e}")

    if len(all_samples) == 0:
        print("ERROR: Could not load any epochs. Check your preprocessing output.")
        return

    # THE Epoch- Wise SPLIT: Shuffle ALL epochs globally using the locked seed
    train_samples, val_samples = train_test_split(all_samples, test_size=0.2, random_state=seed)

    print(f"Total Training Epochs: {len(train_samples)}")
    print(f"Total Validation Epochs: {len(val_samples)}\n")

    train_dataset = GlobalLeakageDataset(train_samples)
    val_dataset = GlobalLeakageDataset(val_samples)

    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=0, pin_memory=True)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=0, pin_memory=True)
    
    print("Initializing Spatial-Attention Spectrogram ResNet (v2)...")
    model = SpectrogramResNet(num_classes=1, num_electrodes=64).to(DEVICE)
    
    criterion = nn.BCELoss() 
    optimizer = optim.AdamW(model.parameters(), lr=LEARNING_RATE, weight_decay=WEIGHT_DECAY)
    
    scaler = torch.amp.GradScaler('cuda', enabled=(DEVICE.type == 'cuda'))
    
    history_train_acc = []
    history_val_acc = []
    
    for epoch in range(EPOCHS):
        epoch_num = epoch + 1
        print(f"--- Epoch [{epoch_num}/{EPOCHS}] ---")
        
        t_loss, t_acc, t_prec, t_rec, t_f1, t_auc = run_epoch(
            model, train_loader, criterion, optimizer, scaler, is_train=True)
        print_metrics("Train", t_loss, t_acc, t_prec, t_rec, t_f1, t_auc)
        
        history_train_acc.append(t_acc)
        
        v_loss, v_acc, v_prec, v_rec, v_f1, v_auc = run_epoch(
            model, val_loader, criterion, optimizer, scaler, is_train=False)
        print_metrics("Val  ", v_loss, v_acc, v_prec, v_rec, v_f1, v_auc)
        
        history_val_acc.append(v_acc)
        
    print("\nTraining Complete!")

    print("\nGenerating Accuracy Curve...")
    plt.figure(figsize=(8, 5))
    epochs_range = range(1, EPOCHS + 1)
    
    plt.plot(epochs_range, history_train_acc, linestyle='--', marker='o', color='#1f77b4', label='Train')
    plt.plot(epochs_range, history_val_acc, linestyle='--', marker='o', color='#ff7f0e', label='Valid')
    
    plt.title('Training and validation Accuracy of Proposed Model Using EEG Signals')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.legend(loc='upper left')
    plt.tight_layout()
    
    acc_plot_filename = "accuracy_curve.png"
    plt.savefig(acc_plot_filename, dpi=300)
    print(f"Accuracy curve successfully saved as '{acc_plot_filename}'")
    plt.close()

    print("\nEvaluating final validation set for plots...")
    model.eval()
    all_preds, all_probs, all_labels = [], [], []
    with torch.no_grad():
        for x, y in val_loader:
            x = x.to(DEVICE, non_blocking=True)
            y = y.to(DEVICE, non_blocking=True)
            with torch.amp.autocast('cuda', enabled=(DEVICE.type == 'cuda')):
                outputs = model(x)
            probs = outputs.detach().float()
            preds = (probs > 0.5).float()
            all_probs.extend(probs.view(-1).cpu().numpy())
            all_preds.extend(preds.view(-1).cpu().numpy())
            all_labels.extend(y.view(-1).cpu().numpy())
            
    cm = confusion_matrix(all_labels, all_preds)
    fpr, tpr, _ = roc_curve(all_labels, all_probs)
    roc_auc_val = auc(fpr, tpr)
    
    print("\nFinal Validation Confusion Matrix:")
    print(cm)
    
    fig, axs = plt.subplots(1, 2, figsize=(12, 5))
    
    cax = axs[0].matshow(cm, cmap=plt.cm.Blues, alpha=0.8)
    fig.colorbar(cax, ax=axs[0])
    for (i, j), val in np.ndenumerate(cm):
        axs[0].text(j, i, f'{val}', ha='center', va='center', fontsize=12)
    axs[0].set_title("Confusion Matrix")
    axs[0].set_xlabel("Predicted Label")
    axs[0].set_ylabel("True Label")
    axs[0].set_xticks([0, 1])
    axs[0].set_yticks([0, 1])
    axs[0].set_xticklabels(['TD (0)', 'ASD (1)'])
    axs[0].set_yticklabels(['TD (0)', 'ASD (1)'])
    axs[0].xaxis.set_ticks_position('bottom')
    
    axs[1].plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (AUC = {roc_auc_val:.4f})')
    axs[1].plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    axs[1].set_xlim([0.0, 1.0])
    axs[1].set_ylim([0.0, 1.05])
    axs[1].set_xlabel('False Positive Rate')
    axs[1].set_ylabel('True Positive Rate')
    axs[1].set_title('Receiver Operating Characteristic (ROC)')
    axs[1].legend(loc="lower right")
    
    plt.tight_layout()
    plt.show()  

if __name__ == "__main__":
    main()