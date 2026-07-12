/**
 * Browser Automation Wrapper Module
 *
 * Provides browser automation integration for Dagger workflows:
 * - Stagehand-based automated browser interactions
 * - Human-in-the-loop approval for WebAuthn/manual steps
 * - Form automation and data extraction
 *
 * Integrates with: sruth/browser/ multi-backend router
 *
 * Usage:
 *   const browser = new BrowserAutomation("http://localhost:3001");
 *   await browser.setupPocketIdAdmin("example.com");
 *   await browser.createOAuthClient("example.com", "https://tinyauth.example.com/callback");
 */

import {
  dag,
  Container,
  object,
  func,
  field,
} from "@dagger.io/dagger";

import type {
  OAuthCredentials,
  HumanApprovalRequest,
  HumanApprovalResult,
  BrowserAction,
  BrowserExtractResult,
  FormField,
} from "./types";

@object()
export class BrowserAutomation {
  @field()
  serverUrl: string;

  @field()
  backend: string;

  constructor(
    serverUrl: string = "http://localhost:3001",
    backend: string = "stagehand"
  ) {
    this.serverUrl = serverUrl;
    this.backend = backend;
  }

  /**
   * Get a curl container for API requests
   */
  private curlContainer(): Container {
    return dag
      .container()
      .from("curlimages/curl:8.11.1");
  }

  /**
   * Execute a browser automation request
   */
  private async browserRequest(
    endpoint: string,
    method: string = "POST",
    body?: object
  ): Promise<string> {
    const args = [
      "curl",
      "-sf",
      "-X", method,
      `${this.serverUrl}${endpoint}`,
      "-H", "Content-Type: application/json",
    ];

    if (body) {
      args.push("-d", JSON.stringify(body));
    }

    return this.curlContainer()
      .withExec(args)
      .stdout();
  }

  // ===========================================================================
  // Core Browser Operations
  // ===========================================================================

  /**
   * Navigate to a URL
   */
  @func()
  async navigate(url: string): Promise<string> {
    return this.browserRequest("/api/navigate", "POST", { url, backend: this.backend });
  }

  /**
   * Perform an action (click, type, etc.) using natural language
   */
  @func()
  async act(action: string, variables?: string): Promise<string> {
    const vars = variables ? JSON.parse(variables) : undefined;
    return this.browserRequest("/api/act", "POST", {
      action,
      variables: vars,
      backend: this.backend,
    });
  }

  /**
   * Observe the page to find interactive elements
   */
  @func()
  async observe(instruction: string): Promise<string> {
    return this.browserRequest("/api/observe", "POST", {
      instruction,
      backend: this.backend,
    });
  }

  /**
   * Extract data from the page
   */
  @func()
  async extract(instruction: string, schema?: string): Promise<string> {
    const schemaObj = schema ? JSON.parse(schema) : undefined;
    return this.browserRequest("/api/extract", "POST", {
      instruction,
      schema: schemaObj,
      backend: this.backend,
    });
  }

  /**
   * Take a screenshot of the current page
   */
  @func()
  async screenshot(name?: string): Promise<string> {
    return this.browserRequest("/api/screenshot", "POST", {
      name: name || `screenshot-${Date.now()}`,
      backend: this.backend,
    });
  }

  /**
   * Get current page URL
   */
  @func()
  async getUrl(): Promise<string> {
    return this.browserRequest("/api/url", "GET");
  }

  // ===========================================================================
  // Form Operations
  // ===========================================================================

  /**
   * Fill a form with multiple fields
   */
  @func()
  async fillForm(fields: string): Promise<string> {
    const formFields: FormField[] = JSON.parse(fields);
    return this.browserRequest("/api/form/fill", "POST", {
      fields: formFields,
      backend: this.backend,
    });
  }

  /**
   * Submit the current form
   */
  @func()
  async submitForm(): Promise<string> {
    return this.act("Click the submit button or press Enter to submit the form");
  }

