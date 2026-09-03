"""
Type definitions for RepoSwarm doc generator.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any


class RepoType(str, Enum):
    """Repository type classification."""

    BACKEND = "backend"
    FRONTEND = "frontend"
    LIBRARY = "library"
    MONOREPO = "monorepo"
    DATA_PIPELINE = "data_pipeline"
    INFRASTRUCTURE = "infrastructure"
    GENERIC = "generic"


@dataclass
class ArchSection:
    """A section of the architecture document."""

    title: str
    content: str
    prompt_template: str | None = None
    mermaid_diagram: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ArchDocument:
    """Complete architecture document."""

    title: str
    repo_type: RepoType
    description: str
    sections: list[ArchSection]
    generated_at: datetime
    git_sha: str | None = None
    repo_path: str | None = None
    languages: dict[str, int] = field(default_factory=dict)
    dependencies: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_markdown(self) -> str:
        """Render document as markdown."""
        lines = [
            f"# {self.title}",
            "",
            f"> {self.description}",
            "",
            f"**Type:** {self.repo_type.value}",
            f"**Generated:** {self.generated_at.isoformat()}",
        ]

        if self.git_sha:
            lines.append(f"**Commit:** `{self.git_sha[:8]}`")

        if self.languages:
            lang_str = ", ".join(
                f"{lang} ({count})"
                for lang, count in sorted(self.languages.items(), key=lambda x: -x[1])[:5]
            )
            lines.append(f"**Languages:** {lang_str}")

        lines.append("")
        lines.append("---")
        lines.append("")

        # Table of contents
        lines.append("## Table of Contents")
        lines.append("")
        for i, section in enumerate(self.sections, 1):
            anchor = section.title.lower().replace(" ", "-").replace("&", "and")
            lines.append(f"{i}. [{section.title}](#{anchor})")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Sections
        for section in self.sections:
            lines.append(f"## {section.title}")
            lines.append("")
            lines.append(section.content)
            lines.append("")

            if section.mermaid_diagram:
                lines.append(section.mermaid_diagram)
                lines.append("")

        return "\n".join(lines)


@dataclass
class GenerationConfig:
    """Configuration for document generation."""

    # LLM settings
    model: str = "claude-3-5-sonnet-20241022"
    max_tokens: int = 4096
    temperature: float = 0.3

    # Generation settings
    max_file_depth: int = 5
    include_file_contents: bool = True
    max_files_per_section: int = 20
    max_content_per_file: int = 5000

    # Output settings
    output_format: str = "markdown"
    include_mermaid: bool = True
    include_toc: bool = True


@dataclass
class CacheConfig:
    """Configuration for caching."""

    enabled: bool = True
    ttl_hours: int = 24
    db_path: str | Path = ".arch_cache.duckdb"
    table_name: str = "arch_docs"
