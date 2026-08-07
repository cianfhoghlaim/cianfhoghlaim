// bonneagar/iac/commands/sync-resources.ts — Sync Pangolin private resources
// Fixes blocker #2: DELETE-then-CREATE the 3 manually-created resources (komodo, cal-diy, infisical)

import { log, logStep, logOk, logError, logWarn } from "../cli.ts";
import { discoverResources } from "../sources/discover-resources.ts";
import { ensurePangolinAuth } from "../auth.ts";
import { CLI_FLAGS } from "../cli.ts";

// The 4 manually-created resources that override the blueprints (per
// DEPLOYMENT-STRATEGY.md blocker #2). `openchamber` added 2026-08-07 — same
// shadowing pattern (existing resource skips the create path, so a stale
// site/destination binding never gets corrected without an explicit
// delete+recreate).
const MANUAL_OVERRIDE_NICE_IDS = new Set(["komodo", "cal-diy", "infisical", "openchamber"]);

export async function syncResources() {
  logStep("sync-resources");

  const client = await ensurePangolinAuth();
  const { data: existing } = await client.listResources();
  const existingByNiceId = new Map(existing.siteResources.map((r) => [r.niceId, r]));

  // Live site name -> siteId map, so discoverResources() can resolve each
  // stack's `site:` field against reality instead of a hardcoded guess.
  const { data: sitesData } = await client.listSites();
  const siteIdsByName = Object.fromEntries(sitesData.sites.map((s) => [s.name, s.id as number]));
  log(`  resolved ${Object.keys(siteIdsByName).length} live sites: ${Object.entries(siteIdsByName).map(([n, i]) => `${n}=${i}`).join(", ")}`);

  const iacResources = discoverResources(undefined, { siteIdsByName });
  if (iacResources.length === 0) {
    logWarn("no Pangolin resources discovered in any stack's pangolin.yaml");
    return;
  }
  log(`  discovered ${iacResources.length} resources`);

  if (CLI_FLAGS.dryRun) {
    log(`  --dry-run: would sync ${iacResources.length} resources`);
    for (const r of iacResources) {
      const found = existingByNiceId.get(r.niceId);
      const action = found ? "update" : "create";
      log(`    ${action} ${r.niceId} -> ${r.destination}:${r.destinationPort}`);
    }
    return;
  }

  for (const r of iacResources) {
    try {
      const found = existingByNiceId.get(r.niceId);
      if (MANUAL_OVERRIDE_NICE_IDS.has(r.niceId) && found) {
        // DELETE then CREATE (fixes blocker #2)
        log(`  fix: deleting manual override ${r.niceId} (id=${found.siteResourceId})`);
        await client.deleteSiteResource(found.siteResourceId);
        await client.createSiteResource(r);
        logOk(`${r.niceId} (deleted + recreated)`);
      } else if (found) {
        // Skip — the existing resource matches the IaC-declared one
        log(`  - skip ${r.niceId} (already exists)`);
      } else {
        await client.createSiteResource(r);
        logOk(`${r.niceId} (created)`);
      }
    } catch (e) {
      logError(`${r.niceId}`, e);
    }
  }
}
