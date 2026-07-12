/**
 * Forgejo API Automation Module
 *
 * Provides programmatic access to Forgejo REST API for:
 * - User management (create users, generate tokens)
 * - Repository management (add collaborators)
 * - Webhook configuration
 * - Actions secrets management
 * - Runner registration
 */

import {
  dag,
  Container,
  Secret,
  object,
  func,
  field,
} from "@dagger.io/dagger";

@object()
export class Forgejo {
  @field()
  baseUrl: string;

  @field()
  adminToken: Secret;

  constructor(baseUrl: string, adminToken: Secret) {
    this.baseUrl = baseUrl;
    this.adminToken = adminToken;
  }

  /**
   * Get a curl container with auth configured
   */
  private curlContainer(): Container {
    return dag
      .container()
      .from("curlimages/curl:8.11.1")
      .withSecretVariable("FORGEJO_TOKEN", this.adminToken);
  }

  /**
   * Create a new user via Forgejo Admin API
   */
  @func()
  async createUser(
    username: string,
    email: string,
    password: Secret,
    mustChangePassword: boolean = false
  ): Promise<string> {
    return this.curlContainer()
      .withSecretVariable("USER_PASSWORD", password)
      .withExec([
        "sh",
        "-c",
        `curl -sf -X POST "${this.baseUrl}/admin/users" \
          -H "Authorization: token $FORGEJO_TOKEN" \
          -H "Content-Type: application/json" \
          -d '{"username":"${username}","email":"${email}","password":"'"$USER_PASSWORD"'","must_change_password":${mustChangePassword}}'`,
      ])
      .stdout();
  }

  /**
   * Create an access token for a user
   * Returns JSON with token details including sha1 field
   */
  @func()
  async createAccessToken(
    username: string,
    tokenName: string,
    scopes: string[]
  ): Promise<string> {
    const scopeJson = JSON.stringify(scopes);
    return this.curlContainer()
      .withExec([
        "sh",
        "-c",
        `curl -sf -X POST "${this.baseUrl}/users/${username}/tokens" \
          -H "Authorization: token $FORGEJO_TOKEN" \
          -H "Content-Type: application/json" \
          -d '{"name":"${tokenName}","scopes":${scopeJson}}'`,
      ])
      .stdout();
  }

  /**
   * Add a user as collaborator to a repository
   */
  @func()
  async addCollaborator(
    owner: string,
    repo: string,
    username: string,
    permission: string = "write"
  ): Promise<string> {
    return this.curlContainer()
      .withExec([
        "sh",
        "-c",
        `curl -sf -X PUT "${this.baseUrl}/repos/${owner}/${repo}/collaborators/${username}" \
          -H "Authorization: token $FORGEJO_TOKEN" \
          -H "Content-Type: application/json" \
          -d '{"permission":"${permission}"}'`,
      ])
      .stdout();
  }

  /**
   * Create a webhook for a repository
   */
  @func()
  async createWebhook(
    owner: string,
    repo: string,
    targetUrl: string,
    webhookSecret: Secret,
    events: string[] = ["push"],
    branchFilter: string = "main"
  ): Promise<string> {
    const eventsJson = JSON.stringify(events);
    return this.curlContainer()
      .withSecretVariable("WEBHOOK_SECRET", webhookSecret)
      .withExec([
        "sh",
        "-c",
        `curl -sf -X POST "${this.baseUrl}/repos/${owner}/${repo}/hooks" \
          -H "Authorization: token $FORGEJO_TOKEN" \
          -H "Content-Type: application/json" \
          -d '{"type":"forgejo","config":{"url":"${targetUrl}","content_type":"json","secret":"'"$WEBHOOK_SECRET"'"},"events":${eventsJson},"branch_filter":"${branchFilter}","active":true}'`,
      ])
      .stdout();
  }

  /**
   * List webhooks for a repository
   */
  @func()
  async listWebhooks(owner: string, repo: string): Promise<string> {
    return this.curlContainer()
      .withExec([
        "sh",
        "-c",
        `curl -sf -X GET "${this.baseUrl}/repos/${owner}/${repo}/hooks" \
          -H "Authorization: token $FORGEJO_TOKEN"`,
      ])
      .stdout();
  }

  /**
   * Set an Actions secret for a repository
   */
  @func()
  async setActionsSecret(
    owner: string,
    repo: string,
    secretName: string,
    secretValue: Secret
  ): Promise<string> {
    return this.curlContainer()
      .withSecretVariable("SECRET_VALUE", secretValue)
      .withExec([
        "sh",
        "-c",
        `curl -sf -X PUT "${this.baseUrl}/repos/${owner}/${repo}/actions/secrets/${secretName}" \
          -H "Authorization: token $FORGEJO_TOKEN" \
          -H "Content-Type: application/json" \
          -d '{"data":"'"$SECRET_VALUE"'"}'`,
      ])
      .stdout();
  }

