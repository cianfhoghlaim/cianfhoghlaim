// bonneagar/iac/clients/infisical-rest.ts — Direct REST client for Infisical v0.161+
// Bypasses the buggy @infisical/sdk v5.0.2. Uses form-encoded body for login
// (NOT JSON — the server expects application/x-www-form-urlencoded for the
// /api/v1/auth/universal-auth/login endpoint).

import { fetch } from "undici";

// ---------------------------------------------------------------------------
// URL discovery (env → localhost dev fallback → public prod)
// ---------------------------------------------------------------------------

const PUBLIC_URL = "https://infisical.cianfhoghlaim.ie";
const DEV_URL = "http://localhost:8081";

/**
 * Returns the Infisical base URL to use. Order:
 *   1. INFISICAL_URL env var (operator override)
 *   2. http://localhost:8081 (dev — works on this Mac only)
 *   3. https://infisical.cianfhoghlaim.ie (prod)
 */
export function discoverInfisicalUrl(): string {
  return (
    process.env.INFISICAL_URL?.trim() ||
    (canReach(DEV_URL) ? DEV_URL : PUBLIC_URL)
  );
}

async function canReach(url: string): Promise<boolean> {
  try {
    const r = await fetch(`${url}/api/status`, {
      signal: AbortSignal.timeout(2000),
    });
    return r.ok;
  } catch {
    return false;
  }
}

// ---------------------------------------------------------------------------
// Auth (Universal Auth — form-encoded body, not JSON)
// ---------------------------------------------------------------------------

export interface InfisicalAuth {
  clientId: string;
  clientSecret: string;
}

export interface InfisicalToken {
  accessToken: string;
  expiresAt: number; // unix seconds
}

let _tokenCache: { url: string; auth: InfisicalAuth; token: InfisicalToken; fetchedAt: number } | null = null;
const TOKEN_TTL_SECONDS = 60 * 60; // 1 hour (Infisical's default access_token TTL)

/**
 * Login via Universal Auth. Uses form-encoded body (NOT JSON — that's the
 * bug in the @infisical/sdk v5.0.2 wrapper).
 *
 * Caches the token per (url + auth) pair so we don't login on every call.
 */
export async function infisicalLogin(
  baseUrl: string = discoverInfisicalUrl(),
  auth: InfisicalAuth = {
    clientId: process.env.INFISICAL_UNIVERSAL_AUTH_CLIENT_ID ?? "",
    clientSecret: process.env.INFISICAL_UNIVERSAL_AUTH_CLIENT_SECRET ?? "",
  },
): Promise<InfisicalToken> {
  if (!auth.clientId || !auth.clientSecret) {
    throw new Error(
      "infisicalLogin: INFISICAL_UNIVERSAL_AUTH_CLIENT_ID + INFISICAL_UNIVERSAL_AUTH_CLIENT_SECRET must be set in env",
    );
  }

  // Cache check
  const cached = _tokenCache;
  if (
    cached &&
    cached.url === baseUrl &&
    cached.auth.clientId === auth.clientId &&
    cached.auth.clientSecret === auth.clientSecret &&
    Date.now() / 1000 < cached.token.expiresAt - 60 // refresh 60s early
  ) {
    return cached.token;
  }

  const r = await fetch(`${baseUrl}/api/v1/auth/universal-auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      clientId: auth.clientId,
      clientSecret: auth.clientSecret,
    }).toString(),
  });
  if (!r.ok) {
    throw new Error(`infisical login failed: ${r.status} ${await r.text()}`);
  }
  const data = (await r.json()) as { accessToken: string; expiresIn: number };
  const token: InfisicalToken = {
    accessToken: data.accessToken,
    expiresAt: Math.floor(Date.now() / 1000) + (data.expiresIn ?? TOKEN_TTL_SECONDS),
  };
  _tokenCache = {
    url: baseUrl,
    auth,
    token,
    fetchedAt: Date.now(),
  };
  return token;
}

// ---------------------------------------------------------------------------
// Projects
// ---------------------------------------------------------------------------

export interface InfisicalProject {
  id: string;
  name: string;
  slug: string;
  description?: string;
}

export async function infisicalListProjects(
  baseUrl: string = discoverInfisicalUrl(),
): Promise<InfisicalProject[]> {
  const token = await infisicalLogin(baseUrl);
  const r = await fetch(`${baseUrl}/api/v3/projects`, {
    headers: { Authorization: `Bearer ${token.accessToken}` },
  });
  if (!r.ok) throw new Error(`infisical list projects failed: ${r.status} ${await r.text()}`);
  const data = (await r.json()) as { projects: Array<{ id: string; name: string; slug: string; description?: string }> };
  return data.projects;
}

export async function infisicalGetProject(
  projectId: string,
  baseUrl: string = discoverInfisicalUrl(),
): Promise<InfisicalProject> {
  const token = await infisicalLogin(baseUrl);
  const r = await fetch(`${baseUrl}/api/v3/projects/${projectId}`, {
    headers: { Authorization: `Bearer ${token.accessToken}` },
  });
  if (!r.ok) throw new Error(`infisical get project failed: ${r.status} ${await r.text()}`);
  const data = (await r.json()) as { project: InfisicalProject };
  return data.project;
}

// ---------------------------------------------------------------------------
// Secrets
// ---------------------------------------------------------------------------

export interface InfisicalSecret {
  id?: string;
  key: string;
  value: string;
  path: string;
  environment: string;
  projectId: string;
  type?: "shared" | "personal";
}

export async function infisicalGetSecret(
  opts: {
    secretName: string;
    projectId: string;
    environment: string;
    secretPath?: string;
  },
  baseUrl: string = discoverInfisicalUrl(),
): Promise<InfisicalSecret | null> {
  const token = await infisicalLogin(baseUrl);
  const path = opts.secretPath ?? "/";
  const url = `${baseUrl}/api/v3/secrets/raw/${encodeURIComponent(opts.secretName)}?workspaceId=${opts.projectId}&environment=${opts.environment}&secretPath=${encodeURIComponent(path)}`;
  const r = await fetch(url, {
    headers: { Authorization: `Bearer ${token.accessToken}` },
  });
  if (r.status === 404) return null;
  if (!r.ok) throw new Error(`infisical get secret failed: ${r.status} ${await r.text()}`);
  const data = (await r.json()) as { secret: { _id: string; key: string; value: string; secretPath?: string; type?: string } };
  return {
    id: data.secret._id,
    key: data.secret.key,
    value: data.secret.value,
    path: data.secret.secretPath ?? path,
    environment: opts.environment,
    projectId: opts.projectId,
    type: data.secret.type === "personal" ? "personal" : "shared",
  };
}

export async function infisicalCreateSecret(
  opts: InfisicalSecret,
  baseUrl: string = discoverInfisicalUrl(),
): Promise<InfisicalSecret> {
  const token = await infisicalLogin(baseUrl);
  const r = await fetch(`${baseUrl}/api/v3/secrets/${encodeURIComponent(opts.projectId)}`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token.accessToken}`, "Content-Type": "application/json" },
    body: JSON.stringify({
      secretName: opts.key,
      secretValue: opts.value,
      secretPath: opts.path ?? "/",
      environment: opts.environment,
      type: opts.type ?? "shared",
    }),
  });
  if (!r.ok) throw new Error(`infisical create secret failed: ${r.status} ${await r.text()}`);
  const data = (await r.json()) as { secret: InfisicalSecret };
  return data.secret;
}

