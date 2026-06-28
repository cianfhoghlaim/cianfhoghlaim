// Komodo IaC — Direct API client (browser-free, for use in Bun/Node)
// Uses fetch() to call the Komodo RPC API endpoints.

import { CONFIG } from "./config.ts";

export class KomodoRpc {
  constructor(
    private url: string = CONFIG.komodoUrl,
    private jwt: string = CONFIG.komodoJwt,
  ) {}

  private async call<T>(path: string, params: unknown = {}): Promise<T> {
    const r = await fetch(`${this.url}${path}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${this.jwt}`,
      },
      body: JSON.stringify(params),
    });
    if (!r.ok) {
      const text = await r.text();
      throw new Error(`komodo ${path} failed: ${r.status} ${text}`);
    }
    return r.json() as Promise<T>;
  }

  // ----- Auth -----
  async login(username: string, password: string): Promise<{ jwt: string }> {
    const r = await fetch(`${this.url}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        type: "LoginLocalUser",
        params: { username, password },
      }),
    });
    if (!r.ok) throw new Error(`login failed: ${r.status} ${await r.text()}`);
    const data = (await r.json()) as { data: { jwt: string } };
    this.jwt = data.data.jwt;
    return { jwt: this.jwt };
  }

  // ----- Read API -----
  read<T = unknown>(name: string, params: Record<string, unknown> = {}): Promise<T> {
    return this.call<T>(`/read/${name}`, params);
  }

  // ----- Write API -----
  write<T = unknown>(name: string, params: Record<string, unknown> = {}): Promise<T> {
    return this.call<T>(`/write/${name}`, params);
  }

  // ----- Execute API -----
  execute<T = unknown>(name: string, params: Record<string, unknown> = {}): Promise<T> {
    return this.call<T>(`/execute/${name}`, params);
  }

  // ----- Convenience -----
  async listServers() {
    return this.read<Array<{ id: string; name: string; tags: string[]; info: { state: string; address: string | null; region: string; public_key: string | null } }>>(
      "ListServers",
      {},
    );
  }
  async listStacks() {
    return this.read<Array<{ id: string; name: string; info: { server_id: string; state: string; status: string | null } }>>(
      "ListStacks",
      {},
    );
  }
  async listUsers() {
    return this.read<Array<{ username: string; admin: boolean; super_admin: boolean }>>("ListUsers", {});
  }
  async listResourceSyncs() {
    return this.read<Array<{ id: string; name: string; config: { resource_type: string; repo: string; directory: string } }>>(
      "ListResourceSyncs",
      {},
    );
  }

  // ----- High-level upserters (idempotent) -----
  async upsertServer(opts: {
    name: string;
    description: string;
    tags: string[];
    publicKey: string;
    region?: string;
  }) {
    // Create-or-update: try CreateServer, on conflict look up id and UpdateServer
    try {
      return await this.write("CreateServer", {
        name: opts.name,
        config: {
          description: opts.description,
          tags: opts.tags,
          config: {
            address: "",
            enabled: true,
            region: opts.region ?? "local",
            public_key: opts.publicKey,
          },
        },
      });
    } catch (e) {
      const msg = (e as Error).message;
      if (msg.includes("already exists") || msg.includes("409")) {
        const servers = await this.listServers();
        const existing = servers.find((s) => s.name === opts.name);
        if (!existing) throw new Error(`server ${opts.name} exists but not in list`);
        return await this.write("UpdateServer", {
          id: existing.id,
          config: {
            description: opts.description,
            tags: opts.tags,
            config: {
              address: "",
              enabled: true,
              region: opts.region ?? "local",
              public_key: opts.publicKey,
            },
          },
        });
      }
      throw e;
    }
  }

  async upsertStack(opts: {
    name: string;
    description: string;
    serverId: string;
    runDirectory: string;
    filePaths: string[];
    environment: string;
    tags: string[];
  }) {
    const body = {
      name: opts.name,
      config: {
        description: opts.description,
        tags: opts.tags,
        server_id: opts.serverId,
        run_directory: opts.runDirectory,
        config: {
          file_paths: opts.filePaths,
          environment: opts.environment,
        },
      },
    };
    try {
      return await this.write("CreateStack", body);
    } catch (e) {
      const msg = (e as Error).message;
      if (msg.includes("already exists") || msg.includes("409")) {
        const stacks = await this.listStacks();
        const existing = stacks.find((s) => s.name === opts.name);
        if (!existing) throw new Error(`stack ${opts.name} exists but not in list`);
        return await this.write("UpdateStack", { id: existing.id, ...body.config });
      }
      throw e;
    }
  }

  async upsertResourceSync(opts: {
    name: string;
    resourceType: "Stack" | "Procedure" | "ResourceSync";
    repo: string;
    branch: string;
    directory: string;
  }) {
    const config = {
      description: `Sync ${opts.resourceType} from ${opts.repo}:${opts.directory}`,
      resource_type: opts.resourceType,
      repo: opts.repo,
      branch: opts.branch,
      directory: opts.directory,
      managed: false,
      include_tags: [] as string[],
      exclude_tags: [] as string[],
      include_resources: [] as string[],
      exclude_resources: [] as string[],
    };
    try {
      return await this.write("CreateResourceSync", { name: opts.name, config });
    } catch (e) {
      const msg = (e as Error).message;
      if (msg.includes("already exists") || msg.includes("409")) {
        return await this.write("UpdateResourceSync", { name: opts.name, config });
      }
      throw e;
    }
  }

  async deployStack(stack: string, server: string): Promise<{ _id: { $oid: string } }> {
    return this.execute("DeployStack", { stack, server });
  }

  async getUpdate(id: string) {
    return this.read<{ status: string; success: boolean }>("GetUpdate", { id });
  }
}
