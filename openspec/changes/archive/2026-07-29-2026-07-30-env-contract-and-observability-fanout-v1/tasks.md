# Tasks: 2026-07-30-env-contract-and-observability-fanout-v1

11 actions across 4 sub-areas. Each task is independently shippable as a commit.

## Sub-area A — URI grammar unification

- [ ] **A.1** Extend `scripts/normalize-infisical-uri.ts` with a `--check-grammar` flag that returns non-zero exit code if any stack's `secrets.env` mixes the bare + Jinja forms
- [ ] **A.2** Add `[tasks."stack-doctor:strict"]` alias to `mise.toml` near line 991 that runs `bun run scripts/stack-doctor.sh --strict --check-grammar`

## Sub-area B — OTLP fan-out collector

- [ ] **B.1** Add `langfuse` exporter block to `bonneagar/stacks/logfire/config/otelcol.yaml` (parallel to the existing `logfire` exporter block at line 40-48). Add Langfuse endpoint / headers env vars (`LANGFUSE_OTLP_ENDPOINT`, `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`)
- [ ] **B.2** Modify `bonneagar/stacks/logfire/compose.yaml` lines 35-44: bind `4317/4318/8888/8889` to `127.0.0.1` only. Add `LANGFUSE_OTLP_ENDPOINT`, `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY` to the env block

## Sub-area C — OTEL/LANGFUSE wiring to memory + observability backends

- [ ] **C.1** graphiti: `compose.yaml` (after line 41) add 5 env vars; `secrets.env` (after line 19) add 3 LANGFUSE infisical refs
- [ ] **C.2** cognee: `compose.yaml` (after line 66) add 5 env vars; `secrets.env` (after line 18) add 3 LANGFUSE infisical refs
- [ ] **C.3** mlflow: `compose.yaml` (after line 61) add 5 env vars; `secrets.env` (after line 28) add 3 LANGFUSE infisical refs
- [ ] **C.4** agent-os: `secrets.env` add 5 infisical refs (LANGFUSE_HOST/PUBLIC_KEY/SECRET_KEY + OPENAI_API_KEY + ANTHROPIC_API_KEY)

## Sub-area D — Standardization + docs

- [ ] **D.1** `bonneagar/stacks/dagster/.env.dev` line 33: `LANGFUSE_HOST=http://langfuse:3000` → canonical comment-only (resolve from Infisical via `secrets.env`); add note that the previous default only worked when dagster shared a docker context with langfuse
- [ ] **D.2** NEW: `docs/observability/env-var-contract.md` (canonical 17-var reference: 7 LANGFUSE_* + 3 MLFLOW_* + 7 OTEL_* / LOGFIRE_*)
- [ ] **D.3** NEW: spec delta `specs/infrastructure-stacks/spec.md` (1 ADDED Requirement: the URI grammar must be unified)
- [ ] **D.4** NEW: spec delta `specs/agent-observability/spec.md` (2 ADDED Requirements: (a) the logfire collector must fan-out to langfuse + logfire; (b) every memory/observability backend must export OTLP)

## Final verification

- [ ] `openspec validate 2026-07-30-env-contract-and-observability-fanout-v1 --strict` passes
- [ ] `bun run scripts/stack-doctor.sh --strict --check-grammar` reports zero grammar-mixed `secrets.env` files
- [ ] `bash -n` on all 0 NEW shell scripts (this change has no shell scripts) — N/A
- [ ] All 14 modified files compile/parse (compose yaml + .env files are parsed by docker compose, not by our tooling; just verify with `docker compose config`)
- [ ] Git commit lands; push succeeds

## Dependency graph

```
A.1 ──► A.2 ──┐
              │
              ├──► B.1 ──► B.2 ──┐
              │                  │
              ├──► C.1 ──► C.2 ──► C.3 ──► C.4 ──┐
              │                                    │
              └──► D.1 ──► D.2 ──► D.3 ──► D.4 ──┘
                                                    │
                                                    ▼
                                          openspec validate --strict
                                                    │
                                                    ▼
                                                 commit + push
```