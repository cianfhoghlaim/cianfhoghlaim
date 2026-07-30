#!/usr/bin/env bash
# Layer 5: per-stack health report
# Per the 2026-08-15-stacks-sync-loop-v1 change.
set -uo pipefail
mkdir -p stedding/sync-reports
REPORT="stedding/sync-reports/stacks-health-$(date +%Y-%m-%d).md"
{
  echo "# Stacks Per-Stack Health Report -- $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo ""
  echo "## Per-Stack GOLD_STANDARD Status"
  echo ""
  total=0
  clean=0
  violators=0
  expected_files=("compose.yaml" "sidecar.yaml" "secrets.env" "pangolin.yaml" "blueprint.yaml" ".env.example")
  for stack_dir in bonneagar/stacks/*/; do
    if [ -d "$stack_dir" ]; then
      stack_name=$(basename "$stack_dir")
      if [ ! -f "${stack_dir}compose.yaml" ]; then
        continue
      fi
      missing=()
      for f in "${expected_files[@]}"; do
        if [ ! -f "${stack_dir}${f}" ]; then
          missing+=("$f")
        fi
      done
      total=$((total + 1))
      if [ "${#missing[@]}" -gt 0 ]; then
        status="VIOLATOR (missing: ${missing[*]})"
        violators=$((violators + 1))
      else
        status="OK (all 6 files)"
        clean=$((clean + 1))
      fi
      printf "| %-30s | %s |\n" "$stack_name" "$status"
    fi
  done
  echo ""
  echo "## Summary"
  echo ""
  echo "- Total stacks: $total"
  echo "- GOLD_STANDARD clean: $clean"
  echo "- GOLD_STANDARD violators: $violators"
} > "$REPORT"
cat "$REPORT"
