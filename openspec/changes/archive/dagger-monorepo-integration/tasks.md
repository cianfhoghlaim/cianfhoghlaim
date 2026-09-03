# Tasks — Dagger Monorepo Integration

- [ ] 1. Create the `infrastructure/dagger/` module skeleton: `dagger.json`, `pyproject.toml`, `src/` package init.
- [ ] 2. Implement `src/shared/containers.py` with `python_container`, `bun_container`, `rust_container` (pinned sha256 base images, `Ignore` exclude list, cache volume mounting).
- [ ] 3. Implement `src/shared/caching.py` with `uv_cache`, `bun_cache`, `cargo_cache` `CacheVolume` helpers.
- [ ] 4. Implement `src/shared/secrets.py` with `InfisicalSecret`, `locket_secrets_env`, and the canonical INFRA/WEB/DATA secret registries.
- [ ] 5. Implement `src/shared/testing.py` with the 8 polyglot test/lint/typecheck runners.
- [ ] 6. Implement `src/infrastructure/__init__.py` (`InfrastructurePipeline`) with `test`, `build_api`, `deploy`, `rollback` (Pulumi → Locket → Komodo → Pangolin label verify).
- [ ] 7. Implement `src/web/__init__.py` (`WebPipeline`) with `test`, `build_ui`, `deploy`, `rollback` (`bunx turbo run build` → Cloudflare Pages → Komodo).
- [ ] 8. Implement `src/data/__init__.py` (`DataPipeline`) with `test`, `build_dagster`, `deploy`, `rollback` (Dagster materialise → Komodo → LiteLLM smoke test).
- [ ] 9. Implement `src/__init__.py` (`UnifiedPipeline` with `test_all`, `build_images`, `deploy`, `rollback`) using `asyncio.gather` to compose the 3 pipelines in parallel.
- [ ] 10. Copy the prior `stedding/dev/cianfhoghlaim copy/bonneagar/dagger/` TypeScript implementation into `infrastructure/dagger/ts_submodules/bonneagar/`. Add a local `README.md` explaining it is consumed as a TS submodule.
- [ ] 11. Create `infrastructure/dagger/templates/secrets.env.template` with `{{ infisical://dev-baile/... }}` refs.
- [ ] 12. Create `infrastructure/dagger/templates/sidecar.yaml.template` with the Locket sidecar snippet per `GOLD_STANDARD.md`.
- [ ] 13. Create `infrastructure/dagger/.forgejo/workflows/ci.yaml` (install Dagger + mise, run `dagger call test-all`).
- [ ] 14. Create `infrastructure/dagger/.forgejo/workflows/deploy.yaml` (gated staging + production deploy).
- [ ] 15. Create `infrastructure/dagger/README.md` documenting the 8 functions, the Locket secret model, the TS submodule integration, and the mise + Forgejo Actions integration.
- [ ] 16. Update the 4 broken `dagger:*` task aliases in `mise.toml` to point at the new `infrastructure/dagger/`. Add a `dagger:build-images` alias.
- [ ] 17. Update the 6 OpenSpec capability specs (`dagger-{ci,gitops,forgejo,komodo,cloudflare,blockchain}/spec.md`) to reference `infrastructure/dagger/src/*.py` (or `*.ts` for the submodule) instead of `bonneagar/dagger/src/*.ts`.
- [ ] 18. Update `openspec/project.md` to add the `dagger-monorepo-integration` capability to the table.
- [ ] 19. Run `dagger develop` from `infrastructure/dagger/` to validate the module + generate `client.gen.py`.
- [ ] 20. Run `dagger call test-all --source ../..` to smoke-test the unified test pipeline.
- [ ] 21. Run `openspec validate dagger-monorepo-integration --strict` (if openspec CLI is available; otherwise manual review of the 5 spec deltas).
- [ ] 22. Commit and push to `origin/main` per the Landing the Plane protocol in `AGENTS.md`.

## Defer (out of scope)

- `dagger-blockchain` SpacetimeDB + Solana + Ethereum CI (requires Rust toolchain in the Python root + GPU support) — filed as a followup OpenSpec change.
- Komodo SDK vs raw `curl` decision (verify whether `@komodo/sdk` is published on npm; fall back to `curl` if not).
- Multi-runner Dagger cache (S3/MinIO-backed) for Forgejo Actions.
- GPU support for Dagster AI / LiteLLM.
