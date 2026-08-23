"""
Dagster assets for FIBO educational image generation.

Assets for generating educational visual assets:
- fibo_json_configs: Generate FIBO JSON from curriculum concepts
- generated_images: Generate images from FIBO JSON configs
- fibo_configs_from_syllabus_diagrams: Generate FIBO JSON from REAL
  extracted SyllabusDiagram records (see its own docstring below)
"""

import json
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from dagster import (
    AssetExecutionContext,
    Config,
    MaterializeResult,
    MetadataValue,
    asset,
)

from .resources import FiboResource, ValidationResource


class GenerationConfig(Config):
    """Configuration for image generation."""

    subject: str = "chemistry"
    max_concepts: int = 10
    style: str = "digital_illustration"
    seed: int = -1  # -1 for random


@asset(
    group_name="fibo_generation",
    description="Generate FIBO JSON configurations for curriculum concepts",
    compute_kind="baml",
)
async def fibo_json_configs(
    context: AssetExecutionContext,
    config: GenerationConfig,
    fibo_resource: FiboResource,
) -> MaterializeResult:
    """
    Transform curriculum concepts into FIBO-compatible JSON configurations.

    For each concept with visual requirements:
    1. Generate structured FIBO prompt
    2. Apply subject-specific styling
    3. Store configurations for generation

    Returns metadata about generated configs.
    """
    context.log.info(f"Generating FIBO configs for {config.subject}...")

    # Check for concepts file
    concepts_path = Path(f"data/concepts/{config.subject}_concepts.json")

    if not concepts_path.exists():
        # Generate sample concepts if none exist
        context.log.warning("No concepts file found - generating sample concepts")

        # Sample concepts by subject
        sample_concepts = {
            "chemistry": [
                {
                    "id": str(uuid.uuid4())[:8],
                    "title": "Covalent Bonding",
                    "description": "Sharing of electron pairs between atoms",
                    "visual_requirements": [
                        {"diagram_type": "molecular", "description": "Electron sharing"}
                    ],
                },
                {
                    "id": str(uuid.uuid4())[:8],
                    "title": "Ionic Bonding",
                    "description": "Transfer of electrons between atoms",
                    "visual_requirements": [
                        {"diagram_type": "molecular", "description": "Electron transfer"}
                    ],
                },
            ],
            "biology": [
                {
                    "id": str(uuid.uuid4())[:8],
                    "title": "Cell Structure",
                    "description": "Components of a eukaryotic cell",
                    "visual_requirements": [
                        {"diagram_type": "cell_diagram", "description": "Cell organelles"}
                    ],
                },
                {
                    "id": str(uuid.uuid4())[:8],
                    "title": "DNA Replication",
                    "description": "Process of DNA copying",
                    "visual_requirements": [
                        {"diagram_type": "process_flow", "description": "Replication steps"}
                    ],
                },
            ],
            "physics": [
                {
                    "id": str(uuid.uuid4())[:8],
                    "title": "Force Vectors",
                    "description": "Representation of forces on objects",
                    "visual_requirements": [
                        {"diagram_type": "force_diagram", "description": "Vector arrows"}
                    ],
                },
            ],
        }

        concepts = sample_concepts.get(config.subject, [])
    else:
        with open(concepts_path) as f:
            concepts = json.load(f)

    configs = []
    for i, concept in enumerate(concepts):
        if i >= config.max_concepts:
            break

        visual_reqs = concept.get("visual_requirements", [])
        if not visual_reqs:
            continue

        # Generate FIBO config for each visual requirement
        for vr in visual_reqs:
            try:
                fibo_config = fibo_resource.create_educational_prompt(
                    concept=concept["title"],
                    diagram_type=vr.get("diagram_type", "diagram"),
                    subject=config.subject,
                    style=config.style,
                )

                # Add concept metadata
                fibo_config["_metadata"] = {
                    "concept_id": concept.get("id", str(uuid.uuid4())[:8]),
                    "concept_title": concept["title"],
                    "visual_requirement": vr,
                    "generated_at": datetime.now().isoformat(),
                }

                configs.append(fibo_config)

            except Exception as e:
                context.log.warning(
                    f"Failed to generate config for {concept.get('id', 'unknown')}: {e}"
                )

    # Save configs to file
    output_path = Path("data/fibo_configs")
    output_path.mkdir(parents=True, exist_ok=True)

    configs_file = output_path / f"{config.subject}_configs.json"
    with open(configs_file, "w") as f:
        json.dump(configs, f, indent=2)

    context.log.info(f"Generated {len(configs)} FIBO configurations")

    return MaterializeResult(
        metadata={
            "configs_generated": MetadataValue.int(len(configs)),
            "subject": MetadataValue.text(config.subject),
            "output_file": MetadataValue.path(str(configs_file)),
            "sample_config": MetadataValue.json(configs[0] if configs else {}),
        }
    )


