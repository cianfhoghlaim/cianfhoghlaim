"""
Download all v4 Unsloth GGUFs to /models/unsloth/.

Per openspec/changes/2026-06-29-fix-ocr-vlm-registry-with-unsloth-priority,
this is a one-time-per-machine operation that populates the GGUF cache
for the llama-swap service.

Usage:
    python scripts/download_unsloth_models.py            # download all
    python scripts/download_unsloth_models.py --dry-run # list only
    python scripts/download_unsloth_models.py --key gemma-4-26B-A4B  # one model

Note: requires the `huggingface-cli` (from the `huggingface_hub` package).
For private/gated repos, set HF_TOKEN in the environment.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import warnings
from pathlib import Path

# Ensure the registry is importable
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

warnings.filterwarnings("ignore")
from cianfhoghlaim.ocr.models import VISION_MODELS  # noqa: E402

DEFAULT_CACHE_DIR = Path("/models/unsloth")


def download_model(model_id: str, cache_dir: Path, dry_run: bool = False) -> bool:
    """Download a single Unsloth GGUF (mmproj + q4_k_m)."""
    if dry_run:
        print(f"  [DRY-RUN] would download: {model_id}")
        return True

    # Build the target dir
    target = cache_dir / model_id.split("/")[-1]
    target.mkdir(parents=True, exist_ok=True)

    # Download the Q4_K_M + mmproj variants
    patterns = [
        f"{model_id}/*Q4_K_M*",
        f"{model_id}/*q4_k_m*",
        f"{model_id}/*mmproj*",
    ]
    env = os.environ.copy()
    env.setdefault("HF_HUB_DOWNLOAD_TIMEOUT", "600")

    for pattern in patterns:
        cmd = [
            "huggingface-cli", "download", model_id,
            "--local-dir", str(target),
            "--include", pattern,
        ]
        print(f"  $ {' '.join(cmd)}")
        try:
            subprocess.run(cmd, check=True, env=env, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            print(f"  WARNING: pattern '{pattern}' not found (this is OK if a different quant is preferred)")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=DEFAULT_CACHE_DIR,
        help=f"Cache directory (default: {DEFAULT_CACHE_DIR})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List the models that would be downloaded without actually downloading",
    )
    parser.add_argument(
        "--key",
        help="Only download this specific registry key (default: all Unsloth GGUFs)",
    )
    args = parser.parse_args()

    print(f"Downloading v4 Unsloth GGUFs to {args.cache_dir}")
    if args.dry_run:
        print("(DRY-RUN mode)")
    print()

    n_total = 0
    n_ok = 0
    n_skip = 0
    for key, model in VISION_MODELS.items():
        if args.key and key != args.key:
            continue
        if not model.unsloth_id:
            print(f"  [SKIP] {key} (no Unsloth variant)")
            n_skip += 1
            continue
        n_total += 1
        print(f"[{n_total}] {key} → {model.unsloth_id}")
        ok = download_model(model.unsloth_id, args.cache_dir, args.dry_run)
        if ok:
            n_ok += 1
        print()

    print(f"Summary: {n_ok}/{n_total} downloaded, {n_skip} skipped (no Unsloth variant)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
