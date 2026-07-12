"""Academic History Manifest — portable bring-your-own-academic-history.

A Pydantic v2 model + a YAML loader that lets any user (including the
author, but also any collaborator) point the academic-history
pipeline at their own notes / assignments / exam_papers / answers /
worked_solutions / feedback folders and produce the same typed
artefacts + marimo notebooks + agent surface as the UoG
math/statistics case study.

Companion to
`openspec/changes/2026-07-11-uog-math-statistics-academic-history-v1/templates/academic_history_manifest.example.yaml`.

This module is intentionally dependency-light: Pydantic v2 + PyYAML.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, field_validator


class ModuleRoot(BaseModel):
    """One module that the academic-history pipeline should ingest."""

    path: str = Field(..., description="Path to the module folder")
    module_code: str = Field(..., description="Module code, e.g. 'ST311'")
    module_title: str | None = Field(None, description="Module title")
    institution: str | None = Field(None, description="Awarding institution")
    academic_year: str | None = Field(None, description="Academic year, e.g. '2024-25'")


class ArtifactRoots(BaseModel):
    """Optional separate roots for assignments / exam papers / answers."""

    assignments: str | None = None
    exam_papers: str | None = None
    answers: str | None = None
    worked_solutions: str | None = None
    feedback: str | None = None


class Privacy(BaseModel):
    """Privacy gate for the academic-history pipeline.

    Defaults to `include_identity_records=False`. Identity folders
    MUST be opt-in only.
    """

    include_identity_records: bool = False
    include_answer_scripts: bool = True
    include_feedback: bool = True
    pseudonym_salt_env: str = "ACADEMIC_HISTORY_PSEUDONYM_SALT"

    @field_validator("include_identity_records")
    @classmethod
    def _warn_on_identity_true(cls, v: bool) -> bool:
        """Identity-record inclusion must be a deliberate choice.

        We do NOT raise here because the user may legitimately want to
        include identity records (e.g. for personal academic record).
        Dagster run-log warnings are emitted by the asset itself.
        """
        return v


class PrivacyOverrides(BaseModel):
    skip_patterns: list[str] = Field(default_factory=list)


class StudentProfile(BaseModel):
    pseudonym: str = Field(..., min_length=1, description="Stable pseudonym (no PII)")
    institution: str | None = None
    programme: str | None = None
    years: list[str] = Field(default_factory=list)


class AcademicHistoryManifest(BaseModel):
    """Top-level manifest model.

    Mirrors the YAML structure documented in
    `templates/academic_history_manifest.example.yaml`.
    """

    student_profile: StudentProfile
    module_roots: list[ModuleRoot] = Field(default_factory=list)
    artifact_roots: ArtifactRoots = Field(default_factory=ArtifactRoots)
    official_module_descriptors: str | None = None
    privacy: Privacy = Field(default_factory=Privacy)
    privacy_overrides: PrivacyOverrides = Field(default_factory=PrivacyOverrides)

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    @property
    def base_path(self) -> Path:
        """Where to resolve relative paths.

        Honours `ACADEMIC_HISTORY_BASE_PATH` (overridable per deployment)
        and falls back to the current working directory.
        """
        return Path(os.environ.get("ACADEMIC_HISTORY_BASE_PATH", "."))

    def resolve_path(self, rel: str) -> Path:
        """Resolve a relative path against `base_path`."""
        p = Path(rel)
        if p.is_absolute():
            return p
        return (self.base_path / p).resolve()

    def resolve_all_paths(self) -> dict[str, Path]:
        """Resolve every path in the manifest.

        Returns a dict with keys: module_roots[*], artifact_roots.*,
        official_module_descriptors.
        """
        resolved: dict[str, Any] = {
            "module_roots": [
                {**r.model_dump(), "resolved_path": self.resolve_path(r.path)}
                for r in self.module_roots
            ],
            "artifact_roots": {
                k: self.resolve_path(v) if v else None
                for k, v in self.artifact_roots.model_dump().items()
            },
            "official_module_descriptors": (
                self.resolve_path(self.official_module_descriptors)
                if self.official_module_descriptors
                else None
            ),
        }
        return resolved

    def pseudonym_hash(self) -> str:
        """Return a SHA-256 hash of (pseudonym + salt) — never PII."""
        import hashlib

        salt = os.environ.get(self.privacy.pseudonym_salt_env, "default-salt")
        raw = f"{self.student_profile.pseudonym}:{salt}".encode()
        return f"h:{hashlib.sha256(raw).hexdigest()[:32]}"

    def should_skip(self, file_path: str) -> bool:
        """Apply `privacy_overrides.skip_patterns` (Python `re` semantics)."""
        import re as _re

        for pattern in self.privacy_overrides.skip_patterns:
            if _re.search(pattern, file_path):
                return True
        return False

    def include_file(self, file_path: str) -> bool:
        """Apply the privacy gate + skip patterns."""
        if self.should_skip(file_path):
            return False
        return self.privacy.include_identity_records or "identity" not in file_path.lower()


# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------


def load_manifest(path: str | Path) -> AcademicHistoryManifest:
    """Load an `AcademicHistoryManifest` from a YAML file."""
    text = Path(path).read_text(encoding="utf-8")
    return AcademicHistoryManifest(**yaml.safe_load(text))


def dump_manifest(manifest: AcademicHistoryManifest) -> str:
    """Dump an `AcademicHistoryManifest` to YAML."""
    return str(
        yaml.safe_dump(manifest.model_dump(), sort_keys=False, allow_unicode=True)
    )


__all__ = [
    "AcademicHistoryManifest",
    "ArtifactRoots",
    "ModuleRoot",
    "Privacy",
    "PrivacyOverrides",
    "StudentProfile",
    "dump_manifest",
    "load_manifest",
]
