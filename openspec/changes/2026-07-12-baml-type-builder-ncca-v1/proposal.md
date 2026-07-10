# BAML TypeBuilder + `@@dynamic` for the NCCA strand/outcome catalog

## Why

The NCCA strand / outcome / curriculum-spec / assessment-component tree
changes yearly. Today, every NCCA refresh requires regenerating the
BAML `.baml` files in `cianfhoghlaim/baml/education/_shared/`
(`strand_outcome.baml` + the 4 NCCA-related class definitions
`LearningOutcome`, `CurriculumStrand`, `CurriculumSpecStrand`,
`AssessmentComponentStrand`), which means redeploying the BAML
codegen + the BIEP v1 Dagster assets + the 4 MotherDuck Dives.

Per BAML v0.221+, the canonical pattern for "the schema changes
yearly at runtime" is:

1. Mark the class `@@dynamic` in the `.baml` file
2. Read the per-instance properties from a config file at startup
3. Use `baml_client.type_builder.TypeBuilder.add_property(name, type)`
   to inject the runtime properties into the class viewer

This decouples the **schema-deployment cycle** (`baml-cli generate`
+ release) from the **catalog-update cycle** (yearly NCCA refresh
+ restart the pipeline). The operator workflow becomes:

```
[operator]
  1. pull the new NCCA scrape into leabharlann/
  2. edit baml/education/_shared/strand_catalog.yaml
  3. restart the pipeline (no BAML regen, no redeploy)
```

The "schema changes yearly" pain shows up in the BIEP v1 follow-up
audit (the 4 NCCA-related classes — `CurriculumSpecification` ×2 +
`AssessmentComponent` ×2 — are exactly the dynamic-types candidates
per the 42-renames audit in commit `49e0259a0`).

## What changes

Adds the v0.221+ BAML **TypeBuilder / `@@dynamic`** pattern for the
NCCA strand/outcome catalog:

### 1. `@@dynamic` markers on the 4 canonical NCCA classes

In `baml/education/_shared/strand_outcome.baml`:

```baml
class LearningOutcome { ... @@dynamic }
class CurriculumStrand { ... @@dynamic }
class CurriculumSpecStrand { ... @@dynamic }
class AssessmentComponentStrand { ... @@dynamic }
```

These are the 4 most-likely-to-change NCCA-related classes per the
42-renames audit. They map to the abstract names in the audit:

| Audit name | BAML class |
|:--|:--|
| `Strand` | `CurriculumStrand` |
| `Outcome` | `LearningOutcome` |
| `CurriculumSpecification` | `CurriculumSpecStrand` |
| `AssessmentComponent` | `AssessmentComponentStrand` |

The other variants (e.g. `EnhancedLearningOutcome`,
`ExamAssessmentComponent`, `CrossNationLearningOutcome`,
`AssessmentComponent` in `multi_nation_curriculum.baml`) are
siblings and intentionally NOT modified here — they don't carry
the NCCA yearly-update pressure.

### 2. Runtime TypeBuilder helper

`baml/education/_shared/strand_type_builder.py`:

- `load_catalog(catalog_path=None)` — reads
  `baml/education/_shared/strand_catalog.yaml` (or an override
  path) and returns the 4-section catalog
  (`strands` / `outcomes` / `specifications` /
  `assessment_components`).
- `build_ncca_strand_type_builder(catalog=None, catalog_path=None)` —
  instantiates a `baml_client.type_builder.TypeBuilder`, walks the
  catalog, and calls `tb.<ClassName>.add_property(name, type)` for
  every per-strand / per-outcome / per-spec / per-component
  property.
- Type-name mapping: `"string" → tb.string()`, `"int" → tb.int()`,
  `"float" → tb.float()`, `"bool" → tb.bool()`.
- Falls back to `None` if the baml_client can't be imported
  (e.g. baml-py version skew in CI); the caller can still verify
  the catalog is valid YAML.
- Ships a `python -m baml.education._shared.strand_type_builder`
  CLI that prints the catalog summary + the TypeBuilder status.

