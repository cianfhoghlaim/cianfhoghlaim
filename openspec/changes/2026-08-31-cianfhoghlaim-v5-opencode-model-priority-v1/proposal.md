# Change: Cianfhoghlaim v5 — OpenCode + Model Priority + Qwen Removal v1

> **Status:** AUTHORED, ready for execution.
>
> **Phase 1 of 6** in the v5 refactor umbrella
> (`openspec/changes/2026-08-31-cianfhoghlaim-v5-opencode-model-priority-v1`).
>
> **Supersedes:** the prior M3-chokepoint-only `opencode.json` + the
> `litellm_local` provider + every `qwen/*` reference + the
> `DASHSCOPE_API_KEY` / `DASHSCOPE_BASE_URL` env vars. The new chain
> matches the gemini_hackathon profile (Tier 1 = MiniMax M3 / Vertex
> Gemini 3.5 Flash, Tier 2 = Unsloth Studio Gemma 4, Tier 3 = AI
> Studio Gemini 3.5 Flash) with the BIEP chokepoint on M3 retained.

## Why

The cianfhoghlaim project config (`opencode.json`) carried
3 stale patterns that no longer reflect the project's strategic
priorities:

1. **Qwen token-plan references.** The `provider.qwen` block +
   4 qwen entries in `MODEL_REGISTRY` + `DASHSCOPE_*` env vars
   + `qwen3-vl-8b` in 12 cocoindex/meaisinfhoghlaim files all
   reference the qwen Cloud token plan that the user de-prioritised
   on 2026-08-31 in favour of the gemini_hackathon Gemma + Gemini
   refocus.
2. **`litellm_local` provider.** The `litellm_local` block in
   `opencode.json` is a fallback for when the direct M3 endpoint
   is down; the new Unsloth Studio Gemma 4 + Vertex/AI-Studio
   Gemini 3.5 chain covers all the fallbacks that litellm_local
   was meant to cover.
3. **No Gemma-4 + no Google API in the opencode provider set.**
   The model priorities pushed on 2026-08-31 (Gemini Hackathon
   showcase direction) are absent from the opencode config —
   agents are stuck on MiniMax M3 + qwen token-plan only.

The global config (`~/.config/opencode/opencode.jsonc`) currently
points at Google Vertex Gemini 3.1 Pro Preview. That's the
gemini_hackathon-only chain; it has no Gemma 4 + no second MiniMax
key. The build + plan agents need the new `MINIMAX_API_KEY_V2` key.

## What changes

### §1 — Global opencode config (`~/.config/opencode/opencode.jsonc`)

- Add `provider["minimax-coding-plan"]` (key #1 = existing
  `MINIMAX_API_KEY`) — `MiniMax-M3` model.
- Add `provider["minimax-coding-plan-v2"]` (key #2 = new
  `MINIMAX_API_KEY_V2`) — `MiniMax-M3` model.
- Extend `provider["google-vertex"]` to also expose `gemini-3.5-flash`
  + `gemini-2.5-flash`.
- Add `provider["google-aistudio"]` exposing `gemini-3.5-flash`
  via AI Studio fallback.
- Add `provider["unsloth-studio"]` exposing `gemma-4-26b-a4b` +
  `gemma-4-e4b` + `gemma-3-27b-it` via the host process at
  `host.docker.internal:8888/v1`.
