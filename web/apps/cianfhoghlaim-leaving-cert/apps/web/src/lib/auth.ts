// apps/web/src/lib/auth.ts
// Better-auth v1.4 + Pocket ID OIDC for production auth.
// Per openspec/changes/cianfhoghlaim-website-rewrite/proposal.md R5.

import { createAuthClient } from "better-auth/react";

const AUTH_URL = import.meta.env?.VITE_AUTH_URL ?? "http://localhost:8787/api/auth";
const POCKET_ID_DISCOVERY = import.meta.env?.VITE_POCKET_ID_OIDC_DISCOVERY ?? "http://localhost:8080/.well-known/openid-configuration";

export const authClient = createAuthClient({
  baseURL: AUTH_URL,
  // The OIDC discovery is auto-detected by the better-auth pocket-id plugin
  // (configured on the server side in apps/api/src/index.ts).
});

export const { useSession, signIn, signOut, signUp } = authClient;