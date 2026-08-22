"""JurisdictionAssetsBase — canonical base class for all jurisdiction-level
Dagster assets.

Per the `centralized-model-registry` capability +
`dagster-5-layer-component-architecture` spec. The 11 jurisdiction-specific
modules in this directory (`england_assets`, `guernsey_assets`,
`ireland_assets`, `jersey_assets`, `scotland_assets`, `wales_assets`,
`northern_ireland_assets`, `isle_of_man_assets`, `sct_wls_ni_assets`,
`crown_dependencies_assets`) are thin subclasses of `JurisdictionAssetsBase`
that emit a single `jurisdiction_documents_ingested` asset backed by the
canonical `jurisdiction_jurisdiction_pipeline`.

This directory complements the legacy per-jurisdiction education files
(`england_education/`, `guernsey_education/`, etc.) which contain the
per-board-specific assets (AQA / OCR / Edexcel / JC / GCSE / A-Level)
that are NOT yet migrated.

Reference: openspec/changes/2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1
"""
