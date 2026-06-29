# BAML Phase 2.2: Per-Quadrant clients.baml Unification

## Goal

Replace the 4 per-quadrant `clients.baml` files (1 was empty, 3 had
drifted) with thin shims that re-export the canonical clients from
`shared/baml_src/clients.baml`.

## Current state

| Quadrant | File | Status | Drift |
|:--|:--|:--|:--|
| `_oideachais_src/` | `clients.baml` (15 clients) | Live | Hardcoded `litellm/minimax-m3` per-client; not using shared/ |
| `_oideachais_src/` | `clients_0.baml` (3 clients) | Live | Duplicate of clients.baml |
| `_oideachais_src/` | `clients_llama_swap.baml` (4 clients) | Live | Llama-swap local models |
| `_meaisinfhoghlaim_src/` | (no clients.baml) | Inline | All functions use inline `provider "openai"` |
| `_tuatha_src/` | `tuatha_clients.baml` (5 clients) | Live | 4 hardcoded `gpt-4o` clients + 1 Claude |
| `_croilar_baml/` | `clients.baml` (1 client) | Live | `local/vision/qwen3-vl` only |

## Target state

Each quadrant's `clients.baml` becomes a thin shim that imports
the shared/ clients. The shared/clients.baml becomes the single
source of truth.

The 4 BAML files will be reduced from 4 files (3+ clients) to
4 files (0-1 client each, all aliases to shared/).

## Migration plan

### Step 1: Map old client names to new ones

| Old name | New name (in shared/) | Quadrant |
|:--|:--|:--|
| `LitellmClient` | `DefaultLiteLLM` | oideachais |
| `DeepSeekClient` | `DefaultLiteLLM` (deprecate) | oideachais |
| `LitellmLongContext` | `DefaultLiteLLM` (use max_tokens option) | oideachais |
| `Extractor` | `OideachaisDefault` | oideachais |
| `LiteLLM` | `DefaultLiteLLM` | oideachais |
| `Gemini25Pro` | `ReasoningStrong` | oideachais |
| `Gemini25Flash` | `DefaultLiteLLM` (fast model) | oideachais |
| `Gemini3FlashPreview` | (keep inline; opt-in) | oideachais |
| `OpenCodeGo` | `DefaultLiteLLM` (deprecate direct) | oideachais |
| `MiniMax` | `DefaultLiteLLM` (canonical) | oideachais |
| `LocalVision` | `VisionLocal` | oideachais |
| `LocalOCR` | `VisionLocal` | oideachais |
| `LocalIrish` | `OideachaisDefault` (UCCIX model) | oideachais |
| `LocalMath` | `ReasoningStrong` | oideachais |
| `ImageGen` | (keep inline; FIBO model) | oideachais |
| `ExtractEn` | `OideachaisDefault` | oideachais |
| `ExtractEnStrong` | `ReasoningStrong` | oideachais |
| `GPT4o` (tuatha) | `TuathaDefault` | tuatha |
| `Claude` (tuatha) | `OideachaisDefault` | tuatha |
| `LocalVisionQwen` (croilar) | `CroilarDefault` | croilar |

### Step 2: Per-quadrant shim files

#### `_oideachais_src/clients.baml` (reduced to 1 client)

```baml
// Per-quadrant shim — re-exports from shared/. See shared/baml_src/clients.baml
// for the canonical client definitions.
client<llm> LitellmClient {
  provider "openai"
  options {
    model "litellm/minimax-m3"
  }
}
```

Then ALL 14 other oideachais clients are DELETED in favour of
the shared/ clients.

#### `_tuatha_src/tuatha_clients.baml` (reduced to 1 client)

```baml
// Per-quadrant shim — re-exports from shared/. See shared/baml_src/clients.baml
client<llm> GPT4o {
  provider "openai"
  options {
    model "litellm/gpt-4o"
  }
}
```

#### `_croilar_baml/clients.baml` (kept as 1 client)

```baml
client<llm> LocalVisionQwen {
  provider "openai"
  options {
    model "local/vision/qwen3-vl"
  }
}
```

#### `_meaisinfhoghlaim_src/` (no client file)

Add a new `clients.baml` shim that references the shared/ clients.

### Step 3: Update all .baml function references

For each of the 75 .baml files, update the `client "OldName"` references
to the new shared/ name. Use a sed script to do this in bulk:

```bash
find cianfhoghlaim -name "*.baml" -exec sed -i '' \
  -e 's/client "LitellmClient"/client "DefaultLiteLLM"/g' \
  -e 's/client "Extractor"/client "OideachaisDefault"/g' \
  -e 's/client "LocalVision"/client "VisionLocal"/g' \
  -e 's/client "GPT4o"/client "TuathaDefault"/g' \
  -e 's/client "LocalVisionQwen"/client "CroilarDefault"/g' \
  {} \;
```

### Step 4: Validation

```bash
cd cianfhoghlaim/core/baml/shared
baml-cli check
baml-cli generate
cd cianfhoghlaim/core/baml/_oideachais_src
baml-cli check
baml-cli generate
# ... etc. for each quadrant
```

## What this change does NOT do

- It does NOT update the .baml function references (Step 3) — that's
  Phase 2.3 (functions/ireland) + 2.4 (functions/scotland+).
- It does NOT remove the duplicate `clients_0.baml` file.
- It does NOT touch the legacy `docs/legacy/crypteolas/baml_src/`.

## Why a shim and not a hard delete?

A shim file keeps the old client NAMES available while we migrate
the .baml function references. This means:
- Functions that still reference `LitellmClient` continue to work.
- New functions can use the shared/ `DefaultLiteLLM` directly.
- We can deprecate the shim names one at a time.

This is the lowest-risk migration path. Hard delete would require
updating all 75 .baml files in one go, which is much more error-prone.
