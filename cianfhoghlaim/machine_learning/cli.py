"""cianfhoghlaim-ocr — CLI for the OCR/VLM registry, evaluation harness, and adapters.

Usage:
    uv run cianfhoghlaim-ocr --help
    uv run cianfhoghlaim-ocr audit-registry     # verify the v4 VISION_MODELS against HF Hub
    uv run cianfhoghlaim-ocr eval --backend mlx # run the Celtic OCR evaluation harness
"""
from __future__ import annotations

import argparse
import sys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="cianfhoghlaim-ocr",
        description=(
            "OCR/VLM CLI. Manages the v4 VISION_MODELS registry (24 vision models across "
            "Pylaia, TrOCR, PaddleOCR, Tesseract, dots.ocr, VLM backends) and the Celtic OCR "
            "evaluation harness."
        ),
    )
    sub = parser.add_subparsers(dest="cmd")

    p_audit = sub.add_parser("audit-registry", help="Verify all VISION_MODELS against HF Hub")
    p_audit.add_argument("--strict", action="store_true", help="Exit 1 if any model missing")

    p_eval = sub.add_parser("eval", help="Run the Celtic OCR evaluation harness")
    p_eval.add_argument("--backend", default="mlx", help="Backend to evaluate (mlx, paddle, dots, …)")

    args = parser.parse_args(argv)

    if args.cmd == "audit-registry":
        print(f"[cianfhoghlaim-ocr] audit-registry strict={args.strict}")
        print("(Stub: delegates to mise run hf:verify-ocr-registry --strict)")
        return 0

    if args.cmd == "eval":
        print(f"[cianfhoghlaim-ocr] eval backend={args.backend}")
        print("(Stub: delegates to mise run cic:ocr:eval)")
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))