# `dlt_sources/` migrations — Phase 0.2 (ISO-3 → snake_case)

Per Phase 0.2 of the openspec change
[`2026-08-24-dlt-sources-to-multi-repo-scaffold-v1`](../../../../openspec/changes/2026-08-24-dlt-sources-to-multi-repo-scaffold-v1/proposal.md)
and the v2 plan
[`openspec/plans/2026-08-24-dlt-deep-analysis-v2.md`](../../../../openspec/plans/2026-08-24-dlt-deep-analysis-v2.md).

The 873 broken legacy imports in `dlt_sources/` are bulk-fixed by 6
deterministic `git mv` + `sed` one-liners (one per wave), grouped into 6
shell scripts and a single dependency-ordered runner.

## Inventory

| # | Script | Wave | LEGACY_ALIASES.md lines | Pair count |
|---|---|---|---|---|
| 1 | `migration_commonwealth_nigeria_states.sh` | Nigeria states (deepest path) | `L115-L115` | 37 |
| 2 | `migration_commonwealth_canada_provinces.sh` | Canada provinces (rewrite before `can → canada`) | `L109-L109` | 13 |
| 3 | `migration_commonwealth.sh` | Commonwealth top-level | `L103-L103` | 6 |
| 4 | `migration_european_nations.sh` | European nations | `L97-L97` | 40 |
| 5 | `migration_british_isles.sh` | British Isles collapse | `L121-L127` | 7 |
| 6 | `migration_americas.sh` | Americas → American Nations | `L133-L133` | 4 |
| 7 | `apply_all.sh` | Dependency-ordered runner (1 → 6) | n/a | 107 (sum) |

Plus `_generator.py` (deterministic generator) and `README.md` (this file).

## Pair counts

The pair counts in the table above are sourced verbatim from
`dlt_sources/LEGACY_ALIASES.md`. The LEGACY_ALIASES.md is the source of
truth; if a future change adds or removes an ISO-3 code from that file,
re-running `_generator.py` (or `python3 _generator.py --check` for a
diff-only check) regenerates the 7 scripts in lockstep.

## Usage

```bash
# --- from the repo root ----------------------------------------------------
cd /Users/cianmacandeisigh/dev/cianfhoghlaim

# 1. dry-run a single wave (does NOT write, does NOT touch git):
bash dlt_sources/.migrations/2026-08-24/migration_european_nations.sh --dry-run

# 2. apply a single wave (writes; uses `git mv` + `sed -i ''`):
bash dlt_sources/.migrations/2026-08-24/migration_european_nations.sh

# 3. dry-run ALL 6 waves in dependency order:
bash dlt_sources/.migrations/2026-08-24/apply_all.sh --dry-run

# 4. apply ALL 6 waves in dependency order (the canonical path):
bash dlt_sources/.migrations/2026-08-24/apply_all.sh
```

After step 4, the next action is `mise run dlt:smoke-all` to verify
that the 873 originally-failing imports are now resolvable. The grep
counts printed before/after each pair land in
`stedding/sync-reports/legacy-import-fix-{date}.md` per tasks.md task
2.3.

## Regenerating the scripts

```bash
cd /Users/cianmacandeisigh/dev/cianfhoghlaim/dlt_sources/.migrations/2026-08-24/

python3 _generator.py            # write all 7 files
python3 _generator.py --check    # exit 0 if up-to-date, 1 if a regeneration would change bytes
```

`_generator.py` is **deterministic**: same input bytes
(`dlt_sources/LEGACY_ALIASES.md`) → same output bytes. No timestamps, no
random IDs, pair ordering comes verbatim from LEGACY_ALIASES.md. Suitable
for committing to git; every PR that touches LEGACY_ALIASES.md will
generate a corresponding diff in the 7 scripts.

## Dependency order (sed-migration safety)

`apply_all.sh` runs the 6 migrations in the order below. The rule is
**most-specific path first**, so that a broader rewrite later does not
clobber a more specific one.

1. `migration_commonwealth_nigeria_states.sh`
   -- `commonwealth.nigeria.states.nga_<3>` is the deepest of the 6 path
   patterns.
