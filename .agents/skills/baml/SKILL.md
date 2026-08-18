---
name: baml
description: BAML v0.223.0 / baml-language 0.13.1-nightly — schema-validation LLM extraction framework used across the oideachais lakehouse. Use when designing extraction schemas in `.baml` files under `baml_src/`, wiring BAML into dlt sources or Dagster assets, or evaluating a schema with `baml-cli test`. Covers the 5 canonical lc6 extraction functions (ExtractCurriculumSyllabus / ExtractExamPaperLayout / ExtractMarkingSchemeGuideline / ExtractCrossLinguisticConcept / ExtractSyllabusDiagram) + static + dynamic (TypeBuilder) + multimodal + streaming patterns, named clients + retry policies, polyglot codegen (Python Pydantic + TS Zod), `@trace` + Collector observability, BAML VM/lambdas/optional-chaining, and the 8-stage BAML lifecycle. Triggers: 'BAML schema', 'extract from PDF', 'Pydantic from BAML', 'TypeBuilder', 'dynamic schema', '@function', 'baml_src', '@trace', 'Collector', 'lc6', 'lc_extraction'.
---

# BAML Skill

## Context

Use this when designing extraction schemas for the `meaisínfhoghlaim`
brain. BAML (Basically, A Made-up Language) is the schema-validation
LLM extraction framework used across the oideachais lakehouse.

## Project rules (PRESERVED from the original 9-line skill)

1. **Location rule** — define all prompt engineering and extraction
   boundaries in `.baml` files within `baml/`
   (the `baml_src/` symlink points here post-v4). The directory
   contains 23+ BAML files (audio_extraction, celtic_linguistics,
   celtic_sources, cognates, curriculum_extraction,
   education_statistics, grammar_patterns, isles_education,
   leaving_cert_*_extraction, morphology, multi_nation_curriculum,
   named_entities, ocr_extraction, ocr_validation, oideachas,
   portfolio_extraction, site_analysis, …). The auto-generated
   client lives in `baml_client/baml_client/`.
2. **Constraint rule** — use BAML to enforce Zod-like constraints on
   the LLM output, preventing parser crashes downstream in the
   Dagster / DLT pipelines.
3. **Mapping rule** — ensure the extraction schemas map directly to
   the `DuckLake` tables defined in
   `dlt/british_isles/ireland/education/`.

## v7 flattening migration notes (added 2026-07-19)

Per openspec/changes/2026-07-14-fix-foundation-v7-flattening-and-baml-drift-v1:

- The `.baml` source files now live at `baml_src/` (NOT `baml/`)
- The auto-generated Python client lives at `baml_client/baml_client/`
  (with an extra `baml_client/` wrapper due to the post-flatten wheel layout)
- The canonical import path for BAML functions is:
  `from cianfhoghlaim.baml_client import b`
- The `_legacy/` sub-directory contains deprecated BAML files that
  are kept for one release cycle per openspec deprecation policy
- BAML 0.223.0 (NOT 0.222) is the canonical compiler; key differences:
  - Test blocks MUST use lowercase `test` (was PascalCase `Test` in 0.222)
  - String-literal dotted-path type refs like `"baml_src.X.Y.Z"` are REJECTED
  - Class field defaults like `field string = "en"` are REJECTED
  - Use `from ..shared.file import ClassName` for cross-file imports

For new BAML functions in the v7 flattened layout, see:
openspec/specs/oideachais-baml-schemas/spec.md (canonical BAML spec)

## When to use this skill

Use when you need to:

- "Design a new BAML extraction schema for source X"
- "Run a BAML extraction on a document / image / PDF / audio"
- "Add deterministic runtime evals to a BAML extraction"
- "Auto-retry on extraction failure"
- "Stream partial extraction results"
- "Define a BAML client + retry policy"
- "Generate code from a `.baml` file"
- "Use BAML inside a CocoIndex v1 App"
- "Use BAML multimodal (vision / audio / pdf) extraction"

## Pattern 1: Static extraction (the existing pattern)

