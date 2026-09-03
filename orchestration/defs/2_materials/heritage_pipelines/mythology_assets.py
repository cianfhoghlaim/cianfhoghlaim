"""
Mythology Assets for Tuath.

Ingests Celtic mythology, folklore, and cultural content for game NPCs.
"""

import os
from pathlib import Path
from typing import Any

import dlt
import yaml
from dagster import (
    AssetExecutionContext,
    MetadataValue,
    StaticPartitionsDefinition,
    asset,
)

from dlt_sources.common.destinations_tuatha import create_pipeline

# Partitions for mythology traditions/cycles
tradition_partitions = StaticPartitionsDefinition([
    "irish_mythology",
    "welsh_mythology",
    "scottish_folklore",
    "cornish_folklore",
    "breton_folklore",
    "manx_folklore",
])

# Mythological cycles for each tradition
MYTHOLOGY_CYCLES = {
    "irish_mythology": [
        "mythological_cycle",  # Tuatha Dé Danann
        "ulster_cycle",  # Cú Chulainn
        "fenian_cycle",  # Fionn mac Cumhaill
        "historical_cycle",  # Kings and heroes
    ],
    "welsh_mythology": [
        "mabinogion",  # Four Branches
        "arthurian",  # Welsh Arthur
        "taliesin",  # Bardic tradition
    ],
    "scottish_folklore": [
        "fairy_lore",
        "selkie_tales",
        "highland_legends",
    ],
    "cornish_folklore": [
        "giants",
        "piskies",
        "knockers",
    ],
    "breton_folklore": [
        "korrigans",
        "ankou",
        "arthurian_breton",
    ],
    "manx_folklore": [
        "fairy_bridge",
        "moddey_dhoo",
        "buggane",
    ],
}


def load_mythology_config(tradition: str) -> dict[str, Any]:
    """Load mythology configuration from YAML."""
    config_path = Path(__file__).parent.parent / "config" / "mythology.yaml"
    if config_path.exists():
        with open(config_path) as f:
            config = yaml.safe_load(f) or {}
            return config.get(tradition, {})
    return {}


@asset(
    partitions_def=tradition_partitions,
    group_name="mythology",
    description="Celtic mythological characters for NPC generation",
)
def celtic_characters(context: AssetExecutionContext) -> dict:
    """Fetch and structure mythological character data."""
    tradition = context.partition_key
    config = load_mythology_config(tradition)

    pipeline = create_pipeline(
        project="tuath",
        pipeline_name=f"mythology_{tradition}",
        dataset_name="mythology",
    )

    cycles = config.get("cycles", MYTHOLOGY_CYCLES.get(tradition, []))

    # Character data from various sources
    characters = []

    # Import from DLT source if available
    try:
        from dlt_sources.language.mythology.celtic_mythology import celtic_mythology_source

        source = celtic_mythology_source(
            tradition=tradition,
            cycles=cycles,
            resource_types=["characters"],
        )

        info = pipeline.run(source)
        rows_loaded = getattr(info, "loads_info", {}).get("loads", 0)
    except Exception as e:
        context.log.warning(f"DLT source not available for {tradition}: {e}")
        # Use embedded character data
        characters = get_embedded_characters(tradition)
        rows_loaded = len(characters)

        if characters:
            pipeline.run(characters, table_name="characters")

    context.add_output_metadata({
        "tradition": tradition,
        "cycles": MetadataValue.json(cycles),
        "characters_loaded": MetadataValue.int(rows_loaded),
    })

    return {
        "tradition": tradition,
        "status": "success",
        "characters": rows_loaded,
    }


@asset(
    partitions_def=tradition_partitions,
    group_name="mythology",
    description="Celtic mythological stories and tales",
)
def celtic_stories(context: AssetExecutionContext) -> dict:
    """Fetch mythological stories and narrative content."""
    tradition = context.partition_key
    config = load_mythology_config(tradition)

    pipeline = create_pipeline(
        project="tuath",
        pipeline_name=f"stories_{tradition}",
        dataset_name="mythology",
    )

    cycles = config.get("cycles", MYTHOLOGY_CYCLES.get(tradition, []))

    try:
        from dlt_sources.language.mythology.celtic_mythology import celtic_mythology_source

        source = celtic_mythology_source(
            tradition=tradition,
            cycles=cycles,
            resource_types=["stories"],
        )

        info = pipeline.run(source)
        rows_loaded = getattr(info, "loads_info", {}).get("loads", 0)
    except Exception as e:
        context.log.warning(f"DLT source not available for {tradition}: {e}")
        stories = get_embedded_stories(tradition)
        rows_loaded = len(stories)

        if stories:
            pipeline.run(stories, table_name="stories")

    context.add_output_metadata({
        "tradition": tradition,
        "stories_loaded": MetadataValue.int(rows_loaded),
    })

    return {
        "tradition": tradition,
        "status": "success",
        "stories": rows_loaded,
    }


