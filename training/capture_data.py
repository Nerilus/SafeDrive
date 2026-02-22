"""Capture webcam frames for building a custom phone detection dataset.

Controls:
- SPACE : save current frame
- Q     : quit

Usage::

    python -m training.capture_data --label phone --output dataset/phone/train/phone
    python -m training.capture_data --label no_phone --output dataset/phone/train/no_phone
"""

import argparse
import os
import time

import cv2


def main():
    parser = argparse.ArgumentParser(description="Capture webcam frames")
    parser.add_argument("--label", required=True, help="Label name (phone / no_phone)")
    parser.add_argument("--output", required=True, help="Directory to save images")
    parser.add_argument("--camera", type=int, default=0, help="Camera index")
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)
    cap = cv2.VideoCapture(args.camera)
    if not cap.isOpened():
        print("Cannot open camera")
        return

    count = len([f for f in os.listdir(args.output) if f.endswith(".jpg")])
    print(f"Saving to {args.output} (starting at {count})")
    print("SPACE = capture | Q = quit")

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        display = frame.copy()
        cv2.putText(
            display, f"[{args.label}] captured: {count}",
            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2,
        )
        cv2.imshow("Capture", display)

        key = cv2.waitKey(1) & 0xFF
        if key == ord(" "):
            fname = f"{args.label}_{int(time.time())}_{count:04d}.jpg"
            cv2.imwrite(os.path.join(args.output, fname), frame)
            count += 1
            print(f"Saved {fname} ({count} total)")
        elif key == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    print(f"Done. {count} images in {args.output}")


if __name__ == "__main__":
    main()
