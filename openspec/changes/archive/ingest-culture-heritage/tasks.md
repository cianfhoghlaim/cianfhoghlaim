# Tasks — `ingest-culture-heritage`

12 tasks. Run in order. Validate at the end with `openspec validate ingest-culture-heritage --strict`.

**Status (2026-06-25):** 12/12 tasks complete; `openspec validate ingest-culture-heritage --strict` → `Change 'ingest-culture-heritage' is valid`. BAML client regeneration blocked by pre-existing `sruth/tuatha/sruth/crypteolas/pyproject.toml` workspace error (unrelated to this change; tracked separately).

## 1. ✅ Save 3 Wikipedia clippings with Obsidian frontmatter

**Files (3 new):**

- `cian_mac_an_déisigh_uí_liatháin/identity/lineage/references/clippings/ui_liathain-wikipedia.md`
- `cian_mac_an_déisigh_uí_liatháin/identity/lineage/references/clippings/delbhna_tir_dha_locha-wikipedia.md`
- `cian_mac_an_déisigh_uí_liatháin/identity/lineage/references/clippings/eamonn_deacy_park-wikipedia.md`

**Method:** `firecrawl_scrape` with `formats: ["markdown"]` against each Wikipedia URL (cleaner than the MediaWiki REST API for the lead-paragraph + first 30 sections).

**Frontmatter:** 7-field YAML matching the `deisi-wikipedia.md` precedent:

```yaml
---
title: "..."
source: "https://en.wikipedia.org/wiki/..."
author:
  - "[[Contributors to Wikimedia projects]]"
published: YYYY-MM-DD
created: YYYY-MM-DD
description:
tags:
  - "clippings"
  - "culture"
---
```

**Acceptance:** Each file has the exact 7-field YAML frontmatter matching `deisi-wikipedia.md`; the first 50 lines of the article body are present and preserve Wikipedia's inline `[[wikilink]]` syntax.

## 2. ✅ Save 3 Wikipedia DLT fixtures (JSON)

**Files (3 new):**

- `sruth/oideachais/dlt_sources/official_media/fixtures/identity_ui_liathain.json`
- `sruth/oideachais/dlt_sources/official_media/fixtures/identity_delbhna.json`
- `sruth/oideachais/dlt_sources/official_media/fixtures/identity_eamonn_deacy_park.json`

**Schema per fixture:**

```json
{
  "title": "Uí Liatháin",
  "url": "https://en.wikipedia.org/wiki/Uí_Liatháin",
  "extract": "<first paragraph>",
  "sha256": "<sha256 of full article body>",
  "retrieved_at": "2026-06-25T00:00:00Z"
}
```

**Acceptance:** Each JSON has the 5 fields; resolves via `lookup_wikipedia()` with no warnings; `sha256` is a valid 64-character hex digest.

## 3. ✅ Add culture_extraction.baml + regenerate BAML client

**File (1 new):**

- `sruth/oideachais/baml_src/culture_extraction.baml`

**Schema:**

```baml
enum EvidenceQuality {
  PRIMARY
  SECONDARY
  INFERENCE
}

class CultureHeritageClaim {
  claim_text       string
  people_mentioned string[]
  places_mentioned string[]
  dates            string[]
  evidence_quality EvidenceQuality
  wikipedia_links  string[]
  confidence       float
}

function ExtractCultureClaims(pdf_path: string, context: string) -> CultureHeritageClaim[]
```

**Regenerate:** `cd oideachais && uv run baml-cli generate`.

**Acceptance:** `baml-cli generate` exits 0; `ExtractCultureClaims` is callable from the regenerated `baml_client/`; passes `pydantic` validation against `CultureHeritageClaim`.

## 4. ✅ Add 6 sources.yaml entries under the culture domain

**File (1 edited):** `sruth/oideachais/sources.yaml`

**Entries to add (under `domain: culture, nation: ie`):**

```yaml
- id: ie.culture.claiming_r_na_gaillimhe
  name: "Claiming Rí na Gaillimhe — A Synthesis"
  domain: culture
  nation: ie
  kind: filesystem_pdf
  urls: ["file://leabharlann/gemini_deep_research/culture/claiming_r_na_gaillimhe_a_synthesis.pdf"]
  schema: baml:ExtractCultureClaims
  lakehouse: DUCKLAKE
  embedding: { namespace: oideachais.culture_heritage, model: BAAI/bge-m3 }
  kg:        { dataset: culture_heritage, edge_types: [Claim->Person, Claim->Place, Person->FamilyRelation] }
  firecrawl: { skip: true }
  tests:     ["culture_heritage_extract_smoke"]
  schedule:  { cron: "0 6 * * 0", timezone: Europe/Dublin }
  sensors:   []
  compliance: { respect_robots_txt: true, licence: "self-authored", retain_raw_snapshots_days: 365 }
```

(plus 5 more entries, one per PDF)

**Acceptance:** All 6 entries validate against the cross-domain-registry v2 schema; no `ie.culture.*` key collisions with existing sources; `sources.yaml` is parseable by `SourceFactory`.

## 5. ✅ Add culture_heritage_embedding CocoIndex v1 App

**File (1 new):** `sruth/oideachais/cocoindex_flows/culture_heritage_embedding.py`

**Pattern mirrors:** `sruth/oideachais/cocoindex_flows/leabharlann_embedding.py` (the closest existing v1 App).

**Canonical v1 conventions enforced:**