@asset(
    partitions_def=tradition_partitions,
    group_name="mythology",
    description="Mythological locations and sacred sites",
)
def celtic_locations(context: AssetExecutionContext) -> dict:
    """Fetch mythological location data for game world."""
    tradition = context.partition_key

    pipeline = create_pipeline(
        project="tuath",
        pipeline_name=f"locations_{tradition}",
        dataset_name="mythology",
    )

    try:
        from dlt_sources.language.mythology.celtic_mythology import celtic_mythology_source

        source = celtic_mythology_source(
            tradition=tradition,
            resource_types=["locations"],
        )

        info = pipeline.run(source)
        rows_loaded = getattr(info, "loads_info", {}).get("loads", 0)
    except Exception as e:
        context.log.warning(f"DLT source not available for {tradition}: {e}")
        locations = get_embedded_locations(tradition)
        rows_loaded = len(locations)

        if locations:
            pipeline.run(locations, table_name="locations")

    context.add_output_metadata({
        "tradition": tradition,
        "locations_loaded": MetadataValue.int(rows_loaded),
    })

    return {
        "tradition": tradition,
        "status": "success",
        "locations": rows_loaded,
    }


@asset(
    group_name="mythology",
    deps=["celtic_characters", "celtic_stories", "celtic_locations"],
    description="Aggregate mythology statistics",
)
def mythology_aggregate(context: AssetExecutionContext) -> dict:
    """Compute aggregate statistics across all mythology data."""
    import duckdb

    db_path = os.environ.get("DUCKDB_PATH", "storage/duckdb/tuath.duckdb")

    stats = {
        "total_characters": 0,
        "total_stories": 0,
        "total_locations": 0,
        "traditions": {},
    }

    try:
        conn = duckdb.connect(db_path, read_only=True)

        # Character counts
        try:
            char_counts = conn.execute(
                """
                SELECT tradition, COUNT(*) as count
                FROM mythology.characters
                GROUP BY tradition
                """
            ).fetchall()

            for tradition, count in char_counts:
                if tradition not in stats["traditions"]:
                    stats["traditions"][tradition] = {}
                stats["traditions"][tradition]["characters"] = count
                stats["total_characters"] += count
        except Exception:
            pass

        # Story counts
        try:
            story_counts = conn.execute(
                """
                SELECT tradition, COUNT(*) as count
                FROM mythology.stories
                GROUP BY tradition
                """
            ).fetchall()

            for tradition, count in story_counts:
                if tradition not in stats["traditions"]:
                    stats["traditions"][tradition] = {}
                stats["traditions"][tradition]["stories"] = count
                stats["total_stories"] += count
        except Exception:
            pass

        # Location counts
        try:
            loc_counts = conn.execute(
                """
                SELECT tradition, COUNT(*) as count
                FROM mythology.locations
                GROUP BY tradition
                """
            ).fetchall()

            for tradition, count in loc_counts:
                if tradition not in stats["traditions"]:
                    stats["traditions"][tradition] = {}
                stats["traditions"][tradition]["locations"] = count
                stats["total_locations"] += count
        except Exception:
            pass

        conn.close()

    except Exception as e:
        context.log.warning(f"Failed to compute mythology stats: {e}")

    context.add_output_metadata({
        "total_characters": stats["total_characters"],
        "total_stories": stats["total_stories"],
        "total_locations": stats["total_locations"],
        "traditions_covered": len(stats["traditions"]),
    })

    return stats


