// Real BAML extraction prompts for ALL 14 LC subjects.
// Per the 2026-08-10-baml-extraction-completion-v1 change +
// the 2026-08-13-web-monorepo-consolidation-and-agent-integration-v1 change (Phase 1).
//
// Replaces the "Auto-generated extraction prompt" stub with subject-specific
// prompts for the 14 LC subjects: mathematics, applied_mathematics, chemistry,
// physics, biology, geography, english, gaeilge, french, history, business,
// accounting, art, music, computer_science. Each follows the canonical
// `{{ _.role("user") }}` + `{{ ctx.output_format }}` marker pattern.
//
// The SubjectArea enum below covers ALL 46 subjects across the 4 stages:
// - 14 LC (Ireland Leaving Certificate)
// - 8 JC (Ireland Junior Cycle)
// - 9 GCSE (England General Certificate of Secondary Education)
// - 15 A-Level (England GCE Advanced Level)

function ExtractCurriculumSyllabus(text: string, subject: string) -> CurriculumSyllabus {
  client MiniMaxM3Client
  prompt #"
    {{ _.role("user") }}
    You are an expert Irish Leaving Certificate syllabus extractor for the subject `{{ subject }}`.

    Extract the canonical NCCA structure from the syllabus text below.

    For each topic, capture:
    - `code`: NCCA LO code (e.g. "LC-CHEM-LO-023" for chemistry, "LC-MATH-LO-001" for maths)
    - `title`: the topic title (verbatim from the syllabus)
    - `learning_outcomes`: array of {code, text, blooms_level (remember|understand|apply|analyse|evaluate|create)}

    Also extract:
    - `strands`: array of {name, topics} — the major syllabus strands
    - `assessment_objectives`: array of the AO codes + descriptions
    - `key_competencies`: array of the 5 NCCA Key Competencies (Information Processing, Communicating, Working with Others, Personal Effectiveness, Critical & Creative Thinking)

    Subject-specific guidance:
    {% if subject == "chemistry" %}
    - Topics follow the 4 chemistry strands: Atomic Structure, Chemical Bonding, Stoichiometry, etc.
    - LO codes use prefix "LC-CHEM-LO-NNN"
    {% elif subject == "mathematics" %}
    - Topics are organised by the 5 syllabus strands (Statistics & Probability, Geometry & Trigonometry, Number, Algebra, Functions)
    - LO codes use prefix "LC-MATH-LO-NNN"
    - Capture all formula references as a separate `formulas` array
    {% elif subject == "geography" %}
    - Topics span Physical Geography, Regional Geography, Human Environment
    - LO codes use prefix "LC-GEOG-LO-NNN"
    {% elif subject == "english" %}
    - Capture the prescribed texts (poetry, prose, drama) under `prescribed_texts`
    - LO codes use prefix "LC-ENGL-LO-NNN"
    {% elif subject == "gaeilge" %}
    - Capture the prescribed texts under `prescribed_texts` (Irish-language titles)
    - LO codes use prefix "LC-GAEL-LO-NNN"
    {% elif subject == "computer_science" %}
    - Topics span Algorithms, Data, Networks, Programming, Systems
    - LO codes use prefix "LC-COMP-LO-NNN"
    {% elif subject == "applied_mathematics" %}
    - Topics: Statistics, Mechanics, Dynamics, Probability
    - LO codes use prefix "LC-APM-LO-NNN"
    {% elif subject == "physics" %}
    - Topics span Mechanics, Waves, Light, Electricity & Magnetism, Modern Physics, Particle Physics
    - LO codes use prefix "LC-PHYS-LO-NNN"
    - Capture all formula references as a separate `formulas` array
    - Include SI units + significant figures conventions
    {% elif subject == "biology" %}
    - Topics span the 3 units: The Study of Life, The Cell, The Organism
    - LO codes use prefix "LC-BIO-LO-NNN"
    - Capture diagrams (cell structure, organ systems, ecosystems) under `prescribed_texts`
    - Note practical activities (mandatory 30%) under `assessment_objectives`
    {% elif subject == "history" %}
    - Topics span Early Modern Ireland (1494-1815), Modern Ireland (1815-1989), Contemporary World (1945-present)
    - LO codes use prefix "LC-HIST-LO-NNN"
    - Capture source-handling skills under `key_competencies`
    - Note the document-based research report under `assessment_objectives`
    {% elif subject == "french" %}
    - Capture the prescribed texts (literary extracts, films) under `prescribed_texts`
    - LO codes use prefix "LC-FREN-LO-NNN"
    - Note the 4 language skills (reading, writing, listening, speaking) under `assessment_objectives`
    - Include Gaélisation na bhFréamhacha for cultural context
    {% elif subject == "business" %}
    - Topics span People in Business, Enterprise, Managing 1, Managing 2, Business in Action, Skills
    - LO codes use prefix "LC-BUS-LO-NNN"
    - Capture case studies under `key_competencies`
    - Include the applied business question under `assessment_objectives`
    {% elif subject == "accounting" %}
    - Topics span Financial Accounting, Management Accounting, Finance, Taxation, Auditing
    - LO codes use prefix "LC-ACCT-LO-NNN"
    - Capture formulas (ratios, NPV, IRR) under `formulas`
    - Note the structured questions under `assessment_objectives`
    {% elif subject == "art" %}
    - Topics span Core (drawing + appreciation) + 3 specialisms (painting, sculpture, graphic design)
    - LO codes use prefix "LC-ART-LO-NNN"
    - Capture the prescribed visits (gallery + museum) under `key_competencies`
    - Note the practical course work (50%) under `assessment_objectives`
    {% elif subject == "music" %}
    - Topics span Composition, Performance, Listening, Music Technology
    - LO codes use prefix "LC-MUS-LO-NNN"
    - Capture the prescribed works (Bach, Mozart, Beatles, etc.) under `prescribed_texts`
    - Note the 3 components (performance 50% + composition 25% + listening 25%) under `assessment_objectives`
    {% endif %}

    {{ ctx.output_format }}

    SYLLABUS TEXT:
    {{ text }}
  "#
}

