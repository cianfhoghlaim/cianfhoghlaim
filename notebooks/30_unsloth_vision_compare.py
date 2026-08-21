from notebooks._shared._pep723_template import CANONICAL_DEPENDENCIES  # canonical PEP 723 template (per the 2026-11-25-mega-3c-marimo-and-integration-v1 change)

"""Unsloth v5 10-Way Comparison Notebook — side-by-side OCR/VLM/Classical-OCR evaluation.

Per the 2026-08-21-unsloth-v5-vision-llm-hermes-openclaw-opencode-marimo-integration-v1
change. This notebook compares 10 backends on any of the 6 BIEP LC subjects' PDFs:

  6 Unsloth VLMs (served via unsloth-serve :8889):
    - Qwen3-VL-8B Instruct (v6 default VLM)
    - Qwen3-VL-32B Instruct (strong tier)
    - GLM-4.6V-Flash (fast tier)
    - DeepSeek-OCR-2 (OCR specialist)
    - Qwen3-VL-30B-A3B (MoE)
    - Qwen3-VL-235B-A22B (heavy MoE)

  4 Classical OCR backends (the BIEP v2 4-path ensemble):
    - Docling (IBM DocTags XML)
    - dots-ocr (layout specialist)
    - OlmOCR (tables+latex)
    - PaddleOCR (multilingual)

The notebook routes every (backend, PDF) pair through the canonical
OCR-Router stack at http://ocr-router:8090/v1/ocr (the same endpoint
consumed by the 6 BIEP v3 jurisdiction dashboards). The router fans
out to the 4 classical OCRs + the 6 unsloth-served VLMs.

This is a human-driven surface (no Dagster asset wiring). The outputs
are exported to stedding/eval_results/unsloth_compare_{model_role}_{pdf_hash}.json
for future BIEP v2 ingestion.

KCG patterns used:
- MODEL_REGISTRY (per .agents/skills/centralized-registry/SKILL.md)
- marimo v14 R1+R2+R3 helpers (per .agents/skills/marimo/SKILL.md)
- Dual-mode CLI (per the 2026-08-10 marimo-v14 trilogy)
"""

import marimo

# Centralized registries (per the centralized-model-registry capability).
try:
    from meaisinfhoghlaim.models import MODEL_REGISTRY, model_for  # noqa: E402
    from notebooks._shared.schema import (  # noqa: E402
        list_dlt_sources, list_cocoindex_apps, list_baml_classes,
    )
    _DEFAULT_LLM = model_for("text_llm", "default")
    _REGISTRY_SUMMARY = MODEL_REGISTRY.summary()
    _DLT_SOURCE_COUNT = len(list_dlt_sources())
    _COCO_APP_COUNT = len(list_cocoindex_apps())
    _BAML_CLASS_COUNT = len(list_baml_classes())
except ImportError:
    _DEFAULT_LLM = "minimax-m3"  # fallback (the legacy hardcoded value)
    _REGISTRY_SUMMARY = {"total": 0, "by_family": {}, "available": 0, "deprecated": 0}
    _DLT_SOURCE_COUNT = _COCO_APP_COUNT = _BAML_CLASS_COUNT = 0

__generated_with_marimo__ = "0.13.0"
app = marimo.App(width="full")


@app.cell
def _intro(mo):
    mo.md(
        f"""
        # Unsloth v5 10-Way Comparison Notebook

        Compare **10 backends** on any of the 6 BIEP LC subjects' PDFs:

        - **6 Unsloth VLMs** (served via unsloth-serve :8889 — `local/unsloth/*` LiteLLM routes)
        - **4 Classical OCRs** (Docling, dots-ocr, OlmOCR, PaddleOCR)

        All 10 backends route through the canonical OCR-Router at
        `http://ocr-router:8090/v1/ocr` (the same endpoint the 6 BIEP v3
        jurisdiction dashboards use).

        **Human-driven only** — no Dagster asset wiring. Exports to
        `stedding/eval_results/unsloth_compare_{model_role}_{pdf_hash}.json`
        for future BIEP v2 ingestion.

        Registry: **{_REGISTRY_SUMMARY.get("total", 0)}** total models / **{_REGISTRY_SUMMARY.get("available", 0)}** available.
        Default LLM: `{_DEFAULT_LLM}`.
        """
    )
    return


