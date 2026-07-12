// bonneagar/iac/models/komodo.ts — Komodo typed models
// The 9 Komodo object types the IaC manages (Server, Stack, Procedure, ResourceSync, Monitor, Alert, Variable, Schedule, ActionRecipient) + 2 supporting types (Repo, Builder).

export interface KomodoServer {
  id?: string;
  name: string;
  description?: string;
  tags: string[];
  config: {
    address: string;
    enabled: boolean;
    region: string;
    public_key: string;
  };
}

export interface KomodoStack {
  id?: string;
  name: string;
  description?: string;
  server_id: string;
  run_directory: string;
  file_paths: string[];
  environment: string; // "\nK=V\n" block
  tags: string[];
}

export interface KomodoProcedure {
  id?: string;
  name: string;
  description?: string;
  config: {
    stages: KomodoProcedureStage[];
  };
  tags?: string[];
}

export interface KomodoProcedureStage {
  name: string;
  description?: string;
  exec: KomodoProcedureExec[];
}

export interface KomodoProcedureExec {
  kind: "BashCommand" | "HttpRequest" | "GitOperation" | "ContainerOperation";
  path?: string;
  command?: string;
  url?: string;
  method?: string;
  [key: string]: unknown;
}

export interface KomodoResourceSync {
  id?: string;
  name: string;
  description?: string;
  config: {
    resource_type: "Stack" | "Procedure" | "ResourceSync" | "Server" | "Monitor" | "Alert" | "Variable" | "Schedule" | "ActionRecipient";
    repo: string;
    branch: string;
    directory: string;
    managed?: boolean;
    delete?: boolean;
    include_tags?: string[];
    exclude_tags?: string[];
    include_resources?: string[];
    exclude_resources?: string[];
  };
  tags?: string[];
}

export interface KomodoMonitor {
  id?: string;
  name: string;
  description?: string;
  config: {
    resource_type: "Server" | "Stack" | "Container";
    resource_id: string;
    http_check?: { url: string; method?: string; interval_secs?: number };
    container_check?: { container_name: string };
  };
  tags?: string[];
}

export interface KomodoAlert {
  id?: string;
  name: string;
  description?: string;
  config: {
    target: { type: "Monitor" | "Stack" | "Server" | "Procedure"; id: string };
    level: "INFO" | "WARNING" | "CRITICAL";
    recipients: string[];
  };
  tags?: string[];
}

export interface KomodoVariable {
  id?: string;
  name: string;
  description?: string;
  value: string; // Redacted in diff output
  is_secret: boolean;
  tags?: string[];
}

export interface KomodoSchedule {
  id?: string;
  name: string;
  description?: string;
  config: {
    cron: string;
    target: { type: "Procedure" | "Stack" | "Script"; id: string };
  };
  tags?: string[];
}

export interface KomodoActionRecipient {
  id?: string;
  name: string;
  description?: string;
  config: {
    kind: "Discord" | "Slack" | "Email" | "Webhook";
    url?: string;
    channel?: string;
    recipients?: string[];
  };
  tags?: string[];
}

export interface KomodoRepo {
  id?: string;
  name: string;
  description?: string;
  config: {
    provider: "GitHub" | "GitLab" | "Gitea" | "Forgejo";
    account: string;
    repo: string;
    branch: string;
  };
  tags?: string[];
}

export interface KomodoBuilder {
  id?: string;
  name: string;
  description?: string;
  config: {
    build_path: string;
    dockerfile: string;
    repo_id: string;
    image_tag: string;
  };
  tags?: string[];
}
