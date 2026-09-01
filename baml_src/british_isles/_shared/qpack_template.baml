// BAML template: Cross-stage Quest Pack Generator
//
// Per the 2026-08-18-mega-3-roadmap-v1 + the 2026-08-26-mega-3a-baml-and-adk-v1 change.
//
// Replaces the 8 hand-written qpack_*.baml files:
//   - qpack_mathematics.baml (382 LOC)
//   - qpack_gaeilge.baml (345 LOC)
//   - qpack_chemistry.baml (342 LOC)
//   - qpack_history.baml (323 LOC)
//   - qpack_geography.baml (313 LOC)
//   - qpack_english.baml (307 LOC)
//   - qpack_computer_science.baml (290 LOC)
//   - qpack_applied_mathematics.baml (368 LOC)
//   = 2,670 LOC removed, ~250 LOC added, net -2,420 LOC
//
// This template covers ALL 4 stages (Leaving Cycle + Junior Cycle +
// A-Level + GCSE) via the `subject` and `stage` parameters + the
// `{% if %}` conditional blocks below.
//
// The 8 NCCA Junior Cycle subjects at full scope (per Q4):
// Mathematics, English, Gaeilge, Science, Geography, History, CSPE, SPHE.
//
// The canonical 14 LC subjects (per LC_SUBJECT_CONFIG):
// mathematics, applied_mathematics, chemistry, physics, biology
// art, music, computer_science.
//
// The canonical 15 A-Level + 9 GCSE subjects (per the 3 boards):
// see baml_src/british_isles/england/education/a_level_extraction/
// and gcse_extraction/.
//
// Re-gen: cd cianfhoghlaim && uv run baml-cli generate --from baml_src
//
// Reference:
//   openspec/changes/2026-08-26-mega-3a-baml-and-adk-v1/proposal.md
//   baml_src/british_isles/_shared/qpack_template.baml (this file)

// ============================================================================
// Canonical enums
// ============================================================================

enum QuestPackStage {
  JC @description("Junior Cycle (Ireland, ages 12-15)")
  LC_FL @description("Leaving Certificate Foundation Level")
  LC_OL @description("Leaving Certificate Ordinary Level")
  LC_HL @description("Leaving Certificate Higher Level")
  GCSE @description("GCSE (England, ages 14-16)")
  AS_LEVEL @description("AS-Level (England)")
  A_LEVEL @description("A-Level (England)")
}

enum NCCASubjectSlug {
  MATHEMATICS
  APPLIED_MATHEMATICS
  CHEMISTRY
  PHYSICS
  BIOLOGY
  GEOGRAPHY
  ENGLISH
  GAEILGE
  FRENCH
  HISTORY
  BUSINESS
  ACCOUNTING
  ART
  MUSIC
  COMPUTER_SCIENCE
  SCIENCE          @description("Junior Cycle Science only")
  IRISH_HISTORY    @description("Junior Cycle History only")
  CSPE             @description("Junior Cycle CSPE only")
  SPHE             @description("Junior Cycle SPHE only")
}

enum QuestPackLanguage {
  EN @description("English only")
  GA @description("Irish (Gaeilge) only")
  EN_AND_GA @description("Bilingual EN + GA")
}

enum QuestPackDifficulty {
  FOUNDATION @description("Difficulty 1-2: recall + comprehension")
  INTERMEDIATE @description("Difficulty 3-4: application + analysis")
  ADVANCED @description("Difficulty 5-6: synthesis + evaluation")
  EXTENSION @description("Difficulty 7+: stretch / olympiad")
}

enum QuestPackItemType {
  SHORT_ANSWER
  WORKED_SOLUTION
  MULTIPLE_CHOICE
  CONCEPTUAL
  VISUAL_INTERPRETATION
  WORD_PROBLEM
  PROOF
  STRUCTURE_DRAWING
  DIAGRAM_BASED
  ESSAY
  PRACTICAL
  FILL_IN_BLANK
}

enum QuestPackFeedbackChannel {
  SUBJECT_TUTOR @description("Concrete + worked-example feedback")
  QUEST_GUIDE @description("Graduated hints (4 levels)")
  CURRICULUM_LOOKUP @description("Direct NCCA LO code citation")
  LAB_ASSISTANT @description("Mandatory experiment guidance (for lab questions)")
  RESEARCH_ASSISTANT @description("Cross-topic + cross-subject synthesis")
}

// ============================================================================
// Core value types (replaces per-subject BilingualText/EvidenceLink)
// ============================================================================

class QuestPackBilingualText {
  text_en string @description("English text")
  text_ga string? @description("Irish translation; null if EN-only")
}

