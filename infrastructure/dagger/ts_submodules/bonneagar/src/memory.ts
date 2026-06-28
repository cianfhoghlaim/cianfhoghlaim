/**
 * AI Memory Module
 *
 * Provides integration with:
 * - Cognee (AI memory and knowledge graph)
 * - Letta (MemGPT - agent persistent memory)
 * - Context Banking (AGENTS.md to archival memory)
 */

import { dag, Container, Directory, object, func } from "@dagger.io/dagger";

// =============================================================================
// Types
// =============================================================================

export interface CogneeConfig {
  host: string;
  port: number;
  apiKey?: string;
  graphProvider: "memgraph" | "neo4j" | "falkordb";
  vectorProvider: "lancedb" | "qdrant" | "weaviate";
}

export interface LettaConfig {
  host: string;
  port: number;
  apiKey?: string;
}

export interface AgentMemory {
  agentId: string;
  name: string;
  persona: string;
  archivalMemorySize: number;
  recallMemorySize: number;
}

export interface ContextBankingResult {
  documentsProcessed: number;
  chunksCreated: number;
  entitiesExtracted: number;
}

// =============================================================================
// Default endpoints
// =============================================================================

// OLM proxy endpoints for private access (no SSO required)
const DEFAULT_COGNEE_HOST = "http://pangolin.cianfhoghlaim.ie:8087";
const DEFAULT_COGNEE_LOCAL = "http://localhost:8001";
const DEFAULT_COGNEE_PORT = 8087;
// Public HTTPS endpoint (requires SSO)
const DEFAULT_COGNEE_PUBLIC = "https://cognee.cianfhoghlaim.ie";

const DEFAULT_LETTA_HOST = "https://letta.cianfhoghlaim.ie";
const DEFAULT_LETTA_LOCAL = "http://localhost:8283";
const DEFAULT_LETTA_PORT = 8283;

@object()
export class AIMemory {
  /**
   * Get Cognee configuration
   */
  @func()
  getCogneeConfig(local: boolean = false): CogneeConfig {
    return {
      host: local ? DEFAULT_COGNEE_LOCAL : DEFAULT_COGNEE_HOST,
      port: DEFAULT_COGNEE_PORT,
      graphProvider: "memgraph",
      vectorProvider: "lancedb",
    };
  }

  /**
   * Get Letta configuration
   */
  @func()
  getLettaConfig(local: boolean = false): LettaConfig {
    return {
      host: local ? DEFAULT_LETTA_LOCAL : DEFAULT_LETTA_HOST,
      port: DEFAULT_LETTA_PORT,
    };
  }

  /**
   * Test Cognee connection
   */
  @func()
  async testCogneeConnection(host?: string): Promise<boolean> {
    const url = host || DEFAULT_COGNEE_HOST;

    try {
      const result = await dag
        .container()
        .from("curlimages/curl:latest")
        .withExec(["curl", "-sf", `${url}/health`])
        .stdout();

      return result.length > 0;
    } catch {
      return false;
    }
  }

  /**
   * Test Letta connection
   */
  @func()
  async testLettaConnection(host?: string): Promise<boolean> {
    const url = host || DEFAULT_LETTA_HOST;

    try {
      const result = await dag
        .container()
        .from("curlimages/curl:latest")
        .withExec(["curl", "-sf", `${url}/v1/health`])
        .stdout();

      return result.length > 0;
    } catch {
      return false;
    }
  }