2. `migration_commonwealth_canada_provinces.sh`
   -- `commonwealth.can.<2>` must be rewritten to
   `commonwealth.canada.provinces.<prov>` BEFORE the broader
   `commonwealth.can → commonwealth.canada` rename fires (otherwise the
   province rewrite would land after the parent collapse and miss).
3. `migration_commonwealth.sh`
   -- canonical rename of all 6 jurisdictions
   (aus/can/ind/nga/nzl/zaf). The `nga → nigeria` rewrite happens here,
   not in step 1; the step 1 sed pattern ends in `\b` which won't
   collide.
4. `migration_european_nations.sh`
   -- 40 European ISO-3 codes. Independent of the commonwealth subtree.
5. `migration_british_isles.sh`
   -- 7 BI ISO-3 codes (en/ni/sct/wls/iom/jey/ggy). Independent.
6. `migration_americas.sh`
   -- `americas → american_nations` collapse (4 nations).

## Constraints (per the v2 plan + this openspec change)

- **macOS only** (per the v2 plan §A): the scripts use `sed -i ''` (BSD
  in-place). On GNU/Linux the empty argument is interpreted as the
  backup-file suffix, creating a backup next to every file. Do not run
  on Linux.
- **`#!/usr/bin/env bash`** (per the v2 plan §A): not `#!/bin/bash`.
- **Repo-root cwd**: the scripts assume `cwd = repo root` (so `git mv`
  and `git grep` resolve correctly). `apply_all.sh` does not enforce
  this; out-of-tree runs fail silently.
- **Idempotent**: each migration script is safe to re-run. The `sed`
  pattern no longer matches after a successful rewrite, so re-runs are
  no-ops on the import side. The `git mv` is fail-safe (errors if the
  destination already exists, halting cleanly on partial re-runs).

## What the scripts do NOT touch

- No files under `dlt_sources/european_nations/`,
  `dlt_sources/commonwealth/`, `dlt_sources/british_isles/`, or
  `dlt_sources/american_nations/` are written or modified by this
  generator. Only the scripts under
  `dlt_sources/.migrations/2026-08-24/` are emitted.
- The legacy imports already fixed in the Wave 1 bulk-rename (per
  `dlt_sources/LEGACY_ALIASES.md` §"Wave 1") are NOT touched. The
  domain-first `law/`, `medicine/`, `education/` splits are part of
  Wave 1 and out of scope for Phase 0.2.

## Files

```
dlt_sources/.migrations/
├── .gitignore                                   # ignores the __pycache__ from _generator.py
└── 2026-08-24/
    ├── README.md                                # this file
    ├── _generator.py                            # deterministic generator
    ├── migration_americas.sh                    # 4 pairs (bra, mex, us, ven)
    ├── migration_british_isles.sh               # 7 pairs (en, ni, sct, wls, iom, jey, ggy)
    ├── migration_commonwealth.sh                # 6 pairs (aus, can, ind, nga, nzl, zaf)
    ├── migration_commonwealth_canada_provinces.sh  # 13 pairs (ab, bc, mb, nb, nl, ns, nt, nu, on, pe, qc, sk, yt)
    ├── migration_commonwealth_nigeria_states.sh    # 37 pairs (nga_abi, nga_ada, ..., nga_zam)
    ├── migration_european_nations.sh            # 40 pairs (alb, aut, ..., xkx)
    └── apply_all.sh                             # dependency-ordered runner
```

## Cross-references

- [`openspec/changes/2026-08-24-dlt-sources-to-multi-repo-scaffold-v1/proposal.md`](../../../../openspec/changes/2026-08-24-dlt-sources-to-multi-repo-scaffold-v1/proposal.md)
- [`openspec/changes/2026-08-24-dlt-sources-to-multi-repo-scaffold-v1/tasks.md`](../../../../openspec/changes/2026-08-24-dlt-sources-to-multi-repo-scaffold-v1/tasks.md) — Phase 0.2 tasks 2.1–2.5
- [`openspec/plans/2026-08-24-dlt-deep-analysis-v2.md`](../../../../openspec/plans/2026-08-24-dlt-deep-analysis-v2.md) — the v2 plan §C Phase 0
- [`dlt_sources/LEGACY_ALIASES.md`](../../../LEGACY_ALIASES.md) — the rename map (single source of truth)
- [`dlt_sources/AGENTS.md`](../../../AGENTS.md) — the canonical dlt_sources/ entry point