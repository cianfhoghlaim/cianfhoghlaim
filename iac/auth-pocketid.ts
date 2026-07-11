// bonneagar/iac/auth-pocketid.ts — Pocket ID OIDC client_credentials flow
//
// Implements the 3-step auth rotation documented in
// openspec/changes/2026-07-14-repair-bonneagar-iac-3-way-auth-v1:
//
//   Step 1: Mint a Pocket ID access_token via client_credentials grant
//           POST https://auth.cianfhoghlaim.ie/api/oidc/token
//           grant_type=client_credentials
//           client_id=POCKETID_CLIENT_ID
//           client_secret=POCKETID_CLIENT_SECRET
//           → { access_token, token_type, expires_in }
//
//   Step 2: Exchange the Pocket ID JWT for a Pangolin session cookie
//           POST https://pangolin.cianfhoghlaim.ie/api/v1/auth/login
//           Authorization: Bearer <pocket_id_jwt>
//           → Set-Cookie: session=...
//
//   Step 3: Use the session cookie to mint a fresh Pangolin API key
//           PUT /v1/org/{orgId}/api-key
//           Cookie: session=...
//           → { apiKey, apiKeyId, lastChars, name, createdAt }
//
// The 3 env vars required (POCKETID_CLIENT_ID + POCKETID_CLIENT_SECRET
// + PANGOLIN_ORG_ID) are loaded from process.env. The POCKETID_*
// credentials come from Infisical at /pangolin/ (see PANGOLIN-SETUP.md
// Manual Step 1).
//
// Spec: openspec/changes/2026-07-14-repair-bonneagar-iac-3-way-auth-v1
// =============================================================================

const POCKETID_ISSUER = process.env.POCKETID_URL ?? "https://auth.cianfhoghlaim.ie";
const PANGOLIN_URL = process.env.PANGOLIN_URL ?? "https://pangolin.cianfhoghlaim.ie";
const PANGOLIN_ORG_ID = process.env.PANGOLIN_ORG_ID ?? "cianfhoghlaim";
const POCKETID_CLIENT_ID = process.env.POCKETID_CLIENT_ID;
const POCKETID_CLIENT_SECRET = process.env.POCKETID_CLIENT_SECRET;

interface PocketIdTokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  scope?: string;
}

interface PocketIdDiscovery {
  issuer: string;
  token_endpoint: string;
  introspection_endpoint?: string;
  userinfo_endpoint?: string;
  grant_types_supported: string[];
  token_endpoint_auth_methods_supported: string[];
}

export interface PocketIdLoginResult {
  accessToken: string;
  expiresIn: number;
}

/**
 * Discovers Pocket ID's OIDC endpoints via .well-known/openid-configuration.
 * Cached per-process so we don't hit the discovery endpoint on every call.
 */
