# `baml_src/` — BAML Extraction Schemas

> **The 320 BAML files for the Cianfhoghlaim platform — 558 functions, 838 classes, 288 enums, 33 LLM clients (all routing to `minimax-m3`).** Post-v7 flattening the canonical directory is `baml_src/` (not `baml/`). Jurisdiction-clustered at `./baml_src/{british_isles,european_nations,european_union,commonwealth,american_nations,celtic,processing}/` with a shared `_shared/` and `shared/` home.

## Routing

Load this AGENTS.md when:

- You need to add / modify a BAML extraction function or class
- You need to regenerate the `baml_client/` Python module after a `.baml` change
- You need to wire a BAML client into a dlt source or Dagster asset
- You need to validate the BAML test blocks (the hard CI gate)

For platform-wide context, load [`../AGENTS.md`](../AGENTS.md).

## Quick start

```bash
mise run baml:generate              # Regenerate the baml_client/ Python module from baml_src/
mise run baml:test                  # Run BAML test blocks (hard CI gate)
mise run cic:baml:lint              # Lint all 56+ .baml schema files for consistency
```

## Key sources

| Path | Why it matters |
|:--|:--|
| `baml_src/baml.toml` | The BAML project config (source of truth for `baml:generate`) |
| `baml_src/british_isles/` | The 6 LC subject extraction schemas (Mathematics, Chemistry, Geography, Gaeilge, English, Computer Science) + gov.ie circulars |
| `baml_src/celtic/` | The 6 Celtic-language extraction schemas (Irish, Welsh, Scottish Gaelic, Breton, Cornish, Manx) |
| `baml_src/_shared/` | The shared extraction patterns (cross-linguistic concept, marking scheme, exam layout) |
| `baml_src/clients_llama_swap.baml` | The llama-swap LLM client (serves the v4 Unsloth GGUFs at :8080) |

## Adjacent specs

- [`centralized-schema-registry`](../openspec/specs/centralized-schema-registry/spec.md) — BAML is the single source of truth; Pydantic + Zod are codegen
- [`centralized-model-registry`](../openspec/specs/centralized-model-registry/spec.md) — the 52-entry model registry that the BAML clients route through
- [`british-isles-education-pipeline-v3`](../openspec/specs/british-isles-education-pipeline-v3/spec.md) — the BIEP v3 consumer of the 6 LC subject BAML schemas
- [`celtic-language-pipeline`](../openspec/specs/celtic-language-pipeline/spec.md) — the 6 Celtic-language consumer

## DO NOT

- **Never** hand-write a Pydantic model that duplicates a BAML class — codegen it from `.baml`.
- **Never** import `from cianfhoghlaim.baml...` before running `mise run baml:generate` (the client module doesn't exist).
- **Never** edit a generated file in `baml_client/` — it's regenerated on every `baml:generate`.

## Skill pointers

| Skill | When to load |
|:--|:--|
| [`baml`](../.agents/skills/baml/SKILL.md) | BAML v0.223.0 schema authoring + the 5 canonical lc6 extraction functions |
| [`centralized-registry`](../.agents/skills/centralized-registry/SKILL.md) | The model + schema registry pattern |
| [`ccc`](../.agents/skills/ccc/SKILL.md) | Semantic code search across the BAML + Python client |
| [`motherduck`](../.agents/skills/motherduck/SKILL.md) | The BIEP lakehouse that the BAML outputs land in |

<!-- generated: 2026-07-29; do not hand-edit -->
