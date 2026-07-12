// bonnegar/iac/clients/komodo-client.ts — Komodo RPC + REST API client
// Hand-rolled fetch() (the komodo_client npm package has a localStorage browser-only bug).
// Extends the v0 KomodoRpc with 18 NEW methods (9 types: Procedure, ResourceSync, Monitor, Alert, Variable, Schedule, ActionRecipient, Repo, Builder).

import { CONFIG } from "../config.ts";
import type {
  KomodoServer,
  KomodoStack,
  KomodoProcedure,
  KomodoResourceSync,
  KomodoMonitor,
  KomodoAlert,
  KomodoVariable,
  KomodoSchedule,
  KomodoActionRecipient,
  KomodoRepo,
  KomodoBuilder,
} from "../models/komodo.ts";

export class KomodoClient {
  constructor(
    private url: string = CONFIG.komodoUrl,
    private jwt: string = CONFIG.komodoJwt,
  ) {}

  // -----------------------------------------------------------------------
  // Auth
  // -----------------------------------------------------------------------
  async login(username: string, password: string): Promise<{ jwt: string }> {
    const r = await fetch(`${this.url}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ type: "LoginLocalUser", params: { username, password } }),
    });
    if (!r.ok) throw new Error(`komodo login failed: ${r.status} ${await r.text()}`);
    const data = (await r.json()) as { data: { jwt: string } };
    this.jwt = data.data.jwt;
    return { jwt: this.jwt };
  }

  // -----------------------------------------------------------------------
  // Core RPC (read / write / execute)
  // -----------------------------------------------------------------------
  private async call<T>(path: string, params: unknown = {}): Promise<T> {
    const r = await fetch(`${this.url}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${this.jwt}` },
      body: JSON.stringify(params),
    });
    if (!r.ok) throw new Error(`komodo ${path} failed: ${r.status} ${await r.text()}`);
    return r.json() as Promise<T>;
  }

  read<T = unknown>(name: string, params: Record<string, unknown> = {}): Promise<T> {
    return this.call<T>(`/read/${name}`, params);
  }
  write<T = unknown>(name: string, params: Record<string, unknown> = {}): Promise<T> {
    return this.call<T>(`/write/${name}`, params);
  }
  execute<T = unknown>(name: string, params: Record<string, unknown> = {}): Promise<T> {
    return this.call<T>(`/execute/${name}`, params);
  }

  // -----------------------------------------------------------------------
  // Lists
  // -----------------------------------------------------------------------
  listServers() {
    return this.read<KomodoServer[]>("ListServers", {});
  }
  listStacks() {
    return this.read<KomodoStack[]>("ListStacks", {});
  }
  listResourceSyncs() {
    return this.read<KomodoResourceSync[]>("ListResourceSyncs", {});
  }
  listProcedures() {
    return this.read<KomodoProcedure[]>("ListProcedures", {});
  }
  listMonitors() {
    return this.read<KomodoMonitor[]>("ListMonitors", {});
  }
  listAlerts() {
    return this.read<KomodoAlert[]>("ListAlerts", {});
  }
  listVariables() {
    return this.read<KomodoVariable[]>("ListVariables", {});
  }
  listSchedules() {
    return this.read<KomodoSchedule[]>("ListSchedules", {});
  }
  listActionRecipients() {
    return this.read<KomodoActionRecipient[]>("ListActionRecipients", {});
  }
  listRepos() {
    return this.read<KomodoRepo[]>("ListRepos", {});
  }
  listBuilders() {
    return this.read<KomodoBuilder[]>("ListBuilders", {});
  }
  listUsers() {
    return this.read<Array<{ username: string; admin: boolean; super_admin: boolean }>>("ListUsers", {});
  }

  // -----------------------------------------------------------------------
  // High-level upserters (idempotent)
  // -----------------------------------------------------------------------
  async upsertServer(opts: KomodoServer) {
    try {
      return await this.write("CreateServer", { name: opts.name, config: opts });
    } catch (e) {
      const msg = (e as Error).message;
      if (msg.includes("already exists") || msg.includes("409")) {
        const servers = await this.listServers();
        const existing = servers.find((s) => s.name === opts.name);
        if (!existing) throw e;
        return await this.write("UpdateServer", { id: existing.id, config: opts });
      }
      throw e;
    }
  }

  async upsertStack(opts: KomodoStack) {
    try {
      return await this.write("CreateStack", { name: opts.name, config: opts });
    } catch (e) {
      const msg = (e as Error).message;
      if (msg.includes("already exists") || msg.includes("409")) {
        const stacks = await this.listStacks();
        const existing = stacks.find((s) => s.name === opts.name);
        if (!existing) throw e;
        return await this.write("UpdateStack", { id: existing.id, config: opts });
      }
      throw e;
    }
  }

  async upsertProcedure(opts: KomodoProcedure) {
    try {
      return await this.write("CreateProcedure", { name: opts.name, config: opts.config });
    } catch (e) {
      const msg = (e as Error).message;
      if (msg.includes("already exists") || msg.includes("409")) {
        const procedures = await this.listProcedures();
        const existing = procedures.find((p) => p.name === opts.name);
        if (!existing) throw e;
        return await this.write("UpdateProcedure", { id: existing.id, config: opts.config });
      }
      throw e;
    }
  }

  async upsertResourceSync(opts: KomodoResourceSync) {
    try {
      return await this.write("CreateResourceSync", { name: opts.name, config: opts.config });
    } catch (e) {
      const msg = (e as Error).message;
      if (msg.includes("already exists") || msg.includes("409")) {
        return await this.write("UpdateResourceSync", { name: opts.name, config: opts.config });
      }
      throw e;
    }
  }

  async upsertMonitor(opts: KomodoMonitor) {
    try {
      return await this.write("CreateMonitor", { name: opts.name, config: opts.config });
    } catch (e) {
      const msg = (e as Error).message;
      if (msg.includes("already exists") || msg.includes("409")) {
        return await this.write("UpdateMonitor", { name: opts.name, config: opts.config });
      }
      throw e;
    }
  }

  async upsertAlert(opts: KomodoAlert) {
    try {
      return await this.write("CreateAlert", { name: opts.name, config: opts.config });
    } catch (e) {
      const msg = (e as Error).message;
      if (msg.includes("already exists") || msg.includes("409")) {
        return await this.write("UpdateAlert", { name: opts.name, config: opts.config });
      }
      throw e;
    }
  }

  async upsertVariable(opts: KomodoVariable) {
    try {
      return await this.write("CreateVariable", { name: opts.name, value: opts.value, is_secret: opts.is_secret, config: opts });
    } catch (e) {
      const msg = (e as Error).message;
      if (msg.includes("already exists") || msg.includes("409")) {
        return await this.write("UpdateVariable", { name: opts.name, value: opts.value, is_secret: opts.is_secret, config: opts });
      }
      throw e;
    }
  }

  async upsertSchedule(opts: KomodoSchedule) {
    try {
      return await this.write("CreateSchedule", { name: opts.name, config: opts.config });
    } catch (e) {
      const msg = (e as Error).message;
      if (msg.includes("already exists") || msg.includes("409")) {
        return await this.write("UpdateSchedule", { name: opts.name, config: opts.config });
      }
      throw e;
    }
  }

  async upsertActionRecipient(opts: KomodoActionRecipient) {
    try {
      return await this.write("CreateActionRecipient", { name: opts.name, config: opts.config });
    } catch (e) {
      const msg = (e as Error).message;
      if (msg.includes("already exists") || msg.includes("409")) {
        return await this.write("UpdateActionRecipient", { name: opts.name, config: opts.config });
      }
      throw e;
    }
  }

  async upsertRepo(opts: KomodoRepo) {
    try {
      return await this.write("CreateRepo", { name: opts.name, config: opts.config });
    } catch (e) {
      const msg = (e as Error).message;
      if (msg.includes("already exists") || msg.includes("409")) {
        return await this.write("UpdateRepo", { name: opts.name, config: opts.config });
      }
      throw e;
    }
  }

  async upsertBuilder(opts: KomodoBuilder) {
    try {
      return await this.write("CreateBuilder", { name: opts.name, config: opts.config });
    } catch (e) {
      const msg = (e as Error).message;
      if (msg.includes("already exists") || msg.includes("409")) {
        return await this.write("UpdateBuilder", { name: opts.name, config: opts.config });
      }
      throw e;
    }
  }

  // -----------------------------------------------------------------------
  // Execute
  // -----------------------------------------------------------------------
  async deployStack(stack: string, server: string): Promise<{ _id: { $oid: string } }> {
    return this.execute("DeployStack", { stack, server });
  }
  async runProcedure(procedure: string): Promise<{ _id: { $oid: string } }> {
    return this.execute("RunProcedure", { procedure });
  }
  async getUpdate(id: string) {
    return this.read<{ status: string; success: boolean }>("GetUpdate", { id });
  }
}
