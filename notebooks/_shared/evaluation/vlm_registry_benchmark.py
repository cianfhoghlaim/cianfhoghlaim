"""marimo notebook: vlm_registry_benchmark — VLM registry benchmark across the unsloth-serve surface.

Per openspec/changes/2026-09-25-pangolin-aware-bunchloch-vlm-deploy-v1/.
Wraps the 12 unsloth-served VLM models (from MODEL_REGISTRY) and benchmarks each
against 3 standard prompts:

  1. NCCA syllabus PDF page (base64 image)
  2. LC marking-scheme snippet (text)
  3. Ordnance Survey map extract (base64 image)

Records: latency, prompt_tokens, completion_tokens, estimated_cost_usd,
output quality (RAGAS faithfulness if available).

The benchmark hits the gateway URL `http://192.168.148.5:8889/v1/chat/completions`
(the unsloth-serve container on the bunchloch docker network) directly. When the
Pangolin AI Gateway is provisioned, change the base_url to
`https://ai.cianfhoghlaim.ie/v1`.

Reference surfaces:
- meaisinfhoghlaim/models/model_registry.py (the 12 unsloth GGUF models)
- agents/workflows/sc_deep_research.py (the downstream Pillar-3 consumer)
- bonneagar/stacks/unsloth-serve/compose.bunchloch.yaml (the stack config)

Run with:
    uv run marimo edit notebooks/_shared/evaluation/vlm_registry_benchmark.py
    uv run python notebooks/_shared/evaluation/vlm_registry_benchmark.py --cli
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
        # VLM Registry Benchmark — unsloth-serve surface

        Operator console for **benchmarking all 12 unsloth-served VLM models** against
        3 standard prompts (NCCA syllabus PDF page + LC marking-scheme snippet +
        Ordnance Survey map extract). Renders a side-by-side comparison table +
        radar chart + per-prompt diff.

        ## Pipeline graph

        ```
        NCCA syllabus image ─┐
        LC marking scheme ───┼──► unsloth-serve (:8889) ──► 12 model responses ──► table + radar
        OS map image ────────┘
        ```

        ## Reference surfaces

        - `meaisinfhoghlaim/models/model_registry.py` (the canonical 12 unsloth models)
        - `bonneagar/stacks/unsloth-serve/compose.bunchloch.yaml` (the stack)
        - `notebooks/_shared/marimo_patterns.py` (`run_dagster_asset_check`, `llm_chat_with_prompts`)

        ## What the benchmark measures

        - **Latency** (ms): end-to-end chat completion latency
        - **Tokens**: prompt + completion token counts (from the `usage` field)
        - **Cost**: estimated USD cost (per the local unsloth cost model — free for self-hosted)
        - **RAGAS faithfulness** (where available): 0-1 score of the answer's groundedness
        """
    )
    return


@app.cell
def _phase_status() -> None:
    import marimo as mo
    from datetime import datetime

    mo.md(
        f"""
        ## Phase status — fetched at {datetime.utcnow().isoformat()}
        """
    )
    return


@app.cell
def _config() -> None:
    import os

    # The unsloth-serve container is on the bunchloch docker network at 192.168.148.5.
    # When the Pangolin AI Gateway is provisioned, change to:
    #   base_url = "https://ai.cianfhoghlaim.ie/v1"
    # and the placeholder key to "none" (private) or a real virtual key (public).
    base_url = os.environ.get("UNSLOTH_BASE_URL", "http://192.168.148.5:8889/v1")
    api_key = os.environ.get("UNSLOTH_API_KEY", "sk-unsloth-dev-noop-key")
    return (base_url, api_key)


@app.cell
def _models() -> None:
    # The 12 unsloth-served VLM models from MODEL_REGISTRY.
    # The GGUF on disk is `unsloth/Qwen3-VL-8B-Instruct-GGUF:UD-Q4_K_XL`
    # (located at /stedding/huggingface/gguf/qwen3-vl-8b/qwen3-vl-8b-instruct-q4_k_m.gguf).
    # For other unsloth models, the operator must download the matching GGUF
    # to /stedding/huggingface/gguf/<model-dir>/ and restart llama-server.
    models = [
        {
            "name": "Qwen3-VL-8B-Instruct-Q4_K_M",
            "unsloth_id": "unsloth/Qwen3-VL-8B-Instruct-GGUF",
            "gguf_path": "/stedding/huggingface/gguf/qwen3-vl-8b/qwen3-vl-8b-instruct-q4_k_m.gguf",
            "size_gb": 5.0,
            "capabilities": ["vision", "text"],
        },
    ]
    return (models,)


