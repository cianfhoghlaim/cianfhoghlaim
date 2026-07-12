//! Tuath Celtic MMO - SpacetimeDB Game Module
//!
//! Authoritative game state for the Celtic MMO:
//! - Player identity and wallet linking
//! - Position tracking with spatial indexing
//! - Inventory with on-chain sync status
//! - Clan membership and governance
//!
//! Compile to WASM: cargo build --target wasm32-unknown-unknown --release

use spacetimedb::{
    Identity, ReducerContext, SpacetimeType, Table, Timestamp,
    reducer, table,
};

// Re-export shared types
pub use cianfhoghlaim_shared_types::{
    CelticLanguage, CelticStyle, ClanId, GameZone, IrishDialect, ItemType,
    ObjectiveType, OnChainStatus, Position, ProposalStatus, ProposalType,
    QuestStatus, QuestType, WalletChain,
};

// ============================================================================
// Tables
// ============================================================================

/// Player identity and wallet associations
#[table(name = player, public)]
pub struct Player {
    #[primary_key]
    pub identity: Identity,
    pub username: Option<String>,
    /// Ethereum address (checksummed)
    pub eth_address: Option<String>,
    /// Solana public key (base58)
    pub sol_address: Option<String>,
    /// Current clan membership
    pub clan_id: Option<u64>,
    pub created_at: Timestamp,
    pub last_active: Timestamp,
}

/// Entity position with spatial indexing
#[table(name = entity_position, public)]
pub struct EntityPosition {
    #[primary_key]
    pub entity_id: u64,
    pub x: f32,
    pub y: f32,
    pub z: f32,
    /// Spatial bucket for efficient proximity queries
    pub region_bucket: i64,
    pub last_updated: Timestamp,
}

/// Game inventory items with blockchain sync status
#[table(name = inventory_item, public)]
pub struct InventoryItem {
    #[primary_key]
    #[auto_inc]
    pub id: u64,
    pub owner_identity: Identity,
    pub item_type: ItemTypeDb,
    pub name: String,
    pub metadata_uri: Option<String>,
    pub on_chain_status: OnChainStatusDb,
    /// Solana mint address (if minted)
    pub solana_mint: Option<String>,
    /// Ethereum token ID (if bridged)
    pub eth_token_id: Option<String>,
    pub created_at: Timestamp,
}

/// Clan definitions
#[table(name = clan, public)]
pub struct Clan {
    #[primary_key]
    #[auto_inc]
    pub id: u64,
    pub name: String,
    pub description: String,
    /// Solana treasury PDA (confidential transfers)
    pub treasury_sol: Option<String>,
    /// Ethereum L2 multisig
    pub treasury_eth: Option<String>,
    pub member_count: u32,
    pub territory_count: u32,
    pub created_at: Timestamp,
}

/// Pending blockchain operations for relayer
#[table(name = pending_mint, public)]
pub struct PendingMint {
    #[primary_key]
    pub item_id: u64,
    pub owner_identity: Identity,
    pub requested_at: Timestamp,
    pub attempts: u32,
}

// ============================================================================
// Quest System Tables
// ============================================================================

/// Quest definition template
#[table(name = quest, public)]
pub struct Quest {
    #[primary_key]
    pub id: String,
    pub name: String,
    /// Irish/Welsh/Scottish Gaelic name
    pub native_name: String,
    pub description: String,
    pub quest_type: QuestTypeDb,
    /// Zone where quest takes place
    pub zone: GameZoneDb,
    /// Primary language for this quest
    pub language: CelticLanguageDb,
    pub level_required: u8,
    pub xp_reward: u32,
    /// Serialized JSON array of item IDs
    pub item_rewards_json: String,
    /// Serialized JSON array of QuestObjective
    pub objectives_json: String,
    /// Quest IDs that must be completed first
    pub prerequisites_json: String,
    /// Whether quest requires x402 payment
    pub is_premium: bool,
    pub created_at: Timestamp,
}

/// Player's quest progress
#[table(name = player_quest, public)]
pub struct PlayerQuest {
    #[primary_key]
    #[auto_inc]
    pub id: u64,
    pub player_identity: Identity,
    pub quest_id: String,
    pub status: QuestStatusDb,
    /// Serialized JSON array of booleans
    pub objectives_completed_json: String,
    pub hints_used: u8,
    pub started_at: Timestamp,
    pub completed_at: Option<Timestamp>,
}

