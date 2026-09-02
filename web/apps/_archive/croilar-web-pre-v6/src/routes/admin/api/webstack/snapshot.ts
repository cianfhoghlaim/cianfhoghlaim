import { createFileRoute } from "@tanstack/react-router";
import { readFile } from "node:fs/promises";
import { existsSync } from "node:fs";
import { resolve } from "node:path";
import { spawnSync } from "node:child_process";

export const Route = createFileRoute("/admin/api/webstack/snapshot")({
  server: {
    handlers: {
      GET: async () => {
        const { snapshot, regenerated } = await loadOrRegenerate();
        return Response.json(snapshot, {
          headers: {
            "cache-control": "no-store",
            "x-snapshot-regenerated": regenerated ? "1" : "0",
          },
        });
      },
    },
  },
});

const SNAPSHOT_PATH = resolve(
  process.env.CROILAR_REPO_ROOT ?? resolve(process.cwd(), "../.."),
  "croilar/.cache/webstack-snapshot.json",
);

const ANALYZER = resolve(
  process.env.CROILAR_REPO_ROOT ?? resolve(process.cwd(), "../.."),
  "croilar/scripts/analyze-web-stack.ts",
);

async function loadOrRegenerate(): Promise<{ snapshot: unknown; regenerated: boolean }> {
  if (existsSync(SNAPSHOT_PATH)) {
    const stat = await import("node:fs/promises").then((m) => m.stat(SNAPSHOT_PATH));
    if (Date.now() - stat.mtimeMs < 60_000) {
      return { snapshot: JSON.parse(await readFile(SNAPSHOT_PATH, "utf-8")), regenerated: false };
    }
  }
  const result = spawnSync("bun", ["run", ANALYZER, "--out", SNAPSHOT_PATH], {
    encoding: "utf-8",
    timeout: 120_000,
  });
  if (result.status !== 0) {
    return { snapshot: emptySnapshot(), regenerated: false };
  }
  return { snapshot: JSON.parse(await readFile(SNAPSHOT_PATH, "utf-8")), regenerated: true };
}

function emptySnapshot() {
  return {
    generatedAt: Date.now(),
    tanstackRoutes: [],
    convexFunctions: [],
    cloudflareResources: [],
    bamlSchemas: [],
    marimoNotebooks: [],
  };
}
