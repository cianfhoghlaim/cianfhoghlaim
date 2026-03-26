// =============================================================================
// SYNC STORAGE CONFIGS ACTION
// =============================================================================
// Copies storage compose files to Komodo root directories on each server.
// Run this after initial setup to distribute configuration files.
// =============================================================================

const dryRun = ARGS.dryRun || false;
const targetServer = ARGS.server || "all"; // "all", "hetzner", "macbook", "oci"

interface CopyTask {
  server: string;
  source: string;
  destination: string;
}

// Define which stacks go to which servers
const serverStacks: Record<string, string[]> = {
  "arm1-oci": ["garage", "beszel", "dozzle", "qdrant"],
  "cax41-hetzner": [
    "memgraph",
    "falkordb",
    "graphiti",
    "lancedb",
    "cognee",
    "mlflow",
    "langfuse",
    "nimtable",
    "mathesar",
  ],
  bunchloch: [
    "lakefs",
    "lakekeeper",
    "olake-ui",
    "convex",
    "scraping",
  ],
};

const results: { server: string; stacks: string[]; status: string }[] = [];

for (const [server, stacks] of Object.entries(serverStacks)) {
  // Skip if targeting specific server and this isn't it
  if (targetServer !== "all" && !server.includes(targetServer)) {
    continue;
  }

  console.log(`\n📦 Processing server: ${server}`);

  const copiedStacks: string[] = [];

  for (const stack of stacks) {
    const sourcePath = `/repo/bonneagar/storage/${stack}`;
    const destPath = `/etc/komodo/storage/${stack}`;

    console.log(`  → ${stack}: ${sourcePath} -> ${destPath}`);

    if (!dryRun) {
      try {
        // Use Komodo's built-in file sync capabilities
        // This executes on the target server via Periphery
        await komodo.execute("RunCommand", {
          server: server,
          command: `mkdir -p ${destPath} && cp -r ${sourcePath}/* ${destPath}/`,
        });
        copiedStacks.push(stack);
      } catch (error) {
        console.error(`  ❌ Failed to copy ${stack}: ${error}`);
      }
    } else {
      copiedStacks.push(`${stack} (dry-run)`);
    }
  }

  results.push({
    server,
    stacks: copiedStacks,
    status: dryRun ? "dry-run" : "completed",
  });
}

return {
  message: dryRun ? "Dry run complete" : "Storage configs synced",
  results,
  totalStacks: results.reduce((acc, r) => acc + r.stacks.length, 0),
};
