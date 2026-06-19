import torch
import torch.nn as nn
from timm.models import create_model
from timm.models.vision_transformer import VisionTransformer

class ViTASD(nn.Module):
    def __init__(self, backbone: str, num_classes, drop_rate, drop_path_rate, input_size):
        super(ViTASD, self).__init__()
        self.num_classes = num_classes
        self.input_size = input_size

        # Core Logic Preservation: Dynamically filter arguments based on model type
        kwargs = {
            "model_name": backbone,
            "pretrained": True,
            "num_classes": num_classes,
            "drop_rate": drop_rate
        }
        
        # Only pass Transformer-specific arguments if using a ViT/DeiT model
        if "deit" in backbone.lower() or "vit" in backbone.lower():
            kwargs["drop_path_rate"] = drop_path_rate
            kwargs["img_size"] = input_size
            
        self.backbone = create_model(**kwargs)

    def forward(self, x):
        return self.backbone(x)

    def get_target_layer(self):
        # Automatically detects the correct target layer for Grad-CAM
        
        # 1. Vision Transformers (DeiT)
        if hasattr(self.backbone, 'patch_embed'): 
            return [self.backbone.blocks[-1].norm1]
            
        # 2. GhostNet explicitly (Fixes the solid blue square bug!)
        elif "ghostnet" in self.backbone.__class__.__name__.lower():
            # Grabs the final spatial GhostBottleneck block before it gets pooled
            return [self.backbone.blocks[-1]]
            
        # 3. MobileNetV2 / EfficientNet
        elif hasattr(self.backbone, 'conv_head'):
            return [self.backbone.conv_head]
            
        # 4. VGG Architectures
        elif hasattr(self.backbone, 'features'): 
            return [self.backbone.features[-1]]
            
        # 5. ResNet Architectures
        elif hasattr(self.backbone, 'layer4'): 
            return [self.backbone.layer4[-1]]
            
        # 6. Universal Fallback for standard sequential CNNs
        else:
            return [list(self.backbone.children())[-2]]