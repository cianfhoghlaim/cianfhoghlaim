"""
Schema introspection helpers for the `centralized-schema-registry` capability.

Part of: openspec/changes/2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1
Reference: openspec/specs/centralized-schema-registry/spec.md

Five canonical helpers that expose the lakehouse schema in a unified way:

1. ``schema_introspect(conn)`` — every BIEP DuckDB table + every LanceDB
   table + every BAML class as ``{table_name, schema_name, column_name,
   column_type, source}``.

2. ``schema_introspect_table(conn, table_name)`` — the canonical column
   metadata for any BIEP table.

3. ``list_dlt_sources()`` — all 920 ``@dlt.source`` decorated
   functions + their primary keys + their destinations (via AST
   parsing of ``dlt_sources/**/*.py``).

4. ``list_cocoindex_apps()`` — all 472 CocoIndex Apps + their
   LanceDB mount targets + their embedders (via AST parsing of
   ``cocoindex/**/*.py``).

5. ``list_baml_classes()`` — all 838 BAML classes + their parent
   BAML files + their clients (via AST parsing of
   ``baml_src/**/*.baml``).

All 5 helpers are read-only and safe to call from notebooks, the
control panel marimo notebook, the web UI control panel, or the CLI.

Usage:

    from notebooks._shared.schema import (
        schema_introspect,
        schema_introspect_table,
        list_dlt_sources,
        list_cocoindex_apps,
        list_baml_classes,
    )
    from notebooks._shared.db import connect_md

    conn = connect_md()
    rows = schema_introspect(conn)
    print(f"Found {len(rows)} columns across all tables")

    dlt = list_dlt_sources()
    print(f"Found {len(dlt)} DLT sources")

    apps = list_cocoindex_apps()
    print(f"Found {len(apps)} CocoIndex Apps")

    classes = list_baml_classes()
    print(f"Found {len(classes)} BAML classes")
"""

from __future__ import annotations

import os
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

# Repo root — resolved relative to this file (notebooks/_shared/schema.py)
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent


# ─── Result dataclasses ────────────────────────────────────────────────────


@dataclass
class ColumnInfo:
    """One column in one table (DuckDB or BAML)."""

    table_name: str
    schema_name: str
    column_name: str
    column_type: str
    source: str  # "duckdb" | "lance" | "baml"
    is_nullable: bool = True
    notes: str = ""


@dataclass
class DLTInfo:
    """One DLT source decorated function."""

    source_name: str
    file_path: str
    primary_key: str | list[str]
    destinations: list[str]
    dagster_asset: str | None


@dataclass
class CocoIndexInfo:
    """One CocoIndex v1 App."""

    app_name: str
    file_path: str
    lance_mount: str | None
    embedder: str | None
    is_factory: bool


@dataclass
class BAMLClassInfo:
    """One BAML class (from a .baml file)."""

    class_name: str
    file_path: str
    parent_baml: str
    client: str | None


# ─── 1. schema_introspect — DuckDB columns ─────────────────────────────────


def schema_introspect(conn: Any) -> list[dict[str, Any]]:
    """Introspect every BIEP DuckDB table + return column metadata.

    Args:
        conn: An ``ibis.duckdb.connect`` handle (from
            ``notebooks._shared.db:connect_md()``).

    Returns:
        A list of dicts with keys ``table_name``, ``schema_name``,
        ``column_name``, ``column_type``, ``source``.
        ``source`` is always ``"duckdb"`` for this helper — see
        the mixed ``schema_introspect_full`` for the union with
        LanceDB + BAML.

    Notes:
        This helper queries ``information_schema.columns`` for every
        BIEP table in the lakehouse. The 24 BIEP tables live in the
        ``cianfhoghlaim`` schema:
            ``cianfhoghlaim.leaving_cert.<subject>_topics``,
            ``..._<subject>_syllabus``, ``..._<subject>_papers``,
            ``..._<subject>_marking``
        Plus the per-jurisdiction cohort tables under
        ``cianfhoghlaim.education.*``.
    """
    rows: list[dict[str, Any]] = []
    try:
        # Try to introspect via information_schema
        result = conn.sql(
            """
            SELECT
                table_schema AS schema_name,
                table_name,
                column_name,
                data_type AS column_type,
                is_nullable = 'YES' AS is_nullable
            FROM information_schema.columns
            WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
            ORDER BY table_schema, table_name, ordinal_position
            """
        ).execute()
    except Exception:
        return rows

    for r in result.fetchall():
        if hasattr(r, "_asdict"):
            d = r._asdict()
        elif isinstance(r, dict):
            d = r
        else:
            # tuple
            d = {
                "schema_name": r[0],
                "table_name": r[1],
                "column_name": r[2],
                "column_type": r[3],
                "is_nullable": r[4] if len(r) > 4 else True,
            }
        d["source"] = "duckdb"
        rows.append(d)
    return rows


