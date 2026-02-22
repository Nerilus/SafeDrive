"""Reorganise the State Farm Distracted Driver dataset into binary folders.

Expected input layout (Kaggle download)::

    <src>/
        c0/   # safe driving
        c1/   # texting - right
        c2/   # talking on the phone - right
        c3/   # texting - left
        c4/   # talking on the phone - left
        c5/   # operating the radio
        c6/   # drinking
        c7/   # reaching behind
        c8/   # hair and makeup
        c9/   # talking to passenger

Output layout::

    <dst>/
        phone/      # c1 + c2 + c3 + c4
        no_phone/   # c0 + c5 + c6 + c7 + c8 + c9

A random 80/20 train/val split is also created.

Usage::

    python -m training.prepare_statefarm --src path/to/imgs/train --dst dataset/phone
"""

import argparse
import os
import random
import shutil


PHONE_CLASSES = {"c1", "c2", "c3", "c4"}
NO_PHONE_CLASSES = {"c0", "c5", "c6", "c7", "c8", "c9"}


def prepare(src: str, dst: str, val_ratio: float = 0.2, seed: int = 42):
    if not os.path.isdir(src):
        print(
            f"Erreur : le dossier source n'existe pas : {src}\n\n"
            "Telechargez d'abord le dataset State Farm depuis Kaggle :\n"
            "  https://www.kaggle.com/c/state-farm-distracted-driver-detection/data\n\n"
            "Puis relancez avec le bon chemin, par exemple :\n"
            "  python -m training.prepare_statefarm --src C:\\Users\\vous\\Downloads\\imgs\\train --dst dataset/phone"
        )
        return

    random.seed(seed)

    for split in ("train", "val"):
        for label in ("phone", "no_phone"):
            os.makedirs(os.path.join(dst, split, label), exist_ok=True)

    for cls_dir in sorted(os.listdir(src)):
        cls_path = os.path.join(src, cls_dir)
        if not os.path.isdir(cls_path):
            continue

        if cls_dir in PHONE_CLASSES:
            label = "phone"
        elif cls_dir in NO_PHONE_CLASSES:
            label = "no_phone"
        else:
            continue

        images = [f for f in os.listdir(cls_path) if f.lower().endswith((".jpg", ".png", ".jpeg"))]
        random.shuffle(images)
        split_idx = int(len(images) * (1 - val_ratio))

        for i, fname in enumerate(images):
            split = "train" if i < split_idx else "val"
            src_file = os.path.join(cls_path, fname)
            dst_file = os.path.join(dst, split, label, f"{cls_dir}_{fname}")
            shutil.copy2(src_file, dst_file)

    for split in ("train", "val"):
        for label in ("phone", "no_phone"):
            count = len(os.listdir(os.path.join(dst, split, label)))
            print(f"{split}/{label}: {count} images")


def main():
    parser = argparse.ArgumentParser(description="Prepare State Farm dataset for binary classification")
    parser.add_argument("--src", required=True, help="Path to Kaggle imgs/train folder")
    parser.add_argument("--dst", default="dataset/phone", help="Output directory")
    parser.add_argument("--val-ratio", type=float, default=0.2, help="Validation split ratio")
    args = parser.parse_args()
    prepare(args.src, args.dst, args.val_ratio)


if __name__ == "__main__":
    main()
