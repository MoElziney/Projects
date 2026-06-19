import torch
import cv2
import numpy as np
from torchvision import transforms
from pytorch_grad_cam import GradCAM
from pytorch_grad_cam.utils.image import show_cam_on_image
from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget


def reshape_transform(tensor, height=14, width=14):
    # If the layer outputs a 4D tensor, it's a CNN (VGG/ResNet).
    # CNN feature maps do not require reshaping for Grad-CAM
    if len(tensor.shape) == 4:
        return tensor
        
    # Keeps original core logic perfectly intact for DeiT models
    result = tensor[:, 2:, :].reshape(tensor.size(0), height, width, tensor.size(2))
    result = result.transpose(2, 3).transpose(1, 2)
    return result


def generate_heatmap(model, batch, image_path=r"D:\Datasets\archive\AutismDataset\test\Non_Autistic\Non_Autistic.0.jpg"):
    model.eval()
    
    #
    target_layers = model.get_target_layer()

    # 3. Load the image for the background
    rgb_img = cv2.imread(image_path, 1)[:, :, ::-1] 
    rgb_img = cv2.resize(rgb_img, (224, 224)) 
    rgb_img_float = np.float32(rgb_img) / 255.0

    # 4. Initialize GradCAM
    cam = GradCAM(
        model=model, 
        target_layers=target_layers, 
        
        reshape_transform=lambda tensor: reshape_transform(tensor, height=14, width=14)
    )

    # 5. Generate Heatmap (Targeting class 1 - Autistic)
    targets = [ClassifierOutputTarget(1)] 
    
    print("Generating XAI Heatmap...")
    
    
    with torch.enable_grad():
        
        grayscale_cam = cam(input_tensor=batch[0], targets=targets) 
        
    grayscale_cam = grayscale_cam[0, :]

    # 6. Save Image
    visualization = show_cam_on_image(rgb_img_float, grayscale_cam, use_rgb=True)
    output_path = "xai_result_384.jpg"
    cv2.imwrite(output_path, visualization[:, :, ::-1])
    print(f"Success! Heatmap saved to {output_path}")