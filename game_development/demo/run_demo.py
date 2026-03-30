#!/usr/bin/env python3
"""
Tuath Celtic Educational MMO - Demo Script.

Demonstrates the complete flow:
1. Authentication (SIWE)
2. Hybrid search across curriculum and mythology
3. CopilotKit agent interaction
4. Game state management
5. Knowledge graph traversal
"""

import asyncio
import json
from datetime import datetime

import httpx


BASE_URL = "http://localhost:8000"


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
        print(f"Celtic Greeting: {data['celtic_greeting']}")


async def demo_root_endpoint():
    """Show available endpoints."""
    print("\n" + "=" * 60)
    print("2. API OVERVIEW")
    print("=" * 60)

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/")
        data = response.json()

        print(f"Message: {data['message']}")
        print(f"Description: {data['description']}")
        print("\nSupported Languages:")
        for lang in data["languages"]:
            print(f"  - {lang}")
        print("\nAvailable Endpoints:")
        for name, path in data["endpoints"].items():
            print(f"  {name}: {path}")


async def demo_hybrid_search():
    """Demonstrate hybrid search capabilities."""
    print("\n" + "=" * 60)
    print("3. HYBRID SEARCH DEMO")
    print("=" * 60)

    async with httpx.AsyncClient() as client:
        # Search for Celtic warriors
        print("\n--- Searching for 'Celtic warriors' (hybrid mode) ---")
        response = await client.post(
            f"{BASE_URL}/search/",
            json={
                "query": "Celtic warriors and heroes",
                "mode": "hybrid",
                "limit": 5,
                "vector_weight": 0.6,
                "graph_weight": 0.4,
                "include_relationships": True,
            },
        )

        if response.status_code == 200:
            data = response.json()
            print(f"Query: {data['query']}")
            print(f"Mode: {data['mode']}")
            print(f"Total Results: {data['total']}")

            for result in data["results"][:3]:
                print(f"\n  - {result['title']} ({result['content_type']})")
                print(f"    Score: {result['score']:.3f}")
                print(f"    Source: {result['source']}")
                if result.get("related_entities"):
                    print(f"    Related: {', '.join(result['related_entities'][:3])}")
        else:
            print(f"Search returned: {response.status_code}")
            print("(Search engine may need to be initialized)")


async def demo_curriculum_search():
    """Search Celtic curriculum content."""
    print("\n" + "=" * 60)
    print("4. CURRICULUM SEARCH DEMO")
    print("=" * 60)

    async with httpx.AsyncClient() as client:
        # Search Irish curriculum
        print("\n--- Searching Irish Junior Cycle Language Content ---")
        response = await client.get(
            f"{BASE_URL}/search/curriculum",
            params={
                "query": "greetings and introductions",
                "nation": "ireland",
                "level": "junior_cycle",
                "subject": "language",
                "limit": 5,
            },
        )

        if response.status_code == 200:
            data = response.json()
            print(f"Query: {data['query']}")
            print(f"Filters: {json.dumps(data['filters'], indent=2)}")
            print(f"Total: {data['total']}")
        else:
            print(f"Curriculum search returned: {response.status_code}")


async def demo_mythology_search():
    """Search Celtic mythology content."""
    print("\n" + "=" * 60)
    print("5. MYTHOLOGY SEARCH DEMO")
    print("=" * 60)

    async with httpx.AsyncClient() as client:
        # Search Ulster Cycle characters
        print("\n--- Searching Ulster Cycle Characters ---")
        response = await client.get(
            f"{BASE_URL}/search/mythology",
            params={
                "query": "hero warrior",
                "tradition": "irish_mythology",
                "cycle": "ulster_cycle",
                "content_type": "character",
                "limit": 5,
            },
        )

        if response.status_code == 200:
            data = response.json()
            print(f"Query: {data['query']}")
            print(f"Filters: {json.dumps(data['filters'], indent=2)}")
            print(f"Total: {data['total']}")
        else:
            print(f"Mythology search returned: {response.status_code}")


async def demo_search_suggestions():
    """Get search suggestions."""
    print("\n" + "=" * 60)
    print("6. SEARCH SUGGESTIONS DEMO")
    print("=" * 60)

    async with httpx.AsyncClient() as client:
        partials = ["Cú", "Fionn", "Tuatha"]

        for partial in partials:
            response = await client.get(
                f"{BASE_URL}/search/suggest",
                params={"partial": partial, "limit": 3},
            )

            if response.status_code == 200:
                data = response.json()
                print(f"\nPartial: '{partial}'")
                print(f"Suggestions: {data['suggestions']}")


