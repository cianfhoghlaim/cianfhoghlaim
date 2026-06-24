---
title: Croílár - Portfolio Demo
emoji: "\U0001F310"
colorFrom: gold
colorTo: amber
sdk: gradio
sdk_version: 5.0.0
app_file: app.py
pinned: false
license: apache-2.0
short_description: 3 personas (aleyum / cianfhoghlaim / carlcashman) with the bilingual EN/GA routing + 12 DLT pipelines + marimo notebooks.
---

# Croílár — Portfolio Demo

> 3 personas (aleyum / cianfhoghlaim / carlcashman) with the
> bilingual EN/GA routing + 12 DLT pipelines (Spotify /
> SoundCloud / GitHub / CV PDFs / teaching records) + marimo
> notebooks per persona.

D4 of the spaces alignment plan (2026-06). A demo of the
Croílár multi-persona portfolio platform as 3 personas +
the canonical 12 DLT pipelines + the marimo notebooks.

## What's in this Space

- **Tab 1: Aleyum** (music persona) — Spotify + SoundCloud +
  GitHub DLT pipelines, 5 marimo notebooks
- **Tab 2: Cianfhoghlaim** (teaching persona) — CV PDFs +
  teaching records DLT pipelines, 5 marimo notebooks
- **Tab 3: Carlcashman** (research persona) — ResearchGate +
  LinkedIn + GitHub DLT pipelines, 5 marimo notebooks
- **Tab 4: Bilingual EN/GA** — the Celtic language toggle
  (the canonical bilingual pattern)

## Architecture

```
spaces/croilar_portfolio_demo/
├── app.py               # Gradio: 4-tab portfolio demo
├── aleyum.py            # the music persona
├── cianfhoghlaim.py     # the teaching persona
├── carlcashman.py       # the research persona
├── bilingual.py         # the EN/GA toggle
├── marimo_stream.py     # the marimo notebooks
├── requirements.txt
├── README.md
└── AGENTS.md
```

## Cross-references

- [`../AGENTS.md`](../AGENTS.md) — the Spaces parent
- [`../../croilar/AGENTS.md`](../../croilar/AGENTS.md) — the croilar quadrant
- [`../../.agents/skills/dlt/SKILL.md`](../../.agents/skills/dlt/SKILL.md) — the 12 DLT pipelines
- [`../../.agents/skills/marimo/SKILL.md`](../../.agents/skills/marimo/SKILL.md) — the marimo notebooks
- [`../../.agents/skills/celtic-language-ai/SKILL.md`](../../.agents/skills/celtic-language-ai/SKILL.md) — the bilingual toggle
