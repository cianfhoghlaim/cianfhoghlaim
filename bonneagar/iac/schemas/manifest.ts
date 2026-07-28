// bonneagar/iac/schemas/manifest.ts
// Zod schemas for the canonical Cianfhoghlaim 6-file stack manifest.
// Used by cianfhoghlaim stack lint|plan|deploy|verify|rollback.

import { z } from "zod";

// -----------------------------------------------------------------------------
// Host topology
// -----------------------------------------------------------------------------

export const HostIdSchema = z.enum(["arm1-oci", "bunchloch"]);
export type HostId = z.infer<typeof HostIdSchema>;

// -----------------------------------------------------------------------------
// Secret reference
// -----------------------------------------------------------------------------

/**
 * Canonical Locket template:
 *   {{ infisical:///key?env=dev-baile&path=/<service> }}
 *
 * Legacy plain Infisical URI:
 *   infisical://dev-baile/<service>/<key>
 *
 * Both forms resolve to the same Infisical item. The canonical form
 * is preferred; the legacy form is accepted with a
 * legacy-secret-syntax warning.
 */
export const SecretReferenceSchema = z.object({
  name: z.string().min(1),
  raw: z.string().min(1),
  grammar: z.enum(["locket-template", "infisical-uri"]),
  key: z.string().min(1),
  path: z.string().min(1).startsWith("/"),
  env: z.string().min(1).default("dev-baile"),
  legacyWarning: z.boolean().default(false),
  line: z.number().int().positive().optional(),
});
export type SecretReference = z.infer<typeof SecretReferenceSchema>;

// -----------------------------------------------------------------------------
// Environment variable
// -----------------------------------------------------------------------------

export const EnvironmentVariableSchema = z.object({
  name: z.string().min(1),
  required: z.boolean().default(false),
  sensitive: z.boolean().default(false),
  defaultValue: z.string().optional(),
  source: z.enum([
    "compose",
    "compose-default",
    "secret",
    "komodo",
    "generated",
    "sidecar",
  ]),
  infisicalPath: z.string().optional(),
  services: z.array(z.string()).default([]),
  validation: z
    .enum(["url", "hostname", "port", "boolean", "integer", "secret"])
    .optional(),
  line: z.number().int().positive().optional(),
});
export type EnvironmentVariable = z.infer<typeof EnvironmentVariableSchema>;

// -----------------------------------------------------------------------------
// Compose service
// -----------------------------------------------------------------------------

export const ComposeServiceSchema = z.object({
  name: z.string().min(1),
  image: z.string().optional(),
  restart: z.string().optional(),
  healthcheck: z
    .object({
      test: z.array(z.string()),
      interval: z.string().optional(),
      timeout: z.string().optional(),
      retries: z.number().int().optional(),
      startPeriod: z.string().optional(),
    })
    .optional(),
  dependsOn: z.array(z.string()).default([]),
  environment: z.array(EnvironmentVariableSchema).default([]),
  networks: z.array(z.string()).default([]),
  volumes: z.array(z.string()).default([]),
  ports: z.array(z.string()).default([]),
  containerName: z.string().optional(),
});
export type ComposeService = z.infer<typeof ComposeServiceSchema>;

// -----------------------------------------------------------------------------
// Pangolin resource (Pangolin EE root blueprint shape)
// -----------------------------------------------------------------------------

export const PangolinResourceSchema = z
  .object({
    slug: z.string().min(1),
    visibility: z.enum(["private", "public"]),
    name: z.string().min(1),
    mode: z.enum(["http", "host", "cidr"]),
    sites: z.array(HostIdSchema).default([]),
    destination: z.string().optional(),
    destinationPort: z.number().int().positive().optional(),
    fullDomain: z.string().optional(),
    ssl: z.boolean().default(true),
    scheme: z.enum(["http", "https"]).default("https"),
    enabled: z.boolean().default(true),
    roles: z.array(z.string()).default([]),
    targets: z
      .array(
        z.object({
          site: HostIdSchema,
          hostname: z.string().min(1),
          port: z.number().int().positive(),
          method: z.enum(["http", "https"]).default("http"),
          healthcheck: z
            .object({
              hostname: z.string().min(1),
              port: z.number().int().positive(),
              path: z.string().min(1).startsWith("/"),
            })
            .optional(),
        })
      )
      .default([]),
  })
  .superRefine((value, ctx) => {
    if (value.visibility === "private" && value.fullDomain === undefined) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: "Private resources must declare fullDomain",
        path: ["fullDomain"],
      });
    }
    if (value.visibility === "private" && value.roles.length === 0) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: "Private resources must declare at least one role",
        path: ["roles"],
      });
    }
    if (value.visibility === "public" && value.targets.length === 0) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: "Public resources must declare at least one target",
        path: ["targets"],
      });
    }
  });
