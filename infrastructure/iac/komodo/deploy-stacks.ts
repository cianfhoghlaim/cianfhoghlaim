// Komodo IaC — Deploy all servers, stacks, resource-syncs.
// Idempotent. Re-run safe.

import { CONFIG } from "./config.ts";
import { KomodoRpc } from "./komodo-rpc.ts";

// ============================================================================
// Source of truth: declared in code. Edit here, commit, run.
// ============================================================================

const SERVERS = [
  {
    name: "arm1-oci",
    description: "Oracle Cloud ARM - Control Plane (Pangolin + Komodo Periphery + Infisical)",
    tags: ["location:oracle-london", "role:control-plane", "arch:arm64"],
    publicKey: "MCowBQYDK2VuAyEAQbp8iLZRZQN+fpIU0hXWySQq+V4iCVixdDAR+zNCkhE=",
    region: "uk-london-1",
  },
  {
    name: "bunchloch",
    description: "MacBook M4 Max - Primary Workloads (Komodo Core + Periphery + Newt)",
    tags: ["location:local", "role:primary-workloads", "arch:arm64"],
    publicKey: "MCowBQYDK2VuAyEAvgp1bX/2190RTaY0Mnqr/ERUIJoMzWzNirfWwa14FT4=",
    region: "local",
  },
];

const STACKS = [
  {
    name: "pangolin-core",
    description: "Pangolin Enterprise Edition — Core (PostgreSQL 17, port 443)",
    serverId: "arm1-oci",
    runDirectory: "/opt/pangolin",
    filePaths: ["compose.yaml", "sidecar.yaml"],
    environment: "PANGOLIN_ENDPOINT=https://pangolin.cianfhoghlaim.ie\nLOCKET_MODE=watch",
    tags: ["host:arm1-oci", "tier:infrastructure", "domain:pangolin.cianfhoghlaim.ie"],
  },
  {
    name: "komodo-core",
    description: "Komodo Core (orchestration engine)",
    serverId: "bunchloch",
    runDirectory: "~/.config/komodo",
    filePaths: ["compose.yaml", "sidecar.yaml"],
    environment: "LOCKET_MODE=watch",
    tags: ["host:bunchloch", "tier:infrastructure", "domain:komodo.cianfhoghlaim.ie"],
  },
  {
    name: "komodo-periphery-arm1",
    description: "Komodo Periphery agent (arm1-oci)",
    serverId: "arm1-oci",
    runDirectory: "/etc/komodo",
    filePaths: ["periphery.yaml", "sidecar.yaml"],
    environment: "LOCKET_MODE=watch\nPERIPHERY_MODE=inbound",
    tags: ["host:arm1-oci", "tier:infrastructure"],
  },
  {
    name: "komodo-periphery-bunchloch",
    description: "Komodo Periphery agent (bunchloch)",
    serverId: "bunchloch",
    runDirectory: "~/.config/komodo",
    filePaths: ["periphery.yaml", "sidecar.yaml"],
    environment: "LOCKET_MODE=watch\nPERIPHERY_MODE=inbound",
    tags: ["host:bunchloch", "tier:infrastructure"],
  },
  {
    name: "pangolin-newt",
    description: "Pangolin Newt tunnel agent (mbp)",
    serverId: "bunchloch",
    runDirectory: "~/.config/pangolin-newt",
    filePaths: ["newt.yaml", "newt.sidecar.yaml"],
    environment: "PANGOLIN_ENDPOINT=https://pangolin.cianfhoghlaim.ie",
    tags: ["host:bunchloch", "tier:infrastructure"],
  },
];

const RESOURCE_SYNCS = [
  { name: "komodo-stacks", resourceType: "Stack" as const, directory: "infrastructure/komodo/stacks" },
  { name: "komodo-procedures", resourceType: "Procedure" as const, directory: "infrastructure/komodo/procedures" },
  { name: "komodo-resource-syncs", resourceType: "ResourceSync" as const, directory: "infrastructure/komodo/resource-syncs" },
];

// ============================================================================
// Main
// ============================================================================

async function main() {
  const komodo = new KomodoRpc();
  if (!CONFIG.komodoJwt && process.env.KOMODO_PASSWORD) {
    await komodo.login("ciansedai", process.env.KOMODO_PASSWORD);
  }

  console.log("→ Upserting servers");
  for (const s of SERVERS) {
    console.log(`  → ${s.name}`);
    await komodo.upsertServer(s);
  }

  console.log("→ Upserting stacks");
  for (const s of STACKS) {
    console.log(`  → ${s.name} on ${s.serverId}`);
    await komodo.upsertStack(s);
  }

  console.log("→ Upserting resource syncs (skipped — managed via Komodo UI)");
  // The CreateResourceSync API has a stricter schema than documented. Until
  // the bug is fixed, configure resource syncs via the Komodo UI.
  for (const r of RESOURCE_SYNCS) {
    console.log(`  - ${r.name} (${r.resourceType}) → ${CONFIG.gitProvider}/${CONFIG.gitRepo}@${CONFIG.gitBranch}:${r.directory}`);
  }

  console.log("✓ done");
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