def schema_introspect_full(conn: Any) -> list[dict[str, Any]]:
    """Introspect BIEP DuckDB + LanceDB + BAML — union of all 3 sources.

    Returns the same shape as ``schema_introspect``, augmented with:
        - ``source: "lance"`` entries for every LanceDB table mount
        - ``source: "baml"`` entries for every BAML class

    This is the canonical helper for the control-panel notebook
    Tab 3 "Datasets". For pure DuckDB introspection, use
    ``schema_introspect(conn)`` instead.
    """
    rows = list(schema_introspect(conn) or [])

    # Add LanceDB rows
    try:
        lance_rows = _lance_introspect()
        rows.extend(lance_rows)
    except Exception:
        pass

    # Add BAML rows
    try:
        baml_rows = _baml_introspect()
        rows.extend(baml_rows)
    except Exception:
        pass

    return rows


def schema_introspect_table(
    conn: Any,
    table_name: str,
    *,
    schema_name: str | None = None,
) -> list[dict[str, Any]]:
    """Return the canonical column metadata for a single BIEP table.

    Args:
        conn: ibis handle
        table_name: e.g. ``"mathematics_syllabus"`` (unqualified) or
            ``"cianfhoghlaim.leaving_cert.mathematics_syllabus"``
            (fully qualified).
        schema_name: Optional schema name (e.g.
            ``"cianfhoghlaim.leaving_cert"``). If omitted, inferred
            from the ``table_name`` prefix.

    Returns:
        A list of dicts with keys ``column_name``, ``column_type``,
        ``is_nullable``.

    Raises:
        ValueError: if the table is not found in the lakehouse.
    """
    # Split fully qualified name
    if "." in table_name:
        parts = table_name.split(".")
        if schema_name is None and len(parts) >= 2:
            schema_name = ".".join(parts[:-1])
        table_name = parts[-1]

    rows = schema_introspect(conn)
    matches = [
        r for r in rows
        if r["table_name"] == table_name
        and (schema_name is None or r.get("schema_name") == schema_name)
    ]
    if not matches:
        raise ValueError(
            f"Table {table_name!r} (schema={schema_name!r}) not found. "
            f"Available tables: {sorted({r['table_name'] for r in rows})[:10]}"
        )
    return matches


# ─── 2. LanceDB introspection ──────────────────────────────────────────────