@app.cell
def _backend_picker(mo):
    """The 10 backend picker (6 Unsloth VLMs + 4 Classical OCRs)."""
    # The 6 Unsloth VLMs (from MODEL_REGISTRY, filtered by backend="unsloth"
    # + family="ocr_vision"). Each entry's litellm_alias is the canonical
    # route added in phase 3 (local/unsloth/<key>).
    unsloth_vlm_keys = [
        e.key for e in MODEL_REGISTRY.filter(family="ocr_vision")
        if e.backend == "unsloth" and "Qwen3-VL" in e.upstream_id or "GLM-4" in e.upstream_id or "DeepSeek-OCR" in e.upstream_id
    ]
    # Sorted for deterministic ordering
    unsloth_vlms = sorted(set(unsloth_vlm_keys))

    # The 4 classical OCR backends (the BIEP v2 4-path ensemble).
    # These are the entries in MODEL_REGISTRY that route through the
    # ocr-router :8090 dispatch matrix (not through litellm).
    classical_ocr = [
        "docling-serve",  # IBM Docling HTTP REST API
        "dots-ocr",       # layout specialist
        "olmocr",         # tables + latex
        "paddleocr",      # multilingual
    ]

    all_10_backends = unsloth_vlms + classical_ocr

    backend_picker = mo.ui.multiselect(
        options=all_10_backends,
        value=unsloth_vlms[:3] + classical_ocr[:1],  # default: 3 unsloth + 1 classical
        label="10 Backends (6 Unsloth VLMs + 4 Classical OCRs)",
    )

    capability_filter = mo.ui.multiselect(
        options=["DENSE_OCR", "GROUNDING", "TABLES", "LATEX", "REASONING", "MULTILINGUAL", "GAELIC", "DIAGRAM"],
        value=[],
        label="Filter by Model Capability (optional)",
    )

    mo.vstack([backend_picker, capability_filter])
    return backend_picker, capability_filter, all_10_backends


@app.cell
def _pdf_picker(mo):
    """The PDF picker (6 BIEP LC subjects from stedding/ingest_queue/)."""
    # The 6 BIEP LC subjects (per the british-isles-education-pipeline-v3 spec).
    # The PDF picker reads from stedding/ingest_queue/ (the canonical
    # location for the 6 subjects' PDFs). The list_pipelines helper
    # enumerates the available PDFs.
    try:
        from notebooks._shared.schema import list_pipelines
        pdf_paths = list_pipelines()
    except ImportError:
        pdf_paths = []

    # If the helper is not available, fall back to the canonical 6 BIEP
    # subjects. The PDFs live at stedding/ingest_queue/{subject}/*.pdf
    pdf_picker = mo.ui.multiselect(
        options=pdf_paths or [
            "stedding/ingest_queue/mathematics/lc_2024_paper_1.pdf",
            "stedding/ingest_queue/chemistry/lc_2024_paper_1.pdf",
            "stedding/ingest_queue/geography/lc_2024_paper_1.pdf",
            "stedding/ingest_queue/gaeilge/lc_2024_paper_1.pdf",
            "stedding/ingest_queue/english/lc_2024_paper_1.pdf",
            "stedding/ingest_queue/computer_science/lc_2024_paper_1.pdf",
        ],
        value=[],
        label="PDFs (from stedding/ingest_queue/)",
    )
    return pdf_picker


@app.cell
def _export_button(mo):
    """The export button (writes results to stedding/eval_results/)."""
    export_button = mo.ui.run_button(label="Export results to stedding/eval_results/")
    return export_button


@app.cell
def _comparison_results(mo, backend_picker, capability_filter, pdf_picker, export_button):
    """The side-by-side comparison reactive loop.

    For each (backend, PDF) pair, sends a request to the OCR-Router at
    http://ocr-router:8090/v1/ocr. The router fans out to the canonical
    backends (classical OCRs + llama-swap + unsloth-serve).

    Each column shows:
    - Model name + backend (unsloth / classical)
    - Response text (for VLMs) / DocTags XML (for Docling) / regions (for OCRs)
    - Latency (ms)
    - Tokens (VLMs) / regions (classical)
    - KL-divergence note (for VLMs) / CER/WER note (for classical)
    """
    import time
    import json
    import hashlib
    from pathlib import Path

    backends = backend_picker.value if backend_picker else []
    pdfs = pdf_picker.value if pdf_picker else []

    if not backends or not pdfs:
        mo.md("> Select at least 1 backend and 1 PDF to see results.")
        return

    # The canonical OCR-Router endpoint (the same one the 6 BIEP v3
    # jurisdiction dashboards use). The router handles the fanout to
    # the 4 classical OCRs + the 6 unsloth-served VLMs.
    ocr_router_url = "http://ocr-router:8090/v1/ocr"

    results = []
    for pdf_path in pdfs:
        for backend in backends:
            # The OCR-Router dispatch: model_name = backend key,
            # file_path = PDF path. The router handles the backend-specific
            # input/output format (e.g. DocTags XML for Docling, plain text
            # for VLMs, regions for OCRs).
            started = time.time()
            try:
                # The canonical POST envelope (per the ocr-router contract).
                # The router does the model_id → backend fanout internally.
                import urllib.request
                import urllib.error
                payload = json.dumps({
                    "model": backend,
                    "file_path": pdf_path,
                    "stream": False,
                }).encode("utf-8")
                req = urllib.request.Request(
                    ocr_router_url,
                    data=payload,
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=600) as resp:
                    response = json.loads(resp.read().decode("utf-8"))
                latency_ms = int((time.time() - started) * 1000)
                results.append({
                    "backend": backend,
                    "pdf": pdf_path,
                    "latency_ms": latency_ms,
                    "response": response,
                    "status": "ok",
                })
            except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as exc:
                latency_ms = int((time.time() - started) * 1000)
                results.append({
                    "backend": backend,
                    "pdf": pdf_path,
                    "latency_ms": latency_ms,
                    "response": str(exc),
                    "status": "error",
                })

    # Side-by-side rendering: hstack of vstack columns, one per backend.
    columns = []
    for backend in backends:
        backend_results = [r for r in results if r["backend"] == backend]
        col = mo.vstack(
            [
                mo.md(f"### `{backend}`"),
                mo.md(
                    f"**Backend:** "
                    + ("Unsloth Studio" if backend in [e.key for e in MODEL_REGISTRY.filter(family="ocr_vision") if e.backend == "unsloth"] else "Classical OCR")
                ),
                *[
                    mo.md(
                        f"**PDF:** `{Path(r['pdf']).name}`\n"
                        f"**Latency:** {r['latency_ms']} ms\n"
                        f"**Status:** {r['status']}\n\n"
                        f"```\n{str(r['response'])[:1500]}\n```"
                    )
                    for r in backend_results
                ],
            ]
        )
        columns.append(col)

    side_by_side = mo.hstack(columns, gap=2)

    # Export logic (per the human-driven contract — no Dagster asset).
    if export_button.value:
        export_dir = Path("stedding/eval_results")
        export_dir.mkdir(parents=True, exist_ok=True)
        for r in results:
            pdf_hash = hashlib.sha256(r["pdf"].encode("utf-8")).hexdigest()[:12]
            pdf_name = Path(r["pdf"]).stem
            export_path = export_dir / f"unsloth_compare_{r['backend']}_{pdf_name}_{pdf_hash}.json"
            export_path.write_text(json.dumps(r, indent=2, default=str))
        export_md = mo.md(
            f"> ✅ Exported **{len(results)}** results to `stedding/eval_results/`."
        )
    else:
        export_md = mo.md("> Click **Export** to save results to `stedding/eval_results/`.")

    mo.vstack([side_by_side, export_md])
    return


