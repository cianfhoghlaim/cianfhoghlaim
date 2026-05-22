#!/bin/bash
set -e

# Load local environment
if [ -f "../../../.env" ]; then
    export $(grep -v '^#' ../../../.env | xargs)
fi

echo "========================================"
echo "Pulumi Deployment with ESC & Infisical"
echo "========================================"

# Ensure Pulumi CLI is logged in
if ! pulumi whoami > /dev/null 2>&1; then
    echo "Logging into Pulumi local backend..."
    export PULUMI_CONFIG_PASSPHRASE="${PULUMI_CONFIG_PASSPHRASE:-local-dev-key}"
    pulumi login --local
fi

# Ensure ESC environment exists
if ! pulumi env ls | grep -q "infrastructure/oci"; then
    echo "Creating ESC environment 'infrastructure/oci'..."
    # Create the environment in the local organization
    pulumi env init infrastructure/oci
    
    # Apply the YAML definition
    cat esc-environment.yaml | pulumi env set infrastructure/oci
    echo "ESC environment configured."
else
    echo "Updating ESC environment..."
    cat esc-environment.yaml | pulumi env set infrastructure/oci
fi

echo ""
echo "Running Pulumi Up..."
pulumi stack select prod
pulumi up
