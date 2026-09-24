---
name: adk2-pillars
description: ADK 2.x router for the 3 Pillar orchestration patterns (Workflow + Collaborative + Dynamic). Use when choosing between Pillar 1 (Workflow graphs), Pillar 2 (Collaborative sub_agents + mode='single_turn'), or Pillar 3 (Dynamic @node(parallel_worker=True) + recursive ctx.run_node). Triggers: 'adk 2', 'pillar 1', 'pillar 2', 'pillar 3', 'workflow graph', 'collaborative', 'parallel_worker', 'deep research', 'dynamic workflow'.
---

# ADK 2 Pillars — the 3 orchestration patterns

Per openspec/changes/2026-09-23-upgrade-to-adk2-pillars-1-2-3-v1/.
Pattern source: `docs/google_examples/adk2-tutorial/` (10-level runnable).

## The axis: who decides what runs next?

| Pillar | Who decides what runs next | Built in |
|---|---|---|
| **1 · Workflow** | the graph you drew | L1 + L2a/L2b |
| **2 · Collaborative** | the LLM | L3a/L3b |
| **3 · Dynamic** | your Python code, at runtime | L4a/L4b |

## Pillar 1 — Workflow graphs

When: predictable structure known at design time.

```python
from google.adk import Agent, Workflow
from google.adk.workflow import START

def plan_today(ctx, node_input):  # function node, 0 LLM
    return Event(output={"day_iso": ...})

workflow = Workflow(
    name="teacher_daily",
    edges=[(START, plan_today, lesson_planner, assessment_scorer, sen_pastoral)],
)
```

Cheap rule: "Does a prebuilt SequentialAgent / ParallelAgent / LoopAgent do?"
If yes → use it; reach past it when you need explicit routing, joins, or
non-agent nodes.

## Pillar 2 — Collaborative agents

When: known team, request decides the subset.

```python
teacher_root = Agent(
    name="teacher_root",
    model="gemini-2.5-flash",
    sub_agents=[lesson_planner, assessment_scorer, sen_pastoral, parent_meeting, pro_learning],
    mode="single_turn",  # ★ the parallel-collaborative flag
    instruction="...",
)
```

Two mode flags:
- `mode="single_turn"` — coordinator delegates to multiple specialists in
  ONE turn, synthesizes one answer (L3a beat 2).
- `mode="task"` — coordinator + 1 specialist, conversation until schema
  validates, then return (L3b).

## Pillar 3 — Dynamic workflows

When: shape depends on input.

```python
from google.adk.workflow import RetryConfig, START, node

@node(parallel_worker=True, retry_config=RetryConfig(max_attempts=3))
async def research_topic(ctx, node_input):
    finding = await ctx.run_node(research_agent, node_input=node_input["question"])
    yield Event(output={"question": ..., "summary": finding.summary})
```

Cheap rule: "Let the LLM shape the work, but keep the boundaries in code"
(depth, width, budget).

## The 1.x → 2.x delta

1.x could build all of this. The shift: **2.x gives each shape a more direct
home**, so known control flow leaves the prompt and becomes structure you
can see and test.

| Pattern | 1.x way | 2.x home |
|---|---|---|
| Graph (Pillar 1) | wrap steps in LlmAgent (4 LLM calls) | function + agent nodes as peers → 1 LLM |
| Collaborative (Pillar 2) | wrap specialists in AgentTool by hand | `sub_agents=[...]` + `mode="single_turn"` |
| Dynamic (Pillar 3) | raw `asyncio` drops you out of the framework | `@node(parallel_worker=True)` + recursive `ctx.run_node` |

## The cianfhoghlaim application

| Pipeline | Pillar | Module |
|---|---|---|
| teacher_daily_workflow | Pillar 1 | `agents/workflows/teacher_daily_workflow.py` |
| student_secondary_workflow | Pillar 1 | `agents/workflows/student_secondary_workflow.py` |
| tertiary_personal_workflow | Pillar 1 | `agents/workflows/tertiary_personal_workflow.py` |
| teacher_root + student_root + students_union_root | Pillar 2 | `agents/meaisinfhoghlaim/educational/{teachers,students_jc,students_union}/_root.py` |
| aistear_deep_research + primary + jc + sc + tertiary | Pillar 3 | `agents/workflows/{stage}_deep_research.py` |

## Reference

- `docs/google_examples/adk2-tutorial/L1_graph_basics/workflow.py` — the L1 graph
- `docs/google_examples/adk2-tutorial/L2a_parallel_join/workflow.py` — parallel fan-out + JoinNode
- `docs/google_examples/adk2-tutorial/L3a_collaborative/concierge.py` — single_turn
- `docs/google_examples/adk2-tutorial/L3b_task_desk/desk.py` — task mode
- `docs/google_examples/adk2-tutorial/L4a_flat_research/deep_research.py` — @node(parallel_worker=True)
- `docs/google_examples/adk2-tutorial/L4b_recursion/deep_research.py` — recursive ctx.run_node
- `docs/google_examples/adk2-tutorial/L5_capstone/README.md` — the decision tree
- `docs/google_examples/agent-valley-archive/README.md` — the 4-floor memory ladder twin
