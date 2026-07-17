---
name: hf-spaces-deploy
description: The KCG HuggingFace Spaces deploy pipeline — the 4 active Spaces (an_scrudu, meaisin_cliste, cianfhoghlaim, anam_tuatha) + the 4 new demo Spaces (croilar_portfolio_demo, cianfhoghlaim_mission_control, crypteolas_defi_monitor, tuatha_mmo_demo) + the 1 archived Space (anti-phish) + the canonical reusable workflow at `.github/workflows/spaces-sync.yml` (used by 4 per-Space sync.yml wrappers) + the 5-element palette + the i18n (EN/GA) toggle + the LiteLLM gateway pattern. Use when adding a new Space, debugging a CI sync failure, understanding the 4-file Space structure (app.py + requirements.txt + README.md + AGENTS.md), or asking "how does a Space deploy to HF?".
---

# HuggingFace Spaces Deploy

## Purpose

The `spaces/` directory houses the 4 active HuggingFace Spaces
(the Celtic AI demo suite) + the 4 new demo Spaces + 1
archived Space + the shared `_common/` bundle. This skill
captures the deploy pipeline, the 4-file Space structure, the
reusable workflow, and the add-a-new-Space workflow.

## When to use this skill

Use when you need to:

- "Add a new HuggingFace Space"
- "Debug a CI sync failure (the 4 sync.yml files)"
- "Understand the 4-file Space structure (app.py + requirements.txt + README.md + AGENTS.md)"
- "Wire a new Space to the LiteLLM gateway"
- "Find the canonical reusable workflow at `.github/workflows/spaces-sync.yml`"

## The 4 active Spaces (the Celtic AI demo suite)

| Space | SDK | Maps to | Pent-Elemental | One-liner |
|:--|:--|:--|:--|:--|
| `an_scrudu/` (An Scrúdú) | gradio 5.x | oideachais (Talamh) | Earth | Past-paper heatmap + PCLM-XML/PDF download |
| `meaisin_cliste/` (Meaisín Cliste) | gradio 5.x | meaisinfhoghlaim (Uisce + Aer) | Water + Air | 3 Celtic AI tools: cognate dictionary, school-density map, cross-nation curriculum |
| `cianfhoghlaim/` (RPG) | gradio 5.x | tuatha (Aer + Anam) | Air + Spirit | Hades-style dialogue with 6 Celtic NPCs on a British Isles map |
| `anam_sruth/tuatha/` (Anam) | gradio 5.x | croilar (5 elements) | All 5 | Integration Space: 5 elements + 2 cross-cutting features = 7 panels |

## The 4 new demo Spaces (the 2026-06-24 batch)

| Space | SDK | Maps to | Purpose |
|:--|:--|:--|:--|
| `croilar_portfolio_demo/` | gradio 5.x | croilar | A demo of the 3-persona portfolio site |
| `cianfhoghlaim_mission_control/` | gradio 5.x | oideachais | A mission-control dashboard for the lakehouse |
| `crypteolas_defi_monitor/` | gradio 5.x | crypteolas | A DeFi monitor for the crypteolas platform |
| `tuatha_mmo_demo/` | gradio 5.x | tuatha | A demo of the British Isles formative assessment MMO |

## The 1 archived Space

| Space | Archived to | Reason |
|:--|:--|:--|
| `anti-phish/` | `archive/anti-phish-2022-academic/` | 2022 personal academic project with inappropriate public content |

## The 1 non-gradio Space (the canonical exception)

| Space | SDK | Purpose |
|:--|:--|:--|
| `data-engineering/` | dagster + dbt + evidence | PyPI package analytics dashboard |

The `data-engineering/` Space is the only non-gradio Space.
It lives in `spaces/` for historical reasons but is the
canonical exception (it consumes `sruth/cianfhoghlaim/agents/adk/`
+ `sruth/cianfhoghlaim/baml_src/` directly, not the LiteLLM gateway).

## The 4-file Space structure (the canonical layout)

Every active Space has exactly 4 required files:

```
spaces/<space_name>/
├── app.py             # The Gradio app (the entry point)
├── requirements.txt   # The Gradio + BAML dependencies
├── README.md          # The HF Space README (YAML frontmatter + 1-line tagline)
└── AGENTS.md          # The developer quick reference
```

Plus 2 optional files (the demo + the social card):

- `record_demo.py` — the programmatic demo sequence (the
  `demo_recorder.py` from `_common/`)
- `social_card.png` — the 1200x630 PNG (auto-generated at
  build time)

The Gradio app follows the standard 4-step pattern:

```python
# spaces/meaisin_cliste/app.py
import gradio as gr
from spaces._common import chat_complete_json, theme, i18n, anam_bonneagar

with gr.Blocks(theme=theme) as demo:
    with gr.Tabs():
        with gr.Tab("Foclóir"):
            # the cognate dictionary UI
            ...
        with gr.Tab("Scoil"):
            # the school-density map UI
            ...
    anam_bonneagar.render()  # the per-Space footer

demo.launch(server_name="0.0.0.0", server_port=7860)
```

## The reusable workflow (the canonical CI pattern)

The 4 per-Space sync.yml files are thin wrappers around the
canonical reusable workflow at
`.github/workflows/spaces-sync.yml`. Each per-Space
sync.yml has exactly 5 inputs:

```yaml
# spaces/meaisin_cliste/.github/workflows/sync.yml
name: Sync meaisin_cliste to HF
on:
  push:
    branches: [main]
    paths:
      - 'spaces/meaisin_cliste/**'
      - 'spaces/_common/**'
  workflow_dispatch:
jobs:
  sync:
    uses: ./.github/workflows/spaces-sync.yml
    with:
      space_dir: spaces/meaisin_cliste
      target_space: cianfhoghlaim/meaisin-cliste
      hf_token: ${{ secrets.HF_TOKEN }}
      hf_username: ${{ vars.HF_USERNAME }}
      sdk: gradio
```

The 4 per-Space sync.yml files differ only in the
`space_dir` + `target_space` inputs. The reusable workflow
handles the HF API push + the build cache + the social card
auto-generation.

## The LiteLLM gateway pattern (the LLM stack)

Every active Space uses the canonical LiteLLM gateway
through `spaces/_common/baml_client.py`:

```python
# spaces/meaisin_cliste/app.py
from spaces._common import chat_complete_json, HACKATHON_PRIMARY_MODEL

response = await chat_complete_json(
    model=HACKATHON_PRIMARY_MODEL,  # the canonical model
    messages=[...],
    response_format={"type": "json_object"},
)
```

The `HACKATHON_PRIMARY_MODEL` is the canonical LiteLLM
alias (3-key round-robin + 4-tier fallback). The
`chat_complete_json` helper routes through the gateway +
auto-traces via Langfuse + falls back to HF Inference if
the gateway is unreachable.

## The 5-element palette (the design system)

The `spaces/_common/theme.py` module exports the Celtic
5-element palette:

| Realm | Element | Hex | Use |
|:--|:--|:--|:--|
| Earth (Talamh) | `#3a5f3a` | Earthy green | Oideachais, An Scrúdú |
| Water (Uisce) | `#1e3a5f` | Deep blue | Meaisín Cliste, School map |
| Fire (Tine) | `#a83e3e` | Crimson | Formative assessment, Quests |
| Air (Aer) | `#5f5f8a` | Lavender | Cognate dictionary, Cross-nation |
| Spirit (Anam) | `#8a5f3a` | Bronze | RPG, NPC dialogue |

The palette is used in the `gr.Blocks(theme=theme)`
constructor + in the social card backgrounds.

## The i18n (EN/GA) toggle (the bilingual pattern)

The `spaces/_common/i18n.py` module exports a bilingual
EN/GA toggle. The pattern:

```python
# spaces/meaisin_cliste/app.py
from spaces._common import i18n

with gr.Blocks(theme=theme) as demo:
    lang = gr.Radio(["EN", "GA"], value="EN", label="Language / Teanga")
    # ... the Gradio components use i18n.t("key", lang=lang)
```

