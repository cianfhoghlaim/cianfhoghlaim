import type { KVNamespace } from "@cloudflare/workers-types";

/**
 * KV Cache Helper Functions
 *
 * Provides typed helpers for working with Cloudflare KV storage
 */

export interface CacheOptions {
  /**
   * Time to live in seconds (minimum 60 seconds for KV)
   */
  ttl?: number;
  /**
   * Expiration timestamp (Unix timestamp in seconds)
   */
  expirationTtl?: number;
}

/**
 * Get a value from KV cache with automatic JSON parsing
 */
export async function getFromCache<T = any>(
  kv: KVNamespace,
  key: string
): Promise<T | null> {
  const value = await kv.get(key, "json");
  return value as T | null;
}

/**
 * Set a value in KV cache with automatic JSON stringification
 */
export async function setInCache<T = any>(
  kv: KVNamespace,
  key: string,
  value: T,
  options?: CacheOptions
): Promise<void> {
  const kvOptions: { expirationTtl?: number } = {};

  if (options?.ttl !== undefined) {
    // Cloudflare KV requires TTL >= 60 seconds
    const minTtl = 60;
    const ttl = options.ttl < minTtl ? minTtl : options.ttl;
    kvOptions.expirationTtl = ttl;
  } else if (options?.expirationTtl !== undefined) {
    kvOptions.expirationTtl = options.expirationTtl;
  }

  await kv.put(key, JSON.stringify(value), kvOptions);
}

/**
 * Get a text value from KV cache
 */
export async function getTextFromCache(
  kv: KVNamespace,
  key: string
): Promise<string | null> {
  return await kv.get(key, "text");
}

/**
 * Set a text value in KV cache
 */
export async function setTextInCache(
  kv: KVNamespace,
  key: string,
  value: string,
  options?: CacheOptions
): Promise<void> {
  const kvOptions: { expirationTtl?: number } = {};

  if (options?.ttl !== undefined) {
    const minTtl = 60;
    const ttl = options.ttl < minTtl ? minTtl : options.ttl;
    kvOptions.expirationTtl = ttl;
  } else if (options?.expirationTtl !== undefined) {
    kvOptions.expirationTtl = options.expirationTtl;
  }

  await kv.put(key, value, kvOptions);
}

/**
 * Delete a value from KV cache
 */
export async function deleteFromCache(
  kv: KVNamespace,
  key: string
): Promise<void> {
  await kv.delete(key);
}

/**
 * Check if a key exists in KV cache
 */
export async function existsInCache(
  kv: KVNamespace,
  key: string
): Promise<boolean> {
  const value = await kv.get(key);
  return value !== null;
}

/**
 * List keys in KV cache with optional prefix
 */
export async function listCacheKeys(
  kv: KVNamespace,
  prefix?: string,
  limit?: number
): Promise<string[]> {
  const list = await kv.list({ prefix, limit });
  return list.keys.map(k => k.name);
}
