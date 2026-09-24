// =============================================================================
// Teacher-centric BAML Schema (K-12 Education Pipeline)
// Per openspec/changes/2026-09-23-k12-teacher-student-pipeline-v1/.
//
// Bilingual EN/GA extraction of teacher workflows:
//   - TeacherPlan: teacher's annual plan (subject, year group, class assignments)
//   - LessonPlan: per-session lesson plan (objectives, activities, assessment)
//   - ClassRoster: per-student profile + SEN flags + English additional language
//   - AssessmentTask: CBA + LC exam paper scoring rubric
//   - SENRecord: Special Educational Needs coordinator records
//   - PDRecord: OIDE / PDST professional learning completion
//   - ProLearningModule: an OIDE / PDST module recommendation
//
// The 5 extraction functions (ExtractTeacherPlan, ExtractLessonPlan,
// ExtractClassRoster, ExtractAssessmentTask, ExtractSENRecord) route
// through the canonical `ExtractEn` LiteLLM client (per the
centralized-model-registry spec).
// =============================================================================

// -----------------------------------------------------------------------------
// Enums
// -----------------------------------------------------------------------------

enum TeacherRole {
  PRIMARY_CLASS_TEACHER
    @description("Junior Infants through 6th Class generalist")
  POST_PRIMARY_SUBJECT_TEACHER
    @description("JC + LC subject specialist (e.g. Mathematics, English, Biology)")
  SPECIAL_EDUCATION_NEEDS_COORDINATOR
    @description("SENCO — coordinates SEN provision across the school")
  YEAR_HEAD
    @description("Pastoral year head for a year group")
  SCHOOL_LEADER
    @description("Principal / deputy principal / programme coordinator")
}

enum TeacherSubjectStage {
  PRIMARY
  JUNIOR_CYCLE
  SENIOR_CYCLE
  LCA
  TRANSITION_YEAR
}

enum SENCategory {
  NONE                          @description("No formal SEN allocation")
  RESOURCE_TEACHING              @description("Resource teaching hours")
  LEARNING_SUPPORT               @description("Learning support")
  AUTISM_SPECTRUM_DISORDER       @description("ASD allocation")
  SPECIFIC_LEARNING_DIFFICULTY    @description("SpLD allocation (dyslexia, dyscalculia)")
  PHYSICAL_DISABILITY             @description("Physical disability")
  GIFTED_AND_TALENTED             @description("Gifted + Talented programme")
}

enum AssessmentLevel {
  EXCEPTIONAL
  ABOVE_EXPECTATIONS
  IN_LINE_WITH_EXPECTATIONS
  YET_TO_MEET_EXPECTATIONS
}

// -----------------------------------------------------------------------------
// Classes
// -----------------------------------------------------------------------------

class TeacherPlan {
  plan_id string                 @description("e.g. 'plan-ms-hayes-2025-26'")
  teacher_id string              @description("School staff number")
  teacher_name_en string
  teacher_name_ga string?
  teacher_role TeacherRole
  subjects string[]              @description("Subjects the teacher is qualified to teach")
  year_groups string[]           @description("Year groups taught, e.g. ['3rd-class', '4th-class']")
  classes string[]               @description("Class group identifiers, e.g. ['3rd-class-a']")
  weekly_periods_taught int      @description("Class contact periods per week")
  weekly_planning_periods int    @description("Protected planning periods per week")
  weekly_cpd_periods int         @description("CPD / collaboration periods per week")
  sen_tutorials int               @description("SEN tutorial / support sessions per week")
  effective_from string          @description("ISO date the plan takes effect, e.g. '2025-09-01'")
  effective_to string?           @description("ISO date the plan expires, if applicable")
  source_url string
  scraped_at string
  confidence float
}

class LessonPlan {
  plan_id string                 @description("Unique plan ID, e.g. 'lp-cs203-2025-10-15-01'")
  teacher_id string
  teacher_name_en string
  class_id string                @description("Class group, e.g. '5th-class-a'")
  subject string                 @description("Subject, e.g. 'primary_mathematics'")
  subject_stage TeacherSubjectStage
  date_iso string                @description("ISO date of the lesson")
  duration_minutes int           @description("Lesson duration in minutes (typically 30-60)")
  learning_objectives string[]   @description("3-7 specific learning objectives (BAML extracted)")
  activities string[]            @description("Lesson activities (BAML extracted)")
  differentiation string?        @description("Differentiation strategies for mixed-ability classes")
  assessment string?            @description("Formative assessment method")
  homework string?               @description("Homework assignment")
  resources string[]             @description("Required resources (textbook pages, manipulatives, etc.)")
  irish_language_considerations string?  @description("Specific Gaeilge-medium considerations")
  sen_considerations string?     @description("Specific SEN accommodations")
  source_url string?
  scraped_at string
  confidence float
}

