//! Celtic NFT - Metaplex Core Dynamic NFTs
//!
//! Dynamic NFT collections for Celtic game assets:
//! - Evolving character portraits
//! - Clan heraldry with attribute updates
//! - Territory ownership deeds
//! - Achievement badges
//!
//! Uses Metaplex Core for:
//! - Lower rent costs
//! - Plugin system for attributes
//! - Collection-level royalties
//!
//! Build: anchor build
//! Deploy: anchor deploy --provider.cluster devnet

use anchor_lang::prelude::*;
use mpl_core::instructions::{
    CreateV1CpiBuilder, UpdateV1CpiBuilder, TransferV1CpiBuilder,
};
use solana_program::pubkey;

/// Metaplex Core program ID
pub const MPL_CORE_ID: Pubkey = pubkey!("CoREENxT6tW1HoK8ypY1SxRMZTcVPm7R94rH4PZNhX7d");

declare_id!("CELTicNFT11111111111111111111111111111111");

/// Collection seeds
pub const COLLECTION_SEED: &[u8] = b"celtic_collection";
pub const CHARACTER_COLLECTION_SEED: &[u8] = b"characters";
pub const TERRITORY_COLLECTION_SEED: &[u8] = b"territories";
pub const ACHIEVEMENT_COLLECTION_SEED: &[u8] = b"achievements";

#[program]
pub mod celtic_nft {
    use super::*;

    /// Initialize the Celtic NFT program configuration
    pub fn initialize(
        ctx: Context<Initialize>,
        royalty_bps: u16,
        treasury: Pubkey,
    ) -> Result<()> {
        require!(royalty_bps <= 1000, CelticNftError::RoyaltyTooHigh);

        let config = &mut ctx.accounts.config;
        config.authority = ctx.accounts.authority.key();
        config.royalty_bps = royalty_bps;
        config.treasury = treasury;
        config.total_collections = 0;
        config.total_nfts_minted = 0;
        config.paused = false;
        config.bump = ctx.bumps.config;

        emit!(ConfigInitialized {
            authority: config.authority,
            royalty_bps,
            treasury,
        });

        Ok(())
    }

    /// Create a new NFT collection using Metaplex Core
    pub fn create_collection(
        ctx: Context<CreateCollection>,
        collection_type: CollectionType,
        name: String,
        uri: String,
    ) -> Result<()> {
        require!(!ctx.accounts.config.paused, CelticNftError::ProgramPaused);
        require!(name.len() <= 32, CelticNftError::NameTooLong);
        require!(uri.len() <= 200, CelticNftError::UriTooLong);

        // Get account infos and bump before mutable borrows
        let config_bump = ctx.accounts.config.bump;
        let mpl_core_program_info = ctx.accounts.mpl_core_program.to_account_info();
        let collection_info_account = ctx.accounts.collection.to_account_info();
        let payer_info = ctx.accounts.payer.to_account_info();
        let config_info = ctx.accounts.config.to_account_info();
        let max_supply = match collection_type {
            CollectionType::Characters => 10_000,
            CollectionType::Territories => 1_000,
            CollectionType::Achievements => 100_000,
            CollectionType::ClanHeraldry => 500,
            // Celtic creatures for SpeedRunEthereum Challenge 0
            CollectionType::Creatures => 50_000,
        };

        let collection_info = &mut ctx.accounts.collection_info;
        collection_info.collection_type = collection_type;
        collection_info.collection_address = ctx.accounts.collection.key();
        collection_info.name = name.clone();
        collection_info.uri = uri.clone();
        collection_info.total_minted = 0;
        collection_info.max_supply = max_supply;
        collection_info.bump = ctx.bumps.collection_info;

        // Update global stats
        ctx.accounts.config.total_collections = ctx.accounts.config.total_collections
            .checked_add(1)
            .ok_or(CelticNftError::Overflow)?;

        // Create Metaplex Core collection via CPI
        CreateV1CpiBuilder::new(&mpl_core_program_info)
            .asset(&collection_info_account)
            .payer(&payer_info)
            .authority(Some(&config_info))
            .owner(Some(&config_info))
            .name(name.clone())
            .uri(uri.clone())
            .invoke_signed(&[&[
                b"celtic_nft_config",
                &[config_bump],
            ]])?;

        emit!(CollectionCreated {
            collection: ctx.accounts.collection.key(),
            collection_type,
            name,
            max_supply,
        });

        Ok(())
    }

    /// Mint a Celtic character NFT
    pub fn mint_character(
        ctx: Context<MintNft>,
        name: String,
        uri: String,
        clan: ClanId,
        character_class: CharacterClass,
    ) -> Result<()> {
        require!(!ctx.accounts.config.paused, CelticNftError::ProgramPaused);
        require!(
            ctx.accounts.collection_info.collection_type == CollectionType::Characters,
            CelticNftError::WrongCollectionType
        );
        require!(
            ctx.accounts.collection_info.total_minted < ctx.accounts.collection_info.max_supply,
            CelticNftError::MaxSupplyReached
        );

        // Get account infos and bump before mutable borrows
        let config_bump = ctx.accounts.config.bump;
        let mpl_core_program_info = ctx.accounts.mpl_core_program.to_account_info();
        let asset_info = ctx.accounts.asset.to_account_info();
        let collection_info_account = ctx.accounts.collection.to_account_info();
        let payer_info = ctx.accounts.payer.to_account_info();
        let config_info = ctx.accounts.config.to_account_info();
        let owner_info = ctx.accounts.owner.to_account_info();

        // Create character metadata
        let character_data = &mut ctx.accounts.nft_data;
        character_data.asset = ctx.accounts.asset.key();
        character_data.collection = ctx.accounts.collection.key();
        character_data.owner = ctx.accounts.owner.key();
        character_data.nft_type = NftType::Character {
            clan,
            character_class,
            level: 1,
            experience: 0,
        };
        character_data.created_at = Clock::get()?.unix_timestamp;
        character_data.last_updated = Clock::get()?.unix_timestamp;
        character_data.bump = ctx.bumps.nft_data;

        // Update collection stats
        ctx.accounts.collection_info.total_minted = ctx.accounts.collection_info.total_minted
            .checked_add(1)
            .ok_or(CelticNftError::Overflow)?;

        // Update global stats
        ctx.accounts.config.total_nfts_minted = ctx.accounts.config.total_nfts_minted
            .checked_add(1)
            .ok_or(CelticNftError::Overflow)?;

        // Mint via Metaplex Core
        CreateV1CpiBuilder::new(&mpl_core_program_info)
            .asset(&asset_info)
            .collection(Some(&collection_info_account))
            .payer(&payer_info)
            .authority(Some(&config_info))
            .owner(Some(&owner_info))
            .name(name.clone())
            .uri(uri.clone())
            .invoke_signed(&[&[
                b"celtic_nft_config",
                &[config_bump],
            ]])?;

        emit!(NftMinted {
            asset: ctx.accounts.asset.key(),
            collection: ctx.accounts.collection.key(),
            owner: ctx.accounts.owner.key(),
            name,
        });

        Ok(())
    }

