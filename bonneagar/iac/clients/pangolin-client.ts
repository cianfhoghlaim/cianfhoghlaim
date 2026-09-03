// bonnegar/iac/clients/pangolin-client.ts — Pangolin Integrations API client
// Enterprise Edition (verified by PANGOLIN_LICENCE=PER-...) — uses the
// /v1/org/{orgId}/... per-resource CRUD surface + the /api/v1/integration/...
// bulk-import surface.
// Extends the v0 PangolinRpc with 8 NEW methods (5 per-resource + 3 blueprint).

import { CONFIG } from "../config.ts";
import type {
  PangolinOrg,
  PangolinSite,
  PangolinResource,
  PangolinBlueprint,
  PangolinOlmClient,
  PangolinClientCert,
} from "../models/pangolin.ts";

export class PangolinClient {
  constructor(
    private base: string = CONFIG.pangolinApiBase,
    private apiKey: string = CONFIG.pangolinApiKey,
    private orgId: string = CONFIG.pangolinOrgId,
  ) {}

  // -----------------------------------------------------------------------
  // Core
  // -----------------------------------------------------------------------
  private async call<T>(path: string, body: unknown = {}): Promise<T> {
    const r = await fetch(`${this.base}${path}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${this.apiKey}`,
      },
      body: JSON.stringify(body),
    });
    if (!r.ok) {
      const text = await r.text();
      throw new Error(`pangolin ${path} failed: ${r.status} ${text}`);
    }
    return r.json() as Promise<T>;
  }

  private async callGet<T>(path: string): Promise<T> {
    const r = await fetch(`${this.base}${path}`, {
      headers: { Authorization: `Bearer ${this.apiKey}` },
    });
    if (!r.ok) throw new Error(`pangolin GET ${path} failed: ${r.status} ${await r.text()}`);
    return r.json() as Promise<T>;
  }

  // -----------------------------------------------------------------------
  // Per-resource CRUD (the 9 methods)
  // -----------------------------------------------------------------------
  listOrganizations() {
    return this.callGet<{ data: { orgs: PangolinOrg[] } }>(`/orgs`);
  }
  createOrganization(opts: { name: string; description?: string }) {
    return this.call<{ data: PangolinOrg }>(`/orgs`, opts);
  }
  listSites() {
    return this.callGet<{ data: { sites: PangolinSite[] } }>(`/org/${this.orgId}/sites`);
  }
  createSite(opts: { name: string; description?: string; address?: string; region?: string; public_key?: string }) {
    return this.call<{ data: PangolinSite }>(`/org/${this.orgId}/site`, opts);
  }
  listResources() {
    return this.callGet<{ data: { siteResources: Array<{ siteResourceId: number; fullDomain: string; niceId: string; name: string }> } }>(
      `/org/${this.orgId}/site-resources`,
    );
  }
  createSiteResource(body: PangolinResource) {
    return this.call<{ data: { siteResourceId: number } }>(`/org/${this.orgId}/site-resource`, body);
  }
  async deleteSiteResource(id: number) {
    const r = await fetch(`${this.base}/site-resource/${id}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${this.apiKey}` },
    });
    if (!r.ok) throw new Error(`pangolin delete ${id} failed: ${r.status} ${await r.text()}`);
  }

  // OLM clients
  listOlmClients() {
    return this.callGet<{ data: { olmClients: PangolinOlmClient[] } }>(
      `/api/v1/integration/olm-client?orgId=${this.orgId}`,
    );
  }
  createOlmClient(opts: PangolinOlmClient) {
    return this.call<{ data: PangolinOlmClient }>(
      `/api/v1/integration/olm-client`,
      { orgId: this.orgId, ...opts },
    );
  }

  // -------------------------------------------------------------------------
  // Identity Providers (OIDC / SAML) — Pocket ID wiring
  // -------------------------------------------------------------------------
  // GET /api/v1/idp?org_id=... — list IdPs for an org
  listIdps() {
    return this.call<{ data: Array<{ idp_id: string; name: string; provider_type: string }> }>(
      `/idp?org_id=${this.orgId}`,
    );
  }
  // POST /api/v1/idp — create an IdP (OIDC / OAuth2 / SAML)
  createIdp(opts: {
    org_id: string;
    name: string;
    provider_type: "OAuth2OIDC" | "OAuth2Generic" | "SAML";
    client_id: string;
    client_secret: string;
    authorization_url?: string;
    token_url?: string;
    userinfo_url?: string;
    scopes?: string;
    identifier_path?: string;
    email_path?: string;
    name_path?: string;
    auto_provision?: boolean;
  }) {
    return this.call<{ data: { idp_id: string } }>(`/idp`, opts);
  }
  // DELETE /api/v1/idp/{idp_id}?org_id=... — remove an IdP
  async deleteIdp(idpId: string) {
    const r = await fetch(
      `${this.base}/idp/${idpId}?org_id=${this.orgId}`,
      { method: "DELETE", headers: { Authorization: `Bearer ${this.apiKey}` } },
    );
    if (!r.ok) throw new Error(`pangolin delete idp ${idpId} failed: ${r.status} ${await r.text()}`);
  }

  // -----------------------------------------------------------------------
  // Blueprint import (the 3 methods — bulk surface)
  // -----------------------------------------------------------------------
  uploadBlueprint(opts: { name: string; yaml: string }) {
    return this.call<{ data: PangolinBlueprint }>(
      `/api/v1/integration/blueprint`,
      { orgId: this.orgId, ...opts },
    );
  }
  listBlueprints() {
    return this.callGet<{ data: { blueprints: PangolinBlueprint[] } }>(
      `/api/v1/integration/blueprint?orgId=${this.orgId}`,
    );
  }
  async deleteBlueprint(id: number) {
    const r = await fetch(`${this.base}/api/v1/integration/blueprint/${id}?orgId=${this.orgId}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${this.apiKey}` },
    });
    if (!r.ok) throw new Error(`pangolin delete blueprint ${id} failed: ${r.status} ${await r.text()}`);
  }

  // -----------------------------------------------------------------------
  // Client Management (Integrations API)
  // -----------------------------------------------------------------------
  // ADDED 2026-08-15 (per the 2026-08-15-bonneagar-infra-remediation-v2
  // openspec change). The Pangolin client-mgmt surface is at
  // `/v1/org/{orgId}/clients` (NOT `/v1/api/v1/integration/clients` —
  // the latter is a 404 on this server; the docs at
  // https://docs.pangolin.net/manage/clients/install-client are
  // aspirational). The endpoint returns ALL clients (OLM + user +
  // machine) — filter by `type` client-side if needed.
  //
  // Per https://docs.pangolin.net/manage/clients/install-client:
  //   - User clients are minted for operator-laptop use (the macOS .app
  //     picks them up via `pangolin login --id <id> --secret <secret>
  //     --endpoint https://pangolin.cianfhoghlaim.ie`).
  //   - Machine clients are minted for server-side use (the newt
  //     container + the pangolin CLI in headless mode).
  //   - The `secret` field is write-only (returned ONCE on create).
  // -----------------------------------------------------------------------
  listClients() {
    return this.callGet<{ data: { clients: PangolinClientCert[] } }>(
      `/org/${this.orgId}/clients`,
    );
  }
  getClient(id: number) {
    return this.callGet<{ data: PangolinClientCert }>(
      `/org/${this.orgId}/clients/${id}`,
    );
  }
  createClient(opts: {
    name: string;
    type: "user" | "machine";
    siteIds?: number[];
    expiresIn?: number;
  }) {
    return this.call<{ data: { id: number; clientId: string; secret: string } }>(
      `/org/${this.orgId}/clients`,
      { name: opts.name, type: opts.type, siteIds: opts.siteIds, expiresIn: opts.expiresIn ?? 0 },
    );
  }
  async deleteClient(id: number) {
    const r = await fetch(
      `${this.base}/org/${this.orgId}/clients/${id}`,
      {
        method: "DELETE",
        headers: { Authorization: `Bearer ${this.apiKey}` },
      },
    );
    if (!r.ok) {
      throw new Error(`pangolin delete client ${id} failed: ${r.status} ${await r.text()}`);
    }
  }

  // -----------------------------------------------------------------------
  // Health
  // -----------------------------------------------------------------------
  async health(): Promise<{ healthy: boolean; detail: string }> {
    try {
      const r = await fetch(`${this.base.replace("/v1", "")}/api/health`);
      return { healthy: r.ok, detail: `pangolin health: ${r.status}` };
    } catch (e) {
      return { healthy: false, detail: (e as Error).message };
    }
  }
}
