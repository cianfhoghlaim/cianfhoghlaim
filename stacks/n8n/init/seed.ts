// n8n-init — one-shot seeder for n8n workflows
// Walks the mounted /workflows directory, POSTs each JSON to the n8n REST API.
// Idempotent: skips a workflow whose name already exists.
// Image: ghcr.io/cianfhoghlaim/n8n-init (build context: init/Dockerfile)
//
// Env:
//   N8N_BASE_URL  e.g. http://n8n:5678
//   N8N_API_KEY   from Locket (infisical://dev-baile/n8n/api_key)
//   WORKFLOWS_DIR default /workflows
//   ACTIVATE      default true (POST then PATCH active=true)
import { readdir, readFile } from "node:fs/promises";
import { join } from "node:path";

const N8N_BASE_URL = process.env.N8N_BASE_URL ?? "http://n8n:5678";
const N8N_API_KEY = process.env.N8N_API_KEY ?? "";
const WORKFLOWS_DIR = process.env.WORKFLOWS_DIR ?? "/workflows";
const ACTIVATE = (process.env.ACTIVATE ?? "true") !== "false";

if (!N8N_API_KEY) {
  console.error("[n8n-init] N8N_API_KEY is required");
  process.exit(1);
}

const headers = {
  "X-N8N-API-KEY": N8N_API_KEY,
  "Content-Type": "application/json",
};

async function listExistingWorkflows() {
  const res = await fetch(`${N8N_BASE_URL}/api/v1/workflows?limit=250`, { headers });
  if (!res.ok) {
    throw new Error(`Failed to list workflows: ${res.status} ${await res.text()}`);
  }
  const body = (await res.json()) as { data?: Array<{ id: string; name: string }> };
  return new Map((body.data ?? []).map((w) => [w.name, w.id]));
}

async function importWorkflow(file: string) {
  const raw = await readFile(file, "utf8");
  const workflow = JSON.parse(raw);
  const name = workflow.name ?? "(unnamed)";
  const existing = await listExistingWorkflows();
  if (existing.has(name)) {
    console.log(`[n8n-init] skip (exists): ${name}`);
    return;
  }
  const createRes = await fetch(`${N8N_BASE_URL}/api/v1/workflows`, {
    method: "POST",
    headers,
    body: JSON.stringify(workflow),
  });
  if (!createRes.ok) {
    console.error(`[n8n-init] failed to create ${name}: ${createRes.status} ${await createRes.text()}`);
    return;
  }
  const created = (await createRes.json()) as { id: string };
  console.log(`[n8n-init] created: ${name} (id=${created.id})`);
  if (ACTIVATE) {
    const actRes = await fetch(`${N8N_BASE_URL}/api/v1/workflows/${created.id}/activate`, {
      method: "POST",
      headers,
    });
    if (actRes.ok) {
      console.log(`[n8n-init] activated: ${name}`);
    } else {
      console.error(`[n8n-init] activate failed for ${name}: ${actRes.status} ${await actRes.text()}`);
    }
  }
}

async function main() {
  let entries: string[];
  try {
    entries = await readdir(WORKFLOWS_DIR);
  } catch (err) {
    console.error(`[n8n-init] cannot read ${WORKFLOWS_DIR}: ${(err as Error).message}`);
    process.exit(1);
  }
  const files = entries.filter((f) => f.endsWith(".json")).sort();
  console.log(`[n8n-init] found ${files.length} workflow files in ${WORKFLOWS_DIR}`);
  for (const f of files) {
    try {
      await importWorkflow(join(WORKFLOWS_DIR, f));
    } catch (err) {
      console.error(`[n8n-init] error importing ${f}: ${(err as Error).message}`);
    }
  }
  console.log("[n8n-init] done");
}

main().catch((err) => {
  console.error(`[n8n-init] fatal: ${(err as Error).message}`);
  process.exit(1);
});