    /// Mint a territory deed NFT
    pub fn mint_territory(
        ctx: Context<MintNft>,
        name: String,
        uri: String,
        region_x: i32,
        region_z: i32,
        terrain_type: TerrainType,
    ) -> Result<()> {
        require!(!ctx.accounts.config.paused, CelticNftError::ProgramPaused);
        require!(
            ctx.accounts.collection_info.collection_type == CollectionType::Territories,
            CelticNftError::WrongCollectionType
        );
        require!(
            ctx.accounts.collection_info.total_minted < ctx.accounts.collection_info.max_supply,
            CelticNftError::MaxSupplyReached
        );

        // Get account infos and bump before mutable borrows
        let config_bump = ctx.accounts.config.bump;
        let mpl_core_program_info = ctx.accounts.mpl_core_program.to_account_info();
        let asset_info = ctx.accounts.asset.to_account_info();
        let collection_info_account = ctx.accounts.collection.to_account_info();
        let payer_info = ctx.accounts.payer.to_account_info();
        let config_info = ctx.accounts.config.to_account_info();
        let owner_info = ctx.accounts.owner.to_account_info();

        // Create territory metadata
        let territory_data = &mut ctx.accounts.nft_data;
        territory_data.asset = ctx.accounts.asset.key();
        territory_data.collection = ctx.accounts.collection.key();
        territory_data.owner = ctx.accounts.owner.key();
        territory_data.nft_type = NftType::Territory {
            region_x,
            region_z,
            terrain_type,
            development_level: 0,
            resource_bonus: 100,
        };
        territory_data.created_at = Clock::get()?.unix_timestamp;
        territory_data.last_updated = Clock::get()?.unix_timestamp;
        territory_data.bump = ctx.bumps.nft_data;

        // Update stats
        ctx.accounts.collection_info.total_minted = ctx.accounts.collection_info.total_minted
            .checked_add(1)
            .ok_or(CelticNftError::Overflow)?;

        ctx.accounts.config.total_nfts_minted = ctx.accounts.config.total_nfts_minted
            .checked_add(1)
            .ok_or(CelticNftError::Overflow)?;

        // Mint via Metaplex Core
        CreateV1CpiBuilder::new(&mpl_core_program_info)
            .asset(&asset_info)
            .collection(Some(&collection_info_account))
            .payer(&payer_info)
            .authority(Some(&config_info))
            .owner(Some(&owner_info))
            .name(name.clone())
            .uri(uri.clone())
            .invoke_signed(&[&[
                b"celtic_nft_config",
                &[config_bump],
            ]])?;

        emit!(TerritoryMinted {
            asset: ctx.accounts.asset.key(),
            region_x,
            region_z,
            terrain_type,
            owner: ctx.accounts.owner.key(),
        });

        Ok(())
    }

