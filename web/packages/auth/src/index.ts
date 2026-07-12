// @croilar/auth — BetterAuth React client for the croilar platform.
//
// Wraps the hono-api's `auth.ts` configuration (BetterAuth + Drizzle +
// organization plugin) into a client-side React client that the 4 web
// apps (croilar-web, croilar-portal, tuatha-ui, oideachais-web) can
// import via `import { authClient } from "@croilar/auth"`.
//
// The 3 OIDC audiences are:
//   - convex_backend (Convex)
//   - croilar_web (croilar-web app)
//   - croilar_portal (croilar-portal app)
//
// Reference: web/hono-api/src/auth.ts for the server-side config.

import { createAuthClient } from "better-auth/react";
import { organizationClient } from "better-auth/client/plugins";

/** Resolve the auth API base URL.
 *  - In dev: PUBLIC_AUTH_URL is "http://localhost:4000"
 *  - In prod: PUBLIC_AUTH_URL is "https://auth.croilar.cianfhoghlaim.ie"
 *  - The 4 web apps read this from Vite/TanStack Start env at build time
 */
const baseURL =
  (typeof process !== "undefined" && process.env?.PUBLIC_AUTH_URL) ||
  (typeof import.meta !== "undefined" &&
    (import.meta as { env?: { PUBLIC_AUTH_URL?: string } }).env
      ?.PUBLIC_AUTH_URL) ||
  "http://localhost:4000";

/** The exported `authClient` instance.
 *  Use this in React components:
 *    const { data: session, isPending } = authClient.useSession();
 *    await authClient.signIn.email({ email, password });
 *    await authClient.signOut();
 *    await authClient.organization.list();
 */
export const authClient = createAuthClient({
  baseURL,
  plugins: [organizationClient()],
});

/** Re-export the typed hooks for ergonomic use. */
export const { useSession, signIn, signOut, signUp, useListOrganizations } =
  authClient;

/** The 4 canonical org slugs. */
export const ORG_SLUGS = {
  aleyum: "aleyum",
  cianfhoghlaim: "cianfhoghlaim",
  croilarAdmin: "croilar-admin",
  croilarCollab: "croilar-collab",
} as const;

export type OrgSlug = (typeof ORG_SLUGS)[keyof typeof ORG_SLUGS];
