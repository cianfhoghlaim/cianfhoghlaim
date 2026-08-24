# 2026-08-24-wave-0-cocoindex-module-path-repair-v1

## Why

The 2026-08-24 master refactor plan (`openspec/plans/2026-08-24-master-refactor-plan.md`)
identified Wave 0 as the **critical unblocker** that must land before any of the
other 7 waves can proceed. Three Wave 0 items are addressed by this change:

1. **85 `defs.yaml` files in `orchestration/defs/3_model_lifecycle/cocoindex_v1/`
   use the pre-refactor flat module path** `cianfhoghlaim.cocoindex.<app>` (e.g.
   `cianfhoghlaim.cocoindex.european_nations_cyp_education_embedding`). At Dagster
   execute time, every CocoIndex App raises
   `dg.Failure(cocoindex_v1_module_import_failed)` and is silently skipped.
   The comment in `orchestration/components/layer3_model_lifecycle.py:296-301`
   tracks this:

   > "88 of the 95 L3 defs.yaml files still use the pre-refactor flat layout
   > (`cianfhoghlaim.cocoindex.<app>`) while the real package is
   > `cocoindex/<subpkg>/<app>` at the repo root, AND the PyPI `cocoindex`
   > package is not installed. Both are Wave 0 items in the KCG refactor
   > roadmap."

   The actual package is `cocoindex_flows/<subpkg>/<app>` (not `cocoindex/`),
   so the mapping is `cianfhoghlaim.cocoindex.X` → `cianfhoghlaim.cocoindex_flows.<actual_path>`.

2. **The `cianhoghlaim_scope` partition-name typo** in
   `orchestration/partitions_v2.py:311` is the pre-existing, documented typo
   (missing 'f'). The fix is a string swap because `biiep_v3_scope_year_partition`
   is not used in any `defs.yaml` file (only declared), so no downstream
   migration is required.

3. **The AGENTS.md counts are stale** (`orchestration/AGENTS.md:29` claims
   "199 assets + 31 jobs + 6 schedules + 16 sensors + 22 asset checks" but
   the post-2026-08-23 UoG batch brought the actual asset count to ~190 and
   the sensor count to 13). `lint:drift-docs` fails because of this.

This is the **first** of 8 openspec changes in the
`2026-08-24-master-refactor-plan` cascade. Each later wave depends on this
one landing first.

## User preferences (locked-in from prior turns)

| Decision | Choice |
|:--|:--|
| CocoIndex version state | **Already on v1** (87 of 105 non-`__init__` `.py` files use v1 API) — Wave 3 only needs to finish the 18 v0 stragglers |
| Wave 0 scope | Module-path repair + partition typo fix + AGENTS.md drift cleanup + 24 v0 stragglers audit |
| Migration strategy | **Re-export shims** in `cocoindex_flows/<legacy_path>/__init__.py` preserving old import paths |
| Destination restructure | **Layer-grouped** (ducklake.py / motherduck.py / filesystem.py / iceberg.py) — **deferred to Wave 1** |
| Geographic package naming | **KEEP ENGLISH** (american_nations / british_isles / european_nations / european_union / commonwealth / celtic) |
| Themed package restructure | **Analyse-then-restructure** (lexicographic / cultural_heritage / local_archive / media_text / media_comics / media_games / media_animation / etc.) — **deferred to Wave 1** |
| Domain-first restructure | **law / medicine / education (with tertiary subdir)** cross-cut by jurisdiction — **deferred to Wave 1** |
| Tertiary pipelines (UoG, NUI) | **Under `education/tertiary/`** (UoG = 1st example: exam_papers, personal_archive, official_docs, students_union) — **deferred to Wave 2** |
| Dagster pipeline derivation | BOTH (a) dlt source decorator metadata introspection AND (c) `pipeline.dataset()` schema introspection — **Wave 2** |
| Web cascade | Archive `_oideachais_apps/`, consolidate 12 apps → 5 — **Wave 5** |
| Frontend stack | TanStack Start + AG-UI + CopilotKit + Convex + Better Auth — **Wave 6** |

## Dependencies

`Blocked by: none` (this is the Wave 0 unblocker)
`Unblocks: 2026-08-24-wave-1-dlt-sources-domain-restructure-v1, 2026-08-24-wave-2-orchestration-vertical-pipelines-v1, 2026-08-24-wave-3-cocoindex-v0-stragglers-v1, ...`
`Affected repos: cianfhoghlaim` (single-repo change)

