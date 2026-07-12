// bonneagar/iac/commands/sync-secrets.ts — Sync Infisical secrets from secrets.env refs

import { log, logStep, logOk, logError, logWarn } from "../cli.ts";
import { discoverSecrets } from "../sources/discover-secrets.ts";
import { ensureInfisicalAuth } from "../auth.ts";
import { CLI_FLAGS } from "../cli.ts";

export async function syncSecrets() {
  logStep("sync-secrets");
  const secrets = discoverSecrets();
  if (secrets.length === 0) {
    logWarn("no secrets discovered in any stack's secrets.env");
    return;
  }

  log(`  discovered ${secrets.length} secret refs`);

  if (CLI_FLAGS.dryRun) {
    log(`  --dry-run: would sync ${secrets.length} secrets`);
    return;
  }

  const client = await ensureInfisicalAuth();
  let created = 0, updated = 0, skipped = 0;
  for (const secret of secrets) {
    try {
      // Read the actual value from the .env (which Locket hydrates)
      // The env var name is in secret.comment (format: "env_var=KEY, stack=STACK")
      const envVarMatch = secret.comment?.match(/env_var=([A-Z_][A-Z0-9_]*)/);
      if (!envVarMatch) { skipped++; continue; }
      const envVar = envVarMatch[1];
      const value = process.env[envVar];
      if (!value) { logWarn(`env var ${envVar} not set in .env; skipping ${secret.key}`); skipped++; continue; }
      secret.value = value;

      const existing = await client.getSecret(secret.projectId, secret.environment, secret.key, secret.path);
      if (existing) {
        await client.updateSecret(secret);
        logOk(`${secret.path}/${secret.key} (updated)`);
        updated++;
      } else {
        await client.createSecret(secret);
        logOk(`${secret.path}/${secret.key} (created)`);
        created++;
      }
    } catch (e) {
      logError(`${secret.path}/${secret.key}`, e);
    }
  }
  log(`  created: ${created}, updated: ${updated}, skipped: ${skipped}`);
}
