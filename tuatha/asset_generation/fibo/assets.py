"""tuatha/asset_generation/fibo/assets.py — Dagster assets for FIBO educational image generation.

Per the 2026-10-04-fibo-asset-pipeline-v1 saga change (Plan 4 of
openspec/plans/2026-10-01-convergence-saga-v1.md).

Assets for generating educational visual assets:
- fibo_json_configs: Generate FIBO JSON from curriculum concepts
- generated_images: Generate images from FIBO JSON configs
- fibo_configs_from_syllabus_diagrams: Generate FIBO JSON from REAL
  extracted SyllabusDiagram records (see its own docstring below)

Each asset is wired into the FIBO 5-stage pipeline:
1. fibo_json_configs produces FiboConfig records (from CurriculumConcept inputs)
2. generated_images consumes FiboConfig + uses the FiboResource + ValidationResource
   to render + iterate up to max_refinement_iterations
3. fibo_configs_from_syllabus_diagrams produces FiboConfig records from REAL
   BAML-extracted SyllabusDiagram records (the docs-informed alternative to
   fibo_json_configs' sample-concept fallback)
"""
from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, UTC
from pathlib import Path
from dataclasses import dataclass
from typing import Any

from dagster import (
    AssetExecutionContext,
    Config,
    MaterializeResult,
    MetadataValue,
    asset,
)

from . import schemas
from .resources import FiboResource, ValidationResource


# The canonical repo root for FIBO output paths
REPO_ROOT_FOR_FIBO = Path(__file__).resolve().parents[3]  # tuatha/asset_generation/fibo → repo
LEAVING_CERT_ROOT_FOR_FIBO = REPO_ROOT_FOR_FIBO / "leaving_certificate"


# The syllabus-keyword list (used by fibo_configs_from_syllabus_diagrams to
# match the right canonical syllabus PDF for each subject). Per the
# NCCA Leaving Certificate syllabus structure (5 subjects in scope).
_SYLLABUS_KEYWORDS_FOR_FIBO = {
    "mathematics": ["lc-maths", "mathematics-lc", "lc-mathematics"],
    "applied_mathematics": ["applied-mathematics-lc", "lc-app-maths"],
    "chemistry": ["lc-chemistry", "chemistry-lc"],
    "geography": ["lc-geography", "geography-lc"],
    "history": ["lc-history", "history-lc"],
    "english": ["lc-english", "english-lc"],
    "gaeilge": ["lc-gaeilge", "gaeilge-lc"],
    "computer_science": ["lc-compsci", "computer-science-lc"],
}


@dataclass
class GenerationConfig:
    """The runtime config for fibo_json_configs + generated_images."""
    sample_concept: str = (
        "The Pythagorean theorem is a foundational result in Euclidean geometry "
        "that relates the three sides of a right-angled triangle. For a triangle "
        "with sides a (adjacent), b (opposite), and c (hypotenuse), a^2 + b^2 = c^2."
    )
    subject: str = "mathematics"
    language: str = "en"


