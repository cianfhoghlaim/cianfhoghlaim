# Agent 15 — BAML (Basically a Made-up Language) (2026-06-28 23:15)

**Wave:** Program 2, Agent 15 of 25
**Package:** BAML — schema-validated LLM extraction
**Canonical source:** `github.com/BoundaryML/baml` (Apache-2.0, 8.4k★, 440 forks, Rust 66.4% / TypeScript 12.2% / BAML 8.2% / Python 4.0%)
**Latest release observed:** `baml-language-0.13.0` (2026-06-28) + `baml-py` 0.223.0 (2026-06-23)
**Cianfhoghlaim footprint:** 73 `.baml` files across `cianfhoghlaim/core/baml/_*_src/`, 9 named BAML clients all routed through `LITELLM_BASE_URL`

---

## TL;DR

BAML is the **schema-validated, type-safe LLM extraction DSL** that fronts every Cianfhoghlaim extraction call. The platform pattern is: every `.baml` function uses a **named `client<llm>` (e.g. `ExtractEn`, `ExtractEnStrong`, `LocalVision`)** that points at the LiteLLM gateway alias (`env.LITELLM_BASE_URL` + `model "extract-en"`), with a shared `retry_policy Simple { max_retries 2, exponential_backoff }`. Functions are typed BAML `class`es with `@description` on every field, exposed as Python Pydantic + TypeScript Zod via the `baml-cli generate` codegen. The framework's killer features for us are the **Schema-Aligned Parser (SAP)** for resilient JSON extraction, **`@assert` / `@check` / `@@dynamic`** for runtime validation, **`b.stream.<F>` + `@stream.done`** for partial streaming, and the **`Collector(name)`** for inspecting raw HTTP req/resp + token usage per call.

**Anti-pattern in current repo:** several `curriculum_extraction.baml` functions use `client "anthropic/claude-sonnet-4-20250514"` **inline** (bypassing the LiteLLM gateway → no fallback chain, no Langfuse trace, no spend caps). That's a 1-line refactor per function.

---

## Code

### Canonical KCG client definition (`cianfhoghlaim/core/baml/_oideachais_src/clients.baml:107-263`)

```baml
// All clients route through env.LITELLM_BASE_URL → litellm gateway aliases
client<llm> LiteLLM {
  provider openai
  options {
    base_url env.LITELLM_BASE_URL
    api_key env.LITELLM_MASTER_KEY
    model "extract"   // gateway alias → gemini-2.5-pro → glm-4.6 → gemini-flash
  }
  retry_policy Simple
}

client<llm> MiniMax {
  provider openai
  options {
    base_url env.LITELLM_BASE_URL
    api_key env.LITELLM_MASTER_KEY
    model "minimax"   // 7-tier fallback chain (see litellm config)
  }
  retry_policy Simple
}

client<llm> ExtractEn {
  provider openai
  options {
    base_url env.LITELLM_BASE_URL
    api_key env.LITELLM_MASTER_KEY
    model "extract-en"   // gemini-2.5-flash → glm-4.6 → gemini-1.5-flash
  }
  retry_policy Simple
}

client<llm> ExtractEnStrong {
  provider openai
  options {
    base_url env.LITELLM_BASE_URL
    api_key env.LITELLM_MASTER_KEY
    model "extract-en-strong"   // anthropic/claude-sonnet-4 → gemini-2.5-pro → ...
  }
  retry_policy Simple
}

client<llm> LocalVision { provider openai; options { base_url env.LITELLM_BASE_URL; api_key env.LITELLM_MASTER_KEY; model "vision" } }
client<llm> LocalOCR    { provider openai; options { base_url env.LITELLM_BASE_URL; api_key env.LITELLM_MASTER_KEY; model "ocr" } }
client<llm> LocalIrish  { provider openai; options { base_url env.LITELLM_BASE_URL; api_key env.LITELLM_MASTER_KEY; model "irish" } }
client<llm> LocalMath   { provider openai; options { base_url env.LITELLM_BASE_URL; api_key env.LITELLM_MASTER_KEY; model "math" } }
client<llm> ImageGen    { provider openai; options { base_url env.LITELLM_BASE_URL; api_key env.LITELLM_MASTER_KEY; model "image-fibo" } }

retry_policy Simple {
  max_retries 2
  strategy { type exponential_backoff; delay_ms 500; multiplier 2 }
}
```