// ============================================================================
// Clan Governance Tables
// ============================================================================

/// Clan governance proposal
#[table(name = clan_proposal, public)]
pub struct ClanProposal {
    #[primary_key]
    #[auto_inc]
    pub id: u64,
    pub clan_id: u64,
    pub proposer: Identity,
    pub proposal_type: ProposalTypeDb,
    pub title: String,
    pub description: String,
    /// Serialized action data
    pub execution_data_json: String,
    pub status: ProposalStatusDb,
    pub votes_for: u32,
    pub votes_against: u32,
    pub quorum_required: u32,
    pub created_at: Timestamp,
    /// Unix timestamp when voting ends
    pub voting_ends_at: u64,
    pub executed_at: Option<Timestamp>,
}

/// Individual vote on a proposal
#[table(name = clan_vote, public)]
pub struct ClanVote {
    #[primary_key]
    #[auto_inc]
    pub id: u64,
    pub proposal_id: u64,
    pub voter: Identity,
    /// true = for, false = against
    pub vote: bool,
    /// Voting power based on governance token balance
    pub voting_power: u32,
    pub cast_at: Timestamp,
}

/// Governance token balance for voting
#[table(name = governance_balance, public)]
pub struct GovernanceBalance {
    #[primary_key]
    pub player_identity: Identity,
    pub clan_id: u64,
    /// Total governance tokens
    pub token_balance: u64,
    /// Tokens locked for active votes
    pub staked_amount: u64,
    /// Delegation to another player (optional)
    pub delegation: Option<Identity>,
    pub last_claimed: Timestamp,
}

// ============================================================================
// Zone Presence Tables
// ============================================================================

/// Real-time zone presence for nearby player queries
#[table(name = zone_presence, public)]
pub struct ZonePresence {
    #[primary_key]
    pub player_identity: Identity,
    pub zone_id: GameZoneDb,
    pub region_bucket: i64,
    pub entered_at: Timestamp,
    pub last_heartbeat: Timestamp,
}

// ============================================================================
// NPC and Dialogue Tables
// ============================================================================

/// NPC definitions for Celtic mythological characters
#[table(name = npc, public)]
pub struct Npc {
    #[primary_key]
    pub id: String,
    pub name: String,
    /// Native language name (e.g., "Lugh Lámhfhada")
    pub native_name: String,
    /// Mythological figure reference (e.g., "Lugh", "Cú Chulainn")
    pub mythological_figure: Option<String>,
    pub zone: GameZoneDb,
    /// JSON dialogue tree reference
    pub dialogue_tree_json: String,
    /// Languages this NPC speaks
    pub languages_json: String,
    pub sprite_id: String,
    pub description: String,
}

/// Player's dialogue state with an NPC
#[table(name = npc_dialogue_state, public)]
pub struct NpcDialogueState {
    #[primary_key]
    #[auto_inc]
    pub id: u64,
    pub player_identity: Identity,
    pub npc_id: String,
    pub current_node: String,
    /// JSON array of unlocked branches
    pub unlocked_branches_json: String,
    /// -100 to +100 relationship score
    pub relationship_level: i8,
    pub last_interaction: Timestamp,
}

/// Vocabulary learned from NPCs
#[table(name = vocabulary_progress, public)]
pub struct VocabularyProgress {
    #[primary_key]
    #[auto_inc]
    pub id: u64,
    pub player_identity: Identity,
    pub word: String,
    pub translation: String,
    pub language: CelticLanguageDb,
    /// Spaced repetition interval in hours
    pub srs_interval: u32,
    pub next_review: Timestamp,
    pub times_reviewed: u32,
    pub times_correct: u32,
    pub learned_from_npc: Option<String>,
    pub learned_at: Timestamp,
}

// ============================================================================
// SpacetimeDB-compatible enums
// ============================================================================

#[derive(SpacetimeType, Clone, Copy, PartialEq, Eq, Debug)]
pub enum ItemTypeDb {
    Weapon,
    Armor,
    Artifact,
    Consumable,
    Quest,
    Material,
}

#[derive(SpacetimeType, Clone, Copy, PartialEq, Eq, Debug, Default)]
pub enum OnChainStatusDb {
    #[default]
    OffChain,
    Pending,
    Synced,
    Withdrawn,
}

