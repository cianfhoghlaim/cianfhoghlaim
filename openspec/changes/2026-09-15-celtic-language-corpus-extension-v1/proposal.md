# Change: Celtic Language Corpus Extension (Scots + Cornish + Manx + Corpas CC) + CEFR Learner Analytics

## Why

The current `celtic-language-pipeline` ships 7 source groups. The Celtic
Language Data Aggregation research (~40KB) identifies 4 additional sources
needed to cover the full 5 Celtic languages + Scots:

- **Scots** (DSL, SCOTS, SCOSYA)
- **Cornish** (Akademi Kernewek, Korpus Kernewek)
- **Manx** (Gaelg Corpus, Manx UD treebank)
- **Corpas na Gàidhlig** (ARCOSG)

Plus 3 new analytics surfaces (CEFR Readiness Score, Mutation Density
Index, Acquisition Velocity) for the `fact_Token` table.

## What changes

- **Celtic Language Corpus Extension** (NEW capability
  `celtic-language-corpus-extension`): 4 new DLT source
  groups + `.vrt` parser helper + OntoLex-Lemon edge types.

- **CEFR Learner Analytics** (NEW capability
  `cefr-learner-analytics`): 5 BAML functions + 1 CocoIndex
  v1 App + 1 Dagster asset module + 1 marimo dashboard +
  1 educational agent + 4 CEFR metrics.

- **OntoLex-Lemon cognify edges** (capability
  `agent-memory-systems`): add `cognateOf`,
  `translationOf`, `hasCognateIn` edge types to the Cognee
  cognify pipeline.

## Out of scope

- The 6 deferred BIEP v3 jurisdictions' curriculum rollout (issue #140).
- The Qwen DashScope API re-enablement (issue #147).

## Dependencies

```markdown
## Dependencies

`Blocked by: 2026-08-09-biiep-v3-4-stage-ireland-education-rollout-v1`.

`Blocked by (soft): 2026-09-01-celtic-mythology-content-system-v1`.

`Affected repos: cianfhoghlaim`
```

## Impact

- Affected specs:
  - NEW: `celtic-language-corpus-extension` (4 ADDED Requirements)
  - NEW: `cefr-learner-analytics` (5 ADDED Requirements)
  - `celtic-language-pipeline` (3 ADDED Requirements)
  - `agent-memory-systems` (1 ADDED Requirement)
- Affected code/config:
  - `dlt/language/scots/` (NEW)
  - `dlt/language/cornish/` (NEW)
  - `dlt/language/manx/` (NEW)
  - `dlt/language/corpas_cc_gaelic/` (NEW)
  - `dlt/language/_shared/vrt_parser.py` (NEW)
  - `notebooks/_shared/cefr_scoring.py` (NEW)
  - `notebooks/_shared/cognate.py` (NEW)
  - `baml/celtic/corpus.baml` (NEW)
  - `cocoindex/biep_parity/cefr_embedding.py` (NEW)
  - `orchestration/defs/2_materials/cefr_assets.py` (NEW)
  - `notebooks/35_celtic_corpus_dashboard.py` (NEW)
  - `notebooks/36_cefr_readiness_dashboard.py` (NEW)
  - `agents/meaisinfhoghlaim/educational/cefr_learner_analytics_agent.py` (NEW)