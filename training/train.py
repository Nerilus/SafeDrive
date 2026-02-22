"""Two-phase training script for the phone detector.

Phase 1: Backbone frozen, train head only (5 epochs, lr=1e-3).
Phase 2: Last 4 blocks unfrozen, fine-tune (15 epochs, lr=1e-4, cosine).

Usage::

    python -m training.train --data-dir dataset/phone --epochs 20
"""

import argparse
import os

import torch
import torch.nn as nn
from torch.optim import Adam
from torch.optim.lr_scheduler import CosineAnnealingLR
from torch.utils.data import DataLoader
from sklearn.metrics import f1_score
from tqdm import tqdm

from training.dataset import PhoneDataset
from training.model import build_model, unfreeze_last_n_blocks


def train_one_epoch(model, loader, criterion, optimizer, device):
    model.train()
    running_loss = 0.0
    all_preds, all_labels = [], []

    for images, labels in tqdm(loader, desc="Train", leave=False):
        images = images.to(device)
        labels = labels.float().to(device)

        optimizer.zero_grad()
        logits = model(images).squeeze(1)
        loss = criterion(logits, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item() * images.size(0)
        preds = (torch.sigmoid(logits) >= 0.5).long()
        all_preds.extend(preds.cpu().tolist())
        all_labels.extend(labels.long().cpu().tolist())

    epoch_loss = running_loss / len(loader.dataset)
    epoch_f1 = f1_score(all_labels, all_preds)
    return epoch_loss, epoch_f1


@torch.no_grad()
def evaluate(model, loader, criterion, device):
    model.eval()
    running_loss = 0.0
    all_preds, all_labels = [], []

    for images, labels in tqdm(loader, desc="Val", leave=False):
        images = images.to(device)
        labels = labels.float().to(device)

        logits = model(images).squeeze(1)
        loss = criterion(logits, labels)

        running_loss += loss.item() * images.size(0)
        preds = (torch.sigmoid(logits) >= 0.5).long()
        all_preds.extend(preds.cpu().tolist())
        all_labels.extend(labels.long().cpu().tolist())

    epoch_loss = running_loss / len(loader.dataset)
    epoch_f1 = f1_score(all_labels, all_preds)
    return epoch_loss, epoch_f1


def main():
    parser = argparse.ArgumentParser(description="Train phone detector")
    parser.add_argument("--data-dir", required=True, help="Root with train/ and val/ subfolders")
    parser.add_argument("--epochs", type=int, default=20, help="Total epochs (phase 1 + 2)")
    parser.add_argument("--phase1-epochs", type=int, default=5, help="Epochs with frozen backbone")
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--lr1", type=float, default=1e-3, help="LR for phase 1")
    parser.add_argument("--lr2", type=float, default=1e-4, help="LR for phase 2")
    parser.add_argument("--output", default="models/best.pth", help="Output checkpoint path")
    parser.add_argument("--num-workers", type=int, default=4)
    args = parser.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    train_ds = PhoneDataset(os.path.join(args.data_dir, "train"), train=True)
    val_ds = PhoneDataset(os.path.join(args.data_dir, "val"), train=False)
    print(f"Train: {len(train_ds)} | Val: {len(val_ds)}")

    if len(train_ds) == 0:
        print(
            "\nErreur : aucune image trouvee dans le dataset.\n"
            "Preparez vos donnees d'abord :\n"
            "  Option A — State Farm (Kaggle) :\n"
            "    python -m training.prepare_statefarm --src chemin/vers/imgs/train --dst dataset/phone\n"
            "  Option B — Capture webcam :\n"
            "    python -m training.capture_data --label phone --output dataset/phone/train/phone\n"
            "    python -m training.capture_data --label no_phone --output dataset/phone/train/no_phone\n"
        )
        return

    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True, num_workers=args.num_workers, pin_memory=True)
    val_loader = DataLoader(val_ds, batch_size=args.batch_size, shuffle=False, num_workers=args.num_workers, pin_memory=True)

    model = build_model(freeze_backbone=True).to(device)
    criterion = nn.BCEWithLogitsLoss()

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    best_f1 = 0.0

    # ── Phase 1: frozen backbone ──
    optimizer = Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=args.lr1)
    phase2_epochs = args.epochs - args.phase1_epochs

    print("\n=== Phase 1: Backbone frozen ===")
    for epoch in range(1, args.phase1_epochs + 1):
        train_loss, train_f1 = train_one_epoch(model, train_loader, criterion, optimizer, device)
        val_loss, val_f1 = evaluate(model, val_loader, criterion, device)
        print(f"[{epoch}/{args.phase1_epochs}] train_loss={train_loss:.4f} train_f1={train_f1:.4f} | val_loss={val_loss:.4f} val_f1={val_f1:.4f}")
        if val_f1 > best_f1:
            best_f1 = val_f1
            torch.save(model.state_dict(), args.output)
            print(f"  -> Saved best model (F1={best_f1:.4f})")

    # ── Phase 2: fine-tune last blocks ──
    unfreeze_last_n_blocks(model, n=4)
    optimizer = Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=args.lr2)
    scheduler = CosineAnnealingLR(optimizer, T_max=phase2_epochs)

    print(f"\n=== Phase 2: Fine-tuning ({phase2_epochs} epochs) ===")
    for epoch in range(1, phase2_epochs + 1):
        train_loss, train_f1 = train_one_epoch(model, train_loader, criterion, optimizer, device)
        val_loss, val_f1 = evaluate(model, val_loader, criterion, device)
        scheduler.step()
        print(f"[{epoch}/{phase2_epochs}] train_loss={train_loss:.4f} train_f1={train_f1:.4f} | val_loss={val_loss:.4f} val_f1={val_f1:.4f}")
        if val_f1 > best_f1:
            best_f1 = val_f1
            torch.save(model.state_dict(), args.output)
            print(f"  -> Saved best model (F1={best_f1:.4f})")

    print(f"\nDone. Best val F1 = {best_f1:.4f}")
    print(f"Checkpoint saved to {args.output}")


if __name__ == "__main__":
    main()
