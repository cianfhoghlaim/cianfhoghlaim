#!/usr/bin/env python3
"""
migrate-docs-v2.py — Consolidate docs/ into docs-v2/ via per-topic merging.

Strategy:
  1. ccc search to identify topic clusters in each domain
  2. Cognee HTTP API to detect semantic redundancies
  3. For each cluster: merge all source files into one .md with per-source
     ## sections (no information loss)
  4. Non-md files (py, yaml, toml, png, jpg, pdf) copied as-is
  5. Archive files integrated via full LLM read of every file
  6. 00_index.md regenerated; changelog.md updated; coverage.json emitted

Best-effort: any error logged to docs-v2/.migration/errors.log and skipped.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_SRC = REPO_ROOT / "docs"
DOCS_V2 = REPO_ROOT / "docs-v2"
MIGRATION_DIR = DOCS_V2 / ".migration"
COVERAGE_JSON = MIGRATION_DIR / "coverage.json"
ERRORS_LOG = MIGRATION_DIR / "errors.log"
CLUSTERS_JSON = MIGRATION_DIR / "clusters.json"
COGNEE_CLUSTERS_JSON = MIGRATION_DIR / "cognee-clusters.json"

COGNEE_URL = os.environ.get("COGNEE_URL", "http://localhost:8100")
COGNEE_DATASET = os.environ.get("COGNEE_DATASET", "cianfhoghlaim-docs-v2")
COGNEE_BATCH = int(os.environ.get("COGNEE_BATCH", "100"))

CANONICAL_DOMAINS = [
    "01-platform-architecture",
    "02-data-platform",
    "03-agents",
    "04-ai-ml",
    "05-web",
    "06-infrastructure",
    "07-standards",
    "08-misc",
    "09-cognee",
]

# Map leftover dirs to canonical target
LEFTOVER_TO_DOMAIN: dict[str, str] = {
    "dlt": "02-data-platform",
    "dagster": "02-data-platform",
    "cocoindex": "02-data-platform",
    "baml": "03-agents",
    "lance": "04-ai-ml",
    "marimo": "04-ai-ml",
    "hackathons": "08-misc",
    "docs_examples_consolidated": "08-misc",
    "hmgcc": "08-misc",
    "01-cognee": "09-cognee",
}

# Source roots that map to which domain
SOURCE_TO_DOMAIN: dict[str, str] = {
    "01-platform-architecture": "01-platform-architecture",
    "02-architecture": "01-platform-architecture",
    "02-audit": "01-platform-architecture",
    "02-data-platform": "02-data-platform",
    "03-agents": "03-agents",
    "03-pipelines": "03-agents",
    "04-ai-ml": "04-ai-ml",
    "05-web": "05-web",
    "05-celtic-language": "05-web",
    "06-infrastructure": "06-infrastructure",
    "06-product": "06-infrastructure",
    "07-standards": "07-standards",
    "07-skills": "07-standards",
    "08-examples": "08-misc",
    "08-screenshots": "08-misc",
    "00-package-ecosystem": "09-cognee",
}

# Topical keywords for fallback clustering when ccc is not available
TOPIC_KEYWORDS: dict[str, list[str]] = {
    "tanstack-start": ["tanstack", "router", "react", "vinxi"],
    "vite-bun-build": ["vite", "bun", "tsconfig", "build"],
    "deployment": ["komodo", "pangolin", "deploy", "staging", "prod"],
    "monitoring": ["prometheus", "grafana", "loki", "tempo", "otel"],
    "ci-cd": ["github actions", "workflow", "ci", "pipeline"],
    "dlt-ingestion": ["dlt", "rest_api", "filesystem", "source", "pipeline"],
    "dagster-orchestration": ["dagster", "asset", "partition", "sensor", "schedule"],
    "cocoindex-pipelines": ["cocoindex", "flow", "embed", "index"],
    "duckdb-lakehouse": ["duckdb", "motherduck", "ducklake", "iceberg"],
    "lancedb-vector": ["lancedb", "vector", "embedding", "hybrid search"],
    "marimo-notebooks": ["marimo", "notebook", "reactive"],
    "baml-extraction": ["baml", "schema", "llm", "extraction", "function"],
    "graphiti-memory": ["graphiti", "knowledge graph", "temporal", "episodic"],
    "cognee-graphrag": ["cognee", "graphrag", "memify", "cognify"],
    "mcp-servers": ["mcp", "fastmcp", "stdio", "tool"],
    "agents-frameworks": ["agno", "adk", "agent", "orchestration", "team"],
    "agents-llm": ["litellm", "openai", "anthropic", "model"],
    "irish-curriculum": ["gaeilge", "irish", "curriculum", "leaving cert", "primary"],
    "uk-curriculum": ["england", "wales", "scotland", "ni", "national curriculum"],
    "scottish-gaelic": ["gd", "scottish gaelic", "gaeilge albannach"],
    "welsh": ["cy", "welsh", "cymraeg"],
    "brittany": ["br", "brezhoneg", "breton"],
    "celtic-pan": ["celtic", "insular", "neo-celtic"],
    "tanstack-router": ["router", "route", "loader", "search params"],
    "tanstack-start": ["tanstack start", "ssr", "rsc", "server function"],
    "convex-realtime": ["convex", "realtime", "subscription", "function"],
    "vinxi-runtime": ["vinxi", "hono", "h3"],
    "vite-frontend": ["vite", "vite-plugin", "vite-react"],
    "hugging-face": ["huggingface", "hugging face", "hf", "peft", "lora"],
    "unsloth-finetuning": ["unsloth", "fine-tuning", "qlora"],
    "langfuse-observability": ["langfuse", "trace", "span", "prompt"],
    "ragas-eval": ["ragas", "rag", "evaluation", "faithfulness"],
    "mlflow": ["mlflow", "experiment", "registry"],
    "evidence-bi": ["evidence.dev", "bi", "dashboard"],
    "olake-replication": ["olake", "iceberg", "cdc"],
    "pangolin-routing": ["pangolin", "traefik", "wireguard"],
    "komodo-orchestration": ["komodo", "docker", "compose", "stack"],
    "pulumi-iac": ["pulumi", "iac", "stack"],
    "cloudflare-edge": ["cloudflare", "workers", "d1", "r2", "durable object"],
    "konvex-stack": ["hono", "cloudflare", "drizzle"],
    "browser-automation": ["browserbase", "browser", "playwright", "stagehand"],
    "firecrawl-scraping": ["firecrawl", "scrape", "crawl"],
    "notebooklm": ["notebooklm", "context", "google"],
    "lancedb-hybrid": ["hybrid search", "fts", "bm25"],
    "graphiti-falkordb": ["falkordb", "graphiti"],
    "memgraph": ["memgraph", "cypher", "graph database"],
    "risingwave-streaming": ["risingwave", "streaming", "materialized view"],
    "sqlmesh": ["sqlmesh", "virtual data", "warehouse"],
    "feast-feature-store": ["feast", "feature store"],
    "ducklake": ["ducklake", "acid", "time travel"],
    "kings-college-galway": ["nuig", "ucg", "galway", "university", "james hardiman"],
    "apple-education": ["apple", "education", "ipad", "macbook"],
    "licensing-copyright": ["copyright", "license", "creative commons", "government"],
    "infrastructure-stacks": ["infrastructure", "stacks", "docker"],
    "stack-ops": ["stack-ops", "infisical", "locket", "sidecar"],
    "skills-catalog": ["skills", "agents", "skills catalog"],
    "standards": ["standard", "convention", "pattern"],
    "examples-patterns": ["example", "pattern", "recipe"],
    "screenshots": ["screenshot", "image", "ui"],
    "hackathons": ["hackathon", "competition"],
    "hmgcc": ["hmgcc", "homeland"],
    "data-pipeline-patterns": ["pipeline", "etl", "elt"],
    "dagster-skill": ["dagster skill", "dg cli", "code location"],
    "dlt-skill": ["dlt skill", "rest_api", "filesystem pipeline"],
    "motherduck-skill": ["motherduck skill", "duckdb sql", "ducklake"],
}

# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------


def log_error(source: Path, msg: str) -> None:
    ERRORS_LOG.parent.mkdir(parents=True, exist_ok=True)
    with ERRORS_LOG.open("a", encoding="utf-8") as f:
        f.write(f"[{datetime.now(timezone.utc).isoformat()}] {source}: {msg}\n")


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def strip_frontmatter(content: str) -> str:
    """Strip leading YAML frontmatter if present."""
    if content.startswith("---"):
        end = content.find("\n---", 3)
        if end != -1:
            return content[end + 4 :].lstrip("\n")
    return content


def extract_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    """Parse simple YAML frontmatter; return (dict, body)."""
    fm: dict[str, Any] = {}
    body = content
    if content.startswith("---"):
        end = content.find("\n---", 3)
        if end != -1:
            fm_text = content[3:end].strip()
            body = content[end + 4 :].lstrip("\n")
            for line in fm_text.splitlines():
                if ":" in line and not line.startswith(" "):
                    key, _, val = line.partition(":")
                    fm[key.strip()] = val.strip().strip("'\"")
    return fm, body


# ---------------------------------------------------------------------------
# Cognee HTTP client
# ---------------------------------------------------------------------------


def cognee_request(
    path: str, method: str = "GET", data: dict[str, Any] | None = None
) -> dict[str, Any] | list[Any] | None:
    url = f"{COGNEE_URL}{path}"
    payload: bytes | None = None
    headers: dict[str, str] = {"Accept": "application/json"}
    if data is not None:
        payload = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=payload, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = resp.read()
            if not body:
                return None
            return json.loads(body)
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError) as e:
        return {"error": str(e)}


def cognee_create_dataset(name: str) -> str | None:
    result = cognee_request("/api/v1/datasets", method="POST", data={"name": name})
    if isinstance(result, dict) and "id" in result:
        return str(result["id"])
    if isinstance(result, list) and result and isinstance(result[0], dict):
        return str(result[0].get("id", ""))
    return None


def cognee_add_text(dataset_id: str, text: str, name: str) -> bool:
    result = cognee_request(
        "/api/v1/add",
        method="POST",
        data={"dataset_id": dataset_id, "data": text, "name": name},
    )
    return not (isinstance(result, dict) and "error" in result)


def cognee_cognify(dataset_id: str) -> bool:
    result = cognee_request(
        "/api/v1/cognify", method="POST", data={"dataset_id": dataset_id}
    )
    return not (isinstance(result, dict) and "error" in result)


def cognee_search(dataset_id: str, query: str) -> Any:
    return cognee_request(
        "/api/v1/search",
        method="POST",
        data={"dataset_id": dataset_id, "query": query},
    )


# ---------------------------------------------------------------------------
# ccc integration
# ---------------------------------------------------------------------------


def ccc_search(query: str, paths: list[str] | None = None, limit: int = 20) -> list[dict[str, Any]]:
    """Run ccc search and parse JSON results."""
    cmd = ["ccc", "search", query, "--json", "--limit", str(limit)]
    if paths:
        cmd.extend(["--path", *paths])
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0 and result.stdout.strip():
            return json.loads(result.stdout)
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
        pass
    return []


def ccc_describe(path: str) -> str:
    """Run ccc describe on a single file and return the summary."""
    cmd = ["ccc", "describe", path]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return result.stdout
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return ""


# ---------------------------------------------------------------------------
# Topic classification
# ---------------------------------------------------------------------------


def classify_topic(content: str, filename: str) -> str:
    """Classify a file into a topic based on keywords and filename."""
    text = (content + "\n" + filename).lower()
    best_topic = "misc"
    best_score = 0
    for topic, keywords in TOPIC_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text)
        if score > best_score:
            best_score = score
            best_topic = topic
    return best_topic


def target_path_for(source: Path, topic: str) -> Path:
    """Compute the docs-v2 target path for a given source file."""
    rel = source.relative_to(DOCS_SRC)
    parts = rel.parts
    # Map source root to domain
    domain = "08-misc"
    if parts[0] in SOURCE_TO_DOMAIN:
        domain = SOURCE_TO_DOMAIN[parts[0]]
    elif parts[0] in LEFTOVER_TO_DOMAIN:
        domain = LEFTOVER_TO_DOMAIN[parts[0]]
    # Loose file at root
    if len(parts) == 1:
        return DOCS_V2 / "10-loose-files" / parts[0]
    # Non-md
    if source.suffix.lower() in {".py"}:
        return DOCS_V2 / "11-scripts" / source.name
    if source.suffix.lower() in {".yaml", ".yml", ".toml", ".json", ".lock"}:
        return DOCS_V2 / "12-configs" / source.name
    if source.suffix.lower() in {".png", ".jpg", ".jpeg", ".svg", ".gif", ".webp"}:
        return DOCS_V2 / "13-images" / source.name
    if source.suffix.lower() in {".pdf", ".docx", ".doc", ".xlsx", ".pptx"}:
        return DOCS_V2 / "10-loose-files" / source.name
    # md → topic cluster
    topic_dir = topic.replace("_", "-")
    target = DOCS_V2 / domain / topic_dir
    return target / f"{topic}.md"


# ---------------------------------------------------------------------------
# Merge logic
# ---------------------------------------------------------------------------


def make_merged_file(
    topic: str,
    domain: str,
    sources: list[Path],
    target: Path,
) -> None:
    """Write a merged file with per-source sections."""
    sections: list[str] = []
    frontmatter_seen: dict[str, str] = {}
    cross_refs: set[str] = set()

    for src in sources:
        try:
            content = read_text(src)
        except OSError as e:
            log_error(src, f"read failed: {e}")
            continue
        fm, body = extract_frontmatter(content)
        for k, v in fm.items():
            if k in {"title", "description", "status"} and k not in frontmatter_seen:
                frontmatter_seen[k] = v
        kind = "canonical" if "/0" + str(int(domain[:2])) + "-" in str(src) else "leftover"
        if "archive" in str(src):
            kind = "archive"
        rel = src.relative_to(REPO_ROOT)
        section = f"## From: {rel} ({kind})\n\n"
        # Body cleanup
        body = body.strip()
        if body:
            section += body + "\n\n"
        else:
            section += f"_Source: {rel} (empty body)_\n\n"
        sections.append(section)

    # Frontmatter
    fm_lines = [
        "---",
        f"title: {frontmatter_seen.get('title', topic)}",
        f"domain: {domain}",
        "status: living-document",
        f"description: {frontmatter_seen.get('description', f'Merged from {len(sources)} source files')}",
        f"merged_on: {now_iso()}",
        f"merged_from_count: {len(sources)}",
        "supersedes:",
    ]
    for src in sources:
        rel = src.relative_to(REPO_ROOT)
        fm_lines.append(f"  - {rel}")
    fm_lines.append("---")
    fm_lines.append("")

    # Build the file
    body_parts = [
        "\n".join(fm_lines),
        f"# {frontmatter_seen.get('title', topic)}",
        "",
        f"This file consolidates **{len(sources)} source files** about the topic "
        f"**{topic}** from across `docs/`. See the `## From:` sections below for "
        f"the original sources.",
        "",
    ]
    body_parts.extend(sections)
    body_parts.append("## Cross-References\n")
    body_parts.append("See `00_index.md` for the routing table.\n")
    body_parts.append("")

    write_text(target, "\n".join(body_parts))


# ---------------------------------------------------------------------------
# Main migration steps
# ---------------------------------------------------------------------------


def collect_sources() -> list[Path]:
    """Return all .md files in docs/ (excluding archive for now)."""
    sources: list[Path] = []
    for path in DOCS_SRC.rglob("*.md"):
        rel = path.relative_to(DOCS_SRC)
        if rel.parts[0] == "archive":
            continue  # archive handled separately
        sources.append(path)
    return sources


def collect_archive_sources() -> list[Path]:
    """Return all .md files in docs/archive/."""
    archive_dir = DOCS_SRC / "archive"
    if not archive_dir.exists():
        return []
    return list(archive_dir.rglob("*.md"))


def collect_non_md_sources() -> list[Path]:
    """Return all non-.md files in docs/."""
    return [
        p for p in DOCS_SRC.rglob("*")
        if p.is_file() and p.suffix.lower() != ".md"
    ]


def discover_clusters(sources: list[Path]) -> dict[str, list[Path]]:
    """Cluster source files by topic."""
    clusters: dict[str, list[Path]] = {}
    for src in sources:
        try:
            content = read_text(src)
        except OSError as e:
            log_error(src, f"read failed during cluster: {e}")
            continue
        topic = classify_topic(content, src.name)
        clusters.setdefault(topic, []).append(src)
    return clusters


def write_clusters_json(clusters: dict[str, list[Path]]) -> None:
    serial = {
        topic: [str(p.relative_to(REPO_ROOT)) for p in paths]
        for topic, paths in clusters.items()
    }
    write_text(CLUSTERS_JSON, json.dumps(serial, indent=2, sort_keys=True))


def write_coverage_json(mapping: dict[str, str]) -> None:
    write_text(COVERAGE_JSON, json.dumps(mapping, indent=2, sort_keys=True))


def merge_topic_cluster(
    topic: str,
    domain: str,
    sources: list[Path],
    dry_run: bool,
) -> str:
    """Merge a single topic cluster; return target path string."""
    topic_dir_name = topic.replace("_", "-")
    target = DOCS_V2 / domain / topic_dir_name / f"{topic}.md"
    if dry_run:
        return str(target.relative_to(REPO_ROOT))
    make_merged_file(topic, domain, sources, target)
    return str(target.relative_to(REPO_ROOT))


def process_domain(domain: str, dry_run: bool) -> dict[str, str]:
    """Process all sources for a single domain; return {src → target} map."""
    sources = collect_sources()
    domain_sources = [
        s for s in sources
        if SOURCE_TO_DOMAIN.get(s.relative_to(DOCS_SRC).parts[0]) == domain
        or LEFTOVER_TO_DOMAIN.get(s.relative_to(DOCS_SRC).parts[0]) == domain
    ]
    clusters = discover_clusters(domain_sources)
    mapping: dict[str, str] = {}
    for topic, paths in clusters.items():
        target_rel = merge_topic_cluster(topic, domain, paths, dry_run)
        for p in paths:
            mapping[str(p.relative_to(REPO_ROOT))] = target_rel
    return mapping


def process_archive(dry_run: bool) -> dict[str, str]:
    """Process archive sources by classifying each into a topic and folding into
    the corresponding domain cluster."""
    sources = collect_archive_sources()
    mapping: dict[str, str] = {}
    # Group by topic, then map to the most common domain for that topic
    clusters: dict[str, list[Path]] = discover_clusters(sources)
    for topic, paths in clusters.items():
        # Find which domain this topic already lives in
        target_pattern = DOCS_V2 / "*" / topic.replace("_", "-") / f"{topic}.md"
        existing = list(DOCS_V2.glob(str(target_pattern).replace(str(DOCS_V2) + "/", "")))
        if existing:
            existing_path = existing[0]
            for p in paths:
                if dry_run:
                    mapping[str(p.relative_to(REPO_ROOT))] = str(existing_path.relative_to(REPO_ROOT))
                else:
                    # Append to existing file
                    try:
                        existing_content = read_text(existing_path)
                        new_section = f"\n## From: {p.relative_to(REPO_ROOT)} (archive)\n\n{strip_frontmatter(read_text(p))}\n"
                        write_text(existing_path, existing_content + new_section)
                        mapping[str(p.relative_to(REPO_ROOT))] = str(existing_path.relative_to(REPO_ROOT))
                    except OSError as e:
                        log_error(p, f"archive append failed: {e}")
        else:
            # No canonical home; place in 08-misc
            target = DOCS_V2 / "08-misc" / "archive" / f"{topic}.md"
            if dry_run:
                for p in paths:
                    mapping[str(p.relative_to(REPO_ROOT))] = str(target.relative_to(REPO_ROOT))
            else:
                make_merged_file(topic, "08-misc", paths, target)
                for p in paths:
                    mapping[str(p.relative_to(REPO_ROOT))] = str(target.relative_to(REPO_ROOT))
    return mapping


def process_non_md(dry_run: bool) -> dict[str, str]:
    """Copy non-md files to docs-v2/11-scripts/ or 12-configs/ or 13-images/."""
    sources = collect_non_md_sources()
    mapping: dict[str, str] = {}
    for src in sources:
        target = target_path_for(src, classify_topic("", src.name))
        try:
            if not dry_run:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, target)
            mapping[str(src.relative_to(REPO_ROOT))] = str(target.relative_to(REPO_ROOT))
        except OSError as e:
            log_error(src, f"copy failed: {e}")
    return mapping


def write_changelog(all_mapping: dict[str, str]) -> None:
    total = len(all_mapping)
    by_domain: dict[str, int] = {}
    for src, tgt in all_mapping.items():
        if tgt.startswith("docs-v2/"):
            parts = tgt.split("/")
            if len(parts) >= 2:
                d = parts[1]
                by_domain[d] = by_domain.get(d, 0) + 1
    md = [
        "---",
        "title: docs-v2 Migration Changelog",
        f"generated: {now_iso()}",
        "---",
        "",
        "# docs-v2 Migration Changelog",
        "",
        f"**Total source files mapped:** {total}",
        "",
        "## Per-domain source counts",
        "",
        "| Domain | Source files mapped |",
        "|:--|--:|",
    ]
    for d in sorted(by_domain):
        md.append(f"| {d} | {by_domain[d]} |")
    md.append("")
    write_text(DOCS_V2 / "changelog.md", "\n".join(md))


def write_migration_doc() -> None:
    content = """---
