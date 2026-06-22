"""
MCP Server for EduVision.

Provides MCP tools for agent-friendly access to educational asset generation.
"""

import json
from typing import Optional

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.types import Tool, TextContent


# Initialize MCP server
server = Server("eduvision")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools."""
    return [
        Tool(
            name="generate_fibo_image",
            description="Generate an educational image using FIBO from concept description",
            inputSchema={
                "type": "object",
                "properties": {
                    "subject": {
                        "type": "string",
                        "enum": ["chemistry", "biology", "geography"],
                        "description": "Educational subject",
                    },
                    "concept_title": {
                        "type": "string",
                        "description": "Title of the concept to visualize",
                    },
                    "description": {
                        "type": "string",
                        "description": "What the image should show",
                    },
                    "style": {
                        "type": "string",
                        "enum": ["digital_illustration", "scientific_diagram", "photography", "line_art"],
                        "default": "digital_illustration",
                    },
                    "aspect_ratio": {
                        "type": "string",
                        "enum": ["1:1", "16:9", "4:3"],
                        "default": "16:9",
                    },
                    "seed": {
                        "type": "integer",
                        "description": "Random seed for reproducibility (-1 for random)",
                        "default": -1,
                    },
                },
                "required": ["subject", "concept_title", "description"],
            },
        ),
        Tool(
            name="search_visual_concepts",
            description="Search curriculum for concepts with visual requirements",
            inputSchema={
                "type": "object",
                "properties": {
                    "subject": {
                        "type": "string",
                        "enum": ["chemistry", "biology", "geography"],
                        "description": "Subject to search in",
                    },
                    "query": {
                        "type": "string",
                        "description": "Search query for visual concepts",
                    },
                    "limit": {
                        "type": "integer",
                        "default": 5,
                        "description": "Maximum results to return",
                    },
                },
                "required": ["subject", "query"],
            },
        ),
        Tool(
            name="get_curriculum_tree",
            description="Get hierarchical curriculum structure for a subject",
            inputSchema={
                "type": "object",
                "properties": {
                    "subject": {
                        "type": "string",
                        "enum": ["chemistry", "biology", "geography"],
                        "description": "Subject to get curriculum for",
                    },
                },
                "required": ["subject"],
            },
        ),
        Tool(
            name="validate_image",
            description="Validate a generated educational image against curriculum requirements",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_path": {
                        "type": "string",
                        "description": "Path to the image file",
                    },
                    "concept_title": {
                        "type": "string",
                        "description": "Expected concept title",
                    },
                    "concept_description": {
                        "type": "string",
                        "description": "Expected concept description",
                    },
                },
                "required": ["image_path", "concept_title"],
            },
        ),
        Tool(
            name="get_asset_attribution",
            description="Get curriculum attribution for a generated asset",
            inputSchema={
                "type": "object",
                "properties": {
                    "asset_id": {
                        "type": "string",
                        "description": "Asset identifier",
                    },
                },
                "required": ["asset_id"],
            },
        ),
        Tool(
            name="list_generated_assets",
            description="List generated educational assets in the gallery",
            inputSchema={
                "type": "object",
                "properties": {
                    "subject": {
                        "type": "string",
                        "enum": ["chemistry", "biology", "geography"],
                        "description": "Filter by subject (optional)",
                    },
                    "limit": {
                        "type": "integer",
                        "default": 20,
                        "description": "Maximum assets to return",
                    },
                },
                "required": [],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""

    if name == "generate_fibo_image":
        return await _generate_fibo_image(**arguments)

    elif name == "search_visual_concepts":
        return await _search_visual_concepts(**arguments)

    elif name == "get_curriculum_tree":
        return await _get_curriculum_tree(**arguments)

    elif name == "validate_image":
        return await _validate_image(**arguments)

    elif name == "get_asset_attribution":
        return await _get_asset_attribution(**arguments)

    elif name == "list_generated_assets":
        return await _list_generated_assets(**arguments)

    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def _generate_fibo_image(
    subject: str,
    concept_title: str,
    description: str,
    style: str = "digital_illustration",
    aspect_ratio: str = "16:9",
    seed: int = -1,
) -> list[TextContent]:
    """Generate an educational image using FIBO."""
    try:
        from .components.fibo_controls import build_fibo_json
        from .components.image_preview import generate_preview, save_to_gallery

        # Build FIBO JSON
        fibo_json = build_fibo_json(
            title=concept_title,
            description=description,
            style=style,
            aspect_ratio=aspect_ratio,
            subject=subject,
        )

        # Generate image
        image, status, validation = generate_preview(
            fibo_json=fibo_json,
            seed=seed if seed >= 0 else None,
        )

        if image is None:
            return [TextContent(type="text", text=f"Generation failed: {status}")]

        # Save to gallery
        image_path = save_to_gallery(
            image=image,
            fibo_json=fibo_json,
            validation=validation,
            subject=subject,
        )

        result = {
            "status": "success",
            "image_path": image_path,
            "validation_score": validation.get("scores", {}).get("overall", 0),
            "fibo_json": fibo_json,
        }

        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def _search_visual_concepts(
    subject: str,
    query: str,
    limit: int = 5,
) -> list[TextContent]:
    """Search curriculum for visual concepts."""
    try:
        from ..db.tables import search_concepts

        results = search_concepts(
            query=query,
            subject=subject,
            limit=limit,
        )

        return [TextContent(type="text", text=json.dumps(results, indent=2))]

    except Exception as e:
        # Fallback to basic search
        from .components.subject_selector import get_learning_outcomes

        outcomes = get_learning_outcomes(subject)

        # Filter by query
        query_lower = query.lower()
        matches = [
            o for o in outcomes
            if query_lower in o.get("description", "").lower()
            or query_lower in o.get("topic", "").lower()
        ][:limit]

        return [TextContent(type="text", text=json.dumps(matches, indent=2))]


async def _get_curriculum_tree(subject: str) -> list[TextContent]:
    """Get curriculum tree for a subject."""
    from .components.subject_selector import get_curriculum_tree

    tree = get_curriculum_tree(subject)
    return [TextContent(type="text", text=json.dumps(tree, indent=2))]


async def _validate_image(
    image_path: str,
    concept_title: str,
    concept_description: str = "",
) -> list[TextContent]:
    """Validate an educational image."""
    try:
        from PIL import Image
        from .components.image_preview import validate_generated_image

        image = Image.open(image_path)

        result = validate_generated_image(
            image=image,
            fibo_json={
                "short_description": concept_description,
                "_metadata": {"concept_title": concept_title},
            },
        )

        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    except Exception as e:
        return [TextContent(type="text", text=f"Validation error: {str(e)}")]


async def _get_asset_attribution(asset_id: str) -> list[TextContent]:
    """Get attribution for an asset."""
    from .components.asset_gallery import get_asset_attribution

    attribution = get_asset_attribution(asset_id)
    return [TextContent(type="text", text=json.dumps(attribution, indent=2))]


async def _list_generated_assets(
    subject: Optional[str] = None,
    limit: int = 20,
) -> list[TextContent]:
    """List generated assets."""
    from .components.asset_gallery import get_generated_assets

    assets = get_generated_assets(subject=subject, limit=limit)

    # Simplify for output
    simplified = [
        {
            "asset_id": a["asset_id"],
            "subject": a["subject"],
            "concept_title": a["concept_title"],
            "validation_score": a["validation_score"],
            "image_path": a["image_path"],
        }
        for a in assets
    ]

    return [TextContent(type="text", text=json.dumps(simplified, indent=2))]


async def run_server():
    """Run the MCP server."""
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="eduvision",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(run_server())
