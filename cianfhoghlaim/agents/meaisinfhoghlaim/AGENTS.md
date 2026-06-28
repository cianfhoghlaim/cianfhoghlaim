# meaisínfhoghlaim - AI Agent Instructions

> Irish: *machine learning*. The AI/ML quadrant of the Cianfhoghlaim stack.

> **v4 consolidation note (2026-06-28):** `sruth/meaisinfhoghlaim/`
> was merged into `cianfhoghlaim/` per
> `openspec/changes/2026-06-28-consolidate-sruth-into-cianfhoghlaim-v4/`.
> The 12-agent fleet now lives at `cianfhoghlaim/agents/meaisinfhoghlaim/`,
> the OCR registry at `cianfhoghlaim/ocr/`, and BAML schemas at
> `cianfhoghlaim/core/baml/`. All 6 active OCR vision + 4 classical +
> 3 image-gen models now live in a single
> `cianfhoghlaim/ocr/models/registry.py` registry.

## Priority quick reference

The 8 priority skills, the 4 priority commands, and the 3
priority openspec specs at a glance. **Read this first**; the
rest of the file is the full 8-component matrix routing.

### Priority skills (11 of 111)

| Skill | When to load |
|:--|:--|
| [`agno`](../.agents/skills/agno/SKILL.md) | Multi-agent orchestration with tool calling (Agno AgentOS) |
| [`google-adk`](../.agents/skills/google-adk/SKILL.md) | Google's Agent Development Kit (Multi-Agent Workflow Engine) |
| [`baml`](../.agents/skills/baml/SKILL.md) | BAML extraction schemas (canonical client registry) |
| [`cognee`](../.agents/skills/cognee/SKILL.md) | Knowledge graph memory + temporal cognify + `improve()` |
| [`graphiti`](../.agents/skills/graphiti/SKILL.md) | Temporal knowledge graph (bi-temporal model) |
| [`lancedb`](../.agents/skills/lancedb/SKILL.md) | Vector database for RAG (HNSW, MVCC) |
| [`litellm`](../.agents/skills/litellm/SKILL.md) | Unified LLM gateway (all LLM calls route through here) |
| [`langfuse`](../.agents/skills/langfuse/SKILL.md) | LLM observability (traces, prompts, A/B tests) |
| [`celtic-ocr-evaluation`](../.agents/skills/celtic-ocr-evaluation/SKILL.md) | The 10-model × 6-backend OCR registry + the 5 Celtic-specific eval metrics (round 8) |
| [`irish-speech-pipeline`](../.agents/skills/irish-speech-pipeline/SKILL.md) | The 4-stage ASR → agent → TTS loop + the 4 Irish dialects (round 8) |
| [`agent-fleet-orchestration`](../.agents/skills/agent-fleet-orchestration/SKILL.md) | The 12-agent × 5-framework fleet + the LiteLLM routing + the Letta + RisingWave + Langfuse + MLflow stack (round 8) |

### ccc + openspec commands

```bash
bun run ccc:search "OCR model evaluation metric"      # semantic code search
openspec list --specs                                 # 32 specs total
openspec validate <change-id> --strict                # MUST pass before commit
openspec archive <change-id> --yes                    # after deploy
```

### Priority openspec specs for meaisínfhoghlaim

| Spec | One-liner |
|:--|:--|
| `meaisinfhoghlaim-platform` | 10 sub-packages + 4 heartbeat dagster assets + Dagster code-location |
| `meaisinfhoghlaim-agent-frameworks` | 12 specialised agents (Root, Curriculum, Translation, Corpus, etc.) |
| `meaisinfhoghlaim-ocr-htr` | 10 OCR models across 6 backends (Pylaia, TrOCR, PaddleOCR, Tesseract, dots.ocr, VLM) |

## Overview

`meaisínfhoghlaim/` is the AI/ML services layer. It contains the agents,
OCR/HTR models, Celtic-language data sources, and RAG evaluation harnesses
that populate the lakehouse (`sruth/oideachais/`) and serve the inference surface
of the consumer products (`sruth/croilar/`, `sruth/tuatha/`).

Eight integrated components live here, ~15,000+ lines of Python. See
[`README.md`](README.md) for the full component-by-component overview.

## Quick routing — "I want to add X, where do I go?"

