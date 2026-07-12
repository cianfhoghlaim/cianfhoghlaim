/**
 * Vector & Graph Database Module
 *
 * Provides integration with:
 * - LanceDB (serverless vector database for embeddings)
 * - FalkorDB (graph + vector hybrid database)
 * - Qdrant (alternative vector database)
 */

import { dag, Container, Directory, object, func } from "@dagger.io/dagger";

// =============================================================================
// Types
// =============================================================================

export interface LanceDBConfig {
  uri: string;
  apiKey?: string;
  region?: string;
  s3Endpoint?: string;
}

export interface FalkorDBConfig {
  host: string;
  port: number;
  password?: string;
  database?: string;
}

export interface QdrantConfig {
  host: string;
  httpPort: number;
  grpcPort: number;
  apiKey?: string;
}

export interface VectorDBEndpoints {
  lancedb: LanceDBConfig;
  falkordb: FalkorDBConfig;
  qdrant: QdrantConfig;
}

// =============================================================================
// Default endpoints
// =============================================================================

// OLM proxy endpoints for private access (no SSO required)
const DEFAULT_LANCEDB_HOST = "http://pangolin.cianfhoghlaim.ie:8085";
const DEFAULT_LANCEDB_LOCAL = "http://localhost:8080";
// Public HTTPS endpoint (requires SSO)
const DEFAULT_LANCEDB_PUBLIC = "https://lancedb.cianfhoghlaim.ie";

// OLM proxy endpoint (Redis protocol)
const DEFAULT_FALKORDB_HOST = "pangolin.cianfhoghlaim.ie";
const DEFAULT_FALKORDB_LOCAL = "localhost";
const DEFAULT_FALKORDB_PORT = 6379;
// Public HTTPS endpoint (requires SSO) - for UI only
const DEFAULT_FALKORDB_PUBLIC = "https://falkordb.cianfhoghlaim.ie";

// OLM proxy endpoint (HTTP/gRPC)
const DEFAULT_QDRANT_HOST = "pangolin.cianfhoghlaim.ie";
const DEFAULT_QDRANT_LOCAL = "localhost";
const DEFAULT_QDRANT_HTTP_PORT = 6333;
const DEFAULT_QDRANT_GRPC_PORT = 6334;
// Public HTTPS endpoint (requires SSO)
const DEFAULT_QDRANT_PUBLIC = "https://qdrant.cianfhoghlaim.ie";

@object()
export class VectorDB {
  /**
   * Get LanceDB configuration
   */
  @func()
  getLanceDBConfig(local: boolean = false): LanceDBConfig {
    return {
      uri: local ? DEFAULT_LANCEDB_LOCAL : DEFAULT_LANCEDB_HOST,
    };
  }

  /**
   * Get FalkorDB configuration
   */
  @func()
  getFalkorDBConfig(local: boolean = false): FalkorDBConfig {
    return {
      host: local ? DEFAULT_FALKORDB_LOCAL : DEFAULT_FALKORDB_HOST,
      port: DEFAULT_FALKORDB_PORT,
    };
  }

  /**
   * Get Qdrant configuration
   */
  @func()
  getQdrantConfig(local: boolean = false): QdrantConfig {
    return {
      host: local ? DEFAULT_QDRANT_LOCAL : DEFAULT_QDRANT_HOST,
      httpPort: DEFAULT_QDRANT_HTTP_PORT,
      grpcPort: DEFAULT_QDRANT_GRPC_PORT,
    };
  }

  /**
   * Get all vector DB endpoints
   */
  @func()
  getAllEndpoints(local: boolean = false): VectorDBEndpoints {
    return {
      lancedb: this.getLanceDBConfig(local),
      falkordb: this.getFalkorDBConfig(local),
      qdrant: this.getQdrantConfig(local),
    };
  }

  /**
   * Test LanceDB connection
   */
  @func()
  async testLanceDBConnection(uri?: string): Promise<boolean> {
    const url = uri || DEFAULT_LANCEDB_HOST;

    try {
      const result = await dag
        .container()
        .from("curlimages/curl:latest")
        .withExec(["curl", "-sf", url])
        .stdout();

      return result.length > 0;
    } catch {
      return false;
    }
  }