class QuestPackEvidenceLink {
  source_pdf string @description("Path to the source NCCA / awarding-body PDF")
  source_page int @description("PDF page where the LO appears (1-indexed)")
  excerpt_en string @description("Verbatim English excerpt")
  excerpt_ga string? @description("Verbatim Irish excerpt (if available)")
  ncca_url string? @description("Canonical curriculumonline.ie URL (if known)")
}

// ============================================================================
// The canonical 4-stage quest pack generator
// ============================================================================

function GenerateSubjectQuestPack(
  syllabus_extract: string,
  subject: NCCASubjectSlug,
  stage: QuestPackStage,
  language: QuestPackLanguage,
  lo_codes: string[]
) -> SubjectQuestPack {
  client BIEPV3Extract
  prompt #"
    {{ _.role("user") }}
    You are an expert Irish / UK curriculum-aligned quest pack generator for the subject `{{ subject }}` at stage `{{ stage }}` in language `{{ language }}`.

    Build a formative assessment quest pack from the syllabus extract below. The pack MUST have:
    - 5-10 formative items keyed to the supplied NCCA LO codes ({{ lo_codes | length }} codes).
    - Each item has a difficulty (Foundation / Intermediate / Advanced / Extension), an item type, a prompt, an expected response, and 3-5 marking-scheme points.
    - Items are bilingual where language = EN_AND_GA; text_ga is null otherwise.
    - Each item cites its source NCCA LO code (from `lo_codes`).
    - The pack has a feedback_channel mapping per item (which specialist tutor reviews this item).

    Subject-specific guidance:
    {% if subject == NCCASubjectSlug.MATHEMATICS %}
    - Topics follow the 5 NCCA math strands: Statistics & Probability, Geometry & Trigonometry, Number, Algebra, Functions
    - LO codes use prefix `LC-MATH-LO-NNN` (LC) or `JC-MATH-LO-NNN` (JC)
    - Worked-solution items MUST include all formula references in the marking-scheme points
    {% elif subject == NCCASubjectSlug.CHEMISTRY %}
    - Topics follow the 4 NCCA chemistry strands: Atomic Structure, Chemical Bonding, Stoichiometry, Acids/Bases
    - LO codes use prefix `LC-CHEM-LO-NNN` (LC) or `JC-CHEM-LO-NNN` (JC)
    - Structure-drawing items (Lewis structures) are valid for LC HL only
    {% elif subject == NCCASubjectSlug.PHYSICS %}
    - Topics span Mechanics, Waves, Light, Electricity & Magnetism, Modern Physics, Particle Physics
    - LO codes use prefix `LC-PHYS-LO-NNN`
    - Capture all formula references in the marking-scheme points; include SI units + significant figures conventions
    {% elif subject == NCCASubjectSlug.BIOLOGY %}
    - Topics span the 3 units: The Study of Life, The Cell, The Organism
    - LO codes use prefix `LC-BIO-LO-NNN`
    - Capture diagrams (cell structure, organ systems, ecosystems) under `evidence_link`
    - Note practical activities (mandatory 30%) under `marking_scheme_points`
    {% elif subject == NCCASubjectSlug.GEOGRAPHY %}
    - Topics span Physical Geography, Regional Geography, Human Environment
    - LO codes use prefix `LC-GEOG-LO-NNN` (LC) or `JC-GEOG-LO-NNN` (JC)
    {% elif subject == NCCASubjectSlug.ENGLISH %}
    - Capture the prescribed texts (poetry, prose, drama) under `evidence_link`
    - LO codes use prefix `LC-ENGL-LO-NNN`
    {% elif subject == NCCASubjectSlug.GAEILGE %}
    - Capture the prescribed texts under `evidence_link` (Irish-language titles)
    - LO codes use prefix `LC-GAEL-LO-NNN` (LC) or `JC-GAEL-LO-NNN` (JC)
    {% elif subject == NCCASubjectSlug.COMPUTER_SCIENCE %}
    - Topics span Algorithms, Data, Networks, Programming, Systems
    - LO codes use prefix `LC-COMP-LO-NNN` (LC) or `JC-COMP-LO-NNN` (JC)
    {% elif subject == NCCASubjectSlug.APPLIED_MATHEMATICS %}
    - Topics: Statistics, Mechanics, Dynamics, Probability
    - LO codes use prefix `LC-APM-LO-NNN`
    {% elif subject == NCCASubjectSlug.HISTORY %}
    - Topics span Early Modern Ireland (1494-1815), Modern Ireland (1815-1989), Contemporary World (1945-present)
    - LO codes use prefix `LC-HIST-LO-NNN` (LC) or `JC-HIST-LO-NNN` (JC)
    - Capture source-handling skills in the marking-scheme points
    - Note the document-based research report under `marking_scheme_points`
    {% elif subject == NCCASubjectSlug.FRENCH %}
    - Capture the prescribed texts (literary extracts, films) under `evidence_link`
    - LO codes use prefix `LC-FREN-LO-NNN`
    - Note the 4 language skills (reading, writing, listening, speaking) under `marking_scheme_points`
    {% elif subject == NCCASubjectSlug.BUSINESS %}
    - Topics span People in Business, Enterprise, Managing 1, Managing 2, Business in Action, Skills
    - LO codes use prefix `LC-BUS-LO-NNN`
    - Capture case studies under `marking_scheme_points`
    - Include the applied business question
    {% elif subject == NCCASubjectSlug.ACCOUNTING %}
    - Topics span Financial Accounting, Management Accounting, Finance, Taxation, Auditing
    - LO codes use prefix `LC-ACCT-LO-NNN`
    - Capture formulas (ratios, NPV, IRR) under `marking_scheme_points`
    {% elif subject == NCCASubjectSlug.ART %}
    - Topics span Core (drawing + appreciation) + 3 specialisms (painting, sculpture, graphic design)
    - LO codes use prefix `LC-ART-LO-NNN`
    - Note the practical course work (50%) under `marking_scheme_points`
    {% elif subject == NCCASubjectSlug.MUSIC %}
    - Topics span Composition, Performance, Listening, Music Technology
    - LO codes use prefix `LC-MUS-LO-NNN`
    - Capture the prescribed works (Bach, Mozart, Beatles, etc.) under `evidence_link`
    - Note the 3 components (performance 50% + composition 25% + listening 25%) under `marking_scheme_points`
    {% elif subject == NCCASubjectSlug.SCIENCE %}
    - Topics span the 4 NCCA JC science strands: Nature of Science, Physical World, Biological World, Chemical World
    - LO codes use prefix `JC-SCI-LO-NNN`
    - Capture diagrams (apparatus, cell structure) under `evidence_link`
    - Note the mandatory practical activities (CBA 1 + CBA 2) under `marking_scheme_points`
    {% elif subject == NCCASubjectSlug.IRISH_HISTORY %}
    - Topics: Early Modern Ireland, Modern Ireland, Contemporary World (JC level)
    - LO codes use prefix `JC-HIST-LO-NNN`
    {% elif subject == NCCASubjectSlug.CSPE %}
    - Topics: Citizenship, Human Rights, Sustainable Development, Media Literacy
    - LO codes use prefix `JC-CSPE-LO-NNN`
    - Capture the action project under `marking_scheme_points`
    {% elif subject == NCCASubjectSlug.SPHE %}
    - Topics: Mental Health, Relationships & Sexuality, Substance Use, Physical Activity, Nutrition
    - LO codes use prefix `JC-SPHE-LO-NNN`
    {% endif %}

    Stage-specific guidance:
    {% if stage == QuestPackStage.JC %}
    - Items are designed for Junior Cycle (ages 12-15)
    - CBA (Classroom-Based Assessment) items may appear for Sciences + CSPE
    - LO codes use `JC-<SUBJECT>-LO-NNN`
    {% elif stage == QuestPackStage.LC_FL %}
    - Items are designed for Leaving Certificate Foundation Level (less advanced)
    - LO codes use `LC-<SUBJECT>-FL-NNN`
    {% elif stage == QuestPackStage.LC_OL %}
    - Items are designed for Leaving Certificate Ordinary Level
    - LO codes use `LC-<SUBJECT>-OL-NNN`
    {% elif stage == QuestPackStage.LC_HL %}
    - Items are designed for Leaving Certificate Higher Level (most advanced)
    - LO codes use `LC-<SUBJECT>-HL-NNN`
    {% elif stage == QuestPackStage.GCSE %}
    - Items are designed for GCSE (England, ages 14-16)
    - LO codes use `GCSE-<SUBJECT>-LO-NNN`
    {% elif stage == QuestPackStage.AS_LEVEL %}
    - Items are designed for AS-Level (England)
    - LO codes use `AS-<SUBJECT>-LO-NNN`
    {% elif stage == QuestPackStage.A_LEVEL %}
    - Items are designed for A-Level (England, ages 16-18)
    - LO codes use `AL-<SUBJECT>-LO-NNN`
    {% endif %}

    Language-specific guidance:
    {% if language == QuestPackLanguage.EN %}
    - All user-facing text is English (text_ga is null for all items)
    {% elif language == QuestPackLanguage.GA %}
    - All user-facing text is Irish (text_en is null for all items)
    {% elif language == QuestPackLanguage.EN_AND_GA %}
    - Every user-facing field is bilingual (text_en + text_ga both populated)
    {% endif %}

    SYLLABUS EXTRACT:
    {{ syllabus_extract }}

    LO CODES (use these exact codes):
    {% for code in lo_codes %}
    - {{ code }}
    {% endfor %}

    {{ ctx.output_format }}
  "#
}

