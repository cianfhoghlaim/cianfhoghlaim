#!/usr/bin/env bash
#
# deploy.sh — deploy the 6 per-subject marimo notebooks to Cloudflare
# Workers + Container.
#
# Per openspec/changes/2026-07-18-british-isles-portal-activation-v3/ R15.
#
# Usage:
#   ./deploy.sh                     # deploy all 6 subjects
#   ./deploy.sh mathematics         # deploy a single subject
#   SUBJECT=chemistry ./deploy.sh   # env-var style (single subject)
#
# Prerequisites:
#   - wrangler 3.x installed (bun/npm/pnpm)
#   - Cloudflare account with Workers Paid tier ($5/mo for Containers)
#   - Cloudflare API token in CLOUDFLARE_API_TOKEN env var
#   - Account ID in CLOUDFLARE_ACCOUNT_ID env var
#
# After deployment, the notebooks live at:
#   https://portal-marimo.cianfhoghlaim.ie/<subject>
#
# Subject route mapping (from cross-nation route layout):
#   mathematics     → /mathematics     (EN) + /mata (GA)
#   chemistry       → /chemistry       (EN) + /ceimic (GA)
#   geography       → /geography       (EN) + /tireolaiocht (GA)
#   gaeilge         → /gaeilge         (EN + GA — taught in Irish)
#   english         → /english         (EN) + /bearla (GA)
#   computer_science → /computer-science (EN) + /riomheolaiocht (GA)

set -euo pipefail

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

SUBJECTS_ALL=(
  mathematics
  chemistry
  geography
  gaeilge
  english
  computer_science
)

NOTEBOOK_TEMPLATE='notebooks/12_subject_study_tools/{subject}.py'

# Per-subject URL slug on portal-marimo.cianfhoghlaim.ie
declare -A SUBJECT_SLUG
SUBJECT_SLUG[mathematics]=mathematics
SUBJECT_SLUG[chemistry]=chemistry
SUBJECT_SLUG[geography]=geography
SUBJECT_SLUG[gaeilge]=gaeilge
SUBJECT_SLUG[english]=english
SUBJECT_SLUG[computer_science]=computer-science

CLOUDFLARE_API_TOKEN="${CLOUDFLARE_API_TOKEN:-}"
CLOUDFLARE_ACCOUNT_ID="${CLOUDFLARE_ACCOUNT_ID:-}"

if [ -z "$CLOUDFLARE_API_TOKEN" ] || [ -z "$CLOUDFLARE_ACCOUNT_ID" ]; then
  echo "ERROR: CLOUDFLARE_API_TOKEN + CLOUDFLARE_ACCOUNT_ID must be set" >&2
  exit 1
fi

# ---------------------------------------------------------------------------
# Pick subject(s)
# ---------------------------------------------------------------------------

if [ "$#" -eq 1 ]; then
  SUBJECTS_TO_DEPLOY=("$1")
elif [ -n "${SUBJECT:-}" ]; then
  SUBJECTS_TO_DEPLOY=("$SUBJECT")
else
  SUBJECTS_TO_DEPLOY=("${SUBJECTS_ALL[@]}")
fi

# ---------------------------------------------------------------------------
# Build the container image once, then deploy each subject binding
# ---------------------------------------------------------------------------

echo "==> Building the marimo container image (this takes ~3 minutes)..."
docker build \
  --file notebooks/12_subject_study_tools/Dockerfile \
  --tag cianfhoghlaim/marimo-portal:latest \
  .

for subject in "${SUBJECTS_TO_DEPLOY[@]}"; do
  notebook=$(echo "$NOTEBOOK_TEMPLATE" | sed "s/{subject}/$subject/")
  slug="${SUBJECT_SLUG[$subject]:-$subject}"

  echo "==> Deploying $subject → portal-marimo.cianfhoghlaim.ie/$slug ($notebook)"

  # Stamp the wrangler config for this subject
  sed \
      -e "s|\"SUBJECT\": \"mathematics\"|\"SUBJECT\": \"${subject}\"|g" \
      -e "s|\"NOTEBOOK_PATH\": \"notebooks/12_subject_study_tools/mathematics.py\"|\"NOTEBOOK_PATH\": \"${notebook}\"|g" \
      -e "s|\"name\": \"portal-marimo\"|\"name\": \"portal-marimo-${subject}\"|g" \
      notebooks/12_subject_study_tools/wrangler.jsonc > \
      notebooks/12_subject_study_tools/wrangler.${subject}.jsonc.tmp

  CLOUDFLARE_API_TOKEN="$CLOUDFLARE_API_TOKEN" \
  CLOUDFLARE_ACCOUNT_ID="$CLOUDFLARE_ACCOUNT_ID" \
    wrangler deploy \
      --config notebooks/12_subject_study_tools/wrangler.$subject.jsonc.tmp \
      --name "portal-marimo-$subject" \
      --compatibility-date 2026-07-12

  rm -f notebooks/12_subject_study_tools/wrangler.$subject.jsonc.tmp
done

echo ""
echo "==> Deployment complete. Smoke test with:"
echo "    curl https://portal-marimo.cianfhoghlaim.ie/mathematics"
echo "    curl https://portal-marimo.cianfhoghlaim.ie/gaeilge"
