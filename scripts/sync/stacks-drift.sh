#!/usr/bin/env bash
# Layer 1: detect GOLD_STANDARD violations + name collisions
# Per the 2026-08-15-stacks-sync-loop-v1 change.
set -uo pipefail
mkdir -p stedding/sync-reports
REPORT="stedding/sync-reports/stacks-drift-$(date +%Y-%m-%d).md"
{
  echo "# Stacks Drift Detection Report — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo ""
  echo "## GOLD_STANDARD Violators (the 4 known + any new)"
  echo ""
  total_violators=0
  total_clean=0
  expected_files=("compose.yaml" "sidecar.yaml" "secrets.env" "pangolin.yaml" "blueprint.yaml" ".env.example")
  for stack_dir in bonneagar/stacks/*/; do
    if [ -d "$stack_dir" ]; then
      stack_name=$(basename "$stack_dir")
      # Skip non-stack files (README.md, .DS_Store, etc.)
      if [ ! -f "${stack_dir}compose.yaml" ]; then
        continue
      fi
      missing_files=()
      for f in "${expected_files[@]}"; do
        if [ ! -f "${stack_dir}${f}" ]; then
          missing_files+=("$f")
        fi
      done
      if [ "${#missing_files[@]}" -gt 0 ]; then
        echo "### $stack_name (VIOLATOR)"
        echo "Missing files: ${missing_files[*]}"
        total_violators=$((total_violators + 1))
      else
        total_clean=$((total_clean + 1))
      fi
    fi
  done
  echo ""
  echo "## Name Collisions (fada vs non-fada variants)"
  echo ""
  fada_violators=0
  for d in bonneagar/stacks/*meais*; do
    if [ -d "$d" ]; then
      name=$(basename "$d")
      if [[ "$name" == *"meaisínfhoghlaim"* ]]; then
        echo "- $name (contains fada; may be legacy variant)"
        fada_violators=$((fada_violators + 1))
      fi
    fi
  done
  echo "- fada-variant stacks: $fada_violators"
  echo ""

  echo "## Legacy oideachais/ references (should be 0 after the A2 rename)"
  echo ""
  legacy=0
  for f in $(find bonneagar/stacks -name '*.yaml' -o -name '*.env' 2>/dev/null); do
    if grep -q "oideachais/" "$f" 2>/dev/null; then
      echo "- $f contains oideachais/ reference"
      legacy=$((legacy + 1))
    fi
  done
  echo "- Total legacy oideachais/ refs: $legacy"
  echo ""

  echo "## Summary"
  echo ""
  echo "- Total stacks: $((total_violators + total_clean))"
  echo "- GOLD_STANDARD clean: $total_clean"
  echo "- GOLD_STANDARD violators: $total_violators"
  echo "- fada-variant stacks: $fada_violators"
  echo "- Legacy oideachais/ refs: $legacy"
} > "$REPORT"
cat "$REPORT"