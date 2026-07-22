/**
 * GitHub Sync Module for Dagger
 *
 * Provides programmatic Git subtree operations for syncing flows
 * between Forgejo monorepo and GitHub mirrors.
 *
 * Features:
 * - Subtree split and push to GitHub mirrors
 * - PR forwarding from GitHub to Forgejo
 * - Bidirectional sync status tracking
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

/**
 * Flow configuration for GitHub mirroring
 */
interface FlowMirrorConfig {
  name: string;
  prefix: string;
  githubRepo: string;
  githubOrg: string;
}

/**
 * Pre-configured flows for mirroring
 */
const FLOW_CONFIGS: Record<string, FlowMirrorConfig> = {
  oideachais: {
    name: "oideachais",
    prefix: "sruth/oideachais",
    githubRepo: "oideachais",
    githubOrg: "cianfhoghlaim",
  },
  crypteolas: {
    name: "crypteolas",
    prefix: "sruth/crypteolas",
    githubRepo: "crypteolas",
    githubOrg: "cianfhoghlaim",
  },
  aleyum: {
    name: "aleyum",
    prefix: "sruth/aleyum",
    githubRepo: "aleyum",
    githubOrg: "yedya",
  },
};

@object()
export class GitHubSync {
  @field()
  forgejoUrl: string = "https://git.cianfhoghlaim.ie";

  constructor(forgejoUrl?: string) {
    if (forgejoUrl) {
      this.forgejoUrl = forgejoUrl;
    }
  }

  /**
   * Get a git container configured for operations
   */
  private gitContainer(): Container {
    return dag
      .container()
      .from("alpine/git:2.45.2")
      .withExec(["git", "config", "--global", "user.name", "Dagger Bot"])
      .withExec(["git", "config", "--global", "user.email", "dagger@cianfhoghlaim.ie"]);
  }

  /**
   * Split a flow subtree and push to GitHub
   *
   * @param source - Source directory (git repository root)
   * @param flow - Flow name (oideachais, crypteolas, aleyum)
   * @param githubToken - GitHub PAT with repo write access
   * @param force - Force push (default: true for mirrors)
   * @returns Push result message
   */
  @func()
  async splitAndPush(
    source: Directory,
    flow: string,
    githubToken: Secret,
    force: boolean = true
  ): Promise<string> {
    const config = FLOW_CONFIGS[flow];
    if (!config) {
      throw new Error(`Unknown flow: ${flow}. Available: ${Object.keys(FLOW_CONFIGS).join(", ")}`);
    }

    const forceFlag = force ? "--force" : "";
    const targetUrl = `https://x-access-token:$GITHUB_TOKEN@github.com/${config.githubOrg}/${config.githubRepo}.git`;

    return this.gitContainer()
      .withMountedDirectory("/repo", source)
      .withWorkdir("/repo")
      .withSecretVariable("GITHUB_TOKEN", githubToken)
      .withExec([
        "sh",
        "-c",
        `
        echo "Splitting subtree for ${config.prefix}..."
        git subtree split --prefix=${config.prefix} -b ${flow}-split

        echo "Pushing to github.com/${config.githubOrg}/${config.githubRepo}..."
        git push ${forceFlag} "${targetUrl}" ${flow}-split:main

        echo "Sync complete for ${flow}!"
        `,
      ])
      .stdout();
  }

  /**
   * Sync all configured flows to GitHub
   *
   * @param source - Source directory
   * @param githubToken - GitHub PAT for cianfhoghlaim org
   * @param yedyaGithubToken - GitHub PAT for yedya org (optional)
   * @returns Summary of sync operations
   */
  @func()
  async syncAll(
    source: Directory,
    githubToken: Secret,
    yedyaGithubToken?: Secret
  ): Promise<string> {
    const results: string[] = [];

    // Sync cianfhoghlaim org flows
    for (const flow of ["oideachais", "crypteolas"]) {
      try {
        const result = await this.splitAndPush(source, flow, githubToken);
        results.push(`${flow}: SUCCESS`);
      } catch (error) {
        results.push(`${flow}: FAILED - ${error}`);
      }
    }

    // Sync yedya org flows
    if (yedyaGithubToken) {
      try {
        const result = await this.splitAndPush(source, "aleyum", yedyaGithubToken);
        results.push(`aleyum: SUCCESS`);
      } catch (error) {
        results.push(`aleyum: FAILED - ${error}`);
      }
    } else {
      results.push(`aleyum: SKIPPED (no yedya token)`);
    }

    return results.join("\n");
  }

