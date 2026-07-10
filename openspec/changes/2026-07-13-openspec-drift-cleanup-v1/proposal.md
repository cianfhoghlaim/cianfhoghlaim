# Openspec drift cleanup v1

## Why

The `openspec/specs/*.md` files contain **200+ drift references**
inherited from the pre-v4 monorepo layout (`sruth/<quadrant>/...`):

- **67 `sruth.<quadrant>.*` references** across 5 specs
  (canonical-positive + negative-test + historical contexts)
- **142 bare `oideachais.*` references** across the 5 same specs
  (a mix of legitimate DB/CLI/quadrant-namespace shorthand + stale
  subpath renames)

This drift was supposed to be cleaned up by the
`2026-07-08-five-tangent-modernization` change but was not. The
parent drift change
(`2026-07-09-v6-drift-remediation-and-repo-boundary-lockdown-v1`)
is at 0/52 tasks — too broad to land in one cycle.

This change lands a **focused SUBSTANTIAL subset** of the v6
drift remediation's work — just the openspec spec drift. The
wider skill drift (`.agents/skills/`), infra drift
(`bonneagar/`), and the pre-existing validation issues in
`oideachais-pipeline` + `meaisinfhoghlaim-platform` remain in
their parent changes.

## What changes

### 1. `sruth.<quadrant>.X` → `<quadrant>.X` rename (61 refs renamed, 6 KEEP)

| Old | New | Count | Note |
|:--|:--|--:|:--|
| `sruth.oideachais.X` | `oideachais.X` | ~50 | canonical-positive refs renamed; negative-test `NOT import from sruth.X` refs preserved |
| `sruth.meaisinfhoghlaim.X` | `meaisinfhoghlaim.X` | ~13 | canonical-positive refs renamed; phantom-duplicate negative-test refs preserved |
| `sruth.croilar.X` | `croilar.X` | ~10 | croilar data-engineering refs renamed |
| `sruth.tuatha.X` | `tuatha.X` | 0 | (no `sruth.tuatha` refs existed in openspec specs) |
| `sruth.oideachas` (typo) | (preserved) | 4 | KEEP — typo test scenarios for `sruth.oideachas` per `meaisinfhoghlaim-platform` spec line 258 |
| `sruth.oideachais` (bare import, no dot) | (preserved) | 1 | KEEP — historical packaging-fix context in `croilar-data-engineering` spec line 182 |
| `from sruth.*` (broad regex) | (preserved) | 1 | KEEP — broad-pattern regex check in `oideachais-pipeline` spec line 1533 |

Net: 67 → 6 sruth.* refs (91% reduction). The remaining 6 are
historical/negative-test references that should NOT be renamed.

### 2. `oideachais.dlt_sources.X` → `oideachais.dlt.X` rename (7 refs)

Per the v4 layout, `dlt_sources/` was renamed to `dlt/` and
reorganised into `dlt/{british_isles,language,filesystem,...}/`.

### 3. `oideachais.dagster_defs.X` → `oideachais.orchestration.defs.X` rename (9 refs)

Per the v4 layout, `dagster_defs/` was renamed to
`orchestration/defs/` (a top-level `orchestration/` directory was
introduced to host all Dagster concerns: definitions + sensors +
components + asset groups).

### 4. `oideachais.dagster_assets` → `oideachais.orchestration.defs.assets` rename (1 ref)

Same rationale as (3); `dagster_assets` lives under
`orchestration/defs/assets/` post-v4.

### 5. Spec-text consistency cleanup (1 ref)

`oideachais-pipeline/spec.md:1535` originally listed both
`sruth.oideachais.*` and bare `oideachais.*` as forbidden
namespaces. After the v4 rename, the two collapsed into a single
`oideachais.*` listing (duplicate). The line was rewritten to
preserve the original semantic distinction (the legacy
`sruth.<quadrant>.*` namespaces were already removed by the v4
consolidation; only `sruth.shared.*` + `sruth.browser` + bare
`oideachais.*` remain forbidden).

## What does NOT change

