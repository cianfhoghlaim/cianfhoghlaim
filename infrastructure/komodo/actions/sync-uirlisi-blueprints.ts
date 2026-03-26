// =============================================================================
// SYNC UIRLÍSÍ BLUEPRINTS ACTION [DEPRECATED]
// =============================================================================
//
// ⚠️ DEPRECATED: This action is no longer needed!
//
// Pangolin now uses Docker labels for auto-discovery. Services are automatically
// registered when containers start with the appropriate pangolin.resource.* labels.
//
// See: *.pangolin.yaml files alongside each compose file for the label definitions.
//
// The new approach:
// 1. Add labels to Docker Compose (via separate pangolin.yaml file)
// 2. Komodo stacks include both compose.yaml and pangolin.yaml
// 3. Newt auto-discovers services via Docker socket
//
// This file is kept for reference but should not be used.
// =============================================================================

const dryRun = ARGS.dryRun || false;
const pangolinOrg = ARGS.org || "cianfhoghlaim";

// Server where Pangolin runs (for API calls)
const PANGOLIN_SERVER = "arm1-oci";

// Get Pangolin API key from Komodo variables
const pangolinApiKey = await komodo.read("GetVariable", { name: "PANGOLIN_API_KEY" });

if (!pangolinApiKey?.value) {
  return {
    success: false,
    error: "Missing PANGOLIN_API_KEY variable in Komodo. Create an API key in Pangolin UI first.",
  };
}

// Helper to make Pangolin API calls via curl inside pangolin container
async function pangolinApi<T>(method: string, endpoint: string, body?: object): Promise<T> {
  const bodyArg = body ? `-d '${JSON.stringify(body)}'` : "";
  const curlCmd = `docker exec pangolin curl -s 'http://localhost:3003/v1${endpoint}' -X ${method} -H 'Authorization: Bearer ${pangolinApiKey.value}' -H 'Content-Type: application/json' ${bodyArg}`;

  const result = await komodo.execute("RunCommand", {
    server: PANGOLIN_SERVER,
    command: curlCmd,
  });

  if (!result.success) {
    throw new Error(`Pangolin API call failed: ${result.stderr || "Unknown error"}`);
  }

  try {
    const data = JSON.parse(result.stdout || "{}");
    if (data.error) {
      throw new Error(data.message || "Pangolin API error");
    }
    return data.data as T;
  } catch (e) {
    // API might return success without JSON body for some operations
    return {} as T;
  }
}

// Sync a single blueprint via API
async function syncBlueprint(blueprintPath: string, serverWithBlueprint: string): Promise<void> {
  // Convert YAML to JSON and base64 encode on the server
  const encodeResult = await komodo.execute("RunCommand", {
    server: serverWithBlueprint,
    command: `yq -o json ${blueprintPath} | base64 -w 0`,
  });

  if (!encodeResult.success || !encodeResult.stdout) {
    throw new Error(`Failed to read/encode blueprint: ${encodeResult.stderr || "Empty result"}`);
  }

  const base64Blueprint = encodeResult.stdout.trim();

  // PUT to Pangolin API
  await pangolinApi("PUT", `/org/${pangolinOrg}/blueprint`, {
    blueprint: base64Blueprint,
  });
}

// Define uirlisí blueprint locations
// Format: stack-name -> { path: full-path-to-blueprint, server: where-file-is-stored }
const uirlisiBlueprints: Record<string, { path: string; server: string }> = {
  // Dev-tools (on bunchloch)
  "glance": { path: "/etc/komodo/uirlisi/dev-tools/glance.blueprint.yaml", server: "bunchloch" },
  "storybook": { path: "/etc/komodo/uirlisi/dev-tools/storybook.blueprint.yaml", server: "bunchloch" },
  "chartdb": { path: "/etc/komodo/uirlisi/dev-tools/chartdb.blueprint.yaml", server: "bunchloch" },
  "excalidraw": { path: "/etc/komodo/uirlisi/dev-tools/excalidraw.blueprint.yaml", server: "bunchloch" },
  "perplexica": { path: "/etc/komodo/uirlisi/dev-tools/perplexica.blueprint.yaml", server: "bunchloch" },
  "searxng": { path: "/etc/komodo/uirlisi/dev-tools/searxng.blueprint.yaml", server: "bunchloch" },
  "changedetection": { path: "/etc/komodo/uirlisi/dev-tools/changedetection.blueprint.yaml", server: "bunchloch" },
  "restate": { path: "/etc/komodo/uirlisi/dev-tools/restate.blueprint.yaml", server: "bunchloch" },
  "letterfeed": { path: "/etc/komodo/uirlisi/dev-tools/letterfeed.blueprint.yaml", server: "bunchloch" },
  "pastemax": { path: "/etc/komodo/uirlisi/dev-tools/pastemax.blueprint.yaml", server: "bunchloch" },
  "pipecat": { path: "/etc/komodo/uirlisi/dev-tools/pipecat.blueprint.yaml", server: "bunchloch" },
  // Scraping tools (on bunchloch)
  "skyvern": { path: "/etc/komodo/uirlisi/scraping/skyvern.blueprint.yaml", server: "bunchloch" },
};

interface SyncResult {
  stack: string;
  status: "success" | "failed" | "dry-run";
  message: string;
}

const results: SyncResult[] = [];

console.log("🔄 Syncing uirlisí blueprints to Pangolin via REST API...");
console.log(`   Organization: ${pangolinOrg}`);
console.log(`   Stacks: ${Object.keys(uirlisiBlueprints).length}\n`);

for (const [stack, config] of Object.entries(uirlisiBlueprints)) {
  console.log(`📋 ${stack}: ${config.path}`);

  if (dryRun) {
    results.push({
      stack,
      status: "dry-run",
      message: `Would sync: ${config.path} from ${config.server}`,
    });
    continue;
  }

  try {
    await syncBlueprint(config.path, config.server);
    results.push({
      stack,
      status: "success",
      message: `Blueprint synced via API from ${config.server}`,
    });
    console.log(`  ✅ Synced successfully`);
  } catch (error) {
    results.push({
      stack,
      status: "failed",
      message: `Failed to sync: ${error}`,
    });
    console.error(`  ❌ Failed: ${error}`);
  }
}

// Summary
const successful = results.filter((r) => r.status === "success").length;
const failed = results.filter((r) => r.status === "failed").length;

console.log(`\n📊 Summary: ${successful} synced, ${failed} failed`);

return {
  message: dryRun ? "Dry run complete" : "Uirlisí blueprints synced",
  summary: {
    total: results.length,
    successful,
    failed,
  },
  results,
};
