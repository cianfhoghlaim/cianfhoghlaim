"""
Mythology API Routes.

Search and retrieve Celtic mythology content for NPCs and lore.
Uses LanceDB for vector search with BGE-M3 multilingual embeddings.
"""

import os

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel

from ..services.mythology_service import MythologyService

router = APIRouter()

# Initialize mythology service with LanceDB
_mythology_service: MythologyService | None = None


def get_mythology_service() -> MythologyService:
    """Get or create mythology service singleton."""
    global _mythology_service
    if _mythology_service is None:
        lance_uri = os.environ.get("LANCEDB_URI", "storage/lance/tuath")
        _mythology_service = MythologyService(uri=lance_uri)
    return _mythology_service


class MythologyCharacter(BaseModel):
    """A mythological character."""

    id: str
    name: str
    native_names: dict[str, str]
    tradition: str
    cycle: str
    character_type: str
    description: str
    titles: list[str]
    relationships: dict[str, str]
    stories: list[str]
    game_role: str | None = None


class MythologyLocation(BaseModel):
    """A mythological location."""

    id: str
    name: str
    native_names: dict[str, str]
    tradition: str
    description: str
    significance: str
    characters: list[str]
    game_zone: str | None = None


class MythologyStory(BaseModel):
    """A mythological story."""

    id: str
    title: str
    native_title: str | None
    tradition: str
    cycle: str
    summary: str
    themes: list[str]
    main_characters: list[str]
    educational_value: str


@router.get("/characters")
async def get_characters(
    tradition: str | None = Query(None, description="Filter by tradition (irish, welsh, scottish)"),
    cycle: str | None = Query(None, description="Filter by mythological cycle"),
    character_type: str | None = Query(None, description="Filter by type (deity, hero, etc.)"),
    limit: int = Query(20, ge=1, le=100),
):
    """Get mythological characters from LanceDB or fallback data."""
    service = get_mythology_service()

    # Try to get characters from LanceDB
    db_results = await service.search_mythology(
        query=f"{tradition or ''} {cycle or ''} {character_type or 'character'}".strip(),
        tradition=tradition,
        entity_type=character_type or "character",
        limit=limit,
    )

    # Convert LanceDB results to response model
    characters = []
    for r in db_results:
        if r.get("entity_type") in ["deity", "hero", "bard", "character"]:
            characters.append(
                MythologyCharacter(
                    id=r.get("id", ""),
                    name=r.get("name", ""),
                    native_names={r.get("tradition", "ga")[:2]: r.get("name", "")},
                    tradition=r.get("tradition", ""),
                    cycle=r.get("metadata", {}).get("cycle", ""),
                    character_type=r.get("entity_type", "character"),
                    description=r.get("text", ""),
                    titles=[],
                    relationships={},
                    stories=r.get("metadata", {}).get("related_figures", []),
                    game_role=None,
                )
            )

    # If no results from LanceDB, use fallback data
    if not characters:
        fallback_characters = [
            MythologyCharacter(
                id="char_lugh",
                name="Lugh",
                native_names={"ga": "Lugh Lámhfhada"},
                tradition="irish",
                cycle="tuatha_de_danann",
                character_type="deity",
                description="God of skills, master of all arts, leader of the Tuatha Dé Danann against the Fomorians.",
                titles=["Lámhfhada (Long-Arm)", "Samildánach (Many-Skilled)"],
                relationships={"grandfather": "Balor", "father": "Cian", "son": "Cú Chulainn (some sources)"},
                stories=["Battle of Moytura", "Death of Balor"],
                game_role="Quest giver in Otherworld realm",
            ),
            MythologyCharacter(
                id="char_cu_chulainn",
                name="Cú Chulainn",
                native_names={"ga": "Cú Chulainn"},
                tradition="irish",
                cycle="ulster",
                character_type="hero",
                description="Greatest warrior of Ulster, known for his battle rage (ríastrad) and tragic fate.",
                titles=["Hound of Culann", "Champion of Ulster"],
                relationships={"father": "Lugh", "wife": "Emer", "trainer": "Scáthach"},
                stories=["Táin Bó Cúailnge", "Death of Cú Chulainn", "Training with Scáthach"],
                game_role="Warrior trainer in Ulster zone",
            ),
            MythologyCharacter(
                id="char_fionn",
                name="Fionn mac Cumhaill",
                native_names={"ga": "Fionn mac Cumhaill"},
                tradition="irish",
                cycle="fianna",
                character_type="hero",
                description="Legendary hunter-warrior who gained wisdom from the Salmon of Knowledge.",
                titles=["Leader of the Fianna"],
                relationships={"son": "Oisín", "grandson": "Oscar"},
                stories=["Salmon of Knowledge", "Diarmuid and Gráinne"],
                game_role="Main quest giver for Fianna storyline",
            ),
            MythologyCharacter(
                id="char_rhiannon",
                name="Rhiannon",
                native_names={"cy": "Rhiannon"},
                tradition="welsh",
                cycle="mabinogion",
                character_type="deity",
                description="Divine queen associated with horses, falsely accused of killing her son.",
                titles=["Horse Goddess", "Queen of Dyfed"],
                relationships={"husband": "Pwyll", "son": "Pryderi"},
                stories=["Pwyll Prince of Dyfed", "Manawydan Son of Llŷr"],
                game_role="Key NPC in Gwynedd kingdom",
            ),
            MythologyCharacter(
                id="char_taliesin",
                name="Taliesin",
                native_names={"cy": "Taliesin"},
                tradition="welsh",
                cycle="mabinogion",
                character_type="bard",
                description="Legendary bard who gained wisdom from Ceridwen's cauldron.",
                titles=["Chief Bard", "Primary Bard of Britain"],
                relationships={"mother": "Ceridwen (adoptive)"},
                stories=["Tale of Taliesin"],
                game_role="Bard trainer in Welsh lands",
            ),
        ]

        # Apply filters to fallback
        if tradition:
            fallback_characters = [c for c in fallback_characters if c.tradition == tradition]
        if cycle:
            fallback_characters = [c for c in fallback_characters if c.cycle == cycle]
        if character_type:
            fallback_characters = [c for c in fallback_characters if c.character_type == character_type]

        characters = fallback_characters

    return {
        "characters": characters[:limit],
        "total": len(characters),
    }