  /**
   * Ingest documents into Cognee
   */
  @func()
  async ingestDocuments(
    source: Directory,
    collection: string,
    host?: string
  ): Promise<string> {
    const url = host || DEFAULT_COGNEE_HOST;

    const container = dag
      .container()
      .from("python:3.12-slim")
      .withMountedDirectory("/workspace", source)
      .withWorkdir("/workspace")
      .withExec(["pip", "install", "--quiet", "cognee", "httpx"]);

    const script = `
import cognee
import asyncio
import os

async def main():
    # Configure Cognee
    cognee.config.set_llm_api_key(os.environ.get("LLM_API_KEY", ""))

    # Reset for clean ingestion
    await cognee.prune.prune_data()
    await cognee.prune.prune_system(metadata=True)

    # Add documents from workspace
    docs_added = 0
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith((".md", ".txt", ".pdf")):
                filepath = os.path.join(root, file)
                await cognee.add(filepath, "${collection}")
                docs_added += 1

    # Process and create knowledge graph
    await cognee.cognify()

    print(f"SUCCESS: Processed {docs_added} documents")
    return docs_added

asyncio.run(main())
`;

    try {
      const result = await container
        .withExec(["python", "-c", script])
        .stdout();

      return result;
    } catch (error) {
      return `Error: ${error instanceof Error ? error.message : "Unknown error"}`;
    }
  }

  /**
   * Query Cognee memory
   */
  @func()
  async queryMemory(query: string, host?: string): Promise<string> {
    const url = host || DEFAULT_COGNEE_HOST;

    try {
      const result = await dag
        .container()
        .from("curlimages/curl:latest")
        .withExec([
          "curl", "-sf",
          "-X", "POST",
          `${url}/v1/search`,
          "-H", "Content-Type: application/json",
          "-d", JSON.stringify({ query, top_k: 10 }),
        ])
        .stdout();

      return result;
    } catch (error) {
      return `Error: ${error instanceof Error ? error.message : "Unknown error"}`;
    }
  }

  /**
   * Create a Letta agent
   */
  @func()
  async createAgent(
    name: string,
    persona: string,
    host?: string
  ): Promise<string> {
    const url = host || DEFAULT_LETTA_HOST;

    try {
      const result = await dag
        .container()
        .from("curlimages/curl:latest")
        .withExec([
          "curl", "-sf",
          "-X", "POST",
          `${url}/v1/agents`,
          "-H", "Content-Type: application/json",
          "-d", JSON.stringify({
            name,
            persona,
            human: "A software engineer working on the Cianfhoghlaim educational platform.",
          }),
        ])
        .stdout();

      return result;
    } catch (error) {
      return `Error: ${error instanceof Error ? error.message : "Unknown error"}`;
    }
  }

  /**
   * Bank context to agent archival memory
   */
  @func()
  async bankContext(
    agentId: string,
    content: string,
    host?: string
  ): Promise<string> {
    const url = host || DEFAULT_LETTA_HOST;

    try {
      const result = await dag
        .container()
        .from("curlimages/curl:latest")
        .withExec([
          "curl", "-sf",
          "-X", "POST",
          `${url}/v1/agents/${agentId}/memory/archival`,
          "-H", "Content-Type: application/json",
          "-d", JSON.stringify({ text: content }),
        ])
        .stdout();

      return result;
    } catch (error) {
      return `Error: ${error instanceof Error ? error.message : "Unknown error"}`;
    }
  }

  /**
   * Retrieve context from agent archival memory
   */
  @func()
  async retrieveContext(
    agentId: string,
    query: string,
    host?: string
  ): Promise<string> {
    const url = host || DEFAULT_LETTA_HOST;

    try {
      const result = await dag
        .container()
        .from("curlimages/curl:latest")
        .withExec([
          "curl", "-sf",
          `${url}/v1/agents/${agentId}/memory/archival?query=${encodeURIComponent(query)}&count=10`,
        ])
        .stdout();

      return result;
    } catch (error) {
      return `Error: ${error instanceof Error ? error.message : "Unknown error"}`;
    }
  }

