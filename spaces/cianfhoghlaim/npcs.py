"""
spaces/cianfhoghlaim/npcs.py
The 6 Celtic NPCs for the Cianfhoghlaim RPG.

Each NPC is grounded in a cached Wikipedia article (see
doc/hackathons/wikipedia-sources/). The dialogue model is constrained
to stay in character by grounding the system prompt in the source
excerpt.

The 6 NPCs map to 6 of the 7 Celtic nations in scope (Cornish is
sidelined in favour of Breton, since both have similar revival stories
and Breton has more Wikipedia coverage). The Tuatha De Danann
themselves are not NPCs — they are the env (the map is "Tuatha").

NPC roster (in map order, west to east):
  1. Ui Liathain (IE)            - Leinster cycle
  2. Manannan mac Lir (IM)       - Sea god of the Otherworld
  3. Rhiannon (WLS)              - Mabinogion, the Otherworld rider
  4. Dian Cecht (IE/GOD)         - Physician god (slightly fictional)
  5. Cian (IE)                   - Father of Lugh Lámhfhada
  6. The Deisi (IE diaspora)     - The Expulsion of the Deisi
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Npc:
    """A single NPC entry, grounded in a Wikipedia article."""
    npc_id: str
    name_en: str
    name_ga: str
    title: str
    nation_code: str          # "IE" | "NI" | "WLS" | "IM" | "SCT" | "COR" | "BRT"
    nation_name: str
    era: str                  # "Iron Age" | "Early Medieval" | "Mythological" | "Fictional"
    map_x: float              # 0.0 - 1.0, normalized British Isles map coord
    map_y: float
    diegetic_zone: str        # Where the NPC stands (atmospheric)
    one_line_summary: str     # One sentence for the social card
    scholarly_excerpt: str    # Cached Wikipedia paraphrase (the source-of-truth)
    artifact_offered: str     # What the NPC gives the player
    quest_hook: str           # Optional side-quest
    emotional_default: str    # "wry" | "wounded" | "curious" | "defiant" | "gentle"
    color_token: str          # "emerald" | "azure" | "amber" | "indigo" | "gold"
    wikipedia_source: str     # Filename in doc/hackathons/wikipedia-sources/


NPCS: list[Npc] = [
    Npc(
        npc_id="ui_liathain",
        name_en="Ui Liathain",
        name_ga="Uí Liatháin",
        title="Laoch na nGael / Champion of the Gael",
        nation_code="IE",
        nation_name="Ireland (Leinster)",
        era="Iron Age",
        map_x=0.42, map_y=0.55,
        diegetic_zone="the pine ridge above Glencree",
        one_line_summary=(
            "The Uí Liatháin dynasty, guardians of the Leinster hill-fort "
            "and the memory of a hundred clan feuds."
        ),
        scholarly_excerpt=(
            "The Uí Liatháin were a dynasty of the Laigin, an ancient "
            "people of Leinster, Ireland. They are mentioned in early "
            "Irish genealogies and held territory in what is now south "
            "Dublin and north Wicklow. Their hill-fort at Rathdown was "
            "a centre of learning and craft in the centuries before the "
            "Viking age. They were clients of the kings of Leinster, "
            "and several of their number are recorded in the annals as "
            "warriors, poets, and judges."
        ),
        artifact_offered="a slate whetstone engraved with a triskelion",
        quest_hook="Recover three lost clan-tokens from the Liffey corridor.",
        emotional_default="wry",
        color_token="emerald",
        wikipedia_source="ga:Uí_Liatháin",
    ),
    Npc(
        npc_id="manannan_mac_lir",
        name_en="Manannan mac Lir",
        name_ga="Manannán mac Lir",
        title="Rí na dTonn / King of the Waves",
        nation_code="IM",
        nation_name="Isle of Man",
        era="Mythological",
        map_x=0.40, map_y=0.20,
        diegetic_zone="the fog-bound jetty at Port Erin",
        one_line_summary=(
            "The sea-god of the Otherworld, who ferries the dead across "
            "the sound and keeps the harbour-light lit for lost sailors."
        ),
        scholarly_excerpt=(
            "Manannán mac Lir is a sea deity in Irish mythology. He is "
            "associated with the Otherworld, the afterlife, and the sea. "
            "In the Immram Brain and other early Irish texts, he is the "
            "lord of an island paradise reached by a silver boat. He "
            "appears in the Fenian cycle as a foster-father to the hero "
            "Fionn mac Cumhaill. In Manx tradition, he is the patron of "
            "the island itself, and his name survives in the title of "
            "the Manx ruler. The Isle of Man's parliament, the Tynwald, "
            "is said to commemorate his coronation-day."
        ),
        artifact_offered="a piece of driftwood that hums when storms are near",
        quest_hook="Find the three lost seals of the harbour-light.",
        emotional_default="gentle",
        color_token="azure",
        wikipedia_source="en:Manannán_mac_Lir",
    ),
    Npc(
        npc_id="rhiannon",
        name_en="Rhiannon",
        name_ga="Rhiannon",
        title="MARCHOG Y BYD ARALL / Rider of the Otherworld",
        nation_code="WLS",
        nation_name="Wales",
        era="Early Medieval",
        map_x=0.34, map_y=0.45,
        diegetic_zone="the horse-gate at Pembroke, the wind blowing the gorse",
        one_line_summary=(
            "The Mabinogion's horse-goddess, who rides the night between "
            "Dyfed and the Otherworld on a pale mare that no mortal can "
            "overtake."
        ),
        scholarly_excerpt=(
            "Rhiannon is a figure in Welsh mythology, appearing in the "
            "Mabinogi of Pwyll and the Mabinogi of Branwen. She is "
            "associated with horses and birds, and her story involves "
            "pursuit, marriage to Pwyll, the loss and recovery of her "
            "son Pryderi, and a penance imposed on her for the loss. "
            "She is often identified with the Irish goddess Macha and "
            "the Gaulish Epona. Her name may derive from the Common "
            "Celtic *Rīgantōna, 'great queen'."
        ),
        artifact_offered="a horseshoe nail of pale iron, still warm",
        quest_hook="Help her carry the birdsong across the Dyfed hills.",
        emotional_default="wounded",
        color_token="indigo",
        wikipedia_source="en:Rhiannon",
    ),
    Npc(
        npc_id="dian_cecht",
        name_en="Dian Cecht",
        name_ga="Dian Cécht",
        title="LIAGH / The Physician",
        nation_code="IE",
        nation_name="Ireland (Tuatha Dé Danann)",
        era="Mythological",
        map_x=0.50, map_y=0.40,
        diegetic_zone="the well-spring of Sláine, where the waters run hot",
        one_line_summary=(
            "The physician-god of the Tuatha Dé Danann, who forged a "
            "silver hand for his son and a well of healing that can "
            "raise the dead — for a price."
        ),
        scholarly_excerpt=(
            "Dian Cécht is the physician of the Tuatha Dé Danann in "
            "Irish mythology. He is associated with healing, the forge, "
            "and the well of healing at Sláine (now believed to be in "
            "co. Kildare). In the Second Battle of Mag Tuired he replaces "
            "the mortally wounded Nuada with a silver hand; in some "
            "versions he slays his own son Miach for surpassing him in "
            "craft. He is sometimes paired with Airmed, his daughter, "
            "who tends the herbs that grow from Miach's grave. His name "
            "may mean 'swift in power' or 'swift in step'."
        ),
        artifact_offered="a vial of well-water that glows faintly",
        quest_hook="Find the herb that grows only on the grave of the unjust.",
        emotional_default="defiant",
        color_token="amber",
        wikipedia_source="en:Dian_Cecht",
    ),
    Npc(
        npc_id="cian",
        name_en="Cian of Cualann",
        name_ga="Cian mac Díanmasa",
        title="ATHAIR LÁMHFHADA / Father of Lugh",
        nation_code="IE",
        nation_name="Ireland (Cualann)",
        era="Mythological",
        map_x=0.46, map_y=0.50,
        diegetic_zone="the hazel-wood above the Liffey, where Cian met the balor",
        one_line_summary=(
            "The father of Lugh Lámhfhada, who came to the Tuatha Dé "
            "Danann in the form of a pig, was undone by a jealous "
            "brother, and was avenged by the son he never lived to "
            "raise."
        ),
        scholarly_excerpt=(
            "Cian mac Díanmasa is a figure in Irish mythology, the son "
            "of Díanmas of the Tuatha Dé Danann. He is the father of "
            "the hero Lugh Lámhfhada. In the Cath Maige Tuired he is "
            "killed by the sons of Tuireann (his own brothers), who "
            "disguised themselves as swineherds. Lugh, in his first act "
            "as champion of the Tuatha, leads a war-party to avenge his "
            "father and extracts the fines that became the Treasures "
            "of the Tuatha. His name may mean 'ancient' or 'enduring'."
        ),
        artifact_offered="a tuft of boar-bristle bound with silver wire",
        quest_hook="Walk the three roads Cian walked, and find the well.",
        emotional_default="gentle",
        color_token="emerald",
        wikipedia_source="en:Cian",
    ),
    Npc(
        npc_id="the_deisi",
        name_en="The Deisi",
        name_ga="Na Déise",
        title="AN T-AOS DÍDEANACH / The Dispossessed",
        nation_code="IE",
        nation_name="Ireland (Waterford / diaspora)",
        era="Early Medieval",
        map_x=0.44, map_y=0.65,
        diegetic_zone="the rock of Carrigaphooca, where the smoke of the exile rises",
        one_line_summary=(
            "The Deisi, a free people of the Leinster plain, were driven "
            "from their land by the encroachment of Munster and the "
            "Viking. They became the founders of Waterford, and their "
            "diaspora carried the name of Munster into the heart of "
            "Wales and beyond."
        ),
        scholarly_excerpt=(
            "The Expulsion of the Déisi is an episode in the Lebor "
            "Gabála Érenn and other medieval Irish texts, describing "
            "the displacement of the Déisi, a free people of Leinster, "
            "by the encroachment of the Uí Cheinnselaig and the "
            "kingdom of Munster in the 4th-5th centuries. The Déisi "
            "are variously said to have settled in Munster (where they "
            "became the founders of the kingdom of Osraige and the "
            "Déisi of Waterford), in south Wales, and in the Irish "
            "diaspora. The narrative is preserved in the Book of "
            "Leinster and is cited as one of the earliest documented "
            "examples of a Celtic migration across the Irish Sea."
        ),
        artifact_offered="a leather strap from a currach, salt-stiffened",
        quest_hook="Carry the cairn-stones to the place of the missing.",
        emotional_default="wounded",
        color_token="gold",
        wikipedia_source="en:The_Expulsion_of_the_Déisi",
    ),
]


def get_npc(npc_id: str) -> Npc | None:
    """Return the NPC with the given id, or None if not found."""
    for npc in NPCS:
        if npc.npc_id == npc_id:
            return npc
    return None


def npcs_by_nation() -> dict[str, list[Npc]]:
    """Group NPCs by their nation_code."""
    out: dict[str, list[Npc]] = {}
    for npc in NPCS:
        out.setdefault(npc.nation_code, []).append(npc)
    return out


def build_dialogue_messages(
    npc: Npc,
    player_utterance: str,
    conversation_history: list[dict[str, str]],
) -> list[dict[str, str]]:
    """Build the messages array for the BAML GenerateNpcDialogue call.

    Args:
        npc: The NPC to speak with.
        player_utterance: What the player just said.
        conversation_history: The previous turns, each as
            {"role": "user"|"assistant", "content": ...}. The assistant
            turns are the NPC's previous utterances.

    Returns:
        A list of {"role", "content"} dicts in OpenAI chat-completions
        format, ready to pass to chat_complete().
    """
    history_text = "\n".join(
        f"{turn['role'].title()}: {turn['content']}"
        for turn in conversation_history[-6:]
    ) or "(no previous turns)"

    system = (
        f"You are roleplaying {npc.name_en} ({npc.name_ga}), {npc.title}, "
        f"of {npc.nation_name} in the {npc.era} era. "
        f"Stay in character. Ground every claim in the source material "
        f"below. Mix in one Irish-language phrase every three turns. "
        f"Do not exceed three sentences per turn.\n\n"
        f"Source material (Wikipedia paraphrase):\n---\n"
        f"{npc.scholaraly_excerpt if hasattr(npc, 'scholaraly_excerpt') else npc.scholarly_excerpt}\n---"
    )
    user = (
        f"[Diegetic zone: {npc.diegetic_zone}]\n"
        f"[Emotional default: {npc.emotional_default}]\n"
        f"Conversation so far:\n{history_text}\n\n"
        f"Player: {player_utterance}\n\n"
        f"Reply as {npc.name_en}. Be brief. Stay grounded. "
        f"Reply in JSON with keys: utterance_en, utterance_ga, "
        f"scholarly_footnote_en, scholarly_footnote_ga, emotional_tone, "
        f"asks_player_about."
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
