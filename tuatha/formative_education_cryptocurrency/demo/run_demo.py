#!/usr/bin/env python3
"""
Crypteolas - GitHub Intelligence + DeFi Analytics Demo.

Demonstrates the complete flow:
1. GitHub repository analysis
2. DeFi protocol metrics
3. Hybrid search across both domains
4. CopilotKit agent for research assistance
5. Cross-domain correlation
"""

import asyncio
import json
from datetime import datetime

import httpx


BASE_URL = "http://localhost:8001"


async def demo_health_check():
    """Check API health."""
    print("\n" + "=" * 60)
    print("1. HEALTH CHECK")
    print("=" * 60)

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/health")
        data = response.json()

        print(f"Status: {data['status']}")
        print(f"Service: {data['service']}")


async def demo_root_endpoint():
    """Show available endpoints."""
    print("\n" + "=" * 60)
    print("2. API OVERVIEW")
    print("=" * 60)

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/")
        data = response.json()

        print(f"Message: {data['message']}")
        print("\nAvailable Endpoints:")
        for name, path in data.get("endpoints", {}).items():
            print(f"  {name}: {path}")


async def demo_github_intelligence():
    """Demonstrate GitHub intelligence features."""
    print("\n" + "=" * 60)
    print("3. GITHUB INTELLIGENCE DEMO")
    print("=" * 60)

    async with httpx.AsyncClient(timeout=30.0) as client:
        # Search for DeFi repositories
        print("\n--- Searching DeFi Repositories ---")
        response = await client.get(
            f"{BASE_URL}/github/repos/search",
            params={
                "query": "DeFi smart contracts",
                "language": "Solidity",
                "min_stars": 100,
            },
        )

        if response.status_code == 200:
            data = response.json()
            print(f"Total repositories found: {data.get('total', 0)}")
            for repo in data.get("results", [])[:3]:
                print(f"\n  - {repo.get('full_name')}")
                print(f"    Stars: {repo.get('stars')}")
                print(f"    Language: {repo.get('language')}")
        else:
            print(f"GitHub search returned: {response.status_code}")

        # Get trending repositories
        print("\n--- Trending Repositories (Python) ---")
        response = await client.get(
            f"{BASE_URL}/github/trending",
            params={"language": "Python", "limit": 5},
        )

        if response.status_code == 200:
            data = response.json()
            for repo in data.get("repos", [])[:3]:
                print(f"  - {repo.get('full_name')}: +{repo.get('stars_today', 0)} today")
        else:
            print(f"Trending returned: {response.status_code}")


async def demo_defi_analytics():
    """Demonstrate DeFi analytics features."""
    print("\n" + "=" * 60)
    print("4. DeFi ANALYTICS DEMO")
    print("=" * 60)

    async with httpx.AsyncClient(timeout=30.0) as client:
        # List protocols
        print("\n--- Top DeFi Protocols by TVL ---")
        response = await client.get(
            f"{BASE_URL}/defi/protocols",
            params={"limit": 10, "sort": "tvl"},
        )

        if response.status_code == 200:
            data = response.json()
            for protocol in data.get("protocols", [])[:5]:
                tvl = protocol.get("tvl", 0) / 1e9
                print(f"  - {protocol.get('name')}: ${tvl:.2f}B TVL")
        else:
            print(f"Protocols returned: {response.status_code}")

        # Get yield opportunities
        print("\n--- Top Yield Opportunities ---")
        response = await client.get(
            f"{BASE_URL}/defi/pools",
            params={"min_apy": 5, "limit": 5},
        )

        if response.status_code == 200:
            data = response.json()
            for pool in data.get("pools", [])[:5]:
                print(f"  - {pool.get('protocol')}/{pool.get('pool_id')}: {pool.get('apy')}% APY")
        else:
            print(f"Pools returned: {response.status_code}")

        # Chain TVL breakdown
        print("\n--- TVL by Chain ---")
        response = await client.get(f"{BASE_URL}/defi/metrics/tvl")

        if response.status_code == 200:
            data = response.json()
            for chain, tvl in list(data.get("by_chain", {}).items())[:5]:
                tvl_b = tvl / 1e9
                print(f"  - {chain}: ${tvl_b:.2f}B")
        else:
            print(f"TVL metrics returned: {response.status_code}")


async def demo_hybrid_search():
    """Demonstrate hybrid search across GitHub and DeFi."""
    print("\n" + "=" * 60)
    print("5. HYBRID SEARCH DEMO")
    print("=" * 60)

    async with httpx.AsyncClient() as client:
        # Search across both domains
        print("\n--- Searching 'lending protocols' (hybrid mode) ---")
        response = await client.post(
            f"{BASE_URL}/search/",
            json={
                "query": "lending protocols with high TVL and active development",
                "mode": "hybrid",
                "limit": 5,
                "content_types": ["protocol", "repository"],
            },
        )

        if response.status_code == 200:
            data = response.json()
            print(f"Query: {data['query']}")
            print(f"Mode: {data['mode']}")
            print(f"Total Results: {data['total']}")

            for result in data.get("results", [])[:3]:
                print(f"\n  - {result['title']} ({result['content_type']})")
                print(f"    Score: {result['score']:.3f}")
        else:
            print(f"Search returned: {response.status_code}")


