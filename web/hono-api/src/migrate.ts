import { drizzle } from "drizzle-orm/postgres-js";
import { migrate } from "drizzle-orm/postgres-js/migrator";
import postgres from "postgres";

const connectionString = process.env.DATABASE_URL;
if (!connectionString) {
  console.error("DATABASE_URL is required");
  process.exit(1);
}

const client = postgres(connectionString, { prepare: false, max: 1 });
const db = drizzle(client);

console.log("[migrate] Running Drizzle migrations against", connectionString.replace(/:[^:@/]*@/, ":***@"));

await migrate(db, { migrationsFolder: "./drizzle" });
console.log("[migrate] Done");
await client.end();
