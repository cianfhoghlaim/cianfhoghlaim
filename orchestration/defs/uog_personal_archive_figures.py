"""orchestration.defs.uog_personal_archive_figures — the thesis-figures
asset.

Generates 6 PDFs in `figures/thesis/` for the M.Sc. AI thesis:

  1. cs4423_module_dossier.pdf
  2. mp491_handwritten_ocr_sample.pdf
  3. numerical_analysis_2_topic_graph.pdf
  4. transcript_join_coverage.pdf
  5. cross_module_topic_heatmap.pdf
  6. personal_archive_programme_distribution.pdf

Each PDF is built with matplotlib (the canonical CI dependency, no
extra plotting stack required). The asset is deferred-import-safe —
it materialises with `MaterializeResult(metadata={"figures": [...]})`
even when matplotlib is unavailable.

Per the 2026-08-23-uog-personal-archive-tertiary-modules-v1 change
(WS12 — Tests + observability + thesis figures).
"""

from __future__ import annotations

import os
from collections.abc import Iterable
from pathlib import Path

from dagster import (
    AssetExecutionContext,
    MaterializeResult,
    MetadataValue,
    asset,
)


FIGURES_DIR = Path(
    os.environ.get(
        "UOG_THESIS_FIGURES_DIR",
        "/Users/cianmacandeisigh/dev/kings_college_galway/figures/thesis",
    )
)


# --------------------------------------------------------------------------- #
# DuckLake readers (deferred; the parallel subagent owns the source)
# --------------------------------------------------------------------------- #


def _read_personal_archive_artefacts() -> list[dict]:
    """Read every `personal_archive_artefacts` row from DuckLake."""
    try:
        import duckdb  # type: ignore[import-not-found]
    except ImportError:
        return []
    db_path = os.environ.get(
        "OOG_LOCAL_DUCKDB_PATH", "/tmp/cianfhoghlaim.duckdb"
    )
    if not Path(db_path).exists():
        return []
    try:
        con = duckdb.connect(db_path, read_only=True)
        rows = con.execute(
            "SELECT * FROM cianfhoghlaim.education.ie.personal_archive_artefacts"
        ).fetchall()
        cols = [d[0] for d in con.description]
        return [dict(zip(cols, r, strict=False)) for r in rows]
    except Exception:
        return []


def _read_personal_archive_topics() -> list[dict]:
    try:
        import duckdb  # type: ignore[import-not-found]
    except ImportError:
        return []
    db_path = os.environ.get(
        "OOG_LOCAL_DUCKDB_PATH", "/tmp/cianfhoghlaim.duckdb"
    )
    if not Path(db_path).exists():
        return []
    try:
        con = duckdb.connect(db_path, read_only=True)
        rows = con.execute(
            "SELECT * FROM cianfhoghlaim.education.ie.personal_archive_topics"
        ).fetchall()
        cols = [d[0] for d in con.description]
        return [dict(zip(cols, r, strict=False)) for r in rows]
    except Exception:
        return []


def _read_student_transcripts() -> list[dict]:
    try:
        import duckdb  # type: ignore[import-not-found]
    except ImportError:
        return []
    db_path = os.environ.get(
        "OOG_LOCAL_DUCKDB_PATH", "/tmp/cianfhoghlaim.duckdb"
    )
    if not Path(db_path).exists():
        return []
    try:
        con = duckdb.connect(db_path, read_only=True)
        rows = con.execute(
            "SELECT * FROM cianfhoghlaim.education.ie.student_transcripts"
        ).fetchall()
        cols = [d[0] for d in con.description]
        return [dict(zip(cols, r, strict=False)) for r in rows]
    except Exception:
        return []


# --------------------------------------------------------------------------- #
# 6 figure generators
# --------------------------------------------------------------------------- #


def _ensure_figures_dir() -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)


def _save(fig, name: str) -> str:
    path = FIGURES_DIR / name
    try:
        fig.savefig(str(path), format="pdf", bbox_inches="tight")
    except Exception:
        # Some matplotlib backends refuse PDF on systems without a
        # TeX install. Fall back to PNG to keep the file present.
        png_path = path.with_suffix(".png")
        fig.savefig(str(png_path), format="png", bbox_inches="tight")
        return str(png_path)
    return str(path)


def _make_cs4423_module_dossier(
    artefacts: Iterable[dict], topics: Iterable[dict]
) -> str | None:
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return None
    artefacts = [a for a in artefacts if a.get("module_code") == "CS4423"]
    topics = [t for t in topics if t.get("module_code") == "CS4423"]
    if not artefacts and not topics:
        return None
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_title("CS4423 — Numerical Analysis 2 module dossier")
    ax.set_xlabel("Artefact index")
    ax.set_ylabel("Artefact kind")
    kinds = [str(a.get("artefact_kind", "OTHER")) for a in artefacts]
    if kinds:
        ax.bar(range(len(kinds)), [1] * len(kinds), tick_label=kinds)
    if topics:
        topic_names = [
            str(t.get("topic_name", ""))[:30] for t in topics[:10]
        ]
        ax.text(
            0.05,
            0.95,
            "Topics:\n" + "\n".join(topic_names),
            transform=ax.transAxes,
            verticalalignment="top",
            fontsize=8,
        )
    return _save(fig, "cs4423_module_dossier.pdf")


