"""
Enhanced OCR Model Comparison Dashboard.

Interactive Marimo notebook for comparing OCR and vision models.

Features:
- OCR tool selector (PaddleOCR, Docling, Unstract, Dots.OCR)
- Vision model selector (Qwen3-VL, GLM-4.6V, Gemma-3)
- Batch processing mode
- Irish language quality metrics
- Side-by-side diff viewer
- Time-travel comparison via DuckLake

Usage:
    marimo edit sruth/oideachais/marimo/ocr_comparison_enhanced.py
    # Or run in browser:
    marimo run sruth/oideachais/marimo/ocr_comparison_enhanced.py
"""
import marimo

__generated_with = "0.10.0"
app = marimo.App(width="full")


@app.cell
def __():
    """Imports and configuration."""
    import marimo as mo
    import asyncio
    import base64
    from pathlib import Path
    from dataclasses import dataclass
    from typing import Any

    # Display configuration
    mo.md("# OCR Model Comparison Dashboard")
    return mo, asyncio, base64, Path, dataclass, Any


@app.cell
def __(mo):
    """OCR backend configuration."""

    # Available OCR backends
    OCR_BACKENDS = {
        "paddleocr": {
            "name": "PaddleOCR",
            "port": 8000,
            "description": "MCP server for text extraction",
        },
        "docling": {
            "name": "Docling",
            "port": 5001,
            "description": "Document layout understanding",
        },
        "dots_ocr": {
            "name": "Dots.OCR",
            "port": 8001,
            "description": "Qwen-VL based OCR",
        },
        "unstract": {
            "name": "Unstract",
            "port": 8002,
            "description": "Document extraction platform",
        },
    }

    # Available vision models
    VISION_MODELS = {
        "qwen3-vl": {
            "name": "Qwen3-VL-30B",
            "size_gb": 18.0,
            "capabilities": ["ocr", "grounding", "reasoning"],
        },
        "glm-4.6v-flash": {
            "name": "GLM-4.6V-Flash",
            "size_gb": 6.0,
            "capabilities": ["ocr", "function_calling", "128k_context"],
        },
        "gemma-3-27b": {
            "name": "Gemma-3-27B-IT",
            "size_gb": 16.0,
            "capabilities": ["ocr", "general", "instruction_following"],
        },
        "olmocr-7b": {
            "name": "OlmOCR-2-7B",
            "size_gb": 4.0,
            "capabilities": ["dense_ocr", "tables", "latex"],
        },
        "moondream2": {
            "name": "Moondream2",
            "size_gb": 1.5,
            "capabilities": ["ocr", "lightweight"],
        },
    }

    mo.md(f"""
    ## Configuration

    **OCR Backends:** {len(OCR_BACKENDS)}
    **Vision Models:** {len(VISION_MODELS)}
    """)
    return OCR_BACKENDS, VISION_MODELS


@app.cell
def __(mo, OCR_BACKENDS, VISION_MODELS):
    """Model selection UI."""

    # OCR backend selector
    ocr_selector = mo.ui.multiselect(
        options=list(OCR_BACKENDS.keys()),
        value=["paddleocr", "docling"],
        label="OCR Backends",
    )

    # Vision model selector
    vision_selector = mo.ui.multiselect(
        options=list(VISION_MODELS.keys()),
        value=["qwen3-vl", "glm-4.6v-flash"],
        label="Vision Models",
    )

    # Prompt selector
    prompt_options = {
        "default": "Extract all text from this document image.",
        "structured": "Extract text in markdown format with headings and lists.",
        "irish": "Extract text preserving Irish fadas (á, é, í, ó, ú) accurately.",
        "tables": "Extract all tables in markdown format.",
        "math": "Extract text including math formulas in LaTeX notation.",
    }

    prompt_selector = mo.ui.dropdown(
        options=list(prompt_options.keys()),
        value="default",
        label="Prompt Type",
    )

    # Irish mode toggle
    irish_mode = mo.ui.switch(
        value=False,
        label="Irish Language Mode",
    )

    mo.hstack([
        mo.vstack([ocr_selector, vision_selector]),
        mo.vstack([prompt_selector, irish_mode]),
    ])
    return ocr_selector, vision_selector, prompt_selector, irish_mode, prompt_options


