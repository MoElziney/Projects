import torch
import matplotlib.pyplot as plt
import seaborn as sns
from datasets import AutismDatasetModule
from models import ViTASD
from lib.pos_embed import interpolate_pos_embed
from pytorch_lightning import LightningModule
from pytorch_lightning.cli import LightningCLI
from pytorch_lightning.utilities.types import STEP_OUTPUT
from pytorch_lightning.callbacks import Callback
from torchmetrics import Accuracy, ConfusionMatrix, Precision, Recall, F1Score, ROC, AUROC
from torch.optim import Optimizer
from explain import generate_heatmap
from timm.data import Mixup
from timm.models import create_model
from timm.optim import create_optimizer_v2
from timm.scheduler import create_scheduler
from timm.scheduler.scheduler import Scheduler
from pathlib import Path
from typing import Optional
import os


class ViTASDLM(LightningModule):
    def __init__(self,
                 batch_size: int = 256,
                 num_classes: int = 2,
                 epochs: int = 300,
                 attn_only: bool = False,
                 smoothing: float = 0.0,  # Label smoothing
                 vis_path: str = "./runs/vis",

                 # Model parameters
                 model: str = "deit_small_distilled_patch16_224",  # Name of model to train
                 input_size: int = 224,  # images input size
                 drop: float = 0.0,  # Dropout rate
                 drop_path: float = 0.05,  # Drop path rate
                 pretrain_path: str = "",

                 # Optimizer parameters
                 opt: str = "adamw",
                 weight_decay: float = 0.05,

                 # Learning rate schedule parameters
                 sched: str = "cosine",
                 lr: float = 1e-4,
                 warmup_lr: float = 1e-6,
                 min_lr: float = 1e-6,
                 warmup_epochs: int = 5,  # epochs to warmup LR, if scheduler supports
                 cooldown_epochs: int = 0,  # epochs to cooldown LR at min_lr, after cyclic schedule ends

                 # Mixup parameters
                 mixup: float = 0.8,  # mixup alpha, mixup enabled if > 0
                 cutmix: float = 1.0,  # cutmix alpha, cutmix enabled if > 0.
                 mixup_prob: float = 1.0,  # Prob of performing mixup or cutmix when either/both is enabled
                 mixup_switch_prob: float = 0.5,  # Prob of switching to cutmix when both mixup and cutmix enabled
                 mixup_mode: str = "batch",  # How to apply mixup/cutmix params. Per "batch", "pair", or "elem"
                 ):

        super(ViTASDLM, self).__init__()
        self.save_hyperparameters()

        self.model: torch.nn.Module = ViTASD(
            self.hparams.model,
            num_classes=self.hparams.num_classes,
            drop_rate=self.hparams.drop,
            drop_path_rate=self.hparams.drop_path,
            input_size=self.hparams.input_size
        )
        
        if os.path.exists(pretrain_path):
            self._load_pretrained(pretrain_path)

        self._init_mixup()
        self._init_frozen_params()
        self.train_criterion = torch.nn.CrossEntropyLoss()
        self.valid_criterion = torch.nn.CrossEntropyLoss()
        
        # Define the task type for the new torchmetrics version
        task_type = "binary"
        
        # Training Metrics
        self.train_acc = Accuracy(task=task_type, num_classes=self.hparams.num_classes)
        self.train_precision = Precision(task=task_type, num_classes=self.hparams.num_classes, average='macro')
        self.train_recall = Recall(task=task_type, num_classes=self.hparams.num_classes, average='macro')
        self.train_f1 = F1Score(task=task_type, num_classes=self.hparams.num_classes, average='macro')

        # Validation Metrics
        self.valid_acc = Accuracy(task=task_type, num_classes=self.hparams.num_classes)
        self.valid_precision = Precision(task=task_type, num_classes=self.hparams.num_classes, average='macro')
        self.valid_recall = Recall(task=task_type, num_classes=self.hparams.num_classes, average='macro')
        self.valid_f1 = F1Score(task=task_type, num_classes=self.hparams.num_classes, average='macro')
        
        # Test Metrics
        self.test_acc = Accuracy(task=task_type, num_classes=self.hparams.num_classes)
        self.test_precision = Precision(task=task_type, num_classes=self.hparams.num_classes, average='macro')
        self.test_recall = Recall(task=task_type, num_classes=self.hparams.num_classes, average='macro')
        self.test_f1 = F1Score(task=task_type, num_classes=self.hparams.num_classes, average='macro')
        
        # Added ROC and AUROC initialization
        self.roc = ROC(task=task_type)
        self.auroc = AUROC(task=task_type)
        
        self.confusion_matrix = ConfusionMatrix(task=task_type, num_classes=self.hparams.num_classes, normalize='none')

    def _init_mixup(self):
        self.mixup_fn = None
        mixup_active = self.hparams.mixup > 0 or self.hparams.cutmix > 0.
        if mixup_active:
            self.mixup_fn = Mixup(
                mixup_alpha=self.hparams.mixup,
                cutmix_alpha=self.hparams.cutmix,
                cutmix_minmax=None,
                prob=self.hparams.mixup_prob,
                switch_prob=self.hparams.mixup_switch_prob,
                mode=self.hparams.mixup_mode,
                label_smoothing=self.hparams.smoothing,
                num_classes=self.hparams.num_classes
            )
    
    def _load_pretrained(self, pretrain_path):
        checkpoint = torch.load(pretrain_path)
        print("Load pre-trained checkpoint from: %s" % pretrain_path)
        checkpoint_model = checkpoint['state_dict']
        state_dict = self.model.state_dict()
        for k in ['backbone.head.weight', 'backbone.head.bias']:
            if k in checkpoint_model and checkpoint_model[k].shape != state_dict[k].shape:
                print(f"Removing key {k} from pretrained checkpoint")
                del checkpoint_model[k]
        # interpolate position embedding
        interpolate_pos_embed(self.model, checkpoint_model)
        self.model.load_state_dict(checkpoint_model, strict=False)
        

    def _init_frozen_params(self):
        if self.hparams.attn_only:
            for name_p, p in self.model.named_parameters():
                if '.attn.' in name_p:
                    p.requires_grad = True
                else:
                    p.requires_grad = False

            self.model.backbone.head.weight.requires_grad = True
            self.model.backbone.head.bias.requires_grad = True
            self.model.backbone.pos_embed.requires_grad = True
            for p in self.model.backbone.patch_embed.parameters():
                p.requires_grad = True

    def forward(self, x):
        return self.model(x)

    def training_step(self, batch, batch_idx) -> STEP_OUTPUT:
        samples, targets_orig = batch
        
        # Apply mixup if enabled
        if self.mixup_fn is not None:
            samples, targets_mixup = self.mixup_fn(samples, targets_orig)
            outputs = self.forward(samples)
            loss = self.train_criterion(outputs, targets_mixup)
        else:
            outputs = self.forward(samples)
            loss = self.train_criterion(outputs, targets_orig)

        preds = torch.argmax(outputs, dim=1)

        self.train_acc.update(preds, targets_orig)
        self.train_precision.update(preds, targets_orig)
        self.train_recall.update(preds, targets_orig)
        self.train_f1.update(preds, targets_orig)

        self.log('Loss/train', loss.item(), sync_dist=True)
        self.log('Accuracy/train', self.train_acc, on_step=False, on_epoch=True, sync_dist=True)
        self.log('Precision/train', self.train_precision, on_step=False, on_epoch=True, sync_dist=True)
        self.log('Recall/train', self.train_recall, on_step=False, on_epoch=True, sync_dist=True)
        self.log('F1/train', self.train_f1, on_step=False, on_epoch=True, sync_dist=True)
        
        return loss

    def validation_step(self, batch, batch_idx) -> STEP_OUTPUT:
        samples, targets = batch
        outputs = self.forward(samples)
        loss = self.valid_criterion(outputs, targets)
        
        preds = torch.argmax(outputs, dim=1)
        
        self.valid_acc.update(preds, targets)
        self.valid_precision.update(preds, targets)
        self.valid_recall.update(preds, targets)
        self.valid_f1.update(preds, targets)

        self.log("Loss/val", loss.item(), sync_dist=True)
        self.log("Accuracy/val", self.valid_acc, on_step=False, on_epoch=True, sync_dist=True)
        self.log("Precision/val", self.valid_precision, on_step=False, on_epoch=True, sync_dist=True)
        self.log("Recall/val", self.valid_recall, on_step=False, on_epoch=True, sync_dist=True)
        self.log("F1/val", self.valid_f1, on_step=False, on_epoch=True, sync_dist=True)
        
        return loss
    

    def test_step(self, batch, batch_idx) -> Optional[STEP_OUTPUT]:
        samples, targets = batch
        outputs = self.forward(samples)
        
        preds = torch.argmax(outputs, dim=1)
        
        # Isolate the logits/probabilities for the positive class (Class 1) for ROC
        pos_class_probs = outputs[:, 1]
        
        # Update ROC and AUROC using continuous probabilities
        self.roc.update(pos_class_probs, targets)
        self.auroc.update(pos_class_probs, targets)
        
        # Update other metrics using hard predictions
        self.confusion_matrix.update(preds, targets)
        self.test_acc.update(preds, targets)
        self.test_precision.update(preds, targets)
        self.test_recall.update(preds, targets)
        self.test_f1.update(preds, targets)
        
        # Log metrics
        self.log("Accuracy/test", self.test_acc, on_epoch=True, sync_dist=True)
        self.log("Precision/test", self.test_precision, on_epoch=True, sync_dist=True)
        self.log("Recall/test", self.test_recall, on_epoch=True, sync_dist=True)
        self.log("F1/test", self.test_f1, on_epoch=True, sync_dist=True)
        self.log("AUROC/test", self.auroc, on_epoch=True, sync_dist=True)

    def predict_step(self, batch, batch_idx, dataloader_idx=0):
        # 1. Unpack the list into your images (samples) and your labels (targets)
        samples, targets = batch
        
        # 2. Generate the heatmap for the very first batch
        if batch_idx == 0:
            generate_heatmap(self.model, batch)
        
        # 3. Only pass the 'samples' (the image tensors) to the model
        return self.forward(samples)
    
    def on_train_epoch_end(self) -> None:
        opt = self.optimizers()
        self.log("LR", opt.param_groups[0]["lr"], on_epoch=True, sync_dist=True)

    def on_test_end(self) -> None:
        self.visualize_confusion_matrix()
        self.visualize_roc_curve()  

    def configure_optimizers(self):
        optimizer = create_optimizer_v2(
            self.model,
            opt=self.hparams.opt,
            lr=self.hparams.lr,
            weight_decay=self.hparams.weight_decay,
        )
        scheduler, _ = create_scheduler(self.hparams, optimizer)
        return [optimizer], [{"scheduler": scheduler, "interval": "epoch"}]

    def lr_scheduler_step(self, scheduler, *args, **kwargs) -> None:
        scheduler.step(epoch=self.current_epoch)  

    def visualize_confusion_matrix(self):
        cf_matrix = self.confusion_matrix.compute().cpu()
        categories = ['Non-Autistic', 'Autistic']
        fig, ax = plt.subplots(1)
        
        sns.heatmap(cf_matrix, annot=True, cmap='Blues', fmt='d', xticklabels=categories, yticklabels=categories)
        ax.set_xlabel('Predicted')
        ax.set_ylabel('True Label')
        vis_path = Path(self.hparams.vis_path)
        vis_path.mkdir(parents=True, exist_ok=True)
        fig.savefig(str(vis_path / "cf_matrix.png"), dpi=200)
        
    def visualize_roc_curve(self):
        fpr, tpr, thresholds = self.roc.compute()
        auroc_val = self.auroc.compute().item()
        
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # Plot the ROC curve
        ax.plot(fpr.cpu().numpy(), tpr.cpu().numpy(), color='darkorange', lw=2, label=f'ROC Curve (AUROC = {auroc_val:.3f})')
        
        # Plot the 50/50 random guess line
        ax.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
        
        ax.set_xlabel('False Positive Rate')
        ax.set_ylabel('True Positive Rate')
        ax.set_title('Receiver Operating Characteristic (ROC)')
        ax.legend(loc="lower right")
        
        vis_path = Path(self.hparams.vis_path)
        vis_path.mkdir(parents=True, exist_ok=True)
        fig.savefig(str(vis_path / "roc_curve.png"), dpi=200)
    

def cli_main():
    cli = LightningCLI(ViTASDLM,
                       AutismDatasetModule,
                       seed_everything_default=42,
                       trainer_defaults=dict(accelerator='gpu', devices=1),
                       save_config_kwargs={"overwrite": True},
    )


if __name__ == "__main__":
    cli_main()