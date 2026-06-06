import { drizzle } from "drizzle-orm/postgres-js";
import postgres from "postgres";
import * as schema from "./schema";

const connectionString = process.env.DATABASE_URL;
if (!connectionString) {
  throw new Error("DATABASE_URL is required for BetterAuth Drizzle adapter");
}

// pgBouncer / PlanetScale-safe options:
// - no_prepare: true  — required for transaction-mode pooling
// - max: 1 per worker  — Hono runs single-threaded
// - ssl: 'require'      — PlanetScale enforces TLS
export const client = postgres(connectionString, {
  prepare: false,
  max: 1,
  ssl: connectionString.includes("psdb.cloud") ? "require" : false,
});

export const db = drizzle(client, { schema });
export type DB = typeof db;
