# meaisínfhoghlaim - AI Agent Instructions

> Irish: *machine learning*. The AI/ML quadrant of the Cianfhoghlaim stack.

## Overview

`meaisínfhoghlaim/` is the AI/ML services layer. It contains the agents,
OCR/HTR models, Celtic-language data sources, and RAG evaluation harnesses
that populate the lakehouse (`oideachais/`) and serve the inference surface
of the consumer products (`croilar/`, `tuatha/`).

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
  SDKs directly. Configure routing in `oideachais/foinse/litellm_config.yaml`.
- **All Irish text** must preserve fadas, tironian, and punctum delens
  through the entire pipeline. Never downcast to ASCII.
- **BAML schemas** live in `oideachais/scéimre/` (the Irish word for
  *schema*) — not here. Reuse them; don't redefine.
- **Embeddings** are batched at minimum 100 per call (100× performance
  difference vs unbatched — see `oideachais/README_eile.md` §"Embedding
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
│ meaisínfhoghlaim/   │ ────────────► │   oideachais/    │
│  (agents, OCR, ML)  │               │  (lakehouse +    │
│                     │               │   DLT + Dagster) │
└─────────────────────┘               └──────────────────┘
        │                                      │
        │ exposes                              │ reads/writes
        ▼                                      ▼
┌─────────────────────┐               ┌──────────────────┐
│      tuatha/        │               │      croilar/    │
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
- `oideachais/README.md` — lakehouse data contracts this layer feeds
- `oideachais/AGENTS.md` (if present) — DLT + Dagster conventions
- `tuatha/README.md` — crypteolas/crypteolas_demo agent patterns
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
