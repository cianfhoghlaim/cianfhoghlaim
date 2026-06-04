# Data Unified - Usage Examples

This document provides detailed examples of how to use the Data Unified API.

## Table of Contents

- [Setup](#setup)
- [Basic Operations](#basic-operations)
- [Analytics Queries](#analytics-queries)
- [Caching Patterns](#caching-patterns)
- [Advanced Use Cases](#advanced-use-cases)

## Setup

### Start Required Services

```bash
# Start Redis/Dragonfly
docker run -d -p 6379:6379 redis:latest
# OR
docker run -d -p 6380:6380 docker.dragonflydb.io/dragonflydb/dragonfly

# Start the application
npm run dev
```

### Initialize with Sample Data

```bash
curl -X POST http://localhost:3000/seed
```

## Basic Operations

### Create Users

```bash
# Create first user
curl -X POST http://localhost:3000/users \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "user_alice",
    "username": "alice",
    "email": "alice@example.com"
  }'

# Create second user
curl -X POST http://localhost:3000/users \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "user_bob",
    "username": "bob",
    "email": "bob@example.com"
  }'
```

### Create Events

```bash
# Page view event
curl -X POST http://localhost:3000/events \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "user_alice",
    "eventType": "page_view",
    "eventData": {
      "page": "/dashboard",
      "category": "analytics",
      "duration": 45
    }
  }'

# Click event
curl -X POST http://localhost:3000/events \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "user_alice",
    "eventType": "click",
    "eventData": {
      "element": "export_button",
      "page": "/dashboard"
    }
  }'

# Purchase event
curl -X POST http://localhost:3000/events \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "user_bob",
    "eventType": "purchase",
    "eventData": {
      "product": "premium_plan",
      "amount": 99.99,
      "currency": "USD"
    }
  }'
```

## Analytics Queries

### Event Statistics

Get aggregated statistics by event type:

```bash
curl http://localhost:3000/analytics/events/stats | jq
```

Expected response:
```json
{
  "success": true,
  "data": [
    {
      "event_type": "page_view",
      "count": 50,
      "unique_users": 3
    },
    {
      "event_type": "click",
      "count": 30,
      "unique_users": 2
    },
    {
      "event_type": "purchase",
      "count": 5,
      "unique_users": 2
    }
  ],
  "cached": true
}
```

### User Activity

Get activity for all users:

```bash
curl http://localhost:3000/analytics/users/activity | jq
```

Get activity for specific user:

```bash
curl "http://localhost:3000/analytics/users/activity?userId=user_alice" | jq
```

Expected response:
```json
{
  "success": true,
  "data": [
    {
      "user_id": "user_alice",
      "event_count": 45,
      "last_event": "2024-11-30T19:30:00Z",
      "first_event": "2024-11-25T10:00:00Z"
    }
  ],
  "cached": true
}
```

### Time Series Data

Get hourly event data for last 7 days:

```bash
curl "http://localhost:3000/analytics/timeseries?days=7" | jq
```

Get data for different time periods:

```bash
# Last 24 hours
curl "http://localhost:3000/analytics/timeseries?days=1" | jq

# Last 30 days
curl "http://localhost:3000/analytics/timeseries?days=30" | jq
```

Expected response:
```json
{
  "success": true,
  "data": [
    {
      "date": "2024-11-30",
      "hour": 14,
      "event_count": 23
    },
    {
      "date": "2024-11-30",
      "hour": 15,
      "event_count": 31
    }
  ],
  "cached": false
}
```

### Top Users

Get top 10 users:

```bash
curl "http://localhost:3000/analytics/users/top?limit=10" | jq
```

Get top 5 users:

```bash
curl "http://localhost:3000/analytics/users/top?limit=5" | jq
```

### Custom Queries

Execute any DuckDB SQL query:

```bash
# Count events by hour
curl -X POST http://localhost:3000/analytics/query \
  -H "Content-Type: application/json" \
  -d '{
    "sql": "SELECT HOUR(timestamp) as hour, COUNT(*) as count FROM events GROUP BY hour ORDER BY hour",
    "useCache": true
  }' | jq

# Get purchase statistics
curl -X POST http://localhost:3000/analytics/query \
  -H "Content-Type: application/json" \
  -d '{
    "sql": "SELECT user_id, SUM(CAST(json_extract(event_data, '"'"'$.amount'"'"') AS DOUBLE)) as total_spent FROM events WHERE event_type = '"'"'purchase'"'"' GROUP BY user_id",
    "useCache": true
  }' | jq

# Get daily active users
curl -X POST http://localhost:3000/analytics/query \
  -H "Content-Type: application/json" \
  -d '{
    "sql": "SELECT DATE_TRUNC('"'"'day'"'"', timestamp) as date, COUNT(DISTINCT user_id) as dau FROM events GROUP BY date ORDER BY date DESC LIMIT 30",
    "useCache": true
  }' | jq
```

## Caching Patterns

### Cache Performance

First request (cache miss):

```bash
time curl http://localhost:3000/analytics/events/stats
# Response includes: "cached": false
```

Second request (cache hit):

```bash
time curl http://localhost:3000/analytics/events/stats
# Response includes: "cached": true
# Should be significantly faster
```

### Cache Information

Get cache statistics:

```bash
curl http://localhost:3000/cache/info | jq
```

Expected response:
```json
{
  "success": true,
  "cacheStats": {
    "analytics": 15,
    "queries": 8,
    "users": 3,
    "events": 10,
    "total": 36
  }
}
```

### Cache Invalidation

Invalidate specific pattern:

```bash
# Invalidate all analytics caches
curl -X DELETE http://localhost:3000/cache/invalidate/analytics:* | jq

# Invalidate specific user cache
curl -X DELETE http://localhost:3000/cache/invalidate/user:user_alice | jq

# Invalidate all query caches
curl -X DELETE http://localhost:3000/cache/invalidate/query:* | jq
```

Flush entire cache:

```bash
curl -X DELETE http://localhost:3000/cache/flush | jq
```

## Advanced Use Cases

### Event Stream Analysis

Track user journey:

```bash
# Create a series of events for a user
curl -X POST http://localhost:3000/events \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "user_journey_test",
    "eventType": "page_view",
    "eventData": {"page": "/landing"}
  }'

sleep 1

curl -X POST http://localhost:3000/events \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "user_journey_test",
    "eventType": "page_view",
    "eventData": {"page": "/pricing"}
  }'

sleep 1

curl -X POST http://localhost:3000/events \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "user_journey_test",
    "eventType": "signup",
    "eventData": {"plan": "free"}
  }'

# Query the journey
curl "http://localhost:3000/events/user_journey_test" | jq
```

### Funnel Analysis

```bash
curl -X POST http://localhost:3000/analytics/query \
  -H "Content-Type: application/json" \
  -d '{
    "sql": "WITH funnel AS (SELECT user_id, MAX(CASE WHEN event_type = '"'"'page_view'"'"' THEN 1 ELSE 0 END) as viewed, MAX(CASE WHEN event_type = '"'"'signup'"'"' THEN 1 ELSE 0 END) as signed_up, MAX(CASE WHEN event_type = '"'"'purchase'"'"' THEN 1 ELSE 0 END) as purchased FROM events GROUP BY user_id) SELECT SUM(viewed) as total_views, SUM(signed_up) as total_signups, SUM(purchased) as total_purchases, ROUND(100.0 * SUM(signed_up) / NULLIF(SUM(viewed), 0), 2) as signup_rate, ROUND(100.0 * SUM(purchased) / NULLIF(SUM(signed_up), 0), 2) as purchase_rate FROM funnel",
    "useCache": true
  }' | jq
```

### Revenue Analysis

```bash
curl -X POST http://localhost:3000/analytics/query \
  -H "Content-Type: application/json" \
  -d '{
    "sql": "SELECT DATE_TRUNC('"'"'day'"'"', timestamp) as date, COUNT(*) as purchase_count, SUM(CAST(json_extract(event_data, '"'"'$.amount'"'"') AS DOUBLE)) as revenue FROM events WHERE event_type = '"'"'purchase'"'"' GROUP BY date ORDER BY date DESC",
    "useCache": true
  }' | jq
```

### User Retention

```bash
curl -X POST http://localhost:3000/analytics/query \
  -H "Content-Type: application/json" \
  -d '{
    "sql": "WITH first_event AS (SELECT user_id, MIN(DATE_TRUNC('"'"'day'"'"', timestamp)) as first_day FROM events GROUP BY user_id), returning_users AS (SELECT f.first_day, COUNT(DISTINCT CASE WHEN DATE_DIFF('"'"'day'"'"', f.first_day, DATE_TRUNC('"'"'day'"'"', e.timestamp)) = 1 THEN e.user_id END) as day_1, COUNT(DISTINCT CASE WHEN DATE_DIFF('"'"'day'"'"', f.first_day, DATE_TRUNC('"'"'day'"'"', e.timestamp)) = 7 THEN e.user_id END) as day_7, COUNT(DISTINCT CASE WHEN DATE_DIFF('"'"'day'"'"', f.first_day, DATE_TRUNC('"'"'day'"'"', e.timestamp)) = 30 THEN e.user_id END) as day_30 FROM first_event f JOIN events e ON f.user_id = e.user_id GROUP BY f.first_day) SELECT * FROM returning_users ORDER BY first_day DESC LIMIT 10",
    "useCache": true
  }' | jq
```

### Performance Testing

Test cache performance:

```bash
# Flush cache first
curl -X DELETE http://localhost:3000/cache/flush

# First request (cold cache)
time curl http://localhost:3000/analytics/events/stats > /dev/null

# Second request (warm cache)
time curl http://localhost:3000/analytics/events/stats > /dev/null

# Load test (requires 'ab' - Apache Bench)
ab -n 1000 -c 10 http://localhost:3000/analytics/events/stats
```

### Batch Event Creation

```bash
# Create multiple events quickly
for i in {1..100}; do
  curl -X POST http://localhost:3000/events \
    -H "Content-Type: application/json" \
    -d "{
      \"userId\": \"user_$((RANDOM % 10))\",
      \"eventType\": \"page_view\",
      \"eventData\": {\"page\": \"/page_$((RANDOM % 20))\"}
    }" &
done
wait

# Check the results
curl http://localhost:3000/analytics/events/stats | jq
```

## Tips and Best Practices

### 1. Use Caching Wisely

- Enable caching for frequently accessed queries
- Set appropriate TTLs based on data freshness requirements
- Invalidate cache when underlying data changes

### 2. Query Optimization

- Use indexes where appropriate
- Limit result sets for large queries
- Use aggregations in DuckDB rather than in application code

### 3. Error Handling

Always check the `success` field in responses:

```bash
response=$(curl -s http://localhost:3000/analytics/events/stats)
if echo "$response" | jq -e '.success' > /dev/null; then
  echo "Success!"
else
  echo "Error: $(echo "$response" | jq -r '.error')"
fi
```

### 4. Monitoring

Regularly check cache statistics to optimize TTLs:

```bash
watch -n 5 'curl -s http://localhost:3000/cache/info | jq'
```

## Troubleshooting

### Redis Connection Issues

```bash
# Check if Redis is running
redis-cli ping
# Should return "PONG"

# Check connection from application logs
npm run dev
# Look for "Redis client connected" message
```

### DuckDB Query Errors

Test queries in isolation:

```bash
curl -X POST http://localhost:3000/analytics/query \
  -H "Content-Type: application/json" \
  -d '{
    "sql": "SELECT 1 as test",
    "useCache": false
  }' | jq
```

### Cache Not Working

```bash
# Check cache info
curl http://localhost:3000/cache/info | jq

# Verify Redis connection
redis-cli keys "*"
```
