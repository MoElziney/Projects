import torch
import torch.nn as nn
import torch.nn.functional as F

class SpatialAttention(nn.Module):
    """
    Squeeze-and-Excitation (SE) block adapted for Spatial Attention over EEG channels.
    """
    def __init__(self, num_channels, reduction_ratio=8):
        super(SpatialAttention, self).__init__()
        self.avg_pool = nn.AdaptiveAvgPool2d(1)
        
        self.fc = nn.Sequential(
            nn.Linear(num_channels, num_channels // reduction_ratio, bias=False),
            nn.ReLU(inplace=True),
            nn.Linear(num_channels // reduction_ratio, num_channels, bias=False),
            nn.Sigmoid()
        )

    def forward(self, x):
        b, c, _, _ = x.size()
        y = self.avg_pool(x).view(b, c)
        y = self.fc(y).view(b, c, 1, 1)
        return x * y.expand_as(x)

class ResBlock(nn.Module):
    """
    Standard 2D Residual Block for spectrogram analysis.
    """
    def __init__(self, in_channels, out_channels, stride=1):
        super(ResBlock, self).__init__()
        self.conv1 = nn.Conv2d(in_channels, out_channels, kernel_size=3, stride=stride, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(out_channels)
        self.relu = nn.ReLU(inplace=True)
        self.conv2 = nn.Conv2d(out_channels, out_channels, kernel_size=3, stride=1, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(out_channels)
        
        self.shortcut = nn.Sequential()
        if stride != 1 or in_channels != out_channels:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_channels, out_channels, kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm2d(out_channels)
            )

    def forward(self, x):
        residual = self.shortcut(x)
        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)
        out = self.conv2(out)
        out = self.bn2(out)
        out += residual
        out = self.relu(out)
        return out

class SpectrogramResNetV3(nn.Module):
    
    
    def __init__(self, num_classes=1, num_electrodes=64, dropout_rate=0.5):
        super(SpectrogramResNetV3, self).__init__()
        
        self.spatial_attention = SpatialAttention(num_channels=num_electrodes)
        
        # Reduced initial filters from 32 to 16
        self.initial_conv = nn.Sequential(
            nn.Conv2d(num_electrodes, 16, kernel_size=3, stride=1, padding=1, bias=False),
            nn.BatchNorm2d(16),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2)
        )
        
        # Simplified Residual Blocks (Max 64 channels instead of 128)
        self.layer1 = ResBlock(16, 16, stride=1)
        self.layer2 = ResBlock(16, 32, stride=2)
        self.layer3 = ResBlock(32, 64, stride=2)
        
        self.gap = nn.AdaptiveAvgPool2d((1, 1))
        
        # Heavy Dropout added before the final classification head
        self.dropout = nn.Dropout(p=dropout_rate)
        self.fc = nn.Linear(64, num_classes)

    def forward(self, x):
        x = self.spatial_attention(x)
        
        x = self.initial_conv(x)
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        
        x = self.gap(x)
        x = x.view(x.size(0), -1)
        
        # Apply Dropout
        x = self.dropout(x)
        
        out = self.fc(x)
        return torch.sigmoid(out)

if __name__ == "__main__":
    print("Testing Regularized V3 Architecture...")
    dummy_spec = torch.randn(8, 64, 26, 33)
    model = SpectrogramResNetV3()
    output = model(dummy_spec)
    print(f"Output Shape: {output.shape} -> Test Passed!")