```baml
// baml/education/curriculum_extraction.baml
class PrimaryLearningOutcome {
  stage string
  curriculum_area string
  learning_outcome string
  @@description #"
    A single learning outcome from the NCCA Primary curriculum.
    The `stage` is one of: junior_infants, senior_infants,
    first_class, second_class, third_class, fourth_class,
    fifth_class, sixth_class.
  "#
}

function ExtractPrimaryLearningOutcomes(
  document_text: string
) -> PrimaryLearningOutcome[] {
  client "openai/gpt-4o-mini"
  prompt #"
    Extract all primary learning outcomes from the following
    NCCA Primary curriculum document:

    {{ document_text }}

    {{ ctx.output_format }}
  "#
}

test primary_extraction {
  functions [ExtractPrimaryLearningOutcomes]
  args {
    document_text <<<
      "Children should be able to count to 10..."
    >>>
  }
}
```

Run `baml generate` to regenerate the Python client. Then:

```python
from cianfhoghlaim.baml_client import b
outcomes = b.ExtractPrimaryLearningOutcomes(document_text)
for o in outcomes:
    print(f"[{o.stage}] {o.curriculum_area}: {o.learning_outcome}")
```

## Pattern 2: Dynamic schema extraction (TypeBuilder + `@@dynamic`)

Use this when the schema is not known at `.baml` authoring time
(e.g. ad-hoc corpus ingestion). Two steps:

```baml
// 1. Generate the schema
class Schema {
  interface_code string
  return_type string
  other_code string?
}

function GenerateBAML(content: string) -> Schema {
  client "openai/gpt-4o"
  prompt #"..."#
}

// 2. Execute against the runtime-built schema
class Response {
  @@dynamic
}

function ExecuteBAML(
  content: string,
  dynamic_class_output: string  // the `return_type` from step 1
) -> Response {
  client "openai/gpt-4o"
  prompt #"..."#
}
```

Python glue:

```python
from cianfhoghlaim.baml_client import b
from cianfhoghlaim.baml_client.type_builder import TypeBuilder

def extract_anything(content: str):
    # Step 1: ask the LLM to describe the schema
    schema = b.GenerateBAML(content)
    # Build a TypeBuilder from the schema
    tb = TypeBuilder()
    tb.add_baml(f"class Response {{ data {schema.return_type} }}")
    # Step 2: execute the extraction
    response = b.ExecuteBAML(content, schema.return_type, baml_options={"tb": tb})
    return response
```

See [`references/dynamic-schemas.md`](references/dynamic-schemas.md)
for the full two-step pattern.

## Pattern 3: Multimodal (vision / audio / pdf) extraction

```baml
function ExtractReceiptTransactions(
  receipt_image: image
) -> ReceiptData {
  client "google-ai/gemini-2.5-flash"
  prompt #"Extract the line-item transactions from this receipt."#
}
```

```python
import baml_py
from cianfhoghlaim.baml_client import b

with open("receipt.png", "rb") as f:
    image = baml_py.Image.from_base64("image/png", base64.b64encode(f.read()).decode())

receipt = b.ExtractReceiptTransactions(receipt_image=image)
```

For PDFs:

```python
pdf = baml_py.Pdf.from_base64(pdf_bytes)
result = b.ExtractDocumentStructure(document=pdf)
```

See [`references/multimodal-vision.md`](references/multimodal-vision.md)
for PIL preprocessing, client config, and the OCR pattern (the
in-repo `baml/ocr_extraction.baml` uses this).

## Pattern 4: Streaming extraction

```baml
function GenerateSummary(content: string) -> string
  @stream.not_null
{
  client "openai/gpt-4o-mini"
  prompt #"Summarize this document in one paragraph."#
}
```

```python
from cianfhoghlaim.baml_client import b

stream = b.stream.GenerateSummary(content)
async for chunk in stream:
    print(chunk, end="", flush=True)
final = await stream.get_final_response()
print(f"\nFinal: {final}")
```

## Pattern 5: Runtime evals + auto-retry

After BAML extraction, run deterministic evals (no LLM-as-judge):

```python
def sum_validation(receipt: ReceiptData) -> EvaluationResult:
    expected = (
        sum(t.total_price for t in receipt.transactions)
        + (receipt.service_charge or 0)
        + (receipt.tax or 0)
        + (receipt.rounding or 0)
        - abs(receipt.discount or 0)
    )
    passed = abs(expected - receipt.grand_total) < 0.01
    return EvaluationResult(
        check="sum_validation",
        passed=passed,
        message=f"expected={expected:.2f}, actual={receipt.grand_total:.2f}",
        expected_value=expected,
        actual_value=receipt.grand_total,
    )

# Run all 6 evals
results = [
    sum_validation(receipt),
    positive_values(receipt),
    subtotal_consistency(receipt),
    unit_price_accuracy(receipt),
    grand_total_calculation(receipt),
    data_completeness(receipt),
]

# Auto-retry on failure (max 1 retry to prevent runaway cost)
if not all(r.passed for r in results):
    receipt = b.ExtractReceiptTransactions(receipt_image=image)  # retry
    results = [eval_fn(receipt) for eval_fn in evals]
```

