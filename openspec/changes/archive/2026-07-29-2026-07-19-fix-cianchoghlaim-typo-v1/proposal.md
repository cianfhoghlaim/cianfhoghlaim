## Shipped in code

All work proposed here has been delivered to the codebase since this change was opened. The remaining tasks are validation gates + the final `openspec archive` call.

## Shipped in code

All work proposed here has been delivered to the codebase since this change was opened. The remaining tasks are validation gates + the final `openspec archive` call.

# Change: 2026-07-19-fix-cianchoghlaim-typo-v1

> Note: the change-id folder name intentionally retains the typo token
> `cianchoghlaim` to make the change self-documenting in `openspec list`
> and search. The change title in this heading and below uses the
> corrected spelling for clarity.

## Why

The repo contained **~3,633 occurrences** of `cianchoghlaim` (a typo of
`cianfhoghlaim`) across 176 files. The typo was not cosmetic — it was
scattered across:

- **Source identifiers**: the Python package `name = "cianchoghlaim"` in
  `pyproject.toml` (line 2 + 3,270 force-include paths), the Dagster
  `code_location_name = "cianchoghlaim"` in `dg.toml`, and the dagger
  module directory `bonneagar/dagger/cianchoghlaim_dagger/` (with the
  PascalCase class `CianchoghlaimDagger`).
- **Runtime identifiers** (require redeploy + data migration):
  - Docker bridge network `cianchoghlaim` (used by 12 stacks)
  - External tmpfs volume `cianchoghlaim_locket_secrets`
  - Container name prefix `cianchoghlaim-oideachais-*` (6 services)
  - OpenChamber theme `cianchoghlaim-dark`
  - Postgres DB `ducklake_cianchoghlaim`
  - S3 bucket `ducklake-cianchoghlaim`
  - DuckLake schema `cianchoghlaim.education._registry`
  - Pangolin internal URLs (`http://cianchoghlaim-oideachais-*`)
- **Docstrings, comments, agent prompts**: 70+ `cocoindex/__init__.py`
  files, 7 `opencode.json` agent prompts, all `.agents/skills/*`,
  all `openspec/changes/**/proposal.md|tasks.md|spec.md` (active +
  archived), all `docs/**`, plus `mise.toml` and `clio.py`.

The source-level Python imports (`from cianfhoghlaim.cli import main`)
were already correct — the typo never broke source imports — but the
package metadata, runtime identifiers, and a lot of documentation
carried it.

The fix was mandatory because:

1. The package name `name = "cianchoghlaim"` in `pyproject.toml`
   produced a wheel installed under the wrong name (the
   `_editable_impl_cianchoghlaim.pth` filename leak).
2. The dagger module's `main_object = "cianchoghlaim_dagger:..."`
   referenced a non-existent class name in the new wheel layout.
3. New docker resources named with the typo would propagate the
   mistake to every freshly-deployed stack.

## What Changes

A single omnibus that renames every `cianchoghlaim` → `cianfhoghlaim`
across the full repo (case-insensitive, case-preserving), with explicit
handling for:

1. **Package metadata**: `pyproject.toml` `[project].name` + 3,270
   `force-include` mappings.
2. **Source identifiers**: `dg.toml` `code_location_name`, `cli.py`
   subcommand list, `clio.py` docstring.
3. **Dagger module**: rename directory
   `bonneagar/dagger/cianchoghlaim_dagger/` →
   `bonneagar/dagger/cianfhoghlaim_dagger/`, rename class
   `CianchoghlaimDagger` → `CianfhoghlaimDagger`, update
   `pyproject.toml` (name + `main_object` + `packages`), update
   `dagger.json` (name), update `templates/*.env.template` rendered-by
   comment, update `README.md`.
4. **CocoIndex package markers**: rewrite docstring in all 70+
   `cocoindex/**/__init__.py` files
   (`"""cianchoghlaim.cocoindex.X — …"""` →
   `"""cianfhoghlaim.cocoindex.X — …"""`).
5. **Agent prompts**: rewrite all 7 `opencode.json` subagent prompts
   that contain the typo in their v7-flattening update sections.
6. **Skills**: rewrite all `.agents/skills/**/SKILL.md` and
   `.agents/skills_backup/**/*.md` occurrences.
7. **OpenSpec**: rewrite active + archived `proposal.md`, `tasks.md`,
   and `spec.md` files under `openspec/changes/**` and
   `openspec/specs/**`.
8. **Docs**: rewrite all `docs/stacks/*.md`, `docs/lakehouse/*.md`,
   `docs/p3-*.md`, and the affected `web/apps/croilar-web/README.md`.
9. **Root files**: `mise.toml` (comment block), `pyproject.toml`
   (the force-include lines), `.github/workflows/skill-refs-check.yaml`
   (regex pattern).