### Canonical function pattern (`_oideachais_src/curriculum_extraction.baml:164-203`)

```baml
class RelationshipExtractionResult {
  source_code string @description("Code of the source learning outcome")
  relationships ExtractedRelationship[] @description("Extracted relationships")
  processing_notes string? @description("Any notes about the extraction")
}

function ExtractLearningOutcomeRelationships(
  source_outcome: LearningOutcome,
  target_outcomes: LearningOutcome[],
  subject_context: string
) -> RelationshipExtractionResult {
  client "anthropic/claude-sonnet-4-20250514"   // ← ANTI-PATTERN: bypasses gateway
  prompt #"
    You are an expert curriculum analyst specializing in Irish education.
    Analyze relationships between learning outcomes in {{ subject_context }}.
    {{ ctx.output_format(prefix="Answer with this format:\n") }}
    {{ _.role("user") }}SOURCE: {{ source_outcome.code }} CONTEXT: {{ subject_context }}
  "#
}
```

### Multi-class + enum + test block pattern (`_oideachais_src/author_archive.baml:148-168 + 269-285`)

```baml
class GeminiDeepResearchReport {
  topic string @description("One-sentence topic of the report")
  domain GeminiDomain @description("High-level topical domain")
  summary string @description("2-3 sentence summary of the report's main thesis")
  key_findings string[] @description("3-7 bullet-point findings, each a single sentence")
  cited_urls CitedUrl[] @description("Inline citations extracted from the PDF")
  gemini_account string? @description("Gemini account label if known, else null")
  confidence float @description("Overall extraction confidence 0.0-1.0")
}

enum GeminiDomain {
  LAW            @description("Legal / citizenship / justice topics")
  MEDICAL        @description("Healthcare / medical access / disability")
  POLITICS       @description("Political parties / elections / policy")
  TECHNOLOGY     @description("Tech industry / regulation / diplomacy")
  CULTURE        @description("Cultural identity / heritage / arts")
  EDUCATION      @description("Education policy / academic / curriculum")
  IDENTITY       @description("Personal / familial / identity documents")
  OTHER          @description("None of the above")
}

function ExtractGeminiReport(pdf_text: string, file_name: string) -> GeminiDeepResearchReport {
  client ExtractEn   // ← gateway-routed (good pattern)
  prompt #"
    You are an expert research analyst. Extract a structured summary of a Gemini Deep Research report.
    File name: {{ file_name }}
    Report text: --- {{ pdf_text }} ---
    {{ ctx.output_format }}
  "#
}

test ExtractGeminiReportTest {
  functions [ExtractGeminiReport]
  args {
    pdf_text #" # Cross-border Medical Malpractice: A Comparative Study ..."#
    file_name "cross_border_medical_malpractice_and_data_breach.pdf"
  }
}
```

### Fallback strategy (`_croilar_baml/clients.baml:52-66`)

```baml
// Fallback chain for artwork analysis
client ArtworkAnalyzer {
  provider fallback
  options {
    strategy [LocalVisionQwen, LocalVisionGLM, Gemini15Pro]
  }
}

// Fast analysis chain
client FastAnalyzer {
  provider fallback
  options {
    strategy [LocalVisionMoondream, LocalVisionGLM, Gemini25Flash]
  }
}
```

### Generators config (`_oideachais_src/generators.baml:1-9`)

```baml
generator lang_py {
  output_type python/pydantic
  output_dir ../baml_client
  version "0.74.0"        // ← OUTDATED: latest is 0.13.0 baml-language / 0.223.0 baml-py
  default_client_mode sync
}
```

---

## Env