See [`references/runtime-evals.md`](references/runtime-evals.md) for
the 6 standard checks, and [`references/auto-retry.md`](references/auto-retry.md)
for the retry-loop pattern.

## Pattern 6: Named clients + retry policies

```baml
// baml/clients.baml
client<llm> ExtractEn {
  provider "openai"
  options {
    model "gpt-4o-mini"
    temperature 0.0
  }
  retry_policy Constant {
    max_retries 3
    delay_ms 1000
  }
}

client<llm> ExtractEnStrong {
  provider "openai"
  options {
    model "gpt-4o"
    temperature 0.0
  }
  retry_policy Exponential {
    max_retries 5
    strategy { type exponential_backoff, multiplier 2.0 }
  }
}

client<llm> LocalVision {
  provider "openai-generic"
  options {
    base_url "http://localhost:8000/v1"
    model "dots-ocr"
  }
}
```

See [`references/clients-and-retries.md`](references/clients-and-retries.md)
for the full provider list, fallback chains, and round-robin
strategies.

## Pattern 7: TypeBuilder + streaming (combined)

For dynamic schemas with partial streaming:

```python
import asyncio
from cianfhoghlaim.baml_client import b
from cianfhoghlaim.baml_client.type_builder import TypeBuilder

async def extract_with_streaming(content: str):
    schema = b.GenerateBAML(content)
    tb = TypeBuilder()
    tb.add_baml(f"class Response {{ data {schema.return_type} }}")

    stream = b.stream.ExecuteBAML(content, schema.return_type, {"tb": tb})
    async for chunk in stream:
        yield chunk
    final = await stream.get_final_response()
    yield final
```

## Project conventions

- One `.baml` per source family (e.g. `leaving_cert_past_paper_extraction.baml`
  for SEC past papers, `named_entities.baml` for entity recognition)
- Map every output class to a `dlt_sources/ireland/*` table
- Use `@@description` for every field the LLM might miss
- Ship a `test` block with each extraction function (at least one
  positive case)
- Use `client "<name>"` (not inline `provider`/`model`) so clients
  are reusable across functions
- For multimodal, preprocess images with PIL (grayscale, contrast
  enhancement) before calling BAML — see
  [`references/multimodal-vision.md`](references/multimodal-vision.md)

## Anti-patterns

- **LLM-as-judge evals** — use deterministic math (sum, ratios,
  presence/absence) instead. LLM-as-judge is expensive, non-deterministic,
  and circular.
- **Hardcoding schemas for one-off sources** — use `TypeBuilder` to
  generate the schema at runtime instead.
- **Retries on validation failures** — BAML only retries API failures.
  For validation failures, use the auto-retry-on-eval pattern above.
- **Streaming for high-stakes decisions** — streaming partial results
  may give wrong answers. Use it for UX (showing progress) but always
  validate the final result.
- **Inlining prompts in Python** — keep prompts in `.baml` files so
  they version-control with the schema and can be A/B tested.

## BAML syntax quick reference

| Construct | Purpose | Example |
|:--|:--|:--|
| `class Foo { x string }` | Typed class | `class Product { name string price float }` |
| `class Foo { @@dynamic }` | Runtime-injected fields | `class Response { @@dynamic }` |
| `enum Bar { A B C }` | Enum | `enum Stage { infant junior_cycle senior_cycle }` |
| `function Name(args) -> Ret { client "X" prompt #"..."# }` | Function | `function Extract(pdf: pdf) -> Data { ... }` |
| `client "openai/gpt-4o"` | Inline client | (use a named client instead) |
| `client<llm> Name { provider "openai" options { model "gpt-4o" } }` | Named client | (preferred) |
| `retry_policy Constant { max_retries 3 }` | Retry policy | (apply to a named client) |
| `test name { functions [F] args { x "y" } }` | Test block | (one per extraction function) |
| `@@assert { … }` | Assertion (LLM) | (for properties the LLM should check) |
| `@@check { … }` | Check (deterministic) | (for mathematical properties) |
| `@stream.not_null` | Stream with non-null | (use for partial-result UX) |
| `@stream.done` | Stream with done event | (advanced) |
| `template_string Name() { ... }` | Reusable prompt fragment | (DRY for repeated instructions) |
| `image` / `pdf` / `audio` | Multimodal types | (built-in primitive types) |

