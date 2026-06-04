//! Crypteolas DeFi Analytics - SpacetimeDB Sync Module
//!
//! Real-time synchronization of DeFi data for analytics:
//! - Protocol metrics (TVL, volume, fees)
//! - Token prices and market data
//! - Liquidity pool states
//! - Cross-chain bridge activity
//! - Governance proposals and votes
//!
//! Compile to WASM: cargo build --target wasm32-unknown-unknown --release

use spacetimedb::{
    Identity, ReducerContext, SpacetimeType, Table, Timestamp,
    reducer, table,
};

// ============================================================================
// Tables - Protocol Registry
// ============================================================================

/// Registered DeFi protocols for tracking
#[table(name = protocol, public)]
pub struct Protocol {
    #[primary_key]
    pub id: String,
    pub name: String,
    pub chain: ChainId,
    pub category: ProtocolCategory,
    /// Contract addresses (JSON array)
    pub contracts: String,
    pub tvl_usd: f64,
    pub volume_24h_usd: f64,
    pub fees_24h_usd: f64,
    pub last_updated: Timestamp,
    pub is_active: bool,
}

/// Token registry with multi-chain support
#[table(name = token, public)]
pub struct Token {
    #[primary_key]
    pub id: String,
    pub symbol: String,
    pub name: String,
    pub decimals: u8,
    pub chain: ChainId,
    /// Contract address or mint address
    pub address: String,
    /// CoinGecko ID for price feeds
    pub coingecko_id: Option<String>,
    pub price_usd: f64,
    pub market_cap_usd: f64,
    pub volume_24h_usd: f64,
    pub price_change_24h: f64,
    pub last_updated: Timestamp,
}

// ============================================================================
// Tables - Price Data
// ============================================================================

/// Historical price snapshots (hourly)
#[table(name = price_snapshot, public)]
pub struct PriceSnapshot {
    #[primary_key]
    #[auto_inc]
    pub id: u64,
    pub token_id: String,
    pub price_usd: f64,
    pub volume_usd: f64,
    /// Unix timestamp rounded to hour
    pub hour_timestamp: u64,
    pub recorded_at: Timestamp,
}

/// Real-time price from DEX aggregators
#[table(name = dex_price, public)]
pub struct DexPrice {
    #[primary_key]
    pub token_pair: String,
    pub base_token: String,
    pub quote_token: String,
    pub price: f64,
    pub liquidity_usd: f64,
    pub source: DexSource,
    pub last_updated: Timestamp,
}

// ============================================================================
// Tables - Liquidity Pools
// ============================================================================

/// AMM liquidity pool state
#[table(name = liquidity_pool, public)]
pub struct LiquidityPool {
    #[primary_key]
    pub id: String,
    pub protocol_id: String,
    pub chain: ChainId,
    pub pool_type: PoolType,
    pub token_a: String,
    pub token_b: String,
    pub reserve_a: f64,
    pub reserve_b: f64,
    pub tvl_usd: f64,
    pub volume_24h_usd: f64,
    pub fee_tier: u32,
    pub apr: f64,
    pub last_updated: Timestamp,
}

/// User LP positions
#[table(name = lp_position, public)]
pub struct LpPosition {
    #[primary_key]
    #[auto_inc]
    pub id: u64,
    pub owner_identity: Identity,
    pub pool_id: String,
    pub liquidity_tokens: f64,
    pub token_a_deposited: f64,
    pub token_b_deposited: f64,
    pub entry_price_usd: f64,
    pub current_value_usd: f64,
    pub unclaimed_fees_usd: f64,
    pub created_at: Timestamp,
    pub last_updated: Timestamp,
}

// ============================================================================
// Tables - Cross-Chain Bridge
// ============================================================================

/// Bridge transfer records
#[table(name = bridge_transfer, public)]
pub struct BridgeTransfer {
    #[primary_key]
    pub transfer_id: String,
    pub bridge_provider: BridgeProvider,
    pub source_chain: ChainId,
    pub dest_chain: ChainId,
    pub token_symbol: String,
    pub amount: f64,
    pub amount_usd: f64,
    pub sender_address: String,
    pub recipient_address: String,
    pub status: BridgeStatus,
    /// Wormhole VAA sequence number
    pub vaa_sequence: Option<u64>,
    /// Source chain tx hash
    pub source_tx: Option<String>,
    /// Destination chain tx hash
    pub dest_tx: Option<String>,
    pub initiated_at: Timestamp,
    pub completed_at: Option<Timestamp>,
}

