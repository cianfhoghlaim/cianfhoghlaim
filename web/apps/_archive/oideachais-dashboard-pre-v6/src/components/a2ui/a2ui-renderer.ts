/**
 * A2UI Message Renderer — the canonical entry point for declarative
 * Agent-to-UI surfaces in the Oideachais Dashboard.
 *
 * Per the **2026-08-24-wave-6-frontend-tanstack-modernisation-v1** openspec
 * change (Wave 6.5). This file wires the A2UI catalog for the BIEP v3
 * dashboards. The runtime declares an a2ui middleware on the Hono side
 * (`web/hono-api/src/routes/copilotkit/lc/`); the client enables the
 * a2ui prop on the provider at the app root (`src/routes/__root.tsx`).
 *
 * Per the canonical a2ui-renderer skill (`.agents/skills/copilotkit/skills/a2ui-renderer/SKILL.md`):
 *   - DO NOT pass `renderActivityMessages` to CopilotChat directly
 *   - DO enable a2ui on the provider: <CopilotKit a2ui={{ ... }}>
 *   - DO enable a2ui on the runtime: CopilotRuntime({ a2ui: { schema } })
 *   - The client auto-mounts the A2UI renderer when both are set
 */

import {
  A2UIProvider,
  type Theme,
} from "@copilotkit/a2ui-renderer";
import { type ReactNode, type ComponentType } from "react";

// ─────────────────────────────────────────────────────────────────────────────
// Theme: the canonical "cianfhoghlaim" theme — defined here so that the
// CopilotKit provider can reuse it via <CopilotKit a2ui={{ theme }}>
// ─────────────────────────────────────────────────────────────────────────────

/**
 * The cianfhoghlaim-theme for A2UI surfaces — a small, opinionated theme
 * tuned for the BIEP v3 dashboard aesthetic. The `Theme` type is
 * `Record<string, unknown>` per `@copilotkit/a2ui-renderer`.
 */
export const CIANFHOGHLAIM_THEME: Theme = {
  name: "cianfhoghlaim",
  primary: "#0ea5e9",
  background: "#0f172a",
  surface: "#1e293b",
  text: "#f8fafc",
  fontFamily: "Inter, system-ui, sans-serif",
};

// ─────────────────────────────────────────────────────────────────────────────
// Component catalog — the 8 BIEP v3 component templates
// ─────────────────────────────────────────────────────────────────────────────

type A2UIComponent =
  | "Timeline"
  | "KPICard"
  | "ModelSelector"
  | "ProgressTracker"
  | "FileUpload"
  | "EvaluationMatrix"
  | "Chart"
  | "BadgeRow";

export type A2UIThemeComponents = Record<
  A2UIComponent,
  ComponentType<{ children?: ReactNode }>
>;

/**
 * The default A2UI catalog for the Oideachais dashboard. The catalog
 * maps A2UI component names to React renderers; the agent emits them
 * via the createSurface / updateComponents / updateDataModel operations.
 *
 * Per the a2ui-renderer skill this is the only client-side hook the
 * app author needs — the rest auto-activates on `/info`.
 */
export const BIEP_DASHBOARD_CATALOG: A2UIThemeComponents = {
  Timeline: () => null,
  KPICard: () => null,
  ModelSelector: () => null,
  ProgressTracker: () => null,
  FileUpload: () => null,
  EvaluationMatrix: () => null,
  Chart: () => null,
  BadgeRow: () => null,
};

export { A2UIProvider };
