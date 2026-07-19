"""Subjects manifest lookup — Cianfhoghlaim Oideachais.

Reads the bilingual JSON manifests (stages.json, lc_subjects.json,
hei.json) and exposes a typed lookup API used by the BAML context loaders,
the DLT source router, and the SPA's route metadata.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

MANIFEST_DIR = Path(__file__).parent


@lru_cache(maxsize=1)
def _load_stages() -> dict[str, Any]:
    with open(MANIFEST_DIR / "stages.json") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def _load_lc_subjects() -> dict[str, Any]:
    with open(MANIFEST_DIR / "lc_subjects.json") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def _load_hei() -> dict[str, Any]:
    with open(MANIFEST_DIR / "hei.json") as f:
        return json.load(f)


def lookup(stage: str, subject: str | None = None) -> dict[str, Any]:
    """Look up a stage (and optionally a subject) in the manifest.

    Returns a dict with at least `name_en`, `name_ga`, `slug`, `ga_slug`,
    `baml_file`, `dagster_asset`, `cognee_dataset`, `lancedb_table`,
    `agent_team`, `primary_components`, `primary_route_en`, `primary_route_ga`.
    """
    for s in _load_stages()["stages"]:
        if s["slug"] == stage:
            if subject is None:
                return s
            for ls in _load_lc_subjects()["subjects"]:
                if ls["slug"] == subject:
                    return {**s, "subject": ls}
            raise KeyError(f"Subject '{subject}' not found in stage '{stage}'")
    raise KeyError(f"Stage '{stage}' not found in manifest")


def all_stages() -> list[dict[str, Any]]:
    """Return the 5 stages in canonical order: aistear, primary, junior_cycle, senior_cycle, tertiary."""
    return _load_stages()["stages"]


def all_lc_subjects() -> list[dict[str, Any]]:
    """Return the 50+ Leaving Certificate subjects."""
    return _load_lc_subjects()["subjects"]


def all_hei() -> list[dict[str, Any]]:
    """Return the 13 HEIs."""
    return _load_hei()["institutions"]


def all_qqi_awards() -> list[dict[str, Any]]:
    """Return the 8+ QQI FET awards."""
    return _load_hei().get("qqi_awards", [])
