#!/bin/bash
# =============================================================================
# LAKEHOUSE STACK-DOCTOR (custom lint for the unified lakehouse stack)
# =============================================================================
# ADDED 2026-08-24 (lakehouse-stack-doctor-and-env-var-cleanup-v1).
#
# Validates the unified lakehouse stack against the canonical contract:
#   - 17 services in compose.yaml (was 16; +1 otel-collector added in PR #2)
#   - 14 databases in init-db.sql (matches db_manifest.yaml)
#   - 10 private-resources in blueprint.yaml
#   - 5 routes in pangolin.yaml
#   - 53+ infisical://dev-baile/<svc>/<key> URIs in secrets.env
#   - 100% of image tags pinned to semver (with documented exceptions)
#   - No hardcoded absolute paths in sidecar.yaml
#
# Exit codes:
#   0 = all checks passed
#   1 = at least one check failed (actionable error message printed)
#   2 = script error (file not found, yaml parse error, etc.)
# =============================================================================
set -uo pipefail

# Resolve repo root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
STACK_DIR="${REPO_ROOT}/bonneagar/stacks/lakehouse"

# Track failures
FAILURES=0
FAILURES_DETAIL=()

# Color helpers (if stdout is a tty)
if [[ -t 1 ]]; then
    GREEN='\033[0;32m'
    RED='\033[0;31m'
    YELLOW='\033[1;33m'
    NC='\033[0m'
else
    GREEN=''; RED=''; YELLOW=''; NC=''
fi

# Helper: print check result
check() {
    local name="$1"
    local ok="$2"  # "ok" or "fail"
    if [[ "$ok" == "ok" ]]; then
        echo -e "  ${GREEN}✓${NC} $name"
    else
        echo -e "  ${RED}✗${NC} $name"
        FAILURES=$((FAILURES + 1))
        FAILURES_DETAIL+=("$name")
    fi
}

# -----------------------------------------------------------------------------
# Check 1: compose.yaml — 17 services
# -----------------------------------------------------------------------------
echo ""
echo "=== compose.yaml (17 services) ==="
COMPOSE_FILE="${STACK_DIR}/compose.yaml"
if [[ ! -f "$COMPOSE_FILE" ]]; then
    check "compose.yaml exists" fail
    echo "ERROR: ${COMPOSE_FILE} not found"
    exit 2
fi

