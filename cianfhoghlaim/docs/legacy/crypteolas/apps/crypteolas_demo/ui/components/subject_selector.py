"""
Subject selector component for EduVision.

Loads curriculum metadata and provides syllabus navigation.
"""

import json
from pathlib import Path
from typing import Optional


# Path to education sources
EDUCATION_SOURCES_PATH = Path(__file__).parent.parent.parent.parent.parent / "education_sources"


def load_subject_metadata(subject: str) -> dict:
    """
    Load metadata for a specific subject.

    Args:
        subject: Subject slug (chemistry, biology, geography)

    Returns:
        Subject metadata dictionary
    """
    metadata_file = EDUCATION_SOURCES_PATH / subject / "metadata.json"

    if not metadata_file.exists():
        return {
            "slug": subject,
            "description": f"Metadata not found for {subject}",
            "metadata": {},
        }

    with open(metadata_file) as f:
        return json.load(f)


def get_curriculum_tree(subject: str) -> dict:
    """
    Build a hierarchical curriculum tree for display.

    Args:
        subject: Subject slug

    Returns:
        Nested dictionary representing syllabus structure
    """
    metadata = load_subject_metadata(subject)

    tree = {
        "subject": metadata.get("name", subject.title()),
        "slug": subject,
        "level": metadata.get("metadata", {}).get("level", "unknown"),
        "strands": [],
    }

    # Extract strands/units from curriculum structure
    curriculum = metadata.get("curriculum_structure", {})

    if "strands" in curriculum:
        for strand in curriculum["strands"]:
            strand_node = {
                "name": strand.get("name", "Unnamed Strand"),
                "strand_number": strand.get("strand_number"),
                "topics": [],
            }

            for topic in strand.get("topics", []):
                topic_node = {
                    "name": topic.get("name", "Unnamed Topic"),
                    "learning_outcomes": topic.get("learning_outcomes", []),
                    "key_skills": topic.get("key_skills", []),
                }
                strand_node["topics"].append(topic_node)

            tree["strands"].append(strand_node)

    elif "units" in curriculum:
        # Alternative structure (Biology uses units)
        for unit in curriculum["units"]:
            strand_node = {
                "name": unit.get("name", "Unnamed Unit"),
                "strand_number": unit.get("unit_number"),
                "topics": [],
            }

            for topic in unit.get("topics", []):
                topic_node = {
                    "name": topic.get("name", "Unnamed Topic"),
                    "learning_outcomes": topic.get("learning_outcomes", []),
                }
                strand_node["topics"].append(topic_node)

            tree["strands"].append(strand_node)

    return tree


def get_learning_outcomes(subject: str, strand_name: Optional[str] = None) -> list[dict]:
    """
    Get learning outcomes for a subject, optionally filtered by strand.

    Args:
        subject: Subject slug
        strand_name: Optional strand name to filter by

    Returns:
        List of learning outcome dictionaries
    """
    tree = get_curriculum_tree(subject)
    outcomes = []

    for strand in tree.get("strands", []):
        if strand_name and strand["name"] != strand_name:
            continue

        for topic in strand.get("topics", []):
            for i, lo in enumerate(topic.get("learning_outcomes", [])):
                if isinstance(lo, str):
                    outcomes.append({
                        "code": f"{strand.get('strand_number', 'S')}.{i+1}",
                        "description": lo,
                        "topic": topic["name"],
                        "strand": strand["name"],
                        "visual_potential": estimate_visual_potential(lo),
                    })
                elif isinstance(lo, dict):
                    outcomes.append({
                        "code": lo.get("code", f"{strand.get('strand_number', 'S')}.{i+1}"),
                        "description": lo.get("description", str(lo)),
                        "topic": topic["name"],
                        "strand": strand["name"],
                        "visual_potential": estimate_visual_potential(lo.get("description", "")),
                    })

    return outcomes


def estimate_visual_potential(text: str) -> str:
    """
    Estimate the visual potential of a learning outcome.

    Returns 'High', 'Medium', or 'Low' based on keywords.
    """
    text_lower = text.lower()

    high_keywords = [
        "diagram", "structure", "model", "process", "cycle", "mechanism",
        "reaction", "apparatus", "setup", "experiment", "graph", "chart",
        "cell", "organ", "system", "flow", "map", "landscape", "formation",
    ]

    medium_keywords = [
        "describe", "explain", "compare", "analyse", "investigate",
        "demonstrate", "illustrate", "identify", "classify",
    ]

    if any(kw in text_lower for kw in high_keywords):
        return "High"
    elif any(kw in text_lower for kw in medium_keywords):
        return "Medium"
    else:
        return "Low"


def get_all_subjects() -> list[dict]:
    """
    Get list of all available subjects.

    Returns:
        List of subject metadata dictionaries
    """
    subjects = []

    if EDUCATION_SOURCES_PATH.exists():
        for subject_dir in EDUCATION_SOURCES_PATH.iterdir():
            if subject_dir.is_dir() and (subject_dir / "metadata.json").exists():
                metadata = load_subject_metadata(subject_dir.name)
                subjects.append({
                    "slug": subject_dir.name,
                    "name": metadata.get("name", subject_dir.name.title()),
                    "level": metadata.get("metadata", {}).get("level", "unknown"),
                })

    return subjects
