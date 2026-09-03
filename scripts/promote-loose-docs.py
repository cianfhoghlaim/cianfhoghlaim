#!/usr/bin/env python3
"""
scripts/promote-loose-docs.py
Phase 2: promote the 100 loose .md files at docs/ root into
numbered dirs, with ccc/cognee-clean frontmatter added.

Approach:
  1. Scan the 100 loose .md files at docs/ root.
  2. For each, infer the best destination numbered dir from the title
     + first paragraph using a deterministic keyword-routing table.
     (No LLM call - we keep this offline-deterministic per the
     user's "do it properly" framing.)
  3. Synthesize ccc/cognee-clean frontmatter (title from H1, domain
     matching target dir, status: stable, description from first
     paragraph, read_when, supersedes).
  4. Move the file to the target dir.
  5. Report stats: total, by-target-dir, low-confidence, skipped.

Modes:
  --dry-run    Show what would be done; don't write anything.
  --apply      Actually do it (the default if no flag given).
  --reset      Undo all prior moves (reads doc/hackathons/docs-promotion-state.json).
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_ROOT = REPO_ROOT / "docs"
STATE_FILE = REPO_ROOT / "doc" / "hackathons" / "docs-promotion-state.json"
REPORT_FILE = REPO_ROOT / "doc" / "hackathons" / "docs-promotion-2026-06-10.md"


# ---------------------------------------------------------------------
# Routing table: keyword -> (target_dir, domain)
# ---------------------------------------------------------------------
# Keywords are case-insensitive. The first match (in order) wins.
# If no keyword matches, the file lands in docs/00-core/ with
# domain=standards and a "low-confidence" flag in the report.

_ROUTING: list[tuple[str, str, str]] = [
    # (regex, target_dir, domain)
    # -- 00-core: project core
    (r"^#\s*CLAUDE\b|Cianfhoghlaim\s+context\s+library",
     "00-core", "standards"),
    (r"^#\s*CONSTRAINTS\b|^\s*critical\s+constraints",
     "00-core", "standards"),
    (r"^#\s*AGENTS\s+[-:]|AGENTS\s+-\s+Pattern",
     "00-core", "agents"),
    (r"^#\s*AGENTS\.md$",
     "00-core", "agents"),
    (r"project\s+spec|project_overview|project-conventions|project_spec|project\s+identity",
     "00-core", "standards"),
    (r"critical\s+constraints|^\s*CONSTRAINTS",
     "00-core", "standards"),
    (r"AGENTS\.md|ai\s+agent\s+instructions|agent\s+design",
     "00-core", "agents"),

    # -- 01-cognee: Cognee stack (cognify, graph, MCP) — match only
    # when the *primary topic* of the doc IS the cognee stack, not when
    # a doc merely mentions it. Keep the generic patterns ("cognif",
    # "knowledge graph") at low priority so they don't out-catch more
    # specific matches earlier in the routing table.
    (r"^#\s*COGNEE_SETUP|^#\s*COGNEE_INTEGRATION|^#\s*CCC_INTEGRATION",
     "01-cognee", "cognee"),
    (r"cognee[- ]?(architecture|setup|integration|mcp|sdk)",
     "01-cognee", "cognee"),
    (r"ccc|cocoindex[- ]?(code|readiness|setup|comprehensive)",
     "01-cognee", "cognee"),
    (r"^#\s*graphiti\b.*temporal|^#\s*Knowledge\s+Graphs\b",
     "01-cognee", "cognee"),
    (r"^#\s*Graphiti\s+Python\s+SDK\b",
     "01-cognee", "cognee"),

    # -- 01-patterns: domain-specific patterns
    (r"^#\s*BAML\b|BAML\s*[-:]|BAML\s+as\s+|Basically\s+A\s+Made",
     "01-patterns", "patterns"),
    (r"data\s+pipeline\s+pattern|data\s+pipeline\s+architecture",
     "01-patterns", "patterns"),
    (r"embedding\s+(model|pattern|strategy)",
     "01-patterns", "patterns"),
    (r"observability\s+pattern|^#\s*OBSERVABILITY",
     "01-patterns", "patterns"),
    (r"^#\s*STORAGE\b", "01-patterns", "patterns"),
    (r"^#\s*WEB\b|web\s+pattern", "01-patterns", "patterns"),

    # -- 01-platform-architecture: top-level
    (r"^#\s*Tech(nical)?\s+Blueprint|Technical\s+Blueprint\s+for",
     "01-platform-architecture", "architecture"),
    (r"^#\s*Tuath\s+System\s+Architecture|^#\s*Tuath\s+Celtic\s+Educational",
     "06-product", "product"),
    (r"^#\s*Tuath\s+Quickstart|^#\s*TUATH_?QUICKSTART",
     "06-product", "product"),
    (r"^#\s*Implementation\s+Guide|^\s*#\s*Implementation\s+Guide\s+&",
     "08-examples", "examples"),
    (r"^#\s*Subject[- ]?Specific\s+Implementations",
     "08-examples", "examples"),
    (r"^#\s*BEADS\s+TRACKER|^#\s*Beads\s+Tracker|^#\s*Beads\b.*issue\s+tracking",
     "08-examples", "examples"),
    (r"^#\s*Frontend\s+Stack|^#\s*TanStack|^#\s*Convex\s+Hono",
     "05-web", "web"),
    (r"^#\s*Pattern:\s+Web|web\s+pattern|Web\s+Frameworks",
     "01-patterns", "patterns"),
    (r"^#\s*Pattern:\s+Observability|^\s*Observability\b",
     "01-patterns", "patterns"),
    (r"^#\s*Pattern:\s+Embeddings|^#\s*Pattern:\s+Data\s+Pipeline",
     "01-patterns", "patterns"),
    (r"^#\s*Irish\s+EdTech\s+Platform|^#\s*Irish\s*\(Gaeilge\)\s+Language",
     "05-celtic-language", "celtic_language"),
    (r"^#\s*Meais.+\s*-\s*ML\s+Models|Meais.nfhoghlaim",
     "04-ai-ml", "ai_ml"),
    (r"^#\s*ML\s+Stack|ML\s+stack",
     "04-ai-ml", "ai_ml"),
    (r"^#\s*ML\s+MODELS_REGISTRY|ML_MODELS_REGISTRY",
     "04-ai-ml", "ai_ml"),
    (r"^#\s*Comprehensive\s+AI/ML\s+Systems|ML_?SYSTEMS\b",
     "04-ai-ml", "ai_ml"),
    (r"^#\s*Model\s+Fine-?Tuning|Fine-?Tuning\s+Strategy",
     "04-ai-ml", "ai_ml"),
    (r"^#\s*Babylon\.js",
     "06-product", "product"),
    (r"^#\s*Cloudflare\s+R2",
     "06-infrastructure", "infrastructure"),
    (r"^#\s*Lower\s+Socioeconomic",
     "00-core", "standards"),
    (r"^name:\s+oideachas-pipeline",
     "05-celtic-language", "celtic_language"),
    (r"^name:\s+ml-stack",
     "04-ai-ml", "ai_ml"),
    (r"^#\s*Helsinki\s+OPUS",
     "05-celtic-language", "celtic_language"),
    (r"^#\s*Google\s+ADK\b",
     "03-agents", "agents"),
    (r"^name:\s+cocoindex|^name:\s+baml|^name:\s+dagster|^name:\s+dlt",
     "07-skills", "skills"),
    (r"^name:\s+duckdb|^name:\s+lancedb|^name:\s+neo4j|^name:\s+memgraph",
     "07-skills", "skills"),
    (r"^name:\s+graphiti|^name:\s+unsloth|^name:\s+trl|^name:\s+ragas",
     "07-skills", "skills"),
    (r"^name:\s+sqlmesh|^name:\s+ducklake",
     "07-skills", "skills"),
    (r"^name:\s+hono|^name:\s+tanstack-start|^name:\s+copilotkit",
     "07-skills", "skills"),
    (r"^name:\s+crawl4ai-sdk|^name:\s+patchright|^name:\s+stagehand|^name:\s+modal|^name:\s+marimo",
     "07-skills", "skills"),
    (r"^name:\s+pydantic-ai|^name:\s+agno|^name:\s+google-adk|^name:\s+cognee-sdk|^name:\s+graphiti-sdk",
     "07-skills", "skills"),
    (r"^name:\s+dagster-sdk|^name:\s+helsinki-opus-mt|^name:\s+nllb-200|^name:\s+m2m-100",
     "07-skills", "skills"),
    (r"^name:\s+wav2vec2-xlsr-irish|^name:\s+whisper-faster-whisper|^name:\s+chatterbox|^name:\s+bge-m3|^name:\s+gabert",
     "07-skills", "skills"),
    (r"^#\s*OPENSPEC\b|^#\s*openspec",
     "07-standards", "standards"),
    (r"platform\s+overview|monorepo",
     "01-platform-architecture", "architecture"),
    (r"infrastructure[- ]?stacks|pangolin|komodo[- ]?gitops",
     "01-platform-architecture", "architecture"),
    (r"secrets\s+management|infisical|locket",
     "01-platform-architecture", "architecture"),
    (r"kubernetes|talos|deployment",
     "01-platform-architecture", "architecture"),

    # -- 02-architecture: high-level architecture
    (r"EDUCATION_ARCHITECTURE|^#\s*OIDEACHAIS\b|OIDEACHAIS\s+(SPEC|PIPELINE)",
     "02-architecture", "architecture"),
    (r"OIDEACHAIS\b.*pipeline|^#\s*SRUTH\b|^#\s*ALEYUM\b|^#\s*TUATH_?MMO\b|^#\s*ML_?SYSTEMS",
     "02-architecture", "architecture"),
    (r"^#\s*Document\s+Processing\s+Pipeline",
     "06-infrastructure", "infrastructure"),
    (r"^#\s*DOCUMENT_PROCESSING|^#\s*AGENT_IMPLEMENTATIONS\b|MULTI_AGENT_PRODUCTION",
     "02-architecture", "architecture"),

    # -- 02-audit: 2026-06-06 retrospective
    (r"consolidation\s+plan|retrospective|readiness\s+audit|^#\s*TODO_AUDIT",
     "02-audit", "audit"),
    (r"agent_skill_consumability|consumability",
     "02-audit", "audit"),

    # -- 02-data-platform: Dagster, DLT, lakehouse
    (r"^#\s*Data\s+Architecture|^#\s*DATA_ARCHITECTURE\b|^#\s*DATA_PIPELINE\b|sqlmesh|ducklake|olake|iceberg",
     "02-data-platform", "data_platform"),
    (r"^#\s*Dagster\b|^#\s*DLT\b|^#\s*duckdb|^#\s*dagster[- ]sdk|^#\s*DuckDB\b|^#\s*Data\s+Pipeline\b",
     "02-data-platform", "data_platform"),

    # -- 03-agents: agent frameworks
    (r"^#\s*agno\b|^#\s*google-adk\b|^#\s*pydantic-ai\b|^#\s*copilotkit\b|agent\s+framework",
     "03-agents", "agents"),
    (r"^#\s*stagehand\b|^#\s*patchright\b|^#\s*colpali\b|^#\s*crawl4ai",
     "03-agents", "agents"),
    (r"^#\s*AG-?UI\b|^#\s*ag-ui\b|AGENTIC\s+(EDUCATION|TRANSLATION|CRYPTO|WEB)",
     "03-agents", "agents"),
    (r"^#\s*MCP_RESEARCH|model\s+context\s+protocol",
     "03-agents", "agents"),

    # -- 03-pipelines: pipeline code-as-doc
    (r"^#\s*ag_ui_protocol|^#\s*api_main|orchestrator|api\.main",
     "03-pipelines", "pipelines"),
    (r"^#\s*curriculum_embedding|dagster_definitions|dagster_factories",
     "03-pipelines", "pipelines"),
    (r"^#\s*storage_init|^#\s*observability_init",
     "03-pipelines", "pipelines"),

    # -- 04-ai-ml: ML/AI
    (r"^#\s*MODEL_FINETUNING|^#\s*MODEL_TRAINING|^#\s*unsloth\b|^#\s*lora",
     "04-ai-ml", "ai_ml"),
    (r"^#\s*trl|^#\s*ML_?MODELS_REGISTRY|^#\s*ML_?STACK|^#\s*ML_?SYSTEMS",
     "04-ai-ml", "ai_ml"),
    (r"^#\s*EMBEDDINGS|^#\s*ragas\b|^#\s*colpali\b",
     "04-ai-ml", "ai_ml"),
    (r"^#\s*wav2vec2|^#\s*whisper|^#\s*chatterbox\b|^#\s*helsinki-opus-mt",
     "04-ai-ml", "ai_ml"),
    (r"^#\s*nllb-200|^#\s*m2m-100|^#\s*bge-m3|^#\s*gabert",
     "04-ai-ml", "ai_ml"),
    (r"^#\s*AI_?ML_?PIPELINE|ai_?ml_?pipeline",
     "04-ai-ml", "ai_ml"),
    (r"OCR|HTR|gaelic|manuscript",
     "04-ai-ml", "ai_ml"),
    (r"^#\s*MODAL\b|modal\.com|modal\s+labs",
     "04-ai-ml", "ai_ml"),

    # -- 05-celtic-language
    (r"^#\s*BILINGUAL_EDTECH|^#\s*IRISH_ENGLISH|^#\s*CELTIC_AI_RESOURCES|^#\s*IRISH_HUGGINGFACE|^#\s*LANGUAGE_ARCHITECTURE",
     "05-celtic-language", "celtic_language"),
    (r"^#\s*OIDEACHAIS_PIPELINE|^#\s*OIDEACHAIS_SPEC|oideachais-pipeline",
     "05-celtic-language", "celtic_language"),
    (r"^#\s*CELTIC_AI|celtic[- ]language[- ]?ai",
     "05-celtic-language", "celtic_language"),

    # -- 05-web
    (r"^#\s*FRONTEND_STACK|tanstack[- ]?start|^#\s*hono\b|^#\s*convex",
     "05-web", "web"),

    # -- 06-infrastructure
    (r"^#\s*DEPLOYMENT_STATUS|^#\s*TECH_STACK|^#\s*BONNEAGAR_OVERVIEW",
     "06-infrastructure", "infrastructure"),
    (r"^#\s*cloudflare-r2|^#\s*neo4j|^#\s*memgraph|^#\s*lancedb|^#\s*lance\b|^#\s*marimo",
     "06-infrastructure", "infrastructure"),
    (r"agentic[- ]?scraping|apple[- ]?silicon[- ]?deployment|ansible|komodo",
     "06-infrastructure", "infrastructure"),
    (r"^#\s*SUBJECT_IMPLEMENTATIONS|^#\s*API_?MAIN|apple[- ]?silicon",
     "06-infrastructure", "infrastructure"),

    # -- 06-product
    (r"^#\s*TUATH_?MMO|^#\s*TUATH_?QUICKSTART|^#\s*CRYPTEOLAS|^#\s*BABYLONJS",
     "06-product", "product"),
    (r"tuatha\s+mmo|tuatha[- ]?quickstart|game[- ]?development",
     "06-product", "product"),

    # -- 07-standards
    (r"^#\s*openspec|OPENSPEC_AGENTS|spec[- ]?driven",
     "07-standards", "standards"),

    # -- 07-skills
    (r"^#\s*BAML\b.*type-safe|BAML\s+development|type-safe\s+LLM",
     "07-skills", "skills"),
    (r"^#\s*dagster\.md|^#\s*dlt\.md|^#\s*duckdb\.md|^#\s*lancedb\.md|^#\s*neo4j\.md|^#\s*memgraph\.md",
     "07-skills", "skills"),
    (r"^#\s*graphiti\.md|^#\s*unsloth\.md|^#\s*trl\.md|^#\s*ragas\.md|^#\s*sqlmesh\.md|^#\s*ducklake\.md",
     "07-skills", "skills"),
    (r"^#\s*hono\.md|^#\s*tanstack-start\.md|^#\s*copilotkit\.md|^#\s*cloudflare-r2\.md",
     "07-skills", "skills"),
    (r"^#\s*crawl4ai-sdk\.md|^#\s*patchright\.md|^#\s*stagehand\.md|^#\s*modal\.md|^#\s*marimo\.md",
     "07-skills", "skills"),
    (r"^#\s*pydantic-ai\.md|^#\s*agno\.md|^#\s*google-adk\.md|^#\s*cognee-sdk\.md|^#\s*graphiti-sdk\.md",
     "07-skills", "skills"),
    (r"^#\s*dagster-sdk\.md|^#\s*helsinki-opus-mt\.md|^#\s*nllb-200\.md|^#\s*m2m-100\.md",
     "07-skills", "skills"),
    (r"^#\s*wav2vec2-xlsr-irish\.md|^#\s*whisper-faster-whisper\.md|^#\s*chatterbox\.md|^#\s*bge-m3\.md|^#\s*gabert\.md",
     "07-skills", "skills"),

    # -- 08-examples
    (r"^#\s*IMPLEMENTATION_GUIDE|^#\s*BEADS\s+TRACKER|^#\s*OPENSPEC_AGENTS",
     "08-examples", "examples"),
    (r"^#\s*SUBJECT_IMPLEMENTATIONS",
     "08-examples", "examples"),

    # -- 02-audit (low priority - things about audits)
    (r"audit|retrospective|consolidation",
     "02-audit", "audit"),
]


# Files we should NEVER move (they're at root intentionally)
_DO_NOT_MOVE = {
    "00_index.md",          # master index
    "INDEX.md",             # legacy context library index (deprecate, don't move)
}


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def _strip_frontmatter(text: str) -> tuple[dict, str]:
    """Pull a simple frontmatter block off the top of the file."""
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    fm_text = parts[1]
    body = parts[2].lstrip("\n")
    fm: dict = {}
    current_key: str | None = None
    for line in fm_text.splitlines():
        if not line.strip():
            continue
        if line.startswith("  - ") and current_key:
            value = fm.setdefault(current_key, [])
            if isinstance(value, list):
                value.append(line.split("- ", 1)[1].strip())
        elif ":" in line:
            key, _, raw = line.partition(":")
            current_key = key.strip()
            raw = raw.strip()
            if raw:
                fm[current_key] = raw
    return fm, body


def _h1_title(body: str) -> str | None:
    """Return the first H1 in the body, or None."""
    m = re.search(r"^#\s+(.+?)\s*$", body, re.MULTILINE)
    if m:
        return m.group(1).strip()
    return None


def _first_paragraph(body: str) -> str:
    """Return the first non-heading, non-empty paragraph in the body."""
    in_para = False
    lines: list[str] = []
    for line in body.splitlines():
        s = line.strip()
        if not s:
            if lines:
                break
            continue
        if s.startswith("#"):
            if lines:
                break
            continue
        lines.append(s)
    return " ".join(lines)[:280]


def _classify(text: str, filename: str) -> tuple[str, str, float]:
    """Return (target_dir, domain, confiance). 0.0-1.0 confiance.

    Confiance = 1.0 if a routing rule matches the H1 line directly,
    0.85 if it matches the first paragraph, 0.7 if only the filename,
    0.3 if no match.

    H1 matching uses the full H1 *line* (including the `#` marker) so
    that `^#\s*` patterns in the routing table can anchor correctly.
    """
    fm, body = _strip_frontmatter(text)
    # Full H1 line (with leading `# `) so `^#\s*` patterns match
    h1_line_m = re.search(r"^#\s*.+", body, re.MULTILINE)
    h1_line = h1_line_m.group(0) if h1_line_m else ""
    h1_text = h1_line_m.group(0).lstrip("# ").strip() if h1_line_m else ""
    para = _first_paragraph(body) or ""
    # Also include the *raw* frontmatter (for `^name:` patterns targeting SKILL docs)
    fm_str = "\n".join(f"{k}: {v}" for k, v in fm.items()) if fm else ""
    haystack = "\n".join([fm_str, h1_line, para, filename])
    for pattern, target_dir, domain in _ROUTING:
        if re.search(pattern, haystack, re.IGNORECASE | re.MULTILINE):
            if re.search(pattern, h1_line, re.IGNORECASE | re.MULTILINE):
                return target_dir, domain, 1.0
            if re.search(pattern, para, re.IGNORECASE):
                return target_dir, domain, 0.85
            return target_dir, domain, 0.7
    return "00-core", "standards", 0.3


def _build_frontmatter(
    title: str, domain: str, description: str, old_path: Path,
    existing_fm: dict | None = None,
) -> str:
    """Generate a ccc/cognee-clean frontmatter block.

    If `existing_fm` is provided, merge — preserve any keys that the
    existing frontmatter had (e.g. `name:`, `description:`, `category:`
    in SKILL docs) and only fill in the ones missing.
    """
    today = "2026-06-10"
    rel = f"docs/{old_path.name}" if old_path.parent == DOCS_ROOT \
        else f"{old_path.relative_to(REPO_ROOT)}"
    title_safe = title.replace("'", "''")
    desc_safe = description.replace("'", "''")
    fm = existing_fm or {}
    # Build the merged dict: existing values win, our fills in the gaps
    merged = {
        **{
            "title": title_safe,
            "domain": domain,
            "status": "stable",
            "description": desc_safe,
            "read_when": ["looking for documentation on this topic"],
            "updated": today,
            "supersedes": [rel],
            "ccc_query_hints": [title.lower()[:40]],
        },
        **fm,  # existing fields override our defaults
    }
    # But always re-set the meta fields we author (title/domain/updated/supersedes)
    merged["title"] = title_safe
    merged["domain"] = domain
    merged["updated"] = today
    merged["supersedes"] = [rel]
    # If the existing fm had a 'description', keep it (the user may have
    # written something more useful than our auto-generated one)
    if "description" in fm and fm["description"].strip():
        merged["description"] = fm["description"]
    else:
        merged["description"] = desc_safe

    lines = ["---"]
    for key, value in merged.items():
        if isinstance(value, list):
            lines.append(f"{key}:")
            for item in value:
                lines.append(f"  - {item}")
        else:
            s = str(value).replace("'", "''")
            lines.append(f"{key}: '{s}'")
    lines.append("---")
    lines.append("")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------
# Dataclass for a single promotion
# ---------------------------------------------------------------------

@dataclass
class Promotion:
    src: Path
    target_dir: str
    domain: str
    confidence: float
    title: str
    description: str
    new_path: Path = field(init=False)
    skipped: bool = False
    reason: str = ""

    def __post_init__(self) -> None:
        self.new_path = DOCS_ROOT / self.target_dir / self.src.name


def _build_promotions() -> list[Promotion]:
    """Scan the loose .md files at docs/ root and build a Promotion per file."""
    out: list[Promotion] = []
    for path in sorted(DOCS_ROOT.glob("*.md")):
        if path.name in _DO_NOT_MOVE:
            continue
        if path.name in {"INDEX.md", "00_index.md"}:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        fm, body = _strip_frontmatter(text)
        # If already has domain frontmatter, skip
        if "domain" in fm:
            out.append(Promotion(
                src=path, target_dir="", domain=fm.get("domain", "?"),
                confidence=1.0, title=fm.get("title", path.stem),
                description=fm.get("description", ""),
                skipped=True, reason="already has domain frontmatter",
            ))
            continue
        target_dir, domain, confidence = _classify(text, path.name)
        h1 = _h1_title(body) or path.stem.replace("-", " ").replace("_", " ").title()
        para = _first_paragraph(body) or f"Documentation for {h1}."
        # Escape quotes in title/description
        h1_esc = h1.replace('"', '\\"')
        para_esc = para.replace('"', '\\"')
        out.append(Promotion(
            src=path, target_dir=target_dir, domain=domain,
            confidence=confidence, title=h1_esc, description=para_esc,
        ))
    return out


def _apply_promotion(p: Promotion) -> bool:
    """Actually do the promotion: read, patch frontmatter, write, move, log.

    Returns True if the move succeeded, False if it was skipped (because
    the target file already existed - we'd rather flag this than
    silently clobber).
    """
    text = p.src.read_text(encoding="utf-8", errors="replace")
    fm, body = _strip_frontmatter(text)
    new_fm = _build_frontmatter(p.title, p.domain, p.description, p.src, fm)
    new_text = new_fm + body
    if p.new_path.exists():
        # The target file already exists. We don't want to silently
        # clobber it. Instead, log a warning and return False; the
        # caller will see it in the report.
        print(f"  WARN: target already exists, skipping: {p.new_path}")
        return False
    p.new_path.parent.mkdir(parents=True, exist_ok=True)
    p.new_path.write_text(new_text, encoding="utf-8")
    p.src.unlink()  # remove the original
    return True


def _undo_promotion() -> None:
    """Reverse all prior promotions using the state file.

    The state file now includes the *original content* of each file
    so the undo is exact. If the original content is missing (older
    state files), fall back to a stub + a warning.
    """
    if not STATE_FILE.exists():
        print(f"No state file at {STATE_FILE}; nothing to undo")
        return
    state = json.loads(STATE_FILE.read_text())
    n_undone = 0
    n_fallback = 0
    for entry in state.get("promotions", []):
        src = Path(entry["src"])
        new_path = Path(entry["new_path"])
        if new_path.exists():
            new_path.unlink()
        if not src.exists():
            original = entry.get("original_content")
            if original is None:
                # Old state file: no original content. Reconstruct
                # a stub so the file exists, but warn the user.
                text = (
                    f"# {entry['title']}\n\n"
                    f"{entry['description']}\n"
                )
                n_fallback += 1
            else:
                text = original
            src.write_text(text, encoding="utf-8")
            n_undone += 1
    STATE_FILE.unlink()
    msg = f"Undid {n_undone} promotions"
    if n_fallback:
        msg += f" ({n_fallback} used stub fallback — restore from git if you need the originals)"
    print(msg)


# ---------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be done; don't write")
    parser.add_argument("--apply", action="store_true",
                        help="Actually do it (default if no flag)")
    parser.add_argument("--reset", action="store_true",
                        help="Undo all prior moves")
    args = parser.parse_args()

    if args.reset:
        _undo_promotion()
        return 0

    do_apply = args.apply or (not args.dry_run)

    promotions = _build_promotions()
    moved = [p for p in promotions if not p.skipped]
    skipped = [p for p in promotions if p.skipped]
    low_conf = [p for p in moved if p.confidence < 0.7]

    # Group by target dir
    by_target: dict[str, list[Promotion]] = {}
    for p in moved:
        by_target.setdefault(p.target_dir, []).append(p)

    # Report
    print("=" * 70)
    print(f"Total loose .md files at docs/ root: {len(promotions) + len(skipped)}")
    print(f"  Skipped (already has frontmatter or in _DO_NOT_MOVE): {len(skipped)}")
    print(f"  Will move: {len(moved)}")
    print(f"  Of which low-confidence (< 0.7): {len(low_conf)}")
    print()
    print("By target dir:")
    for target, ps in sorted(by_target.items()):
        print(f"  {target}: {len(ps)} files")
    print()

    if not do_apply:
        print("DRY RUN - not writing. Pass --apply to actually do it.")
        print()
        print("Sample first 10 promotions:")
        for p in moved[:10]:
            print(f"  {p.src.name:40s} -> {p.target_dir}/{p.src.name} "
                  f"(confidence={p.confidence:.1f}, domain={p.domain})")
        print()
        print("Low-confidence promotions (would land in 00-core):")
        for p in low_conf[:20]:
            print(f"  {p.src.name:40s} confidence={p.confidence:.1f}")
        return 0

    # Actually do it
    applied: list[dict] = []
    skipped_overwrite: list[dict] = []
    for p in moved:
        # Snapshot the original content BEFORE moving, so the undo can
        # restore it exactly (no data loss across apply/reset cycles).
        try:
            original_content = p.src.read_text(encoding="utf-8", errors="replace")
        except OSError:
            original_content = None
        success = _apply_promotion(p)
        if success:
            applied.append({
                "src": str(p.src.relative_to(REPO_ROOT)),
                "new_path": str(p.new_path.relative_to(REPO_ROOT)),
                "target_dir": p.target_dir,
                "domain": p.domain,
                "confidence": p.confidence,
                "title": p.title,
                "description": p.description,
                "original_content": original_content,
            })
        else:
            skipped_overwrite.append({
                "src": str(p.src.relative_to(REPO_ROOT)),
                "new_path": str(p.new_path.relative_to(REPO_ROOT)),
                "target_dir": p.target_dir,
            })
    if skipped_overwrite:
        print(f"\nWARN: {len(skipped_overwrite)} files skipped (target existed):")
        for s in skipped_overwrite:
            print(f"  {s['src']} -> {s['new_path']}")

    # Persist state
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps({
        "applied_at": "2026-06-10",
        "promotions": applied,
    }, indent=2))

    # Write the human-readable report
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with REPORT_FILE.open("w", encoding="utf-8") as f:
        f.write("# Loose-docs Promotion Report — 2026-06-10\n\n")
        f.write(f"- Total loose `.md` files at `docs/` root: {len(promotions) + len(skipped)}\n")
        f.write(f"- Skipped (already has frontmatter or in `_DO_NOT_MOVE`): {len(skipped)}\n")
        f.write(f"- Moved: {len(moved)}\n")
        f.write(f"- Low-confidence moves (landed in `00-core/`): {len(low_conf)}\n\n")
        f.write("## By target dir\n\n")
        for target, ps in sorted(by_target.items()):
            f.write(f"### `docs/{target}/` ({len(ps)} files)\n\n")
            for p in sorted(ps, key=lambda x: x.src.name):
                marker = "  (low-confidence)" if p.confidence < 0.7 else ""
                f.write(f"- `{p.src.name}` -> `{p.target_dir}/{p.src.name}`{marker}\n")
                f.write(f"  - title: {p.title}\n")
                f.write(f"  - domain: {p.domain}\n")
                f.write(f"  - confidence: {p.confidence:.2f}\n")
            f.write("\n")
        f.write("## Skipped\n\n")
        for p in skipped:
            f.write(f"- `{p.src.name}` ({p.reason})\n")
        f.write("\n")
    print(f"Wrote report to {REPORT_FILE}")
    print(f"Wrote state to {STATE_FILE} (for --reset)")
    print(f"Moved {len(moved)} files. Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
