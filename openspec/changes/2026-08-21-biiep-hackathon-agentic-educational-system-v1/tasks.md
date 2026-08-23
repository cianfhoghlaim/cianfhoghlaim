# Tasks — All Things Agentic Hackathon Branch

## Phase 0: Worktree + Spec (Day 1 — Aug 21) ✅ DONE

### TASK-HACK-0.1 — Create the sibling git worktree ✅
- **Status**: done
- **Files**: `../biiep-hackathon-2026-08-31/` (new directory)
- **What**: `git worktree add -b hackathon/biiep-google-cloud-2026-08 ../biiep-hackathon-2026-08-31 HEAD`

### TASK-HACK-0.2 — Initialise the pyproject.toml ✅
- **Status**: done
- **Files**: `../biiep-hackathon-2026-08-31/pyproject.toml`
- **What**: Bumped baml-py to 0.223.0, added pydantic-ai>=1.0.0, vertexai>=1.50.0

### TASK-HACK-0.3 — Write the openspec change bundle ✅
- **Status**: done
- **Files**: `openspec/changes/2026-08-21-biiep-hackathon-agentic-educational-system-v1/`
- **What**: 4 files: proposal.md, tasks.md, 2 spec deltas

### TASK-HACK-0.4 — Validate the openspec change ✅
- **Status**: done
- **What**: `openspec validate --strict` → ✅ valid

### TASK-HACK-0.5 — Submit the $150 credit form
- **Status**: pending
- **What**: User submits before Aug 28 @ 12:00pm PT

## Phase 1: Copy + Prune (Day 2 — Aug 22) ✅ DONE

### TASK-HACK-1.1 — Copy the 13 ADK agents ✅
- **Status**: done
- **Files**: `sruth/oideachais/agents/adk/` (all 13 agents copied)
- **What**: Used rsync to copy the full adk/ tree

### TASK-HACK-1.2 — Copy agent registry ✅
- **Status**: done
- **What**: The `__init__.py` auto-exposes all 13 agents (the canonical Agent Registry)

### TASK-HACK-1.3 — Copy BAML extraction functions ✅
- **Status**: done
- **What**: All 6 jurisdictions inherited from the canonical commit

### TASK-HACK-1.4 — Copy TanStack Start scaffold ✅
- **Status**: done
- **What**: Forked `web/apps/croilar-web/` → `web/apps/biiep-agent/`

### TASK-HACK-1.4a — Add biiep-agent README ✅
- **Status**: done (2026-08-23, Phase E of post-lakehouse series)
- **Files**: `web/apps/biiep-agent/README.md` (130 lines)
- **What**: Replaced the Croílár-vestigial README with the hackathon-facing documentation (the 4 ideas + the 7 Fortified Fleet primitives + the BAML functions + the quick start + the reused infrastructure matrix)
- **Commit**: `24b116b3b` on `hackathon/biiep-google-cloud-2026-08`

### TASK-HACK-1.5 — Write UPSTREAM_REFS.md ✅
- **Status**: done

### TASK-HACK-1.6 — Write DISCLOSURE.md ✅
- **Status**: done

## Phase 2: Local LLM Stack + 4 Idea Stubs (Day 3 — Aug 23)

### TASK-HACK-2.1 — Verify litellm stack is up
- **Status**: pending
- **What**: `docker ps | grep litellm` (port 4000); `curl http://localhost:4000/v1/models`
- **Impact**: The local LLM gateway

### TASK-HACK-2.2 — Verify llama-swap stack is up
- **Status**: pending
- **What**: `docker ps | grep llama-swap` (port 8080); `curl http://localhost:8080/v1/models`
- **Impact**: The 14 GGUF entries

### TASK-HACK-2.3 — Verify unsloth-serve stack is up
- **Status**: pending
- **What**: `docker ps | grep unsloth` (port 8889); `curl http://localhost:8889/v1/models`
- **Impact**: The Unsloth Studio + Qwen3.8-27B

### TASK-HACK-2.4 — Verify OCR Router stack is up
- **Status**: pending
- **What**: `docker ps | grep ocr-router` (port 8090); `curl http://localhost:8090/docs`
- **Impact**: The 7-capability dispatch

### TASK-HACK-2.5 — Refactor the 13 ADK agents to use litellm
- **Status**: pending
- **Files**: `sruth/oideachais/agents/adk/*.py` (all 13 agents)
- **What**: Each agent uses `make_litellm_agent(name, model_alias="minimax")` (the canonical 7-tier fallback)
- **Impact**: All 13 agents route through the local LLM gateway