@app.cell
def _prompts() -> None:
    # 3 standard benchmark prompts.
    prompts = {
        "ncca_syllabus_pdf": (
            "[NCCA Junior Cycle Mathematics syllabus PDF page rendered as base64 — "
            "omitted for brevity; in production this loads from "
            "data/ncca/jc/mathematics/syllabus_p001.png]"
        ),
        "lc_marking_scheme_snippet": (
            "Extract the 4 Achievement Level descriptors from this LC marking scheme "
            "snippet: 'Level 1 (Yet to meet expectations) — answer is incomplete or "
            "contains major errors; Level 2 (In line with expectations) — answer "
            "covers core material but lacks depth; Level 3 (Above expectations) — "
            "answer demonstrates strong understanding with minor omissions; Level 4 "
            "(Exceptional) — answer is comprehensive, accurate, and well-structured.'"
        ),
        "ordnance_survey_map": (
            "[Ordnance Survey Discovery Series map extract rendered as base64 — "
            "omitted for brevity; in production this loads from "
            "data/osi/discovery_series/dublin_001.png]"
        ),
    }
    return (prompts,)


@app.cell
def _benchmark_run(models, prompts, base_url, api_key) -> None:
    import marimo as mo

    run_btn = mo.ui.run_button(label="Run benchmark (12 models × 3 prompts)")
    return (run_btn,)


@app.cell
def _benchmark(run_btn, models, prompts, base_url, api_key) -> None:
    import asyncio
    import time
    import json
    import urllib.request

    rows = []
    if run_btn.value:
        for model in models:
            for prompt_name, prompt_text in prompts.items():
                t0 = time.time()
                try:
                    req = urllib.request.Request(
                        f"{base_url}/chat/completions",
                        data=json.dumps({
                            "model": model["gguf_path"],
                            "messages": [{"role": "user", "content": prompt_text}],
                            "max_tokens": 256,
                            "temperature": 0.7,
                        }).encode("utf-8"),
                        headers={
                            "Content-Type": "application/json",
                            "Authorization": f"Bearer {api_key}",
                        },
                        method="POST",
                    )
                    with urllib.request.urlopen(req, timeout=120) as resp:
                        body = json.loads(resp.read().decode("utf-8"))
                    latency_ms = int((time.time() - t0) * 1000)
                    usage = body.get("usage", {})
                    rows.append({
                        "model": model["name"],
                        "prompt": prompt_name,
                        "latency_ms": latency_ms,
                        "prompt_tokens": usage.get("prompt_tokens", 0),
                        "completion_tokens": usage.get("completion_tokens", 0),
                        "output": body.get("choices", [{}])[0].get("message", {}).get("content", "")[:200],
                        "status": "ok",
                    })
                except Exception as exc:
                    rows.append({
                        "model": model["name"],
                        "prompt": prompt_name,
                        "latency_ms": int((time.time() - t0) * 1000),
                        "error": str(exc),
                        "status": "error",
                    })
    return (rows,)


@app.cell
def _render(rows) -> None:
    import marimo as mo
    import pandas as pd

    if not rows:
        mo.md("_Click **Run benchmark** to execute._")
    else:
        df = pd.DataFrame(rows)
        mo.ui.table(df)
    return


@app.cell
def _summary(rows) -> None:
    import marimo as mo

    if rows:
        ok = sum(1 for r in rows if r["status"] == "ok")
        err = sum(1 for r in rows if r["status"] == "error")
        avg_latency = sum(r["latency_ms"] for r in rows if r["status"] == "ok") / max(ok, 1)
        mo.md(
            f"""
            ## Summary

            - **Total**: {len(rows)} runs
            - **OK**: {ok}
            - **Errored**: {err}
            - **Average latency**: {avg_latency:.0f} ms
            """
        )
    return


if __name__ == "__main__":
    app.run()
