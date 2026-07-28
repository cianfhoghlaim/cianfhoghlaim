// bonneagar/iac/auth-pocketid.ts — Pocket ID OIDC client_credentials flow + Pangolin session exchange
//
// v2.9.0+ behavior: Pocket ID rotates the OIDC client_secret on EVERY call
// to POST /api/oidc/clients/{id}/secret. This means we CANNOT persist the
// secret to .env between calls — it would be stale within seconds.
//
// The correct flow:
//   1. Fetch a FRESH secret from Pocket ID admin API (X-API-Key auth)
//   2. IMMEDIATELY use that secret in the client_credentials grant
//   3. If you need to persist a key, persist the PANGOLIN_API_KEY (not the
//      pocket ID secret) — the API key has a longer TTL (configurable at mint time)
//
// Step 1: Pocket ID client_credentials grant
//   POST https://auth.cianfhoghlaim.ie/api/oidc/token
//   grant_type=client_credentials
//   client_id=POCKETID_PANGOLIN_CLIENT_ID
//   client_secret=<FRESHLY FETCHED from /api/oidc/clients/{id}/secret>
//   → { access_token, token_type, expires_in }
//
// Step 2: Exchange the Pocket ID JWT for a Pangolin session cookie
//   POST https://pangolin.cianfhoghlaim.ie/api/v1/auth/login
//   Authorization: Bearer <pocket_id_jwt>
//   → Set-Cookie: session=...
//
// Step 3: Use the session cookie to mint a fresh Pangolin API key
//   PUT /v1/org/{orgId}/api-key
//   Cookie: session=...
//   → { apiKey, apiKeyId, lastChars, name, createdAt }
//
// The 3 env vars required (POCKETID_PANGOLIN_CLIENT_ID + POCKETID_PANGOLIN_CLIENT_SECRET
// + PANGOLIN_ORG_ID) are loaded from process.env. The POCKETID_PANGOLIN_*
// credentials come from the .env at /Users/cianmacadeisigh/dev/kings_college_galway/.env
// (created by `bun run iac:bootstrap-pocketid-admin`).
//
// Spec: openspec/changes/2026-07-14-repair-bonneagar-iac-3-way-auth-v1
// =============================================================================

const POCKETID_ISSUER = process.env.POCKETID_URL ?? "https://auth.cianfhoghlaim.ie";
const PANGOLIN_URL = process.env.PANGOLIN_URL ?? "https://pangolin.cianfhoghlaim.ie";
const PANGOLIN_ORG_ID = process.env.PANGOLIN_ORG_ID ?? "cianfhoghlaim";
// v2.9.0+: the Pangolin OIDC client in Pocket ID is named "pangolin"
// (not the generic "bons-iac" or unprefixed POCKETID_PANGOLIN_CLIENT_ID).
const POCKETID_PANGOLIN_CLIENT_ID = process.env.POCKETID_PANGOLIN_CLIENT_ID;
const POCKETID_PANGOLIN_CLIENT_SECRET = process.env.POCKETID_PANGOLIN_CLIENT_SECRET;

interface PocketIdTokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  scope?: string;
}

interface PocketIdDiscovery {
  issuer: string;
  authorization_endpoint: string;
  token_endpoint: string;
  userinfo_endpoint: string;
  jwks_uri: string;
  grant_types_supported: string[];
  response_types_supported: string[];
  scopes_supported: string[];
}

interface PocketIdLoginResult {
  accessToken: string;
  expiresIn: number;
}

interface PocketIdAdminKey {
  apiKey: string;
  apiKeyId: string;
  lastChars: string;
  name: string;
  createdAt: string;
}

let _discoveryCache: PocketIdDiscovery | null = null;

