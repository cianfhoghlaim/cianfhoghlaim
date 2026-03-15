#!/usr/bin/env python3
"""
Context Banking Script for Cianfhoghlaim.

Archives project documentation to Letta Cloud for persistent agent memory.
This enables the ProjectArchitect agent to have deep knowledge of the codebase.

Documents ingested:
- AGENTS.md files from each directory
- CLAUDE.md project instructions
- Pattern files from taighde/patterns/
- Skill definitions from .claude/skills/
- README files from key directories

Usage:
    python scripts/bank-context.py [--clear] [--dry-run] [--verbose]

Options:
    --clear     Clear existing archival memory before banking
    --dry-run   List files without uploading
    --verbose   Show detailed progress

Requires:
    - LETTA_API_KEY environment variable
    - letta-client package: pip install letta-client
"""

import argparse
import glob
import logging
import os
import sys
from pathlib import Path

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "sruth" / "oideachais"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def find_documents(root: Path) -> list[tuple[str, Path]]:
    """
    Find all documents to bank.

    Returns:
        List of (category, path) tuples.
    """
    documents = []

    # Skip patterns for directories
    skip_dirs = {
        "node_modules",
        ".venv",
        "__pycache__",
        ".git",
        ".ruff_cache",
        "dist",
        "build",
        ".next",
        ".turbo",
        "taighde_bonneagar",
        "taighde_scoil",
        "taighde_meaisínfhoghlaim",
        "taighde_teanga",
        "taighde_new",
    }

    # AGENTS.md files
    for agents_md in root.glob("**/AGENTS.md"):
        if not any(skip in agents_md.parts for skip in skip_dirs):
            documents.append(("agents", agents_md))

    # CLAUDE.md
    claude_md = root / "CLAUDE.md"
    if claude_md.exists():
        documents.append(("instructions", claude_md))

    # Pattern files
    patterns_dir = root / "taighde" / "patterns"
    if patterns_dir.exists():
        for pattern_file in patterns_dir.glob("PATTERNS_*.md"):
            documents.append(("pattern", pattern_file))

    # Skill definitions
    skills_dir = root / ".claude" / "skills"
    if skills_dir.exists():
        for skill_md in skills_dir.glob("*/SKILL.md"):
            documents.append(("skill", skill_md))

    # Key README files
    key_readmes = [
        root / "README.md",
        root / "bonneagar" / "README.md",
        root / "sruth" / "README.md",
        root / "sruth" / "oideachais" / "README.md",
    ]
    for readme in key_readmes:
        if readme.exists():
            documents.append(("readme", readme))

    return documents


def bank_document(
    client,
    agent,
    category: str,
    path: Path,
    root: Path,
) -> bool:
    """
    Bank a single document to archival memory.

    Args:
        client: Letta client
        agent: Agent to bank to
        category: Document category
        path: Path to document
        root: Project root for relative path calculation

    Returns:
        True if successful
    """
    try:
        content = path.read_text(encoding="utf-8")
        relative_path = path.relative_to(root)

        # Format with metadata
        source = f"[{category}] {relative_path}"

        # Use the archive_document function from letta_client
        from agents.letta_client import archive_document

        return archive_document(content, source, agent=agent, client=client)

    except Exception as e:
        logger.error(f"Failed to bank {path}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Bank project context to Letta Cloud archival memory"
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing archival memory before banking",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List files without uploading",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed progress",
    )
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Find documents
    documents = find_documents(PROJECT_ROOT)
    logger.info(f"Found {len(documents)} documents to bank")

    if args.dry_run:
        print("\nDocuments to bank:")
        for category, path in documents:
            rel_path = path.relative_to(PROJECT_ROOT)
            size_kb = path.stat().st_size / 1024
            print(f"  [{category:12}] {rel_path} ({size_kb:.1f} KB)")

        total_size = sum(p.stat().st_size for _, p in documents)
        print(f"\nTotal: {len(documents)} documents, {total_size / 1024:.1f} KB")
        print(f"Estimated tokens: ~{total_size // 4:,}")
        return

    # Import Letta client
    try:
        from agents.letta_client import (
            get_letta_client,
            get_or_create_architect_agent,
            clear_archival_memory,
            get_memory_stats,
        )
    except ImportError as e:
        logger.error(f"Failed to import letta_client: {e}")
        logger.error("Make sure you're running from the project root")
        sys.exit(1)

    # Connect to Letta
    client = get_letta_client()
    if client is None:
        logger.error("Failed to connect to Letta Cloud")
        logger.error("Ensure LETTA_API_KEY is set")
        sys.exit(1)

    # Get or create agent
    agent = get_or_create_architect_agent(client)
    if agent is None:
        logger.error("Failed to get/create ProjectArchitect agent")
        sys.exit(1)

    logger.info(f"Using agent: {agent.name} (id: {agent.id})")

    # Clear if requested
    if args.clear:
        logger.info("Clearing existing archival memory...")
        if clear_archival_memory(agent=agent, client=client):
            logger.info("Archival memory cleared")
        else:
            logger.warning("Failed to clear archival memory")

    # Bank documents
    success_count = 0
    failed_count = 0

    for category, path in documents:
        rel_path = path.relative_to(PROJECT_ROOT)
        logger.debug(f"Banking: {rel_path}")

        if bank_document(client, agent, category, path, PROJECT_ROOT):
            success_count += 1
            if args.verbose:
                print(f"  [OK] {rel_path}")
        else:
            failed_count += 1
            if args.verbose:
                print(f"  [FAIL] {rel_path}")

    # Summary
    print(f"\nContext banking complete:")
    print(f"  Successful: {success_count}")
    print(f"  Failed: {failed_count}")

    # Show memory stats
    stats = get_memory_stats(agent=agent, client=client)
    if stats.get("available"):
        print(f"\nAgent memory stats:")
        print(f"  Agent: {stats['agent_name']} ({stats['agent_id'][:8]}...)")
        print(f"  Archival passages: {stats['archival_count']}")
        print(f"  Total characters: {stats['total_characters']:,}")
        print(f"  Estimated tokens: ~{stats['estimated_tokens']:,}")


if __name__ == "__main__":
    main()
