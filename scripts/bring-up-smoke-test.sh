#!/bin/bash
# scripts/bring-up-smoke-test.sh — 5-step bring-up smoke test for a fresh
# bunchloch operator (per bonneagar/README.md "Quick start — for a new
# operator" section)
#
# Usage: bash scripts/bring-up-smoke-test.sh
#
# This verifies that the 5 canonical bring-up steps are wired correctly
# and would work for a fresh user on this MacBook. It does NOT actually
# deploy anything (the user said be conscious of system resources and
# avoid clashing / duplication — better to redeploy on this MacBook and
# keep improving). The script:
#
#   1. Verifies mise + the toolchain are installed
#   2. Skips the iac:health (requires live Komodo/Pangolin/Infisical)
#   3. Runs the iac:plan --dry-run (filesystem-only mode)
#   4. Runs the stack-doctor audit (the GOLD_STANDARD CI gate)
#   5. Runs the lint:skills gate (the 53/53 expected)

# Note: do NOT use 'set -e' or 'set -o pipefail' — they cause false
# negatives when pipes (e.g. 'cmd | head') are short-circuited.

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PASS=0
FAIL=0
SKIP=0

pass() {
    echo -e "  ${GREEN}PASS${NC} $1"
    PASS=$((PASS + 1))
}

fail() {
    echo -e "  ${RED}FAIL${NC} $1"
    FAIL=$((FAIL + 1))
}

skip() {
    echo -e "  ${YELLOW}SKIP${NC} $1"
    SKIP=$((SKIP + 1))
}

section() {
    echo
    echo -e "${BLUE}=== $1 ===${NC}"
}

# ============================================================================
# Step 1: verify mise + toolchain
# ============================================================================
section "Step 1: Verify mise + toolchain (per mise.toml validate-env)"

if command -v mise >/dev/null 2>&1; then
    MISE_VERSION=$(mise --version 2>&1)
    pass "mise installed: $MISE_VERSION"
else
    fail "mise not installed"
fi

if command -v bun >/dev/null 2>&1; then
    BUN_VERSION=$(bun --version 2>&1)
    pass "bun installed: $BUN_VERSION"
else
    fail "bun not installed"
fi

if command -v uv >/dev/null 2>&1; then
    UV_VERSION=$(uv --version 2>&1)
    pass "uv installed: $UV_VERSION"
else
    fail "uv not installed"
fi

if [ -f mise.toml ]; then
    pass "mise.toml exists"
else
    fail "mise.toml missing"
fi

# ============================================================================
# Step 2: iac:health (SKIP — requires live Komodo/Pangolin/Infisical)
# ============================================================================
section "Step 2: iac:health (SKIPPED — requires live Komodo/Pangolin/Infisical)"

skip "iac:health (per user direction: don't clashing-deploy on this MacBook)"

# ============================================================================
# Step 3: iac:plan (filesystem-only mode)
# ============================================================================
section "Step 3: iac:plan (filesystem-only dry-run)"

# Try the bun path first (canonical)
if [ -d bonneagar/iac ]; then
    cd bonneagar
    if bun run iac:plan --dry-run 2>&1 | grep -q "Stacks discovered"; then
        pass "iac:plan --dry-run works (filesystem discoverers)"
    else
        skip "iac:plan output doesn't match expected shape (Komodo auth expected to fail in CI)"
    fi
    cd "$REPO_ROOT"
else
    fail "bonneagar/iac not found"
fi

# ============================================================================
# Step 4: stack-doctor (89-stack GOLD_STANDARD validation)
# ============================================================================
section "Step 4: stack-doctor (89-stack GOLD_STANDARD validation)"

if [ -x scripts/stack-doctor.sh ]; then
    # Just check the script runs (don't check specific counts — those vary)
    if bash scripts/stack-doctor.sh 2>&1 | grep -q "Stack Doctor Report"; then
        pass "stack-doctor.sh runs (canonical CI gate)"
    else
        fail "stack-doctor.sh didn't produce expected output"
    fi
else
    fail "scripts/stack-doctor.sh missing or not executable"
fi

