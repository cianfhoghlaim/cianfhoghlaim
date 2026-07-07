/**
 * Pangolin Docker Label Generator
 *
 * Generates Pangolin Docker labels for service discovery and routing.
 * Supports both old format (pangolin.resource.*) and new format (pangolin.public-resources.*).
 *
 * Usage:
 *   dagger call pangolin-labels generate --resource-id="komodo" --domain="komodo.example.com" --port=9120
 *   dagger call pangolin-labels generate-yaml --service-name="komodo" --config='{"resourceId":"komodo",...}'
 */

import { object, func, field } from "@dagger.io/dagger";

/** Label format version */
export type LabelFormat = "v1" | "v2";

/** Protocol for the service */
export type Protocol = "http" | "https";

/** Authentication configuration */
export interface AuthConfig {
  ssoEnabled: boolean;
  ssoRoles?: string[];
}

/** Configuration for a single resource */
export interface ResourceConfig {
  resourceId: string;
  name: string;
  domain: string;
  port: number;
  protocol?: Protocol;
  auth?: AuthConfig;
  siteName?: string;
  hostname?: string;
}

/** Domain configuration for parameterized deployments */
export interface DomainConfig {
  baseDomain: string;
  subdomainPattern?: string; // e.g., "{service}.{baseDomain}"
}

@object()
export class PangolinLabels {
  @field()
  baseDomain: string;

  @field()
  defaultSite: string;

  @field()
  labelFormat: string;

  constructor(
    baseDomain: string = "cianfhoghlaim.ie",
    defaultSite: string = "arm1-oci",
    labelFormat: string = "v2"
  ) {
    this.baseDomain = baseDomain;
    this.defaultSite = defaultSite;
    this.labelFormat = labelFormat;
  }

  /**
   * Generate Pangolin labels for a service
   */
  @func()
  generate(
    resourceId: string,
    name: string,
    subdomain: string,
    port: number,
    protocol: string = "http",
    siteName?: string,
    hostname?: string,
    ssoEnabled: boolean = false,
    ssoRoles: string = ""
  ): string {
    const site = siteName || this.defaultSite;
    const host = hostname || resourceId;
    const domain = `${subdomain}.${this.baseDomain}`;
    const format = this.labelFormat as LabelFormat;

    const labels: Record<string, string> = {};

    if (format === "v2") {
      // New format: pangolin.public-resources.RESOURCE_ID.*
      const prefix = `pangolin.public-resources.${resourceId}`;
      labels[`${prefix}.name`] = name;
      labels[`${prefix}.full-domain`] = domain;
      labels[`${prefix}.protocol`] = protocol;
      labels[`${prefix}.targets[0].site`] = site;
      labels[`${prefix}.targets[0].hostname`] = host;
      labels[`${prefix}.targets[0].method`] = protocol;
      labels[`${prefix}.targets[0].port`] = String(port);

      if (ssoEnabled) {
        labels[`${prefix}.auth.sso-enabled`] = "true";
        if (ssoRoles) {
          // Parse comma-separated roles
          const roles = ssoRoles.split(",").map((r) => r.trim());
          roles.forEach((role, i) => {
            labels[`${prefix}.auth.sso-roles[${i}]`] = role;
          });
        }
      }
    } else {
      // Legacy format: pangolin.resource.*
      labels["pangolin.enabled"] = "true";
      labels["pangolin.resource.name"] = name;
      labels["pangolin.resource.domain"] = domain;
      labels["pangolin.resource.protocol"] = protocol;
      labels["pangolin.resource.port"] = String(port);
      labels["pangolin.resource.site"] = site;
      labels["pangolin.resource.hostname"] = host;

      if (ssoEnabled) {
        labels["pangolin.resource.sso.enabled"] = "true";
        labels["pangolin.resource.sso.roles"] = ssoRoles;
      }
    }

    return JSON.stringify(labels, null, 2);
  }

