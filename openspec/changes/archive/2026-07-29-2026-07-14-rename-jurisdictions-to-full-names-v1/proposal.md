# 2026-07-14-rename-jurisdictions-to-full-names-v1

## Why

The British Isles parity + EU + Commonwealth + Americas + Nigeria
scaffolds use short ISO codes everywhere (DE for Germany, AUT for
Austria, ng_los for Lagos State, ng_kan for Kano State, etc.).
This is correct for **identifiers** (file paths, source_id strings,
partition values, table names), but the **display strings** (BAML
class + function names, Python class names, docstrings, MotherDuck
Dive descriptions, Dagster metadata, CocoIndex v1 descriptions)
should use full country + state names for human readability.

This change renames every display string to the full official name
while preserving every short ID. It does NOT touch:

- file paths
- module names (`.py` filenames)
- variable / function / class *internal* names
- `source_id` strings
- asset keys
- Dagster partition values (`country: ["deu"]`)
- DuckLake table names (`cianfhoghlaim.<...>.<iso3>...`)
- cache directory names
- BAML parameter names (`nation: string`)

## What gets renamed

### BAML files (`baml/<region>/<iso3>/{education,law,medicine}.baml`)

For each country / state:

```baml
// Before
class DEUSubjectCurriculum { ... }
function ExtractDEUSubjectCurriculum(
  nation: string,
  language: string,
  text: string
) -> DEUSubjectCurriculum { ... }

// After
class GermanySubjectCurriculum { ... }
function ExtractGermanySubjectCurriculum(
  nation: string,
  language: string,
  text: string
) -> GermanySubjectCurriculum { ... }
```

The `nation` parameter name stays. The class + function names get the
full name. The docstrings + prompt bodies mention the full country name
("German curriculum document", not "DE curriculum document").

### DLT source files (`dlt/<region>/<iso3>/...`)

```python
# Before
class DEUEducationSource(NationSource):
    """DLT source for the Federal Ministry of Education."""

# After
class GermanyEducationSource(NationSource):
    """DLT source for the Federal Ministry of Education of Germany."""
```

### Dagster defs.yaml

```yaml
# Before
metadata:
  openspec_change: 2026-07-13-eu-nations-full-depth-expansion-v1

# After
metadata:
  openspec_change: 2026-07-13-eu-nations-full-depth-expansion-v1
  country_name: "Federal Republic of Germany"
  official_languages: ["de"]
```

The `country: ["deu"]` partition value stays. A new
`country_name` + `official_languages` metadata field is added.

### MotherDuck Dive descriptions

```python
# Before
DIVE_DESCRIPTION = "Per-subject curriculum coverage matrix for the DE BIEP parity layer."

# After
DIVE_DESCRIPTION = "Per-subject curriculum coverage matrix for the Germany BIEP parity layer."
```

The Dive name (file + MotherDuck identifier) stays short
(`deu_curriculum_dive`).

### CocoIndex v1 App class names + descriptions

```python
# Before
@dataclass
class DEUEducationChunk:
    """A chunk for the DE education pipeline."""

# After
@dataclass
class GermanyEducationChunk:
    """A chunk for the Germany education pipeline."""
```

The `TABLE_NAME` stays `cianfhoghlaim.lc.european_nations.deu.education_chunks`.

## Sub-state convention

- **Nigeria states**: `LagosStateSubjectCurriculum`, `KanoStateSubjectCurriculum`,
  `FederalCapitalTerritorySubjectCurriculum` (or `AbujaFederalCapitalTerritory`).
- **US states**: `CaliforniaSubjectCurriculum`, `TexasSubjectCurriculum`
  (no "State" suffix — "California" alone is unambiguous).
- **Canadian provinces**: `QuebecSubjectCurriculum`, `OntarioSubjectCurriculum`
  (no "Province" suffix — same convention).
- **Australian states**: `NewSouthWalesSubjectCurriculum`,
  `VictoriaSubjectCurriculum` (CamelCase for multi-word names).
- **Indian states**: `MaharashtraSubjectCurriculum`, `TamilNaduSubjectCurriculum`.

## Scope

| Region | Subagent | Countries / states | Approx file count |
|---|---|---|---:|
| EU nations | #1 | 34 new + 6 pilot (40 total) | ~1,320 |
| Canada | #2 | 13 provinces + 3 territories + Quebec deep | ~470 |
| Nigeria | #3 | 36 states + FCT | ~740 |
| Americas | #4 | 5 US states + BRA + MEX + VEN | ~260 |
| Other Commonwealth | #5 | 5 AU + 5 NZ + 4 SA + 5 IN | ~510 |
| BIEP (light touch) | bundled into #1 | 8 nations | (covered by #1) |
| **Total** | | | **~3,300** files touched |

## Dependencies

```yaml
Blocked by: none
Blocked by (soft):
  - 2026-07-11-global-region-source-contract-v1
  - 2026-07-13-eu-nations-full-depth-expansion-v1

Affected repos: cianfhoghlaim (single-repo change)
```

## Acceptance gates

- `openspec validate 2026-07-14-rename-jurisdictions-to-full-names-v1 --strict` passes
- All BAML class + function names use full country / state names
- All Python class names use full country / state names
- All docstrings mention full country / state names (not ISO codes)
- All Dagster defs.yaml files carry the new `country_name` + `official_languages` metadata
- All MotherDuck Dive descriptions use full country names
- All CocoIndex v1 App descriptions use full country names
- **No file paths, module names, source_id strings, partition values, table names, cache directory names, BAML parameter names were renamed**
- `git grep "DE " dlt/european_nations/` returns 0 short-code-in-comment hits (every short ID must be wrapped in display strings only)
- `git grep "nga_los" cianfhoghlaim/` still returns the existing matches (file paths preserved)
- All existing 5 commits still build + validate
- `dg check yaml` passes
- `mise run lint:skills` still passes (53/53)
- Push target: `origin/pick-4-biep-v1`

## Cross-references

- [`cross-region-pipeline`](../../specs/cross-region-pipeline/spec.md) —
  the umbrella contract
- [`british-isles-education-pipeline`](../british-isles-education-pipeline/spec.md) —
  the BIEP spec (light touch)
- [`cianfhoghlaim-pipeline`](../cianfhoghlaim-pipeline/spec.md) —
  the parent pipeline
- `openspec/changes/2026-07-13-eu-nations-full-depth-expansion-v1/` —
  the change this rename complements
- `.agents/skills/dlt/SKILL.md` — DLT conventions
- `.agents/skills/baml/SKILL.md` — BAML schema patterns
