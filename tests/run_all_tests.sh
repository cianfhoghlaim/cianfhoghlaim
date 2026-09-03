#!/usr/bin/env bash
# =============================================================================
# SRUTH PIPELINE TEST RUNNER
# =============================================================================
# Runs tests for all sruth pipelines in parallel where possible.
#
# USAGE:
#   ./tests/run_all_tests.sh              # Run all tests
#   ./tests/run_all_tests.sh oideachais   # Run specific pipeline
#   ./tests/run_all_tests.sh --mcp        # Run MCP integration tests only
#   ./tests/run_all_tests.sh --parallel   # Run all in parallel
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Pipelines
PIPELINES=(
    "oideachais"
    "crypteolas"
    "tuath"
    "códeolas"
    "browser"
    "taighde"
    "aleyum"
)

# Results tracking
declare -A RESULTS

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

log_error() {
    echo -e "${RED}[FAIL]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Run tests for a single pipeline
run_pipeline_tests() {
    local pipeline=$1
    local pipeline_dir="$PROJECT_ROOT/sruth/$pipeline"

    if [[ ! -d "$pipeline_dir" ]]; then
        log_warn "Pipeline directory not found: $pipeline_dir"
        RESULTS[$pipeline]="skipped"
        return 0
    fi

    log_info "Testing $pipeline..."

    if [[ ! -f "$pipeline_dir/pyproject.toml" ]]; then
        log_warn "No pyproject.toml found for $pipeline"
        RESULTS[$pipeline]="skipped"
        return 0
    fi

    cd "$pipeline_dir"

    # Install dependencies
    if ! uv sync --dev 2>/dev/null; then
        log_error "Failed to install dependencies for $pipeline"
        RESULTS[$pipeline]="failed"
        return 1
    fi

    # Run tests
    if [[ -d "tests" ]]; then
        if uv run pytest tests/ -v --tb=short 2>&1; then
            log_success "$pipeline tests passed"
            RESULTS[$pipeline]="passed"
        else
            log_error "$pipeline tests failed"
            RESULTS[$pipeline]="failed"
            return 1
        fi
    else
        log_warn "No tests directory for $pipeline"
        RESULTS[$pipeline]="no_tests"
    fi

    cd "$PROJECT_ROOT"
    return 0
}

# Run MCP integration tests
run_mcp_tests() {
    log_info "Running MCP integration tests..."

    cd "$PROJECT_ROOT"

    # Run MCP health checks
    log_info "Running MCP health checks..."
    if uv run python tests/mcp/health_check.py 2>&1; then
        log_success "MCP health checks passed"
    else
        log_warn "Some MCP health checks failed (non-critical)"
    fi

    # Run integration tests
    log_info "Running integration tests..."
    if uv run pytest tests/integration/ -v -m "integration" --tb=short 2>&1; then
        log_success "Integration tests passed"
        RESULTS["integration"]="passed"
    else
        log_error "Integration tests failed"
        RESULTS["integration"]="failed"
        return 1
    fi

    return 0
}

# Run all tests in parallel
run_parallel() {
    log_info "Running all pipeline tests in parallel..."

    local pids=()
    local results_file=$(mktemp)

    for pipeline in "${PIPELINES[@]}"; do
        (
            run_pipeline_tests "$pipeline" > /tmp/test_${pipeline}.log 2>&1
            echo "${pipeline}:${RESULTS[$pipeline]:-unknown}" >> "$results_file"
        ) &
        pids+=($!)
    done

    # Wait for all background jobs
    for pid in "${pids[@]}"; do
        wait "$pid" || true
    done

    # Collect results
    while IFS=: read -r pipeline result; do
        RESULTS[$pipeline]=$result
    done < "$results_file"

    rm -f "$results_file"
}

# Print summary
print_summary() {
    echo ""
    echo "========================================"
    echo "          TEST SUMMARY                  "
    echo "========================================"

    local passed=0
    local failed=0
    local skipped=0

    for pipeline in "${!RESULTS[@]}"; do
        case ${RESULTS[$pipeline]} in
            passed)
                echo -e "${GREEN}✓${NC} $pipeline"
                ((passed++))
                ;;
            failed)
                echo -e "${RED}✗${NC} $pipeline"
                ((failed++))
                ;;
            skipped|no_tests)
                echo -e "${YELLOW}○${NC} $pipeline (${RESULTS[$pipeline]})"
                ((skipped++))
                ;;
            *)
                echo -e "${YELLOW}?${NC} $pipeline (unknown)"
                ;;
        esac
    done

    echo "----------------------------------------"
    echo -e "Passed: ${GREEN}$passed${NC}"
    echo -e "Failed: ${RED}$failed${NC}"
    echo -e "Skipped: ${YELLOW}$skipped${NC}"
    echo "========================================"

    if [[ $failed -gt 0 ]]; then
        return 1
    fi
    return 0
}

# Main
main() {
    local run_all=true
    local run_mcp=false
    local run_parallel_flag=false
    local specific_pipeline=""

    while [[ $# -gt 0 ]]; do
        case $1 in
            --mcp)
                run_mcp=true
                run_all=false
                shift
                ;;
            --parallel)
                run_parallel_flag=true
                shift
                ;;
            --help|-h)
                echo "Usage: $0 [OPTIONS] [PIPELINE]"
                echo ""
                echo "Options:"
                echo "  --mcp       Run MCP integration tests only"
                echo "  --parallel  Run all pipeline tests in parallel"
                echo "  --help      Show this help message"
                echo ""
                echo "Pipelines: ${PIPELINES[*]}"
                exit 0
                ;;
            *)
                specific_pipeline=$1
                run_all=false
                shift
                ;;
        esac
    done

    echo "========================================"
    echo "     SRUTH PIPELINE TEST RUNNER         "
    echo "========================================"
    echo ""

    cd "$PROJECT_ROOT"

    if [[ -n "$specific_pipeline" ]]; then
        run_pipeline_tests "$specific_pipeline"
    elif [[ "$run_mcp" == true ]]; then
        run_mcp_tests
    elif [[ "$run_parallel_flag" == true ]]; then
        run_parallel
        run_mcp_tests
    else
        # Run sequentially
        for pipeline in "${PIPELINES[@]}"; do
            run_pipeline_tests "$pipeline" || true
        done
        run_mcp_tests || true
    fi

    print_summary
}

main "$@"
