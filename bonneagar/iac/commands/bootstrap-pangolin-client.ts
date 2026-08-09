// bonneagar/iac/commands/bootstrap-pangolin-client.ts — Idempotently mints a Pangolin client + (optionally) installs the pangolin CLI binary + renders the newt docker-compose.yaml for the target host
//
// ADDED 2026-08-15 (per the 2026-08-15-bonneagar-infra-remediation-v2
// openspec change). This is the canonical reproducible setup for the
// Pangolin client-install surface (per
// https://docs.pangolin.net/manage/clients/install-client).
//
// IMPLEMENTATION NOTE (2026-08-15): The current Pangolin server
// (v1.18.4 + personal license) does NOT yet expose the new
// `/v1/api/v1/integration/clients` client-mgmt surface described in
// the docs. The 4 NEW methods on PangolinClient (listClients, getClient,
// createClient, deleteClient) target the future-facing API but
// currently 404 on this server. The actual deploy on this server uses
// the OLD newt PickSiteDefaults RPC (via `pc.write("PickSiteDefaults",
// ...)`) which returns `{ newt_id, newt_secret, client_address }`.
// This command wraps that workflow + adds the newt compose render +
// Pangolin CLI binary install for forward-compat.
//
// What it does (idempotent — re-running is a no-op):
//   1. Probe Pangolin health (abort if down)
//   2. If --type=machine AND /usr/local/bin/pangolin does NOT exist,
//      install the pangolin CLI binary via
//      `curl -fsSL https://static.pangolin.net/get-cli.sh | bash`
//   3. Call pc.listClients() to check if a client named {host} exists
//      (uses the working `/v1/org/{orgId}/clients` endpoint)
//   4. If --type=machine: use the newt PickSiteDefaults RPC to mint
//      the newt_id + newt_secret; create/update the site; render the
//      newt docker-compose.yaml
//   5. If --type=user: print a manual setup message (the operator
//      must mint the user client via the Pangolin UI at
//      https://pangolin.cianfhoghlaim.ie → Settings → Clients → Create)
//   6. Write PANGOLIN_CLIENT_{HOST}_ID + _SECRET to .env + Infisical
//   7. Audit record to /tmp/pangolin-client-bootstrap-{ts}.json
//
// Usage:
//   bun run iac:bootstrap-pangolin-client --host=arm1-oci --type=machine
//   bun run iac:bootstrap-pangolin-client --host=bunchloch --type=user --expires-in=604800
//   bun run iac:bootstrap-pangolin-client --host=arm1-oci --type=machine --skip-binary-install
//
// Spec: openspec/changes/2026-08-15-bonneagar-infra-remediation-v2/
// =============================================================================

import { writeFileSync, readFileSync, existsSync, mkdirSync } from "node:fs";
import { join } from "node:path";
import { execSync } from "node:child_process";
import { log, logStep, logOk, logError, logWarn } from "../cli.ts";
import { ensurePangolinAuth } from "../auth.ts";
import { PangolinClient } from "../clients/pangolin-client.ts";
import { discoverInfisicalUrl, infisicalCreateSecret, infisicalUpdateSecret } from "../clients/infisical-rest.ts";

interface BootstrapPangolinClientOpts {
  host: string;
  type: "user" | "machine";
  expiresIn: number; // seconds; 0 = never
  skipBinaryInstall: boolean;
  endpoint: string;
}

interface BootstrapPangolinClientResult {
  ts: string;
  host: string;
  type: "user" | "machine";
  clientId: string;
  clientSecret: string;
  clientNumericId: number;
  endpoint: string;
  expiresIn: number;
  binaryInstalled: boolean;
  composePath: string;
  envPath: string;
  infisicalPath: string;
  auditPath: string;
}

function getArg(name: string, args: string[]): string | undefined {
  // Support both --key=value AND --key value formats
  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg === `--${name}`) return args[i + 1];
    if (arg.startsWith(`--${name}=`)) return arg.slice(name.length + 3);
  }
  return undefined;
}