  // ===========================================================================
  // Human-in-the-Loop Operations
  // ===========================================================================

  /**
   * Request human approval for a task
   */
  @func()
  async requestHumanApproval(
    task: string,
    instructions: string, // JSON array of instruction strings
    url?: string,
    timeout: number = 300
  ): Promise<string> {
    const instructionList: string[] = JSON.parse(instructions);

    const request: HumanApprovalRequest = {
      task,
      instructions: instructionList,
      url,
      timeout,
    };

    return this.browserRequest("/api/approval/request", "POST", request);
  }

  /**
   * Check status of a human approval request
   */
  @func()
  async checkApprovalStatus(awakeableId: string): Promise<string> {
    return this.browserRequest(`/api/approval/status/${awakeableId}`, "GET");
  }

  /**
   * Complete a human approval request
   */
  @func()
  async completeApproval(
    awakeableId: string,
    approved: boolean,
    notes?: string
  ): Promise<string> {
    return this.browserRequest("/api/approval/complete", "POST", {
      awakeableId,
      approved,
      notes,
    });
  }

  // ===========================================================================
  // Session Management
  // ===========================================================================

  /**
   * Create a new browser session
   */
  @func()
  async createSession(sessionId?: string): Promise<string> {
    return this.browserRequest("/api/session/create", "POST", {
      sessionId,
      backend: this.backend,
    });
  }

  /**
   * Close the current browser session
   */
  @func()
  async closeSession(): Promise<string> {
    return this.browserRequest("/api/session/close", "POST", {
      backend: this.backend,
    });
  }

  // ===========================================================================
  // High-Level Workflow Methods
  // ===========================================================================

  /**
   * Setup PocketID admin account
   * Requires human approval for WebAuthn passkey registration
   */
  @func()
  async setupPocketIdAdmin(domain: string): Promise<string> {
    // First check if already configured
    const healthCheck = await this.curlContainer()
      .withExec([
        "curl",
        "-sf",
        `https://auth.${domain}/healthz`,
      ])
      .stdout()
      .catch(() => "error");

    if (healthCheck.includes("ok")) {
      return JSON.stringify({
        success: true,
        skipped: true,
        message: "PocketID already configured",
      });
    }

    // Request human approval for WebAuthn setup
    const approvalResult = await this.requestHumanApproval(
      "PocketID Admin Setup",
      JSON.stringify([
        `Navigate to https://auth.${domain}/setup`,
        "Create admin account with a secure username",
        "Register your passkey (WebAuthn) when prompted",
        "Complete the setup wizard",
        "Verify you can access the admin dashboard",
      ]),
      `https://auth.${domain}/setup`,
      600 // 10 minute timeout for manual setup
    );

    const approval: HumanApprovalResult = JSON.parse(approvalResult);

    return JSON.stringify({
      success: approval.approved,
      humanApproved: approval.approved,
      completedBy: approval.completedBy,
      notes: approval.notes,
    });
  }

  /**
   * Create OAuth client for TinyAuth in PocketID
   * Can be automated via Stagehand
   */
  @func()
  async createOAuthClient(
    domain: string,
    redirectUri: string
  ): Promise<string> {
    try {
      // Create browser session
      await this.createSession();

      // Navigate to PocketID admin
      await this.navigate(`https://auth.${domain}/admin`);

      // Navigate to OIDC clients section
      await this.act("Click on OIDC Clients or OAuth Clients in the navigation menu");

      // Wait for page load
      await this.act("Wait for the clients list to load");

      // Click add new client
      await this.act("Click the Add Client or Create Client button");

      // Fill the form
      await this.fillForm(JSON.stringify([
        { name: "name", value: "TinyAuth", type: "text" },
        { name: "redirectUri", value: redirectUri, type: "text" },
        { name: "scopes", value: "openid email profile groups", type: "text" },
      ]));

      // Submit
      await this.act("Click the Save or Create button to save the client");

      // Wait for creation
      await this.act("Wait for the client to be created and credentials to be displayed");

      // Extract credentials
      const extractResult = await this.extract(
        "Extract the Client ID and Client Secret values from the page",
        JSON.stringify({
          type: "object",
          properties: {
            clientId: { type: "string" },
            clientSecret: { type: "string" },
          },
          required: ["clientId", "clientSecret"],
        })
      );

      // Close session
      await this.closeSession();

      const credentials: OAuthCredentials = JSON.parse(extractResult);

      return JSON.stringify({
        success: true,
        clientId: credentials.clientId,
        clientSecret: credentials.clientSecret,
      });
    } catch (error) {
      await this.closeSession().catch(() => {});

      return JSON.stringify({
        success: false,
        error: error instanceof Error ? error.message : "Unknown error",
      });
    }
  }

