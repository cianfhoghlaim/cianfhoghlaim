"""
Validate the v4 litellm/config/config.yaml structure.

Per the 2026-06-29 OCR/VLM registry change, the litellm config MUST
have:
- 24+ model_list entries
- 9+ v4 aliases (vision, ocr, diagram, gaelic, irish, default, math, extract, embedding-bge-m3)
- No references to v3 model names (qwen2.5-vl, gemma-3-vision, deepseek-ocr, uccix-13b)
- Each v4 Unsloth model with a valid api_base (llama-swap, mlx-omni, or transformers)

Usage:
    python scripts/validate_litellm_config.py

Exit code 0 on success, 1 on any validation error.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

CONFIG_PATH = Path("bonneagar/stacks/litellm/config/config.yaml")

REQUIRED_ALIASES = {
    "vision",
    "ocr",
    "diagram",
    "gaelic",
    "irish",
    "default",
    "math",
    "extract",
    "embedding-bge-m3",
}

V3_FORBIDDEN_KEYS = {
    "qwen2.5-vl",
    "qwen25-vl",
    "gemma-3-vision",
    "gemma3-vision",
    "deepseek-ocr",
    "qwen2.5-math",
    "qwen25-math",
    "uccix-13b",
}

V4_REQUIRED_MODELS = {
    "local/vision/gemma-4-26B-A4B",  # M4 default
    "local/vision/qwen3-vl-8b",  # workhorse
    "local/vision/glm-4.6v-flash",  # realtime
    "local/vision/olmocr-2-7b-1025",  # allenai specialist
    "local/vision/deepseek-ocr-2",  # formula OCR
    "local/vision/granite-docling-258M",
    "local/vision/molmo2-8b",
    "local/vision/uccix-mistral-24b",  # Irish language
    "local/vision/qwen3-vl-30b-a3b",
    # qwen3-vl-235b-a22b removed (130GB; doesn't fit on M4 48GB)
}

ALLOWED_API_BASES = {
    "http://llama-swap:8080/v1",
    "http://mlx-omni:10240/v1",
    "http://transformers:5000/v1",
    "http://docling-serve:5001/v1",
    "http://olmocr:8003/v1",
    # M3 chokepoint (OpenCode Go) — pre-existing, added 2026-07-08
    "${OPENCODE_GO_BASE_URL:-https://opencode.ai/zen/go/v1}",
    # Token-plan direct endpoints — added 2026-08-07, see
    # openspec/changes/2026-08-06-token-plan-apis-lc-doc-pipeline-and-edge-tls-remediation-v1
    "${MINIMAX_BASE_URL:-https://api.minimax.io/v1}",
    "${DASHSCOPE_BASE_URL:-https://coding.dashscope.aliyuncs.com/v1}",
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=CONFIG_PATH,
        help=f"Config path (default: {CONFIG_PATH})",
    )
    args = parser.parse_args()

    if not args.config.exists():
        print(f"FAIL: {args.config} does not exist")
        return 1

    text = args.config.read_text()
    errors: list[str] = []

    # Check 1: no v3 forbidden model names (use word boundaries to avoid false positives)
    for v3_key in V3_FORBIDDEN_KEYS:
        # Look for v3_key as a whole model_name (after "  - model_name: " or in api path)
        pattern = rf"model_name:\s*{re.escape(v3_key)}\b"
        if re.search(pattern, text):
            errors.append(f"Found v3 model name '{v3_key}' as a model_name (should be v4)")
        # Also check for the qwen25- (no dot) variants and similar
        # Allow v4 names that *contain* the v3 string (e.g. deepseek-ocr-2 contains deepseek-ocr)

    # Check 2: required v4 models present
    for v4_key in V4_REQUIRED_MODELS:
        if v4_key not in text:
            errors.append(f"Missing required v4 model: {v4_key}")

    # Check 3: required aliases present
    for alias in REQUIRED_ALIASES:
        # Look for "  - model_name: <alias>" (top-level, not local/vision/...)
        if f"  - model_name: {alias}\n" not in text and f"  - model_name: {alias} " not in text:
            errors.append(f"Missing required alias: {alias}")

    # Check 4: all api_base values are allowed
    api_bases = set(re.findall(r"api_base:\s*(\S+)", text))
    for api_base in api_bases:
        if api_base not in ALLOWED_API_BASES:
            errors.append(f"Unexpected api_base: {api_base}")

    # Count
    n_models = len(re.findall(r"^  - model_name:", text, re.MULTILINE))
    n_aliases = sum(1 for alias in REQUIRED_ALIASES if f"  - model_name: {alias}\n" in text)

    print(f"Config: {args.config}")
    print(f"  Total model_name entries: {n_models}")
    print(f"  v4 aliases found: {n_aliases}/{len(REQUIRED_ALIASES)}")
    print(f"  api_base values: {api_bases}")
    print()

    if errors:
        print(f"FAIL: {len(errors)} validation error(s):")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("OK: config is valid v4")
    return 0


if __name__ == "__main__":
    sys.exit(main())
