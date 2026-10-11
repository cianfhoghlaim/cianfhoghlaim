"""baml_src/_shared/__init__.py
BAML shared extraction patterns + cross-cutting helpers.

This package contains:
  - templates/            : The 18 canonical BAML prompt templates (per the 2026-12-XX-mega-3d-baml-quality-v1 change).
  - dltq_naming.py        : The schema-naming helper (per the 2026-10-30-platform-reset-saga-v1).
  - dltq_naming_legacy.py : The 6-month deprecation shim for the 3 historical naming conventions.
"""
from .dltq_naming import (
    DUCKLAKE_NAMESPACE,
    QUADRANTS,
    to_dlq_cognee_dataset,
    to_dlq_lance_table,
    to_dlq_table_name,
)
from .dltq_naming_legacy import legacy_to_dlq_table_name

__all__ = [
    "DUCKLAKE_NAMESPACE",
    "QUADRANTS",
    "legacy_to_dlq_table_name",
    "to_dlq_cognee_dataset",
    "to_dlq_lance_table",
    "to_dlq_table_name",
]