## CLI

```bash
# Generate the Python / TS client from your .baml files
baml generate

# Run the test suite
baml test

# Format .baml files
baml fmt

# Check for type errors
baml check
```

## Polyglot IDL (BAML → Python+TS)

When the BAML source has to feed both the **Python data
layer** (Dagster + DLT + Pydantic) **and** the **TypeScript
front-end** (TanStack + oRPC + Zod) from a single `.baml`
file, treat BAML as the master Interface Definition
Language (IDL). The compiler is the seam: one BAML class
becomes a Pydantic model in Python and a TS interface
in the browser.

### Dual-target codegen (`generators.baml`)

Configure two generators so a single `baml-cli generate`
run produces both client libraries:

```baml
// baml/generators.baml

// Generator 1: Python data layer (DLT + Dagster)
generator python_client {
  output_type "python/pydantic"
  output_dir "../backend/baml_client"
  version "0.76.2"
  default_client_mode "async"
}

// Generator 2: TypeScript application layer (TanStack/oRPC)
generator typescript_client {
  output_type "typescript"
  output_dir "../frontend/src/baml_client"
  version "0.76.2"
  default_client_mode "async"
}
```

The BAML `@@description` annotations become Pydantic field
descriptions (used by dlt for schema docs) **and** JSDoc
comments on the TS side. One source of truth, two
synced clients.

### Python side: BAML → Pydantic → dlt Resource

dlt introspects Pydantic models to infer the schema of a
resource. Wire the BAML-generated Pydantic class as the
`columns` contract:

```python
import dlt
from cianfhoghlaim.baml_client import b
from backend.baml_client.types import ResearchInsight

@dlt.source
def research_source(texts: list[str]):
    @dlt.resource(
        name="research_insights",
        write_disposition="merge",
        primary_key="id",
        columns=ResearchInsight,   # Pydantic from BAML
    )
    def extract_insights():
        for text in texts:
            yield b.ExtractInsight(text)   # BAML SAP validates JSON

    return extract_insights
```

If the LLM produces malformed JSON, BAML's **Schema-Aligned
Parsing (SAP)** raises *before* dlt ever sees the row —
fail-fast prevents schema pollution downstream. For nested
fields (`entities IdentifiedEntity[]`), dlt's
normalization engine auto-creates a child table
`research_insights__entities` with FK back to the parent.

### Polyglot persistence (one class → 5 stores)

The same BAML class can fan out to:

| Store | dlt mechanism | KCG use |
|:--|:--|:--|
| **Postgres / DuckDB** | Native dlt destination | `secrets.toml` swap |
| **LanceDB** | `dlt.destinations.adapters.lancedb_adapter(embed=[...])` | Vector search |
| **FalkorDB** | Custom `@dlt.destination` + Cypher `MERGE` | Knowledge graph |
| **Graphiti** | Custom `@dlt.destination` + `client.add_episode()` | Temporal memory |
| **MotherDuck** | DuckDB native dest via `md:` URI | Read-only lakehouse |

For graph stores without a native dlt destination, write
a `@dlt.destination(batch_size=50)` that translates the
BAML Pydantic dict into Cypher (FalkorDB) or JSON episodes
(Graphiti). Use `MERGE` for idempotency aligned with
dlt's retry behaviour.

### TypeScript side: BAML → TS interface → Zod

BAML does not emit Zod directly. Bridge the gap with
`ts-to-zod` so the front-end runtime validator never
drifts from the BAML definition:

```jsonc
// package.json scripts
{
  "generate:baml": "baml-cli generate",
  "generate:zod": "ts-to-zod --input ./src/baml_client/types.ts --output ./src/gen/zod.ts --skipValidation",
  "codegen": "npm run generate:baml && npm run generate:zod"
}
```

The generated `researchInsightSchema` then drives:

- **TanStack AI tools** — `toolDefinition({ inputSchema: researchInsightSchema, ... })`
- **oRPC procedures** — `os.procedure.input(researchInsightSchema)`
- **Drizzle** — store nested BAML objects as `jsonb` columns

### Schema evolution in 4 steps

Add a field once; propagate everywhere.

