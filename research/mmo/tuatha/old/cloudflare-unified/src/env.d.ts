import type { D1Database, KVNamespace, R2Bucket, Ai } from "@cloudflare/workers-types";

/**
 * Cloudflare bindings available in the worker environment
 */
export interface CloudflareBindings {
  /**
   * D1 Database binding for SQLite at the edge
   */
  DATABASE: D1Database;

  /**
   * KV Namespace binding for caching and secondary storage
   */
  CACHE: KVNamespace;

  /**
   * R2 Bucket binding for object storage
   */
  FILES: R2Bucket;

  /**
   * Workers AI binding for running AI models at the edge
   */
  AI: Ai;
}

/**
 * TypeScript module augmentation for process.env
 */
declare global {
  namespace NodeJS {
    interface ProcessEnv extends CloudflareBindings {
      /**
       * Better Auth secret for signing tokens
       */
      BETTER_AUTH_SECRET?: string;

      /**
       * Better Auth base URL for callbacks
       */
      BETTER_AUTH_URL?: string;

      /**
       * GitHub OAuth client ID
       */
      GITHUB_CLIENT_ID?: string;

      /**
       * GitHub OAuth client secret
       */
      GITHUB_CLIENT_SECRET?: string;

      /**
       * Google OAuth client ID
       */
      GOOGLE_CLIENT_ID?: string;

      /**
       * Google OAuth client secret
       */
      GOOGLE_CLIENT_SECRET?: string;
    }
  }
}

export {};