@router.get("/characters/{character_id}")
async def get_character(character_id: str):
    """Get a specific mythological character."""
    # Simplified lookup
    characters = await get_characters()
    for char in characters["characters"]:
        if char.id == character_id:
            return char

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Character '{character_id}' not found",
    )


@router.get("/locations")
async def get_locations(
    tradition: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
):
    """Get mythological locations."""
    locations = [
        MythologyLocation(
            id="loc_tir_na_nog",
            name="Tír na nÓg",
            native_names={"ga": "Tír na nÓg"},
            tradition="irish",
            description="The Land of Eternal Youth, Otherworldly realm of beauty and immortality.",
            significance="Celtic paradise accessible through sidhe mounds or across the sea.",
            characters=["Niamh", "Oisín", "Manannán mac Lir"],
            game_zone="otherworld",
        ),
        MythologyLocation(
            id="loc_emain_macha",
            name="Emain Macha",
            native_names={"ga": "Eamhain Mhacha"},
            tradition="irish",
            description="Royal seat of the Ulster kings in the Ulster Cycle.",
            significance="Capital of Ulster, home of the Red Branch warriors.",
            characters=["Conchobar mac Nessa", "Cú Chulainn"],
            game_zone="ulster_highlands",
        ),
        MythologyLocation(
            id="loc_annwfn",
            name="Annwfn",
            native_names={"cy": "Annwfn"},
            tradition="welsh",
            description="The Welsh Otherworld, realm of Arawn.",
            significance="Land of the dead and supernatural beings.",
            characters=["Arawn", "Pwyll"],
            game_zone="otherworld",
        ),
        MythologyLocation(
            id="loc_dun_scaith",
            name="Dún Scáith",
            native_names={"ga": "Dún Scáith", "gd": "Dùn Sgàthaich"},
            tradition="scottish",
            description="Fortress of Scáthach on the Isle of Skye.",
            significance="Training ground where Cú Chulainn learned combat.",
            characters=["Scáthach", "Aoife"],
            game_zone="skye_highlands",
        ),
    ]

    if tradition:
        locations = [l for l in locations if l.tradition == tradition]

    return {
        "locations": locations[:limit],
        "total": len(locations),
    }


