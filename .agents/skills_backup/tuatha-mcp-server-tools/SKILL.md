---
name: tuatha-mcp-server-tools
description: The KCG Tuatha MCP server tools in `sruth/tuatha/agents/mcp_server/`. Covers the 5 tools (search_curriculum, get_learning_outcomes, search_mythology, get_character_lore, get_location_lore), the `sruth/oideachais/agents/adk/tools/tuatha_*` shim pattern (the canonical home for the 5 tools), the broken-import bug at `sruth/tuatha/agents/mcp_server/server.py:23-33` (the `from ..tools.X` imports fail because `sruth/tuatha/agents/tools/` does not exist), the MCP server name (`tuatha-education`), the 4 MCP transports (stdio / SSE / WebSocket / HTTP), and the canonical add-a-new-tool workflow. Use when adding a new MCP tool, debugging the broken-import bug, wiring a new MCP transport, or onboarding a new CopilotKit AG-UI client that needs the Celtic domain tools.
---

# Tuatha MCP Server Tools

## Purpose

The `sruth/tuatha/agents/mcp_server/` directory houses the **MCP
(Model Context Protocol) server** that exposes the 5 Celtic
domain tools to external clients (the TanStack Start CopilotKit
AG-UI consumer, the MEOBots orchestrator, the OpenCode Go
agents). This skill captures the 5 tools + the canonical home
for the tool implementations + the broken-import bug + the
add-a-new-tool workflow.

## When to use this skill

Use when you need to:

- "Add a new MCP tool"
- "Debug the broken-import bug in `sruth/tuatha/agents/mcp_server/server.py`"
- "Wire a new MCP transport (stdio / SSE / WebSocket / HTTP)"
- "Onboard a new CopilotKit AG-UI client that needs the Celtic domain tools"
- "Understand the 5 tools + the canonical home"

## The 5 tools (the surface)

| Tool | Signature | Returns | Source |
|:--|:--|:--|:--|
| `search_curriculum` | `(query: str, nation: str \| None = None, level: str \| None = None) -> List[dict]` | The top-5 curriculum results from the LanceDB `leabharlann_*` tables | `sruth/oideachais/agents/adk/tools/tuatha_curriculum_search.py:search_curriculum` |
| `get_learning_outcomes` | `(topic: str, nation: str \| None = None, level: str \| None = None) -> List[dict]` | The learning outcomes for the topic across the 5 frameworks | `sruth/oideachais/agents/adk/tools/tuatha_curriculum_search.py:get_learning_outcomes` |
| `search_mythology` | `(query: str, tradition: str \| None = None, cycle: str \| None = None) -> List[dict]` | The top-5 mythology results from the `tuatha_mythology` LanceDB table | `sruth/oideachais/agents/adk/tools/tuatha_mythology_query.py:search_mythology` |
| `get_character_lore` | `(character_name: str) -> List[dict]` | The lore for the character across the Pent-Elemental Cosmology | `sruth/oideachais/agents/adk/tools/tuatha_mythology_query.py:get_character_lore` |
| `get_location_lore` | `(location_name: str, tradition: str \| None = None) -> List[dict]` | The lore for the location | `sruth/oideachais/agents/adk/tools/tuatha_mythology_query.py:get_location_lore` |

The 5 tools are exposed by the MCP server at
`sruth/tuatha/agents/mcp_server/server.py:server = Server("tuatha-education")`.

## The canonical tool home (the shim pattern)

The 5 tool implementations live at
**`sruth/oideachais/agents/adk/tools/tuatha_*.py`** (the canonical home,
per the 6-phase refactor pattern). The `sruth/tuatha/agents/tools/`
directory was historically the home but has been deprecated (per
Phase 5 of the refactor plan).

The canonical shim pattern:

```python
# sruth/oideachais/agents/adk/tools/tuatha_curriculum_search.py
from sruth.oideachais.cocoindex_flows.leabharlann_embedding import (
    search_leabharlann_books,
    search_leabharlann_zotero,
    search_leabharlann_takeout,
)
# ... the canonical implementation
```

The `sruth/tuatha/agents/mcp_server/server.py` does:

```python
# WRONG (broken):
from ..tools.curriculum_search import search_curriculum
# (this fails because sruth/tuatha/agents/tools/ doesn't exist)

# RIGHT (canonical shim):
from sruth.oideachais.agents.adk.tools.tuatha_curriculum_search import (
    search_curriculum,
    get_learning_outcomes,
)
```

