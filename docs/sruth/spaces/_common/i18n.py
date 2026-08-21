"""
spaces/_common/i18n.py
Bilingual EN/GA toggle (plus 5 other Celtic languages as placeholders).

Per the hackathon plan, the build primary is EN + Gaeilge (the Irish
language). The 5 other Celtic nations (Manx, Scottish, Welsh, Cornish,
Breton) are i18n placeholders - the strings exist but are TODO. This
mirrors the croilar/packages/i18n/ pattern (typed dict, no runtime
fuzzy matching, no missing-key crashes).

The toggle is a Gradio component (Radio) whose value updates a global
`current_lang` module variable, then every `translate()` call picks it
up. This is the simplest approach for Gradio Spaces - no React Context,
no signal state.
"""

from __future__ import annotations

from typing import Final


# Supported languages
LANGS: Final[tuple[str, ...]] = ("en", "ga", "gd", "cy", "gv", "kw", "br")
LANG_NAMES: Final[dict[str, str]] = {
    "en": "English",
    "ga": "Gaeilge",
    "gd": "Gaidhlig (TODO)",
    "cy": "Cymraeg (TODO)",
    "gv": "Gaelg (TODO)",
    "kw": "Kernewek (TODO)",
    "br": "Brezhoneg (TODO)",
}

# Module-level current language (mutated by set_lang)
_current_lang: str = "en"


# Typed i18n strings. Keep keys in the "section.subkey" namespace.
I18N_STRINGS: dict[str, dict[str, str]] = {
    "app.title": {
        "en": "Cianfhoghlaim",
        "ga": "Cianfhoghlaim",
    },
    "app.subtitle": {
        "en": "4 Spaces. 5 Elements. 1 typed pipeline.",
        "ga": "4 Spás. 5 Duil. 1 piblíne chlóscríofa.",
    },
    "common.submit": {
        "en": "Submit",
        "ga": "Seol",
    },
    "common.loading": {
        "en": "Loading...",
        "ga": "A lódáil...",
    },
    "common.error": {
        "en": "An error occurred. Please try again.",
        "ga": "Tharla earráid. Bain triail eile as.",
    },
    "common.bilingual_toggle": {
        "en": "Gaeilge",
        "ga": "English",
    },
    "space1.title": {
        "en": "An Scrudu - Past Paper Heatmap",
        "ga": "An Scrudu - Léarscáil Teasa an Scrúdaithe",
    },
    "space1.subtitle": {
        "en": "BAML extracts marking schemes from Irish Leaving Cert past papers.",
        "ga": "Baintear scéimeanna marcála as scrúduithe cáilitheacha na hÉireann.",
    },
    "space1.upload_label": {
        "en": "Upload a past paper PDF (or pick from the corpus).",
        "ga": "Uaslódáil PDF scrúdaithe (nó roghnaigh ón gcorpas).",
    },
    "space1.extract_button": {
        "en": "Extract Marking Scheme",
        "ga": "Bain an Scéim Mharcála",
    },
    "space1.heatmap_caption": {
        "en": "Topic heatmap: frequency of marking points by topic & year.",
        "ga": "Léarscáil teasa: minicíocht bpointí marcála de réir ábhair & bliana.",
    },
    "space2.title": {
        "en": "Meaisín Cliste - Celtic AI Tools",
        "ga": "Meaisín Cliste - Uirlisí AI Ceilteacha",
    },
    "space2.focloir_tab": {
        "en": "Foclóir na Sé Náisiún (Aer)",
        "ga": "Foclóir na Sé Náisiún (Aer)",
    },
    "space2.scoil_tab": {
        "en": "Scoil ar an Léarscáil (Uisce)",
        "ga": "Scoil ar an Léarscáil (Uisce)",
    },
    "space2.curaclam_tab": {
        "en": "Curaclam Trasteorann (Aer)",
        "ga": "Curaclam Trasteorann (Aer)",
    },
    "space3.title": {
        "en": "Cianfhoghlaim - Tuatha RPG",
        "ga": "Cianfhoghlaim - RPG Tuatha",
    },
    "space3.subtitle": {
        "en": "Hades-style dialogue with 6 Celtic NPCs on a navigable British Isles map.",
        "ga": "Caint ar nós Hades le 6 NPCs Ceilteacha ar léarscáil nasctha na nOileán Briotanach.",
    },
    "space3.choose_npc": {
        "en": "Choose a champion to speak with:",
        "ga": "Roghnaigh laoch le caint leis:",
    },
    "space3.diegetic_zone": {
        "en": "You stand in {zone}. The wind carries salt and heather.",
        "ga": "Tá tú i {zone}. Iompraíonn an ghaoth salann agus fraoch.",
    },
    "space4.title": {
        "en": "Anam: Tuatha na nGaelscoil",
        "ga": "Anam: Tuatha na nGaelscoil",
    },
    "space4.subtitle": {
        "en": "5 elements, 7 features, 1 soulbound wallet.",
        "ga": "5 duil, 7 ngné, 1 sparán anam-bhainte.",
    },
    "space4.elem_talamh": {
        "en": "Talamh - Earth (Curriculum Map)",
        "ga": "Talamh - Talamh (Léarscáil Curaclaim)",
    },
    "space4.elem_uisce": {
        "en": "Uisce - Water (Chem Visual)",
        "ga": "Uisce - Uisce (Léirshamhlú Ceimice)",
    },
    "space4.elem_tine": {
        "en": "Tine - Fire (OCR Gaelscríbhneoir)",
        "ga": "Tine - Tine (OCR Gaelscríbhneoir)",
    },
    "space4.elem_aer": {
        "en": "Aer - Air (Languages)",
        "ga": "Aer - Aer (Teangacha)",
    },
    "space4.elem_anam": {
        "en": "Anam - Spirit (Soulbound Token)",
        "ga": "Anam - Anam (Comhartha Anam-bhainte)",
    },
    "space4.mac_leinn": {
        "en": "Mac Léinn - Formative Assessment",
        "ga": "Mac Léinn - Measúnú Formeach",
    },
    "space4.fiosraigh": {
        "en": "Fiosraigh - Classroom Bridge",
        "ga": "Fiosraigh - Droichead Seomra Ranga",
    },
    "footer.anam_bonneagar": {
        "en": "Anam Bonneagar",
        "ga": "Anam Bonneagar",
    },
}


def set_lang(lang: str) -> None:
    """Set the current language. Must be one of LANGS."""
    if lang not in LANGS:
        raise ValueError(f"Unknown language '{lang}'. Supported: {', '.join(LANGS)}")
    global _current_lang
    _current_lang = lang


def get_lang() -> str:
    """Get the current language code."""
    return _current_lang


def translate(key: str, lang: str | None = None, **kwargs: object) -> str:
    """Translate a key into the current (or specified) language.

    Args:
        key: The i18n key (e.g. "space3.title").
        lang: Optional explicit language override. Defaults to current.
        **kwargs: For keys with placeholders, e.g. translate(
            "space3.diegetic_zone", zone="Emain Macha").

    Returns:
        The translated string. Falls back to English, then the key itself
        if neither is available. Missing languages return the English
        string and a TODO marker.
    """
    target = lang or _current_lang
    strings = I18N_STRINGS.get(key)
    if strings is None:
        return key
    translated = strings.get(target)
    if translated is None:
        translated = strings.get("en", key)
        if target != "en":
            return f"{translated} (TODO: {target})"
    if kwargs:
        try:
            return translated.format(**kwargs)
        except (KeyError, IndexError):
            return translated
    return translated
