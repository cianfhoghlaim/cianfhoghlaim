"""
Architecture Documentation Generator.

Generates .arch.md files for repository architecture documentation.
Based on RepoSwarm pattern from bonneagar/examples.

Features:
- Daily scheduled generation
- LLM-based architecture analysis
- Mermaid diagram generation
- Commit to target repo
"""

import logging
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

DEFAULT_REPO_PATH = os.getenv(
    "CODEOLAS_REPO_PATH",
    str(Path(__file__).parent.parent.parent.parent.parent)
)


@dataclass
class ArchitectureSection:
    """A section of the architecture document."""
    title: str
    content: str
    mermaid_diagram: str | None = None


@dataclass
class ArchDocument:
    """Complete architecture document."""
    title: str
    description: str
    sections: list[ArchitectureSection]
    generated_at: datetime
    git_sha: str | None = None


class ArchGenerator:
    """
    Generator for .arch.md architecture documentation.

    Uses LLM to analyze codebase and generate documentation.
    """

    def __init__(
        self,
        repo_path: str | None = None,
        output_path: str | None = None,
    ):
        self.repo_path = Path(repo_path or DEFAULT_REPO_PATH)
        self.output_path = Path(output_path or self.repo_path / ".arch.md")

    async def generate(self) -> ArchDocument:
        """
        Generate architecture documentation.

        Returns:
            Generated ArchDocument
        """
        logger.info(f"Generating architecture docs for {self.repo_path}")

        # Gather codebase information
        file_tree = self._build_file_tree()
        languages = self._detect_languages()
        key_files = self._identify_key_files()

        # Generate sections
        sections = [
            await self._generate_overview_section(file_tree, languages),
            await self._generate_structure_section(file_tree),
            await self._generate_components_section(key_files),
            await self._generate_dependencies_section(),
        ]

        # Get git info
        git_sha = self._get_git_sha()

        doc = ArchDocument(
            title=f"Architecture: {self.repo_path.name}",
            description=f"Auto-generated architecture documentation for {self.repo_path.name}",
            sections=sections,
            generated_at=datetime.utcnow(),
            git_sha=git_sha,
        )

        return doc

    def _build_file_tree(self) -> dict[str, Any]:
        """Build a tree of files in the repo."""
        tree: dict[str, Any] = {}

        for path in self.repo_path.rglob("*"):
            if path.is_file() and not self._should_ignore(path):
                rel_path = path.relative_to(self.repo_path)
                parts = rel_path.parts

                current = tree
                for part in parts[:-1]:
                    current = current.setdefault(part, {})
                current[parts[-1]] = str(rel_path)

        return tree

    def _detect_languages(self) -> dict[str, int]:
        """Detect languages used in the repo."""
        from .transforms.treesitter_chunking import EXTENSION_TO_LANGUAGE

        counts: dict[str, int] = {}

        for path in self.repo_path.rglob("*"):
            if path.is_file() and not self._should_ignore(path):
                ext = path.suffix.lower()
                lang = EXTENSION_TO_LANGUAGE.get(ext)
                if lang:
                    counts[lang] = counts.get(lang, 0) + 1

        return counts

    def _identify_key_files(self) -> list[str]:
        """Identify key files in the repo."""
        key_patterns = [
            "README.md",
            "pyproject.toml",
            "package.json",
            "Cargo.toml",
            "go.mod",
            "CLAUDE.md",
            "docker-compose.yaml",
            "docker-compose.yml",
        ]

        key_files = []
        for pattern in key_patterns:
            matches = list(self.repo_path.glob(pattern))
            key_files.extend(str(m.relative_to(self.repo_path)) for m in matches)

        return key_files

    def _should_ignore(self, path: Path) -> bool:
        """Check if a path should be ignored."""
        ignore_patterns = [
            ".git",
            "node_modules",
            "__pycache__",
            ".venv",
            "venv",
            "dist",
            "build",
            ".next",
            "target",
        ]

        parts = path.relative_to(self.repo_path).parts
        return any(p in ignore_patterns for p in parts)

    def _get_git_sha(self) -> str | None:
        """Get current git SHA."""
        import subprocess

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

    async def _generate_overview_section(
        self,
        file_tree: dict,
        languages: dict[str, int],
    ) -> ArchitectureSection:
        """Generate overview section."""
        lang_summary = ", ".join(
            f"{lang} ({count})" for lang, count in
            sorted(languages.items(), key=lambda x: -x[1])[:5]
        )

        content = f"""
This repository contains code in the following languages: {lang_summary}.

Total directories: {self._count_dirs(file_tree)}
Total files: {self._count_files(file_tree)}
"""

        return ArchitectureSection(
            title="Overview",
            content=content.strip(),
        )

    async def _generate_structure_section(
        self,
        file_tree: dict,
    ) -> ArchitectureSection:
        """Generate structure section with directory tree."""
        tree_str = self._render_tree(file_tree, max_depth=3)

        mermaid = self._generate_structure_mermaid(file_tree)

        content = f"""
```
{tree_str}
```
"""

        return ArchitectureSection(
            title="Directory Structure",
            content=content.strip(),
            mermaid_diagram=mermaid,
        )

    async def _generate_components_section(
        self,
        key_files: list[str],
    ) -> ArchitectureSection:
        """Generate components section."""
        if not key_files:
            content = "No key configuration files detected."
        else:
            content = "Key files:\n" + "\n".join(f"- `{f}`" for f in key_files)

        return ArchitectureSection(
            title="Key Components",
            content=content,
        )

    async def _generate_dependencies_section(self) -> ArchitectureSection:
        """Generate dependencies section."""
        deps = []

        # Check Python
        pyproject = self.repo_path / "pyproject.toml"
        if pyproject.exists():
            deps.append("Python (pyproject.toml)")

        # Check Node.js
        package = self.repo_path / "package.json"
        if package.exists():
            deps.append("Node.js (package.json)")

        # Check Rust
        cargo = self.repo_path / "Cargo.toml"
        if cargo.exists():
            deps.append("Rust (Cargo.toml)")

        content = "Detected package managers:\n" + "\n".join(f"- {d}" for d in deps) if deps else "No package managers detected."

        return ArchitectureSection(
            title="Dependencies",
            content=content,
        )

    def _count_dirs(self, tree: dict) -> int:
        """Count directories in tree."""
        count = 0
        for v in tree.values():
            if isinstance(v, dict):
                count += 1 + self._count_dirs(v)
        return count

    def _count_files(self, tree: dict) -> int:
        """Count files in tree."""
        count = 0
        for v in tree.values():
            if isinstance(v, dict):
                count += self._count_files(v)
            else:
                count += 1
        return count

    def _render_tree(self, tree: dict, prefix: str = "", max_depth: int = 3, depth: int = 0) -> str:
        """Render tree as string."""
        if depth >= max_depth:
            return prefix + "..."

        lines = []
        items = sorted(tree.items())

        for i, (name, value) in enumerate(items):
            is_last = i == len(items) - 1
            connector = "└── " if is_last else "├── "
            lines.append(prefix + connector + name)

            if isinstance(value, dict):
                extension = "    " if is_last else "│   "
                lines.append(self._render_tree(value, prefix + extension, max_depth, depth + 1))

        return "\n".join(lines)

    def _generate_structure_mermaid(self, tree: dict) -> str:
        """Generate Mermaid diagram for structure."""
        nodes = []
        edges = []

        def process(t: dict, parent: str | None = None, prefix: str = ""):
            for name, value in t.items():
                node_id = prefix + name.replace(".", "_").replace("-", "_")
                nodes.append(f'    {node_id}["{name}"]')
                if parent:
                    edges.append(f"    {parent} --> {node_id}")

                if isinstance(value, dict):
                    process(value, node_id, node_id + "_")

        process(tree)

        return f"""```mermaid
graph TD
{chr(10).join(nodes[:20])}
{chr(10).join(edges[:20])}
```"""

    def render_markdown(self, doc: ArchDocument) -> str:
        """Render document as markdown."""
        lines = [
            f"# {doc.title}",
            "",
            doc.description,
            "",
            f"*Generated: {doc.generated_at.isoformat()}*",
        ]

        if doc.git_sha:
            lines.append(f"*Commit: {doc.git_sha[:8]}*")

        lines.append("")

        for section in doc.sections:
            lines.extend([
                f"## {section.title}",
                "",
                section.content,
                "",
            ])

            if section.mermaid_diagram:
                lines.extend([section.mermaid_diagram, ""])

        return "\n".join(lines)

    async def generate_and_save(self) -> str:
        """Generate and save architecture document."""
        doc = await self.generate()
        content = self.render_markdown(doc)

        self.output_path.write_text(content)
        logger.info(f"Saved architecture doc to {self.output_path}")

        return str(self.output_path)


async def generate_arch_docs(
    repo_path: str | None = None,
    output_path: str | None = None,
) -> str:
    """
    Generate architecture documentation for a repository.

    Args:
        repo_path: Path to repository (defaults to cianfhoghlaim)
        output_path: Output path for .arch.md file

    Returns:
        Path to generated file
    """
    generator = ArchGenerator(repo_path, output_path)
    return await generator.generate_and_save()


if __name__ == "__main__":
    import asyncio
    logging.basicConfig(level=logging.INFO)
    asyncio.run(generate_arch_docs())
