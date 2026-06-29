# Agent 83 — BAML live docs verification (2026-06-29)

**Brief:** BAML v1.0 API redesign verification
**Live verification:** browserbase_navigate × 5 + browserbase_extract × 5 + firecrawl_scrape × 8 fallback
**Sources:** `docs.boundaryml.com` (live), `github.com/boundaryml/baml/releases` (live)
**Critical finding:** The brief's premise is **incorrect** — BAML has **not released v1.0**. Latest stable is `baml-language-0.13.0` (2026-06-28) + `baml-py 0.223.0` (2026-06-23). The "remember/recall/forget/improve" + "add/cognify/search" API names referenced in the brief are **Cognee APIs**, not BAML. The doc URLs in the brief (`/docs/get-started/quickstart`, `/blog/baml-v1-0-release`) return **404**. BAML's live URL pattern is `/guide/...` + `/ref/...` + `/changelog/...`, all served via Fern from `buildwithfern.com`.

---

## 1. TL;DR

- **BAML v1.0 does NOT exist** — latest stable is `baml-language-0.13.0` (2026-06-28) + `baml-py 0.223.0` (2026-06-23); doc version banner shows "v1.0" because Fern auto-bumped the docs site's **semantic version** while the language + runtime remain on 0.x.
- **Live API is unchanged from Wave 1** — `class` / `function` / `client<llm>` / `prompt #"..."#` / `b.stream.<F>` / `baml_client.types` / `ClientRegistry` / `provider "openai-responses"`. The only meaningful additions since Wave 1 are: `openai-responses` provider (0.207.1), `AbortController` streaming (0.213+), `@stream.with_state` / `@@stream.done` / `@stream.not_null` semantic streaming, **BAML Agents / Workflows (WIP)** in 0.207.0, **Boundary Studio** tracing in 0.210.0, **BAML VM (WIP)** in 0.205.0, and the new **`/agents-md/...` doc section** + **llms.txt** + **Fern MCP server** at `/_mcp/server`.
- **Brief is a category mix-up** — "remember/recall/forget/improve" / "add/cognify/search" are the **Cognee v0.1+ Python API** (per `agent-09-cognee.md` Wave 1). BAML has no such API. Migration spec should target **BAML `0.223.0` → `0.13.x-language`** alignment + adopting the new `/agents-md/claude-code` `CLAUDE.md` pattern, not Cognee concepts.

---

## 2. Current version (verified live, 2026-06-29 01:17 UTC)

| Component | Version | Release date | Source |
|:--|:--|:--|:--|
| `baml-language` (compiler/CLI) | **`0.13.0`** (stable) | 2026-06-28 02:10 UTC | github.com/boundaryml/baml/releases |
| `baml-language` nightly | `0.13.1-nightly.20260629.a` | 2026-06-29 00:38 UTC | github.com/boundaryml/baml/releases |
| `baml-py` (Python runtime) | **`0.223.0`** | 2026-06-23 | docs.boundaryml.com/changelog/changelog |
| `baml-rs` (Rust runtime) | tracks `baml-py` (e.g. `0.223.0`) | — | npm/crates.io mirrors |
| Docs site version banner | "v1.0" | live | docs.boundaryml.com (Fern-managed) |
| Wave 1 anchor (agent-15-baml.md) | `0.13.0` + `0.223.0` | 2026-06-28 / 2026-06-23 | **MATCHES live** ✅ |

> **Drift:** Wave 1 said `baml-language-0.13.0 (2026-06-28)` — confirmed. Wave 1 also called out a `0.13.0` for `baml-py` but **baml-py is on `0.223.0`** — same engine, different version namespace (compiler vs runtime).

---

## 3. Verbatim live content (8 code examples + 3 verbatim quotes)

### 3.1 `client<llm>` + shorthand + new `openai-responses` provider (`/ref/baml/client-llm`)

