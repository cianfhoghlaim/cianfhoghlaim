#!/usr/bin/env bash
# croilar/scripts/fix-pth.sh — Post-install fix for the broken
# uv editable-install pth file.
#
# The problem (per https://github.com/cianfhoghlaim/kings_college_galway/issues/17):
#   `uv pip install -e .` for a project whose pyproject.toml sits AT
#   the project root (e.g. /path/to/croilar/pyproject.toml) generates
#   a _editable_impl_croilar.pth file with N lines, one per entry in
#   the pyproject.toml `packages = [...]` list, ALL pointing to
#   /path/to/croilar/. This is the wrong path: Python needs the
#   PARENT of /path/to/croilar/ on sys.path so that `import croilar`
#   resolves to /path/to/croilar/__init__.py.
#
# The fix: rewrite the pth file to contain a single line — the
# project's parent directory.
#
# This script is idempotent. Run it manually after every `uv sync`,
# or hook it into the `mise.toml` (e.g. as a postinstall hook in
# `[env] _.python.uv_sync` or via a Makefile target).
set -euo pipefail

REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." >/dev/null 2>&1 && pwd)"
CROILAR_ROOT="${REPO_ROOT}/croilar"
VENV_PTH_DIR="${REPO_ROOT}/.venv/lib/python3.13/site-packages"
PTH_FILE="${VENV_PTH_DIR}/_editable_impl_croilar.pth"

if [[ ! -d "${CROILAR_ROOT}" ]]; then
  echo "ERROR: ${CROILAR_ROOT} does not exist" >&2
  exit 1
fi

if [[ ! -d "${VENV_PTH_DIR}" ]]; then
  echo "ERROR: ${VENV_PTH_DIR} does not exist (no venv at ${REPO_ROOT}/.venv)" >&2
  exit 1
fi

# Write the pth file with the parent of croilar
echo "${REPO_ROOT}" > "${PTH_FILE}"

echo "Rewrote ${PTH_FILE}"
echo "  contains: $(cat "${PTH_FILE}")"
echo
echo "Verifying:"

PYTHON="${REPO_ROOT}/.venv/bin/python"
if [[ ! -x "${PYTHON}" ]]; then
  PYTHON="$(command -v python3)"
fi

"${PYTHON}" -c "
import importlib.util
spec = importlib.util.find_spec('croilar')
if spec is None:
    print('  FAIL: croilar still cannot be imported')
    exit(1)
print(f'  OK: croilar -> {spec.origin}')
spec2 = importlib.util.find_spec('croilar._shared.streams')
if spec2 is None:
    print('  FAIL: croilar._shared.streams still cannot be imported')
    exit(1)
print(f'  OK: croilar._shared.streams -> {spec2.origin}')
"