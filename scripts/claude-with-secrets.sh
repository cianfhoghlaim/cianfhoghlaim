#!/usr/bin/env bash
# =============================================================================
# Claude Code Launcher with 1Password Secret Injection
# =============================================================================
# This script wraps Claude Code with `op run` to inject 1Password secrets
# at runtime. MCP servers will inherit these environment variables.
#
# USAGE:
#   ./scripts/claude-with-secrets.sh [claude args...]
#
# REQUIREMENTS:
#   - 1Password CLI (op) installed and authenticated
#   - .env.local file with op:// references
#
# ALTERNATIVE:
#   Add this alias to your shell config (~/.zshrc or ~/.bashrc):
#   alias cclaude="op run --env-file=/Users/cliste/dev/cianfhoghlaim/.env.local -- claude"
# =============================================================================

set -euo pipefail

# Navigate to project root
cd "$(dirname "$0")/.." || exit 1

# Check if op CLI is available
if ! command -v op >/dev/null 2>&1; then
    echo "Error: 1Password CLI (op) not found." >&2
    echo "Install it: brew install 1password-cli" >&2
    exit 1
fi

# Check if .env.local exists
if [[ ! -f ".env.local" ]]; then
    echo "Error: .env.local not found in project root." >&2
    echo "Create it with op:// references for MCP server credentials." >&2
    exit 1
fi

# Launch Claude Code with secrets injected
exec op run --env-file=.env.local -- claude "$@"
