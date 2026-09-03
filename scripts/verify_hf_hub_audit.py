"""
HF Hub liveness audit for the v4 VISION_MODELS registry.

Per the 2026-06-29 OCR/VLM registry change, every entry in
`cianfhoghlaim.ocr.models.VISION_MODELS` MUST be live on the HF Hub.

This script verifies all `unsloth_id`, `mlx_id`, and `upstream_id`
strings against the HF Hub API and reports any 404s.

Usage:
    python scripts/verify_hf_hub_audit.py [--strict]

Exit code 0 if all IDs are live, 1 otherwise.
"""

from __future__ import annotations

import argparse
import os
import sys
import time
import urllib.error
import urllib.request
import warnings

# Ensure the registry is importable
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

warnings.filterwarnings("ignore")
from cianfhoghlaim.ocr.models import VISION_MODELS  # noqa: E402

HF_HUB_API = "https://huggingface.co/api/models/{model_id}"
HF_HUB_HEADERS = {"User-Agent": "kcg-ocr-registry-audit/1.0"}


def check_hf_hub(model_id: str, timeout: float = 10.0) -> tuple[bool, int, str]:
    """Check if a HF model_id is live.

    Returns (is_live, http_status, error_message).
    """
    url = HF_HUB_API.format(model_id=model_id)
    req = urllib.request.Request(url, headers=HF_HUB_HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return True, resp.status, ""
    except urllib.error.HTTPError as e:
        return False, e.code, str(e)
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        return False, 0, str(e)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with non-zero status on any 404",
    )
    parser.add_argument(
        "--only",
        choices=("unsloth", "mlx", "upstream", "all"),
        default="all",
        help="Which ID types to check (default: all)",
    )
    args = parser.parse_args()

    print(f"Checking {len(VISION_MODELS)} VISION_MODELS entries against HF Hub...")
    print()

    n_ok = 0
    n_fail = 0
    failures: list[tuple[str, str, int, str]] = []

    for key, model in VISION_MODELS.items():
        ids_to_check = []
        if args.only in ("unsloth", "all") and model.unsloth_id:
            ids_to_check.append(("unsloth_id", model.unsloth_id))
        if args.only in ("mlx", "all") and model.mlx_id:
            ids_to_check.append(("mlx_id", model.mlx_id))
        if args.only in ("upstream", "all") and model.upstream_id:
            ids_to_check.append(("upstream_id", model.upstream_id))

        for field, model_id in ids_to_check:
            is_live, status, err = check_hf_hub(model_id)
            if is_live:
                print(f"  OK   {key:30s}  {field:12s}  {model_id}")
                n_ok += 1
            else:
                print(f"  FAIL {key:30s}  {field:12s}  {model_id}  (HTTP {status}: {err})")
                failures.append((key, field, model_id, status, err))
                n_fail += 1
            time.sleep(0.1)  # be polite to HF Hub

    print()
    print(f"Summary: {n_ok} OK, {n_fail} FAIL")

    if failures:
        print()
        print("Failed model_ids:")
        for key, field, model_id, status, err in failures:
            print(f"  - {key}.{field}: {model_id} (HTTP {status})")

    if args.strict and n_fail > 0:
        print()
        print("STRICT mode: exiting with code 1")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
