# Tasks: 2026-07-28-openchamber-bunchloch-dev-parity-v1

## 1. Confirm prerequisites and scope

- [ ] 1.1 Confirm both hard dependencies have archived before deployment:
      `2026-07-24-deploy-openclaw-hermes-bunchloch-local-infisical-fallback-v1`
      and `2026-07-24-full-local-agent-platform-stack-up-v1`.
- [ ] 1.2 Confirm the target host is `bunchloch` and the host OpenCode version
      is exactly `1.17.9` (`opencode --version`).
- [ ] 1.3 Confirm the host repository exists at the canonical absolute path:
      `/Users/cianmacandeisigh/dev/kings_college_galway`.
- [ ] 1.4 Confirm no arm1-oci deployment or public listener is included in the
      Bunchloch development implementation.

## 2. Build/pin the OpenChamber runtime

- [ ] 2.1 Pin the OpenChamber image/build to `1.16.3`; do not use `latest` or
      an unversioned image reference.
- [ ] 2.2 Ensure the runtime image contains the `git` executable and verify
      `git --version` from inside the running container.
- [ ] 2.3 Keep the application work directory available at
      `/home/bun/.openchamber`; no persistent volume may mount over that path.
- [ ] 2.4 Persist OpenChamber configuration/state in a dedicated XDG config
      volume mounted at `/home/bun/.config/openchamber` (or an equivalent
      subdirectory that leaves application files visible).

## 3. Configure external OpenCode mode

- [ ] 3.1 Set the external-server contract explicitly with
      `OPENCODE_HOST=http://host.docker.internal:4096`,
      `OPENCODE_PORT=4096`, and `OPENCODE_SKIP_START=true`.
- [ ] 3.2 Confirm the OpenChamber startup command does not launch a bundled
      OpenCode process and does not silently fall back to bundled mode.
- [ ] 3.3 Make the host OpenCode service reachable from the container without
      changing ownership of its sessions or MCP configuration.
- [ ] 3.4 Mount the host repository read/write at the identical absolute path:
      `/Users/cianmacandeisigh/dev/kings_college_galway:/Users/cianmacandeisigh/dev/kings_college_galway`.
- [ ] 3.5 Confirm an OpenChamber session opened for that directory reports the
      same absolute project path and can inspect the host checkout.

## 4. Preserve host sessions and MCP configuration

- [ ] 4.1 Do not copy, regenerate, or shadow the host OpenCode session store
      or MCP configuration in the OpenChamber volume.
- [ ] 4.2 Start the host OpenCode 1.17.9 server with its existing session and
      MCP configuration intact.
- [ ] 4.3 Verify `curl -fsS http://127.0.0.1:4096/global/health` succeeds from
      the host and the equivalent `host.docker.internal:4096/global/health`
      check succeeds from the OpenChamber container.
- [ ] 4.4 Verify that at least one pre-existing host OpenCode session is
      discoverable through the OpenChamber UI/API and opens against the
      canonical repository path.
- [ ] 4.5 Verify the OpenCode enabled MCP list through the external server/API
      and record only MCP names/statuses (never credentials) in the deployment
      receipt or test output.

## 5. Inject secrets and constrain networking

- [ ] 5.1 Define all runtime secrets as Infisical references consumed by the
      Locket sidecar; no secret value may be placed in `compose.yaml`,
      `.env.example`, the Dockerfile, the image, or committed logs.
- [ ] 5.2 Confirm the OpenChamber service starts only after the Locket health
      check and reads the runtime-mounted secret file.
- [ ] 5.3 Confirm the Bunchloch UI publication binds to loopback only,
      `127.0.0.1:<dev-port>:<container-port>`, with no `0.0.0.0` host bind.
- [ ] 5.4 Confirm the host OpenCode dev port remains local to Bunchloch and is
      not added to Pangolin, a public resource, or a non-loopback publish.

## 6. Health and parity verification

- [ ] 6.1 Verify the OpenChamber container health endpoint is exactly
      `http://127.0.0.1:<dev-port>/health` and returns HTTP 200.
- [ ] 6.2 Verify the external OpenCode endpoint is exactly
      `http://127.0.0.1:4096/global/health` and returns HTTP 200.
- [ ] 6.3 Repeat the OpenCode health check from inside the OpenChamber
      container using `host.docker.internal` and require HTTP 200.
- [ ] 6.4 Verify the UI can list and reopen an existing host session, use the
      canonical repository path, and display the expected enabled MCP list.
- [ ] 6.5 Verify `docker inspect` shows the pinned `1.16.3` image, the
      identical-path repository mount, the non-shadowing config mount, the
      loopback-only port, and no plaintext secret environment values.

## 7. Documentation and final gates

- [ ] 7.1 Document the Bunchloch external-mode contract and the distinction
      between host-owned OpenCode state and OpenChamber-owned UI config.
- [ ] 7.2 Document rollback: stop/remove only the OpenChamber development
      container and config volume; leave host OpenCode sessions, MCP config,
      and the repository checkout untouched.
- [ ] 7.3 Run `openspec validate 2026-07-28-openchamber-bunchloch-dev-parity-v1 --strict`.
- [ ] 7.4 Do not implement stack files during this proposal-authoring change;
      implementation proceeds only after review and approval.