export type PangolinResource = z.infer<typeof PangolinResourceSchema>;

// -----------------------------------------------------------------------------
// Komodo resource
// -----------------------------------------------------------------------------

export const KomodoResourceSchema = z.object({
  name: z.string().min(1),
  server: HostIdSchema,
  runDirectory: z.string().min(1),
  filePaths: z.array(z.string()).default(["compose.yaml"]),
  repo: z.string().optional(),
  branch: z.string().default("main"),
  environment: z.record(z.string(), z.string()).default({}),
  after: z.array(z.string()).default([]),
  deploy: z.boolean().default(true),
});
export type KomodoResource = z.infer<typeof KomodoResourceSchema>;

// -----------------------------------------------------------------------------
// Locket sidecar
// -----------------------------------------------------------------------------

export const LOCKET_MODES = ["watch", "park", "one-shot"] as const;
export type LocketMode = (typeof LOCKET_MODES)[number];

export const LocketSidecarSchema = z.object({
  image: z.string().min(1),
  user: z.string().default("65532:65532"),
  securityOpt: z.array(z.string()).default(["no-new-privileges:true"]),
  capDrop: z.array(z.string()).default(["ALL"]),
  tmpfsMode: z.string().default("0700"),
  mode: z.union([z.literal("watch"), z.literal("park"), z.literal("one-shot")]),
  environment: z.record(z.string(), z.string()).default({}),
  healthcheck: z
    .object({
      test: z.array(z.string()),
      interval: z.string().default("10s"),
      timeout: z.string().default("5s"),
      retries: z.number().int().default(3),
      startPeriod: z.string().default("5s"),
    })
    .optional(),
  isCianfhoghlaimOwned: z.boolean().default(false),
});
export type LocketSidecar = z.infer<typeof LocketSidecarSchema>;

// -----------------------------------------------------------------------------
// Stack manifest (the canonical 6-file contract)
// -----------------------------------------------------------------------------

export const StackManifestSchema = z.object({
  name: z.string().min(1),
  host: HostIdSchema,
  tier: z.enum(["control-plane", "storage", "workload"]),
  composeFiles: z.array(z.string()).default(["compose.yaml"]),
  services: z.array(ComposeServiceSchema).default([]),
  environment: z.array(EnvironmentVariableSchema).default([]),
  secrets: z.array(SecretReferenceSchema).default([]),
  pangolin: z.array(PangolinResourceSchema).default([]),
  komodo: KomodoResourceSchema.optional(),
  locket: LocketSidecarSchema.optional(),
  dependencies: z.array(z.string()).default([]),
  manifestVersion: z.literal("1"),
});
export type StackManifest = z.infer<typeof StackManifestSchema>;

// -----------------------------------------------------------------------------
// Deployment receipt
// -----------------------------------------------------------------------------

export const DeploymentReceiptSchema = z.object({
  receiptVersion: z.literal("1"),
  stack: z.string().min(1),
  host: HostIdSchema,
  gitSha: z.string().min(1),
  manifestHash: z.string().min(1),
  composeHash: z.string().min(1),
  targetHost: HostIdSchema,
  imageDigests: z.record(z.string(), z.string()).default({}),
  komodoDeploymentId: z.string().optional(),
  pangolinResourceIds: z.array(z.string()).default([]),
  startedAt: z.string().min(1),
  completedAt: z.string().min(1),
  status: z.enum(["success", "failed", "rolled_back"]),
  checks: z.object({
    composeConfig: z.enum(["passed", "failed"]),
    secretReferences: z.enum(["passed", "failed"]),
    locket: z.enum(["healthy", "failed", "skipped"]),
    services: z.enum(["healthy", "failed"]),
    routes: z.enum(["healthy", "failed", "skipped"]),
  }),
  diagnostics: z
    .array(
      z.object({
        code: z.string().min(1),
        message: z.string().min(1),
        file: z.string().optional(),
        line: z.number().int().positive().optional(),
      })
    )
    .default([]),
});
export type DeploymentReceipt = z.infer<typeof DeploymentReceiptSchema>;