  /**
   * Create a GitHub repository for a flow (if it doesn't exist)
   *
   * @param flow - Flow name
   * @param githubToken - GitHub PAT with repo:create scope
   * @param isPrivate - Whether the repo should be private
   * @returns Repository URL
   */
  @func()
  async createMirrorRepo(
    flow: string,
    githubToken: Secret,
    isPrivate: boolean = false
  ): Promise<string> {
    const config = FLOW_CONFIGS[flow];
    if (!config) {
      throw new Error(`Unknown flow: ${flow}`);
    }

    return dag
      .container()
      .from("curlimages/curl:8.11.1")
      .withSecretVariable("GITHUB_TOKEN", githubToken)
      .withExec([
        "sh",
        "-c",
        `
        # Check if repo exists
        STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
          -H "Authorization: token $GITHUB_TOKEN" \
          "https://api.github.com/repos/${config.githubOrg}/${config.githubRepo}")

        if [ "$STATUS" = "200" ]; then
          echo "Repository already exists: https://github.com/${config.githubOrg}/${config.githubRepo}"
          exit 0
        fi

        # Create repo
        curl -sf -X POST \
          -H "Authorization: token $GITHUB_TOKEN" \
          -H "Accept: application/vnd.github.v3+json" \
          "https://api.github.com/orgs/${config.githubOrg}/repos" \
          -d '{
            "name": "${config.githubRepo}",
            "description": "Mirror of ${config.prefix} from Forgejo",
            "private": ${isPrivate},
            "has_issues": false,
            "has_projects": false,
            "has_wiki": false
          }'

        echo "Created: https://github.com/${config.githubOrg}/${config.githubRepo}"
        `,
      ])
      .stdout();
  }

  /**
   * Forward a GitHub PR to Forgejo
   *
   * Creates a branch and PR on Forgejo with the changes from a GitHub PR.
   *
   * @param forgejoToken - Forgejo API token
   * @param flow - Flow name
   * @param prNumber - GitHub PR number
   * @param prTitle - PR title
   * @param prBody - PR body
   * @param prBranch - Source branch from GitHub PR
   * @returns Forgejo PR URL
   */
  @func()
  async forwardGitHubPR(
    forgejoToken: Secret,
    flow: string,
    prNumber: number,
    prTitle: string,
    prBody: string,
    prBranch: string
  ): Promise<string> {
    const config = FLOW_CONFIGS[flow];
    if (!config) {
      throw new Error(`Unknown flow: ${flow}`);
    }

    const forgejoApi = `${this.forgejoUrl}/api/v1`;
    const branchName = `github-pr-${flow}-${prNumber}`;
    const fullTitle = `[GitHub PR #${prNumber}] ${prTitle}`;
    const fullBody = `Forwarded from GitHub: https://github.com/${config.githubOrg}/${config.githubRepo}/pull/${prNumber}\n\nChanges in ${config.prefix}/\n\n${prBody}`;

    return dag
      .container()
      .from("curlimages/curl:8.11.1")
      .withSecretVariable("FORGEJO_TOKEN", forgejoToken)
      .withExec([
        "sh",
        "-c",
        `
        # Create PR on Forgejo
        curl -sf -X POST \
          "${forgejoApi}/repos/cliste/bonneagar/pulls" \
          -H "Authorization: token $FORGEJO_TOKEN" \
          -H "Content-Type: application/json" \
          -d '{
            "title": "${fullTitle.replace(/"/g, '\\"')}",
            "head": "${branchName}",
            "base": "main",
            "body": "${fullBody.replace(/"/g, '\\"').replace(/\n/g, "\\n")}"
          }'
        `,
      ])
      .stdout();
  }

  /**
   * List all configured flow mirrors
   */
  @func()
  listFlows(): string {
    const lines = Object.entries(FLOW_CONFIGS).map(([name, config]) => {
      return `${name}: ${config.prefix} -> github.com/${config.githubOrg}/${config.githubRepo}`;
    });
    return lines.join("\n");
  }

  /**
   * Check if a flow has changes compared to its GitHub mirror
   *
   * @param source - Source directory
   * @param flow - Flow name
   * @param githubToken - GitHub PAT for reading
   * @returns true if there are changes to sync
   */
  @func()
  async hasChanges(
    source: Directory,
    flow: string,
    githubToken: Secret
  ): Promise<boolean> {
    const config = FLOW_CONFIGS[flow];
    if (!config) {
      throw new Error(`Unknown flow: ${flow}`);
    }

    const result = await this.gitContainer()
      .withMountedDirectory("/repo", source)
      .withWorkdir("/repo")
      .withSecretVariable("GITHUB_TOKEN", githubToken)
      .withExec([
        "sh",
        "-c",
        `
        # Get local subtree HEAD
        LOCAL_HEAD=$(git subtree split --prefix=${config.prefix} -b temp-check 2>/dev/null | tail -1)

        # Get remote HEAD
        REMOTE_HEAD=$(git ls-remote https://x-access-token:$GITHUB_TOKEN@github.com/${config.githubOrg}/${config.githubRepo}.git HEAD 2>/dev/null | cut -f1)

        # Clean up temp branch
        git branch -D temp-check 2>/dev/null || true

        if [ "$LOCAL_HEAD" = "$REMOTE_HEAD" ]; then
          echo "false"
        else
          echo "true"
        fi
        `,
      ])
      .stdout();

    return result.trim() === "true";
  }
}
