/**
 * LRU-based session store for Stagehand instances.
 * Manages browser sessions with automatic TTL expiration.
 */

import { LRUCache } from "lru-cache";
import { v4 as uuidv4 } from "uuid";
import type { Stagehand } from "@browserbasehq/stagehand";

export interface SessionInfo {
  stagehand: Stagehand;
  createdAt: Date;
  lastAccessedAt: Date;
  env: "LOCAL" | "BROWSERBASE";
  modelName: string;
}

export interface SessionStoreOptions {
  maxCapacity?: number;
  ttlMs?: number;
}

export class SessionStore {
  private cache: LRUCache<string, SessionInfo>;
  private cleanupInterval: NodeJS.Timeout | null = null;

  constructor(options: SessionStoreOptions = {}) {
    const maxCapacity = options.maxCapacity ?? 10;
    const ttlMs = options.ttlMs ?? 300_000; // 5 minutes default

    this.cache = new LRUCache<string, SessionInfo>({
      max: maxCapacity,
      ttl: ttlMs,
      dispose: async (value, key) => {
        console.log(`[SessionStore] Disposing session: ${key}`);
        try {
          await value.stagehand.close();
        } catch (error) {
          console.error(`[SessionStore] Error closing session ${key}:`, error);
        }
      },
      updateAgeOnGet: true,
    });

    // Periodic cleanup check
    this.cleanupInterval = setInterval(() => {
      this.cache.purgeStale();
    }, 60_000);
  }

  async createSession(
    stagehand: Stagehand,
    env: "LOCAL" | "BROWSERBASE",
    modelName: string
  ): Promise<string> {
    const sessionId = uuidv4();
    const now = new Date();

    this.cache.set(sessionId, {
      stagehand,
      createdAt: now,
      lastAccessedAt: now,
      env,
      modelName,
    });

    console.log(`[SessionStore] Created session: ${sessionId} (env: ${env}, model: ${modelName})`);
    return sessionId;
  }

  getSession(sessionId: string): SessionInfo | undefined {
    const session = this.cache.get(sessionId);
    if (session) {
      session.lastAccessedAt = new Date();
    }
    return session;
  }

  getStagehand(sessionId: string): Stagehand | undefined {
    return this.getSession(sessionId)?.stagehand;
  }

  async closeSession(sessionId: string): Promise<boolean> {
    const session = this.cache.get(sessionId);
    if (!session) {
      return false;
    }

    try {
      await session.stagehand.close();
    } catch (error) {
      console.error(`[SessionStore] Error closing session ${sessionId}:`, error);
    }

    return this.cache.delete(sessionId);
  }

  async upgradeToCloud(
    sessionId: string,
    newStagehand: Stagehand
  ): Promise<boolean> {
    const session = this.cache.get(sessionId);
    if (!session) {
      return false;
    }

    // Close old local session
    try {
      await session.stagehand.close();
    } catch (error) {
      console.error(`[SessionStore] Error closing local session for upgrade:`, error);
    }

    // Update with cloud session
    session.stagehand = newStagehand;
    session.env = "BROWSERBASE";
    session.lastAccessedAt = new Date();

    console.log(`[SessionStore] Upgraded session ${sessionId} to BROWSERBASE`);
    return true;
  }

  getStats(): {
    activeSessions: number;
    maxCapacity: number;
    sessions: Array<{
      sessionId: string;
      env: "LOCAL" | "BROWSERBASE";
      modelName: string;
      ageMs: number;
    }>;
  } {
    const sessions: Array<{
      sessionId: string;
      env: "LOCAL" | "BROWSERBASE";
      modelName: string;
      ageMs: number;
    }> = [];

    const now = Date.now();
    for (const [sessionId, info] of this.cache.entries()) {
      sessions.push({
        sessionId,
        env: info.env,
        modelName: info.modelName,
        ageMs: now - info.createdAt.getTime(),
      });
    }

    return {
      activeSessions: this.cache.size,
      maxCapacity: this.cache.max,
      sessions,
    };
  }

  async shutdown(): Promise<void> {
    if (this.cleanupInterval) {
      clearInterval(this.cleanupInterval);
      this.cleanupInterval = null;
    }

    // Close all sessions
    const closePromises: Promise<void>[] = [];
    for (const [, info] of this.cache.entries()) {
      closePromises.push(
        info.stagehand.close().catch((e) => {
          console.error("[SessionStore] Error during shutdown:", e);
        })
      );
    }

    await Promise.all(closePromises);
    this.cache.clear();
    console.log("[SessionStore] Shutdown complete");
  }
}
