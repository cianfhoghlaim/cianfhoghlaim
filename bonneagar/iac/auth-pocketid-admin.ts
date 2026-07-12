// bonneagar/iac/auth-pocketid-admin.ts — Pocket ID admin API client
//
// Pocket ID v2.9.0 admin API:
//   - Base path: /api/  (NOT /api/v1/oidc/ — that was wrong in v1 of this IaC)
//   - Auth: API key (Bearer token) preferred; session cookie (legacy password login) also works
//
// Used by `bootstrap-pocketid-admin` to:
//   - Set allowUserSignups (enables the /signup/* endpoints; was signupEnabled in old versions)
//   - Create signup tokens
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
 * session cookie that admin endpoints require.
 *
 * v2.9.0 NOTE: Pocket ID is passkey-only by default. Password login
 * only works if an admin has set a password on their account via the
 * admin UI. Most admins will use an API key instead.
 *
 * Throws if the user doesn't exist or has no password.
 */
export async function pocketIdAdminLogin(
  username: string,
  password: string,
): Promise<SessionCookie> {
  const r = await fetch(`${POCKETID_ISSUER}/api/users/me/login`, {
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
// Auth header builder (v2.9.0+: use X-API-Key for API key auth)
// ---------------------------------------------------------------------------

/**
 * Returns the correct Authorization/Cookie header value for admin API calls.
 * - If `apiKey` is provided → `X-API-Key: <key>` (Pocket ID v2.9.0+ preferred)
 * - Otherwise → `Cookie: session=<cookie>` (legacy session login)
 */
export function pocketIdAuthHeader(
  apiKey: string,
  sessionCookie?: string,
): Record<string, string> {
  if (apiKey) {
    return { "X-API-Key": apiKey };
  }
  if (sessionCookie) {
    return { Cookie: sessionCookie };
  }
  throw new Error("pocketid auth required: provide either apiKey or sessionCookie");
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
 * Toggle allowUserSignups in Pocket ID's app_config_variables.
 * v2.9.0 renamed `signupEnabled` → `allowUserSignups` (with values: `disabled`, `withToken`, `open`).
 *
 * Requires admin session cookie OR X-API-Key header (POCKETID_API_KEY).
 */
export async function pocketIdSetSignupEnabled(
  adminCookie: string,
  enabled: boolean,
  apiKey: string = "",
): Promise<void> {
  const authHeaders: Record<string, string> = apiKey
    ? { "X-API-Key": apiKey }
    : { Cookie: adminCookie };
  // v2.9.0 stores the full config as a single JSON list; PUT replaces the whole list.
  // We need to GET the current config, toggle allowUserSignups, then PUT it back.
  // The single-key endpoint was removed in v2.9.0.
  const getR = await fetch(`${POCKETID_ISSUER}/api/application-configuration`, {
    headers: authHeaders,
  });
  if (!getR.ok) {
    throw new Error(`pocketid get app-config failed: ${getR.status} ${await getR.text()}`);
  }
  const current = (await getR.json()) as Array<{ key: string; value: string }>;
  const updated = current.map((c) =>
    c.key === "allowUserSignups"
      ? { ...c, value: enabled ? "open" : "disabled" }
      : c
  );
  // If the key doesn't exist yet, add it
  if (!current.find((c) => c.key === "allowUserSignups")) {
    updated.push({ key: "allowUserSignups", value: enabled ? "open" : "disabled", type: "" });
  }
  const putR = await fetch(`${POCKETID_ISSUER}/api/application-configuration`, {
    method: "PUT",
    headers: { ...authHeaders, "Content-Type": "application/json" },
    body: JSON.stringify(updated),
  });
  if (!putR.ok) {
    throw new Error(`pocketid set allowUserSignups failed: ${putR.status} ${await putR.text()}`);
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
    username: "cianfhoghlaim", email: "cianfhoghlaim@cianfhoghlaim.ie",
  },
  apiKey: string = "",
): Promise<{ token: string; expiresAt: string; url: string }> {
  const authHeaders: Record<string, string> = apiKey
    ? { "X-API-Key": apiKey, "Content-Type": "application/json" }
    : { Cookie: adminCookie, "Content-Type": "application/json" };
  const r = await fetch(`${POCKETID_ISSUER}/api/signup-tokens`, {
    method: "POST",
    headers: authHeaders,
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

/* duplicate-removed legacy block — kept for diff visibility, intentionally blank */

// ---------------------------------------------------------------------------
// OIDC clients (for the bons-iac client + Pangolin admin SSO client)
// ---------------------------------------------------------------------------

/**
 * List all OIDC clients in Pocket ID.
 */
export async function pocketIdListOidcClients(
  adminCookie: string,
  apiKey: string = "",
): Promise<OidcClientSummary[]> {
  const authHeaders: Record<string, string> = apiKey
    ? { "X-API-Key": apiKey }
    : { Cookie: adminCookie };
  const r = await fetch(`${POCKETID_ISSUER}/api/oidc/clients`, {
    headers: authHeaders,
  });
  if (!r.ok) {
    throw new Error(`pocketid list oidc-clients failed: ${r.status} ${await r.text()}`);
  }
  const data = await r.json() as { data: OidcClientSummary[] } | OidcClientSummary[];
  const list = Array.isArray(data) ? data : (data as { data: OidcClientSummary[] }).data ?? [];
  return list;
}

/**
 * Fetch the client_secret for an OIDC client. Pocket ID v2.9.0 returns
 * the secret via a separate POST /api/oidc/clients/:id/secret endpoint
 * (the create response only returns the id, not the secret).
 *
 * Requires admin session cookie OR Bearer token (POCKETID_API_KEY).
 */
export async function pocketIdGetOidcClientSecret(
  adminCookie: string,
  clientId: string,
  apiKey: string = "",
): Promise<string> {
  const authHeaders: Record<string, string> = apiKey
    ? { "X-API-Key": apiKey }
    : { Cookie: adminCookie };
  const r = await fetch(`${POCKETID_ISSUER}/api/oidc/clients/${clientId}/secret`, {
    method: "POST",
    headers: authHeaders,
  });
  if (!r.ok) {
    throw new Error(`pocketid get oidc-client secret failed: ${r.status} ${await r.text()}`);
  }
  const data = await r.json() as { secret?: string };
  if (!data.secret) {
    throw new Error(`pocketid get oidc-client secret: response missing secret`);
  }
  return data.secret;
}

/**
 * Create a new OIDC client. Returns the client_id + client_secret.
 *
 * v2.9.0 behavior: the POST /api/oidc/clients response only includes the id
 * (not the secret). To get the secret, we MUST call POST /api/oidc/clients/{id}/secret.
 * The secret is only available once — re-calling /secret generates a new one.
 */
export async function pocketIdCreateOidcClient(
  adminCookie: string,
  input: CreateOidcClientInput,
  apiKey: string = "",
): Promise<CreateOidcClientResult> {
  const authHeaders: Record<string, string> = apiKey
    ? { "X-API-Key": apiKey, "Content-Type": "application/json" }
    : { Cookie: adminCookie, "Content-Type": "application/json" };
  const r = await fetch(`${POCKETID_ISSUER}/api/oidc/clients`, {
    method: "POST",
    headers: authHeaders,
    body: JSON.stringify({
      name: input.name,
      callbackURLs: input.redirectUris,  // v2.9.0 renamed redirectUris → callbackURLs
      grantTypes: input.grantTypes,
      scopes: input.scopes ?? ["openid", "profile", "email"],
      isPublic: input.isPublic ?? false,
      pkceEnabled: input.grantTypes.includes("authorization_code"),  // PKCE for auth code flow
    }),
  });
  if (!r.ok) {
    throw new Error(`pocketid create oidc-client failed: ${r.status} ${await r.text()}`);
  }
  const data = await r.json() as { data: CreateOidcClientResult } | CreateOidcClientResult;
  const result = "data" in data ? data.data : data;
  if (!result.id) {
    throw new Error(`pocketid create oidc-client: response missing id`);
  }
  // Fetch the secret via the separate endpoint (v2.9.0)
  const secret = await pocketIdGetOidcClientSecret(adminCookie, result.id, apiKey);
  return {
    id: result.id,
    clientId: result.id,  // v2.9.0 uses the id as the public client_id
    clientSecret: secret,
    name: result.name ?? input.name,
  };
}

/**
 * Get a specific OIDC client by ID.
 */
export async function pocketIdGetOidcClient(
  adminCookie: string,
  id: string,
  apiKey: string = "",
): Promise<OidcClientSummary | null> {
  const authHeaders: Record<string, string> = apiKey
    ? { "X-API-Key": apiKey }
    : { Cookie: adminCookie };
  const r = await fetch(`${POCKETID_ISSUER}/api/oidc/clients/${id}`, {
    headers: authHeaders,
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
  apiKey: string = "",
): Promise<UserSummary[]> {
  const authHeaders: Record<string, string> = apiKey
    ? { "X-API-Key": apiKey }
    : { Cookie: adminCookie };
  const r = await fetch(`${POCKETID_ISSUER}/api/users`, {
    headers: authHeaders,
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
export const pocketIdDisableSignup = (adminCookie: string, apiKey: string = "") =>
  pocketIdSetSignupEnabled(adminCookie, false, apiKey);

/**
 * Enable signup (for the bootstrap workflow).
 */
export const pocketIdEnableSignup = (adminCookie: string, apiKey: string = "") =>
  pocketIdSetSignupEnabled(adminCookie, true, apiKey);

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
  const r = await fetch(`${POCKETID_ISSUER}/api/admin/jwt/rotate`, {
    method: "POST",
    headers: { Cookie: adminCookie },
  });
  if (!r.ok) {
    throw new Error(`pocketid rotate jwt failed: ${r.status} ${await r.text()}`);
  }
  const data = await r.json() as { newKeyId: string };
  return data;
}
