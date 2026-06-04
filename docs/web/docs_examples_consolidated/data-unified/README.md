# Data Unified - Integrated Analytics & Caching Layer

A comprehensive example demonstrating the integration of **DuckDB analytics**, **Redis/Dragonfly caching**, and **BAML schema generation** into a unified data layer.

## Features

- **DuckDB Analytics**: High-performance analytical queries on structured data
- **Redis/Dragonfly Caching**: Multiple caching patterns for optimal performance
- **BAML Integration**: Type-safe schema generation and LLM-powered analytics
- **Hono API**: Fast, lightweight REST API with type validation
- **Real-time Analytics**: Event tracking and user activity analysis

## Architecture

```
┌─────────────────┐
│   Hono API      │
│   (REST)        │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼──┐  ┌──▼────┐
│DuckDB│  │ Redis │
│      │  │Cache  │
└──────┘  └───────┘
    │         │
    └────┬────┘
         │
    ┌────▼────┐
    │  BAML   │
    │Schemas  │
    └─────────┘
```

## Quick Start

### Prerequisites

- Node.js 18+
- Redis or Dragonfly running locally (default: localhost:6379)
- TypeScript

### Installation

```bash
npm install
```

### Environment Setup

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Configure your environment variables:

```env
PORT=3000
REDIS_HOST=localhost
REDIS_PORT=6379

# Optional: For remote data sources
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=us-east-1

# Optional: For BAML LLM features
OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
```

### Running the Server

Development mode with hot reload:

```bash
npm run dev
```

Build and run:

```bash
npm run build
npm start
```

## API Endpoints

### Health & Info

- `GET /` - API information
- `GET /_health` - Health check

### Analytics (DuckDB)

- `GET /analytics/events/stats` - Event statistics grouped by type
- `GET /analytics/users/activity?userId=<id>` - User activity summary
- `GET /analytics/timeseries?days=7` - Time series event data
- `GET /analytics/users/top?limit=10` - Top users by event count
- `POST /analytics/query` - Execute custom SQL query

### Events

- `POST /events` - Create new event
  ```json
  {
    "userId": "user_1",
    "eventType": "page_view",
    "eventData": {
      "page": "/dashboard",
      "category": "analytics"
    }
  }
  ```
- `GET /events/:userId` - Get events for specific user

### Users

- `POST /users` - Create new user
  ```json
  {
    "userId": "user_1",
    "username": "alice",
    "email": "alice@example.com"
  }
  ```

### Cache Management

- `GET /cache/info` - Cache statistics
- `DELETE /cache/invalidate/:pattern` - Invalidate cache by pattern
- `DELETE /cache/flush` - Flush entire cache

### Utility

- `POST /seed` - Generate sample data for testing

## Caching Patterns

The application demonstrates multiple caching strategies:

### 1. Cache-Aside (Lazy Loading)

```typescript
const stats = await cachePatterns.cacheAside(
  cacheKey,
  () => queries.getEventStats(),
  CACHE_TTL
);
```

### 2. Write-Through

```typescript
await cachePatterns.writeThrough(
  cacheKey,
  data,
  async (data) => await saveToDatabase(data),
  CACHE_TTL
);
```

### 3. Write-Behind

```typescript
await cachePatterns.writeBehind(
  cacheKey,
  data,
  async (data) => await saveToDatabase(data),
  CACHE_TTL
);
```

### 4. Stale-While-Revalidate

```typescript
const data = await cachePatterns.staleWhileRevalidate(
  cacheKey,
  fetchFn,
  { ttl: 300, staleTtl: 60 }
);
```

## DuckDB Queries

### Event Statistics

```sql
SELECT
  event_type,
  COUNT(*) as count,
  COUNT(DISTINCT user_id) as unique_users
FROM events
GROUP BY event_type
ORDER BY count DESC
```

### Time Series Analysis

```sql
SELECT
  DATE_TRUNC('day', timestamp) as date,
  HOUR(timestamp) as hour,
  COUNT(*) as event_count
FROM events
WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '7 days'
GROUP BY date, hour
ORDER BY date, hour
```

### Cohort Analysis