#[derive(SpacetimeType, Clone, Copy, PartialEq, Eq, Debug)]
pub enum WalletChainDb {
    Ethereum,
    Solana,
}

#[derive(SpacetimeType, Clone, Copy, PartialEq, Eq, Debug)]
pub enum QuestTypeDb {
    LanguageLearning,
    MythologyDiscovery,
    CulturalExploration,
    Combat,
    Crafting,
    Social,
    MainStory,
}

#[derive(SpacetimeType, Clone, Copy, PartialEq, Eq, Debug, Default)]
pub enum QuestStatusDb {
    #[default]
    Available,
    InProgress,
    Completed,
    Failed,
    Abandoned,
}

#[derive(SpacetimeType, Clone, Copy, PartialEq, Eq, Debug)]
pub enum ObjectiveTypeDb {
    Collect,
    Defeat,
    Visit,
    TalkTo,
    LearnVocabulary,
    LanguageExercise,
    DiscoverLore,
    Craft,
    Deliver,
    Escort,
}

#[derive(SpacetimeType, Clone, Copy, PartialEq, Eq, Debug)]
pub enum ProposalTypeDb {
    TreasurySpend,
    MemberAdmission,
    MemberExpulsion,
    RankChange,
    TerritoryConquest,
    AllianceFormation,
    ParameterChange,
    TokenDistribution,
}

#[derive(SpacetimeType, Clone, Copy, PartialEq, Eq, Debug, Default)]
pub enum ProposalStatusDb {
    #[default]
    Active,
    Passed,
    Failed,
    Executed,
    Cancelled,
    Expired,
}

#[derive(SpacetimeType, Clone, Copy, PartialEq, Eq, Debug)]
pub enum CelticLanguageDb {
    Irish,
    ScottishGaelic,
    Welsh,
    Manx,
    Cornish,
    Breton,
}

#[derive(SpacetimeType, Clone, Copy, PartialEq, Eq, Debug)]
pub enum GameZoneDb {
    // Irish regions (Gaeltacht)
    Connemara,
    Donegal,
    Kerry,
    ClearIsland,
    AranIslands,
    // Scottish regions
    SkyeIsland,
    Highlands,
    OuterHebrides,
    // Welsh regions
    Dyfed,
    Gwynedd,
    Anglesey,
    // Mythological realms
    TirNaNog,
    TechDuinn,
    MagMell,
    Annwn,
}

// ============================================================================
// Reducers (Game Logic)
// ============================================================================

/// Create a new player on first connection
#[reducer]
pub fn create_player(ctx: &ReducerContext, username: Option<String>) -> Result<(), String> {
    let identity = ctx.sender;
    let now = ctx.timestamp;

    // Check if player already exists
    if ctx.db.player().identity().find(identity).is_some() {
        return Err("Player already exists".to_string());
    }

    ctx.db.player().insert(Player {
        identity,
        username,
        eth_address: None,
        sol_address: None,
        clan_id: None,
        created_at: now,
        last_active: now,
    });

    Ok(())
}

/// Link a wallet address to player identity
#[reducer]
pub fn link_wallet(
    ctx: &ReducerContext,
    chain: WalletChainDb,
    address: String,
    _signature: Vec<u8>,
    _message: String,
) -> Result<(), String> {
    let identity = ctx.sender;

    // TODO: Verify signature matches address
    // For Ethereum: ecrecover with keccak256 message hash
    // For Solana: ed25519_verify with message bytes

    let mut player = ctx.db.player().identity().find(identity)
        .ok_or("Player not found")?;

    match chain {
        WalletChainDb::Ethereum => {
            if player.eth_address.is_some() {
                return Err("Ethereum wallet already linked".to_string());
            }
            player.eth_address = Some(address);
        }
        WalletChainDb::Solana => {
            if player.sol_address.is_some() {
                return Err("Solana wallet already linked".to_string());
            }
            player.sol_address = Some(address);
        }
    }

    ctx.db.player().identity().update(player);
    Ok(())
}

/// Update entity position with spatial indexing
#[reducer]
pub fn update_position(
    ctx: &ReducerContext,
    entity_id: u64,
    x: f32,
    y: f32,
    z: f32,
) -> Result<(), String> {
    let now = ctx.timestamp;

    // Calculate region bucket for spatial queries
    let pos = Position::new(x, y, z);
    let region_bucket = pos.region_bucket();

    // Upsert position
    if let Some(mut existing) = ctx.db.entity_position().entity_id().find(entity_id) {
        existing.x = x;
        existing.y = y;
        existing.z = z;
        existing.region_bucket = region_bucket;
        existing.last_updated = now;
        ctx.db.entity_position().entity_id().update(existing);
    } else {
        ctx.db.entity_position().insert(EntityPosition {
            entity_id,
            x,
            y,
            z,
            region_bucket,
            last_updated: now,
        });
    }

    Ok(())
}

