"""
Translation tools for Tuath.

Translate between Celtic languages (Irish, Scottish Gaelic, Welsh)
and English. Uses BGE-M3 multilingual embeddings for similarity search.
"""

from pydantic import BaseModel

import lancedb


class TranslationResult(BaseModel):
    """A translation result."""

    source_text: str
    source_language: str
    target_text: str
    target_language: str
    confidence: float
    alternatives: list[str]
    notes: str | None = None


class VocabularyEntry(BaseModel):
    """A vocabulary entry with translations."""

    word: str
    language: str
    translations: dict[str, list[str]]
    pronunciation: str | None = None
    part_of_speech: str | None = None
    examples: list[dict[str, str]]
    notes: str | None = None
    related_words: list[str]


# Language codes
CELTIC_LANGUAGES = {
    "ga": "Irish",
    "gd": "Scottish Gaelic",
    "cy": "Welsh",
    "gv": "Manx",
    "kw": "Cornish",
    "br": "Breton",
    "en": "English",
}

# LanceDB connection
_db: lancedb.DBConnection | None = None


def _get_db() -> lancedb.DBConnection:
    """Get LanceDB connection."""
    global _db
    if _db is None:
        _db = lancedb.connect("/Users/cliste/dev/cianfhoghlaim/sruth/tuath/storage/lance")
    return _db


async def translate_text(
    text: str,
    source_language: str,
    target_language: str,
) -> TranslationResult:
    """
    Translate text between Celtic languages and English.

    Args:
        text: Text to translate
        source_language: Source language code (ga, gd, cy, en)
        target_language: Target language code

    Returns:
        TranslationResult with translation and alternatives
    """
    # Check for common phrases in static dictionary first
    phrase_key = f"{source_language}:{text.lower().strip()}"
    if phrase_key in COMMON_PHRASES:
        translation = COMMON_PHRASES[phrase_key].get(target_language, "")
        if translation:
            return TranslationResult(
                source_text=text,
                source_language=source_language,
                target_text=translation,
                target_language=target_language,
                confidence=1.0,
                alternatives=[],
                notes="From common phrases dictionary",
            )

    # Try vector similarity search
    try:
        db = _get_db()

        if "translations" in db.table_names():
            table = db.open_table("translations")

            # Search for similar translations
            results = (
                table.search(text)
                .where(f"source_lang = '{source_language}' AND target_lang = '{target_language}'")
                .limit(5)
                .to_pandas()
            )

            if len(results) > 0:
                best = results.iloc[0]
                alternatives = [row["target_text"] for _, row in results.iloc[1:].iterrows()]

                return TranslationResult(
                    source_text=text,
                    source_language=source_language,
                    target_text=best["target_text"],
                    target_language=target_language,
                    confidence=float(1 - best.get("_distance", 0.5)),
                    alternatives=alternatives,
                )

    except Exception:
        pass

    # Fallback: return placeholder
    return TranslationResult(
        source_text=text,
        source_language=source_language,
        target_text=f"[Translation to {CELTIC_LANGUAGES.get(target_language, target_language)} not available]",
        target_language=target_language,
        confidence=0.0,
        alternatives=[],
        notes="No translation found in database",
    )


async def get_vocabulary(
    word: str,
    source_language: str = "en",
    target_language: str = "ga",
) -> VocabularyEntry:
    """
    Get vocabulary entry with translations and examples.

    Args:
        word: Word to look up
        source_language: Source language code
        target_language: Target language code

    Returns:
        VocabularyEntry with translations and examples
    """
    word_lower = word.lower().strip()

    # Check static vocabulary
    if word_lower in CELTIC_VOCABULARY:
        entry = CELTIC_VOCABULARY[word_lower]
        return VocabularyEntry(
            word=word,
            language=source_language,
            translations=entry.get("translations", {}),
            pronunciation=entry.get("pronunciation", {}).get(target_language),
            part_of_speech=entry.get("pos"),
            examples=entry.get("examples", []),
            notes=entry.get("notes"),
            related_words=entry.get("related", []),
        )

    # Try vector search
    try:
        db = _get_db()

        if "vocabulary" in db.table_names():
            table = db.open_table("vocabulary")

            results = (
                table.search(word).where(f"source_lang = '{source_language}'").limit(1).to_pandas()
            )

            if len(results) > 0:
                row = results.iloc[0]
                return VocabularyEntry(
                    word=word,
                    language=source_language,
                    translations=row.get("translations", {}),
                    pronunciation=row.get("pronunciation"),
                    part_of_speech=row.get("pos"),
                    examples=row.get("examples", []),
                    notes=row.get("notes"),
                    related_words=row.get("related", []),
                )

    except Exception:
        pass

    # Return empty entry
    return VocabularyEntry(
        word=word,
        language=source_language,
        translations={},
        examples=[],
        related_words=[],
        notes="Word not found in vocabulary database",
    )