if __name__ == "__main__":
    # The canonical dual-mode CLI dispatcher (per the 2026-08-10 marimo-v14 trilogy).
    # CLI flags: --backends (comma-separated) --pdfs (comma-separated)
    #            --output (json / table)
    import argparse
    import json as _json
    import sys

    parser = argparse.ArgumentParser(
        prog="30_unsloth_vision_compare",
        description="Unsloth v5 10-Way Comparison Notebook (CLI mode)",
    )
    parser.add_argument(
        "--backends",
        type=str,
        default="qwen3-vl-8b-instruct,glm-4.6v-flash,docling-serve,dots-ocr",
        help="Comma-separated backend keys (default: 2 Unsloth VLMs + 2 Classical OCRs).",
    )
    parser.add_argument(
        "--pdfs",
        type=str,
        default="stedding/ingest_queue/gaeilge/lc_2024_paper_1.pdf",
        help="Comma-separated PDF paths.",
    )
    parser.add_argument(
        "--output",
        type=str,
        choices=["json", "table"],
        default="table",
        help="Output format (default: table).",
    )
    args = parser.parse_args()

    backends = [b.strip() for b in args.backends.split(",") if b.strip()]
    pdfs = [p.strip() for p in args.pdfs.split(",") if p.strip()]

    # The CLI mode directly calls the OCR-Router (mirror of the reactive loop).
    import time as _time
    import urllib.request as _ur
    import urllib.error as _ue
    cli_results = []
    for pdf_path in pdfs:
        for backend in backends:
            started = _time.time()
            try:
                payload = _json.dumps({
                    "model": backend,
                    "file_path": pdf_path,
                    "stream": False,
                }).encode("utf-8")
                req = _ur.Request(
                    "http://ocr-router:8090/v1/ocr",
                    data=payload,
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with _ur.urlopen(req, timeout=600) as resp:
                    response = _json.loads(resp.read().decode("utf-8"))
                latency_ms = int((_time.time() - started) * 1000)
                cli_results.append({
                    "backend": backend,
                    "pdf": pdf_path,
                    "latency_ms": latency_ms,
                    "response": response,
                    "status": "ok",
                })
            except (_ue.URLError, _ue.HTTPError, TimeoutError, _json.JSONDecodeError) as exc:
                latency_ms = int((_time.time() - started) * 1000)
                cli_results.append({
                    "backend": backend,
                    "pdf": pdf_path,
                    "latency_ms": latency_ms,
                    "response": str(exc),
                    "status": "error",
                })

    if args.output == "json":
        print(_json.dumps(cli_results, indent=2, default=str))
    else:
        # Tabular output
        print(f"{'Backend':<25} {'PDF':<40} {'Latency (ms)':<12} {'Status':<8}")
        print("-" * 90)
        for r in cli_results:
            print(f"{r['backend']:<25} {r['pdf'][:38]:<40} {r['latency_ms']:<12} {r['status']:<8}")

    sys.exit(0)
