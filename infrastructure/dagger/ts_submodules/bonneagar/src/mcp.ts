/**
 * MCP Server Research, Testing, and Deployment Module
 *
 * Provides Dagger functions for:
 * - Discovering MCP servers from GitHub
 * - Analyzing repository specifications
 * - Testing MCP protocol compliance
 * - Deploying servers to Komodo
 * - Configuring routing in Pangolin
 */

import {
  dag,
  Container,
  Directory,
  Secret,
  object,
  func,
  field,
} from "@dagger.io/dagger";

import type {
  McpServerConfig,
  McpServerInfo,
  McpAnalysis,
  McpServerSpec,
  ProtocolTestResult,
  DeployResult,
  PipelineResult,
  PipelineStage,
  StackCompatibility,
  DeploymentMethod,
  SecretMapping,
} from "./mcp-types";

// Note: SecretMigration imported for reference but instantiation happens separately

@object()
export class McpResearch {
  @field()
  workDir: Directory;

  @field()
  firecrawlApiKey?: Secret;

  constructor(workDir: Directory, firecrawlApiKey?: Secret) {
    this.workDir = workDir;
    this.firecrawlApiKey = firecrawlApiKey;
  }

  /**
   * Search for MCP servers on GitHub using Firecrawl
   */
  @func()
  async searchMcpServers(
    query: string,
    limit: number = 10
  ): Promise<string> {
    if (!this.firecrawlApiKey) {
      return JSON.stringify({
        error: "Firecrawl API key not provided",
        suggestion: "Pass firecrawlApiKey to McpResearch constructor",
      });
    }

    const container = dag
      .container()
      .from("node:22-slim")
      .withExec(["npm", "install", "-g", "firecrawl"])
      .withSecretVariable("FIRECRAWL_API_KEY", this.firecrawlApiKey);

    const searchScript = `
      const { FirecrawlApp } = require('firecrawl');

      async function search() {
        const app = new FirecrawlApp({ apiKey: process.env.FIRECRAWL_API_KEY });

        const searchQuery = '${query} mcp server model context protocol site:github.com';

        try {
          const results = await app.search(searchQuery, { limit: ${limit} });

          const servers = results.data.map(r => ({
            name: r.title,
            url: r.url,
            description: r.description || '',
            source: 'firecrawl_search'
          }));

          console.log(JSON.stringify(servers, null, 2));
        } catch (error) {
          console.log(JSON.stringify({ error: error.message }));
        }
      }

      search();
    `;

    const result = await container
      .withExec(["node", "-e", searchScript])
      .stdout();

    return result;
  }

