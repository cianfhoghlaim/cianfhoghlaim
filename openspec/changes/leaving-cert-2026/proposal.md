# Leaving Certificate 2026 — Resource Pipeline & Pages Hosting

## Why

The Leaving Certificate 2026 exams run **Friday 5 June (Mathematics Paper 1)** through **Thursday 11 June (Business & Construction Studies)**. This change activates the existing `oideachais/data_platform` infrastructure to produce per-subject study resources for the 7 highest-priority subjects:

| Subject | Exam date | Day | Papers | Times |
|:--|:--|:--|:--|:--|
| **Mathematics** | Fri 5 Jun + Mon 8 Jun | — | P1 (H&O + F), P2 (H&O) | P1: 2:00-4:30 (Fri), P2: 9:30-12:00 (Mon) |
| **Irish (Gaeilge)** | Mon 8 Jun + Tue 9 Jun | 1+2 | P1 (incl aural), P2 | P1: 2:00-4:20 (H), 2:00-3:50 (O), 2:00-4:20 (F); P2: 9:30-12:35 (H), 9:30-11:50 (O) |
| **Biology** | Tue 9 Jun | 2 | Single (H&O) | 2:00-5:00 |
| **French** | Wed 10 Jun | 3 | Written + Aural | Written: 9:30-12:00, Aural: 12:10-12:50 |
| **History** | Wed 10 Jun | 3 | (H&O) | 2:00-4:50 |
| **Business** | Thu 11 Jun | 4 | (H), (O) | H: 9:30-12:30, O: 9:30-12:00 |
| **Construction Studies** | Thu 11 Jun | 4 | (H), (O) | H: 2:00-5:00, O: 2:00-4:30 |

## What

This change wires up the **per-subject resource pipeline** that produces, for each of the 7 subjects, the following outputs:

1. **Syllabus analysis** — NCCA syllabus summarised, each learning outcome tagged by topic and weighting
2. **Past exam question analysis** — BAML extraction of every past exam question (2017-2025) tagged by topic, paper, marks, year
3. **Marking scheme analysis** — PCLM (Partial Credit, Logical Marking) conventions per subject, common mistakes, allocation patterns
4. **Study prioritisation** — MiniMax M3 analysis ranking each topic by `expected_marks ÷ hours_of_study`
5. **Exam layout tips** — paper structure, time-per-question, common traps, marker expectations

These outputs are exposed as **public pages** at `oideachais.cianfhoghlaim.ie/leaving-cert/{subject}/`, with the original PDFs in Cloudflare R2 (`cianfhoghlaim-leaving-cert` bucket) and the analysis rendered via DuckDB/MotherDuck queries on the page.

## Impact

### Affected specs
- NEW `leaving-cert-pipeline` — per-subject asset graph
- NEW `oideachais-leaving-cert-portal` — per-subject public pages

### Existing assets to extend
- `oideachais/data_platform/dagster_defs/assets/ireland/exam_materials_assets.py` — extend to include 7 subjects
- `oideachais/data_platform/cocoindex_flows/curriculum_specification_extraction.py` — reuse BAML extraction for syllabus
- `oideachais/data_platform/cocoindex_flows/research_embedding.py` — reuse embeddings for past papers
- `oideachais/data_platform/dlt_sources/ireland/examinations.py` — extend for 7 subjects
- `oideachais/data_platform/dlt_sources/ireland/curriculum_source.py` — extend for 7 subjects

### LLM stack
- **MiniMax M3** (token-plan API) for analysis via LiteLLM gateway
- **DeepSeek V4 Pro** for BAML extraction
- New LiteLLM model entry in `oideachais/data_platform/dlt_utils/foinse/litellm_config.yaml`

### Hosting
- `oideachais.cianfhoghlaim.ie/leaving-cert/{subject}/` — TanStack Start, CopilotKit AG-UI, MotherDuck Dives, Recharts
- Cloudflare R2: `cianfhoghlaim-leaving-cert` bucket (syllabus, exam-papers, marking-schemes)
- MotherDuck: `md:cianfhoghlaim_leaving_cert` (public-read tables)

### Cost
- ~$3-6 per subject, ~$20-35 total one-time
- Year-over-year refresh: ~$5-10 per year (incremental)

## Non-Goals
- No interactive study plan (manual: self-tracked)
- No new external scraping beyond existing DLT assets
- No Croilar portal surface (oideachais web only)
- No live exam-year results (deferred to post-exam annual sensor)

## Per-Subject Build Order

| # | Subject | Day | Date |
|--:|:--|:--|:--|
| 1 | Mathematics | -3 | Fri 5 Jun |
| 2 | Irish | 0 | Mon 8 Jun |
| 3 | Biology | 1 | Tue 9 Jun |
| 4 | French | 2 | Wed 10 Jun |
| 5 | History | 2 | Wed 10 Jun |
| 6 | Business | 3 | Thu 11 Jun |
| 7 | Construction Studies | 3 | Thu 11 Jun |

## Risks
1. Cognee cognify() blocked by LLM key (opencode.json fix committed; takes effect next session)
2. SEC exam-paper scraping needs `?fp=` re-verification each year
3. Irish-language content from M3 must be reviewed by an Irish speaker
4. MotherDuck token rotation (Infisical handles)
5. Audio for French/Irish listening (existing `sec_aural_transcripts.py` as starting point)