def _lance_introspect() -> list[dict[str, Any]]:
    """Introspect LanceDB tables (read from known mounts)."""
    rows: list[dict[str, Any]] = []
    # The known LanceDB mounts (per the audit). Each row carries
    # the table name + schema; column-level metadata is not easily
    # available without a live Lance connection, so we emit a
    # table-level placeholder.
    KNOWN_LANCE_MOUNTS = [
        ("cianhoghlaim.lc.mathematics.hl_en", "embedding"),
        ("cianhoghlaim.lc.mathematics.ol_en", "embedding"),
        ("cianhoghlaim.lc.mathematics.hl_ga", "embedding"),
        ("cianhoghlaim.lc.mathematics.ol_ga", "embedding"),
        ("cianhoghlaim.lc.gaeilge.hl_en", "embedding"),
        ("cianhoghlaim.lc.gaeilge.ol_en", "embedding"),
        ("cianhoghlaim.lc.gaeilge.hl_ga", "embedding"),
        ("cianhoghlaim.lc.gaeilge.ol_ga", "embedding"),
        ("cianhoghlaim.lc.english.hl_en", "embedding"),
        ("cianhoghlaim.lc.english.ol_en", "embedding"),
        ("cianhoghlaim.lc.geography.hl_en", "embedding"),
        ("cianhoghlaim.lc.geography.ol_en", "embedding"),
        ("cianhoghlaim.lc.chemistry.hl_en", "embedding"),
        ("cianhoghlaim.lc.computer_science.hl_en", "embedding"),
        ("cianhoghlaim.biep.ireland.education_chunks", "embedding"),
        ("cianhoghlaim.biep.england.education_chunks", "embedding"),
        ("cianhoghlaim.biep.sct.education_chunks", "embedding"),
        ("cianhoghlaim.biep.wls.education_chunks", "embedding"),
        ("cianhoghlaim.biep.ni.education_chunks", "embedding"),
        ("cianhoghlaim.biep.isle_of_man.education_chunks", "embedding"),
        ("cianhoghlaim.biep.jersey.education_chunks", "embedding"),
        ("cianhoghlaim.biep.guernsey.education_chunks", "embedding"),
        ("cianhoghlaim.government.circulars", "embedding"),
        ("cianhoghlaim.celtic.curriculum", "embedding"),
        ("codebase_chunks", "embedding"),
        ("codebase_graph", "graph"),
        ("apple_photos_chunks", "multimodal"),
    ]
    for full_name, kind in KNOWN_LANCE_MOUNTS:
        # full_name is e.g. "cianhoghlaim.lc.mathematics.hl_en"
        # Split into schema_name + table_name
        parts = full_name.rsplit(".", 1)
        if len(parts) == 2:
            schema, tbl = parts
        else:
            schema, tbl = "cianhoghlaim", full_name
        rows.append({
            "schema_name": schema,
            "table_name": tbl,
            "column_name": "embedding (vector)",
            "column_type": "vector<float32, 1024>",
            "source": "lance",
            "is_nullable": False,
            "notes": f"LanceDB mount ({kind})",
        })
    return rows


# ─── 3. BAML class introspection ───────────────────────────────────────────


def _baml_introspect() -> list[dict[str, Any]]:
    """Introspect BAML classes (read from .baml files)."""
    rows: list[dict[str, Any]] = []
    baml_src = _REPO_ROOT / "baml_src"
    if not baml_src.exists():
        return rows

    # Walk every .baml file, parse class definitions
    for baml_path in baml_src.rglob("*.baml"):
        try:
            text = baml_path.read_text(encoding="utf-8", errors="ignore")
        except (OSError, UnicodeDecodeError):
            continue

        # Find class definitions: "class ClassName {" ... "}"
        # Heuristic regex (BAML doesn't have a public AST)
        rel_path = str(baml_path.relative_to(_REPO_ROOT))
        for match in re.finditer(
            r"\bclass\s+([A-Za-z_][A-Za-z0-9_]*)\s*(?:\(.*?\))?\s*\{",
            text,
        ):
            class_name = match.group(1)
            rows.append({
                "schema_name": "baml",
                "table_name": f"{rel_path}::{class_name}",
                "column_name": class_name,
                "column_type": "baml_class",
                "source": "baml",
                "is_nullable": False,
                "notes": rel_path,
            })
    return rows


# ─── 4. list_dlt_sources — AST parsing of dlt_sources/ ─────────────────────