@asset(
    group_name="fibo",
    description="Generate FIBO JSON configurations for curriculum concepts",
    compute_kind="python",
)
def fibo_json_configs(
    ctx: AssetExecutionContext,
    fibo_resource: FiboResource,
) -> MaterializeResult:
    """Generate FIBO JSON configs for the 8 NCCA Leaving Certificate subjects.

    Reads the subject + language from a sample concept (the canonical
    Pythagorean theorem for mathematics; iterates through all 8 subjects
    in the offline dev mode). Looks up the canonical FIBO prompt template
    (per education_fibo.py) + produces a typed FiboConfig record per subject.
    """
    from .education_fibo import get_fibo_prompt

    # The offline dev mode iterates through all 8 subjects (in production,
    # this is parameterised via the Dagster launch config).
    subjects = list_subjects()
    generated_paths = []

    for subject in subjects:
        language = "en"
        try:
            prompt_data = get_fibo_prompt(subject, language)
        except KeyError:
            ctx.log.warning(f"Subject {subject!r} not in canonical 8 NCCA subjects; using mathematics fallback")
            prompt_data = get_fibo_prompt("mathematics", language)

        # Build a FiboConfig record from the prompt template
        config_id = str(uuid.uuid4())
        prompt = prompt_data["prompt"]
        palette_hex = ["#1a0e1a", "#d4af37", "#f0e6d2", "#3a4f8c"]
        fibo_config = schemas.FiboConfig(
            config_id=config_id,
            concept_id=str(uuid.uuid4()),
            language=language,
            prompt=prompt,
            palette_hex=palette_hex,
            iconography=[
                prompt_data["tuatha_de_deity"],
                prompt_data["tuatha_de_treasure"],
                prompt_data["game_ui_inspiration"],
            ],
            validation_criteria=[
                "uses the palette_hex correctly",
                "Tuatha Dé deity is recognisable",
                f"subject = {subject} (NCCA syllabus match)",
                "no text overflow",
            ],
            max_refinement_iterations=3,
            metadata={
                "baml_color": prompt_data["baml_color"],
                "subject": subject,
                "language": language,
            },
        )

        # Write the FIBO JSON config to disk (the canonical surface)
        out_dir = REPO_ROOT_FOR_FIBO / "stedding" / "fibo" / subject / language
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{config_id}.fibo.json"
        out_path.write_text(json.dumps({
            "config_id": fibo_config.config_id,
            "concept_id": fibo_config.concept_id,
            "language": fibo_config.language,
            "prompt": fibo_config.prompt,
            "palette_hex": fibo_config.palette_hex,
            "iconography": fibo_config.iconography,
            "width": fibo_config.width,
            "height": fibo_config.height,
            "validation_criteria": fibo_config.validation_criteria,
            "max_refinement_iterations": fibo_config.max_refinement_iterations,
            "metadata": fibo_config.metadata,
            "created_at": fibo_config.created_at.isoformat(),
        }, indent=2))
        generated_paths.append(str(out_path))

    return MaterializeResult(
        metadata={
            "configs_generated": MetadataValue.int(len(generated_paths)),
            "subjects_processed": MetadataValue.int(len(subjects)),
            "subject": MetadataValue.text(", ".join(subjects)),
        }
    )
    return MaterializeResult(
        metadata={
            "configs_generated": MetadataValue.int(len(generated_paths)),
            "subjects_processed": MetadataValue.int(len(subjects)),
            "subject": MetadataValue.text(", ".join(subjects)),
        }
    )


