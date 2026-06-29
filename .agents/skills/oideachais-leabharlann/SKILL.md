---
name: oideachais-leabharlann
description: The KCG leabharlann (personal archive) pipeline pattern in `sruth/oideachais/`. Covers the 4 dlt sources (books, zotero, takeout_v1, uog_coursework), the 3 v1 CocoIndex Apps (leabharlann_books_embedding, leabharlann_zotero_embedding, leabharlann_takeout_embedding), the 7 Dagster assets in `sruth/oideachais/dagster_defs/assets/leabharlann_assets.py`, the 1 directory-watch sensor, the 3 cognify passes (leabharlann_cognify), the 3 cross-archive edge rules (leabharlann_cross_archive), and the canonical home for the leabharlann subtree at `leabharlann/`. Use when adding a new corpus, wiring a v1 CocoIndex App, registering a sensor, running a cognify pass, populating the cross-archive graph, or implementing the BAML extraction for Zotero papers.
---

# Oideachais Leabharlann

## Purpose

The `sruth/oideachais/` quadrant houses the **leabharlann** (Irish for
"library") pipeline — the personal-archive ingestion + embedding
+ cognify + cross-archive edge-rule system that powers the
KCG knowledge graph. This skill captures the 4-source + 3-App
+ 7-asset + 1-sensor + 3-cognify + 3-edge pattern that every
leabharlann corpus follows.

## When to use this skill

Use when you need to:

- "Add a new leabharlann corpus"
- "Wire a v1 CocoIndex App for a new corpus"
- "Register a directory-watch sensor for a new corpus"
- "Run a cognify pass on a new corpus"
- "Populate the cross-archive graph from a new corpus"
- "Implement the BAML extraction for Zotero papers"

## The 4 dlt sources (the ingestion surface)

| Source | Path | Purpose |
|:--|:--|:--|
| `books` | `sruth/oideachais/dlt_sources/author_archive/books_source.py` | PDFs + DOCX + EPUB + Markdown from `leabharlann/gaeilge/` and `leabharlann/aigne/` |
| `zotero` | `sruth/oideachais/dlt_sources/author_archive/zotero_source.py` | Zotero-exported PDFs with full text + metadata |
| `takeout_v1` | `sruth/oideachais/dlt_sources/author_archive/takeout_source.py` | Google Takeout filesystem (auto-discovered at `stedding/Takeout/`) |
| `uog_coursework` | `sruth/oideachais/dlt_sources/author_archive/uog_coursework_source.py` | University of Galway coursework PDFs |

The 4 dlt sources are registered in
`sruth/oideachais/dagster_defs/assets/leabharlann_assets.py` and are
materialised by the `leabharlann_full_stack_demo` asset group
(the canonical end-to-end pipeline).

## The 3 v1 CocoIndex Apps (the embedding surface)

| App | Class | Output table | Query helper |
|:--|:--|:--|:--|
| `leabharlann_books_embedding` | `LeabharlannBooksApp` | `leabharlann_books` | `search_leabharlann_books(query, limit=10)` |
| `leabharlann_zotero_embedding` | `LeabharlannZoteroApp` | `leabharlann_zotero` | `search_leabharlann_zotero(query, limit=10)` |
| `leabharlann_takeout_embedding` | `LeabharlannTakeoutApp` | `leabharlann_takeout` | `search_leabharlann_takeout(query, limit=10)` |

The 3 Apps live at `sruth/oideachais/cocoindex_flows/leabharlann_embedding.py`
(the canonical v1 home). Each App is a `coco.App` instance with
`@coco.lifespan` + `@coco.fn` decorators (per the canonical v1
pattern in `sruth/oideachais/cocoindex_flows/codebase_indexing.py`).

## The 7 Dagster assets (the orchestration surface)

| Asset | Group | Materialises |
|:--|:--|:--|
| `leabharlann_books` | `leabharlann_ingestion` | The books dlt source → DuckLake → LanceDB |
| `leabharlann_zotero` | `leabharlann_ingestion` | The zotero dlt source → DuckLake → LanceDB |
| `leabharlann_takeout` | `leabharlann_ingestion` | The takeout dlt source → DuckLake → LanceDB |
| `leabharlann_books_chunks` | `leabharlann_ingestion` | The 3 v1 CocoIndex Apps (leabharlann_books_embedding) → LanceDB |
| `leabharlann_zotero_chunks` | `leabharlann_ingestion` | The 3 v1 CocoIndex Apps (leabharlann_zotero_embedding) → LanceDB |
| `leabharlann_takeout_chunks` | `leabharlann_ingestion` | The 3 v1 CocoIndex Apps (leabharlann_takeout_embedding) → LanceDB |
| `leabharlann_full_stack_demo` | `leabharlann_ingestion` | The end-to-end pipeline (all 6 above + the cognify passes) |