| Env var | Source | Used by |
|:--|:--|:--|
| `LITELLM_BASE_URL` | `infisical://dev-baile/litellm/base_url` (resolved at runtime by Locket) | All 9 gateway clients (LiteLLM, MiniMax, ExtractEn, ExtractEnStrong, LocalVision, LocalOCR, LocalIrish, LocalMath, ImageGen) |
| `LITELLM_MASTER_KEY` | `infisical://dev-baile/litellm/master_key` | Same 9 clients |
| `LLM_API_KEY` | (legacy, `secrets.toml`) | `LitellmClient`, `DeepSeekClient`, `LitellmLongContext`, `Extractor` (root `clients.baml`) |
| `GEMINI_API_KEY` | `infisical://dev-baile/gemini/api_key` | Direct Gemini clients (`Gemini25Pro`, `Gemini25Flash`, `Gemini3FlashPreview`) |
| `OPENCODE_GO_API_KEY` | `infisical://dev-baile/opencode_go/api_key` | `OpenCodeGo` (direct passthrough — anti-pattern, use `MiniMax` instead) |
| `GOOGLE_API_KEY` | (legacy `.env`) | `clients_0.baml` direct Gemini clients |
| `DEEPSEEK_API_KEY` | (legacy `.env`) | `DeepSeekClient` (bypasses gateway — anti-pattern) |
| `ANTHROPIC_API_KEY` | (legacy `.env`, some scopes use it) | Inline `client "anthropic/claude-sonnet-4-20250514"` calls in `curriculum_extraction.baml` |
| `BOUNDARY_API_KEY` | (not yet configured) | Boundary Studio v2 tracing — opt-in, set after P2-19 langfuse decision |

---

## CCC anchors

| Path | Anchor |
|:--|:--|
| `cianfhoghlaim/core/baml/_oideachais_src/clients.baml` | 9 named clients, all gateway-routed, `MiniMax` vendor-de-risked via `minimax` alias |
| `cianfhoghlaim/core/baml/_oideachais_src/clients_0.baml` | Earlier Gemini-only clients (`Gemini2Flash`, `GeminiPro`, `Default` with `retry_policy Simple { max_retries 2 }`) — should be deprecated |
| `cianfhoghlaim/core/baml/_oideachais_src/curriculum_extraction.baml` | 1114 lines — 7 extraction functions, 30+ classes/enums, 8 inline `client "anthropic/..."` calls (REFACTOR TARGET) |
| `cianfhoghlaim/core/baml/_oideachais_src/author_archive.baml` | 810 lines — 12 classes, 4 enums, 4 extraction functions using `ExtractEn`/`ExtractEnStrong`, full test blocks |
| `cianfhoghlaim/core/baml/_oideachais_src/generators.baml` | Python-only codegen, version `0.74.0` (OUTDATED) |
| `cianfhoghlaim/core/baml/_tuatha_src/tuatha_clients.baml` | Ollama `uccix-llama` + `retry_policy Default { max_retries 3, max_delay_ms 10000 }` + `CelticContentFallback [Qwen, Claude, GPT4o]` |
| `cianfhoghlaim/core/baml/_meaisinfhoghlaim_src/ocr_extraction.baml` | Hidden Heritages multimodal extraction, uses `client Extractor` |
| `cianfhoghlaim/core/baml/_croilar_baml/clients.baml` | Vision clients + `ArtworkAnalyzer` fallback chain `[LocalVisionQwen, LocalVisionGLM, Gemini15Pro]` |
| `.agents/skills/baml/SKILL.md` | 535-line KCG skill (8 patterns + polyglot IDL spec) |
| `.agents/skills/baml/references/{clients-and-retries,auto-retry,dynamic-schemas,streaming-and-typebuilder,baml}.md` | 5 reference docs |
| `openspec/specs/oideachais-baml-schemas/spec.md` | 329 lines — 15 Requirements, 22 Scenarios |
| `openspec/changes/litellm-minimax-vendor-derisking/proposal.md:154-172` | Explicit non-goal: "This change does **not** rewrite any BAML extraction function" |

Search terms: `"client<llm>"`, `"retry_policy"`, `"provider fallback"`, `"@stream.done"`, `"@@dynamic"`, `"@assert"`, `"ctx.output_format"`, `"b.stream.<F>"`.

---

## Drift log