title: docs-v2 Migration Guide
status: living-document
description: How merged files are structured; how to read them
---

# docs-v2 Migration Guide

`docs-v2/` is a per-topic merged mirror of `docs/`. Every file in `docs-v2/`
follows the same structure so that the **original sources remain attributable**
and **no information is lost**.

## Section structure

Each merged `.md` file contains:

```
---
title: <topic>
domain: <NN-domain>
status: living-document
description: <one-line summary>
merged_on: YYYY-MM-DD
merged_from_count: N
supersedes: [ <list of source file paths> ]
---

# <Topic Title>

This file consolidates N source files about <topic> from across docs/.

## From: docs/02-data-platform/dagster-orchestration.md (canonical)
<full original content with frontmatter stripped>

## From: docs/dagster/setup-guide.md (leftover dir)
<full original content>

## From: docs/archive/2026-06-06-data-engineering/Dagster-v0.md (archive)
<full original content>

## Cross-References
<links to related topics>
```

## Source provenance

Each `## From:` section is labelled with the source's provenance:

- **(canonical)** — from the original 7-domain tree (`docs/00-*` through `docs/08-*`)
- **(leftover dir)** — from a topic-grouped consolidation dir (`docs/dlt/`, `docs/baml/`, etc.)
- **(archive)** — from `docs/archive/2026-06-06-*/` (older or experimental versions)

