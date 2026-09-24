# Cross-repo sync: 2026-09-23-upgrade-to-adk2-pillars-1-2-3-v1

This change touches ONLY `cianfhoghlaim/`. No sister-repo coordination required.

## Files touched (all in cianfhoghlaim/)

- `pyproject.toml` — bump `google-adk>=1.17.0` → `google-adk>=2.5.0,<3`
- `agents/agent_registry.py` — register 10 new fleet entries (priority 15-24)
- `agents/routing_keywords.py` — add 10 new keyword buckets
- `agents/meaisinfhoghlaim/educational/students_union/root_agent.py` — add `mode="single_turn"`
- The 24 existing agents: unchanged at the source level (ADK 1.x LlmAgent + FunctionTool are backwards-compatible under ADK 2.x)

## Order of operations

1. **cianfhoghlaim commits + archives** the change (single-repo)
2. **Push to origin/openspec/cianchosaint-handoff-v1**

No ciandlithe or other sister-repo coordination required.

## Verification

```bash
# 1. ADK 2 + the 3 Pillars preflight
uv run python scripts/preflight_education.py
# Expected: exit 0 (5 rows pass)

# 2. Walk the 5 chapters end-to-end
uv run python scripts/walk_education.py
# Expected: exit 0 (all 5 chapters pass)

# 3. Openspec strict validation
openspec validate 2026-09-23-upgrade-to-adk2-pillars-1-2-3-v1 --strict
# Expected: exit 0

# 4. AST parse the 8 workflow files
python3 -c "import ast, glob; [ast.parse(open(f).read()) for f in glob.glob('agents/workflows/*.py')]"
# Expected: exit 0
```