@asset(
    group_name="fibo_generation",
    deps=["fibo_json_configs"],
    description="Generate educational images from FIBO configurations",
    compute_kind="fibo",
)
async def generated_images(
    context: AssetExecutionContext,
    config: GenerationConfig,
    fibo_resource: FiboResource,
    validation_resource: ValidationResource,
) -> MaterializeResult:
    """
    Execute FIBO image generation with validation loop.

    For each FIBO configuration:
    1. Generate image using FIBO/LiteLLM
    2. Validate with VLM
    3. Refine if needed (up to 3 iterations)
    4. Store with full lineage

    Returns metadata about generated assets.
    """
    context.log.info(f"Generating images for {config.subject}...")

    # Load configs
    configs_file = Path(f"data/fibo_configs/{config.subject}_configs.json")
    if not configs_file.exists():
        context.log.warning("No configs found - run fibo_json_configs first")
        return MaterializeResult(
            metadata={"images_generated": MetadataValue.int(0)}
        )

    with open(configs_file) as f:
        configs = json.load(f)

    # Output directory
    output_dir = Path(f"data/assets/{config.subject}")
    output_dir.mkdir(parents=True, exist_ok=True)

    generated = []
    failed = []

    for i, fibo_config in enumerate(configs):
        metadata = fibo_config.pop("_metadata", {})
        concept_id = metadata.get("concept_id", f"unknown_{i}")
        concept_title = metadata.get("concept_title", "Unknown Concept")

        context.log.info(f"Generating image {i+1}/{len(configs)}: {concept_title}")

        try:
            # Determine seed
            seed = config.seed if config.seed >= 0 else None

            # Generate image
            asset_id = str(uuid.uuid4())[:8]
            output_path = output_dir / f"{asset_id}.png"

            image = await fibo_resource.generate(
                prompt=fibo_config,
                seed=seed,
                output_path=str(output_path),
            )

            # Validate
            visual_req = metadata.get("visual_requirement", {})
            validation = await validation_resource.validate_image(
                image=image,
                concept_title=concept_title,
                concept_description=fibo_config.get("short_description", ""),
                visual_requirements=visual_req,
            )

            # Refinement loop
            refinement_count = 0
            current_config = fibo_config

            while (
                not validation.get("passes_threshold", False)
                and refinement_count < validation_resource.max_refinement_iterations
            ):
                context.log.info(f"Refining image (attempt {refinement_count + 1})...")

                # Get refinement suggestions
                issues = validation.get("issues", [])
                suggestions = await validation_resource.suggest_refinements(
                    image=image,
                    target_concept=concept_title,
                    issues=issues,
                )

                if suggestions:
                    # Refine with first suggestion
                    image, current_config = await fibo_resource.refine(
                        existing_json=current_config,
                        instruction=suggestions[0],
                    )

                    # Save refined image
                    image.save(str(output_path))

                    # Re-validate
                    validation = await validation_resource.validate_image(
                        image=image,
                        concept_title=concept_title,
                        concept_description=fibo_config.get("short_description", ""),
                        visual_requirements=visual_req,
                    )

                refinement_count += 1

            # Store result
            result = {
                "asset_id": asset_id,
                "concept_id": concept_id,
                "concept_title": concept_title,
                "image_path": str(output_path),
                "fibo_config": current_config,
                "validation_score": validation.get("scores", {}).get("overall", 0),
                "passes_validation": validation.get("passes_threshold", False),
                "refinement_count": refinement_count,
                "generated_at": datetime.now().isoformat(),
            }

            generated.append(result)

        except Exception as e:
            context.log.error(f"Failed to generate image for {concept_title}: {e}")
            failed.append({
                "concept_id": concept_id,
                "error": str(e),
            })

    context.log.info(f"Generated {len(generated)} images, {len(failed)} failed")

    # Save results
    results_file = output_dir / "generation_results.json"
    with open(results_file, "w") as f:
        json.dump(
            {"generated": generated, "failed": failed},
            f,
            indent=2,
        )

    return MaterializeResult(
        metadata={
            "images_generated": MetadataValue.int(len(generated)),
            "images_failed": MetadataValue.int(len(failed)),
            "validation_pass_rate": MetadataValue.float(
                sum(1 for g in generated if g["passes_validation"]) / len(generated)
                if generated
                else 0
            ),
            "output_directory": MetadataValue.path(str(output_dir)),
            "sample_results": MetadataValue.json(generated[:3] if generated else []),
        }
    )


