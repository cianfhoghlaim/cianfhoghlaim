/**
 * Docker Service Orchestration Module
 *
 * Manages infrastructure services (postgres, redis, etc.) with health checks.
 */

import { dag, Container, Service, object, func } from "@dagger.io/dagger";

export interface ServiceConfig {
  image: string;
  port: number;
  healthCheck?: string[];
  envVars: Record<string, string>;
}

/**
 * Pre-configured service definitions
 */
export const SERVICES: Record<string, ServiceConfig> = {
  postgres: {
    image: "postgres:16-alpine",
    port: 5432,
    healthCheck: ["pg_isready", "-U", "postgres"],
    envVars: {
      POSTGRES_USER: "postgres",
      POSTGRES_PASSWORD: "postgres",
      POSTGRES_DB: "cianfhoghlaim",
    },
  },
  redis: {
    image: "redis:7-alpine",
    port: 6379,
    healthCheck: ["redis-cli", "ping"],
    envVars: {},
  },
  dragonfly: {
    image: "docker.dragonflydb.io/dragonflydb/dragonfly:latest",
    port: 6379,
    envVars: {},
  },
  memgraph: {
    image: "memgraph/memgraph-platform:latest",
    port: 7687,
    envVars: {
      MEMGRAPH_USER: "memgraph",
      MEMGRAPH_PASSWORD: "memgraph",
    },
  },
};

@object()
export class ServiceOrchestrator {
  /**
   * Create a service from a predefined config
   */
  @func()
  createService(name: string): Service {
    const config = SERVICES[name];
    if (!config) {
      throw new Error("Unknown service: " + name);
    }

    let container = dag.container().from(config.image);

    for (const [key, value] of Object.entries(config.envVars)) {
      container = container.withEnvVariable(key, value);
    }

    container = container.withExposedPort(config.port);

    return container.asService();
  }

  /**
   * Create PostgreSQL service
   */
  @func()
  createPostgres(database?: string): Service {
    return dag
      .container()
      .from("postgres:16-alpine")
      .withEnvVariable("POSTGRES_USER", "postgres")
      .withEnvVariable("POSTGRES_PASSWORD", "postgres")
      .withEnvVariable("POSTGRES_DB", database || "cianfhoghlaim")
      .withExposedPort(5432)
      .asService();
  }

  /**
   * Create Redis service
   */
  @func()
  createRedis(): Service {
    return dag
      .container()
      .from("redis:7-alpine")
      .withExposedPort(6379)
      .asService();
  }

  /**
   * Create Dragonfly (Redis-compatible) service
   */
  @func()
  createDragonfly(): Service {
    return dag
      .container()
      .from("docker.dragonflydb.io/dragonflydb/dragonfly:latest")
      .withExposedPort(6379)
      .asService();
  }

  /**
   * Create Memgraph service
   */
  @func()
  createMemgraph(): Service {
    return dag
      .container()
      .from("memgraph/memgraph-platform:latest")
      .withEnvVariable("MEMGRAPH_USER", "memgraph")
      .withEnvVariable("MEMGRAPH_PASSWORD", "memgraph")
      .withExposedPort(7687)
      .withExposedPort(7444)
      .asService();
  }

  /**
   * Create Langfuse observability service
   */
  @func()
  createLangfuse(postgresService: Service): Service {
    return dag
      .container()
      .from("langfuse/langfuse:latest")
      .withServiceBinding("postgres", postgresService)
      .withEnvVariable("DATABASE_URL", "postgresql://postgres:postgres@postgres:5432/langfuse")
      .withEnvVariable("NEXTAUTH_SECRET", "dev-secret")
      .withEnvVariable("NEXTAUTH_URL", "http://localhost:3000")
      .withEnvVariable("SALT", "dev-salt")
      .withExposedPort(3000)
      .asService();
  }

  /**
   * Get the connection string for a service
   */
  @func()
  getConnectionString(serviceName: string, host: string = "localhost"): string {
    switch (serviceName) {
      case "postgres":
        return "postgresql://postgres:postgres@" + host + ":5432/cianfhoghlaim";
      case "redis":
      case "dragonfly":
        return "redis://" + host + ":6379";
      case "memgraph":
        return "bolt://" + host + ":7687";
      default:
        throw new Error("Unknown service: " + serviceName);
    }
  }

  /**
   * List available services
   */
  @func()
  listServices(): string[] {
    return ["postgres", "redis", "dragonfly", "memgraph"];
  }
}
