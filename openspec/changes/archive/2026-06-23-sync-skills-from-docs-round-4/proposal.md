# Change: sync-skills-from-docs-round-4

## Why

A fourth round of `docs/*` consolidation. The user listed 24
specific files spanning Celtic language AI, ML/ASR/TTS,
browser automation, BAML extraction, Convex auth, and durable
execution. Three concrete patterns emerge:

1. **Tiny 38-65 line "package pointer" docs add real KCG
   context** (`gabert.md`, `nllb-200.md`, `helsinki-opus-mt.md`,
   `wav2vec2-xlsr-irish.md`, `whisper-faster-whisper.md`,
   `Agent UI Ecosystem - A2UI.md`, `CONVEX_AGENT_PLATFORM.md`,
   `modal.md`-class stubs) — the KCG blurb is the only unique
   value; the rest is upstream marketing.
2. **Big 500-1000+ line docs are mostly redundant with
   just-expanded skills** (`IRISH_HUGGINGFACE.md`,
   `CELTIC_AI_RESOURCES.md`, `baml-extraction.md`,
   `AGENT_IMPLEMENTATIONS.md`, `DURABLE_EXECUTION_COMPREHENSIVE_REFERENCE.md`)
   — but contain valuable KCG-specific sections that should
   be folded into the canonical skills.
3. **No skills exist for `tts`, `asr`, `trl`, `peft`,
   `better-auth`** — all are first-class project dependencies
   (Chatterbox TTS, wav2vec2-XLSR-Irish, HuggingFace TRL
   SFT/DPO/GRPO, PEFT LoRA/QLoRA, BetterAuth OAuth/SIWE).

## What Changes

### New skills (5)

- `.agents/skills/tts/SKILL.md` — text-to-speech synthesis via
  Chatterbox (primary), MMS-TTS, Piper. KCG: Irish-language
  pronunciation guides, audio study notes, AI tutor speech.
- `.agents/skills/asr/SKILL.md` — speech recognition. KCG:
  wav2vec2-XLSR-Irish for accuracy-critical Irish (séimhiú,
  urú, dialectal variation), Whisper large-v3 / faster-whisper
  for general multilingual.
- `.agents/skills/trl/SKILL.md` — HuggingFace TRL (SFT, DPO,
  GRPO, RewardTrainer). KCG: RAGAS-as-DPO-preference-signal
  pattern; MLflow + Langfuse tracking via Dagster assets.
- `.agents/skills/peft/SKILL.md` — HuggingFace PEFT (LoRA,
  QLoRA, adapter merging, 4-bit quant). KCG: parameter-efficient
  fine-tuning on MacBook M4 48GB unified memory; Unsloth
  wrapper.
- `.agents/skills/better-auth/SKILL.md` — BetterAuth framework.
  KCG: multi-layer auth architecture (BetterAuth → PocketID →
  TinyAuth → Infisical); SIWE plugin; Drizzle adapter.

### Major skill expansions (5)

- `.agents/skills/celtic-language-ai/SKILL.md` — promote from
  9-line stub to ~250 lines (model catalog by language,
  translation stack, speech stack, datasets, KCG conventions).
  Note: the existing `irish-edtech/SKILL.md` (344 lines)
  already covers Irish-only; the new `celtic-language-ai`
  covers all 6 living Celtic languages.
- `.agents/skills/unsloth/SKILL.md` — append "Related tools"
  section pointing to new `trl` and `peft` skills.
- `.agents/skills/ragas/SKILL.md` — append "KCG Integration"
  section: faithfulness ≥ 0.8 gate; RAGAS as DPO preference
  signal; MLflow + Langfuse tracking.
- `.agents/skills/convex/SKILL.md` — append Agent component
  (`@convex-dev/agent`) + MCP server (`npx -y convex@latest
  mcp start`) + 30 lines from `references/convex-authentication-and-integration-guide.md`
  §"AI Agents".
- `.agents/skills/hono/SKILL.md` — append "Convex integration"
  subsection (HonoWithConvex + HttpRouterWithHono pattern).

### Minor expansions (5)

- `.agents/skills/lancedb/SKILL.md` — append 6-line "BGE-M3
  is the KCG canonical embedding model" note in the Best
  Practices section.
- `.agents/skills/pydantic-ai/SKILL.md` — append ~80 lines on
  Restate + DBOS (composable AI patterns table, awakeables,
  virtual objects, TypeScript Restate example).
