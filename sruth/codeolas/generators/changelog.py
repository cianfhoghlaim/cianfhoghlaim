"""
Changelog generator for códeolas.

Stub implementation. A real implementation would diff the git log between
two refs and format the result as markdown. The placeholder keeps the
public API surface (`ChangelogGenerator`) so existing call sites
(`CodebaseAnalyzer.generate_changelog`) and tests can import it without
breaking.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class ChangelogGenerator:
    """
    Generate a markdown changelog from git history.

    Args:
        repo_path: Path to the git repository to summarize.

    Example:
        >>> gen = ChangelogGenerator(Path("."))
        >>> md = await gen.generate(from_tag="v0.1.0", to_tag="HEAD")
    """

    def __init__(self, repo_path: Path | str):
        self.repo_path = Path(repo_path)

    async def generate(
        self,
        from_tag: str | None = None,
        to_tag: str | None = "HEAD",
    ) -> str:
        """
        Build a markdown changelog between two refs.

        The current implementation returns an empty stub. A real
        implementation would shell out to `git log` and group commits
        by conventional-commit type.
        """
        logger.info(
            "ChangelogGenerator.generate() is a stub. "
            "from_tag=%s to_tag=%s",
            from_tag,
            to_tag,
        )
        return "# Changelog\n\n_Stub: changelog generation not yet implemented._\n"

    def get_stats(self) -> dict[str, Any]:
        """Return basic statistics about the generator."""
        return {
            "repo_path": str(self.repo_path),
            "implementation": "stub",
        }


__all__ = ["ChangelogGenerator"]
