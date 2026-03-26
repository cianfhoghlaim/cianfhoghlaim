// =============================================================================
// DEPLOY AUTH STACK VIA DAGGER ACTION
// =============================================================================
// Deploys infrastructure stacks with TinyAuth authentication using the
// Dagger auth-stack module.
//
// Usage:
//   km run action deploy-auth-stack-dagger --stack=lakehouse
//   km run action deploy-auth-stack-dagger --stack=lakehouse --dryRun=true
//   km run action deploy-auth-stack-dagger --stack=lakehouse --stage=verify-auth
//   km run action deploy-auth-stack-dagger --stack=lakehouse --rollback=deploy-stack
//
// Available Stacks:
//   - lakehouse (Garage S3, Lakekeeper, Lance Namespace)
//   - lancedb (LanceDB Viewer)
//   - memgraph (Memgraph Lab)
//   - mlflow (MLflow Tracking)
//   - langfuse (Langfuse Observability)
//   - graphiti (Graphiti Knowledge Graph)
//
// Stages:
//   - pre-flight: Validate TinyAuth and PocketID health
//   - create-oauth: Create OAuth client in PocketID
//   - inject-secrets: Store credentials in 1Password
//   - deploy-stack: Deploy via Komodo
//   - verify-auth: Test authentication redirects
//
// Prerequisites:
//   - Dagger CLI installed on target execution server
//   - 1Password Connect available
//   - PocketID admin token available
//   - Komodo API credentials available
// =============================================================================

const stack = ARGS.stack;
const dryRun = ARGS.dryRun || false;
const stage = ARGS.stage || "full";
const rollback = ARGS.rollback || undefined;
const verify = ARGS.verify || false;

// Validate stack argument
if (!stack) {
  console.error("ERROR: --stack argument is required");
  console.log("Available stacks: lakehouse, lancedb, memgraph, mlflow, langfuse, graphiti");
  return { success: false, error: "Missing --stack argument" };
}

// Dagger runs on arm1-oci (OCI control plane)
const daggerServer = "arm1-oci";
const daggerRoot = "/etc/komodo/bonneagar/dagger";

console.log("=".repeat(60));
console.log("DEPLOY AUTH STACK VIA DAGGER");
console.log("=".repeat(60));
console.log(`Stack: ${stack}`);
console.log(`Dry Run: ${dryRun}`);
console.log(`Stage: ${stage}`);
if (verify) console.log("Mode: Verification only");
if (rollback) console.log(`Rollback Stage: ${rollback}`);
console.log(`Dagger Server: ${daggerServer}`);
console.log("=".repeat(60));

// Build the dagger command
let cmd = `cd ${daggerRoot} && dagger call auth-stack`;

// Add connection arguments (from environment)
const connectionArgs = [
  `--komodo-url="https://komodo.cianfhoghlaim.ie"`,
  `--komodo-api-key=env:KOMODO_API_KEY`,
  `--komodo-api-secret=env:KOMODO_API_SECRET`,
  `--pocket-id-url="https://auth.cianfhoghlaim.ie"`,
  `--pocket-id-token=env:POCKETID_TOKEN`,
  `--op-connect-host="http://132.145.27.89:8080"`,
  `--op-connect-token=env:OP_CONNECT_TOKEN`,
].join(" ");

cmd += ` ${connectionArgs}`;

// Add operation
if (verify) {
  // Verification only - test auth redirects
  cmd += ` verify-authentication --service-url="https://${stack}.cianfhoghlaim.ie"`;
} else if (rollback) {
  // Rollback to stage
  cmd += ` rollback --stack-name="${stack}" --stage="${rollback}"`;
} else if (stage === "full") {
  // Full deployment
  cmd += ` deploy-authenticated-stack --stack-name="${stack}"`;
  if (dryRun) cmd += ` --dry-run=true`;
} else {
  // Single stage execution
  switch (stage) {
    case "pre-flight":
      // Check Komodo health
      cmd += ` list-available-stacks`;
      break;
    case "create-oauth":
      // Create OAuth client
      cmd += ` create-o-auth-client`;
      cmd += ` --service-name="${stack}"`;
      cmd += ` --domain="${stack}.cianfhoghlaim.ie"`;
      cmd += ` --redirect-uri="https://${stack}.cianfhoghlaim.ie/oauth/callback"`;
      break;
    case "inject-secrets":
      // This requires client ID and secret from previous stage
      console.log("INFO: inject-secrets stage requires client credentials");
      console.log("Run with --stage=full for complete workflow");
      return { success: true, stage, info: "Requires full workflow" };
    case "deploy-stack":
      // Deploy via Komodo
      cmd += ` deploy-stack --stack-name="${stack}"`;
      break;
    case "verify-auth":
      // Verify authentication
      cmd += ` verify-authentication --service-url="https://${stack}.cianfhoghlaim.ie"`;
      break;
    default:
      console.error(`ERROR: Unknown stage: ${stage}`);
      console.log("Available stages: pre-flight, create-oauth, inject-secrets, deploy-stack, verify-auth, full");
      return { success: false, error: `Unknown stage: ${stage}` };
  }
}

console.log(`\nCommand: ${cmd}\n`);
console.log("-".repeat(60));

// Execute via Komodo RunCommand
const result = await komodo.execute("RunCommand", {
  server: daggerServer,
  command: cmd,
});

// Parse and display results
if (result.stdout) {
  console.log(result.stdout);

  // Try to parse JSON output
  try {
    const deployResult = JSON.parse(result.stdout);
    console.log("\n" + "-".repeat(60));
    console.log("DEPLOYMENT SUMMARY");
    console.log("-".repeat(60));

    if (deployResult.stages) {
      for (const stageResult of deployResult.stages) {
        const status = stageResult.status === "completed"
          ? stageResult.skipped
            ? "⏭️  SKIPPED"
            : "✅ SUCCESS"
          : stageResult.status === "failed"
            ? "❌ FAILED"
            : "⏳ PENDING";
        console.log(`${status} - ${stageResult.name}`);
        if (stageResult.error) console.log(`   Error: ${stageResult.error}`);
        if (stageResult.output) console.log(`   Output: ${stageResult.output.substring(0, 100)}...`);
      }
    }

    if (deployResult.stackName) {
      console.log(`\nStack: ${deployResult.stackName}`);
    }

    if (deployResult.dryRun) {
      console.log("\n⚠️  DRY RUN MODE - No changes were made");
    }

    console.log(`\nOverall: ${deployResult.success ? "SUCCESS" : "FAILED"}`);
    if (deployResult.error) console.log(`Error: ${deployResult.error}`);
  } catch {
    // Not JSON, just raw output
  }
}

if (result.stderr) {
  console.error("\nSTDERR:");
  console.error(result.stderr);
}

console.log("\n" + "=".repeat(60));
console.log(`Result: ${result.success ? "SUCCESS" : "FAILED"}`);
console.log("=".repeat(60));

return {
  success: result.success,
  stack,
  stage,
  dryRun,
  verify,
  rollback,
};