/// Request on-chain minting of an item
#[reducer]
pub fn request_item_mint(ctx: &ReducerContext, item_id: u64) -> Result<(), String> {
    let identity = ctx.sender;
    let now = ctx.timestamp;

    // Verify ownership
    let mut item = ctx.db.inventory_item().id().find(item_id)
        .ok_or("Item not found")?;

    if item.owner_identity != identity {
        return Err("Not item owner".to_string());
    }

    if item.on_chain_status != OnChainStatusDb::OffChain {
        return Err("Item already has on-chain status".to_string());
    }

    // Mark as pending and queue for relayer
    item.on_chain_status = OnChainStatusDb::Pending;
    ctx.db.inventory_item().id().update(item);

    ctx.db.pending_mint().insert(PendingMint {
        item_id,
        owner_identity: identity,
        requested_at: now,
        attempts: 0,
    });

    Ok(())
}

/// Callback from relayer after successful mint
#[reducer]
pub fn confirm_mint(
    ctx: &ReducerContext,
    item_id: u64,
    solana_mint: String,
    _tx_signature: String,
) -> Result<(), String> {
    // TODO: Verify caller is authorized relayer

    // Update item with mint info
    let mut item = ctx.db.inventory_item().id().find(item_id)
        .ok_or("Item not found")?;

    item.on_chain_status = OnChainStatusDb::Synced;
    item.solana_mint = Some(solana_mint);
    ctx.db.inventory_item().id().update(item);

    // Remove from pending queue
    if let Some(pending) = ctx.db.pending_mint().item_id().find(item_id) {
        ctx.db.pending_mint().item_id().delete(pending.item_id);
    }

    Ok(())
}

/// Create a new inventory item (for testing/admin)
#[reducer]
pub fn create_item(
    ctx: &ReducerContext,
    item_type: ItemTypeDb,
    name: String,
) -> Result<(), String> {
    let identity = ctx.sender;
    let now = ctx.timestamp;

    ctx.db.inventory_item().insert(InventoryItem {
        id: 0, // auto_inc
        owner_identity: identity,
        item_type,
        name,
        metadata_uri: None,
        on_chain_status: OnChainStatusDb::OffChain,
        solana_mint: None,
        eth_token_id: None,
        created_at: now,
    });

    Ok(())
}

// ============================================================================
// Quest System Reducers
// ============================================================================

/// Start a quest (validates prerequisites)
#[reducer]
pub fn start_quest(ctx: &ReducerContext, quest_id: String) -> Result<(), String> {
    let identity = ctx.sender;
    let now = ctx.timestamp;

    // Verify quest exists
    let quest = ctx.db.quest().id().find(&quest_id)
        .ok_or("Quest not found")?;

    // Check if already started
    for pq in ctx.db.player_quest().iter() {
        if pq.player_identity == identity && pq.quest_id == quest_id {
            if pq.status == QuestStatusDb::InProgress {
                return Err("Quest already in progress".to_string());
            }
            if pq.status == QuestStatusDb::Completed {
                return Err("Quest already completed".to_string());
            }
        }
    }

    // Parse prerequisites and check completion
    if !quest.prerequisites_json.is_empty() && quest.prerequisites_json != "[]" {
        // Simple JSON parsing for string array
        let prereqs: Vec<&str> = quest.prerequisites_json
            .trim_matches(|c| c == '[' || c == ']')
            .split(',')
            .map(|s| s.trim().trim_matches('"'))
            .filter(|s| !s.is_empty())
            .collect();

        for prereq in prereqs {
            let mut found_completed = false;
            for pq in ctx.db.player_quest().iter() {
                if pq.player_identity == identity
                    && pq.quest_id == prereq
                    && pq.status == QuestStatusDb::Completed
                {
                    found_completed = true;
                    break;
                }
            }
            if !found_completed {
                return Err(format!("Prerequisite quest '{}' not completed", prereq));
            }
        }
    }

    // Parse objectives to initialize completion array
    let objectives_count = quest.objectives_json
        .matches("objective_type")
        .count()
        .max(1);
    let objectives_completed = vec!["false"; objectives_count].join(",");
    let objectives_completed_json = format!("[{}]", objectives_completed);

    ctx.db.player_quest().insert(PlayerQuest {
        id: 0, // auto_inc
        player_identity: identity,
        quest_id,
        status: QuestStatusDb::InProgress,
        objectives_completed_json,
        hints_used: 0,
        started_at: now,
        completed_at: None,
    });

    Ok(())
}