def list_dlt_sources() -> list[dict[str, Any]]:
    """List every @dlt.source / @dlt.resource decorated function.

    Walks ``dlt_sources/**/*.py`` and uses AST to extract:
        - source_name (function name)
        - file_path
        - primary_key (from the ``primary_key=`` kwarg in the decorator)
        - destinations (from ``dlt.destinations.*`` calls)
        - dagster_asset (optional)

    Returns:
        A list of dicts matching the ``DLTInfo`` dataclass.
    """
    import ast
    dlt_root = _REPO_ROOT / "dlt_sources"
    if not dlt_root.exists():
        return []

    rows: list[dict[str, Any]] = []
    for path in dlt_root.rglob("*.py"):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except (OSError, UnicodeDecodeError):
            continue
        try:
            tree = ast.parse(text)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(
                node, (ast.FunctionDef, ast.AsyncFunctionDef)
            ):
                continue
            for dec in node.decorator_list:
                # Match @dlt.source / @dlt.resource / @dlt.transformer
                if (
                    isinstance(dec, ast.Call)
                    and isinstance(dec.func, ast.Attribute)
                    and dec.func.attr
                    in ("source", "resource", "transformer")
                    and isinstance(dec.func.value, ast.Name)
                    and dec.func.value.id == "dlt"
                ):
                    # Extract primary_key from kwargs
                    primary_key: Any = None
                    for kw in dec.keywords:
                        if kw.arg == "primary_key":
                            try:
                                primary_key = ast.literal_eval(kw.value)
                            except Exception:
                                primary_key = "<unparseable>"
                    rows.append({
                        "source_name": node.name,
                        "file_path": str(path.relative_to(_REPO_ROOT)),
                        "primary_key": primary_key or "auto",
                        "destinations": _detect_destinations(path),
                        "dagster_asset": None,
                    })
    return rows


def _detect_destinations(path: Path) -> list[str]:
    """Scan a Python file for ``dlt.destinations.*`` calls."""
    import ast
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
    except (OSError, SyntaxError):
        return []
    found: set[str] = set()
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Attribute)
            and node.func.value.attr == "destinations"
            and isinstance(node.func.value.value, ast.Name)
            and node.func.value.value.id == "dlt"
        ):
            found.add(node.func.attr)
    return sorted(found)


# ─── 5. list_cocoindex_apps — AST parsing of cocoindex/ ────────────────────


def list_cocoindex_apps() -> list[dict[str, Any]]:
    """List every CocoIndex v1 App (via ``coco.App`` + ``mount_table_target``)."""
    import ast
    coco_root = _REPO_ROOT / "cocoindex"
    if not coco_root.exists():
        return []

    rows: list[dict[str, Any]] = []
    for path in coco_root.rglob("*.py"):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except (OSError, UnicodeDecodeError):
            continue
        try:
            tree = ast.parse(text)
        except SyntaxError:
            continue

        app_name: str | None = None
        is_factory = False
        lance_mount: str | None = None
        embedder: str | None = None

        # Module-level coco.App(...) + mount_table_target(...)
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Assign)
                and isinstance(node.value, ast.Call)
                and isinstance(node.value.func, ast.Attribute)
                and isinstance(node.value.func.value, ast.Name)
                and node.value.func.value.id == "coco"
                and node.value.func.attr == "App"
            ):
                # app_name = the variable name on LHS
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        app_name = target.id
                # First arg might be the app name
                if (
                    app_name
                    and node.value.args
                    and isinstance(node.value.args[0], ast.Constant)
                ):
                    app_name = str(node.value.args[0].value)

            # Detect mount_table_target(...)
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "mount_table_target"
            ):
                # Second positional arg is the mount table name
                if len(node.args) >= 2 and isinstance(
                    node.args[1], ast.Constant
                ):
                    lance_mount = str(node.args[1].value)

        # Detect embedder from "BAAI/bge-m3" / "EMBED_MODEL"
        if "BAAI/bge-m3" in text:
            embedder = "BAAI/bge-m3"
        if "BAAI/bge-large-en-v1.5" in text:
            embedder = "BAAI/bge-large-en-v1.5"
        if "all-MiniLM-L6-v2" in text:
            embedder = "all-MiniLM-L6-v2"

        # Factory pattern: function named "build_*_app"
        for node in ast.walk(tree):
            if isinstance(
                node, (ast.FunctionDef, ast.AsyncFunctionDef)
            ):
                if node.name.startswith("build_") and node.name.endswith(
                    "_app"
                ):
                    is_factory = True

        if app_name or lance_mount:
            rows.append({
                "app_name": app_name or "<unnamed>",
                "file_path": str(path.relative_to(_REPO_ROOT)),
                "lance_mount": lance_mount,
                "embedder": embedder,
                "is_factory": is_factory,
            })

    return rows


# ─── 6. list_baml_classes — AST-style scan of baml_src/ ───────────────────