The 4 active Spaces are all bilingual (EN default, GA
alternate). The HF Space page exposes the toggle via
the `ga` route (e.g. `https://huggingface.co/spaces/cianfhoghlaim/meaisin-cliste/ga`).

## The Anam Bonneagar footer (the canonical footer)

The `spaces/_common/anam_bonneagar.py` module exports the
per-Space footer:

```python
# spaces/meaisin_cliste/app.py
from spaces._common import anam_bonneagar

with gr.Blocks(theme=theme) as demo:
    # ... the Gradio app
    anam_bonneagar.render()  # adds the footer with Pobal HP + 32B alias + linter score
```

The footer shows: the Pobal HP Deprivation Index score
(for Irish social-context grounding), the 32B alias
identifier (the LLM model version), and the linter score
(for code quality).

## Worked example: add a new Space

1. Create the 4 required files:

   ```bash
   mkdir -p spaces/my_new_space
   # spaces/my_new_space/app.py
   # spaces/my_new_space/requirements.txt
   # spaces/my_new_space/README.md
   # spaces/my_new_space/AGENTS.md
   ```

2. Wire the LiteLLM gateway:

   ```python
   # spaces/my_new_space/app.py
   import gradio as gr
   from spaces._common import chat_complete_json, HACKATHON_PRIMARY_MODEL, theme

   with gr.Blocks(theme=theme) as demo:
       input_text = gr.Textbox(label="Query")
       output_text = gr.Textbox(label="Response")
       btn = gr.Button("Submit")
       btn.click(
           fn=lambda q: chat_complete_json(model=HACKATHON_PRIMARY_MODEL, messages=[{"role": "user", "content": q}]),
           inputs=input_text,
           outputs=output_text,
       )
   demo.launch()
   ```

3. Create the per-Space sync.yml wrapper:

   ```yaml
   # spaces/my_new_space/.github/workflows/sync.yml
   name: Sync my_new_space to HF
   on:
     push:
       branches: [main]
       paths:
         - 'spaces/my_new_space/**'
         - 'spaces/_common/**'
     workflow_dispatch:
   jobs:
     sync:
       uses: ./.github/workflows/spaces-sync.yml
       with:
         space_dir: spaces/my_new_space
         target_space: cianfhoghlaim/my-new-space
         hf_token: ${{ secrets.HF_TOKEN }}
         hf_username: ${{ vars.HF_USERNAME }}
         sdk: gradio
   ```

4. Add the Space to the `spaces/AGENTS.md` active Spaces
   table.

5. Update the openspec change
   `spaces-bundle-decomposition-v1` to document the new
   Space.

## Common failure modes

| Symptom | Cause | Fix |
|:--|:--|:--|
| The sync workflow times out | HF API rate limit | Add `retry: 3` to the reusable workflow |
| The Gradio app fails to import | The `_common/` bundle is missing | Add `from spaces._common import ...` at the top of `app.py` |
| The 5-element palette is missing | The `theme.py` import is missing | Add `from spaces._common import theme` + use `gr.Blocks(theme=theme)` |
| The bilingual toggle doesn't work | The `i18n.py` import is missing | Add `from spaces._common import i18n` + use `i18n.t("key")` |
| The LLM call returns a 502 | The LiteLLM gateway is unreachable | The `chat_complete_json` helper auto-falls back to HF Inference |

## Cross-references

- `spaces/_common/theme.py` — the 5-element palette
- `spaces/_common/baml_client.py` — the LiteLLM gateway shim
- `spaces/_common/i18n.py` — the bilingual EN/GA toggle
- `spaces/_common/anam_bonneagar.py` — the per-Space footer
- `spaces/_common/soulbound_svg.py` — the deterministic Celtic-knot SVG
- `spaces/_common/social_card.py` — the HF social card auto-renderer
- `spaces/_common/hf_hub_push.py` — the HF Hub push helper
- `spaces/_common/demo_recorder.py` — the programmatic demo sequence
- `.github/workflows/spaces-sync.yml` — the canonical reusable workflow
- `openspec/changes/spaces-bundle-decomposition-v1/` — the round 12 openspec change
