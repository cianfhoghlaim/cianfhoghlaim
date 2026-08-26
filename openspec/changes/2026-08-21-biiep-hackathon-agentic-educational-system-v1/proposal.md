# Hackathon Branch — All Things Agentic (13-agent ADK + 4 New Ideas)

## Why

The **All Things Agentic hackathon** (Google, deadline **Aug 31 2026 @ 8:00pm EDT**,
$180K prize pool, 6,126 participants) is the canonical external validation surface
for the 13-agent ADK fleet + the British-Isles Education Pipeline (BIEP). This
change branches a focused `../biiep-hackathon-2026-08-31/` sibling worktree that
delivers **4 NEW education features** on top of the existing infrastructure:

1. **Adaptive Marking Grader** — student uploads answer + marking scheme → instant grade + feedback (Taskmaster + Collaborative Partner fit)
2. **Adaptive Tutor Chat** — stateful 6-jurisdiction syllabus tutor with persistent memory (Collaborative Partner fit)
3. **Cross-Jurisdiction Equivalency Generator** — compare LC ↔ A-Level ↔ GCSE topics side-by-side (Fortified Fleet + Collaborative Partner fit)
4. **Curriculum Change Detection Sensor** — Dagster sensor that watches NCCA + AQA + SQA + WJEC + CCEA + IoM websites and fires the SequentialAgent on changes (Taskmaster enabler)

All 4 features leverage the **existing cianfhoghlaim infrastructure** —
no Ollama, no new memory backends, no new agent fleet, no new web stack:

| Layer | What we reuse |
|:--|:--|
| **Local LLM** | `litellm` (`:4000`) → `llama-swap` (`:8080`, 14 GGUF entries) + `unsloth-serve` (`:8889`, Qwen3.8-27B) |
| **OCR/VLM** | `ocr-router` (`:8090`, the 7-capability dispatch) |
| **Agent fleet** | The existing **13 ADK agents** at `sruth/oideachais/agents/adk/` |
| **BAML extraction** | `baml_src/british_isles/{ireland,england,scotland,wales,ni,isle_of_man}/education/` |
| **Model selection** | `MODEL_REGISTRY` (52 entries / 7 families) + `VISION_MODELS` (22 entries) |
| **Memory (prod)** | Cognee (`:8000`) for structured knowledge + LanceDB for vectors |
| **Memory (serving)** | Firestore (the new layer on Cloud Run, for cross-instance persistence) |
| **Observability** | Langfuse (`:3000`) + Logfire + MLflow + RAGAS + structlog |
| **Web stack** | TanStack Start + Convex + Hono + CopilotKit + Better Auth |
| **Auth** | Pocket ID + TinyAuth + Better Auth |
| **Agent runtimes** | OpenChamber + Hermes + OpenClaw + OpenCode + Claude Code (all wired via the 2026-08-21 Unsloth v5 change) |

The cianfhoghlaim main repo continues to evolve the data engineering +
ML pipelines (BAML, DLT, CocoIndex, Dagster, DuckLake, MotherDuck) — this branch
focuses on the **4 new agentic features** that consume those pipelines.

## What changes

### The worktree is the deliverable

```
../biiep-hackathon-2026-08-31/                  # Sibling git worktree
├── baml_src/                                 # Carried over (read-only) — all 6 jurisdictions
├── meaisinfhoghlaim/models/                   # Carried over (read-only) — MODEL_REGISTRY + VISION_MODELS
├── sruth/oideachais/agents/                  # Carried over (read-only) — 13 ADK agents
├── notebooks/30_unsloth_vision_compare.py    # Carried over (read-only) — the 10-way comparison
├── web/apps/biiep-agent/                      # NEW — TanStack Start (the 4 ideas' surface)
├── cloud/                                     # NEW — Cloud Run + Vertex AI serving layer only
├── sruth/oideachais/agents/adk/               # NEW additions only
│   ├── marking_grader_workflow.py             # Idea 1
│   ├── adaptive_tutor.py                      # Idea 2
│   ├── equivalency_generator.py               # Idea 3
│   ├── curriculum_change_sensor.py            # Idea 4
│   ├── cloud_agent.py                         # The Vertex AI factory
│   ├── gateway.py                             # Agent Gateway primitive (Fleet)
│   ├── identity.py                            # Agent Identity primitive (Fleet)
│   ├── armor.py                               # Model Armor primitive (Fleet)
│   └── observability.py                       # Agent Observability primitive (Fleet)
├── baml_src/british_isles/_shared/            # NEW BAML only
│   ├── marking_grader.baml
│   ├── adaptive_tutor.baml
│   └── equivalency_table.baml
└── docs/
    ├── ARCHITECTURE.md
    ├── diagrams/architecture.{mmd,png}
    ├── DEMO_SCRIPT.md
    ├── SUBMISSION.md                          # 3-track narratives
    ├── DISCLOSURE.md                          # ✅ Day 2 — Rule 6 compliance
    └── UPSTREAM_REFS.md                       # ✅ Day 2 — provenance
```

