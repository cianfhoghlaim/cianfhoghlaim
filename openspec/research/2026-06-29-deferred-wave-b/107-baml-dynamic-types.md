# 107 - BAML Dynamic Types (deferred site)

**Status:** Researched 2026-06-29 via firecrawl MCP
**Canonical source:** https://docs.boundaryml.com/guide/baml-advanced/dynamic-types
**Cianfhoghlaim footprint:** 75 .baml files in
`cianfhoghlaim/core/baml/_*_src/`; the new v4 home is
`cianfhoghlaim/core/baml/shared/` (per Phase 2.1 of the per-domain
BAML merger).

## TL;DR

BAML's `TypeBuilder` is the runtime-injected types mechanism that
lets you add or modify class properties / enum variants AFTER the
.baml file has been compiled. This is the recommended pattern for
schemas that depend on runtime data (DB rows, user input, JSON
Schema).

**The 3 use cases for cianfhoghlaim:**
1. **Category classifier** — categories come from a DB table
2. **Custom tool calls** — ChatResponse tools are user-defined
3. **Adaptive syllabus** — learning outcomes vary by NCCA stage

## Code

```baml
// In baml_src/dynamic_curriculum.baml
enum LearningOutcome {
  READING // static
  WRITING
  @@dynamic // can be extended at runtime
}

function ExtractOutcomes(text: string) -> LearningOutcome[] {
  client DefaultLiteLLM
  prompt #"Extract from {{ text }}{{ ctx.output_format }}"#
}
```

```python
# In cianfhoghlaim/core/baml/dynamic_runtime.py
from baml_client.type_builder import TypeBuilder
from baml_client import b

async def adaptive_extract(text: str, ncca_stage: str):
    tb = TypeBuilder()
    # Add the NCCA-stage-specific outcomes at runtime
    outcomes = fetch_outcomes_for_stage(ncca_stage)  # DB query
    for outcome in outcomes:
        tb.LearningOutcome.add_value(outcome.name)
    return await b.ExtractOutcomes(text, {"tb": tb})
```

## Env

- No new env vars (BAML clients already configured in
  `shared/baml_src/clients.baml` per Phase 2.1)
- `baml-cli` 0.222+ for the `TypeBuilder.add_baml()` API

## ccc anchors

- `baml` skill at `.agents/skills/baml/SKILL.md` (Pattern 2 + Pattern 7)
- `celtic-asset-generation` skill (Pattern 8: dynamic BAML for
  adaptive syllabi)
- The new `shared/baml_src/clients.baml` (7 clients, 3 retry
  policies) from Phase 2.1

## Anti-patterns

- **Hardcoding schemas for one-off sources** — use `TypeBuilder` to
  generate the schema at runtime
- **Mutating a non-`@@dynamic` class** — TypeBuilder cannot add
  properties to static classes; you must declare `@@dynamic`
- **Building TypeBuilder in a hot path** — instantiate once at
  module load, mutate per call (TypeBuilder is mutable)
- **Skipping the test `type_builder` block** — every BAML function
  that uses dynamic types should have at least one test with a
  `type_builder` block

## Decision matrix

| Use TypeBuilder when | Use static .baml when | Use Firecrawl `json` when |
|:--|:--|:--|
| Schema comes from a DB | Schema is fixed at compile time | Schema is content-derived |
| Schema is user-defined | Schema is content-derived | No Pydantic model needed |
| Schema varies per request | Schema is shared across requests | One-off extraction |
| Test-time schema injection | Production schema is fixed | External website scraping |
