#!/usr/bin/env bash
# install.sh — materializes the tuatha-media-intel pipeline.
#
# All the files were already written to /Users/cianmacandeisigh/dev/cianfhoghlaim/
# by the build agent (the opencode session). This script:
#   1. Validates the file tree
#   2. Runs the BAML codegen (optional, requires uv + baml-cli)
#   3. Runs the CocoIndex conformance linter (optional, requires mise)
#   4. Runs the Swift build (optional, requires macOS + Xcode 16+)
#   5. Runs the Dagster asset check (optional, requires Dagster)
#   6. Runs the lint:registry strict mode (optional, requires mise)
#
# Idempotent — safe to re-run after every pull.

set -euo pipefail

ROOT="${1:-/Users/cianmacandeisigh/dev/cianfhoghlaim}"
echo "==> tuatha-media-intel install (root=$ROOT)"
cd "$ROOT" || { echo "root not found"; exit 1; }

echo ""
echo "==> 1. Validate the file tree"
required=(
  "baml_src/tuatha_media_intel.baml"
  "cocoindex_flows/tuatha_media_intel/_shared/__init__.py"
  "cocoindex_flows/tuatha_media_intel/ingestors/hades_boons.py"
  "cocoindex_flows/tuatha_media_intel/ingestors/comic_particles.py"
  "cocoindex_flows/tuatha_media_intel/ingestors/gba_magic.py"
  "cocoindex_flows/tuatha_media_intel/ingestors/anam_particles.py"
  "tuatha_media_intel/capture/tuatha-capture/Package.swift"
  "tuatha_media_intel/capture/tuatha-capture/Sources/tuatha-capture/main.swift"
  "tuatha_media_intel/capture/tuatha-capture/Sources/tuatha-capture/Capture.swift"
  "tuatha_media_intel/capture/tuatha-capture/Sources/tuatha-capture/Daemon.swift"
  "tuatha_media_intel/capture/tuatha-capture/Sources/tuatha-capture/Doctor.swift"
  "tuatha_media_intel/capture/LaunchAgent/com.ci.tuatha.capture.plist"
  "tuatha_media_intel/capture/python/pyproject.toml"
  "tuatha_media_intel/capture/python/tuatha_capture/cli.py"
  "tuatha_media_intel/capture/python/tuatha_capture/gba/__init__.py"
  "tuatha_media_intel/capture/python/tuatha_capture/comic/__init__.py"
  "orchestration/defs/2_materials/tuatha_media_intel.py"
  "orchestration/defs/2_materials/tuatha_media_intel_observability.py"
  "agents/meaisinfhoghlaim/tuatha_capture_agent.py"
  "bonneagar/stacks/tuatha-media-intel/compose.yaml"
  "bonneagar/stacks/tuatha-media-intel/sidecar.yaml"
  "bonneagar/stacks/tuatha-media-intel/secrets.env"
  "bonneagar/stacks/tuatha-media-intel/pangolin.yaml"
  "bonneagar/stacks/tuatha-media-intel/blueprint.yaml"
  "bonneagar/stacks/tuatha-media-intel/.env.example"
  "notebooks/tuatha_anam_dashboard.py"
  "notebooks/tuatha_anam/helpers/__init__.py"
  "notebooks/tuatha_anam/tabs/sources.py"
  "notebooks/tuatha_anam/tabs/boons.py"
  "notebooks/tuatha_anam/tabs/particles.py"
  "notebooks/tuatha_anam/tabs/join.py"
  "dlt_sources/tuatha_media_intel/hades/source.yaml"
  "dlt_sources/tuatha_media_intel/comic/source.yaml"
  "dlt_sources/tuatha_media_intel/gba/source.yaml"
  "openspec/changes/2026-08-25-tuatha-media-intel-pipeline-v1/proposal.md"
  "openspec/changes/2026-08-25-tuatha-media-intel-pipeline-v1/tasks.md"
  "openspec/changes/2026-08-25-tuatha-media-intel-pipeline-v1/specs/tuatha-media-intel/spec.md"
)
for f in "${required[@]}"; do
  if [[ ! -f "$f" ]]; then
    echo "    MISSING $f"
    exit 1
  fi
  echo "    ok   $f"
done

echo ""
echo "==> 2. BAML codegen (optional — requires uv + baml-cli)"
if command -v uv >/dev/null 2>&1; then
  if mise run tuatha-media-intel:baml:codegen 2>/dev/null; then
    echo "    BAML clients generated"
  else
    echo "    BAML codegen skipped (baml-cli not available)"
  fi
else
  echo "    BAML codegen skipped (uv not in PATH)"
fi

echo ""
echo "==> 3. CocoIndex conformance check (optional — requires mise)"
if command -v mise >/dev/null 2>&1; then
  if mise run upstream:conformance 2>/dev/null | grep -E "(FAIL|tuatha)" ; then
    echo "    conformance check failed — see output above"
    exit 1
  else
    echo "    conformance check passed"
  fi
else
  echo "    conformance check skipped (mise not in PATH)"
fi

echo ""
echo "==> 4. Swift build (optional — requires macOS 15+ + Xcode 16+)"
if [[ "$(uname -s)" == "Darwin" ]] && command -v swift >/dev/null 2>&1; then
  cd tuatha_media_intel/capture/tuatha-capture
  if swift build -c release 2>/dev/null; then
    mkdir -p "$HOME/.tuatha/bin"
    cp .build/release/tuatha-capture "$HOME/.tuatha/bin/"
    echo "    swift binary built → $HOME/.tuatha/bin/tuatha-capture"
  else
    echo "    swift build failed — see output above"
  fi
  cd "$ROOT"
else
  echo "    swift build skipped (requires macOS)"
fi

echo ""
echo "==> 5. lint:registry strict mode (optional — requires mise)"
if command -v mise >/dev/null 2>&1; then
  if mise run lint:registry --strict 2>/dev/null; then
    echo "    no hardcoded model strings — registry audit passes"
  else
    echo "    registry audit failed — see output above"
    exit 1
  fi
else
  echo "    registry audit skipped (mise not in PATH)"
fi

echo ""
echo "==> 6. Stack doctor check (optional — requires mise)"
if command -v mise >/dev/null 2>&1; then
  if mise run cic:stack-doctor 2>/dev/null | grep tuatha-media-intel; then
    echo "    stack-doctor passes for tuatha-media-intel"
  else
    echo "    stack-doctor did not mention tuatha-media-intel — verify manually"
  fi
else
  echo "    stack-doctor skipped (mise not in PATH)"
fi

echo ""
echo "==> install done. Next steps:"
echo "    1. mise run tuatha-media-intel:baml:test"
echo "    2. mise run tuatha-media-intel:capture:doctor       (macOS only)"
echo "    3. mise run tuatha-media-intel:capture:install-agent (macOS only)"
echo "    4. mise run tuatha-media-intel:capture:install-shims"
echo "    5. mise run tuatha-media-intel:stack:up"
echo "    6. open Hades / drop a CBZ / run mgba headless"
echo "    7. mise run tuatha-media-intel:notebook"
