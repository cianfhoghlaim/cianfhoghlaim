"""
RepoSwarm Architecture Documentation Generator.

Uses LLM analysis to generate comprehensive architecture documentation.
"""

import asyncio
import logging
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

from .cache import ArchDocCache
from .detector import RepoTypeDetector
from .types import (
    ArchDocument,
    ArchSection,
    CacheConfig,
    GenerationConfig,
    RepoType,
)

logger = logging.getLogger(__name__)

# Extension to language mapping
EXTENSION_TO_LANGUAGE = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".jsx": "javascript",
    ".rs": "rust",
    ".go": "go",
    ".java": "java",
    ".rb": "ruby",
    ".php": "php",
    ".cs": "csharp",
    ".cpp": "cpp",
    ".c": "c",
    ".swift": "swift",
    ".kt": "kotlin",
    ".scala": "scala",
    ".vue": "vue",
    ".svelte": "svelte",
}


class RepoSwarmGenerator:
    """
    LLM-powered architecture documentation generator.

    Uses multi-provider LLM routing for analysis and DuckDB for caching.
    """

    def __init__(
        self,
        repo_path: str | Path,
        output_path: str | Path | None = None,
        config: GenerationConfig | None = None,
        cache_config: CacheConfig | None = None,
    ):
        self.repo_path = Path(repo_path).resolve()
        self.output_path = Path(output_path) if output_path else self.repo_path / ".arch.md"
        self.config = config or GenerationConfig()
        self.cache = ArchDocCache(cache_config)
        self.detector = RepoTypeDetector(self.repo_path)

        self._llm_router = None

    async def _get_llm_router(self):
        """Get the LLM router for Claude API calls."""
        if self._llm_router is None:
            try:
                try:
                    from sruth.oideachais.http_utils.llm_router import get_llm_router
                except ImportError:
                    from sruth_browser.llm_router import get_llm_router
                self._llm_router = await get_llm_router()
            except ImportError:
                logger.warning("LLM router not available")
                return None
        return self._llm_router

    def _get_git_sha(self) -> str | None:
        """Get current git SHA."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
            )
            return result.stdout.strip() if result.returncode == 0 else None
        except Exception:
            return None

    def _build_file_tree(self, max_depth: int | None = None) -> dict[str, Any]:
        """Build a tree of files in the repo."""
        max_depth = max_depth or self.config.max_file_depth
        tree: dict[str, Any] = {}
        ignore_patterns = {
            ".git", "node_modules", "__pycache__", ".venv", "venv",
            "dist", "build", ".next", "target", ".tox", ".pytest_cache",
            ".mypy_cache", ".ruff_cache", "coverage", ".coverage",
        }

        for path in self.repo_path.rglob("*"):
            if not path.is_file():
                continue

            rel_path = path.relative_to(self.repo_path)
            parts = rel_path.parts

            # Skip ignored directories
            if any(p in ignore_patterns for p in parts):
                continue

            # Skip if too deep
            if len(parts) > max_depth:
                continue

            current = tree
            for part in parts[:-1]:
                current = current.setdefault(part, {})
            current[parts[-1]] = str(rel_path)

        return tree

    def _detect_languages(self) -> dict[str, int]:
        """Detect languages used in the repo."""
        counts: dict[str, int] = {}

        for path in self.repo_path.rglob("*"):
            if not path.is_file():
                continue

            # Skip common ignored dirs
            if any(p in path.parts for p in [".git", "node_modules", "__pycache__", ".venv"]):
                continue

            ext = path.suffix.lower()
            lang = EXTENSION_TO_LANGUAGE.get(ext)
            if lang:
                counts[lang] = counts.get(lang, 0) + 1

        return counts

    def _get_dependencies(self) -> list[str]:
        """Extract dependencies from package files."""
        deps = []

        # Python
        pyproject = self.repo_path / "pyproject.toml"
        if pyproject.exists():
            deps.append("Python (pyproject.toml)")

        requirements = self.repo_path / "requirements.txt"
        if requirements.exists():
            deps.append("Python (requirements.txt)")

        # Node.js
        package = self.repo_path / "package.json"
        if package.exists():
            deps.append("Node.js (package.json)")

        # Rust
        cargo = self.repo_path / "Cargo.toml"
        if cargo.exists():
            deps.append("Rust (Cargo.toml)")

        # Go
        gomod = self.repo_path / "go.mod"
        if gomod.exists():
            deps.append("Go (go.mod)")

        return deps

    def _render_tree(self, tree: dict, prefix: str = "", max_depth: int = 3, depth: int = 0) -> str:
        """Render tree as string."""
        if depth >= max_depth:
            return ""

        lines = []
        items = sorted(tree.items())

        for i, (name, value) in enumerate(items):
            is_last = i == len(items) - 1
            connector = "└── " if is_last else "├── "
            lines.append(prefix + connector + name)

            if isinstance(value, dict) and depth < max_depth - 1:
                extension = "    " if is_last else "│   "
                subtree = self._render_tree(value, prefix + extension, max_depth, depth + 1)
                if subtree:
                    lines.append(subtree)

        return "\n".join(lines)

    def _get_repo_structure_prompt(self) -> str:
        """Get the repo structure for prompts."""
        tree = self._build_file_tree()
        tree_str = self._render_tree(tree, max_depth=4)
        return f"```\n{tree_str}\n```"

    async def _analyze_with_llm(
        self,
        prompt: str,
        section_name: str,
    ) -> str:
        """Analyze using LLM."""
        router = await self._get_llm_router()

        if router is None:
            logger.warning(f"LLM router unavailable, using fallback for {section_name}")
            return f"*Analysis not available - LLM router not configured*"

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a senior software architect analyzing a codebase. "
                    "Provide clear, concise technical documentation. "
                    "Use markdown formatting. Include code examples where helpful. "
                    "Be specific about what you observe in the actual codebase."
                ),
            },
            {"role": "user", "content": prompt},
        ]

        try:
            response = await router.complete(
                messages,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
            )

            if response.success:
                logger.info(f"LLM analysis complete for {section_name} ({response.latency_ms:.0f}ms)")
                return response.content
            else:
                logger.warning(f"LLM analysis failed for {section_name}: {response.error}")
                return f"*Analysis failed: {response.error}*"

        except Exception as e:
            logger.error(f"LLM error for {section_name}: {e}")
            return f"*Analysis error: {e}*"

    async def _generate_overview_section(self, repo_type: RepoType) -> ArchSection:
        """Generate high-level overview section."""
        repo_structure = self._get_repo_structure_prompt()
        languages = self._detect_languages()
        deps = self._get_dependencies()

        prompt = f"""
