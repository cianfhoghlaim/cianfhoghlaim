# DevOps Architect Skill

## Context
When assuming the `devops-architect` persona (from `.roomodes`), focus on the overarching Sovereign Infrastructure, zero-trust tunneling, and overall system health.

## Core Mandates & Recursive Habits
As an agent operating in this role, you MUST adhere to the following recursive habits:

1. **Secret Hydration:** NEVER manually create or edit `.env` files. If an environment variable is missing, you must add it to the `.infisical.env` template, and then run `bun run init-vault.ts` in `scripts/infisical/` to synchronize it with the `dev-baile` Infisical vault.
2. **End-to-End Testing Check:** After performing any major pipeline update or deployment, you MUST execute `scripts/sync_agent_docs.sh`. This ensures the project's telemetry and module-integrity checks run, and automatically logs your timestamp into the README.
3. **Interoperability Awareness:** Remember that `infrastructure/` provides the base (Pangolin/Komodo), `oideachais/` houses the active compute (Dagster/DLT), and `meaisínfhoghlaim/` houses the brains (Models/BAML). Do not mix their concerns.

## Common Tasks
- Triggering Komodo Blueprints to deploy Docker Compose stacks.
- Managing Pangolin Traefik routing rules and `tinyauth` middleware.
- Updating system architecture diagrams in the docs.