The 7 assets are registered in
`sruth/oideachais/dagster_defs/assets/leabharlann_assets.py` (the
canonical home for the asset group).

## The 1 directory-watch sensor

`sruth/oideachais/dagster_defs/sensors/leabharlann_sensor.py:LeabharlannDirectorySensor`
monitors the `leabharlann/gaeilge/` + `leabharlann/aigne/` +
`stedding/Takeout/` directories for new files. When a new file
appears, the sensor materialises the relevant asset. The sensor
runs on a 60s polling interval (per the canonical Dagster sensor
pattern).

## The 3 cognify passes (the knowledge-graph surface)

| Pass | Cognee dataset | Purpose |
|:--|:--|:--|
| `leabharlann_books_cognify` | `leabharlann_books` | Cognifies the books into the Cognee knowledge graph |
| `leabharlann_zotero_cognify` | `leabharlann_zotero` | Cognifies the Zotero papers (uses the BAML `ZoteroPaper` schema for the metadata) |
| `leabharlann_takeout_cognify` | `leabharlann_takeout` | Cognifies the Google Takeout into the knowledge graph |

The 3 cognify passes are at
`sruth/oideachais/cognee_integration/leabharlann_cognify.py` (the
canonical home for the cognify adapters).

## The 3 cross-archive edge rules (the cross-corpus surface)

| Rule | Description |
|:--|:--|
| `GeminiReport-CITES-ZoteroPaper` | A `author_archive_gemini_report` cites a `leabharlann_zotero_paper` (the citation is detected by the arxiv_id match) |
| `UoGArtifact-TEACHES-ZoteroPaper` | A `uog_coursework_artifact` teaches a `leabharlann_zotero_paper` (the match is detected by title fuzzy) |
| `TakeoutDoc-CITES-GeminiReport` | A `leabharlann_takeout_doc` cites a `author_archive_gemini_report` (the match is detected by URL substring) |

The 3 edge rules are at
`sruth/oideachais/cognify_rules/leabharlann_cross_archive.py` (the
canonical home for the edge rules).

## The canonical `leabharlann/` subtree

```
leabharlann/
├── gaeilge/         # Irish-language books (the 5 NCCA themes)
│   ├── teanga/      # Language + grammar books
│   ├── litriocht/   # Literature + poetry books
│   ├── stairiaiocht/ # History + mythology books
│   ├── eolaiocht/   # Science + nature books
│   └── cultur/      # Culture + folklore books
├── aigne/           # English-language books (the 5 CEFR levels)
│   ├── a1/
│   ├── a2/
│   ├── b1/
│   ├── b2/
│   └── c1/
├── zotero/          # Zotero-exported PDFs (auto-watched)
└── uog/             # University of Galway coursework PDFs
```

The 4 dlt sources auto-discover files in these directories.

## Worked example: add a new corpus (e.g. `leabharlann/cineáltas/`)

1. Create the corpus directory at `leabharlann/cineáltas/`.

2. Add the dlt source at
   `sruth/oideachais/dlt_sources/author_archive/cinealtas_source.py`:

   ```python
   @dlt.resource(name="cinealtas_chunks", write_disposition="merge")
   def cinealtas_chunks():
       for path in Path("leabharlann/cineáltas/").rglob("*.pdf"):
           yield {"file_path": str(path), "text": extract_text(path), "corpus": "cinealtas"}
   ```

3. Add the v1 CocoIndex App at
   `sruth/oideachais/cocoindex_flows/leabharlann_embedding.py:LeabharlannCinealtasApp`
   (or a new file `sruth/oideachais/cocoindex_flows/cinealtas_embedding.py`).

4. Add the Dagster asset at
   `sruth/oideachais/dagster_defs/assets/leabharlann_assets.py:leabharlann_cinealtas`.

5. Update the sensor at
   `sruth/oideachais/dagster_defs/sensors/leabharlann_sensor.py` to also
   watch `leabharlann/cineáltas/`.

6. Add the cognify pass at
   `sruth/oideachais/cognee_integration/leabharlann_cognify.py:leabharlann_cinealtas_cognify`.

7. Add the cross-archive edge rules at
   `sruth/oideachais/cognify_rules/leabharlann_cross_archive.py:LeabharlannCinealtasCrossArchive`.

8. Update the BAML extraction schemas at
   `sruth/oideachais/baml_src/leabharlann_extraction.baml`.

## Common failure modes