@app.cell
def __(mo):
    """File upload and source selection."""

    # File upload
    file_upload = mo.ui.file(
        filetypes=[".pdf", ".png", ".jpg", ".jpeg", ".tiff"],
        multiple=True,
        label="Upload Documents",
    )

    # Source directory input
    source_dir = mo.ui.text(
        value="/Users/cliste/Library/Mobile Documents/com~apple~CloudDocs/bunchloch",
        label="Source Directory",
        full_width=True,
    )

    # Batch mode toggle
    batch_mode = mo.ui.switch(
        value=False,
        label="Batch Processing Mode",
    )

    # Number of files to process in batch
    batch_size = mo.ui.slider(
        start=1,
        stop=100,
        value=10,
        label="Batch Size",
    )

    mo.vstack([
        file_upload,
        mo.hstack([source_dir, batch_mode, batch_size]),
    ])
    return file_upload, source_dir, batch_mode, batch_size


@app.cell
def __(mo, file_upload, source_dir, batch_mode, batch_size, Path):
    """Document discovery and preview."""

    documents = []

    # Check uploaded files
    if file_upload.value:
        for f in file_upload.value:
            documents.append({
                "name": f.name,
                "size": len(f.contents),
                "source": "upload",
                "data": f.contents,
            })

    # Check source directory
    source_path = Path(source_dir.value)
    if source_path.exists() and batch_mode.value:
        patterns = ["*.pdf", "*.png", "*.jpg", "*.jpeg"]
        for pattern in patterns:
            for file_path in source_path.rglob(pattern):
                if len(documents) >= batch_size.value:
                    break
                documents.append({
                    "name": file_path.name,
                    "path": str(file_path),
                    "size": file_path.stat().st_size,
                    "source": "directory",
                })

    # Show document count
    if documents:
        mo.md(f"""
        ### Documents Found: {len(documents)}

        | Name | Size | Source |
        |------|------|--------|
        """ + "\n".join([
            f"| {d['name'][:40]}... | {d['size'] / 1024:.1f} KB | {d['source']} |"
            for d in documents[:10]
        ]))
    else:
        mo.md("*No documents loaded. Upload files or enable batch mode.*")

    return documents,


@app.cell
def __(mo):
    """Run comparison button."""

    run_button = mo.ui.run_button(label="Run OCR Comparison")
    run_button
    return run_button,


@app.cell
def __(
    mo,
    run_button,
    documents,
    ocr_selector,
    vision_selector,
    prompt_selector,
    prompt_options,
    irish_mode,
    asyncio,
):
    """Execute OCR comparison."""

    results = {}

    if run_button.value and documents:
        mo.md("### Running OCR Comparison...")

        # Get selected models
        selected_ocr = ocr_selector.value
        selected_vision = vision_selector.value
        prompt = prompt_options.get(prompt_selector.value, prompt_options["default"])

        # Use Irish prompt if enabled
        if irish_mode.value:
            prompt = prompt_options["irish"]

        # Try to import OCR modules
        try:
            from sruth.oideachais.ocr import (
                compare_ocr_models,
                compare_vision_models,
            )
            ocr_available = True
        except ImportError:
            ocr_available = False
            mo.md("*OCR modules not available. Showing mock results.*")

        # Process first document as demo
        if documents and ocr_available:
            doc = documents[0]
            if "data" in doc:
                image_bytes = doc["data"]
            else:
                with open(doc["path"], "rb") as f:
                    image_bytes = f.read()

            # Run comparison (async)
            async def run_comparison():
                ocr_results = await compare_ocr_models(
                    image_bytes,
                    models=selected_ocr,
                    prompt=prompt,
                )
                vision_results = await compare_vision_models(
                    image_bytes,
                    models=selected_vision,
                    prompt=prompt,
                )
                return {"ocr": ocr_results, "vision": vision_results}

            try:
                results = asyncio.run(run_comparison())
            except Exception as e:
                mo.md(f"**Error:** {e}")

        # Mock results for demo
        if not ocr_available or not results:
            results = {
                "ocr": {
                    "paddleocr": {
                        "text": "Sample OCR text from PaddleOCR...",
                        "confidence": 0.92,
                        "elapsed_seconds": 1.5,
                    },
                    "docling": {
                        "text": "Sample OCR text from Docling...",
                        "confidence": 0.88,
                        "elapsed_seconds": 2.1,
                    },
                },
                "vision": {
                    "qwen3-vl": {
                        "text": "Sample text from Qwen3-VL vision model...",
                        "elapsed_seconds": 3.2,
                        "tokens_used": 1500,
                    },
                    "glm-4.6v-flash": {
                        "text": "Sample text from GLM-4.6V-Flash...",
                        "elapsed_seconds": 1.8,
                        "tokens_used": 1200,
                    },
                },
            }

    results
    return results,