function GenerateSubjectFormativeItem(
  syllabus_extract: string,
  subject: NCCASubjectSlug,
  stage: QuestPackStage,
  language: QuestPackLanguage,
  lo_code: string,
  difficulty: QuestPackDifficulty
) -> QuestPackFormativeItem {
  client BIEPV3Extract
  prompt #"
    {{ _.role("user") }}
    Generate a single formative assessment item for NCCA LO code `{{ lo_code }}` in subject `{{ subject }}` at stage `{{ stage }}` with difficulty `{{ difficulty }}`.

    The item MUST have:
    - A clear prompt (3-6 sentences)
    - An expected response (the model answer)
    - 3-5 marking-scheme points (the grading criteria)
    - An item_type that matches the subject + difficulty
    - An evidence_link to the source NCCA PDF page
    - Bilingual fields if language = EN_AND_GA

    {{ ctx.output_format }}
  "#
}

function ScoreSubjectFormativeResponse(
  item: QuestPackFormativeItem,
  student_response: string,
  subject: NCCASubjectSlug
) -> QuestPackScore {
  client BIEPV3ExtractStrong
  prompt #"
    {{ _.role("user") }}
    Score the student response below against the formative item.

    Item: {{ item.prompt }}
    Expected response: {{ item.expected_response }}
    Marking-scheme points: {{ item.marking_scheme_points }}

    Student response:
    {{ student_response }}

    Return a structured score with:
    - overall_score (0.0 - 1.0)
    - per_criterion_scores (one per marking-scheme point)
    - feedback_text (2-3 sentences)
    - next_steps (1-2 sentence recommendation)

    {{ ctx.output_format }}
  "#
}

