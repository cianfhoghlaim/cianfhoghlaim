/**
 * scripts/schema-codegen/index.ts
 *
 * The canonical orchestrator for the schema-driven codegen pipeline
 * (per the 2026-08-13-web-monorepo-consolidation-and-agent-integration-v1
 * change, Phase O).
 *
 * Calls the 5 sub-generators in dependency order:
 *
 *   1. baml-to-ts.ts            — wraps `baml-cli generate`
 *   2. convex-from-zod.ts      — Zod → Convex validator generator
 *   3. copilotkit-actions.ts   — Zod → CopilotKit action registry generator
 *   4. ag-ui-types.ts          — Zod → AG-UI event type generator
 *   5. per-subject-routes.ts   — Per-subject route generator
 *
 * The pipeline is idempotent — running it twice on the same input
 * produces byte-identical output.
 *
 * Usage:
 *   bun run scripts/schema-codegen/index.ts               # default: all 5 steps
 *   bun run scripts/schema-codegen/index.ts --step <1-5>  # run a single step
 *   bun run scripts/schema-codegen/index.ts --subject mathematics  # limit to one subject
 *   bun run scripts/schema-codegen/index.ts --dry-run     # preview only
 *   bun run scripts/schema-codegen/index.ts --help
 *
 * Reference:
 *   openspec/changes/2026-08-13-web-monorepo-consolidation-and-agent-integration-v1/
 *   specs/schema-driven-codegen/spec.md
 */

import * as path from "node:path";

import { runBamlToTs } from "./baml-to-ts";
import { runConvexFromZod } from "./convex-from-zod";
import { runCopilotKitActions } from "./copilotkit-actions";
import { runAgUiTypes } from "./ag-ui-types";
import { runPerSubjectRoutes } from "./per-subject-routes";

// =============================================================================
// CLI arg parsing
// =============================================================================

interface CliArgs {
  repoRoot: string;
  step: number | "all";
  subject: string | null;
  stage: string | null;
  dryRun: boolean;
  help: boolean;
}

function parseArgs(argv: readonly string[]): CliArgs {
  const args: CliArgs = {
    repoRoot: process.cwd(),
    step: "all",
    subject: null,
    stage: null,
    dryRun: false,
    help: false,
  };

  for (let i = 2; i < argv.length; i++) {
    const arg = argv[i];
    switch (arg) {
      case "--help":
      case "-h":
        args.help = true;
        break;
      case "--dry-run":
        args.dryRun = true;
        break;
      case "--step": {
        const n = Number(argv[++i]);
        if (!Number.isFinite(n) || n < 1 || n > 5) {
          throw new Error(`--step must be 1-5, got ${argv[i]}`);
        }
        args.step = n;
        break;
      }
      case "--subject":
        args.subject = argv[++i] ?? null;
        break;
      case "--stage":
        args.stage = argv[++i] ?? null;
        break;
      case "--root":
        args.repoRoot = path.resolve(argv[++i] ?? ".");
        break;
      default:
        throw new Error(`Unknown arg: ${arg}`);
    }
  }
  return args;
}

function printHelp(): void {
  console.log("schema-codegen — the BAML → Zod → Convex → CopilotKit → AG-UI pipeline");

  console.log("");

  console.log("Usage:");
  console.log("  bun run scripts/schema-codegen/index.ts                       # default: all 5 steps");
  console.log("  bun run scripts/schema-codegen/index.ts --step <1-5>          # run a single step");
  console.log("  bun run scripts/schema-codegen/index.ts --subject mathematics  # limit to one subject");
  console.log("  bun run scripts/schema-codegen/index.ts --stage lc             # limit to one stage");
  console.log("  bun run scripts/schema-codegen/index.ts --dry-run             # preview only");
  console.log("  bun run scripts/schema-codegen/index.ts --help");

  console.log("");

  console.log("Steps (run in dependency order):");
  console.log("  1. baml-to-ts            — wraps baml-cli generate (TypeScript target)");
  console.log("  2. convex-from-zod      — Zod → Convex table validator generator");
  console.log("  3. copilotkit-actions   — Zod → CopilotKit useCopilotAction registry generator");
  console.log("  4. ag-ui-types          — Zod → AG-UI 17-event-type generator");
  console.log("  5. per-subject-routes   — Per-subject TanStack Start route generator");

  console.log("");

  console.log("Reference:");
  console.log("  openspec/changes/2026-08-13-web-monorepo-consolidation-and-agent-integration-v1/");
  console.log("  specs/schema-driven-codegen/spec.md");
}

