/**
 * scripts/fix-legacy-ts1005.ts
 *
 * One-shot fix for the 24 pre-existing `TS1005` errors in the
 * cianfhoghlaim-leaving-cert per-subject routes. Each file ends with:
 *
 *     ...
 *     );
 *
 *     // (no further navigation)
 *
 * but the function `XxxPage()` is missing its closing `}`. This script
 * appends `}` to the end of each of the 24 files.
 *
 * Pre-flight (run from repo root):
 *   bunx tsc --noEmit -p web/apps/cianfhoghlaim-leaving-cert/apps/web/tsconfig.json
 *   # Expected: 24 errors of the form `(34,1): error TS1005: '}' expected.`
 *
 * Post-flight (re-run the same tsc command):
 *   # Expected: 0 errors.
 *
 * Usage:
 *   bun run scripts/fix-legacy-ts1005.ts            # fix all 24
 *   bun run scripts/fix-legacy-ts1005.ts --check   # verify (no writes)
 */
import * as fs from "node:fs/promises";
import * as path from "node:path";

const SUBJECTS = [
  "mathematics",
  "chemistry",
  "geography",
  "gaeilge",
  "english",
  "computer_science",
] as const;

const FILES = [
  "syllabus",
  "exam-papers",
  "marking-schemes",
  "study-plan",
] as const;

const ROUTE_DIR =
  "web/apps/cianfhoghlaim-leaving-cert/apps/web/src/routes/en/subjects";

interface FileResult {
  path: string;
  before: string;
  after: string;
  changed: boolean;
}

async function readFile(repoRoot: string, relativePath: string): Promise<string> {
  return fs.readFile(path.join(repoRoot, relativePath), "utf8");
}

async function writeFile(
  repoRoot: string,
  relativePath: string,
  content: string,
): Promise<void> {
  await fs.writeFile(path.join(repoRoot, relativePath), content, "utf8");
}

async function main(): Promise<void> {
  const repoRoot = path.resolve(process.cwd());
  const check = process.argv.includes("--check");

  const results: FileResult[] = [];

  for (const subject of SUBJECTS) {
    for (const file of FILES) {
      const rel = `${ROUTE_DIR}/${subject}/${file}.tsx`;
      const abs = path.join(repoRoot, rel);
      const before = await fs.readFile(abs, "utf8");

      // Pattern: the file ends with `  );\n\n// (no further navigation)\n`
      // (i.e. the return statement ends but the function body never closes).
      // Fix: append `}\n` at end of file (before EOF).
      let after: string;
      let changed = false;
      if (!before.trimEnd().endsWith("}")) {
        // Determine the source of the trailing comment / blank lines
        // and insert the closing brace BEFORE the trailing comment block.
        const lines = before.split("\n");
        // Find the index of the first trailing comment line (// ...)
        let firstCommentLine = -1;
        for (let i = lines.length - 1; i >= 0; i--) {
          const line = lines[i]!;
          const trimmed = line.trim();
          if (trimmed === "") continue;
          if (trimmed.startsWith("//")) {
            firstCommentLine = i;
            continue;
          }
          // Found the last non-comment content line.
          break;
        }
        if (firstCommentLine > 0) {
          // Insert `}` right before the trailing comment block.
          after = [...lines.slice(0, firstCommentLine), "}", ...lines.slice(firstCommentLine)].join("\n");
        } else {
          // No trailing comment — just append `}\n`.
          after = before.trimEnd() + "\n}\n";
        }
        if (after !== before) changed = true;
      } else {
        after = before;
      }
      results.push({ path: rel, before, after, changed });
    }
  }

  const changed = results.filter((r) => r.changed);
  console.log(`Found ${changed.length} files missing the closing '}'`);

  if (check) {
    process.exit(changed.length === 0 ? 0 : 1);
  }

  for (const r of changed) {
    await writeFile(repoRoot, r.path, r.after);
    console.log(`  fixed: ${r.path}`);
  }

  console.log(`Done — ${changed.length} files written.`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});