"""Marimo Dashboards per-area shim.

Re-exports the canonical ``connect_md()`` helper from
``notebooks/_shared/db.py`` for use by every
``notebooks/marimo_dashboards/*.py`` notebook.

## KCG patterns used
- ibis (per `.agents/skills/ibis/SKILL.md`) — use ``connect_md()``
  instead of raw ``duckdb.connect``.
- marimo (per `.agents/skills/marimo/SKILL.md`).

Reference: openspec/changes/2026-07-25-nb-utils-ibis-first-v1/
"""
from __future__ import annotations

from notebooks._shared.db import connect_md, connect_local, lakehouse_uri

__all__ = ["connect_md", "connect_local", "lakehouse_uri"]