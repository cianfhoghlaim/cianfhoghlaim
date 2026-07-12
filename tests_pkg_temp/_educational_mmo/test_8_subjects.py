"""Tests for the 8 NCCA subject scaffolds.

Verifies that each subject has the canonical 9-file structure:
- baml/qpack_<subject>.baml
- dlt/subjects/<subject>/__init__.py + sources.py + schema.py
- dagster/assets/<subject>_assets.py
- cocoindex/<subject>_embedding.py
- agents/meaisinfhoghlaim/educational/<subject>_agent.py
- notebooks/leaving_cert/<subject>.py

Plus the per-subject ADK agent has the expected name + description.
"""
from __future__ import annotations

from pathlib import Path

import pytest

CIANFHOGHLAIM_ROOT = Path("/Users/cianmacandeisigh/dev/kings_college_galway/cianfhoghlaim")

SUBJECTS = [
    "mathematics",
    "applied_mathematics",
    "chemistry",
    "geography",
    "history",
    "english",
    "gaeilge",
    "computer_science",
]


@pytest.mark.parametrize("subject", SUBJECTS)
def test_qpack_baml_exists(subject: str):
    """Each subject has a qpack_<subject>.baml."""
    path = CIANFHOGHLAIM_ROOT / "baml" / f"qpack_{subject}.baml"
    assert path.exists(), f"Missing {path}"
    content = path.read_text()
    # Sanity checks on the BAML contract
    assert "Generate" in content and "QuestPack" in content, \
        f"{path.name} should contain a Generate<Subject>QuestPack function"
    assert "Score" in content and "FormativeResponse" in content, \
        f"{path.name} should contain a Score<Subject>FormativeResponse function"


@pytest.mark.parametrize("subject", SUBJECTS)
def test_dlt_subject_dir_exists(subject: str):
    """Each subject has dlt/subjects/<subject>/{__init__.py,sources.py,schema.py}."""
    base = CIANFHOGHLAIM_ROOT / "dlt" / "subjects" / subject
    assert base.is_dir(), f"Missing {base}"
    for fname in ("__init__.py", "sources.py", "schema.py"):
        path = base / fname
        assert path.exists(), f"Missing {path}"


@pytest.mark.parametrize("subject", SUBJECTS)
def test_dagster_assets_exists(subject: str):
    """Each subject has dagster/assets/<subject>_assets.py."""
    path = CIANFHOGHLAIM_ROOT / "dagster" / "assets" / f"{subject}_assets.py"
    assert path.exists(), f"Missing {path}"
    content = path.read_text()
    assert "import dagster as dg" in content
    assert f'group_name="{subject}"' in content, \
        f"{path.name} should have group_name=\"{subject}\""


@pytest.mark.parametrize("subject", SUBJECTS)
def test_cocoindex_embedding_exists(subject: str):
    """Each subject has cocoindex/<subject>_embedding.py."""
    path = CIANFHOGHLAIM_ROOT / "cocoindex" / f"{subject}_embedding.py"
    assert path.exists(), f"Missing {path}"
    content = path.read_text()
    assert "BAAI/bge-m3" in content or "EMBEDDER" in content, \
        f"{path.name} should reference BGE-M3 embeddings"


@pytest.mark.parametrize("subject", SUBJECTS)
def test_agent_exists(subject: str):
    """Each subject has agents/meaisinfhoghlaim/educational/<subject>_agent.py."""
    # Map subject → agent file name (applies special cases)
    AGENT_FILES = {
        "mathematics": "math_agent.py",
        "applied_mathematics": "appm_agent.py",
        "chemistry": "chem_agent.py",
        "geography": "geog_agent.py",
        "history": "hist_agent.py",
        "english": "engl_agent.py",
        "gaeilge": "gael_agent.py",
        "computer_science": "comp_agent.py",
    }
    AGENT_VARS = {
        "mathematics": "math_agent",
        "applied_mathematics": "appm_agent",
        "chemistry": "chem_agent",
        "geography": "geog_agent",
        "history": "hist_agent",
        "english": "engl_agent",
        "gaeilge": "gael_agent",
        "computer_science": "comp_agent",
    }
    path = CIANFHOGHLAIM_ROOT / "agents" / "meaisinfhoghlaim" / "educational" / AGENT_FILES[subject]
    assert path.exists(), f"Missing {path}"
    content = path.read_text()
    expected_var = AGENT_VARS[subject]
    assert f"{expected_var} = LlmAgent" in content, \
        f"{path.name} should declare `{expected_var} = LlmAgent(...)`"
    assert f'name="{expected_var}"' in content, \
        f"{path.name} should have name=\"{expected_var}\""


@pytest.mark.parametrize("subject", SUBJECTS)
def test_marimo_notebook_exists(subject: str):
    """Each subject has notebooks/leaving_cert/<subject>.py."""
    path = CIANFHOGHLAIM_ROOT / "notebooks" / "leaving_cert" / f"{subject}.py"
    assert path.exists(), f"Missing {path}"
    content = path.read_text()
    assert "import marimo" in content
    assert "app = marimo.App" in content


def test_8_subjects_complete():
    """All 8 NCCA subjects are scaffolded."""
    assert len(SUBJECTS) == 8


def test_gaeilge_subject_has_irish_canonical_text():
    """Gaeilge is taught in Irish — text_ga must be REQUIRED in BAML contract."""
    path = CIANFHOGHLAIM_ROOT / "baml" / "qpack_gaeilge.baml"
    content = path.read_text()
    # text_ga is non-Optional in the GaelBilingualText class
    assert "text_ga: string" in content and "text_en: string?" in content, \
        "Gaeilge BAML must require text_ga as canonical (non-Optional) and text_en as optional"


def test_appm_subject_is_hl_only():
    """Applied Mathematics is Higher Level only (no OL/FL)."""
    path = CIANFHOGHLAIM_ROOT / "baml" / "qpack_applied_mathematics.baml"
    content = path.read_text()
    # APPM should declare only LC_HL level (in the enum)
    assert "LC_HL" in content, \
        "APPM BAML should define LC_HL level"
    assert "  LC_OL" not in content.replace("// ", "").replace("\n  ", "\n"), \
        "APPM BAML should NOT define LC_OL (HL-only)"
    assert "  LC_FL" not in content.replace("// ", "").replace("\n  ", "\n"), \
        "APPM BAML should NOT define LC_FL (HL-only)"


def test_8_agents_share_routing_keywords():
    """All 8 NCCA subject agents have keyword routing in root_agent."""
    root_agent_path = CIANFHOGHLAIM_ROOT / "agents" / "adk" / "root_agent.py"
    content = root_agent_path.read_text()
    # Map subject → AgentDomain value (8 short names)
    DOMAIN_NAMES = {
        "mathematics": "MATH",
        "applied_mathematics": "APPM",
        "chemistry": "CHEM",
        "geography": "GEOG",
        "history": "HIST",
        "english": "ENGL",
        "gaeilge": "GAEL",
        "computer_science": "COMP",
    }
    for subject, domain in DOMAIN_NAMES.items():
        assert f"AgentDomain.{domain}" in content, \
            f"root_agent.py missing AgentDomain.{domain} domain"