function ExtractExamPaperLayout(text: string, subject: string) -> ExamPaperLayout {
  client MiniMaxM3Client
  prompt #"
    {{ _.role("user") }}
    You are an expert Leaving Certificate exam paper layout extractor for `{{ subject }}`.

    Extract from the exam paper text:
    - `exam_year`: 4-digit year (e.g. 2024)
    - `exam_level`: "Higher" | "Ordinary" | "Foundation"
    - `paper_number`: 1 | 2 | 3
    - `total_marks`: integer
    - `sections`: array of {label, marks, questions: [{question_number, marks, instruction, sub_questions: [{label, marks}]}]}
    - `duration_minutes`: integer (typically 180 or 240)
    - `examiner_notes`: array of strings

    Subject-specific guidance:
    {% if subject == "chemistry" %}
    - 3 sections typically: Section A (short Qs), Section B (experimental), Section C (long Qs)
    {% elif subject == "mathematics" %}
    - 2 papers: Paper 1 (calculators allowed, 150 marks), Paper 2 (same)
    - Each paper has Section A + Section B
    {% elif subject == "english" %}
    - 2 papers: Paper 1 (comprehension + composition), Paper 2 (single text study)
    - Section I + Section II in each
    {% elif subject == "physics" %}
    - 2 papers: Paper 1 (150 marks), Paper 2 (150 marks)
    - Section A: 4 short questions × 25 marks = 100 marks (obligatory)
    - Section B: 5 questions out of 6 × 10 marks = 50 marks
    - 10 experiments from the syllabus must be known
    {% elif subject == "biology" %}
    - 2 papers: Paper 1 (150 marks), Paper 2 (150 marks)
    - Section A: 5 short questions × 30 marks = 150 marks (obligatory)
    - Section B: 3 questions out of 6 × 50 marks = 150 marks
    - 22 mandatory practical activities
    {% elif subject == "geography" %}
    - 1 paper (300 marks), 3 sections
    - Section 1: Short questions (answer 10 from 12)
    - Section 2: Physical/Regional geography topics
    - Section 3: Human/Regional geography topics
    {% elif subject == "gaeilge" %}
    - 2 papers: Paper 1 (comprehension + composition), Paper 2 (literature)
    - Béaltriail (oral exam) is separate + worth 40% of total
    {% elif subject == "computer_science" %}
    - 2 papers: Paper 1 (Short questions), Paper 2 (Long questions)
    - No coursework
    {% elif subject == "applied_mathematics" %}
    - 2 papers, each 150 marks
    - 10 short questions (Section A) + 6 long questions (Section B, choose 5)
    {% elif subject == "french" %}
    - 2 papers: Paper 1 (listening + reading + writing), Paper 2 (comprehension + written production)
    - Oral exam (worth 25%) separate from written papers
    {% elif subject == "history" %}
    - 1 paper (300 marks), 3 sections
    - Section 1: Document-based question (100 marks)
    - Section 2: Three essays from Ireland topic (100 marks)
    - Section 3: Three essays from European + World topic (100 marks)
    {% elif subject == "business" %}
    - 1 paper (400 marks), 7 sections
    - Absent students apply for the Listening Comprehension (LC) day
    - Applied Business Question (ABQ) is a mandatory project
    {% elif subject == "accounting" %}
    - 1 paper (400 marks), 2 sections
    - Section 1: Financial Accounting (250 marks)
    - Section 2: Management Accounting + Finance (150 marks)
    {% elif subject == "art" %}
    - 2 papers: Paper 1 (Imaginative Composition), Paper 2 (Critical Engagement)
    - Coursework is 50% of total (practical + research)
    {% elif subject == "music" %}
    - 1 paper (400 marks), 4 sections
    - Performing (50%): Core + 3 specialist pieces
    - Composing (25%): 3 compositions + 1 IPC
    - Listening (25%): 4 set works + unfamiliar
    {% endif %}

    {{ ctx.output_format }}

    EXAM PAPER TEXT:
    {{ text }}
  "#
}