- `.agents/skills/ag-ui/SKILL.md` — append "A2UI — sibling
  protocol" section (Google's JSON component blueprint
  alternative).
- `.agents/skills/browser/SKILL.md` — append "Multi-agent
  patterns" section (the `BrowserPipeline = SequentialAgent +
  LoopAgent` pattern from `browser_orchestrator.py`); append
  "Backend racing" section (the `BackendRacer` from
  `durable_orchestrator.py`).
- `.agents/skills/copilotkit/SKILL.md` — append 1-2 paragraphs
  on advanced context types (Zustand, Agent OS) from
  `AGENT_IMPLEMENTATIONS.md` §1.

### Docs to delete (24 files)

- `docs/05-celtic-language/helsinki-opus-mt.md` (56)
- `docs/05-celtic-language/IRISH_HUGGINGFACE.md` (545)
- `docs/05-celtic-language/CELTIC_AI_RESOURCES.md` (774)
- `docs/sruth/meaisinfhoghlaim/ragas.md` (53)
- `docs/sruth/meaisinfhoghlaim/chatterbox.md` (54)
- `docs/sruth/meaisinfhoghlaim/fine-tuning.md` (768)
- `docs/sruth/meaisinfhoghlaim/asr.md` (113)
- `docs/sruth/meaisinfhoghlaim/nllb-200.md` (54)
- `docs/05-web/convex-hono-auth.md` (472)
- `docs/01-patterns/gabert.md` (52)
- `docs/01-patterns/bge-m3.md` (54)
- `docs/00-package-ecosystem/speech/wav2vec2-xlsr-irish.md` (38)
- `docs/00-package-ecosystem/speech/whisper-faster-whisper.md` (39)
- `docs/03-agents/Agent UI Ecosystem - A2UI.md` (49)
- `docs/03-agents/AGENT_IMPLEMENTATIONS.md` (1024)
- `docs/03-agents/BROWSER_AUTOMATION_PLATFORM.md` (140)
- `docs/03-agents/browser_orchestrator.py` (262) — byte-identical
  to production
- `docs/03-agents/browser_session.py` (303) — near-duplicate
  of production (3 import lines differ)
- `docs/03-agents/browser-automation.md` (125) — canonical,
  KEEP (not deleted; just link from browser skill)
- `docs/03-agents/baml-extraction.md` (1064) — mostly
  redundant with just-expanded baml skill
- `docs/03-agents/CONVEX_AGENT_PLATFORM.md` (65) — content
  folded into convex skill
- `docs/03-agents/DURABLE_EXECUTION_COMPREHENSIVE_REFERENCE.md`
  (154) — content folded into pydantic-ai skill
- `docs/03-agents/durable_orchestrator.py` (497) — near-duplicate
  of production

**Note**: `browser-automation.md` is kept; only the 3 Python
doc files (which are exact/near-duplicates of
`infrastructure/browser/sruth_browser/...`) are deleted.

### Project rules PRESERVED (not changed)

- All Celtic-language conventions — preserved
- The browser-automation decision tree is canonical
- The meaisinfhoghlaim quadrant structure

## Impact

- **Affected specs (1)**: `meaisinfhoghlaim-platform` adds 4 new
  requirements (TTS pipeline, ASR routing, TRL training, PEFT
  parameter-efficient fine-tuning)
- **Affected code**: none. Skills are documentation.
- **Affected skills** (15 total): 5 new (tts, asr, trl, peft,
  better-auth) + 10 expanded (celtic-language-ai, unsloth,
  ragas, convex, hono, lancedb, pydantic-ai, ag-ui, browser,
  copilotkit)

## Success criteria

- `openspec validate sync-skills-from-docs-round-4 --strict`
  passes
- The 5 new skills exist at
  `.agents/skills/{tts,asr,trl,peft,better-auth}/SKILL.md`
- The 10 existing skills have new KCG context sections
- The 23 listed docs files are removed (or `.superseded` if
  the user prefers)
- `browser-automation.md` is preserved and linked from the
  browser skill

## Rollback

Skills-only. Rollback = restore the 23 docs files from git.
No data, code, or runtime state is affected.

## Out of scope

- `agent-os` skill creation (deferred to a follow-on change)
- The `fine-tuning.md` 612 lines of stale crypto-domain content
  (lines 156-768) — flagged for archive, not extracted
- The `crypteolas-recommended-patterns.md` extraction from
  `AGENT_IMPLEMENTATIONS.md` §9 — a follow-on change
