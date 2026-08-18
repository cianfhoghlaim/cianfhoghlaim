#!/usr/bin/env python3
"""Locket version lint.

Per the 2026-08-17-hygiene-drift-cleanup-v1 change (P2.9): every
compose.yaml under bonneagar/stacks/**/ that references
`bpbradley/locket:infisical` MUST be at version >= v0.18.0 OR
substitute the cianfhoghlaim shim image
`ghcr.io/cianfhoghlaim/locket-shim:infisical-0.2.0`.

The reason: per the 2026-08-15-bonneagar-infra-remediation-v2 change,
the upstream `locket v0.17.3` image ships snake_case field names while
the Infisical v0.161+ REST API requires camelCase (`projectId`,
`secretPath`, `secretType`); the upstream sidecar 422s on every call.
The workaround is the `bonneagar/locket-shim/cianfhoghlaim-locket-shim.py`
295-line Python script, which is the canonical sidecar until
`locket v0.18.0-rc.1` ships the camelCase fix.

Usage:
    mise run lint:locket-version

Exit codes:
    0 = all locket refs are >= v0.18.0 OR use the shim
    1 = one or more locket refs are < v0.18.0
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
STACKS_DIR = REPO_ROOT / "bonneagar" / "stacks"

# Match `image: [ghcr.io/]bpbradley/locket:infisical[:version][@digest]`.
# The shim image and any other locket variant are exempt.
LOCKET_IMAGE_RE = re.compile(
    r"image:\s*['\"]?(?:ghcr\.io/)?bpbradley/locket:infisical(?:-[^\s'\"@]*)?(?:@[\w:.]+)?['\"]?"
)


def parse_version_from_tag(tag: str) -> str | None:
    """Extract the version string from a locket image tag.

    Examples:
        'ghcr.io/bpbradley/locket:infisical'          -> 'latest' (unknown)
        'bpbradley/locket:infisical-v0.17.3'          -> 'v0.17.3'
        'ghcr.io/bpbradley/locket:infisical-v0.18.0'  -> 'v0.18.0'
    """
    # Strip any registry prefix + repo name, then strip the leading dash.
    # What's left is the version suffix.
    suffix = re.sub(r"^(?:ghcr\.io/)?bpbradley/locket:infisical", "", tag)
    suffix = suffix.lstrip("-v")
    if not suffix:
        return None
    return "v" + suffix


def is_shim(image_ref: str) -> bool:
    return "cianfhoghlaim/locket-shim" in image_ref


def scan_compose_files() -> list[tuple[Path, str, str | None]]:
    """Walk all compose.yaml under bonneagar/stacks/ and extract locket refs.

    Returns list of (file_path, image_ref, parsed_version_or_None).
    """
    results: list[tuple[Path, str, str | None]] = []
    for compose_file in STACKS_DIR.glob("*/compose.yaml"):
        text = compose_file.read_text(encoding="utf-8")
        for match in LOCKET_IMAGE_RE.finditer(text):
            image_ref = match.group(0)
            # Strip the `image:` prefix and any trailing quote
            image_ref = re.sub(r"^image:\s*['\"]?", "", image_ref).rstrip("'\"")
            if is_shim(image_ref):
                continue
            version = parse_version_from_tag(image_ref)
            results.append((compose_file, image_ref, version))
    return results


def main() -> int:
    refs = scan_compose_files()
    if not refs:
        print("OK: no bpbradley/locket:infisical refs found.")
        return 0

    print(f"Found {len(refs)} bpbradley/locket:infisical ref(s):")
    for path, image_ref, version in refs:
        print(f"  - {path.relative_to(REPO_ROOT)}: {image_ref} (version={version})")

    failures: list[tuple[Path, str]] = []
    for path, image_ref, version in refs:
        if version is None:
            failures.append((path, f"unknown version for {image_ref}"))
            continue
        # Parse v0.18.0 or later
        try:
            parts = version.lstrip("v").split(".")
            major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
        except (ValueError, IndexError):
            failures.append((path, f"could not parse version {version}"))
            continue
        if (major, minor, patch) < (0, 18, 0):
            failures.append((path, f"{image_ref} is < v0.18.0 (camelCase fix)"))

    if failures:
        print(
            f"\nFAIL: {len(failures)} locket ref(s) are < v0.18.0:",
            file=sys.stderr,
        )
        for path, reason in failures:
            print(f"  - {path.relative_to(REPO_ROOT)}: {reason}", file=sys.stderr)
        print(
            "\nFIX: upgrade to >= v0.18.0 OR substitute the shim image:\n"
            "  image: ghcr.io/cianfhoghlaim/locket-shim:infisical-0.2.0\n"
            "See docs/PANGOLIN_OIDC_CONFIG.md and\n"
            "  openspec/specs/infrastructure-stacks/spec.md\n"
            "for the camelCase Infisical v0.161+ context.",
            file=sys.stderr,
        )
        return 1

    print("\nOK: all locket refs are >= v0.18.0 or use the shim.")
    return 0


if __name__ == "__main__":
    sys.exit(main())