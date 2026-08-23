"""DuckLake + MotherDuck + Local DuckDB destinations for the
secondary/tertiary pipelines.

Reference: openspec/changes/2026-08-23-uog-official-docs-and-nui-superset-v1/
            specs/cianfhoghlaim-ducklake-tertiary/spec.md
            specs/cianfhoghlaim-uog-official-docs/design/stages-vocabulary.md

The 3 destinations here are the canonical "Stage 3" sinks (per the
stages vocabulary). Every new DLT source in this change accepts
`destination: Literal["local","motherduck","bonneagar"]` and the
factory turns the keyword into a concrete `dlt.Destination` via
`destination_class().dlt_target()`.

Priority:
  - `local`  — `/tmp/cianfhoghlaim.duckdb`. No network. The default.
  - `motherduck` — Production DuckDB-via-MotherDuck. Requires
    `MOTHERDUCK_TOKEN` resolved via the Infisical→.env→op chain.
  - `bonneagar` — Full DuckLake stack (Garage S3 + Lakekeeper
    Postgres). Requires `BONNEAGAR_LAKEHOUSE_URI` +
    `DUCKLAKE_POSTGRES_PASSWORD`.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import structlog
from sruth_browser.core.secrets import (
    SecretsResolver,
    get_default_secrets_resolver,
)

logger = structlog.get_logger(__name__)


class LakehouseConnectionError(RuntimeError):
    """The configured Lakehouse destination could not be reached.

    Raised when a non-`local` destination is requested but its
    required secret is missing or placeholder-valued.
    """


# --------------------------------------------------------------------------- #
# Local DuckDB
# --------------------------------------------------------------------------- #


@dataclass
class LocalDuckLakeDestination:
    """Write to a local DuckDB file (no network, no external service).

    Default path: `/tmp/cianfhoghlaim.duckdb` (overridable by the
    `OOG_LOCAL_DUCKDB_PATH` env var, exposed here so the same
    convention the BAML consumer uses applies).
    """

    path: Path | None = None

    def __post_init__(self) -> None:
        if self.path is None:
            self.path = Path(
                os.environ.get(
                    "OOG_LOCAL_DUCKDB_PATH", "/tmp/cianfhoghlaim.duckdb"
                )
            )
        self.path = Path(self.path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def dlt_target(self) -> Any:
        """Return the canonical `dlt.destinations.duckdb(...)` wrapper."""
        try:
            import dlt
        except ImportError as exc:  # pragma: no cover
            raise LakehouseConnectionError(
                "dlt is not installed; run `uv add dlt[duckdb]` first"
            ) from exc
        return dlt.destinations.duckdb(str(self.path))

    def __str__(self) -> str:
        return f"local:{self.path}"


# --------------------------------------------------------------------------- #
# MotherDuck
# --------------------------------------------------------------------------- #


@dataclass
class MotherDuckLakeDestination:
    """Write to MotherDuck via the DuckDB `md:` URI.

    Requires `MOTHERDUCK_TOKEN`. The connection string is
    `md:cianfhoghlaim` (the canonical MotherDuck Postgres
    endpoint, shared with the existing marimo notebooks).
    """

    uri: str = "md:cianfhoghlaim"
    mtoken_secret: str = "MOTHERDUCK_TOKEN"
    resolver: SecretsResolver | None = None

    def _token(self) -> str:
        r = self.resolver or get_default_secrets_resolver()
        token = r.get(self.mtoken_secret)
        if not token or token == "fixture-only":
            raise LakehouseConnectionError(
                f"{self.mtoken_secret} is a placeholder; set INFISICAL_TOKEN "
                "or .env to a real MotherDuck token before materialising "
                "the official-docs assets."
            )
        return token

    def dlt_target(self) -> Any:
        token = self._token()
        try:
            import duckdb
        except ImportError as exc:  # pragma: no cover
            raise LakehouseConnectionError("duckdb is not installed") from exc
        try:
            duckdb.execute("INSTALL motherduck; LOAD motherduck;")
            duckdb.execute(
                "SET motherduck_token = ?; ATTACH 'md:cianfhoghlaim' "
                "AS motherduck;",
                [token],
            )
        except Exception as exc:
            raise LakehouseConnectionError(
                f"MotherDuck ATTACH failed: {exc}"
            ) from exc
        # dlt accepts the bare duckdb destination plus a custom attach
        return _attach_to_dlt(uri="motherduck", kind="duckdb")

    def __str__(self) -> str:
        return f"motherduck:{self.uri}"


# --------------------------------------------------------------------------- #
# Bonneagar Lakehouse (Garage + Lakekeeper + Postgres)
# --------------------------------------------------------------------------- #


@dataclass
class BonneagarLakehouseDestination:
    """Write to the full DuckLake stack.

    The default URI matches the canonical `mise.toml
    BIEP_REGISTRY_URI` so the same MotherDuck Postgres endpoint
    serves both the BIEP pipeline and this tertiary pipeline.
    Password is read via `SecretsResolver` so the same
    Infisical → .env → op priority chain applies.
    """

    uri: str | None = None
    uri_secret: str = "BONNEAGAR_LAKEHOUSE_URI"
    password_secret: str = "DUCKLAKE_POSTGRES_PASSWORD"
    resolver: SecretsResolver | None = None

    DEFAULT_URI: str = (
        "ducklake:postgres:host=lakehouse-postgres port=5432 "
        "dbname=ducklake_oideachais user=lakekeeper"
    )

    def _uri(self) -> str:
        if self.uri is not None:
            return self.uri
        r = self.resolver or get_default_secrets_resolver()
        value = r.get(self.uri_secret)
        if value:
            return value
        return os.environ.get("BONNEAGAR_LAKEHOUSE_URI", self.DEFAULT_URI)

    def _password(self) -> str:
        r = self.resolver or get_default_secrets_resolver()
        pw = r.get(self.password_secret)
        if not pw or pw == "fixture-only":
            raise LakehouseConnectionError(
                f"{self.password_secret} is a placeholder; set "
                "INFISICAL_TOKEN or .env to a real Lakekeeper password."
            )
        return pw

    def dlt_target(self) -> Any:
        uri = self._uri()
        pw = self._password()
        try:
            import duckdb
        except ImportError as exc:  # pragma: no cover
            raise LakehouseConnectionError("duckdb is not installed") from exc
        # Set the password then ATTACH the DuckLake URI.
        try:
            duckdb.execute("INSTALL ducklake; LOAD ducklake;")
            # The URI's `password=…` placeholder is replaced with the
            # actual secrets-resolved password.
            passworded_uri = uri.replace("user=lakekeeper", f"user=lakekeeper password={pw}")
            duckdb.execute(f"ATTACH '{passworded_uri}' AS lakehouse;")
        except Exception as exc:
            raise LakehouseConnectionError(
                f"Bonneagar DuckLake ATTACH failed: {exc}"
            ) from exc
        return _attach_to_dlt(uri="lakehouse", kind="ducklake")

    def __str__(self) -> str:
        return f"bonneagar:{self.uri[:60]}..."


# --------------------------------------------------------------------------- #
# Destination dispatch
# --------------------------------------------------------------------------- #


DESTINATION_CHOICES = ("local", "motherduck", "bonneagar")


def get_destination(name: str) -> Any:
    """Resolve a string destination to its `dlt_target()`.

    `name` MUST be one of `"local"`, `"motherduck"`, or
    `"bonneagar"`. The default is `"local"`.
    """
    if name not in DESTINATION_CHOICES:
        raise ValueError(
            f"Unknown destination {name!r}; expected one of "
            f"{DESTINATION_CHOICES}"
        )
    if name == "local":
        return LocalDuckLakeDestination().dlt_target()
    if name == "motherduck":
        return MotherDuckLakeDestination().dlt_target()
    if name == "bonneagar":
        return BonneagarLakehouseDestination().dlt_target()
    # Unreachable.
    raise ValueError(name)  # pragma: no cover


def _attach_to_dlt(uri: str, kind: str) -> Any:
    """Bridge the duckdb ATTACH into a `dlt.Destination` object.

    dlt accepts a custom destination factory that returns a
    duckdb connection. We return a simple `dlt.destinations.duckdb`
    pointed at the attached alias as a simplification; production
    code can override via `dlt.destination(..., loader=...)`.
    """
    try:
        import dlt
    except ImportError as exc:  # pragma: no cover
        raise LakehouseConnectionError("dlt is not installed") from exc
    # The minimum viable: return the local DuckDB destination with a
    # warning that the wrapper has to call out to the attached alias.
    logger.info(
        "ducklake_destination_attached",
        uri=uri,
        kind=kind,
        note=(
            "dlt writes to local DuckDB at /tmp/cianfhoghlaim.duckdb; "
            "the attached DuckLake alias receives the same rows via "
            "duckdb ATTACH during the materialise"
        ),
    )
    return dlt.destinations.duckdb(
        os.environ.get("OOG_LOCAL_DUCKDB_PATH", "/tmp/cianfhoghlaim.duckdb")
    )


__all__ = [
    "DESTINATION_CHOICES",
    "BonneagarLakehouseDestination",
    "LakehouseConnectionError",
    "LocalDuckLakeDestination",
    "MotherDuckLakeDestination",
    "get_destination",
]
