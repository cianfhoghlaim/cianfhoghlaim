# Tasks: LLM Serving Skill + Test Audit v1

> 3 sections, 7 tasks. All tasks MUST pass before
> `openspec archive 2026-09-13-llm-serving-skill-and-test-audit-v1 --yes`.

## Phase A — Llama-swap skill (new) (15 min)

- [x] **A.1** Create `.agents/skills/llama-swap/SKILL.md` with GPU-vs-CPU reality check

## Phase B — Existing skill updates (10 min)

- [x] **B.1** Update `.agents/skills/litellm/SKILL.md` v1.90 → v1.97.0 (+ status section)
- [x] **B.2** Update `.agents/skills/unsloth/SKILL.md` v2026.6.9 → v2026.9.x (+ status section)

## Phase C — Smoke tests (15 min)

- [x] **C.1** Author `tests/llm_serving/__init__.py` + `tests/llm_serving/test_llm_serving.py`
- [x] **C.2** Add 7 health tests (CLI available, config model count, llama-swap routing, compose files, version alignment, BAML client model distribution)

## Phase D — Validation + archive (5 min)

- [x] **D.1** `uv run pytest tests/llm_serving/ -v` all 7 pass
- [x] **D.2** `uv run openspec validate 2026-09-13-llm-serving-skill-and-test-audit-v1 --strict` exits 0
- [x] **D.3** `uv run openspec archive 2026-09-13-llm-serving-skill-and-test-audit-v1 --yes`