- `model` = `"minimax-coding-plan-v2/MiniMax-M3"` (build v2 key).
- `small_model` = `"unsloth-studio/gemma-4-e4b"`.
- `agent.build.model` = `"minimax-coding-plan-v2/MiniMax-M3"`.
- `agent.plan.model` = `"minimax-coding-plan-v2/MiniMax-M3"`.
- `agent.research.model` = `"minimax-coding-plan/MiniMax-M3"`
  (existing key #1).

### §2 — Project opencode config (`cianfhoghlaim/opencode.json`)

- DELETE `provider.qwen` (3 models + dashscope baseURL).
- DELETE `provider["litellm_local"]`.
- DELETE `unsloth/Qwen3.8-27B-GGUF` from
  `provider["unsloth-studio"].models`.
- ADD `provider["minimax-coding-plan"]` (key #1).
- ADD `provider["minimax-coding-plan-v2"]` (key #2).
- ADD `provider["google-aistudio"]`.
- EXTEND `provider["google-vertex"]` to expose Gemini 3.5/2.5
  Flash.
- EXTEND `provider["unsloth-studio"]` with `gemma-4-26b-a4b` +
  `gemma-4-e4b` + `gemma-3-27b-it`.
- `agent.build.model` = `"minimax-coding-plan-v2/MiniMax-M3"`.
- `agent.plan.model` = `"minimax-coding-plan-v2/MiniMax-M3"`.
- `agent.frontend-apps.model` = `"minimax-coding-plan/MiniMax-M3"`.
- `agent.notebooks.model` = `"unsloth-studio/gemma-4-26b-a4b"`.
- `agent.baml.model` = `"minimax-coding-plan/MiniMax-M3"`.
- `agent.dagster.model` = `"minimax-coding-plan/MiniMax-M3"`.
- `agent.deep-cuts.model` = `"unsloth-studio/gemma-4-26b-a4b"`.
- All other agent models unchanged.

### §3 — `.env.example` + `.infisical.env` cascade

- ADD `MINIMAX_API_KEY_V2=` (new v2 key for build + plan).
- ADD `MODEL_PROFILE=dev` (matches gemini_hackathon profile gate).
- ADD `GEMINI_API_KEY=` (kept; AI-Studio fallback).
- ADD `UNSLOTH_BASE_URL=http://host.docker.internal:8888/v1`
  + `UNSLOTH_API_KEY=` (the Gemma 4 path).
- ADD `GOOGLE_CLOUD_PROJECT=` + `GOOGLE_CLOUD_LOCATION=` (Vertex path).
- REMOVE `DASHSCOPE_API_KEY=` (3 occurrences: lines 225, 381, 610).
- REMOVE `DASHSCOPE_BASE_URL=` (2 occurrences: lines 381-382).

### §4 — `.opencode/agents/*.md` frontmatter edits

Match §2 model assignments.

### §5 — `meaisinfhoghlaim/models/model_registry.py`

- ADD `profile: ModelProfile = "hackathon" | "dev" | "both"` field.
- ADD entries: `gemini-3.5-flash`, `gemini-3.5-flash-aistudio`,
  `gemini-3.5-flash-lite`, `gemini-2.5-flash`,
  `gemini-embedding-2-preview`, `gemma-4-26b-a4b`, `gemma-4-e4b`,
  `gemma-3-27b-it`, `gemma-2-9b`, `gemma-4-26b-a4b-vision`,
  `gemma-4-12b-vision`, `gemma-4-e4b-vision`, `gemma-3-12b-vision`.
- TOMBSTONE (`available=False` + redirect notes) the 4 qwen3
  entries: `qwen3.7-plus`, `qwen3-coder-next`, `qwen3-coder-plus`,
  `qwen3.6-27b-mtp`.
- SET profile gates: `minimax-m3` → `"both"`; `gemini-3.5-flash`
  → `"hackathon"`; `gemma-4-26b-a4b` → `"hackathon"`; `kimi-k2.6`,
  `glm-5.1`, `mimo-v2.5`, `deepseek-v4-flash` → `"dev"`.

### §6 — `baml_src/clients.baml`

- REMOVE the `ExtractQwenCrossCheck` block (qwen dead).
- ADD 3 new retry policies: `Tier1` (3x exp), `Tier2` (2x const),
  `Tier3` (1x const).
- ADD concrete clients: `MiniMaxPrimary`, `VertexGemini35Flash`,
  `AIStudioGemini35Flash`, `UnslothGemma4`,
  `UnslothGemma4Light`, `LlamaSwapGemma4Vision`, `TestMock`.
- ADD `Primary` alias that reads `MODEL_BASE_URL` / `MODEL_API_KEY`
  / `MODEL_PRIMARY` from env.
- UPDATE `BIEPV3Vision` model from `local/vision/qwen3-vl-8b`
  → `local/ocr/gemma-4-26B-A4B-vision`.
- UPDATE `BIEPV3ExtractStrong` to use `MINIMAX_API_KEY_V2`.
- UPDATE the 8 generic aliases to use the new `Primary`-style
  indirection where applicable.

### §7 — Cascade: qwen hardcoded removals (~30 file edits)

Per `mise run lint:registry` audit. Touched:
`cocoindex_flows/{knowledge_graph,corpus,british_isles,_shared,media}/*`,
`meaisinfhoghlaim/{backends,datasets,ocr,training}/*`,
`scripts/lint_*.py`. All `qwen3-vl-8b` references swap to
`gemma-4-26b-a4b-vision`; `qwen3-vl` → `gemma-4-e4b-vision`;
`qwen3.6-27b-mtp` → `gemma-4-26b-a4b`; `DASHSCOPE_API_KEY` branch
removed from reranker.py; `irish-qwen3.8` checkpoint dir renamed
to `irish-gemma-4`.

### §8 — Skills + AGENTS.md + ccc guides cascade

- `.agents/skills/opencode/SKILL.md` — drop qwen example, add
  `minimax-coding-plan-v2` + `google-aistudio` examples.
- `.agents/skills/centralized-registry/SKILL.md` — Gemma 4 + Gemini
  3.5 entries.
- `.agents/skills/litellm/SKILL.md` — Gemini 3.5 + Gemma 4 routes.
- `.cocoindex_code/guides.yml` — `# google-aistudio-models`,
  `# unsloth-gemma-4-tier-2`, `# minimax-coding-plan-v2`.
- `openspec/AGENTS.md` — replace qwen3.7-plus with gemma-4.
- `openspec/specs/centralized-model-registry/spec.md` — ADDED
  Requirements for `Gemma 4 in MODEL_REGISTRY`,
  `gemini-3.5-flash in MODEL_REGISTRY`, `profile field required`,
  `qwen entries tombstoned`.

### §9 — Spec delta

See `specs/centralized-model-registry/spec.md` for the 4 new
ADDED Requirements.

## Impact

- 11 opencode config files edited (1 global + 1 project + 9
  agent markdown files).
- 4 env var files edited (`.env.example` + 4 `.infisical.env.*`
  sub-files).
- 1 `MODEL_REGISTRY` file extended (gemma-4 + gemini-3.5 entries
  + profile field).
- 1 `clients.baml` rewritten (3 new concrete clients + Primary
  alias).
- ~30 qwen-cascade files touched.
- 6 skill files updated.
- 0 breaking changes for BIEP extraction (M3 chokepoint preserved).
- 1 new env var introduced (`MINIMAX_API_KEY_V2`).
- 3 env vars removed (`DASHSCOPE_API_KEY`, `DASHSCOPE_BASE_URL`,
  `QWEN_DASHSCOPE_API_KEY`).

## Dependencies

- `2026-08-31-baml-primary-alias-and-fallback-v1` (Phase 2 — the
  per-function `fallback` chains land here).
- `2026-08-31-meaisinfhoghlaim-unsloth-priority-v1` (Phase 5 —
  the meaisinfhoghlaim refactor reuses the new Gemma 4 entries).
- The `centralized-model-registry` spec (already exists;
  `openspec/specs/centralized-model-registry/spec.md`).
- The `opencode` skill (already exists;
  `.agents/skills/opencode/SKILL.md`).

## Out of scope

- GCP mirror stacks (Phase 3 — separate change).
- Sister-repo transfer (Phase 4 — separate change).
- The `baml:switch-primary` mise task (Phase 2).
- The full `meaisinfhoghlaim/` refactor (Phase 5 — Phase 1 only
  registers the Gemma 4 entries + swaps the 30 hardcoded qwen
  references; the OCR-ensemble path rewrite is Phase 5).

## Quality gates (must pass before archive)

```bash
mise run openspec:validate 2026-08-31-cianfhoghlaim-v5-opencode-model-priority-v1 --strict
mise run lint:registry              # 0 drift — MODEL_REGISTRY covers every model string
mise run lint:skills                # 167+ skills pass
mise run lint:drift-docs            # all AGENTS.md number claims match ground truth
mise run sync:all                   # 14 sync layers green
mise run baml:generate              # baml_client/ regenerated from the new clients.baml
mise run baml:test                  # 558 BAML functions pass
```

---

*Last updated by build subagent at 2026-08-31.*