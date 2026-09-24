#!/usr/bin/env python3
"""Generate the 20 walkthrough marimo notebooks for the UoG tertiary pipeline.

Per openspec/changes/2026-09-23-uog-tertiary-real-data-upgrade-v1/.
Pattern mirrors the canonical notebooks/ciancheiltis_en_ga_roi.py
(dual-mode script, _intro() markdown cell, _phase_status() cell,
DuckLake query cell).

The 20 notebooks:
- 8 feature walkthroughs (feature_*.py)
- 5 per-layer walkthroughs (layer_*.py)
- 7 per-model walkthroughs (model_*.py)
"""
from __future__ import annotations

from pathlib import Path

WALKTHROUGHS = Path("notebooks/_shared/tertiary/walkthroughs")


FEATURE_WALKTHROUGHS = [
    ("01_modules_pipeline", "4-tier College → School → Programme → Module pipeline",
     "dlt_sources/british_isles/ireland/tertiary/uog/{colleges,schools,programmes,modules}.py + uog_to_tertiary.py bridge"),
    ("02_handbooks_ocr", "BIEP v2 4-path OCR ensemble on per-module PDF handbooks",
     "dlt_sources/.../tertiary/uog/module_handbooks.py + cocoindex_flows/.../module_handbook_flow.py + the 4 BAML functions in module_handbook.baml"),
    ("03_reading_lists", "Per-module reading list extraction",
     "dlt_sources/.../tertiary/uog/reading_lists.py + cocoindex_flows/.../reading_list_flow.py + reading_list.baml"),
    ("04_past_papers", "Per-module past papers from regexam.nuigalway.ie",
     "dlt_sources/.../tertiary/uog/{past_papers,regexam_papers}.py + the uoa-portal-vault GOLD_STANDARD stack"),
    ("05_canvas_materials", "Canvas LMS REST + M365 OAuth fallback",
     "dlt_sources/.../tertiary/uog/canvas_materials.py + the canvas-nuig GOLD_STANDARD stack"),
    ("06_governance_minutes", "UoG governance minutes extraction",
     "dlt_sources/.../tertiary/uog/governance_minutes.py + cocoindex_flows/.../governance_flow.py + governance_minute.baml"),
    ("07_press_research", "Press releases + research outputs pipelines",
     "dlt_sources/.../tertiary/uog/{press_releases,research_outputs}.py + 2 CocoIndex flows + 2 BAML files"),
    ("08_students_union", "5 SU agents + snake_case full-name module map",
     "agents/meaisinfhoghlaim/educational/students_union/{root_agent,config,5 specialists,5 tools}.py"),
]

LAYER_WALKTHROUGHS = [
    ("01_ingestion", "L1 Ingestion — 14 DLT sources in dlt_sources/british_isles/ireland/tertiary/uog/",
     "orchestration/defs/1_ingestion/tertiary/uog/{14 DLT asset entries}"),
    ("02_materials", "L2 Materials — 8 BAML extractions + 6 RAGAS asset checks",
     "baml_src/british_isles/ireland/tertiary/{8 BAML files} + orchestration/defs/2_materials/tertiary_extraction/"),
    ("03_model_lifecycle", "L3 Model Lifecycle — embedder + OCR ensemble + vision-language routing",
     "orchestration/defs/3_model_lifecycle/tertiary/ + meaisinfhoghlaim/models/model_registry.py (the 7-family registry)"),
    ("04_asset_generation", "L4 Asset Generation — 10 CocoIndex flows + per-module factory",
     "orchestration/defs/4_asset_generation/tertiary_uog/ + cocoindex_flows/.../tertiary/uog/"),
    ("05_agent_ops", "L5 Agent Ops — uoa_portal + students_union ADK agents + RAGAS",
     "orchestration/defs/5_agent_ops/{uoa_portal,students_union,tertiary} + agents/uoa_portal/portal_agent.py"),
]

