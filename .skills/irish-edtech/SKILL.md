---
name: irish-edtech
description: Expert assistance for Irish educational technology platform development. Use when users need bilingual curriculum systems, Leaving Cert content processing, BAML schemas for education, or Irish language integration with TanStack/Cloudflare stack.
---

# Irish EdTech Platform Architecture

Comprehensive guide for building bilingual educational platforms for Irish curriculum.

## Overview

The Irish education system presents a tripartite data landscape:

| Source | Domain | Content |
|--------|--------|---------|
| **NCCA** (curriculumonline.ie) | Pedagogical Intent | Specifications, Learning Outcomes |
| **SEC** (examinations.ie) | Evidentiary Truth | Exam Papers, Marking Schemes |
| **Dept of Education** | Temporal Governance | Circulars, Policy Amendments |

## When to Use This Skill

Activate when users need:

- "Build a Leaving Cert study platform"
- "Process Irish curriculum documents"
- "Create bilingual educational content"
- "Extract exam questions with BAML"
- "Build knowledge graphs for education"

## Pan-Celtic Education Context

| Jurisdiction | Celtic Enrollment | Growth | Teacher Crisis |
|--------------|-------------------|--------|----------------|
| Wales | 93,377 (21%) | Stable | Critical |
| N. Ireland | 7,414 (IME) | Fast (+50%/decade) | Critical |
| Scotland | 5,066 (GME) | Growing | Severe |
| R. Ireland | 66,318 (8% primary) | Stable | Severe (43% vacancies) |
| Isle of Man | ~69 | Stable | Moderate |

## Core Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| Document Ingestion | ColPali, DeepSeek-OCR, Granite-Docling | Multi-modal extraction |
| Knowledge Base | FalkorDB + Qdrant | Hybrid vector/graph |
| Temporal Reasoning | Graphiti | Bi-temporal data model |
| ETL Orchestration | CocoIndex | High-velocity pipelines |
| Structured Extraction | BAML | Type-safe LLM outputs |
| RAG Retrieval | BGE-M3 + ColPali | Dense + sparse + visual |
| Generation | Qwen2.5-Math-7B | Bilingual math reasoning |
| Frontend | TanStack Start + Cloudflare | Edge-native rendering |
| Interactive Compute | Marimo WASM | Browser-based Python |

## Curriculum Hierarchy Model

```
Subject (e.g., Mathematics)
├── Cycle (Junior/Senior)
│   ├── Strand (e.g., Algebra, Number)
│   │   ├── Topic (e.g., Equations)
│   │   │   └── Learning Outcome (atomic unit)
│   │   └── Assessment Items
│   │       ├── Exam Questions
│   │       └── Marking Schemes (Scales 10A-D)
│   └── Unifying Strands (transverse links)
└── Competency Links (Key Competencies)
```

## Assessment Models by Subject

| Subject | Ontology | Edge Types | Data Modality |
|---------|----------|------------|---------------|
| Mathematics | Derivation Tree | :PREREQUISITE, :ASSESSES | Text + Symbolic |
| Sciences | Taxonomy & System | :FLOWS_TO, :INTERACTS | Text + Diagram |
| Humanities | Causal & Spatial | :CAUSED, :LOCATED_AT | Text + Map |
| Languages | Thematic Web | :EXPLORES, :TRANSLATES | Text + Audio |
| Business | Transaction Graph | :DEBITS, :CREDITS | Text + Table |

## Data Architecture

### Core Ontology

```turtle
@prefix edu: <http://www.irish-edtech.ie/ontology#>.

edu:CurriculumSpecification rdfs:subClassOf edu:EducationalNode.
edu:LearningOutcome rdfs:subClassOf edu:EducationalNode.
edu:AssessmentInstrument rdfs:subClassOf edu:EducationalNode.
edu:PolicyDirective rdfs:subClassOf edu:EducationalNode.
```

### Bi-Temporal Model (Graphiti)

```cypher
// Syllabus versioning
(:Topic {name: "Matrices"}) -[:PART_OF {
  valid_at: "1990-01-01",
  invalid_at: "2015-01-01"
}]-> (:Curriculum {name: "Leaving Cert"})

// Student mastery with decay
(:Student) -[:HAS_MASTERY {
  valid_at: "2024-03-15",
  confidence: 0.85
}]-> (:Topic {name: "Complex Numbers"})
```

### Bilingual Data Strategy

```json
{
  "concept_id": "PYTHAG_THEOREM",
  "name_en": "Theorem of Pythagoras",
  "name_ga": "Teoirim Pythagoras",
  "definition_en": "The square of the hypotenuse...",
  "definition_ga": "An chearnog ar an taobhagan..."
}
```

### Dialect Handling

```cypher
(:Word {lemma: "Look"}) -[:HAS_FORM]-> (:Form {text: "Feach", dialect: "Standard"})
(:Word {lemma: "Look"}) -[:HAS_FORM]-> (:Form {text: "Amharc", dialect: "Ulster"})
```

## Frontend Architecture

### Edge-Native Philosophy

| Layer | Traditional | Proposed |
|-------|-------------|----------|
| Frontend | React (Node.js) | TanStack Start (Edge) |
| Compute | VMs | Cloudflare Workers |
| State | Redis | Durable Objects |
| Runtime (Light) | MicroVMs | Marimo WebAssembly |
| Runtime (Heavy) | MicroVMs | Self-Hosted Coder |

### Bilingual Routing

```
/en/calculus/derivatives
/ga/calcalas/diorthaigh
```

- Middleware inspects `Accept-Language` header
- KV store for glossary (`"Integer" -> "Slanuimhir"`)