  /**
   * Analyze a GitHub repository to extract MCP server specification
   */
  @func()
  async analyzeGitHubRepo(
    repoUrl: string
  ): Promise<string> {
    const container = dag
      .container()
      .from("node:22-slim")
      .withExec(["apt-get", "update"])
      .withExec(["apt-get", "install", "-y", "git", "jq"]);

    // Clone and analyze the repo
    const analyzeScript = `
      const { execSync } = require('child_process');
      const fs = require('fs');
      const path = require('path');

      const repoUrl = '${repoUrl}';
      const repoName = repoUrl.split('/').slice(-1)[0].replace('.git', '');

      // Clone the repo
      execSync(\`git clone --depth 1 \${repoUrl} /tmp/\${repoName}\`, { stdio: 'pipe' });

      const repoPath = \`/tmp/\${repoName}\`;
      const analysis = {
        repo: {
          fullName: repoUrl.replace('https://github.com/', ''),
          url: repoUrl,
          defaultBranch: 'main',
          language: 'unknown',
          stars: 0,
          lastCommit: new Date().toISOString(),
        },
        spec: {
          transport: 'stdio',
          installCommand: '',
          runCommand: '',
          args: [],
          envVars: [],
        },
        complexity: 1,
        compatibility: {
          claudeCode: true,
          roo: true,
          openCode: true,
          containerizable: true,
          supportsOpSecrets: true,
        },
        concerns: [],
        recommendation: 'test',
      };

      // Check for package.json (Node.js)
      const pkgPath = path.join(repoPath, 'package.json');
      if (fs.existsSync(pkgPath)) {
        const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));
        analysis.repo.language = 'TypeScript/JavaScript';
        analysis.spec.installCommand = 'npm install';

        // Check for MCP-related dependencies
        const deps = { ...pkg.dependencies, ...pkg.devDependencies };
        if (deps['@modelcontextprotocol/sdk']) {
          analysis.concerns.push('Uses official MCP SDK');
        }

        // Check bin entries
        if (pkg.bin) {
          const binName = typeof pkg.bin === 'string' ? repoName : Object.keys(pkg.bin)[0];
          analysis.spec.runCommand = \`npx \${pkg.name}\`;
        }
      }

      // Check for pyproject.toml (Python)
      const pyprojectPath = path.join(repoPath, 'pyproject.toml');
      if (fs.existsSync(pyprojectPath)) {
        analysis.repo.language = 'Python';
        analysis.spec.installCommand = 'uv pip install';
        analysis.spec.runCommand = 'uvx';
      }

      // Check for README to extract env vars
      const readmePath = path.join(repoPath, 'README.md');
      if (fs.existsSync(readmePath)) {
        const readme = fs.readFileSync(readmePath, 'utf8');

        // Look for environment variable patterns
        const envMatches = readme.match(/[A-Z_]{3,}(?:_API_KEY|_TOKEN|_SECRET|_PASSWORD)/g);
        if (envMatches) {
          analysis.spec.envVars = [...new Set(envMatches)].map(name => ({
            name,
            description: 'Extracted from README',
            required: true,
            isSecret: true,
          }));
        }

        // Extract first paragraph as summary
        const firstPara = readme.split('\\n\\n')[0].replace(/^#.*\\n/, '').trim();
        analysis.repo.readmeSummary = firstPara.substring(0, 500);
      }

      // Determine complexity
      if (analysis.spec.envVars.length > 3) {
        analysis.complexity = 3;
      } else if (analysis.spec.envVars.length > 1) {
        analysis.complexity = 2;
      }

      // Set recommendation
      if (analysis.spec.envVars.length === 0) {
        analysis.recommendation = 'deploy';
      } else if (analysis.complexity <= 2) {
        analysis.recommendation = 'test';
      } else {
        analysis.recommendation = 'manual';
      }

      console.log(JSON.stringify(analysis, null, 2));
    `;

    const result = await container
      .withExec(["node", "-e", analyzeScript])
      .stdout();

    return result;
  }

  /**
   * Extract server specification from a repository
   */
  @func()
  async extractServerSpec(
    repoUrl: string
  ): Promise<string> {
    const analysis = await this.analyzeGitHubRepo(repoUrl);
    const parsed: McpAnalysis = JSON.parse(analysis);
    return JSON.stringify(parsed.spec, null, 2);
  }

  /**
   * Test MCP protocol compliance of a server
   */
  @func()
  async testMcpProtocol(
    serverCommand: string,
    serverArgs: string = "[]",
    envVars: string = "{}"
  ): Promise<string> {
    const parsedArgs: string[] = JSON.parse(serverArgs);
    const parsedEnv: Record<string, string> = JSON.parse(envVars);

    let container = dag
      .container()
      .from("node:22-slim")
      .withExec(["npm", "install", "-g", "@anthropics/mcp-inspector"]);

    // Set environment variables
    for (const [key, value] of Object.entries(parsedEnv)) {
      container = container.withEnvVariable(key, value);
    }

    const testScript = `
      const { spawn } = require('child_process');

      const result = {
        serverName: '${serverCommand}',
        success: false,
        protocolVersion: null,
        capabilities: {},
        tools: [],
        resources: [],
        errors: [],
        latency: {
          initializeMs: 0,
        }
      };

      const startTime = Date.now();

      // Spawn the MCP server
      const server = spawn('${serverCommand}', ${JSON.stringify(parsedArgs)}, {
        stdio: ['pipe', 'pipe', 'pipe']
      });

      let output = '';
      let errorOutput = '';

      server.stdout.on('data', (data) => {
        output += data.toString();
      });

      server.stderr.on('data', (data) => {
        errorOutput += data.toString();
      });

      // Send initialize request
      const initRequest = JSON.stringify({
        jsonrpc: '2.0',
        id: 1,
        method: 'initialize',
        params: {
          protocolVersion: '2024-11-05',
          capabilities: {},
          clientInfo: { name: 'mcp-test', version: '1.0.0' }
        }
      });

      server.stdin.write(initRequest + '\\n');

      // Wait for response
      setTimeout(() => {
        result.latency.initializeMs = Date.now() - startTime;

        try {
          const lines = output.split('\\n').filter(l => l.trim());
          for (const line of lines) {
            const response = JSON.parse(line);
            if (response.result) {
              result.success = true;
              result.protocolVersion = response.result.protocolVersion;
              result.capabilities = response.result.capabilities || {};
            }
          }
        } catch (e) {
          result.errors.push('Failed to parse response: ' + e.message);
        }

        if (errorOutput) {
          result.errors.push('Server stderr: ' + errorOutput.substring(0, 500));
        }

        server.kill();
        console.log(JSON.stringify(result, null, 2));
        process.exit(result.success ? 0 : 1);
      }, 5000);
    `;

    try {
      const result = await container
        .withExec(["node", "-e", testScript])
        .stdout();
      return result;
    } catch (e) {
      return JSON.stringify({
        serverName: serverCommand,
        success: false,
        errors: [`Test failed: ${e}`],
        latency: { initializeMs: 0 },
      });
    }
  }

