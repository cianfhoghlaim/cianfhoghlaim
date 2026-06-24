---
title: Oideachais - Mission Control
emoji: "\U0001F4CA"
colorFrom: green
colorTo: emerald
sdk: gradio
sdk_version: 5.0.0
app_file: app.py
pinned: false
license: apache-2.0
short_description: 5 educational stages (Aistear / Primary / JC / SC / Tertiary) as marimo notebooks over MotherDuck. Cognee cognify + BAML extraction buttons.
---

# Oideachais — Mission Control

> The 5 educational stages of the Irish curriculum as marimo
> notebooks over the canonical MotherDuck lakehouse. Cognee
> cognify + BAML extraction buttons per stage.

D1 of the spaces alignment plan (2026-06). A new HuggingFace
Space that exposes the oideachais data platform as 5 marimo
notebooks (one per educational stage) + a Cognee cognify button
+ a BAML extraction button.

## What's in this Space

- **5 tabs**: Aistear (early childhood) / Primary / JC / SC /
  Tertiary (the 5 educational stages)
- **Per tab**: a marimo notebook from `oideachais/notebooks/`
  (the canonical oideachais dashboard)
- **Cognee cognify button**: runs the 5-stage cognify pass on
  the selected stage's data (per the canonical
  `oideachais-cognify-knowledge-graph` spec)
- **BAML extraction button**: runs the canonical BAML
  extraction on a user-uploaded PDF (per the
  `oideachais-baml-schemas` spec)
- **MotherDuck Dive per stage**: the canonical BI dashboard
  per stage (per the `motherduck-analytics` skill)

## Architecture

```
spaces/oideachais_mission_control/
├── app.py               # Gradio: 5-tab mission control
├── notebooks/           # the 5 marimo notebooks (one per stage)
│   ├── aistear.py
│   ├── primary.py
│   ├── junior_cycle.py
│   ├── senior_cycle.py
│   └── tertiary.py
├── cognify_button.py    # the Cognee 5-stage cognify pass
├── baml_button.py       # the BAML extraction button
├── motherduck_dive.py   # the MotherDuck BI dashboard per stage
├── requirements.txt     # Gradio 5.x + marimo + dlt
├── README.md            # HF Space README
└── AGENTS.md            # (this file)
```

## Cross-references

- [`../AGENTS.md`](../AGENTS.md) — the Spaces parent
- [`../../oideachais/AGENTS.md`](../../oideachais/AGENTS.md) — the oideachais quadrant
- [`../../.agents/skills/oideachais-pipeline/SKILL.md`](../../.agents/skills/oideachais-pipeline/SKILL.md) — the canonical pipeline
- [`../../.agents/skills/motherduck-analytics/SKILL.md`](../../.agents/skills/motherduck-analytics/SKILL.md) — the MotherDuck analytics
- [`../../.agents/skills/marimo/SKILL.md`](../../.agents/skills/marimo/SKILL.md) — the marimo notebook pattern
- [`../../.agents/skills/cognee/SKILL.md`](../../.agents/skills/cognee/SKILL.md) — the Cognee 5-stage cognify
- [`../../.agents/skills/baml/SKILL.md`](../../.agents/skills/baml/SKILL.md) — the BAML extraction pattern