async def demo_cross_domain_analysis():
    """Show GitHub-DeFi correlation analysis."""
    print("\n" + "=" * 60)
    print("6. CROSS-DOMAIN ANALYSIS DEMO")
    print("=" * 60)

    print("\n--- Protocol Development Metrics ---")
    protocols = [
        {
            "name": "Aave",
            "tvl": 10.5,
            "github_stars": 3500,
            "commits_30d": 150,
            "contributors": 95,
        },
        {
            "name": "Uniswap",
            "tvl": 5.2,
            "github_stars": 4200,
            "commits_30d": 200,
            "contributors": 120,
        },
        {
            "name": "Compound",
            "tvl": 2.8,
            "github_stars": 1800,
            "commits_30d": 45,
            "contributors": 55,
        },
    ]

    print(f"{'Protocol':<12} {'TVL':>8} {'Stars':>8} {'Commits':>10} {'Contributors':>14}")
    print("-" * 60)
    for p in protocols:
        print(
            f"{p['name']:<12} ${p['tvl']:>6.1f}B {p['github_stars']:>8} "
            f"{p['commits_30d']:>10} {p['contributors']:>14}"
        )

    print("\n--- Development Velocity Insights ---")
    print("  - Uniswap: Highest commit activity (200/30d)")
    print("  - Aave: Highest TVL ($10.5B) with strong dev activity")
    print("  - Compound: Lower recent activity, established codebase")


async def demo_agent_capabilities():
    """Demonstrate CopilotKit agent research capabilities."""
    print("\n" + "=" * 60)
    print("7. RESEARCH AGENT CAPABILITIES")
    print("=" * 60)

    print("\n--- Available Agent Tools ---")
    tools = [
        ("search_github", "Search GitHub repositories by query, language, topics"),
        ("get_repo_metrics", "Get detailed metrics for a specific repository"),
        ("analyze_contributors", "Analyze contributor patterns and expertise"),
        ("get_protocol_tvl", "Get current TVL and historical data for a protocol"),
        ("compare_yields", "Compare yield opportunities across pools"),
        ("correlate_dev_tvl", "Correlate development activity with TVL changes"),
    ]

    for name, desc in tools:
        print(f"  - {name}")
        print(f"    {desc}")

    print("\n--- Example Agent Query ---")
    print("User: Find lending protocols with the most active GitHub development")
    print("\nAgent would:")
    print("  1. Call search_github(category='lending')")
    print("  2. Call get_repo_metrics for top results")
    print("  3. Call get_protocol_tvl to correlate with on-chain data")
    print("  4. Render comparison table with render.component")


async def demo_data_pipeline():
    """Show Dagster pipeline configuration."""
    print("\n" + "=" * 60)
    print("8. DATA PIPELINE OVERVIEW")
    print("=" * 60)

    print("\n--- Dagster Assets ---")
    assets = [
        ("github_repositories", "DeFi repos from GitHub API", "hourly"),
        ("github_commits", "Commit history analysis", "hourly"),
        ("defi_protocols", "Protocol TVL from DeFiLlama", "15 min"),
        ("defi_pools", "Pool yields from DeFiLlama", "hourly"),
        ("embeddings", "BGE-M3 vectors for search", "on change"),
        ("knowledge_graph", "Neo4j relationships", "on change"),
    ]

    print(f"{'Asset':<25} {'Description':<35} {'Schedule':>12}")
    print("-" * 75)
    for name, desc, schedule in assets:
        print(f"{name:<25} {desc:<35} {schedule:>12}")

    print("\n--- Pipeline Jobs ---")
    jobs = [
        "github_sync_job: Sync all GitHub data",
        "defi_sync_job: Sync all DeFi data",
        "embedding_pipeline_job: Generate search embeddings",
        "full_sync_job: Complete data refresh",
    ]
    for job in jobs:
        print(f"  - {job}")


async def main():
    """Run all demos."""
    print("\n" + "=" * 60)
    print("CRYPTEOLAS - GITHUB INTELLIGENCE + DeFi ANALYTICS")
    print("Cross-Domain Crypto Research Platform")
    print("=" * 60)
    print(f"Started: {datetime.now().isoformat()}")
    print(f"API Base: {BASE_URL}")

    try:
        await demo_health_check()
        await demo_root_endpoint()
        await demo_github_intelligence()
        await demo_defi_analytics()
        await demo_hybrid_search()
        await demo_cross_domain_analysis()
        await demo_agent_capabilities()
        await demo_data_pipeline()

        print("\n" + "=" * 60)
        print("DEMO COMPLETE")
        print("=" * 60)
        print("\nTo run the full API:")
        print("  cd sruth/crypteolas")
        print("  uv run uvicorn crypteolas.api.main:app --port 8001 --reload")
        print("\nTo run tests:")
        print("  uv run pytest sruth/crypteolas/tests/ -v")
        print("\nTo start Dagster:")
        print("  dagster dev -m crypteolas.dagster_assets")

    except httpx.ConnectError:
        print("\n[!] Could not connect to API.")
        print("    Make sure the API is running at", BASE_URL)
        print("\n    To start: uv run uvicorn crypteolas.api.main:app --port 8001 --reload")


if __name__ == "__main__":
    asyncio.run(main())