10. **Runtime identifiers** (T3, with migration):
    - All Docker Compose `container_name:`, `networks:`, `volumes:`
      references under `bonneagar/stacks/**/compose*.yaml`,
      `bonneagar/stacks/oideachais/{compose,pangolin,sidecar}.yaml`,
      `bonneagar/GOLD_STANDARD.md`.
    - Komodo procedures under `bonneagar/komodo/procedures/*.toml`
      and `bonneagar/komodo/stacks/*.toml` (theme + volume refs).
    - Scripts under `scripts/setup_local_ducklake_registry.py`
      (PG_DB, S3_BUCKET), `scripts/verify_ducklake_population.py`,
      `scripts/export_cohorts_to_lance.py`, `scripts/dev.sh`.
    - DLT sources `dlt_sources/__init__.py` +
      `common/destinations_*.py` (S3 bucket env) +
      `british_isles/_cross/registry_api.py` +
      `british_isles/_cross/registry_loader.py` (DuckLake schema).

After the implementation phase: a `rg -i cianchoghlaim` against the
repo (excluding gitignored caches, `.venv/`, `node_modules/`, etc.)
returns **0 matches**.

## Runtime migration (T3 — operator runbook)

For each runtime identifier, the canonical mapping applied is:

| From | To |
|:--|:--|
| Docker network `cianchoghlaim` | `cianfhoghlaim` |
| Volume `cianchoghlaim_locket_secrets` | `cianfhoghlaim_locket_secrets` |
| Container prefix `cianchoghlaim-*` | `cianfhoghlaim-*` |
| OpenChamber theme `cianchoghlaim-dark` | `cianfhoghlaim-dark` |
| Postgres DB `ducklake_cianchoghlaim` | `ducklake_cianfhoghlaim` |
| S3 bucket `ducklake-cianchoghlaim` | `ducklake-cianfhoghlaim` |
| DuckLake schema `cianchoghlaim.education._registry` | `cianfhoghlaim.education._registry` |
| DLT dataset `cianchoghlaim_education_<j>_subjects` | `cianfhoghlaim_education_<j>_subjects` |

The operator migration is a one-shot runbook executed **after** the
file edits land in `main`:

1. **Stop every stack** that touches the old network/volume/db:
   ```bash
   for s in oideachais openchamber openclaw hermes langfuse \
            wave2/letta wave2/siyuan wave2/mealie wave2/outline \
            wave2/khoj wave2/immich wave2/kavita; do
     docker compose -f bonneagar/stacks/$s/compose.yaml down
   done
   ```
2. **Drop the old external network and volume** (orphaned):
   ```bash
   docker network rm cianchoghlaim 2>/dev/null || true
   docker volume rm cianchoghlaim_locket_secrets 2>/dev/null || true
   docker volume create cianfhoghlaim_locket_secrets --driver local \
     --opt type=tmpfs --opt device=tmpfs --opt o=size=64m,uid=65532,gid=65532
   docker network create cianfhoghlaim
   ```
3. **Rename the Postgres DB** (preserve data):
   ```sql
   ALTER DATABASE ducklake_cianchoghlaim RENAME TO ducklake_cianfhoghlaim;
   UPDATE ducklake_metadata.ducklake_schema
      SET schema_name = REPLACE(schema_name, 'cianchoghlaim.', 'cianfhoghlaim.')
    WHERE schema_name LIKE 'cianchoghlaim.%';
   ```
4. **Rename the S3 bucket** (Garage S3 — use `mc mirror`):
   ```bash
   mise run s3:mirror ducklake-cianchoghlaim ducklake-cianfhoghlaim
   mise run s3:rm-bucket ducklake-cianchoghlaim
   ```
   Update Infisical `dev-baile`: `DUCKLAKE_BUCKET=ducklake-cianfhoghlaim`.
5. **Restart every stack** so they join the new network + mount the new
   volume + connect to the renamed DB + write to the new bucket.

## Implementation summary

- 3,633 occurrences rewritten across 176 files
- 1 directory renamed: `bonneagar/dagger/cianchoghlaim_dagger/` →
  `bonneagar/dagger/cianfhoghlaim_dagger/` (via `git mv`)
- 1 PascalCase class renamed: `CianchoghlaimDagger` →
  `CianfhoghlaimDagger` (in `__init__.py` docstring, `__all__`, and
  class definition)

All replacements were case-preserving — `cianchoghlaim`,
`Cianchoghlaim`, `CianchoghlaimDagger`, `cianchoghlaim_dagger`,
`cianchoghlaim-dark`, `cianchoghlaim_locket_secrets` all became their
correctly-spelled equivalents.

## Dependencies

Blocked by: none
Blocked by (soft): `2026-07-09-v6-drift-remediation-and-repo-boundary-lockdown-v1`
  (the `preflight:arm-oci` script is a soft dep if a redeploy is needed)
Affected repos: cianfhoghlaim (this repo)
