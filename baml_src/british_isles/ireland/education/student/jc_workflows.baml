// =============================================================================
// Student-centric BAML Schema (K-12 Education Pipeline)
// Per openspec/changes/2026-09-23-k12-teacher-student-pipeline-v1/.
//
// Bilingual EN/GA extraction of student workflows (post-primary /
// Junior Cycle + Senior Cycle + LCA + Transition Year):
//   - HomeworkItem: per-subject homework tracker
//   - CBAPlan: JC Classroom-Based Assessment tracker
//   - StudyPlan: LC / TY revision tracker
//   - WellbeingCheckIn: student wellbeing self-report
//   - ExamTimetable: State Exams Commission timetable row
//
// The 5 extraction functions route through the canonical `ExtractEn`
// LiteLLM client (per the centralized-model-registry spec).
// =============================================================================

// -----------------------------------------------------------------------------
// Enums
// -----------------------------------------------------------------------------

enum HomeworkStatus {
  NOT_STARTED
  IN_PROGRESS
  SUBMITTED
  GRADED
  RETURNED
  MISSING
}

enum CBAType {
  WRITTEN_TASK
    @description("A research-based written task (e.g. English CBA 1)")
  PRACTICAL_INVESTIGATION
    @description("A practical / scientific investigation (e.g. Science CBA)")
  ORAL_PRESENTATION
    @description("An oral / aural presentation (e.g. Gaeilge CBA)")
  PRACTICAL_PORTFOLIO
    @description("A practical portfolio (e.g. Art CBA)")
  RESEARCH_PROJECT
    @description("A research project (e.g. History CBA)")
}

enum CBALevel {
  HIGHER
  ORDINARY
  COMMON
}

enum WellbeingLevel {
  EXCELLENT
  GOOD
  FAIR
  STRUGGLING
  CRISIS
}

enum WellbeingDomain {
  ACADEMIC
    @description("Coping with academic workload")
  SOCIAL
    @description("Peer relationships + sense of belonging")
  FAMILY
    @description("Home life + parental support")
  PHYSICAL
    @description("Sleep, exercise, nutrition")
  EMOTIONAL
    @description("Anxiety, mood, resilience")
  FINANCIAL
    @description("Cost of materials, travel, exam fees")
}

// -----------------------------------------------------------------------------
// Classes
// -----------------------------------------------------------------------------

class HomeworkItem {
  homework_id string              @description("e.g. 'hw-2026-03-15-cs203-saoirse'")
  student_id string
  class_id string
  subject string
  teacher_id string
  assigned_at string              @description("ISO timestamp")
  due_at string                   @description("ISO timestamp")
  title_en string
  title_ga string?
  description_en string
  description_ga string?
  status HomeworkStatus
  estimated_minutes int
  resource_links string[]         @description("URLs to textbook chapters, videos, etc.")
  grade_pct int?                 @description("Grade percentage (0-100) once graded")
  scraped_at string
}

class CBAPlan {
  cba_id string                   @description("e.g. 'cba-english-jc1-2026-saoirse'")
  student_id string
  class_id string
  subject string
  cba_type CBAType
  cba_level CBALevel
  title_en string
  title_ga string?
  brief_received_at string?      @description("ISO date the brief was received")
  draft_due_at string             @description("ISO date the draft is due")
  final_due_at string             @description("ISO date the final task is due")
  status HomeworkStatus
  word_count int?
  sources_count int?
  plan_notes string?             @description("Student's planning notes")
  teacher_feedback string?
  scraped_at string
}

class StudyPlan {
  plan_id string
  student_id string
  class_id string
  exam_window string              @description("e.g. 'LC 2026 June', 'JC CBA 2 2026 March'")
  start_date string
  end_date string
  subjects StudyPlanSubject[]     @description("Per-subject study schedule")
  total_study_hours int           @description("Planned total study hours")
  hours_per_day float             @description("Daily study hour target")
  scraped_at string
}

class StudyPlanSubject {
  subject string
  topics string[]                 @description("Topics to cover in revision")
  hours_allocated int
  resources string[]              @description("Textbook chapters, videos, etc.")
}

class WellbeingCheckIn {
  check_in_id string
  student_id string
  date string
  overall WellbeingLevel
  by_domain dict<string, WellbeingLevel
    @description("Map of domain → level")
  notes_en string?
  notes_ga string?
  flagged_for_support bool        @description("True if any domain is 'crisis' or 'struggling'")
  follow_up_required bool
  scraped_at string
}

class ExamTimetable {
  exam_id string                  @description("e.g. 'lc-2026-maths-p1'")
  subject string
  level string                    @description("'higher' or 'ordinary'")
  paper_number int                @description("1, 2, etc.")
  date_iso string
  start_time string               @description("HH:MM")
  duration_minutes int
  venue string?
  centre_number string?
  scraped_at string
}

// =============================================================================
// Extraction functions
// =============================================================================

function ExtractHomeworkItem(input: string, student_id: string) -> HomeworkItem {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert at extracting homework items from Irish school
    learning platforms (Google Classroom / Microsoft Teams / Seesaw).

    For student {{ student_id }}, extract the homework item: subject,
    teacher, dates, title, description, status, estimated minutes,
    resource links, grade.

    {{ ctx.output_format }}
    {{ input }}
  "#
}

function ExtractCBAPlan(input: string, student_id: string) -> CBAPlan {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert at extracting Junior Cycle Classroom-Based
    Assessment (CBA) planning from Irish school documents.

    For student {{ student_id }}, extract the CBA plan: subject,
    CBA type + level, title, brief/draft/final due dates, status,
    word count, planning notes, teacher feedback.

    {{ ctx.output_format }}
    {{ input }}
  "#
}

function ExtractStudyPlan(input: string, student_id: string) -> StudyPlan {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert at extracting Leaving Certificate study plans
    from Irish school documents.

    For student {{ student_id }}, extract the study plan: exam window,
    dates, per-subject schedule with topics + hours + resources, total
    study hours, daily target.

    {{ ctx.output_format }}
    {{ input }}
  "#
}

function ExtractWellbeingCheckIn(input: string, student_id: string) -> WellbeingCheckIn {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert at extracting student wellbeing check-ins from
    Irish school pastoral care documents.

    For student {{ student_id }}, extract the check-in: date, overall
    level, per-domain level map, notes (EN + GA), support flag, follow-up
    flag.

    {{ ctx.output_format }}
    {{ input }}
  "#
}

function ExtractExamTimetable(input: string) -> ExamTimetable[] {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert at extracting State Examinations Commission
    exam timetables from the SEC official timetable PDFs.

    Extract each exam row: exam_id, subject, level, paper number,
    date, start time, duration, venue, centre number.

    {{ ctx.output_format }}
    {{ input }}
  "#
}