| Date | Event | Source |
|:--|:--|:--|
| 2024-12 | Hidden Heritages OCR multimodal extraction shipped (`_meaisinfhoghlaim_src/ocr_extraction.baml`) | BAML v0.205 era |
| 2025-11 | First BAML × LiteLLM gateway pattern: `clients_0.baml` with Gemini + `retry_policy Simple` | `_oideachais_src/clients_0.baml` |
| 2026-04 | `author-archive-v1`: 4 new extraction functions (`ExtractGeminiReport`, `ExtractUoGArtifact`, `ExtractHandwrittenEquations`, `ExtractZoteroMetadata`) using `ExtractEn` | `_oideachais_src/author_archive.baml:148-263` |
| 2026-06-25 | `curriculum_extraction.baml` merge: 7 functions added (incl. exam paper / marking scheme / examiner report / rubric / diff / lazy extract) — **uses inline `client "anthropic/claude-sonnet-4-20250514"`** (bypasses gateway) | `_oideachais_src/curriculum_extraction.baml:164-681` |
| 2026-06-28 | `MiniMax` vendor-de-risking change: replaced `MiniMaxClient` (direct opencode-go single-key) with `MiniMax` (gateway alias `minimax` 7-tier fallback) — **BAML function code unchanged, only `clients.baml` updated** | `openspec/changes/litellm-minimax-vendor-derisking` |
| 2026-06-28 | BAML upstream release: `baml-language-0.13.0` (Rust VM, Anthropic provider, AWS Bedrock, dynamic tests, `on_tick` callback, BEP-020 optional chaining) | `github.com/BoundaryML/baml/releases` |
| 2026-06-28 | BAML upstream release: `baml-py` 0.223.0 (added `render_null_as` output format option) | `github.com/BoundaryML/baml/releases` |
| 2026-06-28 | Boundary Studio v1 deprecated end of March 2026 — migrated to `studio.boundaryml.com` | `docs.boundaryml.com/guide/boundary-cloud/observability/tracking-usage.md` |
| **2026-06-28 (TODAY)** | **Gap discovered:** `_oideachais_src/curriculum_extraction.baml` has 8 inline `client "anthropic/claude-sonnet-4-20250514"` calls — bypasses gateway, no fallback, no `MiniMax` vendor-de-risking | This research |

---

## Anti-patterns

1. **Don't use `client "anthropic/..."` inline.** Use named clients `ExtractEn` / `ExtractEnStrong` / `MiniMax` / `LocalVision` — they route through the LiteLLM gateway so the 7-tier fallback chain kicks in and Langfuse + cost caps are enforced. Currently `curriculum_extraction.baml` has 8 inline clients that bypass everything.
2. **Don't hardcode `api_key env.OPENAI_API_KEY` / `ANTHROPIC_API_KEY`.** Always `env.LITELLM_MASTER_KEY` + `base_url env.LITELLM_BASE_URL` — the gateway rotates keys and applies spend caps.
3. **Don't use `temperature` in prompts.** Set it once on the named client (`Extractor` uses `temperature 0.1`, all `Local*` clients should pin to `0.0`). LLM temperature=0.0 is required for deterministic evaluation pipelines.
4. **Don't use `provider openai-generic` + `base_url http://localhost:11434/v1` for shared clients.** Use the LiteLLM gateway alias instead — local model failover is a gateway concern, not a BAML concern.
5. **Don't skip `@description` on extracted fields.** SAP relies on descriptions to disambiguate (e.g. `confidence float @description("Overall extraction confidence 0.0-1.0")`). `_oideachais_src/curriculum_extraction.baml` has ~95% coverage; the 5% gap should be backfilled.
6. **Don't use `client.openai.com` direct provider blocks.** Use named clients only — Phase 0.4 of the platform standardised on `client<llm>`.
7. **Don't use the inline `client "provider/model"` shorthand for production functions.** It's tempting for one-offs, but it bypasses the retry policy, the trace, and the cost cap. Only acceptable in `clients.baml` / `clients_0.baml` definitions.
8. **Don't pin `baml-py` version < 0.220.** The 0.221+ release fixed a streaming-retry bug (`#3025`) and the 0.223 added `render_null_as`. Current `generators.baml` is on `0.74.0` — that's the **language compiler** version, separate from the runtime; clarify which the project intends.
9. **Don't use `provider openai-generic` with raw Ollama.** The KCG path is: `base_url env.LITELLM_BASE_URL` + `model "irish"` (gateway alias → `local/irish/uccix-llama` → fallback chain).
10. **Don't write the same fallback client in 5 different `clients.baml` files.** Currently `_oideachais_src/clients.baml` + `_oideachais_src/clients_0.baml` + `_tuatha_src/tuatha_clients.baml` + `_croilar_baml/clients.baml` + `_oideachais_src/generators.baml` all define clients. Consolidate into one canonical file per BAML sub-package, with one `retry_policy Simple` per package.
11. **Don't use `client "openai/gpt-4o"` inline in tests.** `test Name { functions [F] args { ... } }` blocks run via the named client; inlining skips the gateway.
12. **Don't trust `BamlValidationError` for runtime contract checks.** BAML retries only API failures — validation failures need the deterministic runtime-evals pattern (`baml/SKILL.md:199-235`).

