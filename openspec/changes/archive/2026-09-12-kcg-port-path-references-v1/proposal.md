# Change: KCG Path References Port — fix hardcoded host paths

## Why

The 2026-09-12 audit for the sibling change
`2026-09-12-kcg-legacy-folder-retirement-v1` revealed that
`/Users/cianmacandeisigh/dev/kings_college_galway/` (the legacy
working-tree name of this repo) is not just a stale directory — **12+
live code paths in `cianfhoghlaim/` itself still hardcode the legacy
host path**. Deleting KCG without first fixing these references would
cause a hard runtime regression, not a quiet drift.

This change is the port that fixes those hardcoded paths.

## What's at risk (audit findings, 2026-09-12)

Live code (would fail with `FileNotFoundError` /
`cd: /Users/...: No such file or directory` after KCG deletion):

| File | Line(s) | What breaks |
|---|---|---|
| `bonneagar/iac/commands/bootstrap-control-plane.ts` | 87, 139 | `execSync("cd /Users/.../kings_college_galway/bonneagar/stacks/...")` — the `iac:bootstrap` command fails |
| `dlt_sources/filesystem/pdf_download_source.py` | 69 | `samples_dir = "/Users/.../kings_college_galway/cianfhoghlaim"` — DLT filesystem source fails |
| `dlt_sources/jobs/government_circulars_job.py` | 42 | `samples_dir = "/Users/.../kings_college_galway/stedding/site_scrape_samples/oide.ie"` — gov circulars job fails |
| `dlt_sources/british_isles/ireland/education/gov_ie_circulars.py` | 96 | Same — DLT source fails |
| `dlt_sources/british_isles/ireland/education/curriculumonline_syllabi.py` | 255 | `Path("/Users/.../kings_college_galway/stedding/ingest_queue")` — fails |
| `dlt_sources/british_isles/ireland/education/curriculum.py` | 92 | `Path("/Users/.../kings_college_galway/stedding/ingest_queue")` — fails |
| `dlt_sources/british_isles/england/education/gcse/england_gcse_sources.py` | 140 | `samples_dir = "/Users/.../kings_college_galway/stedding/site_scrape_samples"` — fails |
| `dlt_sources/british_isles/england/education/a_level/england_a_level_sources.py` | 139 | Same — fails |
| `orchestration/defs/2_materials/lc_extraction/lc_subjects.py` | 103, 252, 264 | Dagster LC extraction assets fail (site samples + .venv/python3) |
| `web/apps/cianfhoghlaim-leaving-cert/apps/web/src/lib/lineage-registry.ts` | 41, 49, 57, 65, 73, 85, 93, 101, 109, 119, 127, 135, 147, 155, 163, 171, 179, 187, 197, 205, 213, 221, 229, 237, 249, 257, 265, 273, 281, 289, 299, 307, 315, 323, 331, 339 + more | Leaving Cert lineage-registry pdf_path fields point to non-existent paths |
| `cocoindex_flows/corpus/unified_embedding.py` | 122 | DuckDB lance path hardcoded to KCG |
| `web/apps/cianfhoghlaim-leaving-cert/apps/web/packages/mcp/design-system-server.py` | 19 | Docstring references KCG `.agents/skills/` path |

Documentation-only (does not break runtime, just lies about paths):

| File | Notes |
|---|---|
| `agents/tuatha/{DEVELOPMENT,README}.md` | `cd /Users/.../kings_college_galway` instruction |
| `bonneagar/iac/docs/locket.md` | same |
| `bonneagar/dagger/README.md` | same |
| `bonneagar/stacks/openchamber/README.md` | same |
| `bonneagar/stacks/cianfhoghlaim/README.md` | same |
| `bonneagar/stacks/control-plane/README.md` | same |
| `bonneagar/stacks/HEALTH_REPORT.md` | same |
| `bonneagar/stacks/wave2/{letta,siyuan,mealie,outline,khoj,immich,kavita}/sidecar.yaml` | sidecar workdir references |
| `bonneagar/stacks/unstract/sidecar.yaml` | same |
| `bonneagar/stacks/lakehouse/sidecar.yaml` | same |
| `docs/pangolin-komodo/PANGOLIN_KOMODO_SETUP.md` | doc |
| `docs/PHASE_0.3_DEPLOY_RUNBOOK.md` | doc |
| `docs/dagster/group-name-underscore-migration.md` | doc |
| `docs/agents/dlthub-run-vs-serve.md` | doc |
| `docs/deploy-runbooks/bunchloch-bootstrap.md` | doc |
| `docs/deploy-runbooks/bunchloch-infisical-data-plane-2026-07.md` | doc |
| `web/apps/_oideachais_apps/README.md` | doc |
| `web/apps/croilar-web/README.md` | doc |
| `bonneagar/setup-iac-env.sh` | shell script (may be live) |
| `scripts/*` | most are one-off dev scripts |

This change ports the **12 live-code files** that would break
runtime. Documentation-only updates are NOT in scope for this change
(they will be addressed in a separate follow-up; the
retirement change handles the canonical specs).

## What changes

For each of the 12 live-code files:

1. Replace every literal
   `/Users/cianmacandeisigh/dev/kings_college_galway`
   with
   `/Users/cianmacandeisigh/dev/cianfhoghlaim`
   (the canonical post-v7 location, which has the same relative paths
   below the root — e.g. both `/kings_college_galway/bonneagar` and
   `/cianfhoghlaim/bonneagar` exist with identical content).
2. Verify the replacement with a per-file `rg` check that no stray
   `kings_college_galway` remains in that file.
3. For Python files that reference `samples_dir`, also add a fallback
   `os.environ.get("BIEP_SAMPLES_DIR", ...)` indirection so the
   paths are env-overridable in CI/dev (the pre-v7 fallback pattern
   per `AGENTS.md §2. Respect the Ingestion Cache`).

## Why now

- The sibling retirement change
  (`2026-09-12-kcg-legacy-folder-retirement-v1`) archives spec deltas
  but does NOT migrate the live code paths.
- Deleting KCG without this port first is exactly the failure mode
  catalogued in MEMORY 1 (`kcg-runtime-inert-layers`): a hidden
  runtime regression that only surfaces when an agent actually invokes
  the broken code path.

## Risk

- **Low per file**: a simple literal path swap, with no logic change.
- **Medium in aggregate**: 12 files, all in critical paths (DLT sources,
  Dagster assets, iac bootstrap, leaving-cert lineage). Mitigated by
  per-file grep verification.
- The `samples_dir` fallback indirection is additive (env var wins) —
  no existing behavior changes.

## Dependencies

`Blocked by: none`
`Blocked by (soft): 2026-09-12-kcg-legacy-folder-retirement-v1` (this
change must land before the KCG directory is deleted)
`Affected repos: cianfhoghlaim` (single-repo change)

## Out of scope

- Renaming the forgejo git remote
  (`forgejo.cianfhoghlaim.ie/cliste/kings_college_galway`) —
  requires forgejo admin action.
- Updating `iac/config.ts:43` (`CONFIG.gitRepo` default) — same reason.
- Documentation-only references (~30 files) — separate follow-up
  change.
- The 5 inert-layer defects catalogued in MEMORY 1 — separate openspec
  change.