// bonneagar/iac/planetscale-postgres.ts — PlanetScale PostgreSQL connection helper
//
// Per openspec/changes/2026-07-19-planetscale-postgres-migration-phase-b0-v1/
//
// Phase B.0 ships 3 stacks to PlanetScale PG:
//   - Lakekeeper (hard switch — local postgres removed)
//   - Convex self-host (hard switch — local SQLite removed)
//   - Dagster / DuckLake (env swap only — local postgres kept as fallback)
//
// Phase B.0 uses **manual dashboard provisioning** (per operator choice):
//   - The operator creates the PlanetScale branch + 3 databases via the
//     PlanetScale dashboard
//   - The operator creates 3 Infisical secrets (lakekeeper/database_url,
//     dagster/database_url, convex/database_url)
//   - This file RESOLVES those secrets at runtime (via Locket) into the
//     canonical PlanetScale PG URL format
//
// Companion file: procedures/verify_planetscale_databases.ts — the
// read-only verifier that asserts the 3 databases exist before deploy.
//
// Per ADR openspec/architecture-decisions/0005-planetscale-postgres-centralisation.md
// § "Connection conventions":
//   - TLS: ?sslmode=verify-full
//   - URL format: postgresql://<user>:<pwd>@<host>.pg.psdb.cloud/<db>?sslmode=verify-full

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface PlanetScaleConfig {
  host: string;
  branch: string;
  sslMode: "verify-full" | "require" | "prefer";
}

export interface StackDatabaseMapping {
  /** Infisical path segment (used as the secret's path under dev-baile/) */
  stackSlug: string;
  /** PlanetScale PG database name */
  databaseName: string;
}

// ---------------------------------------------------------------------------
// Defaults
// ---------------------------------------------------------------------------

const DEFAULT_CONFIG: PlanetScaleConfig = {
  host: process.env.PLANETSCALE_HOST ?? "eu-west-3.pg.psdb.cloud",
  branch: process.env.PLANETSCALE_BRANCH ?? "bunchloch-prod",
  sslMode: "verify-full",
};

/**
 * The canonical mapping of stack → PlanetScale database name for Phase B.0.
 *
 * Phase B.1+ will add additional mappings as more stacks migrate.
 */
export const PHASE_B0_DATABASE_MAP: Record<string, StackDatabaseMapping> = {
  lakekeeper: { stackSlug: "lakekeeper", databaseName: "lakekeeper" },
  convex:     { stackSlug: "convex",     databaseName: "convex_production" },
  dagster:    { stackSlug: "dagster",    databaseName: "dagster_state" },
};

// ---------------------------------------------------------------------------
// LCP integration — resolve Infisical secrets via Locket
// ---------------------------------------------------------------------------

/**
 * Resolve an Infisical secret via Locket. Locket injects secrets into the
 * process env at container start; the Infisical CLI is a fallback when
 * Locket is unavailable.
 *
 * In production, Locket sidecars mount the resolved secrets as files at
 * `/run/secrets/<secret-name>`; this helper reads from process.env first
 * (the canonical path) then falls back to file lookup then to Infisical CLI.
 */
async function resolveInfisicalSecret(secretPath: string): Promise<string> {
  // Convention: secrets are exposed as env vars of the form
  // `SECRET_<UPPER_SNAKE>` after LCP resolution
  const envVar = `SECRET_${secretPath.replace(/[\/.-]/g, "_").toUpperCase()}`;
  const fromEnv = process.env[envVar];
  if (fromEnv) return fromEnv;

  // Fallback 1: Locket mounts /run/secrets/<slug>
  // (out of scope for this file — assumes the operator has Locket wired)
  // Fallback 2: Infisical CLI (last resort)
  // We don't shell out here because this file is consumed at module-import
  // time by compose.yaml; the caller is expected to use this function
  // at IaC-plan time when Locket secrets are already resolved.
  throw new Error(
    `Locket-injected secret not found in process.env: ${envVar}. ` +
    `Ensure the operator has created the Infisical secret at dev-baile/${secretPath} ` +
    `and that Locket resolves it before this module loads.`,
  );
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/**
 * Resolve the canonical PlanetScale PG connection URL for a stack.
 *
 * Usage:
 *   import { resolvePlanetScaleDatabaseUrl } from "./planetscale-postgres";
 *   const url = await resolvePlanetScaleDatabaseUrl("lakekeeper");
 *   // → "postgresql://<user>:<pwd>@eu-west-3.pg.psdb.cloud/lakekeeper?sslmode=verify-full"
 */
export async function resolvePlanetScaleDatabaseUrl(
  stack: keyof typeof PHASE_B0_DATABASE_MAP,
  cfg: PlanetScaleConfig = DEFAULT_CONFIG,
): Promise<string> {
  const mapping = PHASE_B0_DATABASE_MAP[stack];
  if (!mapping) {
    throw new Error(
      `Unknown stack "${stack}" — no PlanetScale database mapping. ` +
      `Phase B.0 supports: ${Object.keys(PHASE_B0_DATABASE_MAP).join(", ")}.`,
    );
  }

  // Infisical paths: dev-baile/<stack>/db_user, dev-baile/<stack>/db_password
  const userSecretPath = `${mapping.stackSlug}/db_user`;
  const pwdSecretPath  = `${mapping.stackSlug}/db_password`;

  const user = await resolveInfisicalSecret(userSecretPath);
  const pwd  = await resolveInfisicalSecret(pwdSecretPath);

  return `postgresql://${user}:${pwd}@${cfg.host}/${mapping.databaseName}?sslmode=${cfg.sslMode}`;
}

/**
 * List the required Phase B.0 databases.
 */
export function listPhaseB0Databases(): string[] {
  return Object.values(PHASE_B0_DATABASE_MAP).map((m) => m.databaseName);
}

/**
 * List the actual PlanetScale databases on the branch.
 * Uses the PlanetScale API (POST /v1/organizations/{org}/databases).
 *
 * In production, this requires a `PLANETSCALE_API_TOKEN` secret in Infisical
 * (not Phase B.0 scope). Phase B.1 will wire the read-only verifier.
 */
export async function listPlanetScaleDatabases(
  cfg: PlanetScaleConfig = DEFAULT_CONFIG,
): Promise<string[]> {
  // Phase B.0 ships this as a stub — the actual PlanetScale API client
  // (via the @planetscale/client npm package or the REST API) lands in Phase B.1.
  // For Phase B.0, the operator verifies the 3 databases exist manually
  // via the PlanetScale dashboard; this function throws with a clear
  // error if called.
  throw new Error(
    `listPlanetScaleDatabases() is not yet implemented in Phase B.0. ` +
    `Use the PlanetScale dashboard to verify the 3 databases exist: ` +
    listPhaseB0Databases().join(", ") + ". " +
    `Phase B.1 will wire the @planetscale/client API client.`,
  );
}