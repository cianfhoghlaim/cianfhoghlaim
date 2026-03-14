#!/bin/bash
# =============================================================================
# ANSIBLE VAULT PASSWORD SCRIPT
# =============================================================================
# Returns the vault password from environment variable.
# Used by ansible.cfg with vault_password_file setting.

if [ -n "$ANSIBLE_VAULT_PASSWORD" ]; then
    printf '%s' "$ANSIBLE_VAULT_PASSWORD"
elif [ -f /tmp/.vaultpass ]; then
    cat /tmp/.vaultpass
else
    echo "Error: ANSIBLE_VAULT_PASSWORD not set and /tmp/.vaultpass not found" >&2
    exit 1
fi
