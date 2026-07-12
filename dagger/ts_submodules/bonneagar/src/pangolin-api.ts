/**
 * Pangolin Integration API Wrapper Module
 *
 * Provides programmatic access to Pangolin's Integration API for:
 * - Organization management
 * - Site creation and configuration
 * - Resource management
 * - Blueprint application
 * - API key generation
 *
 * API Reference: bonneagar/pangolin/config/openapi.yaml
 */

import {
  dag,
  Container,
  Secret,
  object,
  func,
  field,
} from "@dagger.io/dagger";

import type {
  OrgResult,
  SiteResult,
  SiteDefaults,
  ApiKey,
  SiteConfig,
} from "./types";

@object()
export class PangolinApi {
  @field()
  baseUrl: string;

  @field()
  apiToken: Secret;

  constructor(baseUrl: string, apiToken: Secret) {
    this.baseUrl = baseUrl;
    this.apiToken = apiToken;
  }

  /**
   * Get a curl container with Pangolin auth configured
   */
  private curlContainer(): Container {
    return dag
      .container()
      .from("curlimages/curl:8.11.1")
      .withSecretVariable("PANGOLIN_TOKEN", this.apiToken);
  }

  /**
   * Execute a GET request to Pangolin API
   */
  private async get(path: string): Promise<string> {
    return this.curlContainer()
      .withExec([
        "sh",
        "-c",
        `curl -sf -X GET "${this.baseUrl}/v1${path}" \
          -H "Content-Type: application/json" \
          -H "Authorization: Bearer $PANGOLIN_TOKEN"`,
      ])
      .stdout();
  }

  /**
   * Execute a PUT request to Pangolin API
   */
  private async put(path: string, body: object): Promise<string> {
    const jsonBody = JSON.stringify(body);
    return this.curlContainer()
      .withExec([
        "sh",
        "-c",
        `curl -sf -X PUT "${this.baseUrl}/v1${path}" \
          -H "Content-Type: application/json" \
          -H "Authorization: Bearer $PANGOLIN_TOKEN" \
          -d '${jsonBody}'`,
      ])
      .stdout();
  }

  /**
   * Execute a POST request to Pangolin API
   */
  private async post(path: string, body: object): Promise<string> {
    const jsonBody = JSON.stringify(body);
    return this.curlContainer()
      .withExec([
        "sh",
        "-c",
        `curl -sf -X POST "${this.baseUrl}/v1${path}" \
          -H "Content-Type: application/json" \
          -H "Authorization: Bearer $PANGOLIN_TOKEN" \
          -d '${jsonBody}'`,
      ])
      .stdout();
  }

  // ==========================================================================
  // Health Check
  // ==========================================================================

  /**
   * Check Pangolin Integration API health
   */
  @func()
  async health(): Promise<string> {
    return this.curlContainer()
      .withExec([
        "sh",
        "-c",
        `curl -sf "${this.baseUrl}/v1/" \
          -H "Authorization: Bearer $PANGOLIN_TOKEN"`,
      ])
      .stdout();
  }

  // ==========================================================================
  // Organization Management
  // ==========================================================================

  /**
   * Create a new organization
   */
  @func()
  async createOrg(
    orgId: string,
    name: string,
    subnet: string
  ): Promise<string> {
    return this.put("/org", { orgId, name, subnet });
  }

  /**
   * Get an organization by ID
   */
  @func()
  async getOrg(orgId: string): Promise<string> {
    return this.get(`/org/${orgId}`);
  }

  /**
   * List all organizations
   */
  @func()
  async listOrgs(limit: number = 1000, offset: number = 0): Promise<string> {
    return this.get(`/orgs?limit=${limit}&offset=${offset}`);
  }

  /**
   * Update an organization
   */
  @func()
  async updateOrg(orgId: string, updates: object): Promise<string> {
    return this.post(`/org/${orgId}`, updates);
  }

  // ==========================================================================
  // Site Management
  // ==========================================================================

  /**
   * Get pre-requisite data for creating a site
   */
  @func()
  async pickSiteDefaults(orgId: string): Promise<string> {
    return this.get(`/org/${orgId}/pick-site-defaults`);
  }

  /**
   * Create a new site
   */
  @func()
  async createSite(
    orgId: string,
    name: string,
    type: "newt" | "wireguard" | "local",
    exitNodeId?: number,
    newtId?: string,
    secret?: string,
    subnet?: string,
    address?: string
  ): Promise<string> {
    const body: Record<string, unknown> = { name, type };
    if (exitNodeId) body.exitNodeId = exitNodeId;
    if (newtId) body.newtId = newtId;
    if (secret) body.secret = secret;
    if (subnet) body.subnet = subnet;
    if (address) body.address = address;

    return this.put(`/org/${orgId}/site`, body);
  }

  /**
   * Get a site by ID
   */
  @func()
  async getSite(siteId: number): Promise<string> {
    return this.get(`/site/${siteId}`);
  }

