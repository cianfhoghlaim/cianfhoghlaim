# Tuatha onboarding tasks

13 tasks across 4 phases. Each task is independently shippable as a commit
if necessary; the spec validates only when all 4 phases have landed.

## Phase 1 — IaC completion (5 NEW + 1 MODIFIED in `bonneagar/stacks/tuatha/`)

- [ ] 1.1 Write `bonneagar/stacks/tuatha/README.md` (~120 lines, mirror pocket-id/README.md)
- [ ] 1.2 Write `bonneagar/stacks/tuatha/secrets.env` (6 TUATH_* secret references with infisical URIs)
- [ ] 1.3 Write `bonneagar/stacks/tuatha/sidecar.yaml` (Locket sidecar template, mirror pocket-id/sidecar.yaml)
- [ ] 1.4 Write `bonneagar/stacks/tuatha/.env.example` (12 env vars for api/ui/game/langfuse)
- [ ] 1.5 Write `bonneagar/stacks/tuatha/blueprint.yaml` (2 private resources: tuath-api, tuath-ui)
- [ ] 1.6 Update `bonneagar/stacks/tuatha/pangolin.yaml` (replace singular `pangolin.resource.*` with plural `pangolin.resources.*`, drop the stale Tuath Dagster route)

## Phase 2 — Operator automation (4 NEW shell scripts in `scripts/`)

- [ ] 2.1 Write `scripts/onboard-tuatha.sh` (~120 L, mirror `onboard-pocketid.sh`; prompt for 11 secrets; optionally dry-run wire; 0 expected lines of Python)
- [ ] 2.2 Write `scripts/wire-tuatha.sh` (~280 L, 6-step wiring: Infisical seed → Pocket ID OIDC → Pangolin 3 resources → Komodo trigger → .env upsert → audit record)
- [ ] 2.3 Write `scripts/wire-tuatha-resource-idp.sh` (~180 L, 3-step IdP binding to the 2 TinyAuth-gated resources; skip game)
- [ ] 2.4 Write `scripts/rotate-tuatha-secrets.sh` (~190 L, with `--install-cron` writing `/etc/cron.d/tuatha-rotation`)

## Phase 3 — Tuatha code (9 NEW files in `tuatha/`)

- [ ] 3.1 Write `tuatha/README.md` (module-level overview, sub-module READMEs, dlt sources table, quick start, ops notes)
- [ ] 3.2 Write `tuatha/dlt/__init__.py` (re-export the 2 source functions)
- [ ] 3.3 Write `tuatha/dlt/_shared.py` (conventions: REPO_ROOT, PIPELINES_DIR, table-name constants, build_pipeline, observer_for)
- [ ] 3.4 Write `tuatha/dlt/player_assets.py` (dlt resource with 10 columns; 20-word Celtic corpus; `merge` write disposition)
- [ ] 3.5 Write `tuatha/dlt/credential_events.py` (dlt resource with 8 columns including sidecar MLflow + Langfuse trace IDs)
- [ ] 3.6 Write `tuatha/dlt/run_all.py` (orchestrator)
- [ ] 3.7 Write `tuatha/scripts/bootstrap.sh` (one-command local dev; sets USE_LOCAL_SCRAPES=true + USE_DUCKLAKE=false; seeds SpacetimeDB; runs dlt)
- [ ] 3.8 Write `tuatha/tests/test_smoke.py` (7 tests: imports, schema, observability, destination, run_all)
- [ ] 3.9 Run `python3 -m pytest tuatha/tests/test_smoke.py -v` (or skip if the dlt+ducklake env is missing; the tests gracefully skip)

## Phase 4 — OpenSpec change + README update

- [ ] 4.1 This `proposal.md` (DONE)
- [ ] 4.2 This `tasks.md` (DONE)
- [ ] 4.3 Write `specs/bonneagar-tuatha-iac-stack/spec.md` (5 new requirements: IaC GOLD_STANDARD)
- [ ] 4.4 Update repo `README.md` with a "Quick Start for Tuatha" section (3 commands)
- [ ] 4.5 Run `openspec validate 2026-07-29-tuatha-onboarding-and-wiring-v1 --strict`
- [ ] 4.6 Commit as 4 separate commits (one per phase) then push

## Final verification

- [ ] 4 files in `scripts/` pass `bash -n` (no syntax errors)
- [ ] 1 file in `tuatha/scripts/` passes `bash -n`
- [ ] `git status` clean after the 4 commits
- [ ] `git push` succeeds (no rebase conflicts)

## Dependency graph (Phase dependencies)

```
Phase 1 (IaC)               ──┐
                              ├──> Phase 4 (OpenSpec)
Phase 2 (Scripts)            ──┤
Phase 3 (Code)               ──┘

Phase 4 blocks the change archive: openspec requires everything in tasks.md
to be checked off before `openspec archive` will succeed.
```