/// Complete a specific objective in a quest
#[reducer]
pub fn complete_objective(
    ctx: &ReducerContext,
    quest_id: String,
    objective_index: u8,
) -> Result<(), String> {
    let identity = ctx.sender;

    // Find player's quest progress
    let mut player_quest = None;
    for pq in ctx.db.player_quest().iter() {
        if pq.player_identity == identity && pq.quest_id == quest_id {
            player_quest = Some(pq);
            break;
        }
    }

    let mut pq = player_quest.ok_or("Quest not started")?;

    if pq.status != QuestStatusDb::InProgress {
        return Err("Quest not in progress".to_string());
    }

    // Parse and update objectives
    let mut completed: Vec<bool> = pq.objectives_completed_json
        .trim_matches(|c| c == '[' || c == ']')
        .split(',')
        .map(|s| s.trim() == "true")
        .collect();

    let idx = objective_index as usize;
    if idx >= completed.len() {
        return Err("Invalid objective index".to_string());
    }

    completed[idx] = true;

    pq.objectives_completed_json = format!(
        "[{}]",
        completed.iter().map(|b| if *b { "true" } else { "false" }).collect::<Vec<_>>().join(",")
    );

    ctx.db.player_quest().id().update(pq);

    Ok(())
}

/// Complete a quest and receive rewards
#[reducer]
pub fn complete_quest(ctx: &ReducerContext, quest_id: String) -> Result<(), String> {
    let identity = ctx.sender;
    let now = ctx.timestamp;

    // Find quest definition
    let quest = ctx.db.quest().id().find(&quest_id)
        .ok_or("Quest not found")?;

    // Find player's quest progress
    let mut player_quest = None;
    for pq in ctx.db.player_quest().iter() {
        if pq.player_identity == identity && pq.quest_id == quest_id {
            player_quest = Some(pq);
            break;
        }
    }

    let mut pq = player_quest.ok_or("Quest not started")?;

    if pq.status != QuestStatusDb::InProgress {
        return Err("Quest not in progress".to_string());
    }

    // Verify all objectives completed
    let all_completed = !pq.objectives_completed_json.contains("false");
    if !all_completed {
        return Err("Not all objectives completed".to_string());
    }

    // Mark quest completed
    pq.status = QuestStatusDb::Completed;
    pq.completed_at = Some(now);
    ctx.db.player_quest().id().update(pq);

    // TODO: Award XP (quest.xp_reward) to player
    // TODO: Award items (quest.item_rewards_json) to player inventory

    Ok(())
}

/// Abandon a quest in progress
#[reducer]
pub fn abandon_quest(ctx: &ReducerContext, quest_id: String) -> Result<(), String> {
    let identity = ctx.sender;

    // Find player's quest progress
    let mut player_quest = None;
    for pq in ctx.db.player_quest().iter() {
        if pq.player_identity == identity && pq.quest_id == quest_id {
            player_quest = Some(pq);
            break;
        }
    }

    let mut pq = player_quest.ok_or("Quest not started")?;

    if pq.status != QuestStatusDb::InProgress {
        return Err("Quest not in progress".to_string());
    }

    pq.status = QuestStatusDb::Abandoned;
    ctx.db.player_quest().id().update(pq);

    Ok(())
}

// ============================================================================
// Clan Governance Reducers
// ============================================================================

