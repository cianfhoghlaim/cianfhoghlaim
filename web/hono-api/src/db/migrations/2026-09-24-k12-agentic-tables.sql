-- 2026-09-24-web-agentic-deep-refactor-v1 — K-12 agentic tables
--
-- Adds the canonical cianfhoghlaim project row + the K-12 student +
-- class + agent workflow outputs. Mirrors the Drizzle ORM definitions
-- at web/hono-api/src/db/schema.ts.
--
-- Uses TEXT for JSON (SQLite-flavor compatible — Cloudflare D1 does not
-- support JSONB type). The Python + TS layers use json.loads / json.dumps.

-- 1) The canonical cianfhoghlaim project row (singleton)
INSERT OR IGNORE INTO project (id, name, description, stage_taxonomy, created_at)
VALUES (
  'cianfhoghlaim',
  'cianfhoghlaim',
  'The single canonical cianfhoghlaim project (BIEP v3 5-stage taxonomy)',
  '["aistear","primary","junior_cycle","senior_cycle","tertiary"]',
  CURRENT_TIMESTAMP
);

-- 2) Student table (K-12)
CREATE TABLE IF NOT EXISTS student (
  id                        TEXT PRIMARY KEY,
  school_id                 TEXT NOT NULL,
  class_id                  TEXT NOT NULL,
  year_level                TEXT NOT NULL,
  first_name_en             TEXT NOT NULL,
  last_name_en              TEXT NOT NULL,
  first_name_ga             TEXT,
  last_name_ga              TEXT,
  date_of_birth             INTEGER NOT NULL,
  guardian_email           TEXT,
  sen_status                TEXT NOT NULL DEFAULT 'none',
  english_additional_language INTEGER NOT NULL DEFAULT 0,
  attendance_pct_ytd        REAL NOT NULL DEFAULT 0.0,
  created_at                INTEGER NOT NULL DEFAULT (unixepoch())
);

-- 3) Class registry + class roster
CREATE TABLE IF NOT EXISTS class_registry (
  id            TEXT PRIMARY KEY,
  school_id     TEXT NOT NULL,
  year_level    TEXT NOT NULL,
  subject       TEXT NOT NULL,
  class_group   TEXT NOT NULL,
  teacher_id    TEXT,
  created_at    INTEGER NOT NULL DEFAULT (unixepoch())
);

CREATE TABLE IF NOT EXISTS class_roster (
  class_id     TEXT NOT NULL,
  student_id   TEXT NOT NULL REFERENCES student(id) ON DELETE CASCADE,
  year_level   TEXT NOT NULL,
  enrolled_at  INTEGER NOT NULL DEFAULT (unixepoch()),
  PRIMARY KEY (class_id, student_id)
);

-- 4) Teacher workload
CREATE TABLE IF NOT EXISTS teacher_workload (
  id                       TEXT PRIMARY KEY,
  teacher_id               TEXT NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
  school_id                TEXT NOT NULL,
  email                    TEXT NOT NULL,
  name_en                  TEXT NOT NULL,
  name_ga                  TEXT,
  teaching_subjects        TEXT NOT NULL DEFAULT '[]',  -- JSON array
  class_assignments        TEXT NOT NULL DEFAULT '[]',  -- JSON array
  weekly_periods_taught    INTEGER NOT NULL,
  weekly_planning_periods  INTEGER NOT NULL,
  weekly_cpd_periods        INTEGER NOT NULL,
  sen_tutorials            INTEGER NOT NULL,
  effective_from           INTEGER NOT NULL,
  effective_to             INTEGER,
  created_at               INTEGER NOT NULL DEFAULT (unixepoch())
);

-- 5) Agent workflow outputs (the 5 K-12 teacher + student outputs)
CREATE TABLE IF NOT EXISTS agent_lesson_plan (
  id                    TEXT PRIMARY KEY,
  student_id            TEXT REFERENCES student(id),
  teacher_id            TEXT NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
  class_id              TEXT NOT NULL,
  subject               TEXT NOT NULL,
  week_iso              TEXT NOT NULL,
  objectives            TEXT NOT NULL DEFAULT '[]',  -- JSON array
  activities            TEXT NOT NULL DEFAULT '[]',  -- JSON array
  sen_considerations    TEXT NOT NULL DEFAULT '[]',  -- JSON array
  created_at            INTEGER NOT NULL DEFAULT (unixepoch())
);

