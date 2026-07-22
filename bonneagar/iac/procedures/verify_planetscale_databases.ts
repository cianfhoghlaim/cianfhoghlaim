// bonneagar/iac/procedures/verify_planetscale_databases.ts
//
// Per openspec/changes/2026-07-19-planetscale-postgres-migration-phase-b0-v1/.
//
// Phase B.0 ships with **manual dashboard provisioning** (per operator choice).
// This procedure is the READ-ONLY verifier that runs at IaC-plan time
// to assert the 3 required Phase B.0 databases exist on the PlanetScale
// branch BEFORE compose.yaml is deployed.
//
// If a database is missing, this procedure throws with a clear message
// directing the operator to the PlanetScale dashboard. The operator
// creates the database via the dashboard + re-runs `bun run iac:plan`.
//
// Phase B.1 will replace this stub with a full PlanetScale API client
// (via @planetscale/client or the REST API).

import { listPhaseB0Databases, listPlanetScaleDatabases } from "../planetscale-postgres";

export interface VerifyResult {
  ok: boolean;
  expected: string[];
  actual: string[];
  missing: string[];
  message: string;
}

export async function verifyPlanetScaleDatabases(): Promise<VerifyResult> {
  const expected = listPhaseB0Databases().sort();

  let actual: string[] = [];
  let apiError: Error | null = null;
  try {
    actual = (await listPlanetScaleDatabases()).sort();
  } catch (e) {
    apiError = e as Error;
  }

  if (apiError) {
    return {
      ok: false,
      expected,
      actual: [],
      missing: expected,
      message:
        `PlanetScale API client is not yet wired in Phase B.0. ` +
        `Use the PlanetScale dashboard to manually verify these ` +
        `${expected.length} databases exist on the PlanetScale ` +
        `branch (eu-west-3.pg.psdb.cloud):\n  - ${expected.join("\n  - ")}\n` +
        `Phase B.1 will wire the @planetscale/client API client.`,
    };
  }

  const missing = expected.filter((db) => !actual.includes(db));

  return {
    ok: missing.length === 0,
    expected,
    actual,
    missing,
    message:
      missing.length === 0
        ? `All ${expected.length} Phase B.0 databases present on PlanetScale branch.`
        : `Missing ${missing.length} Phase B.0 database(s): ${missing.join(", ")}.`,
  };
}

// CLI entrypoint
if (typeof require !== "undefined" && require.main === module) {
  verifyPlanetScaleDatabases()
    .then((result) => {
      console.log(result.message);
      if (!result.ok) {
        console.error("Expected:", result.expected);
        console.error("Actual:", result.actual);
        console.error("Missing:", result.missing);
        process.exit(1);
      }
      process.exit(0);
    })
    .catch((e) => {
      console.error("Verifier threw:", e);
      process.exit(2);
    });
}