/// Create a new governance proposal
#[reducer]
pub fn create_proposal(
    ctx: &ReducerContext,
    clan_id: u64,
    proposal_type: ProposalTypeDb,
    title: String,
    description: String,
    execution_data_json: String,
) -> Result<(), String> {
    let identity = ctx.sender;
    let now = ctx.timestamp;

    // Verify player is in the clan
    let player = ctx.db.player().identity().find(identity)
        .ok_or("Player not found")?;

    if player.clan_id != Some(clan_id) {
        return Err("Not a member of this clan".to_string());
    }

    // Check governance balance for proposal threshold
    let balance = ctx.db.governance_balance().player_identity().find(identity);
    let token_balance = balance.map(|b| b.token_balance).unwrap_or(0);

    // Default proposal threshold is 100 tokens
    const PROPOSAL_THRESHOLD: u64 = 100;
    if token_balance < PROPOSAL_THRESHOLD {
        return Err(format!("Need at least {} governance tokens to create proposal", PROPOSAL_THRESHOLD));
    }

    // Get clan member count for quorum calculation
    let clan = ctx.db.clan().id().find(clan_id)
        .ok_or("Clan not found")?;

    // Quorum is 20% of members (minimum 1)
    let quorum = (clan.member_count / 5).max(1);

    // Voting period is 48 hours
    let voting_ends_at = now.to_micros_since_epoch() / 1_000_000 + (48 * 60 * 60);

    ctx.db.clan_proposal().insert(ClanProposal {
        id: 0, // auto_inc
        clan_id,
        proposer: identity,
        proposal_type,
        title,
        description,
        execution_data_json,
        status: ProposalStatusDb::Active,
        votes_for: 0,
        votes_against: 0,
        quorum_required: quorum,
        created_at: now,
        voting_ends_at,
        executed_at: None,
    });

    Ok(())
}

/// Cast a vote on a proposal
#[reducer]
pub fn cast_vote(
    ctx: &ReducerContext,
    proposal_id: u64,
    vote: bool,
) -> Result<(), String> {
    let identity = ctx.sender;
    let now = ctx.timestamp;

    // Get proposal
    let mut proposal = ctx.db.clan_proposal().id().find(proposal_id)
        .ok_or("Proposal not found")?;

    // Verify proposal is active
    if proposal.status != ProposalStatusDb::Active {
        return Err("Proposal is not active".to_string());
    }

    // Check voting deadline
    let now_secs = now.to_micros_since_epoch() / 1_000_000;
    if now_secs > proposal.voting_ends_at {
        return Err("Voting period has ended".to_string());
    }

    // Verify voter is in the clan
    let player = ctx.db.player().identity().find(identity)
        .ok_or("Player not found")?;

    if player.clan_id != Some(proposal.clan_id) {
        return Err("Not a member of this clan".to_string());
    }

    // Check if already voted
    for existing_vote in ctx.db.clan_vote().iter() {
        if existing_vote.proposal_id == proposal_id && existing_vote.voter == identity {
            return Err("Already voted on this proposal".to_string());
        }
    }

    // Get voting power from governance balance
    let balance = ctx.db.governance_balance().player_identity().find(identity);
    let voting_power = balance.map(|b| b.token_balance as u32).unwrap_or(1);

    // Record vote
    ctx.db.clan_vote().insert(ClanVote {
        id: 0, // auto_inc
        proposal_id,
        voter: identity,
        vote,
        voting_power,
        cast_at: now,
    });

    // Update proposal vote counts
    if vote {
        proposal.votes_for += voting_power;
    } else {
        proposal.votes_against += voting_power;
    }
    ctx.db.clan_proposal().id().update(proposal);

    Ok(())
}

/// Execute a passed proposal
#[reducer]
pub fn execute_proposal(ctx: &ReducerContext, proposal_id: u64) -> Result<(), String> {
    let now = ctx.timestamp;

    // Get proposal
    let mut proposal = ctx.db.clan_proposal().id().find(proposal_id)
        .ok_or("Proposal not found")?;

    // Verify voting has ended
    let now_secs = now.to_micros_since_epoch() / 1_000_000;
    if now_secs <= proposal.voting_ends_at {
        return Err("Voting period has not ended".to_string());
    }

    // Check if proposal passed
    let total_votes = proposal.votes_for + proposal.votes_against;
    if total_votes < proposal.quorum_required {
        proposal.status = ProposalStatusDb::Expired;
        ctx.db.clan_proposal().id().update(proposal);
        return Err("Quorum not reached".to_string());
    }

    if proposal.votes_for <= proposal.votes_against {
        proposal.status = ProposalStatusDb::Failed;
        ctx.db.clan_proposal().id().update(proposal);
        return Err("Proposal did not pass".to_string());
    }

    // Mark as executed
    proposal.status = ProposalStatusDb::Executed;
    proposal.executed_at = Some(now);
    ctx.db.clan_proposal().id().update(proposal);

    // TODO: Parse execution_data_json and perform action based on proposal_type
    // This would integrate with treasury, membership, etc.

    Ok(())
}

