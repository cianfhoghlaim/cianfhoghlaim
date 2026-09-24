import { drizzle } from "drizzle-orm/postgres-js";
import postgres from "postgres";
import * as schema from "./schema";

const connectionString = process.env.DATABASE_URL;
if (!connectionString) {
  throw new Error("DATABASE_URL is required for BetterAuth Drizzle adapter");
}

// pgBouncer / PlanetScale-safe options:
// - no_prepare: true  — required for transaction-mode pooling
// - max: 1 per worker  — Hono runs single-threaded
// - ssl: 'require'      — PlanetScale enforces TLS
export const client = postgres(connectionString, {
  prepare: false,
  max: 1,
  ssl: connectionString.includes("psdb.cloud") ? "require" : false,
});

export const db = drizzle(client, { schema });
export type DB = typeof db;

// =============================================================================
// Per the 2026-09-24-web-agentic-deep-refactor-v1 change.
// The CopilotKit runtime (the 13 + 14 actions wired in
// web/apps/cianfhoghlaim-web/apps/api/src/copilotkit/actions.ts)
// reads + writes these tables. Helper type aliases for the agentic surface.
// =============================================================================

export type Student = typeof schema.student.$inferSelect;
export type NewStudent = typeof schema.student.$inferInsert;

export type AgentLessonPlan = typeof schema.agentLessonPlan.$inferSelect;
export type NewAgentLessonPlan = typeof schema.agentLessonPlan.$inferInsert;

export type AgentHomeworkItem = typeof schema.agentHomeworkItem.$inferSelect;
export type NewAgentHomeworkItem = typeof schema.agentHomeworkItem.$inferInsert;

export type AgentCbaPlan = typeof schema.agentCbaPlan.$inferSelect;
export type NewAgentCbaPlan = typeof schema.agentCbaPlan.$inferInsert;

export type AgentWellbeingCheckin = typeof schema.agentWellbeingCheckin.$inferSelect;
export type NewAgentWellbeingCheckin = typeof schema.agentWellbeingCheckin.$inferInsert;

export type AgentExamTimetable = typeof schema.agentExamTimetable.$inferSelect;
export type NewAgentExamTimetable = typeof schema.agentExamTimetable.$inferInsert;

export type AgentSenRecord = typeof schema.agentSenRecord.$inferSelect;
export type NewAgentSenRecord = typeof schema.agentSenRecord.$inferInsert;

export type TeacherWorkload = typeof schema.teacherWorkload.$inferSelect;
export type NewTeacherWorkload = typeof schema.teacherWorkload.$inferInsert;

export type ClassRegistry = typeof schema.classRegistry.$inferSelect;
export type NewClassRegistry = typeof schema.classRegistry.$inferInsert;
