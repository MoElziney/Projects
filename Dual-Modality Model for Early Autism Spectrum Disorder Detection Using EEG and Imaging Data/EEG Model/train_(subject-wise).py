import os
import glob
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.model_selection import GroupKFold
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix, roc_curve
from collections import Counter
import random
import matplotlib.pyplot as plt

from model_v2 import SpectrogramResNetV3

# --- Configuration ---
PROCESSED_DIR = "D:/ds006780-download/processed_data_v2"
BATCH_SIZE = 32
EPOCHS = 10
LEARNING_RATE = 1e-4 


WEIGHT_DECAY = 1e-2 
PATIENCE = 10 
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def calculate_pos_weight(file_paths):
    print("Calculating class weights (scanning training files)...")
    neg_count = 0
    pos_count = 0
    for path in file_paths:
        try:
            data_dict = np.load(path, allow_pickle=True).item()
            label = data_dict['label']
            num_epochs = data_dict['data'].shape[0]
            if label == 0:
                neg_count += num_epochs
            else:
                pos_count += num_epochs
        except Exception:
            pass
            
    if pos_count == 0: return torch.tensor(1.0)
    return torch.tensor(neg_count / pos_count, dtype=torch.float32)

def run_epoch_lazy(model, file_paths, criterion, optimizer, is_train=True, fold=1, epoch=1, save_plots=False):
    if is_train:
        model.train()
        random.shuffle(file_paths)
    else:
        model.eval()
        
    running_loss = 0.0
    total_samples = 0
    all_preds, all_probs, all_labels = [], [], []

    with torch.set_grad_enabled(is_train):
        for path in file_paths:
            try:
                data_dict = np.load(path, allow_pickle=True).item()
                data = data_dict['data']          
                label = data_dict['label']        
                
                num_epochs = data.shape[0]
                indices = np.arange(num_epochs)
                
                    
                
                for i in range(0, num_epochs, BATCH_SIZE):
                    batch_idx = indices[i:i+BATCH_SIZE]
                    
                    x = torch.tensor(data[batch_idx], dtype=torch.float32).to(DEVICE)
                    y = torch.tensor([label] * len(batch_idx), dtype=torch.float32).unsqueeze(1).to(DEVICE)
                    
                    # DATA AUGMENTATION (Gaussian Noise Injection)
                    # This scrambles the exact pixels slightly so the model cannot memorize subjects
                    if is_train:
                        noise = torch.randn_like(x) * 0.2  # 20% random noise
                        x = x + noise
                    
                    if is_train: optimizer.zero_grad()
                    
                    outputs = model(x)
                    loss = criterion(outputs, y)
                    
                    if is_train:
                        loss.backward()
                        optimizer.step()
                    
                    running_loss += loss.item() * x.size(0)
                    total_samples += x.size(0)
                    
                    probs = outputs.detach().cpu().numpy()
                    preds = (outputs.detach() > 0.5).float().cpu().numpy()
                    
                    all_probs.extend(probs)
                    all_preds.extend(preds)
                    all_labels.extend(y.cpu().numpy())
                    
            except Exception as e:
                pass 
                
    epoch_loss = running_loss / total_samples if total_samples > 0 else 0.0
    
    try:
        acc = accuracy_score(all_labels, all_preds)
        prec = precision_score(all_labels, all_preds, zero_division=0)
        rec = recall_score(all_labels, all_preds, zero_division=0)
        f1 = f1_score(all_labels, all_preds, zero_division=0)
        auc = roc_auc_score(all_labels, all_probs)
        cm = confusion_matrix(all_labels, all_preds)
    except ValueError:
        acc = accuracy_score(all_labels, all_preds)
        prec, rec, f1, auc = 0.0, 0.0, 0.0, 0.0
        cm = np.zeros((2,2))

    if save_plots and not is_train and np.unique(all_labels).size > 1:
        fpr, tpr, _ = roc_curve(all_labels, all_probs)
        plt.figure()
        plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (area = {auc:.2f})')
        plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title(f'ROC Curve V3 - Fold {fold}')
        plt.legend(loc="lower right")
        plt.savefig(f"ROC_Curve_V3_Fold_{fold}.png")
        plt.close()

    return epoch_loss, acc, prec, rec, f1, auc, cm

