/**
 * Shared TypeScript Types for Dagger Modules
 *
 * Common interfaces used across Pangolin deployment, browser automation,
 * and infrastructure orchestration modules.
 */

// =============================================================================
// Stage Execution Results
// =============================================================================

export interface StageResult {
  stage: string;
  success: boolean;
  output: string;
  skipped?: boolean;
  error?: string;
  duration?: number;
  humanApproved?: boolean;
}

export interface DeploymentResult {
  id: string;
  success: boolean;
  stages: StageResult[];
  totalDuration: number;
  startedAt: string;
  completedAt: string;
}

export interface VerificationResult {
  healthy: boolean;
  services: ServiceHealth[];
  ssl?: SSLHealth;
  crowdsec?: CrowdSecHealth;
  tunnels?: TunnelHealth[];
  timestamp: string;
}

// =============================================================================
// Health Check Types
// =============================================================================

export interface ServiceHealth {
  name: string;
  url: string;
  healthy: boolean;
  statusCode?: number;
  responseTime?: number;
  error?: string;
}

export interface SSLHealth {
  domain: string;
  valid: boolean;
  issuer?: string;
  expiresAt?: string;
  daysUntilExpiry?: number;
}

export interface CrowdSecHealth {
  enabled: boolean;
  bouncerRegistered: boolean;
  decisionsCount?: number;
  alertsCount?: number;
}

export interface TunnelHealth {
  name: string;
  connected: boolean;
  lastSeen?: string;
  subnet?: string;
}

// =============================================================================
// Configuration Types
// =============================================================================

export interface DeploymentConfig {
  /** Target server SSH address (user@host) */
  targetHost: string;
  /** Path to SSH private key */
  sshKeyPath?: string;

  /** Primary domain for services */
  domain: string;
  /** Organization ID in Pangolin */
  orgId?: string;
  /** Organization name */
  orgName?: string;

  /** 1Password Connect host URL */
  opConnectHost: string;
  /** Path to 1Password credentials JSON */
  opCredentialsPath?: string;

  /** Browser automation backend */
  browserBackend: "stagehand" | "skyvern" | "browserbase" | "human";
  /** Browser automation server URL */
  browserServerUrl?: string;

  /** Sites to create in Pangolin */
  sites: SiteConfig[];

  /** Application stacks to deploy */
  stacks: string[];

  /** Enable dry-run mode */
  dryRun: boolean;
  /** Skip browser automation steps */
  skipBrowserSteps: boolean;
  /** Timeout for human approval (minutes) */
  humanApprovalTimeout: number;
}

export interface SiteConfig {
  /** Site name */
  name: string;
  /** Site type (newt, olm, wireguard) */
  type: "newt" | "olm" | "wireguard";
  /** Target server for this site */
  server?: string;
  /** Apply blueprint after creation */
  blueprint?: string;
}

// =============================================================================
// OLM Client Types
// =============================================================================

export interface OLMClientConfig {
  /** Client name (e.g., "arm1-oci-olm") */
  name: string;
  /** Server where OLM agent deploys */
  server: string;
  /** Newt site names this OLM can access (resolved to IDs) */
  siteNames: string[];
  /** Optional TCP resources blueprint to apply */
  blueprint?: string;
}

export interface OLMClientResult {
  /** Client ID in Pangolin */
  id: number;
  /** Client display name */
  name: string;
  /** OLM identifier for authentication */
  olmId: string;
  /** OLM secret (only returned on creation) */
  secret: string;
  /** Assigned subnet for this client */
  subnet: string;
  /** Site IDs this client can access */
  siteIds: number[];
}

// =============================================================================
// Pangolin API Types
// =============================================================================

export interface OrgResult {
  id: string;
  name: string;
  subnet: string;
}

export interface SiteResult {
  id: number;
  name: string;
  niceId: string;
  type: string;
  newtId?: string;
  newtSecret?: string;
  subnet: string;
  exitNodeId?: number;
}

export interface SiteDefaults {
  suggestedSubnet: string;
  exitNodeId: number;
  blockSize: string;
}

export interface ApiKey {
  id: string;
  name: string;
  key: string;
  createdAt: string;
}

// =============================================================================
// OAuth & Authentication Types
// =============================================================================

export interface OAuthCredentials {
  clientId: string;
  clientSecret: string;
}

