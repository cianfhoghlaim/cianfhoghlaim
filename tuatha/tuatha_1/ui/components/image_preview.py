"""
Image preview component for EduVision.

Handles FIBO image generation and preview display.
"""

from typing import Optional, Tuple
from PIL import Image
import io


def generate_preview(
    fibo_json: dict,
    seed: Optional[int] = None,
) -> Tuple[Optional[Image.Image], str, dict]:
    """
    Generate an image preview from FIBO JSON.

    Args:
        fibo_json: FIBO-compatible JSON configuration
        seed: Optional seed for reproducibility

    Returns:
        Tuple of (image, status_message, validation_results)
    """
    try:
        from ...models.fibo_mlx import FiboMLXGenerator

        # Initialize generator
        generator = FiboMLXGenerator()

        # Generate image
        image = generator.generate_sync(
            prompt=fibo_json,
            seed=seed,
        )

        # Validate the generated image
        validation = validate_generated_image(
            image=image,
            fibo_json=fibo_json,
        )

        status = f"Generated successfully. Validation score: {validation.get('scores', {}).get('overall', 0):.2f}"

        return image, status, validation

    except ImportError as e:
        # Fallback to placeholder if FIBO not available
        return _generate_placeholder(fibo_json), f"FIBO not available: {e}", {"scores": {"overall": 0}}

    except Exception as e:
        return None, f"Generation failed: {str(e)}", {"scores": {"overall": 0}, "error": str(e)}


def validate_generated_image(
    image: Image.Image,
    fibo_json: dict,
) -> dict:
    """
    Validate a generated image against requirements.

    Args:
        image: Generated PIL image
        fibo_json: Original FIBO configuration

    Returns:
        Validation results dictionary
    """
    try:
        from ...models.qwen_vlm import Qwen3VLClient

        client = Qwen3VLClient()

        # Get concept info from metadata
        metadata = fibo_json.get("_metadata", {})
        concept_title = metadata.get("concept_title", "Unknown")

        # Run validation
        result = client.validate_educational_image_sync(
            generated_image=image,
            concept_title=concept_title,
            concept_description=fibo_json.get("short_description", ""),
            visual_requirements={
                "style": fibo_json.get("style_medium", ""),
                "objects": [obj.get("class_label", "") for obj in fibo_json.get("objects", [])],
            },
        )

        return result

    except ImportError:
        # Fallback validation based on image properties
        return _fallback_validation(image, fibo_json)

    except Exception as e:
        return {
            "scores": {"overall": 0},
            "error": str(e),
            "passes_threshold": False,
        }


def _fallback_validation(image: Image.Image, fibo_json: dict) -> dict:
    """
    Fallback validation when VLM is not available.

    Performs basic checks on image properties.
    """
    scores = {
        "image_quality": 0.0,
        "resolution": 0.0,
        "aspect_ratio_match": 0.0,
    }

    # Check resolution
    width, height = image.size
    if width >= 512 and height >= 512:
        scores["resolution"] = 1.0
    elif width >= 256 and height >= 256:
        scores["resolution"] = 0.5

    # Check aspect ratio
    target_ratio = fibo_json.get("photographic_characteristics", {}).get("aspect_ratio", "16:9")
    if target_ratio:
        try:
            tw, th = map(int, target_ratio.split(":"))
            actual_ratio = width / height
            target = tw / th
            ratio_diff = abs(actual_ratio - target) / target
            scores["aspect_ratio_match"] = max(0, 1 - ratio_diff)
        except (ValueError, ZeroDivisionError):
            scores["aspect_ratio_match"] = 0.5

    # Basic quality estimate (non-blank image)
    if image.mode in ("RGB", "RGBA"):
        # Check if image has content (not all one color)
        extrema = image.convert("L").getextrema()
        if extrema[1] - extrema[0] > 10:
            scores["image_quality"] = 0.7

    overall = sum(scores.values()) / len(scores)

    return {
        "scores": {
            **scores,
            "overall": overall,
        },
        "passes_threshold": overall >= 0.5,
        "method": "fallback",
    }


