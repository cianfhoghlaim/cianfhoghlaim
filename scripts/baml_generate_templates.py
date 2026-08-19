#!/usr/bin/env python3
"""Generate the 18 domain-specific BAML templates for Phase 3.

Per the 2026-12-XX-mega-3d-baml-quality-v1 change (Phase 3).

The script writes 18 template files to baml_src/_shared/templates/.

Usage:
    python scripts/baml_generate_templates.py            # Generate
    python scripts/baml_generate_templates.py --dry-run  # Preview
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TEMPLATES_DIR = REPO_ROOT / "baml_src" / "_shared" / "templates"


HEADER = """// BAML template: {title}
//
// Per the 2026-12-XX-mega-3d-baml-quality-v1 change (Phase 3:
// BAML bulk-quality). Replaces the {count} stub prompts in
// `{parent_dir}/` with a single canonical extractor.
//
// Each stub function in the parent dir routes through this
// template via `baml_bulk_replace_stubs.py`. The template is
// shared (not duplicated per function) so a single improvement
// benefits all {count} extractors.
//
// Re-gen: `python scripts/baml_generate_templates.py`
// Re-apply: `python scripts/baml_bulk_replace_stubs.py`

"""


# Each template entry: (filename, title, parent_dir, stub_count, role, source_type,
#                        fields, branching, extra_guidance)
TEMPLATES: list[dict] = [
    {
        "filename": "processing_gemini_report.baml",
        "title": "Gemini Deep Research Report Extractor",
        "parent_dir": "processing/gemini_deep_research",
        "count": 10,
        "role": "expert at extracting structured metadata from a Gemini deep research report PDF",
        "source_type": "PDF text (gemini_deep_research_*.pdf)",
        "fields": [
            ("title", "the report title"),
            ("summary", "2-3 sentence executive summary"),
            ("findings", "list of key findings with section headings"),
            ("citations", "list of cited URLs with section context"),
            ("methodology", "description of the research methodology used"),
        ],
        "branching": "",
        "extra_guidance": "The Gemini reports are typically 20-50 page PDFs with rich citation networks. Preserve citation context (page number + section).",
    },
    {
        "filename": "processing_author_archive.baml",
        "title": "Author Archive Extractor",
        "parent_dir": "processing/author_archive.baml",
        "count": 10,
        "role": "expert at extracting author/creator metadata from an archival document",
        "source_type": "PDF text + filename",
        "fields": [
            ("author_name", "full name of the primary author/creator"),
            ("author_role", "their role/title at time of creation"),
            ("organization", "the affiliated organization (if any)"),
            ("publication_year", "ISO year of publication or creation"),
            ("archive_collection", "the canonical archive collection name"),
            ("shelfmark", "the canonical shelfmark / call number"),
        ],
        "branching": "",
        "extra_guidance": "The author archive includes a mix of academics, politicians, and educators. Use the document content (not the filename) to determine role and organization.",
    },
    {
        "filename": "processing_style_transfer.baml",
        "title": "Style Transfer Spec Extractor",
        "parent_dir": "processing/style_transfer.baml",
        "count": 7,
        "role": "expert at generating a style transfer specification from a reference prompt",
        "source_type": "free-form reference prompt text",
        "fields": [
            ("style_name", "the canonical style name (e.g. 'ukiyo-e', 'watercolor')"),
            ("palette", "list of hex colour codes for the style"),
            ("line_work", "description of the line work characteristics"),
            ("era", "the era or time period the style evokes"),
            ("subject_matter", "the typical subject matter for this style"),
        ],
        "branching": "",
        "extra_guidance": "The style transfer spec drives a downstream image generation flow. The palette + line_work are the most critical fields.",
    },
    {
        "filename": "processing_game_content.baml",
        "title": "Game Content Extractor",
        "parent_dir": "processing/game_content.baml",
        "count": 6,
        "role": "expert at extracting structured game content from a game design document",
        "source_type": "markdown game design document",
        "fields": [
            ("game_title", "the title of the game"),
            ("mechanics", "list of game mechanics with descriptions"),
            ("levels", "list of levels with difficulty + learning objectives"),
            ("subject_focus", "the canonical subject slug (chemistry, mathematics, etc.)"),
            ("age_range", "the target age range (e.g. '12-15')"),
        ],
        "branching": "",
        "extra_guidance": "The game content is used by the Túatha educational MMO. The age_range + subject_focus drive the cohort matching.",
    },
    {
        "filename": "processing_circular_extraction.baml",
        "title": "Government Circular Extractor",
        "parent_dir": "processing/circular_extraction.baml",
        "count": 6,
        "role": "expert at extracting structured metadata from an Irish government education circular",
        "source_type": "PDF text from gov.ie / Department of Education",
        "fields": [
            ("circular_number", "the canonical circular number (e.g. '0059/2026')"),
            ("issuing_department", "the department that issued the circular"),
            ("issue_date", "ISO 8601 date of issue"),
            ("subject", "the subject of the circular"),
            ("summary", "2-3 sentence executive summary"),
            ("action_required", "what schools/principals are required to do"),
        ],
        "branching": "",
        "extra_guidance": "The circular_number follows the pattern NNNN/YYYY. Cross-link to the affected LC subjects when possible.",
    },
    {
        "filename": "processing_cv_extraction.baml",
        "title": "CV Extractor",
        "parent_dir": "processing/cv_extraction.baml",
        "count": 5,
        "role": "expert at extracting structured CV / resume data from a PDF",
        "source_type": "PDF text from a CV or resume",
        "fields": [
            ("name", "the full name of the candidate"),
            ("email", "primary email address"),
            ("education", "list of education entries (degree, institution, year)"),
            ("experience", "list of work experience entries"),
            ("publications", "list of publications (if present)"),
        ],
        "branching": "",
        "extra_guidance": "The CV is used for portfolio/agent attribution. Preserve the canonical ordering of education + experience entries.",
    },
    {
        "filename": "celtic_tearma.baml",
        "title": "Tearma.ie Terminology Extractor",
        "parent_dir": "celtic/gaois/tearma.baml",
        "count": 26,
        "role": "expert at extracting structured terminology data from Tearma.ie (the Irish National Terminology Database)",
        "source_type": "JSON response or HTML page from tearma.ie",
        "fields": [
            ("term_ga", "the Irish term"),
            ("term_en", "the English term"),
            ("domains", "list of subject domains"),
            ("definitions", "list of term definitions with language tag"),
            ("grammar", "grammatical info (gender, declension, verb form)"),
            ("usage_examples", "list of EN/GA usage examples"),
        ],
        "branching": "{% if language == 'ga' %}\n    - Preserve the full Irish grammar (gender + declension)\n    {% elif language == 'en' %}\n    - The grammar field is optional for English-only terms\n    {% endif %}",
        "extra_guidance": "Tearma.ie is the authoritative Irish terminology source. Cross-reference the term with related Dúchas / Gaois records when the definitions overlap.",
    },
    {
        "filename": "celtic_grammar_patterns.baml",
        "title": "Celtic Grammar Pattern Extractor",
        "parent_dir": "celtic/grammar_patterns.baml",
        "count": 7,
        "role": "expert at extracting Celtic-language grammar patterns from a pedagogical text",
        "source_type": "markdown pedagogical text",
        "fields": [
            ("language", "the Celtic language (ga, cy, gd, br, kw, gv)"),
            ("pattern_name", "the name of the grammar pattern (e.g. 'Irish mutations')"),
            ("examples", "list of example sentences demonstrating the pattern"),
            ("rules", "list of formal rules for the pattern"),
            ("related_patterns", "list of cross-references to related patterns"),
        ],
        "branching": "{% if language == 'ga' %}\n    - Capture the 4 Irish mutations (séimhiú + urú + eclipsis + lenition)\n    {% elif language == 'cy' %}\n    - Capture the Welsh soft + nasal + aspirate mutations\n    {% endif %}",
        "extra_guidance": "Celtic mutations are the most distinctive feature. Always capture the input → output transformation explicitly.",
    },
    {
        "filename": "celtic_curriculum.baml",
        "title": "Celtic Curriculum Extractor",
        "parent_dir": "celtic/curriculum/celtic_curriculum.baml",
        "count": 7,
        "role": "expert at extracting Celtic-language curriculum data from a national curriculum document",
        "source_type": "PDF text from a Celtic-nation curriculum authority",
        "fields": [
            ("language", "the Celtic language"),
            ("stage", "the educational stage (primary, secondary, etc.)"),
            ("learning_outcomes", "list of learning outcomes with codes"),
            ("assessment_objectives", "list of assessment objectives"),
            ("cross_curricular", "cross-subject links"),
        ],
        "branching": "{% if language == 'ga' %}\n    - NCCA LO codes use prefix `JC-GAEL-LO-NNN`\n    {% elif language == 'cy' %}\n    - CBAC (Welsh) LO codes use prefix `CBAC-CYM-LO-NNN`\n    {% endif %}",
        "extra_guidance": "The 6 Celtic languages are: ga (Irish), cy (Welsh), gd (Scottish Gaelic), br (Breton), kw (Cornish), gv (Manx). Each has its own national curriculum authority.",
    },
    {
        "filename": "ireland_lc_stage.baml",
        "title": "Ireland Leaving Cert Stage Extractor",
        "parent_dir": "british_isles/ireland/education/stages/upper_secondary.baml",
        "count": 8,
        "role": "expert Irish Leaving Certificate (Senior Cycle) curriculum extractor for the 14 NCCA LC subjects",
        "source_type": "PDF text from NCCA syllabus documents",
        "fields": [
            ("subject", "the LC subject slug"),
            ("level", "the level (OL, HL, FDN)"),
            ("module_topics", "list of module / strand topics"),
            ("learning_outcomes", "list of LOs with codes (LC-<SUBJ>-LO-NNN)"),
            ("assessment_objectives", "NCCA assessment objectives"),
        ],
        "branching": "{% if subject == 'LCSubjectSlug.MATHEMATICS' %}\n    - Topics follow the 5 syllabus strands\n    - LO codes use prefix `LC-MATH-LO-NNN`\n    {% elif subject == 'LCSubjectSlug.CHEMISTRY' %}\n    - Topics follow the 4 chemistry strands\n    - LO codes use prefix `LC-CHEM-LO-NNN`\n    {% endif %}",
        "extra_guidance": "The LC syllabus structure is well-documented by NCCA. Cross-link LOs to the NCCA published syllabus documents.",
    },
    {
        "filename": "ireland_jc_stage.baml",
        "title": "Ireland Junior Cycle Stage Extractor",
        "parent_dir": "british_isles/ireland/education/stages/junior_cycle.baml",
        "count": 8,
        "role": "expert Irish Junior Cycle (ages 12-15) curriculum extractor for the 8 NCCA JC subjects",
        "source_type": "PDF text from NCCA Junior Cycle specifications",
        "fields": [
            ("subject", "the JC subject slug"),
            ("learning_outcomes", "list of LOs with codes (JC-<SUBJ>-LO-NNN)"),
            ("strand_elements", "list of strand elements"),
            ("cba_objectives", "Classroom-Based Assessment objectives"),
            ("assessment_objectives", "final exam assessment objectives"),
        ],
        "branching": "{% if subject == 'JCSubjectSlug.MATHEMATICS' %}\n    - Topics span Number, Algebra, Functions, Geometry, Statistics\n    - LO codes use prefix `JC-MATH-LO-NNN`\n    {% elif subject == 'JCSubjectSlug.ENGLISH' %}\n    - Capture the prescribed texts under `prescribed_texts`\n    {% endif %}",
        "extra_guidance": "Junior Cycle has a different assessment structure (CBA + final exam) than Leaving Cert. Always capture both the CBA objectives and the final exam objectives.",
    },
    {
        "filename": "ireland_university_module.baml",
        "title": "Ireland University Module Extractor",
        "parent_dir": "british_isles/ireland/education/university",
        "count": 21,
        "role": "expert at extracting University of Galway (or Irish university) module syllabus data from PDF",
        "source_type": "PDF text from a university module descriptor",
        "fields": [
            ("module_code", "the canonical module code (e.g. 'MA216')"),
            ("module_title", "the module title"),
            ("credits", "ECTS credits"),
            ("learning_outcomes", "list of LOs"),
            ("assessment_breakdown", "breakdown of assessment weightings"),
            ("prerequisites", "list of prerequisite modules"),
        ],
        "branching": "",
        "extra_guidance": "University module descriptors follow a common template. The module_code is the canonical identifier (cross-reference with the University of Galway module registry).",
    },
    {
        "filename": "ireland_web_content.baml",
        "title": "Ireland Web Content Extractor",
        "parent_dir": "british_isles/ireland/education/web",
        "count": 18,
        "role": "expert at extracting structured data from Irish education web pages",
        "source_type": "markdown from a scraped web page (NCCA, gov.ie, examinations.ie)",
        "fields": [
            ("title", "the page title"),
            ("publication_date", "ISO 8601 publication date"),
            ("subject_area", "the subject area covered (if any)"),
            ("key_findings", "list of key findings or facts"),
            ("links", "list of related URLs"),
        ],
        "branching": "{% if domain == 'ncca' %}\n    - Cross-link to the canonical NCCA LO code\n    {% elif domain == 'examinations_ie' %}\n    - Capture the chief examiner's report insights\n    {% endif %}",
        "extra_guidance": "The web content extractor handles pages from NCCA, gov.ie, examinations.ie, and Scoilnet. Always preserve the canonical URL.",
    },
    {
        "filename": "isles_marking_scheme.baml",
        "title": "British Isles Marking Scheme Extractor",
        "parent_dir": "british_isles/_shared/marking",
        "count": 6,
        "role": "expert at extracting structured marking scheme guidelines from a British Isles exam marking PDF",
        "source_type": "PDF text from a marking scheme / chief examiner report",
        "fields": [
            ("exam_board", "the exam board (AQA, OCR, Edexcel, NCCA, SQA, CBAC, CCEA)"),
            ("subject", "the subject slug"),
            ("year", "the exam year"),
            ("marking_bands", "list of marking bands with mark ranges"),
            ("common_mistakes", "list of common student mistakes"),
            ("model_answers", "list of model answers for high-mark questions"),
        ],
        "branching": "{% if exam_board == 'AQA' %}\n    - AQA marking bands are 5-level (1-5)\n    {% elif exam_board == 'OCR' %}\n    - OCR marking bands are A-E\n    {% endif %}",
        "extra_guidance": "Marking schemes differ by exam board. Always capture the board-specific band naming convention.",
    },
    {
        "filename": "isles_statistics.baml",
        "title": "British Isles Education Statistics Extractor",
        "parent_dir": "british_isles/_shared/statistics",
        "count": 5,
        "role": "expert at extracting education statistics from a British Isles statistical bulletin",
        "source_type": "PDF text from a government statistics office (CSO, ONS, NRS, NISRA)",
        "fields": [
            ("publication", "the canonical publication name"),
            ("publication_date", "ISO 8601 publication date"),
            ("cohort", "the cohort year(s) covered"),
            ("data_points", "list of data points with year + value + jurisdiction"),
            ("methodology", "link or description of the methodology"),
        ],
        "branching": "{% if jurisdiction == 'ireland' %}\n    - Use CSO.ie source URL pattern\n    {% elif jurisdiction == 'england' %}\n    - Use explore-education-statistics.service.gov.uk\n    {% endif %}",
        "extra_guidance": "Statistics are versioned by year. Always capture the publication_date + the cohort year separately.",
    },
    {
        "filename": "isles_grading.baml",
        "title": "British Isles Grading System Extractor",
        "parent_dir": "british_isles/_shared/grading",
        "count": 12,
        "role": "expert at extracting grading system data (boundaries, distributions, comparability) from a British Isles exam board PDF",
        "source_type": "PDF text from a grade boundaries bulletin",
        "fields": [
            ("exam_board", "the exam board"),
            ("subject", "the subject slug"),
            ("year", "the exam year"),
            ("grade_boundaries", "map of grade → minimum mark"),
            ("grade_distribution", "list of grade distribution entries (count + percentage)"),
        ],
        "branching": "{% if exam_board == 'AQA' %}\n    - Grades are 1-9 (with 9 being highest)\n    {% elif exam_board == 'Edexcel' %}\n    - Grades are 1-9 (with 9 being highest)\n    {% endif %}",
        "extra_guidance": "Grade boundaries are released annually after the exam. Always capture the year explicitly.",
    },
    {
        "filename": "european_nations_curriculum.baml",
        "title": "European Nations Curriculum Extractor",
        "parent_dir": "european_nations/_shared/curriculum",
        "count": 13,
        "role": "expert at extracting curriculum data from a European national education authority",
        "source_type": "PDF text from a European national education ministry",
        "fields": [
            ("country", "the country code (alpha-2)"),
            ("stage", "the educational stage (primary, lower-secondary, upper-secondary)"),
            ("subject", "the subject slug"),
            ("learning_outcomes", "list of LOs with country-specific codes"),
            ("assessment_methods", "list of assessment methods used"),
        ],
        "branching": "{% if country == 'FR' %}\n    - French cycle nomenclature: primaire / collège / lycée\n    {% elif country == 'DE' %}\n    - German Land-specific Länder codes\n    {% endif %}",
        "extra_guidance": "European curriculum structures vary widely. Use the country code as the primary branching signal.",
    },
    {
        "filename": "american_nations_law.baml",
        "title": "American Nations Law Extractor",
        "parent_dir": "american_nations/_shared/law",
        "count": 7,
        "role": "expert at extracting structured legal data from an American (USA / Brazil / California) legal document",
        "source_type": "PDF text from a state or federal legal document",
        "fields": [
            ("jurisdiction", "the jurisdiction (US-Federal, US-CA, BR-Federal, BR-State, MX-Federal)"),
            ("code_section", "the canonical code section (e.g. 'Cal. Penal Code § 187')"),
            ("title", "the section title"),
            ("effective_date", "ISO 8601 effective date"),
            ("summary", "2-3 sentence executive summary"),
            ("amendments", "list of amendments (if any)"),
        ],
        "branching": "{% if jurisdiction == 'US-CA' %}\n    - California codes are organized by subject area (Penal, Civil, etc.)\n    {% elif jurisdiction == 'BR-Federal' %}\n    - Brazilian federal laws use the LEI N pattern\n    {% endif %}",
        "extra_guidance": "Legal documents have a strict citation convention. Always capture the canonical code_section as the primary identifier.",
    },
]


def render_template(t: dict) -> str:
    """Render one template BAML file."""
    body = HEADER.format(
        title=t["title"],
        count=t["count"],
        parent_dir=t["parent_dir"],
    )

    fields_str = "\n".join(f"    - {n}: {d}" for n, d in t["fields"])

    body += f"""function DomainExtractor(input: string) -> string {{
  client ExtractEn
  prompt #"
    {{{{ _.role("user") }}}}
    You are an {t['role']}.

    Source type: {t['source_type']}

    Extract:
{fields_str}

    {t['branching']}

    {t['extra_guidance']}

    {{{{ ctx.output_format }}}}

    {{{{ input }}}}
  "#
}}
"""
    return body


def main(dry_run: bool = False) -> int:
    print(f"Generating {len(TEMPLATES)} templates to {TEMPLATES_DIR}")
    if not dry_run:
        TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
    for t in TEMPLATES:
        body = render_template(t)
        path = TEMPLATES_DIR / t["filename"]
        if dry_run:
            print(f"  [DRY] would write {path} ({len(body)} bytes)")
        else:
            path.write_text(body)
            print(f"  wrote {path} ({len(body)} bytes)")
    return 0


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    sys.exit(main(dry_run=dry_run))
