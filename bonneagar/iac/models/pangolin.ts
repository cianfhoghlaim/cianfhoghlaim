// bonneagar/iac/models/pangolin.ts — Pangolin typed models
// The 5 Pangolin object types the IaC manages (Site, Resource, Target, Blueprint, OlmClient) — verified by PANGOLIN_LICENCE=PER-... (Enterprise Edition).

export interface PangolinOrg {
  id?: string;
  name: string;
  description?: string;
}

export interface PangolinSite {
  id?: number;
  name: string;
  description?: string;
  config?: {
    address?: string;
    region?: string;
    public_key?: string;
  };
}

export type PangolinResourceMode = "http" | "host" | "cidr" | "tcp";
export type PangolinResourceScheme = "http" | "https";
export type PangolinResourceProtocol = "http" | "https" | "tcp" | "udp";

export interface PangolinResource {
  name: string;
  niceId: string;
  subdomain: string;
  destination: string;
  destinationPort: number;
  siteId: number;
  description?: string;
  mode?: PangolinResourceMode;
  scheme?: PangolinResourceScheme;
  protocol?: PangolinResourceProtocol;
  enabled?: boolean;
  userIds?: number[];
  roleIds?: number[];
  clientIds?: number[];
  domainId?: string;
}

export interface PangolinTarget {
  siteId: number;
  hostname: string;
  method: "http" | "https" | "tcp";
  port: number;
}

export interface PangolinBlueprint {
  id?: number;
  name: string;
  yaml: string; // The full blueprint YAML (private-resources + public-resources)
}

export interface PangolinOlmClient {
  id?: number;
  name: string;
  siteId: number;
  olmId?: string;
  config?: Record<string, unknown>;
}
