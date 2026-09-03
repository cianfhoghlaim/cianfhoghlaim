#!/usr/bin/env bash
# Flatten cianfhoghlaim/* → repo root, with conflict resolution.
# Run from the repo root. Uses git mv to preserve history.
set -euo pipefail

# Files in cianfhoghlaim/ that conflict at root and need special handling:
# - README.md       → cianfhoghlaim/README.md moved to docs/legacy/cianfhoghlaim-pkg-readme.md
#                     (root README.md will be rewritten in Phase 4.2; the package-level
#                     README is preserved as a legacy artifact)
# - pyproject.toml  → MERGE: take root's pyproject.toml, append the [tool.*] sections
#                     from cianfhoghlaim/pyproject.toml (the package's own tool config
#                     and the [project.scripts] block). The root workspace shell wins
#                     for [project] and [build-system]; the package provides the rest.
# - cli.py          → RENAME cianfhoghlaim/cli.py → cian_clio.py and keep it
#                     (the root cli.py is `cianfhoghlaim-stack-doctor`; the package
#                     needs its own CLI entrypoint)
# - data/           → cianfhoghlaim/data was added in the IaC merge. Check collision.
# - __pycache__/    → SKIP (already gitignored, but won't be committed)
# - scripts/        → MERGE (most scripts are unique per side; check for name collisions)

cd "$(git rev-parse --show-toplevel)"

# 1. Move the non-conflicting cianfhoghlaim/* contents to root
git mv cianfhoghlaim/agents .
git mv cianfhoghlaim/baml .
git mv cianfhoghlaim/baml_client .
git mv cianfhoghlaim/baml_src .
git mv cianfhoghlaim/cocoindex .
git mv cianfhoghlaim/dlt .
git mv cianfhoghlaim/dlthub-ai-workbench .
git mv cianfhoghlaim/leabharlann .
git mv cianfhoghlaim/leaving_certificate .
git mv cianfhoghlaim/meaisinfhoghlaim .
git mv cianfhoghlaim/motherduck .
git mv cianfhoghlaim/notebooks .
git mv cianfhoghlaim/observability .
git mv cianfhoghlaim/orchestration .
git mv cianfhoghlaim/storage .
git mv cianfhoghlaim/tests .
git mv cianfhoghlaim/tuatha .
git mv cianfhoghlaim/web .
git mv cianfhoghlaim/__init__.py .
git mv cianfhoghlaim/__main__.py .
git mv cianfhoghlaim/__deployment__.py .

# 2. Resolve cli.py collision: rename cianfhoghlaim/cli.py → clio.py
# (the IaC's root cli.py is `cianfhoghlaim-stack-doctor`; the package keeps its own CLI)
git mv cianfhoghlaim/cli.py clio.py

# 3. Resolve README.md collision: cianfhoghlaim/README.md → docs/legacy/cianfhoghlaim-pkg-readme.md
mkdir -p docs/legacy
git mv cianfhoghlaim/README.md docs/legacy/cianfhoghlaim-pkg-readme.md

# 4. Resolve pyproject.toml collision: merge manually after the rest moves
git mv cianfhoghlaim/pyproject.toml pyproject.merged.toml.tmp

# 5. Move the remaining cianfhoghlaim contents
# scripts/ — both root and cianfhoghlaim have scripts/. Check for collisions.
if [ -d "cianfhoghlaim/scripts" ]; then
  # Move each script into root scripts/ unless it already exists at root
  for f in cianfhoghlaim/scripts/*; do
    rel="${f#cianfhoghlaim/}"
    if [ -e "$rel" ]; then
      # Collision: move to scripts/legacy/ instead
      mkdir -p scripts/legacy
      git mv "$f" "scripts/legacy/$(basename "$f").pkg"
    else
      git mv "$f" "$rel"
    fi
  done
  # Remove now-empty cianfhoghlaim/scripts if it's empty
  rmdir cianfhoghlaim/scripts 2>/dev/null || true
fi

# data/ — if both root and cianfhoghlaim have data/, keep root's, rename cianfhoghlaim's
if [ -d "cianfhoghlaim/data" ]; then
  if [ -d "data" ]; then
    mkdir -p data/legacy
    git mv cianfhoghlaim/data data/legacy/cianfhoghlaim-pkg-data
  else
    git mv cianfhoghlaim/data data
  fi
fi

# 6. Remove the now-empty cianfhoghlaim directory
if [ -d cianfhoghlaim ]; then
  # Move the orphaned pyproject.toml back if it's still there
  if [ -f pyproject.merged.toml.tmp ]; then
    mv pyproject.merged.toml.tmp /tmp/cianfhoghlaim-pyproject.toml
  fi
  rmdir cianfhoghlaim 2>/dev/null || {
    echo "WARNING: cianfhoghlaim/ is not empty after move:"
    ls -la cianfhoghlaim/
    exit 1
  }
fi

echo "Flatten complete. Top-level dirs:"
ls -1
echo "---"
echo "If pyproject.merged.toml.tmp was created, run:"
echo "  /Users/cianmacandeisigh/dev/kings_college_galway/./scripts/merge-pyproject.sh"
