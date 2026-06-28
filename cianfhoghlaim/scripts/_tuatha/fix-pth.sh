#!/usr/bin/env bash
# sruth/tuatha/scripts/fix-pth.sh — Post-install fix for the broken
# uv editable-install pth file.
#
# The problem (per the same issue as croilar's commit `e9e0fc7d2`):
#   `uv pip install -e .` for a project whose pyproject.toml sits AT
#   the project root (e.g. /path/to/sruth/tuatha/pyproject.toml)
#   generates a `_editable_impl_tuath.pth` file with N lines, one per
#   entry in the pyproject.toml `packages = [...]` list, ALL pointing
#   to /path/to/sruth/tuatha/. This is the wrong path: Python needs
#   the PARENT (`/path/to/sruth/`) on sys.path so that `import tuatha`
#   resolves to /path/to/sruth/tuatha/__init__.py.
#
# The fix: rewrite the pth file to contain a single line — the
# `sruth/` directory (the parent of `tuatha/`).
#
# This script is idempotent. Run it manually after every `uv sync`,
# or hook it into `mise.toml` as a postinstall hook
# (e.g. via `[env] _.python.uv_sync`).
set -euo pipefail

REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../.." >/dev/null 2>&1 && pwd)"
SRUTH_ROOT="${REPO_ROOT}/sruth"
TUATHA_ROOT="${SRUTH_ROOT}/tuatha"
VENV_PTH_DIR="${REPO_ROOT}/.venv/lib/python3.13/site-packages"
PTH_FILE="${VENV_PTH_DIR}/_editable_impl_tuath.pth"

if [[ ! -d "${TUATHA_ROOT}" ]]; then
  echo "ERROR: ${TUATHA_ROOT} does not exist" >&2
  exit 1
fi

if [[ ! -d "${VENV_PTH_DIR}" ]]; then
  echo "ERROR: ${VENV_PTH_DIR} does not exist (no venv at ${REPO_ROOT}/.venv)" >&2
  exit 1
fi

# Write the pth file with sruth/ (parent of tuatha/)
echo "${SRUTH_ROOT}" > "${PTH_FILE}"

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
spec = importlib.util.find_spec('tuatha')
if spec is None:
    print('  FAIL: tuatha still cannot be imported')
    exit(1)
print(f'  OK: tuatha -> {spec.origin}')
spec2 = importlib.util.find_spec('tuatha.api.main')
if spec2 is None:
    print('  FAIL: tuatha.api.main still cannot be imported')
    exit(1)
print(f'  OK: tuatha.api.main -> {spec2.origin}')
# tuatha's cocoindex_flows/ is a sub-package of tuatha; canonical import is
# tuatha.cocoindex_flows.transforms.celtic_multilingual (NOT bare
# cocoindex_flows.transforms.celtic_multilingual, which would resolve to
# oideachais' cocoindex_flows/ tree when sruth/oideachais is on sys.path).
spec3 = importlib.util.find_spec('tuatha.cocoindex_flows.transforms.celtic_multilingual')
if spec3 is None:
    print('  FAIL: tuatha.cocoindex_flows.transforms.celtic_multilingual still cannot be imported')
    exit(1)
print(f'  OK: tuatha.cocoindex_flows.transforms.celtic_multilingual -> {spec3.origin}')
"