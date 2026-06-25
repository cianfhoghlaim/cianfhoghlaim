## Why

D1 of the spaces alignment plan. Adds a new HuggingFace Space
`spaces/oideachais_mission_control/` that surfaces the 5
educational stages of the oideachais quadrant as marimo
notebooks over the canonical MotherDuck lakehouse.

The Space is the **operational mission control** for the
oideachais data platform: 5 tabs (Aistear / Primary / JC /
SC / Tertiary), each backed by a marimo notebook from
`sruth/oideachais/notebooks/`, plus Cognee cognify + BAML
extraction buttons per stage.

## What changes

- New `spaces/oideachais_mission_control/` directory:
  - `app.py` (the 5-tab Gradio app)
  - `README.md` (the HF Space README)
  - `AGENTS.md` (the developer-quick-reference)
  - `requirements.txt` (Gradio 5.x + marimo + duckdb + pydantic)
- 1 ADDED Requirement to the `oideachais-pipeline` spec

## Out of scope

- The 5 marimo notebook implementations (planned follow-up)
- The Cognee cognify + BAML extraction button implementations
  (planned follow-up; the buttons are placeholders)
- The MotherDuck Dive per stage (planned follow-up; uses
  the `motherduck-analytics` skill)
