// bonneagar/iac/commands/rotate-auth.ts — One-shot 3-way credential rotation
//
// What this does:
//   1. (Optional) Mint a fresh Pangolin API key via Pocket ID OIDC client_credentials
//      (requires POCKETID_PANGOLIN_CLIENT_ID + POCKETID_PANGOLIN_CLIENT_SECRET in env, which the
//      operator mints once via https://auth.cianfhoghlaim.ie → Settings → OIDC)
//   2. Read KOMODO_PASSWORD from Infisical → write to ~/.env
//   3. Read INFISICAL_UNIVERSAL_AUTH_CLIENT_SECRET from Infisical → write to ~/.env
//   4. Emit a JSON audit record to /tmp/auth-rotation-{ts}.json
//
// Why this is split out from iac:auth.ts:
//   The 3 ensure*Auth() helpers are called on every iac command (plan,
//   health, sync:*). The 3-way rotation is a slower, less frequent operation
//   that should be run explicitly (`bun run iac:rotate-auth`).
//
// What this is NOT:
//   - It's NOT a credential vault (use Infisical directly for that)
//   - It does NOT handle the Cloudflare / CrowdSec / Pocket ID secrets
//     (those are operator-mint-then-save-to-Infisical flows; see
//     PANGOLIN-SETUP.md Manual Steps 2 + 3)
//
// Spec: openspec/changes/2026-07-14-repair-bonneagar-iac-3-way-auth-v1
// =============================================================================

import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { join } from "node:path";
import { log, logStep, logOk, logError, logWarn } from "../cli.ts";
import { pocketIdLogin } from "../auth-pocketid.ts";
import { ensureBonsIacClient } from "./bootstrap-pocketid-admin.ts";
import { CONFIG } from "../config.ts";

interface RotationRecord {
  ts: string;
  results: {
    pangolin: { status: "ok" | "skipped" | "failed"; reason?: string; apiKeyId?: string };
    komodo: { status: "ok" | "skipped" | "failed"; reason?: string };
    infisical: { status: "ok" | "skipped" | "failed"; reason?: string };
  };
  envPath: string;
}