  /**
   * List Actions secrets for a repository
   */
  @func()
  async listActionsSecrets(owner: string, repo: string): Promise<string> {
    return this.curlContainer()
      .withExec([
        "sh",
        "-c",
        `curl -sf -X GET "${this.baseUrl}/repos/${owner}/${repo}/actions/secrets" \
          -H "Authorization: token $FORGEJO_TOKEN"`,
      ])
      .stdout();
  }

  /**
   * Get a runner registration token (admin endpoint)
   */
  @func()
  async getRunnerRegistrationToken(): Promise<string> {
    return this.curlContainer()
      .withExec([
        "sh",
        "-c",
        `curl -sf -X GET "${this.baseUrl}/admin/runners/registration-token" \
          -H "Authorization: token $FORGEJO_TOKEN" | jq -r '.token'`,
      ])
      .stdout();
  }

  /**
   * List registered runners (admin endpoint)
   */
  @func()
  async listRunners(): Promise<string> {
    return this.curlContainer()
      .withExec([
        "sh",
        "-c",
        `curl -sf -X GET "${this.baseUrl}/admin/runners" \
          -H "Authorization: token $FORGEJO_TOKEN"`,
      ])
      .stdout();
  }

  /**
   * Register a runner offline using forgejo-runner CLI
   * Returns a container with the registered runner config
   */
  @func()
  async registerRunner(
    runnerName: string,
    labels: string[],
    registrationToken: Secret
  ): Promise<Container> {
    const labelStr = labels.join(",");
    const instanceUrl = this.baseUrl.replace("/api/v1", "");

    return dag
      .container()
      .from("code.forgejo.org/forgejo/runner:9.0.3")
      .withSecretVariable("RUNNER_TOKEN", registrationToken)
      .withExec([
        "sh",
        "-c",
        `forgejo-runner register \
          --instance "${instanceUrl}" \
          --token "$RUNNER_TOKEN" \
          --name "${runnerName}" \
          --labels "${labelStr}" \
          --no-interactive`,
      ]);
  }

  /**
   * Create an OAuth2 authentication source in Forgejo
   * Type 6 = OAuth2 provider
   */
  @func()
  async createAuthSource(
    providerName: string,
    providerKey: string,
    clientId: string,
    clientSecret: Secret,
    authUrl: string,
    tokenUrl: string,
    userinfoUrl: string,
    scopes: string = "openid email profile"
  ): Promise<string> {
    const scopesArray = scopes.split(" ");
    return this.curlContainer()
      .withSecretVariable("OAUTH_CLIENT_SECRET", clientSecret)
      .withExec([
        "sh",
        "-c",
        `curl -sf -X POST "${this.baseUrl}/admin/auths" \
          -H "Authorization: token $FORGEJO_TOKEN" \
          -H "Content-Type: application/json" \
          -d '{
            "type": 6,
            "name": "${providerName}",
            "is_active": true,
            "oauth2_config": {
              "provider": "openidConnect",
              "client_id": "${clientId}",
              "client_secret": "'"$OAUTH_CLIENT_SECRET"'",
              "open_id_connect_auto_discovery_url": "",
              "custom_url_mapping": {
                "auth_url": "${authUrl}",
                "token_url": "${tokenUrl}",
                "profile_url": "${userinfoUrl}"
              },
              "scopes": ${JSON.stringify(scopesArray)},
              "required_claim_name": "",
              "required_claim_value": "",
              "group_claim_name": "groups",
              "admin_group": "",
              "restricted_group": "",
              "group_team_map": "",
              "group_team_map_removal": false,
              "enable_auto_registration": true,
              "icon_url": ""
            }
          }'`,
      ])
      .stdout();
  }

  /**
   * List authentication sources
   */
  @func()
  async listAuthSources(): Promise<string> {
    return this.curlContainer()
      .withExec([
        "sh",
        "-c",
        `curl -sf -X GET "${this.baseUrl}/admin/auths" \
          -H "Authorization: token $FORGEJO_TOKEN"`,
      ])
      .stdout();
  }

  /**
   * Delete an authentication source by ID
   */
  @func()
  async deleteAuthSource(authSourceId: number): Promise<string> {
    return this.curlContainer()
      .withExec([
        "sh",
        "-c",
        `curl -sf -X DELETE "${this.baseUrl}/admin/auths/${authSourceId}" \
          -H "Authorization: token $FORGEJO_TOKEN"`,
      ])
      .stdout();
  }

  /**
   * Check Forgejo API health
   */
  @func()
  async health(): Promise<string> {
    return dag
      .container()
      .from("curlimages/curl:8.11.1")
      .withExec(["curl", "-sf", `${this.baseUrl}/version`])
      .stdout();
  }

  /**
   * Get current user info (validates token)
   */
  @func()
  async getCurrentUser(): Promise<string> {
    return this.curlContainer()
      .withExec([
        "sh",
        "-c",
        `curl -sf -X GET "${this.baseUrl}/user" \
          -H "Authorization: token $FORGEJO_TOKEN"`,
      ])
      .stdout();
  }
}
