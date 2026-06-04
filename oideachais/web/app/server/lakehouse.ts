/**
 * Lakehouse server functions.
 *
 * `queryLakehouse` runs a DuckDB SQL statement against either:
 *  - the local DuckLake destination (Garage S3 + PostgreSQL catalog), or
 *  - a shared MotherDuck database (when MOTHERDUCK_ENABLED=true).
 *
 * Routing follows the runtime selector pattern in the marimo notebooks
 * (`exam_papers_explorer.py` etc.).
 */

import { createServerFn } from "@tanstack/react-start";
import { z } from "zod";

const SUBJECT_RUBRIC: Record<string, string> = {
  english: "PCLM: Purpose, Coherence, Language, Mechanics (each band ~25%)",
  gaeilge: "Cumarsáid · Léamhthuiscint · Litríocht · Gramadach",
  mathematics: "Equation steps + final numerical answer (mark per step)",
  biology: "Mandatory keywords (10+) · experiment steps · diagram labels",
  chemistry:
    "Balanced equations · state symbols · calculation steps · significant figures",
  physics: "Definitions · units · formula manipulation · significant figures",
  geography:
    "SRPs (Significant Relevant Points): 2 marks per distinct factual point",
  history: "SRPs · historiographical perspective · primary source citation",
  french: "Compréhension écrite · expression écrite · grammaire · vocabulaire",
  german: "Leseverstehen · Schreiben · Grammatik · Wortschatz",
  spanish: "Comprensión lectora · expresión escrita · gramática · vocabulario",
  irish: "Léamh · Scríbhneoireacht · Gramadach · Líofacht",
};

interface SqlRow {
  [key: string]: string | number | boolean | null;
}

async function runDuckLakeQuery(sql: string, limit: number): Promise<SqlRow[]> {
  const useMotherduck =
    (process.env.MOTHERDUCK_ENABLED ?? "false").toLowerCase() === "true";

  if (useMotherduck) {
    const token = process.env.MOTHERDUCK_TOKEN;
    if (!token) {
      throw new Error("MOTHERDUCK_TOKEN required when MOTHERDUCK_ENABLED=true");
    }
    const res = await fetch("https://api.motherduck.com/v1/query", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ sql: `${sql} LIMIT ${limit}` }),
    });
    if (!res.ok) {
      throw new Error(`MotherDuck query ${res.status}: ${await res.text()}`);
    }
    const payload = (await res.json()) as { rows?: SqlRow[] };
    return payload.rows ?? [];
  }

  // Local DuckDB WASM path
  const duckdb = await import("@duckdb/duckdb-wasm");
  const workerUrl = (
    await import("@duckdb/duckdb-wasm/dist/duckdb-browser-mvp?url")
  ).default;
  const worker = new Worker(workerUrl);
  const logger = new duckdb.ConsoleLogger();
  const bundle = await duckdb.selectBundle(duckdb.getJsDelivrBundles());
  const db = new duckdb.AsyncDuckDB(logger, worker);
  await db.instantiate(bundle as never, new duckdb.ConsoleLogger() as never);
  const conn = await db.connect();
  try {
    const trimmed = sql.trim().replace(/;$/, "");
    const bounded = /limit\s+\d+/i.test(trimmed)
      ? trimmed
      : `${trimmed} LIMIT ${limit}`;
    const result = await conn.query(bounded);
    return result.toArray().map((row: { toJSON: () => Record<string, unknown> }) =>
      Object.fromEntries(
        Object.entries(row.toJSON()).map(([k, v]) => [k, v as SqlRow[string]]),
      ),
    );
  } finally {
    await conn.close();
    await db.terminate();
    worker.terminate();
  }
}

// Server function factory helpers — TanStack Start's `createServerFn`
// pattern. The new API uses `inputValidator(zodSchema).handler(async ({ data }) => ...)`
// rather than the older `.validator(schema).handler()` form.
const querySchema = z.object({
  sql: z.string().min(1).max(10_000),
  limit: z.number().int().min(1).max(1000).default(200),
});

export const queryLakehouse = createServerFn({ method: "POST" })
  .inputValidator(querySchema)
  .handler(async ({ data }: { data: z.infer<typeof querySchema> }) => {
    return runDuckLakeQuery(data.sql, data.limit);
  });

const listExamMaterialsSchema = z.object({
  subject: z.string().min(1).max(120),
  year: z.number().int().min(1999).max(2030),
  level: z
    .enum(["leaving_certificate", "junior_cycle", "leaving_certificate_applied"])
    .default("leaving_certificate"),
  materialType: z.enum(["exam_papers", "marking_schemes"]).default("exam_papers"),
});

export const listExamMaterials = createServerFn({ method: "POST" })
  .inputValidator(listExamMaterialsSchema)
  .handler(async ({ data }: { data: z.infer<typeof listExamMaterialsSchema> }) => {
    const safeSubject = data.subject.replace(/'/g, "''");
    const sql = `
      SELECT level, subject, year, material_type, pdf_url, title,
             scraper, status, scraped_at
      FROM examinations.all_exam_materials
      WHERE subject = '${safeSubject}'
        AND year = ${data.year}
        AND level = '${data.level}'
        AND material_type = '${data.materialType}'
      ORDER BY pdf_url
    `;
    return runDuckLakeQuery(sql, 200);
  });

const markingSchemeSchema = z.object({
  subject: z.string().min(1).max(120),
});

export const getMarkingSchemeSummary = createServerFn({ method: "POST" })
  .inputValidator(markingSchemeSchema)
  .handler(async ({ data }: { data: z.infer<typeof markingSchemeSchema> }) => {
    const rubric = SUBJECT_RUBRIC[data.subject.toLowerCase()] ?? "Generic SRPs";
    const safeSubject = data.subject.replace(/'/g, "''");
    const sql = `
      SELECT year, count(*) AS schemes
      FROM examinations.all_exam_materials
      WHERE subject = '${safeSubject}'
        AND material_type = 'marking_schemes'
        AND pdf_url IS NOT NULL AND pdf_url != ''
      GROUP BY year
      ORDER BY year DESC
      LIMIT 20
    `;
    const recent = await runDuckLakeQuery(sql, 20);
    return {
      subject: data.subject,
      rubric,
      recentYears: recent.map((r) => ({
        year: r.year as number,
        schemes: r.schemes as number,
      })),
    };
  });

export const listBuckets = createServerFn({ method: "GET" }).handler(async () => {
  const endpoint = process.env.AWS_ENDPOINT_URL ?? "http://localhost:3900";
  const accessKey = process.env.GARAGE_ACCESS_KEY_ID ?? "";
  const secretKey = process.env.GARAGE_SECRET_ACCESS_KEY ?? "";
  if (!accessKey || !secretKey) return [];
  const auth = Buffer.from(`${accessKey}:${secretKey}`).toString("base64");
  const res = await fetch(`${endpoint}/`, {
    headers: { Authorization: `Basic ${auth}` },
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`Garage list_buckets ${res.status}: ${await res.text()}`);
  }
  const body = (await res.text()) as string;
  const names: string[] = [];
  for (const m of body.matchAll(/<Name>([^<]+)<\/Name>/g)) {
    names.push(m[1]);
  }
  return names;
});
