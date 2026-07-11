// bonneagar/iac/auth-pocketid-admin.ts — Pocket ID admin API client
//
// The admin API requires session-cookie auth (NOT a bearer token).
// Login is done via POST /api/v1/oidc/users/me/login with username + password
// (yes, Pocket ID still supports password-based admin login in v2.9.0,
// even though the user-facing flow is passkey-only).
//
// After login, the session cookie is sent with every admin request.
// Used by `bootstrap-pocketid-admin` to:
//   - Set signupEnabled (enables the /signup/* endpoints)
//   - Create signup tokens
//   - Create the first user (via signup token redemption)
//   - Create OIDC clients (e.g. bons-iac)
//   - Disable signup after bootstrap is complete
//   - Rotate signing keys
//
// Spec: openspec/changes/2026-07-14-tightly-knit-auth-stack-v1
// =============================================================================

import { fetch } from "undici";

const POCKETID_ISSUER = process.env.POCKETID_URL ?? "https://auth.cianfhoghlaim.ie";

interface SessionCookie {
  cookie: string;        // full "session=<token>" pair
  expiresAt: number;     // unix seconds
}

export interface OidcClientSummary {
  id: string;
  name: string;
  clientId: string;       // public client_id (the OIDC client identifier)
  createdAt: string;
  redirectUris?: string[];
  grantTypes?: string[];
}

export interface CreateOidcClientInput {
  name: string;
  redirectUris: string[];   // e.g. ['https://pangolin.cianfhoghlaim.ie']
  grantTypes: string[];     // e.g. ['authorization_code'] or ['client_credentials']
  scopes?: string[];        // defaults to ['openid', 'profile', 'email']
  isPublic?: boolean;       // false = confidential client (default)
}

export interface CreateOidcClientResult {
  id: string;
  clientId: string;
  clientSecret: string;     // only returned on create
  name: string;
}

export interface UserSummary {
  id: string;
  username: string;
  email: string;
  isAdmin: boolean;
  disabled: boolean;
  createdAt: string;
}

export interface PocketIdHealth {
  healthy: boolean;
  dbUsers: number;
  dbOidcClients: number;
  version: string;
  signupEnabled: boolean;
  healthyDetail: string;
}

// ---------------------------------------------------------------------------
// Session login (admin)
// ---------------------------------------------------------------------------

/**
 * Login to Pocket ID as a user (username + password). Returns the
 * session cookie that admin endpoints require. Pocket ID v2.9.0 supports
 * password login for users who have a password set, even though the
 * user-facing flow is passkey-only.
 *
 * Throws if the user doesn't exist or has no password.
 */
