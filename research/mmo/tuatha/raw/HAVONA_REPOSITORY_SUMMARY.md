# Havona Repository Summary

**AI-Optimized Documentation for Repository Analysis**

---

## Repository Overview

**Name:** Havona
**Purpose:** Trade contract and document management platform for international trade using blockchain-based data persistence
**Location:** `/Users/cliste/dev/bonneagar/flows/crypto/havona`
**Git Branch:** `onboarding` (main branch: `main`)
**Status:** Clean working tree

---

## Core Architecture

### Dual Persistence Strategy

Havona uses a sophisticated dual persistence approach:

1. **DGraph** - Fast, searchable GraphQL interface for real-time data access
2. **Blockchain (TEN Network)** - Immutable audit trail and verification with TEE privacy
3. **Field History** - Comprehensive change tracking for regulatory compliance

### Development Philosophy

- **Schema-First Development** - All types defined in GraphQL, code generated for all languages
- **Multi-Tenant Architecture** - Complete namespace isolation per organization
- **Dynamic Type Handling** - API can process any schema type automatically

---

## Cryptocurrency & Blockchain Implementation

### Network Configuration

| Environment | Type | Contract Address | Purpose |
|-------------|------|------------------|---------|
| **Local** | Anvil | `0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512` | Development and testing |
| **UAT** | Ten Testnet | `0xD8010Dbf1254D9cfE81e1b508ebCf78006fBaa79` | User acceptance testing with TEE |
| **Production** | TEN Network | *Configured separately* | Production with Trusted Execution Environment |

### Smart Contract Architecture

#### HavonaPersistor Contract

**Location:** `contracts/src/HavonaPersistor.sol`
**Solidity Version:** 0.8.20
**Security:** EIP-712, ReentrancyGuard, Ownable

**Key Features:**
- **CBOR-Encoded Storage** - Binary encoding for efficient on-chain data
- **EIP-712 Signatures** - Typed data signing for delegated transactions
- **Automatic Versioning** - Up to 100 versions per data key
- **Granular Access Control** - Per-key read permissions
- **TEN.xyz TEE Privacy** - Data encrypted in Trusted Execution Environment
- **Batch Operations** - Gas-optimized bulk storage (max 50 items)

**Storage Mechanism:**
```solidity
mapping(bytes32 => bytes) private dataBlobs;           // CBOR data storage
mapping(bytes32 => uint256) private blobVersions;      // Version tracking
mapping(bytes32 => mapping(address => bool)) public canAccess;  // Access control
mapping(bytes32 => bytes32) public contentHashes;      // Hash verification
mapping(address => uint256) public nonces;             // Replay protection
```

**Security Features:**
- Nonce-based replay attack prevention
- Signature expiry (maximum 1 hour)
- Content hash verification with keccak256
- Owner-only writes with granular read permissions

#### Supporting Contracts

- **HavonaMemberManager** - Member lifecycle and role management
- **CBOREncoding/CBORDecoding** - Binary data encoding utilities
- **ParentChild** - Hierarchical document relationships

### Blockchain Integration Flow

#### Write Operation
```
1. API receives JSON payload
2. Detect Pydantic model type via introspection
3. Validate against schema
4. Generate unique ID (HavonaIDGenerator)
5. Encode to CBOR format
6. Generate storage key (keccak256)
7. Sign with EIP-712 (if delegated submission)
8. Submit transaction to HavonaPersistor contract
9. Store in DGraph for fast queries
10. Return transaction receipt
```

#### Read Operation
```
1. Query DGraph for fast access (primary path)
2. Optionally verify with blockchain (audit path)
3. Decode CBOR to JSON
4. Return to API consumer
```

### Blockchain Service

**Implementation:** `server/api/services/blockchain.py`
**Library:** web3.py 7.5.0

**Responsibilities:**
- Web3 HTTP Provider connection management
- Account management with private keys
- Contract instance initialization with ABI
- Transaction signing and submission
- Connection health monitoring

### Privacy Model (TEN Network)

- **TEE Encryption** - Data encrypted at rest in Trusted Execution Environment
- **Access Control** - Smart contract enforces who can decrypt `eth_getLogs` responses
- **Admin Access** - Havona admin (contract owner) has full access
- **User Access** - Explicit permission required per data key via `canAccess` mapping

### Build & Deployment Tools

**Foundry:**
- Compiler: solc 0.8.20
- Optimizer: Enabled with viaIR
- Testing: Foundry test framework
- Deployment: Forge scripts in `script/` directory

**Hardhat:**
- Additional testing and deployment scripts
- Integration via `contracts/package.json`

**Local Deployment:**
```bash
cd contracts
anvil --host 0.0.0.0 --port 8545
forge script script/Deploy.s.sol --broadcast --rpc-url http://localhost:8545
```

---

## Docker & Compose File Management

### Multi-Environment Compose Strategy

Havona uses a **base + override** pattern for Docker Compose configuration:

**Base Configuration:** `docker/compose.yml` (313 lines)
**Overrides:** `compose-UAT.yml`, `compose-DEV.yml`, `compose-PROD.yml`

### Service Architecture

```
                    ┌─────────────────┐
                    │   React UI      │ :3000 (dev) / :8080 (prod)
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  Flask Server   │ :5000
                    └────┬────┬───┬───┘
                         │    │   │
        ┌────────────────┘    │   └──────────────┐
        │                     │                  │
┌───────▼────────┐   ┌────────▼────────┐   ┌────▼──────┐
│ DGraph Alpha   │   │    Blockchain   │   │   Redis   │
│ (GraphQL)      │   │     (Anvil)     │   │  (Cache)  │
│ :8080, :9080   │   │     :8545       │   │   :6379   │
└───────┬────────┘   └─────────────────┘   └───────────┘
        │
┌───────▼────────┐
│ DGraph Zero    │
│ (Coordinator)  │
│ :5080, :6080   │
└────────────────┘
```

### Core Services

#### 1. Redis (6379)
- **Image:** redis:8-alpine
- **Purpose:** Session storage, caching, pub/sub
- **Persistence:** AOF (Append-Only File)
- **Health Check:** `redis-cli ping`

#### 2. DGraph Cluster

**Zero (Coordinator):**
- **Ports:** 5080 (gRPC), 6080 (HTTP)
- **Purpose:** Cluster coordination and shard management
- **Command:** `dgraph zero --my=dgraph-zero:5080`

**Alpha (Database):**
- **Ports:** 8080 (GraphQL), 9080 (gRPC)
- **Purpose:** Database node with native GraphQL API
- **Features:** ACL, namespace isolation, schema management
- **ACL Secret:** Stored in `/data/acl-secret.txt` from `DGRAPH_ACL_SECRET` env var

#### 3. Namespace Service (5001)
- **Language:** Go microservice
- **Purpose:** DGraph v25 namespace management
- **Dependencies:** Requires healthy dgraph-alpha
- **Health Check:** `wget --spider http://localhost:5001/health`

#### 4. Blockchain (8545)
- **Type:** Anvil (local Ethereum node)
- **Dockerfile:** `docker/blockchain/Dockerfile`
- **Startup:** `start.sh` script deploys contracts on initialization
- **Persistence:** `blockchain_data` volume stores chain state

#### 5. Server (5000)
- **Dockerfile:** `docker/server/Dockerfile` (multi-stage: dev/production)
- **Dependencies:** redis, dgraph-alpha, namespace-service, blockchain
- **Environment:** Loads from `.env.local`, `.env.uat`, or `.env.prod`
- **Key Environment Variables:**
  - `CHAIN_RPC_URL` - Blockchain endpoint
  - `GRAPHQL_URL` - DGraph GraphQL endpoint
  - `REDIS_URL` - Redis connection string
  - `AUTH0_*` - Auth0 configuration
  - `NAMESPACE_SERVICE_URL` - Namespace service endpoint

#### 6. UI (3000 dev, 8080 prod)
- **Dockerfile:** `docker/ui/Dockerfile` (multi-stage: build/serve)
- **Development:** Vite dev server with HMR on port 3000
- **Production:** Static files served by `serve` on port 8080
- **Build Args:** `BUILD_ENV` (uat, prod)
- **UAT Memory Fix:** Production build mode prevents OOM issues

#### 7. Inference Service (5001) - Optional
- **Profile:** `inference`
- **Purpose:** GPU ML/AI inference
- **Conflict:** Port 5001 conflicts with namespace-service (use profiles to manage)

#### 8. Seed Services - Profile-Based
- **seed-init** - Initial data seeding
- **seed-verify** - Verify blockchain persistence
- **seed-reset** - Clean and re-seed

### Environment-Specific Configurations

**Local Development (`compose.yml`):**
- Development build targets
- Hot module reloading
- No resource limits
- Cloudflare Tunnel for Auth0 callbacks

**UAT (`compose-UAT.yml` overrides):**
```yaml
services:
  server:
    build:
      target: production
    env_file: ../server/.env.uat
    deploy:
      resources:
        limits:
          memory: 1G
  ui:
    build:
      target: production
    deploy:
      resources:
        limits:
          memory: 512M  # Production build uses less memory
```

**Production (`compose-PROD.yml`):**
- Production build targets
- Resource limits for cloud deployment
- Health check optimizations

### Volume Management

**Persistent Volumes:**
- `dgraph_zero_data` - DGraph coordinator state
- `dgraph_alpha_data` - DGraph database storage
- `blockchain_data` - Anvil chain state and deployed contract addresses
- `redis_data` - Redis AOF persistence
- `server_logs` - Application logs
- `inference_models` - ML model cache

### Network Configuration

**Network:** `havona-network`
**Driver:** bridge
**Subnet:** 172.20.0.0/16

All services communicate via this custom bridge network using service names as hostnames.

### Health Check Strategy

Each service defines health checks; dependent services use `condition: service_healthy`:
```yaml
depends_on:
  redis:
    condition: service_healthy
  dgraph-alpha:
    condition: service_healthy
```

### Service Profiles

**Default Profile:** Core services (redis, dgraph, blockchain, server, ui)
**Seed Profile:** Data seeding services
**Inference Profile:** Optional GPU inference

**Usage:**
```bash
# Start core services
docker compose up

# Start with seeding
docker compose --profile seed up

# Start with inference
docker compose --profile inference up
```

---

## API & Backend Architecture

### Technology Stack

- **Framework:** Flask 3.0.3
- **Language:** Python 3.11
- **Pattern:** Service-Oriented Architecture with Blueprint registration

### Entry Point: HavonaServer

**Location:** `server/api/havona.py`

**Responsibilities:**
- Service initialization and lifecycle management
- Flask app creation and configuration
- Middleware setup (CORS, namespace isolation)
- Blueprint registration for API routes
- Background thread management
- Graceful shutdown handling

### Service Layer

All services initialized by `HavonaServer` class:

#### ConfigService (`server/api/services/config.py`)
- Centralized configuration from environment variables
- Validation of required settings
- Environment-specific defaults

#### BlockchainService (`server/api/services/blockchain.py`)
- Web3 HTTP Provider connection
- Account management with private keys
- Contract instance initialization with ABI
- Transaction signing and submission
- Health checks and monitoring

#### AuthService (`server/api/services/auth.py`)
- Auth0 Management Client initialization
- JWT validation middleware
- Organization namespace mapping
- Admin domain handling (`@havona.io`)
- Can be disabled with `AUTH_DISABLED=true`

#### NamespaceService (`server/api/services/namespace.py`)
- Integration with Go microservice on port 5001
- Multi-tenant namespace isolation
- Namespace creation and management

#### RedisService (`server/api/services/redis.py`)
- Connection to Redis instance
- Caching layer for frequently accessed data
- Session storage

#### AIService (`server/api/services/ai.py`)
- LLM integration (Google Generative AI, LiteLLM)
- Prompt engineering utilities
- Structured outputs with Pydantic

### Blueprint Routes

Blueprints provide modular API route organization:

#### SimpleOnboarding (`server/api/blueprints/simple_onboarding.py` - 81KB)
**Endpoints:**
- `POST /api/onboard` - Complete user onboarding flow
- `GET /api/onboarding/status` - Check onboarding status

**Flow:**
1. Validate JWT token
2. Extract organization from Auth0
3. Create DGraph namespace
4. Provision user on blockchain
5. Sync metadata to Auth0
6. Return onboarding status

#### MemberProvision (`server/api/blueprints/member_provision.py`)
- `POST /api/members/provision` - Provision member to blockchain

#### NamespaceProvision (`server/api/blueprints/namespace_provision.py`)
- `POST /api/namespaces/provision` - Create new namespace

#### AuthSync (`server/api/blueprints/auth_sync.py`)
- `POST /api/auth/sync` - Synchronize Auth0 data

#### DomainManagement (`server/api/blueprints/domain_management.py`)
- `GET /api/domains` - List whitelisted domains
- `POST /api/domains` - Add domain to whitelist
- `DELETE /api/domains/:id` - Remove domain

#### InvitationManagement (`server/api/blueprints/invitation_management.py`)
- `POST /api/invitations` - Create user invitation
- `GET /api/invitations/:id` - Get invitation status

#### AdminAuthManagement (`server/api/blueprints/admin_auth_management.py`)
- Various `/api/admin/auth/*` endpoints for administration

### Core Processing Components

#### DynamicPersistor (`server/api/core/dynamic_persistor.py` - 69KB)

**Purpose:** Universal data persistence for any schema type

**Key Method:** `detect_model_type(data: Dict) -> Tuple[Type[BaseModel], str]`

**Detection Flow:**
1. Check for explicit `model_type` or `type` field
2. Use `PydanticModelIntrospector` to analyze payload structure
3. Match payload keys against all available Pydantic models
4. Return best deterministic match based on field overlap

**Write Flow:**
```python
def persist(payload: Dict) -> str:
    # 1. Detect model type
    model_class, model_name = detect_model_type(payload)

    # 2. Validate with Pydantic
    validated_data = model_class(**payload)

    # 3. Generate unique ID
    doc_id = HavonaIDGenerator.generate(model_name)

    # 4. Encode to CBOR
    cbor_data = encode_json_to_cbor(validated_data.model_dump())

    # 5. Generate storage key
    storage_key = make_storage_key(doc_id)

    # 6. Submit to blockchain
    tx_hash = contract.setBlob(storage_key, cbor_data)

    # 7. Store in DGraph
    graphql_client.mutate(validated_data)

    # 8. Return transaction receipt
    return {"id": doc_id, "tx_hash": tx_hash}
```

#### SimplifiedProcessor (`server/api/core/simplified_processor.py` - 15KB)
- Streamlined request processing pipeline
- Error handling and retry logic

#### GraphQLPool (`server/api/core/graphql_pool.py`)
- Connection pooling for GraphQL clients
- Automatic reconnection on failure

### Request Lifecycle

```
1. Request → Flask app
2. CORS middleware → Add CORS headers
3. Auth middleware → Validate JWT (if enabled)
4. Namespace middleware → Extract organization → Route to namespace
5. Blueprint handler → Process request
6. Service layer → Business logic
7. DynamicPersistor → Data operations
8. Response → Client
```

### Validation Layer

**Library:** Pydantic 2.11.2

**Location:** `server/api/validation/`

**Validators:**
- Request/response schema validation
- GraphQL mutation validation
- Input sanitization
- Type checking

### Error Handling & Monitoring

- **Logging:** structlog 24.4.0 with JSON formatting
- **Metrics:** Prometheus client integration
- **Retry Logic:** tenacity 9.0.0 for resilient operations
- **Health Endpoint:** `GET /health`

### Key API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Service health check |
| `/graphql` | POST | DGraph GraphQL proxy |
| `/api/persist` | POST | Dynamic data persistence |
| `/api/onboard` | POST | User onboarding |
| `/api/admin/*` | Various | Admin operations |

---

## Frontend Architecture

### Technology Stack

- **Framework:** React 18.2.0
- **Build Tool:** Vite 4.4.0
- **Language:** TypeScript 5.0.2
- **Styling:** Emotion 11.11.1 (CSS-in-JS)

### Directory Structure

```
ui/src/
├── main.tsx                # Entry point
├── pages/                  # 28 page components
├── components/             # 11 reusable UI components
├── hooks/                  # 12 custom React hooks
├── services/               # API integration layer
├── store/                  # Zustand state management
├── context/                # 7 React context providers
├── utils/                  # 17 utility modules
├── types/                  # TypeScript type definitions
└── providers/              # Context and provider setup
```

### State Management

**Global State:** Zustand 5.0.4
- Simple, performant state management
- No boilerplate like Redux
- TypeScript-first design

**Server State:** TanStack Query 5.65.1
- Declarative data fetching
- Automatic caching and background updates
- Optimistic updates

**Immutable Updates:** Immer 10.1.1
- Simplified immutable state updates
- Works seamlessly with Zustand

### Data Fetching

**REST API:** TanStack Query for server state management
**GraphQL:** Apollo Client 3.7.17 for DGraph queries
**Data Tables:** TanStack Table 8.9.3 for complex table UI

### Web3 Integration

**Stack:**
- **wagmi 2.14.9** - React hooks for Ethereum
- **RainbowKit 2.2.3** - Wallet connection UI
- **viem 2.22.16** - Low-level Ethereum client

**Wallet Connection Flow:**
```
1. User clicks "Connect Wallet"
2. RainbowKit modal appears with wallet options
3. User selects wallet (MetaMask, WalletConnect, etc.)
4. wagmi handles connection and provides hooks
5. viem manages low-level Ethereum interactions
6. Contract interactions signed by user's wallet
```

### Authentication Flow

**Library:** @auth0/auth0-react 2.3.0

**Flow:**
```
1. User clicks "Login"
2. Redirected to Auth0 hosted login page
3. User authenticates (email/password, social, SSO)
4. Redirected back with authorization code
5. Auth0Provider exchanges code for tokens
6. Access token stored in memory
7. Token automatically included in API requests
```

### UI Component Libraries

- **Ant Design 5.7.0** - Comprehensive React component library
- **Framer Motion 11.3.24** - Animation library
- **Chart.js 4.4.9** - Data visualization
- **Mapbox GL 3.12.0** - Geographic visualization

### Build Modes

| Command | Environment | Details |
|---------|-------------|---------|
| `npm run start` | Development | Vite dev server with HMR on port 3000 |
| `npm run uat` | UAT | Optimized build for UAT environment |
| `npm run prod` | Production | Optimized build with minification |
| `npm run build` | Production | Alias for `npm run prod` |

### Code Quality Tools

- **Linting:** ESLint with TypeScript support
- **Formatting:** Prettier 3.0.1
- **Testing:** Jest 30.0.3, Puppeteer for E2E
- **Type Generation:** GraphQL Codegen from schema

---

## Authentication System

### Architecture Overview

**Provider:** Auth0
**Pattern:** Organization-based multi-tenancy
**Protocol:** OAuth 2.0 / OpenID Connect

### Components

#### AuthService (`server/api/services/auth.py`)

**Initialization:**
1. Initialize Auth0 Management Client
2. Check `AUTH_DISABLED` environment variable
3. Load Auth0 configuration for environment
4. Setup JWT validation middleware

**Features:**
- Can be disabled for local development
- Management API always available for admin operations

#### Auth Middleware

**Location:** `server/auth/`

**Responsibilities:**
- JWT signature verification (RS256)
- Token expiration validation
- Audience and issuer validation
- User claims extraction
- Organization context extraction

#### Auth0 Management Client

**Location:** `server/auth/auth0_management.py`

**Capabilities:**
- Create and update users
- Manage organization memberships
- Assign roles and permissions
- Sync domain whitelist
- Manage invitations

### Access Control Model

**Admin Domain:** `@havona.io`
- Users with this domain have special admin access

**Domain Validation:**
- Only pre-onboarded domains can access the system

**Pre-Invitation Requirement:**
- Users must be invited before they can login

**Namespace Isolation:**
- Each organization has a separate DGraph namespace
- Data is completely isolated between organizations

### Auth0 Configuration by Environment

**Local Development:**
- **Domain:** havona-dev.us.auth0.com
- **Audience:** https://api.havona.com
- **Tenant:** havona-dev

**UAT:**
- **Tenant:** UAT-specific tenant
- **Config:** Loaded from `server/.env.uat`

**Production:**
- **Tenant:** Production tenant
- **Config:** Loaded from `server/.env.prod`

### User Onboarding Flow

**Implementation:** `server/api/blueprints/simple_onboarding.py` (81KB)

**Complete Flow:**
```
1. Admin creates invitation in system
2. Invitation email sent to user
3. User clicks link → Auth0 sign-up page
4. User completes sign-up
5. User logs in for first time
6. Frontend detects first login
7. Frontend calls POST /api/onboard
8. Backend creates DGraph namespace for organization
9. Backend provisions user on blockchain (HavonaMemberManager)
10. Backend syncs metadata to Auth0
11. Backend returns onboarding status
12. User gains full access to system
```

### Security Features

- **JWT RS256 Signature Verification** - Cryptographically secure
- **Token Expiration Enforcement** - Short-lived tokens
- **Organization-Based Access Control** - Multi-tenant isolation
- **Domain Whitelist Validation** - Only approved domains
- **Pre-Invitation Requirement** - No open registration
- **Namespace Isolation** - Complete data separation

### Testing Without Auth

**Environment Variable:**
```bash
AUTH_DISABLED=true
```

**Documentation:**
- `docs/AUTH_TESTING_GUIDE.md` - Authentication testing procedures
- `docs/UAT_MANUAL_TESTING_GUIDE.md` - Complete UAT guide (30KB)

---

## Pydantic Usage & Data Validation

### Overview

**Version:** Pydantic 2.11.2
**Purpose:** Type validation, serialization, schema enforcement

### Schema-First Code Generation

**Source:** `schema/master.graphql` (6,116 lines)
**Generator:** `model/generators/generate_all.py`

**Generation Flow:**
```
1. Update schema/master.graphql
2. Run: python3 model/generators/generate_all.py
3. Generated outputs:
   - server/model/models.py (Python Pydantic models)
   - ui/src/types/ (TypeScript interfaces)
4. Import models in server code
5. Use for validation and serialization
```

### Generated Models

**Location:** `server/model/models.py`
**Generated:** 2025-10-20 23:20:01

**Structure:**
```python
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

# Enums
class BlockchainSyncStatus(str, Enum):
    NOT_SYNCED = "NOT_SYNCED"
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    FAILED = "FAILED"

# Models
class TradeContract(BaseModel):
    id: str
    contractNo: Optional[str] = None
    contractDate: Optional[str] = None
    status: Optional[BlockchainSyncStatus] = None
    seller: Optional['Member'] = None
    buyer: Optional['Member'] = None
    # ... more fields
```

**Features:**
- Automatic field validation
- Type coercion where appropriate
- Optional vs required fields
- Forward references for circular dependencies
- Nested model support

### Usage Patterns

#### 1. Request Validation

**Location:** `server/api/validation/`

**Pattern:**
```python
@app.route('/api/persist', methods=['POST'])
def persist_data():
    payload = request.json

    # Detect type
    model_class, model_name = detect_model_type(payload)

    # Validate
    try:
        validated_data = model_class(**payload)
    except ValidationError as e:
        return {"error": str(e)}, 400

    # Process validated data
    result = persist(validated_data)
    return result
```

#### 2. Dynamic Type Detection

**Location:** `server/api/core/dynamic_persistor.py`
**Method:** `detect_model_type(data: Dict)`

**Flow:**
```
1. Check for explicit 'model_type' or 'type' field
2. Use PydanticModelIntrospector to analyze payload structure
3. Match payload keys against all Pydantic model fields
4. Calculate field overlap score for each model
5. Return model with highest overlap (deterministic match)
```

**Example:**
```python
payload = {
    "contractNo": "TC-001",
    "contractDate": "2025-10-26",
    "seller": {...},
    "buyer": {...}
}

# Automatically detects as TradeContract
model_class, model_name = detect_model_type(payload)
# Returns: (TradeContract, "TradeContract")
```

#### 3. Response Serialization

**Pattern:**
```python
trade_contract = TradeContract(**data)

# Serialize to JSON
json_data = trade_contract.model_dump()

# Serialize excluding None values
json_data = trade_contract.model_dump(exclude_none=True)

# Return to client
return jsonify(json_data)
```

#### 4. GraphQL Integration

Pydantic models mirror GraphQL schema types:
```
GraphQL Schema → Pydantic Models → Validation → DGraph Storage
```

This ensures data sent to DGraph always matches the schema.

### Model Categories

**Trade Documents:**
- `TradeContract`
- `DigitalTradeTransaction`
- `TransportDocumentEBL`
- `ElectronicRecord`

**Risk Management:**
- `RiskProfile`
- `RiskExposure`
- `HedgingStrategy`
- `MarketRiskAnalysis`

**Commodities:**
- `CommodityReference`
- `CommodityPrice`
- `ProductGoods`

**Parties:**
- `Member`
- `PrincipleParties`
- `PrinciplePaymentParties`

**Blockchain:**
- `DLTTransaction`
- `PostTradeDocumentSeal`
- `Signature`

**Field Tracking:**
- `FieldStatus`
- `FieldHistory`

### Advanced Features

**Field Validators:**
```python
class TradeContract(BaseModel):
    contractNo: str

    @validator('contractNo')
    def validate_contract_no(cls, v):
        if not v.startswith('TC-'):
            raise ValueError('Contract number must start with TC-')
        return v
```

**Field Constraints:**
```python
class Member(BaseModel):
    name: str = Field(..., max_length=200)
    email: str = Field(..., regex=r'^[\w\.-]+@[\w\.-]+\.\w+$')
```

**Nested Models:**
```python
class TradeContract(BaseModel):
    seller: Optional[Member] = None
    buyer: Optional[Member] = None
    productGoods: Optional[ProductGoods] = None
```

### Integration with AI/ML

**Pydantic AI:** `pydantic-ai 0.0.16`
- Structured LLM outputs with Pydantic validation
- Used in `server/agents/` for AI agent responses

**RAG Applications:**
- Validate extracted entities from documents
- Ensure AI-extracted data matches schema

### Validation Benefits

1. **Catch Errors Early** - Before database or blockchain operations
2. **Prevent Invalid Data** - On blockchain (immutable)
3. **API Contract Compliance** - Consistent interface
4. **Automatic Documentation** - JSON schemas generated from models
5. **IDE Support** - Autocomplete and type hints in VS Code/PyCharm

---

## GraphQL & DGraph Integration

### Overview

**DGraph Version:** v25.0.0
**Feature:** Native GraphQL API with multi-tenant namespace isolation

### Architecture

#### DGraph Cluster

**Zero (Coordinator):**
- **Ports:** 5080 (gRPC), 6080 (HTTP)
- **Purpose:** Cluster coordination, shard management, global state

**Alpha (Database Node):**
- **Ports:** 8080 (GraphQL), 9080 (gRPC)
- **Features:**
  - Native GraphQL API endpoint
  - ACL (Access Control Lists)
  - Namespace isolation (v25 feature)
  - Schema management per namespace

**Namespace Service:**
- **Language:** Go microservice
- **Port:** 5001
- **Location:** `server/services/namespace/`
- **Purpose:** Manage DGraph v25 namespaces via gRPC

### GraphQL Schema Management

#### Master Schema

**Location:** `schema/master.graphql`
**Size:** 6,116 lines
**Types:** 150+ GraphQL types

**Custom Directives:**
```graphql
directive @id on FIELD_DEFINITION
directive @search on FIELD_DEFINITION
directive @length(max: Int) on FIELD_DEFINITION
directive @ledger on FIELD_DEFINITION    # Sync to blockchain
directive @offledger on FIELD_DEFINITION # Exclude from blockchain
```

**Example Type:**
```graphql
type TradeContract {
    id: String @id
    contractNo: String
    contractDate: String
    status: DigitalTradeTransactionStatus @search
    seller: Member
    buyer: Member
    productGoods: ProductGoods
    fieldHistories: [FieldHistory]
    # ... more fields
}
```

#### Schema Deployment

**Local:**
```bash
cd agents/extras
make ENV=local schema-gql
```

**Programmatic:**
```python
# server/dgraph/dgraph_update_schema.py
from dgraph_manager import update_schema

schema = load_schema('schema/master.graphql')
update_schema(schema)
```

**Validation:**
```python
# server/dgraph/utils/graphql_validator.py
validate_schema(schema_string)
```

#### Field History Schema

**Location:** `schema/field_history.graphql`
**Purpose:** Comprehensive change tracking

**Integration:** Automatically merged with master schema

### GraphQL Client Integration

#### Python Client

**Library:** gql 3.5.0, pydgraph 24.0.2

**Implementation:**
```python
# server/graph/graphql.py
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

class GraphQLClient:
    def __init__(self, url: str):
        transport = RequestsHTTPTransport(url=url)
        self.client = Client(transport=transport)

    def query(self, query_string: str):
        query = gql(query_string)
        return self.client.execute(query)
```

**Connection Pooling:**
```python
# server/api/core/graphql_pool.py
class GraphQLPool:
    def __init__(self, size=10):
        self.pool = [GraphQLClient(url) for _ in range(size)]

    def get_client(self):
        # Return available client from pool
        pass
```

#### JavaScript Client

**Library:** @apollo/client 3.7.17

**Setup:**
```typescript
import { ApolloClient, InMemoryCache } from '@apollo/client';

const client = new ApolloClient({
  uri: 'http://localhost:8080/graphql',
  cache: new InMemoryCache(),
});
```

### GraphQL Operations

#### Queries

**Example:**
```graphql
query GetTradeContract($id: String!) {
  getTradeContract(id: $id) {
    id
    contractNo
    contractDate
    status
    seller {
      id
      name
      email
    }
    buyer {
      id
      name
      email
    }
    productGoods {
      name
      quantity
      price {
        amount
        currency
      }
    }
  }
}
```

**With Filters:**
```graphql
query FilterTradeContracts {
  queryTradeContract(filter: {
    status: { eq: CONFIRMED }
  }) {
    id
    contractNo
    status
  }
}
```

#### Mutations

**Add Data:**
```graphql
mutation AddTradeContract($input: AddTradeContractInput!) {
  addTradeContract(input: [$input]) {
    tradeContract {
      id
      contractNo
    }
  }
}
```

**Update Data:**
```graphql
mutation UpdateTradeContract($id: String!, $patch: TradeContractPatch!) {
  updateTradeContract(input: {
    filter: { id: { eq: $id } }
    set: $patch
  }) {
    tradeContract {
      id
      contractNo
    }
  }
}
```

**Mutation Validation:**
```python
# server/dgraph/utils/mutation_validator.py
def validate_mutation(mutation: str, schema: str):
    # Ensure mutation matches schema
    pass
```

### Multi-Tenancy with Namespaces

#### Namespace Strategy

**Isolation Level:** Complete data isolation per organization
**Namespace Naming:** `org_{auth0_org_id}`

#### Namespace Middleware

**Location:** `server/dgraph/namespaces/namespace_middleware.py`

**Flow:**
```python
@app.before_request
def namespace_middleware():
    # 1. Extract JWT from Authorization header
    token = request.headers.get('Authorization')

    # 2. Decode JWT
    claims = jwt.decode(token)

    # 3. Extract organization ID
    org_id = claims.get('org_id')

    # 4. Set namespace context
    g.namespace = f"org_{org_id}"

    # 5. Get namespace-specific GraphQL client
    g.graphql_client = get_namespace_client(g.namespace)
```

#### Namespace Manager

**Location:** `server/dgraph/namespaces/namespace_manager.py`

**Functions:**
```python
def create_namespace(org_id: str):
    """Create new DGraph namespace for organization"""
    namespace = f"org_{org_id}"
    # Call Go namespace service
    requests.post('http://namespace-service:5001/namespaces',
                  json={'namespace': namespace})

def get_namespace_client(org_id: str) -> GraphQLClient:
    """Get GraphQL client for specific namespace"""
    namespace = f"org_{org_id}"
    return GraphQLClient(f"http://dgraph-alpha:8080/graphql?namespace={namespace}")

def delete_namespace(org_id: str):
    """Delete namespace (admin only)"""
    namespace = f"org_{org_id}"
    requests.delete(f'http://namespace-service:5001/namespaces/{namespace}')
```

### Data Flow

#### Write Path
```
1. API receives JSON payload
2. Validate with Pydantic model
3. Extract namespace from JWT (g.namespace)
4. Build GraphQL mutation
5. Submit to DGraph alpha with namespace parameter
6. DGraph stores in isolated namespace
7. Asynchronously sync to blockchain (if @ledger directive)
8. Return DGraph ID to client
```

#### Read Path
```
1. API receives query request
2. Extract namespace from JWT
3. Build GraphQL query
4. Query DGraph alpha with namespace parameter
5. DGraph returns data only from that namespace
6. Return results to client
7. Optionally verify with blockchain
```

### Schema Introspection

**Handler:** `server/graph/graph_introspection_handler.py`

**Use Cases:**
- Generate UI forms dynamically from schema
- Validate payloads without hardcoded models
- Build query builders

**Example:**
```python
def get_type_fields(type_name: str):
    introspection_query = """
    query IntrospectType($name: String!) {
      __type(name: $name) {
        fields {
          name
          type {
            name
            kind
          }
        }
      }
    }
    """
    return graphql_client.query(introspection_query, {"name": type_name})
```

### ACL Security

**ACL Secret:** `DGRAPH_ACL_SECRET` environment variable
**Storage:** `/data/acl-secret.txt` inside Alpha container
**Groot User:** DGraph super admin with password from environment

**Namespace ACL:**
- Each namespace has separate ACL rules
- Users can only access their organization's namespace

### Performance Optimizations

**Connection Pooling:**
- Reuse GraphQL clients across requests
- Pool size configurable (default: 10)

**Batching:**
- Batch mutations for bulk operations
- Reduces round trips to database

**Indexing:**
- `@search` directive creates indices
- Fast filtering on indexed fields

**Caching:**
- Redis cache for frequently accessed data
- GraphQL response caching

### Testing

**Unit Tests:** `server/dgraph/namespaces/test/`
**Isolation Tests:** Verify namespace data isolation
**Integration Tests:** End-to-end GraphQL operations

---

## Development Environment

### Port Allocation

| Port | Service | Purpose |
|------|---------|---------|
| 3000 | React UI | Development mode with HMR |
| 5000 | Flask API | Python backend server |
| 5001 | Namespace Service | Go microservice (conflicts with inference) |
| 5080 | DGraph Zero | gRPC endpoint |
| 6080 | DGraph Zero | HTTP endpoint |
| 6379 | Redis | Caching and sessions |
| 8080 | DGraph Alpha | GraphQL endpoint |
| 8545 | Blockchain | Anvil local node |
| 9080 | DGraph Alpha | gRPC endpoint |

### Quick Start

**Automated Setup:**
```bash
./scripts/setup_local_env.sh
```

**Manual Setup:**
```bash
# 1. Start DGraph
cd infra/dgraph && ./dgraph_up.sh

# 2. Generate Pydantic models
python3 model/generators/generate_all.py

# 3. Start Anvil blockchain
cd contracts && anvil --host 0.0.0.0 --port 8545

# 4. Deploy contracts (in new terminal)
cd contracts && forge script script/Deploy.s.sol --broadcast --rpc-url http://localhost:8545

# 5. Update .env.local with deployed contract address

# 6. Start server
python3 server/api/havona.py

# 7. Start UI (in new terminal)
cd ui && npm run start
```

**Docker Compose:**
```bash
# Start all services
docker compose up

# With seeding
docker compose --profile seed up

# Clean restart
docker compose down -v && docker compose up
```

### Environment Configuration Files

**.env.local** - Local development
```bash
ENVIRONMENT=LOCAL
CHAIN_RPC_URL=http://localhost:8545
GRAPHQL_URL=http://localhost:8080/graphql
REDIS_URL=redis://localhost:6379
AUTH_DISABLED=true
```

**.env.ten** - UAT/Ten testnet
```bash
ENVIRONMENT=UAT
CHAIN_RPC_URL=https://testnet.ten.xyz
CONTRACT_ADDRESS=0xD8010Dbf1254D9cfE81e1b508ebCf78006fBaa79
GRAPHQL_URL=https://hypermode.host/dgraph/graphql
```

**.env.prod** - Production
```bash
ENVIRONMENT=PRODUCTION
# Production-specific configuration
```

### Master Startup Script

**Location:** `tools/start-havona.sh`

**Usage:**
```bash
./start-havona.sh --local --clean
./start-havona.sh --uat
./start-havona.sh --prod
```

**Features:**
- Environment detection
- Dependency validation
- Service health checks
- Clean startup option

---

## Deployment Environments

### Local Development

**Blockchain:** Anvil (localhost:8545)
**DGraph:** localhost:8080
**Deployment:** Docker Compose
**Purpose:** Development and testing

### UAT (User Acceptance Testing)

**Blockchain:** Ten Testnet
**Contract:** 0xD8010Dbf1254D9cfE81e1b508ebCf78006fBaa79
**DGraph:** hypermode.host/dgraph/graphql
**Deployment:** Google Cloud Run
**URL:** uat.app.post-trade.com

### Production

**Blockchain:** TEN Network
**Deployment:** Google Cloud Run
**URL:** app.post-trade.com
**CI/CD:** GitHub Actions + Google Cloud Build

---

## CI/CD Pipeline

### GitHub Actions

**Workflow:** `.github/workflows/build.yml`

**Triggers:**
- Push to any branch
- Pull requests

**Steps:**
1. Checkout code
2. Setup Node.js 18 and Python 3.11
3. Install dependencies
4. Run linters (ESLint, Flake8, Black)
5. Run tests (Jest, Pytest)
6. Build Docker images
7. Push to Google Container Registry (if main/uat branch)

### Google Cloud Build

**Config:** `cloudbuild.yaml`

**Machine Specs:**
- Type: E2_HIGHCPU_8
- Disk: 50GB
- Timeout: 1200s (20 minutes)

**Steps:**
1. Install dependencies (npm, pip)
2. Lint code (ESLint, Flake8)
3. Build Docker images
4. Push to Container Registry
5. Deploy to Cloud Run
6. Run health checks

**Environment Substitutions:**
- Branch-based configuration
- Separate deployments for CI, UAT, PROD

### Deployment Scripts

**Production:**
```bash
./infra/cloudrun/deploy-prod.sh
```

**UAT:**
```bash
./infra/cloudrun/deploy-uat.sh
```

**CI (Feature Branches):**
```bash
./infra/cloudrun/deploy-ci.sh
```

**Complete Deployment:**
```bash
./infra/cloudrun/deploy_complete.sh
```

---

## Key Dependencies

### Python Backend

| Package | Version | Purpose |
|---------|---------|---------|
| flask | 3.0.3 | Web framework |
| web3 | 7.5.0 | Blockchain integration |
| pydantic | 2.11.2 | Data validation |
| pydgraph | 24.0.2 | DGraph database client |
| gql | 3.5.0 | GraphQL client |
| cbor2 | 5.6.5 | CBOR encoding |
| redis | 5.2.0 | Caching |
| pyjwt | 2.10.1 | JWT authentication |
| authlib | 1.3.1 | OAuth integration |
| google-generativeai | 0.8.5 | AI integration |
| litellm | 1.55.4 | LLM abstraction |
| fastembed | 0.4.2 | Embeddings |
| tenacity | 9.0.0 | Retry logic |
| structlog | 24.4.0 | Structured logging |

### JavaScript Frontend

| Package | Version | Purpose |
|---------|---------|---------|
| react | 18.2.0 | UI framework |
| vite | 4.4.0 | Build tool |
| typescript | 5.0.2 | Type safety |
| @emotion/react | 11.11.1 | CSS-in-JS |
| zustand | 5.0.4 | State management |
| @tanstack/react-query | 5.65.1 | Server state |
| wagmi | 2.14.9 | Ethereum hooks |
| @rainbow-me/rainbowkit | 2.2.3 | Wallet connection |
| viem | 2.22.16 | Ethereum client |
| @auth0/auth0-react | 2.3.0 | Authentication |
| @apollo/client | 3.7.17 | GraphQL client |
| antd | 5.7.0 | UI components |
| framer-motion | 11.3.24 | Animations |

---

## Testing

### Backend Testing

**Framework:** pytest 8.3.4
**Async Support:** pytest-asyncio 0.24.0

**Test Locations:**
- `server/tests/unit/` - Unit tests
- `server/tests/integration/` - Integration tests
- `server/tests/e2e/` - End-to-end tests
- `server/tests/blockchain/` - Blockchain-specific tests

### Frontend Testing

**Framework:** Jest 30.0.3
**E2E:** Puppeteer for browser automation

### Smart Contract Testing

**Framework:** Foundry test suite
**Tests:** `contracts/test/*.t.sol`

**Run Tests:**
```bash
cd contracts
forge test
forge test --gas-report
forge test -vvv  # Verbose output
```

---

## Documentation

### Key Documentation Files

| File | Size | Purpose |
|------|------|---------|
| CLAUDE.md | - | Project guidance for AI assistants |
| docs/SYSTEM_OVERVIEW.md | - | Complete system architecture |
| docs/AUTH_OPS.md | 63KB | Auth0 operations guide |
| docs/AUTH_TESTING_GUIDE.md | - | Authentication testing |
| docs/UAT_MANUAL_TESTING_GUIDE.md | 30KB | Complete UAT procedures |
| docs/START_HERE.md | - | Getting started guide |
| docs/DEPLOY_TEN.md | - | Ten network deployment |

---

## Must-Follow Development Rules

### Smart Contracts
- ❌ **Never deploy new contract if one exists**
- ✅ Always verify contract address in `.env` files

### Schema Operations
- ❌ **Never iterate through full schema**
- ✅ Always operate arbitrarily on specific types

### Python Code
- ❌ **Never use `async` keyword** - too error prone
- ✅ Use threads or Redis for concurrency

### Code Quality
- ❌ Don't leave AI-generated comments
- ✅ Only short, meaningful descriptions
- ✅ Clean up temporary files
- ✅ Place files logically based on architecture

---

## Code Statistics

| Metric | Value |
|--------|-------|
| Total Files | 1,000+ |
| Total Lines | 50,000+ |
| GraphQL Schema | 6,116 lines |
| Python Files | 342 files |
| TypeScript Files | 237 files |
| Solidity Contracts | 392 files |
| Largest Python Module | dynamic_persistor.py (69KB) |
| Largest Blueprint | simple_onboarding.py (81KB) |

---

## Summary for AI Analysis

Havona is a **production-grade trade contract management platform** with:

1. **Dual Persistence** - DGraph for speed, blockchain for immutability
2. **Schema-First** - GraphQL schema drives code generation
3. **Multi-Tenant** - Complete namespace isolation
4. **Crypto Integration** - EIP-712 signed CBOR-encoded blockchain storage
5. **Modern Stack** - React/TypeScript frontend, Flask/Python backend
6. **Docker-Orchestrated** - Multi-environment compose configurations
7. **Auth0 Authentication** - Organization-based access control
8. **Pydantic Validation** - Type-safe data processing
9. **GraphQL + DGraph** - Native GraphQL database with namespaces
10. **Production-Ready** - CI/CD, monitoring, comprehensive testing

The system handles international trade contracts with blockchain-verified audit trails, comprehensive risk management, and regulatory compliance through field history tracking.