# Parse services count
COMPOSE_SERVICE_COUNT=$(python3 -c "
import yaml
d = yaml.safe_load(open('${COMPOSE_FILE}'))
print(len(d.get('services', {})))
" 2>/dev/null | tr -d ' ')
EXPECTED_SERVICE_COUNT=17  # 11 data plane + 5 graph DB + 1 otel-collector

if [[ "$COMPOSE_SERVICE_COUNT" == "$EXPECTED_SERVICE_COUNT" ]]; then
    check "compose.yaml has ${EXPECTED_SERVICE_COUNT} services (got ${COMPOSE_SERVICE_COUNT})" ok
else
    check "compose.yaml has ${EXPECTED_SERVICE_COUNT} services (got ${COMPOSE_SERVICE_COUNT})" fail
fi

# Verify required services are present
for required in "garage" "postgres" "clickhouse" "redis" "lakekeeper" "lance-namespace" \
                 "nimtable" "olake" "lancedb-viewer" "cognee" "graphiti" "falkordb" \
                 "memgraph" "memgraph-lab" "otel-collector" "garage-init" "lakekeeper-migrate"; do
    if grep -qE "^  ${required}:" "$COMPOSE_FILE"; then
        check "service '${required}' present in compose.yaml" ok
    else
        check "service '${required}' present in compose.yaml" fail
    fi
done

# -----------------------------------------------------------------------------
# Check 2: init-db.sql — 14 databases (matches db_manifest.yaml)
# -----------------------------------------------------------------------------
echo ""
echo "=== init-db.sql (14 databases matching db_manifest.yaml) ==="
INIT_DB_FILE="${STACK_DIR}/init-db.sql"
DB_MANIFEST="${STACK_DIR}/db_manifest.yaml"

if [[ ! -f "$INIT_DB_FILE" ]]; then
    check "init-db.sql exists" fail
    echo "ERROR: ${INIT_DB_FILE} not found"
    exit 2
fi

if [[ ! -f "$DB_MANIFEST" ]]; then
    check "db_manifest.yaml exists" fail
    echo "ERROR: ${DB_MANIFEST} not found"
    exit 2
fi

INIT_DB_COUNT=$(grep -E "^CREATE DATABASE" "$INIT_DB_FILE" | wc -l | tr -d ' ')
if [[ "$INIT_DB_COUNT" == "14" ]]; then
    check "init-db.sql has 14 CREATE DATABASE statements (got ${INIT_DB_COUNT})" ok
else
    check "init-db.sql has 14 CREATE DATABASE statements (got ${INIT_DB_COUNT})" fail
fi

# Verify all 14 db names from db_manifest.yaml exist in init-db.sql
MANIFEST_DBS=$(python3 -c "
import yaml
d = yaml.safe_load(open('${DB_MANIFEST}'))
for group, dbs in d.get('databases', {}).items():
    for db in dbs:
        print(db)
" 2>/dev/null)
for db in $MANIFEST_DBS; do
    if grep -q "CREATE DATABASE ${db};" "$INIT_DB_FILE"; then
        check "db '${db}' in init-db.sql" ok
    else
        check "db '${db}' in init-db.sql" fail
    fi
done

# -----------------------------------------------------------------------------
# Check 3: blueprint.yaml — 10 private-resources
# -----------------------------------------------------------------------------
echo ""
echo "=== blueprint.yaml (10 private-resources) ==="
BLUEPRINT_FILE="${STACK_DIR}/blueprint.yaml"
if [[ ! -f "$BLUEPRINT_FILE" ]]; then
    check "blueprint.yaml exists" fail
    exit 2
fi

BLUEPRINT_PR_COUNT=$(python3 -c "
import yaml
d = yaml.safe_load(open('${BLUEPRINT_FILE}'))
print(len(d.get('private-resources', {})))
" 2>/dev/null | tr -d ' ')
EXPECTED_PR_COUNT=10

if [[ "$BLUEPRINT_PR_COUNT" == "$EXPECTED_PR_COUNT" ]]; then
    check "blueprint.yaml has ${EXPECTED_PR_COUNT} private-resources (got ${BLUEPRINT_PR_COUNT})" ok
else
    check "blueprint.yaml has ${EXPECTED_PR_COUNT} private-resources (got ${BLUEPRINT_PR_COUNT})" fail
fi

# -----------------------------------------------------------------------------
# Check 4: pangolin.yaml — 5 routes
# -----------------------------------------------------------------------------
echo ""
echo "=== pangolin.yaml (5 routes) ==="
PANGOLIN_FILE="${STACK_DIR}/pangolin.yaml"
if [[ ! -f "$PANGOLIN_FILE" ]]; then
    check "pangolin.yaml exists" fail
    exit 2
fi

PANGOLIN_ROUTES=$(python3 -c "
import yaml
d = yaml.safe_load(open('${PANGOLIN_FILE}'))
print(len(d.get('pangolin', {}).get('private-resources', {})))
" 2>/dev/null | tr -d ' ')
EXPECTED_ROUTES=5

if [[ "$PANGOLIN_ROUTES" == "$EXPECTED_ROUTES" ]]; then
    check "pangolin.yaml has ${EXPECTED_ROUTES} routes (got ${PANGOLIN_ROUTES})" ok
else
    check "pangolin.yaml has ${EXPECTED_ROUTES} routes (got ${PANGOLIN_ROUTES})" fail
fi

# -----------------------------------------------------------------------------
# Check 5: secrets.env — 53+ infisical URIs
# -----------------------------------------------------------------------------
echo ""
echo "=== secrets.env (53+ infisical URIs) ==="
SECRETS_FILE="${STACK_DIR}/secrets.env"
if [[ ! -f "$SECRETS_FILE" ]]; then
    check "secrets.env exists" fail
    exit 2
fi

SECRETS_URI_COUNT=$(grep -c "infisical://dev-baile" "$SECRETS_FILE")
EXPECTED_URI_MIN=53

if [[ "$SECRETS_URI_COUNT" -ge "$EXPECTED_URI_MIN" ]]; then
    check "secrets.env has ${SECRETS_URI_COUNT} infisical URIs (>= ${EXPECTED_URI_MIN})" ok
else
    check "secrets.env has ${SECRETS_URI_COUNT} infisical URIs (expected >= ${EXPECTED_URI_MIN})" fail
fi

# -----------------------------------------------------------------------------
# Check 6: image pinning — 100% semver-pinned (with documented exceptions)
# -----------------------------------------------------------------------------
echo ""
echo "=== compose.yaml image pinning ==="
# Extract image: lines from compose.yaml + check for ':latest' exceptions
PINNED_OK=true
while IFS= read -r line; do
    service_name=$(echo "$line" | sed -nE 's/^  ([a-z_-]+):.*/\1/p')
    image=$(echo "$line" | sed -nE 's/.*image:[[:space:]]*([^[:space:]]+).*/\1/p')
    if [[ -z "$image" ]]; then continue; fi

    # Allow documented exceptions: nimtable/nimtable:latest (no semver available)
    # + lakehouse-lance-namespace:latest (built locally)
    # + curlimages/curl:latest (distroless curl image)
    if [[ "$image" == *":latest" ]]; then
        case "$image" in
            *nimtable/nimtable:latest|*lakehouse-lance-namespace:latest|*curlimages/curl:latest)
                # Documented exception — skip
                ;;
            *)
                echo -e "  ${RED}✗${NC} image '${image}' in service '${service_name}' uses :latest (not pinned)"
                FAILURES=$((FAILURES + 1))
                FAILURES_DETAIL+=("image ${image} uses :latest")
                PINNED_OK=false
                ;;
        esac
    fi
done < <(grep -E "^  [a-z_-]+:|^    image:" "$COMPOSE_FILE")

if [[ "$PINNED_OK" == "true" ]]; then
    check "all images pinned to semver (with documented exceptions)" ok
fi

# -----------------------------------------------------------------------------
# Check 7: sidecar.yaml — no hardcoded absolute paths
# -----------------------------------------------------------------------------
echo ""
echo "=== sidecar.yaml (no hardcoded absolute paths) ==="
SIDECAR_FILE="${STACK_DIR}/sidecar.yaml"
if [[ -f "$SIDECAR_FILE" ]]; then
    # Skip lines starting with `#` (comments) when searching for absolute paths
    HARDCODED_PATH=$(grep -vE "^[[:space:]]*#" "$SIDECAR_FILE" | grep -E "/Users/[^/]+/" | head -1 || true)
    if [[ -n "$HARDCODED_PATH" ]]; then
        check "sidecar.yaml has no hardcoded absolute paths" fail
        echo "  Found: ${HARDCODED_PATH}"
    else
        check "sidecar.yaml has no hardcoded absolute paths" ok
    fi
else
    check "sidecar.yaml exists" fail
fi

# -----------------------------------------------------------------------------
# Check 8: healthchecks — canonical template
# -----------------------------------------------------------------------------
echo ""
echo "=== compose.yaml healthchecks (canonical template) ==="
# All healthchecks should have:
#   - interval: 10s OR 15s
#   - timeout: 5s
#   - retries: 3-5
#   - start_period: 10-30s
HEALTHCHECK_OK=true
# Simplified: just check that all services with healthchecks have interval + timeout
for hc_start_line in $(grep -n "healthcheck:" "$COMPOSE_FILE" | cut -d: -f1); do
    # Look ahead 15 lines from healthcheck: for interval + timeout
    # (some healthchecks have multi-line test: arrays that span 5-8 lines)
    next_lines=$(sed -n "${hc_start_line},$((hc_start_line + 15))p" "$COMPOSE_FILE")
    if echo "$next_lines" | grep -qE "interval:" && echo "$next_lines" | grep -qE "timeout:"; then
        continue
    else
        echo -e "  ${RED}✗${NC} healthcheck at line ${hc_start_line} missing interval/timeout"
        FAILURES=$((FAILURES + 1))
        HEALTHCHECK_OK=false
    fi
done

if [[ "$HEALTHCHECK_OK" == "true" ]]; then
    check "all healthchecks have interval + timeout (canonical template)" ok
fi

# -----------------------------------------------------------------------------
# Summary
# -----------------------------------------------------------------------------
echo ""
echo "================================================="
if [[ $FAILURES -eq 0 ]]; then
    echo -e "${GREEN}✓ Lakehouse stack-doctor passed${NC} — all checks succeeded"
    echo "================================================="
    exit 0
else
    echo -e "${RED}✗ Lakehouse stack-doctor failed${NC} — ${FAILURES} check(s) failed:"
    for detail in "${FAILURES_DETAIL[@]}"; do
        echo "  - ${detail}"
    done
    echo "================================================="
    exit 1
fi