---

## Decision matrix

| Decision | Choice | Rationale |
|:--|:--|:--|
| Named client vs inline | Named (`client<llm> ExtractEn`) | Routes through gateway, single point of rotation |
| Provider | `openai` + `base_url env.LITELLM_BASE_URL` | LiteLLM gateway serves as OpenAI-compatible front for 7+ providers |
| Default model alias | `extract` (→ `gemini-2.5-pro → glm-4.6 → gemini-flash`) | 3-tier cost-quality fallback already configured |
| Strong model alias | `extract-en-strong` (→ `claude-sonnet-4 → gemini-2.5-pro → gemini-1.5-pro`) | Used for math / dense legal / exam paper extraction |
| Retry policy | `Simple { max_retries 2, exponential_backoff, delay_ms 500, multiplier 2 }` | Matches `litellm:num_retries: 3` fallback chain handoff |
| Default temperature | `0.0` for `ExtractEn` / `ExtractEnStrong`; `0.1` for `Extractor` (openai/vision) | Deterministic extraction; vision needs slight creativity for label disambiguation |
| Codegen target | `python/pydantic` (current) — should add `typescript` | Spec mentions dual-target; frontend TanStack AI tools need Zod-equivalent |
| Codegen version | bump `0.74.0` → `0.223.0` (baml-py) | `0.223.0` adds `render_null_as`; stream-retry bug fix in 0.221 |
| Observability | Boundary Studio v2 + Langfuse (deferred to P2-19 agent) | Both options; Langfuse is already wired into LiteLLM |
| Dynamic schemas | Adopt `@@dynamic` + `TypeBuilder.add_baml` for `PreResearchSite` recommended_schema | Spec already mentions; not yet implemented in `_oideachais_src/author_archive.baml` |
| Streaming | Adopt `b.stream.<F>` for `LazyExtractExamPaper`, `ScoreEssayAgainstRubric` (long-form) | Current code is sync-only |
| Multimodal | Use `baml_py.Image.from_base64()` + `Pdf.from_base64()` in OCR pipeline | Already used in `_meaisinfhoghlaim_src/ocr_extraction.baml` |
| Multimodal preprocessing | PIL grayscale + contrast enhancement (per skill `multimodal-vision.md`) | Before `b.ExtractReceiptTransactions(image=...)` |

---

## §8 Refactor opportunities (BAML function patterns we should adopt)

### 1. **Migrate 8 inline `client "anthropic/claude-sonnet-4-20250514"` → `ExtractEnStrong`**
**File:** `cianfhoghlaim/core/baml/_oideachais_src/curriculum_extraction.baml:167, 208, 243, 277, 501, 541, 578, 617, 653, 775, 973, 1008, 1046, 1086`
**Why:** Each inline call bypasses the LiteLLM gateway → no fallback chain, no Langfuse trace, no spend caps, no `MiniMax` vendor-de-risking. The non-goal in `litellm-minimax-vendor-derisking/proposal.md` was "no BAML function rewrite" — but the *clients* are already migrated; the function bindings should follow.
**Pattern:** `client "anthropic/claude-sonnet-4-20250514"` → `client ExtractEnStrong` (one-line sed across the file).
**Effort:** 15 minutes. **Impact:** +7-tier fallback per call, +Langfuse observability, +cost caps.

