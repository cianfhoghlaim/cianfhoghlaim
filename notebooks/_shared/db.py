"""Canonical ibis-first connection helper for the Cianfhoghlaim lakehouse.

The single source of truth for connecting to the BIEP MotherDuck +
DuckLake lakehouse. Replaces the 5+ raw `duckdb.connect(...)` call-sites
in the legacy `nb_utils.py`.

The pattern matches `marimo_dashboards/06_per_subject_analytics.py:84-95`
which already used ibis-first successfully.

## KCG patterns used
- ibis (per `.agents/skills/ibis/SKILL.md`) — `ibis.duckdb.connect`
  is the canonical entry point; no raw `duckdb.connect(uri)`.
- marimo (per `.agents/skills/marimo/SKILL.md`) — pure functions,
  marimo-agnostic.

Reference: openspec/changes/2026-07-25-nb-utils-ibis-first-v1/
"""
from __future__ import annotations

import os
from typing import Any

__all__ = ["connect_md", "connect_local", "lakehouse_uri"]


LAKEHOUSE_URI_DEFAULT = "md:cianfhoghlaim"
"""The canonical MotherDuck + DuckLake lakehouse alias."""


def lakehouse_uri() -> str:
    """Return the canonical lakehouse URI (env override supported).

    Honors ``CIANFHOGHLAIM_LAKEHOUSE_DUCKDB``; defaults to ``md:cianfhoghlaim``.
    """
    return os.environ.get(
        "CIANFHOGHLAIM_LAKEHOUSE_DUCKDB",
        LAKEHOUSE_URI_DEFAULT,
    )


def connect_md(*, read_only: bool = True) -> Any:
    """Return an ``ibis.duckdb.connect`` handle to the BIEP lakehouse.

    Parameters
    ----------
    read_only : bool
        If True (the default), connect in read-only mode.

    Returns
    -------
    ibis.duckdb.connect
        An ibis-wrapped DuckDB connection. NOT a raw ``duckdb.connect``
        handle (the legacy `nb_utils.connect_md_oideachais()` returns the
        raw handle — this helper is the ibis-first replacement).

    Notes
    -----
    The MotherDuck token is read from the runtime env
    (``MOTHERDUCK_TOKEN``); mise + Infisical hydration handles this.
    Falls back to ``:memory:`` if ``MOTHERDUCK_ENABLED != "true"`` or the
    token is missing.
    """
    try:
        import ibis  # type: ignore[import-not-found]
    except ImportError as exc:
        raise ImportError(
            "ibis is required for the canonical connect_md() helper. "
            "Install with `uv add ibis-framework[duckdb]`."
        ) from exc

    use_md = os.environ.get("MOTHERDUCK_ENABLED", "").lower() == "true"
    token = os.environ.get("MOTHERDUCK_TOKEN", "")
    uri = lakehouse_uri()

    if use_md and token:
        try:
            return ibis.duckdb.connect(uri, read_only=read_only)
        except Exception:
            pass  # fall through to :memory:

    return ibis.duckdb.connect(":memory:", read_only=read_only)


def connect_local(*, read_only: bool = True) -> Any:
    """Return an ``ibis.duckdb.connect`` handle to an in-memory DuckDB.

    Convenience helper for local development when the MotherDuck
    lakehouse is unreachable. Always succeeds (provided ibis is installed).
    """
    try:
        import ibis  # type: ignore[import-not-found]
    except ImportError as exc:
        raise ImportError(
            "ibis is required for connect_local(); "
            "install with `uv add ibis-framework[duckdb]`."
        ) from exc

    return ibis.duckdb.connect(":memory:", read_only=read_only)