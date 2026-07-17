# 2026-07-15-eu-multilingual-irish-english-v1

## Why

The EU institutional pipeline
([`2026-07-11-european-union-official-language-pipeline-v1`](../../specs/european-union-official-language-pipeline/spec.md))
publishes across all 24 EU official languages (including Irish `ga`
which became the 24th on 2022-01-01). The British Isles parity work
established that the British Isles Ireland + Northern Ireland data
surface is bilingual (English + Irish for Ireland; English + Irish
for Northern Ireland's Irish-medium schools).

The user explicitly said: "focusing for now on fleshing out the
british isles, european nations, european union multilingual sources
(especially focused on what is available in irish and english for
later alignment)".

This change adds:
- A canonical bilingual (English + Irish) BAML extraction class
- Per-source `language_availability` metadata documenting which EU
  institutions actually publish in Irish (limited set)
- 3 new Dagster L2 assets for monitoring + alignment
- 1 new MotherDuck Dive for coverage matrix
- 1 daily Flight for BAML backfill

## What changes

### 1. New BAML class `BilingualTextEnGa`

In `baml/european_union/_shared/eu_document.baml`:

```baml
class BilingualTextEnGa {
  en string? @description("English text")
  ga string? @description("Irish / Gaeilge text")
}

class EUExtractableBilingualDocument {
  url string
  institution EUInstitution
  language EULanguage
  celex_id string?
  title BilingualTextEnGa
  summary BilingualTextEnGa?
  publication_date string?
  source_url string
  content_hash string?
  language_availability map<string, string>
  @description("Per-language availability: 'full' | 'partial' | 'none'")
}

function ExtractEUDocumentBilingualEnGa(
  institution: EUInstitution,
  language: EULanguage,
  text: string
) -> EUExtractableBilingualDocument {
  client Claude
  prompt #"
    Extract the canonical EU document from the following text.
    When the source document is in English or Irish, populate the
    corresponding fields. When in another language, set the en/ga
    fields to null and the language_availability accordingly.

    Institution: {{ institution }}
    Language: {{ language }}
    Text: {{ text }}

    {{ ctx.output_format }}
  "#
}
```

### 2. Per-source `language_availability` metadata

Every EU institutional DLT source (EUR-Lex, EMA, ECDC, Eurydice,
Cedefop, Eurostat, Publications Office, Council, Parliament,
Commission, Europa Portal) gets a new `language_availability`
metadata field documenting actual Irish (`ga`) + English (`en`)
coverage. Per the EU institutions' published translation policies:

| Institution | English (en) | Irish (ga) |
|---|---|---|
| EUR-Lex (regulations/directives/treaties/cjeu_case_law) | full | full |
| Eurydice | full | full |
| Cedefop | full | full |
| EMA | full | full |
| ECDC | full | partial |
| Eurostat | full | full |
| Publications Office | full | full |
| Council Documents | full | full |
| Parliament Documents | full | full |
| Commission Press | full | full |
| Europa Portal | full | full |
| School Education Gateway | full | full |

### 3. Dagster L2 assets (3 new)

Under `orchestration/defs/2_materials/eu_multilingual/`:

- `english_coverage_monitor.py` — weekly audit of EU institutional
  sources' English coverage
- `irish_coverage_monitor.py` — weekly audit of EU institutional
  sources' Irish coverage (will be full per EU regulations 1/1958
  + Council Decision 2020/2172)
- `language_alignment_mapper.py` — maps EU documents to the
  British Isles (Ireland + Northern Ireland) corpus for
  cross-jurisdiction linking via the `ga`/`en` language pair

Each runs `0 5 * * *` (daily at 05:00 UTC) and emits rows to a new
`cianfhoghlaim.multilingual.eu_coverage` DuckLake table.

### 4. Dagster defs (3 L2 + 1 shared L2 config)

- `orchestration/defs/2_materials/eu_multilingual/defs.yaml`
- The 3 L2 modules above

### 5. MotherDuck Dive

`motherduck/dives/eu_multilingual_coverage.py`:
- A coverage matrix showing per institution × per language (en + ga)
  the row count of extracted documents
- Cross-joined with the British Isles Ireland + Northern Ireland
  data for the alignment workflow

### 6. MotherDuck Flight

`motherduck/flights/eu_multilingual_daily_sync_flight.py`:
- Cron `0 5 * * *` — daily BAML backfill of EU institutional
  sources into the bilingual extraction pipeline

### 7. CocoIndex v1 App (new — 1)

`cocoindex/eu_multilingual_alignment_embedding.py`:
- Bilingual (en + ga) embeddings of EU institutional documents
- LanceDB table: `cianfhoghlaim.eu.multilingual_alignment_chunks`
- Partition: `(institution, language)`
- Embedding model: BAAI/bge-m3 1024-d

### 8. Cache fixtures (12 institutional sources × 2 languages = 24 fixtures)

For each EU institutional source, add an `en` + `ga` cache fixture
under `stedding/ingest_queue/eu/<institution>/<lang>/sample.json`.

## Dependencies

```yaml
Blocked by: 2026-07-11-european-union-official-language-pipeline-v1
Blocked by (soft):
  - 2026-07-12-british-isles-parity-pipeline-v1

Affected repos: cianfhoghlaim (single-repo change)
```

## Acceptance gates

- `openspec validate 2026-07-15-eu-multilingual-irish-english-v1 --strict` passes
- `baml/european_union/_shared/eu_document.baml` has the new
  `BilingualTextEnGa` + `EUExtractableBilingualDocument` classes +
  `ExtractEUDocumentBilingualEnGa` function
- All 12 EU institutional DLT sources carry the
  `language_availability` metadata field
- 3 new Dagster L2 assets created + 1 shared L2 defs.yaml
- 24 cache fixtures (12 institutions × en + ga)
- 1 CocoIndex v1 App conforms to R1–R4
- 1 MotherDuck Dive + 1 daily Flight
- All AST-parse + YAML-parse cleanly
- `dg check yaml` passes
- `mise run lint:skills` still passes (53/53)
- Push target: `origin/pick-4-biep-v1`

## Cross-references

- [`cross-region-pipeline`](../cross-region-pipeline/spec.md) —
  the umbrella contract
- [`european-union-official-language-pipeline`](../european-union-official-language-pipeline/spec.md) —
  the EU institutional scaffold (parent)
- [`british-isles-education-pipeline`](../british-isles-education-pipeline/spec.md) —
  the bilingual reference (Irish + English)
- [`cianfhoghlaim-pipeline`](../cianfhoghlaim-pipeline/spec.md) —
  the parent pipeline
- `.agents/skills/dlt/SKILL.md` — DLT conventions
- `.agents/skills/baml/SKILL.md` — BAML schema patterns
- `.agents/skills/cocoindex/SKILL.md` — the R1–R4 conformance contract
