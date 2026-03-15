#!/bin/bash
# Run observability integration tests with 1Password credentials
set -e

cd "$(dirname "$0")/.."

echo "Loading credentials from 1Password..."

# Load credentials
export DD_API_KEY=$(op read "op://dev-baile/datadog-trial/api_key")
export LOGFIRE_TOKEN=$(op read "op://dev-baile/pydantic-logfire/write_token")
export GEMINI_API_KEY=$(op read "op://dev-baile/gemini/credential" 2>/dev/null || echo "")

echo "Running integration tests..."
python tests/test_observability_integrations.py