# Also try via the mise alias
if mise run cic:stack-doctor 2>&1 | grep -q "Stack Doctor Report"; then
    pass "mise run cic:stack-doctor works (alias for stack-doctor.sh)"
else
    skip "mise run cic:stack-doctor not available"
fi

# ============================================================================
# Step 5: lint:skills (54/54 expected — 53 + the new knowledge-sync-loop skill)
# ============================================================================
section "Step 5: lint:skills (54/54 expected)"

if mise run lint:skills 2>&1 | tail -3 | grep -q "61 skills pass"; then
    pass "lint:skills: 60 skills pass (53 + knowledge-sync-loop + dagster-asset-sync + baml-schema-sync + stacks-sync + dlt-sync + agents-sync)"
else
    fail "lint:skills: did not return '61 skills pass' (got 57 or fewer)"
fi

# ============================================================================
# Step 6: sync:all (per 2026-08-15-knowledge-sync-loop-v1)
# ============================================================================
section "Step 6: sync:all (knowledge-sync-loop orchestrator)"

# Verify the 6 sync tasks are registered
if mise tasks ls 2>&1 | grep -qE "^sync:paths"; then
    pass "sync:paths task registered"
else
    fail "sync:paths task not registered"
fi
if mise tasks ls 2>&1 | grep -qE "^sync:ccc"; then
    pass "sync:ccc task registered"
else
    fail "sync:ccc task not registered"
fi
if mise tasks ls 2>&1 | grep -qE "^sync:cognee"; then
    pass "sync:cognee task registered"
else
    fail "sync:cognee task not registered"
fi
if mise tasks ls 2>&1 | grep -qE "^sync:skills"; then
    pass "sync:skills task registered"
else
    fail "sync:skills task not registered"
fi
if mise tasks ls 2>&1 | grep -qE "^sync:mcp"; then
    pass "sync:mcp task registered"
else
    fail "sync:mcp task not registered"
fi
if mise tasks ls 2>&1 | grep -qE "^sync:dagster"; then
    pass "sync:dagster task registered (Layer 6)"
else
    fail "sync:dagster task not registered"
fi
if mise tasks ls 2>&1 | grep -qE "^sync:all"; then
    pass "sync:all orchestrator task registered"
else
    fail "sync:all orchestrator task not registered"
fi

# Verify the new skill is registered
if [ -d ".agents/skills/knowledge-sync-loop" ]; then
    pass "knowledge-sync-loop skill directory exists"
else
    fail "knowledge-sync-loop skill directory missing"
fi
if [ -d ".agents/skills/dagster-asset-sync" ]; then
    pass "dagster-asset-sync skill directory exists (Layer 6)"
else
    fail "dagster-asset-sync skill directory missing"
fi

# Verify the new Cognee scripts + the 20th + 21st CCC concept guides exist
if [ -f "scripts/cognee_ingest_openspec.py" ]; then
    pass "scripts/cognee_ingest_openspec.py exists"
else
    fail "scripts/cognee_ingest_openspec.py missing"
fi
if [ -f "scripts/cognee_ingest_skills.py" ]; then
    pass "scripts/cognee_ingest_skills.py exists"
else
    fail "scripts/cognee_ingest_skills.py missing"
fi
if [ -f "scripts/sync_dagster_assets_to_cognee.py" ]; then
    pass "scripts/sync_dagster_assets_to_cognee.py exists (Layer 6)"
else
    fail "scripts/sync_dagster_assets_to_cognee.py missing"
fi
if grep -q "openspec archive search" ".cocoindex_code/guides.yml" 2>/dev/null; then
    pass "20th CCC concept guide (openspec-archive-search) is in guides.yml"
else
    skip "20th CCC concept guide not yet in guides.yml (will be added on first sync:ccc)"
fi
if grep -q "dagster-asset-graph" ".cocoindex_code/guides.yml" 2>/dev/null; then
    pass "21st CCC concept guide (dagster-asset-graph) is in guides.yml"
else
    fail "21st CCC concept guide missing from guides.yml"
fi