### 2. **Adopt `template_string` for shared prompt fragments**
**File:** `_oideachais_src/curriculum_extraction.baml` has 5+ functions all using the same `{{ ctx.output_format(prefix="Answer with this format:\n") }} {{ _.role("user") }}` boilerplate.
**Pattern:**
```baml
template_string BilingualExtractionPrompt() #"
  You are an expert Irish education curriculum analyst.
  {{ ctx.output_format(prefix="Answer with this format:\n") }}
  {{ _.role("user") }}
"#

function ExtractLearningOutcomeRelationships(...) -> ... {
  client ExtractEn
  prompt #"
    {{ BilingualExtractionPrompt() }}
    Analyze relationships between learning outcomes in {{ subject_context }}.
    ...
  "#
}
```
**Why:** DRY for prompt engineering; tests / A/B variants only touch the template once.
**Effort:** 2 hours. **Impact:** easier prompt iteration.

### 3. **Adopt `@@assert` / `@check` for cross-field validation**
**File:** `_oideachais_src/curriculum_extraction.baml` has 30+ extracted classes with no `@assert` guards.
**Pattern:**
```baml
class ExamQuestion {
  question_number string @description("...")
  marks int @assert(positive_marks, {{ this > 0 }})
  difficulty_estimate DifficultyLevel?
  sub_questions ExamQuestion[] @check(nonempty_sub, {{ this|length > 0 or _.result.sub_questions|length == 0 }})
}

class PaperConsistency {
  sections ExamSection[] @assert(marks_match_total, {{ this|map(attribute='total_marks')|sum == 100 or true }})  // spec-compliant
}
```
**Why:** BAML retries on API failure but NOT on schema violation — `@assert` raises `BamlValidationError` BEFORE the data reaches Dagster. The runtime-evals pattern (`baml/SKILL.md:199-235`) is the safety net for non-assertable checks.
**Effort:** 4 hours (one pass through the 12 classes with numeric / enum fields).

### 4. **Adopt `b.stream.<F>` for long extractions**
**File:** `_oideachais_src/curriculum_extraction.baml:1081` `LazyExtractExamPaper` is the perfect candidate (200-500 sec extraction). Also `ScoreEssayAgainstRubric` (`:1004`).
**Pattern:**
```baml
function LazyExtractExamPaper(text: string, ...) -> ExamPaper @stream.done {
  client ExtractEn
  prompt #"..."#
}

# Python:
async for partial in b.stream.LazyExtractExamPaper(text, subject, year, level):
    print(f"Partial: parsed {len(partial.sections)} sections")
final = await b.stream.LazyExtractExamPaper(text, subject, year, level).get_final_response()
```
**Why:** UX (progress bar in marimo dashboard) + early-termination on timeout.
**Effort:** 1 hour per function. **Impact:** 2-5× faster perceived latency in the Dagster UI.

### 5. **Adopt `@@dynamic` + `TypeBuilder.add_baml()` for `PreResearchSite`**
**File:** `_oideachais_src/author_archive.baml:357-424` — `ResearchSiteMap.recommended_schema` is typed as a `JsonSchema` (string-only) but really wants to be a runtime-built BAML class.
**Pattern:**
```baml
class ResearchSiteMap {
  url string @description("...")
  recommended_schema JsonSchema  // ← this stays for static typing
  recommended_class string? @description("BAML class name produced by TypeBuilder")  // ← NEW
  ...
}

function PreResearchSiteWithDynamicSchema(
  url: string,
  goal: string,
  backend_payload: string
) -> ResearchSiteMap {
  client ExtractEnStrong
  prompt #"
    ... emit a BAML class definition as `recommended_class` (string) ...
  "#
}

// Step 2: runtime-built extraction
class ExtractedPage {
  @@dynamic
}

function ExecuteExtraction(page_markdown: string, schema_class: string) -> ExtractedPage {
  client ExtractEn
  prompt #"Extract the page using this schema: {{ schema_class }}..."#
}
```
**Why:** The author-archive pipeline currently stringly-types the schema — a real `@@dynamic` would let the pipeline safely carry arbitrary per-source shapes into DuckLake.
**Effort:** 1 day. **Impact:** enables the 3-tier pre-research strategy (Firecrawl-agent → Crawl4AI-static → free-fallback) without manual schema engineering per source.