Act as a senior software architect. Analyze this repository structure:

{repo_structure}

**Languages detected:** {', '.join(f'{l} ({c})' for l, c in sorted(languages.items(), key=lambda x: -x[1])[:5])}
**Package managers:** {', '.join(deps) if deps else 'None detected'}
**Repository type:** {repo_type.value}

Provide a concise summary covering:

1. **Project Purpose:** What problem does this project solve? What is its primary domain?
2. **Architecture Pattern:** The overall architectural pattern(s) used (MVC, layered, microservices, etc.)
3. **Technology Stack:** Primary languages, frameworks, and major dependencies
4. **Directory Organization:** How the code is organized (by feature, by layer, etc.)
5. **Build & Run:** How is the project built, run, and tested?

Be specific to what you observe in the structure. Do NOT make assumptions about technologies not present.
"""

        content = await self._analyze_with_llm(prompt, "overview")

        return ArchSection(
            title="Overview",
            content=content,
            prompt_template="hl_overview",
        )

    async def _generate_components_section(self, repo_type: RepoType) -> ArchSection:
        """Generate components/entities section."""
        repo_structure = self._get_repo_structure_prompt()

        if repo_type == RepoType.FRONTEND:
            prompt = f"""
Act as a frontend component architect. Analyze this frontend application:

{repo_structure}

Document the component architecture:

1. **Component Organization:** Directory structure, naming conventions
2. **Core Components:** List main reusable components (layout, form, display, feedback)
3. **Component Patterns:** Presentational vs container, HOCs, hooks, composition
4. **State Management:** How state flows between components
5. **Styling Approach:** CSS strategy, theming, responsive design

Only document what is ACTUALLY present in the codebase.
"""
        elif repo_type == RepoType.BACKEND:
            prompt = f"""
Act as a backend architect. Analyze this backend service:

{repo_structure}

Document the core entities and services:

1. **Domain Entities:** Core business objects and their relationships
2. **Service Layer:** Main services and their responsibilities
3. **API Layer:** Endpoints, controllers, routes
4. **Data Layer:** Repositories, models, database access patterns

Only document what is ACTUALLY present in the codebase.
"""
        else:
            prompt = f"""
Analyze the main components of this project:

{repo_structure}

Document:

1. **Core Modules:** Main modules and their purposes
2. **Public API:** Exported functions, classes, interfaces
3. **Internal Structure:** How modules are organized and connected
4. **Key Files:** Most important source files and their roles

Only document what is ACTUALLY present.
"""

        content = await self._analyze_with_llm(prompt, "components")

        return ArchSection(
            title="Components & Entities",
            content=content,
            prompt_template="core_entities",
        )

    async def _generate_data_section(self, repo_type: RepoType) -> ArchSection:
        """Generate data layer section."""
        repo_structure = self._get_repo_structure_prompt()

        prompt = f"""
Act as a data architect. Analyze the data layer of this project:

{repo_structure}

Document only components that are ACTUALLY present:

