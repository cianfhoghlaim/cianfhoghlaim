#!/bin/bash
# =============================================================================
# ANSIBLE EXECUTION ENVIRONMENT ENTRYPOINT
# =============================================================================
# Sets up the vault password file from environment variable if provided.

set -e

# Create vault password file if ANSIBLE_VAULT_PASSWORD is set
if [ -n "$ANSIBLE_VAULT_PASSWORD" ]; then
    printf '%s' "$ANSIBLE_VAULT_PASSWORD" > /tmp/.vaultpass
    chmod 600 /tmp/.vaultpass
    export ANSIBLE_VAULT_PASSWORD_FILE=/tmp/.vaultpass
fi

# Create SSH directory if it doesn't exist
mkdir -p /root/.ssh
chmod 700 /root/.ssh

# Disable strict host key checking if running non-interactively
if [ ! -t 0 ]; then
    if [ ! -f /root/.ssh/config ]; then
        echo "StrictHostKeyChecking no" > /root/.ssh/config
        echo "UserKnownHostsFile /dev/null" >> /root/.ssh/config
        chmod 600 /root/.ssh/config
    fi
fi

# Execute the command
exec "$@"
