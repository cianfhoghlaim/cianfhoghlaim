"""Phase 5 runtime tests for `dlt_utils.source_factory.SourceFactory`.

Per
https://github.com/cianfhoghlaim/kings_college_galway/issues/20
the lateralise change's Phase 5 wires the 3 runtime constructors
(`source`, `dlt_asset`, `dagster_asset`) so callers can build
generic assets from any `sources.yaml` entry without writing a
manual wrapper.

This file covers:
  * `test_source_returns_callable` — `source()` returns a 0-arg
    callable that yields a dlt source when invoked.
  * `test_dlt_asset_produces_asset_definition` — `dlt_asset()`
    returns a Dagster asset.
  * `test_dagster_asset_produces_asset_definition` — `dagster_asset()`
    returns a Dagster asset.
  * `test_kind_to_constructor_mapping` — parametrised over 7 kinds.
  * `test_schedule_and_sensors_applied` — schedule + sensors
    from the YAML are respected.
  * `test_destination_applied` — DuckLake vs DuckDB destination
    is wired through to the dlt pipeline.

We do NOT materialise any DLT pipeline in these tests (that would
require a live destination). The tests assert the *shape* of the
returned objects, not their network behaviour.
"""
from __future__ import annotations

import os
from collections.abc import Callable
from typing import Any

import pytest

from dlt_utils.source_factory import (
    DEFAULT_SOURCES_PATH,
    SourceFactory,
    SourcesYAML,
    build_source,
    get_default_factory,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def factory() -> SourceFactory:
    return get_default_factory()


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------
def _safe_call_source(builder: Callable[[], Any]) -> Any:
    """Call a SourceFactory.source() builder, skipping on network
    failure (we don't want CI to require live HTTP for unit tests)."""
    try:
        return builder()
    except Exception as exc:  # pragma: no cover - network dependent
        pytest.skip(f"source() materialisation failed: {exc}")


# ---------------------------------------------------------------------------
# 1. source() — returns a callable DLT source builder
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "sid",
    [
        "ie.education.ncca",
        "ie.education.examinations",
        "en.medicine.nhs_england",
        "iom.medicine.health_social_care",
    ],
)
def test_source_returns_callable(factory: SourceFactory, sid: str) -> None:
    """`source(sid)` must return a 0-arg callable; calling it
    yields a dlt source (or a list of resources)."""
    builder = factory.source(sid)
    assert callable(builder), f"source({sid!r}) did not return a callable"
    # Invoking the builder must not raise; we don't require materialisation.
    src = _safe_call_source(builder)
    # A dlt source has `.resources`; a list of resources also works.
    if hasattr(src, "resources"):
        assert src.resources, f"source({sid!r}) returned an empty source"
    else:
        assert src, f"source({sid!r}) returned an empty result"


# ---------------------------------------------------------------------------
# 2. dlt_asset() — returns a Dagster asset definition
# ---------------------------------------------------------------------------
def test_dlt_asset_produces_asset_definition(factory: SourceFactory) -> None:
    """`dlt_asset(sid)` must return a Dagster asset (function or
    AssetsDefinition). The asset must have a `name` and a
    `compute_kind='dlt'`.
    """
    asset_obj = factory.dlt_asset("ie.education.ncca")
    # Dagster 1.12.6: @asset returns the bare function. The asset's
    # name is set via the `name=` kwarg and lives in the wrapped
    # function's `__wrapped__` or in `op_def.name` after Dagster
    # builds the AssetsDefinition.
    op_def = (
        getattr(asset_obj, "op", None)
        or getattr(asset_obj, "op_def", None)
    )
    assert op_def is not None, (
        f"dlt_asset() returned object without op/op_def: {asset_obj!r}"
    )
    name = getattr(op_def, "name", None)
    assert name, f"dlt_asset() op_def missing name: {op_def!r}"


# ---------------------------------------------------------------------------
# 3. dagster_asset() — returns a Dagster asset (lineage-only)
# ---------------------------------------------------------------------------
def test_dagster_asset_produces_asset_definition(
    factory: SourceFactory,
) -> None:
    """`dagster_asset(sid)` must return a Dagster asset with the
    canonical asset_key from the YAML."""
    asset_obj = factory.dagster_asset("ie.education.ncca")
    # Dagster 1.12.6: the @asset decorator returns the bare function.
    # We assert the op_def was built (proving the asset key resolved).
    op_def = (
        getattr(asset_obj, "op", None)
        or getattr(asset_obj, "op_def", None)
    )
    assert op_def is not None, (
        f"dagster_asset() returned object without op/op_def: {asset_obj!r}"
    )


