import { pgTable, text, timestamp, boolean, integer, real, jsonb, primaryKey } from "drizzle-orm/pg-core";

// =============================================================================
// BetterAuth + Organisation schema (canonical)
// =============================================================================

export const user = pgTable("user", {
  id: text("id").primaryKey(),
  name: text("name").notNull(),
  email: text("email").notNull().unique(),
  emailVerified: boolean("email_verified").notNull().default(false),
  image: text("image"),
  createdAt: timestamp("created_at").notNull().defaultNow(),
  updatedAt: timestamp("updated_at").notNull().defaultNow(),
});

export const session = pgTable("session", {
  id: text("id").primaryKey(),
  expiresAt: timestamp("expires_at").notNull(),
  token: text("token").notNull().unique(),
  createdAt: timestamp("created_at").notNull().defaultNow(),
  updatedAt: timestamp("updated_at").notNull().defaultNow(),
  ipAddress: text("ip_address"),
  userAgent: text("user_agent"),
  userId: text("user_id").notNull().references(() => user.id, { onDelete: "cascade" }),
  activeOrganizationId: text("active_organization_id"),
});

export const account = pgTable("account", {
  id: text("id").primaryKey(),
  accountId: text("account_id").notNull(),
  providerId: text("provider_id").notNull(),
  userId: text("user_id").notNull().references(() => user.id, { onDelete: "cascade" }),
  accessToken: text("access_token"),
  refreshToken: text("refresh_token"),
  idToken: text("id_token"),
  accessTokenExpiresAt: timestamp("access_token_expires_at"),
  refreshTokenExpiresAt: timestamp("refresh_token_expires_at"),
  scope: text("scope"),
  password: text("password"),
  createdAt: timestamp("created_at").notNull().defaultNow(),
  updatedAt: timestamp("updated_at").notNull().defaultNow(),
});

export const verification = pgTable("verification", {
  id: text("id").primaryKey(),
  identifier: text("identifier").notNull(),
  value: text("value").notNull(),
  expiresAt: timestamp("expires_at").notNull(),
  createdAt: timestamp("created_at").notNull().defaultNow(),
  updatedAt: timestamp("updated_at").notNull().defaultNow(),
});

export const organization = pgTable("organization", {
  id: text("id").primaryKey(),
  name: text("name").notNull(),
  slug: text("slug").notNull().unique(),
  logo: text("logo"),
  metadata: text("metadata"),
  createdAt: timestamp("created_at").notNull().defaultNow(),
});

export const member = pgTable("member", {
  id: text("id").primaryKey(),
  organizationId: text("organization_id").notNull().references(() => organization.id, { onDelete: "cascade" }),
  userId: text("user_id").notNull().references(() => user.id, { onDelete: "cascade" }),
  role: text("role").notNull().default("member"),
  createdAt: timestamp("created_at").notNull().defaultNow(),
});

export const invitation = pgTable("invitation", {
  id: text("id").primaryKey(),
  organizationId: text("organization_id").notNull().references(() => organization.id, { onDelete: "cascade" }),
  email: text("email").notNull(),
  role: text("role"),
  status: text("status").notNull().default("pending"),
  expiresAt: timestamp("expires_at").notNull(),
  inviterId: text("inviter_id").notNull().references(() => user.id, { onDelete: "cascade" }),
});

export const jwks = pgTable("jwks", {
  id: text("id").primaryKey(),
  publicKey: text("public_key").notNull(),
  privateKey: text("private_key").notNull(),
  createdAt: timestamp("created_at").notNull().defaultNow(),
});

// =============================================================================
// Cianfhoghlaim project (single canonical instance)
// =============================================================================
// Per the 2026-09-24-web-agentic-deep-refactor-v1 change. The platform is
// a single cianfhoghlaim project — we don't run multiple instances, so the
// table is a singleton that records the canonical stage taxonomy.
// =============================================================================

export const project = pgTable("project", {
  id: text("id").primaryKey(),
  name: text("name").notNull(),
  description: text("description"),
  stageTaxonomy: jsonb("stage_taxonomy")
    .$type<Array<"aistear" | "primary" | "junior_cycle" | "senior_cycle" | "tertiary">>()
    .notNull(),
  createdAt: timestamp("created_at").notNull().defaultNow(),
});

