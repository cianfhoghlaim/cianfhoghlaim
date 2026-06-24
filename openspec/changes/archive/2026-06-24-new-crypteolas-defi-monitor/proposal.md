## Why

D2 of the spaces alignment plan. Adds a new HuggingFace
Space `spaces/crypteolas_defi_monitor/` that exposes the
crypteolas Defi monitor as 4 tabs + the canonical Cognee +
Graphiti knowledge graph + the Agno multi-agent team.

The Space is the **4-stream integration** for the crypteolas
data platform: GitHub + DeFi + Knowledge Graph + Marimo.

## What changes

- New `spaces/crypteolas_defi_monitor/` directory:
  - `app.py` (the 4-tab Gradio app)
  - `README.md` (the HF Space README)
  - `AGENTS.md` (the developer-quick-reference)
  - `requirements.txt`
- 1 ADDED Requirement to the `infrastructure-stacks` spec

## Out of scope

- The 8 DLT stream implementations (planned follow-up; uses
  the canonical `dlt` skill)
- The Cognee + Graphiti cognify (planned follow-up; uses
  the canonical `cognee` + `graphiti` skills)
- The Agno multi-agent team (planned follow-up; uses the
  canonical `agno` skill)
- The 4 marimo notebooks (planned follow-up; uses the
  canonical `marimo` skill)