function ExtractMarkingSchemeGuideline(text: string, subject: string) -> MarkingSchemeGuideline {
  client MiniMaxM3Client
  prompt #"
    {{ _.role("user") }}
    You are an expert Leaving Certificate marking scheme extractor for `{{ subject }}`.

    Extract from the marking scheme text:
    - `exam_year`: 4-digit year
    - `marking_instructions`: array of {section, general_notes, common_mistakes}
    - `grade_boundaries`: array of {grade, percentage_lower_bound}
    - `question_specific_schemes`: array of {question_number, parts: [{label, scheme: string, marks: integer}]}
    - `distribution_of_marks`: dict of {cognitive_level, percentage}

    Subject-specific guidance:
    {% if subject == "chemistry" %}
    - Grade boundaries are typically 90/80/70/60/50/40/30 for H1-H7/O1-O8
    - Section A usually has 10 questions × 10 marks
    {% elif subject == "mathematics" %}
    - 2 papers, each 150 marks
    - Grade boundaries include F1-F3 (failures) below 30%
    {% elif subject == "english" %}
    - Grading is more qualitative for composition (60-70% on ideas + structure)
    - Comprehension is quantitative
    {% elif subject == "physics" %}
    - Two papers each 150 marks, total 300 marks
    - Grade boundaries: H1 ≥ 90%, H7 ≥ 30%, O1 ≥ 60%, O8 ≥ 30%
    - 10 prescribed experiments must be demonstrable
    {% elif subject == "biology" %}
    - Two papers each 150 marks, total 300 marks
    - Grade boundaries: H1 ≥ 90%, H7 ≥ 30%, O1 ≥ 60%, O8 ≥ 30%
    - 22 mandatory practical activities must be recorded
    {% elif subject == "geography" %}
    - Single paper 300 marks
    - 4 separate questions to be answered (out of 12)
    - Grade boundaries: H1 ≥ 90%, H7 ≥ 30%, O1 ≥ 60%, O8 ≥ 30%
    {% elif subject == "gaeilge" %}
    - 3 components: paistí (Béaltriail 40%), scríbhneoireacht (30%), léamhthuiscint (30%)
    - Grade boundaries: H1 ≥ 90%, H7 ≥ 30%, O1 ≥ 60%, O8 ≥ 30%
    {% elif subject == "computer_science" %}
    - Two papers each 150 marks, total 300 marks
    - 8 short questions (Section A) + 6 long questions (Section B)
    {% elif subject == "applied_mathematics" %}
    - Two papers each 150 marks, total 300 marks
    - 10 short questions (Section A) + 6 long questions (Section B, choose 5)
    {% elif subject == "french" %}
    - 3 components: Production écrite (15%), Production orale (25%), Compréhension écrite (35%), Compréhension orale (25%)
    - Grade boundaries: H1 ≥ 90%, H7 ≥ 30%, O1 ≥ 60%, O8 ≥ 30%
    {% elif subject == "history" %}
    - Single paper 300 marks
    - Document-based research report (200 marks) + 3 essays (100 marks)
    - Grade boundaries: H1 ≥ 90%, H7 ≥ 30%, O1 ≥ 60%, O8 ≥ 30%
    {% elif subject == "business" %}
    - Single paper 400 marks
    - Applied Business Question (ABQ) is mandatory (60% of final grade)
    - 3 short questions (Section A) + 4 long questions (Section B)
    {% elif subject == "accounting" %}
    - Single paper 400 marks
    - Section 1: 6 questions (choose 5) | Section 2: 6 questions (choose 4)
    - Grade boundaries: H1 ≥ 90%, H7 ≥ 30%, O1 ≥ 60%, O8 ≥ 30%
    {% elif subject == "art" %}
    - 2 papers: Paper 1 (Imaginative Composition), Paper 2 (Critical Engagement)
    - Coursework is 50% of total (practical + research)
    - Grade boundaries: H1 ≥ 90%, H7 ≥ 30%, O1 ≥ 60%, O8 ≥ 30%
    {% elif subject == "music" %}
    - 1 paper (400 marks), 4 sections
    - Performing (50%): Core + 3 specialist pieces
    - Composing (25%): 3 compositions + 1 IPC
    - Listening (25%): 4 set works + unfamiliar
    {% endif %}

    {{ ctx.output_format }}

    MARKING SCHEME TEXT:
    {{ text }}
  "#
}

