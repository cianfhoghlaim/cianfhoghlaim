// bonneagar/iac/models/infisical.ts — Infisical typed models
// The 5 Infisical object types the IaC manages (Project, Environment, Folder, Secret, MachineIdentity).

export interface InfisicalProject {
  id: string;
  name: string;
  slug: string;
  description?: string;
}

export interface InfisicalEnvironment {
  id: string;
  name: string;
  slug: string;
  projectId: string;
}

export interface InfisicalFolder {
  id: string;
  name: string;
  path: string;
  environmentId: string;
  projectId: string;
}

export interface InfisicalSecret {
  id?: string;
  key: string; // e.g. "slack_webhook_url"
  value: string; // e.g. "https://hooks.slack.com/..." (REDACTED in diff output)
  type?: "shared" | "personal";
  path: string; // e.g. "/ci/hf-watchdog"
  environment: string; // e.g. "dev-baile"
  projectId: string;
  comment?: string;
}

export interface InfisicalMachineIdentity {
  id: string;
  name: string;
  projectId: string;
  // The client_id + client_secret are returned ONCE on creation
  // (similar to AWS access keys). Store in Infisical's own vault
  // + in the .env (via Locket).
  clientId?: string;
  clientSecret?: string;
  permissions?: string[];
}
