//! Shared types for Cianfhoghlaim
//!
//! Common data structures used across:
//! - SpacetimeDB game modules
//! - Solana programs
//! - Ethereum contracts
//! - Python/TypeScript clients

use serde::{Deserialize, Serialize};

// ============================================================================
// Quest System Types
// ============================================================================

/// Quest type categories for the Celtic MMO
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum QuestType {
    /// Language learning quests (vocabulary, grammar, pronunciation)
    LanguageLearning,
    /// Mythology discovery (learn about Celtic gods, heroes, creatures)
    MythologyDiscovery,
    /// Cultural exploration (visit historical sites, learn traditions)
    CulturalExploration,
    /// Combat/adventure quests
    Combat,
    /// Crafting and gathering quests
    Crafting,
    /// Social quests (clan activities, trading)
    Social,
    /// Main story progression
    MainStory,
}

/// Quest completion status
#[derive(Debug, Clone, Copy, PartialEq, Eq, Default, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum QuestStatus {
    /// Quest available but not started
    #[default]
    Available,
    /// Quest in progress
    InProgress,
    /// Quest completed successfully
    Completed,
    /// Quest failed
    Failed,
    /// Quest abandoned by player
    Abandoned,
}

/// Objective types within quests
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ObjectiveType {
    /// Collect N items
    Collect,
    /// Defeat N enemies
    Defeat,
    /// Visit a location
    Visit,
    /// Talk to an NPC
    TalkTo,
    /// Learn vocabulary words
    LearnVocabulary,
    /// Complete a language exercise
    LanguageExercise,
    /// Discover mythology lore
    DiscoverLore,
    /// Craft an item
    Craft,
    /// Deliver an item
    Deliver,
    /// Escort an NPC
    Escort,
}

// ============================================================================
// Governance Types
// ============================================================================

/// Clan governance proposal types
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ProposalType {
    /// Spend from clan treasury
    TreasurySpend,
    /// Admit new member to clan
    MemberAdmission,
    /// Remove member from clan
    MemberExpulsion,
    /// Change member's rank
    RankChange,
    /// Declare war on territory
    TerritoryConquest,
    /// Form alliance with another clan
    AllianceFormation,
    /// Change clan parameters (quorum, voting period, etc.)
    ParameterChange,
    /// Distribute governance tokens
    TokenDistribution,
}

/// Governance proposal status
#[derive(Debug, Clone, Copy, PartialEq, Eq, Default, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ProposalStatus {
    /// Proposal open for voting
    #[default]
    Active,
    /// Proposal passed and awaiting execution
    Passed,
    /// Proposal failed to reach quorum or majority
    Failed,
    /// Proposal executed successfully
    Executed,
    /// Proposal cancelled by proposer
    Cancelled,
    /// Proposal expired before reaching quorum
    Expired,
}

// ============================================================================
// Celtic Language Types
// ============================================================================

/// Celtic language identifiers
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum CelticLanguage {
    /// Irish (Gaeilge)
    #[serde(rename = "ga")]
    Irish,
    /// Scottish Gaelic (Gàidhlig)
    #[serde(rename = "gd")]
    ScottishGaelic,
    /// Welsh (Cymraeg)
    #[serde(rename = "cy")]
    Welsh,
    /// Manx (Gaelg)
    #[serde(rename = "gv")]
    Manx,
    /// Cornish (Kernewek)
    #[serde(rename = "kw")]
    Cornish,
    /// Breton (Brezhoneg)
    #[serde(rename = "br")]
    Breton,
}

/// Irish dialect variants
#[derive(Debug, Clone, Copy, PartialEq, Eq, Default, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum IrishDialect {
    /// Connacht Irish (Gaeilge Chonnacht)
    Connacht,
    /// Munster Irish (Gaeilge na Mumhan)
    Munster,
    /// Ulster Irish (Gaeilge Uladh)
    Ulster,
    /// Standard Irish (An Caighdeán Oifigiúil)
    #[default]
    Standard,
}

// ============================================================================
// Game Zone Types
// ============================================================================

/// Celtic region zones in the game world
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum GameZone {
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

/// Wallet chain identifier
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum WalletChain {
    /// Ethereum (and L2s like Base)
    Ethereum,
    /// Solana
    Solana,
}

/// On-chain synchronization status for game items
#[derive(Debug, Clone, Copy, PartialEq, Eq, Default, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum OnChainStatus {
    /// Item exists only in SpacetimeDB
    #[default]
    OffChain,
    /// Mint transaction submitted, awaiting confirmation
    Pending,
    /// Successfully minted on-chain
    Synced,
    /// Withdrawn from game to user wallet
    Withdrawn,
}

/// Celtic clan identifier
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum ClanId {
    /// Tuatha Dé Danann - skilled in arts and magic
    TuathaDeDanann,
    /// Fir Bolg - warriors and farmers
    FirBolg,
    /// Fomorians - chaotic sea giants
    Fomorians,
    /// Milesians - children of Míl Espáine
    Milesians,
}

/// Game item types
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ItemType {
    /// Weapons (swords, spears, slings)
    Weapon,
    /// Armor (shields, helms, cloaks)
    Armor,
    /// Magical artifacts
    Artifact,
    /// Consumables (potions, food)
    Consumable,
    /// Quest items
    Quest,
    /// Crafting materials
    Material,
}

/// Celtic art style for asset generation
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum CelticStyle {
    /// Swirling curves, S-curves, plant motifs (Iron Age)
    LaTene,
    /// Linear inscriptions, standing stones
    Ogham,
    /// Interlaced patterns, endless loops
    Knotwork,
    /// Stylized animal forms
    Zoomorphic,
    /// Spiral patterns
    Spiral,
}

/// Position in 3D space
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct Position {
    pub x: f32,
    pub y: f32,
    pub z: f32,
}

impl Position {
    pub fn new(x: f32, y: f32, z: f32) -> Self {
        Self { x, y, z }
    }

    /// Calculate region bucket for spatial indexing
    /// Buckets are 100x100 unit squares
    pub fn region_bucket(&self) -> i64 {
        let bx = (self.x / 100.0).floor() as i64;
        let bz = (self.z / 100.0).floor() as i64;
        // Cantor pairing function for unique bucket ID
        ((bx + bz) * (bx + bz + 1) / 2) + bz
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_region_bucket() {
        let pos = Position::new(150.0, 0.0, 250.0);
        let bucket = pos.region_bucket();
        assert!(bucket > 0);
    }

    #[test]
    fn test_onchain_status_default() {
        let status = OnChainStatus::default();
        assert_eq!(status, OnChainStatus::OffChain);
    }
}
