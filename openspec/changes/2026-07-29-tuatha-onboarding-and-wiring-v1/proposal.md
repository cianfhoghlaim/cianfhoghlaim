# Tuatha onboarding + wiring + lakehouse integration (v1)

## Why

The Tuatha educational MMO stack (`bonneagar/stacks/tuatha/`) is the only
public-facing web surface in the Cianfhoghlaim platform — yet it is the only
stack shipping without the GOLD_STANDARD IaC contract that Pocket ID has
demonstrated works. As shipped today:

- ✅ `compose.yaml`, `compose.dev.yaml`, `pangolin.yaml` exist
- ❌ No `README.md`, `secrets.env`, `sidecar.yaml`, `blueprint.yaml`,
     `.env.example` (operators learn 7 different patterns per stack)
- ❌ No onboarding / wiring / rotation scripts (Pocket ID has 4; Tuatha has 0)
- ❌ No dlt → MotherDuck lakehouse integration (player assets + credential
     events are not persisted to the central lakehouse)
- ❌ No OpenSpec change documenting the GOLD_STANDARD contract

Without this change, onboarding a new Tuatha operator takes 4–6 hours of
shape-rotating (RTFM over Discord) and the team has no observable rehearsal
loop for the LC Gaeilge content (cannot measure whether the in-game tutor
NPC actually helps students).

## What changes

This is a **multi-phase, single openspec change** that adds the same 4-script
automation pattern that Pocket ID owns (4 onboarding scripts → Pangolin +
Komodo + Locket sidecar + DaisyDisk-level IaC contract), and integrates
Tuatha's player assets + credential events into the shared
`md:cianfhoghlaim` MotherDuck lakehouse.

### Phase 1 — IaC completion (5 NEW files + 1 MODIFIED in `bonneagar/stacks/tuatha/`)

| File | Status | Purpose |
|:--|:--|:--|
| `README.md` | NEW | Explains what Tuatha is, why it matters, 5 features, 8 env vars, 3 routes |
| `secrets.env` | NEW | The 6 Locket-managed secrets (TUATH_OPENAI_API_KEY etc.) |
| `sidecar.yaml` | NEW | The Locket sidecar template (mirrors pocket-id exactly) |
| `blueprint.yaml` | NEW | Pangolin private-resource blueprint (3 named routes) |
| `.env.example` | NEW | Local dev env template (12 vars for api/ui/game/langfuse) |
| `pangolin.yaml` | MODIFIED | Replaces the singular `pangolin.resource.*` with the plural `pangolin.resources.*` form, consistent with pocket-id |

### Phase 2 — Operator automation (4 NEW scripts in `scripts/`)

| Script | Purpose | Mirrors |
|:--|:--|:--|
| `scripts/onboard-tuatha.sh` | TUI/CLI wizard for non-technical operators | `onboard-pocketid.sh` (172 L, colour-scheme identical) |
| `scripts/wire-tuatha.sh` | ONE-SHOT Pocket ID OIDC client + Pangolin 3 resources + Komodo trigger + Infisical seed | `wire-pocketid-pangolin-komodo.sh` (377 L) |
| `scripts/wire-tuatha-resource-idp.sh` | Binds Pocket ID as Resource IdP for the 2 TinyAuth-gated routes | `wire-pocketid-resource-idp.sh` |
| `scripts/rotate-tuatha-secrets.sh` | 90-day cron rotation via `--install-cron` → `/etc/cron.d/tuatha-rotation` | `rotate-pocketid-secrets.sh` (85 L) |

### Phase 3 — Tuatha code (4 NEW + 1 NEW package in `tuatha/`)

| File | Purpose |
|:--|:--|
| `tuatha/README.md` | Module-level README (3-level tree + dlt sources table + quick start + ops notes) |
| `tuatha/dlt/__init__.py` | Re-exports `player_assets_source` + `credential_events_source` |
| `tuatha/dlt/_shared.py` | Conventions: NEVER absolute namespaces, ALWAYS honour `USE_LOCAL_SCRAPES` / `USE_DUCKLAKE`, ALWAYS `DltRunObserver`, ALWAYS `pipelines_dir` under repo root |
| `tuatha/dlt/player_assets.py` | dlt source for per-player procedural asset ledger; 10 columns (asset_id, player_id, asset_kind, world_x/y/z, created_at, curriculum_hook, celtic_token_ga, celtic_token_en); 20-word Celtic vocabulary corpus + Celtic asset kinds |
| `tuatha/dlt/credential_events.py` | dlt source for auth + quest-completion events; 8 columns including sidecar `langfuse_trace_id` + `mlflow_run_id` |
| `tuatha/dlt/run_all.py` | Orchestrator that runs both sources sequentially |
| `tuatha/scripts/bootstrap.sh` | One-command local dev (build api/ui/game, seed SpacetimeDB, run dlt → local DuckDB) |
| `tuatha/tests/test_smoke.py` | 7 tests (imports, schema, observability, destination helper, run_all) |

### Phase 4 — OpenSpec change + README update (this directory + repo root)

| File | Purpose |
|:--|:--|
| `openspec/changes/2026-07-29-tuatha-onboarding-and-wiring-v1/proposal.md` | This document |
| `openspec/changes/2026-07-29-tuatha-onboarding-and-wiring-v1/tasks.md` | The 13-task execution checklist |
| `openspec/changes/2026-07-29-tuatha-onboarding-and-wiring-v1/specs/bonneagar-tuatha-iac-stack/spec.md` | The 5 new IaC requirements on the `bonneagar-tuatha-iac-stack` capability |
| `README.md` (repo root) | A new "Quick Start for Tuatha" section (3 commands) |

## Definition of done

- [ ] Phase 1: 5 NEW files + 1 MODIFIED in `bonneagar/stacks/tuatha/`
- [ ] Phase 2: 4 NEW shell scripts in `scripts/`, all pass `bash -n`
- [ ] Phase 3: 9 NEW files in `tuatha/` (1 README, 5 dlt, 1 scripts, 1 tests, 1 .env)
- [ ] Phase 4: This openspec change + the README Quick Start
- [ ] `openspec validate 2026-07-29-tuatha-onboarding-and-wiring-v1 --strict` passes
- [ ] All 4 commits land on the working branch

## Dependencies

- **Blocked by**: `2026-07-09-v6-drift-remediation-and-repo-boundary-lockdown-v1`
  (must archive first; this change needs the IaC + agent + docs baseline)
- **Blocks**: `2026-08-XX-cianfhoghlaim-cohort-tutor-v1` (which will use the
  `credential_events` pipeline + Langfuse traces to evaluate the tutor NPC
  via RAGAS)

## Why a single change (not 4)?

Pocket ID and Tuatha share the same operational story — once the operator
learns the 4-script pattern for Pocket ID they should not have to learn
another pattern for Tuatha. Shipping the 4 scripts in one change keeps that
ergonomic contract atomic.