// =============================================================================
// The 60 subject × 4-stage matrix (the canonical coverage table)
// =============================================================================

export type Stage = "lc" | "jc" | "gcse" | "a-level";

export interface SubjectRow {
  stage: Stage;
  subject: string;
  display_name: string;
  ncca_code: string;
  languages: ReadonlyArray<"en" | "ga">;
}

const SUBJECT_MATRIX: ReadonlyArray<SubjectRow> = [
  // 14 LC subjects
  { stage: "lc", subject: "mathematics",      display_name: "Mathematics",      ncca_code: "LC-MATH-LO", languages: ["en", "ga"] },
  { stage: "lc", subject: "chemistry",        display_name: "Chemistry",        ncca_code: "LC-CHEM-LO", languages: ["en", "ga"] },
  { stage: "lc", subject: "physics",         display_name: "Physics",         ncca_code: "LC-PHYS-LO", languages: ["en", "ga"] },
  { stage: "lc", subject: "biology",         display_name: "Biology",         ncca_code: "LC-BIO-LO",  languages: ["en", "ga"] },
  { stage: "lc", subject: "english",         display_name: "English",         ncca_code: "LC-ENGL-LO", languages: ["en", "ga"] },
  { stage: "lc", subject: "gaeilge",         display_name: "Gaeilge",         ncca_code: "LC-GAEL-LO", languages: ["ga"] },
  { stage: "lc", subject: "french",          display_name: "French",          ncca_code: "LC-FREN-LO", languages: ["en", "ga"] },
  { stage: "lc", subject: "history",         display_name: "History",         ncca_code: "LC-HIST-LO", languages: ["en", "ga"] },
  { stage: "lc", subject: "geography",       display_name: "Geography",       ncca_code: "LC-GEOG-LO", languages: ["en", "ga"] },
  { stage: "lc", subject: "business",        display_name: "Business",        ncca_code: "LC-BUS-LO",  languages: ["en", "ga"] },
  { stage: "lc", subject: "accounting",      display_name: "Accounting",      ncca_code: "LC-ACCT-LO", languages: ["en", "ga"] },
  { stage: "lc", subject: "art",             display_name: "Art",             ncca_code: "LC-ART-LO",  languages: ["en", "ga"] },
  { stage: "lc", subject: "music",           display_name: "Music",           ncca_code: "LC-MUS-LO",  languages: ["en", "ga"] },
  { stage: "lc", subject: "computer_science",display_name:"Computer Science",ncca_code: "LC-COMP-LO", languages: ["en", "ga"] },
  // 8 JC subjects
  { stage: "jc", subject: "mathematics",      display_name: "Mathematics",     ncca_code: "JC-MATH-LO", languages: ["en", "ga"] },
  { stage: "jc", subject: "english",         display_name: "English",         ncca_code: "JC-ENGL-LO", languages: ["en", "ga"] },
  { stage: "jc", subject: "gaeilge",         display_name: "Gaeilge",         ncca_code: "JC-GAEL-LO", languages: ["ga"] },
  { stage: "jc", subject: "science",         display_name: "Science",         ncca_code: "JC-SCI-LO",  languages: ["en", "ga"] },
  { stage: "jc", subject: "history",         display_name: "History",         ncca_code: "JC-HIST-LO", languages: ["en", "ga"] },
  { stage: "jc", subject: "geography",       display_name: "Geography",       ncca_code: "JC-GEOG-LO", languages: ["en", "ga"] },
  { stage: "jc", subject: "french",          display_name: "French",          ncca_code: "JC-FREN-LO", languages: ["en", "ga"] },
  { stage: "jc", subject: "business",        display_name: "Business",        ncca_code: "JC-BUS-LO",  languages: ["en", "ga"] },
  // 9 GCSE subjects
  { stage: "gcse", subject: "mathematics",      display_name: "Mathematics",     ncca_code: "GCSE-MATH", languages: ["en"] },
  { stage: "gcse", subject: "english_literature",display_name: "English Literature", ncca_code: "GCSE-ENGLIT", languages: ["en"] },
  { stage: "gcse", subject: "english_language", display_name: "English Language", ncca_code: "GCSE-ENGLANG", languages: ["en"] },
  { stage: "gcse", subject: "biology",          display_name: "Biology",         ncca_code: "GCSE-BIO",  languages: ["en"] },
  { stage: "gcse", subject: "chemistry",        display_name: "Chemistry",       ncca_code: "GCSE-CHEM", languages: ["en"] },
  { stage: "gcse", subject: "physics",          display_name: "Physics",         ncca_code: "GCSE-PHYS", languages: ["en"] },
  { stage: "gcse", subject: "history",          display_name: "History",         ncca_code: "GCSE-HIST", languages: ["en"] },
  { stage: "gcse", subject: "geography",        display_name: "Geography",       ncca_code: "GCSE-GEOG", languages: ["en"] },
  { stage: "gcse", subject: "modern_foreign_languages", display_name: "Modern Foreign Languages", ncca_code: "GCSE-MFL", languages: ["en"] },
  // 15+ A-Level subjects (the canonical English A-Level set)
  { stage: "a-level", subject: "mathematics",            display_name: "Mathematics",          ncca_code: "AL-MATH",      languages: ["en"] },
  { stage: "a-level", subject: "further_mathematics",     display_name: "Further Mathematics",  ncca_code: "AL-FMATH",      languages: ["en"] },
  { stage: "a-level", subject: "chemistry",              display_name: "Chemistry",            ncca_code: "AL-CHEM",      languages: ["en"] },
  { stage: "a-level", subject: "biology",                display_name: "Biology",              ncca_code: "AL-BIO",       languages: ["en"] },
  { stage: "a-level", subject: "physics",                display_name: "Physics",              ncca_code: "AL-PHYS",      languages: ["en"] },
  { stage: "a-level", subject: "english_literature",     display_name: "English Literature",   ncca_code: "AL-ENGLIT",    languages: ["en"] },
  { stage: "a-level", subject: "english_language",       display_name: "English Language",     ncca_code: "AL-ENGLANG",   languages: ["en"] },
  { stage: "a-level", subject: "history",                display_name: "History",              ncca_code: "AL-HIST",      languages: ["en"] },
  { stage: "a-level", subject: "geography",              display_name: "Geography",            ncca_code: "AL-GEOG",      languages: ["en"] },
  { stage: "a-level", subject: "psychology",             display_name: "Psychology",           ncca_code: "AL-PSYCH",     languages: ["en"] },
  { stage: "a-level", subject: "economics",              display_name: "Economics",            ncca_code: "AL-ECON",      languages: ["en"] },
  { stage: "a-level", subject: "business",               display_name: "Business",             ncca_code: "AL-BUS",       languages: ["en"] },
  { stage: "a-level", subject: "politics",               display_name: "Politics",             ncca_code: "AL-POL",       languages: ["en"] },
  { stage: "a-level", subject: "sociology",              display_name: "Sociology",            ncca_code: "AL-SOC",       languages: ["en"] },
  { stage: "a-level", subject: "modern_foreign_languages",display_name:"Modern Foreign Languages",ncca_code: "AL-MFL",     languages: ["en"] },
];

