#!/usr/bin/env bash
# scripts/push_spaces_to_hf.sh
#
# Push the 4 Spaces from this monorepo to the cianfhoghlaim personal
# HF account as 4 separate Space repos. Run from the monorepo root.
#
# Uses the modern `hf` CLI (huggingface_hub >= 1.2). The old
# `huggingface-cli` is deprecated; `hf` is the new entry point.
#
# Prereqs:
#   1. Authenticated:  hf auth login
#   2. The venv at .venv/ has huggingface_hub >= 1.13 installed
#      with typer<0.16 (or hf upgraded to the version that matches
#      the installed typer).
#
# Usage:
#   bash scripts/push_spaces_to_hf.sh
#
# After it finishes, visit each Space on HF and set the HF_TOKEN
# secret at /spaces/<slug>/settings.

set -euo pipefail

# -- 0. Resolve the monorepo root (parent of this script's dir) ---------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
HF="${ROOT}/.venv/bin/hf"

# -- 1. Preflight checks ------------------------------------------------
if [[ ! -x "${HF}" ]]; then
    echo "ERROR: hf CLI not found at ${HF}" >&2
    echo "Run: uv pip install --python .venv/bin/python3 huggingface_hub" >&2
    exit 1
fi

# Verify the CLI works (catches the typer<0.16 / typer>=0.16 mismatch
# that silently breaks the deprecation-warning fix)
if ! "${HF}" --help >/dev/null 2>&1; then
    echo "ERROR: hf CLI is broken (likely a typer version mismatch)." >&2
    echo "Fix: uv pip install --python .venv/bin/python3 'typer<0.16'" >&2
    echo "  OR upgrade: uv pip install --python .venv/bin/python3 --upgrade huggingface_hub" >&2
    "${HF}" --help 2>&1 | head -3
    exit 1
fi

# Auth check
if ! "${HF}" auth whoami >/dev/null 2>&1; then
    echo "ERROR: not authenticated. Run: ${HF} auth login" >&2
    echo "   Get a write-enabled token at https://huggingface.co/settings/tokens" >&2
    echo "   Grant scope: write" >&2
    exit 1
fi

HF_USER="$(${HF} auth whoami 2>/dev/null | head -1 | awk '{print $2}')"
if [[ -z "${HF_USER}" ]]; then
    # Fallback: try the JSON output
    HF_USER="$(${HF} auth whoami 2>/dev/null | grep -oE '"name": "[^"]+"' | head -1 | cut -d'"' -f4)"
fi
echo "Authenticated as: ${HF_USER}"
echo

if [[ "${HF_USER}" != "cianfhoghlaim" ]]; then
    echo "WARNING: expected 'cianfhoghlaim', got '${HF_USER}'." >&2
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    case "${REPLY}" in
        [Yy]|[Yy][Ee][Ss]) ;;
        *) exit 1 ;;
    esac
fi

# -- 2. The 4 Space definitions ----------------------------------------
# Format: "local_dir|space_slug"
SPACES=(
    "spaces/an_scrudu|an-scrudu"
    "spaces/meaisin_cliste|meaisin-cliste"
    "spaces/cianfhoghlaim|cianfhoghlaim"
    "spaces/anam_tuatha|anam-tuatha"
)

# -- 3. Create a per-Space staging dir with _common bundled in ---------
STAGING="${ROOT}/.hf-spaces-staging"
rm -rf "${STAGING}"
mkdir -p "${STAGING}"

# -- 4. Per-Space work loop --------------------------------------------
for entry in "${SPACES[@]}"; do
    local_dir="${entry%|*}"
    slug="${entry#*|}"
    src="${ROOT}/${local_dir}"
    stage="${STAGING}/${slug}"
    full_slug="${HF_USER}/${slug}"

    echo "=================================================="
    echo "Building stage for: ${full_slug}"
    echo "  from: ${src}"
    echo "=================================================="

    mkdir -p "${stage}"

    # Copy the Space's own files (not _common, which we add separately)
    rsync -a --exclude='_common' "${src}/" "${stage}/"

    # Copy the shared bundle into the Space
    rsync -a "${ROOT}/spaces/_common/" "${stage}/_common/"

    # Make sure the social card made it
    if [[ -f "${src}/social_card.png" ]]; then
        cp "${src}/social_card.png" "${stage}/"
    fi

    # -- 4a. Create the empty HF Space repo (no error if exists) -----
    echo
    echo "Creating (or reusing) HF repo: ${full_slug}"
    "${HF}" repos create "${full_slug}" \
        --type space \
        --space-sdk gradio \
        --exist-ok 2>&1 | sed 's/^/  /'

    # -- 4b. Upload the staging dir to the Space via hf upload ------
    # This is the modern replacement for `git init && git push`.
    # It handles the git LFS setup, .gitattributes, and the commit
    # in one call.
    echo
    echo "Uploading ${stage}/ -> ${full_slug}"
    "${HF}" upload "${full_slug}" "${stage}" "." \
        --repo-type space \
        --commit-message "Initial Space push (Build Small 2026 submission)" \
        --commit-description "4 Celtic AI Spaces from cianfhoghlaim/kings_college_galway" \
        2>&1 | sed 's/^/  /'

    echo "  -> DONE: ${full_slug}"
    echo
done

# -- 5. Reminders for secrets -----------------------------------------
echo "=================================================="
echo "All 4 Spaces pushed. Now go set secrets on each:"
echo "=================================================="
for entry in "${SPACES[@]}"; do
    slug="${entry#*|}"
    echo "  https://huggingface.co/spaces/${HF_USER}/${slug}/settings"
done
echo
echo "For each Space, add this secret:"
echo "  Name:  HF_TOKEN"
echo "  Value: <your HF token with inference permissions>"
echo
echo "Without HF_TOKEN, the Spaces will run but fall back to the"
echo "offline regex/template paths in each module (the demo still works)."
echo
echo "Cleanup: rm -rf ${STAGING}"