let _discoveryCache: PocketIdDiscovery | null = null;
export async function discoverPocketId(): Promise<PocketIdDiscovery> {
  if (_discoveryCache) return _discoveryCache;
  const r = await fetch(`${POCKETID_ISSUER}/.well-known/openid-configuration`);
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
 * Mints a Pocket ID access_token via the client_credentials grant.
 * Returns the access_token + expires_in seconds.
 *
 * Requires POCKETID_CLIENT_ID + POCKETID_CLIENT_SECRET in env (or in the
 * caller-supplied `creds` arg for testability).
 */
export async function pocketIdClientCredentials(
  creds: { clientId: string; clientSecret: string } = {
    clientId: POCKETID_CLIENT_ID ?? "",
    clientSecret: POCKETID_CLIENT_SECRET ?? "",
  },
): Promise<PocketIdLoginResult> {
  if (!creds.clientId || !creds.clientSecret) {
    throw new Error(
      "POCKETID_CLIENT_ID and POCKETID_CLIENT_SECRET must be set in env. " +
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
 * Exchanges a Pocket ID access_token for a Pangolin session cookie.
 *
 * NOTE: This is the trickiest part of the flow. The exact endpoint
 * + request format depends on how Pangolin is configured to trust
 * Pocket ID. Two patterns that have been observed in production:
 *
 *   Pattern A (older Pangolin builds): POST /api/v1/auth/login
 *     body: { accessToken: <jwt> } OR { username/password } OR { idpToken: <jwt> }
 *     → Set-Cookie: session=...
 *
 *   Pattern B (newer Pangolin builds with OIDC direct): POST /v1/auth/oidc/callback
 *     body: { code: <auth_code>, state: <csrf> } (after a redirect flow)
 *     → not usable for client_credentials (no user, no redirect)
 *
 * We try Pattern A with both `accessToken` and `idpToken` field names
 * for backwards compatibility. If neither works, the caller gets a
 * clear error message.
 */
export async function exchangePocketIdForPangolinSession(
  pocketIdJwt: string,
): Promise<string> {
  // Try the modern endpoint first
  const endpoints = [
    { path: "/api/v1/auth/login", body: { accessToken: pocketIdJwt } },
    { path: "/api/v1/auth/login", body: { idpToken: pocketIdJwt } },
    { path: "/v1/auth/login", body: { accessToken: pocketIdJwt } },
    { path: "/v1/auth/login", body: { idpToken: pocketIdJwt } },
  ];

  for (const ep of endpoints) {
    const r = await fetch(`${PANGOLIN_URL}${ep.path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(ep.body),
    });
    if (r.ok) {
      const setCookie = r.headers.get("set-cookie");
      if (setCookie) {
        // Extract the session cookie (just the name=value pair, not the path/expires/...)
        const sessionMatch = setCookie.match(/session=([^;]+)/);
        if (sessionMatch) return `session=${sessionMatch[1]}`;
      }
      // Some Pangolin builds return the session token in the response body
      const data = (await r.json()) as { session?: string; token?: string; data?: { session?: string; token?: string } };
      const sessionToken = data.session ?? data.token ?? data.data?.session ?? data.data?.token;
      if (sessionToken) return `session=${sessionToken}`;
    }
  }

  throw new Error(
    `pangolin session exchange failed: tried ${endpoints.length} endpoint variants, none returned a session cookie.\n` +
      `  (the operator must verify that Pocket ID is configured as a trusted ` +
      `OIDC identity provider in the Pangolin dashboard at ` +
      `https://pangolin.cianfhoghlaim.ie/admin → Settings → Identity Providers)`,
  );
}

/**
 * Mints a fresh Pangolin API key using the session cookie.
 * Returns the raw API key value (NOT just the apiKeyId).
 */
export async function mintPangolinApiKey(
  sessionCookie: string,
  name: string = `bons-iac-${new Date().toISOString().slice(0, 10)}`,
): Promise<{ apiKey: string; apiKeyId: string; name: string }> {
  const r = await fetch(`${PANGOLIN_URL}/v1/org/${PANGOLIN_ORG_ID}/api-key`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      Cookie: sessionCookie,
    },
    body: JSON.stringify({ name }),
  });
  if (!r.ok) {
    throw new Error(`pangolin api-key mint failed: ${r.status} ${await r.text()}`);
  }
  const data = (await r.json()) as {
    data?: { apiKey?: string; apiKeyId?: string; name?: string };
    apiKey?: string;
    apiKeyId?: string;
    name?: string;
  };
  const apiKey = data.data?.apiKey ?? data.apiKey;
  const apiKeyId = data.data?.apiKeyId ?? data.apiKeyId;
  if (!apiKey || !apiKeyId) {
    throw new Error(
      `pangolin api-key mint returned 200 but no apiKey in response: ${JSON.stringify(data)}`,
    );
  }
  return { apiKey, apiKeyId, name: data.data?.name ?? data.name ?? name };
}

/**
 * The full 3-step flow: Pocket ID client_credentials → Pangolin session → API key.
 * This is the function that `ensurePangolinAuth()` will call when the
 * PANGOLIN_API_KEY env var is missing/expired.
 */
export async function pocketIdLogin(): Promise<string> {
  logStep("pocketIdLogin (3-step): mint Pangolin API key via Pocket ID OIDC");

  // Step 1: Pocket ID client_credentials grant
  const { accessToken } = await pocketIdClientCredentials();
  logOk(`Step 1: Pocket ID access_token minted (expires_in=${"expiresIn" in ({} as { expiresIn?: unknown }) ? "?" : "?"})`);

  // Step 2: Exchange Pocket ID JWT for Pangolin session
  const sessionCookie = await exchangePocketIdForPangolinSession(accessToken);
  logOk(`Step 2: Pangolin session cookie obtained`);

  // Step 3: Mint a fresh Pangolin API key
  const { apiKey, apiKeyId } = await mintPangolinApiKey(sessionCookie);
  logOk(`Step 3: Pangolin API key minted (id=${apiKeyId})`);

  return apiKey;
}

// Lightweight logger helpers (so this file doesn't import cli.ts and
// create a circular dep). The caller can pipe to the same `log` functions
// by wrapping if needed.
function logStep(msg: string) { console.log(`\n→ ${msg}`); }
function logOk(msg: string) { console.log(`  ✓ ${msg}`); }