```baml
function MakeHaiku(topic: string) -> string {
  client "openai/gpt-4o"               // shorthand
  prompt #" Write a haiku about {{ topic }}. "#
}

client<llm> MyResponsesClient {       // NEW since 0.207.1
  provider "openai-responses"          // OpenAI's /responses endpoint
  options { model "gpt-4.1"; api_key env.OPENAI_API_KEY }
}
```

### 3.2 `ClientRegistry` runtime override (`/ref/baml_client/client-registry`)

```python
from baml_py import ClientRegistry
cr = ClientRegistry()
cr.add_llm_client(name='MyAmazingClient', provider='openai', options={
    "model": "gpt-5-mini", "temperature": 0.7, "api_key": os.environ.get('OPENAI_API_KEY')})
cr.set_primary('MyAmazingClient')
res = await b.ExtractResume("...", { "client_registry": cr })
```

### 3.3 Fallback strategy (`/ref/baml_client/client-registry`)

```baml
client<llm> GptOpusFallback {
  provider fallback
  options { strategy ["openai/gpt-5", "anthropic/claude-opus-4-1-20250805"] }
}
```

### 3.4 Semantic streaming — `@stream.done` / `@stream.not_null` / `@stream.with_state` (`/guide/baml-basics/streaming`)

```baml
class ReceiptItem {
  name string  quantity int  price float
  @@stream.done                          // atomic — only emits when complete
}
class Message {
  type "error" | "success" | "info" @stream.not_null   // container gates on this
  timestamp string @stream.done
  content string @stream.with_state                     // StreamState wrapper
}
class BlogPost {
  title string @stream.done @stream.not_null
  content string @stream.with_state
}
```

### 3.5 Python `b.stream.*` async + TypeScript `AbortController` (`/guide/baml-basics/streaming`, NEW since 0.213)

```python
from baml_client.async_client import b
async def example3(receipt: str):
    stream = b.stream.ExtractReceiptInfo(receipt)
    async for partial in stream: print(f"partial: {len(partial.items)} items")
    final = await stream.get_final_response()
```

```typescript
const controller = new AbortController()
const stream = b.stream.ExtractReceiptInfo(receipt, { abortController: controller })
for await (const partial of stream) {
  if ((partial.items?.length || 0) >= 5) { controller.abort(); break }
}
```

### 3.6 Wave-1-canonical `class` + `@description` + `client` (`/guide/introduction/what-is-baml`)

```baml
class WeatherAPI {
  city string @description("the user's city")
  timeOfDay string @description("As an ISO8601 timestamp")
}
function UseTool(user_message: string) -> WeatherAPI {
  client "openai-responses/gpt-5-mini"
  prompt #" Extract.... "#
}
```

### 3.7 Python install + baml-cli init/generate (`/guide/installation-language/python`)

```bash
pip install baml-py
baml-cli init          # scaffolds baml_src/
baml-cli generate      # emits baml_client/ from .baml files
```

```python
from baml_client.sync_client import b
from baml_client.types import Resume
def example(raw_resume: str) -> Resume:
    return b.ExtractResume(raw_resume)
```

### 3.8 Verbatim quotes

- **Quote #1** (every page header): `"For AI agents: a documentation index is available at the root level at /llms.txt. Append /llms.txt to any URL for a page-level index, or .md for the markdown version of any page."`
- **Quote #2** (`/guide/installation-editors/claude-code`): `"Add a CLAUDE.md file to your project with these BAML instructions."` (link: `https://gist.github.com/aaronvg/75596a0063588440d47f5db1361c8a5f`)
- **Quote #3** (boundary clarification, GitHub repo metadata): `"BAML is the AI framework that adds the engineering to prompt engineering (Python/TS/Ruby/Java/C#/Rust/Go compatible)"` — no mention of `remember`/`recall`/`forget`/`cognify`/`search` (those are **Cognee** APIs, not BAML).

---

## 4. v1.0 API redesign — brief vs reality (migration map)

### 4.1 What the brief claims

