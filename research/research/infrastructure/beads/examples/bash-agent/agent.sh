#!/usr/bin/env bash
#
# Simple AI agent workflow using bd (Beads issue tracker).
#
# This demonstrates the full lifecycle of an agent managing tasks:
# - Find ready work
# - Claim and execute (with optional Agent Mail reservation)
# - Discover new issues
# - Link discoveries
# - Complete and move on
#
# Optional Agent Mail integration:
#   export BEADS_AGENT_MAIL_URL=http://127.0.0.1:8765
#   export BEADS_AGENT_NAME=bash-agent-1
#   export BEADS_PROJECT_ID=my-project

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}ℹ ${NC}$1"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

# Agent Mail integration (optional, graceful degradation)
AGENT_MAIL_ENABLED=false
AGENT_MAIL_URL="${BEADS_AGENT_MAIL_URL:-}"
AGENT_NAME="${BEADS_AGENT_NAME:-bash-agent-$$}"
PROJECT_ID="${BEADS_PROJECT_ID:-default}"

# Check Agent Mail health
check_agent_mail() {
    if [[ -z "$AGENT_MAIL_URL" ]]; then
        return 1
    fi
    
    if ! command -v curl &> /dev/null; then
        log_warning "curl not available, Agent Mail disabled"
        return 1
    fi
    
    if curl -s -f "$AGENT_MAIL_URL/health" > /dev/null 2>&1; then
        return 0
    fi
    return 1
}

# Reserve an issue (prevents other agents from claiming)
reserve_issue() {
    local issue_id="$1"
    
    if ! $AGENT_MAIL_ENABLED; then
        return 0  # Skip if disabled
    fi
    
    local response=$(curl -s -X POST "$AGENT_MAIL_URL/api/reserve" \
        -H "Content-Type: application/json" \
        -d "{\"file_path\": \"$issue_id\", \"agent_name\": \"$AGENT_NAME\", \"project_id\": \"$PROJECT_ID\", \"ttl_seconds\": 300}" \
        2>/dev/null || echo "")
    
    if [[ -z "$response" ]] || echo "$response" | grep -q "error"; then
        log_warning "Failed to reserve $issue_id (may be claimed by another agent)"
        return 1
    fi
    
    return 0
}

# Release an issue reservation
release_issue() {
    local issue_id="$1"
    
    if ! $AGENT_MAIL_ENABLED; then
        return 0  # Skip if disabled
    fi
    
    curl -s -X POST "$AGENT_MAIL_URL/api/release" \
        -H "Content-Type: application/json" \
        -d "{\"file_path\": \"$issue_id\", \"agent_name\": \"$AGENT_NAME\", \"project_id\": \"$PROJECT_ID\"}" \
        > /dev/null 2>&1 || true
}

# Send notification to other agents
notify() {
    local event_type="$1"
    local issue_id="$2"
    local message="$3"
    
    if ! $AGENT_MAIL_ENABLED; then
        return 0  # Skip if disabled
    fi
    
    curl -s -X POST "$AGENT_MAIL_URL/api/notify" \
        -H "Content-Type: application/json" \
        -d "{\"event_type\": \"$event_type\", \"from_agent\": \"$AGENT_NAME\", \"project_id\": \"$PROJECT_ID\", \"payload\": {\"issue_id\": \"$issue_id\", \"message\": \"$message\"}}" \
        > /dev/null 2>&1 || true
}

# Initialize Agent Mail
if check_agent_mail; then
    AGENT_MAIL_ENABLED=true
    log_success "Agent Mail enabled (agent: $AGENT_NAME)"
else
    log_info "Agent Mail disabled (Beads-only mode)"
fi

# Check if bd is installed
if ! command -v bd &> /dev/null; then
    log_error "bd is not installed"
    echo "Install with: go install github.com/steveyegge/beads/cmd/bd@latest"
    exit 1
fi

# Check if we're in a beads-initialized directory
if ! bd list &> /dev/null; then
    log_error "Not in a beads-initialized directory"
    echo "Run: bd init"
    exit 1
