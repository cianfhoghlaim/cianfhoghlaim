---
title: 'LLM Stack Hierarchy'
domain: 'ai_ml'
status: 'stable'
description: 'The BAML → litellm → ADK/AGNO → ccc cocoindex-code → Cognee stack. Where each layer fits, and the calling order between them.'
read_when:
  - adding a new LLM call anywhere in the platform
  - choosing between BAML / raw litellm / ADK / AGNO
  - debugging a knowledge-graph vs vector-search mismatch
truth: sole
updated: '2026-06-13'
ccc_query_hints:
  - llm stack baml litellm adk agno ccc cognee
  - knowledge graph ccc cocoindex code
---

# LLM Stack Hierarchy

> **The stack:**
> `BAML (structured extraction in DE pipelines) → litellm (LLM routing) → ADK / AGNO (agent orchestration) → ccc cocoindex-code (semantic index over the codebase) → Cognee (knowledge graph memory)`.
>
> All five layers are first-class. None of them replaces the others.

## Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  BAML  ──────►  litellm  ──────►  ADK / AGNO  ──────►  ccc  ──────►  Cognee │
│                                                                             │
│  • structured        • model           • agent            • codebase    • knowledge
│    extraction         routing            orchestration      semantic       graph
│  • mandatory in     • gateway          • tools            index        • long-term
│    DE pipelines     • all LLM calls     • multi-step         (SQLite)     memory
│  • BAML only                                  reasoning                    • episode
│    structures                                                                 storage
│    payloads
└─────────────────────────────────────────────────────────────────────────────┘
       ▲                                                                       ▲
       │                                                                       │
       └───────── Each layer may call the next layer down; not up ─────────────┘
