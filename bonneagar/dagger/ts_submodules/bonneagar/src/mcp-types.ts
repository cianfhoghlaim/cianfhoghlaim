/**
 * MCP Server Types and Interfaces
 *
 * TypeScript definitions for MCP (Model Context Protocol) server configuration,
 * discovery, testing, and deployment workflows.
 */

// =============================================================================
// MCP Server Configuration Types
// =============================================================================

export interface McpServerConfig {
  /** Unique server identifier */
  name: string;
  /** Server description */
  description?: string;
  /** Transport type */
  transport: "stdio" | "http" | "sse";
  /** Server command (for stdio) */
  command?: string;
  /** Command arguments (for stdio) */
  args?: string[];
  /** Working directory */
  cwd?: string;
  /** URL (for http/sse) */
  url?: string;
  /** HTTP headers */
  headers?: Record<string, string>;
  /** Environment variables */
  env?: Record<string, string>;
  /** Required secrets (1Password references) */
  secrets?: SecretMapping[];
  /** Server capabilities */
  capabilities?: McpCapabilities;
}

export interface McpCapabilities {
  /** Supported tools */
  tools?: boolean;
  /** Supported resources */
  resources?: boolean;
  /** Supported prompts */
  prompts?: boolean;
  /** Sampling support */
  sampling?: boolean;
}

export interface SecretMapping {
  /** Environment variable name */
  envVar: string;
  /** 1Password reference (op://vault/item/field) */
  opReference: string;
  /** Is this secret required? */
  required: boolean;
  /** Description of what this secret is for */
  description?: string;
}

// =============================================================================
// MCP Server Discovery Types
// =============================================================================

export interface McpServerInfo {
  /** GitHub repository URL */
  repoUrl: string;
  /** Server name (from package.json or README) */
  name: string;
  /** Server description */
  description: string;
  /** Package manager (npm, uvx, etc.) */
  packageManager: "npm" | "npx" | "uvx" | "uv" | "pip" | "docker" | "binary";
  /** Package name */
  packageName: string;
  /** Latest version */
  version?: string;
  /** Required environment variables */
  envVars: EnvVarSpec[];
  /** Provided tools */
  tools: ToolSpec[];
  /** Documentation URL */
  docsUrl?: string;
  /** License */
  license?: string;
  /** Star count */
  stars?: number;
  /** Last updated */
  lastUpdated?: string;
}

export interface EnvVarSpec {
  /** Variable name */
  name: string;
  /** Description */
  description: string;
  /** Is this required? */
  required: boolean;
  /** Example value */
  example?: string;
  /** Is this a secret? */
  isSecret: boolean;
}

export interface ToolSpec {
  /** Tool name */
  name: string;
  /** Tool description */
  description: string;
  /** Input schema (JSON Schema) */
  inputSchema?: Record<string, unknown>;
}

// =============================================================================
// GitHub Analysis Types
// =============================================================================

export interface McpAnalysis {
  /** Repository information */
  repo: RepoInfo;
  /** Detected MCP server specification */
  spec: McpServerSpec;
  /** Setup complexity score (1-5) */
  complexity: number;
  /** Compatibility with our stack */
  compatibility: StackCompatibility;
  /** Recommended deployment method */
  deploymentMethod: DeploymentMethod;
  /** Potential issues or concerns */
  concerns: string[];
  /** Overall recommendation */
  recommendation: "deploy" | "test" | "skip" | "manual";
}

export interface RepoInfo {
  /** Full repo name (owner/repo) */
  fullName: string;
  /** Repository URL */
  url: string;
  /** Default branch */
  defaultBranch: string;
  /** Primary language */
  language: string;
  /** Star count */
  stars: number;
  /** Last commit date */
  lastCommit: string;
  /** README content (summarized) */
  readmeSummary?: string;
}

export interface McpServerSpec {
  /** Transport type */
  transport: "stdio" | "http" | "sse";
  /** Installation command */
  installCommand: string;
  /** Runtime command */
  runCommand: string;
  /** Command arguments */
  args: string[];
  /** Required environment variables */
  envVars: EnvVarSpec[];
  /** Protocol version */
  protocolVersion?: string;
  /** Dependencies */
  dependencies?: string[];
}

export interface StackCompatibility {
  /** Works with Claude Code */
  claudeCode: boolean;
  /** Works with Roo (VS Code) */
  roo: boolean;
  /** Works with OpenCode */
  openCode: boolean;
  /** Can be deployed as container */
  containerizable: boolean;
  /** Works with 1Password secrets */
  supportsOpSecrets: boolean;
}

