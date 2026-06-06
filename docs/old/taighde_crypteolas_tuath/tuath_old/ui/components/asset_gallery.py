"""
Asset gallery component for EduVision.

Displays generated assets with curriculum attribution.
"""

import json
from pathlib import Path
from typing import Optional
from datetime import datetime


# Path to generated assets
ASSETS_PATH = Path("data/assets")


def get_generated_assets(
    subject: Optional[str] = None,
    limit: int = 50,
    sort_by: str = "created_at",
) -> list[dict]:
    """
    Get list of generated assets from gallery.

    Args:
        subject: Optional subject filter
        limit: Maximum number of assets to return
        sort_by: Field to sort by (created_at, validation_score)

    Returns:
        List of asset metadata dictionaries
    """
    assets = []

    if not ASSETS_PATH.exists():
        return assets

    # Determine directories to search
    if subject:
        search_dirs = [ASSETS_PATH / subject]
    else:
        search_dirs = [d for d in ASSETS_PATH.iterdir() if d.is_dir()]

    for asset_dir in search_dirs:
        if not asset_dir.exists():
            continue

        # Find all metadata files
        for metadata_file in asset_dir.glob("*.json"):
            try:
                with open(metadata_file) as f:
                    metadata = json.load(f)

                # Ensure image exists
                image_path = Path(metadata.get("image_path", ""))
                if not image_path.exists():
                    # Try relative path
                    image_path = asset_dir / f"{metadata_file.stem}.png"
                    if not image_path.exists():
                        continue

                assets.append({
                    "asset_id": metadata.get("asset_id", metadata_file.stem),
                    "subject": metadata.get("subject", asset_dir.name),
                    "concept_title": metadata.get("fibo_config", {}).get("_metadata", {}).get("concept_title", "Unknown"),
                    "image_path": str(image_path),
                    "validation_score": metadata.get("validation", {}).get("scores", {}).get("overall", 0),
                    "created_at": metadata.get("created_at", ""),
                    "metadata": metadata,
                })

            except (json.JSONDecodeError, KeyError) as e:
                continue

    # Sort assets
    if sort_by == "validation_score":
        assets.sort(key=lambda x: x.get("validation_score", 0), reverse=True)
    else:
        assets.sort(key=lambda x: x.get("created_at", ""), reverse=True)

    return assets[:limit]


def get_asset_attribution(asset_id: str) -> dict:
    """
    Get curriculum attribution for an asset.

    Args:
        asset_id: Asset identifier

    Returns:
        Attribution dictionary with curriculum links
    """
    # Search for asset metadata
    if ASSETS_PATH.exists():
        for subject_dir in ASSETS_PATH.iterdir():
            if not subject_dir.is_dir():
                continue

            for metadata_file in subject_dir.glob(f"*{asset_id}*.json"):
                try:
                    with open(metadata_file) as f:
                        metadata = json.load(f)

                    return _build_attribution(metadata)

                except (json.JSONDecodeError, KeyError):
                    continue

    return {
        "subject": "Unknown",
        "strand": "Unknown",
        "learning_outcome": "Unknown",
        "specification_link": None,
        "similarity_score": 0,
    }


def _build_attribution(metadata: dict) -> dict:
    """Build attribution from asset metadata."""
    fibo_config = metadata.get("fibo_config", {})
    asset_metadata = fibo_config.get("_metadata", {})

    subject = asset_metadata.get("subject", metadata.get("subject", "unknown"))

    # Get curriculum reference if available
    concept_id = metadata.get("concept_id")
    curriculum_ref = _lookup_curriculum_reference(subject, concept_id)

    # Get specification link
    spec_link = _get_specification_link(subject)

    return {
        "subject": subject.title(),
        "strand": curriculum_ref.get("strand", "General"),
        "topic": curriculum_ref.get("topic", asset_metadata.get("concept_title", "Unknown")),
        "learning_outcome": curriculum_ref.get("learning_outcome", fibo_config.get("short_description", "")),
        "specification_link": spec_link,
        "page_number": curriculum_ref.get("page_number"),
        "similarity_score": metadata.get("validation", {}).get("scores", {}).get("concept_alignment", 0),
    }


