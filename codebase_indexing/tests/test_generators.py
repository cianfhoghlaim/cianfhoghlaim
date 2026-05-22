"""Tests for documentation generation."""

from pathlib import Path

import pytest


@pytest.mark.integration
class TestArchDocGeneration:
    """Tests for .arch.md architecture document generation."""

    async def test_generate_arch_doc_basic(self, indexed_analyzer, tmp_path):
        """Test basic architecture doc generation."""
        content = await indexed_analyzer.generate_arch_doc()

        assert content is not None
        assert len(content) > 0
        assert isinstance(content, str)

    async def test_generate_arch_doc_has_headers(self, indexed_analyzer):
        """Test that generated doc has markdown headers."""
        content = await indexed_analyzer.generate_arch_doc()

        assert "#" in content, "Should have markdown headers"

    async def test_generate_arch_doc_write_to_file(self, indexed_analyzer, tmp_path):
        """Test writing arch doc to file."""
        output_path = tmp_path / "ARCHITECTURE.md"

        content = await indexed_analyzer.generate_arch_doc(output_path=str(output_path))

        assert output_path.exists()
        assert output_path.read_text() == content

    async def test_generate_arch_doc_mentions_package(self, indexed_analyzer):
        """Test that arch doc mentions the package name."""
        content = await indexed_analyzer.generate_arch_doc()

        # Should mention codeolas or the package structure
        content_lower = content.lower()
        assert any(
            term in content_lower for term in ["codeolas", "core", "search", "storage"]
        ), "Should mention package components"


@pytest.mark.integration
class TestChangelogGeneration:
    """Tests for changelog generation."""

    async def test_generate_changelog_basic(self, codesola_root):
        """Test basic changelog generation."""
        from codeolas.generators.changelog import ChangelogGenerator

        generator = ChangelogGenerator(codesola_root)
        changelog = await generator.generate(from_tag="HEAD~5", to_tag="HEAD")

        assert isinstance(changelog, str)

    async def test_generate_changelog_empty_range(self, codesola_root):
        """Test changelog with no commits in range."""
        from codeolas.generators.changelog import ChangelogGenerator

        generator = ChangelogGenerator(codesola_root)
        # HEAD~0 to HEAD is effectively empty
        changelog = await generator.generate(from_tag="HEAD", to_tag="HEAD")

        assert isinstance(changelog, str)


@pytest.mark.integration
class TestDocDriftDetection:
    """Tests for documentation drift detection."""

    async def test_check_doc_drift_returns_list(self, indexed_analyzer):
        """Test that doc drift check returns a list."""
        drift_issues = await indexed_analyzer.check_doc_drift()

        assert isinstance(drift_issues, list)


class TestArchGeneratorUnit:
    """Unit tests for ArchGenerator."""

    def test_arch_generator_init(self, codesola_root):
        """Test ArchGenerator initialization."""
        from codeolas.generators.arch import ArchGenerator

        generator = ArchGenerator(codesola_root)
        assert generator.repo_path == codesola_root

    def test_arch_generator_with_string_path(self):
        """Test ArchGenerator with string path."""
        from codeolas.generators.arch import ArchGenerator

        generator = ArchGenerator("/tmp/test")
        assert generator.repo_path == Path("/tmp/test")


class TestChangelogGeneratorUnit:
    """Unit tests for ChangelogGenerator."""

    def test_changelog_generator_init(self, codesola_root):
        """Test ChangelogGenerator initialization."""
        from codeolas.generators.changelog import ChangelogGenerator

        generator = ChangelogGenerator(codesola_root)
        assert generator.repo_path == codesola_root

    def test_changelog_generator_with_string_path(self):
        """Test ChangelogGenerator with string path."""
        from codeolas.generators.changelog import ChangelogGenerator

        generator = ChangelogGenerator("/tmp/test")
        assert generator.repo_path == Path("/tmp/test")
