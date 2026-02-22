"""Evaluate a trained phone detector checkpoint.

Reports accuracy, precision, recall, F1, and sweeps confidence thresholds.

Usage::

    python -m training.evaluate --checkpoint models/best.pth --data-dir dataset/phone/val
"""

import argparse
import os

import torch
import numpy as np
from torch.utils.data import DataLoader
from sklearn.metrics import classification_report, precision_recall_curve

from training.dataset import PhoneDataset
from training.model import build_model


@torch.no_grad()
def collect_predictions(model, loader, device):
    model.eval()
    all_probs, all_labels = [], []

    for images, labels in loader:
        images = images.to(device)
        logits = model(images).squeeze(1)
        probs = torch.sigmoid(logits)
        all_probs.extend(probs.cpu().tolist())
        all_labels.extend(labels.tolist())

    return np.array(all_probs), np.array(all_labels)


def sweep_thresholds(probs, labels):
    """Find the threshold that maximises F1."""
    precision, recall, thresholds = precision_recall_curve(labels, probs)
    # F1 = 2 * P * R / (P + R)
    f1_scores = np.where(
        (precision + recall) > 0,
        2 * precision * recall / (precision + recall),
        0.0,
    )
    best_idx = np.argmax(f1_scores[:-1])  # last entry has no threshold
    return thresholds[best_idx], f1_scores[best_idx]


def main():
    parser = argparse.ArgumentParser(description="Evaluate phone detector")
    parser.add_argument("--checkpoint", required=True, help="Path to .pth checkpoint")
    parser.add_argument("--data-dir", required=True, help="Validation directory (with phone/ and no_phone/)")
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--num-workers", type=int, default=4)
    args = parser.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model = build_model(freeze_backbone=False).to(device)
    model.load_state_dict(torch.load(args.checkpoint, map_location=device, weights_only=True))

    val_ds = PhoneDataset(args.data_dir, train=False)
    val_loader = DataLoader(val_ds, batch_size=args.batch_size, shuffle=False, num_workers=args.num_workers)

    probs, labels = collect_predictions(model, val_loader, device)

    # Classification report at default 0.5 threshold
    preds_05 = (probs >= 0.5).astype(int)
    print("=== Classification Report (threshold=0.5) ===")
    print(classification_report(labels, preds_05, target_names=["no_phone", "phone"]))

    # Threshold sweep
    best_thresh, best_f1 = sweep_thresholds(probs, labels)
    print(f"Best threshold: {best_thresh:.3f} (F1={best_f1:.4f})")

    preds_best = (probs >= best_thresh).astype(int)
    print(f"\n=== Classification Report (threshold={best_thresh:.3f}) ===")
    print(classification_report(labels, preds_best, target_names=["no_phone", "phone"]))


if __name__ == "__main__":
    main()
