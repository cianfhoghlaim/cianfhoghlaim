from notebooks._shared._pep723_template import CANONICAL_DEPENDENCIES  # canonical PEP 723 template (per the 2026-11-25-mega-3c-marimo-and-integration-v1 change)
"""Shared helpers for the Cianfhoghlaim notebooks (British-Isles Education pipeline).

**DEPRECATED — kept for back-compat only.** New code should use:

- ``notebooks._shared.marimo_patterns`` (R1 + P1-P6 helpers —
  ``setup_biep_registry_header``, ``llm_chat_with_prompts``,
  ``cli_argparser_biep``, ``LITELLM_BASE_URL``, etc.)
- ``notebooks._shared.area_shims.biiep_v3_dashboard``
  (R2 + R3 — ``build_biep_v3_dashboard(jurisdiction, milestone, deferred)``)
- ``notebooks._shared.db`` (the ibis-first connect helper —
  ``connect_md``, ``connect_local``, ``connect_local_lakehouse``, etc.)
- ``notebooks._shared.ragas_gauge`` (P5 — the ``RAGASGaugeWidget`` anywidget)

This module will be removed once ``notebooks/01_overview_setup.py`` +
``notebooks/ie_law_explorer.py`` (the only remaining consumers) are
refactored to the v14 standard.

Per the 2026-08-10-marimo-v14-cascading-effects-verification-v1
OpenSpec change + the 2026-08-10-marimo-v14-ireland-england-dashboards-refactor-v1
OpenSpec change.

Importable from any notebook under ``cianfhoghlaim/notebooks/`` (or from
the v4-consolidated venv via ``uv run --with``). Centralises:

- The canonical MotherDuck + DuckLake connection string
  (``md:cianfhoghlaim``) with graceful local-DuckDB fallback
  (``connect_biep_lakehouse()`` — ibis-first).
- The BIEP Leaving Cert subject topic helper.
- The leabharlann↔Leaving Cert cross-archive join helper.
- The path roots used by the demo notebooks (PDF corpus, LanceDB).
- The dual-mode (marimo + CLI) helpers:
  ``cl_argument_parser()``, ``run_as_script()``,
  ``import_dev_env_tool()``.

## KCG patterns used
- ibis (per `.agents/skills/ibis/SKILL.md`) — every connection goes
  through ``notebooks/_shared/db.py:connect_md()`` (NO raw
  ``ibis.duckdb.connect(uri)``). The legacy raw-``duckdb.connect`` helpers
  are kept as backward-compat shims but are no longer the canonical
  path.

Reference: openspec/changes/2026-07-25-nb-utils-ibis-first-v1/
openspec/changes/2026-07-06-british-isles-education-pipeline-v1/
openspec/changes/2026-07-06-notebooks-flatten-refactor-and-wire-bi-ep/
"""
from __future__ import annotations

import argparse
import importlib.util
import os
import sys
from pathlib import Path
from typing import Any

# Canonical BIEP subject / level / language contracts (unchanged from v1).
BIEP_SUBJECTS: tuple[str, ...] = (
    "mathematics",
    "applied_mathematics",
    "english",
    "gaeilge",
    "biology",
    "chemistry",
)
BIEP_LEVELS: tuple[str, ...] = ("higher", "ordinary", "foundation")
BIEP_LANGUAGES: tuple[str, ...] = ("en", "ga")

# Canonical repo-root resolver.
REPO_ROOT = Path(
    os.environ.get(
        "CIANFHOGHLAIM_ROOT",
        str(Path(__file__).resolve().parents[2]),
    )
).resolve()

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
    "md:cianfhoghlaim",
)

__all__ = [
    # BIEP canonical contracts
    "BIEP_SUBJECTS",
    "BIEP_LEVELS",
    "BIEP_LANGUAGES",
    "REPO_ROOT",
    "ROOT",
    "LAKEHOUSE_DUCKDB",
    # ibis-first lakehouse connection (canonical)
    "connect_biep_lakehouse",
    # Backward-compat shims (still callable; raw duckdb internally)
    "connect_md_oideachais",
    # BIEP query helpers
    "lc_subject_query",
    "leabharlann_join_to_lc",
    # CLI / dual-mode helpers
    "cl_argument_parser",
    "run_as_script",
    "import_dev_env_tool",
]


# -----------------------------------------------------------------------------
# Lakehouse connect helpers (ibis-first — canonical, refactored 2026-07-25)
# -----------------------------------------------------------------------------