function ExtractSyllabusDiagram(text: string, subject: string) -> SyllabusDiagram {
  client MiniMaxM3Client
  prompt #"
    {{ _.role("user") }}
    You are an expert at extracting diagrams from `{{ subject }}` Leaving Certificate syllabi.

    Extract from the syllabus text:
    - `figure_id`: identifier (e.g. "Figure 1.2" or "Diagram 2.3")
    - `caption`: the figure's caption/description
    - `diagram_type`: "molecular_structure" | "circuit" | "graph" | "process_flow" | "anatomical" | "geological_cross_section" | "other"
    - `associated_topic_code`: the NCCA LO code the diagram supports
    - `complexity`: "simple" | "moderate" | "complex"

    Subject-specific guidance:
    {% if subject == "chemistry" %}
    - Most diagrams are molecular structures or reaction mechanisms
    {% elif subject == "geography" %}
    - Diagrams are typically geological cross-sections, climate graphs, or population pyramids
    {% elif subject == "computer_science" %}
    - Diagrams are flowcharts, network topologies, or sorting algorithm visualisations
    {% elif subject == "physics" %}
    - Diagrams are typically circuit diagrams, ray diagrams, force diagrams, field line diagrams
    {% elif subject == "biology" %}
    - Diagrams are typically cell structure, organ systems, food webs, population pyramids, genetic crosses
    {% elif subject == "mathematics" %}
    - Diagrams are typically graphs, Venn diagrams, geometric diagrams, statistical distributions
    {% elif subject == "english" %}
    - Diagrams are typically character maps, narrative structure diagrams, textual evidence tables
    {% elif subject == "gaeilge" %}
    - Diagrams are typically scéim filíochta, léaráidí saolré, sceitse dílleachta
    {% elif subject == "applied_mathematics" %}
    - Diagrams are typically cost-revenue graphs, probability trees, time series, stress-strain curves
    {% elif subject == "french" %}
    - Diagrams are typically binary trees, syntactic structures, register shift diagrams
    {% elif subject == "history" %}
    - Diagrams are typically timelines, source matrices, cause-effect diagrams, demographic pyramids
    {% elif subject == "business" %}
    - Diagrams are typically break-even charts, cash flow diagrams, SWOT analysis diagrams, org charts
    {% elif subject == "accounting" %}
    - Diagrams are typically accounts flow, financial statement structure diagrams, ratio analysis charts
    {% elif subject == "art" %}
    - Diagrams are typically composition studies, perspective diagrams, art history timeline diagrams
    {% elif subject == "music" %}
    - Diagrams are typically form and structure diagrams, harmonic analysis diagrams, set work timeline diagrams
    {% endif %}

    {{ ctx.output_format }}

    SYLLABUS TEXT:
    {{ text }}
  "#
}

