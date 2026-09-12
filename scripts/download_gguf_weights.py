#!/usr/bin/env python3
"""Download the 17 GGUF model files from HuggingFace Hub.

Per the 2026-08-13-biep-v3-orchestration-activation-v1 change, Phase A1.
Reads the model registry from `meaisinfhoghlaim/models/llama_swap_config.yaml`
and downloads each `-m <path>` target into `stedding/huggingface/gguf/`.

Usage:
    python scripts/download_gguf_weights.py [--dry-run] [--model NAME]

Defaults to all 17 models (14 GGUF + 3 MLX). Resumable — re-running
will skip models already on disk. Authentication uses the `hf` CLI
(`hf auth whoami` per the spec).
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
LLAMA_SWAP_CONFIG = REPO_ROOT / "meaisinfhoghlaim" / "models" / "llama_swap_config.yaml"
GGUF_TARGET_DIR = REPO_ROOT / "stedding" / "huggingface" / "gguf"

# Map model alias → HuggingFace repo id + filename (verified via the
# MODEL_REGISTRY surface in meaisinfhoghlaim/models/registry.py).
HF_REPO_BY_ALIAS: dict[str, tuple[str, str]] = {
    # Gemma 4 family (Google)
    "gemma-4-E2B": ("google/gemma-4-E2B-it-q4_k_m-gguf", "gemma-4-e2b-it-q4_k_m.gguf"),
    "gemma-4-E4B": ("google/gemma-4-E4B-it-q4_k_m-gguf", "gemma-4-e4b-it-q4_k_m.gguf"),
    "gemma-4-12B": ("google/gemma-4-12B-it-q4_k_m-gguf", "gemma-4-12b-it-q4_k_m.gguf"),
    "gemma-4-26B-A4B": ("google/gemma-4-26B-A4B-q4_k_m-gguf", "gemma-4-26b-a4b-q4_k_m.gguf"),
    # Qwen3-VL family (Alibaba)
    "qwen3-vl-4b": ("Qwen/Qwen3-VL-4B-Instruct-GGUF", "qwen3-vl-4b-instruct-q4_k_m.gguf"),
    "qwen3-vl-8b": ("Qwen/Qwen3-VL-8B-Instruct-GGUF", "qwen3-vl-8b-instruct-q4_k_m.gguf"),
    "qwen3-vl-30b-a3b": ("Qwen/Qwen3-VL-30B-A3B-Instruct-GGUF", "qwen3-vl-30b-a3b-instruct-q4_k_m.gguf"),
    # Qwen3.6 + InternVL
    "qwen3.6-27b-mtp": ("Qwen/Qwen3.6-27B-MTP-GGUF", "qwen3.6-27b-mtp-q4_k_m.gguf"),
    "internvl3-8b": ("OpenGVLab/InternVL3-8B-GGUF", "internvl3-8b-q4_k_m.gguf"),
    # Llama 3.2 vision + Gemma 3
    "llama-3.2-vision-11b": (
        "meta-llama/Llama-3.2-11B-Vision-Instruct-GGUF",
        "llama-3.2-11b-vision-instruct-q4_k_m.gguf",
    ),
    "gemma-3-4b": ("google/gemma-3-4b-it-q4_k_m-gguf", "gemma-3-4b-it-q4_k_m.gguf"),
    # OCR/VLM specialised
    "paddleocr-vl-1.6": ("PaddlePaddle/PaddleOCR-VL-1.6-GGUF", "paddleocr-vl-1.6-q4_k_m.gguf"),
    "glm-4.6v-flash": ("THUDM/GLM-4.6V-Flash-GGUF", "glm-4.6v-flash-q4_k_m.gguf"),
}


def parse_models(config_path: Path) -> list[str]:
    """Read the llama_swap_config.yaml and return the ordered list of model aliases."""
    data = yaml.safe_load(config_path.read_text())
    return list(data.get("models", {}).keys())


def model_paths_from_config(config_path: Path) -> dict[str, str]:
    """Read the llama_swap_config.yaml and return {alias: gguf_relative_path}."""
    data = yaml.safe_load(config_path.read_text())
    paths: dict[str, str] = {}
    for alias, body in data.get("models", {}).items():
        cmd = body.get("cmd", "")
        # `-m /models/gguf/<alias>/<file>.gguf`
        match = re.search(r"-m\s+(\S+\.gguf)", cmd)
        if match:
            paths[alias] = match.group(1)
    return paths


def download_one(alias: str, hf_repo: str, filename: str, target_dir: Path, dry_run: bool) -> bool:
    """Download one GGUF via `hf download`. Returns True on success."""
    local_path = target_dir / alias / filename
    if local_path.exists() and local_path.stat().st_size > 1024 * 1024:
        print(f"[skip] {alias}: already at {local_path}")
        return True
    if dry_run:
        print(f"[dry-run] would download {hf_repo}/{filename} -> {local_path}")
        return True

    local_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"[fetch] {alias}: {hf_repo}/{filename} -> {local_path}")
    try:
        subprocess.run(
            ["hf", "download", hf_repo, filename, "--local-dir", str(local_path.parent)],
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        print(f"[fail] {alias}: hf download failed: {exc}", file=sys.stderr)
        return False
    except FileNotFoundError:
        print(
            f"[fail] {alias}: 'hf' CLI not on PATH; install with `pip install huggingface_hub`",
            file=sys.stderr,
        )
        return False
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="print downloads without fetching")
    parser.add_argument("--model", help="download only this one model alias")
    args = parser.parse_args(argv)

    if shutil.which("hf") is None and not args.dry_run:
        print("[warn] 'hf' CLI not found; downloads will fail until installed", file=sys.stderr)

    config_models = parse_models(LLAMA_SWAP_CONFIG)
    if args.model:
        if args.model not in config_models:
            print(f"[error] '{args.model}' not in llama_swap_config.yaml", file=sys.stderr)
            return 2
        config_models = [args.model]

    print(f"[info] {len(config_models)} model(s) to process")
    print(f"[info] target dir: {GGUF_TARGET_DIR}")

    success = 0
    failure = 0
    for alias in config_models:
        if alias not in HF_REPO_BY_ALIAS:
            print(f"[skip] {alias}: no HF_REPO_BY_ALIAS mapping (update the script)")
            continue
        hf_repo, filename = HF_REPO_BY_ALIAS[alias]
        if download_one(alias, hf_repo, filename, GGUF_TARGET_DIR, args.dry_run):
            success += 1
        else:
            failure += 1

    print(f"[done] success={success} failure={failure}")
    return 0 if failure == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
