// bonneagar/iac/commands/sync-action-recipients.ts — Sync Komodo ActionRecipients
// (Discord, email, Slack notification channels)

import { log, logStep, logOk, logError, logWarn } from "../cli.ts";
import { ensureKomodoAuth } from "../auth.ts";
import { CLI_FLAGS } from "../cli.ts";

const RECIPIENTS = [
  { name: "discord", kind: "Discord" as const, envVar: "DISCORD_WEBHOOK_URL" },
  { name: "slack", kind: "Slack" as const, envVar: "SLACK_WEBHOOK_URL" },
  { name: "email-admin", kind: "Email" as const, envVar: "ADMIN_EMAIL" },
];

export async function syncActionRecipients() {
  logStep("sync-action-recipients");
  const client = await ensureKomodoAuth();
  log(`  discovered ${RECIPIENTS.length} recipients`);

  if (CLI_FLAGS.dryRun) {
    log(`  --dry-run: would create ${RECIPIENTS.length} recipients`);
    return;
  }

  for (const r of RECIPIENTS) {
    try {
      const url = process.env[r.envVar] ?? "";
      await client.upsertActionRecipient({
        name: r.name,
        config: r.kind === "Email"
          ? { kind: r.kind, recipients: url ? [url] : [] }
          : { kind: r.kind, url },
        tags: ["iac:synced"],
      });
      logOk(r.name);
    } catch (e) {
      logError(r.name, e);
    }
  }
}