class ClassRoster {
  student_id string              @description("School student number")
  class_id string
  year_level string              @description("e.g. '5th-class', 'jc1', 'lc6'")
  school_id string
  first_name_en string
  last_name_en string
  first_name_ga string?
  last_name_ga string?
  date_of_birth string           @description("ISO date")
  guardian_email string?
  sen_status SENCategory
  english_additional_language bool  @description("True if EAL student")
  attendance_pct_ytd float       @description("Year-to-date attendance percentage")
  subject_enrolments string[]    @description("Subjects the student is enrolled in (e.g. ['english', 'gaeilge', 'mathematics'])")
  scraped_at string
}

class AssessmentTask {
  task_id string                 @description("e.g. 'cba-english-jc1-2026'")
  teacher_id string
  class_id string
  subject string
  subject_stage TeacherSubjectStage
  cba_type string?               @description("CBA type, e.g. 'written_task', 'practical_investigation', 'oral_present'")
  task_description string
  learning_outcomes_assessed string[]
  level AssessmentLevel
  marks_available int             @description("Maximum marks for the assessment")
  marks_awarded int?             @description("Marks the student received")
  teacher_comment string?        @description("Qualitative teacher comment")
  scraped_at string
}

class SENRecord {
  sen_id string
  student_id string
  sen_category SENCategory
  date_opened string             @description("ISO date the SEN record was opened")
  primary_difficulty string?     @description("Brief description of the primary difficulty")
  accommodations string[]        @description("Accommodations provided (e.g. ['reader_at_exams', 'separate_room'])")
  senco_id string?               @description("SENCO teacher ID")
  next_review_date string?       @description("ISO date of next SEN review meeting")
  parent_consent_obtained bool   @description("True if parental consent is on file")
  scraped_at string
}

class PDRecord {
  pd_id string
  teacher_id string
  module_id string               @description("OIDE/PDST module ID")
  module_name_en string
  provider string                @description("'oide' or 'pdst'")
  start_date string
  end_date string?
  hours_completed int
  certificate_url string?
  reflection_notes string?
  scraped_at string
}

class ProLearningModule {
  module_id string
  name_en string
  name_ga string?
  provider string                @description("'oide' or 'pdst'")
  target_stage TeacherSubjectStage
  subjects string[]              @description("Subjects the module covers")
  duration_hours int
  format string                  @description("e.g. 'workshop', 'online_course', 'summer_course'")
  url string
  scraped_at string
}

// =============================================================================
// Extraction functions
// =============================================================================

function ExtractTeacherPlan(input: string, teacher_id: string) -> TeacherPlan {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert at extracting teacher workload plans from Irish
    school documents.

    For teacher {{ teacher_id }}, extract the annual workload plan.
    Include subjects, year groups, classes, weekly periods (taught,
    planning, CPD), SEN tutorials, effective dates.

    {{ ctx.output_format }}
    {{ input }}
  "#
}

function ExtractLessonPlan(input: string, teacher_id: string, class_id: string) -> LessonPlan {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert at extracting lesson plans from Irish primary /
    post-primary school documents.

    For teacher {{ teacher_id }} teaching class {{ class_id }}, extract
    the lesson plan including learning objectives, activities,
    differentiation, assessment, homework, resources, SEN considerations.

    {{ ctx.output_format }}
    {{ input }}
  "#
}

function ExtractClassRoster(input: string) -> ClassRoster[] {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert at extracting class roster entries from Irish
    school MIS exports.

    Extract each student row including student_id, class_id,
    year_level, names (EN + GA), date of birth, guardian email,
    SEN status, EAL flag, attendance percentage, subject enrolments.

    {{ ctx.output_format }}
    {{ input }}
  "#
}

function ExtractAssessmentTask(input: string, task_id: string) -> AssessmentTask {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert at extracting assessment task details from Irish
    school documents (CBA for JC, exam papers for LC).

    For task {{ task_id }}, extract the task description, learning
    outcomes assessed, level, marks available, teacher comment.

    {{ ctx.output_format }}
    {{ input }}
  "#
}

function ExtractSENRecord(input: string, student_id: string) -> SENRecord {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert at extracting Special Educational Needs (SEN)
    records from Irish school SENCO documents.

    For student {{ student_id }}, extract the SEN category, date
    opened, primary difficulty, accommodations, SENCO, next review
    date, parent consent flag.

    {{ ctx.output_format }}
    {{ input }}
  "#
}
