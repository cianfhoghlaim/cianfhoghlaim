# Data Unified - Architecture & Design

This document explains the architecture and design decisions of the Data Unified example.

## Overview

Data Unified demonstrates a modern data layer that combines:

1. **DuckDB** - OLAP database for analytical queries
2. **Redis/Dragonfly** - High-performance caching layer
3. **BAML** - Type-safe schema generation and LLM integration
4. **Hono** - Lightweight, fast web framework

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                     Client Layer                         │
│                   (HTTP/REST API)                        │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────┐
│                   Hono Application                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │Analytics │  │ Events   │  │  Cache   │              │
│  │  Routes  │  │  Routes  │  │  Routes  │              │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘              │
└───────┼────────────┼──────────────┼────────────────────┘
        │            │              │
┌───────▼────┐  ┌───▼──────┐  ┌───▼──────┐
│  DuckDB    │  │  Redis/  │  │   BAML   │
│  Client    │  │Dragonfly │  │ Schemas  │
│            │  │  Cache   │  │          │
└───────┬────┘  └────┬─────┘  └────┬─────┘
        │            │              │
┌───────▼────────────▼──────────────▼─────┐
│         Cache Patterns Layer            │
│  • Cache-Aside    • Write-Through       │
│  • Read-Through   • Write-Behind        │
│  • Stale-While-Revalidate               │
└─────────────────────────────────────────┘
```

## Component Details

### 1. DuckDB Layer (`src/duckdb/`)

**Purpose**: Analytical query processing

**Files**:
- `client.ts` - Connection management, initialization
- `queries.ts` - Pre-built analytical queries

**Key Features**:
- In-memory database for fast queries
- Support for external data sources (S3, Parquet)
- Analytical functions (window functions, CTEs, aggregations)
- JSON data support

**Example Queries**:
```sql
-- Event statistics
SELECT event_type, COUNT(*) as count
FROM events
GROUP BY event_type

-- Time series analysis
SELECT DATE_TRUNC('hour', timestamp) as hour,
       COUNT(*) as events
