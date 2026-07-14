// tests/iac/verify_planetscale_databases.test.ts
//
// Per openspec/changes/2026-07-19-planetscale-postgres-migration-phase-b0-v1/.
//
// Smoke test for the read-only verifier. Phase B.0 ships the stub that
// throws (because the PlanetScale API client is not yet wired); this
// test confirms the verifier produces the expected error message that
// points the operator at the dashboard.

import { describe, it, expect } from "bun:test";

const { verifyPlanetScaleDatabases } = await import(
  "../../bonneagar/iac/procedures/verify_planetscale_databases"
);

describe("verifyPlanetScaleDatabases — Phase B.0 stub behaviour", () => {
  it("returns ok=false when the API client is not yet wired", async () => {
    const result = await verifyPlanetScaleDatabases();
    expect(result.ok).toBe(false);
    expect(result.expected.sort()).toEqual([
      "convex_production",
      "dagster_state",
      "lakekeeper",
    ]);
    expect(result.missing).toEqual(result.expected);
  });

  it("the error message points the operator at the PlanetScale dashboard", async () => {
    const result = await verifyPlanetScaleDatabases();
    expect(result.message).toMatch(/PlanetScale dashboard/);
    expect(result.message).toMatch(/eu-west-3\.pg\.psdb\.cloud/);
    expect(result.message).toMatch(/Phase B\.1 will wire/);
  });

  it("the error message lists the 3 expected databases", async () => {
    const result = await verifyPlanetScaleDatabases();
    expect(result.message).toContain("lakekeeper");
    expect(result.message).toContain("dagster_state");
    expect(result.message).toContain("convex_production");
  });
});