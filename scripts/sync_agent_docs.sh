#!/usr/bin/env bash
# =============================================================================
# Automated Project Telemetry & Agent Docs Sync
# =============================================================================
# This script is designed to be run by CLI Agents (like OpenCode or Roo)
# after completing major pipeline or infrastructure milestones.
# It ensures README.md and AGENTS.md are kept up-to-date with actual data volumes.
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🔄 Synchronizing Agent Documentation & Telemetry..."

# 1. Calculate Local Data Volumes
echo "📊 Analyzing local cache volumes..."
EXAM_CACHE_COUNT=$(ls -1 "$PROJECT_ROOT/stedding/ingest_queue/examinations.ie" 2>/dev/null | wc -l || echo 0)
NCCA_CACHE_COUNT=$(ls -1 "$PROJECT_ROOT/stedding/ingest_queue/ncca.ie" 2>/dev/null | wc -l || echo 0)
ONLINE_CACHE_COUNT=$(ls -1 "$PROJECT_ROOT/stedding/ingest_queue/curriculumonline.ie" 2>/dev/null | wc -l || echo 0)
TOTAL_CACHE=$((EXAM_CACHE_COUNT + NCCA_CACHE_COUNT + ONLINE_CACHE_COUNT))

# 2. Update README.md with latest telemetry
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S UTC")

# Check if the telemetry block exists, if not, we append it. If it does, we replace it.
if grep -q "<!-- AGENT_TELEMETRY_START -->" "$PROJECT_ROOT/README.md"; then
    # Use sed to replace everything between the tags
    sed -i '' -e "/<!-- AGENT_TELEMETRY_START -->/,/<!-- AGENT_TELEMETRY_END -->/c\\
<!-- AGENT_TELEMETRY_START -->\\
> **Agent Telemetry (Last Updated: $TIMESTAMP)**\\
> - **Total Cached Structural Documents:** $TOTAL_CACHE\\
> - **Examinations.ie Cache:** $EXAM_CACHE_COUNT files\\
> - **NCCA.ie Cache:** $NCCA_CACHE_COUNT files\\
> - **CurriculumOnline Cache:** $ONLINE_CACHE_COUNT files\\
<!-- AGENT_TELEMETRY_END -->" "$PROJECT_ROOT/README.md"
else
    # Append to README
    echo -e "\n<!-- AGENT_TELEMETRY_START -->\n> **Agent Telemetry (Last Updated: $TIMESTAMP)**\n> - **Total Cached Structural Documents:** $TOTAL_CACHE\n> - **Examinations.ie Cache:** $EXAM_CACHE_COUNT files\n> - **NCCA.ie Cache:** $NCCA_CACHE_COUNT files\n> - **CurriculumOnline Cache:** $ONLINE_CACHE_COUNT files\n<!-- AGENT_TELEMETRY_END -->" >> "$PROJECT_ROOT/README.md"
fi

# 3. Sanity check for bad absolute imports
echo "🔍 Checking for bad absolute imports in data_platform..."
BAD_IMPORTS=$(find "$PROJECT_ROOT/oideachais/data_platform" -type f -name "*.py" -exec grep -l "from oideachais\." {} + || true)
if [ ! -z "$BAD_IMPORTS" ]; then
    echo "⚠️ WARNING: Found rogue absolute imports in the following files:"
    echo "$BAD_IMPORTS"
    echo "Fix these imports to ensure Dagster and DLT do not encounter ModuleNotFoundErrors!"
else
    echo "✅ Import integrity check passed."
fi

echo "✨ Sync complete!"