// ============================================================================
// The canonical quest pack + item + score types
// ============================================================================

class QuestPackFormativeItem {
  item_id string
  lo_code string @description("The NCCA / awarding-body LO code (matches /LC-.../-LO-\d+/)")
  subject NCCASubjectSlug
  stage QuestPackStage
  language QuestPackLanguage
  difficulty QuestPackDifficulty
  item_type QuestPackItemType
  prompt QuestPackBilingualText
  expected_response QuestPackBilingualText
  marking_scheme_points QuestPackBilingualText[]
  evidence_link QuestPackEvidenceLink?
  feedback_channel QuestPackFeedbackChannel
}

class SubjectQuestPack {
  pack_id string
  subject NCCASubjectSlug
  stage QuestPackStage
  language QuestPackLanguage
  title string
  description string
  items QuestPackFormativeItem[]
  total_marks int
  estimated_duration_minutes int
}

class QuestPackScore {
  item_id string
  overall_score float @description("0.0 - 1.0")
  per_criterion_scores float[]
  feedback_text string
  next_steps string
}

// ============================================================================
// BAML test blocks (per the @assert requirement in this change)
// ============================================================================

test qpack_lc_lo_code_matches {
  functions [GenerateSubjectQuestPack]
  args {
    syllabus_extract "Sample syllabus extract"
    subject NCCASubjectSlug.MATHEMATICS
    stage QuestPackStage.LC_HL
    language QuestPackLanguage.EN
    lo_codes ["LC-MATH-LO-001", "LC-MATH-LO-002"]
  }
}

test qpack_jc_lo_code_matches {
  functions [GenerateSubjectQuestPack]
  args {
    syllabus_extract "Sample JC syllabus"
    subject NCCASubjectSlug.SCIENCE
    stage QuestPackStage.JC
    language QuestPackLanguage.EN_AND_GA
    lo_codes ["JC-SCI-LO-001", "JC-SCI-LO-002"]
  }
}

test qpack_gcse_lo_code_matches {
  functions [GenerateSubjectQuestPack]
  args {
    syllabus_extract "Sample GCSE syllabus"
    subject NCCASubjectSlug.MATHEMATICS
    stage QuestPackStage.GCSE
    language QuestPackLanguage.EN
    lo_codes ["GCSE-MATH-LO-001", "GCSE-MATH-LO-002"]
  }
}

test qpack_alevel_lo_code_matches {
  functions [GenerateSubjectQuestPack]
  args {
    syllabus_extract "Sample A-Level syllabus"
    subject NCCASubjectSlug.MATHEMATICS
    stage QuestPackStage.A_LEVEL
    language QuestPackLanguage.EN
    lo_codes ["AL-MATH-LO-001", "AL-MATH-LO-002"]
  }
}
