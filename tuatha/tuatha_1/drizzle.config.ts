import { defineConfig } from "drizzle-kit";
import "dotenv/config";

export default defineConfig({
  schema: "./src/db/schema.ts",
  out: "./drizzle",
  dialect: "postgresql",
  dbCredentials: {
    url: process.env.DATABASE_URL as string,
  },
  // Enable verbose logging in development
  verbose: process.env.NODE_ENV !== "production",
  // Strict mode for safer migrations
  strict: true,
});
