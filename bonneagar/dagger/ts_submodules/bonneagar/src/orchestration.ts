/**
 * Orchestration Module
 *
 * Provides integration with:
 * - Netflix Conductor (business logic orchestration)
 * - Dagster (data/ML job orchestration)
 * - Conductor-Dagster Bridge (orchestrator-of-orchestrators pattern)
 */

import { dag, Container, Directory, Service, object, func } from "@dagger.io/dagger";

// =============================================================================
// Types
// =============================================================================

export interface ConductorConfig {
  serverUrl: string;
  apiUrl: string;
  uiUrl: string;
}

export interface DagsterConfig {
  host: string;
  port: number;
  graphqlEndpoint: string;
}

export interface JobSelector {
  repositoryName: string;
  jobName: string;
  location?: string;
}

export interface DagsterRunConfig {
  selector: JobSelector;
  runConfigData?: Record<string, unknown>;
  tags?: Record<string, string>;
}

export interface ConductorWorkflow {
  name: string;
  version: number;
  tasks: ConductorTask[];
}

export interface ConductorTask {
  name: string;
  taskReferenceName: string;
  type: "SIMPLE" | "SUB_WORKFLOW" | "FORK_JOIN" | "DECISION" | "DO_WHILE";
  inputParameters?: Record<string, unknown>;
}

// =============================================================================
// Default endpoints
// =============================================================================

// NOTE: Conductor and Dagster stacks are NOT YET DEPLOYED
// These endpoints are placeholders - create stacks before using
const DEFAULT_CONDUCTOR_SERVER = "https://conductor.cianfhoghlaim.ie";
const DEFAULT_CONDUCTOR_LOCAL = "http://localhost:8080";

const DEFAULT_DAGSTER_HOST = "dagster.cianfhoghlaim.ie";
const DEFAULT_DAGSTER_LOCAL = "localhost";
const DEFAULT_DAGSTER_PORT = 3000;

@object()
export class Orchestration {
  /**
   * Get Conductor configuration
   */
  @func()
  getConductorConfig(local: boolean = false): ConductorConfig {
    const baseUrl = local ? DEFAULT_CONDUCTOR_LOCAL : DEFAULT_CONDUCTOR_SERVER;
    return {
      serverUrl: baseUrl,
      apiUrl: `${baseUrl}/api`,
      uiUrl: `${baseUrl}/ui`,
    };
  }

  /**
   * Get Dagster configuration
   */
  @func()
  getDagsterConfig(local: boolean = false): DagsterConfig {
    const host = local ? DEFAULT_DAGSTER_LOCAL : DEFAULT_DAGSTER_HOST;
    return {
      host,
      port: DEFAULT_DAGSTER_PORT,
      graphqlEndpoint: `http://${host}:${DEFAULT_DAGSTER_PORT}/graphql`,
    };
  }

  /**
   * Test Conductor connection
   */
  @func()
  async testConductorConnection(serverUrl?: string): Promise<boolean> {
    const url = serverUrl || DEFAULT_CONDUCTOR_SERVER;

    try {
      const result = await dag
        .container()
        .from("curlimages/curl:latest")
        .withExec(["curl", "-sf", `${url}/health`])
        .stdout();

      return result.includes("healthy") || result.length > 0;
    } catch {
      return false;
    }
  }

  /**
   * Test Dagster connection
   */
  @func()
  async testDagsterConnection(host?: string, port?: number): Promise<boolean> {
    const h = host || DEFAULT_DAGSTER_HOST;
    const p = port || DEFAULT_DAGSTER_PORT;

    try {
      const result = await dag
        .container()
        .from("curlimages/curl:latest")
        .withExec(["curl", "-sf", `http://${h}:${p}/graphql`])
        .stdout();

      return result.length > 0;
    } catch {
      return false;
    }
  }

  /**
   * Launch a Dagster run via GraphQL
   */
  @func()
  async launchDagsterRun(
    config: DagsterRunConfig,
    host?: string,
    port?: number
  ): Promise<string> {
    const h = host || DEFAULT_DAGSTER_HOST;
    const p = port || DEFAULT_DAGSTER_PORT;
    const endpoint = `http://${h}:${p}/graphql`;

    const query = `
      mutation LaunchRun($selector: JobSelector!, $runConfigData: RunConfigData, $tags: [ExecutionTag!]) {
        launchRun(
          executionParams: {
            selector: $selector
            runConfigData: $runConfigData
            executionMetadata: { tags: $tags }
          }
        ) {
          __typename
          ... on LaunchRunSuccess {
            run {
              runId
              status
            }
          }
          ... on PythonError {
            message
            stack
          }
          ... on InvalidStepError {
            invalidStepKey
          }
          ... on InvalidOutputError {
            stepKey
            invalidOutputName
          }
        }
      }
    `;

    const variables = {
      selector: {
        repositoryName: config.selector.repositoryName,
        jobName: config.selector.jobName,
        repositoryLocationName: config.selector.location || "__repository__",
      },
      runConfigData: config.runConfigData || {},
      tags: config.tags
        ? Object.entries(config.tags).map(([key, value]) => ({ key, value }))
        : [],
    };

    try {
      const result = await dag
        .container()
        .from("curlimages/curl:latest")
        .withExec([
          "curl", "-sf",
          "-X", "POST",
          endpoint,
          "-H", "Content-Type: application/json",
          "-d", JSON.stringify({ query, variables }),
        ])
        .stdout();

      return result;
    } catch (error) {
      return `Error: ${error instanceof Error ? error.message : "Unknown error"}`;
    }
  }

