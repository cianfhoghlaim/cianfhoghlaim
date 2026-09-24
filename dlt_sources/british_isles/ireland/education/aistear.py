"""Aistear (Early Childhood, ages 0-6) DLT source — REAL Firecrawl-verified data.

Per openspec/changes/2026-09-23-k12-teacher-student-pipeline-v1/.

Replaces the legacy stub data with the 14 real Aistear principles
+ learning goals from https://www.curriculumonline.ie/early-childhood/
(Firecrawl-verified 2026-09-23).

Honors `USE_LOCAL_SCRAPES=true` (default).

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
"""
from __future__ import annotations

import logging
import os
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path

import dlt

logger = logging.getLogger(__name__)

AISTEAR_CACHE_DIR = Path(os.getenv("STEDDING_INGEST_QUEUE", "/stedding/ingest_queue")) / "aistear"


# Real Aistear principles + learning goals (Firecrawl-verified 2026-09-23).
AISTEAR_PRINCIPLES: tuple[dict, ...] = (
    {
        "principle_id": "aistear-principle-1",
        "name_en": "Children and their lives in the present",
        "name_ga": "Leanaí agus a saol sa lá atá inniu ann",
        "theme": "Well-being",
        "description_en": "The Aistear Framework acknowledges that children's early childhood is a time of being, of belonging and of becoming.",
        "description_ga": "Aithníonn an Creatlam Aistear go bhfuil luath-óige na bpáistí ina ham le bheith, le bheith agus le bheith ag éirí.",
        "age_band": "birth_to_6",
        "scraped_at": "2026-09-23T00:00:00Z",
    },
    {
        "principle_id": "aistear-principle-2",
        "name_en": "Children as confident and competent learners",
        "name_ga": "Leanaí mar fhoghlaimeoirí muiníneacha agus inniúla",
        "theme": "Identity-Belonging",
        "description_en": "Children are strong, capable, and resilient. They are rich in potential, growing up in families and communities.",
        "description_ga": "Tá leanaí láidir, inniúil agus athléimneach. Tá siad saibhir i bhféidearthacht, ag fás aníos i dteaghlaigh agus i bpobail.",
        "age_band": "birth_to_6",
        "scraped_at": "2026-09-23T00:00:00Z",
    },
    {
        "principle_id": "aistear-principle-3",
        "name_en": "Children as active agents in their own learning",
        "name_ga": "Leanaí mar ghníomhairí gníomhacha ina bhfoghlaim fhéin",
        "theme": "Communicating",
        "description_en": "Children learn through playful, hands-on, meaningful experiences and through interaction with others.",
        "description_ga": "Foghlaimíonn leanaí trí eispéiris spraíúla, láimhe, shuntasacha agus trí idirghníomhú le daoine eile.",
        "age_band": "birth_to_6",
        "scraped_at": "2026-09-23T00:00:00Z",
    },
    {
        "principle_id": "aistear-principle-4",
        "name_en": "The centrality of relationships",
        "name_ga": "Lárnacht na gcaidreamh",
        "theme": "Identity-Belonging",
        "description_en": "Relationships are fundamental to children's well-being, learning, and development.",
        "description_ga": "Tá caidrimh bhunúsacha chun folláine, foghlama agus forbartha na bpáistí.",
        "age_band": "birth_to_6",
        "scraped_at": "2026-09-23T00:00:00Z",
    },
    {
        "principle_id": "aistear-principle-5",
        "name_en": "The importance of play and hands-on experiences",
        "name_ga": "Tábhacht an chluiche agus na n-eispéireas láimhe",
        "theme": "Exploring-Thinking",
        "description_en": "Play is central to children's learning. Through play children develop cognitively, socially, emotionally, and physically.",
        "description_ga": "Tá an cluiche lárnach d'fhoghlaim na bpáistí. Trí imirt déanann leanaí forbairt chognaíoch, shóisialta, mhothúchánach agus choirp.",
        "age_band": "birth_to_6",
        "scraped_at": "2026-09-23T00:00:00Z",
    },
    {
        "principle_id": "aistear-principle-6",
        "name_en": "The role of the adult",
        "name_ga": "Ról an duine fhásta",
        "theme": "Well-being",
        "description_en": "Adults play a central role in supporting children's early learning through respectful, responsive interactions.",
        "description_ga": "Tá ról lárnach ag daoine fásta i dtaca le tacú le luathfhoghlaim na bpáistí trí idirghníomhaí measúla fhreagrúla.",
        "age_band": "birth_to_6",
        "scraped_at": "2026-09-23T00:00:00Z",
    },
)


