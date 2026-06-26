---
title: Meaisin Cliste - Celtic AI Tools
emoji: "\U0001F9F1"
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: false
license: apache-2.0
short_description: 3 Celtic AI tools in one Space: 6-nation cognate dictionary, school-density map, cross-nation curriculum compare.
---

# Meaisín Cliste — Celtic AI Tools

> "The Smart Machine" — 3 themes for Celtic AI in one Gradio Space.

**Build Small 2026 hackathon submission.** Space 2 of 4. Elements: **Aer**
(Air, themes 1+3) and **Uisce** (Water, theme 2).

## What's in this Space

### Theme 1: Foclóir na Sé Náisiún (Aer)

A 6-nation Celtic cognate dictionary. Type a word in any of the 6
Celtic languages (or in proto-Celtic) and see cognates across all 6.
30 hand-picked seed entries; production uses the full DLT pipeline
at `sruth/oideachais/language/cognates.py` (~1,800 rows).

### Theme 2: Scoil ar an Léarscáil (Uisce)

A self-contained SVG school-density map of Ireland (26 counties, 1,629
schools). Marker colour and size are by the **Pobal HP Deprivation
Index 2022**: crimson for the most deprived (Dublin 8, -9.8), emerald
for the most affluent (Meath, +1.2). Hover reveals school counts and
% DEIS.

### Theme 3: Curaclam Trasteorann (Aer)

A cross-nation curriculum comparison. Type a topic and the BAML
`CompareCelticNations` function returns how it's taught in 5
Celtic-nation curricula (NCCA, CCEA, WJEC, DESC, SQA). 6 hand-curated
reference topics; BAML chain handles the rest.

## Architecture

```
spaces/meaisin_cliste/
├── app.py           # Gradio app: 3 tabs (Focloir + Scoil + Curaclam)
├── cognates.py      # 30 hand-picked cognate seeds (proto-Celtic + 6 langs)
├── scoil_map.py     # 26-county school-density SVG + Pobal HP scoring
├── curaclam.py      # CompareCelticNations handler + offline reference
├── record_demo.py   # Programmatic demo sequence
├── requirements.txt # Gradio 4.44+
├── social_card.png  # 1200x630 PNG (generated at build time)
└── README.md        # (this file)
```

Shared with the other 3 Spaces via `spaces/_common/`:

- `theme.py` — Celtic 5-element palette + Hades Shadow-First CSS
- `baml_client.py` — 3-tier HF Inference fallback
- `anam_bonneagar.py` — per-Space trust-signal footer
- `i18n.py` — bilingual EN/GA toggle

## Headline numbers

- 30 cognates × 6 languages = 180 cells (Breton = TODO across)
- 26 counties × Pobal HP 2022 = 1,629 schools mapped
- 5 Celtic-nation curricula × 6 reference topics = 30 cross-nation mappings
- 1 typed pipeline: BAML → HF Inference → Gradio

## Element mapping

| Theme | Element | Color |
|:--|:--|:--|
| Foclóir na Sé Náisiún | Aer (Air) | `#5a4fcf` indigo |
| Scoil ar an Léarscáil | Uisce (Water) | `#1e80c6` azure |
| Curaclam Trasteorann | Aer (Air) | `#5a4fcf` indigo |

## Running locally

```bash
cd spaces/meaisin_cliste
pip install -r requirements.txt
HF_TOKEN=hf_xxx python app.py
# open http://localhost:7860
```

## License

Apache 2.0. Built on Bun + uv + Turbo.