export interface HumanApprovalRequest {
  task: string;
  instructions: string[];
  timeout: number;
  url?: string;
  awakeableId?: string;
}

export interface HumanApprovalResult {
  approved: boolean;
  completedBy?: string;
  completedAt?: string;
  notes?: string;
}

// =============================================================================
// Browser Automation Types
// =============================================================================

export interface BrowserAction {
  action: string;
  selector?: string;
  value?: string;
}

export interface BrowserExtractResult {
  success: boolean;
  data: Record<string, unknown>;
  error?: string;
}

export interface FormField {
  name: string;
  value: string;
  type?: "text" | "password" | "select" | "checkbox";
}

// =============================================================================
// Deployment State (for resume capability)
// =============================================================================

export interface DeploymentState {
  id: string;
  config: DeploymentConfig;
  currentStage: number;
  completedStages: StageResult[];
  failedStage?: StageResult;
  secrets: string[];
  resources: string[];
  startedAt: string;
  updatedAt: string;
}

// =============================================================================
// Constants
// =============================================================================

export const STAGES = [
  "initServer",
  "deployOpConnect",
  "deployPangolinCore",
  "setupPocketIdAdmin",
  "createOAuthClient",
  "generateCrowdSecKey",
  "deployKomodo",
  "deployForgejo",
  "createPangolinSites",
  "deployAppStacks",
] as const;

export type StageName = typeof STAGES[number];

// =============================================================================
// Auth Stack Types
// =============================================================================

export interface AuthStackConfig {
  /** Komodo API URL */
  komodoUrl: string;
  /** PocketID OIDC URL */
  pocketIdUrl: string;
  /** 1Password Connect host */
  opConnectHost: string;
  /** TinyAuth forward auth URL */
  tinyauthUrl: string;
}

export interface AuthServiceConfig {
  /** Service display name */
  name: string;
  /** Service domain */
  domain: string;
  /** Service port */
  port: number;
  /** Middleware to apply (tinyauth, rate-limit-api, etc.) */
  middleware: string;
}

export interface AuthStackDefinition {
  /** Stack name in Komodo */
  stackName: string;
  /** Services included in the stack */
  services: AuthServiceConfig[];
  /** 1Password vault for secrets */
  secretsVault: string;
  /** 1Password item name for this stack */
  secretsItem: string;
}

export interface AuthStage {
  /** Stage name */
  name: string;
  /** Stage status */
  status: "pending" | "in_progress" | "completed" | "failed" | "skipped";
  /** Stage start time */
  startedAt?: string;
  /** Stage completion time */
  completedAt?: string;
  /** Stage output */
  output?: string;
  /** Error message if failed */
  error?: string;
}

export interface AuthDeploymentResult {
  /** Overall success */
  success: boolean;
  /** Stack name */
  stackName: string;
  /** Stages executed */
  stages: AuthStage[];
  /** Deployment start time */
  startedAt: string;
  /** Deployment completion time */
  completedAt: string;
  /** Whether this was a dry run */
  dryRun: boolean;
  /** Error message if failed */
  error?: string;
}

// =============================================================================
// Dev Environment Types
// =============================================================================

export interface DevEnvironmentConfig {
  /** Target domain for all services */
  domain: string;
  /** 1Password vault for credentials */
  vault: string;
  /** 1Password Connect host URL */
  opConnectHost: string;
  /** Browser automation backend */
  browserBackend: "stagehand" | "browserbase" | "human";
  /** Browser server URL (for stagehand/browserbase) */
  browserServerUrl?: string;
}

export interface OidcClientConfig {
  /** Client name displayed in PocketID */
  name: string;
  /** OAuth2 redirect URIs */
  redirectUris: string[];
  /** OAuth2 scopes */
  scopes: string[];
  /** Grant types (authorization_code, refresh_token) */
  grantTypes: string[];
  /** Response types (code) */
  responseTypes: string[];
}

export interface ForgejoAuthSource {
  /** Provider name (displayed in login UI) */
  name: string;
  /** Provider key (used in URL, e.g., "pocketid") */
  providerKey: string;
  /** OIDC configuration */
  oidc: {
    clientId: string;
    authUrl: string;
    tokenUrl: string;
    userinfoUrl: string;
    scopes: string[];
  };
  /** Auto-create users on first login */
  autoCreateUsers: boolean;
  /** Update user info on each login */
  updateUserInfo: boolean;
}

