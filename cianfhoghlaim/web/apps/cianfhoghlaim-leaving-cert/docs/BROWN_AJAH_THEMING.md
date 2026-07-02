# Brown Ajah Theming Guide

> The canonical theming guide for the Cianfhoghlaim OS.
> Maps the **Brown Ajah** of the Wheel of Time to the platform's components.

---

## The Brown Ajah

The **Brown Ajah** is one of the 7 Ajahs of the White Tower in Robert
Jordan's *Wheel of Time* series. The Brown Ajah are known for:

- **Healing** — in the WoT world, the Brown Ajah are the primary healers
- **Patience** — they study the Pattern for years before acting
- **Earth focus** — they work with Earth (the geography / land)
- **Scholarly** — the Brown Ajah library is the largest in the Tower

The Brown Ajah badge (per WoT) is a **knotwork pattern in russet brown**.
The Cianfhoghlaim OS uses **russet brown** (the colour of fertile earth)
as the platform's accent colour, alongside the 5 NCCA Key Competencies
colours (emerald, blue, gold, slate, rose).

---

## The 8 Brown Ajah members (the 8 NCCA subject specialists)

The 8 NCCA subject specialists at `cianfhoghlaim/agents/tuatha/agents/`
become the 8 Brown Ajah members. Each is mapped to a Tuatha Dé deity:

| Brown Ajah member | NCCA subject | Colour | Earth/healing aspect | Tuatha Dé deity |
|:--|:--|:--|:--|:--|
| Mathematics | Mathematics | blue-600 | The healing of the number | The Dagda (cauldron of plenty) |
| Applied Mathematics | Applied Mathematics | violet-600 | The healing of the application | Lugh (master of all arts) |
| Biology | Biology | emerald-600 | The healing of the body | Dian Cecht (medicine) |
| Chemistry | Chemistry | green-600 | The healing of the matter | Dian Cecht (healing) |
| Geography | Geography | yellow-600 | The healing of the land | Manannán mac Lir (sea) |
| History | History | red-700 | The healing of the memory | The Morrígan (war + death) |
| English | English | orange-600 | The healing of the word | Brigid (poetry + healing) |
| Gaeilge | Gaeilge | emerald (slightly different hue) | The healing of the language | Ogma (eloquence + learning) |
| Computer Science | Computer Science | slate-600 | The healing of the data | — (modern subject) |

The **Trí Dé Dána** ("Three Gods of Craft") — Brigid + Dian Cecht + Ogma
— are the 3 senior Brown Ajah who anchor the curriculum.

---

## The Amyrlin Seat (the orchestrator)

The **Amyrlin Seat** is the **root orchestrator agent**
(`agents/tuatha/agents/root_agent.py` + `agents/tuatha/orchestrator.py`).
The Amyrlin's name derives from **Tamyrlin** (per WoT) and parallels
the Catholic Church hierarchy:

- The **Amyrlin** dispatches to the 8 Brown Ajah
- The **Keeper of the Chronicles** records every formative attempt
- The **Hall of the Tower** is the `/about` page (a public, signed record)

The Western Schism of 1378-1415 (per WoT) parallels the **NCCA +
Cambridge Assessment International Education + AQA + OCR + Edexcel +
WJEC + CCEA + SQA** split — the "two Amyrlins" representing the
multiple examining bodies. The Cianfhoghlaim platform is one Amyrlin's
Tower; the 7 external exam boards are the other Amyrlins. The student
can sit the LC exam under either Amyrlin.

---

## The Dragon Reborn (the student)

The **Dragon Reborn** is the **student** who has completed the full
cross-subject mastery (5 NCCA Key Competencies × 8 NCCA subjects).

- **The White Tower** = the Cianfhoghlaim platform
- **Tar Valon** (the city of the White Tower) = the landing page (`/en` or `/ga`)
- **The Eye of the World** = the welcome banner — the first thing the student sees
- **The Two Rivers** = Connacht (the home base; the Cian lineage)

---

## The Dragon Banner of Wales

The **Dragon Banner** (per WoT: Cadwaladr ap Cadwallon + Owain Glyndwr;
red dragon on white) is the **Wales subnation flag** in the app.

- **Cadwaladr ap Cadwallon** (7th century, King of Gwynedd) — the red dragon on white background
- **Owain Glyndwr** (1400 rebellion against the English) — the quartered red-and-gold standard of 4 lions rampant, then the golden dragon on white from 1401

The Welsh dragon is the subnation's symbol; when the student reaches
the Wales subnation, the dragon banner flies on the realm map.

---

## The Tuatha'an (the Travelling People)

The **Tuatha'an** are the **Irish Travellers** (per WoT: Irish Travellers
+ Aiel + Irish red hair + Murphy Village, SC near Jordan's hometown
of Charleston).

- The **student-as-Tuatha'an** travels the 6 subnations in a covered wagon (the Cianfhoghlaim mobile client)
- The student is a **peaceful traveller** — they do not fight; they **learn**
- The Aiel connection (Irish red hair, itinerant metalworking) grounds the Brown Ajah's earth-working + patient study themes

---

## The 13 éraic treasures (the 13-tier SkillTreeBadge progression)

The 13 magical treasures that Lugh demanded as éraic for Cian's death
become the **13-tier SkillTreeBadge progression** (instead of the 4-tier
Khan Academy mastery levels).