```

## Layer 1 — BAML (structured extraction in DE)

- **Purpose**: type-safe extraction of structured payloads (Pydantic
  shapes) from unstructured text. BAML is the **structured-extraction
  layer** for the data engineering pipelines.
- **When to use**:
  - You're writing a `@dlt.resource` that needs to parse a curriculum
    document.
  - You're writing a CocoIndex flow that needs a typed output.
  - You're writing a cognify step that needs entities.
- **When NOT to use**:
  - You need a free-form chat completion with an agent → use **ADK/AGNO**
    which calls litellm directly.
  - You need a one-line completion that doesn't need structure → use
    litellm directly.
- **Where it lives**: `oideachais/baml_src/`, `meaisínfhoghlaim/baml_src/`.
- **Compiled client**: `baml_client/`.

## Layer 2 — litellm (LLM routing)

- **Purpose**: model-routing proxy. All LLM calls go through litellm
  (or through ADK/AGNO which calls litellm). The platform runs
  litellm as a Docker stack at `infrastructure/stacks/engineering/litellm/`.
- **When to use**:
  - You need to call an LLM outside of BAML.
  - You're in an agent step that needs a free-form completion.
  - You want to swap models (DeepSeek V4 Pro, Claude, Gemini, etc.)
    without changing call sites.
- **Where it lives**:
  - Server: `infrastructure/stacks/engineering/litellm/`
  - Python client: `litellm` package (in `oideachais/pyproject.toml`).
  - Config: `infrastructure/stacks/engineering/litellm/litellm_config.yaml`.
- **Models available**: see the litellm config; primary is
  `deepseek-v4-pro` via OpenCode Go.

## Layer 3 — ADK / AGNO (agent orchestration)

- **Purpose**: multi-step agent workflows with tool calls. Two
  frameworks are available; pick the one that fits.
- **ADK (Google ADK)**:
  - When to use: agents that need a strict, typed, multi-step
    orchestration graph. The ADK agent framework is the canonical
    choice for `oideachais/agents/`.
  - Where it lives: `oideachais/agents/adk/`.
- **AGNO**:
  - When to use: agents that need a lighter, more flexible,
    Python-first orchestration. Better for ad-hoc research
    agents, multi-modal agents, etc.
  - Where it lives: `oideachais/agents/agno/`.
- **Both call litellm** under the hood. They never call BAML directly
  (BAML is a layer below the agents).
- **Both may call ccc** (see next) for codebase-grounded reasoning.

## Layer 4 — ccc cocoindex-code (semantic index over the codebase)

- **Purpose**: a SQLite vector index of the entire monorepo's source
  code, used by agent skills to find the right file at runtime.
  The CLI is `ccc` (lowercase). The index is at `.cocoindex_code/`.
- **Important**: this is **different** from the uppercase
  `CocoIndex` framework (used for **document** embeddings in
  `oideachais/cocoindex_flows/`). The lowercase `ccc` is the
  *codebase* search; the uppercase `CocoIndex` is the *document*
  embedding flow.
- **When to use**:
  - An agent skill is invoked and the runtime needs to find the
    right file (e.g. "where is the DLT destinations factory?").
  - You're writing a new agent skill and you need the agent to
    ground its responses in the actual codebase.
- **Where it lives**:
  - CLI: `ccc` (installed via mise).
  - Index: `.cocoindex_code/target_sqlite.db` (regenerable via
    `bun run ccc:index`).
  - Config: `mise.toml` + `bun run ccc:search "..."`.
- **Maintained by**: `infrastructure/stacks/engineering/` (no compose;
  CLI-only).

## Layer 5 — Cognee (knowledge graph memory)

- **Purpose**: the long-term knowledge graph. After BAML extracts
  entities, Cognee stores them as nodes/edges and exposes them
  for retrieval.
- **When to use**:
  - You have extracted entities and want a queryable graph.
  - You want episodic memory (e.g. "what did the agent learn last
    week about NCCA?").
- **When NOT to use**:
  - You just want vector search over a corpus → use **LanceDB**
    (which is downstream of CocoIndex, not Cognee).
- **Where it lives**:
  - Stack: `infrastructure/stacks/machine_learning/cognee/`.
  - Python client: `cognee` package.
  - Datasets: `oideachais_cognee_integration/` registers one
    dataset per domain.
- **Alternative**: Graphiti (bi-temporal). See
  [`docs/00-core/graphiti.md`](../00-core/graphiti.md).

## Calling order

- BAML is a **library** called from DLT resources, CocoIndex flows,
  and cognify steps. It does not call the other layers.
- litellm is a **service** (and a Python client). All other layers
  call it. It is the model-routing layer.
- ADK / AGNO call litellm (for chat) and may call ccc (for codebase
  search). They do not call BAML or Cognee directly.
- ccc is a **service** (the CLI). Called by agents (ADK/AGNO) and by
  the `mise` task `ccc:search`.
- Cognee is a **service** + Python client. Called by the
  `oideachais/cognee_integration/` layer (which is a BAML → Cognee
  pipeline) and by the Dagster cognify assets.

## Common mistakes

- Calling a free-form prompt from a `@dlt.resource` directly via
  litellm. → Use BAML; the prompt should be a BAML function.
- Calling BAML from an ADK agent step. → Use litellm; the agent
  needs free-form text, BAML is for structured extraction.
- Skipping ccc and asking an agent "where is X in the codebase?". →
  The agent should call `bun run ccc:search "X"` first; the ccc index
  is the canonical answer.
- Using Cognee for vector search. → Use LanceDB. Cognee is the
  graph; LanceDB is the vector store.

## See also

- [`docs/01-patterns/BAML.md`](../01-patterns/BAML.md) — BAML pattern reference
- [`docs/04-ai-ml/knowledge-graphs.md`](../04-ai-ml/knowledge-graphs.md) — KG landscape
- [`docs/01-cognee/COGNEE_INTEGRATION.md`](../01-cognee/COGNEE_INTEGRATION.md) — Cognee setup
- [`oideachais/cognee_integration/`](../../oideachais/cognee_integration/) — Cognee client code
- [`opencode.json`](../../opencode.json) — where the ccc + motherduck + cognee MCP servers are wired