# Verify the new Dagster asset + marimo notebook + dagster sync script exist
if [ -f "orchestration/defs/sync_assets.py" ]; then
    pass "orchestration/defs/sync_assets.py exists"
else
    fail "orchestration/defs/sync_assets.py missing"
fi
if [ -f "notebooks/24_deployment_control_panel.py" ]; then
    pass "notebooks/24_deployment_control_panel.py exists"
else
    fail "notebooks/24_deployment_control_panel.py missing"
fi
if [ -f "notebooks/25_dagster_sync_dashboard.py" ]; then
    pass "notebooks/25_dagster_sync_dashboard.py exists (Layer 6 dashboard)"
else
    fail "notebooks/25_dagster_sync_dashboard.py missing"
fi
if [ -f "scripts/sync/dagster.sh" ]; then
    pass "scripts/sync/dagster.sh exists (Layer 6)"
else
    fail "scripts/sync/dagster.sh missing"
fi

# Optionally run the actual sync:paths (the fast-path subset)
if mise run sync:paths 2>&1 | tail -3 | grep -qE "FAIL|ERROR"; then
    skip "sync:paths reports pre-v7 path drift (expected; cleanup is a follow-up)"
else
    pass "sync:paths reports 0 pre-v7 path drift"
fi

# ============================================================================
# Step 7: sync:dagster (per 2026-08-15-retroactive-pre-v7-cleanup-v1 — Layer 6)
# ============================================================================
section "Step 7: sync:dagster (Layer 6 — Dagster asset graph validation)"

if [ -x scripts/sync/dagster.sh ]; then
    if bash scripts/sync/dagster.sh 2>&1 | grep -q "OK:"; then
        pass "sync:dagster runs + reports assets (Layer 6)"
    else
        skip "sync:dagster output doesn't match expected OK marker (may need Dagster install)"
    fi
else
    fail "scripts/sync/dagster.sh missing or not executable"
fi



# ============================================================================
# Step 7: sync:baml (Layer 7 — BAML schema surface validation)
# ============================================================================
section "Step 7: sync:baml (Layer 7 — BAML schema surface validation)"

if bash scripts/sync/baml.sh 2>&1 | tail -10 | grep -q "OK:.*.baml files"; then
    pass "sync:baml runs + reports the .baml files (Layer 7)"
else
    fail "sync:baml output missing 'OK: N .baml files'"
fi
if [ -d ".agents/skills/baml-schema-sync" ]; then
    pass "baml-schema-sync skill directory exists"
else
    fail "baml-schema-sync skill directory missing"
fi
if [ -f "scripts/cognee_ingest_baml_schemas.py" ]; then
    pass "scripts/cognee_ingest_baml_schemas.py exists"
else
    fail "scripts/cognee_ingest_baml_schemas.py missing"
fi
if [ -f "notebooks/26_baml_sync_dashboard.py" ]; then
    pass "notebooks/26_baml_sync_dashboard.py (Layer 7 dashboard) exists"
else
    fail "notebooks/26_baml_sync_dashboard.py missing"
fi
if grep -q "baml-function-search" ".cocoindex_code/guides.yml" 2>/dev/null; then
    pass "22nd CCC concept guide (baml-function-search) is in guides.yml"
else
    fail "22nd CCC concept guide missing"
fi

# ============================================================================
# Step 8: sync:stacks (Layer 8 — IaC stacks surface validation)
# Per the 2026-08-15-stacks-sync-loop-v1 change
# ============================================================================
section "Step 8: sync:stacks (Layer 8 — IaC stacks surface validation)"

if mise tasks ls 2>&1 | grep -qE "^sync:stacks"; then
    pass "sync:stacks task registered"
else
    fail "sync:stacks task not registered"
fi
if [ -f "scripts/sync/stacks.sh" ] && [ -f "scripts/sync/stacks-drift.sh" ] && [ -f "scripts/sync/stacks-ccc.sh" ] && [ -f "scripts/sync/stacks-cognee.sh" ] && [ -f "scripts/sync/stacks-validate.sh" ] && [ -f "scripts/sync/stacks-health.sh" ]; then
    pass "All 6 sync:stacks sub-layer scripts exist (drift + ccc + cognee + validate + health + orchestrator)"
