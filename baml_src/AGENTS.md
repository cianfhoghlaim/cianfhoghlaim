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

## The 18 domain templates (per the 2026-12-XX-mega-3d-baml-quality-v1 change)

The canonical 18 domain-specific BAML prompt templates live at
`baml_src/_shared/templates/`. Each template is a high-quality
extractor prompt body that replaces the historical
`"Auto-generated extraction prompt."` stub.

| Pattern | Convention |
|:--|:--|
| **Stub replacement** | Every `Extract*` function MUST have a substantive prompt body (no `Auto-generated extraction prompt.` stubs). Enforced by `python scripts/lint_baml_stub_prompts.py`. |
| **Catch coverage** | Every `Extract*` function MUST have a `catch_all` block that emits a safe-default value for the return type. Enforced by `python scripts/lint_baml_catch_coverage.py`. |
| **BAML 0.223.0 features** | Use `_.role("user")`, `ctx.output_format`, `{% if %}` branching, `catch_all`, `TypeBuilder`, `@stream.done`, `@assert`, and dynamic schemas where appropriate. |
| **Reference path** | Read the canonical templates at `baml_src/_shared/templates/<domain>.baml` when adding new extraction functions. |

To regenerate the 18 templates from scratch:
```bash
python scripts/baml_generate_templates.py
```

To re-apply the stub-replacement + catch-block sweep:
```bash
python scripts/baml_bulk_replace_stubs.py
python scripts/baml_bulk_add_catch.py
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

## Data platform router

> **The single router for the 5 per-area data platform docs** is at [`../dlt_sources/DATA_PLATFORM_ROUTER.md`](../dlt_sources/DATA_PLATFORM_ROUTER.md). Documents the 6 critical conventions (relative imports / `USE_LOCAL_SCRAPES` / zero absolute namespaces / R1-R4 conformance / MODEL_REGISTRY-only / factory pattern) that apply ACROSS all 5 sub-packages.

<!-- generated: 2026-07-29; do not hand-edit -->
