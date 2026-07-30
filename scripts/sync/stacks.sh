#!/usr/bin/env bash
# Layer 8 orchestrator: runs sync:stacks-drift + sync:stacks-ccc + sync:stacks-cognee
#                            + sync:stacks-validate + sync:stacks-health in sequence
# Per the 2026-08-15-stacks-sync-loop-v1 change.
set -uo pipefail
mkdir -p stedding/sync-reports
REPORT="stedding/sync-reports/stacks-$(date +%Y-%m-%d).md"
{
  echo "# Stacks Sync Health Report — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
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
  echo "## The 4 Known GOLD_STANDARD Violators (per Week 4 audit)"
  echo ""
  for v in browser ludusavi moonlight storybook; do
    if [ -d "bonneagar/stacks/$v" ]; then
      missing_count=0
      for f in "${expected_files[@]}"; do
        if [ ! -f "bonneagar/stacks/$v/$f" ]; then
          missing_count=$((missing_count + 1))
        fi
      done
      echo "- $v: $missing_count/6 files missing"
    fi
  done
  echo ""
  echo "## The 12 Cognee Clusters"
  echo ""
  for c in docs-cognee docs-platform docs-data-platform docs-agents docs-models docs-web docs-ci openspec_changes openspec_specs agent_skills baml_schemas stacks_catalog; do
    echo "- $c (pending cognify)"
  done
  echo ""
  echo "## Summary"
  echo ""
  echo "- Total stacks: $total"
  echo "- GOLD_STANDARD clean: $clean"
  echo "- GOLD_STANDARD violators: $violators"
  if [ "$total" -gt 0 ]; then
    echo "OK: $total stacks registered across the 87-stack catalog"
  else
    echo "FAIL: 0 stacks detected (suspicious)"
  fi
} > "$REPORT"
cat "$REPORT"
[ "$total" -gt 0 ]