    /// Mint a Celtic creature NFT (SpeedRunEthereum Challenge 0)
    /// Parallel to Ethereum CelticCreatureNFT.sol mint function
    pub fn mint_creature(
        ctx: Context<MintNft>,
        name: String,
        uri: String,
        tradition: CelticTradition,
        creature_type: CreatureCategory,
        strength: u8,
        wisdom: u8,
        magic: u8,
        special_ability: String,
    ) -> Result<()> {
        require!(!ctx.accounts.config.paused, CelticNftError::ProgramPaused);
        require!(
            ctx.accounts.collection_info.collection_type == CollectionType::Creatures,
            CelticNftError::WrongCollectionType
        );
        require!(
            ctx.accounts.collection_info.total_minted < ctx.accounts.collection_info.max_supply,
            CelticNftError::MaxSupplyReached
        );
        require!(strength <= 100, CelticNftError::AttributeTooHigh);
        require!(wisdom <= 100, CelticNftError::AttributeTooHigh);
        require!(magic <= 100, CelticNftError::AttributeTooHigh);
        require!(special_ability.len() <= 32, CelticNftError::NameTooLong);

        // Calculate rarity based on total attributes (mirrors Ethereum logic)
        let total: u16 = strength as u16 + wisdom as u16 + magic as u16;
        let rarity = if total >= 270 {
            Rarity::Legendary
        } else if total >= 220 {
            Rarity::Epic
        } else if total >= 150 {
            Rarity::Rare
        } else if total >= 100 {
            Rarity::Uncommon
        } else {
            Rarity::Common
        };

        // Get account infos and bump before mutable borrows
        let config_bump = ctx.accounts.config.bump;
        let mpl_core_program_info = ctx.accounts.mpl_core_program.to_account_info();
        let asset_info = ctx.accounts.asset.to_account_info();
        let collection_info_account = ctx.accounts.collection.to_account_info();
        let payer_info = ctx.accounts.payer.to_account_info();
        let config_info = ctx.accounts.config.to_account_info();
        let owner_info = ctx.accounts.owner.to_account_info();

        // Create creature metadata
        let creature_data = &mut ctx.accounts.nft_data;
        creature_data.asset = ctx.accounts.asset.key();
        creature_data.collection = ctx.accounts.collection.key();
        creature_data.owner = ctx.accounts.owner.key();
        creature_data.nft_type = NftType::Creature {
            tradition,
            creature_type,
            strength,
            wisdom,
            magic,
            rarity,
        };
        creature_data.created_at = Clock::get()?.unix_timestamp;
        creature_data.last_updated = Clock::get()?.unix_timestamp;
        creature_data.bump = ctx.bumps.nft_data;

        // Update collection stats
        ctx.accounts.collection_info.total_minted = ctx.accounts.collection_info.total_minted
            .checked_add(1)
            .ok_or(CelticNftError::Overflow)?;

        // Update global stats
        ctx.accounts.config.total_nfts_minted = ctx.accounts.config.total_nfts_minted
            .checked_add(1)
            .ok_or(CelticNftError::Overflow)?;

        // Mint via Metaplex Core
        CreateV1CpiBuilder::new(&mpl_core_program_info)
            .asset(&asset_info)
            .collection(Some(&collection_info_account))
            .payer(&payer_info)
            .authority(Some(&config_info))
            .owner(Some(&owner_info))
            .name(name.clone())
            .uri(uri.clone())
            .invoke_signed(&[&[
                b"celtic_nft_config",
                &[config_bump],
            ]])?;

        emit!(CreatureMinted {
            asset: ctx.accounts.asset.key(),
            collection: ctx.accounts.collection.key(),
            owner: ctx.accounts.owner.key(),
            name,
            tradition,
            creature_type,
            rarity,
            strength,
            wisdom,
            magic,
            special_ability,
        });

        Ok(())
    }

    /// Update character NFT attributes (level up, experience, etc.)
    pub fn update_character(
        ctx: Context<UpdateNft>,
        new_level: Option<u8>,
        experience_gained: Option<u64>,
        new_uri: Option<String>,
    ) -> Result<()> {
        let nft_data = &mut ctx.accounts.nft_data;

        match &mut nft_data.nft_type {
            NftType::Character { level, experience, .. } => {
                if let Some(exp) = experience_gained {
                    *experience = experience.checked_add(exp)
                        .ok_or(CelticNftError::Overflow)?;
                }
                if let Some(lvl) = new_level {
                    require!(lvl > *level, CelticNftError::InvalidLevelUpdate);
                    *level = lvl;
                }
            }
            _ => return Err(CelticNftError::WrongNftType.into()),
        }

        nft_data.last_updated = Clock::get()?.unix_timestamp;

        // Update on-chain metadata if URI changed
        if let Some(uri) = new_uri {
            let config = &ctx.accounts.config;
            UpdateV1CpiBuilder::new(&ctx.accounts.mpl_core_program.to_account_info())
                .asset(&ctx.accounts.asset.to_account_info())
                .payer(&ctx.accounts.payer.to_account_info())
                .authority(Some(&ctx.accounts.config.to_account_info()))
                .new_uri(uri)
                .invoke_signed(&[&[
                    b"celtic_nft_config",
                    &[config.bump],
                ]])?;
        }

        emit!(NftUpdated {
            asset: ctx.accounts.asset.key(),
            nft_type: nft_data.nft_type.clone(),
        });

        Ok(())
    }

    /// Update territory NFT (development, conquests)
    pub fn update_territory(
        ctx: Context<UpdateNft>,
        new_development_level: Option<u8>,
        new_resource_bonus: Option<u16>,
        new_uri: Option<String>,
    ) -> Result<()> {
        let nft_data = &mut ctx.accounts.nft_data;

        match &mut nft_data.nft_type {
            NftType::Territory { development_level, resource_bonus, .. } => {
                if let Some(dev) = new_development_level {
                    *development_level = dev;
                }
                if let Some(bonus) = new_resource_bonus {
                    *resource_bonus = bonus;
                }
            }
            _ => return Err(CelticNftError::WrongNftType.into()),
        }

        nft_data.last_updated = Clock::get()?.unix_timestamp;

        if let Some(uri) = new_uri {
            let config = &ctx.accounts.config;
            UpdateV1CpiBuilder::new(&ctx.accounts.mpl_core_program.to_account_info())
                .asset(&ctx.accounts.asset.to_account_info())
                .payer(&ctx.accounts.payer.to_account_info())
                .authority(Some(&ctx.accounts.config.to_account_info()))
                .new_uri(uri)
                .invoke_signed(&[&[
                    b"celtic_nft_config",
                    &[config.bump],
                ]])?;
        }

        emit!(NftUpdated {
            asset: ctx.accounts.asset.key(),
            nft_type: nft_data.nft_type.clone(),
        });

        Ok(())
    }

    /// Pause/unpause minting (admin only)
    pub fn set_paused(ctx: Context<AdminOnly>, paused: bool) -> Result<()> {
        ctx.accounts.config.paused = paused;
        Ok(())
    }

    // ========================================================================
    // Relayer Instructions
    // ========================================================================

    /// Add a trusted relayer that can mint on behalf of players
    pub fn add_relayer(ctx: Context<ManageRelayer>, relayer: Pubkey) -> Result<()> {
        let relayer_info = &mut ctx.accounts.relayer_info;
        relayer_info.relayer = relayer;
        relayer_info.authority = ctx.accounts.config.authority;
        relayer_info.total_mints = 0;
        relayer_info.enabled = true;
        relayer_info.bump = ctx.bumps.relayer_info;

        emit!(RelayerAdded {
            relayer,
            authority: ctx.accounts.config.authority,
        });

        Ok(())
    }

