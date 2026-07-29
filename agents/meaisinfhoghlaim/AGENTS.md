# agents/meaisinfhoghlaim — OCR/HTR/Alignment Sub-Package

> **The OCR/HTR/alignment sub-package** for the agent fleet.
> Houses the 10 OCR backends across 4 ensemble patterns + the
> 3 alignment primitives + the 3 educational agents. The
> canonical home for OCR/HTR processing of scanned curricula,
> manuscripts, and historical documents.

## Priority quick reference

### Priority skills (4 of 53)

| Skill | When to load |
|:--|:--|
| [`agent-observability`](../.agents/skills/agent-observability/SKILL.md) | The 5-layer observability stack (used by OCR/HTR pipelines) |
| [`cognee`](../.agents/skills/cognee/SKILL.md) | The knowledge graph backend (used by OCR/HTR pipelines) |
| [`baml`](../.agents/skills/baml/SKILL.md) | BAML extraction patterns for OCR outputs |
| [`dignified-python`](../.agents/skills/dignified-python/SKILL.md) | Production Python standards |

### Priority commands

```bash
# The 10 OCR backends
python -c "from cianfhoghlaim.meaisinfhoghlaim.models.registry import CLASSICAL_OCR; print(len(CLASSICAL_OCR))"
# Expected: 6 (the canonical 6 from the 2026-07-17 phantom-agents fix)

# The M4-Max dispatch helper
python -c "from cianfhoghlaim.meaisinfhoghlaim.models.registry import select_optimal_for_m4_max; print(select_optimal_for_m4_max())"
# Expected: gemma-4-26B-A4B
```

### Priority openspec specs (2)

| Spec | One-liner |
|:--|:--|
| `meaisinfhoghlaim-platform` | The 10 sub-packages + the 4 heartbeat Dagster assets |
| `meaisinfhoghlaim-ocr-htr` | The 10 OCR models across the canonical 6 backends |

## Overview

`agents/meaisinfhoghlaim/` is the **OCR/HTR/alignment sub-package**
for the agent fleet. It houses:

- **10 OCR backends** across 4 ensemble patterns (the canonical
  6 from `meaisinfhoghlaim/models/registry.py:CLASSICAL_OCR` + the
  4 HTR/Dúchas specialists)
- **3 alignment primitives** (cross-frame, cross-archive, cross-nation)
- **3 educational agents** at `agents/meaisinfhoghlaim/educational/`
  - `academic_history_agent` — the cross-archive academic history
  - `celtic_grammar_agent` — the Celtic grammar specialist
  - `celtic_morphology_agent` — the Celtic morphology specialist

The sub-package is part of the `meaisinfhoghlaim/` (top-level)
package which is the canonical home for OCR/HTR/alignment work.
The `agents/meaisinfhoghlaim/` sub-tree provides the agent-side
integration.

## The 10 OCR backends

The canonical 6 backends (per the `2026-07-17-fix-phantom-agents-and-ocr-backend-list-v1`
change):

| Backend | Purpose | Port |
|:--|:--|--:|
| **Docling-serve** | Document layout + table extraction | 5001 |
| **PaddleOCR** | Multilingual OCR (100+ languages) | 5002 |
| **Dots-OCR** | High-fidelity OCR for handwritten text | 5003 |
| **Unstract** | No-code LLM-powered extraction | 8002 |
| **Tesseract** | The classic OCR engine | 5004 |
| **Tesseract-shadow** | Tesseract 4 shadow variant for A/B testing | 8890 |

The 4 HTR/Dúchas specialists (deferred from the canonical set):

| Backend | Purpose |
|:--|:--|
| Pylaia | The Dúchas HTR specialist (handwritten Irish manuscript recognition) |
| TrOCR | The Microsoft transformer OCR |
| OlmOCR | The Allen AI OCR |
| VLM | The vision-language model OCR |

The Pylaia Dúchas HTR specialist is preserved for the Dúchas
corpus and remains available via `tuatha_root_agent`, but is
no longer in the canonical `CLASSICAL_OCR` registry.

## The 4 ensemble patterns

| Pattern | Description | Used when |
|:--|:--|:--|
| **Single-best** | Pick the highest-confidence backend | Production: when 1 backend is the obvious winner |
| **Voting** | All backends vote; majority wins | Production: when backends are roughly equivalent |
| **Confidence-weighted** | Each backend's vote is weighted by confidence | Production: when backends have different reliability profiles |
| **Cascade** | Backend A first; fall through to B/C/D if confidence is low | Production: when one backend is fast + cheap + usually sufficient |

The canonical ensemble dispatcher is in
`agents/meaisinfhoghlaim/ocr/ensemble/`.

## The 3 alignment primitives

| Primitive | Description |
|:--|:--|
| **Cross-frame** | Align OCR output across video frames (the Apple Photos ingestion pipeline) |
| **Cross-archive** | Align OCR output across archive boundaries (the Cognee knowledge graph) |
| **Cross-nation** | Align OCR output across national curriculum variants (the BIEP v3 pipeline) |

The canonical alignment dispatcher is in
`agents/meaisinfhoghlaim/alignment/aligner.py`.

## The 3 educational agents

| Agent | Framework | Purpose |
|:--|:--|:--|
| `academic_history_agent` | ADK | The cross-archive academic history (research paper retrieval + citation extraction) |
| `celtic_grammar_agent` | ADK | The Celtic grammar specialist (Irish + Welsh + Scottish Gaelic + Breton + Cornish + Manx) |
| `celtic_morphology_agent` | ADK | The Celtic morphology specialist (verb conjugation + noun declension + adjective agreement) |

## Quick routing — "I want to add X, where do I go?"

| If you want to... | Look at... |
|:--|:--|
| Add a new OCR backend | `meaisinfhoghlaim/models/registry.py` (add to `CLASSICAL_OCR`) |
| Add a new ensemble pattern | `agents/meaisinfhoghlaim/ocr/ensemble/` |
| Add a new alignment primitive | `agents/meaisinfhoghlaim/alignment/` |
| Modify an educational agent | `agents/meaisinfhoghlaim/educational/<slug>_agent.py` |
| Add OCR/HTR Dagster assets | `orchestration/defs/5_agent_ops/ocr_assets/` |
| Deploy the OCR/HTR pipeline | `meaisinfhoghlaim/cli.py` |

## Cross-references

- [`agents/AGENTS.md`](../AGENTS.md) — the quadrant overview
- [`agents/api/AGENTS.md`](../api/AGENTS.md) — the Hono API layer
- [`agents/tools/AGENTS.md`](../tools/AGENTS.md) — the tools layer
- [`meaisinfhoghlaim/AGENTS.md`](../../meaisinfhoghlaim/AGENTS.md) — the top-level OCR/HTR package