| # | Éraic treasure | Educational theme | Subject affinity |
|--:|:--|:--|:--|
| 1 | Pig of Dobar (heals wounds) | Healing feedback | Biology |
| 2 | Heifer of Dobar | Pastoral care | Geography |
| 3 | Spear of Assal (never misses) | Precise reasoning | Mathematics |
| 4 | Chariot of king of Sidrach | Speed of completion | Applied Mathematics |
| 5 | Sword of Caladbolg (wielded by Tethra) | Algorithmic clarity | Computer Science |
| 6 | 7 pigs of Easmal (regenerate daily) | Daily practice | All subjects |
| 7 | Whelp of king of Ioruaidh | Loyalty + tenacity | English |
| 8 | Cooking spit of woman of Innis Cera | Crafted response | Gaeilge |
| 9 | Helmet + breastplate of king of Clochur | Defensive argument | History |
| 10 | 3 apples of the Hesperides | Triple-crown mastery | Cross-subject |
| 11 | Pigskin bag of healing well | Citation rigor | All subjects |
| 12 | Feather of Bird of Crannog (resurrects) | Recovery from failure | All subjects |
| 13 | Lugh's own samildanach | Universal mastery | All subjects |

The 4-tier Khan Academy Mastery (Attempted / Familiar / Proficient /
Mastered) becomes a 4-step ladder *within* each of the 13 éraic tiers,
giving 4 × 13 = **52 total mastery levels** instead of just 4.

---

## The 4 magical treasures of the Tuatha Dé Danann

The 4 treasures brought from the 4 northern cities become 4 fixed-anchor
learning aids in the app's header:

| City | Treasure | Learning instrument | Where in the app |
|:--|:--|:--|:--|
| **Falias** | Lia Fáil (Stone of Destiny, roars under the rightful king) | Search bar that "roars" (haptic-feel vibration) when valid NCCA LO code is typed | Top-center header |
| **Gorias** | Spear of Lugh (never misses) | Auto-evaluate button that always returns a per-criterion score | Practice page action bar |
| **Finias** | Sword of Nuada / Caladbolg | Tactile answer-input (the sword-strike of typing a response) | Formative item card |
| **Murias** | Cauldron of the Dagda (feeds an entire army) | Streak flame (never empties) | Header right |

---

## The 5 mythological invasions (5 educational stages)

The 4 mythological invasions of Ireland (Cessair → Partholón → Nemedians
→ Fomorians → Tuatha Dé Danann) map to 5 progression tiers:

| Mythological invasion | Educational stage | Subject scope |
|:--|:--|:--|
| Cessair (the first, pre-Flood) | Aistear (ages 0-6) | The 4 Aistear themes |
| Partholón (cleared the plains) | Primary (ages 4-12) | The 12 Primary curriculum areas |
| Nemedians (the third wave) | Junior Cycle (ages 12-15) | The 18 Junior Cycle subjects |
| Fomorians (the chaos before order) | Senior Cycle (ages 15-18) | The 50+ Leaving Cert subjects |
| Tuatha Dé Danann (the synthesis) | Tertiary + Enduring Learning | The 5 NCCA Key Competencies |

---

## The Esker Riada (the EN ↔ GA divider)

The **Esker Riada** (Dublin Bay to Galway Bay) is the visual dividing
line between the 4 northern realms (Leath Cuinn) and the 4 southern
realms (Leath Moga) on the realm map. The TranslationToggle in the
header is the "Esker Riada" — when you flip from EN to GA, you cross
the esker and the realm map's left half (Connacht) becomes the right
half (Munster).

---

## The Samhain + Beltane seasonal events

| Festival | Date | In-app event |
|:--|:--|:--|
| Samhain | 1 November | Éraic Season — students can "demand" (earn) the 13 magical treasures as badges |
| Beltane | 1 May | Cauldron of the Dagda — the streak flame is refilled to 100% for every student (summer refresh before the Leaving Cert exams in June) |

---

## The Grianan of Aileach (the Key Competencies matrix header)

The **Grianan of Aileach** (the ringfort seat of the Northern Uí
Néill, in Co. Donegal) is the visual reference for the circular
**5 Key Competencies × 8 subjects matrix** — a stone ringfort on a
hilltop, the sun illuminating the central courtyard (the cross-subject
mastery). The 5 NCCA Key Competencies are the 5 gate-towers, the 8
subjects are the 8 wall segments.

---

## The 3 sea-kings of Connacht (the 4 Geography specialisations)

The **3 sea-kings of Connacht** (O'Malleys, O'Dowds, O'Flahertys) plus
the **Mac Con Raoi** (the 4th) become 4 Geography subject specialisations:

- **O'Malleys** — the coastal cartography
- **O'Dowds** — the inland topography
- **O'Flahertys** — the Connemara wilds
- **Mac Con Raoi** — the Lough Corrib lake studies

The **Claddagh District** in Galway (a historic Gaeltacht area where
Irish was the everyday language) is the prototype for the Gaeilge
realm's "everyday Irish" toggle in the practice page.

---

## The Cian → Lugh header tagline (operator-only)

The Header's tagline draws from the clippings:

> **"Enduring Learning"** — *Cian fhoglaim* (Irish: "enduring learning"); in mythology, Cian ("the enduring one") was the father of Lugh ("master of all arts").

This is the only place where the Cian → Lugh mapping appears in
user-facing copy. It is documented in `CIANFHLOGHLAIM_LORE.md` only —
NOT on the public surface.

The public-facing tagline is the Brown Ajah motto:

> **"Aes Sedai — servants of all"**

(The Cian → Lugh → threefold gift of knowledge + skill + prophecy is
implicit in the Brown Ajah theming but is NEVER spelled out on the
public surface.)