  /**
   * Get a site by org ID and nice ID
   */
  @func()
  async getSiteByNiceId(orgId: string, niceId: string): Promise<string> {
    return this.get(`/org/${orgId}/site/${niceId}`);
  }

  /**
   * List all sites in an organization
   */
  @func()
  async listSites(
    orgId: string,
    limit: number = 1000,
    offset: number = 0
  ): Promise<string> {
    return this.get(`/org/${orgId}/sites?limit=${limit}&offset=${offset}`);
  }

  /**
   * Update a site
   */
  @func()
  async updateSite(siteId: number, updates: object): Promise<string> {
    return this.post(`/site/${siteId}`, updates);
  }

  // ==========================================================================
  // Resource Management
  // ==========================================================================

  /**
   * Create a resource
   */
  @func()
  async createResource(
    orgId: string,
    name: string,
    http: boolean,
    protocol: "tcp" | "udp",
    domainId?: string,
    proxyPort?: number,
    subdomain?: string,
    stickySession?: boolean
  ): Promise<string> {
    const body: Record<string, unknown> = { name, http, protocol };
    if (domainId) body.domainId = domainId;
    if (proxyPort) body.proxyPort = proxyPort;
    if (subdomain) body.subdomain = subdomain;
    if (stickySession !== undefined) body.stickySession = stickySession;

    return this.put(`/org/${orgId}/resource`, body);
  }

  /**
   * Get a resource by ID
   */
  @func()
  async getResource(resourceId: number): Promise<string> {
    return this.get(`/resource/${resourceId}`);
  }

  /**
   * List resources for an organization
   */
  @func()
  async listResources(
    orgId: string,
    limit: number = 1000,
    offset: number = 0
  ): Promise<string> {
    return this.get(`/org/${orgId}/resources?limit=${limit}&offset=${offset}`);
  }

  /**
   * Create a target for a resource
   */
  @func()
  async createTarget(
    resourceId: string,
    siteId: number,
    ip: string,
    port: number,
    method?: string,
    enabled?: boolean
  ): Promise<string> {
    const body: Record<string, unknown> = { siteId, ip, port };
    if (method) body.method = method;
    if (enabled !== undefined) body.enabled = enabled;

    return this.put(`/resource/${resourceId}/target`, body);
  }

  // ==========================================================================
  // Blueprint Management
  // ==========================================================================

  /**
   * Apply a blueprint to an organization (base64 encoded JSON)
   */
  @func()
  async applyBlueprint(orgId: string, blueprintBase64: string): Promise<string> {
    return this.put(`/org/${orgId}/blueprint`, { blueprint: blueprintBase64 });
  }

  /**
   * List all blueprints for an organization
   */
  @func()
  async listBlueprints(
    orgId: string,
    limit: number = 1000,
    offset: number = 0
  ): Promise<string> {
    return this.get(`/org/${orgId}/blueprints?limit=${limit}&offset=${offset}`);
  }

  /**
   * Get a blueprint by ID
   */
  @func()
  async getBlueprint(orgId: string, blueprintId: string): Promise<string> {
    return this.get(`/org/${orgId}/blueprint/${blueprintId}`);
  }

  // ==========================================================================
  // API Key Management
  // ==========================================================================

  /**
   * Create an API key for an organization
   */
  @func()
  async createApiKey(orgId: string, name: string): Promise<string> {
    return this.put(`/org/${orgId}/api-key`, { name });
  }

  /**
   * List API keys for an organization
   */
  @func()
  async listApiKeys(
    orgId: string,
    limit: number = 1000,
    offset: number = 0
  ): Promise<string> {
    return this.get(`/org/${orgId}/api-keys?limit=${limit}&offset=${offset}`);
  }

  // ==========================================================================
  // Domain Management
  // ==========================================================================

  /**
   * List domains for an organization
   */
  @func()
  async listDomains(
    orgId: string,
    limit: number = 1000,
    offset: number = 0
  ): Promise<string> {
    return this.get(`/org/${orgId}/domains?limit=${limit}&offset=${offset}`);
  }

  /**
   * Get a domain by ID
   */
  @func()
  async getDomain(orgId: string, domainId: string): Promise<string> {
    return this.get(`/org/${orgId}/domain/${domainId}`);
  }

  /**
   * Get DNS records for a domain
   */
  @func()
  async getDnsRecords(orgId: string, domainId: string): Promise<string> {
    return this.get(`/org/${orgId}/domain/${domainId}/dns-records`);
  }

  // ==========================================================================
  // Role Management
  // ==========================================================================

  /**
   * Create a role
   */
  @func()
  async createRole(
    orgId: string,
    name: string,
    description?: string
  ): Promise<string> {
    const body: Record<string, unknown> = { name };
    if (description) body.description = description;
    return this.put(`/org/${orgId}/role`, body);
  }

