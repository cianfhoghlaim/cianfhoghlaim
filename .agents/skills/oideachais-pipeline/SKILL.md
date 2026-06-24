---
name: oideachais-pipeline
description: Celtic education curriculum pipeline for Irish, UK, and pan-Celtic content processing with DLT ingestion, CocoIndex embeddings, and Dagster orchestration.
---

# Oideachas Pipeline

**Version:** 1.0 | **Last Updated:** 2025-12

## Overview

The oideachas (Irish: "education") pipeline processes Celtic education curriculum content from multiple sources (NCCA, SEC, UK DfE) and transforms it into searchable, AI-enhanced learning materials.

| Feature | Description |
|---------|-------------|
| DLT Ingestion | Multi-source curriculum extraction |
| CocoIndex Flows | Embedding generation for semantic search |
| Dagster Assets | Orchestrated data transformation |
| ADK Agents | Education-focused AI assistants |

## When to Use This Skill

Activate when users need:

- "Process curriculum documents from NCCA or SEC"
- "Generate embeddings for curriculum search"
- "Build education knowledge graph"
- "Create ADK agent for curriculum queries"
- "Extract exam papers and marking schemes"

## Project Integration

### Data Flow Location

| Component | Path |
|-----------|------|
| Main Pipeline | `sruth/oideachais/` |
| DLT Sources | `sruth/oideachais/dlt_sources/` |
| CocoIndex Flows | `sruth/oideachais/cocoindex_flows/` |
| Dagster Definitions | `sruth/oideachais/dagster/` |
| ADK Agents | `sruth/oideachais/agents/` |

### Research References (taighde/)

| Directory | Relevant Documents |
|-----------|-------------------|
| `taighde_scoil/` | Curriculum analysis, indexing strategies |
| `taighde_teanga/` | Irish NLP resources, dialect handling |

### ML Model Dependencies (meaisinfhoghlaim/)

| Model | Usage |
|-------|-------|
| UCCIX-Llama2-13B | Irish text generation |
| GaBERT | Irish embeddings |
| Qwen2.5-Math-7B | Bilingual math reasoning |
| ColPali | Visual document embeddings |

## Core Concepts

### 1. DLT Source Configuration

```python
from dlt import pipeline, source

@dlt.source
def ncca_curriculum():
    """NCCA curriculum document source."""
    yield dlt.resource(
        fetch_specifications,
        name="specifications",
        write_disposition="merge",
        primary_key="specification_id"
    )
```

### 2. CocoIndex Embedding Flow

```python
import cocoindex as ci

@ci.flow_def(name="curriculum_embeddings")
def curriculum_embeddings(doc: ci.DataScope):
    """Generate embeddings for curriculum documents."""
    text = doc.content.text
    embedding = ci.functions.embed(
        text,
        model="text-embedding-3-large",
        batch_size=100  # REQUIRED: min batch size
    )
    return {"embedding": embedding}
```

### 3. Dagster Asset Definition

```python
from dagster import asset, AssetExecutionContext

@asset(
    group_name="curriculum",
    compute_kind="dlt",
)
def curriculum_documents(context: AssetExecutionContext):
    """Ingest NCCA curriculum documents."""
    pipeline = dlt.pipeline(
        pipeline_name="ncca_curriculum",
        destination="duckdb",
        dataset_name="curriculum"
    )
    # CRITICAL: Single-threaded DuckDB access
    return pipeline.run(ncca_curriculum())
```

## KCG Tripartite Data Landscape

The Irish education data is governed by **three evidential
sources** with distinct ownership and change cadence:

| Source | Domain | Cadence | Schema | DLT source |
|:--|:--|:--|:--|:--|
| **NCCA** (curriculumonline.ie) | Pedagogical intent | ~Decade | Specifications, Learning Outcomes | `ncca_curriculum` |
| **SEC** (examinations.ie) | Evidentiary truth | Annual | Exam Papers + Marking Schemes | `sec_examinations` |
| **DES Circulars** | Temporal governance | Monthly | Policy, amendments, repeals | `des_circulars` |

All three ingest into the lakehouse via the
`oideachais/sources.yaml` registry; every Dagster asset
follows the `{nation}.{domain}.{entity}` contract from
`.agents/skills/cross-domain-registry/SKILL.md`.

## BAML Schemas (the structured extraction layer)

The oideachais pipeline uses BAML to convert raw
extracted text (PDF, HTML) into typed records. The
canonical schemas live at `oideachais/baml_src/`:

| BAML class | Purpose | Source doc |
|:--|:--|:--|
| `PrimaryLearningOutcome` | NCCA primary LOs (en + ga) | NCCA specifications |
| `ScienceOutcome` | Junior Cycle science experiments | NCCA JC science |
| `MarkingPoint` | SEC marking point + 10C scale | SEC marking schemes |
| `RubricDescriptor` | JC/LC rubric levels (4 bands) | SEC rubrics |
| `CircularMetadata` | DES circular (issue, effective, status) | DES circulars |
| `SiteAnalysis` | Browser page fingerprint (BAML) | Browser pipeline |

The bilingual strategy uses a **unified concept node**:
`name_en` and `name_ga` are sibling fields on the same
record; dialect variations (Connacht, Munster, Ulster)
attach via `HAS_FORM` edges in the knowledge graph. See
`.agents/skills/irish-edtech/SKILL.md` for the canonical
Irish-language model stack (GaBERT, UCCIX).

## Cianfhoghlaim-Specific Usage

### Database Safety (from CLAUDE.md)

**DuckDB:** SINGLE_THREADED_ONLY
```python
# Use SerialDatabaseExecutor for DuckDB access
from sruth.storage import SerialDatabaseExecutor

with SerialDatabaseExecutor() as db:
    db.execute("SELECT * FROM curriculum")
```

**LanceDB:** MVCC-safe with automatic conflict resolution
```python
# LanceDB handles concurrent writes with retry/backoff
import lancedb

db = lancedb.connect("./embeddings")
table = db.create_table("curriculum", data, mode="overwrite")
```

### Embedding Batching

```python
# REQUIRED: Batch minimum 100 texts per API call
texts = [doc.content for doc in documents]
embeddings = embed_batch(texts, batch_size=100)

# For bulk inserts >50 rows, drop HNSW index first
db.execute("ALTER TABLE curriculum DROP INDEX embedding_idx")
# ... insert data ...
db.execute("CREATE INDEX embedding_idx ON curriculum USING HNSW(embedding)")
```

## Best Practices

1. **Always batch embeddings** - Minimum 100 texts per API call
2. **Single-threaded DuckDB** - Use SerialDatabaseExecutor
3. **Irish models** - Use UCCIX or GaBERT for Irish text
4. **BAML validation** - Schema validation for LLM extraction

## Resources

- **OpenSpec:** `openspec/specs/oideachais-pipeline/spec.md`
- **Dagster Docs:** https://docs.dagster.io
- **CocoIndex Docs:** https://cocoindex.io/docs
- **Related Skills:** dagster, cocoindex, dlt, lancedb, baml

## EU sources (1800-line catalogue)

Irish is the **24th official EU language** (since 2007)
and a **full working language** (since 2022), which makes
EU institutions the single largest source of
**professionally translated, parallel Irish-English
text** available under open licences. The 1800-line
catalogue at `docs/teanga/eu-irish-datasets.md` indexes
the full inventory; this section is the pointer + the
canonical KCG routing rules.

### The 4 largest parallel sources (by pair count)

| Source | Pairs (en↔ga) | Domain | License | Access |
|:--|--:|:--|:--|:--|
| **DGT-Translation Memory** | 1-3M | EU legal, administrative | CC-BY 4.0 | JRC direct download, also OPUS `dgt` |
| **JRC-Acquis** | ~1M | EU legislation (acquis communautaire) | research-friendly | OPUS `JRC-Acquis` |
| **Europarl v10** | ~700k | Parliamentary debates (2007+) | OPUS-licensed | OPUS `Europarl`, also `statmt.org/europarl` |
| **ELRC-CORDIS** | smaller | EU research project descriptions | per-resource | ELRC-SHARE |

For NMT training data, **DGT-TM is the KCG default** —
it's the largest, cleanest, and CC-BY 4.0. Europarl is
second choice for political-domain adaptation.

### The 10 EU institutions with Irish resources

