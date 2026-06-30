#!/usr/bin/env bun
// export-marimo-wasm.ts — Export marimo notebooks to WASM bundles.
//
// Walks the monorepo for marimo notebooks (notebooks/**/*.py, marimo/**/*.py)
// and exports each one to HTML-WASM via `marimo export html-wasm`. The
// resulting bundles are emitted to croilar/apps/web/public/wasm/<slug>/index.html
// so the portal's /notebooks/$slug route can render them inline.
//
// Usage:
//   bun run croilar/scripts/export-marimo-wasm.ts
//   bun run croilar/scripts/export-marimo-wasm.ts --project croilar
//   bun run croilar/scripts/export-marimo-wasm.ts --force
//   CROILAR_REPO_ROOT=/path/to/repo bun run croilar/scripts/export-marimo-wasm.ts
//
// Env:
//   CROILAR_REPO_ROOT — repo root (defaults to ../../ from this script)

import { readdir, readFile, mkdir, stat, writeFile } from "node:fs/promises";
import { existsSync } from "node:fs";
import { join, relative, resolve, basename } from "node:path";
import { spawn } from "node:child_process";

interface ExportOptions {
  repoRoot: string;
  project?: string;
  force: boolean;
  outputRoot: string;
}

const NOTEBOOK_ROOTS: Record<string, string[]> = {
  tuatha: ["tuatha/crypteolas/marimo"],
  oideachais: ["oideachais/marimo", "oideachais/notebooks"],
  croilar: ["croilar/notebooks"],
  meaisinfhoghlaim: ["meaisínfhoghlaim/notebooks"],
};

function parseArgs(argv: string[]): ExportOptions {
  const envRoot = process.env.CROILAR_REPO_ROOT;
  const scriptDir = import.meta.dir;
  const defaultRoot = resolve(scriptDir, "../..");
  const opts: ExportOptions = {
    repoRoot: envRoot && envRoot.length > 0 ? envRoot : defaultRoot,
    force: false,
    outputRoot: resolve(
      envRoot && envRoot.length > 0 ? envRoot : defaultRoot,
      "croilar/apps/portal/public/wasm",
    ),
  };
  for (let i = 0; i < argv.length; i += 1) {
    const a = argv[i];
    if (a === "--project") opts.project = argv[++i];
    else if (a === "--force") opts.force = true;
    else if (a === "--out") opts.outputRoot = resolve(argv[++i]!);
    else if (a === "--repo-root") opts.repoRoot = argv[++i]!;
  }
  return opts;
}

async function pathExists(p: string): Promise<boolean> {
  try {
    await stat(p);
    return true;
  } catch {
    return false;
  }
}

async function listNotebooks(root: string): Promise<string[]> {
  const out: string[] = [];
  async function walk(dir: string) {
    let entries;
    try {
      entries = await readdir(dir, { withFileTypes: true });
    } catch {
      return;
    }
    for (const entry of entries) {
      const p = join(dir, entry.name);
      if (entry.isDirectory()) {
        if (
          entry.name === "node_modules" ||
          entry.name === ".git" ||
          entry.name === "__pycache__" ||
          entry.name === "venv" ||
          entry.name === ".venv"
        ) {
          continue;
        }
        await walk(p);
      } else if (entry.isFile() && p.endsWith(".py") && !p.includes("__")) {
        const text = await readFile(p, "utf-8");
        if (text.includes("marimo.App") || text.includes("@app.cell")) {
          out.push(p);
        }
      }
    }
  }
  await walk(root);
  return out;
}

function notebookSlug(file: string, repoRoot: string): string {
  const rel = relative(repoRoot, file)
    .replace(/\.py$/, "")
    .replace(/^[^/]+\/[^/]+\//, "") // strip "<project>/<subfolder>/"
    .replace(/\//g, "__");
  return rel;
}

async function exportOne(
  file: string,
  slug: string,
  opts: ExportOptions,
): Promise<{ ok: true; bytes: number } | { ok: false; error: string }> {
  const outDir = join(opts.outputRoot, slug);
  const indexHtml = join(outDir, "index.html");
  if (!opts.force && existsSync(indexHtml)) {
    const st = await stat(indexHtml);
    return { ok: true, bytes: st.size };
  }
  await mkdir(outDir, { recursive: true });
  return new Promise((resolvePromise) => {
    const proc = spawn(
      "marimo",
      ["export", "html-wasm", file, "--no-show-code", "-o", outDir],
      { stdio: ["ignore", "pipe", "pipe"] },
    );
    let stderr = "";
    proc.stderr.on("data", (chunk) => (stderr += chunk.toString()));
    proc.on("error", (e) => resolvePromise({ ok: false, error: String(e) }));
    proc.on("close", async (code) => {
      if (code !== 0) {
        resolvePromise({ ok: false, error: `exit ${code}: ${stderr.slice(-512)}` });
        return;
      }
      const st = await stat(indexHtml);
      resolvePromise({ ok: true, bytes: st.size });
    });
  });
}

async function writeManifest(opts: ExportOptions, results: { slug: string; file: string; ok: boolean; bytes: number; error?: string }[]) {
  const manifestPath = join(opts.outputRoot, "manifest.json");
  const manifest = {
    generatedAt: new Date().toISOString(),
    notebooks: results,
  };
  await writeFile(manifestPath, JSON.stringify(manifest, null, 2), "utf-8");
}

async function main() {
  const opts = parseArgs(process.argv.slice(2));
  if (!(await pathExists(opts.repoRoot))) {
    throw new Error(`CROILAR_REPO_ROOT not found: ${opts.repoRoot}`);
  }
  await mkdir(opts.outputRoot, { recursive: true });

  const projects = opts.project ? [opts.project] : Object.keys(NOTEBOOK_ROOTS);
  const results: { slug: string; file: string; ok: boolean; bytes: number; error?: string }[] = [];

  for (const project of projects) {
    const roots = NOTEBOOK_ROOTS[project] ?? [];
    for (const root of roots) {
      const abs = resolve(opts.repoRoot, root);
      if (!(await pathExists(abs))) continue;
      const notebooks = await listNotebooks(abs);
      for (const file of notebooks) {
        const slug = notebookSlug(file, opts.repoRoot);
        const r = await exportOne(file, slug, opts);
        if (r.ok) {
          results.push({ slug, file: relative(opts.repoRoot, file), ok: true, bytes: r.bytes });
          console.error(`  ✓ ${slug} (${r.bytes} bytes)`);
        } else {
          results.push({ slug, file: relative(opts.repoRoot, file), ok: false, bytes: 0, error: r.error });
          console.error(`  ✗ ${slug}: ${r.error}`);
        }
      }
    }
  }

  await writeManifest(opts, results);
  const ok = results.filter((r) => r.ok).length;
  const total = results.length;
  console.error(
    `\nExported ${ok}/${total} notebooks to ${opts.outputRoot} (manifest: manifest.json)`,
  );
  process.stdout.write(
    JSON.stringify({
      ok,
      total,
      outputRoot: opts.outputRoot,
      manifest: "manifest.json",
    }),
  );
}

main().catch((e) => {
  console.error(e instanceof Error ? e.message : String(e));
  process.exit(1);
});
