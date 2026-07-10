// =============================================================================
// Subject Rubric Functions (split from curriculum_extraction.baml)
// Rubric generation + scoring + comparison functions for Leaving Certificate subjects.
// =============================================================================

function ExtractSubjectRubric(text: string,
  subject: string,
  level: ExamLevel,
  exam_years: int[]) -> SubjectRubric {
  client Claude
  prompt #"You are an expert at synthesizing assessment rubrics for Irish Leaving Certificate subjects.

Given a subject specification and recent exam years, build a comprehensive scoring rubric that captures both the official marking scheme patterns and trends observed across multiple exam years.

SUBJECT: {{ subject }}
LEVEL: {{ level }}
EXAM YEARS: {{ exam_years|join(", ") }}

SOURCE TEXT:
{{ text }}

Extract:
1. Rubric style (e.g., "analytic", "holistic", "trait-based", "level-based", "mixed")
2. Common assessment criteria with bilingual labels (e.g., "Knowledge & Understanding" / "Eolas agus Tuiscint")
3. Performance levels with descriptors (4-6 levels typically: Exceptional, Above Expectations, In Line With, Yet to Meet Expectations)
4. Mark allocation per criterion
5. Common deductions/pénalisations (unit errors, arithmetic slips, off-by-one)
6. Bilingual terminology (canonical Irish-language assessment terms)

The rubric should be reusable across exam years and help teachers apply consistent grading.

{{ ctx.output_format(prefix="Answer with this format:\n") }}

{{ _.role("user") }}
    SUBJECT: {{ subject }}
    LEVEL: {{ level }}
"#
}


function ScoreEssayAgainstRubric(essay: string,
  subject: string,
  level: ExamLevel,
  rubric_text: string) -> RubricScore {
  client Claude
  prompt #"You are an expert at applying an assessment rubric to score an Irish Leaving Certificate student essay.

Apply the rubric rigorously and provide detailed feedback.

SUBJECT: {{ subject }}
LEVEL: {{ level }}

RUBRIC:
{{ rubric_text }}

STUDENT ESSAY:
{{ essay }}

Score the essay on each rubric criterion, providing:
1. Per-criterion score (numeric, with maximum)
2. Per-criterion feedback explaining the score (cite specific parts of the essay)
3. Strengths demonstrated
4. Areas for improvement
5. Overall score (sum of criteria scores)
6. Suggested grade band (e.g., H1, H2, O1, O2 for Leaving Cert)
7. Bilingual feedback labels where appropriate (use both English and Irish)

Be fair, consistent, and pedagogically constructive. Reference the rubric criteria explicitly in your justification.

{{ ctx.output_format(prefix="Answer with this format:\n") }}

{{ _.role("user") }}
    SUBJECT: {{ subject }}
    LEVEL: {{ level }}
"#
}


function CompareMarkingSchemes(year_a: int,
  year_b: int,
  scheme_a: string,
  scheme_b: string,
  subject: string) -> MarkingSchemeDiff {
  client Claude
  prompt #"You are an expert at comparing State Examination Commission (SEC) marking schemes across years to identify patterns, trends, and shifts in assessment emphasis.

SUBJECT: {{ subject }}
YEAR A: {{ year_a }}
YEAR B: {{ year_b }}

MARKING SCHEME A ({{ year_a }}):
{{ scheme_a }}

MARKING SCHEME B ({{ year_b }}):
{{ scheme_b }}

Compare the two schemes and identify:
1. Question structure changes (added/removed/merged questions)
2. Mark allocation shifts (which questions got more/fewer marks)
3. Topic emphasis changes (which strands got more coverage)
4. Difficulty progression (easier/harder than prior year)
5. New question types introduced
6. Removed question types
7. Overall assessment philosophy shift (e.g., "more focus on application vs recall")
8. Predicted implications for future years (e.g., "this pattern suggests X")

This comparison helps teachers identify assessment trends and predict future exam patterns.

{{ ctx.output_format(prefix="Answer with this format:\n") }}

{{ _.role("user") }}
    SUBJECT: {{ subject }}
    YEARS: {{ year_a }} vs {{ year_b }}
"#
}


function LazyExtractExamPaper(text: string,
  subject: string,
  year: int,
  level: ExamLevel) -> ExamPaper {
  client Claude
  prompt #"You are an expert at lazy/on-demand extraction of exam paper data for the Cianfhoghlaim Oideachais platform.

This is a cost-optimized extraction function used when a user requests specific exam paper data. The function only extracts what is needed to answer the user's request, not the full exam paper structure.

SUBJECT: {{ subject }}
YEAR: {{ year }}
LEVEL: {{ level }}

EXAM PAPER TEXT:
{{ text }}

For lazy extraction, focus on the highest-value structured data:
1. Paper metadata (total marks, duration, structure type)
2. Question summary (count by type, total marks per section)
3. Topic distribution (which strands/learning outcomes are most heavily tested)
4. Difficulty profile (estimated proportion of Easy/Medium/Hard questions)
5. Notable patterns (e.g., "calculations cluster in Section B", "essay is 30% of total marks")

This is a SPARSE extraction — return only the structured metadata needed to populate UI components, not the full question text.

{{ ctx.output_format(prefix="Answer with this format:\n") }}

{{ _.role("user") }}
    SUBJECT: {{ subject }}
    YEAR: {{ year }}
"#
}