MODEL_WALKTHROUGHS = [
    ("01_ocr_vision", "22-entry ocr_vision family (qwen3-vl-8b, gemma-4-26B-A4B, olmocr-2-7b-1025, etc.)",
     "meaisinfhoghlaim/models/registry.py:VISION_MODELS + meaisinfhoghlaim/models/llama_swap_config.yaml"),
    ("02_text_llm", "9-entry text_llm family (minimax-m3 + 7-tier fallback)",
     "baml_src/clients.baml + meaisinfhoghlaim/models/model_registry.py"),
    ("03_embedder", "3-entry embedder family (bge-m3 + bge-large-en + MiniLM)",
     "meaisinfhoghlaim/models/model_registry.py + cocoindex_flows/_shared/_lifespan.py:108"),
    ("04_rerank", "3-entry rerank family (Jina + Cohere + Aliyun)",
     "meaisinfhoghlaim/models/model_registry.py + cocoindex_flows/_shared/reranker.py"),
    ("05_image_gen", "5-entry image_gen family (flux2-dev + z-image-turbo + qwen-image + sdxl + fibo)",
     "meaisinfhoghlaim/models/model_registry.py"),
    ("06_voice", "5-entry voice family (whisper-large + wav2vec2-irish + chatterbox + aba-tts)",
     "meaisinfhoghlaim/models/model_registry.py"),
    ("07_translation", "3-entry translation family (opus-mt + m2m100 + nllb)",
     "meaisinfhoghlaim/models/model_registry.py"),
]


TEMPLATE = '''"""marimo notebook: {walkthrough_name} — UoG tertiary pipeline walkthrough.

Per openspec/changes/2026-09-23-uog-tertiary-real-data-upgrade-v1/.
Pattern mirrors notebooks/ciancheiltis_en_ga_roi.py (dual-mode script,
_intro() markdown cell describing what + how + where the docs live,
_phase_status() cell querying DuckLake).

{walkthrough_description}

Reference surfaces:
{reference_surfaces}

Run with:
    uv run marimo edit notebooks/_shared/tertiary/walkthroughs/{walkthrough_id}.py
    uv run python notebooks/_shared/tertiary/walkthroughs/{walkthrough_id}.py --cli
"""
from __future__ import annotations

import marimo

__generated_with = "0.14.0"
app = marimo.App(width="full")


@app.cell
def _intro() -> None:
    import marimo as mo

    mo.md(
        """
        # {walkthrough_name}

        {walkthrough_description_long}

        ## Reference surfaces
{reference_surfaces_md}

        See:
        - `openspec/changes/2026-09-23-uog-tertiary-real-data-upgrade-v1/specs/`
        - `openspec/changes/2026-09-23-consolidate-uog-tertiary-pipeline-v1/specs/cianfhoghlaim-tertiary-pipeline/spec.md`
        - `notebooks/_shared/tertiary/students_union_adk_case_studies.py`
        - `.agents/skills/uoa-tertiary-pipeline/SKILL.md`
        - `baml_src/british_isles/ireland/tertiary/university_extraction.baml`
        """
    )
    return


@app.cell
def _phase_status() -> None:
    import marimo as mo
    from datetime import datetime

    mo.md(
        f"""
        ## Phase status (live DuckLake query)

        Walkthrough `{walkthrough_name}` — fetched at {{datetime.utcnow().isoformat()}}.
        """
    )
    return


@app.cell
def _ducklake_query() -> None:
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
    from ducklake_helpers import walkthrough_1_data_inlining  # type: ignore

    result = walkthrough_1_data_inlining()
    return (result,)


@app.cell
def _render_result(result) -> None:
    import marimo as mo

    mo.md(f"```json\\n{{result}}\\n```")
    return


if __name__ == "__main__":
    app.run()
'''


def main() -> None:
    WALKTHROUGHS.mkdir(parents=True, exist_ok=True)
    count = 0
    for walkthrough_id, title, _desc in FEATURE_WALKTHROUGHS + LAYER_WALKTHROUGHS + MODEL_WALKTHROUGHS:
        walkthrough_name = walkthrough_id + ": " + title
        walkthrough_description = title
        walkthrough_description_long = (
            f"This notebook walks through **{title}** — what it is, "
            f"how it works, where the docs live, and how to query the live DuckLake data."
        )
        reference_surfaces_md = "\\n        - " + "\\n        - ".join(_desc.split(" + "))
        reference_surfaces = _desc.replace("+ ", "+ \n")
        content = TEMPLATE.format(
            walkthrough_name=walkthrough_name,
            walkthrough_id=walkthrough_id,
            walkthrough_description=walkthrough_description,
            walkthrough_description_long=walkthrough_description_long,
            reference_surfaces=reference_surfaces,
            reference_surfaces_md=reference_surfaces_md,
        )
        target = WALKTHROUGHS / f"{walkthrough_id}.py"
        target.write_text(content)
        count += 1
    print(f"Generated {count} walkthrough notebooks in {WALKTHROUGHS}")


if __name__ == "__main__":
    main()
