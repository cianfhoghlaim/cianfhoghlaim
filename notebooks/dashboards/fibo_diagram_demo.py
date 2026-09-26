"""marimo notebook: fibo_diagram_demo — the FIBO 2D diagram generation demo.

Per the 2026-10-04-fibo-asset-pipeline-v1 saga change (Plan 4 of
openspec/plans/2026-10-01-convergence-saga-v1.md).

A marimo notebook that demonstrates the FIBO 2D diagram generation pipeline:
- Shows the 8 canonical NCCA subjects with their deities + treasures
- Lets you render one subject (EN + GA) via FiboResource
- Validates the rendered asset via ValidationResource (the VLM scorer)
- Shows the validation score + iteration history

When litellm + the VLM are unreachable, the notebook shows the
stub mode (placeholder PNGs + null score) gracefully.

Run with:
    uv run marimo edit notebooks/dashboards/fibo_diagram_demo.py
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
        # FIBO 2D Diagram Demo (Plan 4 of the 2026-10 convergence saga)

        The FIBO asset pipeline turns canonical NCCA syllabus concepts
        into celtic-art window chrome + 2D sprite atlases for the 8
        NCCA subject realms (mathematics + applied_mathematics + chemistry
        + geography + history + english + gaeilge + computer_science).

        Each subject has a BAML prompt template that references the
        relevant Tuatha Dé deity + treasure + game UI inspiration (Hades /
        Clair Obscur / WoW / BitCraft).
        """
    )
    return


@app.cell
def _subjects() -> None:
    import marimo as mo
    from tuatha.asset_generation.fibo import get_fibo_prompt, list_subjects
    import json

    rows = []
    for subject in list_subjects():
        prompt = get_fibo_prompt(subject, "en")
        rows.append({
            "subject": subject,
            "deity": prompt["tuatha_de_deity"],
            "treasure": prompt["tuatha_de_treasure"],
            "ui_inspiration": prompt["game_ui_inspiration"],
            "baml_color": prompt["baml_color"],
        })

    mo.md(
        f"""
        ## The 8 canonical NCCA subjects + their FIBO prompts

        {mo.ui.table(rows, label="subjects")}
        """
    )
    return


@app.cell
def _render() -> None:
    import marimo as mo
    import asyncio
    from pathlib import Path

    subjects = ["mathematics", "applied_mathematics", "chemistry", "geography",
                "history", "english", "gaeilge", "computer_science"]
    languages = ["en", "ga"]

    subject = mo.ui.dropdown(options=subjects, value="chemistry", label="Subject")
    language = mo.ui.dropdown(options=languages, value="en", label="Language")

    return subject, language


@app.cell
def _render_action(subject, language) -> None:
    import marimo as mo
    import asyncio
    import time
    from pathlib import Path

    from tuatha.asset_generation.fibo import get_fibo_prompt
    from tuatha.asset_generation.fibo.resources import FiboResource, ValidationResource
    from tuatha.asset_generation.fibo.assets import fibo_json_configs

    run_btn = mo.ui.run_button(label="Render FIBO diagram")

    if run_btn.value:
        prompt = get_fibo_prompt(subject.value, language.value)
        mo.md(
            f"""
            ### Subject: {subject.value} ({language.value})

            - **Deity**: {prompt['tuatha_de_deity']}
            - **Treasure**: {prompt['tuatha_de_treasure']}
            - **UI inspiration**: {prompt['game_ui_inspiration']}
            - **Prompt**: {prompt['prompt'][:120]}...

            (Rendering now — this calls FiboResource.render() + ValidationResource.validate())
            """
        )

        # Actually render
        async def render():
            fr = FiboResource(model_name="local/image/qwen-image", api_base="http://192.168.148.5:8889/v1", api_key="sk-unsloth-dev-noop-key")
            out_dir = Path("stedding/fibo_demo") / subject.value / language.value
            out_dir.mkdir(parents=True, exist_ok=True)
            out_path = str(out_dir / f"{subject.value}_{language.value}.png")
            result = fr.render(prompt=prompt["prompt"], palette_hex=["#1a0e1a", "#d4af37"], out_path=out_path)

            vr = ValidationResource(score_threshold=0.7)
            val = vr.validate(asset_path=result["path"], criteria=[f"subject = {subject.value}"])

            return result, val

        try:
            result, val = asyncio.run(render())
            mo.md(
                f"""
                ### Render result

                - **Path**: {result['path']}
                - **SHA256**: {result['sha256'][:24]}...
                - **Stub**: {result['stub']} (offline fallback fires when litellm gateway is unreachable)
                - **Validation score**: {val.get('score', 0):.2f}
                - **Validation pass**: {val.get('pass', False)}
                - **Validation stub**: {val.get('stub', True)}
                """
            )
        except Exception as exc:
            mo.md(f"  Error: {exc}")
    else:
        mo.md("Click **Render FIBO diagram** to render + validate.")
    return


@app.cell
def _summary() -> None:
    import marimo as mo

    mo.md(
        """
        ## Summary

        - **Subjects**: 8 (the canonical NCCA Leaving Cert subjects)
        - **Languages**: 2 (EN + GA)
        - **Asset pairs**: 16 (8 subjects × 2 languages)
        - **BAML function**: `ExtractGameplayPattern` (Plan 3) + the FIBO prompt templates
        - **Dagster assets**: 3 (`fibo_json_configs` + `generated_images` + `fibo_configs_from_syllabus_diagrams`)
        - **Resources**: 2 (`FiboResource` + `ValidationResource`)
        - **Reference**: `openspec/changes/2026-10-04-fibo-asset-pipeline-v1/specs/fibo-asset-pipeline/spec.md`
        """
    )
    return


if __name__ == "__main__":
    app.run()
