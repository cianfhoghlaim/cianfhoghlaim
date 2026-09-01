"""cocoindex_flows._shared._docling_grid_segmenter — row × column grid detection.

Phase 1 helper for the 2026-08-31-uk-ncce-learning-graph-showcase-v1
change. The NCCE learning-graph PDFs are visual grids — a row of skill
descriptions down the left side, a row of lesson columns across the
top, and cells at each (row, column) intersection describing the skill
outcome for that lesson.

When Docling converts such a PDF to Markdown it typically flattens the
structure — every cell ends up as a paragraph and the row/column
relationship is lost. This module wraps Docling (when available) and
post-processes the output to detect + preserve the grid structure.

Behaviour contract:

  * The pure-Python ``detect_grid()`` function analyses a list of
    paragraphs (from any Markdown extractor) and emits a Markdown
    string that renders the grid as a Markdown table when at least 2
    rows × 2 columns are detected.
  * The lazy ``extract_markdown_with_grid()`` function loads Docling
    on first call (so the heavy ML deps don't crash the import graph
    when the helper isn't used), converts the PDF, then runs the grid
    detector over the result.
  * When Docling isn't installed, ``extract_markdown_with_grid()``
    falls back to the existing pypdfium2 extractor in
    ``cocoindex_flows/pdf/_shared.py`` — preserving the canonical
    Phase 2b pipeline behaviour.

CocoIndex itself is **not** imported here — this is a pure helper that
the ``uk_ncce/learning_graphs_app.py`` App calls from inside an
``@coco.fn`` block. That keeps the CocoIndex optional-degradation
pattern (the App falls back to a plain ``run()`` when CocoIndex isn't
installed) intact.

This module deliberately does NOT touch
``cocoindex_flows/pdf/_shared.py`` — that file owns the canonical
Phase 2b pypdfium2 fallback, and the Phase 1 NCCE grid preservation is
a thin layer on top.
"""

from __future__ import annotations

import logging
import re
from collections.abc import Iterable
from dataclasses import dataclass
from typing import TYPE_CHECKING

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    pass  # CocoIndex is optional + not used here.


# ---------------------------------------------------------------------------
# Grid detection dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class GridCell:
    """One cell in a detected row × column grid."""

    row_label: str
    column_label: str
    text: str


@dataclass(frozen=True)
class DetectedGrid:
    """A row × column grid extracted from a PDF page.

    Attributes:
        row_labels: The N row labels, top-to-bottom (e.g. ["Variables",
            "Selection", "Iteration"]).
        column_labels: The M column labels, left-to-right (e.g. ["Lesson
            1", "Lesson 2", ..., "Lesson 7"]).
        cells: One GridCell per (row, column) intersection. Always
            ``len(cells) == len(row_labels) * len(column_labels)`` (an
            empty cell is represented as ``text=""``).
        confidence: Detection confidence in [0.0, 1.0].
    """

    row_labels: tuple[str, ...]
    column_labels: tuple[str, ...]
    cells: tuple[GridCell, ...]
    confidence: float

    def is_valid(self) -> bool:
        """A grid is valid when it has at least 2 rows and 2 columns."""
        return len(self.row_labels) >= 2 and len(self.column_labels) >= 2

    def to_markdown(self) -> str:
        """Render the grid as a Markdown table.

        Returns a Markdown string with a header row of column labels +
        one body row per row label. Empty cells become an empty string.
        """
        if not self.is_valid():
            return ""
        header = "| (row) | " + " | ".join(self.column_labels) + " |"
        sep = "| --- | " + " | ".join(["---"] * len(self.column_labels)) + " |"
        body_rows: list[str] = []
        # Build an index from (row_label, column_label) → cell text.
        idx: dict[tuple[str, str], str] = {
            (c.row_label, c.column_label): c.text for c in self.cells
        }
        for row_label in self.row_labels:
            cells = [idx.get((row_label, col), "") for col in self.column_labels]
            body_rows.append("| " + row_label + " | " + " | ".join(cells) + " |")
        return "\n".join([header, sep, *body_rows])


# ---------------------------------------------------------------------------
# Grid detection heuristics
# ---------------------------------------------------------------------------

#: Headers commonly used as NCCE column labels — "Lesson 1", "Lesson 12",
#: "Y8 - Term 1", etc.  This is a deliberately permissive regex so the
#: heuristic catches both "Lesson 1" and "L1" forms.
_LESSON_HEADER_RE = re.compile(
    r"^(lesson|les|column|col|y[0-9]+|term|unit|step|wk|week)"
    r"[\s\-\.]*(\d+|[ivx]+)$",
    flags=re.IGNORECASE,
)

#: Headers commonly used as NCCE row labels — short, often a single word.
_ROW_HEADER_HINTS = (
    "variable",
    "selection",
    "iteration",
    "function",
    "loop",
    "condition",
    "operator",
    "sequence",
    "decomposition",
    "abstraction",
    "evaluation",
    "algorithm",
    "pattern",
    "data",
    "input",
    "output",
)