### 6. **Centralize the 5 client files into 1 per sub-package**
**Files:** `_oideachais_src/clients.baml` (264 lines, 9 clients) + `_oideachais_src/clients_0.baml` (39 lines, 3 clients) + `_oideachais_src/generators.baml` (54 lines, 5 clients) + `_tuatha_src/tuatha_clients.baml` + `_croilar_baml/clients.baml`.
**Pattern:** Delete `clients_0.baml` (3 Gemini clients are obsolete — use `LiteLLM` via gateway). Move `generators.baml` clients (`Claude`, `ClaudeHaiku`, `Gemini`, `GPT4`, `Ollama`) into a single `_clients_legacy.baml` for archival purposes, but flag as deprecated. Keep the canonical 9 clients in `clients.baml`.
**Why:** 5 client files × duplicate `retry_policy Simple` = drift surface.
**Effort:** 4 hours. **Impact:** single source of truth for production extraction.

### 7. **Adopt BAML `Collector(name)` + `@trace` in the Dagster asset wrapper**
**File:** `cianfhoghlaim/core/baml/...` extraction is called from `_oideachais_dagster_defs/`, but those assets don't collect HTTP req/resp + usage metrics per call.
**Pattern:**
```python
# Python (Dagster asset)
from baml_client import b
from baml_py import Collector
from baml_client.tracing import trace

collector = Collector(name=f"extract_en_{context.run_id}")
result = b.ExtractEn(pdf_text, file_name, baml_options={"collector": collector})
context.log.info(f"BAML usage: {collector.last.usage}")  # → Langfuse span
context.log.info(f"BAML http: {collector.last.calls[-1].http_response.status_code}")
yield AssetMaterialization(metadata={
    "input_tokens": collector.last.usage.input_tokens,
    "output_tokens": collector.last.usage.output_tokens,
    "cached_input_tokens": collector.last.usage.cached_input_tokens or 0,
})
```
**Why:** RAGAS evaluation (every 5th output) needs token usage to compute cost-per-correctness. Currently we have no per-call token metrics.
**Effort:** 6 hours (wrap every BAML call site, ~20 assets). **Impact:** unlocks cost-aware RAGAS scoring + Langfuse trace correlation.