async function discoverPocketId(): Promise<PocketIdDiscovery> {
  if (_discoveryCache) return _discoveryCache;
  const wellKnown = `${POCKETID_ISSUER.replace(/\/$/, "")}/.well-known/openid-configuration`;
  const r = await fetch(wellKnown);
  if (!r.ok) {
    throw new Error(`pocketid discovery failed: ${r.status} ${await r.text()}`);
  }
  const d = (await r.json()) as PocketIdDiscovery;
  if (!d.grant_types_supported.includes("client_credentials")) {
    throw new Error(
      `pocketid ${POCKETID_ISSUER} does not support client_credentials grant. ` +
        `supported: ${d.grant_types_supported.join(", ")}`,
    );
  }
  _discoveryCache = d;
  return d;
}

/**
 * Mint a FRESH Pocket ID client_secret via the admin API (X-API-Key auth).
 * Returns the secret string. Caller MUST use it immediately — Pocket ID
 * invalidates the previous secret on every call to /secret.
 *
 * Uses POCKETID_PANGOLIN_CLIENT_ID + POCKETID_API_KEY from env.
 */
export async function pocketIdFreshPangolinSecret(
  apiKey: string = process.env.POCKETID_API_KEY ?? "",
  clientId: string = POCKETID_PANGOLIN_CLIENT_ID ?? "",
): Promise<string> {
  if (!apiKey) {
    throw new Error("POCKETID_API_KEY must be set to mint a fresh Pangolin secret");
  }
  if (!clientId) {
    throw new Error(
      "POCKETID_PANGOLIN_CLIENT_ID must be set. " +
        "See PANGOLIN-SETUP.md Manual Step 1 to mint it via " +
        "https://auth.cianfhoghlaim.ie → Settings → OIDC Clients → Create.",
    );
  }
  const url = `${POCKETID_ISSUER.replace(/\/$/, "")}/api/oidc/clients/${clientId}/secret`;
  const r = await fetch(url, {
    method: "POST",
    headers: { "X-API-Key": apiKey, "Content-Type": "application/json" },
  });
  if (!r.ok) {
    const text = await r.text();
    throw new Error(`pocketid client-secret fetch failed: ${r.status} ${text}`);
  }
  const data = (await r.json()) as { secret?: string };
  if (!data.secret) {
    throw new Error("pocketid client-secret response missing 'secret' field");
  }
  return data.secret;
}

/**
 * Mints a Pocket ID access_token via the client_credentials grant.
 * Takes the secret as an arg (so the caller can pass a freshly-fetched
 * secret without persisting it). Falls back to POCKETID_PANGOLIN_CLIENT_SECRET
 * in env if no secret is supplied (for back-compat).
 */
export async function pocketIdClientCredentials(
  creds: { clientId: string; clientSecret: string } = {
    clientId: POCKETID_PANGOLIN_CLIENT_ID ?? "",
    clientSecret: POCKETID_PANGOLIN_CLIENT_SECRET ?? "",
  },
): Promise<PocketIdLoginResult> {
  if (!creds.clientId || !creds.clientSecret) {
    throw new Error(
      "POCKETID_PANGOLIN_CLIENT_ID and POCKETID_PANGOLIN_CLIENT_SECRET must be set in env. " +
        "See PANGOLIN-SETUP.md Manual Step 1 to mint them via " +
        "https://auth.cianfhoghlaim.ie → Settings → OIDC Clients → Create.",
    );
  }

  const discovery = await discoverPocketId();

  // The SDK uses `client_secret_post` (passes client_id + client_secret in
  // the form body). That's the most portable across auth libraries.
  const body = new URLSearchParams({
    grant_type: "client_credentials",
    client_id: creds.clientId,
    client_secret: creds.clientSecret,
    scope: "openid profile email",
  });

  const r = await fetch(discovery.token_endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: body.toString(),
  });

  if (!r.ok) {
    const text = await r.text();
    throw new Error(
      `pocketid token endpoint failed: ${r.status} ${text}\n` +
        `  (likely causes: wrong client_id, wrong client_secret, or client_credentials grant not enabled)`,
    );
  }

  const token = (await r.json()) as PocketIdTokenResponse;
  return { accessToken: token.access_token, expiresIn: token.expires_in };
}

