import { serve } from '@hono/node-server';
import { Hono } from 'hono';
import { cors } from 'hono/cors';
import { logger } from 'hono/logger';
import { prettyJSON } from 'hono/pretty-json';
import { requestId } from 'hono/request-id';
import { zValidator } from '@hono/zod-validator';
import { z } from 'zod';

// DuckDB imports
import { initializeDuckDB, query as duckQuery } from './duckdb/client';
import * as queries from './duckdb/queries';

// Cache imports
import * as cache from './cache/redis';
import * as cachePatterns from './cache/patterns';

// BAML schemas
import type { AnalyticsQuery, EventSchema, AnalyticsReport } from './baml/schemas';

// ============================================================================
// Configuration
// ============================================================================

const PORT = process.env.PORT ? parseInt(process.env.PORT) : 3000;
const ANALYTICS_CACHE_TTL = parseInt(process.env.ANALYTICS_CACHE_TTL || '60');

// ============================================================================
// Zod Validators
// ============================================================================

const EventInsertSchema = z.object({
  userId: z.string(),
  eventType: z.string(),
  eventData: z.record(z.any()),
});

const QuerySchema = z.object({
  sql: z.string(),
  useCache: z.boolean().optional().default(true),
});

const UserInsertSchema = z.object({
  userId: z.string(),
  username: z.string(),
  email: z.string().email(),
});

// ============================================================================
// Hono App Setup
// ============================================================================

const app = new Hono();

// Middleware
app.use('*', cors());
app.use('*', logger());
app.use('*', prettyJSON());
app.use('*', requestId());

// ============================================================================
// Health & Info Routes
// ============================================================================

app.get('/', (c) => {
  return c.json({
    message: 'Data Unified API',
    version: '1.0.0',
    features: [
      'DuckDB Analytics',
      'Redis/Dragonfly Caching',
      'BAML Schema Generation',
    ],
    endpoints: {
      health: '/_health',
      analytics: '/analytics/*',
      cache: '/cache/*',
      events: '/events',
      users: '/users',
    },
  });
});

app.get('/_health', (c) => c.text('OK'));

// ============================================================================
// Analytics Routes (DuckDB)
// ============================================================================

// Get event statistics
app.get('/analytics/events/stats', async (c) => {
  const cacheKey = cache.buildCacheKey(cache.CachePrefix.ANALYTICS, 'events', 'stats');

  try {
    const stats = await cachePatterns.cacheAside(
      cacheKey,
      () => queries.getEventStats(),
      ANALYTICS_CACHE_TTL
    );

    return c.json({
      success: true,
      data: stats,
      cached: await cache.exists(cacheKey) > 0,
    });
  } catch (error) {
    return c.json({ success: false, error: String(error) }, 500);
  }
});

// Get user activity
app.get('/analytics/users/activity', async (c) => {
  const userId = c.req.query('userId');
  const cacheKey = cache.buildCacheKey(
    cache.CachePrefix.ANALYTICS,
    'users',
    'activity',
    userId || 'all'
  );

  try {
    const activity = await cachePatterns.cacheAside(
      cacheKey,
      () => queries.getUserActivity(userId),
      ANALYTICS_CACHE_TTL
    );

    return c.json({
      success: true,
      data: activity,
      cached: await cache.exists(cacheKey) > 0,
    });
  } catch (error) {
    return c.json({ success: false, error: String(error) }, 500);
  }
});

// Get time series data
app.get('/analytics/timeseries', async (c) => {
  const days = parseInt(c.req.query('days') || '7');
  const cacheKey = cache.buildCacheKey(
    cache.CachePrefix.ANALYTICS,
    'timeseries',
    `${days}days`
  );

  try {
    const timeseries = await cachePatterns.cacheAside(
      cacheKey,
      () => queries.getTimeSeriesData(days),
      ANALYTICS_CACHE_TTL
    );

    return c.json({
      success: true,
      data: timeseries,
      cached: await cache.exists(cacheKey) > 0,
    });
  } catch (error) {
    return c.json({ success: false, error: String(error) }, 500);
  }
});

