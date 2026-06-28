"""
oideachais.tests.dlt_sources.{nation}.law.test_crown_deps — Crown Dependencies
medicine + law DLT source tests.

Per
https://github.com/cianfhoghlaim/kings_college_galway/issues/19
(closed 2026-06-15) the lateralise change wired this as one of
the 6 crown-dependencies (IOM/JEY/GGY) medicine + law DLT
sources.

Parametrised over 6 (domain, nation, source_module,
asset_module, source_function, dlt_resource, asset_function)
tuples so the same test contract applies to all 6:

  * iom.medicine → medicine_iom_health_social_care
  * jey.medicine → medicine_jey_health_community_services
  * ggy.medicine → medicine_ggy_health_social_care
  * iom.law     → law_iom_legislation
  * jey.law     → law_jey_legislation
  * ggy.law     → law_ggy_legislation
"""
from __future__ import annotations

import importlib
from collections.abc import Callable
from typing import Any

import pytest

# ---------------------------------------------------------------------------
# Parametrisation data: (domain, nation, source_module, asset_module,
# source_function, dlt_resource, asset_function)
# ---------------------------------------------------------------------------
PARAMS: list[tuple[str, str, str, str, str, str, str]] = [
    (
        "medicine",
        "iom",
        "dlt_sources.iom.medicine.health_social_care",
        "dagster_defs.assets.medicine.iom",
        "iom_health_social_care_source",
        "pages",
        "medicine_iom_health_social_care",
    ),
    (
        "medicine",
        "jey",
        "dlt_sources.jey.medicine.health_community_services",
        "dagster_defs.assets.medicine.jey",
        "jey_health_community_services_source",
        "pages",
        "medicine_jey_health_community_services",
    ),
    (
        "medicine",
        "ggy",
        "dlt_sources.ggy.medicine.health_social_care",
        "dagster_defs.assets.medicine.ggy",
        "ggy_health_social_care_source",
        "pages",
        "medicine_ggy_health_social_care",
    ),
    (
        "law",
        "iom",
        "dlt_sources.iom.law.legislation",
        "dagster_defs.assets.law.iom",
        "iom_legislation_source",
        "acts",
        "law_iom_legislation",
    ),
    (
        "law",
        "jey",
        "dlt_sources.jey.law.legislation",
        "dagster_defs.assets.law.jey",
        "jey_legislation_source",
        "acts",
        "law_jey_legislation",
    ),
    (
        "law",
        "ggy",
        "dlt_sources.ggy.law.legislation",
        "dagster_defs.assets.law.ggy",
        "ggy_legislation_source",
        "acts",
        "law_ggy_legislation",
    ),
]


@pytest.fixture(params=PARAMS, ids=lambda p: f"{p[0]}_{p[1]}")
def crown_dep_source(
    request: pytest.FixtureRequest,
) -> tuple[str, str, str, str, str, str, str]:
    return request.param


def test_crown_dep_source_module_imports(crown_dep_source):
    """The dlt source module must import without error."""
    _domain, _nation, src_mod, _am, _sf, _dr, _af = crown_dep_source
    mod = importlib.import_module(src_mod)
    assert mod is not None


def test_crown_dep_source_function_is_dlt_source(
    crown_dep_source: tuple[str, str, str, str, str, str, str],
):
    """The *_<...>_source factory must return a dlt source with the expected resource."""
    _domain, _nation, src_mod, _am, src_fn, dlt_resource, _af = crown_dep_source
    mod = importlib.import_module(src_mod)
    fn: Callable[..., Any] = getattr(mod, src_fn)
    src = fn(max_pages=1)
    # dlt sources are containers of resources; verify the resource exists.
    assert dlt_resource in src.resources, (
        f"{src_fn}() is missing dlt resource {dlt_resource!r}; "
        f"available: {list(src.resources)!r}"
    )


def test_crown_dep_source_resource_metadata(
    crown_dep_source: tuple[str, str, str, str, str, str, str],
):
    """The dlt resource must declare primary_key=url + write_disposition=merge."""
    _domain, _nation, src_mod, _am, src_fn, dlt_resource, _af = crown_dep_source
    mod = importlib.import_module(src_mod)
    fn = getattr(mod, src_fn)
    src = fn(max_pages=1)
    res = src.resources[dlt_resource]
    # dlt exposes write_disposition as a stringly typed attribute.
    assert getattr(res, "write_disposition", None) == "merge", (
        f"{src_fn}/{dlt_resource} expected write_disposition='merge', "
        f"got {getattr(res, 'write_disposition', None)!r}"
    )
    # In dlt 1.x, primary_key lives on the resource hints, not as a public attr.
    primary_key = res._hints.get("primary_key")
    assert primary_key == ["url"], (
        f"{src_fn}/{dlt_resource} expected primary_key=['url'], "
        f"got {primary_key!r}"
    )


def test_crown_dep_asset_module_imports(crown_dep_source):
    """The dagster asset module must import without error."""
    _domain, _nation, _sm, asset_mod, _sf, _dr, _af = crown_dep_source
    mod = importlib.import_module(asset_mod)
    assert mod is not None


def test_crown_dep_asset_function_present(crown_dep_source):
    """The dagster asset function must exist on the module."""
    _domain, _nation, _sm, asset_mod, _sf, _dr, asset_fn = crown_dep_source
    mod = importlib.import_module(asset_mod)
    assert hasattr(mod, asset_fn), (
        f"{asset_mod} missing expected dagster asset function {asset_fn!r}"
    )


def test_crown_dep_in_global_definitions(crown_dep_source):
    """The asset must be wired into the global Dagster Definitions object."""
    from dagster_defs.definitions import combined_assets  # type: ignore[import-not-found]

    _domain, _nation, _sm, _am, _sf, _dr, asset_fn = crown_dep_source
    # Dagster 1.12.6: combined_assets is a list[AssetsDefinition].
    # The asset key is "medicine_iom_health_social_care" (function name) and
    # lives at a.asset_and_check_keys[*].to_user_string() with underscores.
    asset_user_strings = set()
    for adef in combined_assets:
        if hasattr(adef, "asset_and_check_keys"):
            for k in adef.asset_and_check_keys:
                if hasattr(k, "to_user_string"):
                    asset_user_strings.add(k.to_user_string())
    assert asset_fn in asset_user_strings, (
        f"Asset {asset_fn!r} not registered in dagster_defs.definitions.combined_assets. "
        f"Known assets: {sorted(asset_user_strings)[:20]!r}..."
    )
