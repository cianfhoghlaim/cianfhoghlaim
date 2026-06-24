---
title: Crypteolas - DeFi Monitor
emoji: "\U0001F4B0"
colorFrom: indigo
colorTo: purple
sdk: gradio
sdk_version: 5.0.0
app_file: app.py
pinned: false
license: apache-2.0
short_description: 4 tabs (GitHub / DeFi / Knowledge Graph / Marimo) over the canonical crypteolas lakehouse. Cognee + Graphiti + Agno multi-agent team.
---

# Crypteolas — DeFi Monitor

> The 4 streams of the crypteolas data platform (GitHub / DeFi /
> Knowledge Graph / Marimo) as a single Gradio app. Cognee +
> Graphiti for the knowledge graph, Agno for the multi-agent
> team.

D2 of the spaces alignment plan (2026-06). A new HuggingFace
Space that exposes the crypteolas Defi monitor as 4 tabs +
the canonical Cognee + Graphiti knowledge graph + the Agno
multi-agent team.

## What's in this Space

- **Tab 1: GitHub** — the 4 GitHub streams (issues, PRs,
  commits, workflows) via DLT
- **Tab 2: DeFi** — the 4 DeFi streams (DeFiLlama,
  CoinGecko, Binance, Aave/Pendle subgraphs) via DLT
- **Tab 3: Knowledge Graph** — the Cognee + Graphiti
  bi-temporal graph (the canonical memory stack)
- **Tab 4: Marimo** — the 4 crypteolas marimo notebooks
  (per the crypteolas / dagster_assets / marimo pattern)

## Architecture

```
spaces/crypteolas_defi_monitor/
├── app.py                   # Gradio: 4-tab monitor
├── github_stream.py         # the GitHub DLT streams
├── defi_stream.py           # the DeFi DLT streams
├── knowledge_graph.py       # the Cognee + Graphiti cognify
├── marimo_stream.py         # the marimo notebook launcher
├── agno_team.py             # the Agno multi-agent team
├── requirements.txt
├── README.md
└── AGENTS.md
```

## Cross-references

- [`../AGENTS.md`](../AGENTS.md) — the Spaces parent
- [`../../tuatha/AGENTS.md`](../../tuatha/AGENTS.md) — the tuatha quadrant
- [`../../.agents/skills/dlt/SKILL.md`](../../.agents/skills/dlt/SKILL.md) — the DLT pattern
- [`../../.agents/skills/cognee/SKILL.md`](../../.agents/skills/cognee/SKILL.md) — the Cognee cognify
- [`../../.agents/skills/graphiti/SKILL.md`](../../.agents/skills/graphiti/SKILL.md) — the Graphiti temporal
- [`../../.agents/skills/agno/SKILL.md`](../../.agents/skills/agno/SKILL.md) — the Agno multi-agent
- [`../../.agents/skills/marimo/SKILL.md`](../../.agents/skills/marimo/SKILL.md) — the marimo pattern
