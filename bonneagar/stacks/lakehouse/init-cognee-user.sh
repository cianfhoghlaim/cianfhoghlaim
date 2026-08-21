#!/bin/bash
# =============================================================================
# COGNEE POST-INIT SHELL SCRIPT (added 2026-08-23 hardening)
# =============================================================================
# Runs AFTER init-db.sql via docker-entrypoint-initdb.d/ (alphabetical).
# Sets the cognee user's password from $COGNEE_POSTGRES_PASSWORD env var
# (which Locket resolves from dev-baile/lakehouse/cognee_postgres_password).
#
# Why a shell script (not init-db.sql):
#   Docker's postgres initdb scripts are SQL-only and don't have shell
#   variable interpolation. A shell script runs psql -c with the env var.
#
# Usage: mounted at /docker-entrypoint-initdb.d/02-init-cognee-user.sh in
# the postgres service (see compose.yaml).
# =============================================================================

set -euo pipefail

# Default fallback: use POSTGRES_PASSWORD (Locket resolves both from the
# same vault path; the cognee user only has permissions on
# cognee_cianfhoghlaim, so using the same password is safe).
COGNEE_PWD="${COGNEE_POSTGRES_PASSWORD:-${POSTGRES_PASSWORD:-no-key-needed}}"

echo "Setting cognee user password from COGNEE_POSTGRES_PASSWORD env var..."
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    ALTER USER cognee WITH PASSWORD '${COGNEE_PWD}';
EOSQL

echo "cognee user password updated successfully."