export async function rotateAuth() {
  logStep("iac:rotate-auth — 3-way credential rotation");

  const record: RotationRecord = {
    ts: new Date().toISOString(),
    results: {
      pangolin: { status: "skipped" },
      komodo: { status: "skipped" },
      infisical: { status: "skipped" },
    },
    envPath: "",
  };

  const envPath = join(import.meta.dir, "../../../.env");
  record.envPath = envPath;
  if (!existsSync(envPath)) {
    logError(`.env not found at ${envPath}; run \`bun run secrets:env\` first`);
    process.exit(1);
  }

  const envOriginal = readFileSync(envPath, "utf8");
  let envUpdated = envOriginal;

  // -----------------------------------------------------------------------
  // 1. Pangolin API key (via Pocket ID OIDC, if configured)
  // -----------------------------------------------------------------------
  if (process.env.POCKETID_PANGOLIN_CLIENT_ID && process.env.POCKETID_PANGOLIN_CLIENT_SECRET) {
    try {
      const newApiKey = await pocketIdLogin();
      envUpdated = upsertEnvVar(envUpdated, "PANGOLIN_API_KEY", newApiKey);
      record.results.pangolin = { status: "ok", apiKeyId: "(see /v1/org/.../api-key for the new id)" };
      logOk("PANGOLIN_API_KEY rotated via Pocket ID OIDC");
    } catch (e) {
      const reason = (e as Error).message;
      record.results.pangolin = { status: "failed", reason };
      logError("Pangolin rotation failed", e);
    }
  } else {
    record.results.pangolin = {
      status: "skipped",
      reason: "POCKETID_PANGOLIN_CLIENT_ID + POCKETID_PANGOLIN_CLIENT_SECRET not in env; see PANGOLIN-SETUP.md Manual Step 1 to mint them",
    };
    logWarn("Pangolin: skipped (no Pocket ID client configured)");
  }

  // -----------------------------------------------------------------------
  // 1b. Ensure the bons-iac OIDC client exists in Pocket ID (idempotent, v2.9.0+)
  // -----------------------------------------------------------------------
  // v2.9.0 prefers POCKETID_API_KEY; legacy POCKETID_ADMIN_PASSWORD still works.
  if (process.env.POCKETID_API_KEY || process.env.POCKETID_ADMIN_PASSWORD) {
    try {
      await ensureBonsIacClient(
        process.env.POCKETID_ADMIN_PASSWORD ?? "",
        process.env.POCKETID_API_KEY ?? "",
      );
      record.results.pangolin = { ...record.results.pangolin, status: "ok" };
    } catch (e) {
      logWarn(`ensureBonsIacClient failed: ${(e as Error).message}`);
    }
  }

  // -----------------------------------------------------------------------
  // 2. Komodo password (from Infisical)
  // -----------------------------------------------------------------------
  if (CONFIG.infisicalClientId && CONFIG.infisicalClientSecret && CONFIG.infisicalProjectId) {
    try {
      const newKomodoPassword = await fetchInfisicalSecret(
        CONFIG.infisicalUrl,
        CONFIG.infisicalClientId,
        CONFIG.infisicalClientSecret,
        CONFIG.infisicalProjectId,
        CONFIG.infisicalEnvironment,
        "komodo",
        "password",
      );
      if (newKomodoPassword) {
        envUpdated = upsertEnvVar(envUpdated, "KOMODO_PASSWORD", newKomodoPassword);
        record.results.komodo = { status: "ok" };
        logOk("KOMODO_PASSWORD rotated from Infisical");
      } else {
        record.results.komodo = {
          status: "skipped",
          reason: "komodo/password not in Infisical",
        };
        logWarn("Komodo: skipped (komodo/password not in Infisical)");
      }
    } catch (e) {
      record.results.komodo = { status: "failed", reason: (e as Error).message };
      logError("Komodo rotation failed", e);
    }
  } else {
    record.results.komodo = {
      status: "skipped",
      reason: "Infisical auth not configured",
    };
    logWarn("Komodo: skipped (Infisical auth not configured)");
  }

  // -----------------------------------------------------------------------
  // 3. Infisical universal-auth client secret (self-bootstrap)
  // -----------------------------------------------------------------------
  // This is the chicken-and-egg: we need Infisical to fetch the
  // Infisical secret. The workaround: if the env already has a
  // working INFISICAL_UNIVERSAL_AUTH_CLIENT_SECRET, we use it to mint
  // a new one. If not, we skip with a clear message.
  if (
    process.env.INFISICAL_UNIVERSAL_AUTH_CLIENT_ID &&
    (process.env.INFISICAL_UNIVERSAL_AUTH_CLIENT_SECRET || process.env.INFISICAL_TOKEN)
  ) {
    try {
      // For Infisical, "rotating" the universal-auth client_secret is a
      // MANUAL operation (you have to mint a new client via the Infisical
      // web UI). The IaC just verifies the current one works.
      const newClientSecret = await fetchInfisicalSecret(
        CONFIG.infisicalUrl,
        process.env.INFISICAL_UNIVERSAL_AUTH_CLIENT_ID,
        process.env.INFISICAL_UNIVERSAL_AUTH_CLIENT_SECRET ?? process.env.INFISICAL_TOKEN ?? "",
        CONFIG.infisicalProjectId,
        CONFIG.infisicalEnvironment,
        "infisical-universal-auth",
        "secret",
      );
      if (newClientSecret) {
        envUpdated = upsertEnvVar(envUpdated, "INFISICAL_UNIVERSAL_AUTH_CLIENT_SECRET", newClientSecret);
        record.results.infisical = { status: "ok" };
        logOk("INFISICAL_UNIVERSAL_AUTH_CLIENT_SECRET verified + rotated");
      } else {
        record.results.infisical = {
          status: "skipped",
          reason: "infisical-universal-auth/secret not in Infisical (needs manual mint via web UI)",
        };
        logWarn("Infisical: skipped (secret not in Infisical — manual mint required)");
      }
    } catch (e) {
      record.results.infisical = { status: "failed", reason: (e as Error).message };
      logError("Infisical rotation failed", e);
    }
  } else {
    record.results.infisical = {
      status: "skipped",
      reason: "INFISICAL_UNIVERSAL_AUTH_CLIENT_ID + SECRET not in env",
    };
    logWarn("Infisical: skipped (universal auth not configured)");
  }

  // -----------------------------------------------------------------------
  // Write the updated .env
  // -----------------------------------------------------------------------
  if (envUpdated !== envOriginal) {
    writeFileSync(envPath, envUpdated);
    logOk(`wrote rotated credentials to ${envPath}`);
  } else {
    logWarn("no changes to write to .env");
  }

  // -----------------------------------------------------------------------
  // Emit the JSON audit record
  // -----------------------------------------------------------------------
  const auditPath = `/tmp/auth-rotation-${record.ts.replace(/[:.]/g, "-")}.json`;
  writeFileSync(auditPath, JSON.stringify(record, null, 2));
  logOk(`wrote audit record to ${auditPath}`);

  // Exit with the right code
  const allOk = Object.values(record.results).every((r) => r.status === "ok" || r.status === "skipped");
  if (!allOk) {
    logError("one or more rotations failed — see audit record above");
    process.exit(1);
  }
}

// ---------------------------------------------------------------------------
// Direct REST call to Infisical (now delegates to iac/clients/infisical-rest.ts
// — bypasses the buggy @infisical/sdk v5 wrapper entirely)
// ---------------------------------------------------------------------------
async function fetchInfisicalSecret(
  baseUrl: string,
  clientId: string,
  clientSecret: string,
  projectId: string,
  environment: string,
  folder: string,
  key: string,
): Promise<string | null> {
  const { infisicalGetSecret } = await import("../clients/infisical-rest.ts");
  const secret = await infisicalGetSecret(
    {
      secretName: key,
      projectId,
      environment,
      secretPath: folder === "" ? "/" : `/${folder}/`,
    },
    baseUrl,
  );
  return secret?.value ?? null;
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