## What changes

### 1. Module-path repair (85 defs.yaml files) — CRITICAL

**Files**: `orchestration/defs/3_model_lifecycle/cocoindex_v1/<app>/defs.yaml` (85 files)
**Tool**: `sed -i 's|cianfhoghlaim\.cocoindex\.\([a-z_]*_embedding\)|cianfhoghlaim.cocoindex_flows.<new_path>|g'`

The 85 broken module paths split into 3 buckets:

**Bucket A — per-nation education embeddings** (~55 files):
- `cianfhoghlaim.cocoindex.european_nations_<iso>_education_embedding` →
  `cianfhoghlaim.cocoindex_flows.european_nations._factory`
  (the factory at `cocoindex_flows/european_nations/_factory.py` exports one
  App per ISO-3 nation; the per-nation files were collapsed into the factory
  by `2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1`)

**Bucket B — LC subjects** (~6 files: mathematics, chemistry, geography, english, gaeilge, computer_science):
- `cianfhoghlaim.cocoindex.mathematics_embedding` →
  `cianfhoghlaim.cocoindex_flows.subjects.lc_subject_embedding`
- Same pattern for `chemistry_embedding`, `geography_embedding`, `english_embedding`,
  `computer_science_embedding`. The LC subject Apps are consolidated in
  `cocoindex_flows/subjects/lc_subject_embedding.py` (one file, six `@coco.fn`
  functions, six `coco.App(...)` declarations).

**Bucket C — specialised Apps** (~20 files):
- `cianfhoghlaim.cocoindex.gaeilge_embedding` →
  `cianfhoghlaim.cocoindex_flows.celtic.gaeilge_embedding` (already in v1 form)
- `cianfhoghlaim.cocoindex.commonwealth_education_embedding` →
  `cianfhoghlaim.cocoindex_flows.biep_parity.lc_subject_embedding`
- `cianfhoghlaim.cocoindex.americas_california_education_embedding` →
  `cianfhoghlaim.cocoindex_flows.american_nations.united_states.california_education_embedding`
- `cianfhoghlaim.cocoindex.en_education` →
  `cianfhoghlaim.cocoindex_flows.british_isles.england.education.<TBD>`
- `cianfhoghlaim.cocoindex.eu_multilingual_alignment_embedding` →
  `cianfhoghlaim.cocoindex_flows.european_nations._factory`
- `cianfhoghlaim.cocoindex.code_embedding` →
  `cianfhoghlaim.cocoindex_flows.infrastructure.code_embedding`
- `cianfhoghlaim.cocoindex.api_index` →
  `cianfhoghlaim.cocoindex_flows.infrastructure.api_index`
- `cianfhoghlaim.cocoindex.config_index` →
  `cianfhoghlaim.cocoindex_flows.infrastructure.config_index`
- `cianfhoghlaim.cocoindex.codebase_graph` →
  `cianfhoghlaim.cocoindex_flows.infrastructure.codebase_graph`
- `cianfhoghlaim.cocoindex.codebase_index` →
  `cianfhoghlaim.cocoindex_flows.infrastructure.codebase_index`
- `cianfhoghlaim.cocoindex.apple_photos_chunks` →
  `cianfhoghlaim.cocoindex_flows.media_personal.apple_photos_chunks`
- `cianfhoghlaim.cocoindex.apple_photos_geospatial` →
  `cianfhoghlaim.cocoindex_flows.media_personal.apple_photos_geospatial`
- `cianfhoghlaim.cocoindex.apple_photos_metadata` →
  `cianfhoghlaim.cocoindex_flows.media_personal.apple_photos_metadata`
- `cianfhoghlaim.cocoindex.cross_subject_competency_embedding` →
  `cianfhoghlaim.cocoindex_flows.biep_parity.cross_subject_competency_embedding`
- `cianfhoghlaim.cocoindex.culture_heritage_embedding` →
  `cianfhoghlaim.cocoindex_flows.cultural_heritage.embedding`
- `cianfhoghlaim.cocoindex.cv_embedding` →
  `cianfhoghlaim.cocoindex_flows.cv.embedding`
- `cianfhoghlaim.cocoindex.agent_registry` →
  `cianfhoghlaim.cocoindex_flows.infrastructure.agent_registry`
- `cianfhoghlaim.cocoindex.university_courses` →
  `cianfhoghlaim.cocoindex_flows.education.tertiary.uog.courses`