CREATE TABLE IF NOT EXISTS agent_homework_item (
  id                    TEXT PRIMARY KEY,
  student_id            TEXT NOT NULL REFERENCES student(id) ON DELETE CASCADE,
  class_id              TEXT NOT NULL,
  subject               TEXT NOT NULL,
  teacher_id            TEXT NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
  assigned_at           INTEGER NOT NULL DEFAULT (unixepoch()),
  due_at                INTEGER NOT NULL,
  title_en              TEXT NOT NULL,
  title_ga              TEXT,
  description_en        TEXT NOT NULL,
  description_ga        TEXT,
  status                TEXT NOT NULL DEFAULT 'not_started',
  estimated_minutes     INTEGER NOT NULL DEFAULT 30,
  resource_links        TEXT NOT NULL DEFAULT '[]',  -- JSON array
  grade_pct             INTEGER,
  created_at            INTEGER NOT NULL DEFAULT (unixepoch())
);

CREATE TABLE IF NOT EXISTS agent_cba_plan (
  id                    TEXT PRIMARY KEY,
  student_id            TEXT NOT NULL REFERENCES student(id) ON DELETE CASCADE,
  class_id              TEXT NOT NULL,
  subject               TEXT NOT NULL,
  cba_type              TEXT NOT NULL,
  cba_level             TEXT NOT NULL,
  title_en              TEXT NOT NULL,
  title_ga              TEXT,
  brief_received_at    INTEGER,
  draft_due_at          INTEGER NOT NULL,
  final_due_at          INTEGER NOT NULL,
  status                TEXT NOT NULL DEFAULT 'not_started',
  word_count            INTEGER,
  sources_count         INTEGER,
  plan_notes            TEXT,
  teacher_feedback      TEXT,
  created_at            INTEGER NOT NULL DEFAULT (unixepoch())
);

CREATE TABLE IF NOT EXISTS agent_wellbeing_checkin (
  id                    TEXT PRIMARY KEY,
  student_id            TEXT NOT NULL REFERENCES student(id) ON DELETE CASCADE,
  class_id              TEXT NOT NULL,
  date_iso              TEXT NOT NULL,
  overall               TEXT NOT NULL,
  by_domain             TEXT NOT NULL DEFAULT '{}',  -- JSON object
  notes_en              TEXT,
  notes_ga              TEXT,
  flagged_for_support   INTEGER NOT NULL DEFAULT 0,
  follow_up_required    INTEGER NOT NULL DEFAULT 0,
  created_at            INTEGER NOT NULL DEFAULT (unixepoch())
);

CREATE TABLE IF NOT EXISTS agent_exam_timetable (
  id                    TEXT PRIMARY KEY,
  student_id            TEXT NOT NULL REFERENCES student(id) ON DELETE CASCADE,
  class_id              TEXT NOT NULL,
  subject               TEXT NOT NULL,
  level                 TEXT NOT NULL,
  paper_number          INTEGER NOT NULL DEFAULT 1,
  date_iso              TEXT NOT NULL,
  start_time            TEXT NOT NULL,
  duration_minutes      INTEGER NOT NULL,
  venue                 TEXT,
  centre_number         TEXT,
  created_at            INTEGER NOT NULL DEFAULT (unixepoch())
);

CREATE TABLE IF NOT EXISTS agent_sen_record (
  id                        TEXT PRIMARY KEY,
  student_id                TEXT NOT NULL REFERENCES student(id) ON DELETE CASCADE,
  sen_category              TEXT NOT NULL,
  date_opened               INTEGER NOT NULL,
  primary_difficulty        TEXT,
  accommodations            TEXT NOT NULL DEFAULT '[]',  -- JSON array
  senco_id                  TEXT,
  next_review_date          INTEGER,
  parent_consent_obtained   INTEGER NOT NULL DEFAULT 0,
  created_at                INTEGER NOT NULL DEFAULT (unixepoch())
);

-- 6) Verify the 13 + 14 actions will be able to read the new schema
SELECT 'project' AS table_name, COUNT(*) AS rows FROM project
UNION ALL
SELECT 'student', COUNT(*) FROM student
UNION ALL
SELECT 'class_registry', COUNT(*) FROM class_registry
UNION ALL
SELECT 'class_roster', COUNT(*) FROM class_roster
UNION ALL
SELECT 'teacher_workload', COUNT(*) FROM teacher_workload
UNION ALL
SELECT 'agent_lesson_plan', COUNT(*) FROM agent_lesson_plan
UNION ALL
SELECT 'agent_homework_item', COUNT(*) FROM agent_homework_item
UNION ALL
SELECT 'agent_cba_plan', COUNT(*) FROM agent_cba_plan
UNION ALL
SELECT 'agent_wellbeing_checkin', COUNT(*) FROM agent_wellbeing_checkin
UNION ALL
SELECT 'agent_exam_timetable', COUNT(*) FROM agent_exam_timetable
UNION ALL
SELECT 'agent_sen_record', COUNT(*) FROM agent_sen_record;
