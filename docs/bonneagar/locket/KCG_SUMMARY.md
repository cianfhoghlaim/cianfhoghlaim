# Locket — KCG Summary

## What It Is
Locket is a secret injection sidecar by Bradley that resolves Infisical URI references at container runtime. It mounts a tmpfs volume with hydrated secrets, allowing containers to access credentials without hardcoded `.env` files or Kubernetes secrets.

## Why This Matters for Kings' College Galway
Every production Docker Compose stack uses a `sidecar.yaml` that defines a Locket container. Locket reads `secrets.env` templates (containing `{{ infisical:///<key> }}` references), resolves them against the Infisical vault, and writes hydrated secrets to `/run/secrets/locket/secrets.env` on a non-root tmpfs. This means no `.env` file is ever committed or exposed.

## Key Patterns
- **Infisical provider**: `--provider=infisical` with machine identity client credentials
- **Watch mode**: `--mode=watch` auto-reloads secrets when Infisical vault changes
- **Tmpfs secrets**: `/run/secrets/locket` is a memory-only tmpfs — never touches disk
- **Service dependency**: `depends_on: locket: condition: service_healthy` in sidecar.yaml

## Source Files
Full source code was removed (2026-06-05). Available at <https://github.com/bpbradley/locket>. Live sidecar configs are in every `infrastructure/stacks/*/*/sidecar.yaml`.