1. `class ResearchInsight { ...; author string? @description("...") }`
2. `npm run codegen` (regenerates Pydantic + TS + Zod).
3. Next dlt run auto-`ALTER TABLE` on Postgres; the
   `lancedb_adapter` picks up the new field.
4. The TS compiler flags any strict callers; the Zod
   schema gains `.optional()` for old data.

### The 8-stage lifecycle

| # | Stage | Component | Schema state |
|:--|:--|:--|:--|
| 1 | Definition | BAML `.baml` file | Source of truth |
| 2 | Compilation | `baml-cli generate` | Pydantic + TS synced |
| 3 | Bridge | `ts-to-zod` | Zod synced |
| 4 | Ingestion | `b.ExtractInsight(text)` | Validated instance |
| 5 | ETL | dlt → 5 destinations | Persisted |
| 6 | Frontend | TanStack AI tool | — |
| 7 | API | oRPC + Zod | Validated response |
| 8 | UI | React + TS interface | Rendered |

### KCG anti-patterns for polyglot BAML

- **Don't write Zod by hand** — drift is inevitable.
  Always `ts-to-zod` from the BAML-generated TS.
- **Don't inline prompts in Python** — keep them in
  `.baml` so they version-control with the schema.
- **Don't normalise every nested list in Postgres** —
  dlt's child tables are fine for SQL; store as
  `jsonb` only when the query pattern is always
  "load the whole record" (oRPC round-trip).
- **Don't synchronously write to 5 stores from a UI
  request** — push the BAML extraction to a background
  worker (Celery, Temporal, or Dagster asset) and use
  optimistic UI / polling.

See `openspec/changes/lc6-biep/references/baml-adaptive-syllabus.md` and
the full BAML+DLT+TanStack deep dive in
`openspec/changes/lc6-biep/references/baml-irish-education-kg.md`
for the canonical KCG pattern with Restate workflows
and adaptive TypeBuilder schemas.

## Cross-references

- [`baml/`](../../../baml/) — the 23+ BAML files (the `baml_src/` symlink points here)
- [`baml_client/`](../../../baml_client/) — the auto-generated client
- [`baml/README.md`](../../../baml/README.md) — the BAML file map
- [`.agents/skills/cocoindex/SKILL.md`](../cocoindex/SKILL.md) — how
  to use BAML inside a CocoIndex v1 App
- [`.agents/skills/dlt/SKILL.md`](../dlt/SKILL.md) — the type-safe
  BAML → dlt pipeline pattern
- [`.agents/skills/tanstack-start/SKILL.md`](../tanstack-start/SKILL.md) —
  the TanStack AI / oRPC / Zod consumer side
- [`.agents/skills/motherduck/SKILL.md`](../motherduck/SKILL.md) —
  the 4 canonical MotherDuck Dives (`lc_syllabus_topics`,
  `lc_exam_difficulty`, `lc_marking_complexity`,
  `gov_circulars_archive`) that consume the BAML-extracted rows

## Pattern 8: Tracing + Collector observability (added 2026-06)

```python
from cianfhoghlaim.baml_client import b
from baml_client.tracing import trace, set_tags
from baml_py import Collector

@trace                          # <-- NOT @observe
async def extract_with_trace(receipt: str, run_id: str):
    set_tags(parent_id=run_id, app="cianfhoghlaim")
    collector = Collector(name=f"extract-{run_id}")
    result = await b.ExtractReceipt(receipt, baml_options={"collector": collector})
    log = collector.last
    if log:
        print(f"tokens={log.usage.input_tokens}+{log.usage.output_tokens}")
    return result
```

Multi-collector fan-out: `b.ExtractReceipt(receipt, baml_options={"collector": [c1, c2]})`.
For Langfuse: wrap `collector.last.calls[-1].http_request` / `.http_response` (or `.sse_responses()` for streams) into Langfuse spans.

**Wave 1 misnote:** the decorator is `@trace`, not `@observe`. `@observe` is a Langfuse convention — BAML uses `@trace` from `baml_client.tracing`.

## Pattern 9: Semantic streaming attributes (added 0.214+)

```baml
class BlogPost {
  title string @stream.done @stream.not_null
  content string @stream.with_state
}
type OutputItem = ToolCall | Message
function Run(input: string) -> (OutputItem @stream.done)[] {
  client MyClient
  prompt #"{{ input }}\n{{ ctx.output_format }}"#
}
```