export async function pocketIdAdminLogin(
  username: string,
  password: string,
): Promise<SessionCookie> {
  const r = await fetch(`${POCKETID_ISSUER}/api/v1/oidc/users/me/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ username, password }).toString(),
    redirect: "manual",
  });
  // Pocket ID returns 303 with Set-Cookie on success
  if (r.status !== 303 && r.status !== 200) {
    throw new Error(`pocketid admin login failed: ${r.status} ${await r.text()}`);
  }
  const setCookie = r.headers.get("set-cookie");
  if (!setCookie) {
    throw new Error(`pocketid admin login returned ${r.status} but no Set-Cookie header`);
  }
  const sessionMatch = setCookie.match(/session=([^;]+)/);
  if (!sessionMatch) {
    throw new Error(`pocketid admin login: Set-Cookie has no session token`);
  }
  return { cookie: `session=${sessionMatch[1]}`, expiresAt: Date.now() / 1000 + 3600 * 24 };
}

// ---------------------------------------------------------------------------
// Health
// ---------------------------------------------------------------------------

/**
 * Returns the live health of the running Pocket ID instance. Uses
 * the .well-known/openid-configuration (public, no auth) + a
 * direct sqlite query (via docker exec, since the admin API is
 * gated behind auth) for DB stats.
 */
export async function pocketIdHealth(): Promise<PocketIdHealth> {
  // 1. OIDC discovery (no auth)
  const r = await fetch(`${POCKETID_ISSUER}/.well-known/openid-configuration`, {
    signal: AbortSignal.timeout(5000),
  });
  if (!r.ok) {
    return {
      healthy: false, dbUsers: 0, dbOidcClients: 0,
      version: "unknown", signupEnabled: false,
      healthyDetail: `OIDC discovery returned ${r.status}`,
    };
  }
  const d = await r.json() as { issuer?: string };

  // 2. Container version (via docker exec — requires pocket-id container; 3s timeout)
  let version = "unknown";
  try {
    const v = (await Promise.race([
      new Promise<{ stdout: string }>((resolve, reject) => {
        const cp = require("node:child_process").spawn("docker", [
          "exec", "pocket-id", "/app/pocket-id", "version",
        ]);
        let out = "";
        cp.stdout.on("data", (d: Buffer) => out += d.toString());
        cp.on("close", (code: number) => code === 0 ? resolve({ stdout: out }) : reject(new Error(`exit ${code}`)));
        cp.on("error", reject);
      }),
      new Promise<{ stdout: string }>((_, reject) => setTimeout(() => reject(new Error("timeout")), 3000)),
    ])).stdout.trim();
    // Strip the "pocket-id " prefix to get a clean version string
    version = v.replace(/^pocket-id\s+/, "") || "unknown";
  } catch {
    // Couldn't query the container; assume OIDC discovery is enough
  }

  // 3. DB stats (via docker exec sqlite query) — with 3s timeout + fallback
  let dbUsers = 0, dbOidcClients = 0, signupEnabled = false;
  try {
    const db = (await Promise.race([
      new Promise<{ stdout: string }>((resolve, reject) => {
        const cp = require("node:child_process").spawn("docker", [
          "exec", "pocket-id", "sh", "-c",
          "test -x /usr/bin/sqlite3 && sqlite3 /app/data/pocket-id.db \"SELECT (SELECT COUNT(*) FROM users), (SELECT COUNT(*) FROM oidc_clients), COALESCE((SELECT value FROM app_config_variables WHERE key='signupEnabled'), 'false');\" || echo 'no-sqlite3'",
        ]);
        let out = "";
        cp.stdout.on("data", (d: Buffer) => out += d.toString());
        cp.on("close", (code: number) => code === 0 ? resolve({ stdout: out }) : reject(new Error(`exit ${code}`)));
        cp.on("error", reject);
      }),
      new Promise<{ stdout: string }>((_, reject) => setTimeout(() => reject(new Error("timeout")), 3000)),
    ])).stdout.trim();
    if (db && db !== "no-sqlite3" && !db.startsWith("no-sqlite3")) {
      const parts = db.split("|");
      dbUsers = parseInt(parts[0] || "0", 10);
      dbOidcClients = parseInt(parts[1] || "0", 10);
      signupEnabled = (parts[2] || "").trim().toLowerCase() === "true";
    } else {
      // sqlite3 not in container; can't query DB stats. Report OIDC discovery only.
    }
  } catch {
    // Best-effort; defaults to 0
  }

  return {
    healthy: d.issuer === POCKETID_ISSUER,
    dbUsers, dbOidcClients, version, signupEnabled,
    healthyDetail: `issuer=${d.issuer}`,
  };
}

// ---------------------------------------------------------------------------
// Signup enable/disable (for the bootstrap flow)
// ---------------------------------------------------------------------------

/**
 * Toggle signupEnabled in Pocket ID's app_config_variables. Requires
 * admin session cookie.
 *
 * NOTE: Pocket ID's admin UI uses a generic config-update endpoint.
 * The actual endpoint path is `/api/v1/admin/application-configuration`
 * (per the v2.9.0 source at /settings/admin/application-configuration).
 */
export async function pocketIdSetSignupEnabled(
  adminCookie: string,
  enabled: boolean,
): Promise<void> {
  const r = await fetch(`${POCKETID_ISSUER}/api/v1/admin/application-configuration/signup-enabled`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      Cookie: adminCookie,
    },
    body: JSON.stringify({ value: enabled }),
  });
  if (!r.ok && r.status !== 404) {
    throw new Error(`pocketid set signup-enabled failed: ${r.status} ${await r.text()}`);
  }
  // If 404, fall back to the generic update endpoint
  if (r.status === 404) {
    const r2 = await fetch(`${POCKETID_ISSUER}/api/v1/admin/application-configuration`, {
      method: "PUT",
      headers: { "Content-Type": "application/json", Cookie: adminCookie },
      body: JSON.stringify({ signupEnabled: { value: enabled } }),
    });
    if (!r2.ok) {
      throw new Error(`pocketid set signup-enabled (fallback) failed: ${r2.status} ${await r2.text()}`);
    }
  }
}

// ---------------------------------------------------------------------------
// Signup tokens (for the bootstrap flow)
// ---------------------------------------------------------------------------

/**
 * Create a signup token. The token is a one-time-use URL that the
 * operator can visit in a browser to register a passkey.
 *
 * Returns the token string (the URL path is `/st/<token>`).
 */
export async function pocketIdCreateSignupToken(
  adminCookie: string,
  opts: { username: string; email: string; expiresIn?: number } = {
    username: "ciansedai", email: "ciansedai@cianfhoghlaim.ie",
  },
): Promise<{ token: string; expiresAt: string; url: string }> {
  const r = await fetch(`${POCKETID_ISSUER}/api/v1/admin/signup-tokens`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Cookie: adminCookie },
    body: JSON.stringify({
      username: opts.username,
      email: opts.email,
      expiresIn: opts.expiresIn ?? 3600,  // 1 hour
    }),
  });
  if (!r.ok) {
    throw new Error(`pocketid create signup-token failed: ${r.status} ${await r.text()}`);
  }
  const data = await r.json() as { id: string; token: string; expiresAt: string };
  return { token: data.token, expiresAt: data.expiresAt, url: `${POCKETID_ISSUER}/st/${data.token}` };
}

// ---------------------------------------------------------------------------
// OIDC clients (for the bons-iac client + Pangolin admin SSO client)
// ---------------------------------------------------------------------------

/**
 * List all OIDC clients in Pocket ID.
 */
export async function pocketIdListOidcClients(
  adminCookie: string,
): Promise<OidcClientSummary[]> {
  const r = await fetch(`${POCKETID_ISSUER}/api/v1/oidc/clients`, {
    headers: { Cookie: adminCookie },
  });
  if (!r.ok) {
    throw new Error(`pocketid list oidc-clients failed: ${r.status} ${await r.text()}`);
  }
  const data = await r.json() as { data: OidcClientSummary[] } | OidcClientSummary[];
  const list = Array.isArray(data) ? data : (data as { data: OidcClientSummary[] }).data ?? [];
  return list;
}

/**
 * Create a new OIDC client. Returns the client_id + client_secret
 * (the client_secret is only available on create, not on subsequent
 * reads — so the caller MUST persist it to Infisical immediately).
 */
export async function pocketIdCreateOidcClient(
  adminCookie: string,
  input: CreateOidcClientInput,
): Promise<CreateOidcClientResult> {
  const r = await fetch(`${POCKETID_ISSUER}/api/v1/oidc/clients`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Cookie: adminCookie },
    body: JSON.stringify({
      name: input.name,
      redirectUris: input.redirectUris,
      grantTypes: input.grantTypes,
      scopes: input.scopes ?? ["openid", "profile", "email"],
      isPublic: input.isPublic ?? false,
    }),
  });
  if (!r.ok) {
    throw new Error(`pocketid create oidc-client failed: ${r.status} ${await r.text()}`);
  }
  const data = await r.json() as { data: CreateOidcClientResult } | CreateOidcClientResult;
  const result = "data" in data ? data.data : data;
  if (!result.clientId || !result.clientSecret) {
    throw new Error(`pocketid create oidc-client: response missing clientId/clientSecret`);
  }
  return result;
}

/**
 * Get a specific OIDC client by ID.
 */
export async function pocketIdGetOidcClient(
  adminCookie: string,
  id: string,
): Promise<OidcClientSummary | null> {
  const r = await fetch(`${POCKETID_ISSUER}/api/v1/oidc/clients/${id}`, {
    headers: { Cookie: adminCookie },
  });
  if (r.status === 404) return null;
  if (!r.ok) {
    throw new Error(`pocketid get oidc-client failed: ${r.status} ${await r.text()}`);
  }
  return (await r.json()) as OidcClientSummary;
}

// ---------------------------------------------------------------------------
// Users (for admin verification + first-user management)
// ---------------------------------------------------------------------------

/**
 * List all users in Pocket ID. Used by iac:health to count.
 */
export async function pocketIdListUsers(
  adminCookie: string,
): Promise<UserSummary[]> {
  const r = await fetch(`${POCKETID_ISSUER}/api/v1/users`, {
    headers: { Cookie: adminCookie },
  });
  if (!r.ok) {
    throw new Error(`pocketid list users failed: ${r.status} ${await r.text()}`);
  }
  const data = await r.json() as { data: UserSummary[] } | UserSummary[];
  return Array.isArray(data) ? data : (data as { data: UserSummary[] }).data ?? [];
}

/**
 * Disable signup (post-bootstrap).
 * (Reuses pocketIdSetSignupEnabled for the actual work.)
 */
export const pocketIdDisableSignup = (adminCookie: string) =>
  pocketIdSetSignupEnabled(adminCookie, false);

/**
 * Enable signup (for the bootstrap workflow).
 */
export const pocketIdEnableSignup = (adminCookie: string) =>
  pocketIdSetSignupEnabled(adminCookie, true);

// ---------------------------------------------------------------------------
// Key rotation (for periodic security hygiene)
// ---------------------------------------------------------------------------

/**
 * Rotate the JWT signing key. Old tokens become invalid.
 * Returns the new key (the IaC should write it to .env).
 */
export async function pocketIdRotateSigningKey(
  adminCookie: string,
): Promise<{ newKeyId: string }> {
  const r = await fetch(`${POCKETID_ISSUER}/api/v1/admin/jwt/rotate`, {
    method: "POST",
    headers: { Cookie: adminCookie },
  });
  if (!r.ok) {
    throw new Error(`pocketid rotate jwt failed: ${r.status} ${await r.text()}`);
  }
  const data = await r.json() as { newKeyId: string };
  return data;
}