  /**
   * Test FalkorDB connection
   */
  @func()
  async testFalkorDBConnection(host?: string, port?: number): Promise<boolean> {
    const h = host || DEFAULT_FALKORDB_HOST;
    const p = port || DEFAULT_FALKORDB_PORT;

    try {
      const result = await dag
        .container()
        .from("redis:alpine")
        .withExec(["redis-cli", "-h", h, "-p", String(p), "PING"])
        .stdout();

      return result.trim() === "PONG";
    } catch {
      return false;
    }
  }

  /**
   * Test Qdrant connection
   */
  @func()
  async testQdrantConnection(host?: string, port?: number): Promise<boolean> {
    const h = host || DEFAULT_QDRANT_HOST;
    const p = port || DEFAULT_QDRANT_HTTP_PORT;

    try {
      const result = await dag
        .container()
        .from("curlimages/curl:latest")
        .withExec(["curl", "-sf", `http://${h}:${p}/health`])
        .stdout();

      return result.length > 0;
    } catch {
      return false;
    }
  }

  /**
   * Execute a Cypher query on FalkorDB
   */
  @func()
  async executeGraphQuery(
    cypher: string,
    graphName: string = "curriculum",
    host?: string,
    port?: number,
    password?: string
  ): Promise<string> {
    const h = host || DEFAULT_FALKORDB_HOST;
    const p = port || DEFAULT_FALKORDB_PORT;

    const authArgs = password ? ["-a", password] : [];

    try {
      const result = await dag
        .container()
        .from("redis:alpine")
        .withExec([
          "redis-cli",
          "-h", h,
          "-p", String(p),
          ...authArgs,
          "GRAPH.QUERY",
          graphName,
          cypher,
        ])
        .stdout();

      return result;
    } catch (error) {
      return `Error: ${error instanceof Error ? error.message : "Unknown error"}`;
    }
  }