// ============================================================================
// Tables - Governance
// ============================================================================

/// DAO governance proposals
#[table(name = governance_proposal, public)]
pub struct GovernanceProposal {
    #[primary_key]
    pub id: String,
    pub protocol_id: String,
    pub proposal_id: u64,
    pub title: String,
    pub description_uri: String,
    pub proposer: String,
    pub status: ProposalStatus,
    pub votes_for: f64,
    pub votes_against: f64,
    pub votes_abstain: f64,
    pub quorum_required: f64,
    pub start_time: Timestamp,
    pub end_time: Timestamp,
    pub executed_at: Option<Timestamp>,
}

/// Individual votes on proposals
#[table(name = governance_vote, public)]
pub struct GovernanceVote {
    #[primary_key]
    #[auto_inc]
    pub id: u64,
    pub proposal_id: String,
    pub voter_identity: Identity,
    pub voter_address: String,
    pub vote_type: VoteType,
    pub voting_power: f64,
    pub voted_at: Timestamp,
}

// ============================================================================
// Tables - Analytics Aggregates
// ============================================================================

/// Daily protocol metrics aggregate
#[table(name = daily_protocol_metrics, public)]
pub struct DailyProtocolMetrics {
    #[primary_key]
    pub id: String,
    pub protocol_id: String,
    /// Unix timestamp for day start (UTC)
    pub day_timestamp: u64,
    pub tvl_usd: f64,
    pub volume_usd: f64,
    pub fees_usd: f64,
    pub unique_users: u32,
    pub transactions: u32,
    pub recorded_at: Timestamp,
}

/// Sync job tracking for external data sources
#[table(name = sync_job, public)]
pub struct SyncJob {
    #[primary_key]
    #[auto_inc]
    pub id: u64,
    pub source: DataSource,
    pub job_type: SyncJobType,
    pub status: SyncStatus,
    pub records_processed: u32,
    pub error_message: Option<String>,
    pub started_at: Timestamp,
    pub completed_at: Option<Timestamp>,
}

// ============================================================================
// Enums
// ============================================================================

#[derive(SpacetimeType, Clone, Copy, PartialEq, Eq, Debug)]
pub enum ChainId {
    Ethereum,
    Solana,
    Base,
    Arbitrum,
    Polygon,
    Optimism,
}

#[derive(SpacetimeType, Clone, Copy, PartialEq, Eq, Debug)]
pub enum ProtocolCategory {
    Dex,
    Lending,
    Derivatives,
    Yield,
    Bridge,
    Nft,
    Gaming,
    Other,
}

#[derive(SpacetimeType, Clone, Copy, PartialEq, Eq, Debug)]
pub enum DexSource {
    Jupiter,
    Raydium,
    Orca,
    Uniswap,
    Curve,
    Balancer,
    Aerodrome,
}

#[derive(SpacetimeType, Clone, Copy, PartialEq, Eq, Debug)]
pub enum PoolType {
    ConstantProduct,
    StableSwap,
    Concentrated,
    Weighted,
}

#[derive(SpacetimeType, Clone, Copy, PartialEq, Eq, Debug)]
pub enum BridgeProvider {
    Wormhole,
    LayerZero,
    Chainlink,
    Axelar,
}

#[derive(SpacetimeType, Clone, Copy, PartialEq, Eq, Debug, Default)]
pub enum BridgeStatus {
    #[default]
    Initiated,
    VaaEmitted,
    Redeemed,
    Failed,
}

#[derive(SpacetimeType, Clone, Copy, PartialEq, Eq, Debug)]
pub enum ProposalStatus {
    Active,
    Passed,
    Defeated,
    Queued,
    Executed,
    Cancelled,
}

#[derive(SpacetimeType, Clone, Copy, PartialEq, Eq, Debug)]
pub enum VoteType {
    For,
    Against,
    Abstain,
}

#[derive(SpacetimeType, Clone, Copy, PartialEq, Eq, Debug)]
pub enum DataSource {
    DefiLlama,
    CoinGecko,
    Dune,
    TheGraph,
    Helius,
    Alchemy,
}