    /// Remove/disable a relayer
    pub fn disable_relayer(ctx: Context<DisableRelayer>) -> Result<()> {
        ctx.accounts.relayer_info.enabled = false;

        emit!(RelayerDisabled {
            relayer: ctx.accounts.relayer_info.relayer,
        });

        Ok(())
    }

    /// Mint character NFT via relayer (gasless for player)
    /// The relayer pays transaction fees, player receives the NFT
    pub fn mint_character_with_relayer(
        ctx: Context<MintWithRelayer>,
        name: String,
        uri: String,
        clan: ClanId,
        character_class: CharacterClass,
        spacetimedb_mint_id: u64,
    ) -> Result<()> {
        require!(!ctx.accounts.config.paused, CelticNftError::ProgramPaused);
        require!(ctx.accounts.relayer_info.enabled, CelticNftError::RelayerDisabled);
        require!(
            ctx.accounts.collection_info.collection_type == CollectionType::Characters,
            CelticNftError::WrongCollectionType
        );
        require!(
            ctx.accounts.collection_info.total_minted < ctx.accounts.collection_info.max_supply,
            CelticNftError::MaxSupplyReached
        );

        // Get account infos and bump before mutable borrows
        let config_bump = ctx.accounts.config.bump;
        let mpl_core_program_info = ctx.accounts.mpl_core_program.to_account_info();
        let asset_info = ctx.accounts.asset.to_account_info();
        let collection_info_account = ctx.accounts.collection.to_account_info();
        let relayer_info_account = ctx.accounts.relayer.to_account_info();
        let config_info = ctx.accounts.config.to_account_info();

        // Create character metadata
        let character_data = &mut ctx.accounts.nft_data;
        character_data.asset = ctx.accounts.asset.key();
        character_data.collection = ctx.accounts.collection.key();
        character_data.owner = ctx.accounts.owner.key();
        character_data.nft_type = NftType::Character {
            clan,
            character_class,
            level: 1,
            experience: 0,
        };
        character_data.created_at = Clock::get()?.unix_timestamp;
        character_data.last_updated = Clock::get()?.unix_timestamp;
        character_data.bump = ctx.bumps.nft_data;

        // Initialize custody tracking
        let custody = &mut ctx.accounts.custody;
        custody.asset = ctx.accounts.asset.key();
        custody.game_owner = ctx.accounts.owner.key();
        custody.wallet_owner = None; // In-game custody initially
        custody.custody_type = CustodyType::InGame;
        custody.deposited_at = Some(Clock::get()?.unix_timestamp);
        custody.withdrawn_at = None;
        custody.bump = ctx.bumps.custody;

        // Update collection stats
        let collection_info = &mut ctx.accounts.collection_info;
        collection_info.total_minted = collection_info.total_minted
            .checked_add(1)
            .ok_or(CelticNftError::Overflow)?;

        // Update global stats
        ctx.accounts.config.total_nfts_minted = ctx.accounts.config.total_nfts_minted
            .checked_add(1)
            .ok_or(CelticNftError::Overflow)?;

        // Update relayer stats
        ctx.accounts.relayer_info.total_mints = ctx.accounts.relayer_info.total_mints
            .checked_add(1)
            .ok_or(CelticNftError::Overflow)?;

        // Mint via Metaplex Core - config is the authority
        CreateV1CpiBuilder::new(&mpl_core_program_info)
            .asset(&asset_info)
            .collection(Some(&collection_info_account))
            .payer(&relayer_info_account)
            .authority(Some(&config_info))
            .owner(Some(&config_info)) // Config holds custody
            .name(name.clone())
            .uri(uri.clone())
            .invoke_signed(&[&[
                b"celtic_nft_config",
                &[config_bump],
            ]])?;

        emit!(RelayerMinted {
            asset: ctx.accounts.asset.key(),
            collection: ctx.accounts.collection.key(),
            owner: ctx.accounts.owner.key(),
            relayer: ctx.accounts.relayer.key(),
            spacetimedb_mint_id,
            name,
        });

        Ok(())
    }