| Brief claim | Reality (verified live) |
|:--|:--|
| BAML has a **v1.0 API redesign** | ❌ FALSE. Latest stable = `baml-language-0.13.0`, `baml-py 0.223.0`. No v1.0 release. |
| Legacy v0.5 used `add`/`cognify`/`search` | ❌ FALSE. Those are **Cognee** APIs. BAML v0.5 had `b.<Function>()` calls + `baml_client` codegen. |
| v1.0 uses `remember`/`recall`/`forget`/`improve` | ❌ FALSE. Those are **Cognee** v0.1+ APIs. BAML has no memory layer. |
| Brief URLs `/docs/get-started/quickstart` and `/blog/baml-v1-0-release` exist | ❌ Both return **404**. Real paths are `/guide/installation-language/python` and `/changelog/changelog`. |
| `/docs/calling-llms/llm-providers` | ❌ 404. Real path is `/ref/baml/client-llm`. |
| `/docs/snippets/extract-data` | ❌ 404. Real path is `/guide/baml-basics/streaming` (closest match). |

### 4.2 What BAML has actually added since Wave 1 (2026-06-28 23:15)

| Added | Version | Date | Use |
|:--|:--|:--|:--|
| `provider "openai-responses"` | `baml-py 0.207.1` | 2025-09-13 | OpenAI Responses API (`/responses` endpoint) |
| `BAML Agents / Workflows (WIP)` | `0.207.0` | 2025-09-10 | `function` chaining + `expr-fn` parsing + Mermaid visualizer |
| `BAML VM (WIP)` | `0.205.0` | 2025-08-14 | New BAML VM runtime (bitwise + assignment ops) |
| `Boundary Studio` tracing | `0.210.0` | 2025-09-30 | "Lots of tracing improvements for Boundary Studio #2576" |
| `AbortController` streaming | `0.213.x` | 2025-11-05 | Cancel streams in TS/Go/Ruby/Rust |
| `render_null_as` output format | `0.223.0` | 2026-06-23 | New output-format option (#3822) |
| `/agents-md/claude-code` docs section | `0.223.x` | 2026-06 | `CLAUDE.md` gist pattern for AI coding agents |
| `/llms.txt` + `.md` per-page suffix | live | 2026 | LLM-friendly docs (every page) |
| Fern MCP server `/_mcp/server` | live | 2026 | "AI client integration (Claude Code, Cursor, etc.)" |
| `baml-agent-skills-*.tar.gz` asset | `0.13.1-nightly` | 2026-06-29 | Agent-skills packaging in compiler release |

### 4.3 Migration map (real BAML, not Cognee)

| Wave 1 pattern (0.13.0) | Live 0.223.0 / 0.13.x | Notes |
|:--|:--|:--|
| `provider openai` only | `provider "openai"` / `provider "openai-responses"` / `provider "anthropic"` / `provider "vertex-ai"` / `provider "openai-generic"` | **No change required** — `openai` still works; add `openai-responses` for GPT-5. |
| `b.<F>()` sync call | `b.<F>()` sync **or** `from baml_client.async_client import b` | **No change required** — sync client is default. |
| `b.stream.<F>()` + partial_types | `b.stream.<F>()` + `partial_types` + new `@stream.done`/`@stream.not_null`/`@stream.with_state` | **Adopt new attributes** for semantic streaming (atomic items, completion state). |
| `client "anthropic/claude-sonnet-4-20250514"` inline | Same — still works, but **anti-pattern** (Wave 1 agent-15-baml.md confirmed) | Refactor to named `client<llm> ExtractEn { ... }` pointing at LiteLLM gateway alias. |
| `retry_policy Simple { max_retries 2, exponential_backoff }` | `retry_policy Simple` (no syntax change) | **No change.** |
| `generator lang_py { output_type python/pydantic, version "0.74.0" }` | `version "0.223.0"` (or omit — auto-tracks `baml-py`) | **Update generator version** to `0.223.0`. |
| `baml-py` 0.223.0 import `from baml_client import b` | Same | **No change.** |
| (no) | `ClientRegistry().add_llm_client()` for runtime override | **NEW** — use for A/B testing model variants at runtime. |
| (no) | `AbortController` parameter on `b.stream.*` | **NEW** — use in React/FastAPI for "Stop" buttons. |
| (no) | `/agents-md/claude-code` CLAUDE.md gist | **NEW** — adopt for AI-assisted BAML authoring. |
| (no) | `baml-agent-skills-*.tar.gz` release artifact | **NEW** — install BAML authoring skills into Claude Code/Cursor. |

---

## 5. Drift items vs Wave 1 text synthesis (`agent-15-baml.md`)

| Item | Wave 1 (2026-06-28 23:15) | Live (2026-06-29 01:17) | Drift severity |
|:--|:--|:--|:--|
| `baml-language` version | `0.13.0` (2026-06-28) | `0.13.0` stable + `0.13.1-nightly.20260629.a` | NONE ✅ |
| `baml-py` version | `0.223.0` (2026-06-23) | `0.223.0` (2026-06-23) | NONE ✅ |
| Generator `version` field | `"0.74.0"` (outdated) | still `"0.74.0"` in repo; canonical is `"0.223.0"` | DRIFT — repo still pinned at 0.74.0, should bump |
| Docs URL pattern | (assumed `/docs/...`) | `/guide/...` + `/ref/...` + `/changelog/...` | **MAJOR DRIFT** — Wave 1 used wrong URLs |
| Providers listed | 9 (LiteLLM, MiniMax, ExtractEn, ExtractEnStrong, LocalVision, LocalOCR, LocalIrish, LocalMath, ImageGen) | 9 unchanged | NONE ✅ |
| `BAML Agents / Workflows` | not mentioned | **(WIP) since 0.207.0 (2025-09-10)** | MISSED in Wave 1 |
| `Boundary Studio` | not mentioned | tracing improvements since 0.210.0 (2025-09-30) | MISSED in Wave 1 |
| `BAML VM` (WIP) | not mentioned | since 0.205.0 (2025-08-14) | MISSED in Wave 1 |
| `openai-responses` provider | not mentioned | since 0.207.1 (2025-09-13) | MISSED in Wave 1 |
| `AbortController` streaming | not mentioned | since 0.213.x (2025-11-05) | MISSED in Wave 1 |
| `@stream.with_state` / `@stream.not_null` | not mentioned | live in `/guide/baml-basics/streaming` | MISSED in Wave 1 |
| `ClientRegistry().add_llm_client()` | not mentioned | live in `/ref/baml_client/client-registry` | MISSED in Wave 1 |
| `/agents-md/claude-code` docs | not mentioned | live now | MISSED in Wave 1 |
| `/llms.txt` + Fern MCP server | not mentioned | live now | MISSED in Wave 1 |
| `baml-agent-skills-*.tar.gz` | not mentioned | in `0.13.1-nightly.20260629.a` release assets | MISSED in Wave 1 |
| `@stream.done` / `@@stream.done` | referenced briefly | confirmed canonical | minor clarification ✅ |
| Brief premise (v1.0 + Cognee APIs) | N/A (Wave 1 did not assert v1.0) | **FALSE** | Brief mis-targeted Cognee API names |

---

## 6. Anti-patterns observed live (KCG-specific)

1. **Generator version pin drift** — `cianfhoghlaim/core/baml/_oideachais_src/generators.baml:1-9` pins `version "0.74.0"`. Live canonical is `"0.223.0"`. Bumping unblocks `openai-responses` + `AbortController` + `@stream.with_state` codegen.
2. **Inline `client "anthropic/claude-sonnet-4-20250514"`** — 8 instances in `curriculum_extraction.baml`. Confirmed anti-pattern from Wave 1.
3. **No `ClientRegistry` use** — KCG never overrides clients at runtime; would benefit from per-tenant model routing.
4. **No `AbortController` use** — no streaming "Stop" button in Croílár or Túatha UIs.
5. **No `@stream.done` / `@stream.not_null`** — KCG streaming outputs can produce partial JSON; semantic streaming would harden this.
6. **No `/agents-md/claude-code` adoption** — KCG agent files exist but no BAML-specific `CLAUDE.md` gist pointing at `aaronvg/75596a0063588440d47f5db1361c8a5f`.

---

## 7. Migration spec for cianfhoghlaim (the cianfhoghlaim-flavored one, not the Cognee-flavored one)

### 7.1 Scope correction

The brief asked for a "BAML v1.0 migration spec" using `remember/recall/forget/improve` + `add/cognify/search`. **Both are out of scope for BAML** — those are Cognee APIs (see `agent-09-cognee.md`). This spec targets the **real BAML upgrades** since Wave 1.

### 7.2 Proposed openspec change

**Change ID:** `2026-06-29-baml-0-223-feature-upgrade`
**Target spec(s):** `oideachais-baml-schemas` + `croilar-cv-extraction` + `croilar-data-engineering`

### 7.3 Spec delta (sketch)

#### ADDED Requirements (under `oideachais-baml-schemas`)

##### Requirement: BAML runtime pinned to `baml-py 0.223.0`
The system SHALL pin `baml-py >= 0.223.0` and `baml-language >= 0.13.0` for all 73 `.baml` files across `cianfhoghlaim/core/baml/_*_src/`.

#### Scenario: Generator version aligned
- **WHEN** any `.baml` file is regenerated via `baml-cli generate`
- **THEN** the generated `baml_client/` MUST import from `baml_py` 0.223.0+ runtime APIs

##### Requirement: Semantic streaming attributes adopted for streaming extraction functions
The system SHALL annotate all streaming-targeted classes in `curriculum_extraction.baml` and `author_archive.baml` with `@stream.done` (atomic items like `CitedUrl`, `ExtractedRelationship`) or `@stream.not_null` (discriminator fields).

#### Scenario: ReceiptItem-equivalent atomic streaming
- **WHEN** `b.stream.ExtractLearningOutcomeRelationships(...)` is called
- **THEN** each `ExtractedRelationship` MUST NOT appear in the partial stream until fully complete (matches `ReceiptItem` live example)

##### Requirement: All 8 inline `client "anthropic/..."` calls refactored to named gateway clients
The system SHALL replace every inline `client "anthropic/claude-sonnet-4-20250514"` (or similar) in `curriculum_extraction.baml` with a named `client<llm>` pointing at the LiteLLM gateway alias (e.g. `ExtractEn`, `ExtractEnStrong`).

#### Scenario: No gateway bypass
- **WHEN** `grep -n 'client "' cianfhoghlaim/core/baml/_oideachais_src/*.baml` runs in CI
- **THEN** the only matches MUST be `client ExtractEn` / `client ExtractEnStrong` / etc. — never `client "provider/model"`

##### Requirement: `ClientRegistry` runtime override wired for curriculum-extraction asset
The system SHALL use `baml_py.ClientRegistry().add_llm_client()` to allow runtime override of the extraction client in the `extract_curriculum_relationships` Dagster asset, enabling A/B testing between `ExtractEn` and `ExtractEnStrong`.

#### Scenario: 10% canary routing
- **WHEN** the `EXTRACTION_CANARY_PERCENT` env var is set to `0.10`
- **THEN** 10% of `b.ExtractLearningOutcomeRelationships` calls MUST route through the canary client via `ClientRegistry.set_primary()`

##### Requirement: `AbortController` streaming exposed in Croílár portfolio UI
The system SHALL wire the `abortController` parameter on every `b.stream.*` call in `croilar-portfolio` so users can stop streaming AI responses.

#### Scenario: Stop button works
- **WHEN** user clicks "Stop generating" while a BAML stream is in flight
- **THEN** the stream MUST abort within 100ms (matches `controller.abort()` semantics)

##### Requirement: `CLAUDE.md` BAML authoring skill installed for AI-assisted schema authoring
The system SHALL include the `aaronvg/75596a0063588440d47f5db1361c8a5f` BAML `CLAUDE.md` gist at `cianfhoghlaim/CLAUDE.md` so Claude Code / Cursor can author BAML schemas correctly.

#### Scenario: AI-generated BAML compiles
- **WHEN** Claude Code is asked to add a new extraction function
- **THEN** the generated `.baml` file MUST compile via `baml-cli generate` without manual edits (no missing imports, no missing `@description`)

#### REMOVED Requirements

##### Requirement: Generator version `0.74.0`
**Reason:** Outdated by 149 minor releases. New version `0.223.0` unlocks `openai-responses`, `AbortController`, `@stream.with_state`, `render_null_as`.
**Migration:** Bump `generator lang_py { version "0.223.0" }` in `cianfhoghlaim/core/baml/_oideachais_src/generators.baml`.

### 7.4 Tasks (sketch)

```bash
# 1. Bump generator versions in 3 BAML files
edit cianfhoghlaim/core/baml/_oideachais_src/generators.baml     # 0.74.0 → 0.223.0
edit cianfhoghlaim/core/baml/_croilar_baml/generators.baml        # if present
edit cianfhoghlaim/core/baml/_tuatha_baml/generators.baml         # if present

# 2. Refactor 8 inline anthropic client calls in curriculum_extraction.baml
#    client "anthropic/claude-sonnet-4-20250514" → client ExtractEn

# 3. Add semantic streaming attributes to streaming classes
#    class RelationshipExtractionResult { ... } → add @@stream.done

# 4. Wire ClientRegistry in extract_curriculum_relationships asset
#    Add EXTRACTION_CANARY_PERCENT env var + canary routing logic

# 5. Add AbortController to croilar-portfolio streaming calls
#    b.stream.GenerateContent(..., { abortController: new AbortController() })

# 6. Install BAML CLAUDE.md gist at cianfhoghlaim/CLAUDE.md
curl -L https://gist.githubusercontent.com/aaronvg/75596a0063588440d47f5db1361c8a5f/raw > cianfhoghlaim/CLAUDE.md

# 7. Bump baml-py in pyproject.toml
#    baml-py>=0.223.0 (was baml-py==0.220.0 or similar)

# 8. Validate
openspec validate 2026-06-29-baml-0-223-feature-upgrade --strict
bun run ccc:search "baml-py 0.223.0 openai-responses"   # verify no stragglers
```

### 7.5 Risks

- **BAML VM (WIP) is still WIP** — do not adopt BAML VM until `baml-language` ships a stable 0.14.0+.
- **BAML Agents / Workflows (WIP)** — same — do not adopt until stable.
- **`render_null_as`** — verify Pydantic compat (added in `baml-py 0.223.0`); regenerate all `baml_client/` and run typecheck.
- **Cognee v1.0 rename** — if cianfhoghlaim actually wants `remember/recall/forget/improve`, that's a **separate** change under `agent-memory-systems` spec, not BAML.

---

## Appendix — Sources & URL patterns

**Live (200):** `/` · `/changelog/changelog[.md]` · `/guide/introduction/what-is-baml` · `/guide/installation-language/python` · `/guide/baml-basics/streaming` · `/ref/overview` · `/ref/baml/client-llm` · `/ref/baml_client/client-registry` · `/guide/installation-editors/claude-code` · `https://github.com/boundaryml/baml/releases`
**404 (brief's URLs):** `/docs/get-started/quickstart` · `/blog/baml-v1-0-release` · `/docs/calling-llms/llm-providers` · `/docs/snippets/extract-data`
**URL pattern:** `https://docs.boundaryml.com/{guide|ref|examples|changelog|agents-md|home}/<subsection>/<page>` · `.md` suffix → markdown · `/llms.txt` → AI index · `/_mcp/server` → Fern MCP · `<meta name="generator" content="https://buildwithfern.com">` on every page