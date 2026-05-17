// =============================================================================
// SYNC BLUEPRINT ACTION [DEPRECATED]
// =============================================================================
//
// ⚠️ DEPRECATED: This action is no longer needed!
//
// Pangolin now uses Docker labels for auto-discovery. Services are automatically
// registered when containers start with the appropriate pangolin.resource.* labels.
//
// See: pangolin.yaml files alongside each compose.yaml for the label definitions.
//
// The new approach:
// 1. Add labels to Docker Compose (via separate pangolin.yaml file)
// 2. Komodo stacks include both compose.yaml and pangolin.yaml
// 3. Newt auto-discovers services via Docker socket
//
// This file is kept for reference but should not be used.
// =============================================================================

const stackName = ARGS.stack;
const dryRun = ARGS.dryRun || false;
const pangolinOrg = ARGS.org || "cianfhoghlaim";

if (!stackName) {
  throw new Error("Required argument: --stack=<stack-name> or --stack=all");
}

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

// Define stack locations and their categories
// Each stack includes the server where the blueprint file is stored
const stackLocations: Record<string, { category: string; path: string; server: string }> = {
  // Storage stacks (on arm1-oci)
  "qdrant": { category: "storage", path: "/etc/komodo/storage/qdrant/blueprint.yaml", server: "arm1-oci" },
  "memgraph": { category: "storage", path: "/etc/komodo/storage/memgraph/blueprint.yaml", server: "arm1-oci" },
  "falkordb": { category: "storage", path: "/etc/komodo/storage/falkordb/blueprint.yaml", server: "arm1-oci" },
  "graphiti": { category: "storage", path: "/etc/komodo/storage/graphiti/blueprint.yaml", server: "arm1-oci" },
  "lancedb": { category: "storage", path: "/etc/komodo/storage/lancedb/blueprint.yaml", server: "arm1-oci" },
  "cognee": { category: "storage", path: "/etc/komodo/storage/cognee/blueprint.yaml", server: "arm1-oci" },
  "mlflow": { category: "storage", path: "/etc/komodo/storage/mlflow/blueprint.yaml", server: "arm1-oci" },
  "langfuse": { category: "storage", path: "/etc/komodo/storage/langfuse/blueprint.yaml", server: "arm1-oci" },
  "nimtable": { category: "storage", path: "/etc/komodo/storage/nimtable/blueprint.yaml", server: "arm1-oci" },
  "mathesar": { category: "storage", path: "/etc/komodo/storage/mathesar/blueprint.yaml", server: "arm1-oci" },
  "beszel": { category: "storage", path: "/etc/komodo/storage/beszel/blueprint.yaml", server: "arm1-oci" },
  "dozzle": { category: "storage", path: "/etc/komodo/storage/dozzle/blueprint.yaml", server: "arm1-oci" },
  "garage": { category: "storage", path: "/etc/komodo/storage/garage/blueprint.yaml", server: "arm1-oci" },
  "lakefs": { category: "storage", path: "/etc/komodo/storage/lakefs/blueprint.yaml", server: "arm1-oci" },
  "lakekeeper": { category: "storage", path: "/etc/komodo/storage/lakekeeper/blueprint.yaml", server: "arm1-oci" },
  "lakehouse": { category: "storage", path: "/etc/komodo/storage/lakehouse/blueprint.yaml", server: "arm1-oci" },
  "olake-ui": { category: "storage", path: "/etc/komodo/storage/olake-ui/blueprint.yaml", server: "arm1-oci" },
  "convex": { category: "storage", path: "/etc/komodo/storage/convex/blueprint.yaml", server: "arm1-oci" },
  "autobase": { category: "storage", path: "/etc/komodo/storage/autobase/blueprint.yaml", server: "arm1-oci" },
  "confluent": { category: "storage", path: "/etc/komodo/storage/confluent/blueprint.yaml", server: "arm1-oci" },
  "forgejo": { category: "storage", path: "/etc/komodo/storage/forgejo/blueprint.yaml", server: "arm1-oci" },
};

interface SyncResult {
  stack: string;
  status: "success" | "failed" | "skipped" | "dry-run";
  message: string;
}

const results: SyncResult[] = [];

// Determine which stacks to sync
const stacksToSync = stackName === "all"
  ? Object.keys(stackLocations)
  : [stackName];

console.log(`🔄 Syncing blueprints to Pangolin via REST API...`);
console.log(`   Organization: ${pangolinOrg}`);
console.log(`   Stacks: ${stacksToSync.length}\n`);

for (const stack of stacksToSync) {
  const location = stackLocations[stack];

  if (!location) {
    results.push({
      stack,
      status: "skipped",
      message: `Stack '${stack}' not found in stack locations`,
    });
    continue;
  }

  console.log(`📋 ${stack}: ${location.path}`);

  if (dryRun) {
    results.push({
      stack,
      status: "dry-run",
      message: `Would sync: ${location.path} from ${location.server}`,
    });
    continue;
  }

  try {
    await syncBlueprint(location.path, location.server);
    results.push({
      stack,
      status: "success",
      message: `Blueprint synced via API from ${location.server}`,
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
const skipped = results.filter((r) => r.status === "skipped").length;

console.log(`\n📊 Summary: ${successful} synced, ${failed} failed, ${skipped} skipped`);

return {
  message: dryRun ? "Dry run complete" : "Blueprint sync complete",
  summary: {
    total: results.length,
    successful,
    failed,
    skipped,
  },
  results,
};
