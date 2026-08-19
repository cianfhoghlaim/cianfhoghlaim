#!/usr/bin/env python3
"""Validate opencode.json schema + agent structure + no deprecated tools field.

Per the dev-tooling-surfaces spec Requirement § opencode-permission-api-migration:
- Every agent SHALL use the `permission` field (not the deprecated `tools` field)
- This script exits 0 if all agents comply; exits 1 otherwise.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

CONFIG = Path(__file__).resolve().parent.parent / "opencode.json"


def main() -> int:
    if not CONFIG.exists():
        print(f"ERROR: opencode.json not found at {CONFIG}", file=sys.stderr)
        return 1

    cfg = json.loads(CONFIG.read_text())
    agents = cfg.get("agent", {})

    if not agents:
        print("ERROR: no agents defined in opencode.json", file=sys.stderr)
        return 1

    print(f"OpenCode config: {len(agents)} agents")

    deprecated_tools: list[str] = []
    missing_prompts: list[str] = []
    invalid_permissions: list[str] = []

    for name, body in agents.items():
        mode = body.get("mode", "subagent")
        hidden = body.get("hidden", False)
        prompt = body.get("prompt", "")

        if isinstance(prompt, str) and prompt:
            ptype = "file" if prompt.startswith("{file:") else "inline"
        else:
            ptype = "none"
            missing_prompts.append(name)

        print(f"  {name:20s} mode={mode:10s} hidden={str(hidden):5s} prompt={ptype}")

        # Per the spec: NO deprecated tools field (which is a dict)
        if "tools" in body and isinstance(body["tools"], dict):
            deprecated_tools.append(name)

        # If permission is present, it must be valid
        if "permission" in body:
            perm = body["permission"]
            if not isinstance(perm, dict):
                invalid_permissions.append(name)

    errors: list[str] = []
    if deprecated_tools:
        errors.append(f"deprecated tools field used by: {deprecated_tools}")
    if missing_prompts:
        # OK for hidden internal agents
        non_hidden_missing = [n for n in missing_prompts if not cfg["agent"][n].get("hidden")]
        if non_hidden_missing:
            errors.append(f"non-hidden agents missing prompts: {non_hidden_missing}")
    if invalid_permissions:
        errors.append(f"agents with invalid permission field: {invalid_permissions}")

    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1

    print("OpenCode config: VALID")
    print("  - All agents comply with the permission API (no deprecated tools)")
    print("  - All non-hidden agents have prompts")
    print("  - All permission fields are dicts")
    return 0


if __name__ == "__main__":
    sys.exit(main())
