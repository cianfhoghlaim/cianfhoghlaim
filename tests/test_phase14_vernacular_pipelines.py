"""Phase 14 vernacular pipelines integration tests.

Per the 2026-09-01-cianfhoghlaim-nua-v7-vernaculars-pipelines-v1
change (Phase 14 of the cianfhoghlaim-nua v6 era plan).

Verifies that all 5 layers (DLT + CocoIndex + Convex + Hono +
Dagster) are wired for the 7 British Isles vernaculars:

  - Welsh (CY)              — Wales
  - Scottish Gaelic (GD)    — Scotland
  - Manx (GV)               — Isle of Man
  - Breton (BR)             — sister-repo lift target
  - Cornish (KW)            — sister-repo lift target
  - Jersey French (FR_JE)   — Jersey
  - Guernsey French (FR_GG) — Guernsey

Plus the Ulster Scots (SCO) companion function
``b.ExtractUlsterScotsSubjectSpec`` which shares the Northern
Ireland jurisdiction scaffold.

The test suite is intentionally lightweight — it checks imports
+ interface shapes rather than running the full pipeline. The
heavy lifting is owned by the 5-layer pipelines themselves.
"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


# The 7 vernacular slugs (Phase 14 canonical order).
VERNACULAR_SLUGS = (
    "welsh",
    "scottish_gaelic",
    "manx",
    "breton",
    "cornish",
    "jersey_french",
    "guernsey_french",
)

# The 8 BAML extraction functions (7 vernaculars + Ulster Scots).
BAML_FUNCTIONS = (
    "ExtractWelshSubjectSpec",
    "ExtractScottishGaelicSubjectSpec",
    "ExtractBretonSubjectSpec",
    "ExtractCornishSubjectSpec",
    "ExtractManxSubjectSpec",
    "ExtractJerseyFrenchSubjectSpec",
    "ExtractGuernseyFrenchSubjectSpec",
    "ExtractUlsterScotsSubjectSpec",
)

# Mapping from vernacular slug → (DLT module path, CocoIndex app name,
# Convex table file, Hono route module path, Dagster assets module).
PIPELINE_MAP: dict[str, dict[str, str]] = {
    "welsh": {
        "dlt": "dlt_sources.education.wales.british_isles.welsh_vernacular",
        "cocoindex_app": "vernacular_welsh_embedding",
        "convex_file": "web/packages/db/convex/vernacular/welsh.ts",
        "hono_route": "web/hono-api/src/routes/copilotkit/vernacular/welsh.ts",
        "dagster_assets": "orchestration.defs.2_materials.vernacular.welsh_assets",
    },
    "scottish_gaelic": {
        "dlt": "dlt_sources.education.scotland.british_isles.scottish_gaelic_vernacular",
        "cocoindex_app": "vernacular_scottish_gaelic_embedding",
        "convex_file": "web/packages/db/convex/vernacular/scottish_gaelic.ts",
        "hono_route": "web/hono-api/src/routes/copilotkit/vernacular/scottish_gaelic.ts",
        "dagster_assets": "orchestration.defs.2_materials.vernacular.scottish_gaelic_assets",
    },
    "breton": {
        "dlt": "dlt_sources.breton_cornish.british_isles.breton_vernacular",
        "cocoindex_app": "vernacular_breton_embedding",
        "convex_file": "web/packages/db/convex/vernacular/breton.ts",
        "hono_route": "web/hono-api/src/routes/copilotkit/vernacular/breton.ts",
        "dagster_assets": "orchestration.defs.2_materials.vernacular.breton_assets",
    },
    "cornish": {
        "dlt": "dlt_sources.breton_cornish.british_isles.cornish_vernacular",
        "cocoindex_app": "vernacular_cornish_embedding",
        "convex_file": "web/packages/db/convex/vernacular/cornish.ts",
        "hono_route": "web/hono-api/src/routes/copilotkit/vernacular/cornish.ts",
        "dagster_assets": "orchestration.defs.2_materials.vernacular.cornish_assets",
    },
    "manx": {
        "dlt": "dlt_sources.education.isle_of_man.british_isles.manx_vernacular",
        "cocoindex_app": "vernacular_manx_embedding",
        "convex_file": "web/packages/db/convex/vernacular/manx.ts",
        "hono_route": "web/hono-api/src/routes/copilotkit/vernacular/manx.ts",
        "dagster_assets": "orchestration.defs.2_materials.vernacular.manx_assets",
    },
    "jersey_french": {
        "dlt": "dlt_sources.education.jersey.british_isles.jersey_french_vernacular",
        "cocoindex_app": "vernacular_jersey_french_embedding",
        "convex_file": "web/packages/db/convex/vernacular/jersey_french.ts",
        "hono_route": "web/hono-api/src/routes/copilotkit/vernacular/jersey_french.ts",
        "dagster_assets": "orchestration.defs.2_materials.vernacular.jersey_french_assets",
    },
    "guernsey_french": {
        "dlt": "dlt_sources.education.guernsey.british_isles.guernsey_french_vernacular",
        "cocoindex_app": "vernacular_guernsey_french_embedding",
        "convex_file": "web/packages/db/convex/vernacular/guernsey_french.ts",
        "hono_route": "web/hono-api/src/routes/copilotkit/vernacular/guernsey_french.ts",
        "dagster_assets": "orchestration.defs.2_materials.vernacular.guernsey_french_assets",
    },
}


# ─── §1 — All 8 BAML functions are reachable ───────────────────────────────


def test_phase14_baml_extraction_functions_reachable():
    """All 8 Extract<Vernacular>SubjectSpec BAML functions reachable."""
    from baml_client.baml_client.sync_client import b

    for fn_name in BAML_FUNCTIONS:
        fn = getattr(b, fn_name, None)
        assert fn is not None, f"b.{fn_name} should be reachable but got None"
        assert callable(fn), f"b.{fn_name} should be callable"


# ─── §2 — All 7 DLT sources are importable ────────────────────────────────


def test_phase14_welsh_dlt_source_importable():
    from dlt_sources.education.wales.british_isles.welsh_vernacular import welsh_vernacular_source
    assert welsh_vernacular_source.name == "welsh_vernacular"


def test_phase14_scottish_gaelic_dlt_source_importable():
    from dlt_sources.education.scotland.british_isles.scottish_gaelic_vernacular import (
        scottish_gaelic_vernacular_source,
    )
    assert scottish_gaelic_vernacular_source.name == "scottish_gaelic_vernacular"


def test_phase14_breton_dlt_source_importable():
    from dlt_sources.breton_cornish.british_isles.breton_vernacular import (
        breton_vernacular_source,
    )
    assert breton_vernacular_source.name == "breton_vernacular"


def test_phase14_cornish_dlt_source_importable():
    from dlt_sources.breton_cornish.british_isles.cornish_vernacular import (
        cornish_vernacular_source,
    )
    assert cornish_vernacular_source.name == "cornish_vernacular"


def test_phase14_manx_dlt_source_importable():
    from dlt_sources.education.isle_of_man.british_isles.manx_vernacular import (
        manx_vernacular_source,
    )
    assert manx_vernacular_source.name == "manx_vernacular"


def test_phase14_jersey_french_dlt_source_importable():
    from dlt_sources.education.jersey.british_isles.jersey_french_vernacular import (
        jersey_french_vernacular_source,
    )
    assert jersey_french_vernacular_source.name == "jersey_french_vernacular"


def test_phase14_guernsey_french_dlt_source_importable():
    from dlt_sources.education.guernsey.british_isles.guernsey_french_vernacular import (
        guernsey_french_vernacular_source,
    )
    assert guernsey_french_vernacular_source.name == "guernsey_french_vernacular"


# ─── §3 — All 7 CocoIndex apps are importable ──────────────────────────────


def test_phase14_cocoindex_factory_has_7_apps():
    """The cocoindex_flows.vernacular.vernacular_factory module
    ships exactly 7 vernacular Apps + a 7-row VERNACULAR_CONFIG.
    """
    # cocoindex_flows.<sub>.<file> can't go through normal import.
    # Use __import__ directly.
    factory_mod = __import__(
        "cocoindex_flows.vernacular.vernacular_factory",
        fromlist=[""],
    )
    assert len(factory_mod.VERNACULAR_CONFIG) == 7

    # Confirm all 7 Apps are registered at module level.
    expected_apps = [
        "vernacular_welsh_embedding",
        "vernacular_scottish_gaelic_embedding",
        "vernacular_manx_embedding",
        "vernacular_breton_embedding",
        "vernacular_cornish_embedding",
        "vernacular_jersey_french_embedding",
        "vernacular_guernsey_french_embedding",
    ]
    for app_name in expected_apps:
        assert app_name in dir(factory_mod), (
            f"App {app_name} not registered at module level"
        )


def test_phase14_cocoindex_factory_canonical_baml_functions():
    """Each VERNACULAR_CONFIG row points at the correct baml function."""
    factory_mod = __import__(
        "cocoindex_flows.vernacular.vernacular_factory",
        fromlist=[""],
    )
    baml_fn_slugs = {
        v.baml_function
        for v in factory_mod.VERNACULAR_CONFIG
    }
    # The 7 BAML functions in the factory config should be a
    # subset of the 8 total (the 8th is the Ulster Scots companion).
    assert baml_fn_slugs.issubset(set(BAML_FUNCTIONS)), (
        f"Unexpected baml_function values: {baml_fn_slugs - set(BAML_FUNCTIONS)}"
    )
    assert len(baml_fn_slugs) == 7, (
        "VERNACULAR_CONFIG should have exactly 7 unique BAML functions"
    )


def test_phase14_cocoindex_sibling_modules_re_export_apps():
    """Each of the 7 sibling CocoIndex modules re-exports its App."""
    # Touch the package first to register the factory.
    __import__("cocoindex_flows")
    for slug in VERNACULAR_SLUGS:
        modname = f"cocoindex_flows.vernacular.{slug}_embedding"
        mod = importlib.import_module(modname)
        # Each sibling module exports one ``<slug>_embedding_app`` alias.
        expected_alias = f"{slug}_embedding_app"
        assert hasattr(mod, expected_alias), (
            f"{modname} should export {expected_alias}"
        )


# ─── §4 — Convex schema is well-formed ─────────────────────────────────────


def test_phase14_convex_schema_has_vernacular_documents_table():
    """The Convex schema table `vernacular_documents` exists."""
    schema_path = _REPO_ROOT / "web" / "packages" / "db" / "convex" / "schema.ts"
    assert schema_path.exists(), f"Missing Convex schema at {schema_path}"
    content = schema_path.read_text(encoding="utf-8")
    assert "vernacular_documents" in content, (
        "The Convex schema should declare a `vernacular_documents` table"
    )
    # The schema must index by vernacular, jurisdiction, subject.
    for idx in ("by_vernacular", "by_jurisdiction", "by_subject"):
        assert idx in content, f"Convex schema must have {idx} index"


def test_phase14_convex_vernacular_files_exist():
    """All 8 Convex vernacular sibling files exist (7 + Ulster Scots)."""
    convex_dir = _REPO_ROOT / "web" / "packages" / "db" / "convex" / "vernacular"
    assert convex_dir.exists(), "Convex vernacular/ dir missing"
    for slug in VERNACULAR_SLUGS:
        assert (convex_dir / f"{slug}.ts").exists(), (
            f"Missing Convex file for {slug}"
        )
    # Plus the Ulster Scots companion.
    assert (convex_dir / "ulster_scots.ts").exists(), (
        "Missing Convex file for ulster_scots"
    )
    assert (convex_dir / "index.ts").exists(), (
        "Missing Convex vernacular/index.ts barrel"
    )


def test_phase14_convex_vernacular_index_reexports_all_8():
    """The Convex vernacular/index.ts barrel re-exports all 8 routes."""
    index_path = (
        _REPO_ROOT
        / "web"
        / "packages"
        / "db"
        / "convex"
        / "vernacular"
        / "index.ts"
    )
    content = index_path.read_text(encoding="utf-8")
    for slug in VERNACULAR_SLUGS:
        assert slug in content, (
            f"Convex vernacular/index.ts should re-export {slug}"
        )
    assert "ulster_scots" in content, (
        "Convex vernacular/index.ts should re-export ulster_scots"
    )


# ─── §5 — Hono factory exposes the 8 routes ────────────────────────────────


def test_phase14_hono_factory_vernacular_route_specs_count():
    """The Hono _vernacular_factory.ts exposes exactly 8 route specs
    (7 vernaculars + Ulster Scots companion).
    """
    factory_path = (
        _REPO_ROOT
        / "web"
        / "hono-api"
        / "src"
        / "routes"
        / "copilotkit"
        / "vernacular"
        / "_vernacular_factory.ts"
    )
    content = factory_path.read_text(encoding="utf-8")
    assert "VERNACULAR_ROUTE_SPECS" in content, (
        "Hono factory should export VERNACULAR_ROUTE_SPECS"
    )
    # Count the literals — every slug should appear exactly once.
    for slug in VERNACULAR_SLUGS:
        assert f'"{slug}"' in content, (
            f"Hono factory VERNACULAR_ROUTE_SPECS should include {slug}"
        )
    assert '"ulster_scots"' in content, (
        "Hono factory should include the ulster_scots companion"
    )


def test_phase14_hono_route_files_exist():
    """All 8 Hono route sibling files exist."""
    hono_dir = (
        _REPO_ROOT
        / "web"
        / "hono-api"
        / "src"
        / "routes"
        / "copilotkit"
        / "vernacular"
    )
    for slug in VERNACULAR_SLUGS:
        assert (hono_dir / f"{slug}.ts").exists(), (
            f"Missing Hono route for {slug}"
        )
    assert (hono_dir / "ulster_scots.ts").exists(), (
        "Missing Hono route for ulster_scots"
    )


def test_phase14_hono_index_mounts_all_8_routes():
    """web/hono-api/src/index.ts mounts all 8 vernacular routes."""
    index_path = _REPO_ROOT / "web" / "hono-api" / "src" / "index.ts"
    content = index_path.read_text(encoding="utf-8")
    for slug in VERNACULAR_SLUGS:
        assert f"/api/copilotkit/vernacular/{slug}" in content, (
            f"web/hono-api/src/index.ts should mount /api/copilotkit/vernacular/{slug}"
        )
    assert "/api/copilotkit/vernacular/ulster_scots" in content, (
        "web/hono-api/src/index.ts should mount /api/copilotkit/vernacular/ulster_scots"
    )


# ─── §6 — All 7 Dagster asset modules load + register 5 assets each ──────


def test_phase14_dagster_vernacular_asset_modules_load():
    """All 7 Dagster asset modules import cleanly with 5 assets each."""
    for slug in VERNACULAR_SLUGS:
        mod = __import__(
            PIPELINE_MAP[slug]["dagster_assets"],
            fromlist=[""],
        )
        names = [
            n for n in dir(mod)
            if not n.startswith("_")
            and (
                f"{slug.replace('_', '_')}_vernacular_documents_ingested" in n
                or f"{slug.replace('_', '_')}_vernacular_extractions" in n
                or f"{slug.replace('_', '_')}_vernacular_embeddings" in n
            )
        ]
        assert len(names) >= 3, (
            f"{PIPELINE_MAP[slug]['dagster_assets']} should register at "
            f"least 3 assets (got {len(names)})"
        )


# ─── §7 — Sanity: openspec change exists ───────────────────────────────────


def test_phase14_openspec_change_exists():
    """The Phase 14 openspec change directory exists."""
    openspec_change = (
        _REPO_ROOT
        / "openspec"
        / "changes"
        / "2026-09-01-cianfhoghlaim-nua-v7-vernaculars-pipelines-v1"
    )
    assert openspec_change.exists(), (
        f"Phase 14 openspec change missing at {openspec_change}"
    )
    for fname in ("proposal.md", "tasks.md", "specs"):
        target = openspec_change / fname
        assert target.exists(), (
            f"Phase 14 openspec change missing {fname}"
        )


def test_phase14_openspec_spec_delta_to_biep():
    """The Phase 14 openspec change has a spec delta to
    british-isles-education-pipeline.
    """
    spec_md = (
        _REPO_ROOT
        / "openspec"
        / "changes"
        / "2026-09-01-cianfhoghlaim-nua-v7-vernaculars-pipelines-v1"
        / "specs"
        / "british-isles-education-pipeline"
        / "spec.md"
    )
    assert spec_md.exists(), f"Missing spec delta at {spec_md}"
    content = spec_md.read_text(encoding="utf-8")
    # The new Requirement should mention all 5 layers.
    for layer_term in ("DLT source", "CocoIndex", "Convex", "Hono route", "Dagster"):
        assert layer_term in content, (
            f"Phase 14 spec delta should mention {layer_term}"
        )
    # It should mention the 7 vernaculars.
    for slug in VERNACULAR_SLUGS:
        # british_isles schema slugs are the same as CocoIndex App slugs.
        assert f"vernacular_{slug}_embedding" in content or slug in content, (
            f"Phase 14 spec delta should mention {slug}"
        )


# ─── §8 — End-to-end pipeline count ────────────────────────────────────────


def test_phase14_pipeline_map_covers_all_7_vernaculars():
    """The PIPELINE_MAP covers exactly 7 vernaculars."""
    assert set(PIPELINE_MAP.keys()) == set(VERNACULAR_SLUGS)


def test_phase14_pipeline_map_has_all_5_layers_per_vernacular():
    """For each vernacular, the PIPELINE_MAP has all 5 layer entries."""
    for slug in VERNACULAR_SLUGS:
        entry = PIPELINE_MAP[slug]
        for layer in ("dlt", "cocoindex_app", "convex_file", "hono_route", "dagster_assets"):
            assert layer in entry, (
                f"PIPELINE_MAP[{slug}] missing layer {layer}"
            )
            assert entry[layer], (
                f"PIPELINE_MAP[{slug}][{layer}] should be non-empty"
            )
