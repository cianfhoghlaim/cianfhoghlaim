#!/bin/bash
# =============================================================================
# Validate Deprecated Read-Only Shadow Stacks
# =============================================================================
# ADDED 2026-08-24 (lakehouse-stack-doctor-and-env-var-cleanup-v1).
#
# Per user preference: the 5 deprecated stacks (cognee/ + graphiti/ +
# falkordb/ + memgraph/ + lancedb/) are KEPT as read-only shadow stacks.
# This script verifies they:
#   1. Have valid Docker Compose (parse + docker compose config passes)
#   2. Have the deprecation banner at the top of compose.yaml
#   3. Have a README that documents the move to lakehouse
#
# Exit codes:
#   0 = all checks passed
#   1 = at least one check failed
# =============================================================================
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STACKS_DIR="${REPO_ROOT}/bonneagar/stacks"

DEPRECATED_STACKS=(
    "cognee"
    "graphiti"
    "falkordb"
    "memgraph"
    "lancedb"
)

FAILURES=0
if [[ -t 1 ]]; then
    GREEN='\033[0;32m'; RED='\033[0;31m'; YELLOW='\033[1;33m'; NC='\033[0m'
else
    GREEN=''; RED=''; YELLOW=''; NC=''
fi

echo "==================================================="
echo "Validating deprecated read-only shadow stacks"
echo "==================================================="
echo ""

for stack in "${DEPRECATED_STACKS[@]}"; do
    stack_dir="${STACKS_DIR}/${stack}"
    echo -e "${YELLOW}→ ${stack}${NC}"

    # Check 1: directory exists
    if [[ ! -d "$stack_dir" ]]; then
        echo -e "  ${RED}✗${NC} directory ${stack_dir} does not exist"
        FAILURES=$((FAILURES + 1))
        continue
    fi
    echo -e "  ${GREEN}✓${NC} directory exists"

    compose_file="${stack_dir}/compose.yaml"

    # Check 2: compose.yaml parses
    if [[ ! -f "$compose_file" ]]; then
        echo -e "  ${RED}✗${NC} compose.yaml missing"
        FAILURES=$((FAILURES + 1))
        continue
    fi

    # Check 3: docker compose config passes (cd into stack dir for proper file resolution)
    pushd "$stack_dir" > /dev/null 2>&1
    config_output=$(docker compose config --quiet 2>&1)
    config_exit=$?
    popd > /dev/null 2>&1

    if [[ $config_exit -eq 0 ]]; then
        echo -e "  ${GREEN}✓${NC} docker compose config passes"
    else
        echo -e "  ${RED}�${NC} docker compose config failed:"
        echo "      ${config_output}"
        FAILURES=$((FAILURES + 1))
    fi

    # Check 4: has the deprecation banner
    banner_check=$(head -20 "$compose_file" | grep -c "DEPRECATED 2026-08-15")
    if [[ "$banner_check" -gt 0 ]]; then
        echo -e "  ${GREEN}✓${NC} deprecation banner present"
    else
        echo -e "  ${RED}✗${NC} deprecation banner MISSING (must start with 'DEPRECATED 2026-08-15:')"
        FAILURES=$((FAILURES + 1))
    fi

    # Check 5: has a README that documents the move to lakehouse
    readme_file="${stack_dir}/README.md"
    if [[ -f "$readme_file" ]]; then
        readme_check=$(grep -c -E "(unified lakehouse|moved to lakehouse|now part of lakehouse|consolidated into lakehouse)" "$readme_file")
        if [[ "$readme_check" -gt 0 ]]; then
            echo -e "  ${GREEN}✓${NC} README documents move to lakehouse"
        else
            echo -e "  ${YELLOW}⚠${NC} README exists but doesn't document move to lakehouse"
        fi
    else
        echo -e "  ${YELLOW}⚠${NC} README.md missing (deprecated stack should have one)"
    fi

    echo ""
done

echo "==================================================="
if [[ $FAILURES -eq 0 ]]; then
    echo -e "${GREEN}✓ All deprecated stacks validated${NC}"
    echo "==================================================="
    exit 0
else
    echo -e "${RED}✗ ${FAILURES} validation failure(s)${NC}"
    echo "==================================================="
    exit 1
fi