#[derive(SpacetimeType, Clone, Copy, PartialEq, Eq, Debug)]
pub enum SyncJobType {
    PriceUpdate,
    TvlUpdate,
    PoolSync,
    BridgeMonitor,
    GovernanceSync,
}

#[derive(SpacetimeType, Clone, Copy, PartialEq, Eq, Debug, Default)]
pub enum SyncStatus {
    #[default]
    Pending,
    Running,
    Completed,
    Failed,
}

// ============================================================================
// Reducers - Protocol Management
// ============================================================================

/// Register a new DeFi protocol for tracking
#[reducer]
pub fn register_protocol(
    ctx: &ReducerContext,
    id: String,
    name: String,
    chain: ChainId,
    category: ProtocolCategory,
    contracts: String,
) -> Result<(), String> {
    let now = ctx.timestamp;

    if ctx.db.protocol().id().find(&id).is_some() {
        return Err("Protocol already registered".to_string());
    }

    ctx.db.protocol().insert(Protocol {
        id,
        name,
        chain,
        category,
        contracts,
        tvl_usd: 0.0,
        volume_24h_usd: 0.0,
        fees_24h_usd: 0.0,
        last_updated: now,
        is_active: true,
    });

    Ok(())
}

/// Update protocol metrics from external data source
#[reducer]
pub fn update_protocol_metrics(
    ctx: &ReducerContext,
    protocol_id: String,
    tvl_usd: f64,
    volume_24h_usd: f64,
    fees_24h_usd: f64,
) -> Result<(), String> {
    let now = ctx.timestamp;

    let mut protocol = ctx.db.protocol().id().find(&protocol_id)
        .ok_or("Protocol not found")?;

    protocol.tvl_usd = tvl_usd;
    protocol.volume_24h_usd = volume_24h_usd;
    protocol.fees_24h_usd = fees_24h_usd;
    protocol.last_updated = now;

    ctx.db.protocol().id().update(protocol);
    Ok(())
}

// ============================================================================
// Reducers - Token & Price Management
// ============================================================================

/// Register a token for price tracking
#[reducer]
pub fn register_token(
    ctx: &ReducerContext,
    id: String,
    symbol: String,
    name: String,
    decimals: u8,
    chain: ChainId,
    address: String,
    coingecko_id: Option<String>,
) -> Result<(), String> {
    let now = ctx.timestamp;

    if ctx.db.token().id().find(&id).is_some() {
        return Err("Token already registered".to_string());
    }

    ctx.db.token().insert(Token {
        id,
        symbol,
        name,
        decimals,
        chain,
        address,
        coingecko_id,
        price_usd: 0.0,
        market_cap_usd: 0.0,
        volume_24h_usd: 0.0,
        price_change_24h: 0.0,
        last_updated: now,
    });

    Ok(())
}

/// Update token price from oracle/aggregator
#[reducer]
pub fn update_token_price(
    ctx: &ReducerContext,
    token_id: String,
    price_usd: f64,
    market_cap_usd: f64,
    volume_24h_usd: f64,
    price_change_24h: f64,
) -> Result<(), String> {
    let now = ctx.timestamp;

    let mut token = ctx.db.token().id().find(&token_id)
        .ok_or("Token not found")?;

    token.price_usd = price_usd;
    token.market_cap_usd = market_cap_usd;
    token.volume_24h_usd = volume_24h_usd;
    token.price_change_24h = price_change_24h;
    token.last_updated = now;

    ctx.db.token().id().update(token);
    Ok(())
}

/// Record hourly price snapshot
#[reducer]
pub fn record_price_snapshot(
    ctx: &ReducerContext,
    token_id: String,
    price_usd: f64,
    volume_usd: f64,
    hour_timestamp: u64,
) -> Result<(), String> {
    let now = ctx.timestamp;

    ctx.db.price_snapshot().insert(PriceSnapshot {
        id: 0, // auto_inc
        token_id,
        price_usd,
        volume_usd,
        hour_timestamp,
        recorded_at: now,
    });

    Ok(())
}

// ============================================================================
// Reducers - Liquidity Pool Management
// ============================================================================