| Institution | URL | Key resource |
|:--|:--|:--|
| EUR-Lex | eur-lex.europa.eu | CELEX-numbered legal texts, all 24 langs |
| European Parliament | europarl.europa.eu | Verbatim debates (Europarl corpus) |
| European Commission | ec.europa.eu | Policy docs, communications, reports |
| DGT (Translation) | joint-research-centre.ec.europa.eu/language-technology-resources | DGT-TM (TMX, 24 langs) |
| IATE | iate.europa.eu | **~200K Irish terms** (terminology DB, 8.8M total) |
| EU Open Data Portal | data.europa.eu | Statistical + geospatial + environmental |
| CdT (Translation Centre) | cdt.europa.eu | Agency + pharmaceutical translations |
| CJEU | curia.europa.eu | Selected judgments in Irish |
| Publications Office | op.europa.eu | Official Journal, EuroVoc thesaurus (RDF/SKOS) |
| **Tearma.ie / Focal.ie** | tearma.ie / focal.ie | **Irish national** terminology (cross-refs IATE) |

### KCG ingestion pattern (4 strategies)

For the `oideachais` pipeline, ingest EU Irish data via
the 4 canonical strategies:

1. **OpusTools** for DGT, Europarl, JRC-Acquis (Moses
   format):
   ```python
   from opustools import OpusRead
   OpusRead(directory="dgt", source="en", target="ga", release="latest")
   OpusRead(directory="Europarl", source="en", target="ga", release="v10")
   ```
2. **EUR-Lex SPARQL** (publications.europa.eu/webapi/rdf/sparql)
   for legal texts aligned by CELEX number.
3. **IATE XML/TBX** for terminology (200K Irish terms
   cross-referenced to EU legislation).
4. **Common Crawl regex filter** for EU-domain Irish:
   `*.europa.eu/ga/`, `*.europarl.europa.eu/ga/`,
   `*.ec.europa.eu/*/ga`, `eur-lex.europa.eu/*/ga/*`.

### Quality control (the 4 KCG invariants)

Apply the standard quality pipeline to every EU dataset
before it enters the lakehouse:

1. **Deduplicate** by `(source, target)` exact-match.
2. **Length filter** — drop pairs < 10 chars either
   side; reject `len(src)/len(tgt) > 3.0` (avoids
   one-word "translations").
3. **Langdetect gate** — both sides must classify as
   `en` / `ga`; drop pairs that fail (catches
   translationese that drifted).
4. **Cross-lingual embedding alignment score** — use
   `sentence-transformers/stsb-xlm-r-multilingual` and
   drop pairs with cosine similarity < 0.7.

### Export formats (5 parallel outputs)

For every curated dataset, export to all 5 forms so
downstream tools can pick:

- **Moses format** (separate `.en` + `.ga` files)
- **JSON** (`[{"source": "...", "target": "..."}]`)
- **CSV** (with `source, target` columns)
- **HuggingFace `Dataset`** via `Dataset.from_dict()`
- **HuggingFace Hub** via `dataset.push_to_hub(...)`

### Celtic-specific anti-patterns

- **Don't use the raw Europarl alone for production
  NMT** — the corpus is overwhelmingly political /
  legal prose, which causes "translationese"
  overfitting (the model writes grammatically
  correct Irish that mirrors English syntax). Mix in
  conversational + literary data from teanglann.ie
  / Cnuas samples.
- **Don't trust the IATE terminology without manual
  review for your domain** — IATE is comprehensive
  but contains entries for deprecated/archaic terms
  that are not in current use. Always cross-check
  with `tearma.ie` (the Irish national terminology
  database) for live curriculum work.
- **Don't bypass the langdetect gate** — EU legal
  text often has untranslated boilerplate ("Article 1"
  appears as "Article 1" in both columns); these
  pairs are noise.
- **Don't use `--max-rows 1024` for marimo notebooks**
  over the EU data — 1M-pair DGT requires
  `--max-rows 4096` and `--max-chars 200000` to
  inspect the full distributions.

### KCG `oideachais` ingest schedule

| Source | Cron | Why this cadence |
|:--|:--|:--|
| DGT-TM | `0 0 1 1 *` (Jan 1) | Annual release |
| Europarl | `0 0 * * 0` (weekly) | New plenary sessions every week |
| EUR-Lex | `0 */6 * * *` (6h) | Active legislation updates |
| IATE | `0 0 1 * *` (monthly) | Terminology updates |
| Tearma.ie | `0 0 1 * *` (monthly) | National sync |

See [`docs/teanga/eu-irish-datasets.md`](../../../docs/teanga/eu-irish-datasets.md)
for the full 1800-line EU+Irish dataset catalogue
including the 8 build strategies, the 9 dataset
characteristics, the per-institution access methods,
and the legal/licensing notes.
