# Tasks — Team Workflow Stack

- [x] 1. Create `infrastructure/stacks/engineering/n8n/{compose,sidecar,secrets.env,pangolin,blueprint}.yaml` + `.env.example` (n8n + postgres:16-alpine + redis:7-alpine + locket)
- [x] 2. Create `infrastructure/stacks/tools/vikunja/{compose,sidecar,secrets.env,pangolin,blueprint}.yaml` + `.env.example` (vikunja + postgres:16-alpine + locket)
- [x] 3. Create `infrastructure/stacks/tools/cal-diy/{compose,sidecar,secrets.env,pangolin,blueprint}.yaml` + `.env.example` (calcom-web built from `stedding/repos/cal.diy/` + postgres:16-alpine + redis:7-alpine + locket)
- [x] 4. Add 6 workflow JSONs to `infrastructure/stacks/engineering/n8n/workflows/team-*.json` (daily-briefing, email-triage, booking-to-vikunja, followup-drafter, weekly-summary, stale-task-nudger)
- [x] 5. Write `n8n-init` and `vikunja-seed` one-shot containers (`init/seed.ts` + `init/Dockerfile` for each)
- [x] 6. Add 5 `team-*.toml` Komodo procedures (`team-stack-up`, `team-stack-down`, `team-stack-health`, `team-workflow-reload`, `team-backup`)
- [x] 7. Append 22 new `infisical://dev-baile/...` lines to root `.infisical.env`
- [x] 8. Create 19 new Infisical items in `dev-baile` via REST API (n8n/*, vikunja/*, calcom/*, team-mailbox/*)
- [x] 9. Validate `docker compose -f compose.yaml --env-file .env.example config --quiet` on all 3 stacks (all pass with exit 0)
- [x] 10. Write `openspec/changes/team-workflow-stack/{proposal.md, tasks.md}` and 3 capability specs (`task-management`, `scheduling`, `workflow-automation`)
- [x] 11. `openspec validate team-workflow-stack --strict`
- [x] 12. Update `infrastructure/README.md`, `AGENTS.md`, root `README.md` (generic team copy only — no political framing)
- [x] 13. Git commit + push (Landing the Plane)