export async function infisicalUpdateSecret(
  opts: InfisicalSecret,
  baseUrl: string = discoverInfisicalUrl(),
): Promise<InfisicalSecret> {
  const token = await infisicalLogin(baseUrl);
  const r = await fetch(`${baseUrl}/api/v3/secrets/${encodeURIComponent(opts.projectId)}`, {
    method: "PATCH",
    headers: { Authorization: `Bearer ${token.accessToken}`, "Content-Type": "application/json" },
    body: JSON.stringify({
      secretName: opts.key,
      secretValue: opts.value,
      secretPath: opts.path ?? "/",
      environment: opts.environment,
    }),
  });
  if (!r.ok) throw new Error(`infisical update secret failed: ${r.status} ${await r.text()}`);
  const data = (await r.json()) as { secret: InfisicalSecret };
  return data.secret;
}

export async function infisicalDeleteSecret(
  opts: { secretName: string; projectId: string; environment: string; secretPath?: string },
  baseUrl: string = discoverInfisicalUrl(),
): Promise<void> {
  const token = await infisicalLogin(baseUrl);
  const path = opts.secretPath ?? "/";
  const r = await fetch(
    `${baseUrl}/api/v3/secrets/${encodeURIComponent(opts.secretName)}?workspaceId=${opts.projectId}&environment=${opts.environment}&secretPath=${encodeURIComponent(path)}`,
    { method: "DELETE", headers: { Authorization: `Bearer ${token.accessToken}` } },
  );
  if (!r.ok && r.status !== 404) {
    throw new Error(`infisical delete secret failed: ${r.status} ${await r.text()}`);
  }
}

export async function infisicalListSecrets(
  opts: { projectId: string; environment: string; secretPath?: string },
  baseUrl: string = discoverInfisicalUrl(),
): Promise<InfisicalSecret[]> {
  const token = await infisicalLogin(baseUrl);
  const path = opts.secretPath ?? "/";
  const r = await fetch(
    `${baseUrl}/api/v3/secrets?workspaceId=${opts.projectId}&environment=${opts.environment}&secretPath=${encodeURIComponent(path)}`,
    { headers: { Authorization: `Bearer ${token.accessToken}` } },
  );
  if (!r.ok) throw new Error(`infisical list secrets failed: ${r.status} ${await r.text()}`);
  const data = (await r.json()) as { secrets: Array<{ _id: string; key: string; secretValue?: string; secretPath?: string }> };
  return data.secrets.map((s) => ({
    id: s._id,
    key: s.key,
    value: s.secretValue ?? "",
    path: s.secretPath ?? path,
    environment: opts.environment,
    projectId: opts.projectId,
  }));
}