// ============================================================================
// Zone Presence Reducers
// ============================================================================

/// Enter a zone (tracks player presence)
#[reducer]
pub fn enter_zone(
    ctx: &ReducerContext,
    zone_id: GameZoneDb,
    x: f32,
    z: f32,
) -> Result<(), String> {
    let identity = ctx.sender;
    let now = ctx.timestamp;

    // Calculate region bucket
    let pos = Position::new(x, 0.0, z);
    let region_bucket = pos.region_bucket();

    // Upsert zone presence
    if let Some(mut existing) = ctx.db.zone_presence().player_identity().find(identity) {
        existing.zone_id = zone_id;
        existing.region_bucket = region_bucket;
        existing.last_heartbeat = now;
        ctx.db.zone_presence().player_identity().update(existing);
    } else {
        ctx.db.zone_presence().insert(ZonePresence {
            player_identity: identity,
            zone_id,
            region_bucket,
            entered_at: now,
            last_heartbeat: now,
        });
    }

    Ok(())
}

/// Leave zone (removes presence)
#[reducer]
pub fn leave_zone(ctx: &ReducerContext) -> Result<(), String> {
    let identity = ctx.sender;

    if let Some(presence) = ctx.db.zone_presence().player_identity().find(identity) {
        ctx.db.zone_presence().player_identity().delete(presence.player_identity);
    }

    Ok(())
}

/// Heartbeat to maintain zone presence
#[reducer]
pub fn zone_heartbeat(ctx: &ReducerContext, x: f32, z: f32) -> Result<(), String> {
    let identity = ctx.sender;
    let now = ctx.timestamp;

    let mut presence = ctx.db.zone_presence().player_identity().find(identity)
        .ok_or("Not in any zone")?;

    // Update position and heartbeat
    let pos = Position::new(x, 0.0, z);
    presence.region_bucket = pos.region_bucket();
    presence.last_heartbeat = now;

    ctx.db.zone_presence().player_identity().update(presence);

    Ok(())
}

// ============================================================================
// NPC Interaction Reducers
// ============================================================================

/// Interact with an NPC (starts or continues dialogue)
#[reducer]
pub fn interact_with_npc(ctx: &ReducerContext, npc_id: String) -> Result<String, String> {
    let identity = ctx.sender;
    let now = ctx.timestamp;

    // Verify NPC exists
    let npc = ctx.db.npc().id().find(&npc_id)
        .ok_or("NPC not found")?;

    // Find or create dialogue state
    let mut dialogue_state = None;
    for ds in ctx.db.npc_dialogue_state().iter() {
        if ds.player_identity == identity && ds.npc_id == npc_id {
            dialogue_state = Some(ds);
            break;
        }
    }

    if let Some(mut ds) = dialogue_state {
        ds.last_interaction = now;
        ctx.db.npc_dialogue_state().id().update(ds.clone());
        // Return current dialogue node
        Ok(ds.current_node)
    } else {
        // Create new dialogue state at root
        ctx.db.npc_dialogue_state().insert(NpcDialogueState {
            id: 0, // auto_inc
            player_identity: identity,
            npc_id: npc_id.clone(),
            current_node: "root".to_string(),
            unlocked_branches_json: "[]".to_string(),
            relationship_level: 0,
            last_interaction: now,
        });
        Ok("root".to_string())
    }
}

/// Select a dialogue option (progresses dialogue tree)
#[reducer]
pub fn select_dialogue_option(
    ctx: &ReducerContext,
    npc_id: String,
    option_id: String,
) -> Result<String, String> {
    let identity = ctx.sender;
    let now = ctx.timestamp;

    // Find dialogue state
    let mut dialogue_state = None;
    for ds in ctx.db.npc_dialogue_state().iter() {
        if ds.player_identity == identity && ds.npc_id == npc_id {
            dialogue_state = Some(ds);
            break;
        }
    }

    let mut ds = dialogue_state.ok_or("No dialogue with this NPC")?;

    // Update current node to the selected option
    // In a full implementation, this would validate against the dialogue tree
    ds.current_node = option_id.clone();
    ds.last_interaction = now;

    // Simple relationship change based on option prefix
    if option_id.starts_with("friendly_") {
        ds.relationship_level = (ds.relationship_level + 5).min(100);
    } else if option_id.starts_with("hostile_") {
        ds.relationship_level = (ds.relationship_level - 10).max(-100);
    }

    ctx.db.npc_dialogue_state().id().update(ds);

    Ok(option_id)
}