    /// Mint territory NFT via relayer (gasless for player)
    pub fn mint_territory_with_relayer(
        ctx: Context<MintWithRelayer>,
        name: String,
        uri: String,
        region_x: i32,
        region_z: i32,
        terrain_type: TerrainType,
        spacetimedb_mint_id: u64,
    ) -> Result<()> {
        require!(!ctx.accounts.config.paused, CelticNftError::ProgramPaused);
        require!(ctx.accounts.relayer_info.enabled, CelticNftError::RelayerDisabled);
        require!(
            ctx.accounts.collection_info.collection_type == CollectionType::Territories,
            CelticNftError::WrongCollectionType
        );
        require!(
            ctx.accounts.collection_info.total_minted < ctx.accounts.collection_info.max_supply,
            CelticNftError::MaxSupplyReached
        );

        // Get account infos and bump before mutable borrows
        let config_bump = ctx.accounts.config.bump;
        let mpl_core_program_info = ctx.accounts.mpl_core_program.to_account_info();
        let asset_info = ctx.accounts.asset.to_account_info();
        let collection_info_account = ctx.accounts.collection.to_account_info();
        let relayer_info_account = ctx.accounts.relayer.to_account_info();
        let config_info = ctx.accounts.config.to_account_info();

        // Create territory metadata
        let territory_data = &mut ctx.accounts.nft_data;
        territory_data.asset = ctx.accounts.asset.key();
        territory_data.collection = ctx.accounts.collection.key();
        territory_data.owner = ctx.accounts.owner.key();
        territory_data.nft_type = NftType::Territory {
            region_x,
            region_z,
            terrain_type,
            development_level: 0,
            resource_bonus: 100,
        };
        territory_data.created_at = Clock::get()?.unix_timestamp;
        territory_data.last_updated = Clock::get()?.unix_timestamp;
        territory_data.bump = ctx.bumps.nft_data;

        // Initialize custody tracking
        let custody = &mut ctx.accounts.custody;
        custody.asset = ctx.accounts.asset.key();
        custody.game_owner = ctx.accounts.owner.key();
        custody.wallet_owner = None;
        custody.custody_type = CustodyType::InGame;
        custody.deposited_at = Some(Clock::get()?.unix_timestamp);
        custody.withdrawn_at = None;
        custody.bump = ctx.bumps.custody;

        // Update stats
        let collection_info = &mut ctx.accounts.collection_info;
        collection_info.total_minted = collection_info.total_minted
            .checked_add(1)
            .ok_or(CelticNftError::Overflow)?;

        ctx.accounts.config.total_nfts_minted = ctx.accounts.config.total_nfts_minted
            .checked_add(1)
            .ok_or(CelticNftError::Overflow)?;

        ctx.accounts.relayer_info.total_mints = ctx.accounts.relayer_info.total_mints
            .checked_add(1)
            .ok_or(CelticNftError::Overflow)?;

        // Mint via Metaplex Core
        CreateV1CpiBuilder::new(&mpl_core_program_info)
            .asset(&asset_info)
            .collection(Some(&collection_info_account))
            .payer(&relayer_info_account)
            .authority(Some(&config_info))
            .owner(Some(&config_info))
            .name(name.clone())
            .uri(uri.clone())
            .invoke_signed(&[&[
                b"celtic_nft_config",
                &[config_bump],
            ]])?;

        emit!(RelayerMinted {
            asset: ctx.accounts.asset.key(),
            collection: ctx.accounts.collection.key(),
            owner: ctx.accounts.owner.key(),
            relayer: ctx.accounts.relayer.key(),
            spacetimedb_mint_id,
            name,
        });

        Ok(())
    }

    /// Withdraw NFT from in-game custody to player's wallet
    /// Player must sign to prove ownership
    pub fn withdraw_to_wallet(ctx: Context<WithdrawToWallet>) -> Result<()> {
        require!(
            ctx.accounts.custody.custody_type == CustodyType::InGame,
            CelticNftError::NotInGameCustody
        );
        require!(
            ctx.accounts.custody.game_owner == ctx.accounts.owner.key(),
            CelticNftError::NotOwner
        );

        // Get account infos before mutable borrows
        let config_bump = ctx.accounts.config.bump;
        let mpl_core_program_info = ctx.accounts.mpl_core_program.to_account_info();
        let asset_info = ctx.accounts.asset.to_account_info();
        let payer_info = ctx.accounts.payer.to_account_info();
        let config_info = ctx.accounts.config.to_account_info();
        let owner_info = ctx.accounts.owner.to_account_info();

        // Update custody state
        let custody = &mut ctx.accounts.custody;
        custody.custody_type = CustodyType::Wallet;
        custody.wallet_owner = Some(ctx.accounts.owner.key());
        custody.withdrawn_at = Some(Clock::get()?.unix_timestamp);
        custody.deposited_at = None;

        // Transfer NFT ownership from config PDA to player wallet
        TransferV1CpiBuilder::new(&mpl_core_program_info)
            .asset(&asset_info)
            .payer(&payer_info)
            .authority(Some(&config_info))
            .new_owner(&owner_info)
            .invoke_signed(&[&[
                b"celtic_nft_config",
                &[config_bump],
            ]])?;

        emit!(NftWithdrawn {
            asset: ctx.accounts.asset.key(),
            owner: ctx.accounts.owner.key(),
            timestamp: Clock::get()?.unix_timestamp,
        });

        Ok(())
    }

    /// Deposit NFT from player's wallet back to in-game custody
    /// Player must sign to authorize the deposit
    pub fn deposit_from_wallet(ctx: Context<DepositFromWallet>) -> Result<()> {
        require!(
            ctx.accounts.custody.custody_type == CustodyType::Wallet,
            CelticNftError::NotWalletCustody
        );
        require!(
            ctx.accounts.custody.wallet_owner == Some(ctx.accounts.owner.key()),
            CelticNftError::NotOwner
        );

        // Get account infos before mutable borrows
        let mpl_core_program_info = ctx.accounts.mpl_core_program.to_account_info();
        let asset_info = ctx.accounts.asset.to_account_info();
        let payer_info = ctx.accounts.payer.to_account_info();
        let config_info = ctx.accounts.config.to_account_info();
        let owner_info = ctx.accounts.owner.to_account_info();

        // Update custody state
        let custody = &mut ctx.accounts.custody;
        custody.custody_type = CustodyType::InGame;
        custody.wallet_owner = None;
        custody.deposited_at = Some(Clock::get()?.unix_timestamp);
        custody.withdrawn_at = None;

        // Transfer NFT ownership from player wallet back to config PDA
        TransferV1CpiBuilder::new(&mpl_core_program_info)
            .asset(&asset_info)
            .payer(&payer_info)
            .authority(Some(&owner_info))
            .new_owner(&config_info)
            .invoke()?;

        emit!(NftDeposited {
            asset: ctx.accounts.asset.key(),
            owner: ctx.accounts.owner.key(),
            timestamp: Clock::get()?.unix_timestamp,
        });

        Ok(())
    }
}

// ============================================================================
// Account Structures
// ============================================================================

#[account]
#[derive(InitSpace)]
pub struct NftConfig {
    /// Program authority
    pub authority: Pubkey,
    /// Royalty percentage in basis points
    pub royalty_bps: u16,
    /// Treasury for royalties
    pub treasury: Pubkey,
    /// Total collections created
    pub total_collections: u32,
    /// Total NFTs minted across all collections
    pub total_nfts_minted: u64,
    /// Emergency pause
    pub paused: bool,
    /// PDA bump
    pub bump: u8,
}

