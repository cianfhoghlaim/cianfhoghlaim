"""
Mythology query tools for Tuath.

Search Celtic mythology content for NPC dialogue and lore generation.
Covers Irish, Welsh, and Scottish traditions.
"""

import lancedb
from pydantic import BaseModel


class MythologyResult(BaseModel):
    """A mythology search result."""

    id: str
    title: str
    content: str
    tradition: str
    cycle: str
    characters: list[str]
    locations: list[str]
    themes: list[str]
    score: float


class MythologySearchResults(BaseModel):
    """Results from mythology search."""

    query: str
    results: list[MythologyResult]
    total: int


class CharacterLore(BaseModel):
    """Lore for a mythological character."""

    name: str
    tradition: str
    cycle: str
    titles: list[str]
    description: str
    relationships: dict[str, str]
    stories: list[str]
    attributes: dict[str, str]
    celtic_names: dict[str, str]


class LocationLore(BaseModel):
    """Lore for a mythological location."""

    name: str
    tradition: str
    description: str
    significance: str
    associated_characters: list[str]
    events: list[str]
    celtic_names: dict[str, str]


# LanceDB connection
_db: lancedb.DBConnection | None = None


def _get_db() -> lancedb.DBConnection:
    """Get LanceDB connection."""
    global _db
    if _db is None:
        _db = lancedb.connect("/Users/cliste/dev/cianfhoghlaim/sruth/tuath/storage/lance")
    return _db


async def search_mythology(
    query: str,
    tradition: str | None = None,
    cycle: str | None = None,
    limit: int = 10,
) -> MythologySearchResults:
    """
    Search Celtic mythology content.

    Args:
        query: Search query text
        tradition: Filter by tradition (irish, welsh, scottish)
        cycle: Filter by mythological cycle
        limit: Maximum results

    Returns:
        MythologySearchResults with matching content
    """
    try:
        db = _get_db()

        if "celtic_mythology" not in db.table_names():
            return MythologySearchResults(query=query, results=[], total=0)

        table = db.open_table("celtic_mythology")

        # Build filter
        filters = []
        if tradition:
            filters.append(f"tradition = '{tradition}'")
        if cycle:
            filters.append(f"cycle = '{cycle}'")

        filter_str = " AND ".join(filters) if filters else None

        # Vector search
        results = (
            table.search(query)
            .where(filter_str)
            .limit(limit)
            .to_pandas()
        )

        mythology_results = []
        for _, row in results.iterrows():
            mythology_results.append(
                MythologyResult(
                    id=row.get("id", ""),
                    title=row.get("title", ""),
                    content=row.get("content", ""),
                    tradition=row.get("tradition", ""),
                    cycle=row.get("cycle", ""),
                    characters=row.get("characters", []),
                    locations=row.get("locations", []),
                    themes=row.get("themes", []),
                    score=float(row.get("_distance", 0)),
                )
            )

        return MythologySearchResults(
            query=query,
            results=mythology_results,
            total=len(mythology_results),
        )

    except Exception:
        return MythologySearchResults(query=query, results=[], total=0)


async def get_character_lore(character_name: str) -> list[CharacterLore]:
    """
    Get detailed lore for a mythological character.

    Args:
        character_name: Name of the character

    Returns:
        List of CharacterLore matching the name
    """
    # First check static character database
    character_lower = character_name.lower()
    matches = []

    for tradition, characters in CELTIC_CHARACTERS.items():
        for char in characters:
            if character_lower in char["name"].lower() or any(
                character_lower in alias.lower() for alias in char.get("aliases", [])
            ):
                matches.append(
                    CharacterLore(
                        name=char["name"],
                        tradition=tradition,
                        cycle=char.get("cycle", ""),
                        titles=char.get("titles", []),
                        description=char.get("description", ""),
                        relationships=char.get("relationships", {}),
                        stories=char.get("stories", []),
                        attributes=char.get("attributes", {}),
                        celtic_names=char.get("celtic_names", {}),
                    )
                )

    # Also search vector database
    try:
        db = _get_db()
        if "character_lore" in db.table_names():
            table = db.open_table("character_lore")
            results = table.search(character_name).limit(5).to_pandas()

            for _, row in results.iterrows():
                matches.append(
                    CharacterLore(
                        name=row.get("name", ""),
                        tradition=row.get("tradition", ""),
                        cycle=row.get("cycle", ""),
                        titles=row.get("titles", []),
                        description=row.get("description", ""),
                        relationships=row.get("relationships", {}),
                        stories=row.get("stories", []),
                        attributes=row.get("attributes", {}),
                        celtic_names=row.get("celtic_names", {}),
                    )
                )
    except Exception:
        pass

    return matches


