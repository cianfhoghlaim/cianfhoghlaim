#!/bin/bash

# ============================================================================
# API Unified - cURL Examples
# ============================================================================

BASE_URL="http://localhost:3000"
AUTH_TOKEN="token-1"

echo "================================"
echo "API Unified - cURL Examples"
echo "================================"
echo ""

# ============================================================================
# Root Endpoint
# ============================================================================

echo "1. Get API Info"
echo "---"
curl -s "${BASE_URL}/" | jq .
echo ""
echo ""

# ============================================================================
# OpenAPI Endpoints
# ============================================================================

echo "2. Get Server Health (OpenAPI)"
echo "---"
curl -s "${BASE_URL}/api/public/health" | jq .
echo ""
echo ""

echo "3. Get Server Info (OpenAPI)"
echo "---"
curl -s "${BASE_URL}/api/public/info" | jq .
echo ""
echo ""

# ============================================================================
# Authentication
# ============================================================================

echo "4. Sign Up New User (OpenAPI)"
echo "---"
curl -s -X POST "${BASE_URL}/api/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "name": "Test User",
    "password": "password123"
  }' | jq .
echo ""
echo ""

echo "5. Sign In (OpenAPI)"
echo "---"
curl -s -X POST "${BASE_URL}/api/auth/signin" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "demo@example.com",
    "password": "password123"
  }' | jq .
echo ""
echo ""

echo "6. Get Current User (OpenAPI)"
echo "---"
curl -s "${BASE_URL}/api/auth/me" \
  -H "Authorization: Bearer ${AUTH_TOKEN}" | jq .
echo ""
echo ""

# ============================================================================
# Todo Operations (OpenAPI)
# ============================================================================

echo "7. Create Todo (OpenAPI)"
echo "---"
curl -s -X POST "${BASE_URL}/api/todo/create" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${AUTH_TOKEN}" \
  -d '{
    "title": "Build unified API",
    "description": "Combine MCP, oRPC, and AI streaming"
  }' | jq .
echo ""
echo ""

echo "8. List Todos (OpenAPI)"
echo "---"
curl -s "${BASE_URL}/api/todo/list?limit=10" \
  -H "Authorization: Bearer ${AUTH_TOKEN}" | jq .
echo ""
echo ""

echo "9. Update Todo (OpenAPI)"
echo "---"
curl -s -X POST "${BASE_URL}/api/todo/update" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${AUTH_TOKEN}" \
  -d '{
    "id": "1",
    "completed": true
  }' | jq .
echo ""
echo ""

# ============================================================================
# oRPC Endpoints
# ============================================================================

echo "10. Create Todo (oRPC)"
echo "---"
curl -s -X POST "${BASE_URL}/rpc/todo/create" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${AUTH_TOKEN}" \
  -d '{
    "title": "Learn oRPC patterns",
    "description": "Type-safe RPC is awesome"
  }' | jq .
echo ""
echo ""

echo "11. List Todos (oRPC)"
echo "---"
curl -s -X POST "${BASE_URL}/rpc/todo/list" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${AUTH_TOKEN}" \
  -d '{ "limit": 5 }' | jq .
echo ""
echo ""

# ============================================================================
# MCP Tool Calling
# ============================================================================

echo "12. MCP - Add Numbers"
echo "---"
curl -s -X POST "${BASE_URL}/mcp" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "add",
      "arguments": { "a": 15, "b": 27 }
    }
  }' | jq .
echo ""
echo ""

echo "13. MCP - Search"
echo "---"
curl -s -X POST "${BASE_URL}/mcp" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "search",
      "arguments": {
        "query": "typescript patterns",
        "limit": 5
      }
    }
  }' | jq .
echo ""
echo ""

echo "14. MCP - Analyze Text"
echo "---"
curl -s -X POST "${BASE_URL}/mcp" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "analyzeText",
      "arguments": {
        "text": "This API design is fantastic and very well structured!",
        "includeEntities": true,
        "includeSentiment": true
      }
    }
  }' | jq .
echo ""
echo ""

echo "15. MCP - List Tools"
echo "---"
curl -s -X POST "${BASE_URL}/mcp" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 4,
    "method": "tools/list"
  }' | jq .
echo ""
echo ""

# ============================================================================
# AI Chat
# ============================================================================

echo "16. AI Chat - Simple Question"
echo "---"
curl -s -X POST "${BASE_URL}/ai/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      { "role": "user", "content": "What is MCP?" }
    ]
  }'
echo ""
echo ""
echo ""

echo "17. AI Chat with Tools - Math Problem"
echo "---"
curl -s -X POST "${BASE_URL}/ai/chat-with-tools" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      { "role": "user", "content": "What is 123 + 456? Use the add tool." }
    ]
  }'
echo ""
echo ""
echo ""

# ============================================================================
# Documentation
# ============================================================================

echo "18. Get OpenAPI Specification"
echo "---"
curl -s "${BASE_URL}/api/~openapi.json" | jq '.info'
echo ""
echo ""

echo "================================"
echo "Examples Complete!"
echo ""
echo "View Swagger UI at: ${BASE_URL}/api/~docs"
echo "================================"