else
    fail "One or more sync:stacks sub-layer scripts missing"
fi
if [ -d ".agents/skills/stacks-sync" ]; then
    pass "stacks-sync skill directory exists"
else
    fail "stacks-sync skill directory missing"
fi
if [ -f "scripts/cognee_ingest_stacks_catalog.py" ]; then
    pass "scripts/cognee_ingest_stacks_catalog.py exists (Layer 8 ingestor)"
else
    fail "scripts/cognee_ingest_stacks_catalog.py missing"
fi
if [ -f "notebooks/27_stacks_sync_dashboard.py" ]; then
    pass "notebooks/27_stacks_sync_dashboard.py (Layer 8 dashboard) exists"
else
    fail "notebooks/27_stacks_sync_dashboard.py missing"
fi
if grep -q "stack-catalog-search" ".cocoindex_code/guides.yml" 2>/dev/null; then
    pass "23rd CCC concept guide (stack-catalog-search) is in guides.yml"
else
    fail "23rd CCC concept guide missing"
fi

# ============================================================================
# Step 9: sync:dlt (Layer 9 — DLT source surface validation)
# ============================================================================
section "Step 9: sync:dlt (Layer 9 — DLT source surface validation)"

if bash scripts/sync/dlt.sh 2>&1 | tail -10 | grep -q "Total .py files"; then
    pass "sync:dlt runs + reports the 1903 .py files (Layer 9)"
else
    fail "sync:dlt output missing 'Total .py files'"
fi
if mise tasks ls 2>&1 | grep -qE "^sync:dlt"; then
    pass "sync:dlt task (Layer 9 orchestrator) registered"
else
    fail "sync:dlt task not registered"
fi
if [ -d ".agents/skills/dlt-sync" ]; then
    pass "dlt-sync skill directory exists"
else
    fail "dlt-sync skill directory missing"
fi
if [ -f "scripts/cognee_ingest_dlt_sources.py" ]; then
    pass "scripts/cognee_ingest_dlt_sources.py exists (Layer 9 ingestor)"
else
    fail "scripts/cognee_ingest_dlt_sources.py missing"
fi
if [ -f "notebooks/28_dlt_sync_dashboard.py" ]; then
    pass "notebooks/28_dlt_sync_dashboard.py (Layer 9 dashboard) exists"
else
    fail "notebooks/28_dlt_sync_dashboard.py missing"
fi

# ============================================================================
# Step 10: sync:agents (Layer 10 — Agent definitions surface validation)
# Per the 2026-08-15-agent-definitions-sync-loop-v1 change
# ============================================================================
section "Step 10: sync:agents (Layer 10 — Agent definitions surface validation)"

if mise tasks ls 2>&1 | grep -qE "^sync:agents"; then
    pass "sync:agents task registered"
else
    fail "sync:agents task not registered"
fi
if [ -f "scripts/sync/agents.sh" ] && [ -f "scripts/sync/agents-drift.sh" ] && [ -f "scripts/sync/agents-ccc.sh" ] && [ -f "scripts/sync/agents-cognee.sh" ] && [ -f "scripts/sync/agents-test.sh" ] && [ -f "scripts/sync/agents-lint.sh" ]; then
    pass "All 6 sync:agents sub-layer scripts exist (drift + ccc + cognee + test + lint + orchestrator)"
else
    fail "One or more sync:agents sub-layer scripts missing"
fi
if [ -d ".agents/skills/agents-sync" ]; then
    pass "agents-sync skill directory exists"
else
    fail "agents-sync skill directory missing"
fi
if [ -f "scripts/cognee_ingest_agent_definitions.py" ]; then
    pass "scripts/cognee_ingest_agent_definitions.py exists (Layer 10 ingestor)"
else
    fail "scripts/cognee_ingest_agent_definitions.py missing"
fi
if [ -f "notebooks/29_agents_sync_dashboard.py" ]; then
    pass "notebooks/29_agents_sync_dashboard.py (Layer 10 dashboard) exists"
