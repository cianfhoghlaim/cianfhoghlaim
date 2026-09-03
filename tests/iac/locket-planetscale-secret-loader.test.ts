// tests/iac/locket-planetscale-secret-loader.test.ts
//
// Per openspec/changes/2026-07-19-planetscale-postgres-migration-phase-b0-v1/.
//
// Smoke test for the URL format produced by `resolvePlanetScaleDatabaseUrl`.
// This test mocks process.env to simulate Locket-injected secrets.

import { describe, it, expect } from "bun:test";

// Set up the LCP-injected secrets BEFORE importing the module under test
process.env.SECRET_LAKEKEEPER_DB_USER = "planetscale_user_lake";
process.env.SECRET_LAKEKEEPER_DB_PASSWORD = "pscale_pwd_lake_123";
process.env.SECRET_CONVEX_DB_USER = "planetscale_user_convex";
process.env.SECRET_CONVEX_DB_PASSWORD = "pscale_pwd_convex_456";
process.env.SECRET_DAGSTER_DB_USER = "planetscale_user_dagster";
process.env.SECRET_DAGSTER_DB_PASSWORD = "pscale_pwd_dagster_789";
process.env.PLANETSCALE_HOST = "eu-west-3.pg.psdb.cloud";
process.env.PLANETSCALE_BRANCH = "bunchloch-prod";

const {
  resolvePlanetScaleDatabaseUrl,
  listPhaseB0Databases,
  PHASE_B0_DATABASE_MAP,
} = await import("../../bonneagar/iac/planetscale-postgres");

describe("resolvePlanetScaleDatabaseUrl — Phase B.0", () => {
  it("returns the canonical PlanetScale PG URL for Lakekeeper", async () => {
    const url = await resolvePlanetScaleDatabaseUrl("lakekeeper");
    expect(url).toBe(
      "postgresql://planetscale_user_lake:pscale_pwd_lake_123@eu-west-3.pg.psdb.cloud/lakekeeper?sslmode=verify-full",
    );
  });

  it("returns the canonical URL for Convex (clean-start)", async () => {
    const url = await resolvePlanetScaleDatabaseUrl("convex");
    expect(url).toBe(
      "postgresql://planetscale_user_convex:pscale_pwd_convex_456@eu-west-3.pg.psdb.cloud/convex_production?sslmode=verify-full",
    );
  });

  it("returns the canonical URL for Dagster (env swap only)", async () => {
    const url = await resolvePlanetScaleDatabaseUrl("dagster");
    expect(url).toBe(
      "postgresql://planetscale_user_dagster:pscale_pwd_dagster_789@eu-west-3.pg.psdb.cloud/dagster_state?sslmode=verify-full",
    );
  });

  it("throws on unknown stack", async () => {
    await expect(
      // @ts-expect-error — testing the error path
      resolvePlanetScaleDatabaseUrl("nonexistent"),
    ).rejects.toThrow(/Unknown stack "nonexistent"/);
  });

  it("throws on missing LCP secret (the canonical error path)", async () => {
    const original = process.env.SECRET_LAKEKEEPER_DB_USER;
    delete process.env.SECRET_LAKEKEEPER_DB_USER;
    try {
      await expect(resolvePlanetScaleDatabaseUrl("lakekeeper")).rejects.toThrow(
        /Locket-injected secret not found in process.env/,
      );
    } finally {
      process.env.SECRET_LAKEKEEPER_DB_USER = original ?? "";
    }
  });
});

describe("listPhaseB0Databases — Phase B.0", () => {
  it("returns the canonical 3-database list", () => {
    expect(listPhaseB0Databases().sort()).toEqual([
      "convex_production",
      "dagster_state",
      "lakekeeper",
    ]);
  });
});

describe("PHASE_B0_DATABASE_MAP — Phase B.0", () => {
  it("contains exactly 3 mappings", () => {
    expect(Object.keys(PHASE_B0_DATABASE_MAP).sort()).toEqual([
      "convex",
      "dagster",
      "lakekeeper",
    ]);
  });

  it("all mappings use kebab-case slugs (matching Infisical paths)", () => {
    for (const m of Object.values(PHASE_B0_DATABASE_MAP)) {
      expect(m.stackSlug).toMatch(/^[a-z-]+$/);
    }
  });
});