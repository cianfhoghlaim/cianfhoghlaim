// bonnegar/iac/clients/infisical-client.ts — Infisical client (uses @infisical/sdk)
// The 10 methods for managing secrets, environments, folders, projects, and machine identities.

import { InfisicalSDK as SdkInfisicalClient } from "@infisical/sdk";
import { CONFIG, requireInfisicalAuth } from "../config.ts";
import type {
  InfisicalProject,
  InfisicalEnvironment,
  InfisicalFolder,
  InfisicalSecret,
  InfisicalMachineIdentity,
} from "../models/infisical.ts";

export class InfisicalClient {
  private sdk: SdkInfisicalClient;

  constructor() {
    const auth = requireInfisicalAuth();
    this.sdk = new SdkInfisicalClient({
      siteUrl: CONFIG.infisicalUrl,
      // The SDK accepts either a static token OR client_id + client_secret
      ...(auth && "token" in auth
        ? { token: auth.token }
        : { clientId: (auth as { clientId: string }).clientId, clientSecret: (auth as { clientSecret: string }).clientSecret }),
    });
  }

  // -----------------------------------------------------------------------
  // Projects
  // -----------------------------------------------------------------------
  async listProjects(): Promise<InfisicalProject[]> {
    const { projects } = await this.sdk.listProjects();
    return projects.map((p) => ({ id: p.id, name: p.name, slug: p.slug, description: p.description }));
  }
  async getProject(slug: string): Promise<InfisicalProject> {
    const p = await this.sdk.getProject({ projectId: slug });
    return { id: p.project.id, name: p.project.name, slug: p.project.slug, description: p.project.description };
  }

  // -----------------------------------------------------------------------
  // Environments
  // -----------------------------------------------------------------------
  async listEnvironments(projectId: string): Promise<InfisicalEnvironment[]> {
    const { environments } = await this.sdk.listEnvironments({ projectId });
    return environments.map((e) => ({ id: e.id, name: e.name, slug: e.slug, projectId }));
  }
  async createEnvironment(projectId: string, name: string, slug: string): Promise<InfisicalEnvironment> {
    const e = await this.sdk.createEnvironment({ projectId, name, slug });
    return { id: e.environment.id, name: e.environment.name, slug: e.environment.slug, projectId };
  }

  // -----------------------------------------------------------------------
  // Folders
  // -----------------------------------------------------------------------
  async listFolders(projectId: string, environment: string): Promise<InfisicalFolder[]> {
    const { folders } = await this.sdk.listFolders({ projectId, environment });
    return folders.map((f) => ({ id: f.id, name: f.name, path: f.path, environmentId: f.environment, projectId }));
  }
  async createFolder(projectId: string, environment: string, name: string, path: string = "/"): Promise<InfisicalFolder> {
    const f = await this.sdk.createFolder({ projectId, environment, name, path });
    return { id: f.folder.id, name: f.folder.name, path: f.folder.path, environmentId: f.folder.environment, projectId };
  }

  // -----------------------------------------------------------------------
  // Secrets
  // -----------------------------------------------------------------------
  async listSecrets(projectId: string, environment: string, path: string = "/"): Promise<InfisicalSecret[]> {
    const { secrets } = await this.sdk.listSecrets({ projectId, environment, secretPath: path });
    return secrets.map((s) => ({
      id: s.id,
      key: s.secretKey,
      value: s.secretValue,
      path: s.secretPath,
      environment,
      projectId,
      type: s.type === 2 ? "personal" : "shared",
    }));
  }
  async getSecret(projectId: string, environment: string, key: string, path: string = "/"): Promise<InfisicalSecret | null> {
    try {
      const s = await this.sdk.getSecret({ secretName: key, projectId, environment, secretPath: path });
      return {
        id: s.id,
        key: s.secretKey,
        value: s.secretValue,
        path: s.secretPath,
        environment,
        projectId,
      };
    } catch (e) {
      if ((e as Error).message.includes("404")) return null;
      throw e;
    }
  }
  async createSecret(opts: InfisicalSecret): Promise<InfisicalSecret> {
    const s = await this.sdk.createSecret({
      projectId: opts.projectId,
      environment: opts.environment,
      secretName: opts.key,
      secretValue: opts.value,
      secretPath: opts.path,
      type: opts.type === "personal" ? "personal" : "shared",
    });
    return { ...opts, id: s.id };
  }
  async updateSecret(opts: InfisicalSecret): Promise<InfisicalSecret> {
    const s = await this.sdk.updateSecret(opts.key, {
      projectId: opts.projectId,
      environment: opts.environment,
      secretValue: opts.value,
      secretPath: opts.path,
    });
    return { ...opts, id: s.id };
  }
  async deleteSecret(projectId: string, environment: string, key: string, path: string = "/"): Promise<void> {
    await this.sdk.deleteSecret({ secretName: key, projectId, environment, secretPath: path });
  }

  // -----------------------------------------------------------------------
  // Machine identities
  // -----------------------------------------------------------------------
  async listMachineIdentities(projectId: string): Promise<InfisicalMachineIdentity[]> {
    // The SDK doesn't yet have a high-level list method; use the raw API
    const auth = requireInfisicalAuth();
    const token = "token" in auth ? auth.token : await this.login();
    const r = await fetch(`${CONFIG.infisicalUrl}/api/v1/auth/machine-identities?projectId=${projectId}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!r.ok) throw new Error(`infisical list identities failed: ${r.status} ${await r.text()}`);
    const data = (await r.json()) as { identities: Array<{ id: string; name: string }> };
    return data.identities.map((i) => ({ id: i.id, name: i.name, projectId }));
  }
  async createMachineIdentity(opts: { name: string; projectId: string; permissions?: string[] }): Promise<InfisicalMachineIdentity> {
    // The SDK doesn't yet have a high-level create method; use the raw API
    const auth = requireInfisicalAuth();
    const token = "token" in auth ? auth.token : await this.login();
    const r = await fetch(`${CONFIG.infisicalUrl}/api/v1/auth/machine-identities`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
      body: JSON.stringify({ name: opts.name, projectId: opts.projectId }),
    });
    if (!r.ok) throw new Error(`infisical create identity failed: ${r.status} ${await r.text()}`);
    const data = (await r.json()) as { identity: { id: string; name: string; clientId: string; clientSecret: string } };
    return { id: data.identity.id, name: data.identity.name, projectId: opts.projectId, clientId: data.identity.clientId, clientSecret: data.identity.clientSecret };
  }

  // -----------------------------------------------------------------------
  // Internal
  // -----------------------------------------------------------------------
  private async login(): Promise<string> {
    // Use Universal Auth (clientId + clientSecret → JWT)
    const auth = requireInfisicalAuth();
    if ("token" in auth) return auth.token;
    const r = await fetch(`${CONFIG.infisicalUrl}/api/v1/auth/universal-auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ clientId: auth.clientId, clientSecret: auth.clientSecret }),
    });
    if (!r.ok) throw new Error(`infisical login failed: ${r.status} ${await r.text()}`);
    const data = (await r.json()) as { accessToken: string };
    return data.accessToken;
  }

  async health(): Promise<{ healthy: boolean; detail: string }> {
    try {
      const r = await fetch(`${CONFIG.infisicalUrl}/api/status`);
      return { healthy: r.ok, detail: `infisical status: ${r.status}` };
    } catch (e) {
      return { healthy: false, detail: (e as Error).message };
    }
  }
}
