# Spaces — Cianfhoghlaim HuggingFace Spaces

## Priority quick reference

The 4 active Spaces, the 1 archived Space, the 5 priority skills,
the 4 priority commands, and the 4 priority openspec specs at
a glance. **Read this first**; the rest of the file is the
per-Space routing.

### Active Spaces (4)

| Space | Port | SDK | Maps to | One-liner |
|:--|:--|:--|:--|:--|
| `an_scrudu/` (An Scrúdú) | 7860 | gradio 5.x | oideachais (Talamh) | Past-paper heatmap + PCLM-XML/PDF download |
| `meaisin_cliste/` (Meaisín Cliste) | 7860 | gradio 5.x | meaisinfhoghlaim (Uisce + Aer) | 3 Celtic AI tools: cognate dictionary, school-density map, cross-nation curriculum |
| `cianfhoghlaim/` (RPG) | 7860 | gradio 5.x | tuatha (Aer + Anam) | Hades-style dialogue with 6 Celtic NPCs on a British Isles map |
| `anam_tuatha/` (Anam) | 7860 | gradio 5.x | croilar (5 elements) | Integration Space: 5 elements + 2 cross-cutting features = 7 panels |
| `data-engineering/` (PyPI) | 8000 | dagster + dbt + evidence | oideachais (data plane) | PyPI package analytics dashboard (the only non-gradio Space) |

### Archived Spaces (1)

| Space | Archived to | Reason |
|:--|:--|:--|
| `anti-phish/` | `archive/anti-phish-2022-academic/` | 2022 personal academic project with inappropriate public content |

### Shared bundle

| Path | Purpose |
|:--|:--|
| `spaces/_common/` | The cross-cutting foundation: Celtic 5-element palette, BAML client (now LiteLLM gateway), i18n, Anam Bonneagar footer |
| `spaces/_common/baml_client.py` | LiteLLM gateway shim with HF Inference 3-tier fallback (the offline mode) |

### Priority skills (7 of 120)

| Skill | When to load |
|:--|:--|
| [`baml`](../.agents/skills/baml/SKILL.md) | BAML extraction schemas (the 4 promoted hackathon functions: ExtractCircularMeta, CompareCelticNations, GenerateExitCardQuestions, GenerateNpcDialogue) |
| [`ccc`](../.agents/skills/ccc/SKILL.md) | Code search — use `ccc search` to find prior art in the spaces archive |
| [`motherduck-connections`](../.agents/skills/motherduck-connections/SKILL.md) | LiteLLM gateway wiring (the Spaces' primary LLM tier) |
| [`agent-observability`](../.agents/skills/agent-observability/SKILL.md) | Langfuse auto-traces every LiteLLM call (cost + latency + model) |
| [`oideachais-storage`](../.agents/skills/oideachais-storage/SKILL.md) | The KCG storage mental model (DuckLake 1.0 + Lance Namespace) |
| [`hf-spaces-deploy`](../.agents/skills/hf-spaces-deploy/SKILL.md) | The 4 + 4 + 1 + 1 Spaces inventory + the 4-file Space structure + the reusable workflow + the LiteLLM gateway pattern |
| [`gradio-ensemble-pattern`](../.agents/skills/gradio-ensemble-pattern/SKILL.md) | The `build_ensemble_interface()` helper + the `push_model_to_hub()` HF Hub push helper + the 3 canonical Space structures + the 4 component patterns |

### ccc + openspec commands

```bash
bun run ccc:search "Gradio Space 5-element palette"     # find prior art
openspec list --specs                                   # 32 specs total
openspec validate <change-id> --strict                  # MUST pass before commit
openspec archive <change-id> --yes                      # after deploy
```

### Priority openspec specs for the Spaces

| Spec | One-liner |
|:--|:--|
| `oideachais-pipeline` | The canonical lakehouse pipeline (the 4 Spaces consume this) |
| `agent-observability` | The Langfuse / MLflow / RAGAS observability stack |
| `infrastructure-stacks` | The 94 Docker Compose stacks (some Spaces run as Komodo services) |
| `data-engineering-pipeline-documentation` | The STATUS.md + REFACTORING.md router |

## Per-Space routing

For a Space-specific AGENTS.md, see:

- `spaces/an_scrudu/AGENTS.md`
- `spaces/meaisin_cliste/AGENTS.md`
- `spaces/cianfhoghlaim/AGENTS.md`
- `spaces/anam_tuatha/AGENTS.md`
- `spaces/data-engineering/AGENTS.md`

## When to add a new Space

1. The Space is a deployable Gradio app (has an `app.py` + a `requirements.txt`)
2. The Space consumes data from one of the 4 KCG quadrants (oideachais, meaisinfhoghlaim, tuatha, croilar)
3. The Space uses the canonical LLM stack (LiteLLM gateway + BAML) — not raw HF Inference
4. The Space is wired to the canonical openspec workflow (every change is captured in an openspec change)

## Cross-references

- [`../openspec/AGENTS.md`](../openspec/AGENTS.md) — the openspec workflow
- [`../AGENTS.md`](../AGENTS.md) — the root agent instructions
- [`../oideachais/AGENTS.md`](../oideachais/AGENTS.md) — the oideachais quadrant
- [`../meaisinfhoghlaim/AGENTS.md`](../meaisinfhoghlaim/AGENTS.md) — the AI/ML quadrant
- [`../tuatha/AGENTS.md`](../tuatha/AGENTS.md) — the MMO quadrant
- [`../croilar/AGENTS.md`](../croilar/AGENTS.md) — the portfolio quadrant
- [`../infrastructure/AGENTS.md`](../infrastructure/AGENTS.md) — the 94 Docker Compose stacks
