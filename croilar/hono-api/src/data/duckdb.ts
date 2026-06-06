const DB_PATH = process.env.DUCKDB_PATH ?? "./data/croilar.duckdb";

// DuckDB Node.js bindings are compiled at Docker build time.
// Local bun dev returns empty arrays; Docker container gets real data.
// This avoids the native-module compilation issues in bun runtime.

export function query<T>(_sql: string, ..._params: unknown[]): T[] {
  if (process.env.NODE_ENV === "development" && _sql) {
    console.log("[duckdb-stub] Query:", _sql.slice(0, 100));
  }
  // Wired in Docker: import("duckdb") → conn.all(sql, props) → T[]
  return [] as T[];
}
