"""MobileNetV2 binary classifier for phone detection.

Usage::

    from training.model import build_model
    model = build_model(freeze_backbone=True)
"""

import torch.nn as nn
from torchvision import models


def build_model(freeze_backbone: bool = True) -> nn.Module:
    """Return a MobileNetV2 with a single-output head.

    Parameters
    ----------
    freeze_backbone : bool
        If ``True``, freeze all backbone parameters (only train the head).
    """
    model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.IMAGENET1K_V1)

    if freeze_backbone:
        for param in model.features.parameters():
            param.requires_grad = False

    # Replace classifier: 1280 -> 1 (binary, trained with BCEWithLogitsLoss)
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.2),
        nn.Linear(model.last_channel, 1),
    )

    return model


def unfreeze_last_n_blocks(model: nn.Module, n: int = 4):
    """Unfreeze the last *n* inverted-residual blocks of MobileNetV2."""
    blocks = list(model.features.children())
    for block in blocks[-n:]:
        for param in block.parameters():
            param.requires_grad = True
