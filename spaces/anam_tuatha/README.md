---
title: Anam - Tuatha na nGaelscoil
emoji: "\U0001F525"
colorFrom: gold
colorTo: amber
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: false
license: apache-2.0
short_description: 5 Celtic elements + 2 cross-cutting features = 7 panels in one Gradio Space. The integration Space.
---

# Anam: Tuatha na nGaelscoil

> "Spirit: Tuatha of the Gaelscoil" — the integration Space. 5 elements
> + 2 cross-cutting features = 7 panels, all in one Gradio app.

**Build Small 2026 hackathon submission.** Space 4 of 4. The 5-element
connective tissue that runs through all 4 Spaces, plus the soulbound
token.

## What's in this Space

| # | Feature | Element | Color | What it does |
|:-:|:--|:--|:--|:--|
| 1 | Curriculum Map | **Talamh** (Earth) | `#28955e` | Lifted from Space 1 (summary) |
| 2 | Chemistry Visual | **Uisce** (Water) | `#1e80c6` | 8 molecule SVGs (CPK colours) |
| 3 | OCR Gaelscríbhneoir | **Tine** (Fire) | `#d68c1c` | Fada/eclipsis/punctum metrics |
| 4 | Languages | **Aer** (Air) | `#5a4fcf` | Lifted from Space 2 (Foclóir) |
| 5 | Soulbound Token | **Anam** (Spirit) | `#cc9966` | 3-stage Anvil sidecar mock |
| 6 | Mac Léinn | (formative) | `#cc9966` | BAML exit-card generator |
| 7 | Fiosraigh | (classroom) | `#5a4fcf` | Bilingual EN/GA switcher |

## Architecture

```
spaces/anam_tuatha/
├── app.py               # Gradio: 7-tab integration app
├── chemistry_visual.py  # 8-molecule CPK-coloured SVG renderer
├── gaelscribhneoir.py   # Fada/eclipsis/punctum Irish-text quality checker
├── soulbound_local.py   # 3-stage Anvil sidecar mock (no on-chain tx)
├── mac_leinn.py         # BAML GenerateExitCardQuestions + template bank
├── fiosraigh.py         # Bilingual EN/GA classroom-action switcher
├── record_demo.py       # Programmatic demo sequence
├── requirements.txt     # Gradio 4.44+
├── social_card.png      # 1200x630 PNG (generated at build time)
└── README.md            # (this file)
```

Shared with the other 3 Spaces via `spaces/_common/`:

- `theme.py` — Celtic 5-element palette + Hades Shadow-First CSS
- `baml_client.py` — 3-tier HF Inference fallback
- `soulbound_svg.py` — deterministic Anam SVG (used in Panel 5)
- `anam_bonneagar.py` — per-Space trust-signal footer
- `i18n.py` — bilingual EN/GA toggle (used in Panel 7)

## The 5-element connective tissue

| Element | Color | Where it appears |
|:--|:--|:--|
| **Talamh** (Earth) | `#28955e` | Panel 1 (curriculum) + Space 1 (Talamh accent) |
| **Uisce** (Water) | `#1e80c6` | Panel 2 (chemistry) + Space 2 (Scoil theme) |
| **Tine** (Fire) | `#d68c1c` | Panel 3 (OCR forge) + Space 4 amber accents |
| **Aer** (Air) | `#5a4fcf` | Panel 4 (Foclóir) + Space 2 (Foclóir + Curaclam) |
| **Anam** (Spirit) | `#cc9966` | Panel 5 (soulbound) + Space 3 (Anam element) + Space 4 (footer) |

## Headline numbers

- 7 panels, 5 elements, 1 Gradio app
- 8 molecules × CPK colours = 32 atoms rendered
- 5-feat progression: 0→Setanta, 2→Cúchulainn, 5→Ríastrad
- 10 bilingual classroom actions in Fiosraigh
- 1 typed pipeline: BAML → HF Inference → Gradio

## Running locally

```bash
cd spaces/anam_tuatha
pip install -r requirements.txt
HF_TOKEN=hf_xxx python app.py
# open http://localhost:7860
```

## License

Apache 2.0. Built on Bun + uv + Turbo.
