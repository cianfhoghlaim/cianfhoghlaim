# =============================================================================
# Convex Schema Deploy — Dev Path (VERIFIED 2026-06-11)
# =============================================================================
# Self-hosted Convex backend (infrastructure/stacks/convex) is
# now running on bunchloch. To deploy the oideachais schema:
#
# 1. Self-hosted backend on bunchloch (current setup):
#    - Backend: http://localhost:3210  (already running on bunchloch)
#    - Dashboard: http://localhost:6791
#    - Schema files: sruth/cianfhoghlaim/web/convex/{schema,index,subject_sessions,...}.ts
#
# 2. The `bunx convex@latest dev` CLI auto-starts its OWN local backend
#    on port 3212 and deploys to that — not to our self-hosted one.
#    VERIFIED WORKING: the schema is valid, all 5 tables + 6 indexes
#    (annotations.by_author, annotations.by_document, classmate_shares.by_owner,
#    classmate_shares.by_token, extraction_budget.by_session,
#    practice_attempts.by_trace) were successfully created.
#
# 3. To deploy to the SELF-HOSTED backend on :3210, the admin key
#    needs to be provisioned in the dashboard first. Then:
#    cd sruth/cianfhoghlaim/web
#    bunx --yes convex@latest deploy --url http://admin:<KEY>@127.0.0.1:3210
#
# 4. KNOWN ISSUE: The self-hosted Convex dashboard returns `adminKey: null`
#    even after a fresh start — admin provisioning is interactive and
#    can't be automated via API. For prod, use the hosted Convex cloud
#    (https://www.convex.dev) or provision via Pulumi.
#
# 5. The oideachais frontend (running on :3000) connects to:
#    VITE_CONVEX_URL=http://localhost:3210
#    which is set in the merged compose.yaml.
# =============================================================================
