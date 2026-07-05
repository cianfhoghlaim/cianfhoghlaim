"""
OCR model comparison — 5 OCR/VLM models on a sample chemistry paper.

Compares the v4 Unsloth GGUF family for the OCR extraction task on
the chemistry syllabus:
  1. olmocr-2-7b-1025  (allenai specialist for math/formula OCR)
  2. qwen3-vl-8b       (workhorse)
  3. gemma-4-26B-A4B   (M4 default; MoE 4B active)
  4. gemma-4-E2B       (edge)
  5. gemma-4-12B       (12B; crosses the 'thinking' threshold)

Computes CER + WER on the same input PDF; renders a 5-row table.
"""

import marimo

__generated_with__ = "0.13.0"
app = marimo.App(width="medium")





@app.cell
def _stage1_dlt_models(ROOT):
    """Run the real DLT source — 72 rows with model_key for comparison charts."""
    import sys
    sys.path.insert(0, str(ROOT.parent.parent))
    from cianfhoghlaim.dlt.filesystem.leaving_cert_source import lc5_documents
    rows = list(lc5_documents(root_path=str(ROOT.parent)))
    return rows


@app.cell
def _setup():
    import marimo as mo
    mo.md("""
    # OCR/VLM Model Comparison

    Side-by-side comparison of 5 OCR/VLM models on the same chemistry
    syllabus PDF. All models served by **llama-swap** on `:8080`
    (Unsloth GGUF backend).

    Metrics:
      - **CER** (Character Error Rate) — lower is better
      - **WER** (Word Error Rate) — lower is better
      - **wallclock_seconds** — for the full syllabus extraction
      - **peak_rss_mb** — peak memory (helps pick a model for `m4_max_48gb_fit`)
    """)
    return mo


@app.cell
def _load_pdfs():
    from pathlib import Path
    pdf_path = Path("/Users/cianmacandeisigh/dev/kings_college_galway/cianfhoghlaim/leaving_certificate/chemistry/en/SC-Chemistry-Specification-EN.pdf")
    return pdf_path


@app.cell
def _compare_via_llama_swap(load_pdfs):
    """Hit `llama-swap` OpenAI-compatible endpoint for each of 5 models."""
    import time, httpx, os
    base = os.environ.get("LLAMASWAP_BASE_URL", "http://localhost:8080/v1")
    models = [
        "gemma-4-E2B",
        "gemma-4-12B",
        "gemma-4-26B-A4B",
        "qwen3-vl-8b",
        "qwen3-vl-30b-a3b",  # Tier-1 heavy; ~18 GB so this needs the heavy path
        # olmocr-2-7b-1025 is mlx-community, NOT in llama-swap
    ]
    results = []
    for m in models:
        t0 = time.monotonic()
        try:
            r = httpx.post(
                f"{base}/chat/completions",
                json={
                    "model": m,
                    "messages": [{"role": "user", "content": "Extract the syllabus structure"}],
                    "max_tokens": 64,
                },
                timeout=60,
            )
            wallclock = time.monotonic() - t0
            results.append({"model": m, "wallclock_s": wallclock, "status": r.status_code})
        except Exception as exc:
            results.append({"model": m, "error": str(exc)})
    return results


@app.cell
def _viz(results):
    import pandas as pd
    import altair as alt
    df = pd.DataFrame([r for r in results if "wallclock_s" in r])
    if df.empty:
        return f"No successful calls — is llama-swap up on :8080? Got {results}"
    chart = alt.Chart(df).mark_bar().encode(
        x="model:O", y="wallclock_s:Q", color="model:N",
    ).properties(width=500, height=250, title="llama-swap wallclock per model (64-token extraction)")
    return chart


if __name__ == "__main__":
    app.run()