  /**
   * Bank project documentation (AGENTS.md files) to memory
   * Implements the Credits Strategy context banking pattern
   */
  @func()
  async bankProjectDocumentation(
    source: Directory,
    agentId?: string,
    host?: string
  ): Promise<string> {
    const container = dag
      .container()
      .from("python:3.12-slim")
      .withMountedDirectory("/workspace", source)
      .withWorkdir("/workspace")
      .withExec(["pip", "install", "--quiet", "httpx"]);

    const script = `
import os
import json
import httpx
import asyncio

LETTA_HOST = "${host || DEFAULT_LETTA_HOST}"
AGENT_ID = "${agentId || ""}"

async def main():
    results = {
        "files_processed": 0,
        "chunks_banked": 0,
        "errors": []
    }

    # Find all AGENTS.md, CLAUDE.md, README.md files
    doc_files = []
    for root, dirs, files in os.walk("."):
        # Skip common directories
        if any(skip in root for skip in ["node_modules", ".git", "__pycache__", ".venv"]):
            continue
        for file in files:
            if file in ["AGENTS.md", "CLAUDE.md", "README.md"]:
                doc_files.append(os.path.join(root, file))

    print(f"Found {len(doc_files)} documentation files")

    # Process each file
    for filepath in doc_files:
        try:
            with open(filepath, "r") as f:
                content = f.read()

            # Chunk content (simple chunking by headers)
            chunks = content.split("\\n## ")
            chunks = [chunks[0]] + ["## " + c for c in chunks[1:]]

            for chunk in chunks:
                if len(chunk.strip()) < 50:
                    continue

                # Bank to memory (if agent ID provided)
                if AGENT_ID:
                    async with httpx.AsyncClient() as client:
                        try:
                            await client.post(
                                f"{LETTA_HOST}/v1/agents/{AGENT_ID}/memory/archival",
                                json={"text": f"[Source: {filepath}]\\n\\n{chunk}"},
                                timeout=30.0
                            )
                            results["chunks_banked"] += 1
                        except Exception as e:
                            results["errors"].append(f"{filepath}: {str(e)}")

            results["files_processed"] += 1

        except Exception as e:
            results["errors"].append(f"{filepath}: {str(e)}")

    print(json.dumps(results, indent=2))

asyncio.run(main())
`;

    try {
      const result = await container
        .withExec(["python", "-c", script])
        .stdout();

      return result;
    } catch (error) {
      return `Error: ${error instanceof Error ? error.message : "Unknown error"}`;
    }
  }

  /**
   * Generate Python client code for AI memory services
   */
  @func()
  generatePythonClient(appName: string): string {
    return `# ${appName} - AI Memory Client
# Auto-generated by Dagger Memory module

import os
from typing import Any, Optional

import cognee
import httpx


# =============================================================================
# Cognee Client
# =============================================================================

COGNEE_HOST = os.environ.get("COGNEE_HOST", "${DEFAULT_COGNEE_HOST}")


async def configure_cognee(llm_api_key: Optional[str] = None):
    """Configure Cognee with API keys."""
    key = llm_api_key or os.environ.get("LLM_API_KEY")
    if key:
        cognee.config.set_llm_api_key(key)


async def add_to_memory(content: str, collection: str = "default"):
    """Add content to Cognee memory."""
    await cognee.add(content, collection)
    await cognee.cognify()


async def search_memory(query: str, top_k: int = 10) -> list[dict[str, Any]]:
    """Search Cognee memory."""
    results = await cognee.search(query, top_k=top_k)
    return results


async def get_knowledge_graph(query: str) -> dict[str, Any]:
    """Get knowledge graph for a query."""
    results = await cognee.search(
        query,
        search_type="GRAPH_SEARCH"
    )
    return results


# =============================================================================
# Letta Client
# =============================================================================

LETTA_HOST = os.environ.get("LETTA_HOST", "${DEFAULT_LETTA_HOST}")


async def create_letta_agent(
    name: str,
    persona: str,
    human: str = "A user of the ${appName} application.",
) -> dict[str, Any]:
    """Create a new Letta agent."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{LETTA_HOST}/v1/agents",
            json={
                "name": name,
                "persona": persona,
                "human": human,
            },
        )
        response.raise_for_status()
        return response.json()


async def chat_with_agent(
    agent_id: str,
    message: str,
) -> dict[str, Any]:
    """Send a message to a Letta agent."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{LETTA_HOST}/v1/agents/{agent_id}/messages",
            json={"message": message, "role": "user"},
        )
        response.raise_for_status()
        return response.json()


async def bank_to_archival(
    agent_id: str,
    content: str,
) -> dict[str, Any]:
    """Bank content to agent archival memory."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{LETTA_HOST}/v1/agents/{agent_id}/memory/archival",
            json={"text": content},
        )
        response.raise_for_status()
        return response.json()


async def search_archival(
    agent_id: str,
    query: str,
    count: int = 10,
) -> list[dict[str, Any]]:
    """Search agent archival memory."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{LETTA_HOST}/v1/agents/{agent_id}/memory/archival",
            params={"query": query, "count": count},
        )
        response.raise_for_status()
        return response.json()
`;
  }

