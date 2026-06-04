"""
CLI for códeolas.

Provides command-line interface for code analysis operations.
"""

import argparse
import asyncio
import json
import logging
import sys

from codeolas import CodebaseAnalyzer


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="codeolas",
        description="Code analysis and repository intelligence",
    )

    parser.add_argument(
        "--repo",
        "-r",
        type=str,
        default=".",
        help="Path to repository (default: current directory)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Index command
    index_parser = subparsers.add_parser("index", help="Index the repository")
    index_parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Force re-index",
    )

    # Search command
    search_parser = subparsers.add_parser("search", help="Search for code")
    search_parser.add_argument("query", type=str, help="Search query")
    search_parser.add_argument(
        "--limit",
        "-n",
        type=int,
        default=10,
        help="Maximum results",
    )
    search_parser.add_argument(
        "--language",
        "-l",
        type=str,
        help="Filter by language",
    )
    search_parser.add_argument(
        "--no-rerank",
        action="store_true",
        help="Disable reranking",
    )

    # Research command
    research_parser = subparsers.add_parser("research", help="Deep research a question")
    research_parser.add_argument("question", type=str, help="Research question")
    research_parser.add_argument(
        "--max-sources",
        type=int,
        default=15,
        help="Maximum sources",
    )

    # Stats command
    subparsers.add_parser("stats", help="Show indexing statistics")

    # Arch command
    arch_parser = subparsers.add_parser("arch", help="Generate architecture docs")
    arch_parser.add_argument(
        "--output",
        "-o",
        type=str,
        help="Output file path",
    )

    # MCP command
    subparsers.add_parser("mcp", help="Start MCP server")

    args = parser.parse_args()

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Run command
    if args.command == "index":
        asyncio.run(cmd_index(args))
    elif args.command == "search":
        asyncio.run(cmd_search(args))
    elif args.command == "research":
        asyncio.run(cmd_research(args))
    elif args.command == "stats":
        cmd_stats(args)
    elif args.command == "arch":
        asyncio.run(cmd_arch(args))
    elif args.command == "mcp":
        cmd_mcp(args)
    else:
        parser.print_help()
        sys.exit(1)


async def cmd_index(args):
    """Index command."""
    analyzer = CodebaseAnalyzer(args.repo)
    print(f"Indexing {args.repo}...")

    result = await analyzer.index(force=args.force)

    print(f"Indexed {result['files_indexed']} files")
    print(f"Created {result['chunks_created']} chunks")


async def cmd_search(args):
    """Search command."""
    analyzer = CodebaseAnalyzer(args.repo)

    results = await analyzer.search(
        query=args.query,
        limit=args.limit,
        language=args.language,
        rerank=not args.no_rerank,
    )

    if not results:
        print("No results found.")
        return

    for i, result in enumerate(results, 1):
        chunk = result.chunk
        print(f"\n[{i}] {chunk.file_path}:{chunk.start_line}")
        print(f"    Type: {chunk.chunk_type}")
        if chunk.name:
            print(f"    Name: {chunk.name}")
        print(f"    Score: {result.score:.4f}")
        if result.rerank_score:
            print(f"    Rerank: {result.rerank_score:.4f}")
        print(f"    ---")
        # Show first 3 lines of text
        lines = chunk.text.split("\n")[:3]
        for line in lines:
            print(f"    {line[:80]}")


async def cmd_research(args):
    """Research command."""
    analyzer = CodebaseAnalyzer(args.repo)

    print(f"Researching: {args.question}")
    print("---")

    result = await analyzer.deep_research(
        question=args.question,
        max_sources=args.max_sources,
    )

    print(f"\nIterations: {result['iterations']}")
    print(f"Converged: {result['converged']}")
    print(f"Sources found: {result['total_sources_found']}")
    print(f"\n{result['synthesis']}")


def cmd_stats(args):
    """Stats command."""
    analyzer = CodebaseAnalyzer(args.repo)
    stats = analyzer.get_stats()

    print(json.dumps(stats, indent=2, default=str))


async def cmd_arch(args):
    """Arch command."""
    analyzer = CodebaseAnalyzer(args.repo)

    content = await analyzer.generate_arch_doc(output_path=args.output)

    if args.output:
        print(f"Written to {args.output}")
    else:
        print(content)


def cmd_mcp(args):
    """MCP command."""
    from codeolas.mcp_server.server import main as mcp_main

    mcp_main()


if __name__ == "__main__":
    main()
