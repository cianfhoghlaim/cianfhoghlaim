# Cross-repo sync — academic-history pipeline

This change is **single-repo** from a build standpoint (the
`cianfhoghlaim` repo), but it reads the personal archive stored in the
sibling `leabharlann` repo.

## Commit plan

1. **`cianfhoghlaim` repo** (primary)
   - Branch: `2026-07-11-uog-math-statistics-academic-history-v1`
   - Push target: `origin/cianfhoghlaim`
   - Commit order: FIRST

2. **`leabharlann` repo** (read-only consumer)
   - No commits. The academic-history pipeline reads
     `leabharlann/ollscoil_na_gaillimhe/{mata,past}/` via the
     `AUTHOR_ARCHIVE_UOG_PATH` env var (default in this repo).
   - No push required.

3. **`bonneagar` repo**
   - No commits. The new Dagster assets register via the canonical
     `CelticMaterialsComponent` / `CelticModelLifecycleComponent`
     factory; no stack changes.

## Order of operations

Single-repo change. The change can be archived after:

1. `openspec validate 2026-07-11-uog-math-statistics-academic-history-v1 --strict` passes
2. `baml-cli check` + `baml-cli test` pass
3. `dg check yaml` passes
4. `mise run lint` passes
5. All new marimo notebooks render in headless mode

## Read-only contract for `leabharlann`

The academic-history pipeline SHALL:

- Read files only via `scan_directory` / `localfs.walk_dir`
- Write only to `oideachais.education.ie.uog_math_coursework` (DuckLake)
  and the `oideachais_academic_history` LanceDB table
- Never modify, append, or delete anything under `leabharlann/`
- Never commit personal archive content to `cianfhoghlaim`