# =============================================================================
# fibo_configs_from_syllabus_diagrams (2026-08-08
# vision-model-syllabus-diagram-generation-v1)
# =============================================================================
#
# `fibo_json_configs` above is the ONLY part of "asset generation" that
# was genuinely implemented before this change — but it never consumed
# real curriculum content: with no `data/concepts/<subject>_concepts.json`
# file present (the normal case), it falls back to a small hardcoded
# SAMPLE_CONCEPTS dict ("Covalent Bonding", "Ionic Bonding", ...) baked
# into the function itself. This asset closes that loop: it calls the
# real `ExtractSyllabusDiagram` BAML function
# (baml_src/british_isles/ireland/education/lc_extraction/
# syllabus_diagram.baml) against the actual NCCA syllabus PDF text for a
# subject, and turns each genuinely-detected diagram into a FIBO config
# — never a fabricated concept.
#
# Per the 2026-08-08-lakehouse-extensive-hydration-v1 change:
# `ExtractSyllabusDiagram` now accepts an optional `image: image[]?`
# param (baml_src/british_isles/ireland/education/lc_extraction/
# syllabus_diagram.baml), closing the gap this comment used to document
# ("declared client BIEPV3Vision but takes no image parameter"). This
# asset now renders the syllabus PDF's first few pages via
# `meaisinfhoghlaim.document_factory.pdf_to_image_bridge` and passes
# them alongside `pdf_text`, so detection is genuinely vision-based
# (real pixels) for those pages instead of text-inferred from figure
# captions / "Figure N:" references alone. Bounded to
# `MAX_DIAGRAM_IMAGE_PAGES` pages (not the whole document) to keep the
# request size and per-call cost reasonable — a real, documented
# narrowing, not a silent one. Rendering degrades gracefully to `None`
# per page (pymupdf missing, corrupt page, etc.), so a partially- or
# fully-failed render still falls through to the function's existing
# text-only path rather than failing the whole extraction.
#
# Self-contained PDF discovery (not importing
# orchestration/defs/2_materials/lc_extraction/quest_pack_assets.py's
# `_classify_pdfs`) to keep this module's own layer (`tuatha/`, the
# library code Dagster assets in `orchestration/defs/4_asset_generation/`
# wrap) independent of a Dagster-asset module in a different layer.

