"""
Dagster assets for FIBO image generation.

Assets for generating educational visual assets:
- fibo_json_configs: Generate FIBO JSON from concepts
- generated_images: Generate images from FIBO JSON
"""

import json
import uuid
from datetime import datetime
from pathlib import Path

from dagster import (
    asset,
    AssetExecutionContext,
    MaterializeResult,
    MetadataValue,
    Config,
)

from ..curriculum.resources import LanceDBResource
from .resources import FiboResource, ValidationResource


class GenerationConfig(Config):
    """Configuration for image generation."""
    subject: str = "chemistry"
    max_concepts: int = 10
    style: str = "digital_illustration"
    seed: int = -1  # -1 for random


@asset(
    group_name="fibo_generation",
    deps=["extracted_concepts"],
    description="Generate FIBO JSON configurations for curriculum concepts",
    compute_kind="baml",
)
async def fibo_json_configs(
    context: AssetExecutionContext,
    config: GenerationConfig,
    lancedb_resource: LanceDBResource,
    fibo_resource: FiboResource,
) -> MaterializeResult:
    """
    Transform extracted concepts into FIBO-compatible JSON configurations.

    For each concept with visual requirements:
    1. Use BAML to generate structured FIBO prompt
    2. Apply subject-specific styling
    3. Store configurations for generation

    Returns metadata about generated configs.
    """
    context.log.info(f"Generating FIBO configs for {config.subject}...")

    if not lancedb_resource.table_exists("curriculum_concepts"):
        context.log.warning("No concepts found - run extraction first")
        return MaterializeResult(
            metadata={"configs_generated": MetadataValue.int(0)}
        )

    # Get concepts with visual requirements
    table = lancedb_resource.get_table("curriculum_concepts")
    df = table.to_pandas()

    # Filter by subject
    df = df[df["subject"] == config.subject]

    configs = []
    for i, (_, row) in enumerate(df.iterrows()):
        if i >= config.max_concepts:
            break

        visual_reqs = json.loads(row.get("visual_requirements_json", "[]"))
        if not visual_reqs:
            continue

        # Generate FIBO config for each visual requirement
        for vr in visual_reqs:
            try:
                fibo_config = fibo_resource.create_educational_prompt(
                    concept=row["title"],
                    diagram_type=vr.get("diagram_type", "diagram"),
                    subject=config.subject,
                    style=config.style,
                )

                # Add concept metadata
                fibo_config["_metadata"] = {
                    "concept_id": row["id"],
                    "concept_title": row["title"],
                    "visual_requirement": vr,
                    "generated_at": datetime.now().isoformat(),
                }

                configs.append(fibo_config)

            except Exception as e:
                context.log.warning(f"Failed to generate config for {row['id']}: {e}")

    # Save configs to file for the next asset
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
    lancedb_resource: LanceDBResource,
    fibo_resource: FiboResource,
    validation_resource: ValidationResource,
) -> MaterializeResult:
    """
    Execute FIBO image generation with validation loop.

    For each FIBO configuration:
    1. Generate image using FIBO MLX
    2. Validate with Qwen3-VL
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

            # Add to LanceDB
            from ...db.tables import add_generated_asset

            add_generated_asset(
                db=lancedb_resource.db,
                asset_id=asset_id,
                concept_id=concept_id,
                fibo_prompt_json=json.dumps(current_config),
                style_medium=config.style,
                image_path=str(output_path),
                image_embedding=[0.0] * 512,  # TODO: Generate CLIP embedding
                seed=seed,
                validation_score=validation.get("scores", {}).get("overall", 0),
                scientific_accuracy=validation.get("scores", {}).get("scientific_accuracy", 0),
                educational_clarity=validation.get("scores", {}).get("educational_clarity", 0),
                concept_alignment=validation.get("scores", {}).get("concept_alignment", 0),
                status="validated" if validation.get("passes_threshold") else "draft",
            )

        except Exception as e:
            context.log.error(f"Failed to generate image for {concept_title}: {e}")
            failed.append({
                "concept_id": concept_id,
                "error": str(e),
            })

    context.log.info(f"Generated {len(generated)} images, {len(failed)} failed")

    return MaterializeResult(
        metadata={
            "images_generated": MetadataValue.int(len(generated)),
            "images_failed": MetadataValue.int(len(failed)),
            "validation_pass_rate": MetadataValue.float(
                sum(1 for g in generated if g["passes_validation"]) / len(generated)
                if generated else 0
            ),
            "output_directory": MetadataValue.path(str(output_dir)),
            "sample_results": MetadataValue.json(generated[:3] if generated else []),
        }
    )