### Visualization Stack

| Subject | Technology |
|---------|------------|
| Mathematics | MathBox.js, Mafs |
| Geography | DuckDB WASM + Deck.gl |
| Chemistry | 3Dmol.js, R3F |
| English | D3.js, Compromise.js |
| History | Timeline.js |

## BAML Schema Specifications

### Senior Cycle Marking Schemes

```baml
class MarkingPoint {
  correct_answer: string
  marks_awarded: int
  valid_alternatives: string[]
  mandatory_keywords: string[]
}

class QuestionPartSchema {
  part_id: string @description("e.g., '(b)(ii)'")
  total_marks: int
  marking_points: MarkingPoint[]
  penalties: PenaltyRule[]
}

function ExtractMarkingScheme(text: string) -> QuestionPartSchema[] {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"
    Analyze the Marking Scheme segment.
    Extract logic for awarding marks.

    CRITICAL: Identify 'Penalties' and 'Deductions'.
    Look for alternatives separated by '/'.

    {{ text }}
    {{ ctx.output_format }}
  "#
}
```

### Policy Circulars

```baml
enum CircularStatus {
  NewPolicy
  Amendment
  Repeal
  Clarification
}

class CircularMetadata {
  circular_id: string @description("e.g., '0003/2018'")
  title: string
  issue_date: string
  effective_date: string
  status: CircularStatus
  linked_circulars: LinkedCircular[]
}

function ExtractCircularMeta(text: string) -> CircularMetadata {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"
    1. Extract ID and Dates.
    2. Find 'Supersedes' or 'Rescinds' text.
    3. Identify Domain (Staffing? Assessment?)

    {{ text }}
    {{ ctx.output_format }}
  "#
}
```

## AI/ML Pipeline

### Document Processing Flow

```
PDF Sources → Language Detection → Content Routing
├── Text/Equations → DeepSeek-OCR → LaTeX
├── Diagrams → ColPali → Visual embeddings
└── Tables → Granite-Docling → Structured
         ↓
BAML Structured Extraction → Metadata + JSON
```

### Model Selection

| Tool | LaTeX | Tables | Irish |
|------|-------|--------|-------|
| DeepSeek-OCR | 95% | Very Good | Unconfirmed |
| Qwen2.5-VL | Very Good | Excellent | Likely |
| Granite-Docling | Good | Excellent | Experimental |

### Irish Language Integration

**Challenge:** Irish is <0.1% of web content with ~20% performance gap.

**Solution Stack:**
1. **UCCIX-Llama2-13B-Instruct**: +12% over LLaMA 2-70B on Irish
2. **GaBERT**: Irish-specific BERT embeddings
3. **Qwen2.5-Math**: Native multilingual support

### Training Data Format

```json
{
  "conversations": [
    {
      "role": "user",
      "content": "Leaving Certificate Higher Level:\nDifferentiate f(x) = (3x^2+2)/(x-1). (25 marks)"
    },
    {
      "role": "assistant",
      "content": "<think>Apply quotient rule...</think>\n\n**Step 1: Apply Quotient Rule** (5 marks)\n$$f'(x) = ...$$"
    }
  ]
}
```

**Dataset Mix:** 60-70% LC problems + 20-30% general math

## Subject Implementations

### Mathematics

```cypher
(:Topic {name: "Quadratic Equations"})
  -[:PREREQUISITE]->
(:Topic {name: "Factoring"})
  -[:PREREQUISITE]->
(:Topic {name: "Operations on Integers"})
```

**Scale 10C Marking:**
- 10 marks: Correct answer with full work
- 9-8 marks: Minor slip, correct method
- 7-5 marks: Partial solution
- 4-0 marks: Incorrect approach

### Irish Audio Pipeline

```
Student Audio Recording
    ↓
Whisper (Irish dialect: Connacht, Munster, Ulster)
    ↓
Transcription Analysis:
  - Fluency (pauses, speech rate)
  - Vocabulary (Saibhreas)
  - Grammar (Tuiseal Ginideach)
    ↓
Timestamped Error Feedback
```

## Implementation Phases

| Phase | Weeks | Subjects |
|-------|-------|----------|
| 1 | 1-4 | Mathematics, English, Irish |
| 2 | 5-10 | Physics, Chemistry, Biology |
| 3 | 11-16 | History, Geography |
| 4 | 17-24 | Business, Languages, Applied |

## Cost Profile

| Component | MVP | Production |
|-----------|-----|------------|
| Cloudflare | $5-20 | $50-100 |
| Modal compute | $100-200 | $500-1000 |
| Qdrant Cloud | $25 | $100 |
| API calls (BAML) | $50-100 | $200-500 |
| **Total** | ~$200-350 | ~$900-1750 |

## Decision Framework

| Decision | Recommendation | Rationale |
|----------|----------------|-----------|
| Base model | Qwen2.5-Math-7B | Native Irish, math-optimized |
| Fine-tuning | Unsloth + LoRA | 70% VRAM reduction |
| Vector DB | Qdrant | Multi-vector ColPali |
| Graph DB | FalkorDB | Vector + Cypher |
| Frontend | TanStack Start | Type-safe, edge-rendered |
| WASM Compute | Marimo | Zero-cost browser Python |

## Resources

- **NCCA Curriculum:** https://curriculumonline.ie
- **SEC Exams:** https://examinations.ie
- **UCCIX Demo:** https://aine.chat
- **GaBERT:** https://huggingface.co/DCU-NLP/bert-base-irish-cased-v1
- **TanStack Start:** https://tanstack.com/start
- **Marimo:** https://marimo.io