1. **Database:** Type (SQL/NoSQL), ORM/ODM, connection patterns
2. **Data Models:** Core entities, relationships, schema
3. **Data Access:** Repositories, query patterns, CRUD operations
4. **Caching:** Cache providers, strategies, invalidation
5. **Data Validation:** Schema validation, business rules

Skip any sections that are not implemented in this codebase.
"""

        content = await self._analyze_with_llm(prompt, "data_layer")

        return ArchSection(
            title="Data Layer",
            content=content,
            prompt_template="data_layer",
        )

    async def _generate_dependencies_section(self) -> ArchSection:
        """Generate dependencies section."""
        deps = self._get_dependencies()
        repo_structure = self._get_repo_structure_prompt()

        prompt = f"""
Analyze the dependencies and external integrations of this project:

{repo_structure}

**Detected package managers:** {', '.join(deps) if deps else 'None'}

Document:

1. **Core Dependencies:** Main libraries and frameworks used
2. **Development Dependencies:** Build tools, testing frameworks, linters
3. **External Services:** APIs, databases, cloud services integrated
4. **Configuration:** How dependencies are configured

Be specific to what you can observe from the structure.
"""

        content = await self._analyze_with_llm(prompt, "dependencies")

        return ArchSection(
            title="Dependencies & Integrations",
            content=content,
            prompt_template="dependencies",
        )

    def _generate_mermaid_diagram(self, repo_type: RepoType) -> str:
        """Generate a Mermaid architecture diagram."""
        tree = self._build_file_tree(max_depth=2)

        nodes = []
        edges = []

        # Root node
        root_name = self.repo_path.name
        nodes.append(f'    root["{root_name}"]')

        for name, value in sorted(tree.items())[:10]:
            node_id = name.replace(".", "_").replace("-", "_").replace(" ", "_")
            if isinstance(value, dict):
                nodes.append(f'    {node_id}["{name}/"]')
            else:
                nodes.append(f'    {node_id}["{name}"]')
            edges.append(f"    root --> {node_id}")

        return f"""```mermaid
graph TD
{chr(10).join(nodes)}
{chr(10).join(edges)}
```"""

    async def generate(self, use_cache: bool = True) -> ArchDocument:
        """
        Generate architecture documentation.

        Args:
            use_cache: Whether to use cached results if available

        Returns:
            Generated ArchDocument
        """
        git_sha = self._get_git_sha()

        # Check cache
        if use_cache:
            cached = await self.cache.get(self.repo_path, git_sha)
            if cached:
                logger.info(f"Using cached document for {self.repo_path}")
                return cached

        logger.info(f"Generating architecture docs for {self.repo_path}")

        # Detect repo type
        repo_type = self.detector.detect()

        # Gather metadata
        languages = self._detect_languages()
        dependencies = self._get_dependencies()

        # Generate sections concurrently
        sections_tasks = [
            self._generate_overview_section(repo_type),
            self._generate_components_section(repo_type),
        ]

        # Add data section for backend/data pipeline repos
        if repo_type in (RepoType.BACKEND, RepoType.DATA_PIPELINE):
            sections_tasks.append(self._generate_data_section(repo_type))

        sections_tasks.append(self._generate_dependencies_section())

        sections = await asyncio.gather(*sections_tasks)

        # Add mermaid diagram to overview
        if self.config.include_mermaid:
            mermaid = self._generate_mermaid_diagram(repo_type)
            sections[0].mermaid_diagram = mermaid

        doc = ArchDocument(
            title=f"Architecture: {self.repo_path.name}",
            repo_type=repo_type,
            description=f"Auto-generated architecture documentation for {self.repo_path.name}",
            sections=list(sections),
            generated_at=datetime.utcnow(),
            git_sha=git_sha,
            repo_path=str(self.repo_path),
            languages=languages,
            dependencies=dependencies,
        )

        # Cache the result
        await self.cache.set(self.repo_path, doc, git_sha)

        return doc

    async def generate_and_save(self, use_cache: bool = True) -> str:
        """
        Generate and save architecture document.

        Returns:
            Path to the generated file
        """
        doc = await self.generate(use_cache=use_cache)
        content = doc.to_markdown()

        self.output_path.write_text(content)
        logger.info(f"Saved architecture doc to {self.output_path}")

        return str(self.output_path)


async def generate_architecture_docs(
    repo_path: str | Path,
    output_path: str | Path | None = None,
    use_cache: bool = True,
    config: GenerationConfig | None = None,
) -> str:
    """
    Generate architecture documentation for a repository.

    Args:
        repo_path: Path to repository
        output_path: Output path for .arch.md file
        use_cache: Whether to use cached results
        config: Generation configuration

    Returns:
        Path to generated file
    """
    generator = RepoSwarmGenerator(repo_path, output_path, config)
    return await generator.generate_and_save(use_cache=use_cache)