  /**
   * Generate Python client code for vector databases
   */
  @func()
  generatePythonClient(appName: string): string {
    return `# ${appName} - Vector Database Client
# Auto-generated by Dagger VectorDB module

import os
from typing import Any, Optional

import lancedb
import redis
from qdrant_client import QdrantClient


# =============================================================================
# LanceDB Client
# =============================================================================

def get_lancedb_client(uri: Optional[str] = None) -> lancedb.DBConnection:
    """Get LanceDB connection."""
    db_uri = uri or os.environ.get("LANCEDB_URI", "${DEFAULT_LANCEDB_HOST}")
    return lancedb.connect(db_uri)


def create_lance_table(
    name: str,
    data: list[dict],
    mode: str = "overwrite",
    uri: Optional[str] = None,
):
    """Create or update a LanceDB table."""
    db = get_lancedb_client(uri)
    return db.create_table(name, data, mode=mode)


def search_lance_table(
    table_name: str,
    query_vector: list[float],
    limit: int = 10,
    uri: Optional[str] = None,
):
    """Search a LanceDB table."""
    db = get_lancedb_client(uri)
    table = db.open_table(table_name)
    return table.search(query_vector).limit(limit).to_list()


# =============================================================================
# FalkorDB Client
# =============================================================================

def get_falkordb_client(
    host: Optional[str] = None,
    port: Optional[int] = None,
    password: Optional[str] = None,
) -> redis.Redis:
    """Get FalkorDB (Redis) connection."""
    return redis.Redis(
        host=host or os.environ.get("FALKORDB_HOST", "${DEFAULT_FALKORDB_HOST}"),
        port=port or int(os.environ.get("FALKORDB_PORT", "${DEFAULT_FALKORDB_PORT}")),
        password=password or os.environ.get("FALKORDB_PASSWORD"),
        decode_responses=True,
    )


def execute_cypher(
    query: str,
    graph_name: str = "curriculum",
    host: Optional[str] = None,
    port: Optional[int] = None,
    password: Optional[str] = None,
) -> list[Any]:
    """Execute a Cypher query on FalkorDB."""
    client = get_falkordb_client(host, port, password)
    result = client.execute_command("GRAPH.QUERY", graph_name, query)
    return result


def create_curriculum_node(
    node_type: str,
    properties: dict[str, Any],
    graph_name: str = "curriculum",
    host: Optional[str] = None,
):
    """Create a curriculum node in FalkorDB."""
    prop_parts = [key + ": $" + key for key in properties.keys()]
    props = ", ".join(prop_parts)
    query = f"CREATE (n:{node_type} {{{props}}}) RETURN n"
    return execute_cypher(query, graph_name, host)


def find_prerequisite_chain(
    topic_name: str,
    graph_name: str = "curriculum",
    host: Optional[str] = None,
):
    """Find the prerequisite chain for a curriculum topic."""
    query = f'''
    MATCH path = (start:Topic {{name: "{topic_name}"}})-[:REQUIRES*]->(prereq:Topic)
    RETURN path
    '''
    return execute_cypher(query, graph_name, host)


# =============================================================================
# Qdrant Client
# =============================================================================

def get_qdrant_client(
    host: Optional[str] = None,
    port: Optional[int] = None,
    api_key: Optional[str] = None,
) -> QdrantClient:
    """Get Qdrant connection."""
    return QdrantClient(
        host=host or os.environ.get("QDRANT_HOST", "${DEFAULT_QDRANT_HOST}"),
        port=port or int(os.environ.get("QDRANT_PORT", "${DEFAULT_QDRANT_HTTP_PORT}")),
        api_key=api_key or os.environ.get("QDRANT_API_KEY"),
    )


def search_qdrant(
    collection_name: str,
    query_vector: list[float],
    limit: int = 10,
    host: Optional[str] = None,
):
    """Search a Qdrant collection."""
    client = get_qdrant_client(host)
    return client.search(
        collection_name=collection_name,
        query_vector=query_vector,
        limit=limit,
    )
`;
  }

  /**
   * Generate TypeScript client code for vector databases
   */
  @func()
  generateTypescriptClient(appName: string): string {
    return `// ${appName} - Vector Database Client
// Auto-generated by Dagger VectorDB module

import { connect as lanceConnect, Table } from "@lancedb/lancedb";
import { createClient as createRedisClient, RedisClientType } from "redis";
import { QdrantClient } from "@qdrant/js-client-rest";

// =============================================================================
// LanceDB Client
// =============================================================================

export async function getLanceDBClient(uri?: string) {
  const dbUri = uri || process.env.LANCEDB_URI || "${DEFAULT_LANCEDB_HOST}";
  return lanceConnect(dbUri);
}

export async function createLanceTable<T extends Record<string, unknown>>(
  name: string,
  data: T[],
  uri?: string
): Promise<Table> {
  const db = await getLanceDBClient(uri);
  return db.createTable(name, data, { mode: "overwrite" });
}

export async function searchLanceTable(
  tableName: string,
  queryVector: number[],
  limit = 10,
  uri?: string
) {
  const db = await getLanceDBClient(uri);
  const table = await db.openTable(tableName);
  return table.search(queryVector).limit(limit).toArray();
}

// =============================================================================
// FalkorDB Client
// =============================================================================

let falkordbClient: RedisClientType | null = null;

export async function getFalkorDBClient(
  host?: string,
  port?: number,
  password?: string
): Promise<RedisClientType> {
  if (falkordbClient) return falkordbClient;

  const h = host || process.env.FALKORDB_HOST || "${DEFAULT_FALKORDB_HOST}";
  const p = port || parseInt(process.env.FALKORDB_PORT || "${DEFAULT_FALKORDB_PORT}");
  const pw = password || process.env.FALKORDB_PASSWORD;

  falkordbClient = createRedisClient({
    socket: { host: h, port: p },
    password: pw,
  });

  await falkordbClient.connect();
  return falkordbClient;
}

export async function executeCypher(
  query: string,
  graphName = "curriculum",
  host?: string
): Promise<unknown> {
  const client = await getFalkorDBClient(host);
  return client.sendCommand(["GRAPH.QUERY", graphName, query]);
}

export async function findPrerequisiteChain(
  topicName: string,
  graphName = "curriculum",
  host?: string
) {
  const query = \`
    MATCH path = (start:Topic {name: "\${topicName}"})-[:REQUIRES*]->(prereq:Topic)
    RETURN path
  \`;
  return executeCypher(query, graphName, host);
}

// =============================================================================
// Qdrant Client
// =============================================================================

export function getQdrantClient(host?: string, port?: number, apiKey?: string) {
  return new QdrantClient({
    host: host || process.env.QDRANT_HOST || "${DEFAULT_QDRANT_HOST}",
    port: port || parseInt(process.env.QDRANT_PORT || "${DEFAULT_QDRANT_HTTP_PORT}"),
    apiKey: apiKey || process.env.QDRANT_API_KEY,
  });
}

export async function searchQdrant(
  collectionName: string,
  queryVector: number[],
  limit = 10,
  host?: string
) {
  const client = getQdrantClient(host);
  return client.search(collectionName, {
    vector: queryVector,
    limit,
  });
}
`;
  }

