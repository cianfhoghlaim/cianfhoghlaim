# `web/apps/biiep-agent/` — All-Things-Agentic Hackathon Demo App

> **The 4 NEW education features for the Google All-Things-Agentic hackathon** (deadline Aug 31 2026 @ 8:00pm EDT, $180K prize pool, 6,126 participants). Built on top of the existing Cianfhoghlaim infrastructure — no Ollama, no new memory backends, no new agent fleet, no new web stack.

> **Sibling worktree**: `../biiep-hackathon-2026-08-31/` (branch: `hackathon/biiep-google-cloud-2026-08`).
> **Openspec change**: `openspec/changes/2026-08-21-biiep-hackathon-agentic-educational-system-v1/`.

## The 4 Ideas

### 1. Adaptive Marking Grader (`/marking-grader`) — Taskmaster + Collaborative Partner fit

Student uploads answer + marking scheme → instant grade + personalised feedback.

- BAML: `baml_src/british_isles/_shared/marking_grader.baml` (2 functions: `ScoreMarkingScheme` + `GenerateFeedback`)
- Agent: `sruth/oideachais/agents/adk/marking_grader_workflow.py` (the 4-step SequentialAgent: extract → score → feedback → store)
- Route: `web/apps/biiep-agent/src/routes/marking-grader.tsx`
- Track fit: ✅ Taskmaster (multi-step autonomous workflow) + ✅ Collaborative Partner (stateful, remembers past attempts)

### 2. Adaptive Tutor Chat (`/tutor`) — Collaborative Partner fit

Stateful 6-jurisdiction syllabus tutor with persistent memory.

- BAML: `baml_src/british_isles/_shared/adaptive_tutor.baml` (4 functions: `GenerateQuiz`, `ScoreAnswer`, `AdaptDifficulty`, `RecallStudentContext`)
- Agent: `sruth/oideachais/agents/adk/adaptive_tutor.py` (the persistent-memory tutor with Firestore)
- Route: `web/apps/biiep-agent/src/routes/tutor.tsx`
- Track fit: ✅ Collaborative Partner (stateful across sessions, adapts to student history)

### 3. Cross-Jurisdiction Equivalency Generator (`/equivalency`) — Fortified Fleet + Collaborative Partner fit

Compare LC ↔ A-Level ↔ GCSE topics side-by-side.

- BAML: `baml_src/british_isles/_cross/equivalency_table.baml` (1 function: `GenerateEquivalencyTable`)
- Agent: `sruth/oideachais/agents/adk/equivalency_generator.py` (the ParallelAgent that fans out across 6 jurisdictions)
- Route: `web/apps/biiep-agent/src/routes/equivalency.tsx`
- Track fit: ✅ Fortified Fleet (parallel agent fan-out) + ✅ Collaborative Partner (cross-jurisdiction)

### 4. Curriculum Change Detection Sensor (`/admin/curriculum-change`) — Taskmaster enabler

Dagster sensor that watches NCCA + AQA + SQA + WJEC + CCEA + IoM websites via ChangeDetection.io + Firecrawl MCP. On a syllabus change, fires the marking_grader_workflow SequentialAgent.

- Dagster sensor: `orchestration/sensors/curriculum_change.py`
- Agent: `sruth/oideachais/agents/adk/curriculum_change_sensor.py` (the LoopAgent that classifies the change)
- Track fit: ✅ Taskmaster (event-driven autonomous workflow: watch → classify → act)

## Quick Start

```bash
# Verify the local LLM stack is up (the canonical pre-req)
mise run iac:health              # All 94 stacks healthy
mise run cic:stack-doctor --stack=litellm  # LiteLLM at :4000
curl http://localhost:4000/v1/models | head -3  # Should return the 22+ models

# Verify the BIEP v3 ingestion has run (the canonical data)
mise run data:dagster:up          # Dagster at :3335
dagster asset materialize --select ie_lc_mathematics_curriculum  # Verify the 544 Ireland cohorts

# Run the BIEP-agent app locally
cd web/apps/biiep-agent
bun install
bun run dev  # http://localhost:5173 — the 4 features
```

## The 7 Fortified Fleet Primitives

Per the hackathon's "Fortified Enterprise Fleet" track:

| Primitive | File | Purpose |
|:--|:--|:--|
| Agent Gateway | `sruth/oideachais/agents/adk/gateway.py` | Unified routing across the 13 ADK agents |
| Agent Identity | `sruth/oideachais/agents/adk/identity.py` | IAP (Identity-Aware Proxy) for Cloud Run |
| Model Armor | `sruth/oideachais/agents/adk/armor.py` | Prompt injection + PII detection |
| Agent Observability | `sruth/oideachais/agents/adk/observability.py` | Langfuse + Cloud Logging |
| Cloud Runtime | `sruth/oideachais/agents/adk/cloud_runtime.py` | Vertex AI factory |
| Adaptive Tutor | `sruth/oideachais/agents/adk/adaptive_tutor.py` | The stateful tutor (Idea 2) |
| Fleet Dashboard | `web/apps/biiep-agent/src/routes/fleet.tsx` | Per-agent observability view |

## The BAML Extraction Functions

| Function | File | Client |
|:--|:--|:--|
| `ScoreMarkingScheme` | `baml_src/british_isles/_shared/marking_grader.baml` | `BIEPV3Extract` (text_llm/default → "minimax-m3") |
| `GenerateFeedback` | `baml_src/british_isles/_shared/marking_grader.baml` | `BIEPV3Extract` |
| `GenerateQuiz` | `baml_src/british_isles/_shared/adaptive_tutor.baml` | `BIEPV3Extract` |
| `ScoreAnswer` | `baml_src/british_isles/_shared/adaptive_tutor.baml` | `BIEPV3Extract` |
| `AdaptDifficulty` | `baml_src/british_isles/_shared/adaptive_tutor.baml` | `BIEPV3Extract` |
| `RecallStudentContext` | `baml_src/british_isles/_shared/adaptive_tutor.baml` | `BIEPV3Extract` |
| `GenerateEquivalencyTable` | `baml_src/british_isles/_cross/equivalency_table.baml` | `BIEPV3Extract` |

Re-gen the BAML client after editing:
```bash
cd biiep-hackathon-2026-08-31 && uv run baml-cli generate --from baml_src
```

## The Reused Infrastructure

Per the proposal, the 4 ideas leverage the existing Cianfhoghlaim infrastructure:

| Layer | What we reuse |
|:--|:--|
| Local LLM | `litellm` (`:4000`) → `llama-swap` (`:8080`, 14 GGUF entries) + `unsloth-serve` (`:8889`, Qwen3.8-27B) |
| OCR/VLM | `ocr-router` (`:8090`, the 7-capability dispatch) |
| Agent fleet | The existing **13 ADK agents** at `sruth/oideachais/agents/adk/` |
| BAML extraction | `baml_src/british_isles/{ireland,england,scotland,wales,ni,isle_of_man}/education/` |
| Model selection | `MODEL_REGISTRY` (76 entries / 7 families) + `VISION_MODELS` (22 entries) |
| Memory (prod) | Cognee (`:8100`) for structured knowledge + LanceDB for vectors |
| Memory (serving) | Firestore (the new layer on Cloud Run, for cross-instance persistence) |
| Observability | Langfuse (`:3000`) + Logfire + MLflow + RAGAS + structlog |
| Web stack | TanStack Start + Convex + Hono + CopilotKit + Better Auth |
| Auth | Pocket ID + TinyAuth + Better Auth |
| Agent runtimes | OpenChamber + Hermes + OpenClaw + OpenCode + Claude Code |

## The Status (per the openspec tasks.md)

13 of 64 tasks marked done (Phase 0 + Phase 1 + a few Phase 6):
- ✅ TASK-HACK-0.1 through 0.4: Worktree + scaffolding
- ✅ TASK-HACK-1.1 through 1.6: Copy + prune (13 ADK agents, BAML functions, TanStack Start scaffold)
- ⏳ 51 tasks pending (Phase 2-9: local LLM verification + 4 idea implementations + Cloud Run deploy + demo + submission)

## References

- `openspec/changes/2026-08-21-biiep-hackathon-agentic-educational-system-v1/proposal.md` — the full proposal
- `openspec/changes/2026-08-21-biiep-hackathon-agentic-educational-system-v1/tasks.md` — the 64-task breakdown
- `sruth/oideachais/agents/adk/README.md` — the 13 ADK agents overview
- `baml_src/clients.baml` — the BIEPV3Extract client
- `../cianchosaint/AGENTS.md` — the sibling-repo sister project

---

**Last updated**: 2026-08-23 (Phase E addition by the build agent).
**Owner**: Build agent (the hackathon branch owner).