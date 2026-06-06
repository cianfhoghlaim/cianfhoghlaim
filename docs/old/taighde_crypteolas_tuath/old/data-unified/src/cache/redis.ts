import { Redis } from 'ioredis';

const {
  REDIS_HOST = 'localhost',
  REDIS_PORT = '6379',
  REDIS_PASSWORD = '',
  DEFAULT_CACHE_TTL = '300',
  REDIS_ENABLED = 'true', // Set to 'false' to disable Redis
} = process.env;

/**
 * Track Redis availability
 */
let redisAvailable = REDIS_ENABLED === 'true';

/**
 * Redis/Dragonfly client instance
 */
export const redis = new Redis({
  host: REDIS_HOST,
  port: parseInt(REDIS_PORT),
  password: REDIS_PASSWORD || undefined,
  retryStrategy: (times) => {
    if (times > 3) {
      console.log('Redis connection failed after 3 attempts, disabling cache');
      redisAvailable = false;
      return null; // Stop retrying
    }
    const delay = Math.min(times * 50, 2000);
    return delay;
  },
  maxRetriesPerRequest: 1, // Fail fast
  lazyConnect: true, // Don't connect until first command
  enableOfflineQueue: false, // Don't queue commands when offline
});

/**
 * Default cache TTL in seconds
 */
export const DEFAULT_TTL = parseInt(DEFAULT_CACHE_TTL);

/**
 * Check if Redis is available
 */
export function isRedisAvailable(): boolean {
  return redisAvailable;
}

/**
 * Redis client event handlers
 */
redis.on('connect', () => {
  console.log('Redis client connected');
  redisAvailable = true;
});

redis.on('error', (err) => {
  // Only log once, then mark as unavailable
  if (redisAvailable) {
    console.error('Redis unavailable, cache disabled:', err.code || err.message);
    redisAvailable = false;
  }
});

redis.on('ready', () => {
  console.log('Redis client ready');
  redisAvailable = true;
});

/**
 * Cache key prefixes for different data types
 */
export const CachePrefix = {
  ANALYTICS: 'analytics:',
  QUERY: 'query:',
  USER: 'user:',
  EVENT: 'event:',
  BAML: 'baml:',
} as const;

/**
 * Helper to build cache keys with prefixes
 */
export function buildCacheKey(prefix: string, ...parts: string[]): string {
  return `${prefix}${parts.join(':')}`;
}

/**
 * Get value from cache
 */
export async function get<T = any>(key: string): Promise<T | null> {
  if (!redisAvailable) return null;
  try {
    const value = await redis.get(key);
    if (!value) return null;
    try {
      return JSON.parse(value) as T;
    } catch {
      return value as T;
    }
  } catch {
    redisAvailable = false;
    return null;
  }
}

/**
 * Set value in cache with optional TTL
 */
export async function set(
  key: string,
  value: any,
  ttl: number = DEFAULT_TTL
): Promise<void> {
  if (!redisAvailable) return;
  try {
    const serialized = typeof value === 'string' ? value : JSON.stringify(value);
    if (ttl > 0) {
      await redis.setex(key, ttl, serialized);
    } else {
      await redis.set(key, serialized);
    }
  } catch {
    redisAvailable = false;
  }
}

/**
 * Set value with expiration timestamp (Unix timestamp in seconds)
 */
export async function setWithExpiry(
  key: string,
  value: any,
  expiryTimestamp: number
): Promise<void> {
  if (!redisAvailable) return;
  try {
    const serialized = typeof value === 'string' ? value : JSON.stringify(value);
    await redis.set(key, serialized, 'EXAT', expiryTimestamp);
  } catch {
    redisAvailable = false;
  }
}

/**
 * Delete key(s) from cache
 */
export async function del(...keys: string[]): Promise<number> {
  if (!redisAvailable || keys.length === 0) return 0;
  try {
    return await redis.del(...keys);
  } catch {
    redisAvailable = false;
    return 0;
  }
}

/**
 * Check if key exists
 */
export async function exists(...keys: string[]): Promise<number> {
  if (!redisAvailable || keys.length === 0) return 0;
  try {
    return await redis.exists(...keys);
  } catch {
    redisAvailable = false;
    return 0;
  }
}

/**
 * Get multiple values at once
 */
export async function mget<T = any>(...keys: string[]): Promise<(T | null)[]> {
  if (!redisAvailable || keys.length === 0) return keys.map(() => null);
  try {
    const values = await redis.mget(...keys);
    return values.map((value) => {
      if (!value) return null;
      try {
        return JSON.parse(value) as T;
      } catch {
        return value as T;
      }
    });
  } catch {
    redisAvailable = false;
    return keys.map(() => null);
  }
}

/**
 * Set multiple values at once
 */
export async function mset(keyValuePairs: Record<string, any>): Promise<void> {
  if (!redisAvailable) return;
  try {
    const pairs: string[] = [];
    for (const [key, value] of Object.entries(keyValuePairs)) {
      pairs.push(key, typeof value === 'string' ? value : JSON.stringify(value));
    }
    if (pairs.length > 0) {
      await redis.mset(...pairs);
    }
  } catch {
    redisAvailable = false;
  }
}

/**
 * Increment a counter
 */
export async function incr(key: string, amount: number = 1): Promise<number> {
  if (!redisAvailable) return 0;
  try {
    return await redis.incrby(key, amount);
  } catch {
    redisAvailable = false;
    return 0;
  }
}

/**
 * Get all keys matching a pattern
 */
export async function keys(pattern: string): Promise<string[]> {
  if (!redisAvailable) return [];
  try {
    return await redis.keys(pattern);
  } catch {
    redisAvailable = false;
    return [];
  }
}

/**
 * Set TTL on existing key
 */
export async function expire(key: string, seconds: number): Promise<number> {
  if (!redisAvailable) return 0;
  try {
    return await redis.expire(key, seconds);
  } catch {
    redisAvailable = false;
    return 0;
  }
}

/**
 * Get TTL of a key
 */
export async function ttl(key: string): Promise<number> {
  if (!redisAvailable) return -2; // -2 means key doesn't exist
  try {
    return await redis.ttl(key);
  } catch {
    redisAvailable = false;
    return -2;
  }
}

/**
 * Close Redis connection
 */
export async function close(): Promise<void> {
  if (!redisAvailable) return;
  try {
    await redis.quit();
  } catch {
    // Ignore close errors
  }
}

/**
 * Flush all data in current database
 */
export async function flushdb(): Promise<void> {
  await redis.flushdb();
}

/**
 * Hash operations
 */
export const hash = {
  async get(key: string, field: string): Promise<string | null> {
    return redis.hget(key, field);
  },

  async set(key: string, field: string, value: any): Promise<number> {
    const serialized = typeof value === 'string' ? value : JSON.stringify(value);
    return redis.hset(key, field, serialized);
  },

  async getAll(key: string): Promise<Record<string, string>> {
    return redis.hgetall(key);
  },

  async setMultiple(key: string, data: Record<string, any>): Promise<number> {
    const pairs: string[] = [];
    for (const [field, value] of Object.entries(data)) {
      pairs.push(field, typeof value === 'string' ? value : JSON.stringify(value));
    }
    if (pairs.length === 0) return 0;
    return redis.hset(key, ...pairs);
  },

  async delete(key: string, ...fields: string[]): Promise<number> {
    if (fields.length === 0) return 0;
    return redis.hdel(key, ...fields);
  },

  async exists(key: string, field: string): Promise<number> {
    return redis.hexists(key, field);
  },
};
