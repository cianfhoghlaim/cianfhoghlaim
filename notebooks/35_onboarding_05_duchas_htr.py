"""35_onboarding_05_duchas_htr.py — 20 min Dúchas.ie HTR fine-tune.

Per the 2026-08-21-meaisinfhoghlaim-unsloth-agents-integration-v1 change.
Tutorial 5 of 5. Fine-tunes Gemma 4 4B on Dúchas.ie transcriptions.
Pushes the adapter to HuggingFace Hub for Unsloth Studio inference.

Run: mise run tutorial:05-duchas-htr
"""

import marimo

__generated_with_marimo__ = "0.13.0"
app = marimo.App(width="full")


@app.cell
def _intro(mo):
    mo.md(
        """
        # Tutorial 5: Dúchas.ie HTR fine-tune (~20 min)

        Per the 2026-08-21-meaisinfhoghlaim-unsloth-agents-integration-v1 change.

        **The HTR pipeline** (in ciancheiltis sister repo):
        - **Source**: `dlt_sources/cultural_heritage/duchas_images_htr.py`
        - **Dataset**: Dúchas.ie National Folklore Collection (cbes, transcribed-only)
        - **Fine-tune**: Unsloth + QLoRA r=8 (fits in M4 Max 48 GB)
        - **Output**: `gemma-4-e2b-gaeilge-htr-v1` adapter → HuggingFace Hub
        - **Inference**: Unsloth Studio loads the adapter for downstream HTR

        **Bilingual context**:
        - **English + Irish** (Gaeilge) — NCCA Leaving Certificate + WJEC Welsh-medium
        - **EU** — EUR-Lex Irish-English parallel corpus
        - **Dataset alignment** — `bilingual_align` tool (fast_align + eflomal)
        """
    )
    return


@app.cell
def _pick_fine_tune(mo):
    base_model_picker = mo.ui.dropdown(
        options=[
            "unsloth/gemma-4-E2B-it-GGUF",
            "unsloth/Qwen3-VL-8B-Instruct-GGUF",
            "unsloth/gemma-4-E4B-it-GGUF",
        ],
        value="unsloth/gemma-4-E2B-it-GGUF",
        label="Base model (Unsloth GGUF)",
    )
    dataset_picker = mo.ui.dropdown(
        options=[
            "oideachais.cultural_heritage.cbes",
            "ciancheiltis.language.duchas_transcriptions",
            "tuatha.educational.gaeilge_syllabus",
        ],
        value="oideachais.cultural_heritage.cbes",
        label="DuckLake dataset (target)",
    )
    lora_r = mo.ui.slider(start=4, stop=64, step=4, value=8, label="LoRA rank")
    epochs = mo.ui.slider(start=1, stop=10, step=1, value=3, label="Epochs")
    backend_picker = mo.ui.dropdown(
        options=["m4_max", "modal_h100"],
        value="m4_max",
        label="Backend",
    )
    run_button = mo.ui.run_button(label="Start fine-tune (dry-run preview)")
    return base_model_picker, dataset_picker, lora_r, epochs, backend_picker, run_button


@app.cell
def _preview_fine_tune(base_model_picker, dataset_picker, lora_r, epochs, backend_picker, run_button, mo):
    if not run_button.value:
        return mo.md("> Click **Start fine-tune (dry-run preview)** to see the command that would be run")

    cmd = [
        "uv run python3 meaisinfhoghlaim/training/modal_finetune/finetune_unsloth_local.py",
        f"  --base-model {base_model_picker.value}",
        f"  --dataset {dataset_picker.value}",
        f"  --lora-r {lora_r.value}",
        f"  --epochs {epochs.value}",
        f"  --output-dir ./checkpoints/gaeilge-htr",
        f"  --hub-model-id meaisinfhoghlaim/gaeilge-htr-adapter-v1",
    ]

    return mo.md(
        f"### Fine-tune command (dry-run)\n\n```bash\n{chr(10).join(cmd)}\n```\n\n"
        f"**Config**:\n"
        f"- Base model: `{base_model_picker.value}`\n"
        f"- Dataset: `{dataset_picker.value}`\n"
        f"- LoRA rank: {lora_r.value}\n"
        f"- Epochs: {epochs.value}\n"
        f"- Backend: `{backend_picker.value}`\n\n"
        f"**Note**: this is a DRY-RUN preview. The actual fine-tune is triggered via the `htr_finetune_unsloth_local` tool "
        f"(see `packages/fleet/src/cianfhoghlaim/fleet/tools/htr_finetune_unsloth_local.py`)."
    )


@app.cell
def _next_steps(mo):
    mo.md(
        """
        ## 🎉 Tutorial series complete

        You've now walked through:
        1. **Tutorial 1**: dev env validation
        2. **Tutorial 2**: first Unsloth Studio chat
        3. **Tutorial 3**: 4-stack walkthrough
        4. **Tutorial 4**: 4-path OCR ensemble
        5. **Tutorial 5**: Dúchas.ie HTR fine-tune

        ## Next steps

        - Run `mise run tutorial:verify` — the 7-step verification protocol
        - Read `openspec/changes/2026-08-21-meaisinfhoghlaim-unsloth-agents-integration-v1/` — the umbrella change
        - Read `openspec/specs/meaisinfhoghlaim-ocr-htr/` — the OCR/HTR spec
        - Explore `packages/fleet/src/cianfhoghlaim/fleet/educational/` — the 5 agents
        - Explore `packages/fleet/src/cianfhoghlaim/fleet/tools/` — the 8 tools
        """
    )
    return


if __name__ == "__main__":
    app.run()