// Get top users
app.get('/analytics/users/top', async (c) => {
  const limit = parseInt(c.req.query('limit') || '10');
  const cacheKey = cache.buildCacheKey(
    cache.CachePrefix.ANALYTICS,
    'users',
    'top',
    `${limit}`
  );

  try {
    const topUsers = await cachePatterns.cacheAside(
      cacheKey,
      () => queries.getTopUsers(limit),
      ANALYTICS_CACHE_TTL
    );

    return c.json({
      success: true,
      data: topUsers,
      cached: await cache.exists(cacheKey) > 0,
    });
  } catch (error) {
    return c.json({ success: false, error: String(error) }, 500);
  }
});

// Execute custom query
app.post('/analytics/query', zValidator('json', QuerySchema), async (c) => {
  const { sql, useCache } = c.req.valid('json');
  const cacheKey = cache.buildCacheKey(cache.CachePrefix.QUERY, Buffer.from(sql).toString('base64'));

  try {
    let result;

    if (useCache) {
      result = await cachePatterns.cacheAside(
        cacheKey,
        () => duckQuery(sql),
        ANALYTICS_CACHE_TTL
      );
    } else {
      result = await duckQuery(sql);
    }

    return c.json({
      success: true,
      data: result,
      query: sql,
      cached: useCache && (await cache.exists(cacheKey)) > 0,
    });
  } catch (error) {
    return c.json({
      success: false,
      error: String(error),
      query: sql,
    }, 500);
  }
});

// ============================================================================
// Event Routes
// ============================================================================

app.post('/events', zValidator('json', EventInsertSchema), async (c) => {
  const event = c.req.valid('json');

  try {
    // Write-through pattern: write to DuckDB and cache simultaneously
    await cachePatterns.writeThrough(
      cache.buildCacheKey(cache.CachePrefix.EVENT, event.userId),
      event,
      async (data) => {
        await queries.insertEvent(data.userId, data.eventType, data.eventData);
      },
      cache.DEFAULT_TTL
    );

    // Invalidate analytics caches since new data was added
    await cachePatterns.invalidatePattern(`${cache.CachePrefix.ANALYTICS}*`);

    return c.json({
      success: true,
      message: 'Event created',
      event,
    }, 201);
  } catch (error) {
    return c.json({
      success: false,
      error: String(error),
    }, 500);
  }
});

// Get recent events for a user
app.get('/events/:userId', async (c) => {
  const userId = c.req.param('userId');
  const cacheKey = cache.buildCacheKey(cache.CachePrefix.EVENT, userId);

  try {
    const events = await cachePatterns.cacheAside(
      cacheKey,
      async () => {
        const result = await duckQuery(
          `SELECT * FROM events WHERE user_id = '${userId}' ORDER BY timestamp DESC LIMIT 100`
        );
        return result;
      },
      cache.DEFAULT_TTL
    );

    return c.json({
      success: true,
      userId,
      data: events,
    });
  } catch (error) {
    return c.json({
      success: false,
      error: String(error),
    }, 500);
  }
});

// ============================================================================
// User Routes
// ============================================================================

app.post('/users', zValidator('json', UserInsertSchema), async (c) => {
  const user = c.req.valid('json');

  try {
    await cachePatterns.writeThrough(
      cache.buildCacheKey(cache.CachePrefix.USER, user.userId),
      user,
      async (data) => {
        await queries.insertUser(data.userId, data.username, data.email);
      },
      cache.DEFAULT_TTL
    );

    return c.json({
      success: true,
      message: 'User created',
      user,
    }, 201);
  } catch (error) {
    return c.json({
      success: false,
      error: String(error),
    }, 500);
  }
});

// ============================================================================
// Cache Management Routes
// ============================================================================

// Get cache info
app.get('/cache/info', async (c) => {
  try {
    const analyticsKeys = await cache.keys(`${cache.CachePrefix.ANALYTICS}*`);
    const queryKeys = await cache.keys(`${cache.CachePrefix.QUERY}*`);
    const userKeys = await cache.keys(`${cache.CachePrefix.USER}*`);
    const eventKeys = await cache.keys(`${cache.CachePrefix.EVENT}*`);

    return c.json({
      success: true,
      cacheStats: {
        analytics: analyticsKeys.length,
        queries: queryKeys.length,
        users: userKeys.length,
        events: eventKeys.length,
        total: analyticsKeys.length + queryKeys.length + userKeys.length + eventKeys.length,
      },
    });
  } catch (error) {
    return c.json({
      success: false,
      error: String(error),
    }, 500);
  }
});

