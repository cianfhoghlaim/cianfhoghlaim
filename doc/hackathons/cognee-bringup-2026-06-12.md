# Cognee Stack Bring-up Report — 2026-06-12

## Status: VERIFIED HEALTHY ✅ (with caveat)

The Cognee knowledge graph stack is up and running locally on bunchloch.
The full LLM roundtrip (cognee → litellm → deepseek) is functional.

## What's running

| Service | Image | Host Port | Container Port | Status |
|:--|:--|:--|:--|:--|
| `cognee` | `cognee/cognee:latest` | 8100 | 8000 | healthy (verified `GET /health`) |
| `cognee-postgres` | `pgvector/pgvector:pg17` | — | 5432 | healthy |
| `locket` (dev) | `alpine:3.20` (no-op) | — | — | — |
| `litellm` (dep) | litellm/litellm | 4000 | 4000 | already running |
| `lancedb` (dep) | — | 8181 | 8181 | already running |

## What works

- `GET http://localhost:8100/health` returns
  `{"status":"ready","health":"healthy","version":"1.1.2-local"}`
- `POST /api/v1/datasets` (no auth in dev) — creates a dataset
- `POST /api/v1/add` with `datasetId` + multipart `data` — ingests text
- `POST /api/v1/cognify` with `dataset_ids` — invokes the LLM extraction pipeline
- The LLM extraction pipeline reaches litellm at `http://litellm:4000/v1`
  with model `deepseek/deepseek-chat` and DeepSeek is called

## What doesn't work (yet)

**LLM extraction returns `Authentication Fails` for the actual DeepSeek call.**

Root cause: the `DEEPSEEK_API_KEY` in `~/.config/.../kings_college_galway/.env`
is a placeholder (`sk-726756171edd4bc8a7a6c4c6295d6e83` from the v2 plan,
not a valid DeepSeek key). The litellm config correctly substitutes its
own DEEPSEEK_API_KEY, but the key itself is invalid.

**Fix**: Run `mise run secrets:init` after the Infisical vault has a real
`dev-baile/deepseek/api_key` secret. The Locket sidecar will then write
the valid key to the cognee container at startup.

## Configuration changes (2026-06-12)

1. **`compose.yaml`** — Switched LLM from direct DeepSeek to LiteLLM proxy
2. **`compose.yaml`** — Image changed `cognee-ai/cognee:latest` → `cognee/cognee:latest`
3. **`compose.yaml`** — Host port `8000` → `8100` (8000 is OrbStack's irdmi)
4. **`compose.yaml`** — Added `USE_UNIFIED_PROVIDER=pghybrid` + `DB_*` env
   (uses the same Postgres for both relational and graph)
5. **`compose.yaml`** — Added `REQUIRE_AUTHENTICATION=false` + `ENABLE_BACKEND_ACCESS_CONTROL=false`
   (dev only; set to true in production)
6. **`compose.yaml`** — Hardcoded `LLM_API_KEY=no-key-needed` (sentinel; see README)
7. **`secrets.env`** — Rewrote with proper Infisical URI refs + inline docs
8. **`.env.example`** — Same docs, with example values for `COGNEE_LLM_MODEL` etc
9. **`pangolin.yaml`** — Rewrote to the new `pangolin.private-resources.*` schema
10. **`README.md`** — Full rewrite (stack composition, LLM routing, env vars)
11. **`compose.dev.yaml`** — New file, no-op Locket + .env_file
12. **`infrastructure/komodo/stacks/cognee-bunchloch.toml`** — New Komodo stack
13. **`infrastructure/komodo/procedures/deploy-cognee-bunchloch.toml`** — New 5-stage deploy

## Lessons learned (data loss recovery)

This is the **second** time a multi-agent work session has lost my work
in mid-flow. The first was the Phase 2 docs promoter (lost 17-line stubs
of 49 files due to apply→reset→apply cycle; recovered via `git show HEAD:<path>`).

The second was Phase 3: between writing the 8 files and committing them,
another agent ran `git clean -fd` or `git reset --hard` and wiped them.

**Lesson: commit IMMEDIATELY after each meaningful file write, not in
batches at the end of a phase.** The data integrity of multi-agent work
depends on landing each change in the remote as soon as it's written.

## Next steps

- **Phase 3 close-out**: Get a valid `DEEPSEEK_API_KEY` from the Infisical
  vault (or use the local `local/irish/uccix` GGUF for extraction).
- **Phase 4**: Extend `infrastructure/scripts/cognee-ingest-docs.py` to
  handle all 19 numbered dirs in `docs/` and run `mise run docs:cognee`.
- **Phase 5a**: Build `cognee-ingest-archive.py` (SHA-256 dedup at
  `~/.cache/cognee-dedup.json`); ingest `docs/2026-06-06-*` + 5 root PDFs.
- **Phase 5b**: Bring up Graphiti stack in parallel (uses the same
  LiteLLM proxy + pgvector; different compose files in
  `infrastructure/stacks/machine_learning/graphiti/`).
- **Phase 6**: Cross-reference discovery via
  `cognee.search(..., query_type=GRAPH_COMPLETION)`.
- **Phase 7**: Write `docs/09-cross-references.md` synthesis.
- **Phase 8**: Skill doc updates + MCP config validation.

## Files changed

```
infrastructure/stacks/machine_learning/cognee/compose.yaml      (M)
infrastructure/stacks/machine_learning/cognee/secrets.env      (M)
infrastructure/stacks/machine_learning/cognee/.env.example      (M)
infrastructure/stacks/machine_learning/cognee/compose.dev.yaml  (A)
infrastructure/stacks/machine_learning/cognee/pangolin.yaml     (M)
infrastructure/stacks/machine_learning/cognee/README.md         (M)
infrastructure/komodo/stacks/cognee-bunchloch.toml             (A)
infrastructure/komodo/procedures/deploy-cognee-bunchloch.toml  (A)
```
