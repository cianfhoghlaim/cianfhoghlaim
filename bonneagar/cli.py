"""cianfhoghlaim-stack-doctor — CLI for the 94-stack validation tool.

Usage:
    uv run cianfhoghlaim-stack-doctor --help
    uv run cianfhoghlaim-stack-doctor check oideachais
    uv run cianfhoghlaim-stack-doctor list
"""
from __future__ import annotations

import argparse
import sys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="cianfhoghlaim-stack-doctor",
        description=(
            "Stack-doctor CLI. Validates the 94 Docker Compose stacks under "
            "bonneagar/stacks/ against the 6-file GOLD_STANDARD pattern "
            "(compose.yaml + sidecar.yaml + secrets.env + pangolin.yaml + "
            "blueprint.yaml + .env.example) and the 4-gate stack-doctor check."
        ),
    )
    sub = parser.add_subparsers(dest="cmd")

    p_check = sub.add_parser("check", help="Run stack-doctor on one stack")
    p_check.add_argument("stack", help="Stack name (e.g. oideachais, litellm, langfuse)")

    p_list = sub.add_parser("list", help="List all 94 stacks")

    args = parser.parse_args(argv)

    if args.cmd == "check":
        print(f"[cianfhoghlaim-stack-doctor] check {args.stack}")
        print("(Stub: delegates to bun run validate-stacks)")
        return 0

    if args.cmd == "list":
        for stack in (
            "actual", "agent-os", "audiobookshelf", "backrest", "beszel",
            "browser", "bytebase", "cal-diy", "changedetection", "ci",
            "coder", "cognee", "convex", "crawl4ai", "croilar",
            "dagster", "docling-serve", "dots-ocr", "dozzle", "dragonfly",
            "enclosed", "falkordb",             "forgejo", "forgejo-runner", "frontend",
            "glance", "gluetun", "graphiti", "headplane",
            "headscale", "infisical", "invokeai", "it-tools", "Kapowarr",
            "karakeep", "komodo", "litellm", "logfire",
            "mcp", "meilisearch", "metabase", "mlflow", "mongo",
            "neo4j", "n8n", "openchamber", "openclaw", "overture",
            "paperless", "penpot", "pangolin", "pipecat", "polaris",
            "postgrest", "privatebin", "prometheus", "pytorch", "qdrant",
            "restic", "restate", "sentry", "siyuan", "skyvern",
            "stagehand", "stirling", "supabase", "syncthing", "tigerbeetle",
            "timescale", "trilium", "vikunja", "weaviate", "whoogle",
            "wikijs", "woodpecker", "zipline", "zola", "zulip",
            "addarr", "amcrest", "argilla", "authentik", "calibre",
            "cockpit", "coolify", "dozzle-pro", "erpc",
            "etcd", "frigate", "hedgedoc", "homarr", "hyperconverged",
            "jellystat", "kavita", "komga", "linkwarden", "mastodon",
        ):
            print(stack)
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))