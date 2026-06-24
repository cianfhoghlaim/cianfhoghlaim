---
title: 'Deploy Plan 02 — Cross-Lingual Generative Tutoring Engine'
domain: deploy-plan
status: draft
description: 'Bilingual (en/ga, en/cy, en/gd) generative tutoring with BAML-extracted curriculum grounding, Cognee knowledge graph, and LanceDB outcome embeddings. Built on meaisinfhoghlaim.agents.tutor.'
read_when:
  - 'designing tutoring or LLM-based teaching UIs'
  - 'extending BAML schemas for pedagogical extraction'
supersedes: []
superseded_by: []
related_specs:
  - bilingual-content
  - knowledge-graph
  - semantic-search
  - oideachais-pipeline
related_apps:
  - meaisinfhoghlaim/agents/tutor
  - meaisinfhoghlaim/llm_stack
  - oideachais/web
related_llm_stack:
  - 'BAML (typed curriculum grounding)'
  - 'litellm (model routing: kimi-k2.6, glm-5.1, ollama local)'
  - 'Cognee (long-term learner state)'
  - 'LanceDB (cross-lingual outcome embeddings)'
truth: sole
last_touched: 2026-06-13
---

# Deploy Plan 02 — Cross-Lingual Generative Tutoring Engine

## 0. Why this plan

Replace the original Tangent 2 framing (which named `UCCIX-Llama2-13B-Instruct`
as a single model) with a deploy plan grounded in the
**BAML → litellm → Cognee → LanceDB** stack that already exists in
`meaisinfhoghlaim/llm_stack/`. The goal is a cross-lingual tutoring
engine that:

1. Teaches in **any pair** of {en, ga, cy, gd, gv} (and extensible to
   br, kw) with **grounded** explanations (no hallucination of
   curriculum content).
2. Tracks **learner state** across sessions (long-term memory).
3. Generates **executable content** (Marimo notebooks) on demand.

## 1. Monorepo grounding

| Asset | Path | Use |
|:--|:--|:--|
| Quadrant | `meaisinfhoghlaim/` | AI/ML — agents, OCR, language, pipelines |
| Quadrant | `oideachais/` | Data platform — curriculum, BAML extraction, knowledge graph |
| Quadrant | `tuatha/ui/` | Front-end (Babylon.js) — *only if 3D tutor avatar desired* |
| Skill | `.agents/skills/llm-stack-hierarchy/` | BAML→litellm→Cognee→LanceDB ordering |
| Skill | `.agents/skills/cognee/SKILL.md` | Long-term memory |
| Skill | `.agents/skills/lancedb/SKILL.md` | Cross-lingual outcome embeddings |
| Skill | `.agents/skills/baml/SKILL.md` | Typed curriculum extraction |

The full LLM stack hierarchy is in `docs/04-ai-ml/llm-stack-hierarchy.md`.

## 2. Three-tier language model routing

We do NOT hardcode a single model. The LLM tier is a **litellm router**
that picks the right model for the task:

| Task | Default model | Fallback chain |
|:--|:--|:--|
| Curriculum extraction (BAML) | `baml-gpt-4o` | `baml-claude-sonnet` → `baml-kimi-k2.6` |
| Real-time tutoring chat | `litellm:kimi-k2.6` (multilingual) | `litellm:glm-5.1` → `litellm:openai-gpt-4o-mini` |
| Code generation (Marimo) | `litellm:claude-sonnet` | `litellm:openai-gpt-4o` |
| Local-only mode (offline) | `ollama:qwen2.5-14b-gguf` | `ollama:llama3.1-8b-gguf` |

The router is configured in `meaisinfhoghlaim/llm_stack/router.py` and
reads from Infisical (`/oideachais/llm_keys/*`).

## 3. Grounded curriculum: BAML extraction

Every tutoring response is **grounded** in extracted curriculum
outcomes. The pipeline:

1. **Ingest** curriculum specs (8 nations, see Deploy Plan 01 §2.1).
2. **Extract** learning outcomes with BAML:
   ```baml
   class LearningOutcome {
     id string
     nation string
     qualification string
     subject string
     level int
     description string
     prerequisites string[]            // other outcome ids
     bloom_level string               // remember|understand|apply|analyse|evaluate|create
     bilingual_terms BilingualTerm[]   // see §3.1
   }

   class BilingualTerm {
     term_en string
     term_target string                // ga|cy|gd
     glossary_source string            // "téarma.ie" | "PrysmaGeiriadur" | "Am Faclair Beag" | ...
   }
   ```
3. **Store** outcomes in Cognee (knowledge graph) and LanceDB
   (multilingual embeddings for cross-lingual retrieval).

### 3.1. Bilingual term sources (v1)

| Language pair | Glossary source | DLT source |
|:--|:--|:--|
| en↔ga (Irish) | `téarma.ie`, `gaois.ie` | `oideachais/dlt_sources/ireland/gaois.py` (existing) |
| en↔cy (Welsh) | `PrysmaGeiriadur`, `geiriadur.ac.uk` | `oideachais/dlt_sources/uk/wales/terminology.py` (new) |
| en↔gd (Scottish Gaelic) | `Am Faclair Beag`, `faclair.com` | `oideachais/dlt_sources/uk/scotland/terminology.py` (new) |
| en↔gv (Manx) | `Fockley Rheast, Manx-English Dictionary` | `oideachais/dlt_sources/crown_dependencies/iom/terminology.py` (new) |

The BAML prompt for bilingual terms is in
`meaisinfhoghlaim/llm_stack/baml/term_extraction.baml`.

