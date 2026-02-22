"""Phone detection dataset with augmentations.

Usage::

    from training.dataset import PhoneDataset
    ds = PhoneDataset("dataset/phone/train", train=True)
"""

import os

from PIL import Image
from torch.utils.data import Dataset
from torchvision import transforms


def get_train_transforms(input_size: int = 224) -> transforms.Compose:
    return transforms.Compose([
        transforms.RandomResizedCrop(input_size, scale=(0.8, 1.0)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(15),
        transforms.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.2, hue=0.1),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])


def get_val_transforms(input_size: int = 224) -> transforms.Compose:
    return transforms.Compose([
        transforms.Resize(int(input_size * 1.14)),
        transforms.CenterCrop(input_size),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])


class PhoneDataset(Dataset):
    """Binary dataset: ``phone/`` (label 1) vs ``no_phone/`` (label 0).

    Parameters
    ----------
    root : str
        Directory containing ``phone/`` and ``no_phone/`` subdirectories.
    train : bool
        If ``True`` use training augmentations, otherwise validation transforms.
    input_size : int
        Spatial dimension for the model input.
    """

    def __init__(self, root: str, train: bool = True, input_size: int = 224):
        self.root = root
        self.transform = get_train_transforms(input_size) if train else get_val_transforms(input_size)
        self.samples = []

        for label_name, label_id in [("no_phone", 0), ("phone", 1)]:
            folder = os.path.join(root, label_name)
            if not os.path.isdir(folder):
                continue
            for fname in os.listdir(folder):
                if fname.lower().endswith((".jpg", ".png", ".jpeg")):
                    self.samples.append((os.path.join(folder, fname), label_id))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        path, label = self.samples[idx]
        img = Image.open(path).convert("RGB")
        img = self.transform(img)
        return img, label