`@stream.with_state` generates Python `StreamState[T]` wrappers; check `state == "Complete"` before committing downstream.

## British-Isles Education pipeline (post-v4 canonical pattern)

The post-v4 lc6 pipeline (`openspec/changes/lc6-biep/`) defines
**5 canonical extraction functions** — one per BAML stage —
shared by all 6 LC subjects (Mathematics, Chemistry, Geography,
Gaeilge, English, Computer Science) plus the `gov.ie` circulars
ingester:

```python
from cianfhoghlaim.baml.education.lc_extraction import (
    curriculum_syllabus,       # ExtractCurriculumSyllabus
    exam_paper_layout,         # ExtractExamPaperLayout
    marking_scheme,            # ExtractMarkingSchemeGuideline
    cross_linguistic,          # ExtractCrossLinguisticConcept
    syllabus_diagram,          # ExtractSyllabusDiagram
)
```

Each module exposes the matching BAML `@function`. The
`@function` calls are wired into the `lc5/lc6` Dagster assets
(42 total = 7 subjects × 6 stages) in
`orchestration/defs/2_materials/`. The Pydantic
classes generated by `baml-cli generate` are the canonical
`primary_key` source-of-truth for the matching
`@dlt.resource(write_disposition="merge")` wrappers in
`dlt/british_isles/ireland/education/`.

**British-Isles Education pipeline use case:**

- **6 LC subjects × 2 languages** — Mathematics, Chemistry,
  Geography, Gaeilge, English, Computer Science, each
  partitioned by `language` (`en` / `ga`) so Gaeilge runs in
  parallel with English via the same `@dlt_assets` wrapper.
- **`gov.ie` circulars** — the 7th v1 CocoIndex App
  (`government_circulars`) uses `ExtractCurriculumSyllabus`
  against `gov.ie/.../circulars/...` PDFs to populate
  `cianfhoghlaim.education.ie.gov_circulars_archive` (one of the 4
  MotherDuck Dives).
- **Cross-linguistic concept extraction** —
  `ExtractCrossLinguisticConcept` aligns Gaeilge and English
  terminology (e.g. "matamaitic" ↔ "mathematics") so a single
  RAG query spans both languages.
- **42 lc5/lc6 Dagster assets** — the per-subject BAML extractions
  feed the `2_materials/` asset layer, which fans out to the
  `3_model_lifecycle/` CocoIndex v1 Apps.
- **4 MotherDuck Dives** — `lc_syllabus_topics`,
  `lc_exam_difficulty`, `lc_marking_complexity`,
  `gov_circulars_archive` are the read-only consumer surfaces.
- **6 per-subject marimo notebooks** — each LC subject gets a
   notebook in `notebooks/` that queries its BAML
   rows via `mo.sql(engine="md:cianfhoghlaim")`.
- **7 v1 CocoIndex Apps** — the per-subject embedding pipelines
  consume the BAML-extracted chunks via the canonical
  `mount_table_target` pattern (see the `cocoindex/SKILL.md`).

Cross-references:
- [`.agents/skills/dlt/SKILL.md`](../dlt/SKILL.md) — the
  `from cianfhoghlaim.baml import b` integration pattern
- [`.agents/skills/cocoindex/SKILL.md`](../cocoindex/SKILL.md) —
  the 7 v1 CocoIndex Apps (6 LC subjects + `government_circulars`)
- [`.agents/skills/motherduck/SKILL.md`](../motherduck/SKILL.md) —
  the 4 Dives
- [`.agents/skills/marimo/SKILL.md`](../marimo/SKILL.md) — the 6
  per-subject notebooks
- [`.agents/skills/dagster/SKILL.md`](../dagster/SKILL.md) — the
  42 lc5/lc6 Dagster assets
- [`.agents/skills/change-detection/SKILL.md`](../change-detection/SKILL.md) —
  the NCCA / SEC / `gov.ie` sitemap-hash sensors

---

## ClientRegistry pattern (added 2026-08-17)

Per `https://docs.boundaryml.com/guide/baml-advanced/llm-client-registry`,
the canonical BAML pattern for **per-function primary + fallback
chains** is `ClientRegistry`. Each function declares its own primary
client + ordered fallbacks via `baml_options={"client_registry": ...}`,
and BAML automatically retries through the chain on failure.

This replaces the bare `client "MyClient"` field on `@function` with
explicit fallbacks at the BAML layer (in addition to the LiteLLM
gateway fallbacks).

