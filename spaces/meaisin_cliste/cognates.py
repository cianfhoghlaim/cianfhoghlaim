"""
spaces/meaisin_cliste/cognates.py
Cognate seed data for Focloir na Se Naisiun (Theme 1 of Space 2).

The 6 Celtic nations share ~600-800 proto-Celtic roots. This module
seeds a small cognate table (~30 entries) that the Space can use to
demonstrate the cross-nation dictionary lookup, without needing the
full ~1,800-row DLT pipeline in oideachais/language/cognates.py.

Each row: (proto_celtic, en_translation, ie, ni_or_sc, wls, im, cornish)
Missing cells are TODO (Breton is also TODO across the table).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Cognate:
    proto_celtic: str
    en: str
    ie: str  # Gaeilge
    gd: str  # Gaidhlig (Scottish)
    cy: str  # Cymraeg (Welsh)
    gv: str  # Gaelg (Manx)
    kw: str  # Kernewek (Cornish)
    br: str  # Brezhoneg (Breton) - TODO across the table


# 30 cognate rows, hand-picked from the most-frequent Celtic roots.
COGNATES: list[Cognate] = [
    Cognate("*windo-", "white, fair", "fionn", "fionn", "gwyn", "fynn", "gwynn", "TODO: gwenn"),
    Cognate("*dubno-", "world", "domhan", "domhan", "byd", "cruinne", "bys", "TODO: bed"),
    Cognate("*nokwti-", "night", "oíche", "oidhche", "nos", "oie", "nos", "TODO: noz"),
    Cognate("*kwekwlo-", "wheel", "roth", "cuibhle", "olwyn", "quid", "ros", "TODO: rod"),
    Cognate("*balano-", "valley", "gleann", "gleann", "cwm", "glion", "glyn", "TODO: traoñ"),
    Cognate("*indo-sue-", "island", "inis", "inis", "ynys", "ellan", "enys", "TODO: enez"),
    Cognate("*mori-", "sea", "muir", "muir", "môr", "mooir", "mor", "TODO: mor"),
    Cognate("*kambri-", "compatriot, friend", "comharsa", "coimhearsnach", "cymydog", "skeyl", "kentrevek", "TODO: kenvroad"),
    Cognate("*skaro-", "sharp", "geár", "géar", "garw", "gear", "krev", "TODO: berr"),
    Cognate("*glano-", "clean, pure", "glan", "glan", "glân", "gial", "glan", "TODO: glan"),
    Cognate("*kerd-", "art, craft", "ceird", "ceàrd", "cerdd", "creck", "creft", "TODO: kredenn"),
    Cognate("*bratu-", "judgement, verdict", "breithiúnas", "breitheanas", "barn", "breth", "brennans", "TODO: barn"),
    Cognate("*kaljo-", "hard", "calma", "calma", "caled", "creg", "kales", "TODO: kalet"),
    Cognate("*kluti-", "famous, heard", "clú", "cliù", "clod", "enmys", "enys", "TODO: brud"),
    Cognate("*trebā", "home, dwelling", "treabh", "treabha", "tref", "treigh", "tre", "TODO: tre"),
    Cognate("*wēro-", "water", "uir", "uir", "gŵr", "ushtey", "dowr", "TODO: dour"),
    Cognate("*kīro-", "dark, black", "ciar", "ciar", "du", "doo", "du", "TODO: du"),
    Cognate("*genu-", "mouth, jaw", "giotán", "ginn", "gen", "gea", "gen", "TODO: genou"),
    Cognate("*aliso-", "alder", "fearn", "fhearn", "gwern", "farrane", "gwern", "TODO: gwern"),
    Cognate("*rīgant-", "queen", "ríon", "bantrighe", "rhiain", "queen", "myrgh", "TODO: rouanez"),
    Cognate("*seno-", "old", "Sean", "Sean", "hen", "shenn", "hen", "TODO: hen"),
    Cognate("*klāros", "clear, bright", "glé", "soilleir", "clir", "soyll", "skler", "TODO: sklaer"),
    Cognate("*meld-", "lightning", "mealltach", "dealanaich", "mellt", "mellian", "tan", "TODO: luc'hedenn"),
    Cognate("*beru-", "fierce, strong", "borr", "borr", "braw", "birra", "berr", "TODO: berr"),
    Cognate("*kanyā", "wolf", "mac tíre", "madadh-allaidh", "blaidd", "madjin", "blyd", "TODO: bleiz"),
    Cognate("*kaltā", "hazel", "coll", "calltuinn", "coll", "coll", "coll", "TODO: gwez-koll"),
    Cognate("*penn-", "head", "ceann", "ceann", "pen", "kione", "pen", "TODO: penn"),
    Cognate("*dubros", "water, dark stream", "dobhar", "dobhar", "dwfr", "dobbyr", "dowr", "TODO: douar"),
    Cognate("*windo-berno-", "white peak", "Sliabh gCualann", "Beinn Bhàn", "Bannau Brycheiniog", "Slieu Whallian", "Bre Beago", "TODO: TODO"),
    Cognate("*kaltio-", "wood, forest", "coill", "coille", "celli", "keyll", "kelli", "TODO: koad"),
]


def search(prefix: str, lang: str = "ie") -> list[Cognate]:
    """Return all cognates whose proto-Celtic or selected-language form
    starts with `prefix` (case-insensitive)."""
    prefix = prefix.lower()
    out: list[Cognate] = []
    for c in COGNATES:
        if c.proto_celtic.lower().lstrip("*").startswith(prefix):
            out.append(c)
            continue
        lang_form = getattr(c, lang, "")
        if lang_form and lang_form.lower().startswith(prefix):
            out.append(c)
    return out


def by_proto_root(root: str) -> Cognate | None:
    """Return the cognate with the given proto-Celtic root, or None."""
    for c in COGNATES:
        if c.proto_celtic == root:
            return c
    return None
