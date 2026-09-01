"""cocoindex_flows.uk_ncce.learning_graphs_app — the NCCE grid-aware converter.

Phase 4 of the 2026-09-01-cianfhoghlaim-nua-biep-ncce-showcase-v1 change
(Phase 4 of the cianfhoghlaim-nua v6 era plan). The OSS-first version
of the gemini_hackathon lift.

Walks the 5 NCCE artefacts at ``data/bi_ep/syllabi_raw/uk_ncce/curriculum/``
and writes grid-aware Markdown output to
``data/bi_ep/syllabi_md/uk_ncce/`` — preserving the row × column
structure of the learning-graph PDFs as Markdown tables.

Run::

    python -m cocoindex_flows.uk_ncce.learning_graphs_app

Or programmatically via ``run()``.
"""

from __future__ import annotations

import logging
import pathlib

logger = logging.getLogger(__name__)


#: Default input directory (matches the canonical NCCE PDF layout).
RAW_ROOT: pathlib.Path = pathlib.Path(
    __import__("os").environ.get(
        "BI_EP_NCCE_RAW_ROOT",
        pathlib.Path.cwd() / "data" / "bi_ep" / "syllabi_raw" / "uk_ncce" / "curriculum",
    )
)

#: Default output directory.
MD_ROOT: pathlib.Path = pathlib.Path(
    __import__("os").environ.get(
        "BI_EP_NCCE_MD_ROOT",
        pathlib.Path.cwd() / "data" / "bi_ep" / "syllabi_md" / "uk_ncce",
    )
)

#: The 5 NCCE artefacts we walk.
PDF_ARTEFACTS: tuple[str, ...] = (
    "learning_graph_intro_to_python_programming_y8.pdf",
    "learning_graph_introduction_to_scratch_y7.pdf",
    "learning_graph_introduction_to_variables_y6.pdf",
    "pedagogy_principles.pdf",
    "computing_journey_y7_to_y11.pdf",
)


def _output_path_for(
    artefact_path: pathlib.Path,
    *,
    raw_root: pathlib.Path,
    md_root: pathlib.Path,
) -> pathlib.Path:
    """Return the canonical Markdown output path for an NCCE artefact path."""
    relative = artefact_path.relative_to(raw_root)
    return md_root / relative.with_suffix(".md")


def _process_one_artefact(
    artefact_path: pathlib.Path,
    *,
    raw_root: pathlib.Path,
    md_root: pathlib.Path,
) -> pathlib.Path | None:
    """Read one NCCE artefact, convert to grid-aware Markdown, write the output."""
    try:
        from cocoindex_flows._shared._docling_grid_segmenter import (
            extract_markdown_with_grid,
        )
    except ImportError as e:
        logger.warning("uk_ncce.learning_graphs_app: %s; skipping %s", e, artefact_path)
        return None

    try:
        markdown = extract_markdown_with_grid(artefact_path)
    except Exception as e:
        logger.warning(
            "uk_ncce.learning_graphs_app: failed to extract %s: %s",
            artefact_path,
            e,
        )
        return None

    output_path = _output_path_for(artefact_path, raw_root=raw_root, md_root=md_root)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown)
    logger.info("uk_ncce.learning_graphs_app: wrote %s", output_path)
    return output_path


def run(
    raw_root: pathlib.Path | None = None,
    md_root: pathlib.Path | None = None,
) -> list[pathlib.Path]:
    """Process all 5 NCCE artefacts. Returns the list of written files."""
    raw_root = raw_root or RAW_ROOT
    md_root = md_root or MD_ROOT
    written: list[pathlib.Path] = []
    for suffix in PDF_ARTEFACTS:
        artefact = raw_root / suffix
        if not artefact.exists():
            logger.warning("uk_ncce.learning_graphs_app: missing %s", artefact)
            continue
        out = _process_one_artefact(artefact, raw_root=raw_root, md_root=md_root)
        if out is not None:
            written.append(out)
    return written


if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)
    files = run()
    print(f"Wrote {len(files)} files", file=sys.stderr)