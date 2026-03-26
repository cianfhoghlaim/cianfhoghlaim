# API Architecture Quick Reference

## Three-Tier API Landscape

### Tier 1: OpenAPI Specifications (Current)
- **Cognee** - Knowledge graphs (3.1.0)
- **Firecrawl** - Web scraping (3.0.0)
- **Agno** - Agent framework
- **Status:** Isolated, well-documented

### Tier 2: oRPC Framework (Recommended)
- **Learn-oRPC** - Single service pattern
- **Multi-Service Playground** - Production pattern
- **Status:** Modern, type-safe, ready to adopt

### Tier 3: Compose Services (18 Stacks)
**AI/ML:** Agno, Cognee, LiteLLM, Crawl4AI
**Storage:** Memgraph, Qdrant, Garage, Dragonfly, Dagster
**Observability:** Langfuse, MLflow
**Status:** Isolated, need unification

---

## Recommended Path Forward

### Step 1: Contract-First Design
```typescript
// infrastructure/api/contracts/llm-contract.ts
import { oc } from '@orpc/contract'
import { z } from 'zod'

export const llmContract = {
  chat: oc
    .input(z.object({
      model: z.enum(['gpt-4o', 'claude-3-5-sonnet']),
      messages: z.array(z.object({
        role: z.enum(['user', 'assistant']),
        content: z.string()
      }))
    }))
    .output(z.object({
      text: z.string(),
      usage: z.object({ input: z.number(), output: z.number() })
    }))
}
```

### Step 2: Service Wrapper
```typescript
// infrastructure/api/services/litellm-service.ts
import { router } from '@orpc/server'
import { llmContract } from '../contracts/llm-contract'

export const llmRouter = router({
  chat: llmContract.chat.handler(async (input, context) => {
    // Delegate to http://litellm:4000
    const response = await fetch('http://litellm:4000/v1/chat/completions', {
      method: 'POST',
      body: JSON.stringify({...})
    })
    return response.json()
  })
})
```

### Step 3: Unified Gateway
```typescript
// infrastructure/api/gateway/main.ts
import { createServer } from 'http'
import { RPCHandler } from '@orpc/server/node'
import { OpenAPIHandler } from '@orpc/openapi/node'
import { apiRouter } from './router'

const server = createServer(async (req, res) => {
  const rpcResult = await new RPCHandler(apiRouter).handle(req, res, {
    prefix: '/rpc'
  })
  
  if (!rpcResult.matched) {
    await new OpenAPIHandler(apiRouter).handle(req, res, {
      prefix: '/api'
    })
  }
})

server.listen(8080)
```

### Step 4: Docker Compose
```yaml
# infrastructure/compose/api-gateway/compose.yaml
version: '3.8'

services:
  gateway:
    build: ../../../infrastructure/api/gateway
    ports:
      - "8080:8080"
    environment:
      LITELLM_URL: http://litellm:4000
      COGNEE_URL: http://cognee:8000
    networks:
      - api-network
```

---

## Implementation Checklist

- [ ] Create `infrastructure/api/contracts/` directory
- [ ] Extract Zod schemas from OpenAPI specs
- [ ] Define contracts: llm, cognee, scraping
- [ ] Set up monorepo with `@repo/` namespacing
- [ ] Build LiteLLM service wrapper
- [ ] Build Cognee service wrapper
- [ ] Create unified gateway
- [ ] Generate spec at `/openapi.json`
- [ ] Serve API docs at Scalar UI
- [ ] Add healthchecks
- [ ] Implement inter-service auth
- [ ] Document API catalog

---

## Key Benefits

| Feature | Benefit |
|---------|---------|
| **Type Safety** | Zod schemas guarantee validation |
| **Dual Protocol** | RPC (fast) + REST (compatible) |
| **Auto Docs** | Specs generated from code |
| **DX** | Type-safe client generation |
| **Scalability** | Foundation for service mesh |

---

## Files & References

**Analysis:** `API_ARCHITECTURE_ANALYSIS.md`
**OpenAPI Specs:** `cognee-openapi.json`, `firecrawl-v1-openapi.json`
**oRPC Examples:** `/web/examples/orpc/`
**Compose Stacks:** `/infrastructure/compose/`

---

## Quick Links

- oRPC Docs: https://orpc.unnoq.com
- OpenAPI 3.1: https://spec.openapis.org/oas/v3.1.0
- Zod: https://zod.dev
- Scalar API Ref: https://scalar.com

---

## Contact & Questions

Review the detailed `API_ARCHITECTURE_ANALYSIS.md` for:
- Complete service inventory
- Implementation timeline (phases)
- Code examples
- Service mesh options
- API governance strategy

**Status:** Analysis Complete | Ready for Phase 1 Implementation
