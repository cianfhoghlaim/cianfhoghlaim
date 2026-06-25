"""Game Development Portfolio Showcase.

Yedya-style portfolio for Celtic MMO development projects,
showcasing SpacetimeDB, Godot, Unity, Unreal, and Babylon.js integrations.

Projects:
- SpacetimeDB MMO Backend
- Godot Celtic Shaders
- Unity Particle Effects
- Unreal Weather Simulation
- Babylon.js Web Client
"""

from pathlib import Path

SHOWCASE_DIR = Path(__file__).parent
PROJECT_DATA_DIR = SHOWCASE_DIR / "project_data"


def get_projects() -> list[dict]:
    """Load all project definitions."""
    import yaml

    projects = []
    for yaml_file in PROJECT_DATA_DIR.glob("*.yaml"):
        with open(yaml_file) as f:
            project = yaml.safe_load(f)
            project["slug"] = yaml_file.stem
            projects.append(project)

    return sorted(projects, key=lambda p: p.get("order", 999))


def get_project(slug: str) -> dict | None:
    """Load a specific project by slug."""
    yaml_file = PROJECT_DATA_DIR / f"{slug}.yaml"
    if not yaml_file.exists():
        return None

    import yaml
    with open(yaml_file) as f:
        project = yaml.safe_load(f)
        project["slug"] = slug
        return project


__all__ = ["get_projects", "get_project", "SHOWCASE_DIR", "PROJECT_DATA_DIR"]
