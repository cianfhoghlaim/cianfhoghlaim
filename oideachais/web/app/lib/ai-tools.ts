/**
 * TanStack AI tool definitions for the Oideachais exam visualiser.
 *
 * Each tool wraps a TanStack Start server function that proxies the request
 * to MotherDuck / DuckLake. Tools are exposed to the CopilotKit runtime
 * via the runtime endpoint at `/api/copilotkit`.
 */

import { z } from "zod";
import {
  queryLakehouse,
  listExamMaterials,
  getMarkingSchemeSummary,
} from "../server/lakehouse";

export interface ToolDef {
  name: string;
  description: string;
  inputSchema: z.ZodTypeAny;
  execute: (input: unknown) => Promise<unknown>;
}

export const queryDuckLakeTool: ToolDef = {
  name: "queryDuckLake",
  description:
    "Run an arbitrary DuckDB SQL query against the oideachais lakehouse. " +
    "Use `examinations.all_exam_materials` and `curriculum.*` schemas.",
  inputSchema: z.object({ sql: z.string() }),
  execute: async (input) => {
    const { sql } = input as { sql: string };
    const rows = await queryLakehouse({ data: { sql, limit: 200 } });
    return { rows, rowCount: rows.length };
  },
};

export const listExamMaterialsTool: ToolDef = {
  name: "listExamMaterials",
  description:
    "List exam materials for a subject / year / level. Use this for " +
    "filtering before doing deeper analysis.",
  inputSchema: z.object({
    subject: z.string(),
    year: z.number().int(),
    level: z
      .enum(["leaving_certificate", "junior_cycle", "leaving_certificate_applied"])
      .default("leaving_certificate"),
    materialType: z.enum(["exam_papers", "marking_schemes"]).default("exam_papers"),
  }),
  execute: async (input) => {
    const { subject, year, level, materialType } = input as {
      subject: string;
      year: number;
      level: "leaving_certificate" | "junior_cycle" | "leaving_certificate_applied";
      materialType: "exam_papers" | "marking_schemes";
    };
    const rows = await listExamMaterials({
      data: { subject, year, level, materialType },
    });
    return { materials: rows, count: rows.length };
  },
};

export const getMarkingSchemeSummaryTool: ToolDef = {
  name: "getMarkingSchemeSummary",
  description:
    "Return a per-subject marking-scheme summary: canonical rubric " +
    "(PCLM / SRPs / equation steps / mandatory keywords) and most recent " +
    "scheme years in the lakehouse.",
  inputSchema: z.object({ subject: z.string() }),
  execute: async (input) => {
    const { subject } = input as { subject: string };
    return getMarkingSchemeSummary({ data: { subject } });
  },
};

export const compareHigherVsOrdinaryTool: ToolDef = {
  name: "compareHigherVsOrdinary",
  description:
    "Compare Higher Level exam papers and Ordinary Level marking schemes " +
    "for a given subject / year. Returns both lists side by side for the " +
    "AGUI renderer.",
  inputSchema: z.object({ subject: z.string(), year: z.number().int() }),
  execute: async (input) => {
    const { subject, year } = input as { subject: string; year: number };
    const [papers, schemes] = await Promise.all([
      listExamMaterials({
        data: { subject, year, level: "leaving_certificate", materialType: "exam_papers" },
      }),
      listExamMaterials({
        data: { subject, year, level: "leaving_certificate", materialType: "marking_schemes" },
      }),
    ]);
    return { papers, schemes };
  },
};

export const allTools: ToolDef[] = [
  queryDuckLakeTool,
  listExamMaterialsTool,
  getMarkingSchemeSummaryTool,
  compareHigherVsOrdinaryTool,
];
