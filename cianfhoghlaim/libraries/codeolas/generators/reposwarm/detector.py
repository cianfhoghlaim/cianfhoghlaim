"""
Repository type detection.

Analyzes project structure to determine the type of repository.
"""

import logging
from pathlib import Path

from .types import RepoType

logger = logging.getLogger(__name__)


class RepoTypeDetector:
    """Detects the type of repository based on its structure."""

    # File patterns for each type
    BACKEND_MARKERS = {
        "manage.py",  # Django
        "wsgi.py",
        "asgi.py",
        "app.py",  # Flask
        "main.py",
        "server.py",
        "api/",
        "routes/",
        "controllers/",
        "services/",
        "Gemfile",  # Rails
        "config.ru",
        "go.mod",  # Go
        "cmd/",
        "internal/",
        "pom.xml",  # Java
        "build.gradle",
        "src/main/java",
    }

    FRONTEND_MARKERS = {
        "package.json",  # Could be either, but with these it's frontend
        "src/App.tsx",
        "src/App.jsx",
        "src/App.vue",
        "src/main.tsx",
        "src/main.ts",
        "src/index.tsx",
        "next.config.js",
        "next.config.mjs",
        "nuxt.config.ts",
        "vite.config.ts",
        "vite.config.js",
        "angular.json",
        "svelte.config.js",
        "components/",
        "pages/",
        "public/",
        "static/",
    }

    LIBRARY_MARKERS = {
        "setup.py",
        "pyproject.toml",
        "setup.cfg",
        "Cargo.toml",
        "lib/",
        "src/lib.rs",
        "index.d.ts",
        ".npmrc",
    }

    DATA_PIPELINE_MARKERS = {
        "dbt_project.yml",
        "dagster.yaml",
        "airflow/",
        "dags/",
        "pipelines/",
        "flows/",
        "etl/",
        "data/",
        "notebooks/",
        "cocoindex/",
        "dlt_sources/",
    }

    INFRASTRUCTURE_MARKERS = {
        "terraform/",
        "pulumi/",
        "ansible/",
        "kubernetes/",
        "k8s/",
        "helm/",
        "docker-compose.yaml",
        "docker-compose.yml",
        "Dockerfile",
        ".github/workflows/",
        "cloudbuild.yaml",
        "azure-pipelines.yml",
    }

    MONOREPO_MARKERS = {
        "pnpm-workspace.yaml",
        "lerna.json",
        "nx.json",
        "turbo.json",
        "rush.json",
        "packages/",
        "apps/",
        "modules/",
        "services/",
        "libs/",
    }

    def __init__(self, repo_path: str | Path):
        self.repo_path = Path(repo_path)

    def detect(self) -> RepoType:
        """Detect the repository type."""
        scores: dict[RepoType, int] = dict.fromkeys(RepoType, 0)

        # Check for markers
        for path in self.repo_path.rglob("*"):
            rel_path = str(path.relative_to(self.repo_path))

            # Skip common directories
            if any(p in rel_path for p in [".git", "node_modules", "__pycache__", ".venv"]):
                continue

            name = path.name
            rel_str = rel_path.replace("\\", "/")

            # Check each type
            if any(m in rel_str or name == m.rstrip("/") for m in self.MONOREPO_MARKERS):
                scores[RepoType.MONOREPO] += 2

            if any(m in rel_str or name == m.rstrip("/") for m in self.DATA_PIPELINE_MARKERS):
                scores[RepoType.DATA_PIPELINE] += 2

            if any(m in rel_str or name == m.rstrip("/") for m in self.INFRASTRUCTURE_MARKERS):
                scores[RepoType.INFRASTRUCTURE] += 2

            if any(m in rel_str or name == m.rstrip("/") for m in self.BACKEND_MARKERS):
                scores[RepoType.BACKEND] += 1

            if any(m in rel_str or name == m.rstrip("/") for m in self.FRONTEND_MARKERS):
                scores[RepoType.FRONTEND] += 1

            if any(m in rel_str or name == m.rstrip("/") for m in self.LIBRARY_MARKERS):
                scores[RepoType.LIBRARY] += 1

        # Determine type
        max_score = max(scores.values())
        if max_score == 0:
            return RepoType.GENERIC

        # Get type with highest score
        for repo_type, score in sorted(scores.items(), key=lambda x: -x[1]):
            if score == max_score:
                logger.info(f"Detected repo type: {repo_type.value} (score: {score})")
                return repo_type

        return RepoType.GENERIC

    def get_prompt_sections(self, repo_type: RepoType) -> list[str]:
        """Get the prompt sections for a repo type."""
        # Shared sections for all types
        shared = ["hl_overview", "core_entities", "dependencies"]

        type_specific: dict[RepoType, list[str]] = {
            RepoType.BACKEND: ["data_layer", "apis", "authentication", "events_and_messaging"],
            RepoType.FRONTEND: ["components", "state_and_data", "authentication"],
            RepoType.LIBRARY: ["api_surface", "internals"],
            RepoType.MONOREPO: ["hl_overview", "dependencies"],
            RepoType.DATA_PIPELINE: ["data_layer", "apis"],
            RepoType.INFRASTRUCTURE: ["deployment", "dependencies"],
            RepoType.GENERIC: [],
        }

        return shared + type_specific.get(repo_type, [])
