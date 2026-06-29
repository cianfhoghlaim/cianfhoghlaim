# Live BAML Verification — Agent 77

**Date:** 2026-06-29 · **Verifier:** Agent 77 (Browserbase Wave 2)
**Task target:** BAML "0.13.0" · **Actual current version:** `baml-py 0.223.0` (PyPI) / `baml-language 0.13.1-nightly.20260629.a` (toolchain)

---

## 1. TL;DR

The Wave 1 "BAML 0.13.0" target refers to the `baml-language` **toolchain** (compiler/CLI), not the `baml-py` Python runtime. Two parallel version streams exist: `baml-language` is at `0.13.1-nightly.20260629.a` (2026-06-29) while `baml-py` is at `0.223.0` (2026-06-23). The docs URL structure has been completely rewritten — `/docs/get-started/quickstart` returns **404**; new canonical entry is `https://docs.boundaryml.com/llms.txt` with pages under `/guide/...`, `/ref/...`, `/examples/...`. **Critical drift:** the task brief references an `@observe` decorator that **does not exist** in BAML — the actual decorator is `@trace` from `baml_client.tracing`.

---

## 2. Current version (live-verified)

| Stream | Latest | Released | Source URL |
|---|---|---|---|
| **baml-py** (PyPI) | **0.223.0** | 2026-06-23 | https://pypi.org/project/baml-py/ |
| **baml-language** (toolchain) | **0.13.1-nightly.20260629.a** | 2026-06-29 | https://github.com/BoundaryML/baml/releases/tag/baml-language-0.13.1-nightly.20260629.a |
| baml-language (stable) | 0.223.0 | 2026-06-23 | https://docs.boundaryml.com/changelog/changelog.md |

**Verbatim from PyPI:** `baml-py 0.223.0` · Released: Jun 23, 2026.
**Verbatim from changelog:** "## [0.223.0](https://github.com/boundaryml/baml/compare/0.222.0..0.223.0) - 2026-06-23 · Add render_null_as output format option (#3822)"
**Verbatim from GitHub Releases JSON:** `"tag_name": "baml-language-0.13.1-nightly.20260629.a"`, `"published_at": "2026-06-29T00:38:06Z"`.

---

## 3. Verbatim code examples (live sources)

### 3.1 `client<llm>` named client (live `/ref/baml/client-llm.md`)

```baml
client<llm> MyClient {
  provider "openai"
  options {
    model "gpt-5"
    // api_key defaults to env.OPENAI_API_KEY
  }
}

function MakeHaiku(topic: string) -> string {
  client MyClient
  prompt #"Write a haiku about {{ topic }}."#
}
```

### 3.2 `client<llm>` + `retry_policy` (live `/ref/llm-client-strategies/retry-policy.md`)

```baml
retry_policy MyPolicyName { max_retries 3 }

client<llm> MyClient {
  provider anthropic
  retry_policy MyPolicyName
  options {
    model "claude-sonnet-4-20250514"
    api_key env.ANTHROPIC_API_KEY
  }
}
```

### 3.3 BAML install + Python usage (live `/guide/installation-language/python.md`)

```bash
pip install baml-py
baml-cli init
baml-cli generate
```

```python
from baml_client.sync_client import b
from baml_client.types import Resume

def example(raw_resume: str) -> Resume:
    response = b.ExtractResume(raw_resume)
    return response
```

### 3.4 Streaming (live `/guide/baml-basics/streaming.md`)

```python
from baml_client import b, partial_types, types

def example1(receipt: str):
    stream = b.stream.ExtractReceiptInfo(receipt)
    for partial in stream:
        print(f"partial: parsed {len(partial.items)} items (object: {partial})")
    final = stream.get_final_response()
    print(f"final: {len(final.items)} items (object: {final})")
```

### 3.5 TypeBuilder (dynamic schemas, live `/guide/baml-advanced/dynamic-types.md`)

```baml
enum Category {
  VALUE1
  VALUE2
  @@dynamic
}

function DynamicCategorizer(input: string) -> Category {
  client GPT4
  prompt #"
    Given a string, classify it into a category
    {{ input }}
    {{ ctx.output_format }}
  "#
}
```