@router.get("/stories")
async def get_stories(
    tradition: str | None = Query(None),
    cycle: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
):
    """Get mythological stories."""
    stories = [
        MythologyStory(
            id="story_tain",
            title="Táin Bó Cúailnge",
            native_title="Táin Bó Cúailnge",
            tradition="irish",
            cycle="ulster",
            summary="The epic cattle raid of Cooley, where Queen Medb invades Ulster for the brown bull.",
            themes=["War", "Honor", "Fate", "Single combat"],
            main_characters=["Cú Chulainn", "Medb", "Fergus", "Ailill"],
            educational_value="Central text of Irish mythology, teaches Ulster Cycle vocabulary and themes.",
        ),
        MythologyStory(
            id="story_salmon",
            title="The Salmon of Knowledge",
            native_title="An Bradán Feasa",
            tradition="irish",
            cycle="fianna",
            summary="Young Fionn accidentally gains all knowledge when cooking the magical salmon for the poet Finnegas.",
            themes=["Wisdom", "Fate", "Transformation"],
            main_characters=["Fionn mac Cumhaill", "Finnegas"],
            educational_value="Popular introduction to Fenian Cycle, accessible for beginners.",
        ),
        MythologyStory(
            id="story_pwyll",
            title="Pwyll Prince of Dyfed",
            native_title="Pwyll Pendefig Dyfed",
            tradition="welsh",
            cycle="mabinogion",
            summary="Pwyll exchanges places with Arawn, king of the Otherworld, and later wins Rhiannon as his bride.",
            themes=["Otherworld", "Honor", "Love", "Transformation"],
            main_characters=["Pwyll", "Arawn", "Rhiannon"],
            educational_value="First Branch of the Mabinogi, essential Welsh mythology text.",
        ),
        MythologyStory(
            id="story_children_lir",
            title="The Children of Lir",
            native_title="Oidhe Chlainne Lir",
            tradition="irish",
            cycle="tuatha_de_danann",
            summary="Four children are transformed into swans for 900 years by their jealous stepmother.",
            themes=["Transformation", "Jealousy", "Endurance", "Faith"],
            main_characters=["Lir", "Aoife", "Fionnuala", "Aodh", "Conn", "Fiachra"],
            educational_value="One of the Three Sorrows of Irish Storytelling, teaches advanced vocabulary.",
        ),
    ]

    if tradition:
        stories = [s for s in stories if s.tradition == tradition]
    if cycle:
        stories = [s for s in stories if s.cycle == cycle]

    return {
        "stories": stories[:limit],
        "total": len(stories),
    }


@router.get("/cycles")
async def get_mythological_cycles():
    """Get list of mythological cycles."""
    return {
        "cycles": [
            {
                "id": "tuatha_de_danann",
                "name": "Tuatha Dé Danann Cycle",
                "native_name": "Scéalta na Tuatha Dé Danann",
                "tradition": "irish",
                "description": "Stories of the divine race who ruled Ireland before the Milesians.",
                "key_stories": ["Battle of Moytura", "Children of Lir"],
            },
            {
                "id": "ulster",
                "name": "Ulster Cycle",
                "native_name": "An Rúraíocht",
                "tradition": "irish",
                "description": "Heroic tales centered on King Conchobar and the Red Branch warriors.",
                "key_stories": ["Táin Bó Cúailnge", "Deirdre of the Sorrows"],
            },
            {
                "id": "fianna",
                "name": "Fenian Cycle",
                "native_name": "An Fhiannaíocht",
                "tradition": "irish",
                "description": "Adventures of Fionn mac Cumhaill and the Fianna warrior band.",
                "key_stories": ["Salmon of Knowledge", "Diarmuid and Gráinne", "Oisín in Tír na nÓg"],
            },
            {
                "id": "kings",
                "name": "Historical Cycle",
                "native_name": "An Chéitlín Stairiúil",
                "tradition": "irish",
                "description": "Tales of historical and legendary Irish kings.",
                "key_stories": ["Buile Suibhne", "Cath Maige Tuired"],
            },
            {
                "id": "mabinogion",
                "name": "Mabinogion",
                "native_name": "Y Mabinogion",
                "tradition": "welsh",
                "description": "Collection of Welsh mythological tales in four branches.",
                "key_stories": ["Pwyll Prince of Dyfed", "Branwen Daughter of Llŷr", "Manawydan Son of Llŷr", "Math Son of Mathonwy"],
            },
        ],
    }


@router.get("/traditions")
async def get_traditions():
    """Get list of Celtic traditions."""
    return {
        "traditions": [
            {
                "id": "irish",
                "name": "Irish Mythology",
                "native_name": "Miotaseolaíocht na hÉireann",
                "language": "ga",
                "description": "Rich tradition preserved in medieval manuscripts like Lebor Gabála Érenn.",
                "cycles": ["tuatha_de_danann", "ulster", "fianna", "kings"],
            },
            {
                "id": "welsh",
                "name": "Welsh Mythology",
                "native_name": "Mytholeg Gymreig",
                "language": "cy",
                "description": "Traditions preserved in the Mabinogion and other medieval texts.",
                "cycles": ["mabinogion", "arthurian"],
            },
            {
                "id": "scottish",
                "name": "Scottish Mythology",
                "native_name": "Miotas-eòlas na h-Alba",
                "language": "gd",
                "description": "Folklore shared with Irish tradition, plus unique Highland legends.",
                "cycles": ["ulster", "fianna", "folk"],
            },
        ],
    }
