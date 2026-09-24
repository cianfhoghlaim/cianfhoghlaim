"""cocoindex_flows.british_isles.ireland.education._shared
-- the cianfhoghlaim K-12 CocoIndex factory (College → School → Programme
→ Module → Topic → LO + teacher-centric + student-centric).

Per openspec/changes/2026-09-23-k12-teacher-student-pipeline-v1/.

Mirrors the UoG tertiary factory at
cocoindex_flows/british_isles/ireland/tertiary/uog/_shared.py
(College → School → Programme → Module hierarchy) but for the
4-stage K-12 pipeline (aistear → primary → jc → sc).

The factory emits one CocoIndex v1 App per K-12 entity type from
config YAMLs:
  - _primary_modules.yaml (~50 primary learning outcome areas)
  - _jc_subjects.yaml (18 NCCA JC subjects)
  - _sc_subjects.yaml (40+ NCCA SC subjects + LCA programmes)

R1: import `shared_lifespan` + `LANCE_DB` + `EMBEDDER` from
    `....._shared._lifespan`
R2: declare `app = coco.App(coco.AppConfig(name=...))` at module scope
R3: at least one `@coco.fn(...)` decorator present

Embedder: BAAI/bge-m3 (1024-d, multilingual) per
cocoindex_flows/_shared/_lifespan.py:108.

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
"""
from __future__ import annotations

import hashlib
import os
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


# ============================================================================
# The 4-tier K-12 config
# ============================================================================

@dataclass(frozen=True)
class K12StageSpec:
    """The 5-stage K-12 taxonomy (per british-isles-education-pipeline-v3)."""
    stage_id: str                    # 'aistear' | 'primary' | 'jc' | 'sc' | 'ty' | 'lca'
    display_name: str
    display_name_ga: str
    age_band: str
    age_band_ga: str


K12_STAGES: tuple[K12StageSpec, ...] = (
    K12StageSpec("aistear", "Early Childhood", "Luath-Óige", "0-6", "0-6"),
    K12StageSpec("primary", "Primary", "Bunscoil", "4-12", "4-12"),
    K12StageSpec("jc", "Junior Cycle", "Scoil Mheán", "12-15", "12-15"),
    K12StageSpec("sc", "Senior Cycle", "Scoil Shinsearach", "15-18", "15-18"),
    K12StageSpec("ty", "Transition Year", "Bliain Idirghabhála", "15-17", "15-17"),
    K12StageSpec("lca", "Leaving Cert Applied", "Ardteist Feidhmeach", "16-18", "16-18"),
)


@dataclass(frozen=True)
class K12EntitySpec:
    """A single K-12 entity (programme area, subject, lesson plan, etc.)."""
    entity_id: str
    stage_id: str
    entity_type: str                  # 'primary_area' | 'jc_subject' | 'sc_subject' | 'lesson_plan' | 'class_roster' | 'pro_learning_module' | 'homework' | 'cba' | 'study_plan' | 'wellbeing' | 'exam'
    entity_name_en: str
    entity_name_ga: str | None
    canonical_url: str | None


# ============================================================================
# The factory
# ============================================================================

# CocoIndex is optional — degrade gracefully if not installed.
try:
    import cocoindex as coco  # type: ignore[import-not-found]
    from cocoindex.connectors import lancedb as coco_lancedb  # type: ignore[import-not-found]

    COCOINDEX_AVAILABLE = True
except ImportError:
    COCOINDEX_AVAILABLE = False
    coco = None  # type: ignore[assignment]
    coco_lancedb = None  # type: ignore[assignment]


def create_k12_entity_flow(config: K12EntitySpec) -> Any:
    """Build one CocoIndex v1 App for one K-12 entity.

    Args:
        config: the K12EntitySpec

    Returns: a `coco.App` instance named `k12_<entity_type>_<entity_id>_flow`
    """
    if not COCOINDEX_AVAILABLE or not hasattr(coco, "App"):
        logger.warning("cocoindex_unavailable: cannot create_k12_entity_flow(%s)", config.entity_id)
        return None

    app = coco.App(coco.AppConfig(name=f"k12_{config.entity_type}_{config.entity_id}_flow"))

    @coco.function(
        name=f"k12_{config.entity_type}_{config.entity_id}_process",
    )
    def k12_entity_flow(builder: Any) -> None:
        builder.export(
            "entity_id", config.entity_id,
            "stage_id", config.stage_id,
            "entity_type", config.entity_type,
            "entity_name_en", config.entity_name_en,
            "entity_name_ga", config.entity_name_ga,
            "canonical_url", config.canonical_url,
        )

    return app


# ============================================================================
# Canonical config loaders
# ============================================================================

def load_primary_modules_config() -> list[K12EntitySpec]:
    """Load the 50-row primary factory config from `_primary_modules.yaml`."""
    config_path = Path(__file__).parent.parent / "_shared" / "_primary_modules.yaml"
    if not config_path.exists():
        logger.warning("primary_modules_config_missing: %s", config_path)
        return []
    return _parse_k12_config(config_path, entity_type="primary_area", stage_id="primary")


def load_jc_subjects_config() -> list[K12EntitySpec]:
    """Load the 18-row JC factory config from `_jc_subjects.yaml`."""
    config_path = Path(__file__).parent.parent / "_shared" / "_jc_subjects.yaml"
    if not config_path.exists():
        return []
    return _parse_k12_config(config_path, entity_type="jc_subject", stage_id="jc")


def load_sc_subjects_config() -> list[K12EntitySpec]:
    """Load the 40-row SC factory config from `_sc_subjects.yaml`."""
    config_path = Path(__file__).parent.parent / "_shared" / "_sc_subjects.yaml"
    if not config_path.exists():
        return []
    return _parse_k12_config(config_path, entity_type="sc_subject", stage_id="sc")


def _parse_k12_config(path: Path, *, entity_type: str, stage_id: str) -> list[K12EntitySpec]:
    """Parse a K-12 factory YAML config into a list of K12EntitySpec."""
    try:
        import yaml

        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:
        logger.warning("k12_config_parse_failed: %s: %s", path, exc)
        return []

    out = []
    for row in raw or []:
        out.append(K12EntitySpec(
            entity_id=row.get("entity_id") or row.get("subject_slug") or row.get("area_code"),
            stage_id=stage_id,
            entity_type=entity_type,
            entity_name_en=row.get("entity_name_en") or row.get("name_en") or row.get("subject_name_en"),
            entity_name_ga=row.get("entity_name_ga") or row.get("name_ga"),
            canonical_url=row.get("canonical_url") or row.get("source_url"),
        ))
    return out


def iter_all_k12_entities() -> Iterator[K12EntitySpec]:
    """Yield every K-12 entity across all 3 stage configs."""
    yield from load_primary_modules_config()
    yield from load_jc_subjects_config()
    yield from load_sc_subjects_config()


# ============================================================================
# Stage exports
# ============================================================================

__all__ = [
    "K12StageSpec",
    "K12EntitySpec",
    "K12_STAGES",
    "create_k12_entity_flow",
    "load_primary_modules_config",
    "load_jc_subjects_config",
    "load_sc_subjects_config",
    "iter_all_k12_entities",
]