def print_metrics(phase, loss, acc, prec, rec, f1, auc, cm):
    print(f"  {phase} -> Loss: {loss:.4f} | Acc: {acc:.4f} | Prec: {prec:.4f} | Rec: {rec:.4f} | F1: {f1:.4f} | AUC: {auc:.4f}")
    if cm.shape == (2,2):
        print(f"       Confusion Matrix: TN={cm[0,0]} FP={cm[0,1]} FN={cm[1,0]} TP={cm[1,1]}")

def main():
    print(f"Using device: {DEVICE}")
    all_files = glob.glob(os.path.join(PROCESSED_DIR, "*_spec.npy"))
    if not all_files:
        print(f"No .npy files found in {PROCESSED_DIR}. Run preprocess_v2.py first.")
        return

    print(f"Found {len(all_files)} processed spectrogram files ready for V3 training.")

    file_subjects = np.array([os.path.basename(f).split('_')[0] for f in all_files])
    all_files = np.array(all_files)

    unique_subjects = len(np.unique(file_subjects))
    k_folds = min(5, unique_subjects)
    
    if k_folds < 2:
        print(f"Only {unique_subjects} subject(s) found. Need at least 2 for K-Fold CV.")
        return

    gkf = GroupKFold(n_splits=k_folds)
    fold_metrics = []

    for fold, (train_idx, val_idx) in enumerate(gkf.split(all_files, groups=file_subjects)):
        fold_num = fold + 1
        print(f"\n{'='*50}\nStarting Fold {fold_num}/{k_folds} (V3 Regularized)\n{'='*50}")
        
        train_files = list(all_files[train_idx])
        val_files = list(all_files[val_idx])
        
        pos_weight = calculate_pos_weight(train_files).to(DEVICE)
        print(f"Calculated Positive Class Weight: {pos_weight.item():.2f}")
        
        model = SpectrogramResNetV3(num_classes=1, num_electrodes=64, dropout_rate=0.5).to(DEVICE)
        
        base_criterion = nn.BCELoss(reduction='none')
        
        def weighted_criterion(outputs, targets):
            loss = base_criterion(outputs, targets)
            weight_tensor = torch.where(targets == 1.0, pos_weight, torch.tensor(1.0).to(DEVICE))
            return (loss * weight_tensor).mean()

        optimizer = optim.AdamW(model.parameters(), lr=LEARNING_RATE, weight_decay=WEIGHT_DECAY)
        
        best_val_f1 = 0.0
        epochs_no_improve = 0
        
        for epoch in range(EPOCHS):
            epoch_num = epoch + 1
            print(f"Epoch [{epoch_num}/{EPOCHS}]")
            
            t_loss, t_acc, t_prec, t_rec, t_f1, t_auc, t_cm = run_epoch_lazy(
                model, train_files, weighted_criterion, optimizer, is_train=True, fold=fold_num, epoch=epoch_num)
            print_metrics("Train", t_loss, t_acc, t_prec, t_rec, t_f1, t_auc, t_cm)
            
            v_loss, v_acc, v_prec, v_rec, v_f1, v_auc, v_cm = run_epoch_lazy(
                model, val_files, weighted_criterion, optimizer, is_train=False, fold=fold_num, epoch=epoch_num)
            print_metrics("Val  ", v_loss, v_acc, v_prec, v_rec, v_f1, v_auc, v_cm)
            
            if v_f1 > best_val_f1:
                best_val_f1 = v_f1
                epochs_no_improve = 0
                torch.save(model.state_dict(), f"best_model_v3_fold_{fold_num}.pt")
                _, _, _, _, _, _, _ = run_epoch_lazy(
                    model, val_files, weighted_criterion, optimizer, is_train=False, fold=fold_num, epoch=epoch_num, save_plots=True)
            else:
                epochs_no_improve += 1
                
            if epochs_no_improve >= PATIENCE:
                print(f"Early stopping triggered at epoch {epoch_num}")
                break
                
        print(f"-> Fold {fold_num} Best Validation F1: {best_val_f1:.4f}")
        fold_metrics.append(best_val_f1)
        
    print(f"\n{'='*50}\nCross-Validation Complete!\n{'='*50}")
    print(f"Average Validation F1-Score: {np.mean(fold_metrics):.4f} +/- {np.std(fold_metrics):.4f}")

if __name__ == "__main__":
    main()