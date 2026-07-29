# agents/tools — Tool Modules

> **The 9 tool modules** for the agent fleet. The tools layer
> provides the agent-callable functions for curriculum search,
> corpus lookup, geospatial analysis, statistics computation,
> terminology lookup, spatial queries, and translation.

## Priority quick reference

### Priority skills (3 of 53)

| Skill | When to load |
|:--|:--|
| [`dignified-python`](../.agents/skills/dignified-python/SKILL.md) | Production Python standards for tool modules |
| [`agent-registry`](../.agents/skills/agent-registry/SKILL.md) | The 12-agent fleet dispatch |
| [`baml`](../.agents/skills/baml/SKILL.md) | BAML extraction patterns for tool outputs |

### Priority commands

```bash
# List the 9 tool modules
ls agents/tools/*.py
# Expected: 9 .py files (corpus_search.py, corpus_tools.py,
#           curriculum_search.py, curriculum_tools.py,
#           geospatial_tools.py, spatial_query.py,
#           statistics_query.py, terminology.py,
#           translation_tools.py)
```

### Priority openspec spec

| Spec | One-liner |
|:--|:--|
| `agent-registry` | The 12-agent fleet dispatch |

## Overview

`agents/tools/` is the **tools layer** for the agent fleet. It
houses the 9 tool modules that the 12 main agents call to
perform their work.

## The 9 tool modules

| Module | Purpose | Used by |
|:--|:--|:--|
| `corpus_search.py` | The Dúchas + Gaois + UD + Canúint + Téarma corpus search | `corpus_agent` |
| `corpus_tools.py` | The corpus helper tools (dictionary lookup, document retrieval) | `corpus_agent` |
| `curriculum_search.py` | The 5-nation curriculum search (NCCA + CfE + CfW + CCEA + SQA) | `curriculum_agent`, `curriculum_comparison_agent` |
| `curriculum_tools.py` | The curriculum helper tools (syllabus lookup, learning outcome mapping) | `curriculum_agent`, `mcp_curriculum_agent` |
| `geospatial_tools.py` | The LSOA / Data Zone spatial analysis tools | `geospatial_agent` |
| `spatial_query.py` | The spatial query helpers (PostGIS, GeoPackage) | `geospatial_agent` |
| `statistics_query.py` | The education metrics + benchmarking computation | `statistics_agent` |
| `terminology.py` | The 6-Celtic-language terminology lookup | `translation_agent` |
| `translation_tools.py` | The Celtic translation helpers (GaBERT, Helsinki OPUS-MT, NLLB-200) | `translation_agent` |

## The dispatch pattern

Each tool module exposes a flat set of functions that the agents
call directly. The pattern is:

```python
# agents/tools/curriculum_search.py
def search_curriculum(query: str, *, jurisdiction: str = "ireland") -> dict:
    """Search the 5-nation curriculum corpus."""
    ...

def get_learning_outcomes(subject: str, level: str) -> list[dict]:
    """Return the canonical learning outcomes for a subject × level."""
    ...
```

The 12 agents import these functions and call them directly:

```python
# agents/adk/curriculum_agent.py
from cianfhoghlaim.agents.tools.curriculum_search import search_curriculum

result = search_curriculum("What is the LC Irish syllabus?")
```

## Adding a new tool module

To add a new tool module:

1. **Create the module** at `agents/tools/<name>.py`
2. **Expose 3-5 functions** (the canonical pattern is 3-5 functions per module)
3. **Type-hint everything** (Pydantic v2 types where appropriate)
4. **Document each function** with a docstring that includes:
   - Purpose (1 sentence)
   - Parameters (1 sentence each)
   - Returns (1 sentence)
   - Example (1 code block)
5. **Wire to the agent** by importing the function in the agent module
6. **Add to AGENT_REGISTRY** if the tool is agent-scoped (not needed for shared tools)

## Cross-references

- [`agents/AGENTS.md`](../AGENTS.md) — the quadrant overview
- [`agents/api/AGENTS.md`](../api/AGENTS.md) — the Hono API layer
- [`agents/meaisinfhoghlaim/AGENTS.md`](../meaisinfhoghlaim/AGENTS.md) — the OCR/HTR sub-package
- [`dignified-python/SKILL.md`](../.agents/skills/dignified-python/SKILL.md) — production Python standards