# Common phrases dictionary
COMMON_PHRASES = {
    # Greetings
    "en:hello": {"ga": "Dia duit", "gd": "Halò", "cy": "Shwmae"},
    "en:goodbye": {"ga": "Slán", "gd": "Mar sin leat", "cy": "Hwyl fawr"},
    "en:thank you": {"ga": "Go raibh maith agat", "gd": "Tapadh leat", "cy": "Diolch"},
    "en:please": {"ga": "Le do thoil", "gd": "Ma 's e do thoil e", "cy": "Os gwelwch yn dda"},
    "en:yes": {"ga": "Tá", "gd": "Tha", "cy": "Ie"},
    "en:no": {"ga": "Níl", "gd": "Chan eil", "cy": "Na"},
    "en:how are you": {"ga": "Conas atá tú?", "gd": "Ciamar a tha thu?", "cy": "Sut wyt ti?"},
    "en:i am well": {"ga": "Tá mé go maith", "gd": "Tha mi gu math", "cy": "Rwy'n iawn"},
    "en:what is your name": {
        "ga": "Cad is ainm duit?",
        "gd": "Dè an t-ainm a th' ort?",
        "cy": "Beth ydy dy enw di?",
    },
    "en:my name is": {"ga": "Is mise", "gd": "Is mise", "cy": "Fy enw i yw"},
    "en:welcome": {"ga": "Fáilte", "gd": "Fàilte", "cy": "Croeso"},
    "en:good morning": {"ga": "Maidin mhaith", "gd": "Madainn mhath", "cy": "Bore da"},
    "en:good night": {"ga": "Oíche mhaith", "gd": "Oidhche mhath", "cy": "Nos da"},
    "en:good luck": {"ga": "Go n-éirí an t-ádh leat", "gd": "Gun soirbhich leat", "cy": "Pob lwc"},
    # Irish to others
    "ga:dia duit": {"en": "Hello", "gd": "Halò", "cy": "Shwmae"},
    "ga:slán": {"en": "Goodbye", "gd": "Mar sin leat", "cy": "Hwyl fawr"},
    "ga:go raibh maith agat": {"en": "Thank you", "gd": "Tapadh leat", "cy": "Diolch"},
    # Scottish Gaelic to others
    "gd:halò": {"en": "Hello", "ga": "Dia duit", "cy": "Shwmae"},
    "gd:tapadh leat": {"en": "Thank you", "ga": "Go raibh maith agat", "cy": "Diolch"},
    # Welsh to others
    "cy:shwmae": {"en": "Hello", "ga": "Dia duit", "gd": "Halò"},
    "cy:diolch": {"en": "Thank you", "ga": "Go raibh maith agat", "gd": "Tapadh leat"},
}

# Core vocabulary with translations
CELTIC_VOCABULARY = {
    "water": {
        "pos": "noun",
        "translations": {
            "ga": ["uisce"],
            "gd": ["uisge"],
            "cy": ["dŵr"],
        },
        "pronunciation": {"ga": "ISH-keh", "gd": "OOSH-kyeh", "cy": "doo-r"},
        "examples": [
            {"en": "The water is cold", "ga": "Tá an t-uisce fuar", "cy": "Mae'r dŵr yn oer"},
        ],
        "related": ["river", "sea", "lake"],
    },
    "fire": {
        "pos": "noun",
        "translations": {
            "ga": ["tine"],
            "gd": ["teine"],
            "cy": ["tân"],
        },
        "pronunciation": {"ga": "CHIN-eh", "gd": "CHEN-yeh", "cy": "tahn"},
        "examples": [
            {"en": "Light the fire", "ga": "Las an tine", "cy": "Cynnau'r tân"},
        ],
        "related": ["light", "flame", "hearth"],
    },
    "earth": {
        "pos": "noun",
        "translations": {
            "ga": ["talamh", "cré"],
            "gd": ["talamh"],
            "cy": ["daear", "pridd"],
        },
        "examples": [],
        "related": ["land", "ground", "soil"],
    },
    "sky": {
        "pos": "noun",
        "translations": {
            "ga": ["spéir"],
            "gd": ["speur"],
            "cy": ["awyr"],
        },
        "examples": [],
        "related": ["heaven", "air", "cloud"],
    },
    "tree": {
        "pos": "noun",
        "translations": {
            "ga": ["crann"],
            "gd": ["craobh"],
            "cy": ["coeden"],
        },
        "examples": [
            {"en": "The oak tree", "ga": "An crann darach", "cy": "Y dderwen"},
        ],
        "related": ["oak", "forest", "wood"],
    },
    "king": {
        "pos": "noun",
        "translations": {
            "ga": ["rí"],
            "gd": ["rìgh"],
            "cy": ["brenin"],
        },
        "examples": [],
        "related": ["queen", "crown", "kingdom"],
    },
    "warrior": {
        "pos": "noun",
        "translations": {
            "ga": ["laoch", "gaiscíoch"],
            "gd": ["laoch", "gaisgeach"],
            "cy": ["rhyfelwr"],
        },
        "examples": [],
        "related": ["hero", "sword", "battle"],
    },
    "song": {
        "pos": "noun",
        "translations": {
            "ga": ["amhrán"],
            "gd": ["òran"],
            "cy": ["cân"],
        },
        "examples": [],
        "related": ["music", "poetry", "bard"],
    },
    "love": {
        "pos": "noun",
        "translations": {
            "ga": ["grá"],
            "gd": ["gràdh"],
            "cy": ["cariad"],
        },
        "examples": [
            {"en": "I love you", "ga": "Tá grá agam duit", "cy": "Rwy'n dy garu di"},
        ],
        "related": ["heart", "beloved"],
    },
    "friend": {
        "pos": "noun",
        "translations": {
            "ga": ["cara"],
            "gd": ["caraid"],
            "cy": ["ffrind", "cyfaill"],
        },
        "examples": [],
        "related": ["companion", "ally"],
    },
}
