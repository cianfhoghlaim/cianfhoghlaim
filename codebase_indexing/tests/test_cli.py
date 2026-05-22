"""Tests for CLI commands."""

import subprocess
import sys
from pathlib import Path

import pytest


class TestCLIHelp:
    """Tests for CLI help output."""

    def test_main_help(self):
        """Test that main help works."""
        result = subprocess.run(
            [sys.executable, "-m", "codeolas.cli", "--help"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        assert result.returncode == 0
        assert "codeolas" in result.stdout.lower()
        assert "index" in result.stdout
        assert "search" in result.stdout

    def test_index_help(self):
        """Test index command help."""
        result = subprocess.run(
            [sys.executable, "-m", "codeolas.cli", "index", "--help"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        assert result.returncode == 0
        assert "--force" in result.stdout or "-f" in result.stdout

    def test_search_help(self):
        """Test search command help."""
        result = subprocess.run(
            [sys.executable, "-m", "codeolas.cli", "search", "--help"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        assert result.returncode == 0
        assert "--limit" in result.stdout or "-n" in result.stdout

    def test_research_help(self):
        """Test research command help."""
        result = subprocess.run(
            [sys.executable, "-m", "codeolas.cli", "research", "--help"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        assert result.returncode == 0
        assert "--max-sources" in result.stdout

    def test_arch_help(self):
        """Test arch command help."""
        result = subprocess.run(
            [sys.executable, "-m", "codeolas.cli", "arch", "--help"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        assert result.returncode == 0
        assert "--output" in result.stdout or "-o" in result.stdout


class TestCLIStats:
    """Tests for stats command (no indexing required)."""

    def test_stats_command(self, codesola_root, tmp_path, monkeypatch):
        """Test stats command output."""
        import os

        # Set temp storage
        monkeypatch.setenv("LANCEDB_URI", str(tmp_path / "lancedb"))

        result = subprocess.run(
            [sys.executable, "-m", "codeolas.cli", "--repo", str(codesola_root), "stats"],
            capture_output=True,
            text=True,
            cwd=codesola_root,
            env={**os.environ, "LANCEDB_URI": str(tmp_path / "lancedb")},
        )

        # Stats should work even without indexing
        assert "repo_path" in result.stdout or result.returncode == 0


@pytest.mark.integration
class TestCLIIndex:
    """Tests for index command."""

    def test_index_codebase(self, codesola_root, tmp_path):
        """Test indexing via CLI."""
        import os

        result = subprocess.run(
            [sys.executable, "-m", "codeolas.cli", "--repo", str(codesola_root), "index"],
            capture_output=True,
            text=True,
            cwd=codesola_root,
            env={**os.environ, "LANCEDB_URI": str(tmp_path / "lancedb")},
            timeout=120,  # Allow up to 2 minutes for indexing
        )

        assert result.returncode == 0
        assert "Indexed" in result.stdout or "files" in result.stdout.lower()


@pytest.mark.integration
class TestCLISearch:
    """Tests for search command (requires indexed data)."""

    def test_search_no_results(self, codesola_root, tmp_path):
        """Test search with no indexed data."""
        import os

        # First index
        subprocess.run(
            [sys.executable, "-m", "codeolas.cli", "--repo", str(codesola_root), "index"],
            capture_output=True,
            text=True,
            cwd=codesola_root,
            env={**os.environ, "LANCEDB_URI": str(tmp_path / "lancedb")},
            timeout=120,
        )

        # Then search
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "codeolas.cli",
                "--repo",
                str(codesola_root),
                "search",
                "xyznonexistent123",
                "--limit",
                "5",
            ],
            capture_output=True,
            text=True,
            cwd=codesola_root,
            env={**os.environ, "LANCEDB_URI": str(tmp_path / "lancedb")},
        )

        # Should complete without error
        assert result.returncode == 0


class TestCLIParsing:
    """Tests for CLI argument parsing."""

    def test_no_command_shows_help(self):
        """Test that running without command shows help."""
        result = subprocess.run(
            [sys.executable, "-m", "codeolas.cli"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        # Should exit with error or show help
        assert result.returncode != 0 or "usage" in result.stdout.lower()

    def test_invalid_command(self):
        """Test that invalid command fails gracefully."""
        result = subprocess.run(
            [sys.executable, "-m", "codeolas.cli", "invalidcmd"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        # Should fail
        assert result.returncode != 0

    def test_verbose_flag(self):
        """Test that verbose flag is accepted."""
        result = subprocess.run(
            [sys.executable, "-m", "codeolas.cli", "-v", "--help"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        assert result.returncode == 0
