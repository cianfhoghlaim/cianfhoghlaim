/**
 * Database Client Configuration
 *
 * Provides a singleton Drizzle ORM instance connected to PostgreSQL
 */

import { drizzle } from "drizzle-orm/node-postgres";
import { Pool } from "pg";
import * as schema from "./schema";

// Declare global to prevent multiple instances in development
declare global {
  var __db: ReturnType<typeof createDb> | undefined;
}

function createDb() {
  const connectionString = process.env.DATABASE_URL;

  if (!connectionString) {
    throw new Error(
      "DATABASE_URL environment variable is required. " +
      "Set it to your PostgreSQL connection string."
    );
  }

  const pool = new Pool({
    connectionString,
    max: 10, // Maximum number of clients in the pool
    idleTimeoutMillis: 30000,
    connectionTimeoutMillis: 2000,
  });

  // Log connection errors
  pool.on("error", (err) => {
    console.error("Unexpected error on idle client", err);
  });

  return drizzle(pool, { schema });
}

// Use singleton in development to prevent multiple connections during HMR
export const db = global.__db ?? createDb();

if (process.env.NODE_ENV !== "production") {
  global.__db = db;
}

// Re-export schema for convenience
export * from "./schema";

// Export types
export type Database = typeof db;