function ExtractCrossLinguisticConcept(en_text: string, ga_text: string) -> CrossLinguisticConcept {
  client MiniMaxM3Client
  prompt #"
    {{ _.role("user") }}
    You are an expert bilingual (English ↔ Irish) curriculum concept matcher.

    Given parallel English + Irish syllabus text, extract:
    - `en_concept`: {term, definition, ncca_lo_code}
    - `ga_concept`: {term, definition, ncca_lo_code}
    - `equivalence_score`: 0.0-1.0 (how well the concepts match across languages)
    - `cultural_notes`: any cultural context that differs between EN and GA treatments

    Example:
    {
      "en_concept": {"term": "Atomic Structure", "definition": "Composition of atoms", "ncca_lo_code": "LC-CHEM-LO-001"},
      "ga_concept": {"term": "Struchtúr Adamhach", "definition": "Comhdhéanamh adaimh", "ncca_lo_code": "LC-CEIM-LO-001"},
      "equivalence_score": 0.92,
      "cultural_notes": "GA term uses the older spelling 'Struchtúr' vs modern 'Struchtúr'"
    }

    {{ ctx.output_format }}

    ENGLISH TEXT:
    {{ en_text }}

    IRISH TEXT:
    {{ ga_text }}
  "#
}

function ExtractBilingualLearningOutcome(en_text: string, ga_text: string) -> BilingualLearningOutcome {
  client GaeilgeLCClient
  prompt #"
    {{ _.role("user") }}
    You are an expert bilingual (English ↔ Irish) Leaving Certificate LO pair extractor.

    Given parallel English + Irish syllabus text, extract paired LOs:
    - `en_lo_id`: English NCCA LO code (e.g. "LC-CHEM-LO-023")
    - `ga_lo_id`: Irish NCCA LO code (e.g. "LC-CEIM-LO-023")
    - `confidence`: 0.0-1.0 (pairing confidence)
    - `source_pairs`: array of {en_segment, ga_segment} — matching text segments

    Note: The Irish LO code uses different prefix (CEIM for Chemistry, MATA for Maths, TÍR for Geography, etc.)

    {{ ctx.output_format }}

    ENGLISH TEXT:
    {{ en_text }}

    IRISH TEXT:
    {{ ga_text }}
  "#
}

function ExtractCrossLinguisticGA(ga_text: string) -> CrossLinguisticConcept {
  client GaeilgeLCClient
  prompt #"
    {{ _.role("user") }}
    You are an expert at extracting structured concepts from Irish-language syllabus text.

    Given the GA text below, extract:
    - `ga_concept`: {term, definition, ncca_lo_code}
    - `related_en_terms`: array of English equivalents (if identifiable)

    Example:
    {
      "ga_concept": {"term": "Cothromaíocht Cheimiceach", "definition": "Staid ina bhfuil rátaí na frithghníomhanna ar aghaidh agus ar gcúl comhionann", "ncca_lo_code": "LC-CEIM-LO-045"},
      "related_en_terms": ["Chemical Equilibrium"]
    }

    {{ ctx.output_format }}

    IRISH TEXT:
    {{ ga_text }}
  "#
}

class CurriculumSyllabus {
  subject string
  language SyllabusLanguage
  stage NCCAStage
  source_pdf string
  // Nullable (2026-08-06 token-plan-apis change, Phase 2b): the model
  // cannot know the PDF page count from extracted text alone. Matches
  // the already-nullable LCSyllabus.source_pages in
  // british_isles/_cross/unified_extraction.baml.
  source_pages int?

  // Document content
  module_topics ModuleTopic[]
  total_learning_outcomes int

