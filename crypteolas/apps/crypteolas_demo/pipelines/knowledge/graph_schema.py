"""
Knowledge graph schema for crypto domain.

Defines entity types, relationships, and ontology
for the cryptocurrency knowledge graph.

Supports dual-graph architecture:
- Memgraph: Static knowledge (protocol relationships, token info)
- FalkorDB: Temporal knowledge (price movements, governance events)
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


# =============================================================================
# Entity Types
# =============================================================================


class EntityType(str, Enum):
    """Entity types in the crypto knowledge graph."""

    # Protocols & Projects
    PROTOCOL = "Protocol"
    TOKEN = "Token"
    SMART_CONTRACT = "SmartContract"
    CHAIN = "Chain"

    # Financial Instruments
    LIQUIDITY_POOL = "LiquidityPool"
    LENDING_MARKET = "LendingMarket"
    YIELD_STRATEGY = "YieldStrategy"
    DERIVATIVE = "Derivative"

    # Market Data
    PRICE_FEED = "PriceFeed"
    FUNDING_RATE = "FundingRate"
    APY_METRIC = "APYMetric"

    # Governance
    GOVERNANCE_PROPOSAL = "GovernanceProposal"
    VOTE = "Vote"
    PARAMETER_CHANGE = "ParameterChange"

    # Risk
    RISK_FACTOR = "RiskFactor"
    AUDIT = "Audit"
    INCIDENT = "Incident"

    # Documentation
    DOCUMENTATION = "Documentation"
    CONCEPT = "Concept"


ENTITY_TYPES = {e.value: e for e in EntityType}


# =============================================================================
# Relationship Types
# =============================================================================


class RelationshipType(str, Enum):
    """Relationship types in the crypto knowledge graph."""

    # Protocol relationships
    BUILT_ON = "BUILT_ON"  # Protocol -> Chain
    INTEGRATES_WITH = "INTEGRATES_WITH"  # Protocol -> Protocol
    FORKS_FROM = "FORKS_FROM"  # Protocol -> Protocol
    COMPETES_WITH = "COMPETES_WITH"  # Protocol -> Protocol

    # Token relationships
    NATIVE_TOKEN_OF = "NATIVE_TOKEN_OF"  # Token -> Protocol
    WRAPPED_VERSION_OF = "WRAPPED_VERSION_OF"  # Token -> Token
    BACKED_BY = "BACKED_BY"  # Token -> Token/Collateral
    YIELD_BEARING = "YIELD_BEARING"  # Token -> Strategy

    # Financial relationships
    PROVIDES_LIQUIDITY_TO = "PROVIDES_LIQUIDITY_TO"  # Token -> Pool
    BORROWS_FROM = "BORROWS_FROM"  # User/Protocol -> Market
    SUPPLIES_TO = "SUPPLIES_TO"  # Token -> Market
    HEDGES_WITH = "HEDGES_WITH"  # Strategy -> Derivative

    # Yield relationships
    GENERATES_YIELD = "GENERATES_YIELD"  # Strategy -> APYMetric
    SOURCES_YIELD_FROM = "SOURCES_YIELD_FROM"  # Token -> Strategy
    PAYS_FUNDING = "PAYS_FUNDING"  # Derivative -> FundingRate

    # Governance relationships
    PROPOSES = "PROPOSES"  # Entity -> Proposal
    VOTES_ON = "VOTES_ON"  # Entity -> Proposal
    AFFECTS = "AFFECTS"  # Proposal -> Parameter

    # Risk relationships
    HAS_RISK = "HAS_RISK"  # Protocol/Token -> RiskFactor
    AUDITED_BY = "AUDITED_BY"  # Protocol -> Audit
    AFFECTED_BY = "AFFECTED_BY"  # Protocol -> Incident

    # Documentation relationships
    DOCUMENTS = "DOCUMENTS"  # Doc -> Protocol/Concept
    EXPLAINS = "EXPLAINS"  # Doc -> Concept
    RELATED_TO = "RELATED_TO"  # Concept -> Concept


RELATIONSHIP_TYPES = {r.value: r for r in RelationshipType}


# =============================================================================
# Entity Schemas
# =============================================================================


@dataclass
class BaseEntity:
    """Base entity with common fields."""

    id: str
    name: str
    entity_type: EntityType
    description: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)
    source_url: Optional[str] = None


@dataclass
class ProtocolEntity(BaseEntity):
    """DeFi protocol entity."""

    entity_type: EntityType = EntityType.PROTOCOL
    chain: str = "ethereum"
    category: str = ""  # lending, dex, yield, etc.
    tvl: Optional[float] = None
    website: Optional[str] = None
    github: Optional[str] = None
    documentation_url: Optional[str] = None
    audit_status: str = "unknown"
    launch_date: Optional[datetime] = None


@dataclass
class TokenEntity(BaseEntity):
    """Token/cryptocurrency entity."""

    entity_type: EntityType = EntityType.TOKEN
    symbol: str = ""
    contract_address: Optional[str] = None
    chain: str = "ethereum"
    decimals: int = 18
    token_type: str = "ERC20"  # ERC20, native, LST, LRT, stablecoin
    total_supply: Optional[float] = None
    market_cap: Optional[float] = None
    price_usd: Optional[float] = None


@dataclass
class YieldStrategyEntity(BaseEntity):
    """Yield strategy/mechanism entity."""

    entity_type: EntityType = EntityType.YIELD_STRATEGY
    strategy_type: str = ""  # staking, lending, basis, LP
    base_apy: Optional[float] = None
    reward_apy: Optional[float] = None
    total_apy: Optional[float] = None
    risk_level: str = "medium"  # low, medium, high
    underlying_tokens: list[str] = field(default_factory=list)
    protocols_used: list[str] = field(default_factory=list)


@dataclass
class RiskFactorEntity(BaseEntity):
    """Risk factor entity."""

    entity_type: EntityType = EntityType.RISK_FACTOR
    risk_category: str = ""  # smart_contract, oracle, liquidity, regulatory
    severity: str = "medium"  # low, medium, high, critical
    likelihood: str = "possible"  # unlikely, possible, likely
    mitigation: Optional[str] = None
    affected_protocols: list[str] = field(default_factory=list)


@dataclass
class ConceptEntity(BaseEntity):
    """Conceptual entity for knowledge representation."""

    entity_type: EntityType = EntityType.CONCEPT
    domain: str = "defi"  # defi, tokenomics, governance, risk
    keywords: list[str] = field(default_factory=list)
    related_concepts: list[str] = field(default_factory=list)
    definition: Optional[str] = None


# =============================================================================
# Schema Registry
# =============================================================================


class CryptoEntitySchema:
    """
    Schema registry for crypto knowledge graph entities.

    Provides validation and serialization for graph storage.
    """

    ENTITY_CLASSES = {
        EntityType.PROTOCOL: ProtocolEntity,
        EntityType.TOKEN: TokenEntity,
        EntityType.YIELD_STRATEGY: YieldStrategyEntity,
        EntityType.RISK_FACTOR: RiskFactorEntity,
        EntityType.CONCEPT: ConceptEntity,
    }

    @classmethod
    def create_entity(cls, entity_type: EntityType, **kwargs) -> BaseEntity:
        """Create entity of specified type."""
        entity_class = cls.ENTITY_CLASSES.get(entity_type, BaseEntity)
        return entity_class(**kwargs)

    @classmethod
    def to_graph_node(cls, entity: BaseEntity) -> dict[str, Any]:
        """Convert entity to graph node format."""
        from dataclasses import asdict

        node = asdict(entity)
        node["entity_type"] = entity.entity_type.value

        # Convert datetime fields
        for key, value in node.items():
            if isinstance(value, datetime):
                node[key] = value.isoformat()

        return node

    @classmethod
    def from_graph_node(cls, node: dict[str, Any]) -> BaseEntity:
        """Create entity from graph node."""
        entity_type = EntityType(node.get("entity_type", "Concept"))
        entity_class = cls.ENTITY_CLASSES.get(entity_type, BaseEntity)

        # Parse datetime fields
        for key in ["created_at", "updated_at", "launch_date"]:
            if key in node and isinstance(node[key], str):
                node[key] = datetime.fromisoformat(node[key])

        node["entity_type"] = entity_type
        return entity_class(**node)


# =============================================================================
# Cypher Templates
# =============================================================================


MEMGRAPH_SCHEMA_CYPHER = """
// Create indexes for common queries
CREATE INDEX ON :Protocol(id);
CREATE INDEX ON :Token(id);
CREATE INDEX ON :Token(symbol);
CREATE INDEX ON :YieldStrategy(id);
CREATE INDEX ON :Concept(id);