### TASK-HACK-2.6 — Smoke-test the 13-agent fleet
- **Status**: pending
- **What**: `python -c "from sruth.oideachais.agents.adk.root_agent import root_agent; print(root_agent.run('What is the Leaving Cert English syllabus?'))"`

### TASK-HACK-2.7 — Stub the 4 new ideas
- **Status**: pending
- **Files**:
  - `sruth/oideachais/agents/adk/marking_grader_workflow.py` (Idea 1 stub)
  - `sruth/oideachais/agents/adk/adaptive_tutor.py` (Idea 2 stub)
  - `sruth/oideachais/agents/adk/equivalency_generator.py` (Idea 3 stub)
  - `sruth/oideachais/agents/adk/curriculum_change_sensor.py` (Idea 4 stub)
- **What**: Empty class definitions + `__init__.py` exports

### TASK-HACK-2.8 — Verify Cognee + Firestore memory stacks
- **Status**: pending
- **What**: `curl http://localhost:8100/health` (Cognee); verify Firestore emulator at `localhost:8080`

### TASK-HACK-2.9 — Bump pyproject.toml
- **Status**: pending
- **What**: Add `dagster-dlt>=0.29`, `dagster-webserver>=1.13`, `change-detection-io>=0.4`

## Phase 3: Idea 2 — Adaptive Tutor Chat (Day 4 — Aug 24)

### TASK-HACK-3.1 — Build the `/tutor` route
- **Status**: pending
- **Files**: `web/apps/biiep-agent/src/routes/tutor.tsx`

### TASK-HACK-3.2 — Build the AdaptiveTutorChat CopilotKit component
- **Status**: pending
- **Files**: `web/apps/biiep-agent/src/components/AdaptiveTutorChat.tsx`

### TASK-HACK-3.3 — Write the adaptive_tutor BAML functions
- **Status**: pending
- **Files**: `baml_src/british_isles/_shared/adaptive_tutor.baml`
- **Functions**: `GenerateQuiz`, `ScoreAnswer`, `AdaptDifficulty`, `RecallStudentContext`

### TASK-HACK-3.4 — Wire Cognee Memory Bank
- **Status**: pending
- **Files**: `web/apps/biiep-agent/src/lib/memory/cognee.ts`
- **What**: The 5 typed clusters (already on :8000) + a new cluster `oideachais_tutor_memory`

### TASK-HACK-3.5 — Wire Firestore cross-session state
- **Status**: pending
- **Files**: `web/apps/biiep-agent/src/lib/memory/firestore.ts`
- **What**: `users/{user_id}`, `progress/{user_id}/{jurisdiction}/{level}/{subject}`, `feedback/{user_id}/{timestamp}`

### TASK-HACK-3.6 — Wire AG-UI streaming from the 13-agent fleet
- **Status**: pending
- **Files**: `web/apps/biiep-agent/src/lib/agent-client.ts`
- **What**: Routes through `make_litellm_agent(...)` (the existing factory) → AG-UI events

### TASK-HACK-3.7 — Add the Hono API route for `/api/v1/tutor`
- **Status**: pending
- **Files**: `web/hono-api/src/routes/biiep/tutor.ts`

## Phase 4: Tutor Polish + Progress Dashboard (Day 5 — Aug 25)

### TASK-HACK-4.1 — Build the memory timeline UI
- **Status**: pending
- **Files**: `web/apps/biiep-agent/src/components/MemoryTimeline.tsx`

### TASK-HACK-4.2 — Build the per-student progress dashboard
- **Status**: pending
- **Files**: `web/apps/biiep-agent/src/routes/progress.tsx`

### TASK-HACK-4.3 — Add RAGAS evaluation for tutor quality
- **Status**: pending
- **Files**: `web/apps/biiep-agent/src/lib/quality/ragas_tutor.py`

### TASK-HACK-4.4 — Test the persistent memory (5-turn + 24h gap)
- **Status**: pending

## Phase 5: Idea 3 — Cross-Jurisdiction Equivalency + Fleet Primitives (Day 6 — Aug 26)

### TASK-HACK-5.1 — Write the equivalency BAML functions
- **Status**: pending
- **Files**: `baml_src/british_isles/_cross/equivalency_table.baml`
- **Functions**: `GenerateEquivalencyTable`

### TASK-HACK-5.2 — Implement the ParallelAgent for equivalency
- **Status**: pending
- **Files**: `sruth/oideachais/agents/adk/equivalency_generator.py`

### TASK-HACK-5.3 — Build the `/equivalency` route
- **Status**: pending
- **Files**: `web/apps/biiep-agent/src/routes/equivalency.tsx`

