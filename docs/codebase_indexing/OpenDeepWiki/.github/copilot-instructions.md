# OpenDeepWiki Development Guide for AI Agents

## Project Overview

**OpenDeepWiki** is an AI-driven code knowledge base system built on **.NET 9** and **Semantic Kernel**. It analyzes code repositories, generates documentation, creates directory structures, and supports MCP (Model Context Protocol) for AI integration.

### Core Purpose
- Convert GitHub/GitLab/Gitee repositories into searchable knowledge bases
- Auto-generate documentation, READMEs, and code analysis via LLM
- Support multiple AI providers (OpenAI, AzureOpenAI, Anthropic)
- Provide MCP endpoints for AI agents to query repository knowledge

---

## Architecture

### Full-Stack Structure
```
Backend: .NET 9 ASP.NET Core + Entity Framework Core + Semantic Kernel
Frontend: React 19 + TypeScript + Vite + TailwindCSS + Shadcn/ui
Database: SQLite/PostgreSQL/MySQL/SQL Server (configurable)
Deployment: Docker Compose or Sealos
```

### Backend Layer Breakdown

**`src/KoalaWiki/`** - Main ASP.NET Core application
- **`BackendService/`** - Background task orchestration (warehouse sync, document processing)
- **`KoalaWarehouse/`** - Core document analysis engine:
  - **`Pipeline/`** - Resilient document processing pipeline with 5 ordered steps
  - **`GenerateThinkCatalogue/`** - AI-powered directory structure generation
  - **`DocumentPending/`** - Incomplete document task handling
  - **`MiniMapService.cs`** - Generates knowledge graphs via Mermaid

**`KoalaWiki.Core/`** - Data access layer
- **`DataAccess/IKoalaWikiContext.cs`** - DbSet definitions for 18+ entity types
- **`ServiceExtensions.cs`** - DI registration for database providers

**`KoalaWiki.Domains/`** - Domain models
- **`Warehouse.cs`** - Repository metadata and configuration
- **`Document.cs`** - Document content and metadata
- **`DocumentFile/`** - File structure and catalog definitions
- **`FineTuning/`** - Training dataset generation
- **`MCP/`** - Model Context Protocol entities

**`Provider/`** - Database implementations
- `KoalaWiki.Provider.PostgreSQL`
- `KoalaWiki.Provider.MySQL`
- `KoalaWiki.Provider.SqlServer`

### Frontend Layer Breakdown

**`web-site/src/`** - React application
- **`pages/`** - Route-based page components: `home`, `auth`, `admin`, `repository`, `chat`
- **`components/`** - Reusable UI components (RepositoryLayout, AdminLayout)
- **`services/`** - HTTP API clients and API wrappers
- **`stores/`** - Zustand state management stores
- **`i18n/`** - Internationalization (Chinese, English, French)
- **`routes/`** - React Router configuration with lazy loading

---

## Critical Data Flows

### 1. Repository Analysis Flow (README from README.md)
```
Clone Repository → .gitignore Filtering → Directory Scanning → 
AI Smart Filter (if file count > threshold) → Directory JSON → 
Generate README → Project Classification → Project Overview → 
Save to Database → Generate Task List (Think Catalogue) → 
Process Documents Recursively → Generate Commit Log
```

### 2. Document Processing Pipeline (5-Step Architecture)
Located in `KoalaWarehouse/Extensions/ServiceCollectionExtensions.cs`:

**Execution Order:**
1. **ReadmeGenerationStep** - Generate README.md
2. **CatalogueGenerationStep** - Create directory structure
3. **ProjectClassificationStep** - Classify project type
4. **DocumentStructureGenerationStep** - Build document TOC
5. **DocumentContentGenerationStep** - Generate document content

**Key Classes:**
- `ResilientDocumentProcessingPipeline` - Wraps pipeline with retry/fallback logic
- `DocumentProcessingContext` - Carries data through steps
- `DocumentProcessingOrchestrator` - Orchestrates with OpenTelemetry tracing

### 3. AI Kernel Initialization (KernelFactory Pattern)
`KernelFactory.GetKernel()` initializes Semantic Kernel with:
- **LLM Provider Selection**: OpenAI or AzureOpenAI via `OpenAIOptions.ModelProvider`
- **Plugins Loaded**:
  - Code Analysis plugins (in `plugins/CodeAnalysis/`) with `.skprompt.txt` prompts
  - FileTool plugin - reads repository files with token limits
  - AgentTool plugin - MCP integration
  - Dynamic MCP service loading from `DocumentOptions.McpStreamable`
- **Custom HttpClient** - Handles gzip/brotli decompression

---

## Key Development Workflows

### Build & Run

**Frontend:**
```bash
cd web-site
npm install
npm run dev          # Dev server at localhost:5173
npm run build        # Build to ../src/KoalaWiki/wwwroot
npm run build:analyze  # Bundle analysis
npm run lint         # ESLint check
```

