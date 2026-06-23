# Tasks: sync-skills-from-docs-round-4

## 1. Create OpenSpec change scaffolding
- [x] Create change directory.
- [x] Write `proposal.md`.
- [x] Write `tasks.md` (this file).
- [x] Write 1 spec delta (meaisinfhoghlaim-platform).
- [x] Validate `--strict`.

## 2. New skills (5)
- [x] Create `.agents/skills/tts/SKILL.md` (Chatterbox + MMS-TTS + Piper).
- [x] Create `.agents/skills/asr/SKILL.md` (Whisper + wav2vec2-XLSR-Irish + MMS).
- [x] Create `.agents/skills/trl/SKILL.md` (SFT/DPO/GRPO + RAGAS-as-DPO).
- [x] Create `.agents/skills/peft/SKILL.md` (LoRA + QLoRA + bitsandbytes).
- [x] Create `.agents/skills/better-auth/SKILL.md` (BetterAuth + SIWE + Drizzle).

## 3. Major skill expansions (5)
- [x] Rewrite `.agents/skills/celtic-language-ai/SKILL.md`
      (9 lines → ~250; model catalog by language).
- [x] Append "Related tools" to `.agents/skills/unsloth/SKILL.md`.
- [x] Append KCG integration to `.agents/skills/ragas/SKILL.md`.
- [x] Append Agent component to `.agents/skills/convex/SKILL.md`.
- [x] Append Convex integration to `.agents/skills/hono/SKILL.md`.

## 4. Minor skill expansions (5)
- [x] Append BGE-M3 note to `.agents/skills/lancedb/SKILL.md`.
- [x] Append Restate section to `.agents/skills/pydantic-ai/SKILL.md`.
- [x] Append A2UI section to `.agents/skills/ag-ui/SKILL.md`.
- [x] Append multi-agent patterns to `.agents/skills/browser/SKILL.md`.
- [x] Append context types to `.agents/skills/copilotkit/SKILL.md`.

## 5. Delete the listed docs
- [x] `rm docs/05-celtic-language/helsinki-opus-mt.md`
- [x] `rm docs/05-celtic-language/IRISH_HUGGINGFACE.md`
- [x] `rm docs/05-celtic-language/CELTIC_AI_RESOURCES.md`
- [x] `rm docs/meaisinfhoghlaim/ragas.md`
- [x] `rm docs/meaisinfhoghlaim/chatterbox.md`
- [x] `rm docs/meaisinfhoghlaim/fine-tuning.md`
- [x] `rm docs/meaisinfhoghlaim/asr.md`
- [x] `rm docs/meaisinfhoghlaim/nllb-200.md`
- [x] `rm docs/05-web/convex-hono-auth.md`
- [x] `rm docs/01-patterns/gabert.md`
- [x] `rm docs/01-patterns/bge-m3.md`
- [x] `rm docs/00-package-ecosystem/speech/wav2vec2-xlsr-irish.md`
- [x] `rm docs/00-package-ecosystem/speech/whisper-faster-whisper.md`
- [x] `rm docs/03-agents/Agent\ UI\ Ecosystem\ -\ A2UI.md`
- [x] `rm docs/03-agents/AGENT_IMPLEMENTATIONS.md`
- [x] `rm docs/03-agents/BROWSER_AUTOMATION_PLATFORM.md`
- [x] `rm docs/03-agents/browser_orchestrator.py`
- [x] `rm docs/03-agents/browser_session.py`
- [x] `rm docs/03-agents/baml-extraction.md`
- [x] `rm docs/03-agents/CONVEX_AGENT_PLATFORM.md`
- [x] `rm docs/03-agents/DURABLE_EXECUTION_COMPREHENSIVE_REFERENCE.md`
- [x] `rm docs/03-agents/durable_orchestrator.py`

**Preserve:** `docs/03-agents/browser-automation.md` (125 lines,
canonical decision-tree)

## 6. Verify
- [ ] Re-validate `--strict`.

## 7. Archive
- [ ] `openspec archive sync-skills-from-docs-round-4 --yes`.

## 8. Land the plane
- [ ] `git add` only my changes.
- [ ] `git commit -m "..."`.
- [ ] `git push`.
