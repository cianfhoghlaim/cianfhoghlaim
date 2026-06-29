# Stacks Consolidation — DEFERRED (per user "6")

> **Per user "6 leave stacks separate for now pending infisical and komodo full setup"** — the 16+ Docker Compose stacks remain as separate Compose files for now.

## 1. Why deferred

The user explicitly asked to keep stacks separate until:
- **Infisical is fully set up** (secrets management)
- **Komodo is fully set up** (orchestrator)

These are prerequisites for the consolidated approach:
- Each stack today has its own `secrets.env` file
- A consolidated stack would need centralized secret injection via Infisical
- Komodo's `[[resource_sync]]` primitive is needed to manage the consolidated file

## 2. Current state (16+ stacks at cianfhoghlaim/stacks/)

```
stacks/
├── backrest/
├── cognee/
├── croilar/
├── cuckoo/            (newest, not yet in Wave 1)
├── d4rl/              (newest)
├── dagster/           (legacy)
├── dragonfly/
├── falkordb/
├── graphiti/
├── infisical/         (the secrets manager itself)
├── invokeai/
├── komodo/            (the orchestrator itself)
├── lakehouse/         (the 13-service data plane)
├── langfuse/
├── lakehouse/         (legacy)
├── logfire/
├── marimo/            (new)
├── mlflow/
├── motherduck/
├── oci/               (the cloud platform)
├── olake/
├── ollama/            (new)
├── openchamber/       (new)
├── openclaw/          (new)
├── paddleocr/
├── pangolin/          (the reverse proxy)
├── risingwave/
└── ... (more)
```

## 3. When to revisit

After both:
- **Infisical fully set up** (all stack secrets migrated from `secrets.env` to Infisical paths like `infisical://dev-baile/<stack>/<key>`)
- **Komodo fully set up** (with `[[resource_sync]]` for the consolidated file)

Then the consolidation can proceed. The plan v6 Phase F11 (move + merge stacks) covers this.

## 4. Intermediate step (before full consolidation)

To reduce risk while waiting for Infisical + Komodo:
- **Centralize the secrets file** — all 16+ stacks can share 1 `secrets.env.template` even if they remain separate Compose files
- **Use Komodo's `[[resource_sync]]` primitive** to manage the centralized template
- **Document the secret-dependency graph** — which stack needs which secret, so we can plan the consolidated file

## 5. Next step (until consolidation)

Continue per-domain work:
- Per-domain Dagster Component migration (per audit/dagster-component-migration-plan.md)
- Per-domain BAML merger (per audit/baml-merger-plan.md)
- Per-domain web app consolidation (per audit/web-app-consolidation-plan.md)
- OCR model audit (per audit/ocr-model-audit.md)

These per-domain works do NOT require stack consolidation.