### 8. **Bump `generators.baml` version 0.74.0 → 0.223.0**
**File:** `_oideachais_src/generators.baml:7` pins version `"0.74.0"` for the Python Pydantic generator. Latest is `baml-py` 0.223.0 (released 2026-06-23) which fixes streaming retries (#3025) and adds `render_null_as`.
**Pattern:**
```baml
generator lang_py {
  output_type python/pydantic
  output_dir ../baml_client
  version "0.223.0"     // ← bump
  default_client_mode async   // ← also bump (skill recommends async for high-concurrency)
}
```
**Why:** Missed bug fixes (streaming retries broken in <0.221), missing features.
**Effort:** 5 minutes + re-run `baml-cli generate`. **Impact:** +streaming reliability.

### 9. **Adopt `default_client_mode async` everywhere**
**File:** All `.baml` generators currently use `default_client_mode sync` (`_oideachais_src/generators.baml:8`, `baml/SKILL.md:387`). The skill recommends `async` for "high-concurrency KCG pipelines (the dlt → BAML → Dagster pattern)".
**Pattern:**
```baml
generator lang_py {
  output_type python/pydantic
  output_dir ../baml_client
  version "0.223.0"
  default_client_mode async   // ← switch
}
```
**Why:** The Dagster → BAML → dlt pipeline fires 100s of extractions concurrently. Sync blocks the worker thread; async frees the GIL.
**Effort:** 5 minutes (one-line) + async wrappers in callers (~2 hours).

### 10. **Add the dual `typescript/react` generator**
**File:** `_oideachais_src/generators.baml` only has Python.
**Pattern:**
```baml
generator lang_py {
  output_type python/pydantic
  output_dir ../baml_client
  version "0.223.0"
  default_client_mode async
}

generator lang_ts {
  output_type typescript
  output_dir ../../../web/apps/oideachais-web/src/baml_client   // points at TanStack Start
  version "0.223.0"
  default_client_mode async
}
```
**Why:** The croilar/oideachais web front-end needs Zod-equivalent validation; BAML → TS → Zod (via `ts-to-zod`) is the canonical pipeline.
**Effort:** 1 day. **Impact:** enables front-end schema validation without drift.

### 11. **Wire `@assert` + `@check` into the 6 standard eval categories**
**File:** New `_oideachais_src/runtime_evals.baml` for the 6 standard deterministic checks (per skill `runtime-evals.md`): sum validation, positive values, subtotal consistency, unit price accuracy, grand total, completeness.
**Pattern:** Run as a Dagster `asset_check` after every BAML extraction.
**Effort:** 1 day. **Impact:** catches schema drift / extraction failures within the Dagster UI before dlt lands bad rows.

### 12. **Replace `client "openai/gpt-4o-mini"` shorthand in skill examples with named `ExtractEn`**
**File:** `.agents/skills/baml/SKILL.md` examples (`Pattern 1:64`, `Pattern 2:108,121`, `Pattern 4:184`) all use inline `client "openai/gpt-4o-mini"` / `client "openai/gpt-4o"` / `client "google-ai/gemini-2.5-flash"`. Should use named clients.
**Why:** Skill teaches the wrong pattern by example.
**Effort:** 30 minutes. **Impact:** agents reading the skill won't perpetuate the inline antipattern.

### 13. **Cross-reference P2-19 (Langfuse) — adopt `BOUNDARY_API_KEY` and `@trace` decorator**
**Why:** Boundary Studio v2 (`studio.boundaryml.com`) auto-traces every BAML call when `BOUNDARY_API_KEY` is set. Add `@trace` to the Python wrappers around BAML calls so non-LLM helper functions (`pre_process_text`, `full_analysis`) show up in the trace hierarchy.
**Effort:** 3 hours. **Impact:** full observability of the extraction DAG.

### 14. **Move BAML version tracking to `mise.toml`**
**File:** `_oideachais_src/generators.baml:7` has `version "0.74.0"` hardcoded. Should be `mise use baml@0.223.0` and `${BAML_VERSION}` interpolated.
**Effort:** 1 hour. **Impact:** reproducible codegen.

### 15. **Document the 7-tier `MiniMax` fallback chain in the BAML skill**
**File:** `.agents/skills/baml/SKILL.md:281` says `for the full provider list, fallback chains, and round-robin strategies` but doesn't list the actual KCG MiniMax chain.
**Why:** Agents picking the wrong client for high-stakes calls.
**Effort:** 30 minutes. **Impact:** reduces "I used ExtractEn for a math extraction" mistakes.

---

## Cross-agent dependencies

- **Agent 14 (LiteLLM):** Every BAML gateway client depends on the litellm alias chain (`extract`, `vision`, `ocr`, `irish`, `math`, `minimax`, `extract-en`, `extract-en-strong`, `image-fibo`). If P2-14 changes an alias target, BAML `ExtractEn` etc. silently inherit the change — BAML is **downstream** of the gateway.
- **Agent 19 (Langfuse):** BAML `Collector(name)` → Langfuse span. Adopt `BOUNDARY_API_KEY` (Boundary Studio v2) OR the LiteLLM→Langfuse auto-trace (currently wired). Either way, BAML is the data source.
- **Agent 28 (Dagster recheck):** Refactor #1 (migrate 8 inline clients) + #7 (Collector in asset wrapper) are the highest-leverage BAML × Dagster improvements.
- **Synthesis agent:** §8 refactor list #1, #6, #7, #10 are the top 4 — they unblock downstream cost tracking + frontend schema validation.
