import { drizzle } from "drizzle-orm/d1";
import type { D1Database } from "@cloudflare/workers-types";
import { schema } from "./schema";

/**
 * Initialize Drizzle ORM with D1 database
 *
 * @param database - Cloudflare D1 database binding
 * @returns Drizzle database instance
 */
export function initDatabase(database: D1Database) {
  return drizzle(database, { schema, logger: true });
}

// Re-export schema and drizzle utilities
export * from "./schema";
export * from "drizzle-orm";
