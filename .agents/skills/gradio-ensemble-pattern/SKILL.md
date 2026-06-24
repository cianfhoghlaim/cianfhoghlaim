---
name: gradio-ensemble-pattern
description: The KCG Gradio ensemble pattern — `build_ensemble_interface()` helper + `push_model_to_hub()` HF Hub push helper from `spaces/_common/`. Covers the 4 Space themes (Foclóir / Scoil / Curaclam / Anam), the 3 canonical Space structures (single-tab / multi-tab / multi-page), the `gr.Blocks(theme=...)` + `gr.Tabs()` + `gr.Row()` + `gr.Column()` composition patterns, the `gr.ChatInterface` + `gr.Dataframe` + `gr.Plot` + `gr.Gallery` component patterns, the `chat_complete_json` + `HACKATHON_PRIMARY_MODEL` LLM call pattern, the `anam_bonneagar.render()` footer pattern, the deterministic SVG generator pattern, and the canonical add-a-new-Space workflow. Use when adding a new Space theme, debugging a Gradio composition issue, wiring a new LiteLLM-backed component, or asking "how does the ensemble pattern work?".
---

# Gradio Ensemble Pattern

## Purpose

The 4 active Spaces (An Scrúdú, Meaisín Cliste, Cianfhoghlaim,
Anam Tuatha) + the 4 new demo Spaces (Croílár Portfolio Demo,
Oideachais Mission Control, Crypteolas DeFi Monitor, Tuatha
MMO Demo) all follow the canonical KCG **Gradio ensemble
pattern** — a multi-tab, multi-theme, LiteLLM-backed
composition that exposes the 5 Pent-Elemental realms in a
single Gradio app.

This skill captures the `build_ensemble_interface()` helper
+ the `push_model_to_hub()` HF Hub push helper from
`spaces/_common/`, the 3 canonical Space structures, the
component composition patterns, and the add-a-new-Space
workflow.

## When to use this skill

Use when you need to:

- "Add a new Space theme (a new tab)"
- "Debug a Gradio composition issue"
- "Wire a new LiteLLM-backed component"
- "Understand the ensemble pattern"
- "Add a new `gr.ChatInterface` or `gr.Plot` component"

## The `build_ensemble_interface()` helper (the canonical factory)

The `spaces/_common/__init__.py` exports the
`build_ensemble_interface()` helper:

```python
# spaces/_common/__init__.py
def build_ensemble_interface(
    tabs: list[dict],
    title: str = "Cianfhoghlaim",
    theme: gr.Theme = None,
    footer: bool = True,
    bilingual: bool = True,
) -> gr.Blocks:
    """Build a Gradio ensemble interface from a list of tab specs.

    Args:
        tabs: list of {"label": str, "fn": callable, "inputs": list, "outputs": list}
        title: the Gradio app title (shown in the browser tab)
        theme: the Celtic 5-element palette (defaults to the canonical theme)
        footer: whether to render the Anam Bonneagar footer
        bilingual: whether to expose the EN/GA language toggle

    Returns:
        The configured `gr.Blocks` instance (call `.launch()` to start the server)
    """
```

The helper handles:

- The `gr.Blocks(theme=theme)` + `gr.Tabs()` composition
- The per-tab `gr.Row()` + `gr.Column()` layout
- The `gr.ChatInterface` + `gr.Dataframe` + `gr.Plot` +
  `gr.Gallery` component patterns
- The Anam Bonneagar footer (`anam_bonneagar.render()`)
- The bilingual EN/GA toggle (`i18n.t("key")`)

## The `push_model_to_hub()` helper (the canonical HF Hub push)

The `spaces/_common/__init__.py` exports the
`push_model_to_hub()` helper:

```python
# spaces/_common/__init__.py
def push_model_to_hub(
    model_dir: str,
    repo_id: str,
    private: bool = False,
    commit_message: str = "Update model",
) -> str:
    """Push a model to the HuggingFace Hub.

    Args:
        model_dir: the local model directory
        repo_id: the HF Hub repo id (e.g. "cianfhoghlaim/meaisin-cliste")
        private: whether the repo is private
        commit_message: the commit message

    Returns:
        The HF Hub URL of the pushed repo
    """
```

The helper handles:

- The `huggingface_hub.HfApi()` authentication
- The `repo.create_repo()` + `repo.upload_folder()` calls
- The retry logic (3 retries with exponential backoff)
- The auto-generated model card (from the Space's README.md)

## The 3 canonical Space structures (the 3 patterns)

The 4 active Spaces use 3 different Gradio structures:

### Pattern 1: single-tab (the An Scrúdú pattern)

The `an_scrudu/` Space uses a single-tab pattern (the
past-paper heatmap is a single UI surface):

```python
# spaces/an_scrudu/app.py
import gradio as gr
from spaces._common import build_ensemble_interface, theme

demo = build_ensemble_interface(
    tabs=[{
        "label": "Past Papers",
        "fn": render_heatmap,
        "inputs": [gr.Dropdown(["2024", "2023", "2022"])],
        "outputs": [gr.Plot()],
    }],
    title="An Scrúdú",
)
demo.launch()
```

### Pattern 2: multi-tab (the Meaisín Cliste pattern)

The `meaisin_cliste/` Space uses a 3-tab pattern (Foclóir +
Scoil + Curaclam):

```python
# spaces/meaisin_cliste/app.py
import gradio as gr
from spaces._common import build_ensemble_interface, theme

demo = build_ensemble_interface(
    tabs=[
        {"label": "Foclóir", "fn": render_cognate, "inputs": [gr.Textbox()], "outputs": [gr.Dataframe()]},
        {"label": "Scoil", "fn": render_school_map, "inputs": [gr.Dropdown()], "outputs": [gr.Plot()]},
        {"label": "Curaclam", "fn": compare_curricula, "inputs": [gr.Textbox()], "outputs": [gr.Markdown()]},
    ],
    title="Meaisín Cliste",
)
demo.launch()
```

### Pattern 3: multi-page (the Cianfhoghlaim RPG pattern)

The `cianfhoghlaim/` Space uses a multi-page pattern
(British Isles map + 6 NPC dialogue pages):

```python
# spaces/cianfhoghlaim/app.py
import gradio as gr
from spaces._common import build_ensemble_interface, theme

demo = build_ensemble_interface(
    tabs=[
        {"label": "Map", "fn": render_map, "inputs": [], "outputs": [gr.Plot()]},
        {"label": "Ui Liathain", "fn": chat_ui_liathain, "inputs": [gr.Textbox()], "outputs": [gr.Chatbot()]},
        # ... 5 more NPC tabs
    ],
    title="Cianfhoghlaim",
)
demo.launch()
```

## The 4 component patterns (the canonical types)

The ensemble pattern uses 4 canonical Gradio component types:

| Component | Use case | Example |
|:--|:--|:--|
| `gr.ChatInterface` | NPC dialogue + the chat UI | `gr.ChatInterface(fn=chat_npc)` |
| `gr.Dataframe` | The cognate dictionary + the curriculum comparison | `gr.Dataframe(value=df_cognates)` |
| `gr.Plot` | The school-density map + the past-paper heatmap | `gr.Plot(value=matplotlib_fig)` |
| `gr.Gallery` | The album artwork + the social card preview | `gr.Gallery(value=[img1, img2])` |

Each component has a canonical binding to the
`build_ensemble_interface()` helper.

## The LLM call pattern (the LiteLLM gateway)

Every LLM-backed component uses the canonical
`chat_complete_json()` helper:

```python
# spaces/cianfhoghlaim/app.py
from spaces._common import chat_complete_json, HACKATHON_PRIMARY_MODEL

async def chat_npc(npc_name: str, player_utterance: str) -> str:
    response = await chat_complete_json(
        model=HACKATHON_PRIMARY_MODEL,
        messages=[
            {"role": "system", "content": f"You are {npc_name}, a Celtic NPC..."},
            {"role": "user", "content": player_utterance},
        ],
        response_format={"type": "json_object"},
    )
    return response["choices"][0]["message"]["content"]
```

The `HACKATHON_PRIMARY_MODEL` is the canonical LiteLLM
alias (3-key round-robin + 4-tier fallback). The
`chat_complete_json` helper routes through the gateway +
auto-traces via Langfuse + falls back to HF Inference if
the gateway is unreachable.

## The footer pattern (the Anam Bonneagar)

Every active Space renders the Anam Bonneagar footer:

```python
# spaces/meaisin_cliste/app.py
from spaces._common import anam_bonneagar

with gr.Blocks(theme=theme) as demo:
    # ... the Gradio app
    anam_bonneagar.render()  # adds the footer with Pobal HP + 32B alias + linter score
```

The footer shows:

- The Pobal HP Deprivation Index score (for Irish
  social-context grounding)
- The 32B alias identifier (the LLM model version)
- The linter score (for code quality)

## The deterministic SVG pattern (the Celtic knot)

The `spaces/_common/soulbound_svg.py` module exports a
deterministic Celtic-knot SVG generator:

```python
# spaces/anam_tuatha/app.py
from spaces._common import soulbound_svg

svg = soulbound_svg.generate(seed="ui-liathain", size=512)
# returns a deterministic Celtic-knot SVG as a string
```

The SVG is used for the per-Space social card + the
per-NPC badge + the Anam Cara bond visualization.

## Worked example: add a new Space theme

1. Add the new tab to the `tabs` list:

   ```python
   # spaces/meaisin_cliste/app.py
   from spaces._common import build_ensemble_interface, theme, compare_celtic_nations

   demo = build_ensemble_interface(
       tabs=[
           {"label": "Foclóir", "fn": render_cognate, ...},
           {"label": "Scoil", "fn": render_school_map, ...},
           {"label": "Curaclam", "fn": compare_curricula, ...},
           {"label": "Béaloideas (NEW)", "fn": render_folklore, ...},  # the new tab
       ],
   )
   ```

2. Implement the new tab's function:

   ```python
   # spaces/meaisin_cliste/folklore.py
   from spaces._common import chat_complete_json, HACKATHON_PRIMARY_MODEL

   async def render_folklore(query: str) -> str:
       response = await chat_complete_json(
           model=HACKATHON_PRIMARY_MODEL,
           messages=[{"role": "user", "content": f"Tell me a Celtic folktale: {query}"}],
       )
       return response["choices"][0]["message"]["content"]
   ```

3. Add the i18n keys to `spaces/_common/i18n.py`:

   ```python
   # spaces/_common/i18n.py
   STRINGS = {
       "folklore_tab_label": {"EN": "Folklore", "GA": "Béaloideas"},
       "folklore_input_label": {"EN": "Query", "GA": "Ceist"},
   }
   ```

4. Update the openspec change
   `spaces-bundle-decomposition-v1` to document the new
   theme.

## Common failure modes

| Symptom | Cause | Fix |
|:--|:--|:--|
| The Gradio app fails to import | The `_common/` bundle is missing | Add `from spaces._common import ...` at the top of `app.py` |
| The ensemble pattern is misaligned | The `tabs` list is not properly formatted | Check the `tabs` list shape (4 required keys: label, fn, inputs, outputs) |
| The LLM call returns a 502 | The LiteLLM gateway is unreachable | The `chat_complete_json` helper auto-falls back to HF Inference |
| The footer is missing | The `anam_bonneagar.render()` call is missing | Add `anam_bonneagar.render()` at the end of the `gr.Blocks` body |
| The bilingual toggle doesn't work | The `i18n.t("key")` calls are missing | Use `i18n.t("key", lang=lang)` for all user-facing strings |
| The HF Hub push fails with 403 | The HF token is missing | Add `HF_TOKEN` to the GitHub repo secrets |

## Cross-references

- `spaces/_common/__init__.py` — the `build_ensemble_interface()` + `push_model_to_hub()` helpers
- `spaces/_common/theme.py` — the Celtic 5-element palette
- `spaces/_common/baml_client.py` — the LiteLLM gateway shim
- `spaces/_common/i18n.py` — the bilingual EN/GA toggle
- `spaces/_common/anam_bonneagar.py` — the per-Space footer
- `spaces/_common/soulbound_svg.py` — the deterministic Celtic-knot SVG
- `spaces/_common/social_card.py` — the HF social card auto-renderer
- `spaces/_common/hf_hub_push.py` — the HF Hub push helper
- `spaces/_common/demo_recorder.py` — the programmatic demo sequence
- `tuatha/baml_src/mythology_extraction.baml` — the canonical BAML for the NPC dialogue
- `tuatha/baml_src/celtic_curriculum.baml` — the canonical BAML for the cross-nation comparison
- `openspec/changes/spaces-bundle-decomposition-v1/` — the round 12 openspec change
