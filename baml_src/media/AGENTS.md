# `baml_src/media/` — TG4 + Foghlaim Media Classification BAML

> The 4 BAML extraction functions that power the TG4 + Foghlaim
> multimodal embedding pipeline (the `tg4-foghlaim-corpus`
> capability). Added by the `2026-08-25-tg4-foghlaim-corpus-v1` change.

## Routing

Load this AGENTS.md when:

- You need to add / modify a BAML fn that processes TG4 or Foghlaim content
- You need to extend the BIEP subject taxonomy (the canonical slug list)
- You need to tune the `AuditTranscriptQuality` thresholds
- You need to extend `ExtractWorksheetAnswers` to a new worksheet format

## Quick start

```bash
# Regenerate the BAML client + Python types after editing tg4_classification.baml
mise run baml:generate

# Run the BAML test suite for the 4 functions
mise run baml:test

# Validate against the openspec change
openspec validate 2026-08-25-tg4-foghlaim-corpus-v1 --strict
```

## Key sources

| Path | Why it matters |
|:--|:--|
| `baml_src/media/tg4_classification.baml` | The 4 BAML fns + 4 Pydantic classes |
| `baml_src/clients.baml` | The shared client<llm> blocks (routes via MODEL_REGISTRY) |

## The 4 BAML functions

| Function | Input | Output | Called by |
|:--|:--|:--|:--|
| `ClassifyTg4Episode` | episode metadata + Foghlaim context | `Tg4EpisodeClassification` (biep_subject, dialect, irish_purity_score, ...) | v1 App per episode |
| `ExtractSpeakerLineup` | VTT cues JSON | `SpeakerLineup` (speakers + turns) | v1 App per episode |
| `ExtractWorksheetAnswers` | worksheet PNG URL | `WorksheetAnswers` (questions + marks + Bloom level) | v1 App per `has_worksheet=true` lesson |
| `AuditTranscriptQuality` | VTT + WhisperX JSON | `TranscriptQualityAudit` (coverage + disagreement + insertion rate) | v1 App on 5% sample + every NCCA-tagged lesson |

## Adjacent specs

- [`tg4-foghlaim-corpus`](../../openspec/specs/tg4-foghlaim-corpus/spec.md)
  — the parent capability spec
- [`centralized-model-registry`](../../openspec/specs/centralized-model-registry/spec.md)
  — every client<llm> block routes via MODEL_REGISTRY (no literal
  HuggingFace IDs)

## DO NOT

- **Never** add a literal HuggingFace model string — route via
  `MODEL_REGISTRY` (`meaisinfhoghlaim.models.model_registry`).
- **Never** skip `AuditTranscriptQuality` on NCCA-tagged lessons — the
  alignment coverage metric is required by the spec.
- **Never** use the older `baml_src` sub-namespace — the canonical
  surface is `baml_src/media/tg4_classification.baml`.

## Skill pointers

| Skill | When to load |
|:--|:--|
| [`baml`](../../../.agents/skills/baml/SKILL.md) | BAML authoring + testing patterns |
| [`centralized-registry`](../../.agents/skills/centralized-registry/SKILL.md) | The MODEL_REGISTRY contract |
| [`openspec`](../../.agents/skills/openspec/SKILL.md) | The 4-spec-delta format |

<!-- generated: 2026-08-25; do not hand-edit -->