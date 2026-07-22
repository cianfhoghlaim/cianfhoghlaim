"""
Dagster assets for FIBO educational image generation.

Assets for generating educational visual assets:
- fibo_json_configs: Generate FIBO JSON from curriculum concepts
- generated_images: Generate images from FIBO JSON configs
"""

import json
import uuid
from datetime import datetime
from pathlib import Path

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
