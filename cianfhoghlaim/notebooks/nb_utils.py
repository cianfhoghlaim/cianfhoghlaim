# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Shared helpers for the Cianfhoghlaim notebooks (British-Isles Education pipeline).

Importable from any notebook under ``cianfhoghlaim/notebooks/`` (or from
the v4-consolidated venv via ``uv run --with``). Centralises:

- The canonical MotherDuck + DuckLake connection string
  (``md:oideachais``) with graceful local-DuckDB fallback
  (``connect_biep_lakehouse()``).
- The BIEP Leaving Cert subject topic helper.
- The leabharlann↔Leaving Cert cross-archive join helper.
- The path roots used by the demo notebooks (PDF corpus, LanceDB).
- The dual-mode (marimo + CLI) helpers:
  ``cl_argument_parser()``, ``run_as_script()``,
  ``import_dev_env_tool()``.

Environment variables (all optional — sensible defaults):

- ``MOTHERDUCK_TOKEN`` — read from the Infisical `dev-baile` vault and
  hydrated into the runtime by the mise directory hook. Required only
  when connecting to the shared MotherDuck database.
- ``MOTHERDUCK_ENABLED`` — set to ``"true"`` to opt-in to the shared
  MotherDuck + DuckLake lakehouse (default ``"false"`` → local DuckDB
  fallback).
- ``CIANFHOGHLAIM_LEAVING_CERT_ROOT`` — absolute path to the
  ``leaving_certificate/`` corpus directory. Defaults to
  ``~/dev/kings_college_galway/cianfhoghlaim/leaving_certificate``.
- ``CIANFHOGHLAIM_LAKEHOUSE_DUCKDB`` — the DuckDB attach string used
  for the lakehouse. Defaults to ``"md:oideachais"``. Override for
  local dev with a ``.duckdb`` file path.

