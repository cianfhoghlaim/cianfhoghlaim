# datasets-cleanup — Privacy, Dead Code, and Drift Removal

## Why

The `oideachais/datasets/` directory (3.0 MB, 12 top-level entries) is a
stale, hand-curated scratch directory of sample exam papers, planning
notes, and per-year download statistics that pre-dates the lakehouse
migration to DuckLake + Garage S3. Three problems:

1. **Privacy leak.** `datasets/emily_rachel_2022_2026_gaeilge_ard.pdf`
   (2.3 MB) contains a real student's name. It is byte-identical to
   `datasets/gaeilge.pdf` (same MD5: `ae8296859bb60846dccdb4588cfcac97`).
   Neither file is referenced by any Python module anywhere in the repo.
2. **Dead code.** No Python file in the repo imports from
   `oideachais.datasets` (verified by `grep`). The directory is pure
   scratch from before the dlt + Dagster migration.
3. **Documentation drift.** `datasets/README.md` is a 4-line stub that
   references a non-existent `.skills/` directory. `datasets/stack.md`
   and `datasets/commands.md` are personal scratch notes.
   `datasets/secrets_management_plan.md` is a 13 KB planning document
   for the predecessor project `bonneagar` that describes a
   1Password+SOPS+Komodo secrets workflow which has since been
   superseded by the Infisical + Locket + mise three-way contract
   documented in the root `AGENTS.md`.

The canonical home for Celtic sample data already exists at
`oideachais/samplaí/` (with `gaeilge/irish_samples.yaml`, `cymraeg/`,
`brezhoneg/`, `gaidhlig/`, `gaelg/`, `kernowek/`,
`cognates.yaml`). The 7 Celtic-language buckets and the YAML schema
format are documented in `oideachais/samplaí/README.md`.

## What

1. **Delete the privacy-sensitive file immediately.**
   `datasets/emily_rachel_2022_2026_gaeilge_ard.pdf` and its
   byte-identical twin `datasets/gaeilge.pdf` (same MD5).
2. **Delete the entire `oideachais/datasets/` directory.** All 12
   top-level entries and their sub-trees (`ardteist_leaving_certification_v0.5/`,
   `downloaded_stats/2014..2024/`, `leaving_certificate/`,
   `uk/{dfe,gcse_alevels,gis,ons,raw,ucas}/`, plus 7 stale planning
   files). The canonical home for any useful sample data is already
   `oideachais/samplaí/`.
3. **Migrate the secrets-management-plan content into the root
   `AGENTS.md` "Secrets Management" section** as a 2-paragraph summary
   pointing readers at the canonical Infisical + Locket + mise flow
   (which is already documented at root `AGENTS.md:32-58`). The
   `bonneagar`-specific Komodo details are deleted (the project no
   longer exists under that name).
4. **Add `oideachais/datasets/` to the root `.gitignore`** so any
   future re-creation of the directory is ignored by default.

## Impact

### Affected files
- **Deleted:** `oideachais/datasets/` (entire tree, ~3 MB, 12 top-level entries)
- **Modified:** root `AGENTS.md` (add a "Secrets migration note" paragraph)
- **Modified:** root `.gitignore` (add `oideachais/datasets/`)

### Affected specs
- MODIFIED `oideachais-pipeline` — the rule that the canonical
  sample-data location is `oideachais/samplaí/`, not
  `oideachais/datasets/`. The new rule explicitly forbids private
  data (PDFs with real names) being checked into the quadrant.

### Backward compatibility
- Zero code references to `oideachais.datasets` exist (verified
  by `grep -r "oideachais\.datasets" --include="*.py" --include="*.md"`).
- The `.gitignore` change is forward-only (new entries are ignored).
- No runtime path or import is affected.

## Non-Goals

- No new sample data is added. `oideachais/samplaí/` already covers
  all 7 Celtic languages and 6 corpora.
- No Git history rewrite. The deleted PDFs remain in the git
  history (un-removable without a `git filter-branch` rewrite, which
  is intentionally out of scope). The 2.3 MB privacy leak is
  mitigated by file removal, not by history rewrite.
- No migration of any `datasets/` content. The directory is
  declared stale wholesale — every entry is either sample data
  already in `samplaí/`, scratch notes, or a pre-DuckLake cache
  whose purpose has been served.

## Risk Assessment

- **Risk: someone misses a hidden reference.** Mitigation:
  `grep -r "oideachais\.datasets" --include="*.py"` returns 0 hits
  before deletion.
- **Risk: privacy leak via Git history.** Mitigation: the file is
  removed from HEAD; a follow-up issue should be filed to consider
  `git filter-repo` for thorough removal if required by policy.
- **Risk: someone wanted to keep a maths sample paper.** Mitigation:
  `oideachais/samplaí/` is the canonical location for any
  educational sample; new sample data goes there.

## Validation

1. `grep -r "oideachais\.datasets" --include="*.py"` returns 0 hits
2. `ls oideachais/datasets/` returns "No such file or directory"
3. `git status` shows only the deletion + AGENTS.md + .gitignore
4. `openspec validate datasets-cleanup --strict` passes
5. `mise turbo test` (or equivalent) passes
