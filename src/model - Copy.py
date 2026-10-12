"""
===========================================================
Project : Kisan Mitra AI
File    : model.py
Author  : Sarvesh Kumar
Purpose : Create EfficientNet-B0 model.
===========================================================
"""

import torch.nn as nn

from torchvision.models import (
    efficientnet_b0,
    EfficientNet_B0_Weights
)

from config import NUM_CLASSES


def build_model():

    # Load pretrained EfficientNet-B0
    model = efficientnet_b0(
        weights=EfficientNet_B0_Weights.DEFAULT
    )

    # Freeze the pretrained feature extractor
    # This makes training much faster on CPU.
    for param in model.features.parameters():
        param.requires_grad = False

    # Get the number of input features
    # before replacing the classifier.
    in_features = model.classifier[1].in_features

    # Replace the original classifier
    # Only this classifier will be trained.
    model.classifier[1] = nn.Linear(
        in_features,
        NUM_CLASSES
    )

    return model