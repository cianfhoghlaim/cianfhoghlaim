import { drizzle } from "drizzle-orm/postgres-js";
import postgres from "postgres";
import { env } from "@cianfhoghlaim/env/server";

const client = postgres(env.DUCKLAKE_POSTGRES_URI);
export const db = drizzle({ client });

export * from "./schema/examinations";
export * from "./schema/curriculum";
export * from "./schema/auth";
