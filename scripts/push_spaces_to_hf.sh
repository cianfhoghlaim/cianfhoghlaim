#!/usr/bin/env bash
# scripts/push_spaces_to_hf.sh
#
# Push the 4 Spaces from this monorepo to the cianfhoghlaim personal
# HF account as 4 separate Space repos. Run from the monorepo root.
#
# Prereqs (run these first; the script will check):
#   1. Authenticated with HF:  huggingface-cli login
#   2. The venv at .venv/ exists with huggingface_hub installed.
#   3. The 4 Spaces exist as empty repos on HF (created via the Web UI
#      OR the first `huggingface-cli repo create` call in this script
#      will create them for you).
#
# Usage:
#   bash scripts/push_spaces_to_hf.sh
#
# After it finishes, visit each Space on HF and set the HF_TOKEN secret.

set -euo pipefail

# -- 0. Resolve the monorepo root (parent of this script's dir) ---------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
HF="${ROOT}/.venv/bin/huggingface-cli"

# -- 1. Preflight checks ------------------------------------------------
if [[ ! -x "${HF}" ]]; then
    echo "ERROR: huggingface-cli not found at ${HF}" >&2
    echo "Run: uv pip install -p .venv huggingface_hub" >&2
    exit 1
fi

if ! "${HF}" whoami &>/dev/null; then
    echo "ERROR: not authenticated. Run: ${HF} login" >&2
    echo "   Use a write-enabled token (Settings -> Access Tokens -> New)" >&2
    echo "   Grant scope: write" >&2
    exit 1
fi

HF_USER="$(${HF} whoami | head -1 | awk '{print $2}')"
echo "Authenticated as: ${HF_USER}"
echo

if [[ "${HF_USER}" != "cianfhoghlaim" ]]; then
    echo "WARNING: expected 'cianfhoghlaim', got '${HF_USER}'." >&2
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    [[ "${REPLY}" =~ ^[Yy]$ ]] || exit 1
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

# Pinned versions for reproducibility
GRADIO_VERSION="4.44.0"
HF_HUB_VERSION="0.24.0"

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

    # Add a top-level README if the Space doesn't have one with HF frontmatter
    if ! head -3 "${stage}/README.md" 2>/dev/null | grep -q "^---"; then
        cat > "${stage}/README.md.new" <<EOF
---
title: ${slug}
emoji: "\U0001F30D"
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: ${GRADIO_VERSION}
app_file: app.py
pinned: false
license: apache-2.0
short_description: Build Small 2026 submission
---

# ${slug}

\`\`\`
$(cat "${stage}/README.md" 2>/dev/null || echo "(see spaces/${local_dir}/README.md in the monorepo)")
\`\`\`
EOF
        mv "${stage}/README.md.new" "${stage}/README.md"
    fi

    # Make sure the .py files are executable
    find "${stage}" -name "*.py" -exec chmod +x {} \;

    # -- 4a. Create the empty HF Space repo (no error if exists) -----
    echo
    echo "Creating (or reusing) HF repo: ${full_slug}"
    "${HF}" repo create "${full_slug}" \
        --type space \
        --space_sdk gradio \
        --exist-ok 2>&1 | sed 's/^/  /'

    # -- 4b. Init git in the staging dir and push -------------------
    pushd "${stage}" >/dev/null
    git init -q
    git checkout -q -b main
    git config user.name "cianfhoghlaim"
    git config user.email "cianfhoghlaim@users.noreply.huggingface.co"
    git add .
    if git diff --cached --quiet; then
        echo "  (no changes to commit)"
    else
        git commit -q -m "Initial Space push (Build Small 2026 submission)"
    fi

    # Add the HF remote + push
    git remote remove origin 2>/dev/null || true
    HF_URL="https://huggingface.co/spaces/${full_slug}"
    git remote add origin "${HF_URL}"
    echo "  pushing to ${HF_URL}"
    git push -q -u origin main 2>&1 | sed 's/^/  /'
    popd >/dev/null

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