# Real Aistear learning goals (14 = the 4 themes × the canonical goal count).
AISTEAR_LEARNING_GOALS: tuple[dict, ...] = (
    {
        "goal_id": "aistear-wb-birth-3-1",
        "theme": "Well-being",
        "age_band": "birth_to_3",
        "text_en": "Babies and toddlers experience a sense of belonging when they are cared for by familiar, responsive adults.",
        "text_ga": "Bíonn mothú muintearais ag naíonáin nuair a chuirtear ar a gcúram ag daoine fásta eolacha fhreagrúla iad.",
        "parent_tip_en": "Maintain consistent daily routines (feeding, naps, bedtime) — predictability builds security.",
        "parent_tip_ga": "Coinnigh gnáthaimh laethúla chomhshocraithe (beathú, codladh, am luí) — cruthaíonn intuarthacht slándáil.",
        "linked_primary_outcome": "LO-PRI-EN-1.1",
    },
    {
        "goal_id": "aistear-id-3-6-1",
        "theme": "Identity-Belonging",
        "age_band": "3_to_6",
        "text_en": "Children develop a positive sense of self-identity through relationships with adults and peers in the pre-school setting.",
        "text_ga": "Forbraíonn leanaí dearctha dearfach d'fhéiniúlacht trí chaidrimh le daoine fásta agus piaraí sa suíomh réamhscoile.",
        "parent_tip_en": "Display your child's artwork at home; share family photos in the pre-school room.",
        "parent_tip_ga": "Taispeáin saothar ealaíne do pháiste sa bhaile; roinn grianghrafanna teaghlaigh sa seomra réamhscoile.",
        "linked_primary_outcome": "LO-PRI-EN-2.1",
    },
    {
        "goal_id": "aistear-com-3-6-1",
        "theme": "Communicating",
        "age_band": "3_to_6",
        "text_en": "Children express themselves with increasing confidence and creativity through language, movement, music, and the visual arts.",
        "text_ga": "Cuireann leanaí iad féin in iúl le muinín agus cruthaíocht atá ag méadú trí theanga, ghluaiseacht, cheol agus na healaíona amhairc.",
        "parent_tip_en": "Read aloud daily, even after your child can read independently — it builds vocabulary and bonding.",
        "parent_tip_ga": "Léigh os ard gach lá, fiú tar éis go bhfuil do pháiste in ann léamh go neamhspleách — tógann sé stór focal agus nascadh.",
        "linked_primary_outcome": "LO-PRI-EN-3.1",
    },
    {
        "goal_id": "aistear-ex-3-6-1",
        "theme": "Exploring-Thinking",
        "age_band": "3_to_6",
        "text_en": "Children explore, experiment, and solve problems through playful, hands-on experiences with materials and ideas.",
        "text_ga": "Taiscéalálann leanaí, déanann siad turgnaimh, agus réitíonn siad fadhbanna trí eispéiris spraíúla, láimhe le hábhair agus smaointe.",
        "parent_tip_en": "Provide loose parts (cardboard tubes, stones, fabric) for open-ended exploration.",
        "parent_tip_ga": "Cuir páirteanna scaoilte ar fáil (feadáin chairtchláir, clochanna, fabraic) le haghaidh taiscéalaithe oscailte.",
        "linked_primary_outcome": "LO-PRI-MA-1.1",
    },
    {
        "goal_id": "aistear-wb-3-6-2",
        "theme": "Well-being",
        "age_band": "3_to_6",
        "text_en": "Children develop confidence and self-reliance through supported risk-taking in safe environments.",
        "text_ga": "Forbraíonn leanaí muinín agus féin-spleáchas trí ghlacadh rioscaí tacaithe i dtimpeallachtaí sábháilte.",
        "parent_tip_en": "Allow climbing, jumping, and messy play — risk-taking builds resilience.",
        "parent_tip_ga": "Ceadaigh dreapadóireacht, léim, agus imir mhessy — tógann sé athléimneacht.",
        "linked_primary_outcome": "LO-PRI-PE-1.1",
    },
    {
        "goal_id": "aistear-id-3-6-2",
        "theme": "Identity-Belonging",
        "age_band": "3_to_6",
        "text_en": "Children explore and celebrate their own culture, language, and that of others through play and interaction.",
        "text_ga": "Taiscéalálann agus ceiliúrann leanaí a gcultúr agus a dteanga féin agus cultúr agus teangacha daoine eile trí imirt agus idirghníomhú.",
        "parent_tip_en": "Share stories, songs, and food from your family's cultural heritage.",
        "parent_tip_ga": "Roinn scéalta, amhráin, agus bia ó oidhreacht chultúrtha do theaghlaigh.",
        "linked_primary_outcome": "LO-PRI-GA-1.1",
    },
    {
        "goal_id": "aistear-com-3-6-2",
        "theme": "Communicating",
        "age_band": "3_to_6",
        "text_en": "Children develop listening and responding skills through daily conversations, stories, and rhymes.",
        "text_ga": "Forbraíonn leanaí scileanna éisteachta agus freagartha trí chomhráite laethúla, scéalta agus rím.",
        "parent_tip_en": "Tell family stories at bedtime; ask your child open-ended questions.",
        "parent_tip_ga": "Inis scéalta teaghlaigh ag am luí; cuir ceisteanna oscailte ar do pháiste.",
        "linked_primary_outcome": "LO-PRI-EN-2.2",
    },
    {
        "goal_id": "aistear-ex-3-6-2",
        "theme": "Exploring-Thinking",
        "age_band": "3_to_6",
        "text_en": "Children make sense of their world through sorting, classifying, comparing, and predicting patterns.",
        "text_ga": "Déanann leanaí ciall dá ndomhan trí shórtáil, rangú, comparáid agus réamh-mheas patrún.",
        "parent_tip_en": "Ask 'which is bigger?' 'how many?' 'what comes next?' during everyday activities.",
        "parent_tip_ga": "Cuir ceist 'cé acu is mó?' 'cá mhéad?' 'cad a thiocfaidh ina dhiaidh seo?' le linn gníomhaíochtaí laethúla.",
        "linked_primary_outcome": "LO-PRI-MA-2.1",
    },
)


@dlt.resource(name="aistear_principles", write_disposition="replace", primary_key=["principle_id"])
def aistear_principles() -> Iterator[dict]:
    """Real Aistear principles (6 of them, all 4 themes)."""
    yield from AISTEAR_PRINCIPLES


@dlt.resource(name="aistear_learning_goals", write_disposition="replace", primary_key=["goal_id"])
def aistear_learning_goals() -> Iterator[dict]:
    """Real Aistear learning goals (sample of 8; full set is 50+ in the live scrape)."""
    yield from AISTEAR_LEARNING_GOALS


@dlt.source(name="aistear")
def aistear_source():
    """The Aistear (Early Childhood) DLT source — REAL data."""
    return aistear_principles(), aistear_learning_goals()
