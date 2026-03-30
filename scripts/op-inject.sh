#!/usr/bin/env bash
# =============================================================================
# 1Password Secret Injection for mise hooks
# =============================================================================
# This script is called by mise hooks to inject/unset secrets from 1Password.
#
# USAGE:
#   source scripts/op-inject.sh        # Inject secrets (enter hook)
#   source scripts/op-inject.sh unset  # Unset secrets (leave hook)
#
# PERFORMANCE:
#   - Uses `op inject` for single API call (vs multiple `op read` calls)
#   - Caches to .env file to avoid repeated API calls
#   - Only regenerates if .op.env is newer than .env
#
# REQUIREMENTS:
#   - 1Password CLI (op) installed and authenticated
#   - .op.env template file with op:// references
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ENV_OP_FILE="$PROJECT_ROOT/.op.env"
ENV_FILE="$PROJECT_ROOT/.env"
LOCK_FILE="$PROJECT_ROOT/.env.lock"

# List of env vars to unset (must match .op.env)
ENV_VARS=(
    "BROWSERBASE_API_KEY"
    "BROWSERBASE_PROJECT_ID"
    "FIRECRAWL_API_KEY"
    "Z_AI_API_KEY"
    "HUGGINGFACE_TOKEN"
    "LETTA_API_KEY"
    "PYDANTIC_AI_GATEWAY_API_KEY"
    "LOGFIRE_TOKEN"
    "LANGFUSE_PUBLIC_KEY"
    "LANGFUSE_SECRET_KEY"
    "FORGEJO_TOKEN"
    "OPENAI_API_KEY"
    "GOOGLE_API_KEY"
    "OP_CONNECT_HOST"
    "OP_CONNECT_TOKEN"
)

unset_env_vars() {
    for var in "${ENV_VARS[@]}"; do
        unset "$var" 2>/dev/null || true
    done
}

inject_secrets() {
    # Check if op CLI is available
    if ! command -v op >/dev/null 2>&1; then
        echo "[op-inject] Warning: 1Password CLI (op) not found." >&2
        if [[ -f "$ENV_FILE" ]]; then
            set -a
            source "$ENV_FILE"
            set +a
            echo "[op-inject] Loaded cached secrets from .env" >&2
        else
            echo "[op-inject] No .env cache available. MCP servers may not work." >&2
        fi
        return 0
    fi

    # Check if .op.env template exists
    if [[ ! -f "$ENV_OP_FILE" ]]; then
        echo "[op-inject] Warning: $ENV_OP_FILE not found. Skipping." >&2
        return 0
    fi

    # Check if regeneration is needed (template newer than output)
    if [[ -f "$ENV_FILE" ]] && [[ "$ENV_FILE" -nt "$ENV_OP_FILE" ]]; then
        set -a
        source "$ENV_FILE"
        set +a
        return 0
    fi

    # Prevent concurrent injection with file locking
    exec 200>"$LOCK_FILE"
    if ! flock -n 200 2>/dev/null; then
        # flock not available on macOS, try alternative
        if [[ -f "$LOCK_FILE.pid" ]]; then
            if kill -0 "$(cat "$LOCK_FILE.pid")" 2>/dev/null; then
                echo "[op-inject] Another injection in progress, using cached .env" >&2
                if [[ -f "$ENV_FILE" ]]; then
                    set -a
                    source "$ENV_FILE"
                    set +a
                fi
                return 0
            fi
        fi
    fi
    echo $$ > "$LOCK_FILE.pid"

    echo "[op-inject] Injecting MCP secrets from 1Password..." >&2

    # Use op inject to resolve all secrets in one API call
    if op inject --in-file "$ENV_OP_FILE" --out-file "$ENV_FILE" 2>/dev/null; then
        chmod 600 "$ENV_FILE"
        rm -f "$LOCK_FILE.pid"
        set -a
        source "$ENV_FILE"
        set +a
        echo "[op-inject] Done! Secrets injected." >&2
    else
        rm -f "$LOCK_FILE.pid"
        echo "[op-inject] Warning: Failed to inject. Check 1Password auth." >&2
        # Fall back to cached .env if available
        if [[ -f "$ENV_FILE" ]]; then
            echo "[op-inject] Using cached .env as fallback." >&2
            set -a
            source "$ENV_FILE"
            set +a
        fi
    fi

    exec 200>&- 2>/dev/null || true
}

# Main logic
if [[ "${1:-}" == "unset" ]]; then
    unset_env_vars
else
    inject_secrets
fi