Reference: openspec/changes/2026-07-06-british-isles-education-pipeline-v1/
openspec/changes/2026-07-06-notebooks-flatten-refactor-and-wire-bi-ep/
"""
from __future__ import annotations

import argparse
import importlib.util
import os
import pathlib
import sys
from pathlib import Path
from typing import Any

import duckdb

__all__ = [
    # Lakehouse connect
    "connect_md_oideachais",
    "connect_biep_lakehouse",
    "LAKEHOUSE_DUCKDB",
    # BIEP query helpers
    "lc_subject_query",
    "leabharlann_join_to_lc",
    "ROOT",
    # CLI / dual-mode helpers
    "cl_argument_parser",
    "run_as_script",
    "import_dev_env_tool",
    # BIEP subject/level/language/year contracts
    "BIEP_SUBJECTS",
    "BIEP_LEVELS",
    "BIEP_LANGUAGES",
    "REPO_ROOT",
]


# -----------------------------------------------------------------------------
# BIEP canonical contracts (per openspec/changes/2026-07-06-british-isles-...)
# -----------------------------------------------------------------------------

BIEP_SUBJECTS: tuple[str, ...] = (
    "mathematics",
    "applied_mathematics",
    "english",
    "gaeilge",
    "biology",
    "chemistry",
)
"""The 6 BIEP v1 priority LC subjects. The full Leaving Cert catalogue
(16 subjects) is a superset of this — see
``openspec/changes/2026-07-06-british-isles-education-pipeline-v1/``."""

BIEP_LEVELS: tuple[str, ...] = ("higher", "ordinary", "foundation")
"""The 3 BIEP v1 levels. ``foundation`` is for L1/L2 only."""

BIEP_LANGUAGES: tuple[str, ...] = ("en", "ga")
"""The 2 BIEP v1 working languages. Bilingual EN + GA per Subject."""

# Canonical repo-root resolver (parent.parent = cianfhoghlaim/.parent.parent.parent = repo root
# from cianfhoghlaim/notebooks/nb_utils.py). Falls back to env var, then to
# a hard-coded default that matches the v4 consolidation assumption
# (caller lives in cianfhoghlaim/notebooks/nb_utils.py).
REPO_ROOT = Path(
    os.environ.get(
        "CIANFHOGHLAIM_ROOT",
        str(Path(__file__).resolve().parents[2]),
    )
).resolve()


# -----------------------------------------------------------------------------
# Lakehouse connect helpers (MotherDuck + DuckLake)
# -----------------------------------------------------------------------------

def connect_md_oideachais() -> duckdb.DuckDBPyConnection:
    """Connect to the MotherDuck + DuckLake lakehouse via the ``md:oideachais`` alias.

    Raises on failure — use ``connect_biep_lakehouse()`` for a graceful
    local-DuckDB fallback.
    """
    token = os.environ.get("MOTHERDUCK_TOKEN")
    if token:
        duckdb.sql(f"SET motherduck_token='{token}'")
    return duckdb.connect("md:oideachais")


def connect_biep_lakehouse(
    *,
    use_md: bool | None = None,
    local_fallback: bool = True,
) -> tuple[duckdb.DuckDBPyConnection, str]:
    """Connect to the BIEP MotherDuck + DuckLake lakehouse with graceful fallback.

    Returns ``(con, engine_label)`` where ``engine_label`` is one of:
    ``"md:oideachais"``, ``"local_duckdb"``, or ``"unavailable"``.

    Selection logic:
    1. If ``use_md=True`` (or env ``MOTHERDUCK_ENABLED=true``) AND
       ``MOTHERDUCK_TOKEN`` is set, try ``md:oideachais``.
    2. If that fails AND ``local_fallback=True``, fall back to an
       in-memory DuckDB (with a minimal empty schema) so notebooks
       still render during local development.
    3. If both fail, return ``(:memory:, "unavailable")``.

    This replaces the 12+ duplicated ``try: connect("md:oideachais")
    except: connect(":memory:")`` blocks across the BIEP dashboards.
    """
    if use_md is None:
        use_md = os.environ.get("MOTHERDUCK_ENABLED", "").lower() == "true"

    if use_md:
        token = os.environ.get("MOTHERDUCK_TOKEN", "")
        if token:
            try:
                duckdb.sql(f"SET motherduck_token='{token}'")
                con = duckdb.connect("md:oideachais")
                return con, "md:oideachais"
            except Exception:
                if not local_fallback:
                    raise

    if local_fallback:
        try:
            con = duckdb.connect(":memory:")
            # Best-effort minimal BIEP schema so SELECTs render meaningfully
            con.execute(
                "CREATE TABLE IF NOT EXISTS oideachais_leaving_cert_topics ("
                "  subject VARCHAR, level VARCHAR, language VARCHAR, "
                "  topic VARCHAR, n BIGINT"
                ")"
            )
            return con, "local_duckdb"
        except Exception:
            pass

    return duckdb.connect(":memory:"), "unavailable"


def lc_subject_query(
    subject: str,
    level: str = "higher",
    language: str = "en",
) -> duckdb.DuckDBPyRelation:
    """Read the canonical topic table for an LC subject (raises if MD unreachable)."""
    con = connect_md_oideachais()
    return con.sql(f"""
        SELECT subject, level, language, topic, count(*) AS n
        FROM oideachais.leaving_cert.{subject}_topics
        WHERE level = '{level}' AND language = '{language}'
        GROUP BY subject, level, language, topic
        ORDER BY n DESC
    """)


def leabharlann_join_to_lc(book_id: str, topic: str) -> duckdb.DuckDBPyRelation:
    """Cross-archive join: leabharlann book ↔ LC topic."""
    con = connect_md_oideachais()
    return con.sql(f"""
        SELECT b.book_id, b.title, t.topic, t.subject, t.level, t.language
        FROM oideachais.leabharlann.books b
        JOIN oideachais.leaving_cert.{topic}_topics t
          ON b.topic_embedding <-> t.topic_embedding < 0.3
        WHERE b.book_id = '{book_id}'
    """)


ROOT = Path(
    os.environ.get(
        "CIANFHOGHLAIM_LEAVING_CERT_ROOT",
        str(
            Path.home()
            / "dev"
            / "kings_college_galway"
            / "cianfhoghlaim"
            / "leaving_certificate"
        ),
    )
)

LAKEHOUSE_DUCKDB = os.environ.get(
    "CIANFHOGHLAIM_LAKEHOUSE_DUCKDB",
    "md:oideachais",
)


# -----------------------------------------------------------------------------
# CLI / dual-mode helpers (Phase 5 + Phase 6)
# -----------------------------------------------------------------------------


def cl_argument_parser(
    *,
    prog: str | None = None,
    description: str = "",
) -> argparse.ArgumentParser:
    """Argparse factory with the BIEP canonical flags pre-registered.

    Every notebook imports this and adds its own custom flags on top::

        from cianfhoghlaim.notebooks.nb_utils import cl_argument_parser
        parser = cl_argument_parser(prog="01_chemistry_analysis.py")
        parser.add_argument("--page", type=int, default=1)
        args = parser.parse_args()

    Canonical flags pre-registered:
    - ``--subject`` — one of ``BIEP_SUBJECTS`` (default: ``chemistry``)
    - ``--level`` — one of ``BIEP_LEVELS`` (default: ``higher``)
    - ``--language`` — one of ``BIEP_LANGUAGES`` (default: ``en``)
    - ``--year`` — int (default: ``2025``)
    - ``--limit`` — int (default: ``10``)
    """
    parser = argparse.ArgumentParser(prog=prog, description=description)
    parser.add_argument(
        "--subject",
        type=str,
        default="chemistry",
        choices=list(BIEP_SUBJECTS),
        help="BIEP subject (one of %(choices)s)",
    )
    parser.add_argument(
        "--level",
        type=str,
        default="higher",
        choices=list(BIEP_LEVELS),
        help="LC level (one of %(choices)s)",
    )
    parser.add_argument(
        "--language",
        type=str,
        default="en",
        choices=list(BIEP_LANGUAGES),
        help="Working language (one of %(choices)s)",
    )
    parser.add_argument(
        "--year",
        type=int,
        default=2025,
        help="LC year (2017..2026)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Result row limit",
    )
    return parser


def run_as_script(
    main_fn: Any,
    *,
    argv: list[str] | None = None,
) -> int:
    """Execute ``main_fn(argv)`` and exit with its return code.

    Use this in the ``if __name__ == "__main__"`` block of every
    refactored notebook::

        if __name__ == "__main__":
            from cianfhoghlaim.notebooks.nb_utils import run_as_script
            raise SystemExit(run_as_script(main))
    """
    sys.argv = ["marimo-notebook", *(argv if argv is not None else sys.argv[1:])]
    rc = main_fn(sys.argv[1:])
    return int(rc) if rc is not None else 0


def import_dev_env_tool(name: str = "dev_env") -> Any:
    """Import the canonical ``cianfhoghlaim.agents.adk.tools.dev_env`` module.

    Computes the absolute path from the dev_env notebook's ``__file__``
    (the notebooks live at ``<repo>/notebooks/01_dev_env/0X_*.py``,
    so the tool module is at
    ``<repo>/cianfhoghlaim/agents/adk/tools/dev_env.py`` = 2
    hops up + ``"agents/adk/tools/dev_env.py"``).

    This is a convenience helper. Per the user choice, the dev_env
    notebooks fix this inline (``Phase 1`` of the plan), so this helper
    is opt-in for new notebooks that want to skip the boilerplate.

    Usage from any notebook::

        from cianfhoghlaim.notebooks.nb_utils import import_dev_env_tool
        dev_env = import_dev_env_tool()
        results = await dev_env.ccc_search("Dagster asset", limit=5)
    """
    here = Path(__file__).resolve().parent  # cianfhoghlaim/notebooks/
    tool_path = here.parent / "agents" / "adk" / "tools" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, tool_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"dev_env tool not found at {tool_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod