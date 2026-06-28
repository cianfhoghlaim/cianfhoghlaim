#!/usr/bin/env bash
#
# oideachais/scripts/make_target.sh — runtime helper for the multi-target
# deployment. Stage 4 of ``author-archive-v1``.
#
# Usage:
#   ./oideachais/scripts/make_target.sh                       # default: dev
#   ./oideachais/scripts/make_target.sh dev                   # local DuckDB
#   ./oideachais/scripts/make_target.sh staging               # MotherDuck
#   ./oideachais/scripts/make_target.sh prod                 # Garage + Lakekeeper
#   ./oideachais/scripts/make_target.sh prod "OIDEACHAIS_FORCE=1"
#
# What it does:
#   1. Resolves the target from $1 (or defaults to "dev")
#   2. Sources the target-specific env vars from Infisical (via locket
#      or .env hydration)
#   3. Runs the requested command with OIDEACHAIS_TARGET set
#
# The script never starts a DLT pipeline directly — it just sets the
# env vars and runs whatever the user passes. The Dagster assets and
# the DLT sources pick up the env vars via get_target().

set -euo pipefail

TARGET="${1:-dev}"
shift || true

case "$TARGET" in
    dev|staging|prod)
        ;;
    --help|-h)
        cat <<EOF
Usage: $0 [dev|staging|prod] [command...]

  dev      Local DuckDB at ~/.cache/oideachais/author_archive.duckdb
  staging  MotherDuck (managed DuckDB). Requires MOTHERDUCK_TOKEN.
  prod     Garage S3 + Lakekeeper DuckLake. Requires DUCKLAKE_* and BUCKET.

Examples:
  $0
  $0 dev python -c "from oideachais.dlt_utils.target_factory import get_target; print(get_target().name)"
  $0 staging ./scripts/run_author_archive.sh
  $0 prod

If no command is given, the script just prints the resolved target
and exits. Use it to wrap any author-archive pipeline command.
EOF
        exit 0
        ;;
    *)
        echo "ERROR: unknown target '$TARGET'. Choose dev|staging|prod." >&2
        exit 2
        ;;
esac

# Resolve the absolute path to the repo root (parent of oideachais/).
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Source the env file if it exists (mise / locket hydrates this).
if [ -f "$REPO_ROOT/.env" ]; then
    set -a
    . "$REPO_ROOT/.env"
    set +a
fi

# Export the target selector so get_target() picks it up.
export OIDEACHAIS_TARGET="$TARGET"

# Pre-flight: validate secrets for non-dev targets.
if [ "$TARGET" = "staging" ] && [ -z "${MOTHERDUCK_TOKEN:-}" ]; then
    echo "ERROR: TARGET=staging requires MOTHERDUCK_TOKEN." >&2
    echo "       Run via mise: mise run oideachais:staging" >&2
    echo "       Or set MOTHERDUCK_TOKEN in your shell." >&2
    exit 3
fi

if [ "$TARGET" = "prod" ]; then
    for var in DUCKLAKE_POSTGRES_HOST DUCKLAKE_POSTGRES_PORT \
               DUCKLAKE_POSTGRES_DB DUCKLAKE_POSTGRES_USER \
               DUCKLAKE_POSTGRES_PASSWORD BUCKET; do
        if [ -z "${!var:-}" ]; then
            echo "ERROR: TARGET=prod requires $var." >&2
            echo "       Run via mise: mise run oideachais:prod" >&2
            exit 3
        fi
    done
fi

echo "[make_target] OIDEACHAIS_TARGET=$TARGET"
echo "[make_target] PIPELINE: ${OIDEACHAIS_PIPELINE_NAME:-<unset>}"
echo "[make_target] NAMESPACE: ${OIDEACHAIS_NAMESPACE:-oideachais}"

# If no command was passed, just print the resolved target and exit.
if [ $# -eq 0 ]; then
    echo "[make_target] No command supplied. Use --help for examples."
    exit 0
fi

# Run the requested command with the target env set.
echo "[make_target] exec: $*"
exec "$@"