  /**
   * Generate TypeScript client code for AI memory services
   */
  @func()
  generateTypescriptClient(appName: string): string {
    return `// ${appName} - AI Memory Client
// Auto-generated by Dagger Memory module

const COGNEE_HOST = process.env.COGNEE_HOST || "${DEFAULT_COGNEE_HOST}";
const LETTA_HOST = process.env.LETTA_HOST || "${DEFAULT_LETTA_HOST}";

// =============================================================================
// Cognee Client
// =============================================================================

export async function addToMemory(content: string, collection = "default") {
  const response = await fetch(\`\${COGNEE_HOST}/v1/add\`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content, collection }),
  });

  if (!response.ok) {
    throw new Error(\`Cognee error: \${response.status}\`);
  }

  return response.json();
}

export async function searchMemory(query: string, topK = 10) {
  const response = await fetch(\`\${COGNEE_HOST}/v1/search\`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, top_k: topK }),
  });

  if (!response.ok) {
    throw new Error(\`Cognee error: \${response.status}\`);
  }

  return response.json();
}

// =============================================================================
// Letta Client
// =============================================================================

export async function createLettaAgent(
  name: string,
  persona: string,
  human = "A user of the ${appName} application."
) {
  const response = await fetch(\`\${LETTA_HOST}/v1/agents\`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, persona, human }),
  });

  if (!response.ok) {
    throw new Error(\`Letta error: \${response.status}\`);
  }

  return response.json();
}

export async function chatWithAgent(agentId: string, message: string) {
  const response = await fetch(\`\${LETTA_HOST}/v1/agents/\${agentId}/messages\`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, role: "user" }),
  });

  if (!response.ok) {
    throw new Error(\`Letta error: \${response.status}\`);
  }

  return response.json();
}

export async function bankToArchival(agentId: string, content: string) {
  const response = await fetch(
    \`\${LETTA_HOST}/v1/agents/\${agentId}/memory/archival\`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: content }),
    }
  );

  if (!response.ok) {
    throw new Error(\`Letta error: \${response.status}\`);
  }

  return response.json();
}

export async function searchArchival(
  agentId: string,
  query: string,
  count = 10
) {
  const params = new URLSearchParams({ query, count: String(count) });
  const response = await fetch(
    \`\${LETTA_HOST}/v1/agents/\${agentId}/memory/archival?\${params}\`
  );

  if (!response.ok) {
    throw new Error(\`Letta error: \${response.status}\`);
  }

  return response.json();
}
`;
  }

  /**
   * Generate environment variables for AI memory services
   */
  @func()
  generateEnvVars(): string {
    return `# AI Memory Configuration
# Auto-generated by Dagger Memory module

# Cognee - Knowledge Graph Memory
COGNEE_HOST=${DEFAULT_COGNEE_HOST}
COGNEE_API_KEY=  # Optional

# Letta - Agent Persistent Memory
LETTA_HOST=${DEFAULT_LETTA_HOST}
LETTA_API_KEY=  # Optional

# LLM for memory processing (used by Cognee)
LLM_API_KEY=  # Required for Cognee cognification
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
`;
  }

  /**
   * Apply memory client dependencies to a container
   */
  @func()
  instrumentContainer(
    container: Container,
    runtime: "bun" | "python"
  ): Container {
    if (runtime === "python") {
      return container.withExec([
        "pip", "install", "--quiet",
        "cognee", "httpx",
      ]);
    }
    // TypeScript doesn't have official cognee SDK, use httpx-style fetch
    return container;
  }
}