#[account]
#[derive(InitSpace)]
pub struct CollectionInfo {
    /// Type of collection
    pub collection_type: CollectionType,
    /// Metaplex Core collection address
    pub collection_address: Pubkey,
    /// Collection name
    #[max_len(32)]
    pub name: String,
    /// Metadata URI
    #[max_len(200)]
    pub uri: String,
    /// Number minted in this collection
    pub total_minted: u32,
    /// Maximum supply (0 = unlimited)
    pub max_supply: u32,
    /// PDA bump
    pub bump: u8,
}

#[account]
#[derive(InitSpace)]
pub struct NftData {
    /// Metaplex Core asset address
    pub asset: Pubkey,
    /// Parent collection
    pub collection: Pubkey,
    /// Current owner
    pub owner: Pubkey,
    /// Type-specific data
    pub nft_type: NftType,
    /// Creation timestamp
    pub created_at: i64,
    /// Last update timestamp
    pub last_updated: i64,
    /// PDA bump
    pub bump: u8,
}

#[account]
#[derive(InitSpace)]
pub struct RelayerInfo {
    /// Relayer public key
    pub relayer: Pubkey,
    /// Authority that added this relayer
    pub authority: Pubkey,
    /// Total mints by this relayer
    pub total_mints: u64,
    /// Whether relayer is enabled
    pub enabled: bool,
    /// PDA bump
    pub bump: u8,
}

#[account]
#[derive(InitSpace)]
pub struct NftCustody {
    /// Asset this custody record tracks
    pub asset: Pubkey,
    /// In-game owner (SpacetimeDB player ID mapping)
    pub game_owner: Pubkey,
    /// Wallet owner (when withdrawn)
    pub wallet_owner: Option<Pubkey>,
    /// Current custody type
    pub custody_type: CustodyType,
    /// Timestamp when deposited to game
    pub deposited_at: Option<i64>,
    /// Timestamp when withdrawn to wallet
    pub withdrawn_at: Option<i64>,
    /// PDA bump
    pub bump: u8,
}

// ============================================================================
// Context Structures
// ============================================================================

#[derive(Accounts)]
pub struct Initialize<'info> {
    #[account(
        init,
        payer = authority,
        space = 8 + NftConfig::INIT_SPACE,
        seeds = [b"celtic_nft_config"],
        bump,
    )]
    pub config: Account<'info, NftConfig>,

    #[account(mut)]
    pub authority: Signer<'info>,

    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
#[instruction(collection_type: CollectionType)]
pub struct CreateCollection<'info> {
    #[account(
        mut,
        seeds = [b"celtic_nft_config"],
        bump = config.bump,
    )]
    pub config: Account<'info, NftConfig>,

    #[account(
        init,
        payer = payer,
        space = 8 + CollectionInfo::INIT_SPACE,
        seeds = [b"collection_info", collection.key().as_ref()],
        bump,
    )]
    pub collection_info: Account<'info, CollectionInfo>,

    /// CHECK: Metaplex Core collection account
    #[account(mut)]
    pub collection: Signer<'info>,

    #[account(mut)]
    pub payer: Signer<'info>,

    #[account(
        constraint = authority.key() == config.authority @ CelticNftError::Unauthorized
    )]
    pub authority: Signer<'info>,

    /// CHECK: Metaplex Core program
    #[account(address = MPL_CORE_ID)]
    pub mpl_core_program: UncheckedAccount<'info>,

    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct MintNft<'info> {
    #[account(
        mut,
        seeds = [b"celtic_nft_config"],
        bump = config.bump,
    )]
    pub config: Account<'info, NftConfig>,

    #[account(
        mut,
        seeds = [b"collection_info", collection.key().as_ref()],
        bump = collection_info.bump,
    )]
    pub collection_info: Account<'info, CollectionInfo>,

    /// CHECK: Metaplex Core collection
    #[account(mut)]
    pub collection: UncheckedAccount<'info>,

    /// CHECK: New Metaplex Core asset
    #[account(mut)]
    pub asset: Signer<'info>,

    #[account(
        init,
        payer = payer,
        space = 8 + NftData::INIT_SPACE,
        seeds = [b"nft_data", asset.key().as_ref()],
        bump,
    )]
    pub nft_data: Account<'info, NftData>,

    /// CHECK: NFT recipient
    pub owner: UncheckedAccount<'info>,

    #[account(mut)]
    pub payer: Signer<'info>,

    /// CHECK: Metaplex Core program
    #[account(address = MPL_CORE_ID)]
    pub mpl_core_program: UncheckedAccount<'info>,

    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct UpdateNft<'info> {
    #[account(
        seeds = [b"celtic_nft_config"],
        bump = config.bump,
    )]
    pub config: Account<'info, NftConfig>,

    #[account(
        mut,
        seeds = [b"nft_data", asset.key().as_ref()],
        bump = nft_data.bump,
    )]
    pub nft_data: Account<'info, NftData>,

    /// CHECK: Metaplex Core asset
    #[account(mut)]
    pub asset: UncheckedAccount<'info>,

    #[account(mut)]
    pub payer: Signer<'info>,

    #[account(
        constraint = authority.key() == config.authority @ CelticNftError::Unauthorized
    )]
    pub authority: Signer<'info>,

    /// CHECK: Metaplex Core program
    #[account(address = MPL_CORE_ID)]
    pub mpl_core_program: UncheckedAccount<'info>,
}

#[derive(Accounts)]
pub struct AdminOnly<'info> {
    #[account(
        mut,
        seeds = [b"celtic_nft_config"],
        bump = config.bump,
    )]
    pub config: Account<'info, NftConfig>,

    #[account(
        constraint = authority.key() == config.authority @ CelticNftError::Unauthorized
    )]
    pub authority: Signer<'info>,
}

// ============================================================================
// Relayer Context Structures
// ============================================================================

