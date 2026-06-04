#!/bin/bash

# API Testing Script for Data Unified

set -e

BASE_URL="http://localhost:3000"

echo "🧪 Testing Data Unified API..."
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test function
test_endpoint() {
    local method=$1
    local endpoint=$2
    local data=$3
    local description=$4

    echo -e "${BLUE}Testing:${NC} $description"
    echo -e "${BLUE}Endpoint:${NC} $method $endpoint"

    if [ -z "$data" ]; then
        response=$(curl -s -X $method "$BASE_URL$endpoint")
    else
        response=$(curl -s -X $method "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data")
    fi

    success=$(echo "$response" | jq -r '.success // false')

    if [ "$success" = "true" ]; then
        echo -e "${GREEN}✓ Success${NC}"
    else
        echo -e "${RED}✗ Failed${NC}"
        echo "Response: $response"
    fi
    echo ""
}

# 1. Health check
test_endpoint "GET" "/_health" "" "Health Check"

# 2. API info
test_endpoint "GET" "/" "" "API Information"

# 3. Seed data
echo -e "${BLUE}Seeding sample data...${NC}"
test_endpoint "POST" "/seed" "" "Seed Sample Data"

# 4. Create a user
test_endpoint "POST" "/users" '{
  "userId": "test_user_1",
  "username": "testuser",
  "email": "test@example.com"
}' "Create User"

# 5. Create an event
test_endpoint "POST" "/events" '{
  "userId": "test_user_1",
  "eventType": "page_view",
  "eventData": {
    "page": "/test",
    "category": "testing"
  }
}' "Create Event"

# 6. Get event statistics
test_endpoint "GET" "/analytics/events/stats" "" "Get Event Statistics"

# 7. Get user activity
test_endpoint "GET" "/analytics/users/activity" "" "Get User Activity"

# 8. Get time series data
test_endpoint "GET" "/analytics/timeseries?days=7" "" "Get Time Series Data"

# 9. Get top users
test_endpoint "GET" "/analytics/users/top?limit=5" "" "Get Top Users"

# 10. Execute custom query
test_endpoint "POST" "/analytics/query" '{
  "sql": "SELECT COUNT(*) as total FROM events",
  "useCache": true
}' "Execute Custom Query"

# 11. Get cache info
test_endpoint "GET" "/cache/info" "" "Get Cache Information"

# 12. Cache performance test
echo -e "${BLUE}Testing cache performance...${NC}"
echo "First request (cache miss):"
time curl -s "$BASE_URL/analytics/events/stats" > /dev/null
echo ""
echo "Second request (cache hit):"
time curl -s "$BASE_URL/analytics/events/stats" > /dev/null
echo ""

echo -e "${GREEN}✅ All tests completed!${NC}"
