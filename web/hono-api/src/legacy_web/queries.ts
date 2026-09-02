interface SqlRow {
  [key: string]: string | number | boolean | null;
}

export async function runDuckLakeQuery(
  sql: string,
  limit: number,
): Promise<SqlRow[]> {
  const useMotherduck =
    (process.env.MOTHERDUCK_ENABLED ?? "false").toLowerCase() === "true";

  if (!useMotherduck) {
    // Local DuckDB not wired in Phase 1 API server.
    // The DLT pipeline writes to DuckLake (Garage S3 + PostgreSQL).
    // The frontend should point to MOTHERDUCK_ENABLED=true for now.
    return [];
  }

  const token = process.env.MOTHERDUCK_TOKEN;
  if (!token) throw new Error("MOTHERDUCK_TOKEN required when MOTHERDUCK_ENABLED=true");
  const res = await fetch("https://api.motherduck.com/v1/query", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ sql: `${sql} LIMIT ${limit}` }),
  });
  if (!res.ok) throw new Error(`MotherDuck query ${res.status}`);
  const payload = (await res.json()) as { rows?: SqlRow[] };
  return payload.rows ?? [];
}
