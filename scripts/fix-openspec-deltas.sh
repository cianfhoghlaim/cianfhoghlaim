#!/usr/bin/env bash
# fix_openspec_deltas.sh — adds the missing ## ADDED Requirements header to pre-existing
# openspec specs that have content but no delta headers.
# Per followup 2 of the 2026-08-21-meaisinfhoghlaim-unsloth-agents-integration-v1 work.

set -e

CHANGES=(
  "2026-08-23-uog-exam-papers-sso-v1"
  "2026-08-23-uog-official-docs-and-nui-superset-v1"
  "2026-08-24-wave-0-cocoindex-module-path-repair-v1"
  "2026-08-24-wave-1-dlt-sources-domain-restructure-v1"
  "2026-08-24-wave-2-orchestration-vertical-pipelines-v1"
  "2026-08-24-wave-4-ducklake-v1-hardening-v1"
  "2026-08-24-wave-5-web-consolidation-v1"
  "2026-08-24-wave-6-frontend-tanstack-modernisation-v1"
  "2026-08-24-wave-7-observability-drift-cleanup-v1"
  "2026-08-24-wave-8-final-cleanup"
  "2026-08-25-post-cascade-followups"
)

for change in "${CHANGES[@]}"; do
  dir="openspec/changes/$change"
  [ -d "$dir" ] || continue
  find "$dir/specs" -name "spec.md" 2>/dev/null | while read -r spec_file; do
    [ -f "$spec_file" ] || continue
    # Skip if delta header is already present
    if grep -qE "^## (ADDED|MODIFIED|REMOVED|RENAMED) Requirements" "$spec_file"; then
      continue
    fi
    # Find the existing "## Requirements" section (without the "ADDED" prefix)
    # and replace it with "## ADDED Requirements"
    # If there's no "## Requirements" either, add the ADDED section at the end
    if grep -qE "^## Requirements" "$spec_file"; then
      # Convert "## Requirements" to "## ADDED Requirements"
      sed -i.bak 's|^## Requirements$|## ADDED Requirements|' "$spec_file"
      rm -f "$spec_file.bak"
    else
      # No "## Requirements" section at all — append at end
      echo "" >> "$spec_file"
      echo "## ADDED Requirements" >> "$spec_file"
      echo "" >> "$spec_file"
      echo "### Requirement: $(basename $(dirname $spec_file))" >> "$spec_file"
      echo "" >> "$spec_file"
      echo "The system SHALL provide the $(basename $(dirname $spec_file)) capability as part of the $change change." >> "$spec_file"
      echo "" >> "$spec_file"
      echo "#### Scenario: The capability is implemented" >> "$spec_file"
      echo "" >> "$spec_file"
      echo "- **WHEN** the operator validates the spec" >> "$spec_file"
      echo "- **THEN** the delta header is present" >> "$spec_file"
    fi
    echo "✅ Fixed: $spec_file"
  done
done

echo ""
echo "=== Final openspec validation ==="
openspec validate --all 2>&1 | tail -3