def _generate_placeholder(fibo_json: dict) -> Image.Image:
    """
    Generate a placeholder image when FIBO is not available.

    Creates a simple image with text describing what would be generated.
    """
    from PIL import Image, ImageDraw, ImageFont

    # Parse aspect ratio
    aspect_str = fibo_json.get("photographic_characteristics", {}).get("aspect_ratio", "16:9")
    try:
        aw, ah = map(int, aspect_str.split(":"))
    except (ValueError, AttributeError):
        aw, ah = 16, 9

    # Calculate dimensions
    base_size = 512
    if aw > ah:
        width = base_size
        height = int(base_size * ah / aw)
    else:
        height = base_size
        width = int(base_size * aw / ah)

    # Create image
    img = Image.new("RGB", (width, height), color=(240, 240, 240))
    draw = ImageDraw.Draw(img)

    # Add text
    title = fibo_json.get("_metadata", {}).get("concept_title", "Preview")
    description = fibo_json.get("short_description", "FIBO generation placeholder")

    # Draw border
    draw.rectangle([5, 5, width-5, height-5], outline=(100, 100, 100), width=2)

    # Draw title
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
        small_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
    except OSError:
        font = ImageFont.load_default()
        small_font = font

    # Center title
    bbox = draw.textbbox((0, 0), title, font=font)
    text_width = bbox[2] - bbox[0]
    x = (width - text_width) // 2
    draw.text((x, 30), title, fill=(50, 50, 50), font=font)

    # Add description (wrapped)
    y = 80
    words = description.split()
    line = ""
    for word in words:
        test_line = f"{line} {word}".strip()
        bbox = draw.textbbox((0, 0), test_line, font=small_font)
        if bbox[2] - bbox[0] > width - 40:
            draw.text((20, y), line, fill=(100, 100, 100), font=small_font)
            y += 20
            line = word
        else:
            line = test_line
    if line:
        draw.text((20, y), line, fill=(100, 100, 100), font=small_font)

    # Add placeholder notice
    notice = "[FIBO Preview - Install dependencies for actual generation]"
    bbox = draw.textbbox((0, 0), notice, font=small_font)
    x = (width - (bbox[2] - bbox[0])) // 2
    draw.text((x, height - 40), notice, fill=(150, 100, 100), font=small_font)

    return img


def refine_image(
    current_image: Image.Image,
    current_json: dict,
    instruction: str,
) -> Tuple[Optional[Image.Image], dict, str]:
    """
    Refine an existing image with an instruction.

    Args:
        current_image: Current generated image
        current_json: Current FIBO JSON
        instruction: Refinement instruction

    Returns:
        Tuple of (refined_image, updated_json, status)
    """
    try:
        from ...models.fibo_mlx import FiboMLXGenerator

        generator = FiboMLXGenerator()

        refined_image, updated_json = generator.refine_sync(
            existing_json=current_json,
            instruction=instruction,
        )

        return refined_image, updated_json, f"Refined: {instruction}"

    except Exception as e:
        return current_image, current_json, f"Refinement failed: {str(e)}"


def save_to_gallery(
    image: Image.Image,
    fibo_json: dict,
    validation: dict,
    subject: str,
) -> str:
    """
    Save generated image to asset gallery.

    Args:
        image: Generated image
        fibo_json: FIBO configuration
        validation: Validation results
        subject: Subject slug

    Returns:
        Path to saved asset
    """
    import json
    import uuid
    from datetime import datetime
    from pathlib import Path

    # Create output directory
    output_dir = Path(f"data/assets/{subject}")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate asset ID
    asset_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save image
    image_path = output_dir / f"{asset_id}_{timestamp}.png"
    image.save(str(image_path))

    # Save metadata
    metadata = {
        "asset_id": asset_id,
        "subject": subject,
        "fibo_config": fibo_json,
        "validation": validation,
        "created_at": datetime.now().isoformat(),
        "image_path": str(image_path),
    }

    metadata_path = output_dir / f"{asset_id}_{timestamp}.json"
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)

    return str(image_path)