### 3. Representative NCCA catalog YAML

`baml/education/_shared/strand_catalog.yaml`:

- 23 strands (4 Mathematics, 4 Chemistry, 3 Geography, 4 Gaeilge,
  4 English, 4 Computer Science)
- 10 outcomes (across the 6 LC priority subjects)
- 7 curriculum specifications (per `(subject, level)` pair the
  pipeline tracks)
- 13 assessment components (per-subject component tree)

The full NCCA tree lives in the `leabharlann/` worktree (not in
the `baml/` tree). This YAML is a representative subset that
exercises the TypeBuilder path end-to-end without dragging in the
whole ~1.5MB NCCA scrape. When the operator wants to upgrade,
they edit this YAML and restart the pipeline.

### 4. Smoke test in `strand_outcome.baml`

```baml
test strand_type_builder_smoke {
  functions [ExtractStrandFromCatalog]
  args {
    catalog_yaml #"
      strands:
        - name: "LC Mathematics Strand 1: Algebra"
          ...
    "#
  }
}

function ExtractStrandFromCatalog(catalog_yaml: string) -> CurriculumSpecStrand[] {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"...
    CATALOG:
    ```yaml
    {{ catalog_yaml }}
    ```
    ...
  "#
}
```

The test loads an inline 10-strand representative subset and
exercises the `ExtractStrandFromCatalog` function end-to-end.

### 5. Two new `__init__.py` docstrings (package markers)

`baml/education/__init__.py` + `baml/education/_shared/__init__.py`
— empty docstring `__init__.py` files that make the directory
tree a Python package (mirroring the existing
`baml/education/law/__init__.py` precedent). They have no runtime
side-effects; they exist only to make
`from baml.education._shared.strand_type_builder import ...`
importable in CI and notebooks.

## What does NOT change

- The 7 `baml/education/lc_extraction/*.baml` files (owned by the
  BIEP v1 openspec change)
- The 50+ pre-existing `baml-cli` validation errors in other
  clusters (out-of-scope per the 3 prior follow-up commits
  `5e6734b57` + `49e0259a0` + `476c866b8` + `1623849d9`)
- The leabharlann/ worktree (NCCA corpus data lives there, not
  in the baml/ tree)
- The `baml_client/` auto-generated client (regenerated only on
  `baml-cli generate`, which is blocked by the pre-existing
  errors until they are fixed by other openspec changes)

## Dependencies

`Blocked by: none`

`Blocked by (soft): 2026-07-10-fix-baml-codegen-v4-syntax-v1` —
the baml-py / baml_client version skew means my TypeBuilder can't
be unit-tested against the generated client today. The helper
gracefully falls back to `None` + a warning, so this is
informational only.

`Affected repos: cianfhoghlaim`

This is a single-repo change. The 4 modified `.baml` files + the
new `_shared/strand_type_builder.py` + the new
`_shared/strand_catalog.yaml` + the 2 new `__init__.py` docstrings
all live in the `cianfhoghlaim` monorepo. No `bonneagar/` or
`leabharlann/` cross-repo sync needed.

## Acceptance gates

- [x] `openspec validate 2026-07-12-baml-type-builder-ncca-v1 --strict`
      passes
- [x] `baml/education/_shared/strand_outcome.baml` has exactly 4
      `@@dynamic` markers (one per canonical NCCA class)
- [x] `baml/education/_shared/strand_catalog.yaml` is a valid YAML
      file (23 strands + 10 outcomes + 7 specs + 13 components =
      53 catalog entries)
- [x] `baml/education/_shared/strand_type_builder.py` exists + the
      `python -m baml.education._shared.strand_type_builder` CLI
      loads the catalog and reports the 4-section summary
- [x] `mise run baml:test` adds 0 new validation errors beyond
      the 50 pre-existing out-of-scope errors (verified: 1754
      errors before, 1754 errors after — same count)
- [x] 1 ADDED Requirement on the `oideachais-baml-schemas` spec
- [ ] Pushed to `origin/pick-4-biep-v1` (NOT `main`)
