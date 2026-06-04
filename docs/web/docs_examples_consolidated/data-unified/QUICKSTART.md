# Data Unified - Quick Start Guide

Get up and running in 5 minutes!

## Prerequisites

- Node.js 18+ installed
- Docker (for Redis/Dragonfly)
- curl (for testing)

## Installation

```bash
# Clone and navigate to the project
cd /path/to/data-unified

# Run setup script
./scripts/setup.sh

# Or manually:
npm install
cp .env.example .env
docker-compose up -d
```

## Start the Server

```bash
npm run dev
```

You should see:
```
Initializing DuckDB...
Redis client connected
Sample tables created
DuckDB initialized successfully

Server running on http://localhost:3000
```

## Create Sample Data

```bash
curl -X POST http://localhost:3000/seed
```

## Test the API

### 1. Get Event Statistics

```bash
curl http://localhost:3000/analytics/events/stats | jq
```

### 2. View User Activity

```bash
curl http://localhost:3000/analytics/users/activity | jq
```

### 3. Time Series Data

```bash
curl "http://localhost:3000/analytics/timeseries?days=7" | jq
```

### 4. Custom Query

```bash
curl -X POST http://localhost:3000/analytics/query \
  -H "Content-Type: application/json" \
  -d '{
    "sql": "SELECT event_type, COUNT(*) FROM events GROUP BY event_type",
    "useCache": true
  }' | jq
```

### 5. Create Event

```bash
curl -X POST http://localhost:3000/events \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "user_1",
    "eventType": "purchase",
    "eventData": {"amount": 99.99}
  }' | jq
```

## Run Full Test Suite

```bash
./scripts/test-api.sh
```

## Cache Performance Test

```bash
# Clear cache
curl -X DELETE http://localhost:3000/cache/flush

# First request (cold cache)
time curl -s http://localhost:3000/analytics/events/stats > /dev/null

# Second request (warm cache) - should be much faster!
time curl -s http://localhost:3000/analytics/events/stats > /dev/null
```

## Common Commands

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Generate BAML code
npm run baml:generate

# Start Docker services
docker-compose up -d

# Stop Docker services
docker-compose down

# View logs
docker-compose logs -f
```

## Next Steps

- Read [README.md](./README.md) for full documentation
- Check [EXAMPLES.md](./EXAMPLES.md) for more usage examples
- Review [ARCHITECTURE.md](./ARCHITECTURE.md) for design details

## Troubleshooting

### Server won't start

```bash
# Check if port 3000 is in use
lsof -ti:3000

# Kill the process if needed
kill -9 $(lsof -ti:3000)
```

### Redis connection failed

```bash
# Check if Redis is running
docker-compose ps

# Restart Redis
docker-compose restart dragonfly
```

### DuckDB errors

Check the console for specific error messages. Most common issues:
- SQL syntax errors
- Missing tables (run `/seed` endpoint)
- Extension loading failures

## Quick Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/_health` | GET | Health check |
| `/analytics/events/stats` | GET | Event statistics |
| `/analytics/users/activity` | GET | User activity |
| `/analytics/timeseries` | GET | Time series data |
| `/analytics/users/top` | GET | Top users |
| `/analytics/query` | POST | Custom query |
| `/events` | POST | Create event |
| `/events/:userId` | GET | User events |
| `/users` | POST | Create user |
| `/cache/info` | GET | Cache stats |
| `/seed` | POST | Seed data |

## Environment Variables

```env
PORT=3000                          # API port
REDIS_HOST=localhost               # Redis host
REDIS_PORT=6379                    # Redis port
DEFAULT_CACHE_TTL=300              # Default cache TTL (seconds)
ANALYTICS_CACHE_TTL=60             # Analytics cache TTL
OPENAI_API_KEY=sk-...             # For BAML (optional)
ANTHROPIC_API_KEY=sk-ant-...      # For BAML (optional)
```

## Performance Tips

1. **Use caching**: Set `useCache: true` for repeated queries
2. **Set appropriate TTLs**: Balance freshness vs performance
3. **Invalidate wisely**: Clear caches only when data changes
4. **Limit result sets**: Use LIMIT in queries
5. **Monitor cache hit rate**: Check `/cache/info` regularly

## Resources

- [DuckDB Docs](https://duckdb.org/docs/)
- [Dragonfly Docs](https://www.dragonflydb.io/docs)
- [BAML Docs](https://docs.boundaryml.com)
- [Hono Docs](https://hono.dev/)

---

**Need help?** Check the full documentation or open an issue.
