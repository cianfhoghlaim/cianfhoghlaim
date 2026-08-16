# `cocoindex/biep_parity/` — The 4-stage CocoIndex v1 BIEP factories

> **The canonical CocoIndex v1 source for the 4-stage BIEP App matrix.**
> Per the 2026-08-13-web-monorepo-consolidation-and-agent-integration-v1
> change (Phase 6).

## The 4-stage CocoIndex App matrix

| Stage | Subjects | Boards | Apps | Factory |
|:--|:--|:--|--:|:--|
| LC | 14 | — | 11 | `ireland_lc_factory.py` (existing) |
| JC | 8 | — | 16 | `4_stage_factory.py` (Phase 6) |
| GCSE | 9 × 3 = 27 | 3 | 27 | `england_priority_factory.py` (Phase 6) |
| A-Level | 15 × 3 = 45 | 3 | 45 | `england_priority_factory.py` (Phase 6) |
| **TOTAL** | **46 unique subjects** | — | **99 Cocoa Apps** | — |

## The canonical BAML → CocoIndex → Web pipeline

```
BAML .baml files (Phase 4)
        ↓
OCR/VLM 4-path ensemble (Phase 5)
        ↓
DLT sources (Phase 5)
        ↓
CocoIndex v1 Apps (Phase 6 — this file)
        ↓
CocoIndex codegen pipeline (Phase 7)
        ↓
Per-subject agents (Phase 8)
        ↓
Per-subject notebooks (Phase 9)
        ↓
Central Cianfhoghlaim homepage (Phase 10)
```

## The factory files

### `ireland_lc_factory.py` (existing, 176 LOC)

The 6 NCCA LC subjects (Mathematics, Chemistry, Geography, Gaeilge,
English, Computer Science) — 11 CocoIndex Apps (6 subjects × 2 langs
minus 1 for Gaeilge which is ga-only).

### `4_stage_factory.py` (NEW, 350 LOC)

The canonical 4-stage BIEP CocoIndex factory:
- 14 LC subjects (the canonical Ireland LC priority list)
- 8 JC subjects (the canonical Ireland JC priority list)
- 9 GCSE priority subjects × 3 boards (27 apps)
- 15 A-Level priority subjects × 3 boards (45 apps)
- Total: 99 CocoIndex Apps

### `england_priority_factory.py` (NEW, 240 LOC)

The 9 GCSE + 15 A-Level priority subjects across 3 boards (AQA + OCR
+ Edexcel) — 72 CocoIndex Apps.

## The 4-stage DLT registry (Phase 5)

The CocoIndex factories consume the canonical 4-stage DLT source
registry at `dlt_sources/british_isles/_cross/biep_4_stage_registry.py`:
- 4 DLT sources (`ireland_lc_extractions`, `ireland_jc_extractions`,
  `england_gcse_extractions`, `england_a_level_extractions`)
- 60-subject coverage matrix
- BIEP_BAML_FUNCTIONS map (the canonical per-subject → BAML extraction)

## The 4-stage BAML surface (Phase 4)

The CocoIndex factories consume the canonical 4-stage BAML files:
- `baml_src/british_isles/ireland/education/lc_extraction/curriculum_syllabus.baml`
- `baml_src/british_isles/ireland/education/jc_extraction/canonical_jc_per_subject.baml`
- `baml_src/british_isles/england/education/gcse_extraction/canonical_gcse_per_subject.baml`
- `baml_src/british_isles/england/education/a_level_extraction/canonical_a_level_per_subject.baml`

## Coding conventions

Every CocoIndex App conforms to R1–R4:
- **R1**: imports `shared_lifespan` from `.._shared._lifespan`
- **R2**: no new `ContextKey[` (uses only the 3 shared ones)
- **R3**: `app = coco.App(coco.AppConfig(name=...))` at module scope
- **R4**: at least one `@coco.fn(` decorator

## DO NOT

- **Never** hand-write a Pydantic model that duplicates a BAML class — codegen it from `.baml`
- **Never** create a per-subject CocoIndex file outside the factory pattern — extend the factory
- **Never** import `from cocoindex.*` directly in web app code — always go through the cocoindex_app instance

## Skill pointers

| Skill | When to load |
|:--|:--|
| [`cocoindex`](../../.agents/skills/cocoindex/SKILL.md) | The canonical v1 App pattern + R1–R4 conformance |
| [`lancedb`](../../.agents/skills/lancedb/SKILL.md) | The HNSW vector store |
| [`baml`](../../.agents/skills/baml/SKILL.md) | The BAML extraction framework |
| [`schema-codegen`](../../.agents/skills/schema-codegen/SKILL.md) | The BAML → Zod → Convex → CopilotKit pipeline |
| [`centralized-registry`](../../.agents/skills/centralized-registry/SKILL.md) | MODEL_REGISTRY |

<!-- generated: 2026-08-13 (per the 2026-08-13-web-monorepo-consolidation-and-agent-integration-v1 change, Phase 6) -->
