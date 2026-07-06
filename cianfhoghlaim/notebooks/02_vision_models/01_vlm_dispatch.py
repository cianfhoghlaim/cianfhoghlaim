# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.13.0",
#     "duckdb>=1.0",
#     "pandas>=2.0",
# ]
# ///
"""01 — VLM/OCR dispatch explorer.

Walks the 6 subjects × {en, ga} ``leaving_certificate/`` corpus
(12 dirs) and shows which of the 5 OCR/VLM backends would be
chosen per PDF (and why).

The 5 OCR backends (from
``cianfhoghlaim.meaisinfhoghlaim.models.registry``):
  - ``gemma-4-E2B``       — small text-first PDFs (<5 MB)
  - ``qwen3-vl-8b``        — SEC exam papers (image-heavy)
  - ``glm-4.6v-flash``    — pre-1922 scanned Gaelic texts
  - ``molmo2-8b``         — marking-scheme image-heavy
  - ``dots.ocr``          — dense mathematical content fallback

Dual-mode usage:

    # Interactive
    marimo edit 01_vlm_dispatch.py

    # CLI — single PDF inspection
    uv run 02_vision_models/01_vlm_dispatch.py \\
        --pdf-path leaving_certificate/chemistry/en/SC-Chemistry-Spec-EN.pdf
"""
from __future__ import annotations

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
        # 01 — VLM/OCR Dispatch Explorer

        Live walk of the 6 BIEP subjects × {en, ga} = 12 corpus
        directories. For every PDF, shows the dispatched OCR backend
        and the reason for the routing decision.

        Routing rules live in
        ``cianfhoghlaim.meaisinfhoghlaim.models.registry:select_ocr_backend()``.
        """
    )
    return  # (no-op; marimo-safe)


@app.cell
def _controls(mo):
    from cianfhoghlaim.notebooks.nb_utils import BIEP_SUBJECTS
    subjects = mo.ui.multiselect(
        options=list(BIEP_SUBJECTS),
        value=["chemistry", "biology"],
        label="Subjects to scan (default: chemistry + biology)",
    )
    subjects
    return BIEP_SUBJECTS, subjects


@app.cell
def _walk_corpus(subjects, mo):
    """Walk the 12 corpus dirs and build the routing table."""
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

    rows: list[dict] = []
    root = Path(__file__).resolve().parents[2] / "leaving_certificate"

    for subj in subjects.value:
        for lang in ("en", "ga"):
            corpus_dir = root / subj / lang
            if not corpus_dir.exists():
                rows.append({
                    "subject": subj, "language": lang,
                    "file": "(corpus dir missing)", "size_kb": 0,
                    "model": "—", "reason": "fallback (no corpus)",
                })
                continue
            for pdf in sorted(corpus_dir.glob("*.pdf")):
                size_kb = round(pdf.stat().st_size / 1024, 1)
                try:
                    from cianfhoghlaim.meaisinfhoghlaim.models.registry import select_ocr_backend
                    sel = select_ocr_backend(pdf, page_count=None)
                    rows.append({
                        "subject": subj, "language": lang,
                        "file": pdf.name, "size_kb": size_kb,
                        "model": sel.model.key, "reason": sel.reason,
                    })
                except Exception as exc:
                    rows.append({
                        "subject": subj, "language": lang,
                        "file": pdf.name, "size_kb": size_kb,
                        "model": "ERROR", "reason": str(exc)[:120],
                    })
    return (rows,)


@app.cell
def _render(rows, mo, subjects):
    if not rows:
        _render_md = mo.md("_No rows._")
    else:
        _pdf_count = sum(1 for r in rows if r.get("file", "").endswith(".pdf"))
        _rows_md = "\n".join(
            f"| `{r.get('subject', '?')}` | `{r.get('language', '?')}` | `{r.get('file', '?')}` | "
            f"{r.get('size_kb', '?')} | `{r.get('model', '?')}` | {r.get('reason', '?')} |"
            for r in rows
        )
        _render_md = mo.md(
            f"""
            ## Routing table — {len(rows)} entries across {len(subjects.value)} subjects

            | subject | lang | file | KB | model | reason |
            |---------|------|------|----:|-------|--------|
            {_rows_md}

            **{_pdf_count} PDFs** total scanned. The fallback ``—`` entries
            indicate corpus dirs that don't yet exist on disk — run
            ``dagster asset materialize --select lc6_ncca`` to populate them.
            """
        )
    _render_md
    return (pdf_count, rows_md)


# =============================================================================
# Dual-mode CLI
# =============================================================================
def _cli_main(argv=None) -> int:
    """Inspect a single PDF's OCR dispatch from any cwd.

    Usage:
        uv run 02_vision_models/01_vlm_dispatch.py \\
            --pdf-path leaving_certificate/chemistry/en/SC-Chemistry-Spec-EN.pdf
    """
    import argparse
    import json
    import sys
    from pathlib import Path

    parser = argparse.ArgumentParser(
        prog="01_vlm_dispatch.py",
        description="VLM dispatch inspector (single-PDF mode).",
    )
    parser.add_argument(
        "--pdf-path",
        type=str,
        required=False,
        default=None,
        help="Absolute or relative path to a PDF",
    )
    parser.add_argument("--page-count", type=int, default=None)
    args = parser.parse_args(argv)

    if args.pdf_path is None:
        parser.print_help()
        return 0

    pdf_path = Path(args.pdf_path).resolve()
    if not pdf_path.exists():
        print(json.dumps({"error": "not_found", "path": str(pdf_path)}, indent=2))
        return 2

    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    try:
        from cianfhoghlaim.meaisinfhoghlaim.models.registry import select_ocr_backend
        sel = select_ocr_backend(pdf_path, page_count=args.page_count)
        result = {
            "pdf": str(pdf_path),
            "size_kb": round(pdf_path.stat().st_size / 1024, 1),
            "model": sel.model.key,
            "reason": sel.reason,
        }
        print(json.dumps(result, indent=2))
        return 0
    except Exception as exc:
        print(json.dumps({"error": str(exc), "pdf": str(pdf_path)}, indent=2))
        return 1


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] not in ("run", "edit"):
        sys.exit(_cli_main())
    app.run()