// =============================================================================
// Student table (K-12 student profile)
// =============================================================================
// Per the 2026-09-24-web-agentic-deep-refactor-v1 change. A `student` row
// is the K-12 student-profile (per-class rostering). Separated from `user`
// (BetterAuth account) because a student may have a parent as their user,
// and the agent_registry_runtime needs to JOIN students to agents
// (lesson_planner_agent → class roster → SEN flag → lesson plan output).
// =============================================================================

export const student = pgTable("student", {
  id: text("id").primaryKey(),
  schoolId: text("school_id").notNull(),
  classId: text("class_id").notNull(),
  yearLevel: text("year_level").notNull(),
  firstNameEn: text("first_name_en").notNull(),
  lastNameEn: text("last_name_en").notNull(),
  firstNameGa: text("first_name_ga"),
  lastNameGa: text("last_name_ga"),
  dateOfBirth: timestamp("date_of_birth").notNull(),
  guardianEmail: text("guardian_email"),
  senStatus: text("sen_status").notNull().default("none"),
  englishAdditionalLanguage: boolean("eal").notNull().default(false),
  attendancePctYtd: real("attendance_pct_ytd").notNull().default(0.0),
  createdAt: timestamp("created_at").notNull().defaultNow(),
});

// =============================================================================
// K-12 agentic workflow outputs (the 5 ADK 2 Pillar-1 + Pillar-2 outputs)
// =============================================================================
// Per the 2026-09-23-k12-teacher-student-pipeline-v1 + 2026-09-23-upgrade-to-adk2-pillars-1-2-3-v1
// + 2026-09-24-web-agentic-deep-refactor-v1 changes. Each row is one
// agent's output (a lesson plan, a CBA plan, a homework item, a
// wellbeing check-in, an exam timetable entry, a SEN record).
// The web CopilotKit runtime reads these tables to surface the
// persistent state to the user; the agent writes them.
// =============================================================================

export const agentLessonPlan = pgTable("agent_lesson_plan", {
  id: text("id").primaryKey(),
  studentId: text("student_id").references(() => student.id),
  teacherId: text("teacher_id").notNull().references(() => user.id),
  classId: text("class_id").notNull(),
  subject: text("subject").notNull(),
  weekIso: text("week_iso").notNull(),
  objectives: jsonb("objectives").$type<string[]>().notNull(),
  activities: jsonb("activities").$type<string[]>().notNull(),
  senConsiderations: jsonb("sen_considerations").$type<string[]>().notNull(),
  createdAt: timestamp("created_at").notNull().defaultNow(),
});

export const agentHomeworkItem = pgTable("agent_homework_item", {
  id: text("id").primaryKey(),
  studentId: text("student_id").notNull().references(() => student.id),
  classId: text("class_id").notNull(),
  subject: text("subject").notNull(),
  teacherId: text("teacher_id").notNull().references(() => user.id),
  assignedAt: timestamp("assigned_at").notNull().defaultNow(),
  dueAt: timestamp("due_at").notNull(),
  titleEn: text("title_en").notNull(),
  titleGa: text("title_ga"),
  descriptionEn: text("description_en").notNull(),
  descriptionGa: text("description_ga"),
  status: text("status").notNull().default("not_started"),
  estimatedMinutes: integer("estimated_minutes").notNull().default(30),
  resourceLinks: jsonb("resource_links").$type<string[]>().notNull(),
  gradePct: integer("grade_pct"),
  createdAt: timestamp("created_at").notNull().defaultNow(),
});

export const agentCbaPlan = pgTable("agent_cba_plan", {
  id: text("id").primaryKey(),
  studentId: text("student_id").notNull().references(() => student.id),
  classId: text("class_id").notNull(),
  subject: text("subject").notNull(),
  cbaType: text("cba_type").notNull(),
  cbaLevel: text("cba_level").notNull(),
  titleEn: text("title_en").notNull(),
  titleGa: text("title_ga"),
  briefReceivedAt: timestamp("brief_received_at"),
  draftDueAt: timestamp("draft_due_at").notNull(),
  finalDueAt: timestamp("final_due_at").notNull(),
  status: text("status").notNull().default("not_started"),
  wordCount: integer("word_count"),
  sourcesCount: integer("sources_count"),
  planNotes: text("plan_notes"),
  teacherFeedback: text("teacher_feedback"),
  createdAt: timestamp("created_at").notNull().defaultNow(),
});