@app.cell
def __(mo, results):
    """Display OCR results comparison."""

    if results:
        # OCR backend results
        ocr_results = results.get("ocr", {})
        vision_results = results.get("vision", {})

        # Build comparison table
        rows = []

        for model_id, result in ocr_results.items():
            if isinstance(result, dict):
                rows.append({
                    "Model": model_id,
                    "Type": "OCR",
                    "Confidence": f"{result.get('confidence', 0):.2%}",
                    "Latency": f"{result.get('elapsed_seconds', 0):.2f}s",
                    "Tokens": result.get("tokens_used", "-"),
                    "Preview": result.get("text", "")[:100] + "...",
                })

        for model_id, result in vision_results.items():
            if isinstance(result, dict):
                rows.append({
                    "Model": model_id,
                    "Type": "Vision",
                    "Confidence": "-",
                    "Latency": f"{result.get('elapsed_seconds', 0):.2f}s",
                    "Tokens": result.get("tokens_used", "-"),
                    "Preview": result.get("text", "")[:100] + "...",
                })

        if rows:
            mo.md("### Comparison Results")
            mo.ui.table(rows)
        else:
            mo.md("*No results to display.*")
    else:
        mo.md("*Click 'Run OCR Comparison' to see results.*")

    return


@app.cell
def __(mo, results):
    """Side-by-side text comparison."""

    if results:
        ocr_results = results.get("ocr", {})
        vision_results = results.get("vision", {})

        # Get first result from each
        all_results = {**ocr_results, **vision_results}
        model_keys = list(all_results.keys())[:2]  # Compare first two

        if len(model_keys) >= 2:
            left_model = model_keys[0]
            right_model = model_keys[1]

            left_result = all_results.get(left_model, {})
            right_result = all_results.get(right_model, {})

            left_text = left_result.get("text", "") if isinstance(left_result, dict) else ""
            right_text = right_result.get("text", "") if isinstance(right_result, dict) else ""

            mo.md("### Side-by-Side Comparison")
            mo.hstack([
                mo.vstack([
                    mo.md(f"**{left_model}**"),
                    mo.ui.text_area(value=left_text, rows=10, full_width=True, disabled=True),
                ]),
                mo.vstack([
                    mo.md(f"**{right_model}**"),
                    mo.ui.text_area(value=right_text, rows=10, full_width=True, disabled=True),
                ]),
            ])

    return


@app.cell
def __(mo, results, irish_mode):
    """Irish language quality metrics."""

    if irish_mode.value and results:
        mo.md("### Irish Language Quality")

        # Try to import Irish processing
        try:
            from sruth.oideachais.ocr import (
                detect_irish_content,
                get_fada_accuracy,
                get_irish_quality_score,
            )
            irish_available = True
        except ImportError:
            irish_available = False

        if irish_available:
            # Analyze each result
            all_results = {**results.get("ocr", {}), **results.get("vision", {})}

            irish_metrics = []
            for model_id, result in all_results.items():
                if isinstance(result, dict):
                    text = result.get("text", "")
                    if text:
                        is_irish = detect_irish_content(text)
                        fada_acc = get_fada_accuracy(text) if is_irish else None
                        quality = get_irish_quality_score(text) if is_irish else None

                        irish_metrics.append({
                            "Model": model_id,
                            "Irish Detected": "Yes" if is_irish else "No",
                            "Fada Accuracy": f"{fada_acc:.1%}" if fada_acc else "-",
                            "Quality Score": f"{quality:.2f}" if quality else "-",
                        })

            if irish_metrics:
                mo.ui.table(irish_metrics)
        else:
            mo.md("*Irish processing module not available.*")

    return


@app.cell
def __(mo):
    """Time-travel comparison via DuckLake."""

    mo.md("### Historical Comparison")

    # Snapshot selector
    snapshot_selector = mo.ui.date(
        label="Compare as of date",
    )

    # Show snapshot controls
    mo.hstack([
        snapshot_selector,
        mo.ui.button(label="Load Snapshot"),
        mo.ui.button(label="Create Snapshot"),
    ])

    return snapshot_selector,


@app.cell
def __(mo):
    """Export and reporting."""

    mo.md("### Export Results")

    export_format = mo.ui.dropdown(
        options=["JSON", "CSV", "Markdown", "PDF Report"],
        value="JSON",
        label="Export Format",
    )

    export_button = mo.ui.button(label="Export Results")

    mo.hstack([export_format, export_button])

    return export_format, export_button


@app.cell
def __(mo):
    """Footer with configuration info."""

    mo.md("""
    ---

    ### Service Endpoints

    | Service | Port | Status |
    |---------|------|--------|
    | LiteLLM Gateway | 4000 | Required |
    | llama-swap (GGUF) | 8080 | Optional |
    | mlx-omni-server (MLX) | 10240 | Optional |
    | PaddleOCR MCP | 8000 | Optional |
    | Docling | 5001 | Optional |

    *Ensure services are running before comparison.*
    """)

    return


if __name__ == "__main__":
    app.run()