def _lookup_curriculum_reference(subject: str, concept_id: Optional[str]) -> dict:
    """Look up curriculum reference from LanceDB."""
    if not concept_id:
        return {}

    try:
        from ...db.tables import get_database

        db = get_database()
        if db is None:
            return {}

        table = db.open_table("curriculum_concepts")
        results = table.search().where(f"id = '{concept_id}'").limit(1).to_list()

        if results:
            result = results[0]
            return {
                "strand": result.get("topic_name", ""),
                "topic": result.get("title", ""),
                "learning_outcome": result.get("description", ""),
                "page_number": result.get("source_page_number"),
            }

    except Exception:
        pass

    return {}


def _get_specification_link(subject: str) -> Optional[str]:
    """Get specification PDF link for subject."""
    # Load from education sources
    education_sources = Path(__file__).parent.parent.parent.parent.parent / "education_sources"
    metadata_file = education_sources / subject / "metadata.json"

    if metadata_file.exists():
        try:
            with open(metadata_file) as f:
                metadata = json.load(f)

            # Get first specification URL
            specs = metadata.get("documents", {}).get("specifications", [])
            if specs:
                return specs[0].get("url")

        except (json.JSONDecodeError, KeyError):
            pass

    return None


def export_asset_png(asset_id: str, output_path: Optional[str] = None) -> str:
    """
    Export asset as PNG with embedded metadata.

    Args:
        asset_id: Asset identifier
        output_path: Optional output path

    Returns:
        Path to exported file
    """
    from PIL import Image
    from PIL.PngImagePlugin import PngInfo

    # Find asset
    assets = get_generated_assets()
    asset = next((a for a in assets if a["asset_id"] == asset_id), None)

    if not asset:
        raise ValueError(f"Asset not found: {asset_id}")

    # Load image
    img = Image.open(asset["image_path"])

    # Add metadata
    pnginfo = PngInfo()
    pnginfo.add_text("EduVision:asset_id", asset_id)
    pnginfo.add_text("EduVision:subject", asset.get("subject", ""))
    pnginfo.add_text("EduVision:concept", asset.get("concept_title", ""))

    attribution = get_asset_attribution(asset_id)
    pnginfo.add_text("EduVision:attribution", json.dumps(attribution))

    # Save
    if not output_path:
        output_path = f"export_{asset_id}.png"

    img.save(output_path, pnginfo=pnginfo)

    return output_path


def export_asset_json(asset_id: str, output_path: Optional[str] = None) -> str:
    """
    Export asset FIBO JSON with attribution.

    Args:
        asset_id: Asset identifier
        output_path: Optional output path

    Returns:
        Path to exported file
    """
    # Find asset
    assets = get_generated_assets()
    asset = next((a for a in assets if a["asset_id"] == asset_id), None)

    if not asset:
        raise ValueError(f"Asset not found: {asset_id}")

    # Build export data
    attribution = get_asset_attribution(asset_id)

    export_data = {
        "asset_id": asset_id,
        "fibo_config": asset.get("metadata", {}).get("fibo_config", {}),
        "attribution": attribution,
        "validation": asset.get("metadata", {}).get("validation", {}),
        "created_at": asset.get("created_at"),
        "exported_at": datetime.now().isoformat(),
    }

    # Remove internal metadata
    if "_metadata" in export_data.get("fibo_config", {}):
        del export_data["fibo_config"]["_metadata"]

    # Save
    if not output_path:
        output_path = f"export_{asset_id}.json"

    with open(output_path, "w") as f:
        json.dump(export_data, f, indent=2)

    return output_path


def get_gallery_statistics(subject: Optional[str] = None) -> dict:
    """
    Get statistics about the asset gallery.

    Args:
        subject: Optional subject filter

    Returns:
        Statistics dictionary
    """
    assets = get_generated_assets(subject=subject, limit=1000)

    if not assets:
        return {
            "total_assets": 0,
            "by_subject": {},
            "avg_validation_score": 0,
            "passing_threshold": 0,
        }

    # Count by subject
    by_subject = {}
    for asset in assets:
        subj = asset.get("subject", "unknown")
        by_subject[subj] = by_subject.get(subj, 0) + 1

    # Calculate validation stats
    scores = [a.get("validation_score", 0) for a in assets]
    avg_score = sum(scores) / len(scores) if scores else 0
    passing = sum(1 for s in scores if s >= 0.7)

    return {
        "total_assets": len(assets),
        "by_subject": by_subject,
        "avg_validation_score": round(avg_score, 3),
        "passing_threshold": passing,
        "pass_rate": round(passing / len(assets), 3) if assets else 0,
    }
