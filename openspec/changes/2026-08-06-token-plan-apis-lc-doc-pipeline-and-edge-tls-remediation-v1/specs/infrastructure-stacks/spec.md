## ADDED Requirements

### Requirement: Edge routing verification gate (check-edge-tls)

The platform SHALL verify that every hostname at the Pangolin edge is
correctly routed: genuinely public hostnames MUST serve a full-chain,
cryptographically verifiable certificate, and private hostnames (reached
only through the Pangolin client VPN) MUST resolve to an **online** site and
answer over the tunnel. The repository MUST ship `scripts/check-edge-tls.sh`,
which MUST:

- probe the genuinely public domains (`pangolin.cianfhoghlaim.ie`,
  `auth.cianfhoghlaim.ie`) for certificate validity, and — with `--all` —
  probe the private stack domains for tunnel reachability;
- **exclude the apex `cianfhoghlaim.ie`** from the public-certificate check:
  it is Cloudflare-proxied (resolves to `104.21.79.51`/`172.67.142.10`, not
  the Pangolin origin), so probing it verifies Cloudflare's certificate, not
  Traefik's, and is a permanent false green;
- report FAIL for any public domain whose OpenSSL `Verify return code` is
  not `0`, including the self-signed `CN=TRAEFIK DEFAULT CERT` failure mode
  (verify code 21/20, surfaced to Node/Bun clients as
  `unable to verify the first certificate`);
- report FAIL, distinctly from a certificate failure, for any private
  domain that returns no response (`HTTP 000`) while its DNS resolves into
  the tunnel subnet — this is the signature of a Pangolin private resource
  bound to an **offline** site, not a TLS problem;
- exit non-zero when invoked with `--strict` and any checked domain fails;
- correctly detect DNS failure (the `dig +short` check MUST NOT report OK on
  NXDOMAIN, which returns exit 0 with empty output);
- gate its exit code on priority-domain failures, not only on the aggregate
  failure count.

**Root cause correction (2026-08-07, verified live):** the arm1-oci Traefik
ACME resolver is healthy. `/opt/pangolin/config/traefik/traefik_config.yml`
declares `certificatesResolvers.letsencrypt.acme` using the `httpChallenge`
type, and `entryPoints.websecure.http.tls.certResolver` makes `letsencrypt`
the default for every `websecure` router — so no router needs to reference
the resolver by name, and none of the 7 stacks' `certResolver: letsencrypt`
values were ever mismatched. `acme.json` holds 4 valid, currently-issued
certificates (`pangolin`, `auth`, `infisical`, `openchamber`).
`CLOUDFLARE_DNS_API_TOKEN` is already set in `/opt/pangolin/.env`, and
DNS-01 is not used by this resolver at all — the token is irrelevant to the
observed failure.

The actual cause of `litellm`/`langfuse`/`vikunja`/`n8n`/`glance`/
`changedetection`/`paperless` serving `CN=TRAEFIK DEFAULT CERT` is that
**Traefik has no router for those hostnames at all** — they were never
registered as Pangolin resources, so requests fall through to the default
certificate. A second, independent fault produces `HTTP 000` on tunnel
hostnames for `infisical`, `openchamber`, and `komodo`: their Pangolin
`siteResources` rows are bound to sites that are offline (`bunchloch`,
`macbook`), and `infisical`'s destination is a LAN address unreachable from
arm1. Neither fault is an ACME or DNS-01 problem.

#### Scenario: A domain has DNS but no router

- **WHEN** `litellm.cianfhoghlaim.ie` resolves to the Pangolin edge
- **AND** no Pangolin resource exists for that hostname
- **THEN** Traefik SHALL serve `CN=TRAEFIK DEFAULT CERT` (verify code 21)
- **AND** `check-edge-tls.sh` SHALL report FAIL with remediation "create the
  Pangolin private resource for this hostname", not "repair ACME"

#### Scenario: A private resource is bound to an offline site

- **WHEN** a Pangolin `siteResources` row's site has `online = 0`
- **THEN** the hostname SHALL return no response (`HTTP 000`) rather than a
  certificate error
- **AND** `check-edge-tls.sh --all` SHALL report this distinctly from a TLS
  failure, naming the offline site
- **AND** `mise run iac-health` SHALL NOT report the platform as healthy

#### Scenario: All checked edge certificates and tunnel routes verify

- **WHEN** every public domain serves a full-chain certificate whose
  OpenSSL verify return code is `0`
- **AND** every private domain answers over the tunnel from an online site
- **AND** `bash scripts/check-edge-tls.sh --strict --all` runs
- **THEN** the script SHALL report `OK` per domain
- **AND** SHALL exit `0`
- **AND** `mise run iac-health` MUST invoke this gate and surface any failure

### Requirement: Localhost-first fallback for litellm and langfuse endpoints

Dev-side consumers SHALL resolve the LiteLLM gateway and Langfuse endpoints
to their localhost ports (not the `*.cianfhoghlaim.ie` edge) until those
hostnames are registered as reachable Pangolin private resources per the
edge routing requirement above. The `.infisical.env` template MUST set
`LITELLM_BASE_URL=http://localhost:4000/v1` and
`LANGFUSE_HOST=http://localhost:3000`, and MUST document the private-resource
edge URLs as the restoration targets. `opencode.json` MUST expose a
`litellm_local` provider bound to `http://localhost:4000/v1` authenticated
by `LITELLM_MASTER_KEY`. No consumer configuration MAY reference
`https://litellm.cianfhoghlaim.ie` or `https://langfuse.cianfhoghlaim.ie`
as an active endpoint until `scripts/check-edge-tls.sh --strict --all`
exits `0` for those domains.

#### Scenario: Dev session resolves the gateway locally

- **WHEN** a BAML client, agent, or notebook resolves `LITELLM_BASE_URL`
  from the hydrated environment
- **THEN** the value SHALL be `http://localhost:4000/v1`
- **AND** the request SHALL NOT traverse the edge

#### Scenario: Edge restoration after private-resource registration

- **WHEN** `bash scripts/check-edge-tls.sh --strict --all` exits `0` for
  `litellm.cianfhoghlaim.ie` and `langfuse.cianfhoghlaim.ie`
- **THEN** the template MAY restore `LITELLM_BASE_URL` and `LANGFUSE_HOST`
  to their private-resource hostnames, reachable through the Pangolin
  client VPN
- **AND** the restoration SHALL be recorded in the change tasks
