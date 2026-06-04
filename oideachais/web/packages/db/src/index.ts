import { drizzle } from "drizzle-orm/postgres-js";
import postgres from "postgres";
import { env } from "@oideachais/env/server";

const client = postgres(env.DUCKLAKE_POSTGRES_URI);
export const db = drizzle({ client });

export * from "./schema/examinations";
export * from "./schema/curriculum";
export * from "./schema/auth";