#[derive(Accounts)]
#[instruction(relayer: Pubkey)]
pub struct ManageRelayer<'info> {
    #[account(
        mut,
        seeds = [b"celtic_nft_config"],
        bump = config.bump,
    )]
    pub config: Account<'info, NftConfig>,

    #[account(
        init,
        payer = payer,
        space = 8 + RelayerInfo::INIT_SPACE,
        seeds = [b"relayer", relayer.as_ref()],
        bump,
    )]
    pub relayer_info: Account<'info, RelayerInfo>,

    #[account(mut)]
    pub payer: Signer<'info>,

    #[account(
        constraint = authority.key() == config.authority @ CelticNftError::Unauthorized
    )]
    pub authority: Signer<'info>,

    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct DisableRelayer<'info> {
    #[account(
        seeds = [b"celtic_nft_config"],
        bump = config.bump,
    )]
    pub config: Account<'info, NftConfig>,

    #[account(
        mut,
        seeds = [b"relayer", relayer_info.relayer.as_ref()],
        bump = relayer_info.bump,
    )]
    pub relayer_info: Account<'info, RelayerInfo>,

    #[account(
        constraint = authority.key() == config.authority @ CelticNftError::Unauthorized
    )]
    pub authority: Signer<'info>,
}

#[derive(Accounts)]
pub struct MintWithRelayer<'info> {
    #[account(
        mut,
        seeds = [b"celtic_nft_config"],
        bump = config.bump,
    )]
    pub config: Account<'info, NftConfig>,

    #[account(
        mut,
        seeds = [b"relayer", relayer.key().as_ref()],
        bump = relayer_info.bump,
        constraint = relayer_info.relayer == relayer.key() @ CelticNftError::Unauthorized,
    )]
    pub relayer_info: Account<'info, RelayerInfo>,

    #[account(
        mut,
        seeds = [b"collection_info", collection.key().as_ref()],
        bump = collection_info.bump,
    )]
    pub collection_info: Account<'info, CollectionInfo>,

    /// CHECK: Metaplex Core collection
    #[account(mut)]
    pub collection: UncheckedAccount<'info>,

    /// CHECK: New Metaplex Core asset
    #[account(mut)]
    pub asset: Signer<'info>,

    #[account(
        init,
        payer = relayer,
        space = 8 + NftData::INIT_SPACE,
        seeds = [b"nft_data", asset.key().as_ref()],
        bump,
    )]
    pub nft_data: Account<'info, NftData>,

    #[account(
        init,
        payer = relayer,
        space = 8 + NftCustody::INIT_SPACE,
        seeds = [b"custody", asset.key().as_ref()],
        bump,
    )]
    pub custody: Account<'info, NftCustody>,

    /// CHECK: NFT recipient (in-game owner)
    pub owner: UncheckedAccount<'info>,

    /// Relayer pays transaction fees
    #[account(mut)]
    pub relayer: Signer<'info>,

    /// CHECK: Metaplex Core program
    #[account(address = MPL_CORE_ID)]
    pub mpl_core_program: UncheckedAccount<'info>,

    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct WithdrawToWallet<'info> {
    #[account(
        seeds = [b"celtic_nft_config"],
        bump = config.bump,
    )]
    pub config: Account<'info, NftConfig>,

    #[account(
        mut,
        seeds = [b"custody", asset.key().as_ref()],
        bump = custody.bump,
    )]
    pub custody: Account<'info, NftCustody>,

    #[account(
        seeds = [b"nft_data", asset.key().as_ref()],
        bump = nft_data.bump,
    )]
    pub nft_data: Account<'info, NftData>,

    /// CHECK: Metaplex Core asset
    #[account(mut)]
    pub asset: UncheckedAccount<'info>,

    /// Owner must sign to prove ownership
    #[account(mut)]
    pub owner: Signer<'info>,

    #[account(mut)]
    pub payer: Signer<'info>,

    /// CHECK: Metaplex Core program
    #[account(address = MPL_CORE_ID)]
    pub mpl_core_program: UncheckedAccount<'info>,
}

#[derive(Accounts)]
pub struct DepositFromWallet<'info> {
    #[account(
        seeds = [b"celtic_nft_config"],
        bump = config.bump,
    )]
    pub config: Account<'info, NftConfig>,

    #[account(
        mut,
        seeds = [b"custody", asset.key().as_ref()],
        bump = custody.bump,
    )]
    pub custody: Account<'info, NftCustody>,

    #[account(
        seeds = [b"nft_data", asset.key().as_ref()],
        bump = nft_data.bump,
    )]
    pub nft_data: Account<'info, NftData>,

    /// CHECK: Metaplex Core asset
    #[account(mut)]
    pub asset: UncheckedAccount<'info>,

    /// Owner must sign to authorize deposit
    #[account(mut)]
    pub owner: Signer<'info>,

    #[account(mut)]
    pub payer: Signer<'info>,

    /// CHECK: Metaplex Core program
    #[account(address = MPL_CORE_ID)]
    pub mpl_core_program: UncheckedAccount<'info>,
}

// ============================================================================
// Types
// ============================================================================

#[derive(AnchorSerialize, AnchorDeserialize, Clone, Copy, PartialEq, Eq, InitSpace)]
pub enum CollectionType {
    Characters,
    Territories,
    Achievements,
    ClanHeraldry,
    /// Celtic mythological creatures (SpeedRunEthereum Challenge 0)
    Creatures,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, PartialEq, Eq, InitSpace)]
