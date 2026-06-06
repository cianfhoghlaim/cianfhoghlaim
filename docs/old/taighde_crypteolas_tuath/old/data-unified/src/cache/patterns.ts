import * as cache from './redis';

/**
 * Cache-aside (lazy loading) pattern
 * Read from cache, fallback to data source if miss, then populate cache
 */
export async function cacheAside<T>(
  key: string,
  fetchFn: () => Promise<T>,
  ttl?: number
): Promise<T> {
  // Try to get from cache
  const cached = await cache.get<T>(key);
  if (cached !== null) {
    console.log(`Cache hit: ${key}`);
    return cached;
  }

  // Cache miss - fetch from source
  console.log(`Cache miss: ${key}`);
  const data = await fetchFn();

  // Store in cache
  await cache.set(key, data, ttl);

  return data;
}

/**
 * Read-through cache pattern
 * Similar to cache-aside but the cache handles the data fetch
 */
export async function readThrough<T>(
  key: string,
  fetchFn: () => Promise<T>,
  options?: {
    ttl?: number;
    forceRefresh?: boolean;
  }
): Promise<T> {
  if (!options?.forceRefresh) {
    const cached = await cache.get<T>(key);
    if (cached !== null) {
      return cached;
    }
  }

  const data = await fetchFn();
  await cache.set(key, data, options?.ttl);
  return data;
}

/**
 * Write-through cache pattern
 * Write to cache and data source simultaneously
 */
export async function writeThrough<T>(
  key: string,
  value: T,
  writeFn: (value: T) => Promise<void>,
  ttl?: number
): Promise<void> {
  // Write to both cache and data source
  await Promise.all([
    cache.set(key, value, ttl),
    writeFn(value)
  ]);
}

/**
 * Write-behind (write-back) cache pattern
 * Write to cache immediately, write to data source asynchronously
 */
export async function writeBehind<T>(
  key: string,
  value: T,
  writeFn: (value: T) => Promise<void>,
  ttl?: number
): Promise<void> {
  // Write to cache immediately
  await cache.set(key, value, ttl);

  // Write to data source asynchronously (non-blocking)
  writeFn(value).catch((err) => {
    console.error(`Write-behind error for key ${key}:`, err);
  });
}

/**
 * Cache stampede prevention using locks
 */
export async function withLock<T>(
  key: string,
  fetchFn: () => Promise<T>,
  options?: {
    ttl?: number;
    lockTimeout?: number;
  }
): Promise<T> {
  const lockKey = `lock:${key}`;
  const lockTimeout = options?.lockTimeout || 10; // seconds

  // Try to get from cache first
  const cached = await cache.get<T>(key);
  if (cached !== null) {
    return cached;
  }

  // Try to acquire lock
  const lockAcquired = await cache.redis.set(
    lockKey,
    '1',
    'EX',
    lockTimeout,
    'NX'
  );

  if (lockAcquired === 'OK') {
    try {
      // We have the lock - fetch and cache
      const data = await fetchFn();
      await cache.set(key, data, options?.ttl);
      return data;
    } finally {
      // Release lock
      await cache.del(lockKey);
    }
  } else {
    // Someone else has the lock - wait and retry
    await new Promise((resolve) => setTimeout(resolve, 100));
    return withLock(key, fetchFn, options);
  }
}

/**
 * Time-based cache invalidation
 */
export async function cacheWithExpiry<T>(
  key: string,
  value: T,
  expiryDate: Date
): Promise<void> {
  const expiryTimestamp = Math.floor(expiryDate.getTime() / 1000);
  await cache.setWithExpiry(key, value, expiryTimestamp);
}

/**
 * Batch cache operations
 */
export async function cacheBatch<T>(
  items: Array<{ key: string; value: T }>,
  ttl?: number
): Promise<void> {
  // For items without TTL, use MSET
  const noTtlItems: Record<string, T> = {};
  const ttlItems: Array<{ key: string; value: T }> = [];

  items.forEach((item) => {
    if (ttl) {
      ttlItems.push(item);
    } else {
      noTtlItems[item.key] = item.value;
    }
  });

  await Promise.all([
    Object.keys(noTtlItems).length > 0 ? cache.mset(noTtlItems) : Promise.resolve(),
    ...ttlItems.map((item) => cache.set(item.key, item.value, ttl)),
  ]);
}

/**
 * Invalidate cache by pattern
 */
export async function invalidatePattern(pattern: string): Promise<number> {
  const keys = await cache.keys(pattern);
  if (keys.length === 0) return 0;
  return cache.del(...keys);
}

/**
 * Refresh cache in background
 */
export function refreshInBackground<T>(
  key: string,
  fetchFn: () => Promise<T>,
  ttl?: number
): void {
  fetchFn()
    .then((data) => cache.set(key, data, ttl))
    .catch((err) => console.error(`Background refresh error for ${key}:`, err));
}

/**
 * Cache with stale-while-revalidate pattern
 */
export async function staleWhileRevalidate<T>(
  key: string,
  fetchFn: () => Promise<T>,
  options?: {
    ttl?: number;
    staleTtl?: number; // How long to serve stale data
  }
): Promise<T> {
  const cached = await cache.get<T>(key);
  const ttlRemaining = await cache.ttl(key);

  // If cache is fresh, return it
  if (cached !== null && ttlRemaining > 0) {
    return cached;
  }

  // If cache is stale but exists, return it and refresh in background
  if (cached !== null && ttlRemaining <= 0) {
    refreshInBackground(key, fetchFn, options?.ttl);
    return cached;
  }

  // No cache - fetch and store
  const data = await fetchFn();
  await cache.set(key, data, options?.ttl);
  return data;
}

/**
 * Computed cache - cache the result of a computation
 */
export async function computedCache<T>(
  key: string,
  computeFn: () => T,
  ttl?: number
): Promise<T> {
  const cached = await cache.get<T>(key);
  if (cached !== null) {
    return cached;
  }

  const result = computeFn();
  await cache.set(key, result, ttl);
  return result;
}

/**
 * Multi-level cache miss handler
 */
export async function multiLevelCache<T>(
  key: string,
  fetchFns: Array<() => Promise<T | null>>,
  ttl?: number
): Promise<T | null> {
  // Try each level in order
  for (const fetchFn of fetchFns) {
    const data = await fetchFn();
    if (data !== null) {
      // Found data - cache it and return
      await cache.set(key, data, ttl);
      return data;
    }
  }

  return null;
}
