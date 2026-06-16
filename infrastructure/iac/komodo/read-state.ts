// Komodo IaC — Read current state from Komodo Core via direct RPC.
// This is the browser-free version (no localStorage dependency).

import { CONFIG } from "./config.ts";
import { KomodoRpc } from "./komodo-rpc.ts";

async function main() {
  const komodo = new KomodoRpc();

  if (!CONFIG.komodoJwt) {
    // Auto-login with default dev creds
    if (process.env.KOMODO_PASSWORD) {
      await komodo.login("ciansedai", process.env.KOMODO_PASSWORD);
    } else {
      console.error("KOMODO_JWT or KOMODO_PASSWORD required");
      process.exit(1);
    }
  }

  console.log("=== Servers ===");
  const servers = await komodo.listServers();
  for (const s of servers) {
    console.log(`  ${s.name}  state=${s.info.state}  region=${s.info.region}  address=${s.info.address ?? "(outbound)"}`);
  }

  console.log("\n=== Stacks ===");
  const stacks = await komodo.listStacks();
  for (const s of stacks) {
    console.log(`  ${s.name}  server=${s.info.server_id}  state=${s.info.state}  status=${s.info.status ?? "—"}`);
  }

  console.log("\n=== Resource Syncs ===");
  const syncs = await komodo.listResourceSyncs();
  for (const s of syncs) {
    console.log(`  ${s.name}  type=${s.config.resource_type}  repo=${s.config.repo}  dir=${s.config.directory}`);
  }

  console.log("\n=== Users ===");
  const users = await komodo.listUsers();
  for (const u of users) {
    console.log(`  ${u.username}  admin=${u.admin}  super=${u.super_admin}`);
  }
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