### The 4 new ideas — the headline of this submission

#### Idea 1: Adaptive Marking Grader (Taskmaster + Collaborative Partner)

**Problem:** Teachers spend 30+ minutes grading each Leaving Cert / A-Level / GCSE paper by hand. Students wait weeks for feedback.

**Solution:** The student uploads (1) their written answer (PDF or photo), (2) the marking scheme PDF. The agent:
1. **OCR Router** (`:8090`) extracts the answer + the marking scheme (uses `markscheme` + `english` capabilities)
2. **BAML `ScoreMarkingScheme`** matches the answer against the marking scheme
3. **BAML `GenerateFeedback`** writes personalised feedback in plain English
4. **Cognee Memory Bank** (`:8000`) stores the grade + feedback for the next session
5. **Firestore** (serving layer) persists across Cloud Run instances

#### Idea 2: Adaptive Tutor Chat (Collaborative Partner)

**Problem:** Students struggle to know which topics to study. Generic LLMs don't know the official NCCA / AQA / SQA syllabus.

**Solution:** The student chats with a tutor that:
1. **Knows the syllabus** (the 13-agent fleet routes to the right per-jurisdiction specialist)
2. **Remembers past sessions** (Cognee for structured knowledge + Firestore for cross-session state)
3. **Adapts difficulty** (the agent tracks which concepts the student struggles with)
4. **Multimodal** (PDF + image + diagram support via OCR Router)

#### Idea 3: Cross-Jurisdiction Equivalency Generator (Fortified Fleet + Collaborative Partner)

**Problem:** A student in Northern Ireland studying CCEA Maths doesn't know what the equivalent is in England (A-Level) or Scotland (SQA). Teachers can't easily compare syllabi across jurisdictions.

**Solution:** The user picks a jurisdiction + a subject + a level → the agent:
1. **ParallelAgent** queries the relevant ADK agents in parallel
2. **BAML `GenerateEquivalencyTable`** produces a structured comparison
3. **The UI** renders the side-by-side comparison
4. **Cognee Knowledge Graph** stores the cross-jurisdiction mappings

#### Idea 4: Curriculum Change Detection Sensor (Taskmaster enabler)

**Problem:** The BIEP v3 pipeline only re-ingests on a yearly schedule. When NCCA publishes a new syllabus (Aug 2026), we don't know until the cron fires.

**Solution:** A Dagster sensor that:
1. Watches the NCCA + AQA + OCR + Edexcel + SQA + WJEC + CCEA + IoM websites via the existing ChangeDetection.io stack
2. On a syllabus change, fires the `marking_grader_workflow` SequentialAgent
3. The agent re-extracts the syllabus + re-embeds via the BIEP v3 5-phase pattern
4. Updates the centralised schema-registry

### The local LLM stack — litellm → llama-swap + unsloth-serve + cloud

| Layer | Local (bunchloch) | Cloud (GCP) |
|:--|:--|:--|
| LLM gateway | `litellm` (`:4000`) | `litellm` on Cloud Run (or direct Vertex AI) |
| Local GGUF | `llama-swap` (`:8080`, 14 entries) | — |
| Unsloth Studio | `unsloth-serve` (`:8889`, Qwen3.8-27B) | — |
| Cloud (serving) | — | Gemini 3.5 Flash via Vertex AI |
| Cloud (burst) | — | Gemini 3.5 Pro via Vertex AI (rate-limit fallback) |

The BAML clients are already wired (`baml_src/clients.baml` + `baml_src/clients_llama_swap.baml`). The `make_litellm_agent(...)` factory is already at `sruth/oideachais/agents/adk/litellm_agent.py`.

### The hybrid memory stack

| Backend | Layer | Purpose |
|:--|:--|:--|
| **Cognee** (`:8000`) | Production | Structured knowledge graphs, cross-jurisdiction mappings, per-student context |
| **LanceDB** (existing) | Production | Vector RAG for syllabus search |
| **Firestore** (NEW) | Serving layer | Cross-instance persistence on Cloud Run (the Memory Bank primitive) |
| **Graphiti** (`:8001`) | Optional | Temporal knowledge (per-student progress over time) |

### Submitting 3 tracks with one codebase