async def demo_agent_interaction():
    """Demonstrate CopilotKit agent."""
    print("\n" + "=" * 60)
    print("7. COPILOTKIT AGENT DEMO")
    print("=" * 60)

    async with httpx.AsyncClient() as client:
        # List available agents
        print("\n--- Available Agents ---")
        response = await client.get(f"{BASE_URL}/copilotkit/agents")

        if response.status_code == 200:
            agents = response.json()
            for agent in agents.get("agents", []):
                print(f"  - {agent.get('name', 'Unknown')}: {agent.get('description', 'No description')}")
        else:
            print(f"Agents endpoint returned: {response.status_code}")

        # Simulate chat (would be SSE in production)
        print("\n--- Simulated Agent Interaction ---")
        print("User: Tell me about Cú Chulainn")
        print("Agent: [Would stream A2UI events via SSE]")
        print("  - lifecycle.start")
        print("  - state.snapshot {vocabulary: [], currentQuest: null}")
        print("  - tool.call.start {name: 'search_mythology'}")
        print("  - render.component {type: 'CharacterCard', props: {...}}")
        print("  - message.delta 'Cú Chulainn is the great hero of...'")


async def demo_game_mechanics():
    """Demonstrate game mechanics concepts."""
    print("\n" + "=" * 60)
    print("8. GAME MECHANICS DEMO")
    print("=" * 60)

    print("\n--- Celtic Nations & Regions ---")
    nations = [
        ("Ireland", "Éire", ["Connacht", "Munster", "Ulster", "Leinster"]),
        ("Wales", "Cymru", ["Gwynedd", "Powys", "Dyfed"]),
        ("Scotland", "Alba", ["Highlands", "Lowlands", "Islands"]),
    ]

    for name, native, regions in nations:
        print(f"\n  {name} ({native}):")
        for region in regions:
            print(f"    - {region}")

    print("\n--- Mythology Cycles ---")
    cycles = {
        "Irish": [
            "Mythological Cycle (Tuatha Dé Danann)",
            "Ulster Cycle (Red Branch Knights)",
            "Fenian Cycle (Fionn mac Cumhaill)",
            "Cycles of the Kings (Historical)",
        ],
        "Welsh": [
            "Four Branches of the Mabinogi",
            "Arthurian Tales",
            "Independent Tales",
        ],
    }

    for tradition, cycle_list in cycles.items():
        print(f"\n  {tradition} Mythology:")
        for cycle in cycle_list:
            print(f"    - {cycle}")


async def demo_payment_config():
    """Show x402 payment configuration."""
    print("\n" + "=" * 60)
    print("9. x402 PAYMENT CONFIGURATION")
    print("=" * 60)

    print("\n--- Micropayment Pricing ---")
    pricing = {
        "chat_message": {"price_usd": 0.01, "free_daily": 5},
        "knowledge_search": {"price_usd": 0.02, "free_daily": 3},
        "premium_quest": {"price_usd": 0.05, "free_daily": 0},
        "analytics": {"price_usd": 0.05, "free_daily": 0},
    }

    for service, config in pricing.items():
        print(f"\n  {service}:")
        print(f"    Price: ${config['price_usd']:.2f}")
        print(f"    Free daily: {config['free_daily']}")


async def main():
    """Run all demos."""
    print("\n" + "=" * 60)
    print("TUATH CELTIC EDUCATIONAL MMO - DEMO")
    print("Language Learning Through Mythology")
    print("=" * 60)
    print(f"Started: {datetime.now().isoformat()}")
    print(f"API Base: {BASE_URL}")

    try:
        await demo_health_check()
        await demo_root_endpoint()
        await demo_hybrid_search()
        await demo_curriculum_search()
        await demo_mythology_search()
        await demo_search_suggestions()
        await demo_agent_interaction()
        await demo_game_mechanics()
        await demo_payment_config()

        print("\n" + "=" * 60)
        print("DEMO COMPLETE")
        print("=" * 60)
        print("\nTo run the full API:")
        print("  cd sruth/tuath")
        print("  uv run uvicorn tuath.api.main:app --reload")
        print("\nTo run tests:")
        print("  uv run pytest sruth/tuath/tests/ -v")

    except httpx.ConnectError:
        print("\n[!] Could not connect to API.")
        print("    Make sure the API is running at", BASE_URL)
        print("\n    To start: uv run uvicorn tuath.api.main:app --reload")


if __name__ == "__main__":
    asyncio.run(main())
