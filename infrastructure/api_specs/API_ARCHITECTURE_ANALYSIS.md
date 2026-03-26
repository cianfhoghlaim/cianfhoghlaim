# API Specifications and Integration Patterns Analysis

## Executive Summary

Your infrastructure contains **three distinct API integration approaches** with varying maturity levels:

1. **OpenAPI Specifications** (Existing, structured)
2. **oRPC Framework** (Modern, type-safe, recommended)
3. **Compose Services** (Emerging, needs coordination)

This analysis provides recommendations for unifying these patterns under a cohesive API layer.

---

## 1. Existing OpenAPI Specifications

### Located Files
- `/infrastructure/api/cognee-openapi.json` - Cognee knowledge graph API
- `/infrastructure/api/firecrawl-v1-openapi.json` - Web scraping/crawling API
- `/infrastructure/api/agno.json` - Agent framework API
- `/infrastructure/api/apis.md` - API catalog documentation

### Cognee API (Knowledge Graph)
**Version:** 3.1.0
**Focus:** Knowledge graph operations with dataset management

#### Core Endpoints
```
POST /api/add                          - Add text data to datasets
POST /api/cognify                      - Transform data into knowledge graphs
POST /api/search                       - Semantic search across graphs
DELETE /api/delete                     - Delete data by ID
GET  /api/visualize                    - Generate graph visualizations
POST /api/datasets/                    - Create/list datasets
DELETE /api/datasets/{dataset_id}      - Delete entire dataset
POST /api/permissions/*                - Role/tenant management
```

#### Authentication
- API Key auth via `X-Api-Key` header
- Bearer token support
- Dataset-level access control

#### Notable Patterns
- UUID-based resource identification
- Comprehensive permission model (roles, tenants, principals)
- Background job support (`run_in_background` parameter)
- Custom prompt injection for LLM operations

### Firecrawl API
**Version:** 3.0.0
**Focus:** Web scraping and LLM-powered data extraction

#### Core Endpoints
```
POST /scrape                           - Scrape URL with LLM extraction
```

#### Key Features
- Bearer token authentication
- Complex request/response schemas with LLM options
- Payment-based rate limiting (402, 429 status codes)

### Observations
- OpenAPI specs are **well-documented** and **comprehensive**
- Missing: Service-to-service communication specifications
- Missing: Event/webhook definitions
- Missing: gRPC or Protocol Buffer definitions for high-performance services

---

## 2. oRPC Framework Implementation

### What is oRPC?
oRPC = **OpenRPC** - Type-safe RPC framework for TypeScript/Node.js

**Key Advantages:**
- Type-safe request/response contracts (Zod schemas)
- Auto-generates OpenAPI specs from contracts
- Unified RPC + OpenAPI endpoints
- Zero runtime type assertions
- TanStack Query integration

### Existing oRPC Examples

#### A. Learn-oRPC (Single Service)
**Location:** `/web/examples/orpc/learn-orpc/`

**Structure:**
```
- app/router/auth.ts          - Auth procedures
- app/router/todo.ts          - Todo procedures
- app/api/[[...rest]]/route.ts - OpenAPI + RPC handlers
- lib/orpc.ts                 - Client setup
- lib/orpc.server.ts          - Server setup
```

**Dependencies:**
```json
{
  "@orpc/client": "^1.8.6",
  "@orpc/openapi": "^1.8.6",
  "@orpc/server": "^1.8.6",
  "@orpc/tanstack-query": "^1.8.6",
  "@orpc/zod": "^1.8.6"
}
```

**Example Contract:**
```typescript
export const greetingPublic = {
    greeting: oc
        .input(z.object({ name: z.string().optional() }))
        .output(z.object({ text: z.string() }))
} as const;
```

#### B. Multi-Service Monorepo (Production Pattern)
**Location:** `/web/examples/orpc/orpc-multiservice-monorepo-playground/`

**Architecture:**
```
packages/
├── auth-contract/         - Shared type definitions
├── auth-service/          - Auth service router + handlers
├── chat-contract/         - Chat types
├── chat-service/          - Chat service
└── planet-contract/       - Planet types
   └── planet-service/     - Planet service

apps/
├── api/                   - Unified API gateway
│   ├── service-auth.ts    - Auth service RPC/OpenAPI handlers
│   ├── service-chat.ts    - Chat service handlers
│   ├── service-planet.ts  - Planet service handlers
│   ├── main.ts            - Server startup (routes & prefixes)
│   └── spec.ts            - OpenAPI spec generation
└── web/                   - Frontend client
```

