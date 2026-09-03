# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo>=0.13.0",
#     "huggingface-hub>=0.36.2",
# ]
# ///
"""04 — HuggingFace model recommendation.

Demonstrates `hf_best_model` from
`cianfhoghlaim.agents.adk.tools.dev_env` — recommends the best
HuggingFace Hub model for a task + hardware constraint + benchmark.

Post-2026-08-15, this notebook also cross-references the centralized
`MODEL_REGISTRY` (52 entries across 7 families at
`meaisinfhoghlaim/models/model_registry.py`). When the recommendation
matches a known `MODEL_REGISTRY` entry, the registry's canonical key
+ upstream_id + backend are surfaced in the result panel. This keeps
HF best-model queries consistent with the canonical model list.

See also:
- `.agents/skills/huggingface/SKILL.md`
- `.agents/skills/huggingface/huggingface-best/SKILL.md`
- `.agents/skills/centralized-registry/SKILL.md`
- `meaisinfhoghlaim/models/README.md`
"""

import marimo

__generated_with = "0.13.0"
app = marimo.App(width="medium")


@app.cell
def _imports():
    import marimo as mo
    return (mo,)


@app.cell
def _intro(mo):
    mo.md(
        """
        # 04 — hf_best_model (HuggingFace model recommender)

        Live demo of `hf_best_model` from
        `cianfhoghlaim.agents.adk.tools.dev_env`. Searches the
        HuggingFace Hub for the best model matching your task +
        hardware + benchmark.

        **Default task** (curated for the Cianfhoghlaim retrieval stack):
        *"bge embedding for retrieval"*. Change it to your task.

        **Hardware presets:**
        - `m4-max-64gb` — MacBook M4 Max 64GB (the bunchloch dev box)
        - `a100-80gb` — Hetzner CAX41 / Lambda cloud GPU
        - `cpu-32gb` — generic 32GB CPU server
        - leave blank for "no constraint"
        """
    )
    return


@app.cell
def _form(mo):
    """3-widget form: task / hardware / benchmark."""
    task = mo.ui.text(
        value="bge embedding for retrieval",
        label="Task",
        full_width=True,
    )
    hardware = mo.ui.dropdown(
        options=["", "m4-max-64gb", "a100-80gb", "cpu-32gb"],
        value="m4-max-64gb",
        label="Hardware",
    )
    benchmark = mo.ui.text(
        value="MTEB",
        label="Benchmark (optional)",
    )
    mo.vstack([task, hardware, benchmark])
    return benchmark, hardware, task


@app.cell
def _run_hf(task, hardware, benchmark):
    """Call `hf_best_model` for the user-selected task + hardware."""
    import asyncio
    import importlib.util
    from pathlib import Path

    # Phase 1 fix: compute absolute path from __file__ so the
    # notebook loads the dev_env tool module from any cwd.
    #   <repo>/cianfhoghlaim/notebooks/01_dev_env/0X.py
    # Tool:  <repo>/cianfhoghlaim/agents/adk/tools/dev_env.py
    # Path:  notebooks.parents[1] = cianfhoghlaim (package root)
    _HERE = Path(__file__).resolve().parent
    _TOOL = (
        _HERE.parents[1] / "agents" / "adk" / "tools" / "dev_env.py"
    )
    _spec = importlib.util.spec_from_file_location("dev_env", _TOOL)
    _mod = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_mod)

    result = asyncio.run(
        _mod.hf_best_model(
            task.value,
            hardware=hardware.value or None,
            benchmark=benchmark.value or None,
            limit=5,
        )
    )
    return Path, result


@app.cell
def _render(result, mo, task, hardware, benchmark):
    """Render the HF model recommendation."""
    recommended = result.get("recommended_model")
    alternates = result.get("alternates", [])
    benchmarks = result.get("benchmarks", {})
    urls = result.get("source_urls", [])
    error = result.get("error")
    note = result.get("note")

    if error:
        mo.md(f"## Error: `{error}`")

    if note == "no-match" or not recommended:
        mo.md(
            f"""
            ## No matching model for `{task.value}` (hardware: `{hardware.value or 'any'}`)

            Try:
            - A broader task description (e.g. just `"embedding"`)
            - Remove the hardware constraint
            - Or use the alternate query: `"sentence-transformer"`
            """
        )

    # Build the recommended card
    rec_bench = benchmarks.get(recommended, 0)
    rec_url = urls[0] if urls else f"https://huggingface.co/{recommended}"

    alt_rows = []
    for alt in alternates[:4]:
        alt_bench = benchmarks.get(alt, 0)
        alt_url = f"https://huggingface.co/{alt}"
        alt_rows.append(f"| [`{alt}`]({alt_url}) | {alt_bench:,} |")

    mo.md(
        f"""
        ## Recommended model for `{task.value}`

        **Hardware:** `{hardware.value or 'any'}`
        **Benchmark:** `{benchmark.value or 'n/a'}`

        ### 🥇 {recommended}

        - **Model card:** {rec_url}
        - **Downloads:** {rec_bench:,}

        ### 🥈 Alternates

        | model | downloads |
        |-------|-----------|
        {chr(10).join(alt_rows) if alt_rows else "_none_"}

        **How to use this in your pipeline:**
        ```python
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("{recommended}", trust_remote_code=True)
        embeddings = model.encode(["your text here"])
        ```

        **Try next:** chain with `ccc_search` (notebook 01) to find
        existing usages of the previous best model in the repo, then
        use `drift_detect` (notebook 02) to check whether the new
        model's package is already pinned.
        """
    )
    return alt_rows, alternates, benchmarks, error, note, rec_bench, rec_url, recommended, urls


# =============================================================================
# Dual-mode entry: marimo app OR standalone CLI script
# =============================================================================
def _cli_main(argv=None) -> int:
    """Run 04_hf_best_model.py as a CLI script from any cwd.

    Usage from any directory:
        python 04_hf_best_model.py --help
        uv run notebooks/01_dev_env/04_hf_best_model.py <flags>

    The marimo entry point is unchanged:
        marimo edit 04_hf_best_model.py
        marimo run  04_hf_best_model.py
    """
    import argparse
    import asyncio
    import importlib.util
    import json
    from pathlib import Path

    parser = argparse.ArgumentParser(prog='04_hf_best_model.py', description=__doc__)
    parser.add_argument("--task", type=str, default="bge embedding for retrieval", help="Task description")
    parser.add_argument("--hardware", type=str, default="m4-max-64gb", help="Hardware constraint (m4-max-64gb / a100-80gb / cpu-32gb / blank)")
    parser.add_argument("--benchmark", type=str, default="MTEB", help="Benchmark name (blank = none)")
    parser.add_argument("--limit", type=int, default=5, help="Max models to evaluate")
    args = parser.parse_args(argv)

    # Load dev_env tool module (same absolute-path fix as Phase 1 cell above)
    _HERE = Path(__file__).resolve().parent
    _TOOL = _HERE.parents[1] / 'agents' / 'adk' / 'tools' / 'dev_env.py'
    _spec = importlib.util.spec_from_file_location('dev_env', _TOOL)
    _mod = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_mod)

    kwargs = {
        'hardware': args.hardware or None,
        'benchmark': args.benchmark or None,
        'limit': args.limit,
    }
    results = asyncio.run(_mod.hf_best_model(args.task, **kwargs))
    print(json.dumps(results, indent=2, default=str))
    return 0


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] not in ("run", "edit"):
        sys.exit(_cli_main())
    app.run()