@asset(
    group_name="fibo",
    deps=["fibo_json_configs"],
    description="Generate educational images from FIBO configurations",
    compute_kind="python",
)
def generated_images(
    ctx: AssetExecutionContext,
    fibo_resource: FiboResource,
    validation_resource: ValidationResource,
) -> MaterializeResult:
    """Generate images from the FIBO JSON configs produced by fibo_json_configs.

    Iterates up to max_refinement_iterations: renders, validates via
    the VLM, and re-renders if the score is below the threshold.
    """
    from .schemas import GeneratedAsset

    # Offline dev mode: iterate through all 8 subjects
    subjects = list_subjects()
    language = "en"

    # Discover the latest FIBO config for each subject/language
    all_generated = []
    for subject in subjects:
        configs_dir = REPO_ROOT_FOR_FIBO / "stedding" / "fibo" / subject / language
        if not configs_dir.exists():
            # No configs yet → produce a default placeholder
            configs_dir.mkdir(parents=True, exist_ok=True)
            config_id = str(uuid.uuid4())
            config_path = configs_dir / f"{config_id}.fibo.json"
            config_path.write_text(json.dumps({
                "config_id": config_id,
                "concept_id": str(uuid.uuid4()),
                "language": language,
                "prompt": f"FIBO placeholder for {subject} ({language})",
                "palette_hex": ["#1a0e1a", "#d4af37"],
                "iconography": [],
                "width": 1024,
                "height": 1024,
                "validation_criteria": [],
                "max_refinement_iterations": 3,
                "metadata": {"subject": subject, "language": language},
                "created_at": datetime.now(UTC).isoformat(),
            }, indent=2))

        config_paths = sorted(configs_dir.glob("*.fibo.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not config_paths:
            continue
        latest_config_path = config_paths[0]
        fibo_config_dict = json.loads(latest_config_path.read_text())
        fibo_config = schemas.FiboConfig(**fibo_config_dict)

        # Render + validate (up to max_refinement_iterations)
        best_asset: GeneratedAsset | None = None
        best_score = 0.0

        out_dir = REPO_ROOT_FOR_FIBO / "stedding" / "fibo_assets" / subject / language
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{fibo_config.config_id}.png"

        for iteration in range(1, fibo_config.max_refinement_iterations + 1):
            result = fibo_resource.render(
                prompt=f"{fibo_config.prompt}\n\nPalette: {' '.join(fibo_config.palette_hex)}",
                palette_hex=fibo_config.palette_hex,
                width=fibo_config.width,
                height=fibo_config.height,
                out_path=str(out_path),
            )

            # Validate with the VLM
            validation = validation_resource.validate(
                asset_path=str(out_path),
                criteria=fibo_config.validation_criteria,
                reference_text=fibo_config_dict.get("metadata", {}).get("concept"),
            )

            score = validation.get("score", 0.0)
            if score > best_score:
                best_score = score
                best_asset = GeneratedAsset(
                    asset_id=result["asset_id"],
                    concept_id=fibo_config.concept_id,
                    subject=subject,
                    language=language,
                    path=result["path"],
                    url=result.get("url"),
                    sha256=result.get("sha256", ""),
                    width=result["width"],
                    height=result["height"],
                    palette_hex=result.get("palette_hex", []),
                    iteration=iteration,
                    validation_score=score,
                    fibo_config_id=fibo_config.config_id,
                )

            # If we pass the threshold, break early
            if validation.get("pass", False):
                break

            if best_asset is not None:
                all_generated.append(best_asset)

    if not all_generated:
        return MaterializeResult(
            metadata={"status": MetadataValue.text("render_failed_all_subjects")}
        )

    return MaterializeResult(
        metadata={
            "assets_generated": MetadataValue.int(len(all_generated)),
            "subjects_processed": MetadataValue.int(len(subjects)),
            "avg_score": MetadataValue.float(sum(a.validation_score for a in all_generated) / len(all_generated)),
        }
    )


def _find_english_syllabus_pdf(subject: str) -> Path | None:
    """Find the English-medium syllabus PDF for the given subject.

    Searches `leaving_certificate/<subject>/*.pdf` for files matching
    the syllabus-keyword list for the subject.

    Args:
        subject: One of the 8 NCCA subjects

    Returns:
        Path to the syllabus PDF (the first match), or None if not found.
    """
    if subject not in _SYLLABUS_KEYWORDS_FOR_FIBO:
        return None
    subject_dir = LEAVING_CERT_ROOT_FOR_FIBO / subject
    if not subject_dir.exists():
        return None
    keywords = _SYLLABUS_KEYWORDS_FOR_FIBO[subject]
    for kw in keywords:
        matches = list(subject_dir.glob(f"*{kw}*.pdf"))
        if matches:
            return matches[0]
    # Fallback: any pdf in the subject dir
    pdfs = sorted(subject_dir.glob("*.pdf"))
    return pdfs[0] if pdfs else None


# Regex to extract a date suffix like _2024-05 or _2024-05-01 from a filename
_DATE_SUFFIX_RE_FOR_FIBO = re.compile(r"_\d{4}-\d{2}(?=\.pdf$)")


# (The original SyllabusDiagramGenerationConfig dataclass was removed
# when the asset signature was simplified — the runtime config is now
# implicit via the offline dev mode constants.)


@asset(
    group_name="fibo",
    description=(
        "Generate FIBO JSON configs from REAL extracted SyllabusDiagram records "
        "(the docs-informed alternative to fibo_json_configs' sample-concept fallback)"
    ),
    compute_kind="python",
)
def fibo_configs_from_syllabus_diagrams(
    ctx: AssetExecutionContext,
    fibo_resource: FiboResource,
) -> MaterializeResult:
    """Generate FIBO configs from REAL BAML-extracted SyllabusDiagram records.

    For each of the 8 NCCA subjects:
    1. Locate the English-medium syllabus PDF
    2. (Future) Run BAML ExtractSyllabusDiagram to extract typed
       SyllabusDiagram records (currently returns 0 records when BAML
       client isn't generated — falls back to the sample-concept path)
    3. For each diagram, produce a FiboConfig record (the docs-informed
       alternative to fibo_json_configs' sample-concept path)
    """
    from .education_fibo import get_fibo_prompt

    # Future: replace with b.GenerateSyllabusDiagrams(pdf_text, pdf_images)
    # when BAML client is generated. For now, this falls back to 0 records.

    out_dir = REPO_ROOT_FOR_FIBO / "stedding" / "fibo_from_syllabus"
    out_dir.mkdir(parents=True, exist_ok=True)
    generated_paths: list[str] = []

    for subject, keywords in _SYLLABUS_KEYWORDS_FOR_FIBO.items():
        pdf_path = _find_english_syllabus_pdf(subject)
        if pdf_path is None:
            continue

        # 0 records (stub: BAML client not generated). When BAML is ready,
        # we'll iterate over SyllabusDiagram records + build a FiboConfig
        # for each one (see the docs-informed config in metadata).
        syllabus_diagrams: list[dict[str, Any]] = []

        # For each syllabus diagram (when BAML is ready), produce a FiboConfig
        for diagram in syllabus_diagrams:
            config_id = str(uuid.uuid4())
            prompt_data = get_fibo_prompt(subject, "en")
            fibo_config = schemas.FiboConfig(
                config_id=config_id,
                concept_id=str(uuid.uuid4()),
                language="en",
                prompt=f"{prompt_data['prompt']}\n\nBased on syllabus diagram: {diagram.get('caption', '')}",
                palette_hex=["#1a0e1a", "#d4af37", "#f0e6d2"],
                iconography=[prompt_data["tuatha_de_deity"], diagram.get("caption", "")],
                validation_criteria=[
                    "diagram is recognisable as the syllabus figure",
                    f"subject = {subject} (NCCA syllabus match)",
                    "no text overflow",
                ],
                max_refinement_iterations=3,
                metadata={
                    "source_pdf": str(pdf_path),
                    "source_page": diagram.get("page_number"),
                    "diagram_id": diagram.get("diagram_id"),
                },
            )
            out_path = out_dir / f"{config_id}.fibo.json"
            out_path.write_text(json.dumps({
                "config_id": fibo_config.config_id,
                "subject": subject,
                "language": "en",
                "prompt": fibo_config.prompt,
                "palette_hex": fibo_config.palette_hex,
                "iconography": fibo_config.iconography,
                "source_pdf": str(pdf_path),
                "source_page": diagram.get("page_number"),
                "diagram_id": diagram.get("diagram_id"),
            }, indent=2))
            generated_paths.append(str(out_path))

    return MaterializeResult(
        metadata={
            "configs_generated": MetadataValue.int(len(generated_paths)),
            "subjects_processed": MetadataValue.int(len(_SYLLABUS_KEYWORDS_FOR_FIBO)),
            "note": MetadataValue.text(
                "stub: BAML ExtractSyllabusDiagram not yet wired; "
                "0 records returned when baml_client not generated"
            ),
        }
    )
