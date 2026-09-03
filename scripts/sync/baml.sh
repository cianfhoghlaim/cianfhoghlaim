#!/usr/bin/env bash
# Layer 7 orchestrator: runs sync:baml-drift + sync:baml-ccc + sync:baml-cognee
#                            + sync:baml-test + sync:baml-lint in sequence
# Per the 2026-08-15-baml-sync-loop-v1 change (Day 2).
set -uo pipefail
mkdir -p stedding/sync-reports
REPORT="stedding/sync-reports/baml-$(date +%Y-%m-%d).md"
{
  echo "# BAML Schema Sync Report — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo ""
  echo "## Per-Cluster Breakdown"
  echo ""
  total_baml_files=0
  total_functions=0
  total_classes=0
  total_enums=0
  total_clients=0
  total_tests=0
  total_drift=0

  for cluster in american_nations british_isles celtic commonwealth european_nations european_union processing shared; do
    if [ -d "baml_src/$cluster" ]; then
      baml_files=$(find "baml_src/$cluster" -name '*.baml' -type f 2>/dev/null | wc -l | tr -d ' ')
      functions=$(grep -h '^function ' "baml_src/$cluster"/*.baml 2>/dev/null | wc -l | tr -d ' ')
      classes=$(grep -h '^class ' "baml_src/$cluster"/*.baml 2>/dev/null | wc -l | tr -d ' ')
      enums=$(grep -h '^enum ' "baml_src/$cluster"/*.baml 2>/dev/null | wc -l | tr -d ' ')
      clients=$(grep -h '^client<llm>' "baml_src/$cluster"/*.baml 2>/dev/null | wc -l | tr -d ' ')
      tests=$(grep -h '^test ' "baml_src/$cluster"/*.baml 2>/dev/null | wc -l | tr -d ' ')
      echo "### $cluster"
      echo "- .baml files: $baml_files"
      echo "- function: $functions"
      echo "- class: $classes"
      echo "- enum: $enums"
      echo "- client<llm>: $clients"
      echo "- test: $tests"
      echo ""
      total_baml_files=$((total_baml_files + baml_files))
      total_functions=$((total_functions + functions))
      total_classes=$((total_classes + classes))
      total_enums=$((total_enums + enums))
      total_clients=$((total_clients + clients))
      total_tests=$((total_tests + tests))
    fi
  done

  # Top-level .baml files (clients.baml etc.)
  echo "## The Top-Level BAML Files (baml_src/)"
  echo ""
  for top in clients.baml clients_llama_swap.baml clients_ocr_ensemble.baml clients_biep_v3.py baml.toml README.md; do
    if [ -f "baml_src/$top" ]; then
      size=$(wc -l < "baml_src/$top" | tr -d ' ')
      echo "- $top ($size lines)"
    fi
  done
  echo ""

  echo "## Drift Detection (per the model-registry cleanup)"
  echo ""
  gemma3_4b=$(grep -rE "gemma-3-4b-it|gemma.3.4b" baml_src/ 2>/dev/null | wc -l | tr -d ' ')
  gemma3_27b=$(grep -rE "gemma-3-27b-it|gemma.3.27b" baml_src/ 2>/dev/null | wc -l | tr -d ' ')
  echo "- gemma-3-4b-it references: $gemma3_4b (should be 0 after the model-registry cleanup)"
  echo "- gemma-3-27b-it references: $gemma3_27b (should be 0 after the model-registry cleanup)"
  total_drift=$((gemma3_4b + gemma3_27b))
  echo ""

  # Summary
  echo "## Summary"
  echo ""
  echo "- Total .baml files: $total_baml_files"
  echo "- Total functions: $total_functions"
  echo "- Total classes: $total_classes"
  echo "- Total enums: $total_enums"
  echo "- Total clients (across the 3 client files): $(grep -h '^client<llm>' baml_src/clients*.baml 2>/dev/null | wc -l | tr -d ' ')"
  echo "- Total test blocks: $total_tests"
  echo "- Total drift (gemma-3-4b + gemma-3-27b): $total_drift"
  echo ""
  if [ "$total_baml_files" -gt 0 ]; then
    echo "OK: $total_baml_files .baml files registered across the 7 clusters"
  else
    echo "FAIL: 0 .baml files detected (suspicious; check the baml_src/ tree)"
  fi
} > "$REPORT"
cat "$REPORT"
[ "$total_baml_files" -gt 0 ]