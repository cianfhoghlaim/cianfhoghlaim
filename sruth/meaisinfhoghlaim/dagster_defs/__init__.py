"""meaisínfhoghlaim.dagster_defs — Dagster code-location for the AI/ML quadrant.

Phase 0.2 of lateralise-british-isles-domains. Currently a heartbeat-only
code-location with 4 thin assets that exercise the import path. Real
Dagster+DLT wrappers around the 3 ML pipelines (dialect_classifier,
irish_document_scanner, transcript_aligner) and the 12 agents ship
in a follow-on change.

The `defs = Definitions(...)` instance is what `dg dev` and the
`module_name` in `meaisinfhoghlaim/dg.toml` look for. It uses the
Dagster 1.9+ `load_assets_from_modules` pattern.
"""
from __future__ import annotations

from dagster import Definitions, load_assets_from_modules

from .assets import healthchecks

heartbeat_asset_defs = load_assets_from_modules([healthchecks])

defs = Definitions(assets=heartbeat_asset_defs)