/// Register or update a liquidity pool
#[reducer]
pub fn upsert_liquidity_pool(
    ctx: &ReducerContext,
    id: String,
    protocol_id: String,
    chain: ChainId,
    pool_type: PoolType,
    token_a: String,
    token_b: String,
    reserve_a: f64,
    reserve_b: f64,
    tvl_usd: f64,
    volume_24h_usd: f64,
    fee_tier: u32,
    apr: f64,
) -> Result<(), String> {
    let now = ctx.timestamp;

    if let Some(mut pool) = ctx.db.liquidity_pool().id().find(&id) {
        pool.reserve_a = reserve_a;
        pool.reserve_b = reserve_b;
        pool.tvl_usd = tvl_usd;
        pool.volume_24h_usd = volume_24h_usd;
        pool.apr = apr;
        pool.last_updated = now;
        ctx.db.liquidity_pool().id().update(pool);
    } else {
        ctx.db.liquidity_pool().insert(LiquidityPool {
            id,
            protocol_id,
            chain,
            pool_type,
            token_a,
            token_b,
            reserve_a,
            reserve_b,
            tvl_usd,
            volume_24h_usd,
            fee_tier,
            apr,
            last_updated: now,
        });
    }

    Ok(())
}

/// Record user LP position
#[reducer]
pub fn record_lp_position(
    ctx: &ReducerContext,
    pool_id: String,
    liquidity_tokens: f64,
    token_a_deposited: f64,
    token_b_deposited: f64,
    entry_price_usd: f64,
) -> Result<(), String> {
    let identity = ctx.sender;
    let now = ctx.timestamp;

    ctx.db.lp_position().insert(LpPosition {
        id: 0, // auto_inc
        owner_identity: identity,
        pool_id,
        liquidity_tokens,
        token_a_deposited,
        token_b_deposited,
        entry_price_usd,
        current_value_usd: entry_price_usd,
        unclaimed_fees_usd: 0.0,
        created_at: now,
        last_updated: now,
    });

    Ok(())
}

// ============================================================================
// Reducers - Bridge Operations
// ============================================================================

/// Initiate a bridge transfer record
#[reducer]
pub fn initiate_bridge_transfer(
    ctx: &ReducerContext,
    transfer_id: String,
    bridge_provider: BridgeProvider,
    source_chain: ChainId,
    dest_chain: ChainId,
    token_symbol: String,
    amount: f64,
    amount_usd: f64,
    sender_address: String,
    recipient_address: String,
) -> Result<(), String> {
    let now = ctx.timestamp;

    if ctx.db.bridge_transfer().transfer_id().find(&transfer_id).is_some() {
        return Err("Transfer already exists".to_string());
    }

    ctx.db.bridge_transfer().insert(BridgeTransfer {
        transfer_id,
        bridge_provider,
        source_chain,
        dest_chain,
        token_symbol,
        amount,
        amount_usd,
        sender_address,
        recipient_address,
        status: BridgeStatus::Initiated,
        vaa_sequence: None,
        source_tx: None,
        dest_tx: None,
        initiated_at: now,
        completed_at: None,
    });

    Ok(())
}

/// Update bridge transfer with VAA info (Wormhole)
#[reducer]
pub fn update_bridge_vaa(
    ctx: &ReducerContext,
    transfer_id: String,
    vaa_sequence: u64,
    source_tx: String,
) -> Result<(), String> {
    let mut transfer = ctx.db.bridge_transfer().transfer_id().find(&transfer_id)
        .ok_or("Transfer not found")?;

    transfer.status = BridgeStatus::VaaEmitted;
    transfer.vaa_sequence = Some(vaa_sequence);
    transfer.source_tx = Some(source_tx);

    ctx.db.bridge_transfer().transfer_id().update(transfer);
    Ok(())
}

/// Complete bridge transfer
#[reducer]
pub fn complete_bridge_transfer(
    ctx: &ReducerContext,
    transfer_id: String,
    dest_tx: String,
) -> Result<(), String> {
    let now = ctx.timestamp;

    let mut transfer = ctx.db.bridge_transfer().transfer_id().find(&transfer_id)
        .ok_or("Transfer not found")?;

    transfer.status = BridgeStatus::Redeemed;
    transfer.dest_tx = Some(dest_tx);
    transfer.completed_at = Some(now);

    ctx.db.bridge_transfer().transfer_id().update(transfer);
    Ok(())
}

// ============================================================================
// Reducers - Governance
// ============================================================================