```sql
WITH user_first_event AS (
  SELECT
    user_id,
    DATE_TRUNC('week', MIN(timestamp)) as cohort_week
  FROM events
  GROUP BY user_id
)
SELECT
  cohort_week,
  event_week,
  COUNT(DISTINCT user_id) as active_users
FROM user_events
GROUP BY cohort_week, event_week
```

## BAML Integration

### Schema Definition

Located in `baml_src/main.baml`:

```baml
class AnalyticsQuery {
  query string @description("The SQL query to execute")
  description string
  expectedFields string[]
  queryType ("aggregation" | "timeseries" | "cohort" | "funnel")
}
```

### Functions

```baml
function GenerateAnalyticsQuery(
  userQuestion: string,
  availableTables: string[]
) -> AnalyticsQuery {
  client OpenAI_GPT4_Mini
  prompt #"
    Generate an optimized DuckDB SQL query...
  "#
}
```

### Generate BAML Code

```bash
npm run baml:generate
```

## Project Structure

```
data-unified/
├── src/
│   ├── index.ts              # Main Hono application
│   ├── duckdb/
│   │   ├── client.ts         # DuckDB connection & initialization
│   │   └── queries.ts        # Analytical query functions
│   ├── cache/
│   │   ├── redis.ts          # Redis client & utilities
│   │   └── patterns.ts       # Caching pattern implementations
│   └── baml/
│       └── schemas.ts        # TypeScript schema definitions
├── baml_src/
│   ├── main.baml             # BAML schema & function definitions
│   └── generators.baml       # Code generation config
├── package.json
├── tsconfig.json
└── README.md
```

## Example Usage

### 1. Seed Sample Data

```bash
curl -X POST http://localhost:3000/seed
```

### 2. Get Event Statistics

```bash
curl http://localhost:3000/analytics/events/stats
```

Response:
```json
{
  "success": true,
  "data": [
    {
      "event_type": "page_view",
      "count": 42,
      "unique_users": 3
    },
    {
      "event_type": "click",
      "count": 28,
      "unique_users": 3
    }
  ],
  "cached": true
}
```

### 3. Execute Custom Query

```bash
curl -X POST http://localhost:3000/analytics/query \
  -H "Content-Type: application/json" \
  -d '{
    "sql": "SELECT COUNT(*) as total FROM events",
    "useCache": true
  }'
```

### 4. Create Event

```bash
curl -X POST http://localhost:3000/events \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "user_1",
    "eventType": "purchase",
    "eventData": {
      "product": "premium_plan",
      "amount": 99.99
    }
  }'
```

### 5. Get Cache Stats

```bash
curl http://localhost:3000/cache/info
```

## Performance Considerations

### DuckDB

- Uses in-memory database for fast queries
- Supports external Parquet files via httpfs
- Can connect to S3/R2 for data lakes
- Optimized for analytical workloads

### Redis/Dragonfly

- Dragonfly is recommended for better performance
- Uses connection pooling and retry strategies
- Implements multiple caching patterns
- Supports cache invalidation patterns

### Caching Strategy

- Analytics queries: 60s TTL (configurable)
- User data: 300s TTL
- Event data: 300s TTL
- Query results: 60s TTL

## Advanced Features

### Remote Data Access

Query Parquet files from S3:

```typescript
const data = await queryRemoteParquet('s3://bucket/data.parquet');
```

### Cache Stampede Prevention

```typescript
const data = await cachePatterns.withLock(
  cacheKey,
  fetchFn,
  { lockTimeout: 10 }
);
```

### Batch Operations

```typescript
await cachePatterns.cacheBatch([
  { key: 'key1', value: data1 },
  { key: 'key2', value: data2 }
], ttl);
```

## Contributing

This is a reference implementation demonstrating best practices for:

- Analytical data processing with DuckDB
- Caching strategies with Redis/Dragonfly
- Type-safe schema generation with BAML
- RESTful API design with Hono

Feel free to adapt and extend for your use case.

## License

MIT

## Resources

- [DuckDB Documentation](https://duckdb.org/docs/)
- [Dragonfly Documentation](https://www.dragonflydb.io/docs)
- [BAML Documentation](https://docs.boundaryml.com)
- [Hono Documentation](https://hono.dev/)
