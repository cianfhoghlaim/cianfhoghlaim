---
title: Tuatha - MMO Demo
emoji: "\U0001F3DB"
colorFrom: indigo
colorTo: gold
sdk: gradio
sdk_version: 5.0.0
app_file: app.py
pinned: false
license: apache-2.0
short_description: 1 Babylon.js 7 + WebGPU quest: the 4-feedback-channel formative assessment with the 4 tuatha agents + the crypteolas achievement-ledger.
---

# Tuatha — MMO Demo

> 1 quest in the British Isles Formative Assessment MMO:
> the 4-feedback-channel pattern (Celtic Tutor / Mythology
> Narrator / Quest Guide / Research Assistant) + the
> crypteolas achievement-ledger (skill-tree badges, NOT a
> financial token).

D3 of the spaces alignment plan (2026-06). A demo of the
Tuatha Celtic Educational MMO with:

- 1 Babylon.js 7 + WebGPU 3D scene
- 4 tuatha agents (the formative feedback channels)
- 1 quest: the "BCS topic" formative assessment
- The crypteolas achievement-ledger (5-feat progression)
- The British Isles formative assessment pattern

## What's in this Space

- **Tab 1: Map** — the Babylon.js 7 + WebGPU British Isles map
  (the same map as the Cianfhoghlaim RPG, but in 3D)
- **Tab 2: Quest** — the BCS topic quest with the 4-feedback-channel
  formative assessment (Celtic Tutor / Mythology Narrator /
  Quest Guide / Research Assistant)
- **Tab 3: Achievement Ledger** — the 5-feat progression
  (0 → Setanta, 2 → Cúchulainn, 5 → Ríastrad) per the
  crypteolas ledger
- **Tab 4: Knowledge Graph** — the Cognee + Graphiti
  bi-temporal graph of the MMO content

## Architecture

```
spaces/tuatha_mmo_demo/
├── app.py               # Gradio: 4-tab MMO demo
├── babylon_scene.py     # the Babylon.js 7 + WebGPU scene
├── quest.py             # the BCS topic quest + 4 agents
├── achievement_ledger.py # the crypteolas ledger
├── knowledge_graph.py   # the Cognee + Graphiti cognify
├── requirements.txt
├── README.md
└── AGENTS.md
```

## Cross-references

- [`../AGENTS.md`](../AGENTS.md) — the Spaces parent
- [`../../tuatha/AGENTS.md`](../../tuatha/AGENTS.md) — the tuatha quadrant
- [`../../.agents/skills/babylonjs/SKILL.md`](../../.agents/skills/babylonjs/SKILL.md) — the Babylon.js 7 pattern
- [`../../.agents/skills/tuatha-mmo/SKILL.md`](../../.agents/skills/tuatha-mmo/SKILL.md) — the 4-agent pattern
- [`../../.agents/skills/british-isles-formative-assessment/SKILL.md`](../../.agents/skills/british-isles-formative-assessment/SKILL.md) — the formative assessment
