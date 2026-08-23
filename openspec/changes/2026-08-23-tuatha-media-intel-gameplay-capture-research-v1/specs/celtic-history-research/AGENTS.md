# `celtic-history-research` — Agent Routing

> The 9 Celtic-history research stub sources — the Tuatha Dé
> Danann, Irish mythology, Celtic mythology, Celtic law, Brehon
> law, Aran Islands, Isle of Skye, Isle of Man, Dyfed topics.
> GATED for the downstream Celtic-MMO theming change.

## Routing

Load this AGENTS.md when:

- You activate a Celtic-history stub source (the downstream
  theming change)
- You add a new Celtic-history topic to the sub-package
- You replace the user's clippings directory content with a
  new ingestion

For platform-wide context, load
[`../../../AGENTS.md`](../../../AGENTS.md).

## Quick start

```bash
# Validate the spec
openspec validate 2026-08-23-tuatha-media-intel-gameplay-capture-research-v1 --strict

# The 9 stub sources are GATED; activating requires a downstream
# Celtic-MMO theming change that flips the `status: stub` to
# `status: active` in the per-source `source.yaml`.
```

## Key sources

- `openspec/specs/celtic-history-research/spec.md` — the canonical
  spec
- `dlt_sources/media/celtic_history_research/{topic}/source.yaml`
  — the 9 stub source manifests
- `dlt_sources/media/celtic_history_research/{topic}/scrape.py` —
  the 9 no-op scrape resources (yield zero rows)
- The user's canonical source for the future theming change:
  `cian_mac_an_déisigh_uí_liatháin/identity/lineage/references/clippings/`

## Adjacent specs

- [`../media-intel-corpus/spec.md`](../media-intel-corpus/spec.md)
  — the 7-axis `MediaDescriptor` schema (consumed by every
  Celtic-history stub once activated)
- [`../media-intel-acquisition-plan/spec.md`](../media-intel-acquisition-plan/spec.md)
  — the 5-class source acquisition plan (Class E — Official
  exclusively; the 9 Celtic-history topics do NOT belong in
  Class E)
- [`../../centralized-schema-registry/spec.md`](../../centralized-schema-registry/spec.md)
  — the BAML-as-source-of-truth contract (the per-source
  `BAML function set` is empty for the 9 stubs)

## DO NOT

- **Never** add any of the 9 Celtic-history topics to the Class E
  (official) surface — they live exclusively in this sub-package
- **Never** activate a stub without the downstream Celtic-MMO
  theming change archiving first
- **Never** change the `licence` from `CC-BY-SA-4.0` (Wikipedia
  attribution preserved)
- **Never** use any model string in the stub — they are gated
  (`baml_functions: []`)

## Skill pointers

| Skill | When to load |
|:--|:--|
| [`centralized-registry`](../.agents/skills/centralized-registry/SKILL.md) | MODEL_REGISTRY + schema + codegen patterns |
| [`dlt`](../.agents/skills/dlt/SKILL.md) | DLT source patterns + the `source.yaml` manifest |
| [`celtic-asset-generation`](../.agents/skills/celtic-asset-generation/SKILL.md) | The 4-pipeline Celtic asset generation (gated until the corpus is populated) |
| [`british-isles-formative-assessment`](../.agents/skills/british-isles-formative-assessment/SKILL.md) | The 5 curriculum frameworks + the 4 feedback channels |

<!-- generated: 2026-08-23 by 2026-08-23-tuatha-media-intel-gameplay-capture-research-v1; do not hand-edit -->