  /**
   * Generate complete pangolin.yaml content
   */
  @func()
  generateYaml(resourcesJson: string): string {
    const resources: ResourceConfig[] = JSON.parse(resourcesJson);
    const yamlLines: string[] = [
      "# =============================================================================",
      "# PANGOLIN BLUEPRINT",
      "# =============================================================================",
      `# Generated for domain: ${this.baseDomain}`,
      "# =============================================================================",
      "",
      "public-resources:",
    ];

    for (const resource of resources) {
      const site = resource.siteName || this.defaultSite;
      const host = resource.hostname || resource.resourceId;
      const protocol = resource.protocol || "http";

      yamlLines.push(`  # ---------------------------------------------------------------------------`);
      yamlLines.push(`  # ${resource.name}`);
      yamlLines.push(`  # ---------------------------------------------------------------------------`);
      yamlLines.push(`  ${resource.resourceId}:`);
      yamlLines.push(`    name: "${resource.name}"`);
      yamlLines.push(`    full-domain: "${resource.domain}"`);
      yamlLines.push(`    protocol: "${protocol}"`);

      if (resource.auth?.ssoEnabled) {
        yamlLines.push(`    auth:`);
        yamlLines.push(`      sso-enabled: true`);
        if (resource.auth.ssoRoles && resource.auth.ssoRoles.length > 0) {
          yamlLines.push(`      sso-roles:`);
          for (const role of resource.auth.ssoRoles) {
            yamlLines.push(`        - ${role}`);
          }
        }
      }

      yamlLines.push(`    targets:`);
      yamlLines.push(`      - site: "${site}"`);
      yamlLines.push(`        hostname: "${host}"`);
      yamlLines.push(`        method: "${protocol}"`);
      yamlLines.push(`        port: ${resource.port}`);
      yamlLines.push("");
    }

    return yamlLines.join("\n");
  }

  /**
   * Generate Docker Compose labels section
   */
  @func()
  generateComposeLabels(
    resourceId: string,
    name: string,
    subdomain: string,
    port: number,
    protocol: string = "http",
    siteName?: string,
    hostname?: string,
    ssoEnabled: boolean = false,
    ssoRoles: string = ""
  ): string {
    const labelsJson = this.generate(
      resourceId,
      name,
      subdomain,
      port,
      protocol,
      siteName,
      hostname,
      ssoEnabled,
      ssoRoles
    );

    const labels = JSON.parse(labelsJson);
    const yamlLines: string[] = ["    labels:"];

    for (const [key, value] of Object.entries(labels)) {
      yamlLines.push(`      - "${key}=${value}"`);
    }

    return yamlLines.join("\n");
  }

  /**
   * Generate multiple resources for common infrastructure services
   */
  @func()
  generateInfrastructureBlueprint(
    servicesJson: string = "[]"
  ): string {
    // Default infrastructure services if none provided
    let services = JSON.parse(servicesJson) as ResourceConfig[];

    if (services.length === 0) {
      services = [
        {
          resourceId: "komodo",
          name: "Komodo",
          domain: `komodo.${this.baseDomain}`,
          port: 9120,
          protocol: "http",
        },
        {
          resourceId: "forgejo",
          name: "Forgejo",
          domain: `git.${this.baseDomain}`,
          port: 3000,
          protocol: "http",
        },
        {
          resourceId: "op-connect",
          name: "1Password Connect",
          domain: `op.${this.baseDomain}`,
          port: 8080,
          protocol: "http",
          auth: { ssoEnabled: true, ssoRoles: ["Admin"] },
        },
        {
          resourceId: "pocketid",
          name: "Pocket ID",
          domain: `auth.${this.baseDomain}`,
          port: 1411,
          protocol: "http",
        },
        {
          resourceId: "pangolin",
          name: "Pangolin Dashboard",
          domain: `pangolin.${this.baseDomain}`,
          port: 3001,
          protocol: "http",
        },
      ];
    }

    return this.generateYaml(JSON.stringify(services));
  }

  /**
   * Create a new domain configuration
   */
  @func()
  withDomain(baseDomain: string): PangolinLabels {
    return new PangolinLabels(baseDomain, this.defaultSite, this.labelFormat);
  }

  /**
   * Set the default site for targets
   */
  @func()
  withSite(siteName: string): PangolinLabels {
    return new PangolinLabels(this.baseDomain, siteName, this.labelFormat);
  }

  /**
   * Set the label format (v1 or v2)
   */
  @func()
  withFormat(format: string): PangolinLabels {
    return new PangolinLabels(this.baseDomain, this.defaultSite, format);
  }

  /**
   * Validate a pangolin.yaml file
   */
  @func()
  validate(yamlContent: string): string {
    const errors: string[] = [];
    const warnings: string[] = [];

    // Basic validation
    if (!yamlContent.includes("public-resources:")) {
      errors.push("Missing 'public-resources:' section");
    }

    // Check for required fields
    const requiredFields = ["name:", "full-domain:", "targets:"];
    for (const field of requiredFields) {
      if (!yamlContent.includes(field)) {
        warnings.push(`Missing field: ${field}`);
      }
    }

    // Check for common issues
    if (yamlContent.includes("pangolin.resource.")) {
      warnings.push(
        "Using legacy label format (pangolin.resource.*). Consider migrating to v2 format."
      );
    }

    return JSON.stringify(
      {
        valid: errors.length === 0,
        errors,
        warnings,
      },
      null,
      2
    );
  }
}