def detect_grid(paragraphs: Iterable[str]) -> DetectedGrid | None:
    """Heuristically detect a row × column grid from a list of paragraphs.

    The heuristic is deliberately simple — it's a smoke test for "does
    this PDF have a tabular layout worth surfacing as a Markdown table".
    A real grid detection model would use Docling's TableFormer output
    (see ``extract_markdown_with_grid`` below for the wrapper that
    delegates to it).

    Strategy:
        1. Find the first paragraph that looks like a column-header line
           (``Lesson 1 | Lesson 2 | ...``).
        2. Treat the next N paragraphs as row labels (short, common skill
           words → "variable", "selection", etc.).
        3. Treat the remaining paragraphs as cell text, sequenced by
           (row, column) position.

    Returns ``None`` when the heuristic can't find a grid shape. Callers
    should fall back to the flat paragraph rendering when this returns
    ``None``.
    """
    para_list = [p.strip() for p in paragraphs if p and p.strip()]
    if len(para_list) < 4:
        return None

    column_labels: list[str] = []
    column_idx = -1
    for i, p in enumerate(para_list[:3]):
        # Pipe-separated headers (e.g. "| Lesson 1 | Lesson 2 |")
        if "|" in p and _is_header_line(p):
            parts = [cell.strip() for cell in p.split("|") if cell.strip()]
            if len(parts) >= 2 and all(_LESSON_HEADER_RE.match(part) for part in parts):
                column_labels = parts
                column_idx = i
                break

    if not column_labels or column_idx < 0:
        return None

    # Find row labels: paragraphs immediately after the header that are
    # short + look like skill names.
    row_labels: list[str] = []
    row_idx_start = column_idx + 1
    for p in para_list[row_idx_start : row_idx_start + 12]:
        words = p.split()
        if 1 <= len(words) <= 3 and any(hint in p.lower() for hint in _ROW_HEADER_HINTS):
            row_labels.append(p)
        else:
            break
    if len(row_labels) < 2:
        return None

    # Cell text starts after the row labels; one paragraph per (row, col).
    cell_start = row_idx_start + len(row_labels)
    cell_paras = para_list[cell_start:]
    cells: list[GridCell] = []
    n_cols = len(column_labels)
    for ri, row_label in enumerate(row_labels):
        for ci, col_label in enumerate(column_labels):
            idx = ri * n_cols + ci
            if idx < len(cell_paras):
                cells.append(
                    GridCell(row_label=row_label, column_label=col_label, text=cell_paras[idx])
                )
            else:
                cells.append(GridCell(row_label=row_label, column_label=col_label, text=""))

    return DetectedGrid(
        row_labels=tuple(row_labels),
        column_labels=tuple(column_labels),
        cells=tuple(cells),
        confidence=0.65,
    )


def _is_header_line(p: str) -> bool:
    """True when the paragraph has the shape of a Markdown table header."""
    parts = [c.strip() for c in p.split("|") if c.strip()]
    return len(parts) >= 2


# ---------------------------------------------------------------------------
# Docling-backed grid extractor (lazy import)
# ---------------------------------------------------------------------------


def extract_markdown_with_grid(
    content: bytes,
    *,
    fallback_to_pypdfium2: bool = True,
) -> str:
    """Convert a PDF to Markdown, preserving the row × column grid when found.

    Behaviour:
        1. Try to load Docling lazily. If available, convert the PDF +
           extract TableFormer output.
        2. Run ``detect_grid()`` over the extracted paragraphs.
        3. If a grid is detected, return the Markdown table form.
        4. Otherwise (or when Docling is missing), fall back to the
           canonical Phase 2b pypdfium2 extractor in
           ``cocoindex_flows.pdf._shared``.

    Args:
        content: Raw PDF bytes.
        fallback_to_pypdfium2: When True (the default), the pypdfium2
            extractor is used when Docling is missing or the grid
            detector returns ``None``. Set False to raise instead.

    Returns:
        A Markdown string. When the grid detector fires, the result is a
        Markdown table. Otherwise it's the flat paragraph rendering
        from the fallback extractor.
    """
    paragraphs, docling_available = _docling_extract_paragraphs(content)

    if docling_available and paragraphs:
        grid = detect_grid(paragraphs)
        if grid is not None and grid.is_valid():
            return grid.to_markdown()

    if not fallback_to_pypdfium2:
        return "\n\n".join(paragraphs)

    # Fallback: import the canonical Phase 2b pypdfium2 extractor.
    try:
        from cocoindex_flows.pdf._shared import extract_markdown

        return extract_markdown(content)
    except ImportError as exc:
        logger.warning(
            "_docling_grid_segmenter: docling unavailable + pypdfium2 fallback "
            "failed (%s); returning flat paragraph rendering",
            exc,
        )
        return "\n\n".join(paragraphs)


def _docling_extract_paragraphs(content: bytes) -> tuple[list[str], bool]:
    """Convert a PDF to a list of paragraphs via Docling.

    Returns:
        ``(paragraphs, docling_available)``. When Docling isn't installed,
        ``docling_available`` is False and ``paragraphs`` is empty.
    """
    try:
        from docling.datamodel.base_models import DocumentStream  # type: ignore[import-not-found]
        from docling.document_converter import DocumentConverter  # type: ignore[import-not-found]
    except ImportError:
        logger.debug("_docling_grid_segmenter: docling not installed; returning empty paragraphs")
        return [], False

    try:
        import io

        converter = DocumentConverter()
        doc = converter.convert(DocumentStream(name="in.pdf", stream=io.BytesIO(content)))
    except Exception as exc:
        logger.warning("_docling_grid_segmenter: Docling convert failed: %s", exc)
        return [], True

    markdown = doc.document.export_to_markdown()
    paragraphs = [p.strip() for p in re.split(r"\n{2,}", markdown) if p and p.strip()]
    return paragraphs, True


__all__ = [
    "DetectedGrid",
    "GridCell",
    "detect_grid",
    "extract_markdown_with_grid",
]