export function getSubjectMatrix(): ReadonlyArray<SubjectRow> {
  return SUBJECT_MATRIX;
}

// =============================================================================
// The main orchestrator
// =============================================================================

interface StepResult {
  step: number;
  name: string;
  duration_ms: number;
  files_emitted: number;
  subjects_emitted: number;
}

export async function runAll(
  repoRoot: string,
  subjectFilter: string | null,
  stageFilter: string | null,
  dryRun: boolean,
): Promise<StepResult[]> {
  const subjects = SUBJECT_MATRIX.filter(
    (row) =>
      (!subjectFilter || row.subject === subjectFilter) &&
      (!stageFilter || row.stage === stageFilter),
  );

  console.log(
    `schema-codegen: ${subjects.length} subject(s)` +
      (stageFilter ? ` [stage=${stageFilter}]` : "") +
      (subjectFilter ? ` [subject=${subjectFilter}]` : "") +
      (dryRun ? " [dry-run]" : ""),
  );

  const results: StepResult[] = [];

  // Step 1: BAML → TypeScript (always first — feeds step 2-5)
  {
    const start = Date.now();
    const out = await runBamlToTs(repoRoot, subjects, dryRun);
    results.push({
      step: 1,
      name: "baml-to-ts",
      duration_ms: Date.now() - start,
      files_emitted: out.length,
      subjects_emitted: subjects.length,
    });
  }

  // Step 2: Zod → Convex (depends on step 1's types)
  {
    const start = Date.now();
    const out = await runConvexFromZod(repoRoot, subjects, dryRun);
    results.push({
      step: 2,
      name: "convex-from-zod",
      duration_ms: Date.now() - start,
      files_emitted: out.length,
      subjects_emitted: subjects.length,
    });
  }

  // Step 3: Zod → CopilotKit actions
  {
    const start = Date.now();
    const out = await runCopilotKitActions(repoRoot, subjects, dryRun);
    results.push({
      step: 3,
      name: "copilotkit-actions",
      duration_ms: Date.now() - start,
      files_emitted: out.length,
      subjects_emitted: subjects.length,
    });
  }

  // Step 4: Zod → AG-UI types
  {
    const start = Date.now();
    const out = await runAgUiTypes(repoRoot, subjects, dryRun);
    results.push({
      step: 4,
      name: "ag-ui-types",
      duration_ms: Date.now() - start,
      files_emitted: out.length,
      subjects_emitted: subjects.length,
    });
  }

  // Step 5: Per-subject routes
  {
    const start = Date.now();
    const out = await runPerSubjectRoutes(repoRoot, subjects, dryRun);
    results.push({
      step: 5,
      name: "per-subject-routes",
      duration_ms: Date.now() - start,
      files_emitted: out.length,
      subjects_emitted: subjects.length,
    });
  }

  return results;
}

export function printResults(results: StepResult[]): void {
  console.log("\n=== schema-codegen results ===");
  for (const r of results) {
    console.log(
      `  step ${r.step} (${r.name.padEnd(22)}): ` +
        `${String(r.files_emitted).padStart(4)} files, ` +
        `${String(r.subjects_emitted).padStart(2)} subjects, ` +
        `${String(r.duration_ms).padStart(5)}ms`,
    );
  }
  console.log(`  total: ${results.length} steps`);
}

// =============================================================================
// CLI entrypoint
// =============================================================================

export async function main(argv: readonly string[] = process.argv): Promise<void> {
  let args: CliArgs;
  try {
    args = parseArgs(argv);
  } catch (e) {
    console.error(String(e));
    printHelp();
    process.exit(2);
  }

  if (args.help) {
    printHelp();
    return;
  }

  const start = Date.now();
  const results = await runAll(
    args.repoRoot,
    args.subject,
    args.stage,
    args.dryRun,
  );
  printResults(results);
  console.log(`\nelapsed: ${Date.now() - start}ms`);
}

// Run when invoked directly (not when imported).
if (import.meta.main) {
  void main();
}
