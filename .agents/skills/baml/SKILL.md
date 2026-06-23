# BAML Skill

## Context

Use this when designing extraction schemas for the `meaisínfhoghlaim`
brain. BAML (Basically, A Made-up Language) is the schema-validation
LLM extraction framework used across the oideachais lakehouse.

## Project rules (PRESERVED from the original 9-line skill)

1. **Location rule** — define all prompt engineering and extraction
   boundaries in `.baml` files within `oideachais/baml_src/`. The
   directory contains 23+ BAML files (audio_extraction,
   celtic_linguistics, celtic_sources, cognates, curriculum_extraction,
   education_statistics, grammar_patterns, isles_education,
   leaving_cert_*_extraction, morphology, multi_nation_curriculum,
   named_entities, ocr_extraction, ocr_validation, oideachas,
   portfolio_extraction, site_analysis, …). The auto-generated
   client lives in `baml_client/`.
2. **Constraint rule** — use BAML to enforce Zod-like constraints on
   the LLM output, preventing parser crashes downstream in the
   Dagster / DLT pipelines.
3. **Mapping rule** — ensure the extraction schemas map directly to
   the `DuckLake` tables defined in `oideachais/dlt_sources/ireland/`.

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
// oideachais/baml_src/curriculum_extraction.baml
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
from baml_client import b
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
from baml_client import b
from baml_client.type_builder import TypeBuilder

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
from baml_client import b

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
in-repo `oideachais/baml_src/ocr_extraction.baml` uses this).

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
from baml_client import b

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
// baml_src/clients.baml
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
from baml_client import b
from baml_client.type_builder import TypeBuilder

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

## Cross-references

- [`baml_src/`](../../../baml_src/) — the 23+ BAML files
- [`baml_client/`](../../../baml_client/) — the auto-generated client
- [`baml_src/README.md`](../../../baml_src/README.md) — the BAML file map
- [`.agents/skills/cocoindex/SKILL.md`](../cocoindex/SKILL.md) — how
  to use BAML inside a CocoIndex v1 App
- [`.agents/skills/dlt/SKILL.md`](../dlt/SKILL.md) — the type-safe
  BAML → dlt pipeline pattern