def _make_mp491_handwritten_ocr_sample() -> str | None:
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return None
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_title("MP491 — handwritten OCR sample (placeholder)")
    ax.text(
        0.5,
        0.5,
        "Handwritten OCR sample will appear here once\n"
        "the MP491 transcript PDF is ingested via the\n"
        "personal-archive DLT pipeline.",
        ha="center",
        va="center",
        transform=ax.transAxes,
        fontsize=12,
    )
    ax.set_axis_off()
    return _save(fig, "mp491_handwritten_ocr_sample.pdf")


def _make_numerical_analysis_2_topic_graph(
    topics: Iterable[dict],
) -> str | None:
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return None
    topics = [t for t in topics if t.get("module_code") == "CS4423"]
    if not topics:
        return None
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_title("CS4423 — Topic graph (Numerical Analysis 2)")
    cats = [str(t.get("topic_category", "OTHER")) for t in topics]
    counts: dict[str, int] = {}
    for c in cats:
        counts[c] = counts.get(c, 0) + 1
    ax.bar(counts.keys(), counts.values(), color="seagreen")
    ax.set_xlabel("Topic category")
    ax.set_ylabel("Topic count")
    ax.tick_params(axis="x", rotation=30)
    return _save(fig, "numerical_analysis_2_topic_graph.pdf")


def _make_transcript_join_coverage(
    artefacts: Iterable[dict], transcripts: Iterable[dict]
) -> str | None:
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return None
    artefacts = list(artefacts)
    transcripts = list(transcripts)
    if not artefacts:
        return None
    n_total = len(artefacts)
    transcript_keys = {
        (str(t.get("module_code", "")), int(t.get("academic_year", 0) or 0))
        for t in transcripts
    }
    n_joined = sum(
        1
        for a in artefacts
        if (
            str(a.get("module_code", "")),
            int(a.get("academic_year", 0) or 0),
        )
        in transcript_keys
    )
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_title("Transcript join coverage")
    ax.bar(
        ["Joined", "Not joined"],
        [n_joined, n_total - n_joined],
        color=["steelblue", "lightgray"],
    )
    ax.set_ylabel("Artefact count")
    pct = 100.0 * n_joined / n_total if n_total else 0.0
    ax.text(
        0.5,
        0.95,
        f"{pct:.1f}% coverage",
        ha="center",
        va="top",
        transform=ax.transAxes,
        fontsize=14,
    )
    return _save(fig, "transcript_join_coverage.pdf")


def _make_cross_module_topic_heatmap(
    topics: Iterable[dict],
) -> str | None:
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return None
    topics = list(topics)
    if not topics:
        return None
    modules = sorted({str(t.get("module_code", "")) for t in topics if t.get("module_code")})
    categories = sorted({str(t.get("topic_category", "")) for t in topics if t.get("topic_category")})
    matrix = [[0] * len(categories) for _ in modules]
    module_index = {m: i for i, m in enumerate(modules)}
    cat_index = {c: i for i, c in enumerate(categories)}
    for t in topics:
        m = str(t.get("module_code", ""))
        c = str(t.get("topic_category", ""))
        if m in module_index and c in cat_index:
            matrix[module_index[m]][cat_index[c]] += 1
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.imshow(matrix, cmap="Greens", aspect="auto")
    ax.set_xticks(range(len(categories)))
    ax.set_xticklabels(categories, rotation=45, ha="right")
    ax.set_yticks(range(len(modules)))
    ax.set_yticklabels(modules)
    ax.set_title("Cross-module topic heatmap")
    return _save(fig, "cross_module_topic_heatmap.pdf")


def _make_personal_archive_programme_distribution(
    artefacts: Iterable[dict],
) -> str | None:
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return None
    programmes: dict[str, int] = {}
    for a in artefacts:
        p = str(a.get("programme", "OTHER") or "OTHER")
        programmes[p] = programmes.get(p, 0) + 1
    if not programmes:
        return None
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.pie(
        list(programmes.values()),
        labels=list(programmes.keys()),
        autopct="%1.1f%%",
        startangle=90,
    )
    ax.set_title("Personal archive programme distribution")
    ax.axis("equal")
    return _save(fig, "personal_archive_programme_distribution.pdf")


# --------------------------------------------------------------------------- #
# Asset
# --------------------------------------------------------------------------- #


@asset(
    key=["uog_personal_archive", "thesis_figures"],
    group_name="uog_personal_archive",
    compute_kind="python",
    description=(
        "WS12 — generates 6 thesis figures (PDFs) from the personal "
        "archive DuckLake tables. Outputs to `figures/thesis/`."
    ),
    deps=[
        __import__("dagster").AssetKey(["uog_personal_archive", "embed_lance"]),
    ],
)
def uog_personal_archive_thesis_figures(
    context: AssetExecutionContext,
) -> MaterializeResult:
    _ensure_figures_dir()
    artefacts = _read_personal_archive_artefacts()
    topics = _read_personal_archive_topics()
    transcripts = _read_student_transcripts()

    figures: list[str | None] = [
        _make_cs4423_module_dossier(artefacts, topics),
        _make_mp491_handwritten_ocr_sample(),
        _make_numerical_analysis_2_topic_graph(topics),
        _make_transcript_join_coverage(artefacts, transcripts),
        _make_cross_module_topic_heatmap(topics),
        _make_personal_archive_programme_distribution(artefacts),
    ]
    figures = [f for f in figures if f is not None]
    return MaterializeResult(
        metadata={
            "figures": MetadataValue.json(figures),
            "figures_dir": str(FIGURES_DIR),
            "n_artefacts": len(artefacts),
            "n_topics": len(topics),
            "n_transcripts": len(transcripts),
        }
    )


__all__ = [
    "FIGURES_DIR",
    "uog_personal_archive_thesis_figures",
]
