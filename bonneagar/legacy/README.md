# Legacy Scripts

These standalone TypeScript scripts have been replaced by Komodo actions and procedures.

## Archived Scripts

| Script | Replacement | Notes |
|--------|-------------|-------|
| `cloudflare-dns.ts` | `komodo/actions/sync-dns-records.ts` | DNS sync now uses Komodo server data |
| `pangolin-setup.ts` | `komodo/actions/setup-pangolin-site.ts` | Pangolin site setup via Komodo action |
| `servers.ts` | `komodo/actions/generate-ansible-inventory.ts` | Inventory generation from Komodo servers |
| `taisce-deploy.ts` | `komodo/procedures/deploy-storage-stack.toml` | Orchestration via Komodo procedures |

## Using the New Actions

```bash
# Sync DNS records
km run action sync-dns-records --dryRun=true

# Setup Pangolin site
km run action setup-pangolin-site --server=arm1-oci

# Generate Ansible inventory
km run action generate-ansible-inventory

# Validate deployments
km run action validate-deployments
```

## Using the New Procedures

```bash
# Initialize a new site
km run procedure init-site

# Sync infrastructure before deployment
km run procedure sync-infrastructure

# Deploy storage stack
km run procedure deploy-storage-stack

# Deploy dev tools
km run procedure deploy-devtools
```

## Note on ansible.ts

The `ansible.ts` script remains in the main directory (`/bonneagar/ansible.ts`) as it handles Ansible vault encryption which is not yet replicated in Komodo actions.

## Migration Date

Scripts archived: 2025-12-27
