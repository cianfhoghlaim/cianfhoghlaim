# Tasks — audit-infrastructure-2026-06-15

- [ ] **Phase A** — Audit scripts (deferred-content scripts + README + .gitkeep)
  - [ ] `infrastructure/audit/scripts/inventory-bunchloch.sh`
  - [ ] `infrastructure/audit/scripts/inventory-arm1-oci.sh`
  - [ ] `infrastructure/audit/scripts/diff-against-composes.sh`
  - [ ] `infrastructure/audit/scripts/probe-public-urls.sh`
  - [ ] `infrastructure/audit/inventory/.gitkeep`
  - [ ] `infrastructure/audit/README.md`

- [ ] **Phase B** — Quadrant README updates
  - [ ] `oideachais/README.md` — Status + Known issues
  - [ ] `tuatha/README.md` — Status + Known issues
  - [ ] `croilar/README.md` — Status + Known issues
  - [ ] `meaisinfhoghlaim/README.md` — Status + Known issues
  - [ ] Root `README.md` — Status column on the Quadrant table

- [ ] **Phase C** — Infrastructure docs
  - [ ] NEW `infrastructure/DEPLOYMENT-STRATEGY.md`
  - [ ] UPDATE `infrastructure/GOLD_STANDARD.md` (stack-doctor CI gate)
  - [ ] MOVE `infrastructure/stacks/HEALTH_REPORT.md` historical log → `infrastructure/archive/HEALTH_REPORT-2026-06-12.md`
  - [ ] REWRITE `infrastructure/stacks/HEALTH_REPORT.md` (Session 4 entry)
  - [ ] NEW `infrastructure/QUADRANT-TO-STACK-MAP.md`
  - [ ] UPDATE `docs/06-infrastructure/` pointer

- [ ] **Phase D** — 9 deployment runbooks (deferred content for a future AI agent)
  - [ ] `infrastructure/deploy-runbooks/infisical.md`
  - [ ] `infrastructure/deploy-runbooks/komodo.md`
  - [ ] `infrastructure/deploy-runbooks/pangolin.md`
  - [ ] `infrastructure/deploy-runbooks/ansible.md`
  - [ ] `infrastructure/deploy-runbooks/cal-diy.md`
  - [ ] `infrastructure/deploy-runbooks/vikunja.md`
  - [ ] `infrastructure/deploy-runbooks/n8n.md`
  - [ ] `infrastructure/deploy-runbooks/changedetection.md`
  - [ ] `infrastructure/deploy-runbooks/bytebase.md`

- [ ] **Phase E** — OpenSpec archive
  - [ ] `openspec validate audit-infrastructure-2026-06-15 --strict` passes
  - [ ] `openspec archive audit-infrastructure-2026-06-15 --yes` succeeds
  - [ ] `infrastructure-stacks` spec has 2 new ADDED requirements