pub enum NftType {
    Character {
        clan: ClanId,
        character_class: CharacterClass,
        level: u8,
        experience: u64,
    },
    Territory {
        region_x: i32,
        region_z: i32,
        terrain_type: TerrainType,
        development_level: u8,
        resource_bonus: u16,
    },
    Achievement {
        achievement_id: u32,
        rarity: Rarity,
    },
    ClanHeraldry {
        clan: ClanId,
        rank: u8,
    },
    /// Celtic mythological creature (SpeedRunEthereum Challenge 0)
    /// Parallel to Ethereum CelticCreatureNFT.sol
    Creature {
        /// Celtic tradition (Irish, Welsh, Scottish)
        tradition: CelticTradition,
        /// Creature category (God, Hero, Creature, Spirit)
        creature_type: CreatureCategory,
        /// Combat attribute (0-100)
        strength: u8,
        /// Knowledge attribute (0-100)
        wisdom: u8,
        /// Magical power attribute (0-100)
        magic: u8,
        /// Creature rarity tier
        rarity: Rarity,
    },
}

/// Celtic traditions (mirrors Ethereum CelticCreatureNFT.Tradition)
#[derive(AnchorSerialize, AnchorDeserialize, Clone, Copy, PartialEq, Eq, InitSpace)]
pub enum CelticTradition {
    Irish,
    Welsh,
    Scottish,
}

/// Creature categories (mirrors Ethereum CelticCreatureNFT.CreatureType)
#[derive(AnchorSerialize, AnchorDeserialize, Clone, Copy, PartialEq, Eq, InitSpace)]
pub enum CreatureCategory {
    /// Tuatha Dé Danann, Mabinogion deities, etc.
    God,
    /// Cú Chulainn, Fionn mac Cumhaill, Taliesin, etc.
    Hero,
    /// Púca, Selkie, Afanc, etc.
    Creature,
    /// Banshee, Will-o'-wisp, Bean Nighe, etc.
    Spirit,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, Copy, PartialEq, Eq, InitSpace)]
pub enum ClanId {
    TuathaDeDanann,
    FirBolg,
    Fomorians,
    Milesians,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, Copy, PartialEq, Eq, InitSpace)]
pub enum CharacterClass {
    Druid,
    Warrior,
    Bard,
    Blacksmith,
    Merchant,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, Copy, PartialEq, Eq, InitSpace)]
pub enum TerrainType {
    Forest,
    Plains,
    Mountains,
    Coast,
    Bog,
    Sacred,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, Copy, PartialEq, Eq, InitSpace)]
pub enum Rarity {
    Common,
    Uncommon,
    Rare,
    Epic,
    Legendary,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, Copy, PartialEq, Eq, InitSpace)]
pub enum CustodyType {
    /// NFT held by game config PDA - usable in-game
    InGame,
    /// NFT transferred to player's wallet - tradeable
    Wallet,
}

// ============================================================================
// Events
// ============================================================================

#[event]
pub struct ConfigInitialized {
    pub authority: Pubkey,
    pub royalty_bps: u16,
    pub treasury: Pubkey,
}

#[event]
pub struct CollectionCreated {
    pub collection: Pubkey,
    pub collection_type: CollectionType,
    pub name: String,
    pub max_supply: u32,
}

#[event]
pub struct NftMinted {
    pub asset: Pubkey,
    pub collection: Pubkey,
    pub owner: Pubkey,
    pub name: String,
}

#[event]
pub struct TerritoryMinted {
    pub asset: Pubkey,
    pub region_x: i32,
    pub region_z: i32,
    pub terrain_type: TerrainType,
    pub owner: Pubkey,
}

/// Event emitted when a Celtic creature NFT is minted
/// Parallel to Ethereum CelticCreatureNFT.CreatureMinted event
#[event]
pub struct CreatureMinted {
    pub asset: Pubkey,
    pub collection: Pubkey,
    pub owner: Pubkey,
    pub name: String,
    pub tradition: CelticTradition,
    pub creature_type: CreatureCategory,
    pub rarity: Rarity,
    pub strength: u8,
    pub wisdom: u8,
    pub magic: u8,
    pub special_ability: String,
}

#[event]
pub struct NftUpdated {
    pub asset: Pubkey,
    pub nft_type: NftType,
}

// Relayer Events
#[event]
pub struct RelayerAdded {
    pub relayer: Pubkey,
    pub authority: Pubkey,
}

#[event]
pub struct RelayerDisabled {
    pub relayer: Pubkey,
}

#[event]
pub struct RelayerMinted {
    pub asset: Pubkey,
    pub collection: Pubkey,
    pub owner: Pubkey,
    pub relayer: Pubkey,
    pub spacetimedb_mint_id: u64,
    pub name: String,
}

#[event]
pub struct NftWithdrawn {
    pub asset: Pubkey,
    pub owner: Pubkey,
    pub timestamp: i64,
}

#[event]
pub struct NftDeposited {
    pub asset: Pubkey,
    pub owner: Pubkey,
    pub timestamp: i64,
}

// ============================================================================
// Errors
// ============================================================================

#[error_code]
pub enum CelticNftError {
    #[msg("Unauthorized access")]
    Unauthorized,
    #[msg("Program is paused")]
    ProgramPaused,
    #[msg("Royalty exceeds maximum (10%)")]
    RoyaltyTooHigh,
    #[msg("Name exceeds 32 characters")]
    NameTooLong,
    #[msg("URI exceeds 200 characters")]
    UriTooLong,
    #[msg("Maximum supply reached")]
    MaxSupplyReached,
    #[msg("Wrong collection type for this operation")]
    WrongCollectionType,
    #[msg("Wrong NFT type for this operation")]
    WrongNftType,
    #[msg("Invalid level update")]
    InvalidLevelUpdate,
    #[msg("Arithmetic overflow")]
    Overflow,
    // Relayer errors
    #[msg("Relayer is disabled")]
    RelayerDisabled,
    #[msg("NFT not in game custody")]
    NotInGameCustody,
    #[msg("NFT not in wallet custody")]
    NotWalletCustody,
    #[msg("Not the owner of this NFT")]
    NotOwner,
    #[msg("Attribute value exceeds maximum (100)")]
    AttributeTooHigh,
}