  // Cross-cutting
  cross_curricular string[]
  assessment_objectives string[]

  // Lineage provenance (R28). Composed from
  // `lc_extraction/_shared/lineage_trace.baml`. The Python caller (Dagster
  // asset + Conway envelope wrapper) populates this at write time —
  // the BAML function itself doesn't need to fill it in for its own
  // prompt, but downstream consumers can rely on it being present.
  lineage LineageTrace?
}

// ============================================================================
// BAML function — the canonical extractor (BIEP v1)
// ============================================================================
// Replaces the legacy `b.ExtractLeavingCertSyllabus` from
// `baml/education/pdfs/leaving_cert_syllabus.baml`.
//
// Returns the canonical `SyllabusDocument` Pydantic class.
// NCCA publishes the syllabus for each LC subject as a single combined PDF
// (Higher + Ordinary + Foundation sections in one document). The
// `language` enum distinguishes EN / GA / bilingual PDFs.

function ExtractCurriculumSyllabus(
  pdf_text: string,
  subject: string?,
  language: string?,
) -> SyllabusDocument {  client ExtractEn
  prompt #"
    You are an expert at reading official NCCA (National Council for
    Curriculum and Assessment) Irish Leaving Certificate syllabus
    documents and extracting their structure with complete fidelity —
    every fact below MUST be grounded in the PDF text given; never invent
    a module, learning outcome, or hour count that isn't actually present.

    Subject: {{ subject }}
    Language of this PDF: {{ language }}

    From the syllabus text below, extract:
    - subject: the subject slug (e.g. 'chemistry', 'mathematics')
    - language: EN, GA, or EN_AND_GA depending on what you observe in the text
    - stage: JC, LC_OL, LC_HL, or LC_FDN — NCCA syllabi usually cover
      multiple levels in one document; pick the stage that best matches
      the section you are reading, or LC_HL if the document does not
      distinguish levels
    - source_pdf: leave as an empty string if not derivable from the text;
      the Python caller fills this in from the actual file path
    - module_topics: every distinct module/unit/strand you can find, each with:
      - module_id (a short stable slug, e.g. 'M1', derived from the
        syllabus's own numbering if present)
      - name_en / name_ga (name_ga only if the Irish-language term
        appears in the text)
      - type: CORE, OPTIONAL, SPECIALISM, PRACTICAL, or ASSESSMENT,
        based on how the syllabus itself describes the module
      - learning_outcomes: the exact (or lightly normalised) learning
        outcome statements listed under that module — do not paraphrase
        away specific verbs ('describe', 'derive', 'evaluate') since
        they are pedagogically load-bearing
      - estimated_hours: only if the syllabus states a number of hours
        or class periods for the module; otherwise omit
    - total_learning_outcomes: the count of all learning_outcomes across
      all module_topics
    - cross_curricular: any explicitly named links to other subjects or
      cross-curricular themes (e.g. literacy, numeracy, key competencies)
    - assessment_objectives: the syllabus's own stated assessment
      objectives / aims for how students will be examined

    If a field has no support in the text, leave it empty rather than
    fabricating content — an empty list is a correct and expected answer
    for a syllabus section that doesn't mention cross-curricular links.

    Syllabus PDF text:
    {{ pdf_text }}

    {{ _.role("user") }}
    {{ ctx.output_format }}
  "#
}

// ============================================================================
// LineageTrace composer helper
// ============================================================================
// Helper that downstream Python callers (Dagster asset + DLT destination
// wrapper) invoke to populate the `lineage` field of every row emitted by
// `ExtractCurriculumSyllabus`. Centralised here so the contract is defined
// next to the consumer.
//
// Per openspec R28 (BAML LineageTrace extension).

// ============================================================================
// Backward-compatibility alias (BIEP v1 — Phase 1.3 migration)
// ============================================================================
// The 8 per-subject DLT sources historically called
// `b.ExtractLeavingCertSyllabus` from `baml/education/pdfs/leaving_cert_syllabus.baml`.
// That legacy function is now `## REMOVED` (per the 1.2.1 task) and
// replaced by this canonical `ExtractCurriculumSyllabus`. Any caller that
// still passes legacy kwargs will be transparently routed here.