  /**
   * Get Dagster run status
   */
  @func()
  async getDagsterRunStatus(runId: string, host?: string, port?: number): Promise<string> {
    const h = host || DEFAULT_DAGSTER_HOST;
    const p = port || DEFAULT_DAGSTER_PORT;
    const endpoint = `http://${h}:${p}/graphql`;

    const query = `
      query RunStatus($runId: ID!) {
        runOrError(runId: $runId) {
          __typename
          ... on Run {
            runId
            status
            startTime
            endTime
            tags {
              key
              value
            }
          }
          ... on RunNotFoundError {
            runId
            message
          }
          ... on PythonError {
            message
          }
        }
      }
    `;

    try {
      const result = await dag
        .container()
        .from("curlimages/curl:latest")
        .withExec([
          "curl", "-sf",
          "-X", "POST",
          endpoint,
          "-H", "Content-Type: application/json",
          "-d", JSON.stringify({ query, variables: { runId } }),
        ])
        .stdout();

      return result;
    } catch (error) {
      return `Error: ${error instanceof Error ? error.message : "Unknown error"}`;
    }
  }

  /**
   * Generate DagsterTriggerWorker Python code for Conductor
   */
  @func()
  generateDagsterTriggerWorker(): string {
    return `# DagsterTriggerWorker - Conductor Worker for Dagster Job Triggering
# Auto-generated by Dagger Orchestration module
#
# This worker implements the Conductor-Dagster bridge pattern from the
# "Maximizing Claude Credits" strategy document.

import os
import json
import httpx
from conductor.client.worker.worker_interface import WorkerInterface

DAGSTER_HOST = os.environ.get("DAGSTER_HOST", "${DEFAULT_DAGSTER_HOST}")
DAGSTER_PORT = int(os.environ.get("DAGSTER_PORT", "${DEFAULT_DAGSTER_PORT}"))
DAGSTER_GRAPHQL = f"http://{DAGSTER_HOST}:{DAGSTER_PORT}/graphql"


class DagsterTriggerWorker(WorkerInterface):
    """
    Conductor worker that triggers Dagster jobs.

    Input Parameters:
        - job_name: Name of the Dagster job to run
        - repository_name: Name of the Dagster repository
        - run_config: Optional run configuration (JSON string)
        - tags: Optional tags for the run (JSON object)

    Output:
        - run_id: The Dagster run ID
        - status: Initial run status
    """

    def execute(self, task: dict) -> dict:
        input_data = task.get("inputData", {})

        job_name = input_data.get("job_name")
        repository_name = input_data.get("repository_name", "__repository__")
        run_config = input_data.get("run_config", "{}")
        tags = input_data.get("tags", {})

        if not job_name:
            return {
                "status": "FAILED",
                "reasonForIncompletion": "job_name is required",
            }

        # Parse run_config if it's a string
        if isinstance(run_config, str):
            run_config = json.loads(run_config)

        # Build GraphQL mutation
        query = """
        mutation LaunchRun($selector: JobSelector!, $runConfigData: RunConfigData, $tags: [ExecutionTag!]) {
            launchRun(
                executionParams: {
                    selector: $selector
                    runConfigData: $runConfigData
                    executionMetadata: { tags: $tags }
                }
            ) {
                __typename
                ... on LaunchRunSuccess {
                    run {
                        runId
                        status
                    }
                }
                ... on PythonError {
                    message
                }
            }
        }
        """

        variables = {
            "selector": {
                "repositoryName": repository_name,
                "jobName": job_name,
                "repositoryLocationName": "__repository__",
            },
            "runConfigData": run_config,
            "tags": [{"key": k, "value": v} for k, v in tags.items()],
        }

        try:
            response = httpx.post(
                DAGSTER_GRAPHQL,
                json={"query": query, "variables": variables},
                timeout=30.0,
            )
            response.raise_for_status()
            result = response.json()

            data = result.get("data", {}).get("launchRun", {})

            if data.get("__typename") == "LaunchRunSuccess":
                run = data.get("run", {})
                return {
                    "status": "COMPLETED",
                    "outputData": {
                        "run_id": run.get("runId"),
                        "initial_status": run.get("status"),
                    },
                }
            else:
                return {
                    "status": "FAILED",
                    "reasonForIncompletion": data.get("message", "Unknown error"),
                }

        except Exception as e:
            return {
                "status": "FAILED",
                "reasonForIncompletion": str(e),
            }


class DagsterPollWorker(WorkerInterface):
    """
    Conductor worker that polls Dagster run status.

    Input Parameters:
        - run_id: The Dagster run ID to poll

    Output:
        - status: Current run status
        - completed: Boolean indicating if run is complete
    """

    TERMINAL_STATUSES = {"SUCCESS", "FAILURE", "CANCELED"}

    def execute(self, task: dict) -> dict:
        input_data = task.get("inputData", {})
        run_id = input_data.get("run_id")

        if not run_id:
            return {
                "status": "FAILED",
                "reasonForIncompletion": "run_id is required",
            }

        query = """
        query RunStatus($runId: ID!) {
            runOrError(runId: $runId) {
                __typename
                ... on Run {
                    runId
                    status
                }
                ... on RunNotFoundError {
                    message
                }
            }
        }
        """

        try:
            response = httpx.post(
                DAGSTER_GRAPHQL,
                json={"query": query, "variables": {"runId": run_id}},
                timeout=30.0,
            )
            response.raise_for_status()
            result = response.json()

            data = result.get("data", {}).get("runOrError", {})

            if data.get("__typename") == "Run":
                status = data.get("status")
                completed = status in self.TERMINAL_STATUSES

                return {
                    "status": "COMPLETED",
                    "outputData": {
                        "run_status": status,
                        "completed": completed,
                        "success": status == "SUCCESS",
                    },
                }
            else:
                return {
                    "status": "FAILED",
                    "reasonForIncompletion": data.get("message", "Run not found"),
                }

        except Exception as e:
            return {
                "status": "FAILED",
                "reasonForIncompletion": str(e),
            }
`;
  }

