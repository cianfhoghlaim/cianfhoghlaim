#!/bin/bash
# =============================================================================
# TAISCE STACK MANAGEMENT SCRIPT
# =============================================================================
# Manages taisce stacks with optional Locket secret injection.
#
# Usage:
#   ./scripts/stack.sh <stack> <command> [args...]
#
# Examples:
#   # Development (no Locket, uses defaults or .env.local)
#   ./scripts/stack.sh langfuse up -d
#   ./scripts/stack.sh langfuse down
#   ./scripts/stack.sh langfuse logs -f
#   ./scripts/stack.sh langfuse ps
#
#   # Production (with Locket)
#   LOCKET_ENABLED=1 ./scripts/stack.sh langfuse up -d
#
#   # Or set permanently
#   export LOCKET_ENABLED=1
#   export OP_CONNECT_HOST=http://132.145.27.89:8080
#   ./scripts/stack.sh langfuse up -d
#
# Environment Variables:
#   LOCKET_ENABLED        - Set to 1 to enable Locket secret injection
#   OP_CONNECT_HOST       - 1Password Connect URL (default: http://132.145.27.89:8080)
#   OP_CONNECT_TOKEN_FILE - Path to token file (default: ./op_token)
#   TAISCE_DIR            - Base directory (default: script directory parent)
# =============================================================================

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TAISCE_DIR="${TAISCE_DIR:-$(dirname "$SCRIPT_DIR")}"
STACKS_DIR="${TAISCE_DIR}/stacks"

OP_CONNECT_HOST="${OP_CONNECT_HOST:-http://132.145.27.89:8080}"
OP_CONNECT_TOKEN_FILE="${OP_CONNECT_TOKEN_FILE:-${TAISCE_DIR}/op_token}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse arguments
STACK="${1:-}"
shift || true
COMMAND="${1:-}"
shift || true

# Show usage
show_usage() {
    echo "Usage: $0 <stack> <command> [args...]"
    echo ""
    echo -e "${BLUE}Available stacks:${NC}"
    for stack_dir in "$STACKS_DIR"/*/; do
        if [ -f "${stack_dir}compose.yaml" ]; then
            stack_name=$(basename "$stack_dir")
            echo "  $stack_name"
        fi
    done
    echo ""
    echo -e "${BLUE}Commands:${NC}"
    echo "  up       - Start stack (add -d for detached)"
    echo "  down     - Stop and remove stack"
    echo "  logs     - View logs (add -f to follow)"
    echo "  ps       - List containers"
    echo "  restart  - Restart stack"
    echo "  pull     - Pull latest images"
    echo "  exec     - Execute command in container"
    echo ""
    echo -e "${BLUE}Environment:${NC}"
    echo "  LOCKET_ENABLED=1  - Enable Locket secret injection (production)"
    echo ""
    echo -e "${BLUE}Examples:${NC}"
    echo "  $0 langfuse up -d              # Start Langfuse (dev mode)"
    echo "  $0 langfuse logs -f            # Follow logs"
    echo "  LOCKET_ENABLED=1 $0 langfuse up -d  # Start with secrets"
}

if [ -z "$STACK" ] || [ -z "$COMMAND" ]; then
    show_usage
    exit 1
fi

# Stack paths
STACK_DIR="${STACKS_DIR}/${STACK}"
COMPOSE_FILE="${STACK_DIR}/compose.yaml"
SECRETS_FILE="${STACK_DIR}/secrets.env"

# Validate stack exists
if [ ! -d "$STACK_DIR" ]; then
    echo -e "${RED}Error: Stack not found: ${STACK}${NC}"
    echo ""
    echo "Available stacks:"
    for stack_dir in "$STACKS_DIR"/*/; do
        if [ -f "${stack_dir}compose.yaml" ]; then
            echo "  $(basename "$stack_dir")"
        fi
    done
    exit 1
fi

if [ ! -f "$COMPOSE_FILE" ]; then
    echo -e "${RED}Error: Compose file not found: ${COMPOSE_FILE}${NC}"
    exit 1
fi

# Build the docker compose command
build_compose_cmd() {
    local cmd="docker compose -f $COMPOSE_FILE"

    # Add env file if exists (for development)
    if [ -f "${TAISCE_DIR}/.env.local" ]; then
        cmd="$cmd --env-file ${TAISCE_DIR}/.env.local"
    fi

    echo "$cmd"
}

# Run with Locket (production)
run_with_locket() {
    if [ ! -f "$SECRETS_FILE" ]; then
        echo -e "${YELLOW}Warning: Secrets file not found: ${SECRETS_FILE}${NC}"
        echo "Running without Locket secret injection..."
        run_without_locket "$@"
        return
    fi

    if [ ! -f "$OP_CONNECT_TOKEN_FILE" ]; then
        echo -e "${RED}Error: 1Password Connect token file not found: ${OP_CONNECT_TOKEN_FILE}${NC}"
        echo "Create this file with your 1Password Connect token or set OP_CONNECT_TOKEN_FILE"
        exit 1
    fi

    echo -e "${GREEN}Running with Locket (op-connect)...${NC}"
    echo -e "Stack: ${BLUE}${STACK}${NC}"
    echo -e "Secrets: ${SECRETS_FILE}"
    echo ""

    locket exec \
        --provider op-connect \
        --connect.host "$OP_CONNECT_HOST" \
        --connect.token-file "$OP_CONNECT_TOKEN_FILE" \
        --env-file "$SECRETS_FILE" \
        -- docker compose -f "$COMPOSE_FILE" "$COMMAND" "$@"
}

# Run without Locket (development)
run_without_locket() {
    local compose_cmd
    compose_cmd=$(build_compose_cmd)

    echo -e "${GREEN}Running without Locket (development mode)...${NC}"
    echo -e "Stack: ${BLUE}${STACK}${NC}"
    echo -e "Compose: ${COMPOSE_FILE}"
    echo ""

    $compose_cmd "$COMMAND" "$@"
}

# Main execution
if [ "${LOCKET_ENABLED:-}" = "1" ]; then
    run_with_locket "$@"
else
    run_without_locket "$@"
fi
