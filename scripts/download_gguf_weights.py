#!/usr/bin/env python3
"""Download the 17 GGUF model files for llama-swap.

Per the 2026-08-17-biep-v3-bring-up-v1 change (P2.2): downloads the
17 GGUF model files from HuggingFace Hub via the `hf` CLI into
`stedding/huggingface/gguf/`. Reads the priority order from
`meaisinfhoghlaim/models/llama_swap_config.yaml`.

The order is:
  1. gemma-4-26B-A4B (M4 default workhorse)
  2. qwen3-vl-8b (the 4-path OCR ensemble workhorse)
  3. qwen3.6-27b-mtp (text-only mark floor)
  4-17. 14 specialist / legacy models

Usage:
    uv run python scripts/download_gguf_weights.py
    uv run python scripts/download_gguf_weights.py --dry-run
    uv run python scripts/download_gguf_weights.py --model gemma-4-26B-A4B

Exit codes:
    0 = all selected models downloaded
    1 = one or more downloads failed
    2 = the hf CLI is not available (operator must `pip install huggingface_hub[cli]`)
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEST_DIR = REPO_ROOT / "stedding" / "huggingface" / "gguf"
CONFIG_FILE = REPO_ROOT / "meaisinfhoghlaim" / "models" / "llama_swap_config.yaml"

# Per the 2026-08-17-biep-v3-bring-up-v1 change (P2.2): the canonical
# 17-model llama-swap roster, in priority order.
DEFAULT_MODELS: list[str] = [
    "gemma-4-26B-A4B",            # 1. M4 default workhorse
    "qwen3-vl-8b",                # 2. OCR ensemble workhorse
    "qwen3.6-27b-mtp",            # 3. text-only mark floor
    "deepseek-ocr-2",             # 4. forms specialist
    "docling-serve",              # 5. layout specialist
    "dots-ocr",                   # 6. tesseract fallback
    "gemma-3-4b",                 # 7. lightweight mark
    "glm-4.6v-flash",             # 8. third-party vision
    "internvl3-8b",               # 9. multilingual vision
    "molmo2-4b",                  # 10. diagram specialist
    "molmo2-8b",                  # 11. diagram pointing specialist
    "olmocr-2-7b-1025",           # 12. tables + latex
    "paddleocr-vl-1.6",           # 13. multilingual OCR
    "qwen3-vl-30b-a3b",           # 14. large MoE vision
    "qwen3-vl-4b",                # 15. small vision
    "uccix-mistral-24b",          # 16. Irish-language
    "unstract-api",               # 17. external API
]


def check_hf_cli() -> bool:
    """Verify the `hf` CLI is available (operator pre-flight)."""
    return shutil.which("hf") is not None


def download_model(model_id: str, dry_run: bool = False) -> bool:
    """Download one GGUF file via `hf download`. Returns True on success."""
    hf_repo = f"unsloth/{model_id}-GGUF"
    # The canonical GGUF filename for the model (default quantization = Q4_K_M)
    gguf_filename = f"{model_id}.Q4_K_M.gguf"
    dest_path = DEST_DIR / model_id
    dest_path.mkdir(parents=True, exist_ok=True)

    if dry_run:
        print(f"  DRY-RUN: would download {hf_repo} -> {dest_path}/{gguf_filename}")
        return True

    print(f"  Downloading {hf_repo} -> {dest_path}/{gguf_filename} ...")
    try:
        result = subprocess.run(
            [
                "hf", "download",
                hf_repo,
                gguf_filename,
                "--local-dir", str(dest_path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        print(f"  OK: {result.stdout.strip().splitlines()[-1] if result.stdout else 'downloaded'}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  FAIL: {e.stderr.strip()[:200]}", file=sys.stderr)
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print what would be downloaded without actually downloading",
    )
    parser.add_argument(
        "--model",
        action="append",
        help="restrict to specific model IDs (default: all 17 in priority order)",
    )
    args = parser.parse_args()

    models = args.model if args.model else DEFAULT_MODELS
    print(f"Plan: download {len(models)} GGUF model(s) into {DEST_DIR}")
    print(f"  source: unsloth/<model_id>-GGUF")
    print(f"  filename pattern: <model_id>.Q4_K_M.gguf")
    print(f"  estimated total transfer: ~60-80 GB")
    print()

    if not args.dry_run and not check_hf_cli():
        print(
            "ERROR: `hf` CLI not found. Install with:",
            file=sys.stderr,
        )
        print("  pip install -U 'huggingface_hub[cli]'", file=sys.stderr)
        print(
            "  # or: uv tool install 'huggingface_hub[cli]'",
            file=sys.stderr,
        )
        return 2

    successes = 0
    failures: list[str] = []
    for i, model_id in enumerate(models, start=1):
        print(f"[{i}/{len(models)}] {model_id}")
        if download_model(model_id, dry_run=args.dry_run):
            successes += 1
        else:
            failures.append(model_id)

    print()
    print(f"Summary: {successes} succeeded, {len(failures)} failed")
    if failures:
        print(f"  Failed: {failures}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())