/**
 * Exchange a Pocket ID access_token for a Pangolin session cookie.
 * Uses POST /api/v1/auth/login with the Bearer token. The server sets a
 * session cookie (HttpOnly, Secure, SameSite=Lax).
 */
export async function exchangePocketIdForPangolinSession(
  accessToken: string,
): Promise<string> {
  const url = `${PANGOLIN_URL.replace(/\/$/, "")}/api/v1/auth/login`;
  const r = await fetch(url, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${accessToken}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({}),
    redirect: "manual",
  });
  if (r.status !== 200 && r.status !== 303) {
    const text = await r.text();
    throw new Error(
      `pangolin login (Pocket ID OIDC) failed: ${r.status} ${text}\n` +
        `  (likely causes: Pocket ID client not whitelisted, or session requires browser flow)`,
    );
  }
  const setCookie = r.headers.get("set-cookie");
  if (!setCookie) {
    throw new Error("pangolin login: response missing Set-Cookie header (browser flow required)");
  }
  const sessionMatch = setCookie.match(/session=([^;]+)/);
  if (!sessionMatch) {
    throw new Error("pangolin login: Set-Cookie has no session token");
  }
  return `session=${sessionMatch[1]}`;
}

/**
 * Mint a fresh Pangolin API key (using the session cookie from step 2).
 * The key is returned along with metadata (id, last chars, name, createdAt).
 */
export async function mintPangolinApiKey(
  sessionCookie: string,
  opts: { name?: string; expiresIn?: number } = {},
): Promise<PocketIdAdminKey> {
  const url = `${PANGOLIN_URL.replace(/\/$/, "")}/v1/org/${PANGOLIN_ORG_ID}/api-key`;
  const r = await fetch(url, {
    method: "PUT",
    headers: {
      Cookie: sessionCookie,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      name: opts.name ?? `bons-iac-${new Date().toISOString().slice(0, 19)}`,
      expiresIn: opts.expiresIn ?? 7 * 24 * 60 * 60, // 7 days default
    }),
  });
  if (!r.ok) {
    const text = await r.text();
    throw new Error(`pangolin api-key mint failed: ${r.status} ${text}`);
  }
  const data = (await r.json()) as { apiKey: string; apiKeyId: string; lastChars: string; name: string; createdAt: string };
  return data;
}

/**
 * COMPLETE Pocket ID OIDC → Pangolin session → Pangolin API key flow.
 *
 * IMPORTANT: Pocket ID rotates the OIDC client_secret on every call to
 * /api/oidc/clients/{id}/secret. This function fetches a FRESH secret
 * via the admin API (X-API-Key) and uses it IMMEDIATELY. The previous
 * secret is invalidated by the time this function returns.
 *
 * The returned apiKey is the ONLY stable thing — it has a configurable TTL
 * (default 7 days) and can be safely persisted to .env.
 */
export async function pocketIdLogin(
  opts: { name?: string; expiresIn?: number; apiKey?: string } = {},
): Promise<PocketIdAdminKey> {
  // Step 1a: Fetch a FRESH secret from Pocket ID admin API
  const freshSecret = await pocketIdFreshPangolinSecret(opts.apiKey);
  // Step 1b: Use the fresh secret immediately to get a Pocket ID access_token
  const { accessToken, expiresIn } = await pocketIdClientCredentials({
    clientId: POCKETID_PANGOLIN_CLIENT_ID ?? "",
    clientSecret: freshSecret,
  });
  // Step 2: Exchange the Pocket ID JWT for a Pangolin session cookie
  const sessionCookie = await exchangePocketIdForPangolinSession(accessToken);
  // Step 3: Mint a fresh Pangolin API key
  const apiKey = await mintPangolinApiKey(sessionCookie, opts);
  return apiKey;
}

// Lightweight logger helpers (so this file doesn't import cli.ts and
// create a circular dep). The caller can pipe to the same `log` functions
// by wrapping if needed.
function logStep(msg: string) { console.log(`\n→ ${msg}`); }
function logOk(msg: string) { console.log(`  ✓ ${msg}`); }