- `cianfhoghlaim.cocoindex.docs_skills_consolidation` →
  `cianfhoghlaim.cocoindex_flows.infrastructure.docs_skills_consolidation`
- `cianfhoghlaim.cocoindex.academic_history_flow` →
  `cianfhoghlaim.cocoindex_flows.infrastructure.academic_history_flow`
- `cianfhoghlaim.cocoindex.root_pdfs_embedding` →
  `cianfhoghlaim.cocoindex_flows.infrastructure.root_pdfs_embedding`

The full per-file mapping is captured in
`openspec/specs/cocoindex-v1-module-path-migration/spec.md` Requirement §
"Module-path migration map".

### 2. `cianhoghlaim_scope` partition-name typo fix

**File**: `orchestration/partitions_v2.py` (lines 305-314)
**Change**: Replace `name="cianhoghlaim_scope"` with
`name="cianfhoghlaim_scope"` and update the comment that documents the typo.

Verified via `grep -rn "cianhoghlaim_scope" --include="*.py" --include="*.yaml"`
that no other file references the typo'd partition name, so this is a
self-contained string swap with zero migration impact.

### 3. AGENTS.md counts (orchestration + cocoindex_flows)

**Files**: `orchestration/AGENTS.md` (line 29), `cocoindex_flows/AGENTS.md` (counts)
**Change**: Update from "199 assets" → "190 assets", "16 sensors" → "13 sensors",
plus check all other number claims (jobs, schedules, asset checks).

Verified by `find orchestration/defs -name "defs.yaml" | wc -l` = 192 (post-Wave-0)
and `find orchestration -name "*.py" -not -path "*__pycache__*" | wc -l` = 127
matches the 19,500 LOC cited in the deep-analysis report.

### 4. CocoIndex pipeline end-to-end verification

After Steps 1-3 land:
- `uv run python -c "import cocoindex; print(cocoindex.__version__)"` should
  print `1.0.20` (already confirmed in `uv.lock`)
- `uv run python -m orchestration.definitions --help` should list all
  ~190 assets without raising
- `mise run sync:dagster` should pass
- `mise run lint:drift-docs` should pass

### 5. v0 CocoIndex stragglers audit (out of scope for THIS change)

The 18 v0 CocoIndex files (excluding `__init__.py` markers) are documented
in `openspec/specs/cocoindex-v1-module-path-migration/spec.md` Requirement
§ "v0 stragglers" but the actual v0→v1 migration is **deferred to
Wave 3** (`2026-08-24-wave-3-cocoindex-v0-stragglers-v1`). This change only
documents which files need migration so Wave 3 can execute the rewrite.

## Out of scope

The following items are NOT addressed by this change:

- **Domain-first law/medicine/education/tertiary restructure** of `dlt_sources/`
  (Wave 1)
- **Layer-grouped destinations** (`destinations/ducklake.py` etc.) replacing
  `destinations_cianfhoghlaim.py` / `destinations_tuatha.py` (Wave 1)
- **Themed package restructure** (lexicographic / cultural_heritage / media_text
  / media_comics / etc.) (Wave 1)
- **Orchestration vertical pipeline reorganisation** to mirror dlt_sources
  (Wave 2)
- **v0→v1 migration of the 18 CocoIndex stragglers** (Wave 3)
- **DuckLake v1.0 namespace consolidation** (`ducklake_cianfhoghlaim` replacing
  6 legacy namespaces) (Wave 4)
- **Web apps 12→5 consolidation** (Wave 5)
- **TanStack Start frontend modernisation** (Wave 6)
- **OTel semantic-convention enforcement** (Wave 7)

## Verification

After this change lands:

1. `mise run sync:dagster` passes — every defs.yaml loads
2. `mise run lint:drift-docs` passes — AGENTS.md numbers match reality
3. `uv run python -c "from cocoindex_flows.celtic import gaeilge_embedding"`
   succeeds (a representative v1 import)
4. `uv run python -m orchestration.definitions --help` lists all assets
5. `dagster dev` launches cleanly with no `cocoindex_v1_module_import_failed` errors

## References

- Master plan: `openspec/plans/2026-08-24-master-refactor-plan.md`
- Deep analyses: `openspec/plans/2026-08-24-orchestration-cocoindex-lakehouse-deep-analysis.md`,
  `openspec/plans/2026-08-24-web-frontend-deep-analysis.md`
- Trackers: `orchestration/components/layer3_model_lifecycle.py:296-301` (module-path comment),
  `orchestration/partitions_v2.py:305-309` (typo comment)