/// Record a new governance proposal
#[reducer]
pub fn record_proposal(
    ctx: &ReducerContext,
    id: String,
    protocol_id: String,
    proposal_id: u64,
    title: String,
    description_uri: String,
    proposer: String,
    quorum_required: f64,
    start_time: Timestamp,
    end_time: Timestamp,
) -> Result<(), String> {
    if ctx.db.governance_proposal().id().find(&id).is_some() {
        return Err("Proposal already exists".to_string());
    }

    ctx.db.governance_proposal().insert(GovernanceProposal {
        id,
        protocol_id,
        proposal_id,
        title,
        description_uri,
        proposer,
        status: ProposalStatus::Active,
        votes_for: 0.0,
        votes_against: 0.0,
        votes_abstain: 0.0,
        quorum_required,
        start_time,
        end_time,
        executed_at: None,
    });

    Ok(())
}

/// Record a vote on a proposal
#[reducer]
pub fn record_vote(
    ctx: &ReducerContext,
    proposal_id: String,
    voter_address: String,
    vote_type: VoteType,
    voting_power: f64,
) -> Result<(), String> {
    let identity = ctx.sender;
    let now = ctx.timestamp;

    // Update proposal vote counts
    let mut proposal = ctx.db.governance_proposal().id().find(&proposal_id)
        .ok_or("Proposal not found")?;

    match vote_type {
        VoteType::For => proposal.votes_for += voting_power,
        VoteType::Against => proposal.votes_against += voting_power,
        VoteType::Abstain => proposal.votes_abstain += voting_power,
    }

    ctx.db.governance_proposal().id().update(proposal);

    // Record individual vote
    ctx.db.governance_vote().insert(GovernanceVote {
        id: 0, // auto_inc
        proposal_id,
        voter_identity: identity,
        voter_address,
        vote_type,
        voting_power,
        voted_at: now,
    });

    Ok(())
}

// ============================================================================
// Reducers - Sync Jobs
// ============================================================================

/// Start a new sync job
#[reducer]
pub fn start_sync_job(
    ctx: &ReducerContext,
    source: DataSource,
    job_type: SyncJobType,
) -> Result<u64, String> {
    let now = ctx.timestamp;

    let job = SyncJob {
        id: 0, // auto_inc
        source,
        job_type,
        status: SyncStatus::Running,
        records_processed: 0,
        error_message: None,
        started_at: now,
        completed_at: None,
    };

    // Note: In real impl, we'd return the generated ID
    ctx.db.sync_job().insert(job);
    Ok(0)
}

/// Complete a sync job
#[reducer]
pub fn complete_sync_job(
    ctx: &ReducerContext,
    job_id: u64,
    records_processed: u32,
    error_message: Option<String>,
) -> Result<(), String> {
    let now = ctx.timestamp;

    let mut job = ctx.db.sync_job().id().find(job_id)
        .ok_or("Sync job not found")?;

    job.status = if error_message.is_some() {
        SyncStatus::Failed
    } else {
        SyncStatus::Completed
    };
    job.records_processed = records_processed;
    job.error_message = error_message;
    job.completed_at = Some(now);

    ctx.db.sync_job().id().update(job);
    Ok(())
}

/// Record daily protocol metrics aggregate
#[reducer]
pub fn record_daily_metrics(
    ctx: &ReducerContext,
    protocol_id: String,
    day_timestamp: u64,
    tvl_usd: f64,
    volume_usd: f64,
    fees_usd: f64,
    unique_users: u32,
    transactions: u32,
) -> Result<(), String> {
    let now = ctx.timestamp;
    let id = format!("{}:{}", protocol_id, day_timestamp);

    if let Some(mut metrics) = ctx.db.daily_protocol_metrics().id().find(&id) {
        metrics.tvl_usd = tvl_usd;
        metrics.volume_usd = volume_usd;
        metrics.fees_usd = fees_usd;
        metrics.unique_users = unique_users;
        metrics.transactions = transactions;
        metrics.recorded_at = now;
        ctx.db.daily_protocol_metrics().id().update(metrics);
    } else {
        ctx.db.daily_protocol_metrics().insert(DailyProtocolMetrics {
            id,
            protocol_id,
            day_timestamp,
            tvl_usd,
            volume_usd,
            fees_usd,
            unique_users,
            transactions,
            recorded_at: now,
        });
    }

    Ok(())
}