**Request Flow:**
```
Client Request
    ↓
main.ts (HTTP Server)
    ├→ /rpc/auth/*        → authServiceRPCHandler
    ├→ /api/auth/*        → authServiceOpenAPIHandler (REST)
    ├→ /rpc/planet/*      → planetServiceRPCHandler
    ├→ /api/planet/*      → planetServiceOpenAPIHandler
    ├→ /rpc/chat/*        → chatServiceRPCHandler
    ├→ /api/chat/*        → chatServiceOpenAPIHandler
    └→ /openapi.json      → Generated spec
```

**Key Features:**
- **Shared Contracts:** Type definitions published separately
- **Dual Protocols:** Both RPC (performance) and REST (compatibility)
- **Generated Spec:** OpenAPI auto-generated with `OpenAPIGenerator` + `ZodToJsonSchemaConverter`
- **Unified Documentation:** Scalar API Reference UI at `/`
- **Authentication:** Bearer token in Authorization header

**Service Handler Pattern:**
```typescript
// service-auth.ts
export const authServiceRPCHandler = new RPCHandler(router, {
  plugins: [corsPlugin, loggingPlugin]
})

export const authServiceOpenAPIHandler = new OpenAPIHandler(router, {
  plugins: [corsPlugin, loggingPlugin]
})

// main.ts
const authServiceRPCHandleResult = await authServiceRPCHandler.handle(req, res, {
  prefix: '/rpc/auth',
  context: { authToken }
})

if (!authServiceRPCHandleResult.matched) {
  const authServiceOpenAPIHandleResult = await authServiceOpenAPIHandler.handle(req, res, {
    prefix: '/api/auth',
    context: { authToken }
  })
}
```

### oRPC Ecosystem
**Packages Used:**
- `@orpc/contract` - Contract definitions
- `@orpc/zod` - Zod schema support
- `@orpc/server/node` - Node.js server
- `@orpc/client/fetch` - Fetch-based client
- `@orpc/openapi/*` - OpenAPI generation
- `@orpc/tanstack-query` - TanStack Query integration
- `@orpc/experimental-pino` - Logging
- `@orpc/experimental-publisher` - Real-time events

---

## 3. Compose Stack Services (18 Services)

### AI/ML Layer
1. **Agno** (Agent framework) - `http://localhost:8000`
2. **Cognee** (Knowledge graphs) - Multi-service
3. **LiteLLM** (LLM proxy) - `http://localhost:4000`
4. **Crawl4AI** (Web scraping) - `http://localhost:11235`

### Infrastructure/Storage
5. **Memgraph** (Graph DB) - `bolt://localhost:7687`
6. **Qdrant** (Vector DB) - `http://localhost:6333`
7. **Garage** (S3-compatible storage) - `http://localhost:3900`
8. **Dragonfly** (Redis alternative) - `redis://localhost:6379`
9. **Dagster** (Orchestration) - `http://localhost:3001`

### Monitoring/Observability
10. **Langfuse** (LLM observability) - `http://localhost:3000`
11. **MLflow** (Experiment tracking) - `http://localhost:5000`
12. **Infisical** (Secrets management)

### Development/Utilities
13. **Forgejo** (Git platform)
14. **Supabase** (BaaS)
15. **Pangolin** (API gateway)
16. **Termix** (Terminal orchestration)
17. **Komodo** (Service synchronizer)

---

## 4. Data Layer APIs (Python)

### Location
`/data/` - Unified pipeline structure

### Key Pipelines
1. **docs_to_knowledge** - Document processing
2. **github_to_r2** - Repository scraping
3. **youtube_to_knowledge** - Video transcription
4. **shared/dlt_sources.py** - Data source definitions

### Current Patterns
- Modal distributed execution
- Firecrawl API integration
- CLI-based (Typer), not REST
- No unified service layer

---

## Recommendations for Unified API Layer

### Phase 1: oRPC Contract Layer

#### 1.1 Create Contract Packages
```
infrastructure/api/
├── contracts/
│   ├── common-schema.ts
│   ├── llm-contract.ts
│   ├── cognee-contract.ts
│   └── scraping-contract.ts
├── services/
│   ├── litellm-service.ts
│   ├── cognee-service.ts
│   └── crawl4ai-service.ts
└── gateway/
    ├── main.ts
    ├── router.ts
    └── middleware.ts
```

#### 1.2 LLM Contract Example
```typescript
// infrastructure/api/contracts/llm-contract.ts
import { oc } from '@orpc/contract'
import { z } from 'zod'

const modelSchema = z.enum([
  'gpt-4o',
  'claude-3-5-sonnet',
  'gemini-2.5-pro',
  'deepseek-r1',
])

export const llmContract = {
  chat: oc
    .input(z.object({
      model: modelSchema,
      messages: z.array(z.object({
        role: z.enum(['user', 'assistant', 'system']),
        content: z.string(),
      })),
      temperature: z.number().min(0).max(2).optional(),
      maxTokens: z.number().int().positive().optional(),
    }))
    .output(z.object({
      text: z.string(),
      usage: z.object({
        input: z.number(),
        output: z.number(),
      }),
    })),

  listModels: oc
    .output(z.array(z.object({
      name: modelSchema,
      available: z.boolean(),
    }))),
}
```