REPO_ROOT_FOR_FIBO = Path(__file__).resolve().parents[3]
LEAVING_CERT_ROOT_FOR_FIBO = REPO_ROOT_FOR_FIBO / "leaving_certificate"
_SYLLABUS_KEYWORDS_FOR_FIBO = ("syllabus", "specification")
_DATE_SUFFIX_RE_FOR_FIBO = re.compile(r"_\d{4}-\d{2}-\d{2}(?=\.pdf$)", re.IGNORECASE)
MAX_DIAGRAM_TEXT_CHARS = 60_000
MAX_DIAGRAM_IMAGE_PAGES = 8
"""Cap on how many rendered page images are sent per ExtractSyllabusDiagram
call — a real bound, not the whole document, to keep request size/cost
reasonable (mirrors the qpack-generation item cap fixed in
2026-08-08-docs-informed-quest-and-credential-generation-v1 for the same
"unbounded generation -> HTTP timeout" reason)."""


def _find_english_syllabus_pdf(subject: str) -> Path | None:
    """Find the primary English-medium syllabus PDF for a subject.

    Mirrors the relevant slice of quest_pack_assets.py's
    `_classify_pdfs` heuristic (syllabus/specification filename
    keywords, `_YYYY-MM-DD` refresh-suffix dedup) without importing
    across layers — see the module-level note above.
    """
    subject_dir = LEAVING_CERT_ROOT_FOR_FIBO / subject
    if not subject_dir.exists():
        return None

    seen: set[str] = set()
    candidates: list[Path] = []
    for pdf_path in sorted(subject_dir.rglob("*.pdf")):
        normalized = _DATE_SUFFIX_RE_FOR_FIBO.sub("", pdf_path.name).lower()
        if normalized in seen:
            continue
        seen.add(normalized)
        name_lower = pdf_path.name.lower()
        parent_lower = pdf_path.parent.name.lower()
        is_ga = parent_lower == "ga" or "gaeilge" in name_lower or "siollab" in name_lower
        if is_ga:
            continue
        if any(k in name_lower for k in _SYLLABUS_KEYWORDS_FOR_FIBO):
            candidates.append(pdf_path)

    if not candidates:
        return None
    return min(candidates, key=lambda p: len(p.name))


class SyllabusDiagramGenerationConfig(Config):
    """Configuration for generating FIBO configs from real SyllabusDiagram
    extractions."""

    subject: str = "chemistry"
    max_diagrams: int = 5
    style: str = "digital_illustration"