// Create constraints (Memgraph syntax)
CREATE CONSTRAINT ON (p:Protocol) ASSERT p.id IS UNIQUE;
CREATE CONSTRAINT ON (t:Token) ASSERT t.id IS UNIQUE;
"""


FALKORDB_SCHEMA_CYPHER = """
// FalkorDB schema for temporal knowledge
// Includes timestamp on all nodes and edges

CREATE INDEX ON :Event(timestamp);
CREATE INDEX ON :PricePoint(timestamp);
CREATE INDEX ON :FundingPayment(timestamp);
"""


# =============================================================================
# Ethena-Specific Schema
# =============================================================================


ETHENA_ONTOLOGY = {
    "protocols": [
        {
            "id": "ethena",
            "name": "Ethena",
            "category": "stablecoin",
            "description": "Synthetic dollar protocol using delta-neutral hedging",
        },
    ],
    "tokens": [
        {
            "id": "usde",
            "name": "USDe",
            "symbol": "USDe",
            "token_type": "stablecoin",
            "description": "Ethena synthetic dollar",
        },
        {
            "id": "susde",
            "name": "sUSDe",
            "symbol": "sUSDe",
            "token_type": "yield_bearing",
            "description": "Staked USDe, earns protocol yield",
        },
        {
            "id": "ena",
            "name": "ENA",
            "symbol": "ENA",
            "token_type": "governance",
            "description": "Ethena governance token",
        },
    ],
    "yield_strategies": [
        {
            "id": "ethena_basis",
            "name": "Ethena Basis Trade",
            "strategy_type": "basis",
            "description": "Delta-neutral ETH/BTC staking + short perpetual position",
            "underlying_tokens": ["ETH", "BTC", "stETH"],
            "risk_level": "medium",
        },
    ],
    "risk_factors": [
        {
            "id": "funding_rate_risk",
            "name": "Negative Funding Rate Risk",
            "risk_category": "market",
            "severity": "medium",
            "description": "Extended negative funding could reduce or eliminate yield",
        },
        {
            "id": "exchange_risk",
            "name": "Centralized Exchange Risk",
            "risk_category": "counterparty",
            "severity": "medium",
            "description": "Reliance on CEX custody for hedging positions",
        },
        {
            "id": "depeg_risk",
            "name": "USDe Depeg Risk",
            "risk_category": "market",
            "severity": "high",
            "description": "Risk of USDe losing peg during extreme market conditions",
        },
    ],
    "relationships": [
        ("usde", "NATIVE_TOKEN_OF", "ethena"),
        ("susde", "YIELD_BEARING", "ethena_basis"),
        ("ethena_basis", "HEDGES_WITH", "perp_shorts"),
        ("ethena", "HAS_RISK", "funding_rate_risk"),
        ("ethena", "HAS_RISK", "exchange_risk"),
        ("usde", "HAS_RISK", "depeg_risk"),
    ],
}
