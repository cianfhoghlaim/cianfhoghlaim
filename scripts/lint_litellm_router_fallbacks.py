#!/usr/bin/env python3
"""Litellm router_settings.fallbacks lint.

Per the 2026-08-17-biep-v3-bring-up-v1 change (P2.15): every
`router_settings.fallbacks:` block in
`bonneagar/stacks/litellm/config/config.yaml` MUST use the dict form
`{primary_model: [fallback_model, ...]}`. Bare lists of model-name
strings crash the container at startup (per the
`2026-07-29-lakehouse-extensive-hydration-v1` change + litellm 1.x
Router.validate_fallbacks).

Per-model fallbacks in `model_list[*].litellm_params.fallbacks:`
arrays are exempt (they're per-model, not per-router).

Usage:
    mise run lint:litellm-router-fallbacks

Exit codes:
    0 = no bare-list router_settings.fallbacks
    1 = one or more violations
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
LITELLM_CONFIG = REPO_ROOT / "bonneagar" / "stacks" / "litellm" / "config" / "config.yaml"


def main() -> int:
    if not LITELLM_CONFIG.exists():
        print(f"FAIL: {LITELLM_CONFIG} does not exist", file=sys.stderr)
        return 1

    text = LITELLM_CONFIG.read_text(encoding="utf-8")

    # Find every `router_settings:` block and look at its `fallbacks:` value.
    # The litellm schema requires each fallbacks entry to be `{primary: [...]}`
    # i.e. a single-key mapping. Bare lists like `fallbacks: [gpt-4, claude-3]`
    # are rejected by Router.validate_fallbacks.
    failures: list[tuple[int, str]] = []

    lines = text.splitlines()
    in_router_section = False
    for i, line in enumerate(lines, start=1):
        if line.startswith("router_settings:"):
            in_router_section = True
            continue
        if in_router_section:
            # End of router_settings section is the next top-level key (no indent)
            if line and not line.startswith(" "):
                in_router_section = False
            elif "fallbacks:" in line and "model_list" not in line:
                # Bare-list form: "fallbacks: [gpt-4, claude-3]"
                stripped = line.split(":", 1)[1].strip()
                if stripped.startswith("["):
                    failures.append((i, stripped))

    if failures:
        print(
            f"FAIL: {len(failures)} router_settings.fallbacks: block(s) use the bare-list form:",
            file=sys.stderr,
        )
        for lineno, content in failures:
            print(f"  - line {lineno}: {content!r}", file=sys.stderr)
        print(
            "\nFIX: use the dict form:\n"
            "  fallbacks:\n"
            "    - qwen3-vl-8b: [gemma-4-26B-A4B, glm-4.6v-flash, openai/glm-4.6]\n"
            "Per the 2026-07-29-lakehouse-extensive-hydration-v1 change.",
            file=sys.stderr,
        )
        return 1

    print("OK: all router_settings.fallbacks blocks use the dict form.")
    return 0


if __name__ == "__main__":
    sys.exit(main())