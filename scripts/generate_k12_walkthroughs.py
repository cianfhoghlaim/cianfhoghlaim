#!/usr/bin/env python3
"""Generate the 20 K-12 walkthrough marimo notebooks.

Per openspec/changes/2026-09-23-k12-teacher-student-pipeline-v1/.
Pattern mirrors scripts/generate_tertiary_walkthroughs.py.

The 20 notebooks:
- 8 feature walkthroughs (aistear_framework + primary_curriculum +
  primary_jc_combined + jc_subject_spec + jc_cba + ty_programme +
  lc_subject + teacher_workload)
- 5 per-layer walkthroughs (1_ingestion + 2_materials + 3_model_lifecycle +
  4_asset_generation + 5_agent_ops for K-12)
- 7 per-model walkthroughs (ocr_vision + text_llm + embedder + rerank +
  image_gen + voice + translation for K-12)
"""
from __future__ import annotations

from pathlib import Path

WALKTHROUGHS = Path("notebooks/_shared/k12/walkthroughs")


FEATURE_WALKTHROUGHS = [
    ("01_aistear_framework", "Aistear (Early Childhood) framework + 14 principles",
     "dlt_sources/british_isles/ireland/education/aistear.py + cocoindex_flows/subjects/aistear_embedding.py + baml_src/.../stages/aistear.baml"),
    ("02_primary_curriculum", "12 NCCA primary curriculum areas (Firecrawl-verified)",
     "dlt_sources/.../education/primary.py + cocoindex_flows/subjects/primary_embedding.py + baml_src/.../primary/primary_extraction.baml"),
    ("03_primary_jc_combined", "Primary → Junior Cycle bridging pipeline",
     "dlt_sources/.../education/primary_jc_combined.py + baml_src/.../stages/primary.baml + stages/junior_cycle.baml"),
    ("04_jc_subject_spec", "18 NCCA Junior Cycle subject specifications",
     "dlt_sources/.../education/junior_cycle.py + cocoindex_flows/subjects/junior_cycle_embedding.py + baml_src/.../junior_cycle_extraction/jc_subject_extraction.baml"),
    ("05_jc_cba", "Junior Cycle Classroom-Based Assessment (CBA) tracker",
     "baml_src/.../junior_cycle_extraction/cba_task_extraction.baml + agents/.../students_jc/cba_planner_agent.py"),
    ("06_ty_programme", "Transition Year programme planning",
     "dlt_sources/.../education/senior_cycle.py + LCA programmes + agents/.../students_jc/study_plan_agent.py"),
    ("07_lc_subject", "Leaving Certificate subject picker + past papers",
     "dlt_sources/.../education/senior_cycle.py + cocoindex_flows/subjects/senior_cycle_embedding.py"),
    ("08_teacher_workload", "Teacher timetable + class assignments + OIDE/PDST planning",
     "dlt_sources/.../education/teacher_workload.py + dlt_sources/.../education/teacher_pd.py + agents/.../teachers/lesson_planner_agent.py"),
]

LAYER_WALKTHROUGHS = [
    ("01_ingestion", "L1 Ingestion — 9 K-12 DLT sources (aistear + primary + jc + sc + oide + pdst + teacher_pd + class_roster + teacher_workload)",
     "orchestration/defs/1_ingestion/primary_jc/{9 DLT asset subdirs}"),
    ("02_materials", "L2 Materials — BAML extractions for aistear + primary + jc + sc",
     "baml_src/british_isles/ireland/education/{aistear,primary,junior_cycle,senior_cycle}.baml + orchestration/defs/2_materials/primary_jc/"),
    ("03_model_lifecycle", "L3 Model Lifecycle — BGE-M3 embedder + Gemma-4 extract + OlmOCR",
     "orchestration/defs/3_model_lifecycle/primary_jc/ + meaisinfhoghlaim/models/model_registry.py"),
    ("04_asset_generation", "L4 Asset Generation — 8 K-12 CocoIndex flows + factory",
     "orchestration/defs/4_asset_generation/primary_jc/ + cocoindex_flows/british_isles/ireland/education/_shared.py"),
    ("05_agent_ops", "L5 Agent Ops — 10 K-12 ADK agents (5 teacher + 5 student)",
     "orchestration/defs/5_agent_ops/primary_jc/ + agents/meaisinfhoghlaim/educational/teachers/ + agents/meaisinfhoghlaim/educational/students_jc/"),
]

MODEL_WALKTHROUGHS = [
    ("01_ocr_vision", "7-entry ocr_vision family (qwen3-vl-8b + olmocr-2-7b-1025 for K-12 PDFs)",
     "meaisinfhoghlaim/models/registry.py:VISION_MODELS"),
    ("02_text_llm", "9-entry text_llm family (minimax-m3 + the 7-tier fallback)",
     "baml_src/clients.baml + meaisinfhoghlaim/models/model_registry.py"),
    ("03_embedder", "3-entry embedder family (bge-m3 for K-12 CocoIndex flows)",
     "meaisinfhoghlaim/models/model_registry.py + cocoindex_flows/_shared/_lifespan.py:108"),
    ("04_rerank", "3-entry rerank family (Jina + Cohere + Aliyun)",
     "meaisinfhoghlaim/models/model_registry.py"),
    ("05_image_gen", "5-entry image_gen family (for SEN visual aids + classroom posters)",
     "meaisinfhoghlaim/models/model_registry.py"),
    ("06_voice", "5-entry voice family (whisper-large for SEN audio supports + wav2vec2-irish for Gaeltacht schools)",
     "meaisinfhoghlaim/models/model_registry.py"),
    ("07_translation", "3-entry translation family (opus-mt + m2m100 + nllb) for EN ↔ GA SEN letters",
     "meaisinfhoghlaim/models/model_registry.py"),
]


TEMPLATE = '''"""marimo notebook: {walkthrough_name} — K-12 teacher + student pipeline walkthrough.

Per openspec/changes/2026-09-23-k12-teacher-student-pipeline-v1/.
Pattern mirrors notebooks/ciancheiltis_en_ga_roi.py (dual-mode script,
_intro() markdown cell describing what + how + where the docs live,
_phase_status() cell querying DuckLake).

{walkthrough_description}

Reference surfaces:
{reference_surfaces}

Run with:
    uv run marimo edit notebooks/_shared/k12/walkthroughs/{walkthrough_id}.py
    uv run python notebooks/_shared/k12/walkthroughs/{walkthrough_id}.py --cli
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
        - `openspec/changes/2026-09-23-k12-teacher-student-pipeline-v1/specs/`
        - `openspec/changes/2026-09-23-uog-tertiary-real-data-upgrade-v1/specs/cianfhoghlaim-tertiary-pipeline/spec.md`
        - `.agents/skills/uoa-tertiary-pipeline/SKILL.md`
        - `baml_src/british_isles/ireland/education/stages/aistear.baml`
        - `cocoindex_flows/british_isles/ireland/education/_shared.py`
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
    from ducklake_helpers import walkthrough_k12_demo  # type: ignore

    result = walkthrough_k12_demo()
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
    print(f"Generated {count} K-12 walkthrough notebooks in {WALKTHROUGHS}")


if __name__ == "__main__":
    main()