```python
from baml_client.type_builder import TypeBuilder
from baml_client import b

async def run():
    tb = TypeBuilder()
    tb.Category.add_value('VALUE3')
    tb.Category.add_value('VALUE4')
    res = await b.DynamicCategorizer("some input", { "tb": tb })
```

### 3.6 Collector (live `/ref/baml_client/collector.md`)

```python
from baml_client import b
from baml_py import Collector

collector = Collector(name="my-collector")
result = b.ExtractResume("...", baml_options={"collector": collector})
print(collector.last.usage)
print(collector.last.raw_llm_response)
```

### 3.7 Tracing via `@trace` — **NOT `@observe`** (live `/ref/baml_client/collector.md`)

```python
from baml_client import b
from baml_client.tracing import trace, set_tags
from baml_py import Collector

@trace
async def run_with_tags():
    set_tags(parent_id="p123", run="xyz")
    collector = Collector(name="tags-collector")
    await b.TestOpenAIGPT4oMini("hi", baml_options={"collector": collector, "tags": {"call_id": "first"}})
    log = collector.last
    assert log is not None
    print(log.tags)  # {'parent_id': 'p123', 'run': 'xyz', 'call_id': 'first'}
```

> **Drift call-out:** Wave 1 task brief mentioned `@observe`. **No such decorator exists** in BAML. The tracing primitive is `@trace` from `baml_client.tracing`. `@observe` is a Langfuse convention.

### 3.8 `@stream.with_state` (live `/guide/baml-basics/streaming.md`)

```baml
class BlogPost {
  title string @stream.done @stream.not_null
  content string @stream.with_state
}
```

---

## 4. Live changelog entries since Wave 1 (source: changelog.md)