| If you want to... | Look at... |
|:--|:--|
| Add or tune a specialised agent | `agents/` (12 agents; root router in `orchestrator.py`) |
| Add a new OCR model or eval metric | `ocr/` (10 models across 6 backends) |
| Add a Celtic-language DLT source | `language/` (Dúchas, Canúint, Téarma, Gaois, cognate DB) |
| Add an Irish-specific ML pipeline | `pipelines/` (scanner, dialect classifier, transcript aligner, LLM router) |
| Add a sentence-level en/ga alignment | `alignment/` (ColPali visual aligner, G2P) |
| Evaluate or improve RAG quality | `evaluation/` (RAGAS; baseline 65.2% → agentic 87.9%) |
| Validate document quality / completeness | `quality/` (curriculum scoring, audio validation) |
| Reference model or dataset metadata | `catalog/` (13 models, 16 sources, 3 training mixes) |
| Add a marimo statistical-analysis notebook | `marimo/` (the `celtic-data-engineering-patterns` change; install with `uv pip install -e "meaisinfhoghlaim[marimo]"`) |

## Conventions

- **Python 3.12+** with `uv`. Module name is `meaisínfhoghlaim` (NOT a
  workspace member itself; importable only via the dev `PYTHONPATH` or
  through the `oideachais` workspace which lists it as a dep).
- **All LLM calls** go through LiteLLM — never call `openai`/`anthropic`
  SDKs directly. Configure routing in `sruth/oideachais/foinse/litellm_config.yaml`.
- **All Irish text** must preserve fadas, tironian, and punctum delens
  through the entire pipeline. Never downcast to ASCII.
- **BAML schemas** live in `sruth/oideachais/baml_src/` — not here.
  Reuse them; don't redefine. (The `baml_src → scéimre` rename
  was deferred per `lateralise-british-isles-domains`; see
  `openspec/specs/meaisinfhoghlaim-platform/spec.md` Known
  issues #5.)
- **Embeddings** are batched at minimum 100 per call (100× performance
  difference vs unbatched — see `sruth/oideachais/README_eile.md` §"Embedding
  Batch Minimum").
- **HNSW indexes** must be dropped before bulk inserts > 50 rows and
  recreated after.

## Testing

```bash
# From the oideachais workspace (it lists meaisínfhoghlaim as a dep)
cd oideachais
uv run pytest tests/                              # full suite
uv run pytest tests/ --cov=meaisínfhoghlaim      # with coverage
uv run pytest tests/agents -k "test_curriculum"  # targeted
```

RAG evaluation is run separately as a manual harness — see
`meaisínfhoghlaim/evaluation/README.md`.

## Relationship to other subprojects

```
┌─────────────────────┐   populates   ┌──────────────────┐
│ meaisínfhoghlaim/   │ ────────────► │   sruth/oideachais/    │
│  (agents, OCR, ML)  │               │  (lakehouse +    │
│                     │               │   DLT + Dagster) │
└─────────────────────┘               └──────────────────┘
        │                                      │
        │ exposes                              │ reads/writes
        ▼                                      ▼
┌─────────────────────┐               ┌──────────────────┐
│      sruth/tuatha/        │               │      sruth/croilar/    │
│  (crypteolas, etc)  │ ◄─────reads───┤ (persona-driven  │
│                     │               │  consumer apps)  │
└─────────────────────┘               └──────────────────┘
```

## Critical files

- `README.md` — full 8-component overview
- `STATUS.md` — per-component maturity matrix (if present)
- `evaluation/README.md` — RAGAS harness + 65.2% → 87.9% report
- `agents/orchestrator.py` — root agent router
- `agents/registry.py` — agent factory map
- `pipelines/llm_router.py` — model selection by capability tier
- `language/dlt_sources/` — Celtic-language DLT sources
- `ocr/eval/` — Irish OCR-specific eval metrics

## Resources

- Root [`AGENTS.md`](../../AGENTS.md) — monorepo agent protocols
- `sruth/oideachais/README.md` — lakehouse data contracts this layer feeds
- `sruth/oideachais/AGENTS.md` (if present) — DLT + Dagster conventions
- `sruth/tuatha/README.md` — sruth/crypteolas/crypteolas_demo agent patterns
- `openspec/AGENTS.md` — change-management workflow

## Feedback loop (project → openspec → skill)

Per the `skills-as-project-docs` openspec change, this quadrant
participates in the formal feedback loop:

1. **When an openspec change is archived**, the canonical skill
   gets a "Post-archive update: YYYY-MM-DD-..." note in its
   "Pair this skill with" section.
2. **When this quadrant changes a BAML extraction / DLT source
   / Dagster asset**, the corresponding skill (`baml/SKILL.md`,
   `dlt/SKILL.md`, `dagster/SKILL.md`) gets a 1-line addition
   to its "When to use this skill" section.
3. **When this quadrant's `STATUS.md` / `REFACTORING.md` /
   README.md changes**, the
   `data-engineering-pipeline-documentation/SKILL.md` gets a
   link to the new content.

The lint script `mise run lint:skills` enforces the 4 metadata
rules (frontmatter, name match, description length, line count)
on every skill in `.agents/skills/`.