export const agentWellbeingCheckin = pgTable("agent_wellbeing_checkin", {
  id: text("id").primaryKey(),
  studentId: text("student_id").notNull().references(() => student.id),
  classId: text("class_id").notNull(),
  dateIso: text("date_iso").notNull(),
  overall: text("overall").notNull(),
  byDomain: jsonb("by_domain").$type<Record<string, string>>().notNull(),
  notesEn: text("notes_en"),
  notesGa: text("notes_ga"),
  flaggedForSupport: boolean("flagged_for_support").notNull().default(false),
  followUpRequired: boolean("follow_up_required").notNull().default(false),
  createdAt: timestamp("created_at").notNull().defaultNow(),
});

export const agentExamTimetable = pgTable("agent_exam_timetable", {
  id: text("id").primaryKey(),
  studentId: text("student_id").notNull().references(() => student.id),
  classId: text("class_id").notNull(),
  subject: text("subject").notNull(),
  level: text("level").notNull(),
  paperNumber: integer("paper_number").notNull().default(1),
  dateIso: text("date_iso").notNull(),
  startTime: text("start_time").notNull(),
  durationMinutes: integer("duration_minutes").notNull(),
  venue: text("venue"),
  centreNumber: text("centre_number"),
  createdAt: timestamp("created_at").notNull().defaultNow(),
});

export const agentSenRecord = pgTable("agent_sen_record", {
  id: text("id").primaryKey(),
  studentId: text("student_id").notNull().references(() => student.id),
  senCategory: text("sen_category").notNull(),
  dateOpened: timestamp("date_opened").notNull(),
  primaryDifficulty: text("primary_difficulty"),
  accommodations: jsonb("accommodations").$type<string[]>().notNull(),
  sencoId: text("senco_id"),
  nextReviewDate: timestamp("next_review_date"),
  parentConsentObtained: boolean("parent_consent_obtained").notNull().default(false),
  createdAt: timestamp("created_at").notNull().defaultNow(),
});

// =============================================================================
// Teacher workload (K-12 — per the teacher_pd + teacher_workload DLT sources)
// =============================================================================
// Per the 2026-09-23-k12-teacher-student-pipeline-v1 change.
// =============================================================================

export const teacherWorkload = pgTable("teacher_workload", {
  id: text("id").primaryKey(),
  teacherId: text("teacher_id").notNull().references(() => user.id),
  schoolId: text("school_id").notNull(),
  email: text("email").notNull(),
  nameEn: text("name_en").notNull(),
  nameGa: text("name_ga"),
  teachingSubjects: jsonb("teaching_subjects").$type<string[]>().notNull(),
  classAssignments: jsonb("class_assignments").$type<string[]>().notNull(),
  weeklyPeriodsTaught: integer("weekly_periods_taught").notNull(),
  weeklyPlanningPeriods: integer("weekly_planning_periods").notNull(),
  weeklyCpdPeriods: integer("weekly_cpd_periods").notNull(),
  senTutorials: integer("sen_tutorials").notNull(),
  effectiveFrom: timestamp("effective_from").notNull(),
  effectiveTo: timestamp("effective_to"),
  createdAt: timestamp("created_at").notNull().defaultNow(),
});

// =============================================================================
// Class roster (K-12 — the per-class student membership)
// =============================================================================
// One row per (class_id, student_id) — links students to classes.
// =============================================================================

export const classRoster = pgTable(
  "class_roster",
  {
    classId: text("class_id").notNull(),
    studentId: text("student_id").notNull().references(() => student.id),
    yearLevel: text("year_level").notNull(),
    enrolledAt: timestamp("enrolled_at").notNull().defaultNow(),
  },
  (table) => ({
    pk: primaryKey({ columns: [table.classId, table.studentId] }),
  })
);

// =============================================================================
// Class registry (K-12 — per-school teacher-assignments)
// =============================================================================
// One row per class (the canonical class entity that links to a teacher,
// a year level, a subject, and a list of student_ids via class_roster).
// =============================================================================

export const classRegistry = pgTable("class_registry", {
  id: text("id").primaryKey(),
  schoolId: text("school_id").notNull(),
  yearLevel: text("year_level").notNull(),
  subject: text("subject").notNull(),
  classGroup: text("class_group").notNull(),
  teacherId: text("teacher_id").references(() => user.id),
  createdAt: timestamp("created_at").notNull().defaultNow(),
});