async def get_location_lore(
    location_name: str,
    tradition: str | None = None,
) -> list[LocationLore]:
    """
    Get lore for a mythological location.

    Args:
        location_name: Name of the location
        tradition: Filter by tradition

    Returns:
        List of LocationLore matching the location
    """
    location_lower = location_name.lower()
    matches = []

    for trad, locations in CELTIC_LOCATIONS.items():
        if tradition and trad != tradition:
            continue

        for loc in locations:
            if location_lower in loc["name"].lower() or any(
                location_lower in alias.lower() for alias in loc.get("aliases", [])
            ):
                matches.append(
                    LocationLore(
                        name=loc["name"],
                        tradition=trad,
                        description=loc.get("description", ""),
                        significance=loc.get("significance", ""),
                        associated_characters=loc.get("characters", []),
                        events=loc.get("events", []),
                        celtic_names=loc.get("celtic_names", {}),
                    )
                )

    return matches


# Celtic mythological characters database
CELTIC_CHARACTERS = {
    "irish": [
        {
            "name": "Lugh",
            "cycle": "tuatha_de_danann",
            "aliases": ["Lugh Lámhfhada", "Lugh of the Long Arm"],
            "titles": ["God of Skills", "Samildánach (Many-Skilled)"],
            "description": "Master of all arts, leader of the Tuatha Dé Danann in battle against the Fomorians.",
            "relationships": {
                "father": "Cian",
                "mother": "Ethniu",
                "grandfather": "Balor (Fomorian king)",
            },
            "stories": ["Battle of Moytura", "Death of Balor"],
            "attributes": {
                "weapon": "Spear (Gáe Assail)",
                "skill": "All crafts and arts",
            },
            "celtic_names": {"ga": "Lugh Lámhfhada"},
        },
        {
            "name": "Dagda",
            "cycle": "tuatha_de_danann",
            "aliases": ["The Dagda", "Eochaid Ollathair"],
            "titles": ["The Good God", "Father of All"],
            "description": "Chief of the Tuatha Dé Danann, god of fertility, agriculture, and wisdom.",
            "relationships": {
                "daughter": "Brigid",
                "son": "Aengus",
            },
            "stories": ["Battle of Moytura", "Aengus and Brú na Bóinne"],
            "attributes": {
                "weapon": "Club (one end kills, one revives)",
                "treasure": "Cauldron of Plenty (Undry)",
            },
            "celtic_names": {"ga": "An Dagda"},
        },
        {
            "name": "Cú Chulainn",
            "cycle": "ulster",
            "aliases": ["Sétanta", "Hound of Culann"],
            "titles": ["Champion of Ulster", "The Warped One"],
            "description": "Greatest warrior of Ulster, known for his battle rage (ríastrad) and tragic fate.",
            "relationships": {
                "father": "Lugh (divine)",
                "mother": "Deichtine",
                "wife": "Emer",
                "lover": "Fand",
            },
            "stories": ["Táin Bó Cúailnge", "Death of Cú Chulainn"],
            "attributes": {
                "weapon": "Gáe Bolga",
                "transformation": "Ríastrad (battle frenzy)",
            },
            "celtic_names": {"ga": "Cú Chulainn"},
        },
        {
            "name": "Fionn mac Cumhaill",
            "cycle": "fianna",
            "aliases": ["Finn McCool", "Demne"],
            "titles": ["Leader of the Fianna"],
            "description": "Legendary hunter-warrior who gained wisdom from the Salmon of Knowledge.",
            "relationships": {
                "son": "Oisín",
                "grandson": "Oscar",
                "rival": "Goll mac Morna",
            },
            "stories": ["Salmon of Knowledge", "Diarmuid and Gráinne"],
            "attributes": {
                "wisdom": "Thumb of Knowledge",
                "treasure": "Crane-skin bag",
            },
            "celtic_names": {"ga": "Fionn mac Cumhaill"},
        },
        {
            "name": "Brigid",
            "cycle": "tuatha_de_danann",
            "aliases": ["Bríd", "Saint Brigid"],
            "titles": ["Goddess of Poetry", "Goddess of Healing", "Goddess of Smithcraft"],
            "description": "Triple goddess of poetry, healing, and smithcraft. Later syncreted with Christian saint.",
            "relationships": {
                "father": "Dagda",
                "son": "Ruadán",
            },
            "stories": ["Battle of Moytura", "Origin of Keening"],
            "attributes": {
                "domain": "Poetry, Healing, Smithcraft",
                "festival": "Imbolc",
            },
            "celtic_names": {"ga": "Bríd", "gd": "Brìghde"},
        },
    ],
    "welsh": [
        {
            "name": "Pwyll",
            "cycle": "mabinogion",
            "aliases": ["Pwyll Pen Annwfn"],
            "titles": ["Lord of Dyfed", "Head of Annwfn"],
            "description": "Lord of Dyfed who exchanged places with the king of the Otherworld.",
            "relationships": {
                "wife": "Rhiannon",
                "son": "Pryderi",
            },
            "stories": ["Pwyll Prince of Dyfed"],
            "attributes": {
                "realm": "Dyfed, later Annwfn",
            },
            "celtic_names": {"cy": "Pwyll"},
        },
        {
            "name": "Rhiannon",
            "cycle": "mabinogion",
            "aliases": ["Rigantona"],
            "titles": ["Horse Goddess", "Queen of Dyfed"],
            "description": "Divine queen associated with horses, falsely accused of killing her son.",
            "relationships": {
                "husband": "Pwyll, later Manawydan",
                "son": "Pryderi",
            },
            "stories": ["Pwyll Prince of Dyfed", "Manawydan Son of Llŷr"],
            "attributes": {
                "animal": "Horse",
                "birds": "Birds of Rhiannon",
            },
            "celtic_names": {"cy": "Rhiannon"},
        },
        {
            "name": "Taliesin",
            "cycle": "mabinogion",
            "aliases": ["Gwion Bach"],
            "titles": ["Chief Bard", "Primary Bard of Britain"],
            "description": "Legendary bard who gained wisdom from Ceridwen's cauldron.",
            "relationships": {
                "mother": "Ceridwen (adoptive)",
            },
            "stories": ["Tale of Taliesin"],
            "attributes": {
                "gift": "Poetic inspiration (awen)",
            },
            "celtic_names": {"cy": "Taliesin"},
        },
    ],
    "scottish": [
        {
            "name": "Scáthach",
            "cycle": "ulster",
            "aliases": ["The Shadowy One"],
            "titles": ["Warrior Woman of Alba"],
            "description": "Legendary warrior who trained Cú Chulainn in the arts of war on the Isle of Skye.",
            "relationships": {
                "student": "Cú Chulainn",
                "rival": "Aoife",
            },
            "stories": ["Training of Cú Chulainn"],
            "attributes": {
                "location": "Dún Scáith, Isle of Skye",
                "skill": "Martial arts",
            },
            "celtic_names": {"ga": "Scáthach", "gd": "Sgàthach"},
        },
    ],
}

