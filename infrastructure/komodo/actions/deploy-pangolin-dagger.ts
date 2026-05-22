// =============================================================================
// DEPLOY PANGOLIN VIA DAGGER ACTION
// =============================================================================
// Runs the full Pangolin deployment pipeline using Dagger.
// This action orchestrates the 10-stage deployment from fresh server to
// production-ready state.
//
// Usage:
//   km run action deploy-pangolin-dagger --targetHost=ubuntu@server --domain=example.com
//   km run action deploy-pangolin-dagger --dryRun=true
//   km run action deploy-pangolin-dagger --stage=5  # Resume from stage 5
//
// Stages:
//   0: initServer - Server initialization (Docker, directories)
//   1: deployOpConnect - Infisical deployment
//   2: deployPangolinCore - Pangolin core stack (9 services)
//   3: setupPocketIdAdmin - PocketID admin setup (human-in-loop)
//   4: createOAuthClient - OAuth client creation (browser automation)
//   5: generateCrowdSecKey - CrowdSec bouncer key
//   6: deployKomodo - Komodo Core + Periphery
//   7: deployForgejo - Forgejo + GitOps
//   8: createPangolinSites - Pangolin sites via API
//   9: deployAppStacks - Application stacks via Komodo
//
// Prerequisites:
//   - Dagger CLI installed on target execution server
//   - SSH key available in Infisical
//   - Infisical credentials available
// =============================================================================

const dryRun = ARGS.dryRun || false;
const targetHost = ARGS.targetHost || "ubuntu@132.145.27.89";
const domain = ARGS.domain || "cianfhoghlaim.ie";
const stage = ARGS.stage !== undefined ? parseInt(ARGS.stage) : undefined;
const verify = ARGS.verify || false;
const rollback = ARGS.rollback !== undefined ? parseInt(ARGS.rollback) : undefined;

// Dagger runs on arm1-oci (OCI control plane)
const daggerServer = "arm1-oci";
const daggerRoot = "/etc/komodo/bonneagar/dagger";

console.log("=".repeat(60));
console.log("DEPLOY PANGOLIN VIA DAGGER");
console.log("=".repeat(60));
console.log(`Target Host: ${targetHost}`);
console.log(`Domain: ${domain}`);
console.log(`Dry Run: ${dryRun}`);
if (stage !== undefined) console.log(`Resume from Stage: ${stage}`);
if (verify) console.log("Mode: Verification only");
if (rollback !== undefined) console.log(`Rollback to Stage: ${rollback}`);
console.log(`Dagger Server: ${daggerServer}`);
console.log("=".repeat(60));

// Build the dagger command
let cmd = `cd ${daggerRoot} && dagger call`;

// Add common arguments
const baseArgs = `--target-host="${targetHost}" --domain="${domain}"`;

if (verify) {
  // Verification only
  cmd += ` pangolin-deployment ${baseArgs} verify`;
} else if (rollback !== undefined) {
  // Rollback to stage
  cmd += ` pangolin-deployment ${baseArgs} rollback --stage=${rollback}`;
} else if (stage !== undefined) {
  // Resume from stage
  cmd += ` pangolin-deployment ${baseArgs} deploy-from --stage=${stage}`;
  cmd += ` --pangolin-dir=./pangolin`;
  cmd += ` --komodo-dir=./komodo`;
  cmd += ` --forgejo-dir=./forgejo`;
  cmd += ` --op-credentials=env:OP_CREDENTIALS`;
  cmd += ` --pangolin-token=env:PANGOLIN_TOKEN`;
  cmd += ` --komodo-api-key=env:KOMODO_API_KEY`;
  cmd += ` --komodo-api-secret=env:KOMODO_API_SECRET`;
} else {
  // Full deployment
  cmd += ` pangolin-deployment ${baseArgs}`;
  cmd += ` --ssh-key=env:SSH_KEY`;
  cmd += ` --infisical-token=env:INFISICAL_TOKEN`;
  cmd += ` deploy-full`;
  cmd += ` --pangolin-dir=./pangolin`;
  cmd += ` --komodo-dir=./komodo`;
  cmd += ` --forgejo-dir=./forgejo`;
  cmd += ` --op-credentials=env:OP_CREDENTIALS`;
  cmd += ` --pangolin-token=env:PANGOLIN_TOKEN`;
  cmd += ` --komodo-api-key=env:KOMODO_API_KEY`;
  cmd += ` --komodo-api-secret=env:KOMODO_API_SECRET`;
  if (dryRun) cmd += ` --dry-run=true`;
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
      for (const stage of deployResult.stages) {
        const status = stage.success
          ? stage.skipped
            ? "⏭️  SKIPPED"
            : "✅ SUCCESS"
          : "❌ FAILED";
        console.log(`${status} - ${stage.stage}`);
        if (stage.error) console.log(`   Error: ${stage.error}`);
        if (stage.humanApproved) console.log(`   Human approved: ${stage.humanApproved}`);
      }
    }

    if (deployResult.services) {
      console.log("\nService Health:");
      for (const service of deployResult.services) {
        const status = service.healthy ? "✅" : "❌";
        console.log(`${status} ${service.name}: ${service.url}`);
      }
    }

    console.log(`\nTotal Duration: ${deployResult.totalDuration}ms`);
    console.log(`Overall: ${deployResult.success ? "SUCCESS" : "FAILED"}`);
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
  targetHost,
  domain,
  dryRun,
  stage: stage || "full",
  verify,
  rollback,
};
