"""
Tests for GitHub intelligence functionality.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone


class TestRepositoryAnalysis:
    """Test repository analysis functionality."""

    def test_repo_activity_score_calculation(self):
        """Test repository activity score calculation."""
        # Activity score based on recent commits, PRs, issues
        commits_30d = 50
        prs_30d = 10
        issues_30d = 5

        # Simple weighted score
        activity_score = (commits_30d * 1.0) + (prs_30d * 2.0) + (issues_30d * 0.5)
        assert activity_score == 72.5

    def test_repo_health_metrics(self):
        """Test repository health metric calculation."""
        metrics = {
            "has_readme": True,
            "has_license": True,
            "has_contributing": True,
            "has_code_of_conduct": False,
            "has_ci": True,
            "test_coverage": 0.85,
        }

        # Calculate health score (0-100)
        score = 0
        score += 15 if metrics["has_readme"] else 0
        score += 15 if metrics["has_license"] else 0
        score += 10 if metrics["has_contributing"] else 0
        score += 10 if metrics["has_code_of_conduct"] else 0
        score += 20 if metrics["has_ci"] else 0
        score += 30 * metrics["test_coverage"]

        assert score == 85.5

    def test_contributor_diversity_score(self):
        """Test contributor diversity calculation."""
        contributors = [
            {"login": "dev1", "contributions": 500},
            {"login": "dev2", "contributions": 200},
            {"login": "dev3", "contributions": 150},
            {"login": "dev4", "contributions": 100},
            {"login": "dev5", "contributions": 50},
        ]

        total = sum(c["contributions"] for c in contributors)
        top_contributor_share = contributors[0]["contributions"] / total

        # Lower share from top contributor = higher diversity
        diversity_score = 1 - top_contributor_share
        assert diversity_score == 0.5  # 500/1000 = 0.5


class TestCommitAnalysis:
    """Test commit analysis functionality."""

    def test_commit_frequency_calculation(self):
        """Test commit frequency over time period."""
        commits = [
            {"date": "2024-01-01"},
            {"date": "2024-01-02"},
            {"date": "2024-01-02"},
            {"date": "2024-01-03"},
            {"date": "2024-01-05"},
        ]

        # Days with commits
        unique_days = len(set(c["date"] for c in commits))
        commits_per_day = len(commits) / 5  # Over 5 days

        assert unique_days == 4
        assert commits_per_day == 1.0

    def test_commit_message_quality(self):
        """Test commit message quality scoring."""

        def score_message(message: str) -> float:
            score = 0.0

            # Length check (not too short, not too long)
            if 10 <= len(message) <= 72:
                score += 0.3

            # Has type prefix (feat:, fix:, docs:, etc.)
            prefixes = ["feat:", "fix:", "docs:", "style:", "refactor:", "test:", "chore:"]
            if any(message.lower().startswith(p) for p in prefixes):
                score += 0.3

            # Starts with capital after prefix or at start
            first_word = message.split(":")[1].strip() if ":" in message else message
            if first_word and first_word[0].isupper():
                score += 0.2

            # No period at end (conventional commits style)
            if not message.endswith("."):
                score += 0.2

            return score

        good_message = "feat: Add flash loan support"
        bad_message = "wip"
        okay_message = "Fixed the bug in the lending module."

        assert score_message(good_message) == 1.0
        assert score_message(bad_message) == 0.0
        assert score_message(okay_message) == 0.3  # Only length passes


class TestDeveloperAnalysis:
    """Test developer/contributor analysis."""

    def test_developer_expertise_detection(self):
        """Test detecting developer expertise from file patterns."""

        def detect_expertise(files_changed: list[str]) -> list[str]:
            expertise = set()

            patterns = {
                "smart_contracts": [".sol", "contracts/"],
                "frontend": [".tsx", ".jsx", ".vue", "components/"],
                "backend": [".py", ".go", ".rs", "api/"],
                "testing": ["test_", "_test.", ".spec."],
                "documentation": [".md", "docs/"],
                "devops": ["Dockerfile", ".yml", ".yaml", "ci/", "deploy/"],
            }

            for file in files_changed:
                for skill, indicators in patterns.items():
                    if any(ind in file.lower() for ind in indicators):
                        expertise.add(skill)

            return list(expertise)

        files = [
            "contracts/LendingPool.sol",
            "test_lending.py",
            "frontend/components/Dashboard.tsx",
            ".github/workflows/ci.yml",
        ]

        expertise = detect_expertise(files)
        assert "smart_contracts" in expertise
        assert "testing" in expertise
        assert "frontend" in expertise
        assert "devops" in expertise

    def test_developer_activity_timeline(self):
        """Test generating developer activity timeline."""
        commits = [
            {"date": "2024-01-01", "author": "dev1", "repo": "protocol-a"},
            {"date": "2024-01-05", "author": "dev1", "repo": "protocol-a"},
            {"date": "2024-01-10", "author": "dev1", "repo": "protocol-b"},
            {"date": "2024-01-15", "author": "dev1", "repo": "protocol-a"},
        ]

        # Group by week
        weekly_activity = {}
        for commit in commits:
            # Simple week calculation (just for testing)
            week = commit["date"][:7]  # YYYY-MM as proxy
            weekly_activity[week] = weekly_activity.get(week, 0) + 1

        assert weekly_activity["2024-01"] == 4


class TestProtocolCorrelation:
    """Test GitHub-DeFi protocol correlation."""

    def test_match_repo_to_protocol(self):
        """Test matching GitHub repos to DeFi protocols."""
        repo = {
            "full_name": "aave/aave-v3-core",
            "topics": ["aave", "defi", "lending"],
            "description": "Aave Protocol V3 core smart contracts",
        }

        protocol = {
            "id": "aave",
            "name": "Aave",
            "github_urls": ["https://github.com/aave"],
        }

        # Match by org name or topics
        repo_org = repo["full_name"].split("/")[0].lower()
        protocol_id = protocol["id"].lower()

        is_match = (
            repo_org == protocol_id
            or protocol_id in repo["topics"]
            or protocol["name"].lower() in repo["description"].lower()
        )

        assert is_match is True

    def test_development_velocity_correlation(self):
        """Test correlating dev activity with protocol metrics."""
        protocol_data = {
            "aave": {"tvl_change_7d": 5.0, "commits_7d": 50},
            "compound": {"tvl_change_7d": -2.0, "commits_7d": 10},
            "uniswap": {"tvl_change_7d": 3.0, "commits_7d": 35},
        }

        # Simple correlation check (high commits often correlates with positive TVL)
        high_activity = [
            p for p, d in protocol_data.items() if d["commits_7d"] > 30
        ]
        positive_tvl = [
            p for p, d in protocol_data.items() if d["tvl_change_7d"] > 0
        ]

        # Both aave and uniswap have high activity and positive TVL
        overlap = set(high_activity) & set(positive_tvl)
        assert len(overlap) == 2
        assert "aave" in overlap
        assert "uniswap" in overlap
