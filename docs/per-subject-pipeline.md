# Per-subject end-to-end pipeline

> The canonical 9-file template for each NCCA Leaving Certificate
> subject in the Cianfhoghlaim Educational MMO.

## The 9-file template

For each of the 8 NCCA subjects, the pipeline consists of:

```
cianfhoghlaim/baml/qpack_<subject>.baml                    # 1. BAML quest-pack generator
cianfhoghlaim/dlt/subjects/<subject>/__init__.py         # 2. Sub-package init
cianfhoghlaim/dlt/subjects/<subject>/sources.py          # 3. DLT PDF source
cianfhoghlaim/dlt/subjects/<subject>/schema.py           # 4. Pydantic models
cianfhoghlaim/dagster/assets/<subject>_assets.py         # 5. Dagster assets (6 per subject)
cianfhoghlaim/cocoindex/<subject>_embedding.py           # 6. v1 CocoIndex App
cianfhoghlaim/agents/meaisinfhoghlaim/educational/<subject>_agent.py  # 7. ADK LlmAgent
cianfhoghlaim/notebooks/leaving_cert/<subject>.py        # 8. marimo teacher dashboard
```

Plus the 5 agent tools live at:
```
cianfhoghlaim/agents/meaisinfhoghlaim/educational/tools/<subject>_<tool>.py
```

## Per-subject BAML contract

Each `qpack_<subject>.baml` file contains:

- **3-5 enums** specific to the subject:
  - `<Subject>NCCALevel` (the NCCA levels the subject is offered at)
  - `<Subject>TopicArea` (the topic taxonomy for the subject)
  - `<Subject>ItemType` (the formative item types for the subject)
  - `<Subject>FeedbackChannel` (the feedback channel enum)
- **5 core Pydantic-mirrored classes**:
  - `<Subject>BilingualText`
  - `<Subject>EvidenceLink`
  - `<Subject>NCCALearningOutcome`
  - `<Subject>FormativeItem`
  - `<Subject>ScoreBreakdown`
  - `<Subject>QuestPack`
  - `<Subject>QuestPackValidation`
- **4 BAML functions**:
  - `Generate<Subject>QuestPack(syllabus, past_papers, marking_schemes, level)`
  - `Extract<Subject>LOStatement(paragraph)`
  - `Generate<Subject>FormativeItem(lo_code, difficulty, level, topic)`
  - `Score<Subject>FormativeResponse(item, attempt)`
  - `Validate<Subject>QuestPack(pack)`

## Per-subject DLT source

Each `dlt/subjects/<subject>/sources.py` file:

1. Yields 4 DLT resources from the local NCCA PDF corpus at
   `cianfhoghlaim/leaving_certificate/<subject>/{en,ga}/`:
   - `<subject>_syllabus` (BAML `ExtractLeavingCertSyllabus`)
   - `<subject>_syllabus_structure` (BAML `ExtractSyllabusStructure`)
   - `<subject>_past_papers` (BAML `ExtractLeavingCertPastPaper`)
   - `<subject>_marking_schemes` (BAML `ExtractLeavingCertMarkingScheme`)
2. For HL-only subjects (APPM), filters ALP papers only.
3. For bilingual subjects (gaeilge, history, geography, chemistry,
   english), reads both `en/` and `ga/` subdirs.
4. Uses PyMuPDF (with pdfplumber fallback) for text extraction.

## Per-subject Dagster assets

Each `dagster/assets/<subject>_assets.py` file declares 6 assets:

1. `<subject>_syllabus_raw` — DLT ingestion of NCCA PDFs
2. `<subject>_syllabus_structured` — BAML `ExtractSyllabusStructure`
3. `<subject>_quest_pack` — BAML `Generate<Subject>QuestPack`
4. `<subject>_embedding` — CocoIndex v1 → LanceDB
5. `<subject>_cognify` — Cognee cognify pass
6. `<subject>_dashboard` — marimo notebook execution

Partitions: `MultiPartitionsDefinition(level × language)`. For
APPM (HL-only), the partition is `hl` only. For subjects without
GA PDFs, the partition is `en` only.

## Per-subject CocoIndex v1 App

Each `cocoindex/<subject>_embedding.py` file:

1. Reads the per-subject PDFs from
   `cianfhoghlaim/leaving_certificate/<subject>/<lang>/`
2. Chunks text with sliding window (512 tokens, 64 overlap)
3. Embeds with BGE-M3 multilingual (1024-dim)
4. Mounts the LanceDB table at `cianfhoghlaim.lc.<subject>.<level>_<language>`

## Per-subject ADK LlmAgent

Each `agents/meaisinfhoghlaim/educational/<subject>_agent.py` file
declares an `LlmAgent` with:

- **name**: `<subject>_agent` (8 short names: math / appm / chem /
  geog / hist / engl / gael / comp)
- **model**: `litellm/anthropic/claude-sonnet-4` (via the existing
  LiteLLM gateway)
- **description**: 1-line summary for ADK routing
- **instruction**: Detailed system prompt with:
  - The 5-10 routing keywords
  - The pedagogical approach (cite the LO code, use 4 graduated
    hints, encourage the student)
  - Cross-subject bridges (e.g. APPM → Mathematics for calculus)
- **tools**: 5 BAML-backed `FunctionTool`s (one per agent tool)

## Per-subject marimo notebook

Each `notebooks/leaving_cert/<subject>.py` file is a reactive
marimo notebook with:

- LO search table (from the per-subject DuckDB)
- Formative items table
- Semantic search box (BGE-M3 over LanceDB)
- "Design quest" panel that generates a fresh formative item via BAML

## Verification

For each subject, the canonical 9-file structure is verified by
`tests/_educational_mmo/test_8_subjects.py` (52 tests, one per
subject per file).

## Reference

- `openspec/changes/cianfhoghlaim-educational-mmo-v1/proposal.md` (D3)
- `openspec/specs/cianfhoghlaim-educational-mmo/spec.md`
- `tests/_educational_mmo/test_8_subjects.py`