  /**
   * Generate environment variables for vector databases
   */
  @func()
  generateEnvVars(): string {
    return `# Vector Database Configuration
# Auto-generated by Dagger VectorDB module

# LanceDB - Serverless Vector Database
LANCEDB_URI=${DEFAULT_LANCEDB_HOST}
LANCEDB_API_KEY=  # Optional

# FalkorDB - Graph + Vector Hybrid
FALKORDB_HOST=${DEFAULT_FALKORDB_HOST}
FALKORDB_PORT=${DEFAULT_FALKORDB_PORT}
FALKORDB_PASSWORD=  # Set for production

# Qdrant - Vector Database
QDRANT_HOST=${DEFAULT_QDRANT_HOST}
QDRANT_PORT=${DEFAULT_QDRANT_HTTP_PORT}
QDRANT_API_KEY=  # Optional
`;
  }

  /**
   * Create curriculum knowledge graph in FalkorDB
   * Initializes the graph schema for Irish curriculum data
   */
  @func()
  async createCurriculumGraph(
    source: Directory,
    graphName: string = "curriculum",
    host?: string,
    port?: number,
    password?: string
  ): Promise<string> {
    const h = host || DEFAULT_FALKORDB_HOST;
    const p = port || DEFAULT_FALKORDB_PORT;
    const authArgs = password ? ["-a", password] : [];

    // Create indexes for common queries
    const indexQueries = [
      `CREATE INDEX ON :Subject(name)`,
      `CREATE INDEX ON :Topic(name)`,
      `CREATE INDEX ON :LearningOutcome(code)`,
      `CREATE INDEX ON :ExamPaper(year)`,
    ];

    const results: string[] = [];

    for (const query of indexQueries) {
      try {
        const result = await dag
          .container()
          .from("redis:alpine")
          .withExec([
            "redis-cli",
            "-h", h,
            "-p", String(p),
            ...authArgs,
            "GRAPH.QUERY",
            graphName,
            query,
          ])
          .stdout();
        results.push(`Index created: ${result.trim()}`);
      } catch (error) {
        results.push(`Index error: ${error instanceof Error ? error.message : "Unknown"}`);
      }
    }

    return results.join("\n");
  }

  /**
   * Apply vector DB client dependencies to a container
   */
  @func()
  instrumentContainer(
    container: Container,
    runtime: "bun" | "python"
  ): Container {
    if (runtime === "python") {
      return container.withExec([
        "pip", "install", "--quiet",
        "lancedb", "redis", "qdrant-client",
      ]);
    } else if (runtime === "bun") {
      return container.withExec([
        "bun", "add",
        "@lancedb/lancedb", "redis", "@qdrant/js-client-rest",
      ]);
    }
    return container;
  }
}