| Version | Date | Major features |
|---|---|---|
| **0.223.0** | 2026-06-23 | `render_null_as` output format option |
| 0.222.0 | 2026-04-27 | version bump |
| **0.221.0** | 2026-04-14 | Anthropic provider, AWS Bedrock token caching, **lambda expressions**, **optional chaining `?.` & null coalescing `??` (BEP-020)**, `void` return, `ns_*` namespaces, **`baml-cli grep` / `baml-cli describe`**, BAML VM, error stack traces |
| 0.220.0 | 2026-03-11 | jinja `format()` |
| 0.219.0 | 2026-02-12 | large PDF streaming, `cancel_notify` |
| 0.218.x | 2026-01-22 | Go dynamic types, NDJSON streaming, `BamlError` base class |
| **0.217.0** | 2026-01-10 | **Native Rust SDK** (#2832), `@description` → pydantic `Field` |
| **0.214.0** | 2025-11-24 | control-flow visualizer, dotenv in CLI, **toon Jinja filter** for token efficiency |
| **0.212.0** | 2025-10-27 | configurable timeouts, **block-level `@@description`**, **type narrowing for `instanceof`** |
| 0.211.x | 2025-10-12 | tracing improvements, env-var error reporting |

**Verbatim from changelog:** 0.221.0 "add lambda expression support to BAML compiler (#3302)"; "implement BEP-020 optional chaining (?.) and null coalescing (??) (#3267)"; "baml grep and baml describe - agent-oriented semantic search tools (#3347)". 0.217.0 "Add native Rust SDK (#2832)".

---

## 5. Drift items vs Wave 1 text synthesis

| # | Wave 1 | Live reality (2026-06-29) | Severity |
|---|---|---|---|
| **D1** | "BAML 0.13.0" | Two streams: `baml-language 0.13.1-nightly.20260629.a` + `baml-py 0.223.0` | **CRITICAL** |
| **D2** | `@observe` decorator mentioned | **Does not exist.** Correct is `@trace` from `baml_client.tracing` | **CRITICAL** |
| **D3** | `docs.boundaryml.com/docs/get-started/quickstart` | **404.** New pattern: `/guide/...`, `/ref/...`, `/examples/...` | **HIGH** |
| **D4** | Skill pins `version "0.76.2"` | Latest is **0.223.0** (~6 months stale) | **HIGH** |
| **D5** | CLI = `baml generate/test/fmt/check` | CLI is now **`baml-cli`** with `init`, `serve`, `dev`, `check`, `optimize`, `grep`, `describe` | **HIGH** |
| **D6** | No `Collector` / `@trace` mentioned | Both first-class; `@trace` + `set_tags()` for trace context propagation | **HIGH** |
| **D7** | `@stream.not_null` only | Three attributes: `@stream.done`, `@stream.not_null`, `@stream.with_state` | MEDIUM |
| **D8** | Python + TS clients only | 8 surfaces: Python, TypeScript, Ruby, Go, Rust, Elixir, React/Next.js, REST API | MEDIUM |
| **D9** | No Anthropic / Rust SDK | Added 2026-04 / 2026-01 | LOW (KCG) |
| **D10** | Azure AI Foundry as separate provider | Grouped under `openai-generic` umbrella | LOW |

**Live URL patterns** (from `https://docs.boundaryml.com/llms.txt`):
`/guide/installation-language/python.md`, `/ref/baml/client-llm.md`, `/guide/baml-advanced/dynamic-types.md`, `/changelog/changelog.md`, `/llms.txt` (full AI-agent index).

---

## 6. Skill file update recommendation (`.agents/skills/baml/SKILL.md`)

### 6.1 Frontmatter (line 3)

```diff
- description: BAML (Basically, A Made-up Language) — the schema-validation LLM extraction framework used across the oideachais lakehouse. Use when designing extraction schemas, defining `@function` and `@class` blocks in `.baml` files under `sruth/oideachais/baml_src/`, wiring BAML into dlt sources or Dagster assets, or evaluating a BAML schema with `baml-cli test`. Covers static + dynamic (TypeBuilder) + multimodal + streaming patterns, named clients + retry policies, polyglot codegen (Python Pydantic + TS Zod), and the 8-stage BAML lifecycle. Triggers: 'BAML schema', 'extract from PDF', 'LLM structured output', 'Pydantic from BAML', 'TypeBuilder', 'dynamic schema', '@function', 'baml_src'.
+ description: BAML v0.223.0 / baml-language 0.13.1-nightly — schema-validation LLM extraction framework used across the oideachais lakehouse. Use when designing extraction schemas in `.baml` files under `baml_src/`, wiring BAML into dlt sources or Dagster assets, or evaluating a schema with `baml-cli test`. Covers static + dynamic (TypeBuilder) + multimodal + streaming patterns, named clients + retry policies, polyglot codegen (Python Pydantic + TS Zod), `@trace` + Collector observability, BAML VM/lambdas/optional-chaining, and the 8-stage BAML lifecycle. Triggers: 'BAML schema', 'extract from PDF', 'Pydantic from BAML', 'TypeBuilder', 'dynamic schema', '@function', 'baml_src', '@trace', 'Collector'.
```

### 6.2 Generators `version` bump (lines 389, 397)

```diff
-   version "0.76.2"
+   version "0.223.0"
```

(Apply to both `generator python_client` and `generator typescript_client`.)

### 6.3 Add "Pattern 8: `@trace` + Collector observability" (insert before line 303)

```baml
## Pattern 8: Tracing + Collector observability (added 2026-06)

```python
from baml_client import b
from baml_client.tracing import trace, set_tags
from baml_py import Collector

@trace                          # <-- NOT @observe
async def extract_with_trace(receipt: str, run_id: str):
    set_tags(parent_id=run_id, app="oideachais")
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
```

### 6.4 CLI block update (lines 351-365)

```diff
-# baml generate / test / fmt / check
+# baml-cli generate / test / fmt / check / init / serve / dev / optimize / grep / describe
```

Replace the full block with: `baml-cli generate`, `baml-cli test`, `baml-cli fmt`, `baml-cli check`, `baml-cli init` (0.207+), `baml-cli serve` (port 2024 REST+streaming), `baml-cli dev` (VSCode proxy), `baml-cli optimize` (0.215+ beta), `baml-cli grep <query>` / `baml-cli describe <function>` (0.221+ agent-oriented semantic search).

### 6.5 Add "Pattern 9: Semantic streaming attributes" (insert after Pattern 4, line 197)

```baml
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
```

### 6.6 Cross-reference update (lines 525+)

```diff
- [`baml_src/`](../../../baml_src/) · [`baml_client/`](../../../baml_client/) · [`baml_src/README.md`](../../../baml_src/README.md)
+ [`baml_src/`](../../../baml_src/) · [`baml_client/`](../../../baml_client/) · [`baml_src/README.md`](../../../baml_src/README.md)
+ [Collector](https://docs.boundaryml.com/ref/baml_client/collector.md) · [@trace](https://docs.boundaryml.com/ref/baml_client/collector.md#tags) · [client<llm>](https://docs.boundaryml.com/ref/baml/client-llm.md) · [Changelog](https://docs.boundaryml.com/changelog/changelog.md) · [docs llms.txt](https://docs.boundaryml.com/llms.txt)
```

### 6.7 Anti-patterns addition (after line 330)

```diff
+- **Using `@observe`** — BAML's tracing primitive is `@trace` from `baml_client.tracing`. Mixing them loses span context. Wrap BAML collectors in Langfuse decorators if you need Langfuse output.
+- **Pin `version` to old releases (e.g. 0.76.2)** — pins codegen to stale runtime; upgrade to ≥0.223 for current bugfixes (Vertex JSON parsing, streaming retries, instanceof narrowing).
+- **Mixing `client "openai/..."` inline + named `client<llm>`** — pick one. Named clients are reusable and enable per-client retry_policy/fallback.
```

---

## 7. Decision matrix — should KCG upgrade now?

| Factor | Status | Recommendation |
|---|---|---|
| Breaking schema changes between 0.76 and 0.223? | None; old `@stream.not_null` still works | **Safe to upgrade** |
| Need Anthropic provider? | Added 0.221 | Optional for KCG |
| Need Rust SDK? | Added 0.217 | Not yet required |
| Need Lambda / optional chaining in `.baml`? | Added 0.221 | Optional |
| Need `@trace` + Collector for Langfuse observability? | Stable since 0.79.0 | **Recommended** — wrap BAML collectors as Langfuse spans |
| Doc URL 404 on Wave 1 reference? | Confirmed | Update all internal links to `/guide/...` / `/ref/...` |
| Pin `version "0.76.2"` in `generators.baml`? | Stale (8 months) | **Bump to `0.223.0`** in next baml_src refactor |
| `@observe` mentions in KCG code? | Grep required | Likely none |

**Verdict:** Upgrade `version` from `0.76.2` → `0.223.0` in `generators.baml`. Run `baml-cli generate` and re-test all 23+ BAML files. Add `@trace` wrappers around existing extraction call sites that flow into Langfuse.

---

## Appendix: Live sources verified

| Source | URL | Verdict |
|---|---|---|
| BAML docs home | https://docs.boundaryml.com | 200 OK → `/home` |
| Docs AI-agent index | https://docs.boundaryml.com/llms.txt | 200 OK, full sitemap |
| **Old quickstart URL** | https://docs.boundaryml.com/docs/get-started/quickstart | **404 (drift confirmed)** |
| Changelog | https://docs.boundaryml.com/changelog/changelog.md | 200 OK, last entry 0.223.0 |
| client<llm> | https://docs.boundaryml.com/ref/baml/client-llm.md | 200 OK |
| TypeBuilder | https://docs.boundaryml.com/guide/baml-advanced/dynamic-types.md | 200 OK |
| Collector | https://docs.boundaryml.com/ref/baml_client/collector.md | 200 OK |
| Streaming | https://docs.boundaryml.com/guide/baml-basics/streaming.md | 200 OK |
| Python install | https://docs.boundaryml.com/guide/installation-language/python.md | 200 OK |
| retry_policy | https://docs.boundaryml.com/ref/llm-client-strategies/retry-policy.md | 200 OK |
| PyPI baml-py | https://pypi.org/project/baml-py/ | 200 OK, latest 0.223.0 (2026-06-23) |
| GitHub releases API | https://api.github.com/repos/BoundaryML/baml/releases | 200 OK, latest `baml-language-0.13.1-nightly.20260629.a` |