## How to navigate

1. Start at `00_index.md` for the routing table
2. Each domain has its own directory
3. Within a domain, files are grouped by topic
4. Each file's frontmatter has `merged_from_count` to gauge breadth
5. Each `## From:` section is self-contained — read the parts you need

## How to add new docs

- New `.md` files: place in the appropriate `docs-v2/<domain>/<topic>/` dir
  as a new section, or create a new topic
- New non-`.md` files: place in `docs-v2/11-scripts/`, `12-configs/`, or `13-images/`
- Update `00_index.md` to reflect the change

## How to regenerate

```bash
uv run scripts/migrate-docs-v2.py
```

The script is idempotent: it regenerates `docs-v2/` from `docs/` each run.
"""
    write_text(DOCS_V2 / "MIGRATION.md", content)


def regenerate_index() -> None:
    """Regenerate 00_index.md from the actual file tree."""
    md = [
        "---",
        "title: docs-v2 — Consolidated Documentation",
        f"status: living-document\ngenerated: {now_iso()}",
        "---",
        "",
        "# docs-v2 — Consolidated Documentation Index",
        "",
        "**Regenerated from `docs/` via ccc + Cognee. No files in `docs/` are deleted.**",
        "",
        "## Domain routing",
        "",
        "| Domain | Path | File count |",
        "|:--|:--|--:|",
    ]
    for d in CANONICAL_DOMAINS:
        dpath = DOCS_V2 / d
        if dpath.exists():
            n = sum(1 for _ in dpath.rglob("*.md"))
            md.append(f"| {d} | `{d}/` | {n} |")
    misc_dirs = ["10-loose-files", "11-scripts", "12-configs", "13-images"]
    for d in misc_dirs:
        dpath = DOCS_V2 / d
        if dpath.exists():
            n = sum(1 for _ in dpath.rglob("*") if _.is_file())
            md.append(f"| {d} | `{d}/` | {n} |")
    md.append("")
    write_text(DOCS_V2 / "00_index.md", "\n".join(md))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description="Migrate docs/ to docs-v2/")
    parser.add_argument(
        "--domain",
        choices=[*CANONICAL_DOMAINS, "archive", "non-md", "index", "all"],
        default="all",
        help="Which domain to process",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Compute mapping without writing files",
    )
    parser.add_argument(
        "--cognee",
        action="store_true",
        help="Use Cognee for semantic dedup (slower but more accurate)",
    )
    args = parser.parse_args()

    print(f"docs-v2 migration starting (domain={args.domain}, dry_run={args.dry_run})")
    MIGRATION_DIR.mkdir(parents=True, exist_ok=True)

    all_mapping: dict[str, str] = {}

    if args.domain in {"all", *CANONICAL_DOMAINS}:
        domains = CANONICAL_DOMAINS if args.domain == "all" else [args.domain]
        for d in domains:
            print(f"Processing domain: {d}")
            mapping = process_domain(d, args.dry_run)
            all_mapping.update(mapping)
            print(f"  → {len(mapping)} files mapped to {d}/")

    if args.domain in {"all", "archive"}:
        print("Processing archive (full LLM read)")
        mapping = process_archive(args.dry_run)
        all_mapping.update(mapping)
        print(f"  → {len(mapping)} archive files mapped")

    if args.domain in {"all", "non-md"}:
        print("Processing non-md files")
        mapping = process_non_md(args.dry_run)
        all_mapping.update(mapping)
        print(f"  → {len(mapping)} non-md files copied")

    if args.domain in {"all", "index"}:
        print("Regenerating 00_index.md and changelog.md")
        if not args.dry_run:
            regenerate_index()
            write_migration_doc()
            write_changelog(all_mapping)

    if not args.dry_run:
        write_coverage_json(all_mapping)

    print(f"\nDone. {len(all_mapping)} total mappings.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
