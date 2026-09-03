# BIEP v3 — FAQ (the canonical FAQ for operators)

> Per the `2026-08-13-biep-v3-systematic-download-ireland-england-v1`
> openspec change. The canonical FAQ for BIEP v3 operators.

## Q: How do I add a new jurisdiction to the BIEP v3?

A: Follow the canonical 4-step pattern:

1. **Add the per-jurisdiction BAML `subject_taxonomy.baml`** in
   `baml_src/british_isles/<jurisdiction>/education/subject_taxonomy.baml`
   with the canonical `Enum <Jurisdiction>Level { GCSE, A_LEVEL, ... }`
   + `Enum <Jurisdiction>Subject { ... }` + `function Extract<Jurisdiction>Syllabus(...)`.
2. **Add the per-jurisdiction DLT pipeline** in
   `dlt_sources/british_isles/<jurisdiction>/education/<jurisdiction>_jurisdiction_pipeline.py`
   (subclass of `JurisdictionPipelineBase`, STAGE = the canonical stage).
3. **Add the per-jurisdiction Dagster assets** in
   `orchestration/defs/2_materials/<jurisdiction>_education/<jurisdiction>_assets.py`
   (3 generic assets + 3 asset checks + per-subject backfill jobs).
4. **Add the per-jurisdiction MotherDuck Dive** in
   `motherduck/dives/<jurisdiction>_curriculum_dive.py` + the per-jurisdiction
   `load_<jurisdiction>_subjects()` in
   `dlt_sources/british_isles/_cross/registry_loader.py`.

## Q: How do I add a new BAML `Extract*` function?

A: See `docs/agents/biiep-v3-baml-client.md` for the full pattern. The
short version:

1. Add the function to the per-jurisdiction `subject_taxonomy.baml` with
   `client BIEPV3Extract` and a structured `*Spec` return type.
2. Add a `Test {function_name} { ... }` block with a sample PDF text
   (Phase 4 BAML Test).
3. Run `cd baml_src && uv run baml-cli generate` to compile.
4. Run `cd baml_src && uv run baml-cli test` to validate the test.

## Q: How do I change the scheduling policy?

A: Edit `orchestration/automation/biiep_scheduling.py` and run
`mise run biep:v3:lint` to validate. The canonical 4-cadence policy
(yearly + monthly + weekly + nightly + event-driven) is documented in
`docs/agents/biiep-v3-cron-schedule.md`.

## Q: How do I add a new scan domain (filesystem + language)?

A: See `docs/agents/biiep-v3-bie-8-jurisdictions.md` for the full
pattern. The short version:

1. Add the per-source DLT sources in
   `dlt_sources/<domain>/<source>.py` (e.g. `dlt_sources/filesystem/email_inbox.py`).
2. Add the per-domain generic Dagster assets in
   `orchestration/defs/2_materials/<domain>_pipelines/generic_<domain>_assets.py`.
3. Add the per-domain monthly MotherDuck Flight in
   `motherduck/flights/<domain>_monthly_sync_flight.py`.
4. Add the per-domain MotherDuck Dive in
   `motherduck/dives/<domain>_sources_overview_dive.py`.

## Q: How do I run the BIEP v3 setup on a new machine?

A: Run the canonical operator surface:

```bash
mise run biep:v3:setup
```

This single command handles the entire BIEP v3 setup:
1. Checks Docker
2. Brings up the lakehouse stack (13 services)
3. Smoke-tests the lakehouse
4. Runs BAML codegen
5. Seeds the registry
6. Creates the Lance namespace
7. Validates the 4 openspec changes
8. Runs lint:skills

## Q: How do I check the BIEP v3 status?

A: Run the canonical operator surface:

```bash
mise run biep:v3:status
```

This shows the current state of:
- The 13 lakehouse services
- The 428-cohort registry
- The Dagster assets
- The MotherDuck Dives + Flights
- The Mise tasks
- The 4 openspec changes