@asset(
    group_name="fibo_generation",
    description=(
        "Generate FIBO JSON configurations from REAL diagrams detected in "
        "the official NCCA syllabus PDF via ExtractSyllabusDiagram — "
        "replaces fibo_json_configs' hardcoded sample-concept fallback "
        "with genuinely extracted content for subjects with a real "
        "syllabus PDF in the corpus."
    ),
    compute_kind="baml",
)
async def fibo_configs_from_syllabus_diagrams(
    context: AssetExecutionContext,
    config: SyllabusDiagramGenerationConfig,
    fibo_resource: FiboResource,
) -> MaterializeResult:
    """Extract real diagrams from a subject's syllabus PDF and turn each
    into a FIBO generation config.

    Returns a materialised-but-empty result (0 configs, not a Failure)
    when the subject has no English-medium syllabus PDF, no extractable
    text layer, or the BAML client isn't available — a subject with no
    diagrams (e.g. gaeilge, mostly prose) or an environment without
    BAML configured is an expected, documented outcome, not an error.
    """
    try:
        from baml_client import b  # type: ignore[import-not-found]
    except ImportError:
        try:
            from baml_client.baml_client.sync_client import b  # type: ignore[import-not-found]
        except ImportError:
            context.log.warning(
                "fibo_configs_from_syllabus_diagrams: baml_client not importable; skipping"
            )
            return MaterializeResult(metadata={"configs_generated": MetadataValue.int(0)})

    try:
        from pypdf import PdfReader
    except ImportError:
        context.log.warning(
            "fibo_configs_from_syllabus_diagrams: pypdf not importable; skipping"
        )
        return MaterializeResult(metadata={"configs_generated": MetadataValue.int(0)})

    syllabus_pdf = _find_english_syllabus_pdf(config.subject)
    if syllabus_pdf is None:
        context.log.warning(
            "fibo_configs_from_syllabus_diagrams: no English-medium syllabus "
            "PDF found for subject=%s under %s",
            config.subject,
            LEAVING_CERT_ROOT_FOR_FIBO / config.subject,
        )
        return MaterializeResult(metadata={"configs_generated": MetadataValue.int(0)})

    reader = PdfReader(str(syllabus_pdf))
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    if len(text) > MAX_DIAGRAM_TEXT_CHARS:
        text = text[:MAX_DIAGRAM_TEXT_CHARS]
    if not text.strip():
        context.log.warning(
            "fibo_configs_from_syllabus_diagrams: no extractable text layer in %s",
            syllabus_pdf.name,
        )
        return MaterializeResult(metadata={"configs_generated": MetadataValue.int(0)})

    page_count = len(reader.pages)
    image_page_count = min(page_count, MAX_DIAGRAM_IMAGE_PAGES)
    rendered_images = []
    try:
        from meaisinfhoghlaim.document_factory.pdf_to_image_bridge import (
            pdf_page_to_baml_image,
        )

        for page_number in range(1, image_page_count + 1):
            img = pdf_page_to_baml_image(syllabus_pdf, page_number)
            if img is not None:
                rendered_images.append(img)
    except ImportError:
        context.log.warning(
            "fibo_configs_from_syllabus_diagrams: pdf_to_image_bridge not "
            "importable; falling back to text-only diagram detection"
        )

    context.log.info(
        "fibo_configs_from_syllabus_diagrams: extracting diagrams from %s "
        "(subject=%s, %d/%d page image(s) rendered)",
        syllabus_pdf.name,
        config.subject,
        len(rendered_images),
        page_count,
    )
    try:
        diagrams = b.ExtractSyllabusDiagram(
            pdf_text=text,
            page_text=None,
            page_number=None,
            subject=config.subject,
            subject_language="EN",
            image=rendered_images or None,
        )
    except Exception as exc:  # noqa: BLE001 — BAML error types are not stable API
        context.log.error(
            "fibo_configs_from_syllabus_diagrams: extraction failed for %s: %s",
            config.subject,
            exc,
        )
        return MaterializeResult(metadata={"configs_generated": MetadataValue.int(0)})

    configs: list[dict[str, Any]] = []
    for diagram in diagrams[: config.max_diagrams]:
        concept_title = diagram.caption_en or f"{config.subject} diagram (page {diagram.page_number})"
        fibo_config = fibo_resource.create_educational_prompt(
            concept=concept_title,
            diagram_type="diagram",
            subject=config.subject,
            style=config.style,
        )
        fibo_config["_metadata"] = {
            "diagram_id": diagram.diagram_id,
            "source_pdf": diagram.source_pdf or syllabus_pdf.name,
            "page_number": diagram.page_number,
            "confidence_score": diagram.confidence_score,
            "related_lo_ids": diagram.related_lo_ids,
            "caption_ga": diagram.caption_ga,
            "generated_at": datetime.now().isoformat(),
        }
        configs.append(fibo_config)

    output_path = Path("data/fibo_configs")
    output_path.mkdir(parents=True, exist_ok=True)
    configs_file = output_path / f"{config.subject}_syllabus_diagram_configs.json"
    with open(configs_file, "w") as f:
        json.dump(configs, f, indent=2)

    context.log.info(
        "fibo_configs_from_syllabus_diagrams: %d real diagram(s) -> FIBO configs for %s",
        len(configs),
        config.subject,
    )

    return MaterializeResult(
        metadata={
            "configs_generated": MetadataValue.int(len(configs)),
            "diagrams_detected": MetadataValue.int(len(diagrams)),
            "subject": MetadataValue.text(config.subject),
            "source_pdf": MetadataValue.path(str(syllabus_pdf)),
            "output_file": MetadataValue.path(str(configs_file)),
            "sample_config": MetadataValue.json(configs[0] if configs else {}),
        }
    )