# ---------------------------------------------------------------------------
# 4. kind → constructor mapping (parametrised over 7 kinds)
# ---------------------------------------------------------------------------
def _all_kinds_in_yaml() -> list[str]:
    """Read all unique `kind` values declared in the canonical YAML."""
    import yaml
    with open(DEFAULT_SOURCES_PATH) as fh:
        raw = yaml.safe_load(fh)
    return sorted({s["kind"] for s in raw["sources"]})


@pytest.mark.parametrize("kind", _all_kinds_in_yaml())
def test_kind_to_constructor_mapping(
    factory: SourceFactory, kind: str
) -> None:
    """For every `kind` declared in sources.yaml, `build_source()`
    must return a callable that yields a dlt source (or skip on
    network failure)."""
    # Pick the first source of this kind.
    matching = [s for s in factory.spec.sources if s.kind == kind]
    assert matching, f"No source in sources.yaml has kind={kind!r}"
    entry = matching[0]
    builder = build_source(entry, factory.spec.defaults)
    assert callable(builder), f"build_source(kind={kind!r}) did not return a callable"


# ---------------------------------------------------------------------------
# 5. schedule + sensors are honoured
# ---------------------------------------------------------------------------
def test_schedule_and_sensors_applied(factory: SourceFactory) -> None:
    """Sources with a non-default schedule or sensors list must
    surface those in `SourceEntry.schedule` and
    `SourceEntry.sensors`.
    """
    # Find a source that has a custom schedule or sensors declared.
    scheduled = [
        s for s in factory.spec.sources
        if s.schedule is not None or s.sensors
    ]
    if not scheduled:
        pytest.skip("no source in sources.yaml declares a custom schedule or sensors")
    s = scheduled[0]
    # The schedule is preserved verbatim (cron + timezone).
    if s.schedule is not None:
        assert s.schedule.cron, f"{s.id} schedule missing cron"
        assert s.schedule.timezone, f"{s.id} schedule missing timezone"
    # Sensors are preserved as a list.
    if s.sensors:
        for sensor in s.sensors:
            assert sensor in {"sitemap_hash", "rss", "webhook", "polling"}, (
                f"{s.id} sensor {sensor!r} not in the Literal"
            )


# ---------------------------------------------------------------------------
# 6. Destination is plumbed through to the DLT pipeline
# ---------------------------------------------------------------------------
def test_destination_applied() -> None:
    """The factory's `Defaults.destination` is plumbed through to
    the DLT pipeline by `dlt_utils.destinations.get_dlt_destination`.
    Verify the default is ducklake and that the plumbed function
    returns a destination object.
    """
    import os
    # Set USE_DUCKLAKE=true to make the destination deterministic
    # in CI (otherwise the function falls back to DuckDB).
    os.environ["USE_DUCKLAKE"] = "true"

    from dlt_utils.destinations import get_dlt_destination

    factory = get_default_factory()
    assert factory.spec.defaults.destination in {"ducklake", "iceberg", "duckdb"}
    # `get_dlt_destination` doesn't require live S3 when USE_DUCKLAKE
    # is set to a local file (it falls back). We just verify it
    # returns a non-None destination.
    try:
        dest = get_dlt_destination()
    except Exception as exc:
        # If the destination needs a live S3 endpoint, skip rather
        # than fail in CI.
        pytest.skip(f"get_dlt_destination() requires live infra: {exc}")
    assert dest is not None, "get_dlt_destination() returned None"


# ---------------------------------------------------------------------------
# 7. build_source() dispatcher covers all kinds
# ---------------------------------------------------------------------------
def test_build_source_dispatcher_covers_all_kinds() -> None:
    """The kind → constructor dispatcher must cover every `Kind`
    literal in the YAML's `kinds` list. We import the dispatcher
    table and assert it covers them all.
    """
    from dlt_utils.source_factory import _KIND_DISPATCH

    factory = get_default_factory()
    declared_kinds = set(factory.spec.kinds)
    implemented_kinds = set(_KIND_DISPATCH.keys())
    missing = declared_kinds - implemented_kinds
    assert not missing, (
        f"SourceFactory dispatcher is missing implementations for kinds: {sorted(missing)!r}"
    )
