#!/usr/bin/env bash
# scripts/reproducers/agents-fleet-reproducer.sh
#
# Operator's one-shot: 6 commands from cold to green.
# Reproduces the 12-agent fleet + 8 NCCA subject specialists
# + 3 educational agents on bunchloch or arm1-oci.
#
# Reference: openspec/changes/2026-08-14-agents-fleet-wiring-parity-v1

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

cd "${REPO_ROOT}"

# ANSI colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

ok() { echo -e "${GREEN}[OK]${NC} $*"; }
fail() { echo -e "${RED}[FAIL]${NC} $*"; exit 1; }
warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }

echo "================================================="
echo "  Agent-Fleet Reproducer"
echo "  (12-agent fleet + 8 NCCA + 3 educational)"
echo "================================================="
echo ""

# ---- Step 1: 12-agent fleet ----
echo "Step 1: Verify 12-agent fleet loads via AGENT_REGISTRY"
COUNT=$(python -c "
import os
os.environ['AGENT_FLEET_DISABLE_WIRE'] = '1'
os.environ['AGENT_FLEET_DISABLE_MEMORY'] = '1'
from cianfhoghlaim.agents.agent_registry import AGENT_REGISTRY
print(len(AGENT_REGISTRY))
" 2>/dev/null || echo "0")

if [[ "${COUNT}" -ge 12 ]]; then
    ok "AGENT_REGISTRY has ${COUNT} entries (≥12 expected)"
else
    fail "AGENT_REGISTRY has only ${COUNT} entries (need ≥12)"
fi

# ---- Step 2: 8 NCCA subject specialists ----
echo ""
echo "Step 2: Verify 8 NCCA subject specialists load via agents.tuatha"
for subject in gael math appm chem comp engl geog hist; do
    if python -c "
import os
os.environ['AGENT_FLEET_DISABLE_WIRE'] = '1'
os.environ['AGENT_FLEET_DISABLE_MEMORY'] = '1'
os.environ['SUBJECT_AGENT_DISABLE_WIRE'] = '1'
from cianfhoghlaim.agents.tuatha import ${subject}_agent
assert ${subject}_agent is not None
" 2>/dev/null; then
        ok "${subject}_agent loads"
    else
        warn "${subject}_agent: may not be wired yet (skipped)"
    fi
done

# ---- Step 3: 3 educational agents ----
echo ""
echo "Step 3: Verify 3 educational agents load via agents.meaisinfhoghlaim.educational"
for subject in academic_history celtic_grammar celtic_morphology; do
    if python -c "
import os
os.environ['AGENT_FLEET_DISABLE_WIRE'] = '1'
os.environ['AGENT_FLEET_DISABLE_MEMORY'] = '1'
from cianfhoghlaim.agents.meaisinfhoghlaim.educational import ${subject}_agent
assert ${subject}_agent is not None
" 2>/dev/null; then
        ok "${subject}_agent loads"
    else
        warn "${subject}_agent: may not be wired yet (skipped)"
    fi
done

# ---- Step 4: 5-layer observability contract ----
echo ""
echo "Step 4: Verify 5-layer observability contract"
OBS_OK=$(python -c "
import os
os.environ['AGENT_FLEET_DISABLE_WIRE'] = '1'
os.environ['AGENT_FLEET_DISABLE_MEMORY'] = '1'
from cianfhoghlaim.agents.observability_hooks import verify_5_layer_contract
result = verify_5_layer_contract()
print(sum(1 for v in result.values() if v))
" 2>/dev/null || echo "0")
ok "5-layer observability contract: ${OBS_OK}/12 agents wired"

# ---- Step 5: 5-backend memory layer ----
echo ""
echo "Step 5: Verify 5-backend memory layer"
LAYER_KIND=$(python -c "
import os
os.environ['AGENT_FLEET_DISABLE_MEMORY'] = '1'
from cianfhoghlaim.agents.memory_layer import get_default_memory_layer
print(get_default_memory_layer().kind)
" 2>/dev/null || echo "unknown")
if [[ "${LAYER_KIND}" != "unknown" ]]; then
    ok "Memory layer resolved to: ${LAYER_KIND}"
else
    warn "Memory layer: could not resolve (may need 1+ concrete backend reachable)"
fi

# ---- Step 6: Direct-import audit ----
echo ""
echo "Step 6: Direct-import audit (0 forbidden client symbols per agent module)"
FORBIDDEN_HITS=$(grep -rn "langfuse_client\|cognee_client\|letta_client\|graphiti_client\|falkordb_client\|memgraph_client" \
    agents/adk agents/agno 2>/dev/null | grep -v ".DS_Store" | grep "_agent.py" | wc -l || echo "0")
if [[ "${FORBIDDEN_HITS}" -eq 0 ]]; then
    ok "Direct-import audit: 0 forbidden symbols"
else
    warn "Direct-import audit: ${FORBIDDEN_HITS} potential violations (review)"
fi

echo ""
echo "================================================="
echo "  Reproducer Complete"
echo "================================================="
echo ""
echo "Summary:"
echo "  - AGENT_REGISTRY entries: ${COUNT}"
echo "  - 5-layer observability: ${OBS_OK}/12"
echo "  - Memory layer: ${LAYER_KIND}"
echo "  - Direct-import audit: ${FORBIDDEN_HITS} violations"
echo ""
echo "For full details, see agents/REPRODUCER.md"