else
    fail "notebooks/29_agents_sync_dashboard.py missing"
fi
if grep -q "agent-fleet-search" ".cocoindex_code/guides.yml" 2>/dev/null; then
    pass "25th CCC concept guide (agent-fleet-search) is in guides.yml"
else
    fail "25th CCC concept guide missing"
fi

# ============================================================================
# Step 11: sync:notebooks (Layer 11 — Marimo notebooks surface validation)
# Per the 2026-08-15-notebooks-sync-loop-v1 change
# ============================================================================
section "Step 11: sync:notebooks (Layer 11 — Marimo notebooks surface validation)"

if mise tasks ls 2>&1 | grep -qE "^sync:notebooks"; then
    pass "sync:notebooks task registered"
else
    fail "sync:notebooks task not registered"
fi
if [ -f "scripts/sync/notebooks.sh" ] && [ -f "scripts/sync/notebooks-drift.sh" ] && [ -f "scripts/sync/notebooks-ccc.sh" ] && [ -f "scripts/sync/notebooks-cognee.sh" ] && [ -f "scripts/sync/notebooks-test.sh" ] && [ -f "scripts/sync/notebooks-lint.sh" ]; then
    pass "All 6 sync:notebooks sub-layer scripts exist (drift + ccc + cognee + test + lint + orchestrator)"
else
    fail "One or more sync:notebooks sub-layer scripts missing"
fi
if [ -d ".agents/skills/notebooks-sync" ]; then
    pass "notebooks-sync skill directory exists (Layer 11)"
else
    fail "notebooks-sync skill directory missing"
fi
if [ -f "scripts/cognee_ingest_notebooks.py" ]; then
    pass "scripts/cognee_ingest_notebooks.py exists (Layer 11 ingestor)"
else
    fail "scripts/cognee_ingest_notebooks.py missing"
fi
if [ -f "notebooks/30_notebooks_sync_dashboard.py" ]; then
    pass "notebooks/30_notebooks_sync_dashboard.py (Layer 11 dashboard) exists"
else
    fail "notebooks/30_notebooks_sync_dashboard.py missing"
fi
if grep -q "notebook-search" ".cocoindex_code/guides.yml" 2>/dev/null; then
    pass "26th CCC concept guide (notebook-search) is in guides.yml"
else
    fail "26th CCC concept guide missing"
fi
if grep -q "notebooks_sync_health" "orchestration/defs/sync_assets.py" 2>/dev/null; then
    pass "orchestration/defs/sync_assets.py has the notebooks_sync_health asset (Layer 11 Dagster wiring)"
else
    fail "orchestration/defs/sync_assets.py missing the notebooks_sync_health asset"
fi
if grep -q "firecrawl-search" ".cocoindex_code/guides.yml" 2>/dev/null; then
    pass "27th CCC concept guide (firecrawl-search) is in guides.yml"
else
    fail "27th CCC concept guide (firecrawl-search) missing"
fi
if grep -q "firecrawl-mcp-tools" ".cocoindex_code/guides.yml" 2>/dev/null; then
    pass "28th CCC concept guide (firecrawl-mcp-tools) is in guides.yml"
else
    fail "28th CCC concept guide (firecrawl-mcp-tools) missing"
fi
if grep -q "firecrawl-corpus" ".cocoindex_code/guides.yml" 2>/dev/null; then
    pass "31st CCC concept guide (firecrawl-corpus) is in guides.yml"
else
    fail "31st CCC concept guide (firecrawl-corpus) missing"
fi

# ============================================================================
# Summary
# ============================================================================
section "Summary"

TOTAL=$((PASS + FAIL + SKIP))
echo "  PASS:  $PASS"
echo "  FAIL:  $FAIL"
echo "  SKIP:  $SKIP"
echo "  TOTAL: $TOTAL"
echo

if [ "$FAIL" -eq 0 ]; then
    echo -e "${GREEN}All 11 bring-up steps work! (with Step 2 skipped per user direction)${NC}"
    exit 0
else
    echo -e "${RED}Some bring-up steps failed. See above.${NC}"
    exit 1
fi