fi

# Find ready work
find_ready_work() {
    bd ready --json --limit 1 2>/dev/null | jq -r '.[0] // empty'
}

# Extract field from JSON
get_field() {
    local json="$1"
    local field="$2"
    echo "$json" | jq -r ".$field"
}

# Claim a task
claim_task() {
    local issue_id="$1"
    
    # Try to reserve first (Agent Mail)
    if ! reserve_issue "$issue_id"; then
        log_error "Could not reserve $issue_id - skipping"
        return 1
    fi
    
    log_info "Claiming task: $issue_id"
    bd update "$issue_id" --status in_progress --json > /dev/null
    
    # Notify other agents
    notify "status_changed" "$issue_id" "Claimed by $AGENT_NAME"
    
    log_success "Task claimed"
    return 0
}

# Simulate doing work (in real agent, this would call LLM/execute code)
do_work() {
    local issue="$1"
    local issue_id=$(get_field "$issue" "id")
    local title=$(get_field "$issue" "title")
    local priority=$(get_field "$issue" "priority")

    echo ""
    log_info "Working on: $title ($issue_id)"
    echo "  Priority: $priority"

    # Simulate work delay
    sleep 1

    # Simulate discovering new work (50% chance)
    if [[ $((RANDOM % 2)) -eq 0 ]]; then
        log_warning "Discovered issue while working!"

        # Create new issue
        local new_issue=$(bd create "Follow-up: $title" \
            -d "Discovered while working on $issue_id" \
            -p 2 \
            -t task \
            --json)

        local new_id=$(echo "$new_issue" | jq -r '.id')
        log_success "Created issue: $new_id"

        # Link it back to parent
        bd dep add "$new_id" "$issue_id" --type discovered-from
        log_success "Linked $new_id ← discovered-from ← $issue_id"

        return 0 # Discovered new work
    fi

    return 1 # No new work discovered
}

# Complete a task
complete_task() {
    local issue_id="$1"
    local reason="${2:-Completed successfully}"

    log_info "Completing task: $issue_id"
    bd close "$issue_id" --reason "$reason" --json > /dev/null
    
    # Notify completion and release reservation
    notify "issue_completed" "$issue_id" "$reason"
    release_issue "$issue_id"
    
    log_success "Task completed: $issue_id"
}

# Show statistics
show_stats() {
    echo ""
    echo "═══════════════════════════════════════════════════"
    echo "  Beads Statistics"
    echo "═══════════════════════════════════════════════════"
    bd stats
    echo ""
}

# Main agent loop
run_agent() {
    local max_iterations="${1:-10}"
    local iteration=0

    echo ""
    echo "🚀 Beads Agent starting..."
    echo "   Max iterations: $max_iterations"
    show_stats

    while [[ $iteration -lt $max_iterations ]]; do
        iteration=$((iteration + 1))

        echo ""
        echo "═══════════════════════════════════════════════════"
        echo "  Iteration $iteration/$max_iterations"
        echo "═══════════════════════════════════════════════════"

        # Find ready work
        log_info "Looking for ready work..."
        ready_work=$(find_ready_work)

        if [[ -z "$ready_work" ]]; then
            log_warning "No ready work found. Agent idle."
            break
        fi

        issue_id=$(get_field "$ready_work" "id")

        # Claim it (may fail if another agent reserved it)
        if ! claim_task "$issue_id"; then
            log_warning "Skipping already-claimed task, trying next iteration"
            continue
        fi

        # Do the work
        if do_work "$ready_work"; then
            log_info "New work discovered, will process in next iteration"
        fi

        # Complete it
        complete_task "$issue_id"

        # Brief pause between iterations
        sleep 0.5
    done

    echo ""
    log_success "Agent finished after $iteration iterations"
    show_stats
}

# Handle Ctrl-C gracefully
trap 'echo ""; log_warning "Agent interrupted by user"; exit 130' INT

# Run the agent
run_agent "${1:-10}"