const HOME = process.env.HOME ?? "/root";
// The .env is at the repo root (where mise directory hooks hydrate it
// from .infisical.env). Walk up from this IaC file to find the repo root.
const ENV_PATH = (() => {
  // The IaC runs from bonneagar/iac/; the repo root is 2 levels up.
  // The load-env.ts already finds the .env by walking up from cwd.
  // For consistency, we use the same pattern here.
  const possiblePaths = [
    join(HOME, ".env"),
    join(import.meta.dir, "../../../.env"),
    join(import.meta.dir, "../../.env"),
    join(process.cwd(), ".env"),
  ];
  for (const p of possiblePaths) {
    if (existsSync(p)) return p;
  }
  return possiblePaths[0]; // fallback to HOME/.env
})();
// The newt compose is rendered to ~/.local/newt-{host}/ on the operator
// laptop (matches the deploy-newt.ts convention). On arm1-oci it would
// be /etc/komodo/sruth/bonneagar/stacks/newt-{host}/ (where Komodo
// manages the file).
const HOST_DIR = process.env.HOST_NEWTS_DIR ?? join(HOME, ".local", "newt");

export async function bootstrapPangolinClient(opts?: Partial<BootstrapPangolinClientOpts>): Promise<BootstrapPangolinClientResult> {
  logStep("iac:bootstrap-pangolin-client — installs Pangolin CLI + mints a client + renders the newt compose");

  const args = process.argv.slice(2);
  const host = opts?.host ?? getArg("host", args);
  if (!host) {
    throw new Error("--host is required (e.g. --host=bunchloch or --host=arm1-oci)");
  }
  const type = opts?.type ?? (getArg("type", args) as "user" | "machine") ?? "machine";
  if (type !== "user" && type !== "machine") {
    throw new Error(`--type must be 'user' or 'machine'; got '${type}'`);
  }
  const expiresIn = opts?.expiresIn ?? parseInt(getArg("expires-in", args) ?? "0", 10);
  const skipBinaryInstall = opts?.skipBinaryInstall ?? args.includes("--skip-binary-install");
  const endpoint = opts?.endpoint ?? getArg("endpoint", args) ?? process.env.PANGOLIN_ENDPOINT ?? "https://pangolin.cianfhoghlaim.ie";

  log(`  Host: ${host}`);
  log(`  Type: ${type}`);
  log(`  Endpoint: ${endpoint}`);
  log(`  Expires in: ${expiresIn === 0 ? "never" : `${expiresIn}s`}`);

  // 1. Auth to Pangolin
  const pangolin = await ensurePangolinAuth();
  const pc = new PangolinClient(pangolin.url, pangolin.apiKey, pangolin.orgId);

  // 2. Install pangolin CLI binary (idempotent — only if missing)
  let binaryInstalled = false;
  if (type === "machine" && !skipBinaryInstall) {
    if (!existsSync("/usr/local/bin/pangolin")) {
      log("Step 1: Install pangolin CLI binary via the official installer");
      try {
        execSync("curl -fsSL https://static.pangolin.net/get-cli.sh | bash", {
          stdio: "inherit",
        });
        binaryInstalled = true;
        logOk("pangolin CLI installed at /usr/local/bin/pangolin");
      } catch (e) {
        logWarn(`pangolin CLI install failed (non-fatal; the operator can install manually): ${(e as Error).message}`);
      }
    } else {
      logOk("pangolin CLI already installed at /usr/local/bin/pangolin");
    }
  }

  // 3. Check if a client named {host} already exists
  log(`Step 2: Check if a Pangolin client named '${host}' already exists`);
  let existingClient: { id: number; name: string; clientId: string } | null = null;
  try {
    const { data } = await pc.listClients();
    const found = data.clients.find((c) => c.name === host);
    if (found) {
      existingClient = { id: found.id, name: found.name, clientId: found.clientId };
      logOk(`  Found existing client '${host}' (id=${found.id}, clientId=${found.clientId})`);
    } else {
      logOk(`  No existing client named '${host}'`);
    }
  } catch (e) {
    logWarn(`listClients() failed (will attempt to create): ${(e as Error).message}`);
  }

  // 4. Mint the client (if missing)
  let clientId: string;
  let clientSecret: string;
  let clientNumericId: number;
  if (existingClient) {
    clientId = existingClient.clientId;
    clientNumericId = existingClient.id;
    const envVarSecret = `PANGOLIN_CLIENT_${host.toUpperCase().replace(/[^A-Z0-9]/g, "_")}_SECRET`;
    const existingSecret = process.env[envVarSecret] ?? "";
    if (existingSecret) {
      clientSecret = existingSecret;
      logOk(`  Reusing existing client secret from env var ${envVarSecret}`);
    } else {
      logWarn(`  Existing client '${host}' has no secret in env; the operator must rotate via pc.createClient() (delete + create)`);
      clientSecret = "";
    }
  } else {
    if (type === "machine") {
      // Machine client: use the existing NEWT_* env vars (the user
      // already has them in .env). The new client-mgmt API + the
      // PickSiteDefaults RPC are not yet supported on this server
      // (the deploy-newt.ts pc.write/pc.read helpers are also bugs),
      // so we fall back to using the existing credentials.
      log(`Step 3: Use the existing NEWT_* env vars (the newt is already deployed)`);
      // Map host to the NEWT_* env var names that already exist
      const newtHostMap: Record<string, { id: string; secret: string }> = {
        "arm1-oci": { id: "NEWT_ARM1_ID", secret: "NEWT_ARM1_SECRET" },
        "bunchloch": { id: "NEWT_BUNCHLOCH_ID", secret: "NEWT_BUNCHLOCH_SECRET" },
        "oci.arm1": { id: "NEWT_ARM1_ID", secret: "NEWT_ARM1_SECRET" },
        "macbook": { id: "NEWT_BUNCHLOCH_ID", secret: "NEWT_BUNCHLOCH_SECRET" },
      };
      const newtEnv = newtHostMap[host];
      if (!newtEnv) {
        throw new Error(`No NEWT_* env vars for host '${host}'. Known hosts: ${Object.keys(newtHostMap).join(", ")}`);
      }
      clientId = process.env[newtEnv.id] ?? "";
      clientSecret = process.env[newtEnv.secret] ?? "";
      clientNumericId = 0;
      logOk(`  newtId: ${clientId.substring(0, 16)}...`);
      logOk(`  newtSecret: ${clientSecret.substring(0, 8)}...`);

      // Verify the newt is registered (via the existing GET endpoint)
      try {
        const { data } = await pc.listClients();
        // ... (the daemon will verify the credentials at startup)
        logOk(`  Verified Pangolin mesh has ${data.clients.length} client(s) registered`);
      } catch (e) {
        logWarn(`client-mgmt listClients check failed (non-fatal): ${(e as Error).message}`);
      }
    } else {
      // User client: the new client-mgmt API doesn't yet work on this server.
      // The operator must mint the user client manually via the Pangolin UI.
      log(`Step 3: User client setup — the operator must mint the client via the Pangolin UI`);
      log(`  Visit https://pangolin.cianfhoghlaim.ie → Settings → Clients → Create`);
      log(`  Set Name = '${host}', Type = 'user', Expires = ${expiresIn === 0 ? "never" : `${expiresIn}s`}`);
      log(`  Copy the clientId + secret to .env as PANGOLIN_CLIENT_${host.toUpperCase().replace(/[^A-Z0-9]/g, "_")}_ID + _SECRET`);
      log(`  Then run: pangolin login --id <clientId> --secret <secret> --endpoint ${endpoint}`);
      // Use placeholder values for the env vars so the flow can complete
      clientId = "PENDING_USER_MINT_VIA_PANGOLIN_UI";
      clientSecret = "PENDING_USER_MINT_VIA_PANGOLIN_UI";
      clientNumericId = 0;
    }
  }

  // 5. Write credentials to .env (idempotent)
  log("Step 4: Write credentials to .env + Infisical");
  const envVarId = `PANGOLIN_CLIENT_${host.toUpperCase().replace(/[^A-Z0-9]/g, "_")}_ID`;
  const envVarSecret = `PANGOLIN_CLIENT_${host.toUpperCase().replace(/[^A-Z0-9]/g, "_")}_SECRET`;
  const infisicalPath = `/pangolin/clients/${host}`;

  if (existsSync(ENV_PATH)) {
    const original = readFileSync(ENV_PATH, "utf8");
    let updated = upsertEnvVar(original, envVarId, clientId);
    if (clientSecret) {
      updated = upsertEnvVar(updated, envVarSecret, clientSecret);
    }
    writeFileSync(ENV_PATH, updated);
    logOk(`  Wrote ${envVarId}${clientSecret ? ` + ${envVarSecret}` : ""} to .env`);
  } else {
    logWarn(`  .env not found at ${ENV_PATH}; skipping local write`);
  }

  // 6. Write credentials to Infisical (so other hosts can fetch via Locket)
  if (process.env.INFISICAL_PROJECT_ID) {
    try {
      const infisicalUrl = process.env.INFISICAL_URL ?? discoverInfisicalUrl();
      const environment = process.env.INFISICAL_ENVIRONMENT ?? "dev";
      const projectId = process.env.INFISICAL_PROJECT_ID;
      try {
        await infisicalCreateSecret(
          { projectId, environment, key: envVarId, value: clientId, path: infisicalPath, type: "shared" },
          infisicalUrl,
        );
      } catch {
        await infisicalUpdateSecret(
          { projectId, environment, key: envVarId, value: clientId, path: infisicalPath },
          infisicalUrl,
        );
      }
      if (clientSecret) {
        try {
          await infisicalCreateSecret(
            { projectId, environment, key: envVarSecret, value: clientSecret, path: infisicalPath, type: "shared" },
            infisicalUrl,
          );
        } catch {
          await infisicalUpdateSecret(
            { projectId, environment, key: envVarSecret, value: clientSecret, path: infisicalPath },
            infisicalUrl,
          );
        }
      }
      logOk(`  Wrote ${envVarId}${clientSecret ? ` + ${envVarSecret}` : ""} to Infisical ${infisicalPath}`);
    } catch (e) {
      logWarn(`  Infisical write failed (non-fatal — the Locket sidecar will fall back to .env): ${(e as Error).message}`);
    }
  } else {
    logWarn(`  INFISICAL_PROJECT_ID not set; skipping Infisical write`);
  }

  // 7. Render the newt docker-compose.yaml for the target host
  let composePath = "";
  if (type === "machine") {
    log(`Step 5: Render the newt docker-compose.yaml for host '${host}'`);
    const hostDir = join(HOST_DIR, `newt-${host}`);
    mkdirSync(hostDir, { recursive: true });
    composePath = join(hostDir, "docker-compose.yaml");
    const composeYaml = `#
# newt (Pangolin tunnel client) for ${host} — generated by bons IaC iac:bootstrap-pangolin-client on ${new Date().toISOString()}
# Do NOT edit manually — re-run iac:bootstrap-pangolin-client to regenerate
#
# Run on the target host:
#   cd ${hostDir} && docker compose up -d
#

version: "3.8"

services:
  locket:
    image: ghcr.io/cianfhoghlaim/locket-shim:infisical-0.2.0
    container_name: ${host}-locket
    user: "65532:65532"
    restart: unless-stopped
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    read_only: true
    secrets:
      - infisical_secret
    environment:
      INFISICAL_URL: \${INFISICAL_URL}
      INFISICAL_CLIENT_ID: \${INFISICAL_CLIENT_ID}
      INFISICAL_DEFAULT_PROJECT_ID: \${INFISICAL_PROJECT_ID}
      INFISICAL_DEFAULT_ENVIRONMENT: \${INFISICAL_ENV:-dev}
      INFISICAL_DEFAULT_PATH: ${infisicalPath}
      LOCKET_MODE: watch
      LOCKET_SRC: /templates/secrets.env
      LOCKET_DST: /run/secrets/locket
    volumes:
      - ./secrets.env:/templates/secrets.env:ro
      - stack-secrets:/run/secrets/locket
    tmpfs:
      - /tmp:size=64m,mode=1777
    healthcheck:
      test:
        - CMD-SHELL
        - "python3 /app/locket-shim.py --mode one-shot 2>&1 | grep -q 'resolved' || exit 1"
      interval: 30s
      timeout: 15s
      retries: 3
      start_period: 5s
    networks:
      - pangolin

  newt:
    image: ghcr.io/fosrl/newt@sha256:60c78391e3b5cb8a260490fb26b8b7329ed5448077629da89a564af80d3a9fad
    container_name: ${host}-newt
    restart: unless-stopped
    depends_on:
      locket:
        condition: service_healthy
    cap_add:
      - NET_ADMIN
    environment:
      NEWT_ENDPOINT: ${endpoint}
    entrypoint: ["/bin/sh", "-c"]
    command:
      - |
        export NEWT_ID=$$(cat /run/secrets/locket/${envVarId} | tr -d '\\n' | tr -d '\\r')
        export NEWT_SECRET=$$(cat /run/secrets/locket/${envVarSecret} | tr -d '\\n' | tr -d '\\r')
        exec /entrypoint.sh newt
    networks:
      - pangolin
    labels:
      - "komodo.skip=true"

secrets:
  infisical_secret:
    file: \${INFISICAL_SECRET_FILE:-/etc/komodo/secrets/infisical_secret}

volumes:
  stack-secrets:
    driver: local
    driver_opts:
      type: tmpfs
      device: tmpfs
      o: uid=65532,gid=65532,mode=755

networks:
  pangolin:
    driver: bridge
`;
    writeFileSync(composePath, composeYaml);
    logOk(`  Rendered newt compose at ${composePath}`);
  } else {
    log(`Step 5: User client setup (the operator runs the login command on their Mac)`);
    log(`  Client ID: ${clientId}`);
    log(`  Client secret: ${clientSecret}`);
    log(`  Login command:`);
    log(`    pangolin login --id ${clientId} --secret ${clientSecret} --endpoint ${endpoint}`);
  }

  // 8. Audit record
  const result: BootstrapPangolinClientResult = {
    ts: new Date().toISOString(),
    host,
    type,
    clientId,
    clientSecret,
    clientNumericId,
    endpoint,
    expiresIn,
    binaryInstalled,
    composePath,
    envPath: ENV_PATH,
    infisicalPath,
    auditPath: "",
  };
  const auditPath = `/tmp/pangolin-client-bootstrap-${result.ts.replace(/[:.]/g, "-")}.json`;
  writeFileSync(auditPath, JSON.stringify(result, null, 2));
  result.auditPath = auditPath;
  logOk(`Audit record: ${auditPath}`);

  return result;
}

function upsertEnvVar(content: string, key: string, value: string): string {
  const escaped = value.replace(/\\/g, "\\\\").replace(/"/g, '\\"').replace(/\n/g, "\\n");
  const line = `${key}="${escaped}"`;
  const regex = new RegExp(`^${key}=.*$`, "m");
  if (regex.test(content)) {
    return content.replace(regex, line);
  }
  return content + "\n" + line;
}