  /**
   * Generate Conductor polling workflow JSON for Dagster job
   */
  @func()
  generatePollingWorkflow(
    workflowName: string,
    dagsterJobName: string,
    repositoryName: string = "__repository__",
    pollIntervalSeconds: number = 30,
    maxPollAttempts: number = 120
  ): string {
    const workflow = {
      name: workflowName,
      description: `Workflow that triggers and polls Dagster job: ${dagsterJobName}`,
      version: 1,
      tasks: [
        {
          name: "trigger_dagster_job",
          taskReferenceName: "trigger_job",
          type: "SIMPLE",
          inputParameters: {
            job_name: dagsterJobName,
            repository_name: repositoryName,
            run_config: "${workflow.input.run_config}",
            tags: "${workflow.input.tags}",
          },
        },
        {
          name: "poll_dagster_status",
          taskReferenceName: "poll_status",
          type: "DO_WHILE",
          inputParameters: {
            run_id: "${trigger_job.output.run_id}",
          },
          loopCondition: "if ($.poll_status['completed'] == false) { true; } else { false; }",
          loopOver: [
            {
              name: "check_status",
              taskReferenceName: "check_status_ref",
              type: "SIMPLE",
              inputParameters: {
                run_id: "${trigger_job.output.run_id}",
              },
            },
            {
              name: "wait",
              taskReferenceName: "wait_ref",
              type: "WAIT",
              inputParameters: {
                duration: `${pollIntervalSeconds}s`,
              },
            },
          ],
        },
        {
          name: "evaluate_result",
          taskReferenceName: "evaluate",
          type: "DECISION",
          inputParameters: {
            success: "${poll_status.output.success}",
          },
          caseValueParam: "success",
          caseExpression: {
            true: [
              {
                name: "success_handler",
                taskReferenceName: "on_success",
                type: "SIMPLE",
                inputParameters: {
                  run_id: "${trigger_job.output.run_id}",
                  status: "${poll_status.output.run_status}",
                },
              },
            ],
            false: [
              {
                name: "failure_handler",
                taskReferenceName: "on_failure",
                type: "SIMPLE",
                inputParameters: {
                  run_id: "${trigger_job.output.run_id}",
                  status: "${poll_status.output.run_status}",
                },
              },
            ],
          },
        },
      ],
      inputParameters: ["run_config", "tags"],
      outputParameters: {
        run_id: "${trigger_job.output.run_id}",
        final_status: "${poll_status.output.run_status}",
        success: "${poll_status.output.success}",
      },
    };

    return JSON.stringify(workflow, null, 2);
  }

  /**
   * Generate environment variables for orchestration
   */
  @func()
  generateEnvVars(): string {
    return `# Orchestration Configuration
# Auto-generated by Dagger Orchestration module

# Netflix Conductor
CONDUCTOR_SERVER_URL=${DEFAULT_CONDUCTOR_SERVER}
CONDUCTOR_API_URL=${DEFAULT_CONDUCTOR_SERVER}/api

# Dagster
DAGSTER_HOST=${DEFAULT_DAGSTER_HOST}
DAGSTER_PORT=${DEFAULT_DAGSTER_PORT}
DAGSTER_GRAPHQL_ENDPOINT=http://${DEFAULT_DAGSTER_HOST}:${DEFAULT_DAGSTER_PORT}/graphql
`;
  }

  /**
   * Apply orchestration client dependencies to a container
   */
  @func()
  instrumentContainer(container: Container): Container {
    return container.withExec([
      "pip", "install", "--quiet",
      "conductor-python", "httpx",
    ]);
  }
}