- **142 bare `oideachais.*` refs** — the bare-`oideachais.*` namespace is the **legitimate post-v4 quadrant-namespace shorthand** used throughout the openspec text to refer to Python modules under `cianfhoghlaim/oideachais/<X>/`. Per the spec text convention (line 1533: "the system SHALL have zero `from sruth.*` or `from oideachais.*` imports"), the **Python imports** use `from cianfhoghlaim.X import Y`, but the **spec text** uses `oideachais.X` as a logical quadrant shorthand. We do NOT rename these.
- **Negative-test refs** (e.g. `NOT import from sruth.X`, `sruth.X (the deleted duplicate)`, `ModuleNotFoundError: No module named 'sruth.X'`) — preserved verbatim. These scenarios test for stale `sruth.X` patterns in the codebase; renaming them would break the test logic.
- **Historical refs** (e.g. `formerly sruth.X`, `e9e0fc7d2 packaging fix`, `8484a6353`) — preserved verbatim.
- **Pre-existing validation errors** in `oideachais-pipeline` (1 Requirement outside main section) + `meaisinfhoghlaim-platform` (3 Requirements outside main section) — these are pre-existing on HEAD `54c21dd52` and are tracked separately.
- **The 54 `sruth/` refs in `.agents/skills/`** — a separate drift change (`2026-07-09-v6-drift-remediation-and-repo-boundary-lockdown-v1` task #8).
- **The 100+ `sruth/` refs in `bonneagar/`** — a separate drift change (same parent change, task #9).
- **The 50+ archived openspec changes under `openspec/changes/archive/*`** — point-in-time artifacts, not modified.

## Affected specs (5)

| Spec | sruth refs renamed | bare-oideachais refs renamed | Net effect |
|:--|--:|--:|:--|
| `oideachais-pipeline` | ~16 | ~18 | canonical-positive `sruth.X` refs renamed; `dagster_defs` → `orchestration.defs`; `dlt_sources` → `dlt` |
| `croilar-data-engineering` | 10 | 0 | canonical-positive `sruth.croilar.X` refs renamed |
| `meaisinfhoghlaim-platform` | 17 | 3 | canonical-positive `sruth.X` refs renamed; `dagster_defs` → `orchestration`; negative-test refs preserved |
| `indexing-and-cognition` | 2 | 0 | cocoindex CLI invocation + agent inventory ref renamed |
| `oideachais-leabharlann` | 0 | 0 | (no renames needed — only historical "formerly `sruth.X`" refs which were preserved) |

## Acceptance gates

- [x] `openspec validate 2026-07-13-openspec-drift-cleanup-v1 --strict` passes
- [x] `sruth.*` count in `openspec/specs/*.md` reduced from 67 to 6 (91% reduction)
- [x] `oideachais.dlt_sources` + `oideachais.dagster_defs` + `oideachais.dagster_assets` stale-subpath refs reduced from 17 to 0
- [x] 5 MODIFIED spec deltas are well-formed
- [x] Pushed to `origin/pick-4-biep-v1` (NOT `main`)

## Dependencies

`Blocked by: none` (no upstream blockers)

`Blocked by (soft): 2026-07-09-v6-drift-remediation-and-repo-boundary-lockdown-v1` (parent drift change; this change is a focused subset)

`Affected repos: cianfhoghlaim` (the only repo touched by this change)

## Deferred work

1. **Pre-existing validation errors in `oideachais-pipeline` (1)** + **`meaisinfhoghlaim-platform` (3)** — Requirements outside the main `## Requirements` section. Tracked separately.
2. **`.agents/skills/` drift** (54 `sruth/` refs) — change `2026-07-09-v6-drift-remediation-and-repo-boundary-lockdown-v1` task #8.
3. **`bonneagar/` drift** (100+ `sruth/` refs) — change `2026-07-09-v6-drift-remediation-and-repo-boundary-lockdown-v1` task #9.
4. **Negative-test `sruth.X` refs** (5 instances) — preserved as-is. The scenarios are semantically valid and renaming them would defeat their purpose.
5. **Historical `sruth.X` refs** (1 instance) — preserved as-is per the "point-in-time artifacts" convention.
6. **The 142 bare `oideachais.*` refs in non-renameable contexts** (DB schemas, CLI invocations, agent paths) — these are the legitimate post-v4 quadrant-namespace shorthand.