### TASK-HACK-5.4 — Implement the 7 Fortified Fleet primitives
- **Status**: pending
- **Files**:
  - `agents/adk/gateway.py` (Agent Gateway — unified routing)
  - `agents/adk/identity.py` (Agent Identity — IAP)
  - `agents/adk/armor.py` (Model Armor — prompt injection + PII)
  - `agents/adk/observability.py` (Agent Observability — Langfuse + Cloud Logging)

### TASK-HACK-5.5 — Build the Fleet observability dashboard
- **Status**: pending
- **Files**: `web/apps/biiep-agent/src/routes/fleet.tsx`

## Phase 6: Idea 1 + Idea 4 — Marking Grader + Change Detection Sensor (Day 7 — Aug 27)

### TASK-HACK-6.1 — Write the marking_grader BAML functions
- **Status**: pending
- **Files**: `baml_src/british_isles/_shared/marking_grader.baml`
- **Functions**: `ScoreMarkingScheme`, `GenerateFeedback`

### TASK-HACK-6.2 — Implement the marking_grader_workflow SequentialAgent
- **Status**: pending
- **Files**: `sruth/oideachais/agents/adk/marking_grader_workflow.py`
- **What**: 4 steps (extract → score → feedback → store) + Long-Running resume

### TASK-HACK-6.3 — Build the `/marking-grader` route + PDF uploader
- **Status**: pending
- **Files**: `web/apps/biiep-agent/src/routes/marking-grader.tsx`

### TASK-HACK-6.4 — Wire the OCR Router integration
- **Status**: pending
- **What**: POST `http://localhost:8090/ocr` with `{capability: "markscheme" | "english", image_url: "..."}`

### TASK-HACK-6.5 — Implement the curriculum_change_sensor
- **Status**: pending
- **Files**: `sruth/oideachais/agents/adk/curriculum_change_sensor.py`

### TASK-HACK-6.6 — Wire the Dagster sensor
- **Status**: pending
- **Files**: `orchestration/sensors/curriculum_change.py`
- **What**: Fires the marking_grader_workflow on a ChangeDetection.io event

### TASK-HACK-6.7 — End-to-end test: upload marking scheme → grade → store
- **Status**: pending

## Phase 7: Cloud Serving Layer (Day 8 — Aug 28)

### TASK-HACK-7.1 — Create the GCP project
- **Status**: pending
- **What**: Project `biiep-hackathon-2026-08` (region `europe-west2`)

### TASK-HACK-7.2 — Provision Cloud Run (2 services)
- **Status**: pending
- **Files**: `cloud/terraform/cloud_run.tf`
- **What**: `biiep-agents` + `biiep-web`, min-instances 0

### TASK-HACK-7.3 — Provision IAP
- **Status**: pending
- **Files**: `cloud/terraform/iap.tf`

### TASK-HACK-7.4 — Write cloud_agent.py (Vertex AI factory)
- **Status**: pending
- **Files**: `sruth/oideachais/agents/adk/cloud_agent.py`

### TASK-HACK-7.5 — Wire the agent-client.ts local/Cloud switch
- **Status**: pending
- **Files**: `web/apps/biiep-agent/src/lib/agent-client.ts`
- **What**: If `process.env.NODE_ENV === "production"` → use Vertex AI; else use litellm

### TASK-HACK-7.6 — Write the Cloud Build pipeline
- **Status**: pending

### TASK-HACK-7.7 — Deploy and verify
- **Status**: pending

## Phase 8: Demo + Polish (Day 9 — Aug 29)

### TASK-HACK-8.1 — Write ARCHITECTURE.md
- **Status**: pending

### TASK-HACK-8.2 — Create the architecture diagram
- **Status**: pending

### TASK-HACK-8.3 — Write DEMO_SCRIPT.md
- **Status**: pending

### TASK-HACK-8.4 — Record the 4-min demo video
- **Status**: pending

### TASK-HACK-8.5 — Final lint + validate
- **Status**: pending

## Phase 9: Submission (Day 10 — Aug 30)

### TASK-HACK-9.1 — Final README.md

### TASK-HACK-9.2 — Submit Taskmaster entry

### TASK-HACK-9.3 — Submit Collaborative Partner entry

### TASK-HACK-9.4 — Submit Fortified Enterprise Fleet entry

### TASK-HACK-9.5 — Blog post (Medium or dev.to)

### TASK-HACK-9.6 — Social post with `#AllThingsAgenticHackathon`

### TASK-HACK-9.7 — Veo bonus integration (30-sec explainer)

### TASK-HACK-9.8 — Final reproducibility test

### TASK-HACK-9.9 — Submit by 5:00pm PT (1:00am Aug 31 in Ireland)