| Symptom | Cause | Fix |
|:--|:--|:--|
| `leabharlann_full_stack_demo` is hanging | The 4 dlt sources are blocking on each other | Run the 4 dlt sources in parallel via `@dlt.resource(parallel=True)` |
| The LanceDB table is empty | The v1 CocoIndex App never materialised | Run `mise run locket:exec -- uv run oideachais cocoindex update oideachais.cocoindex_flows.leabharlann_embedding:LeabharlannBooksApp` |
| The cognify pass finds no entities | The Cognee API key is wrong | Check the `cognee.cianfhoghlaim.ie:8000` API key in the vault |
| The cross-archive edge rule finds no matches | The arxiv_id format is wrong | Add a `arxiv_id_normaliser` to the rule |
| The directory-watch sensor doesn't fire | The sensor is in `default_status=stopped` | Set the sensor to `default_status=running` in `definitions.py` |

## Cross-references

- `.agents/skills/cocoindex/SKILL.md` — the v1 CocoIndex patterns
- `.agents/skills/cognee/SKILL.md` — the Cognee cognify patterns
- `.agents/skills/baml/SKILL.md` — the BAML extraction schemas
- `.agents/skills/dlt/SKILL.md` — the dlt source patterns
- `.agents/skills/dagster/SKILL.md` — the Dagster asset + sensor patterns
- `.agents/skills/oideachais-storage/SKILL.md` — the DuckLake + MotherDuck + LanceDB storage layer
- `.agents/skills/cross-domain-registry/SKILL.md` — the cross-corpus entity contract
- `.agents/skills/oideachais-cocoindex-v1/SKILL.md` — the 11 v1 Apps canonical pattern
- `sruth/oideachais/cocoindex_flows/leabharlann_embedding.py` — the canonical 3-App v1 home
- `sruth/oideachais/dagster_defs/assets/leabharlann_assets.py` — the 7-asset home
- `sruth/oideachais/dagster_defs/sensors/leabharlann_sensor.py` — the 1-sensor home
- `sruth/oideachais/cognee_integration/leabharlann_cognify.py` — the 3-cognify home
- `sruth/oideachais/cognify_rules/leabharlann_cross_archive.py` — the 3-edge-rule home
- `sruth/oideachais/baml_src/leabharlann_extraction.baml` — the BAML schema
- `openspec/specs/oideachais-leabharlann/spec.md` — the canonical spec

## Email inbox pipeline (2026-06-29)

Added in the `2026-06-29-leabharlann-email-inbox-pipeline` change
to ingest the user's personal + professional email (4 accounts:
DKIT.ie Microsoft 365, 2 Gmail, Hotmail) into the leabharlann
lakehouse alongside the static Gemini / Zotero / Takeout corpora.

- **DLT source** —
  `cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/leabharlann/email_inbox.py`
  yields 4 resources (`inbox_index`, `inbox_threads`,
  `inbox_attachments`, `inbox_legal_threads`) from
  `/srv/mailcow-exports/mailbox-<account>-*.mbox`. MBOX parsing uses
  Python's `mailbox` stdlib (single-pass `mailbox.mbox()` iterator —
  never loads the full file). Thread reconstruction walks the
  `In-Reply-To` + `References` chain, then falls back to a
  normalised subject (strip `Re:`, `Fwd:`, `Fwd: Re:`,
  `[list-tag]`, `(External)`). Partition keys: `account` (from
  `author_archive_accounts.yaml` — 4 accounts), `year` (from
  `Date`), `legal_flag` (boolean from a first-500-char keyword scan
  + sender-domain regex on the first 500 chars). GPG-at-rest is
  opt-in via the existing
  `_takeout_paths.TakeoutAccountConfig.gpg_encrypt_paths` knob
  (prefixes `legal/`, `medical/`, `hsc/`, `nhs/`).
- **Example config** —
  `cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/leabharlann/_email_accounts.example.yaml`
  with 4 example accounts (dkit_ie, gmail_personal, gmail_academic,
  hotmail_legacy).
- **LBYL exception handling** — every `next()` boundary catches
  `OSError` + `mailbox.Error` + `RuntimeError` so a single bad
  message never crashes the source. Empty mbox → 0 rows +
  `mailbox_empty` log warning.
- **Cross-reference**: the full BAML + CocoIndex + Dagster + marimo
  + cognify wiring lives in
  [`.agents/skills/oideachais-email-triage/SKILL.md`](../oideachais-email-triage/SKILL.md).
  The canonical openspec change is
  [`openspec/changes/2026-06-29-leabharlann-email-inbox-pipeline/`](../../openspec/changes/2026-06-29-leabharlann-email-inbox-pipeline/).