  /**
   * Verify PocketID is accessible and configured
   */
  @func()
  async verifyPocketId(domain: string): Promise<string> {
    try {
      // Create browser session
      await this.createSession();

      // Navigate to login page
      await this.navigate(`https://auth.${domain}`);

      // Check for login form
      const observation = await this.observe(
        "Find the login button or passkey authentication option"
      );

      // Close session
      await this.closeSession();

      const hasLogin = observation.includes("login") || observation.includes("passkey");

      return JSON.stringify({
        configured: hasLogin,
        url: `https://auth.${domain}`,
        observation,
      });
    } catch (error) {
      await this.closeSession().catch(() => {});

      return JSON.stringify({
        configured: false,
        error: error instanceof Error ? error.message : "Unknown error",
      });
    }
  }

  /**
   * Generic automation workflow
   * Executes a series of browser actions
   */
  @func()
  async runWorkflow(
    startUrl: string,
    actions: string // JSON array of BrowserAction
  ): Promise<string> {
    const actionList: BrowserAction[] = JSON.parse(actions);
    const results: { action: string; success: boolean; result?: string; error?: string }[] = [];

    try {
      await this.createSession();
      await this.navigate(startUrl);

      for (const action of actionList) {
        try {
          let result: string;

          switch (action.action) {
            case "navigate":
              result = await this.navigate(action.value || "");
              break;
            case "click":
              result = await this.act(`Click on ${action.selector || action.value}`);
              break;
            case "type":
              result = await this.act(`Type "${action.value}" into ${action.selector}`);
              break;
            case "extract":
              result = await this.extract(action.value || "Extract all visible data");
              break;
            case "observe":
              result = await this.observe(action.value || "Find all interactive elements");
              break;
            case "screenshot":
              result = await this.screenshot(action.value);
              break;
            default:
              result = await this.act(action.action);
          }

          results.push({
            action: action.action,
            success: true,
            result,
          });
        } catch (error) {
          results.push({
            action: action.action,
            success: false,
            error: error instanceof Error ? error.message : "Unknown error",
          });
        }
      }

      await this.closeSession();

      return JSON.stringify({
        success: results.every((r) => r.success),
        results,
      });
    } catch (error) {
      await this.closeSession().catch(() => {});

      return JSON.stringify({
        success: false,
        error: error instanceof Error ? error.message : "Unknown error",
        results,
      });
    }
  }

  // ===========================================================================
  // Health & Diagnostics
  // ===========================================================================

  /**
   * Check browser automation server health
   */
  @func()
  async health(): Promise<string> {
    return this.curlContainer()
      .withExec(["curl", "-sf", `${this.serverUrl}/health`])
      .stdout();
  }

  /**
   * Get available backends
   */
  @func()
  async listBackends(): Promise<string> {
    return this.browserRequest("/api/backends", "GET");
  }

  /**
   * Set the backend to use
   */
  @func()
  setBackend(backend: string): BrowserAutomation {
    return new BrowserAutomation(this.serverUrl, backend);
  }
}