FROM events
WHERE timestamp > NOW() - INTERVAL '7 days'
GROUP BY hour
```

### 2. Cache Layer (`src/cache/`)

**Purpose**: Performance optimization through caching

**Files**:
- `redis.ts` - Redis client and basic operations
- `patterns.ts` - Advanced caching patterns

**Caching Patterns Implemented**:

#### Cache-Aside (Lazy Loading)
```typescript
// Read from cache, fallback to source if miss
const data = await cacheAside(key, fetchFn, ttl);
```

**Use Case**: Analytics queries that don't change frequently

#### Write-Through
```typescript
// Write to cache and database simultaneously
await writeThrough(key, value, writeFn, ttl);
```

**Use Case**: User creation, event logging

#### Write-Behind
```typescript
// Write to cache immediately, database async
await writeBehind(key, value, writeFn, ttl);
```

**Use Case**: High-throughput event streams

#### Stale-While-Revalidate
```typescript
// Serve stale data while refreshing in background
const data = await staleWhileRevalidate(key, fetchFn, options);
```

**Use Case**: Dashboard data that updates frequently

### 3. BAML Integration (`baml_src/`, `src/baml/`)

**Purpose**: Type-safe schema generation and LLM integration

**Files**:
- `baml_src/main.baml` - Schema and function definitions
- `baml_src/generators.baml` - Code generation config
- `src/baml/schemas.ts` - TypeScript type definitions

**Capabilities**:
- Generate SQL queries from natural language
- Analyze query results with LLM
- Create data transformation pipelines
- Generate caching strategies

**Example Function**:
```baml
function GenerateAnalyticsQuery(
  userQuestion: string,
  availableTables: string[]
) -> AnalyticsQuery {
  client OpenAI_GPT4_Mini
  prompt #"
    Generate optimized DuckDB SQL query...
  "#
}
```

### 4. API Layer (`src/index.ts`)

**Purpose**: HTTP interface to the data layer

**Endpoints**:

```
/analytics/*
├── GET  /events/stats           - Event statistics
├── GET  /users/activity         - User activity summary
├── GET  /timeseries            - Time series data
├── GET  /users/top             - Top users
└── POST /query                  - Custom query execution

/events/*
├── POST /                       - Create event
└── GET  /:userId               - Get user events

/users/*
└── POST /                       - Create user

/cache/*
├── GET    /info                 - Cache statistics
├── DELETE /invalidate/:pattern  - Invalidate by pattern
└── DELETE /flush                - Flush entire cache
```

## Data Flow Examples

### Example 1: Analytics Query (Cache-Aside)

```
1. Client → GET /analytics/events/stats
2. API checks cache → Redis
3. Cache miss → Query DuckDB
4. DuckDB returns results
5. API stores in Redis (TTL: 60s)
6. API returns to client

Next request:
1. Client → GET /analytics/events/stats
2. API checks cache → Redis
3. Cache hit → Return cached data
4. API returns to client (much faster!)
```

### Example 2: Event Creation (Write-Through)

```
1. Client → POST /events
2. API validates with Zod
3. Write-through pattern:
   a. Write to Redis (cache)
   b. Write to DuckDB (database)
   Both operations happen in parallel
4. Invalidate analytics caches
5. API returns success
```

### Example 3: Custom Query with Cache

```
1. Client → POST /analytics/query
2. API creates cache key from SQL hash
3. Check Redis for cached result
4. If miss:
   a. Execute in DuckDB
   b. Cache result
5. Return data with cache status
```

## Design Patterns

### 1. Repository Pattern

Each data source has its own module:
- `duckdb/` - Analytical queries
- `cache/` - Caching operations

### 2. Strategy Pattern

Multiple caching strategies:
- `cacheAside`
- `writeThrough`
- `writeBehind`
- `staleWhileRevalidate`

### 3. Builder Pattern

Cache key construction:
```typescript
const key = buildCacheKey(
  CachePrefix.ANALYTICS,
  'events',
  'stats'
);
```

### 4. Decorator Pattern

Request validation and transformation:
```typescript
app.post('/events',
  zValidator('json', EventInsertSchema),
  async (c) => { ... }
);
```

## Performance Optimizations

### 1. DuckDB Optimizations

- **In-memory database**: Fast queries, no disk I/O
- **Parallel execution**: Utilizes multiple CPU cores
- **Columnar storage**: Efficient for analytical queries
- **Query caching**: Results cached in Redis

### 2. Cache Optimizations

- **TTL-based expiration**: Automatic cache invalidation
- **Pattern-based invalidation**: Bulk cache clearing
- **Connection pooling**: Reuse Redis connections
- **Batch operations**: MGET/MSET for multiple keys

### 3. API Optimizations

- **Middleware ordering**: Efficient request processing
- **Streaming responses**: For large datasets
- **Compression**: Automatic JSON compression
- **Connection reuse**: HTTP keep-alive

## Scalability Considerations

### Horizontal Scaling

```
┌─────────┐  ┌─────────┐  ┌─────────┐
│ API     │  │ API     │  │ API     │
│ Server  │  │ Server  │  │ Server  │
└────┬────┘  └────┬────┘  └────┬────┘
     │            │            │
     └────────────┼────────────┘
                  │
         ┌────────▼────────┐
         │  Load Balancer  │
         └────────┬────────┘
                  │
         ┌────────┴────────┐
         │                 │
    ┌────▼─────┐    ┌─────▼────┐
    │ DuckDB   │    │  Redis   │
    │ (shared) │    │ Cluster  │
    └──────────┘    └──────────┘
```

### Vertical Scaling

- DuckDB benefits from more CPU cores
- Redis benefits from more memory
- API server benefits from faster CPUs

## Integration Points

### From DuckDB Example

- Connection management (`client.ts`)
- Query helpers (`queries.ts`)
- Extension loading (httpfs, parquet, JSON)
- S3/R2 integration

### From Dragonfly/Redis Example

- Cache client setup (`redis.ts`)
- Connection pooling
- Retry strategies
- Write-through pattern

### From BAML Example

- Schema definitions (`main.baml`)
- Type generation (`generators.baml`)
- LLM client configuration
- Function definitions

## Error Handling

```typescript
try {
  const result = await cacheAside(
    key,
    () => queries.getEventStats(),
    ttl
  );
  return c.json({ success: true, data: result });
} catch (error) {
  return c.json({
    success: false,
    error: String(error)
  }, 500);
}
```

## Monitoring & Observability

### Metrics to Track

1. **Cache Hit Rate**: `hits / (hits + misses)`
2. **Query Performance**: DuckDB query execution time
3. **API Response Time**: End-to-end latency
4. **Error Rate**: Failed requests / total requests

### Logging

```typescript
// Request ID tracking
app.use('*', requestId());

// Access logs
app.use('*', logger());

// Cache hit/miss logging
console.log(`Cache ${cached ? 'hit' : 'miss'}: ${key}`);
```

## Testing Strategy

### Unit Tests
- Cache pattern functions
- Query builders
- Schema validators

### Integration Tests
- API endpoints
- DuckDB queries
- Redis operations

### Performance Tests
- Cache performance
- Query optimization
- Load testing

## Security Considerations

1. **SQL Injection**: Use parameterized queries
2. **Cache Poisoning**: Validate data before caching
3. **API Authentication**: Add bearer/basic auth
4. **Rate Limiting**: Prevent abuse
5. **Input Validation**: Zod schemas for all inputs

## Future Enhancements

1. **Streaming Analytics**: WebSocket support
2. **Real-time Updates**: Server-Sent Events
3. **Query Optimizer**: Automatic query rewriting
4. **Multi-tenant Support**: Isolated data per tenant
5. **GraphQL API**: Alternative to REST
6. **Metrics Dashboard**: Real-time monitoring UI

## Conclusion

Data Unified demonstrates production-ready patterns for building high-performance data layers that combine analytical processing, intelligent caching, and type-safe schema management.
