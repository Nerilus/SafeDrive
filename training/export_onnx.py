"""Export a trained PyTorch checkpoint to ONNX format.

Usage::

    python -m training.export_onnx --checkpoint models/best.pth --output models/phone_detector.onnx
"""

import argparse

import torch
import onnx

from training.model import build_model


def export(checkpoint_path: str, output_path: str, input_size: int = 224):
    model = build_model(freeze_backbone=False)
    model.load_state_dict(torch.load(checkpoint_path, map_location="cpu", weights_only=True))
    model.eval()

    dummy = torch.randn(1, 3, input_size, input_size)

    torch.onnx.export(
        model,
        dummy,
        output_path,
        input_names=["input"],
        output_names=["logit"],
        dynamic_axes={"input": {0: "batch"}, "logit": {0: "batch"}},
        opset_version=13,
    )

    # Validate the exported model
    onnx_model = onnx.load(output_path)
    onnx.checker.check_model(onnx_model)
    print(f"ONNX model exported and validated: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Export phone detector to ONNX")
    parser.add_argument("--checkpoint", required=True, help="Path to .pth checkpoint")
    parser.add_argument("--output", default="models/phone_detector.onnx", help="Output ONNX path")
    parser.add_argument("--input-size", type=int, default=224)
    args = parser.parse_args()
    export(args.checkpoint, args.output, args.input_size)


if __name__ == "__main__":
    main()