// Invalidate cache by pattern
app.delete('/cache/invalidate/:pattern', async (c) => {
  const pattern = c.req.param('pattern');

  try {
    const deletedCount = await cachePatterns.invalidatePattern(pattern);
    return c.json({
      success: true,
      message: `Invalidated ${deletedCount} cache keys`,
      pattern,
      deletedCount,
    });
  } catch (error) {
    return c.json({
      success: false,
      error: String(error),
    }, 500);
  }
});

// Flush entire cache
app.delete('/cache/flush', async (c) => {
  try {
    await cache.flushdb();
    return c.json({
      success: true,
      message: 'Cache flushed successfully',
    });
  } catch (error) {
    return c.json({
      success: false,
      error: String(error),
    }, 500);
  }
});

// ============================================================================
// Seed Data Route (for testing)
// ============================================================================

app.post('/seed', async (c) => {
  try {
    // Create sample users
    const users = [
      { userId: 'user_1', username: 'alice', email: 'alice@example.com' },
      { userId: 'user_2', username: 'bob', email: 'bob@example.com' },
      { userId: 'user_3', username: 'charlie', email: 'charlie@example.com' },
    ];

    for (const user of users) {
      await queries.insertUser(user.userId, user.username, user.email);
    }

    // Create sample events
    const eventTypes = ['page_view', 'click', 'purchase', 'signup', 'logout'];
    for (let i = 0; i < 100; i++) {
      const userId = users[Math.floor(Math.random() * users.length)].userId;
      const eventType = eventTypes[Math.floor(Math.random() * eventTypes.length)];
      const eventData = {
        page: `/page${Math.floor(Math.random() * 10)}`,
        category: `category_${Math.floor(Math.random() * 5)}`,
        value: Math.floor(Math.random() * 1000),
      };

      await queries.insertEvent(userId, eventType, eventData);
    }

    return c.json({
      success: true,
      message: 'Seed data created',
      stats: {
        users: users.length,
        events: 100,
      },
    });
  } catch (error) {
    return c.json({
      success: false,
      error: String(error),
    }, 500);
  }
});

// ============================================================================
// Error Handler
// ============================================================================

app.notFound((c) => {
  return c.json({ success: false, message: 'Not Found' }, 404);
});

app.onError((err, c) => {
  console.error('Server error:', err);
  return c.json({
    success: false,
    error: err.message,
  }, 500);
});

// ============================================================================
// Server Initialization
// ============================================================================

async function startServer() {
  try {
    console.log('Initializing Data Unified API...');

    // Initialize DuckDB
    await initializeDuckDB();

    // Start server
    const server = serve(
      {
        fetch: app.fetch,
        port: PORT,
      },
      (info) => {
        console.log(`\nServer running on http://localhost:${info.port}`);
        console.log(`\nAvailable endpoints:`);
        console.log(`  GET  /                          - API info`);
        console.log(`  GET  /_health                   - Health check`);
        console.log(`  GET  /analytics/events/stats    - Event statistics`);
        console.log(`  GET  /analytics/users/activity  - User activity`);
        console.log(`  GET  /analytics/timeseries      - Time series data`);
        console.log(`  GET  /analytics/users/top       - Top users`);
        console.log(`  POST /analytics/query           - Custom query`);
        console.log(`  POST /events                    - Create event`);
        console.log(`  GET  /events/:userId            - Get user events`);
        console.log(`  POST /users                     - Create user`);
        console.log(`  GET  /cache/info                - Cache statistics`);
        console.log(`  POST /seed                      - Seed sample data`);
        console.log('');
      }
    );

    // Graceful shutdown
    process.on('SIGINT', async () => {
      console.log('\nShutting down gracefully...');
      server.close();
      await cache.close();
      process.exit(0);
    });

    process.on('SIGTERM', async () => {
      console.log('\nShutting down gracefully...');
      server.close();
      await cache.close();
      process.exit(0);
    });
  } catch (error) {
    console.error('Failed to start server:', error);
    process.exit(1);
  }
}

// Start the server
startServer();