/// Learn vocabulary from an NPC
#[reducer]
pub fn learn_vocabulary(
    ctx: &ReducerContext,
    word: String,
    translation: String,
    language: CelticLanguageDb,
    npc_id: Option<String>,
) -> Result<(), String> {
    let identity = ctx.sender;
    let now = ctx.timestamp;

    // Check if already learned
    for vp in ctx.db.vocabulary_progress().iter() {
        if vp.player_identity == identity && vp.word == word && vp.language == language {
            return Err("Word already learned".to_string());
        }
    }

    // Initial SRS interval is 4 hours
    let next_review_micros = now.to_micros_since_epoch() + (4 * 60 * 60 * 1_000_000);

    ctx.db.vocabulary_progress().insert(VocabularyProgress {
        id: 0, // auto_inc
        player_identity: identity,
        word,
        translation,
        language,
        srs_interval: 4,
        next_review: Timestamp::from_micros_since_epoch(next_review_micros),
        times_reviewed: 0,
        times_correct: 0,
        learned_from_npc: npc_id,
        learned_at: now,
    });

    Ok(())
}

/// Review vocabulary (spaced repetition)
#[reducer]
pub fn review_vocabulary(
    ctx: &ReducerContext,
    word_id: u64,
    correct: bool,
) -> Result<(), String> {
    let identity = ctx.sender;
    let now = ctx.timestamp;

    let mut vocab = ctx.db.vocabulary_progress().id().find(word_id)
        .ok_or("Vocabulary not found")?;

    if vocab.player_identity != identity {
        return Err("Not your vocabulary".to_string());
    }

    vocab.times_reviewed += 1;

    if correct {
        vocab.times_correct += 1;
        // Double the interval on correct answer (SM-2 simplified)
        vocab.srs_interval = (vocab.srs_interval * 2).min(720); // Max 30 days
    } else {
        // Reset to 1 hour on incorrect
        vocab.srs_interval = 1;
    }

    let next_review_micros = now.to_micros_since_epoch() + (vocab.srs_interval as u64 * 60 * 60 * 1_000_000);
    vocab.next_review = Timestamp::from_micros_since_epoch(next_review_micros);

    ctx.db.vocabulary_progress().id().update(vocab);

    Ok(())
}

// ============================================================================
// Admin/Initialization Reducers
// ============================================================================

/// Create a new quest definition (admin only)
#[reducer]
pub fn create_quest(
    ctx: &ReducerContext,
    id: String,
    name: String,
    native_name: String,
    description: String,
    quest_type: QuestTypeDb,
    zone: GameZoneDb,
    language: CelticLanguageDb,
    level_required: u8,
    xp_reward: u32,
    item_rewards_json: String,
    objectives_json: String,
    prerequisites_json: String,
    is_premium: bool,
) -> Result<(), String> {
    let now = ctx.timestamp;

    // Check if quest already exists
    if ctx.db.quest().id().find(&id).is_some() {
        return Err("Quest ID already exists".to_string());
    }

    ctx.db.quest().insert(Quest {
        id,
        name,
        native_name,
        description,
        quest_type,
        zone,
        language,
        level_required,
        xp_reward,
        item_rewards_json,
        objectives_json,
        prerequisites_json,
        is_premium,
        created_at: now,
    });

    Ok(())
}

/// Create a new NPC definition (admin only)
#[reducer]
pub fn create_npc(
    ctx: &ReducerContext,
    id: String,
    name: String,
    native_name: String,
    mythological_figure: Option<String>,
    zone: GameZoneDb,
    dialogue_tree_json: String,
    languages_json: String,
    sprite_id: String,
    description: String,
) -> Result<(), String> {
    // Check if NPC already exists
    if ctx.db.npc().id().find(&id).is_some() {
        return Err("NPC ID already exists".to_string());
    }

    ctx.db.npc().insert(Npc {
        id,
        name,
        native_name,
        mythological_figure,
        zone,
        dialogue_tree_json,
        languages_json,
        sprite_id,
        description,
    });

    Ok(())
}
