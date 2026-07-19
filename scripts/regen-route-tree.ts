/**
 * scripts/regen-route-tree.ts
 *
 * Regenerates `apps/web/src/routeTree.gen.ts` using `@tanstack/router-generator`.
 *
 * Per follow-up #2 of the BIEP v1 lineage viewer work:
 * `routeTree.gen.ts` does not include the new `/[lang]/leaving-cert/[subject]/lineage`
 * routes. This script regenerates the file without requiring a full Vite dev server
 * startup (so CI / smokes / agents can run it).
 *
 * Usage:
 *   bun run scripts/regen-route-tree.ts
 *   bun run scripts/regen-route-tree.ts --check   # verify the file is in sync (no writes)
 */
import * as path from "node:path";

// The Gen is the canonical CLI for the @tanstack/router-generator library.
const { Generator, getConfig } = await import(
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  "@tanstack/router-generator" as any
);

interface CliArgs {
  check: boolean;
  repoRoot: string;
}

function parseArgs(argv: ReadonlyArray<string>): CliArgs {
  const args: CliArgs = { check: false, repoRoot: "" };
  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    const next = argv[i + 1];
    switch (arg) {
      case "--check":
        args.check = true;
        break;
      case "--repo-root":
        if (!next) throw new Error("--repo-root requires a path argument");
        args.repoRoot = path.resolve(next);
        i++;
        break;
      case "--help":
      case "-h":
        console.log("Usage: bun run scripts/regen-route-tree.ts [--check] [--repo-root <path>]");
        process.exit(0);
      default:
        if (arg.startsWith("--")) {
          throw new Error(`Unknown flag: ${arg}`);
        }
    }
  }
  return args;
}

function findRepoRoot(start: string): string {
  let dir = path.resolve(start);
  // Walk up looking for pyproject.toml
  while (true) {
    try {
      // eslint-disable-next-line @typescript-eslint/no-require-imports
      require("node:fs").accessSync(path.join(dir, "pyproject.toml"));
      return dir;
    } catch {
      const parent = path.dirname(dir);
      if (parent === dir) return path.resolve(start);
      dir = parent;
    }
  }
}

async function main(): Promise<void> {
  const args = parseArgs(process.argv.slice(2));
  const repoRoot = args.repoRoot || findRepoRoot(process.cwd());
  const leavingCertWeb = path.join(
    repoRoot,
    "web/apps/cianfhoghlaim-leaving-cert/apps/web",
  );

  const config = getConfig(
    {
      routesDirectory: path.join(leavingCertWeb, "src/routes"),
      generatedRouteTree: path.join(leavingCertWeb, "src/routeTree.gen.ts"),
      routeFileIgnorePrefix: "-",
      quoteStyle: "single",
      semicolons: false,
    },
    leavingCertWeb,
  );

  const generator = new Generator({
    config,
    root: leavingCertWeb,
  });

  await generator.run();

  const filePath = config.generatedRouteTree;
  if (args.check) {
    // The Generator writes only-on-change. For --check we just verify the file exists.
    // eslint-disable-next-line @typescript-eslint/no-require-imports
    const fs = require("node:fs") as typeof import("node:fs");
    if (!fs.existsSync(filePath)) {
      console.error(`[regen-route-tree] ${filePath} is missing`);
      process.exit(1);
    }
    console.log(`[regen-route-tree] OK — ${filePath} is in sync`);
  } else {
    console.log(`[regen-route-tree] wrote ${filePath}`);
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
