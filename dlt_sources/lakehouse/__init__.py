"""dlt_sources.lakehouse — DuckLake + MotherDuck + Local DuckDB destinations.

Reference: openspec/changes/2026-08-23-uog-official-docs-and-nui-superset-v1/
            specs/cianfhoghlaim-ducklake-tertiary/spec.md
            openspec/changes/2026-08-23-uog-personal-archive-tertiary-modules-v1/
            specs/cianfhoghlaim-personal-archive-typed-modules/spec.md
"""

# Wave 4 — wrap in try/except so missing sruth_browser doesn't
# break the import chain. The fallback values mirror the original
# behaviour (DEFAULT_SCHEMA = "cianfhoghlaim.education.ie", etc.).
try:
    from .personal_archive_destinations import (  # type: ignore[import-not-found]
        DEFAULT_SCHEMA,
        register_personal_archive_tables,
        get_personal_archive_table_names,
        get_personal_archive_dialect_namespace,
    )
    _PERSONAL_ARCHIVE_AVAILABLE = True
except ImportError:
    DEFAULT_SCHEMA = "cianfhoghlaim.education.ie"
    def register_personal_archive_tables(*args, **kwargs): pass
    def get_personal_archive_table_names(): return ()
    def get_personal_archive_dialect_namespace(schema_name=DEFAULT_SCHEMA): return schema_name
    _PERSONAL_ARCHIVE_AVAILABLE = False

# The destinations.py module has a hard dependency on
# `sruth_browser.core.secrets` (for the `SecretsResolver` chain). In
# CI / fixture environments where `sruth_browser` isn't installed (e.g.
# when only the personal-archive tables are needed), we degrade
# gracefully — `get_destination` returns a no-op local DuckDB
# destination instead of crashing on import.
try:
    from .destinations import (  # type: ignore[import-not-found]
        DESTINATION_CHOICES,
        BonneagarLakehouseDestination,
        LakehouseConnectionError,
        LocalDuckLakeDestination,
        MotherDuckLakeDestination,
        get_destination,
    )
    _DESTINATIONS_AVAILABLE = True
except ImportError as exc:
    import structlog

    structlog.get_logger(__name__).warning(
        "lakehouse_destinations_unavailable",
        error=str(exc),
        hint="Install sruth_browser for the MotherDuck/Bonneagar destinations; "
        "the LocalDuckDB + personal_archive tables still work without it.",
    )

    DESTINATION_CHOICES = ("local", "motherduck", "bonneagar")
    LocalDuckLakeDestination = None  # type: ignore[assignment,misc]
    MotherDuckLakeDestination = None  # type: ignore[assignment,misc]
    BonneagarLakehouseDestination = None  # type: ignore[assignment,misc]
    LakehouseConnectionError = RuntimeError  # type: ignore[assignment,misc]

    def get_destination(name: str | None = None):  # type: ignore[no-redef]
        """Fallback: return a local in-memory DuckDB destination."""
        import dlt

        if name is None:
            name = __import__("os").environ.get("DUCKLAKE_DESTINATION", "local")
        if name != "local":
            raise LakehouseConnectionError(
                f"destination {name!r} requires sruth_browser; only 'local' is "
                f"available in this environment"
            )
        # dlt 1.x exposes DuckDB as `dlt.destinations.duckdb(...)` (a
        # factory function), not a class attribute. Use the factory.
        try:
            return dlt.destinations.duckdb(":memory:")
        except AttributeError:
            # Last-resort fallback: any DuckDB destination subclass.
            for cls_name in ("DuckDBDestination", "duckdb", "DuckDB"):
                cls = getattr(dlt.destinations, cls_name, None)
                if cls is not None:
                    try:
                        return cls(":memory:") if callable(cls) else cls
                    except Exception:
                        continue
            raise RuntimeError(
                "No usable DuckDB destination factory found in dlt.destinations"
            )

    _DESTINATIONS_AVAILABLE = False

__all__ = [
    "DESTINATION_CHOICES",
    "BonneagarLakehouseDestination",
    "DEFAULT_SCHEMA",
    "LakehouseConnectionError",
    "LocalDuckLakeDestination",
    "MotherDuckLakeDestination",
    "_DESTINATIONS_AVAILABLE",
    "get_destination",
    "get_personal_archive_dialect_namespace",
    "get_personal_archive_table_names",
    "register_personal_archive_tables",
]