Per Rule 6 ("Multiple Submissions … each Submission must be unique and substantially different"), we submit **3 separate Devpost entries** with the same repo, different narrative focus:

1. **Taskmaster** — emphasising the Adaptive Marking Grader + the Change Detection Sensor
2. **Collaborative Partner** — emphasising the Adaptive Tutor Chat + the Firestore Memory Bank
3. **Fortified Enterprise Fleet** — emphasising the 13-agent orchestrator + the Cross-Jurisdiction Equivalency + the 7 Fleet primitives

Each gets a different `README.md` lead section + a different 4-min demo cut.

## Phasing

| Day | Focus | Output |
|:--|:--|:--|
| Day 1 (Aug 21) | Worktree + spec change | ✅ DONE — `proposal.md` + `tasks.md` + 2 spec deltas drafted |
| Day 2 (Aug 22) | Copy + Prune | ✅ DONE — 13 ADK agents + BAML + web scaffold copied + DISCLOSURE.md |
| Day 3 (Aug 23) | **litellm + llama-swap + unsloth-serve + idea stubs** | Refactor 13 agents to use `make_litellm_agent`; smoke-test the fleet; stub the 4 new ideas |
| Day 4 (Aug 24) | **Idea 2: Adaptive Tutor Chat** | TanStack Start + Hono API + AG-UI + Cognee + Firestore cross-session state |
| Day 5 (Aug 25) | **Tutor polish + Progress Dashboard** | Memory timeline UI + per-student progress |
| Day 6 (Aug 26) | **Idea 3: Cross-Jurisdiction Equivalency + Fleet primitives** | ParallelAgent + Gateway + Identity + Armor + Observability |
| Day 7 (Aug 27) | **Idea 1 + Idea 4: Marking Grader + Change Detection Sensor** | The 4-step SequentialAgent + Dagster sensor + OCR Router integration |
| Day 8 (Aug 28) | Cloud serving layer | Cloud Run + Vertex AI + IAP (only the serving surface) |
| Day 9 (Aug 29) | Demo + polish | 4-min video + arch diagram |
| Day 10 (Aug 30) | Submission + bonus | 3 submissions + blog + Veo bonus |

## Version pins

- `google-adk>=1.17.0` (already pinned — SequentialAgent + ParallelAgent + BuiltInPlanner + LongRunningFunctionTool)
- `baml-py>=0.223.0,<0.224.0` (bumped Day 2 — spawn + host.callable + catch + multimodal)
- `pydantic-ai>=1.0.0` (added Day 2 — the agentic chat backbone)
- `vertexai>=1.50.0` (added Day 2 — the Cloud Run serving layer)
- `litellm>=1.97.0` (already pinned — the local LLM gateway)
- `tanstack-start>=1.94.0` (the web stack)
- `copilotkit>=2.0.0` (AG-UI + a2ui-renderer)
- `hono>=4.0.0` (the API gateway)
- `terraform>=1.9.0` (the Cloud Run + IAP)
- `dagster>=1.13` (the sensor for the Change Detection workflow)
- `dagster-dlt>=0.29` (the BIEP v3 integration)

## Spec deltas (2 ADDED — to be updated)

| Spec | Status | Source |
|:--|:--|:--|
| `biiep-agentic-educational-system` | UPDATE | The 13-agent fleet + the 4 new ideas + litellm + llama-swap + unsloth-serve + hybrid memory |
| `google-adk-hackathon-deployment` | UPDATE | Cloud Run + Vertex AI + IAP ONLY (no new Cloud SQL/Firestore mandatory — they exist) |

## Dependencies

`Blocked by: none`
`Blocked by (soft): 2026-08-26-mega-3a-baml-and-adk-v1` (the BAML + ADK foundations)
`Blocked by (soft): 2026-08-21-unsloth-v5-vision-llm-hermes-openclaw-opencode-marimo-integration-v1` (the Unsloth stack)
`Affected repos: cianfhoghlaim` (single repo via worktree — no cross-repo)

## Compliance

- **Rule 6 (Mandatory Tech):** ✅ Gemini 3.5 Flash via Vertex AI + ✅ Google ADK + ✅ Cloud Run
- **Rule 6 (New Projects Only):** The submission is 4 NEW features built on top of pre-existing libraries — disclosed in `docs/DISCLOSURE.md`
- **Rule 6 (Multiple Submissions):** 3 unique submissions of substantially different projects
- **Rule 5 (Credits):** $150 credit form submitted by user before Aug 28 12:00 PT
- **Rule 3 (Eligibility):** Participant is based in Ireland (excluded countries: Italy, Quebec, Crimea, Cuba, Iran, Syria, North Korea, Sudan, Belarus, Russia)