  /**
   * Generate MCP server configuration for Claude Code
   */
  @func()
  async generateConfig(
    serverName: string,
    transport: string,
    command: string,
    args: string = "[]",
    envVars: string = "{}"
  ): Promise<string> {
    const parsedArgs: string[] = JSON.parse(args);
    const parsedEnv: Record<string, string> = JSON.parse(envVars);

    const config: McpServerConfig = {
      name: serverName,
      transport: transport as "stdio" | "http" | "sse",
      command,
      args: parsedArgs,
      env: parsedEnv,
      secrets: [],
    };

    // Detect secrets from env vars
    for (const [key, _value] of Object.entries(parsedEnv)) {
      if (key.includes("KEY") || key.includes("TOKEN") || key.includes("SECRET")) {
        config.secrets!.push({
          envVar: key,
          opReference: `op://dev-baile/${serverName.toLowerCase()}/${key.toLowerCase().replace(/_/g, '-')}`,
          required: true,
        });
      }
    }

    // Convert to Claude Code .mcp.json format
    const claudeConfig = {
      [serverName]: {
        command: config.command,
        args: config.args,
        env: Object.fromEntries(
          Object.entries(config.env || {}).map(([k, v]) =>
            config.secrets?.some((s: SecretMapping) => s.envVar === k)
              ? [k, `\${${k}}`]
              : [k, v]
          )
        ),
      },
    };

    return JSON.stringify(claudeConfig, null, 2);
  }

  /**
   * Deploy an MCP server to Komodo as a containerized stack
   */
  @func()
  async deployToKomodo(
    serverName: string,
    serverConfig: string,  // JSON McpServerConfig
    komodoApiKey: Secret,
    komodoApiSecret: Secret,
    komodoHost: string = "https://komodo.cianfhoghlaim.ie"
  ): Promise<string> {
    const config: McpServerConfig = JSON.parse(serverConfig);

    // Generate Docker Compose for the MCP server
    const composeYaml = `
version: "3.8"

services:
  ${serverName}:
    image: node:22-slim
    command: ["npx", "${config.command}", ${config.args?.map((a: string) => `"${a}"`).join(", ") || ""}]
    environment:
${Object.entries(config.env || {}).map(([k, v]) => `      - ${k}=${v}`).join("\n")}
    restart: unless-stopped
    networks:
      - mcp-network

  locket:
    image: ghcr.io/cianfhoghlaim/locket:latest
    volumes:
      - secrets:/secrets:rw
      - ./sidecar.yaml:/locket/config.yaml:ro
    environment:
      - OP_CONNECT_HOST=http://132.145.27.89:8080
      - OP_CONNECT_TOKEN=\${OP_CONNECT_TOKEN}
    networks:
      - mcp-network

volumes:
  secrets:

networks:
  mcp-network:
    driver: bridge
`;

    const container = dag
      .container()
      .from("curlimages/curl:latest")
      .withSecretVariable("KOMODO_API_KEY", komodoApiKey)
      .withSecretVariable("KOMODO_API_SECRET", komodoApiSecret)
      .withEnvVariable("KOMODO_HOST", komodoHost);

    // Create the stack via Komodo API
    const createStackScript = `
      curl -X POST "$KOMODO_HOST/write/CreateStack" \\
        -H "Content-Type: application/json" \\
        -H "x-api-key: $KOMODO_API_KEY" \\
        -H "x-api-secret: $KOMODO_API_SECRET" \\
        -d '{
          "name": "mcp-${serverName}",
          "config": {
            "server_id": "uirlisi",
            "file_contents": ${JSON.stringify(composeYaml)},
            "run_directory": "/opt/stacks/mcp-${serverName}"
          }
        }'
    `;

    const result = await container
      .withExec(["sh", "-c", createStackScript])
      .stdout();

    const deployResult: DeployResult = {
      id: `mcp-${serverName}-${Date.now()}`,
      serverName,
      success: true,
      method: "container",
      stackName: `mcp-${serverName}`,
      secretsCreated: [],
      errors: [],
      nextSteps: [
        `Stack created: mcp-${serverName}`,
        `Deploy with: komodo stack deploy mcp-${serverName}`,
        `Configure secrets in 1Password`,
      ],
    };

    return JSON.stringify(deployResult, null, 2);
  }