# Embedded data for development when DLT sources are not available
def get_embedded_characters(tradition: str) -> list[dict]:
    """Get embedded character data for a tradition."""
    characters = {
        "irish_mythology": [
            {
                "id": "cu_chulainn",
                "name": "Cú Chulainn",
                "irish_name": "Cú Chulainn",
                "tradition": "irish_mythology",
                "cycle": "ulster_cycle",
                "type": "hero",
                "description": "The Hound of Ulster, greatest warrior of the Red Branch Knights",
                "powers": ["ríastrad (warp spasm)", "gáe bolga", "superhuman strength"],
                "relationships": ["Emer (wife)", "Scáthach (teacher)", "Connla (son)"],
            },
            {
                "id": "lugh",
                "name": "Lugh",
                "irish_name": "Lugh Lámhfhada",
                "tradition": "irish_mythology",
                "cycle": "mythological_cycle",
                "type": "deity",
                "description": "The Long-Armed One, master of all arts",
                "powers": ["all skills mastery", "spear of light", "leadership"],
                "relationships": ["Cian (father)", "Balor (grandfather)", "Cú Chulainn (son in some versions)"],
            },
            {
                "id": "fionn",
                "name": "Fionn mac Cumhaill",
                "irish_name": "Fionn mac Cumhaill",
                "tradition": "irish_mythology",
                "cycle": "fenian_cycle",
                "type": "hero",
                "description": "Leader of the Fianna, gained wisdom from the Salmon of Knowledge",
                "powers": ["prophetic thumb", "wisdom", "leadership"],
                "relationships": ["Sadhbh (wife)", "Oisín (son)", "Oscar (grandson)"],
            },
        ],
        "welsh_mythology": [
            {
                "id": "pryderi",
                "name": "Pryderi",
                "welsh_name": "Pryderi fab Pwyll",
                "tradition": "welsh_mythology",
                "cycle": "mabinogion",
                "type": "hero",
                "description": "Son of Pwyll and Rhiannon, appears in all Four Branches",
                "powers": ["strength", "nobility"],
                "relationships": ["Pwyll (father)", "Rhiannon (mother)", "Cigfa (wife)"],
            },
            {
                "id": "gwydion",
                "name": "Gwydion",
                "welsh_name": "Gwydion fab Dôn",
                "tradition": "welsh_mythology",
                "cycle": "mabinogion",
                "type": "magician",
                "description": "The greatest magician and trickster of Welsh mythology",
                "powers": ["illusion", "transformation", "wisdom"],
                "relationships": ["Dôn (mother)", "Math (uncle)", "Lleu (nephew)"],
            },
        ],
    }
    return characters.get(tradition, [])


def get_embedded_stories(tradition: str) -> list[dict]:
    """Get embedded story data for a tradition."""
    stories = {
        "irish_mythology": [
            {
                "id": "tain_bo_cuailnge",
                "title": "Táin Bó Cúailnge",
                "english_title": "The Cattle Raid of Cooley",
                "tradition": "irish_mythology",
                "cycle": "ulster_cycle",
                "summary": "Queen Medb of Connacht invades Ulster to steal the Brown Bull",
                "themes": ["heroism", "honor", "warfare"],
                "main_characters": ["Cú Chulainn", "Medb", "Fergus mac Róich"],
            },
            {
                "id": "oidheadh_chlainne_lir",
                "title": "Oidheadh Chlainne Lir",
                "english_title": "The Children of Lir",
                "tradition": "irish_mythology",
                "cycle": "mythological_cycle",
                "summary": "Four children cursed to spend 900 years as swans",
                "themes": ["transformation", "patience", "redemption"],
                "main_characters": ["Fionnuala", "Aodh", "Fiachra", "Conn"],
            },
        ],
        "welsh_mythology": [
            {
                "id": "branwen",
                "title": "Branwen ferch Llŷr",
                "english_title": "Branwen Daughter of Llŷr",
                "tradition": "welsh_mythology",
                "cycle": "mabinogion",
                "summary": "Branwen's marriage leads to war between Britain and Ireland",
                "themes": ["honor", "vengeance", "tragedy"],
                "main_characters": ["Branwen", "Bendigeidfran", "Efnysien"],
            },
        ],
    }
    return stories.get(tradition, [])


def get_embedded_locations(tradition: str) -> list[dict]:
    """Get embedded location data for a tradition."""
    locations = {
        "irish_mythology": [
            {
                "id": "emain_macha",
                "name": "Emain Macha",
                "english_name": "Navan Fort",
                "tradition": "irish_mythology",
                "type": "royal_seat",
                "description": "Capital of Ulster and seat of King Conchobar mac Nessa",
                "latitude": 54.3483,
                "longitude": -6.6950,
                "associated_stories": ["Táin Bó Cúailnge", "Deirdre of the Sorrows"],
            },
            {
                "id": "tir_na_nog",
                "name": "Tír na nÓg",
                "english_name": "Land of the Young",
                "tradition": "irish_mythology",
                "type": "otherworld",
                "description": "The supernatural realm where time stands still",
                "latitude": None,
                "longitude": None,
                "associated_stories": ["Oisín in Tír na nÓg"],
            },
        ],
        "welsh_mythology": [
            {
                "id": "annwfn",
                "name": "Annwfn",
                "english_name": "The Otherworld",
                "tradition": "welsh_mythology",
                "type": "otherworld",
                "description": "The Welsh otherworld, ruled by Arawn",
                "latitude": None,
                "longitude": None,
                "associated_stories": ["Pwyll Pendefig Dyfed"],
            },
            {
                "id": "dinas_bran",
                "name": "Dinas Brân",
                "english_name": "Crow Castle",
                "tradition": "welsh_mythology",
                "type": "fortress",
                "description": "Hillfort associated with Brân the Blessed",
                "latitude": 52.9801,
                "longitude": -3.1681,
                "associated_stories": ["Branwen ferch Llŷr"],
            },
        ],
    }
    return locations.get(tradition, [])
