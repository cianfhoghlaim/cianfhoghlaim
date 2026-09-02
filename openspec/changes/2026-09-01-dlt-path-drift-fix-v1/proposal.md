# Change: DLT Path Drift Fix v1 — Update all imports to the new Wave 1 path [COMPLETE]

> **Status:** AUTHORED + IMPLEMENTED.
>
> **Step 1** of the Cianfhoghlaim-Nua v6 era plan
> (post-Phases 0-9). Fixes the 137-file DLT path drift between the
> Wave 1 NEW canonical path
> (`dlt_sources/education/<jurisdiction>/british_isles/...`) and
> the Wave 0 OLD path (`dlt_sources/british_isles/<jurisdiction>/...`)
> that all imports still referenced.

## Why

Per the `2026-08-24-wave-1-dlt-sources-domain-restructure-v1`
change, the DLT source tree was restructured from a jurisdiction-
clustered layout to a domain-clustered layout. The actual files
moved to `dlt_sources/education/<jurisdiction>/british_isles/...` but
all 137 Python imports across the codebase still referenced the
empty old path `dlt_sources/british_isles/<jurisdiction>/...`.

The Wave 1 tasks T2.1 (migration script) + T6.1 (destinations
consolidation) are still unchecked, and the per-jurisdiction
`__init__.py` re-exports at the old path are missing. This change
ships the bulk import update + the openspec change so the
rest of the system can import from the new path without runtime
errors.

## What was shipped

### §1 — Bulk update all 137 imports (1 action)

- **§1.1** Bulk find-replace across `dlt_sources/`,
  `orchestration/`, `agents/`, `tests/`, and `meaisinfhoghlaim/`:
  - `dlt_sources.british_isles.ireland.education.*` →
    `dlt_sources.education.ireland.british_isles.education.*`
  - `dlt_sources.british_isles.england.education.*` →
    `dlt_sources.education.england.british_isles.education.*`
  - `dlt_sources.british_isles.scotland.education.*` →
    `dlt_sources.education.scotland.british_isles.education.*`
  - `dlt_sources.british_isles.wales.education.*` →
    `dlt_sources.education.wales.british_isles.education.*`
  - `dlt_sources.british_isles.northern_ireland.education.*` →
    `dlt_sources.education.northern_ireland.british_isles.education.*`
  - `dlt_sources.british_isles.isle_of_man.education.*` →
    `dlt_sources.education.isle_of_man.british_isles.education.*`
  - `dlt_sources.british_isles.jersey.education.*` →
    `dlt_sources.education.jersey.british_isles.education.*`
  - `dlt_sources.british_isles.guernsey.education.*` →
    `dlt_sources.education.guernsey.british_isles.education.*`
  - `dlt_sources.british_isles.crown_dependencies.education.*` →
    `dlt_sources.education.crown_dependencies.british_isles.education.*`
  - `dlt_sources.british_isles.ireland.education.university.*` →
    `dlt_sources.education.ireland.british_isles.university.*`
    (the `education.` between `british_isles` and `university` is
    removed because the university subpath is at the same level as
    `education/`, not below it)

### §2 — Spec delta to `dev-tooling-surfaces` (1 file)

- **§2.1** `openspec/changes/2026-09-01-dlt-path-drift-fix-v1/specs/dev-tooling-surfaces/spec.md`
  — adds 1 new Requirement:
    - "All Python imports MUST reference the Wave 1 DLT path
      (`dlt_sources.education.<jurisdiction>.british_isles.*`)"

## Impact

- **Audience:** every Cianfhoghlaim developer / agent who imports
  from `dlt_sources.british_isles.*`.
- **Scope:** 137 files modified.
- **LOC delta:** ~±2 per file (no net addition).
- **Risk:** MEDIUM — the bulk find-replace is mechanical but the
  university subpath had to be corrected (the `education.` was
  removed between `british_isles` and `university` to match the
  actual file layout).
- **Reversibility:** full — `git revert` restores the old imports.

## Dependencies

`Blocked by (hard):` none.

`Blocked by (soft):` none.

`Enables:`

- The 8 Ireland NCCA-adjacent + Physics new subjects (Step 2)
  can import the existing per-subject DLT sources cleanly.
- The 7 new jurisdiction extensions (Step 4-8) can add their
  per-subject DLT sources at the new path.
- The future sister-repo lifts (Step 9) can reference the new
  path without drift.

`Affected repos:` `cianfhoghlaim` (this repo only).

## Out of scope

- Wholesale rewrite of the Wave 1 restructure (T2.1 + T3.x + T6.1) —
  those tasks remain unchecked per the
  `2026-08-24-wave-1-dlt-sources-domain-restructure-v1` change.
- The university + tertiary + law + american_nations DLT sources
  that use `dlt_sources.british_isles._legislation_helper` and
  `dlt_sources.british_isles._cross` — these are legitimate uses
  of the `british_isles/` path component, not the same drift.

## Quality gates (ALL PASSED)

```bash
uv run openspec validate 2026-09-01-dlt-path-drift-fix-v1 --strict  ✅
grep -rln 'dlt_sources\.british_isles\.\(ireland\|england\|scotland\|wales\|northern_ireland\|isle_of_man\|jersey\|guernsey\|crown_dependencies\)\.education' --include='*.py'  # 0 results ✅
```

---

*Last updated by build subagent at 2026-09-01.*