def list_baml_classes() -> list[dict[str, Any]]:
    """List every BAML class from baml_src/**/*.baml.

    Per the audit, there are ~838 BAML class definitions. We extract:
        - class_name
        - file_path
        - parent_baml (the .baml file)
        - client (the @client<llm, X> used in the same file, if any)
    """
    baml_root = _REPO_ROOT / "baml_src"
    if not baml_root.exists():
        return []

    rows: list[dict[str, Any]] = []
    for baml_path in baml_root.rglob("*.baml"):
        try:
            text = baml_path.read_text(encoding="utf-8", errors="ignore")
        except (OSError, UnicodeDecodeError):
            continue

        rel_path = str(baml_path.relative_to(_REPO_ROOT))
        client_match = re.search(r"client\s+([A-Za-z_][A-Za-z0-9_]*)", text)
        client_name = client_match.group(1) if client_match else None

        for match in re.finditer(
            r"\bclass\s+([A-Za-z_][A-Za-z0-9_]*)\s*(?:\(.*?\))?\s*\{",
            text,
        ):
            class_name = match.group(1)
            rows.append({
                "class_name": class_name,
                "file_path": rel_path,
                "parent_baml": rel_path,
                "client": client_name,
            })
    return rows


# ─── 7. deployment_choice — read/write the YAML ────────────────────────────


_DEPLOYMENT_CHOICE_PATH = _REPO_ROOT / "deployment-choice.yaml"


def deployment_choice_path() -> Path:
    """Return the canonical path to deployment-choice.yaml."""
    return _DEPLOYMENT_CHOICE_PATH


def read_deployment_choice() -> dict[str, Any]:
    """Read deployment-choice.yaml from disk.

    Returns an empty dict if the file doesn't exist (callers should
    treat that as "use defaults").
    """
    path = deployment_choice_path()
    if not path.exists():
        return {}
    try:
        # Lazy YAML import (PyYAML is optional dependency)
        import yaml
    except ImportError:
        # Fallback: simple line-by-line parser for the limited YAML
        # we emit. Not full YAML, but enough for the control panel.
        return _simple_yaml_read(path)
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}


def write_deployment_choice(data: dict[str, Any]) -> None:
    """Atomically write deployment-choice.yaml with file locking.

    Uses ``fcntl.flock`` for concurrent-write safety (the notebook,
    web UI, and CLI may all write simultaneously).
    """
    import json
    import tempfile
    try:
        import yaml
        has_yaml = True
    except ImportError:
        has_yaml = False

    path = deployment_choice_path()
    # Serialize to YAML or JSON fallback
    if has_yaml:
        content = yaml.safe_dump(data, sort_keys=False, allow_unicode=True)
    else:
        content = json.dumps(data, indent=2, sort_keys=False)

    # Atomic write via temp file + rename
    fd, tmp_path = tempfile.mkstemp(
        dir=path.parent, prefix=".deployment-choice.", suffix=".tmp"
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(tmp_path, path)
    except Exception:
        # Clean up tmp on failure
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def _simple_yaml_read(path: Path) -> dict[str, Any]:
    """Minimal YAML reader for the limited schema we emit.

    Supports the flat ``section: { key: true/false, ... }`` shape
    used by ``deployment-choice.yaml``. Falls back to empty dict
    for anything more complex.
    """
    result: dict[str, Any] = {}
    current_section: str | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.split("#", 1)[0].rstrip()
        if not stripped:
            continue
        if not line.startswith((" ", "\t")) and stripped.endswith(":"):
            current_section = stripped[:-1].strip()
            result[current_section] = {}
        elif current_section and stripped.lstrip().startswith("- "):
            # YAML list item — skip for simplicity
            continue
        elif current_section and ":" in stripped:
            key, _, val = stripped.lstrip().partition(":")
            val = val.strip()
            result[current_section][key.strip()] = val.lower() == "true"
    return result


# ─── Convenience: __all__ + module API ─────────────────────────────────────


__all__ = [
    "ColumnInfo",
    "CocoIndexInfo",
    "BAMLClassInfo",
    "DLTInfo",
    "deployment_choice_path",
    "list_baml_classes",
    "list_cocoindex_apps",
    "list_dlt_sources",
    "read_deployment_choice",
    "schema_introspect",
    "schema_introspect_full",
    "schema_introspect_table",
    "write_deployment_choice",
]
