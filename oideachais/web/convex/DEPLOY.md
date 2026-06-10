# =============================================================================
# Convex Schema Deploy — Dev Path
# =============================================================================
# Self-hosted Convex backend (infrastructure/stacks/engineering/convex) is
# now running on bunchloch. To deploy the oideachais schema:
#
# 1. Local backend (current setup):
#    - Backend: http://localhost:3210  (already running)
#    - Dashboard: http://localhost:6791
#
# 2. Provision admin:
#    - Open http://localhost:6791 in a browser
#    - The dashboard auto-generates an admin key on first visit
#    - OR call: curl -X POST http://localhost:3210/api/init \
#                 -H "Content-Type: application/json" \
#                 -d '{"instance_name":"convex"}'
#
# 3. Get the admin key + deploy URL:
#    - Once provisioned, the dashboard shows them on the home page
#    - Set in .env:
#        CONVEX_DEPLOY_KEY=admin:dev-secret-...
#        CONVEX_DEPLOY_URL=http://127.0.0.1:3210
#
# 4. Push the schema:
#    cd oideachais/web
#    bunx --yes convex@latest dev --once   # or: convex deploy
#
# 5. The oideachais frontend (running on :3000) connects to:
#    VITE_CONVEX_URL=http://localhost:3210
#    which is set in the merged compose.yaml.
#
# KNOWN ISSUE: Convex's local backend requires interactive dashboard
# provisioning which can't be automated in CI. For prod, use the hosted
# Convex cloud (https://www.convex.dev) or provision via Pulumi.
# See follow-up issue for automated provisioning.
# =============================================================================