  /**
   * List roles for an organization
   */
  @func()
  async listRoles(
    orgId: string,
    limit: number = 1000,
    offset: number = 0
  ): Promise<string> {
    return this.get(`/org/${orgId}/roles?limit=${limit}&offset=${offset}`);
  }

  // ==========================================================================
  // Client (OLM) Management
  // ==========================================================================

  /**
   * Get pre-requisite data for creating a client
   */
  @func()
  async pickClientDefaults(orgId: string): Promise<string> {
    return this.get(`/org/${orgId}/pick-client-defaults`);
  }

  /**
   * Create an OLM client
   */
  @func()
  async createClient(
    orgId: string,
    name: string,
    siteIds: number[],
    olmId: string,
    secret: string,
    subnet: string
  ): Promise<string> {
    return this.put(`/org/${orgId}/client`, {
      name,
      siteIds,
      olmId,
      secret,
      subnet,
      type: "olm",
    });
  }

  /**
   * List clients for an organization
   */
  @func()
  async listClients(
    orgId: string,
    limit: number = 1000,
    offset: number = 0
  ): Promise<string> {
    return this.get(`/org/${orgId}/clients?limit=${limit}&offset=${offset}`);
  }

  /**
   * Create an OLM client with all required defaults
   * Convenience wrapper that fetches defaults and generates credentials
   */
  @func()
  async createOLMClientWithDefaults(
    orgId: string,
    name: string,
    siteIds: number[]
  ): Promise<string> {
    // Get defaults first
    const defaultsJson = await this.pickClientDefaults(orgId);
    const defaults = JSON.parse(defaultsJson);

    // Generate credentials for OLM client
    const olmId = `olm-${name.toLowerCase().replace(/\s+/g, "-")}`;
    const secret = await this.generateSecret();

    // Create the client
    const result = await this.createClient(
      orgId,
      name,
      siteIds,
      olmId,
      secret,
      defaults.suggestedSubnet
    );

    // Parse result and attach generated credentials for storage
    const clientData = JSON.parse(result);
    return JSON.stringify({
      ...clientData,
      olmId,
      secret,
    });
  }

  // ==========================================================================
  // Identity Provider Management
  // ==========================================================================

  /**
   * Create an OIDC identity provider
   */
  @func()
  async createOidcIdp(
    name: string,
    clientId: string,
    clientSecret: Secret,
    authUrl: string,
    tokenUrl: string,
    identifierPath: string,
    scopes: string,
    emailPath?: string,
    namePath?: string,
    autoProvision?: boolean
  ): Promise<string> {
    return this.curlContainer()
      .withSecretVariable("IDP_CLIENT_SECRET", clientSecret)
      .withExec([
        "sh",
        "-c",
        `curl -sf -X PUT "${this.baseUrl}/v1/idp/oidc" \
          -H "Content-Type: application/json" \
          -H "Authorization: Bearer $PANGOLIN_TOKEN" \
          -d '{
            "name": "${name}",
            "clientId": "${clientId}",
            "clientSecret": "'"$IDP_CLIENT_SECRET"'",
            "authUrl": "${authUrl}",
            "tokenUrl": "${tokenUrl}",
            "identifierPath": "${identifierPath}",
            "scopes": "${scopes}"
            ${emailPath ? `,"emailPath": "${emailPath}"` : ""}
            ${namePath ? `,"namePath": "${namePath}"` : ""}
            ${autoProvision !== undefined ? `,"autoProvision": ${autoProvision}` : ""}
          }'`,
      ])
      .stdout();
  }

  /**
   * List identity providers
   */
  @func()
  async listIdps(limit: number = 1000, offset: number = 0): Promise<string> {
    return this.get(`/idp?limit=${limit}&offset=${offset}`);
  }

  // ==========================================================================
  // Helper Functions
  // ==========================================================================

  /**
   * Create a site with all required defaults
   * Convenience wrapper that fetches defaults first
   */
  @func()
  async createSiteWithDefaults(
    orgId: string,
    name: string,
    type: "newt" | "wireguard" | "local" = "newt"
  ): Promise<string> {
    // Get defaults first
    const defaultsJson = await this.pickSiteDefaults(orgId);
    const defaults = JSON.parse(defaultsJson);

    // Generate credentials for Newt sites
    const newtId = type === "newt" ? `newt-${name.toLowerCase().replace(/\s+/g, "-")}` : undefined;
    const secret = type === "newt" ? await this.generateSecret() : undefined;

    return this.createSite(
      orgId,
      name,
      type,
      defaults.exitNodeId,
      newtId,
      secret,
      defaults.suggestedSubnet,
      undefined
    );
  }

  /**
   * Generate a random secret string
   */
  private async generateSecret(): Promise<string> {
    const result = await dag
      .container()
      .from("alpine:3.19")
      .withExec(["sh", "-c", "cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1"])
      .stdout();
    return result.trim();
  }
}