# Celtic mythological locations
CELTIC_LOCATIONS = {
    "irish": [
        {
            "name": "Tír na nÓg",
            "aliases": ["Land of Youth", "Land of Eternal Youth"],
            "description": "Otherworldly realm of eternal youth and beauty.",
            "significance": "The Celtic paradise, accessible through sidhe mounds or across the sea.",
            "characters": ["Niamh", "Oisín", "Manannán mac Lir"],
            "events": ["Oisín's journey"],
            "celtic_names": {"ga": "Tír na nÓg"},
        },
        {
            "name": "Emain Macha",
            "aliases": ["Navan Fort"],
            "description": "Royal seat of the Ulster kings in the Ulster Cycle.",
            "significance": "Capital of Ulster, site of the Red Branch warriors.",
            "characters": ["Conchobar mac Nessa", "Cú Chulainn"],
            "events": ["Táin Bó Cúailnge"],
            "celtic_names": {"ga": "Eamhain Mhacha"},
        },
        {
            "name": "Brú na Bóinne",
            "aliases": ["Newgrange", "Síd in Broga"],
            "description": "Great passage tomb, home of the Dagda and later Aengus.",
            "significance": "Sacred mound, gateway to the Otherworld.",
            "characters": ["Dagda", "Aengus Óg"],
            "events": ["Aengus winning Brú na Bóinne"],
            "celtic_names": {"ga": "Brú na Bóinne"},
        },
    ],
    "welsh": [
        {
            "name": "Annwfn",
            "aliases": ["The Otherworld", "The Unworld"],
            "description": "Welsh Otherworld ruled by Arawn.",
            "significance": "Realm of the dead and supernatural beings.",
            "characters": ["Arawn", "Pwyll"],
            "events": ["Pwyll's year in Annwfn"],
            "celtic_names": {"cy": "Annwfn"},
        },
        {
            "name": "Dyfed",
            "aliases": ["Demetia"],
            "description": "Kingdom in southwest Wales, realm of Pwyll.",
            "significance": "Setting for the First and Third Branches of the Mabinogi.",
            "characters": ["Pwyll", "Rhiannon", "Pryderi"],
            "events": ["Birth of Pryderi"],
            "celtic_names": {"cy": "Dyfed"},
        },
    ],
    "scottish": [
        {
            "name": "Dún Scáith",
            "aliases": ["Fortress of Shadows", "Castle of Skye"],
            "description": "Fortress of Scáthach on the Isle of Skye.",
            "significance": "Training ground for warriors, where Cú Chulainn learned combat.",
            "characters": ["Scáthach", "Cú Chulainn", "Aoife"],
            "events": ["Training of Cú Chulainn"],
            "celtic_names": {"gd": "Dùn Sgàthaich"},
        },
    ],
}
