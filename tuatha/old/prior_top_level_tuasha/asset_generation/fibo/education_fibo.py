"""FIBO education prompt templates — the 8 syllabus-conditioned prompts.

Per `openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/tasks.md`
T7.13-T7.18, the FIBO asset generator uses 8 subject-specific prompt
templates to generate the celtic-art window chrome + the 2D sprite
atlases for the 8 NCCA subject realms.

Per the Brown Ajah theming (docs/BROWN_AJAH_THEMING.md), each prompt
references the relevant Tuatha Dé deity + the Celtic-adaptation of the
4 game UIs (Hades / Clair Obscur / WoW / BitCraft).
"""

from __future__ import annotations

from typing import Any


# The 8 subject-specific FIBO prompt templates
EDUCATION_FIBO_PROMPTS: dict[str, dict[str, Any]] = {
    "mathematics": {
        "baml_color": "var(--ci-subject-mathematics)",
        "tuatha_de_deity": "The Dagda",
        "tuatha_de_treasure": "The Cauldron of Plenty",
        "game_ui_inspiration": "Clair Obscur Belle Époque (Obsidian/Black Marble/Gold Leaf) + Khan Academy Mastery Levels",
        "kevin_oconnor_quote": "Enduring Learning — Cian fhoglaim",
        "prompt": (
            "Render a celtic-art window chrome for the Mathematics realm of the "
            "Cianfhoghlaim OS. Use the Belle Époque material library (parchment + "
            "slate + ink-wash + gold-leaf + insular knotwork) with the dagda-cauldron "
            "of plenty motif at the centre. The 8 NCCA Learning Outcomes for Higher "
            "Level Mathematics are arranged in a circular pattern. Use the Dagda's "
            "cauldron-of-plenty for the breadcrumb indicator. Include the 'Aes Sedai "
            "— servants of all' tagline in Cinzel display font."
        ),
    },
    "applied_mathematics": {
        "baml_color": "var(--ci-subject-applied-mathematics)",
        "tuatha_de_deity": "Lugh (samildanach)",
        "tuatha_de_treasure": "The Spear of Lugh (never misses)",
        "game_ui_inspiration": "Clair Obscur Belle Époque + BitCraft Recipe Tree (the algorithm-design-pattern visualisation)",
        "prompt": (
            "Render a celtic-art window chrome for the Applied Mathematics realm. "
            "Use the Clair Obscur Belle Époque material library with the spear-of-Lugh "
            "motif. The 4 Applied Mathematics modules (Mechanics + Statistics) are "
            "arranged in a hierarchical tree (per the BitCraft Recipe Tree). Include "
            "the 'Aes Sedai — servants of all' tagline."
        ),
    },
    "chemistry": {
        "baml_color": "var(--ci-subject-chemistry)",
        "tuatha_de_deity": "Dian Cecht (healing)",
        "tuatha_de_treasure": "The Sword of Nuada (Caladbolg)",
        "game_ui_inspiration": "Hades shadow-first palette + Clair Obscur material library (bronze + verdigris + iron)",
        "prompt": (
            "Render a celtic-art window chrome for the Chemistry realm. Use the "
            "Hades shadow-first palette (deep black + acid green for reactions + "
            "bronze for transition metals) with the Dian Cecht physician motif. "
            "The 5 NCCA Chemistry topics (Atomic Structure + Bonding + Stoichiometry "
            "+ Organic + Rates) are arranged as a forge pattern."
        ),
    },
    "geography": {
        "baml_color": "var(--ci-subject-geography)",
        "tuatha_de_deity": "Manannán mac Lir (sea)",
        "tuatha_de_treasure": "The Chariot of the king of Sidrach",
        "game_ui_inspiration": "WoW map zones + hex-based claims + BiTcraft Empire Panel",
        "prompt": (
            "Render a celtic-art window chrome for the Geography realm. Use the "
            "WoW map zones layout (hex-based claims with decay indicators). The 6 "
            "British Isles subnations are the 6 zones. The 4 Irish provinces (Connacht "
            "+ Leinster + Munster + Ulster) are the home base. Manannán mac Lir's "
            "sea motif is the central compass rose. Include the Esker Riada divider "
            "(Dublin Bay to Galway Bay) as the EN↔GA toggle visual."
        ),
    },
    "history": {
        "baml_color": "var(--ci-subject-history)",
        "tuatha_de_deity": "The Morrígan (war + death)",
        "tuatha_de_treasure": "The Helmet + Breastplate of the king of Clochur",
        "game_ui_inspiration": "WoW raid frames + grid-based unit frames",
        "prompt": (
            "Render a celtic-art window chrome for the History realm. Use the "
            "WoW raid-frames grid layout for the historical figures (the 30+ "
            "Chief Examiner-named figures). The Morrígan's war-mask is the "
            "primary icon. The 4 chronological periods (Early Modern + Modern "
            "+ Contemporary + Today) are the 4 columns."
        ),
    },
    "english": {
        "baml_color": "var(--ci-subject-england)",  # also maps to english subject
        "tuatha_de_deity": "Brigid (poetry + healing)",
        "tuatha_de_treasure": "The Whelp of the king of Ioruaidh",
        "game_ui_inspiration": "Clair Obscur brushstroke textures + skill tree",
        "prompt": (
            "Render a celtic-art window chrome for the English realm. Use the "
            "Clair Obscur brushstroke textures with the Brigid poetry-healing motif. "
            "The 7 NCCA English texts (single text + comparative + studied poets) "
            "are arranged as a poetry line."
        ),
    },
    "gaeilge": {
        "baml_color": "var(--ci-subject-gaeilge)",
        "tuatha_de_deity": "Ogma (eloquence + learning, inventor of Ogham)",
        "tuatha_de_treasure": "The Cooking Spit of the woman of Innis Cera",
        "game_ui_inspiration": "Insular Art (Book of Kells knotwork) + Uncial/Insular script",
        "prompt": (
            "Render a celtic-art window chrome for the Gaeilge realm. Use the "
            "Insular Art (Book of Kells knotwork) + Uncial/Insular script. Ogma's "
            "Ogham script is the central pillar. The 5 NCCA Gaeilge LOs (An Léann "
            "Teanga + An Chultúr + etc.) are arranged as the 5 vertical strokes of "
            "an Ogham inscription. The Claddagh District is the home base (the "
            "historic Gaeltacht district in Galway city)."
        ),
    },
    "computer_science": {
        "baml_color": "var(--ci-subject-computer_science)",
        "tuatha_de_deity": "— (modern subject, no Tuatha Dé mapping)",
        "tuatha_de_treasure": "—",
        "game_ui_inspiration": "BitCraft Recipe Tree + Clair Obscur skill tree",
        "prompt": (
            "Render a celtic-art window chrome for the Computer Science realm. "
            "Use the BitCraft Recipe Tree + Clair Obscur skill tree. The 4 NCCA "
            "Computer Science topics (Algorithms + Data + Systems + Networks) are "
            "arranged as the 4 branches. The brown-ajah russet-brown knotwork "
            "is the primary colour (per the Brown Ajah theming)."
        ),
    },
}


def get_fibo_prompt(subject: str, language: str = "en") -> dict[str, Any]:
    """Return the FIBO prompt template for the given subject.

    Args:
        subject: One of the 8 NCCA subject slugs
        language: 'en' or 'ga' (the bilingual mode)

    Returns:
        Dict with 'baml_color', 'tuatha_de_deity', 'tuatha_de_treasure',
        'game_ui_inspiration', 'prompt', and 'language'.
    """
    template = EDUCATION_FIBO_PROMPTS.get(subject)
    if template is None:
        raise ValueError(f"Unknown subject: {subject}")
    return {**template, "language": language}


def list_subjects() -> list[str]:
    """List the 8 NCCA subject slugs that have FIBO prompt templates."""
    return list(EDUCATION_FIBO_PROMPTS.keys())


__all__ = [
    "EDUCATION_FIBO_PROMPTS",
    "get_fibo_prompt",
    "list_subjects",
]