export type DeploymentMethod =
  | "local" // Run locally with op run
  | "container" // Deploy as container with Locket sidecar
  | "cloud" // Use hosted version
  | "hybrid"; // Multiple deployment options

// =============================================================================
// Secret Migration Types
// =============================================================================

export interface HardcodedSecret {
  /** File path where secret was found */
  filePath: string;
  /** Line number */
  lineNumber: number;
  /** JSON path to the secret */
  jsonPath: string;
  /** The secret value (will be redacted in output) */
  value: string;
  /** Suggested environment variable name */
  suggestedEnvVar: string;
  /** Detected secret type */
  secretType: "api_key" | "token" | "password" | "credentials" | "unknown";
  /** Associated MCP server name */
  serverName?: string;
}

export interface MigrationPlan {
  /** Files to modify */
  files: FileMigration[];
  /** 1Password items to create */
  opItems: OpItemSpec[];
  /** Environment file content */
  envFileContent: string;
  /** Warnings or notes */
  warnings: string[];
}

export interface FileMigration {
  /** File path */
  filePath: string;
  /** Secrets to migrate in this file */
  secrets: SecretReplacement[];
}

export interface SecretReplacement {
  /** JSON path to replace */
  jsonPath: string;
  /** Current value (redacted) */
  oldValue: string;
  /** New value (env var reference) */
  newValue: string;
  /** Environment variable name */
  envVar: string;
}

export interface OpItemSpec {
  /** Vault name */
  vault: string;
  /** Item title */
  title: string;
  /** Item category */
  category: "API Credential" | "Password" | "Login";
  /** Fields to create */
  fields: OpFieldSpec[];
  /** Tags */
  tags?: string[];
}

export interface OpFieldSpec {
  /** Field label */
  label: string;
  /** Field value */
  value: string;
  /** Field type */
  type: "STRING" | "CONCEALED" | "URL";
}

// =============================================================================
// Protocol Testing Types
// =============================================================================

export interface ProtocolTestResult {
  /** Server name */
  serverName: string;
  /** Test passed */
  success: boolean;
  /** Protocol version detected */
  protocolVersion?: string;
  /** Capabilities detected */
  capabilities?: McpCapabilities;
  /** Tools discovered */
  tools?: ToolSpec[];
  /** Resources discovered */
  resources?: ResourceSpec[];
  /** Errors encountered */
  errors: string[];
  /** Latency measurements */
  latency: LatencyMetrics;
}

export interface ResourceSpec {
  /** Resource URI */
  uri: string;
  /** Resource name */
  name: string;
  /** Resource description */
  description?: string;
  /** MIME type */
  mimeType?: string;
}

export interface LatencyMetrics {
  /** Initialize handshake (ms) */
  initializeMs: number;
  /** Tools/list (ms) */
  toolsListMs?: number;
  /** Resources/list (ms) */
  resourcesListMs?: number;
  /** Sample tool call (ms) */
  sampleToolCallMs?: number;
}

// =============================================================================
// Deployment Types
// =============================================================================

export interface DeployResult {
  /** Deployment ID */
  id: string;
  /** Server name */
  serverName: string;
  /** Deployment successful */
  success: boolean;
  /** Deployment method used */
  method: DeploymentMethod;
  /** Stack name (if containerized) */
  stackName?: string;
  /** Configuration file path */
  configPath?: string;
  /** Secrets created */
  secretsCreated: string[];
  /** Verification result */
  verification?: ProtocolTestResult;
  /** Errors */
  errors: string[];
  /** Next steps */
  nextSteps: string[];
}

export interface PipelineResult {
  /** Pipeline ID */
  id: string;
  /** Server name */
  serverName: string;
  /** Overall success */
  success: boolean;
  /** Stages completed */
  stages: PipelineStage[];
  /** Total duration (ms) */
  durationMs: number;
  /** Final configuration */
  finalConfig?: McpServerConfig;
}

export interface PipelineStage {
  /** Stage name */
  name: "research" | "analyze" | "secrets" | "test" | "deploy" | "configure";
  /** Stage success */
  success: boolean;
  /** Stage output */
  output: string;
  /** Duration (ms) */
  durationMs: number;
  /** Errors */
  errors?: string[];
}

// =============================================================================
// Locket Template Types
// =============================================================================

export interface LocketTemplate {
  /** Service name */
  service: string;
  /** Secrets to inject */
  secrets: LocketSecret[];
  /** Output file path */
  outputPath: string;
}

export interface LocketSecret {
  /** Environment variable name */
  envVar: string;
  /** 1Password reference */
  opReference: string;
}
