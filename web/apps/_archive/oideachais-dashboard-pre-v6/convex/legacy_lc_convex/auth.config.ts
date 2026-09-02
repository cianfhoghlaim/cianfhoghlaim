/**
 * Convex auth.config.ts for the conic-leaving-cert deployment.
 *
 * Per openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/specs/
 * cianfhoghlaim-leaving-cert-portal/spec.md Requirement R6.
 *
 * The deployment is the fresh standalone `conic-leaving-cert` (NOT
 * cross-workspace with croilar-portal, per the user's explicit
 * decision). The Pocket ID OIDC discovery is the production SSO
 * identity provider.
 */

const domain = process.env.POCKET_ID_DOMAIN || "pocket-id.cianfhoghlaim.ie";
const applicationID = process.env.POCKET_ID_CLIENT_ID || "cianfhoghlaim-leaving-cert";

export default {
  providers: [
    {
      domain,
      applicationID,
    },
  ],
};