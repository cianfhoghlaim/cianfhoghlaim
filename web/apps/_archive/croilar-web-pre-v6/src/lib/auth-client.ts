/**
 * croilar-web auth client — re-export from the canonical
 * `@cianfhoghlaim/auth` package (which wraps the BetterAuth ^1.7
 * client with the 6 plugins: organization + 2FA + passkey + SIWE +
 * multi-session + OIDC client).
 *
 * Per the **2026-08-24-wave-6-frontend-tanstack-modernisation-v1** openspec
 * change (Wave 6.6). The original stub had loose `Record<string,
 * unknown>` signatures that broke the admin layout + login page
 * (`signIn.email`, `signIn.oauth2`, `useSession`, `signOut`).
 *
 * Server-side `auth.handler` is exported from `./auth`.
 *
 * Reference:
 *   - canonical client: `web/packages/auth/src/index.ts`
 *   - canonical server: `web/hono-api/src/auth.ts`
 */

export {
  authClient,
  useSession,
  signIn,
  signOut,
  signUp,
  useListOrganizations,
  useActiveOrganization,
  twoFactor,
  passkey,
  siwe,
  multiSession,
  ORG_SLUGS,
  type OrgSlug,
  type BetterAuthClient,
} from "@cianfhoghlaim/auth";