## Q: How do I check the BIEP v3 asset checks?

A: Run the canonical milestone gate:

```bash
mise run biep:v3:gate --milestone=m<N>
```

This runs the 3 asset checks for the specified milestone and reports
the exit code + stdout + stderr.

## Q: How do I add a new notebook to the BIEP v3 surface?

A: Add a new `notebooks/<NN>_<name>.py` marimo notebook. The notebook
should:

1. Use the canonical `notebooks._shared.db.connect_md()` for ibis-first
   access to the lakehouse.
2. Render the per-jurisdiction cohort matrix + drill-down + RAGAS scores
   + asset check status.
3. Use the canonical 8-cell pattern (intro + ibis conn + commands +
   cohort matrix + drill-down + schedule + asset check + dive link).
4. Run `mise run lint:skills` to validate skill metadata.

## Q: How do I add a new MotherDuck Dive?

A: Add a new file in `motherduck/dives/<jurisdiction>_<topic>_dive.py`.
The Dive should:

1. Use the canonical `DiveSpec` dataclass (from `motherduck/dives/__init__.py`).
2. Use a SQL query that reads from the canonical BIEP v3 namespace
   (`cianfhoghlaim.education.<jurisdiction>.<stage>.<subject>.voted_canonical`).
3. Include the per-jurisdiction BAML function flag (e.g. `is_welsh_medium`,
   `is_french_bac`, `has_manx_language`, `is_local_qualification`).
4. Have a canonical name (`<jurisdiction>_<topic>_dive`).

## Q: How do I add a new openspec change for the BIEP v3?

A: Follow the canonical openspec pattern:

```bash
openspec list
# Find an existing change to model
openspec show <existing-change-id>
# Create a new change
mkdir -p openspec/changes/<YYYY-MM-DD>-<name>-v1
# Write proposal.md + tasks.md + specs/<capability>/spec.md
openspec validate <new-change-id> --strict
```

## Q: How do I add a new change-detection sensor?

A: Add a new file in `orchestration/sensors/<source>_sensor.py`. The
sensor should:

1. Use the canonical `@sensor` decorator + `SensorEvaluationContext`.
2. Use a cursor for incremental updates.
3. Return `RunRequest(run_key=..., tags={...})` per detected change.
4. The sensor is automatically picked up by the BIEP v3 orchestration
   walker.

## Q: How do I add a new infisical secret?

A: Add the secret to `.infisical.env` (the canonical template) and run
`mise run secrets:init` (which delegates to `scripts/init-vault.ts`).
The mise.toml + Infisical hydration handles the rest.

## Q: How do I roll back a BIEP v3 change?

A: Use git:

```bash
git revert <commit-hash>
git push
```

The BIEP v3 setup is reproducible from scratch — just delete the
`storage/data/lancedb/` + `storage/data/ducklake/` + the
`postgresql://lakekeeper:devpassword@localhost:5433/ducklake_cianfhoghlaim`
DB and re-run `mise run biep:v3:setup`.

## Q: How do I report a bug?

A: File an issue at https://github.com/cianfhoghlaim/cianfhoghlaim/issues
with the `biep:v3` label. Include the output of `mise run biep:v3:status`
and the relevant asset check failure log.

## See also

- `docs/agents/biiep-v3-systematic-download.md` — the canonical newcomer guide
- `docs/agents/biiep-v3-quickstart.md` — the "first 30 minutes" guide
- `docs/agents/biiep-v3-baml-client.md` — how to invoke the 6 new Extract* functions from Python
- `docs/agents/biiep-v3-storage-layout.md` — the DuckLake + Lance + MotherDuck layout
- `docs/agents/biiep-v3-cron-schedule.md` — the 4-cadence scheduling policy in detail
- `docs/agents/biiep-v3-bie-8-jurisdictions.md` — the 8-jurisdiction rollout + the 2 scanner domains
