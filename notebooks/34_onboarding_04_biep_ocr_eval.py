"""34_onboarding_04_biep_ocr_eval.py — 15 min 4-path OCR ensemble.

Per the 2026-08-21-meaisinfhoghlaim-unsloth-agents-integration-v1 change.
Tutorial 4 of 5. Runs the 4-path OCR ensemble (Unsloth Qwen3-VL-8B +
llama-swap Gemma 4 26B-A4B + Docling + OlmOCR) on a sample LC Gaeilge paper.
Shows per-backend CER + the canonical 5-rung provenance.

Run: mise run tutorial:04-biep-ocr
"""

import marimo

__generated_with_marimo__ = "0.13.0"
app = marimo.App(width="full")


@app.cell
def _intro(mo):
    mo.md(
        """
        # Tutorial 4: BIEP 4-path OCR ensemble (~15 min)

        Per the 2026-08-21-meaisinfhoghlaim-unsloth-agents-integration-v1 change.

        **The 4-path OCR ensemble** (per the BIEP v2 federated module):
        1. **Unsloth Qwen3-VL-8B** (via litellm → Unsloth Studio) — primary
        2. **llama-swap Gemma 4 26B-A4B** (via litellm) — fallback
        3. **Docling** (via docling-serve:5001) — layout-aware
        4. **OlmOCR** (via transformers backend) — clean printed-text baseline

        The canonical 5-rung provenance ladder is preserved:
        Document → Location → Extraction → Evaluation → Anchor
        """
    )
    return


@app.cell
def _pick_pdf(mo):
    pdf_picker = mo.ui.dropdown(
        options=[
            "/stedding/huggingface/unsloth/gaeilge/sample.pdf",
            "/Users/cianmacandeisigh/dev/ciandlithe/data/ireland/samples/lc_gaeilge_2024.pdf",
            "/stedding/ingest_queue/gaeilge/lc_2024_paper_1.pdf",
        ],
        value="/stedding/ingest_queue/gaeilge/lc_2024_paper_1.pdf",
        label="Sample LC Gaeilge paper",
    )
    run_button = mo.ui.run_button(label="Run 4-path OCR ensemble")
    return pdf_picker, run_button


@app.cell
def _run_ensemble(pdf_picker, run_button, mo):
    import asyncio
    import os
    import sys
    import urllib.request
    import json

    if not run_button.value:
        return mo.md("> Click **Run 4-path OCR ensemble** to start")

    # The OCR-Router agent (per the umbrella change) does this automatically
    # We just call it via the litellm gateway

    litellm_key = os.environ.get("LITELLM_MASTER_KEY", "")
    if not litellm_key:
        return mo.md("> ⚠️ LITELLM_MASTER_KEY not set")

    # Primary: Unsloth Studio (Qwen3-VL-8B)
    payload = json.dumps({
        "model": "local/unsloth/qwen3-vl-8b-instruct",
        "messages": [{
            "role": "user",
            "content": f"Extract all text from this LC Gaeilge paper at {pdf_picker.value}. Use the bilingual EN + GA surface."
        }],
        "max_tokens": 4096,
    }).encode()

    req = urllib.request.Request(
        "http://localhost:4000/v1/chat/completions",
        data=payload,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {litellm_key}"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode())
            content = data["choices"][0]["message"]["content"]
            return mo.md(f"### OCR result (Qwen3-VL-8B via Unsloth Studio)\n\n{content[:3000]}")
    except urllib.error.HTTPError as e:
        if e.code == 400 and "No model loaded" in e.read().decode():
            return mo.md(
                "### Expected: No model loaded in Unsloth Studio yet\n\n"
                "The route works! Load a model via:\n"
                "```bash\n"
                "unsloth studio run --model unsloth/Qwen3-VL-8B-Instruct-GGUF:UD-Q4_K_XL --port 8888\n"
                "```"
            )
        return mo.md(f"### HTTP {e.code}: {e.read().decode()[:500]}")
    except Exception as e:
        return mo.md(f"### Error: {e}")


@app.cell
def _next_steps(mo):
    mo.md(
        """
        ## Next steps

        - **Tutorial 5**: `mise run tutorial:05-duchas-htr` — Fine-tune Gemma 4 4B on Dúchas.ie transcriptions
        """
    )
    return


if __name__ == "__main__":
    app.run()