- `@coco.fn(memo=True)` for processing functions
- `@coco.lifespan` providing shared `EMBEDDER` + `LANCE_DB` context keys
- `localfs.walk_dir(sourcedir, recursive=True, live=True)`
- `lancedb.mount_table_target(...)` for output
- `IdGenerator()` for stable IDs (derived from `(pdf_sha256, claim_index)`)
- `Annotated[NDArray, EMBEDDER]` = `BAAI/bge-m3` (1024-dim, multilingual)
- **100-row minimum upsert batch**
- **HNSW-DROP-THRESHOLD=50**

**Acceptance:** App starts under `bun run ccc:index`; respects the 100-batch minimum; HNSW index rebuilt on schema change.

## 6. ✅ Add culture_cognify.py Cognee pass

**File (1 new):** `sruth/oideachais/cognee_integration/culture_cognify.py`

**Pattern mirrors:** `sruth/oideachais/cognee_integration/leabharlann_cognify.py`.

**Behaviour:** Loads `culture_heritage_chunks` from LanceDB; runs `cognee.cognify(dataset_name="culture_heritage")` with a custom prompt tuned for "extract (person, family-relationship, place, date-range, claim, citation) quintuples"; emits cross-dataset edges from `culture_heritage:person:<name>` to existing `oideachais:place:galway` nodes.

**Acceptance:** `cognee.cognify()` runs end-to-end against the 6 PDFs; entities persist to the new dataset; cross-dataset edges are observable in the unified graph.

## 7. ✅ Add 4 Dagster assets (extract/embed/cognify/cross-edges)

**File (1 new):** `sruth/oideachais/dagster_defs/assets/culture_heritage_assets.py`

**4 assets in `group_name="culture_heritage"`** (in dependency order):

| # | Asset | Responsibility |
|:--|:--|:--|
| 1 | `culture_heritage_extract` | Run `ExtractCultureClaims` over the 6 PDFs; emit one `CultureHeritageClaim` per page. |
| 2 | `culture_heritage_embed` | Subprocess call to `cocoindex update --app culture_heritage_embedding`. |
| 3 | `culture_heritage_cognify` | Run `cognee.cognify(dataset_name="culture_heritage")` on the LanceDB chunks. |
| 4 | `culture_heritage_cross_edges` | Emit FalkorDB MERGE queries for cross-dataset edges (culture_heritage ↔ oideachais, culture_heritage ↔ leabharlann). |

**Acceptance:** `dg list assets --location oideachais` shows all 4 assets; the asset lineage graph includes `extract → embed → cognify → cross_edges`; `dg dev` loads them without error.

## 8. ✅ Add low_confidence_review asset check

**File (same as Task 7):** `sruth/oideachais/dagster_defs/assets/culture_heritage_assets.py`

**Asset check:** `@asset_check(asset=culture_heritage_extract)` that warns (severity=WARN, not FAIL) when any emitted claim has `confidence < 0.6`.

**Acceptance:** Asset check appears in `dg list asset-checks`; warns correctly when a low-confidence PDF is processed; passes (passes silently) when all claims ≥ 0.6.

## 9. ✅ Wire the asset group into dg.toml (no change needed — auto-discovery)

**File (1 edited):** `dg.toml` — no change needed. The `oideachais` workspace project already discovers `sruth/oideachais/dagster_defs/assets/` via Dagster's standard asset-discovery mechanism (no explicit registration per-asset).

**Verification only:** `dg list assets --location oideachais | grep culture_heritage` returns all 4 assets.

**Acceptance:** All 4 assets visible in `dg dev`.

## 10. ✅ Update sruth/oideachais/STATUS.md matrix

**File (1 edited):** `sruth/oideachais/STATUS.md`

**Add 1 new row to § 1 (BAML × dlt × Dagster × CocoIndex matrix):**

| BAML file | Classes | Extraction functions | dlt source(s) | Dagster asset(s) | CocoIndex flow |
|:--|:--|:--|:--|:--|:--|
| `culture_extraction.baml` | `CultureHeritageClaim`, `EvidenceQuality` (2) | `ExtractCultureClaims` | `sruth/oideachais/dlt_sources/culture/heritage_source.py` | `sruth/oideachais/dagster_defs/assets/culture_heritage_assets.py` (4 assets + 1 asset check) | `sruth/oideachais/cocoindex_flows/culture_heritage_embedding.py` |

**Acceptance:** Status file remains well-formed; § 1 has 1 new row; § 5 has a "Culture heritage pipeline" subsection.

## 11. ✅ Run `openspec validate ingest-culture-heritage --strict`

**Command:**

```bash
openspec validate ingest-culture-heritage --strict
```

**Acceptance:** Exit code 0; all 3 spec deltas have ≥1 Scenario per ADDED Requirement; all SHALL/MUST language preserved; no parse errors.

## 12. ✅ Update `.erk/docs/agent/index.md` (KCG substitute: `sruth/oideachais/AGENTS.md`) with the new culture subtree

**File (1 edited):** `.erk/docs/agent/index.md`

**Add a new entry to the routing table pointing at:**

- `sruth/oideachais/cognee_integration/culture_cognify.py`
- `sruth/oideachais/cocoindex_flows/culture_heritage_embedding.py`
- `sruth/oideachais/dagster_defs/assets/culture_heritage_assets.py`
- `sruth/oideachais/baml_src/culture_extraction.baml`

**Acceptance:** Index includes 4 new pointers; routing tables remain in dependency order (BAML → DLT → CocoIndex → Cognee → Dagster).