**Backend:**
```bash
dotnet build KoalaWiki.sln
dotnet run --project src/KoalaWiki/KoalaWiki.csproj
# API at http://localhost:5085, OpenAPI at /scalar
```

**Docker (with make/Makefile):**
```bash
make build              # Build all images
make build-frontend     # Frontend only
make dev               # Run all services with logs
make dev-backend       # Backend only
make build-arm         # ARM64 architecture
make build-amd         # AMD64 architecture
```

### Database Migrations

Entity Framework Core migrations (in `KoalaWiki.Core/`):
```bash
dotnet ef migrations add <MigrationName> --project KoalaWiki.Core --startup-project src/KoalaWiki/KoalaWiki.csproj
dotnet ef database update --project KoalaWiki.Core --startup-project src/KoalaWiki/KoalaWiki.csproj
```

### Environment Configuration

Critical environment variables in `docker-compose.yml`:
- **`CHAT_MODEL`** (required) - Must support function calling (DeepSeek-V3, GPT-4-turbo)
- **`ANALYSIS_MODEL`** (optional) - Defaults to CHAT_MODEL; recommend GPT-4.1 for better dir structure
- **`CHAT_API_KEY`** - LLM API credential
- **`ENDPOINT`** - API base URL (e.g., https://api.openai.com/v1)
- **`MODEL_PROVIDER`** - OpenAI or AzureOpenAI
- **`DB_TYPE`** - sqlite, postgres, mysql, sqlserver
- **`DB_CONNECTION_STRING`** - Database connection
- **`LANGUAGE`** - Document generation language (default: Chinese)
- **`READ_MAX_TOKENS`** - Token limit for file reading (recommended: 70% of model max)
- **`MCP_STREAMABLE`** - Format: `serviceName=url` (e.g., `claude=http://localhost:8080/api/mcp`)

---

## Project-Specific Patterns & Conventions

### 1. FastAPI Service Pattern
Services inherit from `FastApi` (from FastService NuGet):
```csharp
public class RepositoryService(IKoalaWikiContext db) : FastApi
{
    [HttpGet("/repos")]
    public async Task<List<Warehouse>> GetRepositories()
    {
        // Endpoint auto-exposed via FastService
    }
}
```
- Automatically registers routes without explicit Route attributes
- DI via constructor parameters
- Response mapping via Mapster

### 2. Entity & Domain Model Structure
Base entity in `KoalaWiki.Domains/Entity.cs`:
```csharp
public class Entity<TKey> : IEntity<TKey>, ICreateEntity
{
    public TKey Id { get; set; }
    public DateTime CreatedAt { get; set; }
}
```
- All domain entities inherit this with generic TKey (usually int/string)
- `ICreateEntity` marks automatic timestamp tracking
- Models in `KoalaWiki.Domains/` mapped to database via EF Core

### 3. Semantic Kernel Prompt Files
Located in `src/KoalaWiki/plugins/CodeAnalysis/`:
```
plugins/
├── GenerateReadme/
│   ├── config.json        # Plugin metadata
│   └── skprompt.txt       # Semantic Kernel prompt template
├── CommitAnalyze/
├── GenerateDescription/
└── FunctionPrompt/
```
- `config.json` - Defines function signature, input/output schema
- `skprompt.txt` - Template with `{{$variable}}` syntax (Semantic Kernel format, NOT Handlebars)
- Loaded dynamically in `KernelFactory.GetKernel()`

### 4. Pipeline Context Flow Pattern
```csharp
// DocumentProcessingContext carries state through pipeline steps
public class DocumentProcessingContext
{
    public Document Document { get; init; }
    public Warehouse Warehouse { get; init; }
    public IKoalaWikiContext DbContext { get; init; }
    public Kernel? KernelInstance { get; set; }  // Set in pipeline
    public string? GeneratedReadme { get; set; }
    public DocumentCatalog? Catalogue { get; set; }
}
```
- Each step reads input, modifies context, passes to next step
- Stored kernel instance reused across steps to save initialization overhead

### 5. i18n Convention (Frontend)
`web-site/src/i18n/` structure:
- **`locales/`** - JSON translation files (en.json, zh.json, fr.json)
- **`mergeBundles.ts`** - Combines namespace bundles into single files
- **`i18n.ts`** - i18next initialization
- Usage: `const { t } = useTranslation('common')`
- Build command: `npm run merge-i18n`

### 6. Component Lazy Loading (Frontend)
Routes use `lazy()` + `Suspense`:
```tsx
const RepositoryLayout = lazy(() => import('@/components/layout/RepositoryLayout'))

<Suspense fallback={<Loading />}>
  <RepositoryLayout />
</Suspense>
```
- Reduces initial bundle size
- Fallback component shows during load

### 7. State Management (Frontend)
Zustand stores in `web-site/src/stores/`:
```typescript
const useAuthStore = create((set) => ({
  isAuthenticated: false,
  setAuthenticated: (value) => set({ isAuthenticated: value }),
}))
```
- Lightweight, zero-boilerplate state
- Avoid Redux complexity

### 8. MCP Integration Points
- **Backend MCP Server**: `src/KoalaWiki/MCP/` exposes repository knowledge
- **MCP Client Tools**: `KernelFactory.GetKernel()` loads tools from external MCPs
- **Streamable Config**: `DocumentOptions.McpStreamable` parses `MCP_STREAMABLE` env var

---

## Integration Points & External Dependencies

### LLM Providers
- **OpenAI / AzureOpenAI** - Via Semantic Kernel connectors
- **Anthropic** - Planned support
- **DeepSeek** - Tested with DeepSeek-V3 model
- **Custom Endpoints** - Use `ENDPOINT` env var for API-compatible services

### Git Integration
- **LibGit2Sharp** - Clone, read .gitignore, commit history
- **Octokit** - GitHub API for repo metadata (optional)
- Repository cloned to `KOALAWIKI_REPOSITORIES` directory

### Data Storage
- **Entity Framework Core** - ORM with provider abstraction
- **4 Database Backends** - Pluggable at compile time via Provider projects

### Frontend UI Framework
- **Shadcn/ui** - Headless component library (based on Radix UI)
- **TailwindCSS** - Utility-first styling with Vite plugin
- **Lucide React** - Icon library
- **React Hook Form** + **Zod** - Form handling & validation

### Build Tools
- **Vite 7.x** - Frontend bundler with gzip/brotli compression
- **SWC** - Faster TypeScript compilation (via `@vitejs/plugin-react-swc`)
- **.NET 9** - C# 13 language features
- **Docker** - Multi-stage builds for production

---

## Common Commands Quick Reference

| Task | Command |
|------|---------|
| **Frontend dev** | `cd web-site && npm run dev` |
| **Frontend build** | `cd web-site && npm run build` |
| **Backend run** | `dotnet run --project src/KoalaWiki/KoalaWiki.csproj` |
| **Build all Docker** | `make build` (or `docker-compose build`) |
| **Run all services** | `make dev` (shows logs) |
| **Stop services** | `docker-compose down` |
| **View logs** | `docker-compose logs -f` |
| **DB migration** | `dotnet ef migrations add MigrationName --project KoalaWiki.Core` |
| **Lint frontend** | `cd web-site && npm run lint` |
| **Clean build** | `make clean` |

---

## Debugging & Tracing

### OpenTelemetry Integration
- **`DocumentProcessingOrchestrator`** uses `ActivitySource` for tracing
- **Dashboard**: Aspire Dashboard at `http://localhost:18888` (in docker-compose)
- Tags automatically captured: warehouse ID, document ID, processing duration

### Logging
- **Serilog** configured in `Program.cs`
- **Sinks**: Console, File
- **Configuration**: `appsettings.json`, `appsettings.Development.json`
- Backend logs shown in: `docker-compose logs -f koalawiki`

### Frontend DevTools
- **React DevTools** - Component inspection
- **Network tab** - API calls to `/api/` proxied to backend
- **Console** - Error/warning output
- **Vite HMR** - Hot module replacement on file save

---

## File Structure Reference

**Key Files for Common Tasks:**
- **Add database entity**: `KoalaWiki.Domains/` + migration in `KoalaWiki.Core/`
- **Add API endpoint**: Create `Services/*.cs` inheriting `FastApi`
- **Add frontend page**: Create in `web-site/src/pages/` + route in `web-site/src/routes/index.tsx`
- **Update prompts**: Edit `src/KoalaWiki/plugins/CodeAnalysis/*/skprompt.txt`
- **Add i18n strings**: Update `web-site/src/i18n/locales/*.json`
- **Configure build**: `web-site/vite.config.ts` for frontend, `src/KoalaWiki/KoalaWiki.csproj` for backend

---

## Notes for AI Agents

1. **Token Budget**: Set `READ_MAX_TOKENS` to 70% of model max tokens to leave headroom for processing
2. **Model Requirements**: CHAT_MODEL must support function calling (GPT-4, DeepSeek-V3, Claude 3.5)
3. **MCP Extensibility**: Add tools to pipeline by registering MCPs in `DocumentOptions.McpStreamable`
4. **Database Flexibility**: Each database provider is a separate project; migrate to new DB by swapping reference
5. **Frontend Caching**: Built frontend deployed as static files in `wwwroot/`; no need to rebuild frontend for backend-only changes
6. **Async-First**: Most services use `async/await`; pipeline steps must be async
7. **Error Handling**: Pipeline has resilient wrapper (`ResilientDocumentProcessingPipeline`); step failures logged but may fall back