def connect_biep_lakehouse(
    *,
    use_md: bool | None = None,
    local_fallback: bool = True,
) -> tuple[Any, str]:
    """Connect to the BIEP MotherDuck + DuckLake lakehouse (ibis-first).

    Returns ``(conn, engine_label)`` where ``conn`` is an
    ``ibis.duckdb.connect`` handle (NOT a raw ``duckdb.connect`` handle)
    and ``engine_label`` is one of: ``"md:cianfhoghlaim"``, ``"local_duckdb"``,
    or ``"unavailable"``.

    Selection logic:
    1. If ``use_md=True`` (or env ``MOTHERDUCK_ENABLED=true``) AND
       ``MOTHERDUCK_TOKEN`` is set, try ``md:cianfhoghlaim``.
    2. If that fails AND ``local_fallback=True``, fall back to an
       in-memory DuckDB via ``ibis.duckdb.connect(":memory:")`` so
       notebooks still render during local development.
    3. If both fail, return the in-memory handle with label
       ``"unavailable"``.

    This replaces the 12+ duplicated ``try: connect("md:cianfhoghlaim")
    except: connect(":memory:")`` blocks across the BIEP dashboards
    AND migrates them to ibis-first per the 2026-07-25 refactor.
    """
    from notebooks._shared.db import connect_md as _ibis_connect_md
    from notebooks._shared.db import connect_local as _ibis_connect_local

    if use_md is None:
        use_md = os.environ.get("MOTHERDUCK_ENABLED", "").lower() == "true"

    if use_md and os.environ.get("MOTHERDUCK_TOKEN", ""):
        try:
            return _ibis_connect_md(), "md:cianfhoghlaim"
        except Exception:
            if not local_fallback:
                raise
    if local_fallback:
        return _ibis_connect_local(), "local_duckdb"
    return _ibis_connect_local(), "unavailable"


def connect_md_oideachais(*, legacy_raw: bool = False) -> Any:
    """Connect to the MotherDuck + DuckLake lakehouse.

    By default this returns an ``ibis.duckdb.connect`` handle via the
    canonical ``connect_md()`` helper (per the 2026-07-25 refactor).
    Set ``legacy_raw=True`` to get the legacy raw ``duckdb.connect``
    handle (backward-compat only — do not use in new code).
    """
    if legacy_raw:
        import duckdb  # type: ignore[import-not-found]
        token = os.environ.get("MOTHERDUCK_TOKEN")
        if token:
            duckdb.sql(f"SET motherduck_token='{token}'")
        return ibis.duckdb.connect("md:cianfhoghlaim")
    from notebooks._shared.db import connect_md as _ibis_connect_md
    return _ibis_connect_md()


# -----------------------------------------------------------------------------
# BIEP query helpers (legacy duckdb.Relation return type — keep for compat)
# -----------------------------------------------------------------------------

def lc_subject_query(
    subject: str,
    level: str = "higher",
    language: str = "en",
) -> Any:
    """Read the canonical topic table for an LC subject.

    Returns a relation-like object (ibis Table from the canonical
    ibis connection). For back-compat with old callers that used
    ``.df()`` / ``.fetchall()``, the returned ibis Table supports
    ``.execute()`` and ``.to_pandas()``.
    """
    from notebooks._shared.db import connect_md as _ibis_connect_md
    conn = _ibis_connect_md()
    return conn.sql(f"""
        SELECT subject, level, language, topic, count(*) AS n
        FROM cianfhoghlaim.leaving_cert.{subject}_topics
        WHERE level = '{level}' AND language = '{language}'
        GROUP BY subject, level, language, topic
        ORDER BY n DESC
    """)


def leabharlann_join_to_lc(book_id: str, topic: str) -> Any:
    """Cross-archive join: leabharlann book ↔ LC topic (ibis-first)."""
    from notebooks._shared.db import connect_md as _ibis_connect_md
    conn = _ibis_connect_md()
    return conn.sql(f"""
        SELECT b.book_id, b.title, t.topic, t.subject, t.level, t.language
        FROM cianfhoghlaim.leabharlann.books b
        JOIN cianfhoghlaim.leaving_cert.{topic}_topics t
          ON b.topic_embedding <-> t.topic_embedding < 0.3
        WHERE b.book_id = '{book_id}'
    """)


# -----------------------------------------------------------------------------
# CLI / dual-mode helpers (Phase 5 + Phase 6 — unchanged)
# -----------------------------------------------------------------------------

def cl_argument_parser(
    *,
    prog: str | None = None,
    description: str = "",
) -> argparse.ArgumentParser:
    """Argparse factory with the BIEP canonical flags pre-registered."""
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
    """Execute ``main_fn(argv)`` and exit with its return code."""
    sys.argv = ["marimo-notebook", *(argv if argv is not None else sys.argv[1:])]
    rc = main_fn(sys.argv[1:])
    return int(rc) if rc is not None else 0


def import_dev_env_tool(name: str = "dev_env") -> Any:
    """Import the canonical ``cianfhoghlaim.agents.adk.tools.dev_env`` module."""
    here = Path(__file__).resolve().parent
    tool_path = here.parent / "agents" / "adk" / "tools" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, tool_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"dev_env tool not found at {tool_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod