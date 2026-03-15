# Eliza Patterns to Adopt in Agno

## Executive Summary

Analysis of `/examples/eliza/` reveals several architectural patterns that would enhance Agno for crypto use cases. This document outlines patterns to adopt while maintaining Agno's simpler execution model.

---

## 1. Keep Agno For

### Strengths to Preserve
- **Simpler execution model** - Fewer component types to understand
- **Native Python integration** - Direct compatibility with data pipelines
- **Team/multi-agent coordination** - Built-in from start
- **DBOS compatibility** - DBOSAgent wrapper for durability
- **Tool composition** - Flexible action chaining

### Current Agno Pattern (from github_repo_analyzer)
```python
agent = Agent(
    name="GitHub Repository Analyzer",
    model=get_model_from_id(model_id),
    tools=[GithubTools()],
    instructions="...",
    add_history_to_context=True,
)
```

---

## 2. Patterns to Adopt from Eliza

### Pattern 1: Character System

**Eliza Implementation:**
```typescript
// Character defines agent personality
interface Character {
  name: string;
  username: string;
  system: string;  // System prompt
  templates: Record<string, string>;  // Context templates
  bio: string[];
  messageExamples: MessageExample[];
  topics: string[];
  adjectives: string[];
  knowledge: string[];
  settings: CharacterSettings;
}
```

**Agno Adaptation:**
```python
from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class CryptoCharacter:
    """Personality configuration for crypto agents."""
    name: str
    role: str  # "analyst", "trader", "researcher"
    bio: List[str]
    expertise: List[str]  # ["DeFi", "Tokenomics", "Smart Contracts"]
    communication_style: str  # "formal", "casual", "technical"
    risk_tolerance: str  # "conservative", "moderate", "aggressive"
    templates: Dict[str, str]  # Context-specific prompts

    def to_instructions(self) -> str:
        """Convert character to agent instructions."""
        return f"""
You are {self.name}, a {self.role}.

Background:
{chr(10).join(f'- {b}' for b in self.bio)}

Expertise: {', '.join(self.expertise)}
Communication style: {self.communication_style}
Risk tolerance: {self.risk_tolerance}
"""

# Usage
defi_analyst = CryptoCharacter(
    name="DeFi Analyst",
    role="DeFi protocol analyst",
    bio=["Expert in yield optimization", "5 years in crypto"],
    expertise=["Aave", "Pendle", "Ethena", "Curve"],
    communication_style="technical",
    risk_tolerance="moderate",
    templates={
        "analysis": "Analyze {protocol} focusing on...",
        "risk_assessment": "Assess risks for {position}...",
    }
)

agent = Agent(
    name=defi_analyst.name,
    instructions=defi_analyst.to_instructions(),
    tools=[DeFiTools()],
)
```

**Value for Crypto:**
- Consistent agent personas across sessions
- Role-specific behavior (analyst vs trader)
- Risk tolerance encoded in character

---

### Pattern 2: Provider Pattern (Read-Only Context)

**Eliza Implementation:**
```typescript
// Providers supply read-only context to agents
interface Provider {
  name: string;
  get(runtime: IAgentRuntime, message: Memory, state: State): Promise<ProviderResult>;
}

// Example providers from bootstrap plugin
const providers = [
  timeProvider,        // Current timestamp
  entitiesProvider,    // Entity graph
  factsProvider,       // Knowledge base
  settingsProvider,    // Configuration
  portfolioProvider,   // (custom) Current holdings
];
```

**Agno Adaptation:**
```python
from abc import ABC, abstractmethod
from typing import Any, Dict

class Provider(ABC):
    """Read-only context provider for agents."""

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    async def get(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Return context data (read-only)."""
        pass

class PortfolioProvider(Provider):
    """Provides current portfolio state."""

    name = "portfolio"

    def __init__(self, ledger_client):
        self.ledger = ledger_client

    async def get(self, context: Dict[str, Any]) -> Dict[str, Any]:
        user_id = context.get("user_id")
        portfolio = await self.ledger.get_portfolio(user_id)
        return {
            "total_value_usd": portfolio.total_value,
            "positions": [
                {"symbol": p.symbol, "amount": p.amount, "value_usd": p.value}
                for p in portfolio.positions
            ],
            "cash_available": portfolio.cash,
        }

class MarketDataProvider(Provider):
    """Provides current market context."""

    name = "market"

    async def get(self, context: Dict[str, Any]) -> Dict[str, Any]:
        symbols = context.get("watched_symbols", ["BTC", "ETH"])
        return {
            "fear_greed_index": await self.get_fear_greed(),
            "prices": await self.get_prices(symbols),
            "trending": await self.get_trending_tokens(),
        }

# Agent with providers
class ProviderAwareAgent:
    """Agno agent enhanced with Eliza-style providers."""

    def __init__(self, agent: Agent, providers: List[Provider]):
        self.agent = agent
        self.providers = providers

    async def run(self, message: str, context: Dict[str, Any] = None):
        context = context or {}

        # Gather provider context
        provider_context = {}
        for provider in self.providers:
            provider_context[provider.name] = await provider.get(context)

        # Inject into agent instructions
        enhanced_instructions = f"""
{self.agent.instructions}

Current Context:
{self._format_context(provider_context)}
"""
        # Run with enhanced context
        return await self.agent.run(message, instructions=enhanced_instructions)
```

**Value for Crypto:**
- Separate data fetching from agent logic
- Reusable context across agents
- Clean testing (mock providers)

---

### Pattern 3: Evaluator Pattern (Post-Interaction Learning)

**Eliza Implementation:**
```typescript
// Evaluators run after agent responses
interface Evaluator {
  name: string;
  validate(runtime: IAgentRuntime, message: Memory): Promise<boolean>;
  handler(runtime: IAgentRuntime, message: Memory): Promise<void>;
}

// Example: reflectionEvaluator learns from interactions
```

**Agno Adaptation:**
```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

@dataclass
class AgentResponse:
    content: str
    tool_calls: List[Dict]
    metadata: Dict[str, Any]

class Evaluator(ABC):
    """Post-interaction evaluator for agent learning."""

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    async def should_evaluate(self, response: AgentResponse) -> bool:
        """Determine if this response should be evaluated."""
        pass

    @abstractmethod
    async def evaluate(self, response: AgentResponse, context: Dict) -> Dict:
        """Evaluate the response and return insights."""
        pass

class TradeEvaluator(Evaluator):
    """Evaluates trading decisions after execution."""

    name = "trade_evaluator"

    async def should_evaluate(self, response: AgentResponse) -> bool:
        # Evaluate if agent made a trade
        return any(tc["name"] == "execute_trade" for tc in response.tool_calls)

    async def evaluate(self, response: AgentResponse, context: Dict) -> Dict:
        trade = next(tc for tc in response.tool_calls if tc["name"] == "execute_trade")

        # Analyze trade quality
        return {
            "trade_symbol": trade["args"]["symbol"],
            "entry_price": trade["args"]["price"],
            "market_conditions": context.get("market", {}),
            "risk_score": self._calculate_risk(trade, context),
            "decision_quality": await self._llm_evaluate_decision(trade, context),
        }

    async def _llm_evaluate_decision(self, trade: Dict, context: Dict) -> str:
        """Use LLM to evaluate decision quality."""
        # Similar to Temporal's Judge Agent pattern
        pass

class ComplianceEvaluator(Evaluator):
    """Checks responses for compliance issues."""

    name = "compliance"

    async def should_evaluate(self, response: AgentResponse) -> bool:
        return True  # Always check

    async def evaluate(self, response: AgentResponse, context: Dict) -> Dict:
        return {
            "contains_financial_advice": self._check_advice(response.content),
            "mentions_specific_returns": self._check_returns(response.content),
            "risk_disclaimers_present": self._check_disclaimers(response.content),
        }

# Integration with agent
class EvaluatedAgent:
    """Agent with post-response evaluation."""

    def __init__(self, agent: Agent, evaluators: List[Evaluator]):
        self.agent = agent
        self.evaluators = evaluators

    async def run(self, message: str) -> AgentResponse:
        response = await self.agent.run(message)

        # Run evaluators
        evaluations = {}
        for evaluator in self.evaluators:
            if await evaluator.should_evaluate(response):
                evaluations[evaluator.name] = await evaluator.evaluate(response, {})

        # Store evaluations for learning
        await self._store_evaluations(response, evaluations)

        return response
```

**Value for Crypto:**
- Post-trade analysis for improvement
- Compliance checking
- Risk assessment logging
- Audit trail for regulatory requirements

---

### Pattern 4: Service Type Registry

**Eliza Implementation:**
```typescript
// Typed service registry
enum ServiceType {
  WALLET = 'wallet',
  LP_POOL = 'lp_pool',
  TOKEN_DATA = 'token_data',
  // ...
}

// Type-safe service retrieval
runtime.getService<WalletService>(ServiceType.WALLET)
```

**Agno Adaptation:**
```python
from enum import Enum
from typing import TypeVar, Generic, Type

class ServiceType(Enum):
    WALLET = "wallet"
    LP_POOL = "lp_pool"
    TOKEN_DATA = "token_data"
    PRICE_FEED = "price_feed"
    BLOCKCHAIN_RPC = "blockchain_rpc"
    KNOWLEDGE_GRAPH = "knowledge_graph"

T = TypeVar('T')

class ServiceRegistry:
    """Typed service registry for agent dependencies."""

    def __init__(self):
        self._services: Dict[ServiceType, Any] = {}

    def register(self, service_type: ServiceType, service: Any):
        self._services[service_type] = service

    def get(self, service_type: ServiceType, expected_type: Type[T] = None) -> T:
        service = self._services.get(service_type)
        if service is None:
            raise ValueError(f"Service {service_type} not registered")
        if expected_type and not isinstance(service, expected_type):
            raise TypeError(f"Service {service_type} is not of type {expected_type}")
        return service

# Service interfaces (from Eliza wallet pattern)
class IWalletService(ABC):
    @abstractmethod
    async def get_portfolio(self, owner: str = None) -> WalletPortfolio:
        pass

    @abstractmethod
    async def get_balance(self, asset_address: str, owner: str = None) -> float:
        pass

    @abstractmethod
    async def transfer(self, to: str, amount: float, asset: str) -> str:
        pass

class ILPPoolService(ABC):
    @abstractmethod
    async def get_pool_info(self, pool_address: str) -> PoolInfo:
        pass

    @abstractmethod
    async def get_user_positions(self, user: str) -> List[LPPosition]:
        pass

# Usage
registry = ServiceRegistry()
registry.register(ServiceType.WALLET, SolanaWalletService())
registry.register(ServiceType.LP_POOL, UniswapPoolService())

# In agent tools
class DeFiTools:
    def __init__(self, registry: ServiceRegistry):
        self.wallet = registry.get(ServiceType.WALLET, IWalletService)
        self.pools = registry.get(ServiceType.LP_POOL, ILPPoolService)
```

**Value for Crypto:**
- Clean dependency injection
- Swappable implementations (mock for testing)
- Type-safe service access
- Multi-chain support via registry

---

### Pattern 5: Multi-Type Memory

**Eliza Implementation:**
```typescript
// Multiple memory types with metadata
enum MemoryType {
  MESSAGE = 'message',
  DOCUMENT = 'document',
  FRAGMENT = 'fragment',
  DESCRIPTION = 'description',
  CUSTOM = 'custom',
}

interface Memory {
  id: UUID;
  type: MemoryType;
  content: string;
  embedding?: number[];
  metadata: MemoryMetadata;
  timestamp: Date;
}
```

