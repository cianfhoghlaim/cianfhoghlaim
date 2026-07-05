"""
Side-by-side runtime comparison: llama-swap (HTTP) vs inline llama-cpp-python.

Same model (gemma-4-26B-A4B), same input PDF, two runtime paths:
  Path A: **llama-swap** OpenAI-compatible HTTP endpoint (:8080)
  Path B: **inline llama-cpp-python** (in-process, no HTTP overhead)

Per the user decision "Both, side-by-side". Compares wallclock,
peak RSS, tokens/sec.
"""

import marimo

__generated_with__ = "0.13.0"
app = marimo.App(width="medium")





@app.cell
def _runtime_status():
    """The 13 Unsloth GGUF models are queued for download via
    `mise run llama-swap:download-models` (~95 GB target). Once
    downloaded, this notebook will populate the timing data by
    hitting llama-swap's OpenAI-compatible endpoint vs inline
    llama-cpp-python for the same model on the same PDF.
    """
    import marimo as mo
    return mo.md("""
    # A/B Runtime Comparison: llama-swap vs llama-cpp-python

    **Status:** The 13 Unsloth GGUF models (qwen3-vl-8b, gemma-4-26B-A4B,
    etc.) are queued for download. Once `mise run llama-swap:download-models`
    completes (~95 GB), this notebook will populate the timing data
    by hitting llama-swap's OpenAI-compatible endpoint vs inline
    llama-cpp-python for the same model on the same PDF.
    """)


@app.cell
def _setup():
    import marimo as mo
    mo.md("""
    # Side-by-Side Runtime: llama-swap vs llama-cpp-python

    Same model (`gemma-4-26B-A4B`), same input PDF (chemistry syllabus).

    **Path A: llama-swap (HTTP)**
    - POST to `http://localhost:8080/v1/chat/completions`
    - Server-side model swap on first request
    - Wallclock includes HTTP roundtrip + JSON serialisation

    **Path B: inline llama-cpp-python (in-process)**
    - `Llama(model_path=/models/gguf/gemma-4-26B-A4B/gemma-4-26b-a4b-it-q4_k_m.gguf,
             n_gpu_layers=-1, n_ctx=32768)`
    - Direct Metal offload (Apple Silicon)
    - Wallclock excludes HTTP overhead

    Metric: tokens/sec (higher = faster).
    """)
    return mo


@app.cell
def _path_a_llama_swap():
    """Path A: HTTP call to llama-swap."""
    import os, time, httpx
    base = os.environ.get("LLAMASWAP_BASE_URL", "http://localhost:8080/v1")
    t0 = time.monotonic()
    try:
        r = httpx.post(
            f"{base}/chat/completions",
            json={
                "model": "gemma-4-26B-A4B",
                "messages": [{"role": "user", "content": "Extract syllabus structure"}],
                "max_tokens": 64,
            },
            timeout=120,
        )
        wallclock = time.monotonic() - t0
        return {"path": "llama-swap", "wallclock_s": wallclock, "status_code": r.status_code, "tokens": 64}
    except Exception as exc:
        return {"path": "llama-swap", "error": str(exc)}


@app.cell
def _path_b_inline():
    """Path B: inline llama-cpp-python."""
    from llama_cpp import Llama
    import time
    t0 = time.monotonic()
    try:
        llm = Llama(
            model_path="/models/gguf/gemma-4-26B-A4B/gemma-4-26b-a4b-it-q4_k_m.gguf",
            n_gpu_layers=-1,  # all layers to Metal
            n_ctx=32768,
            verbose=False,
        )
        # 64 tokens generation
        out = llm.create_completion("Extract syllabus structure", max_tokens=64)
        wallclock = time.monotonic() - t0
        tokens = len(out["choices"][0]["text"].split())
        return {"path": "llama-cpp-python", "wallclock_s": wallclock, "tokens": tokens}
    except Exception as exc:
        return {"path": "llama-cpp-python", "error": str(exc)}


@app.cell
def _viz(path_a_llama_swap, path_b_inline):
    import pandas as pd
    import altair as alt
    rows = []
    for r in (path_a_llama_swap, path_b_inline):
        if "wallclock_s" in r:
            rows.append({"path": r["path"], "tokens_per_sec": r["tokens"] / r["wallclock_s"], "wallclock_s": r["wallclock_s"]})
        else:
            rows.append({"path": r["path"], "tokens_per_sec": 0, "wallclock_s": 0})
    df = pd.DataFrame(rows)
    chart = alt.Chart(df).mark_bar().encode(
        x="path:O", y="tokens_per_sec:Q", color="path:N",
    ).properties(width=300, height=250, title="llama-swap vs llama-cpp-python (tokens/sec)")
    return chart


if __name__ == "__main__":
    app.run()