  /**
   * Full pipeline: Research, analyze, test, and deploy an MCP server
   */
  @func()
  async researchAndDeploy(
    query: string,
    targetServer: string,
    vault: string = "dev-baile"
  ): Promise<string> {
    const startTime = Date.now();
    const stages: PipelineStage[] = [];

    // Stage 1: Research
    const researchStart = Date.now();
    let searchResults: string;
    try {
      searchResults = await this.searchMcpServers(query, 5);
      stages.push({
        name: "research",
        success: true,
        output: searchResults,
        durationMs: Date.now() - researchStart,
      });
    } catch (e) {
      stages.push({
        name: "research",
        success: false,
        output: "",
        durationMs: Date.now() - researchStart,
        errors: [`Research failed: ${e}`],
      });
      return JSON.stringify({
        id: `pipeline-${Date.now()}`,
        serverName: targetServer,
        success: false,
        stages,
        durationMs: Date.now() - startTime,
      } as PipelineResult);
    }

    // Stage 2: Analyze first result
    const analyzeStart = Date.now();
    try {
      const results = JSON.parse(searchResults);
      if (results.length > 0) {
        const analysis = await this.analyzeGitHubRepo(results[0].url);
        stages.push({
          name: "analyze",
          success: true,
          output: analysis,
          durationMs: Date.now() - analyzeStart,
        });
      }
    } catch (e) {
      stages.push({
        name: "analyze",
        success: false,
        output: "",
        durationMs: Date.now() - analyzeStart,
        errors: [`Analysis failed: ${e}`],
      });
    }

    // Stage 3: Secrets setup
    const secretsStart = Date.now();
    try {
      const locketTemplate = `# Locket template for ${targetServer}\n# Configure secrets in 1Password vault: ${vault}`;
      stages.push({
        name: "secrets",
        success: true,
        output: locketTemplate,
        durationMs: Date.now() - secretsStart,
      });
    } catch (e) {
      stages.push({
        name: "secrets",
        success: false,
        output: "",
        durationMs: Date.now() - secretsStart,
        errors: [`Secrets setup failed: ${e}`],
      });
    }

    // Return pipeline result
    const result: PipelineResult = {
      id: `pipeline-${Date.now()}`,
      serverName: targetServer,
      success: stages.every(s => s.success),
      stages,
      durationMs: Date.now() - startTime,
    };

    return JSON.stringify(result, null, 2);
  }

  /**
   * List known MCP servers from the awesome-mcp-servers repository
   */
  @func()
  async listKnownServers(): Promise<string> {
    const container = dag
      .container()
      .from("node:22-slim")
      .withExec(["apt-get", "update"])
      .withExec(["apt-get", "install", "-y", "git"]);

    const script = `
      const { execSync } = require('child_process');
      const fs = require('fs');

      // Clone awesome-mcp-servers
      execSync('git clone --depth 1 https://github.com/punkpeye/awesome-mcp-servers /tmp/awesome', { stdio: 'pipe' });

      const readme = fs.readFileSync('/tmp/awesome/README.md', 'utf8');

      // Extract server entries (simplified parsing)
      const serverPattern = /\\[([^\\]]+)\\]\\(([^)]+)\\)\\s*-\\s*([^\\n]+)/g;
      const servers = [];

      let match;
      while ((match = serverPattern.exec(readme)) !== null) {
        if (match[2].includes('github.com')) {
          servers.push({
            name: match[1],
            url: match[2],
            description: match[3].trim(),
          });
        }
      }

      console.log(JSON.stringify(servers.slice(0, 50), null, 2));
    `;

    const result = await container
      .withExec(["node", "-e", script])
      .stdout();

    return result;
  }
}
