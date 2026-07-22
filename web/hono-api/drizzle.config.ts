import { defineConfig } from "drizzle-kit";

export default defineConfig({
  schema: "./src/db/schema.ts",
  out: "./drizzle",
  dialect: "postgresql",
  dbCredentials: {
    url: process.env.DATABASE_URL ?? "postgres://croilar:devpassword@localhost:5434/croilar",
    ssl: process.env.DATABASE_URL?.includes("psdb.cloud") ? "require" : false,
  },
  schemaFilter: ["better_auth", "public"],
  verbose: true,
});