## 4. Cross-lingual outcome retrieval (LanceDB)

The vector space is **multilingual**: a concept in English ("Photosynthesis")
and its Irish translation ("Fótaisintéis") land near each other in the
embedding space. We use a multilingual sentence-transformer
(`paraphrase-multilingual-MiniLM-L12-v2` for v1; upgrade to
`bge-m3` in v2).

Storage is split:

| Store | Content | Why |
|:--|:--|:--|
| LanceDB Cloud (hosted) | Outcome embeddings | HNSW index, multi-region, MVCC-safe (per skill v0.15+) |
| LanceDB local (in-process) | Session-level conversation embeddings | Ephemeral, no network round-trip |

The bilingual cross-walk is a **join** at query time:

```python
# pseudo-code for a tutor turn
outcomes = lance.search(learner_query, language="ga")
    .filter(nation="ROI", level=3)               # Junior Cycle
    .top_k(8)
    .to_list()
grounded_context = cognee.get_subgraph(outcomes)  # knowledge graph
prompt = tutor_prompt(outcomes, grounded_context, learner_state)
response = litellm.completion("tutor", prompt)
```

## 5. Learner state (Cognee long-term memory)

Per learner, we maintain:

- **Concept mastery** — a `ConceptMastery { outcome_id, mastery: 0..1, last_seen, attempts, errors }` row
- **Error history** — vector representations of past mistakes, joined to outcomes
- **Session memory** — recent conversations (last 5 turns verbatim, older summarised)
- **Language preference** — `target_language`, `proficiency: A1..C2`, `scaffolding_level`

Cognee's `improvement()` operation runs nightly to enrich the graph
with inferred prerequisite chains and concept clusters. The skill is
loaded via `cognee.improve(dataset_name="learner_<id>")`.

## 6. Tutoring modes (v1)

| Mode | Behaviour | Backed by |
|:--|:--|:--|
| **Explain** | Tutor explains an outcome in `target_language` with English fallback for technical terms | BAML outcome + glossary |
| **Quiz** | Generate a question aligned to `bloom_level` of the outcome | litellm + BAML Q-schema |
| **Scaffold** | Break a hard outcome into 3-5 prerequisites with simpler language | Cognee graph traversal |
| **Marimo** | Generate a runnable notebook demonstrating the concept | litellm (code) + Marimo template |

The `meaisinfhoghlaim/agents/tutor/` agent orchestrates these modes.
The TanStack Start route at `oideachais/web/routes/tutor.$lessonId.tsx`
is the user surface.

## 7. Real-time streaming

LLM responses are streamed via Server-Sent Events (SSE) from the
oideachais BAML service to the web app. The `llm-stack-hierarchy` skill
documents the streaming contract (BAML partial → litellm stream → SSE).

Latency target: **first token < 1.5s** for tutoring chat
(`litellm:kimi-k2.6` on warm cache).

## 8. Phased action plan

| Phase | Scope | Exit criteria |
|:--|:--|:--|
| 0 | Bilingual term DLT sources for 4 language pairs (en↔ga, en↔cy, en↔gd, en↔gv) | 10,000 terms ingested into `motherduck.oideachais_terminology.*` |
| 1 | `meaisinfhoghlaim/agents/tutor/` orchestrator | Explain + Quiz modes work end-to-end on 1 subject (e.g. Junior Cycle Science) |
| 2 | Multilingual LanceDB index (paraphrase-multilingual-MiniLM-L12-v2) | Cross-lingual recall@10 ≥ 0.7 on a 100-query gold set |
| 3 | Cognee learner state | Concept mastery + error history persist across sessions |
| 4 | Marimo notebook generator | 10 runnable notebooks generated from real outcomes |
| 5 | TanStack Start `/tutor/$lessonId` route with SSE | Pilot with 20 students (5 per language pair) |

## 9. Risks and mitigations

| Risk | Mitigation |
|:--|:--|
| Hallucination of curriculum content | All responses grounded in BAML-extracted outcomes; if no outcome matches, tutor says "I don't know" |
| Token cost explosion | litellm router chooses smaller models for routine turns; prompt cache on outcome payloads |
| Low-quality bilingual glossary | Téarma.ie and equivalents are authoritative; we do NOT translate curriculum terms ourselves |
| Cultural bias in explanations | Glossary sources chosen for region; BAML prompt includes `region_aware` flag |

## 10. Out of scope (deferred)

- 3D Babylon.js tutor avatar — `tuatha/ui/` integration is a v2 feature
- Voice input/output (Whisper / ElevenLabs) — v2
- Real-time classroom mode (multi-student) — v3

## 11. Cross-references

- `docs/00-core/CLAUDE.md` — 5-quadrant topology
- `docs/02-data-platform/storage-mental-model.md` — DuckLake/MotherDuck/LanceDB
- `docs/04-ai-ml/llm-stack-hierarchy.md` — BAML→litellm→Cognee ordering
- `docs/05-web/frontend-topology.md` — TanStack Start `/tutor` route
- `docs/03-agents/agent-frameworks.md` — agent orchestration patterns
- `openspec/specs/bilingual-content/spec.md`
- `openspec/specs/knowledge-graph/spec.md`
- `openspec/specs/semantic-search/spec.md`
- `.agents/skills/llm-stack-hierarchy/` (if loaded)
- `.agents/skills/cognee/SKILL.md`
- `.agents/skills/lancedb/SKILL.md`
- `.agents/skills/baml/SKILL.md`