// ---------------------------------------------------------------------------
// Machine identities
// ---------------------------------------------------------------------------

export interface InfisicalMachineIdentity {
  id: string;
  name: string;
  projectId: string;
  clientId?: string;
  clientSecret?: string;
}

export async function infisicalListMachineIdentities(
  projectId: string,
  baseUrl: string = discoverInfisicalUrl(),
): Promise<InfisicalMachineIdentity[]> {
  const token = await infisicalLogin(baseUrl);
  const r = await fetch(`${baseUrl}/api/v1/auth/machine-identities?projectId=${projectId}`, {
    headers: { Authorization: `Bearer ${token.accessToken}` },
  });
  if (!r.ok) throw new Error(`infisical list identities failed: ${r.status} ${await r.text()}`);
  const data = (await r.json()) as { identities: Array<{ id: string; name: string }> };
  return data.identities.map((i) => ({ id: i.id, name: i.name, projectId }));
}

export async function infisicalCreateMachineIdentity(
  opts: { name: string; projectId: string },
  baseUrl: string = discoverInfisicalUrl(),
): Promise<InfisicalMachineIdentity> {
  const token = await infisicalLogin(baseUrl);
  const r = await fetch(`${baseUrl}/api/v1/auth/machine-identities`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token.accessToken}`, "Content-Type": "application/json" },
    body: JSON.stringify({ name: opts.name, projectId: opts.projectId }),
  });
  if (!r.ok) throw new Error(`infisical create identity failed: ${r.status} ${await r.text()}`);
  const data = (await r.json()) as { identity: { id: string; name: string; clientId: string; clientSecret: string } };
  return {
    id: data.identity.id,
    name: data.identity.name,
    projectId: opts.projectId,
    clientId: data.identity.clientId,
    clientSecret: data.identity.clientSecret,
  };
}

/**
 * Mint a Universal Auth client secret for a machine identity. This is the
 * separate endpoint (mirrors the Pocket ID v2.9.0 pattern where the secret
 * is fetched via a separate POST /api/oidc/clients/:id/secret call).
 */
export async function infisicalCreateMachineIdentitySecret(
  identityId: string,
  baseUrl: string = discoverInfisicalUrl(),
): Promise<{ clientId: string; clientSecret: string }> {
  const token = await infisicalLogin(baseUrl);
  const r = await fetch(`${baseUrl}/api/v1/auth/machine-identities/${identityId}/client-secrets`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token.accessToken}`, "Content-Type": "application/json" },
    body: JSON.stringify({}),
  });
  if (!r.ok) throw new Error(`infisical mint identity secret failed: ${r.status} ${await r.text()}`);
  const data = (await r.json()) as { clientSecret: string; clientId: string };
  return { clientId: data.clientId, clientSecret: data.clientSecret };
}

// ---------------------------------------------------------------------------
// Health
// ---------------------------------------------------------------------------

export async function infisicalHealth(baseUrl: string = discoverInfisicalUrl()): Promise<{
  healthy: boolean;
  detail: string;
  version?: string;
}> {
  try {
    const r = await fetch(`${baseUrl}/api/status`, {
      signal: AbortSignal.timeout(5000),
    });
    if (!r.ok) return { healthy: false, detail: `infisical /api/status returned ${r.status}` };
    const data = (await r.json()) as { message?: string; version?: string };
    return { healthy: true, detail: `infisical ${data.message ?? "ok"}`, version: data.version };
  } catch (e) {
    return { healthy: false, detail: (e as Error).message };
  }
}

// ---------------------------------------------------------------------------
// User count (for the iac:bootstrap flow — detect first-admin-vs-existing)
// ---------------------------------------------------------------------------

export async function infisicalGetUserCount(
  baseUrl: string = discoverInfisicalUrl(),
): Promise<number> {
  const token = await infisicalLogin(baseUrl);
  const r = await fetch(`${baseUrl}/api/v3/admin/users`, {
    headers: { Authorization: `Bearer ${token.accessToken}` },
  });
  if (!r.ok) {
    // /api/v3/admin/users may not be accessible to machine identities.
    // Fallback: list organizations + projects as a proxy for "is there data?".
    try {
      const projects = await infisicalListProjects(baseUrl);
      // Crude heuristic: an empty vault has 0 projects
      return projects.length > 0 ? 1 : 0;
    } catch {
      return -1; // unknown
    }
  }
  const data = (await r.json()) as { users: unknown[] };
  return data.users?.length ?? 0;
}
