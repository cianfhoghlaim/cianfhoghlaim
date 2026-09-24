/**
 * apps/api/src/copilotkit/index.ts — barrel re-export for the shared
 * CopilotKit + AG-UI base.
 *
 * Per the 2026-09-24-web-agentic-deep-refactor-v1 change. The single
 * source of truth for the CopilotKit + AG-UI wire-up lives in
 * apps/api/src/copilotkit/_base.ts (the dev fallback config +
 * subprocess helper + the canonical Tool type).
 */
export {
  defineTool,
  callAgentRegistryRuntime,
  buildCopilotKitRuntimeConfig,
  collectAllAguiEvents,
  devFallbackConfig,
  type Tool,
  type ToolParameter,
  type Student,
  type NewStudent,
  type AgentLessonPlan,
  type NewAgentLessonPlan,
  type AgentHomeworkItem,
  type NewAgentHomeworkItem,
  type AgentCbaPlan,
  type NewAgentCbaPlan,
  type AgentWellbeingCheckin,
  type NewAgentWellbeingCheckin,
  type AgentExamTimetable,
  type NewAgentExamTimetable,
  type AgentSenRecord,
  type NewAgentSenRecord,
  type TeacherWorkload,
  type NewTeacherWorkload,
  type ClassRegistry,
  type NewClassRegistry,
} from "./_base";
