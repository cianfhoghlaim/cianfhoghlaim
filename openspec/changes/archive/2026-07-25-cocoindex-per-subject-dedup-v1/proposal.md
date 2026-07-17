# 2026-07-25-cocoindex-per-subject-dedup-v1

## Why

The 8 CocoIndex v1 Apps at `cocoindex/subjects/<subject>_embedding.py`
(1,581 LOC) are 90% identical scaffolding per the R1–R4 v1 conformance
contract. Each re-declares the same `coco.App` + `lancedb.mount_table_target(LANCE_DB, ...)`
+ `BAAI/bge-m3` embedder pattern with only the subject name changing.

The audit confirmed:
- 7 of the 8 Apps (chemistry, mathematics, english, geography, history,
  computer_science, applied_mathematics) have the same R1–R4 contract
  structure
- Only `cross_subject_competency_embedding.py` has genuinely different
  semantics (cross-subject competency vector search, not single-subject)

Collapsing the 7 near-clones into 1 parameterised `lc_subject_embedding.py`
+ 1 YAML config:
- Preserves the exact asset key shape `oideachais.lc.<subject>.<level>_<lang>`
- Reduces 1,581 LOC to ~530 LOC (parameterised flow + YAML config)
- Dagster `dg list` will show 2 code-location flows instead of 8

## What changes

### 1. Delete 7 per-subject CocoIndex Apps

- DELETE `cocoindex/subjects/chemistry_embedding.py`
- DELETE `cocoindex/subjects/applied_mathematics_embedding.py`
- DELETE `cocoindex/subjects/computer_science_embedding.py`
- DELETE `cocoindex/subjects/english_embedding.py`
- DELETE `cocoindex/subjects/geography_embedding.py`
- DELETE `cocoindex/subjects/history_embedding.py`
- DELETE `cocoindex/subjects/mathematics_embedding.py`

(All 7 use the same R1–R4 pattern + the same `bge-m3` embedder + the same
LanceDB table name shape.)

### 2. Create the parameterised flow

- NEW `cocoindex/subjects/lc_subject_embedding.py` (~250 LOC) — declares
  a single `coco.App(coco.AppConfig(name="lc_subject_embedding"))` with
  a `@coco.function` decorator that takes `subject: str` and produces
  the `oideachais.lc.<subject>.<level>_<lang>` LanceDB table.

### 3. Create the YAML config

- NEW `cocoindex/subjects/lc_subject_config.yaml` (~30 LOC) — 6 subject
  rows driving the Dagster asset materialisations:

  ```yaml
  subjects:
    - subject: mathematics
      dagster_asset_key: lc_mathematics_embedding
    - subject: chemistry
      dagster_asset_key: lc_chemistry_embedding
    - subject: geography
      dagster_asset_key: lc_geography_embedding
    - subject: english
      dagster_asset_key: lc_english_embedding
    - subject: gaeilge
      dagster_asset_key: lc_gaeilge_embedding
    - subject: computer_science
      dagster_asset_key: lc_computer_science_embedding
  ```

### 4. Keep `cross_subject_competency_embedding.py`

- KEEP `cocoindex/subjects/cross_subject_competency_embedding.py`
  (genuinely different semantics — cross-subject competency vector search
  is not a per-subject pattern)

### 5. Spec delta

`openspec/specs/meaisinfhoghlaim-platform/spec.md` — add a
`### Requirement: 8 per-subject CocoIndex Apps → 1 parameterised`
requirement that mandates the 2-app surface (parameterised + cross-subject).

## Dependencies

```yaml
Blocked by: 2026-07-25-nb-utils-ibis-first-v1
Blocked by (soft): 2026-07-25-flatten-notebooks-v1
Affected repos: cianfhoghlaim (single-repo change)
```

## Acceptance gates

- `openspec validate 2026-07-25-cocoindex-per-subject-dedup-v1 --strict` passes
- 7 deprecated `<subject>_embedding.py` files are deleted
- 1 new `lc_subject_embedding.py` + 1 YAML config exist
- `mise run cocoindex:v1-conformance` passes (R1–R4 contract)
- Dagster asset keys `oideachais.lc.<subject>.<level>_<lang>` are preserved
  (zero data migration required)
- `dg list code-locations` shows 2 CocoIndex v1 apps:
  `lc_subject_embedding` + `cross_subject_competency_embedding`
- `mise run lint:skills` — must remain 53/53
- Push target: `origin/main`

## Cross-references

- [`meaisinfhoghlaim-platform`](../../specs/meaisinfhoghlaim-platform/spec.md) —
  the parent platform spec that this change conforms to
- [`british-isles-education-pipeline`](../../specs/british-isles-education-pipeline/spec.md) —
  the BIEP v1 LC spec (the per-subject pipeline is the canonical consumer)
- [`oideachais-cocoindex-v1-migration`](../../specs/oideachais-cocoindex-v1-migration/spec.md) —
  the R1–R4 v1 conformance contract the new flow must obey
- `openspec/changes/2026-07-25-nb-utils-ibis-first-v1/` — the prerequisite
  `_shared/db.py` helper
- `.agents/skills/cocoindex/SKILL.md` — the R1–R4 conformance contract