**Agno Adaptation:**
```python
from enum import Enum
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime

class MemoryType(Enum):
    MESSAGE = "message"           # Conversation messages
    TRANSACTION = "transaction"   # Trade/transfer records
    OBSERVATION = "observation"   # Market observations
    ASSESSMENT = "assessment"     # Risk/quality assessments
    DOCUMENT = "document"         # External documents
    INSIGHT = "insight"           # Generated insights

@dataclass
class CryptoMemory:
    """Multi-type memory for crypto agents."""
    id: str
    type: MemoryType
    content: str
    embedding: Optional[List[float]] = None
    timestamp: datetime = None

    # Type-specific metadata
    metadata: Dict[str, Any] = None

    # Scope control
    scope: str = "private"  # "private" | "shared" | "public"

@dataclass
class TransactionMemory(CryptoMemory):
    """Memory of a trade/transaction."""
    type: MemoryType = MemoryType.TRANSACTION

    symbol: str = None
    action: str = None  # "buy" | "sell" | "swap"
    amount: float = None
    price: float = None
    tx_hash: str = None
    pnl: float = None

@dataclass
class ObservationMemory(CryptoMemory):
    """Memory of a market observation."""
    type: MemoryType = MemoryType.OBSERVATION

    observation_type: str = None  # "price_spike", "volume_anomaly", "sentiment_shift"
    symbols_affected: List[str] = None
    confidence: float = None
    source: str = None

@dataclass
class AssessmentMemory(CryptoMemory):
    """Memory of a risk/quality assessment."""
    type: MemoryType = MemoryType.ASSESSMENT

    assessment_type: str = None  # "risk", "trade_quality", "protocol_health"
    subject: str = None  # What was assessed
    score: float = None
    factors: Dict[str, float] = None

class CryptoMemoryStore:
    """Memory store with type-aware retrieval."""

    def __init__(self, vector_db, sql_db):
        self.vector_db = vector_db
        self.sql_db = sql_db

    async def add(self, memory: CryptoMemory):
        """Store memory with embedding."""
        if memory.embedding is None:
            memory.embedding = await self._embed(memory.content)

        await self.vector_db.insert(memory)
        await self.sql_db.insert(memory)

    async def search(
        self,
        query: str,
        memory_types: List[MemoryType] = None,
        limit: int = 10,
        scope: str = None,
    ) -> List[CryptoMemory]:
        """Search memories with type filtering."""
        query_embedding = await self._embed(query)

        results = await self.vector_db.search(
            embedding=query_embedding,
            filter={
                "type": {"$in": [t.value for t in memory_types]} if memory_types else None,
                "scope": scope,
            },
            limit=limit,
        )

        return results

    async def get_recent_transactions(self, limit: int = 10) -> List[TransactionMemory]:
        """Get recent transaction memories."""
        return await self.sql_db.query(
            type=MemoryType.TRANSACTION,
            order_by="timestamp DESC",
            limit=limit,
        )

    async def get_assessments_for(self, subject: str) -> List[AssessmentMemory]:
        """Get all assessments for a subject."""
        return await self.sql_db.query(
            type=MemoryType.ASSESSMENT,
            filter={"subject": subject},
        )
```

**Value for Crypto:**
- Separate trade history from conversation
- Track market observations over time
- Build assessment history for learning
- Enable type-specific retrieval and analysis

---

## 3. Implementation Priority

### High Priority (Implement First)
1. **Service Type Registry** - Foundation for other patterns
2. **Provider Pattern** - Clean data separation
3. **Multi-Type Memory** - Critical for crypto audit trails

### Medium Priority
4. **Character System** - Enhances agent consistency
5. **Evaluator Pattern** - Enables continuous improvement

### Lower Priority
6. **Event System** - Useful but not critical initially
7. **Plugin Priority System** - For complex multi-plugin scenarios

---

## 4. Integration with DBOS

```python
from dbos import DBOS, DBOSAgent

# Combine patterns with DBOS durability
class DurableCryptoAgent:
    """Agno agent with Eliza patterns and DBOS durability."""

    def __init__(
        self,
        character: CryptoCharacter,
        providers: List[Provider],
        evaluators: List[Evaluator],
        services: ServiceRegistry,
        memory: CryptoMemoryStore,
    ):
        self.character = character
        self.providers = providers
        self.evaluators = evaluators
        self.services = services
        self.memory = memory

        # Create base Agno agent
        self.agent = Agent(
            name=character.name,
            instructions=character.to_instructions(),
            tools=self._build_tools(services),
        )

        # Wrap with DBOS for durability
        self.durable_agent = DBOSAgent(self.agent)

    @DBOS.workflow()
    async def run(self, message: str, context: Dict = None):
        # Gather provider context
        provider_context = await self._gather_context(context)

        # Execute with durability
        response = await self.durable_agent.run(
            message,
            context=provider_context,
        )

        # Run evaluators
        evaluations = await self._run_evaluators(response, context)

        # Store in typed memory
        await self._store_interaction(message, response, evaluations)

        return response
```

---

## 5. Files to Create

Based on these patterns, create:

1. `src/agents/character.py` - Character system implementation
2. `src/agents/providers.py` - Provider base classes and crypto providers
3. `src/agents/evaluators.py` - Evaluator base classes and crypto evaluators
4. `src/agents/services.py` - Service registry and interfaces
5. `src/agents/memory.py` - Multi-type memory implementation
6. `src/agents/crypto_agent.py` - Combined DurableCryptoAgent

---

## References

- `/examples/eliza/packages/core/src/runtime.ts`
- `/examples/eliza/packages/core/src/types/`
- `/examples/eliza/packages/plugin-bootstrap/`
- `/examples/eliza/packages/service-interfaces/src/interfaces/wallet.ts`
- `/examples/agno/github_repo_analyzer/agents.py`
