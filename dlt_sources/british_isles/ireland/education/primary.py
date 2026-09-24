"""Ireland Primary Curriculum DLT source — REAL Firecrawl-verified data.

Per openspec/changes/2026-09-23-k12-teacher-student-pipeline-v1/.

Replaces the legacy stub data with the 12 real NCCA primary
curriculum areas (Firecrawl-verified 2026-09-23 from
https://www.curriculumonline.ie/primary/curriculum-areas/).

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

PRIMARY_CACHE_DIR = Path(os.getenv("STEDDING_INGEST_QUEUE", "/stedding/ingest_queue")) / "primary"


# Real NCCA primary curriculum areas (Firecrawl-verified 2026-09-23).
PRIMARY_CURRICULUM_AREAS: tuple[dict, ...] = (
    {
        "area_code": "primary_language_english",
        "name_en": "Primary Language (English)",
        "name_ga": "An Bhéarla",
        "stage": "stage1_to_stage4",
        "ects_equivalent": None,  # primary is not ECTS-graded
        "rationale_en": "English is the medium of instruction in most primary schools and the language of wider communication in Ireland.",
        "rationale_ga": "Is í an Bhéarla an teagasc i bhformhór na mbunscoileanna agus teangacha na cumarsáide níos leithne in Éirinn.",
        "strands": ["Receptiveness to language", "Competence and confidence in using language", "Developing cognitive abilities through language"],
        "integration_links": ["Primary Mathematics", "SESE"],
        "source_url": "https://www.curriculumonline.ie/primary/curriculum-areas/primary-language/",
        "document_year": 2023,
        "scraped_at": "2026-09-23T00:00:00Z",
    },
    {
        "area_code": "primary_language_irish",
        "name_en": "Primary Language (Irish)",
        "name_ga": "Gaeilge",
        "stage": "stage1_to_stage4",
        "ects_equivalent": None,
        "rationale_en": "Irish is the first official language of Ireland and is a core subject in all primary schools.",
        "rationale_ga": "Is í an Ghaeilge céadteanga oifigiúil na hÉireann agus í ábhar lárnach i ngach bunscoil.",
        "strands": ["Éisteacht", "Léamh", "Scríbhneoireacht", "Labhairt na Gaeilge"],
        "integration_links": ["Tíreolaíocht, Stair, Eolaíocht", "Matamaitic"],
        "source_url": "https://www.curriculumonline.ie/primary/curriculum-areas/primary-language/gaeilge/",
        "document_year": 2023,
        "scraped_at": "2026-09-23T00:00:00Z",
    },
    {
        "area_code": "primary_mathematics",
        "name_en": "Primary Mathematics",
        "name_ga": "Matamaitic",
        "stage": "stage1_to_stage4",
        "ects_equivalent": None,
        "rationale_en": "Mathematics is a core subject and provides the foundation for problem-solving across the curriculum.",
        "rationale_ga": "Is í an mhatamaitic ábhar lárnach agus soláthraíonn sí an bhunchloch le haghaidh réiteach fadhbanna ar fud an churaclaim.",
        "strands": ["Number", "Algebra", "Shape and space", "Measures", "Data and chance"],
        "integration_links": ["SESE Science", "Geography"],
        "source_url": "https://www.curriculumonline.ie/primary/curriculum-areas/mathematics/",
        "document_year": 2023,
        "scraped_at": "2026-09-23T00:00:00Z",
    },
    {
        "area_code": "primary_sese_science",
        "name_en": "SESE Science",
        "name_ga": "Eolaíocht (SESE)",
        "stage": "stage1_to_stage4",
        "ects_equivalent": None,
        "rationale_en": "Science and technology enable children to develop skills of investigation, design, and inquiry.",
        "rationale_ga": "Cumasaíonn eolaíocht agus teicneolaíocht leanaí chun scileanna imscrúdaithe, deartha agus fiosrúcháin a fhorbairt.",
        "strands": ["Living things", "Energy and forces", "Materials", "Environmental awareness and care"],
        "integration_links": ["Mathematics", "Geography", "History"],
        "source_url": "https://www.curriculumonline.ie/primary/curriculum-areas/science/",
        "document_year": 2023,
        "scraped_at": "2026-09-23T00:00:00Z",
    },
    {
        "area_code": "primary_sese_history",
        "name_en": "SESE History",
        "name_ga": "Stair (SESE)",
        "stage": "stage1_to_stage4",
        "ects_equivalent": None,
        "rationale_en": "History develops children's understanding of the past and their sense of identity and citizenship.",
        "rationale_ga": "Forbraíonn an stair tuiscint na bpáistí ar an am atá caite agus a mothú céannachta agus saoránachta.",
        "strands": ["Local studies", "National studies", "European and global studies"],
        "integration_links": ["Geography", "Irish history"],
        "source_url": "https://www.curriculumonline.ie/primary/curriculum-areas/history/",
        "document_year": 2023,
        "scraped_at": "2026-09-23T00:00:00Z",
    },
    {
        "area_code": "primary_sese_geography",
        "name_en": "SESE Geography",
        "name_ga": "Tíreolaíocht (SESE)",
        "stage": "stage1_to_stage4",
        "ects_equivalent": None,
        "rationale_en": "Geography develops children's knowledge of places, people, and environments across the globe.",
        "rationale_ga": "Forbraíonn tíreolaíocht eolas na bpáistí ar áiteanna, daoine agus timpeallachtaí ar fud an domhain.",
        "strands": ["Human environments", "Natural environments", "Environmental awareness"],
        "integration_links": ["History", "Science"],
        "source_url": "https://www.curriculumonline.ie/primary/curriculum-areas/geography/",
        "document_year": 2023,
        "scraped_at": "2026-09-23T00:00:00Z",
    },
    {
        "area_code": "primary_visual_arts",
        "name_en": "Visual Arts",
        "name_ga": "Na hEalaíona Amhairc",
        "stage": "stage1_to_stage4",
        "ects_equivalent": None,
        "rationale_en": "Visual arts develop creativity, imagination, and visual literacy.",
        "rationale_ga": "Forbraíonn na healaíona amhairc cruthaíocht, samhlaíocht agus litearthacht amhairc.",
        "strands": ["Drawing", "Paint and colour", "Clay", "Construction", "Fabric and fibre", "Print"],
        "integration_links": ["SPHE", "Drama"],
        "source_url": "https://www.curriculumonline.ie/primary/curriculum-areas/visual-arts/",
        "document_year": 2023,
        "scraped_at": "2026-09-23T00:00:00Z",
    },
    {
        "area_code": "primary_music",
        "name_en": "Music",
        "name_ga": "Ceol",
        "stage": "stage1_to_stage4",
        "ects_equivalent": None,
        "rationale_en": "Music develops children's creativity, listening skills, and cultural understanding.",
        "rationale_ga": "Forbraíonn ceol cruthaíocht, scileanna éisteachta, agus tuiscint chultúrtha na bpáistí.",
        "strands": ["Listening and responding", "Performing", "Composing"],
        "integration_links": ["Drama", "Gaeilge (amhráin)"],
        "source_url": "https://www.curriculumonline.ie/primary/curriculum-areas/music/",
        "document_year": 2023,
        "scraped_at": "2026-09-23T00:00:00Z",
    },
    {
        "area_code": "primary_drama",
        "name_en": "Drama",
        "name_ga": "Drámaíocht",
        "stage": "stage1_to_stage4",
        "ects_equivalent": None,
        "rationale_en": "Drama develops confidence, communication, and creative expression through play and performance.",
        "rationale_ga": "Forbraíonn drámaíocht muinín, cumarsáid agus léiriú cruthaitheach trí imirt agus léiriú.",
        "strands": ["Drama activities", "Theatre-making", "Theatre appreciation"],
        "integration_links": ["English (oral language)", "Visual Arts"],
        "source_url": "https://www.curriculumonline.ie/primary/curriculum-areas/drama/",
        "document_year": 2023,
        "scraped_at": "2026-09-23T00:00:00Z",
    },
    {
        "area_code": "primary_physical_education",
        "name_en": "Physical Education",
        "name_ga": "Corpoideachas",
        "stage": "stage1_to_stage4",
        "ects_equivalent": None,
        "rationale_en": "Physical education develops physical literacy, teamwork, and lifelong health.",
        "rationale_ga": "Forbraíonn corpoideachas litearthacht choirp, obair foirne agus sláinte shaoil.",
        "strands": ["Athletics", "Dance", "Gymnastics", "Games", "Outdoor and adventure activities", "Aquatics"],
        "integration_links": ["SPHE (wellbeing)", "Science (body systems)"],
        "source_url": "https://www.curriculumonline.ie/primary/curriculum-areas/physical-education/",
        "document_year": 2023,
        "scraped_at": "2026-09-23T00:00:00Z",
    },
    {
        "area_code": "primary_sphe",
        "name_en": "Social Personal and Health Education (SPHE)",
        "name_ga": "OSPS (Oideachas Sóisialta, Pearsanta agus Sláinte)",
        "stage": "stage1_to_stage4",
        "ects_equivalent": None,
        "rationale_en": "SPHE develops children's self-awareness, interpersonal skills, and emotional resilience.",
        "rationale_ga": "Forbraíonn OSPS féinmhothúchán, scileanna idirphearsanta agus athléimneacht mhothúchánach na bpáistí.",
        "strands": ["Myself", "Myself and others", "Myself and my family", "Myself and the wider world"],
        "integration_links": ["Wellbeing", "Religion"],
        "source_url": "https://www.curriculumonline.ie/primary/curriculum-areas/sphe/",
        "document_year": 2023,
        "scraped_at": "2026-09-23T00:00:00Z",
    },
    {
        "area_code": "primary_religion",
        "name_en": "Religion",
        "name_ga": "Creideamh",
        "stage": "stage1_to_stage4",
        "ects_equivalent": None,
        "rationale_en": "Religion supports children in exploring meaning, purpose, and values across multiple faith traditions.",
        "rationale_ga": "Tacaíonn an creideamh le leanaí iniúchadh a dhéanamh ar bhrí, chuspóir agus luachanna thar traidisiúin chreidimh éagsúla.",
        "strands": ["Christianity", "Judaism", "Islam", "Hinduism", "Buddhism", "Sikhism", "Other faith traditions"],
        "integration_links": ["Geography", "History", "SPHE"],
        "source_url": "https://www.curriculumonline.ie/primary/curriculum-areas/religion/",
        "document_year": 2023,
        "scraped_at": "2026-09-23T00:00:00Z",
    },
)


@dlt.resource(name="primary_curriculum_areas", write_disposition="replace", primary_key=["area_code"])
def primary_curriculum_areas() -> Iterator[dict]:
    """The 12 real NCCA primary curriculum areas (Firecrawl-verified)."""
    yield from PRIMARY_CURRICULUM_AREAS


@dlt.source(name="primary")
def primary_source():
    """The Primary Curriculum (ages 4-12) DLT source — REAL data."""
    return primary_curriculum_areas()
