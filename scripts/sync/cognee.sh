#!/usr/bin/env bash
# Layer 3: ingest 8 cianfhoghlaim-scope Cognee clusters.
# Per the 2026-08-15-knowledge-sync-loop-v1 change (Layers 1-5) +
# the 2026-08-15-baml-sync-loop-v1 change (Layer 7) +
# the 2026-08-15-stacks-sync-loop-v1 change (Layer 8) +
# the 2026-08-15-agent-definitions-sync-loop-v1 change (Layer 10) +
# the 2026-08-15-notebooks-sync-loop-v1 change (Layer 11) +
# the 2026-08-24-dlt-sources-to-multi-repo-scaffold-v1 change (Phase 0.8).
#
# 8 cianfhoghlaim-scope clusters:
#   1. openspec_changes    -- 78 in cianfhoghlaim/openspec/changes/ + 4 in cwd openspec/changes/
#   2. baml_schemas        -- 334 .baml files in baml_src/
#   3. dagster_assets      -- 89 .py files in orchestration/defs/
#   4. agents              -- 168 .py files in agents/
#   5. dlt_sources         -- 2173 .py files in dlt_sources/
#   6. notebooks           -- 245 .py/.ipynb/.md files in notebooks/
#   7. stacks              -- 109 compose.yaml + 6-file GOLD_STANDARD at bonneagar/stacks/
#   8. firecrawl_concepts  -- 35 concept guides at .cocoindex_code/guides.yml
#
# Per-cluster sub-tasks:
#   mise run sync:cognee:openspec_changes
#   mise run sync:cognee:baml_schemas
#   mise run sync:cognee:dagster_assets
#   mise run sync:cognee:agents
#   mise run sync:cognee:dlt_sources
#   mise run sync:cognee:notebooks
#   mise run sync:cognee:stacks
#   mise run sync:cognee:firecrawl_concepts
#
# Each per-cluster sub-task delegates to scripts/cognee_ingest_<cluster>.py.
# The orchestrator (sync:cognee) runs all 8 in sequence.
set -uo pipefail
mkdir -p stedding/sync-reports
REPORT="stedding/sync-reports/cognee-$(date +%Y-%m-%d).md"
DATE="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
{
  echo "# Cognee Cluster Population Report -- ${DATE}"
  echo ""
  echo "## 8 cianfhoghlaim-scope clusters (per the 2026-08-24-dlt-sources-to-multi-repo-scaffold-v1 change Phase 0.8)"
  echo ""
  printf "| %-22s | %-40s | %-12s |\n" "Cluster" "Source" "Ingestion script"
  printf "| %-22s | %-40s | %-12s |\n" "-------" "------" "---------------"
  printf "| %-22s | %-40s | %-12s |\n" "openspec_changes" "78 + 4 proposal.md" "cognee_ingest_openspec.py"
  printf "| %-22s | %-40s | %-12s |\n" "baml_schemas" "334 baml_src/**/*.baml" "cognee_ingest_baml_schemas.py"
  printf "| %-22s | %-40s | %-12s |\n" "dagster_assets" "89 orchestration/defs/**/*.py" "sync_dagster_assets_to_cognee.py"
  printf "| %-22s | %-40s | %-12s |\n" "agents" "168 agents/**/*.py" "cognee_ingest_agent_definitions.py"
  printf "| %-22s | %-40s | %-12s |\n" "dlt_sources" "2173 dlt_sources/**/*.py" "cognee_ingest_dlt_sources.py"
  printf "| %-22s | %-40s | %-12s |\n" "notebooks" "245 notebooks/**/*.{py,ipynb,md}" "cognee_ingest_notebooks.py"
  printf "| %-22s | %-40s | %-12s |\n" "stacks" "109 bonneagar/stacks/**/compose.yaml" "cognee_ingest_stacks_catalog.py"
  printf "| %-22s | %-40s | %-12s |\n" "firecrawl_concepts" ".cocoindex_code/guides.yml" "cognee_ingest_firecrawl_concepts.py"
  echo ""
  echo "## Per-cluster file count + estimated entity count"
  echo ""
  printf "| %-22s | %8s | %12s | %12s |\n" "Cluster" "Files" "Est entities" "Est relations"
  printf "| %-22s | %8s | %12s | %12s |\n" "-------" "-----" "-----------" "------------"
  oc_files=$(find /Users/cianmacandeisigh/dev/cianfhoghlaim/openspec/changes -maxdepth 2 -name 'proposal.md' 2>/dev/null | wc -l | tr -d ' ')
  cwd_oc_files=$(find /Users/cianmacandeisigh/dev/kings_college_galway/openspec/changes -maxdepth 2 -name 'proposal.md' 2>/dev/null | wc -l | tr -d ' ')
  oc_total=$((oc_files + cwd_oc_files))
  printf "| %-22s | %8s | %12s | %12s |\n" "openspec_changes" "$oc_total" "$oc_total" "$((oc_total * 5))"
  baml_files=$(find /Users/cianmacandeisigh/dev/cianfhoghlaim/baml_src -name '*.baml' 2>/dev/null | wc -l | tr -d ' ')
  baml_entities=$(find /Users/cianmacandeisigh/dev/cianfhoghlaim/baml_src -name '*.baml' 2>/dev/null | xargs grep -c '^function\|^class\|^client ' 2>/dev/null | awk -F: '{s+=$NF}END{print s+0}')
  printf "| %-22s | %8s | %12s | %12s |\n" "baml_schemas" "$baml_files" "$baml_entities" "$((baml_entities * 3))"
  dag_files=$(find /Users/cianmacandeisigh/dev/cianfhoghlaim/orchestration/defs -name '*.py' -type f 2>/dev/null | wc -l | tr -d ' ')
  dag_entities=$(find /Users/cianmacandeisigh/dev/cianfhoghlaim/orchestration/defs -name '*.py' -type f 2>/dev/null | xargs grep -c '@asset\|@multi_asset\|@asset_check\|@sensor\|@job\|@schedule\|Definitions' 2>/dev/null | awk -F: '{s+=$NF}END{print s+0}')
  printf "| %-22s | %8s | %12s | %12s |\n" "dagster_assets" "$dag_files" "$dag_entities" "$((dag_entities * 2))"
  agent_files=$(find /Users/cianmacandeisigh/dev/cianfhoghlaim/agents -name '*.py' -type f 2>/dev/null | wc -l | tr -d ' ')
  agent_entities=$(find /Users/cianmacandeisigh/dev/cianfhoghlaim/agents -name '*.py' -type f 2>/dev/null | xargs grep -c '^class \|^def [a-z]\|^@' 2>/dev/null | awk -F: '{s+=$NF}END{print s+0}')
  printf "| %-22s | %8s | %12s | %12s |\n" "agents" "$agent_files" "$agent_entities" "$((agent_entities * 3))"
  dlt_files=$(find /Users/cianmacandeisigh/dev/cianfhoghlaim/dlt_sources -name '*.py' -type f 2>/dev/null | wc -l | tr -d ' ')
  dlt_entities=$(find /Users/cianmacandeisigh/dev/cianfhoghlaim/dlt_sources -name '*.py' -type f 2>/dev/null | xargs grep -c '@dlt.source\|@dlt.resource' 2>/dev/null | awk -F: '{s+=$NF}END{print s+0}')
  printf "| %-22s | %8s | %12s | %12s |\n" "dlt_sources" "$dlt_files" "$dlt_entities" "$((dlt_entities * 3 / 2))"
  nb_py=$(find /Users/cianmacandeisigh/dev/cianfhoghlaim/notebooks -name '*.py' -type f 2>/dev/null | wc -l | tr -d ' ')
  nb_ipynb=$(find /Users/cianmacandeisigh/dev/cianfhoghlaim/notebooks -name '*.ipynb' -type f 2>/dev/null | wc -l | tr -d ' ')
  nb_md=$(find /Users/cianmacandeisigh/dev/cianfhoghlaim/notebooks -name '*.md' -type f 2>/dev/null | wc -l | tr -d ' ')
  nb_files=$((nb_py + nb_ipynb + nb_md))
  printf "| %-22s | %8s | %12s | %12s |\n" "notebooks" "$nb_files" "$nb_files" "$((nb_files * 2))"
  stack_files=$(find /Users/cianmacandeisigh/dev/cianfhoghlaim/bonneagar/stacks -maxdepth 4 -name 'compose.yaml' 2>/dev/null | wc -l | tr -d ' ')
  printf "| %-22s | %8s | %12s | %12s |\n" "stacks" "$stack_files" "$stack_files" "$((stack_files * 5))"
  fc_guides=$(grep -c '^- title:' /Users/cianmacandeisigh/dev/cianfhoghlaim/.cocoindex_code/guides.yml 2>/dev/null || echo 0)
  printf "| %-22s | %8s | %12s | %12s |\n" "firecrawl_concepts" "$fc_guides" "$fc_guides" "$((fc_guides * 3))"
  echo ""
  echo "## Per-cluster ingestion sub-tasks (mise run sync:cognee:<cluster>)"
  echo ""
  for cluster in openspec_changes baml_schemas dagster_assets agents dlt_sources notebooks stacks firecrawl_concepts; do
    echo "- mise run sync:cognee:${cluster}"
  done
  echo ""
  echo "## Installation"
  echo ""
  echo "Cognee 1.5.3 CLI: \`uvx --from cognee cognee-cli\`"
  echo "Cognee MCP server: \`uvx cognee-mcp\` (configured in opencode.json mcp.cognee)"
  echo "Cognee Python API: \`uv run --with cognee python -m ...\`"
  echo ""
  echo "Note: full cognify requires an LLM API key (set via LLM_API_KEY env var or the cognee MCP env block)."
  echo "Without an LLM key, the dataset registration via the MCP server still works (creates the cluster);"
  echo "the per-file cognify step (entity extraction + relation detection + embedding) does not."
} > "$REPORT"
cat "$REPORT"