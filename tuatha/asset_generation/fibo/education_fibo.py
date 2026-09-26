"""tuatha/asset_generation/fibo/education_fibo.py — FIBO education prompt templates.

Per the 2026-10-04-fibo-asset-pipeline-v1 saga change (Plan 4 of
openspec/plans/2026-10-01-convergence-saga-v1.md).

The 8 syllabus-conditioned prompts (one per NCCA Leaving Certificate
subject) that the FIBO asset generator uses to produce the celtic-art
window chrome + the 2D sprite atlases for the 8 NCCA subject realms.

Per the Brown Ajah theming (docs/BROWN_AJAH_THEMING.md), each prompt
references the relevant Tuatha Dé deity + the Celtic-adaptation of the
4 game UIs (Hades / Clair Obscur / WoW / BitCraft).

Bilingual (EN + GA) — the GA translation is a 1-1 mirror of the EN
prompt, ready for the GA-medium asset variant (planned in Plan 7).
"""
from __future__ import annotations

from typing import Any


# The canonical 8 NCCA subject prompts. Each entry has the EN/GA bilingual
# text + the design tokens that the FIBO renderer uses.
EDUCATION_FIBO_PROMPTS: dict[str, dict[str, Any]] = {
    "mathematics": {
        "en": {
            "baml_color": "var(--ci-subject-mathematics)",
            "tuatha_de_deity": "The Dagda",
            "tuatha_de_treasure": "The Cauldron of Plenty",
            "game_ui_inspiration": (
                "Clair Obscur Belle Époque (Obsidian/Black Marble/Gold Leaf) "
                "Enduring Learning — Cian fhoglaim"
            ),
            "prompt": (
                "Render a celtic-art window chrome for the Mathematics realm. "
                "Use The Dagda's Cauldron of Plenty as the central UI motif — "
                "spilling golden Sigil runes for each learning outcome. "
                "Style: Clair Obscur Belle Époque obsidian marble + gold leaf."
            ),
        },
        "ga": {
            "baml_color": "var(--ci-subject-mathematics)",
            "tuatha_de_deity": "An Daghda",
            "tuatha_de_treasure": "Coire Brecain",
            "game_ui_inspiration": (
                "Clair Obscur Belle Époque (Oibri/Black Marble/Ór Leaf) "
                "Foghlaim Bhuan — Cian fhoglaim"
            ),
            "prompt": (
                "Déan ciorcal ceoil Ceilteach don réimse Matamaitice. "
                "Úsáid Coire Brecain an Daghda mar mhóitíf láir an UI — "
                "doirteadh rúnai Sigil óir do gach toradh foghlama."
            ),
        },
    },
    "applied_mathematics": {
        "en": {
            "baml_color": "var(--ci-subject-applied-mathematics)",
            "tuatha_de_deity": "Lugh (samildanach)",
            "tuatha_de_treasure": "The Spear of Lugh (never misses)",
            "game_ui_inspiration": (
                "Clair Obscur Belle Époque + BitCraft Recipe Tree (the algorithmic "
                "farming UI)"
            ),
            "prompt": (
                "Render a celtic-art window chrome for the Applied Mathematics realm. "
                "Use Lugh's Spear as the central UI motif — auto-targeting every "
                "recipe / equation. Style: Claire Obscur material library + gold leaf."
            ),
        },
        "ga": {
            "baml_color": "var(--ci-subject-applied-mathematics)",
            "tuatha_de_deity": "Lugh (samildanach)",
            "tuatha_de_treasure": "Sleá Lugh (ní chaillfidh)",
            "game_ui_inspiration": (
                "Clair Obscur Belle Époque + BitCraft Recipe Tree"
            ),
            "prompt": (
                "Déan ciorcal ceoil Ceilteach don réimse Matamaitice Feidhmeach. "
                "Úsáid Sleá Lugh mar mhóitíf láir — spriocadh uathoibríoch gach oideas."
            ),
        },
    },
    "chemistry": {
        "en": {
            "baml_color": "var(--ci-subject-chemistry)",
            "tuatha_de_deity": "Dian Cecht (healing)",
            "tuatha_de_treasure": "The Sword of Nuada (Caladbolg)",
            "game_ui_inspiration": (
                "Hades shadow-first palette + Clair Obscur material library"
            ),
            "prompt": (
                "Render a celtic-art window chrome for the Chemistry realm. "
                "Use Dian Cecht's healing cauldron + Nuada's silver hand as the "
                "central UI motif. Style: Hades shadow-first + material library."
            ),
        },
        "ga": {
            "baml_color": "var(--ci-subject-chemistry)",
            "tuatha_de_deity": "Dian Cécht (leigheas)",
            "tuatha_de_treasure": "Claíomh Nuada (Caladbolg)",
            "game_ui_inspiration": (
                "Hades shadow-first + Clair Obscur material library"
            ),
            "prompt": (
                "Déan ciorcal ceoil Ceilteach don réimse Ceimice. "
                "Úsáid coire leighis Dian Cécht + lámh airgid Nuada mar mhóitíf láir."
            ),
        },
    },
    "geography": {
        "en": {
            "baml_color": "var(--ci-subject-geography)",
            "tuatha_de_deity": "Manannán mac Lir (sea)",
            "tuatha_de_treasure": "The Chariot of the king of Sidrach",
            "game_ui_inspiration": (
                "WoW map zones + hex-based claims + BiTcraft Empire Panel"
            ),
            "prompt": (
                "Render a celtic-art window chrome for the Geography realm. "
                "Use Manannán's chariot + the horse Aonbharr as the central UI motif — "
                "auto-pathing across map zones. Style: WoW map zones + hex claims."
            ),
        },
        "ga": {
            "baml_color": "var(--ci-subject-geography)",
            "tuatha_de_deity": "Manannán mac Lir (muir)",
            "tuatha_de_treasure": "Carbad Rí Shíodraigh",
            "game_ui_inspiration": (
                "WoW map zones + hex-based claims + BiTcraft Empire Panel"
            ),
            "prompt": (
                "Déan ciorcal ceoil Ceilteach don réimse Tíreolaíochta. "
                "Úsáid carbad Manannán + capall Aonbharr mar mhóitíf láir."
            ),
        },
    },
    "history": {
        "en": {
            "baml_color": "var(--ci-subject-history)",
            "tuatha_de_deity": "The Morrígan (war + death)",
            "tuatha_de_treasure": "The Helmet + Breastplate of the king of Clochur",
            "game_ui_inspiration": (
                "Hades chamber progression + Clair Obscur act-and-chapter UI"
            ),
            "prompt": (
                "Render a celtic-art window chrome for the History realm. "
                "Use The Morrígan's helmet + breastplate as the central UI motif — "
                "auto-progressing through chambers. Style: Hades act-and-chapter UI."
            ),
        },
        "ga": {
            "baml_color": "var(--ci-subject-history)",
            "tuatha_de_deity": "An Mhorrígan (cogadh + bás)",
            "tuatha_de_treasure": "Clogad + Luireach Rí Chlochuir",
            "game_ui_inspiration": (
                "Hades chamber progression + Clair Obscur act-and-chapter UI"
            ),
            "prompt": (
                "Déan ciorcal ceoil Ceilteach don réimse Staire. "
                "Úsáid clogad + luireach na Mhorrígan mar mhóitíf láir."
            ),
        },
    },
    "english": {
        "en": {
            "baml_color": "var(--ci-subject-english)",
            "tuatha_de_deity": "Brigid (poetry + smithcraft)",
            "tuatha_de_treasure": "The Sword of Nuada (Caladbolg)",
            "game_ui_inspiration": (
                "Hades boon selection + Clair Obscur skill tree"
            ),
            "prompt": (
                "Render a celtic-art window chrome for the English realm. "
                "Use Brigid's forge as the central UI motif — a boon selection "
                "menu of literary devices. Style: Hades boon selection + skill tree."
            ),
        },
        "ga": {
            "baml_color": "var(--ci-subject-english)",
            "tuatha_de_deity": "Brigid (filíocht + ceardaíocht)",
            "tuatha_de_treasure": "Claíomh Nuada (Caladbolg)",
            "game_ui_inspiration": "Hades boon selection + Clair Obscur skill tree",
            "prompt": (
                "Déan ciorcal ceoil Ceilteach don réimse Béarla. "
                "Úsáid ceardlann Brigid mar mhóitíf láir — roghchlár boon de ghuthanna liteartha."
            ),
        },
    },
    "gaeilge": {
        "en": {
            "baml_color": "var(--ci-subject-gaeilge)",
            "tuatha_de_deity": "Ogma (speech + writing)",
            "tuatha_de_treasure": "The Sword of Nuada (Caladbolg)",
            "game_ui_inspiration": "Hades boon selection + Clair Obscur skill tree",
            "prompt": (
                "Render a celtic-art window chrome for the Gaeilge realm. "
                "Use Ogma's oak-twig as the central UI motif — runes that "
                "auto-translate each learning outcome. Style: Clair Obscur skill tree."
            ),
        },
        "ga": {
            "baml_color": "var(--ci-subject-gaeilge)",
            "tuatha_de_deity": "Ogma (caint + scríbhneoireacht)",
            "tuatha_de_treasure": "Claíomh Nuada (Caladbolg)",
            "game_ui_inspiration": "Hades boon selection + Clair Obscur skill tree",
            "prompt": (
                "Déan ciorcal ceoil Ceilteach don réimse Gaeilge. "
                "Úsáid slat darach Ogma mar mhóitíf láir — rúnai a aistriúchán "
                "uathoibríoch gach toradh foghlama."
            ),
        },
    },
    "computer_science": {
        "en": {
            "baml_color": "var(--ci-subject-computer-science)",
            "tuatha_de_deity": "Lugh (samildanach) + Brigid (smithcraft)",
            "tuatha_de_treasure": "The Sword of Nuada + The Cauldron of Plenty",
            "game_ui_inspiration": (
                "Hades mirror upgrades + Clair Obscur pictos + BiTcraft recipe"
            ),
            "prompt": (
                "Render a celtic-art window chrome for the Computer Science realm. "
                "Use Lugh's Spear + Brigid's forge as the central UI motif — "
                "auto-upgradeable pictos. Style: Hades mirror upgrades + BiTcraft recipe."
            ),
        },
        "ga": {
            "baml_color": "var(--ci-subject-computer-science)",
            "tuatha_de_deity": "Lugh (samildanach) + Brigid (ceardaíocht)",
            "tuatha_de_treasure": "Claíomh Nuada + Coire Brecain",
            "game_ui_inspiration": "Hades mirror upgrades + Clair Obscur pictos + BiTcraft recipe",
            "prompt": (
                "Déan ciorcal ceoil Ceilteach don réimse Ríomheolaíochta. "
                "Úsáid Sleá Lugh + ceardlann Brigid mar mhóitíf láir."
            ),
        },
    },
}


def get_fibo_prompt(subject: str, language: str = "en") -> dict[str, Any]:
    """Return the canonical FIBO prompt template for a subject + language.

    Args:
        subject: One of the 8 NCCA subjects (mathematics / applied_mathematics /
                 chemistry / geography / history / english / gaeilge /
                 computer_science)
        language: "en" | "ga" (default: "en")

    Returns:
        The prompt template dict (with baml_color / tuatha_de_deity /
        tuatha_de_treasure / game_ui_inspiration / prompt keys).

    Raises:
        KeyError: If the subject isn't in the canonical 8 NCCA subjects.
    """
    if subject not in EDUCATION_FIBO_PROMPTS:
        raise KeyError(
            f"Subject {subject!r} not in the canonical 8 NCCA subjects. "
            f"Valid subjects: {sorted(EDUCATION_FIBO_PROMPTS.keys())}"
        )
    return EDUCATION_FIBO_PROMPTS[subject][language]


def list_subjects() -> list[str]:
    """Return the list of canonical 8 NCCA subjects."""
    return sorted(EDUCATION_FIBO_PROMPTS.keys())


__all__ = ["EDUCATION_FIBO_PROMPTS", "get_fibo_prompt", "list_subjects"]