The wrong import is the **broken-import bug** at lines 23-33 of
`sruth/tuatha/agents/mcp_server/server.py` (per the
`sruth/tuatha/agents/mcp_server/server.py:23-33` docstring in the
subagent's report).

## The fix (the 3 shim files)

The fix is to create 3 shim files in `sruth/tuatha/agents/tools/`:

```python
# sruth/tuatha/agents/tools/__init__.py
# Thin re-export shim (round 7 phase 5 of the 6-phase refactor).
# Canonical home: oideachais.agents.adk.tools.tuatha_*
from sruth.oideachais.agents.adk.tools.tuatha_curriculum_search import (
    search_curriculum, get_learning_outcomes, CurriculumSearchResults,
    OIDEACHAIS_LANCEDB_PATH,
)
from sruth.oideachais.agents.adk.tools.tuatha_mythology_query import (
    search_mythology, get_character_lore, get_location_lore,
)
__all__ = [
    "search_curriculum", "get_learning_outcomes", "CurriculumSearchResults", "OIDEACHAIS_LANCEDB_PATH",
    "search_mythology", "get_character_lore", "get_location_lore",
]
```

```python
# sruth/tuatha/agents/tools/curriculum_search.py
# Re-export shim. See __init__.py for the canonical home.
from sruth.oideachais.agents.adk.tools.tuatha_curriculum_search import (
    search_curriculum, get_learning_outcomes, CurriculumSearchResults,
    OIDEACHAIS_LANCEDB_PATH,
)
__all__ = ["search_curriculum", "get_learning_outcomes", "CurriculumSearchResults", "OIDEACHAIS_LANCEDB_PATH"]
```

```python
# sruth/tuatha/agents/tools/mythology_query.py
# Re-export shim. See __init__.py for the canonical home.
from sruth.oideachais.agents.adk.tools.tuatha_mythology_query import (
    search_mythology, get_character_lore, get_location_lore,
)
__all__ = ["search_mythology", "get_character_lore", "get_location_lore"]
```

The 3 shim files preserve the `from ..tools.X` import pattern in
`server.py` while pointing at the canonical home.

## The 4 MCP transports (the runtime)

The MCP server supports 4 transports:

| Transport | Port | Use case |
|:--|--:|:--|
| `stdio` | (stdin/stdout) | The TanStack Start CopilotKit consumer (in-process) |
| `SSE` | 8765 | The MEOBots orchestrator (long-running clients) |
| `WebSocket` | 8766 | The real-time Web clients (the Babylon.js front-end) |
| `HTTP` | 8767 | The curl-friendly debugging clients |

The transport is selected at startup via the `--transport` CLI
flag:

```bash
uv run python -m tuatha.agents.mcp_server.server --transport=stdio
uv run python -m tuatha.agents.mcp_server.server --transport=SSE --port=8765
```

## The server name (the canonical identifier)

The MCP server is registered as `tuatha-education` (the canonical
identifier in the MCP protocol). The 5 tools are namespaced under
`tuatha-education:search_curriculum`, `tuatha-education:search_mythology`, etc.

## Worked example: add a new MCP tool

1. Add the tool implementation at
   `sruth/oideachais/agents/adk/tools/tuatha_achievement_query.py`:

   ```python
   async def get_player_badges(
       player_id: str,
       framework: str | None = None,
       limit: int = 10,
   ) -> list[dict]:
       """Get a player's skill-tree badges (the Phase 6 achievement ledger)."""
       from tuatha.crypteolas.achievements.ledger import AchievementLedger
       return await AchievementLedger.list_badges(
           player_id=player_id,
           framework=framework,
           limit=limit,
       )
   ```

2. Add the shim at `sruth/tuatha/agents/tools/achievement_query.py`:

   ```python
   from sruth.oideachais.agents.adk.tools.tuatha_achievement_query import (
       get_player_badges,
   )
   __all__ = ["get_player_badges"]
   ```

3. Add the tool to the MCP server at
   `sruth/tuatha/agents/mcp_server/server.py`:

   ```python
   from ..tools.achievement_query import get_player_badges

   @server.list_tools()
   async def list_tools() -> list[Tool]:
       return [
           # ... the 5 existing tools
           Tool(
               name="get_player_badges",
               description="Get a player's skill-tree badges from the achievement ledger",
               inputSchema={
                   "type": "object",
                   "properties": {
                       "player_id": {"type": "string"},
                       "framework": {"type": "string"},
                       "limit": {"type": "integer", "default": 10},
                   },
                   "required": ["player_id"],
               },
           ),
       ]

   @server.call_tool()
   async def call_tool(name: str, arguments: dict) -> list[TextContent]:
       if name == "get_player_badges":
           result = await get_player_badges(**arguments)
           return [TextContent(type="text", text=json.dumps(result))]
       # ... the 5 existing tools
   ```

4. Update the openspec change `tuatha-achievement-ledger-v1` to
   document the 6th tool.

## Common failure modes

| Symptom | Cause | Fix |
|:--|:--|:--|
| `ModuleNotFoundError: No module named 'tuatha.agents.tools'` | The 3 shim files are missing | Create the 3 shim files at `sruth/tuatha/agents/tools/{__init__,curriculum_search,mythology_query}.py` |
| The MCP server hangs at startup | The transport is not set | Pass `--transport=stdio` (or one of the 4) |
| The tool returns an empty list | The LanceDB table is empty | Run `mise run locket:exec -- uv run oideachais cocoindex update oideachais.cocoindex_flows.leabharlann_embedding:LeabharlannBooksApp` |
| The tool signature is wrong | The MCP client sends the wrong types | Add a `validate_arguments` call at the start of the tool function |
| The tool hangs | The LanceDB query is too slow | Add a `timeout=5.0` parameter to the LanceDB query |

## Cross-references

- `.agents/skills/tuatha-mmo/SKILL.md` — the MMO tech stack
- `.agents/skills/mcp-builder/SKILL.md` — the general MCP patterns
- `.agents/skills/british-isles-formative-assessment/SKILL.md` — the 5 frameworks
- `.agents/skills/tuatha-achievement-ledger/SKILL.md` — the achievement ledger (the 6th tool's home)
- `sruth/oideachais/agents/adk/tools/tuatha_curriculum_search.py` — the canonical home for the 2 curriculum tools
- `sruth/oideachais/agents/adk/tools/tuatha_mythology_query.py` — the canonical home for the 3 mythology tools
- `sruth/oideachais/agents/adk/tools/tuatha_achievement_query.py` — the canonical home for the 6th tool (achievement query)
- `sruth/tuatha/agents/tools/{__init__,curriculum_search,mythology_query}.py` — the 3 shim files
- `sruth/tuatha/agents/mcp_server/server.py` — the MCP server (line 23-33 is the broken-import bug)
- `sruth/tuatha/agents/mcp_server/__init__.py` — the server module home
- `openspec/specs/tuatha-platform/spec.md` — the canonical spec