### Canonical example (chemistry extraction with Irish fallback)

```baml
// 1. Declare the primary + fallback clients
client<llm> ExtractChemPrimary {
  provider "openai-generic"
  options {
    base_url env.LITELLM_BASE_URL
    api_key env.LITELLM_API_KEY
    model "minimax-m3"
  }
}

client<llm> ExtractChemFallback {
  provider "openai-generic"
  options {
    base_url env.DASHSCOPE_BASE_URL
    api_key env.DASHSCOPE_API_KEY
    model "qwen3.7-plus"
  }
}

// 2. Declare the ClientRegistry (in baml_src/clients.baml)
client_registry ExtractChemRegistry {
  name "chemistry_en_extract_registry"
  primary "ExtractChemPrimary"
  fallbacks ["ExtractChemFallback"]
}

// 3. Each function opts in via `client_registry`
function ExtractChemSyllabus(text: string, source_pdf: string) -> ChemSyllabus {
  client_registry ExtractChemRegistry
  prompt #"
    {{ ctx.output_format }}
    Extract from: {{ text }}
  "#
}
```

### Adopted by 6 LC subjects (per `2026-08-17-baml-extraction-completion-v1`)

All 6 LC subject extractors MUST declare a `ClientRegistry`:

| Subject | Primary client | Fallback chain |
|:--|:--|:--|
| Chemistry | `ExtractChemPrimary` (minimax-m3) | `ExtractChemFallback` (qwen3.7-plus) |
| Mathematics | `ExtractMathPrimary` | `ExtractMathFallback` |
| Geography | `ExtractGeoPrimary` | `ExtractGeoFallback` |
| Gaeilge | `ExtractGaeilgePrimary` (uccix-mistral-24b) | `ExtractGaeilgeFallback` (claude-sonnet-4-5) |
| English | `ExtractEnPrimary` | `ExtractEnFallback` |
| Computer Science | `ExtractCompSciPrimary` | `ExtractCompSciFallback` |

The registry name MUST follow the pattern
`<subject>_<language>_<extraction>_registry` (e.g.
`chemistry_en_extract_registry`).

---

## Collector API (added 2026-08-17)

Per `https://docs.boundaryml.com/guide/baml-advanced/collector-track-tokens`,
the BAML `Collector` class exposes per-call observability:
- `collector.last.usage.input_tokens` / `output_tokens` — for the Langfuse billing pipeline
- `collector.last.raw_llm_response` — for the marimo audit notebook's side-by-side provenance display
- `collector.last.calls[-1].http_response` — for the regression alert when a provider silently changes response shape

### Canonical example (BIEP OCR ensemble Path 1)

```python
from baml_py import Collector

collector = Collector(name="biep_ocr_extract_chem")

result = b.ExtractChemSyllabus(
    text=docling_text,
    source_pdf=str(pdf_path),
    baml_options={"collector": collector},
)

# After the call, access observability
print(collector.last.usage.input_tokens)     # → 1234
print(collector.last.raw_llm_response)       # → raw model output
for call in collector.last.calls:
    print(call.http_response)                # → per-call HTTP response
```

### Wired in `meaisinfhoghlaim/ocr/ensemble/ensembled_extractor.py`

The `EnsembledExtractor._run_path_baml()` method (added by
`2026-08-17-hygiene-drift-cleanup-v1` P1.8) wires the Collector and
populates the new observability fields on `EnsemblePathOutput`:

```python
collector = baml_py.Collector(name=f"biep_ocr_{baml_function}")
result = b.ExtractChemSyllabus(
    text=_docling_text,
    source_pdf=str(pdf_path),
    baml_options={"collector": collector},
)
# path_output.usage_input_tokens = collector.last.usage.input_tokens
# path_output.raw_llm_response = collector.last.raw_llm_response
# path_output.http_responses = [str(c.http_response) for c in collector.last.calls]
```

This closes the false-success loop in the OCR ensemble (the MLflow
observability hook only fires when `evaluate_ensemble()` is called
with populated per-path usage + raw_response fields).

[Collector](https://docs.boundaryml.com/ref/baml_client/collector.md) · [@trace](https://docs.boundaryml.com/ref/baml_client/collector.md#tags) · [client<llm>](https://docs.boundaryml.com/ref/baml/client-llm.md) · [Changelog](https://docs.boundaryml.com/changelog/changelog.md) · [docs llms.txt](https://docs.boundaryml.com/llms.txt)
