"""
Download all v4 mlx-community MLX checkpoints to stedding/huggingface/mlx-community/.

Per the v4 registry (cianfhoghlaim/meaisinfhoghlaim/models/registry.py),
the 4 MLX-only entries (served by mlx-omni :10240, not llama-swap) are:

  - granite-docling-258M  → mlx-community/granite-docling-258m-mlx
  - dots-ocr              → mlx-community/dots.ocr-4bit
  - deepseek-ocr-2        → mlx-community/DeepSeek-OCR-bf16
  - gemma-4-E2B           → mlx-community/gemma-4-e2b-it-4bit (also has GGUF)

Plus optional MLX variants of the Unsloth entries (for Apple Silicon
inference via mlx-omni instead of llama-swap):
  - gemma-4-26B-A4B       → mlx-community/gemma-4-26b-a4b-it-4bit
  - qwen3-vl-8b           → mlx-community/Qwen3-VL-8B-Instruct-4bit
  - qwen3-vl-30b-a3b      → mlx-community/Qwen3-VL-30B-A3B-Instruct-4bit
  - glm-4.6v-flash        → mlx-community/GLM-4.6V-Flash-4bit

Usage:
    python scripts/download_mlx_models.py            # download 4 MLX-only entries
    python scripts/download_mlx_models.py --include-unsloth  # also download 4 Unsloth MLX variants
    python scripts/download_mlx_models.py --dry-run  # list only

Note: requires the `huggingface-cli` (from the `huggingface_hub` package).
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

# Ensure the registry is importable
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

# Filter the deprecation warning from the v4 registry
import warnings  # noqa: E402

warnings.filterwarnings("ignore")
from cianfhoghlaim.ocr.models import VISION_MODELS  # noqa: E402

DEFAULT_CACHE_DIR = Path(
    os.environ.get(
        "MLX_COMMUNITY_CACHE_DIR",
        str(
            Path(__file__).resolve().parent.parent
            / "stedding"
            / "huggingface"
            / "mlx-community"
        ),
    )
)


def download_model(model_id: str, cache_dir: Path, dry_run: bool = False) -> bool:
    """Download a single mlx-community checkpoint."""
    if dry_run:
        print(f"  [DRY-RUN] would download: {model_id}")
        return True

    target = cache_dir / model_id.split("/")[-1]
    target.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env.setdefault("HF_HUB_DOWNLOAD_TIMEOUT", "600")

    cmd = [
        "huggingface-cli", "download", model_id,
        "--local-dir", str(target),
    ]
    print(f"  $ {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True, env=env, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"  WARNING: download failed for {model_id}: {e}")
        return False


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
        "--include-unsloth",
        action="store_true",
        help="Also download the MLX variants of the Unsloth entries (8 more models)",
    )
    args = parser.parse_args()

    print(f"Downloading v4 mlx-community MLX checkpoints to {args.cache_dir}")
    if args.dry_run:
        print("(DRY-RUN mode)")
    print()

    # The 4 MLX-only entries (always included)
    mlx_only_keys = {
        "granite-docling-258M",
        "dots-ocr",
        "deepseek-ocr-2",
        "gemma-4-E2B",
    }

    # The 4 Unsloth entries that ALSO have mlx_id (only with --include-unsloth)
    mlx_plus_unsloth_keys = {
        "gemma-4-26B-A4B",
        "qwen3-vl-8b",
        "qwen3-vl-30b-a3b",
        "glm-4.6v-flash",
    }

    target_keys = mlx_only_keys
    if args.include_unsloth:
        target_keys = mlx_only_keys | mlx_plus_unsloth_keys

    n_total = 0
    n_ok = 0
    n_skip = 0
    for key, model in VISION_MODELS.items():
        if key not in target_keys:
            continue
        if not model.mlx_id:
            print(f"  [SKIP] {key} (no mlx variant in registry)")
            n_skip += 1
            continue
        n_total += 1
        print(f"[{n_total}] {key} → {model.mlx_id}")
        ok = download_model(model.mlx_id, args.cache_dir, args.dry_run)
        if ok:
            n_ok += 1
        print()

    print(
        f"Summary: {n_ok}/{n_total} downloaded, "
        f"{n_skip} skipped (no mlx variant). "
        f"Cache: {args.cache_dir}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