export interface DevEnvironmentStage {
  /** Stage name */
  name: DevEnvironmentStageName;
  /** Stage status */
  status: "pending" | "in_progress" | "completed" | "failed" | "skipped";
  /** Whether human approval was required */
  humanApprovalRequired?: boolean;
  /** Stage start time */
  startedAt?: string;
  /** Stage completion time */
  completedAt?: string;
  /** Stage output */
  output?: string;
  /** Error message if failed */
  error?: string;
}

export interface DevEnvironmentCredentials {
  /** PocketID admin setup status */
  pocketIdSetup: boolean;
  /** PocketID API token reference in 1Password */
  pocketIdToken?: {
    stored: boolean;
    opReference?: string;
  };
  /** TinyAuth OAuth client */
  tinyauthClient?: {
    clientId: string;
    stored: boolean;
    opReference?: string;
  };
  /** Forgejo OAuth client */
  forgejoClient?: {
    clientId: string;
    stored: boolean;
    opReference?: string;
    authSourceCreated: boolean;
  };
  /** Komodo OAuth client */
  komodoClient?: {
    clientId: string;
    stored: boolean;
    opReference?: string;
  };
}

export interface DevEnvironmentVerification {
  /** OIDC discovery endpoint accessible */
  oidcDiscovery: boolean;
  /** Forgejo redirects to PocketID */
  forgejoRedirect: boolean;
  /** TinyAuth health check passes */
  tinyauthHealth: boolean;
}

export interface DevEnvironmentBootstrapResult {
  /** Overall success */
  success: boolean;
  /** Target domain */
  domain: string;
  /** Stages executed */
  stages: DevEnvironmentStage[];
  /** Credentials created/stored */
  credentials: DevEnvironmentCredentials;
  /** Verification results */
  verification: DevEnvironmentVerification;
  /** Deployment start time */
  startedAt: string;
  /** Deployment completion time */
  completedAt: string;
  /** Whether this was a dry run */
  dryRun: boolean;
  /** Error message if failed */
  error?: string;
}

export const DEV_ENVIRONMENT_STAGES = [
  "pre-flight",
  "pocket-id-check",
  "pocket-id-setup",
  "create-tinyauth-client",
  "create-forgejo-client",
  "create-komodo-client",
  "create-litellm-client",
  "store-credentials",
  "configure-forgejo-auth",
  "verify-oidc-flow",
] as const;

export type DevEnvironmentStageName = typeof DEV_ENVIRONMENT_STAGES[number];

/**
 * Generate OIDC client configurations for a domain
 */
export const getOidcClients = (domain: string): Record<string, OidcClientConfig> => ({
  tinyauth: {
    name: "TinyAuth",
    redirectUris: [`https://tinyauth.${domain}/api/oauth/callback/pocketid`],
    scopes: ["openid", "email", "profile", "groups"],
    grantTypes: ["authorization_code", "refresh_token"],
    responseTypes: ["code"],
  },
  forgejo: {
    name: "Forgejo",
    redirectUris: [`https://git.${domain}/user/oauth2/pocketid/callback`],
    scopes: ["openid", "email", "profile"],
    grantTypes: ["authorization_code", "refresh_token"],
    responseTypes: ["code"],
  },
  komodo: {
    name: "Komodo",
    redirectUris: [`https://komodo.${domain}/auth/oidc/callback`],
    scopes: ["openid", "email", "profile"],
    grantTypes: ["authorization_code", "refresh_token"],
    responseTypes: ["code"],
  },
  litellm: {
    name: "LiteLLM",
    redirectUris: [`https://llm.${domain}/sso/callback`],
    scopes: ["openid", "email", "profile", "groups"],
    grantTypes: ["authorization_code", "refresh_token"],
    responseTypes: ["code"],
  },
});

/**
 * Generate PocketID OIDC endpoints for a domain
 */
export const getPocketIdEndpoints = (domain: string) => ({
  base: `https://auth.${domain}`,
  authUrl: `https://auth.${domain}/authorize`,
  tokenUrl: `https://auth.${domain}/api/oidc/token`,
  userinfoUrl: `https://auth.${domain}/api/oidc/userinfo`,
  discoveryUrl: `https://auth.${domain}/.well-known/openid-configuration`,
});
