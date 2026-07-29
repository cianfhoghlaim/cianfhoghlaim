# 2026-07-30-env-contract-and-observability-fanout-v1

## Why

The 91-stack cianfhoghlaim platform is structurally complete (every stack ships
the 6-file GOLD_STANDARD contract; the Infisical + Locket + mise three-way
secret contract is mature; the 12-script `cianfhoghlaim:*` CLI is shipped) —
but the platform is **observability-coherent only at the surface layer** and
**env-coherent in two competing grammars**. Three concrete gaps surfaced from a
2026-07-29 full-tree audit:

1. **Dual Infisical URI grammar.** 39 of 86 `secrets.env` files use the
   Jinja `{{ infisical:///KEY?path=/X }}` form; 52 use the bare
   `infisical://dev-baile/<svc>/<key>` form. The bons-locket-shim v0.2.0
   parses only the Jinja form; `init-vault.ts` parses only the bare form.
   `init-vault.ts` silently misses any Jinja line; the shim silently misses
   any bare line. The two systems never see the same secrets.
2. **OTLP fan-out split.** The 3 agent surfaces (openchamber, openclaw,
   hermes) send OTLP to `langfuse-web:3000/api/public/otel`. The 3 data-plane
   stacks (dagster, khoj, letta) send OTLP to `logfire-otel:4317`. There is
   no shared collector that fans out to both. The `agent-observability`
   SKILL.md claims "all 3 surfaces route to langfuse", which is false for
   the data plane — a single pane of glass does not exist.
3. **3 memory/observability backends emit zero traces.** `graphiti`,
   `cognee`, and `mlflow` declare no `OTEL_*` or `LANGFUSE_*` env vars. Their
   FastAPI / ML server requests are invisible to both Langfuse and Logfire.
   The 7-phase cognition pipeline from the skill says Phase 7 (Monitor)
   covers everything; reality covers only the langfuse-tracked surfaces.

This change ships the foundation that Changes 2 and 3 (in the 2026-07-30
"cohesive-stack-config-and-wiring" trilogy) build on top of.

## What changes

This is a single openspec change with 4 sub-areas. **11 sub-actions total.**

### Sub-area A — URI grammar unification (Action 1)

- **NEW**: 1 inline check in `scripts/normalize-infisical-uri.ts` that flags
  any stack with mixed-grammar `secrets.env` (line 13-19 audit hook)
- **MODIFIED**: `mise.toml` — add the `[tasks."stack-doctor:strict"]` alias
  that runs `bun run scripts/stack-doctor.sh --strict --check-grammar` (line
  991 area)

### Sub-area B — OTLP fan-out collector (Actions 5, 8)

- **MODIFIED**: `bonneagar/stacks/logfire/config/otelcol.yaml` — add a
  `langfuse` exporter block alongside the existing `logfire` exporter; route
  the `traces` pipeline through both via `exporters: [logfire, langfuse,
  debug]`
- **MODIFIED**: `bonneagar/stacks/logfire/compose.yaml` — bind OTLP ports
  `4317` / `4318` to `127.0.0.1` only (was `0.0.0.0`); bind health/metrics
  ports (`8888` / `8889`) the same way; explicit `cianfhoghlaim` network
  allowlist

### Sub-area C — OTEL/LANGFUSE wiring to memory + observability backends (Actions 3, 4)

For each of `graphiti`, `cognee`, `mlflow`:

- **MODIFIED**: `compose.yaml` — add to the env block:
  ```yaml
  OTEL_EXPORTER_OTLP_ENDPOINT: http://logfire-otel:4317
  OTEL_EXPORTER_OTLP_PROTOCOL: grpc
  OTEL_SERVICE_NAME: <graphiti|cognee|mlflow>
  LANGFUSE_HOST: ${LANGFUSE_HOST:-http://langfuse:3000}
  LANGFUSE_PUBLIC_KEY: ${LANGFUSE_PUBLIC_KEY:-}
  LANGFUSE_SECRET_KEY: ${LANGFUSE_SECRET_KEY:-}
  ```
- **MODIFIED**: `secrets.env` — add the corresponding
  `infisical://dev-baile/<svc>/<key>` lines

For `agent-os` only:

- **MODIFIED**: `secrets.env` — add `LANGFUSE_HOST/PUBLIC_KEY/SECRET_KEY` +
  `OPENAI_API_KEY` + `ANTHROPIC_API_KEY` (the 4 AgentOS instances silently
  lose Langfuse today because the compose declares `LANGFUSE_*` but the
  shim never injects them)

### Sub-area D — Standardization + docs (Actions 6, 9, 10)

- **MODIFIED**: `bonneagar/stacks/dagster/.env.dev` — `LANGFUSE_HOST` → use
  canonical Infisical key (was hardcoded `http://langfuse:3000` which only
  works inside the same docker context)
- **NEW**: `docs/observability/env-var-contract.md` — canonical 17-var
  reference for the Langfuse + MLflow + Logfire observability stack

## Definition of done

- [ ] All 11 sub-actions above land
- [ ] `openspec validate 2026-07-30-env-contract-and-observability-fanout-v1 --strict` passes
- [ ] `mise run stack-doctor:strict` passes with zero grammar-mixed `secrets.env` warnings
- [ ] `mise run lint:skills` passes (53/53 skills still validate)
- [ ] 1 commit lands on the working branch with the spec delta + 2 spec files
- [ ] Push succeeds

## Dependencies

- **Blocked by**: nothing (foundation change; unblocks Changes 2 + 3)
- **Blocks**: `2026-07-31-agentic-mesh-and-ocr-pipeline-coherence-v1` (URI
  grammar MUST be unified before any new env vars land; otherwise they land
  in the wrong form)
- **Soft-blocked by**: `2026-07-09-v6-drift-remediation-and-repo-boundary-lockdown-v1`
  (must archive first per the `Blocked by:` edges convention)

## Why a single change (not 4)?

Sub-areas A/B/C/D are co-dependent in a way that does not split cleanly:

- (C) requires (A) — the new OTEL/LANGFUSE env vars added to graphiti/cognee/mlflow
  must use the canonical bare-grammar form
- (B) requires (C) — the langfuse OTLP fanout only matters if there are
  consumers sending traces
- (D) requires all of (A)/(B)/(C) — the env-var-contract doc is the single
  place that pins the canonical form, the fan-out, and the per-stack wiring
  in one table

Splitting into 4 PRs would require 4 rebases against this same change. One
PR, ~13 file diffs, lands cleanly.

## Cross-repo sync

This change touches only this repo (cianfhoghlaim). No `cross-repo-sync.md`
needed. The `leabharlann` corpus repo is unaffected.