### Phase 2: Unified API Gateway

#### 2.1 Gateway Router
```typescript
// infrastructure/api/gateway/router.ts
import { router } from '@orpc/server'
import { llmRouter } from '../services/litellm-service'
import { cogneeRouter } from '../services/cognee-service'
import { scrapingRouter } from '../services/crawl4ai-service'

export const apiRouter = router({
  llm: llmRouter,
  cognee: cogneeRouter,
  scraping: scrapingRouter,
})
```

#### 2.2 Gateway Server
```typescript
// infrastructure/api/gateway/main.ts
import { createServer } from 'http'
import { RPCHandler } from '@orpc/server/node'
import { OpenAPIHandler } from '@orpc/openapi/node'
import { apiRouter } from './router'

const rpcHandler = new RPCHandler(apiRouter)
const openAPIHandler = new OpenAPIHandler(apiRouter)

const server = createServer(async (req, res) => {
  // Try RPC first (performance)
  const rpcResult = await rpcHandler.handle(req, res, {
    prefix: '/rpc',
    context: createContext(req),
  })
  
  if (!rpcResult.matched) {
    // Fall back to OpenAPI (REST)
    const openAPIResult = await openAPIHandler.handle(req, res, {
      prefix: '/api',
      context: createContext(req),
    })
  }
})

server.listen(8080, () => {
  console.log('API Gateway running on http://localhost:8080')
  console.log('OpenAPI spec: http://localhost:8080/openapi.json')
})
```

#### 2.3 Docker Compose
```yaml
# infrastructure/compose/api-gateway/compose.yaml
version: '3.8'

services:
  gateway:
    build: ../../../infrastructure/api/gateway
    ports:
      - "8080:8080"
    depends_on:
      - litellm
      - cognee
      - crawl4ai
    environment:
      LITELLM_URL: http://litellm:4000
      COGNEE_URL: http://cognee:8000
      CRAWL4AI_URL: http://crawl4ai:11235
    networks:
      - api-network

networks:
  api-network:
    name: api-network
```

### Phase 3: Service Mesh (Long-term)

**Recommended Tools:**
- Service discovery: Consul or Kubernetes DNS
- Load balancing: Traefik or Kong
- Observability: OpenTelemetry + Jaeger
- Event streaming: Redis pub-sub or Kafka

### Phase 4: API Documentation

```markdown
# API Gateway

## Endpoints

### RPC (Type-safe, performance)
- POST /rpc/llm/chat
- POST /rpc/cognee/search
- POST /rpc/scraping/scrape

### REST (Compatibility)
- POST /api/llm/chat
- POST /api/cognee/search
- POST /api/scraping/scrape

### Documentation
- GET / - Scalar API Reference UI
- GET /openapi.json - OpenAPI 3.1.0 spec
```

---

## Implementation Timeline

### Immediate (Week 1-2)
1. Create contract packages in `infrastructure/api/contracts/`
2. Extract Zod schemas from existing OpenAPI specs
3. Set up monorepo with shared contracts

### Short-term (Week 3-4)
1. Implement service wrappers for LiteLLM, Cognee, Crawl4AI
2. Build unified gateway with RPC + OpenAPI
3. Generate and serve spec at `/openapi.json`

### Medium-term (Week 5-8)
1. Wrap remaining services (Dagster, MLflow, Langfuse)
2. Add inter-service authentication
3. Implement healthchecks
4. Set up documentation portal

### Long-term
1. Kubernetes deployment
2. Service mesh (Istio)
3. Event streaming layer
4. API governance

---

## Summary Comparison

| Aspect | Current | Recommended |
|--------|---------|-------------|
| **Protocol** | REST only | RPC + REST |
| **Type Safety** | OpenAPI schemas | Zod + oRPC |
| **Documentation** | Manual | Auto-generated |
| **Service Discovery** | Hardcoded URLs | Environment-based |
| **Authentication** | Per-service | Unified context |
| **Developer Experience** | Swagger UI | Type-safe clients |

---

## Conclusion

Your infrastructure has excellent foundations. By adopting **oRPC as the unified contract layer**, you can:

1. Ensure type-safety across all services
2. Auto-generate OpenAPI specs
3. Support both RPC (performance) and REST (compatibility)
4. Build a foundation for future service mesh patterns
5. Improve developer experience with type-safe clients

The key is establishing **contracts first**, then gradually wrapping existing services.
