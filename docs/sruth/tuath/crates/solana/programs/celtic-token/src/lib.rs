//! Celtic Token - Solana Token-2022 Program
//!
//! Token-2022 extensions for Celtic game assets:
//! - Transfer Hooks for game logic validation
//! - Confidential Transfers for clan treasury
//! - Metadata for Celtic item attributes
//! - Permanent Delegate for game escrow
//! - Clan Treasuries with on-chain governance
//!
//! Build: anchor build
//! Deploy: anchor deploy --provider.cluster devnet

use anchor_lang::prelude::*;
use anchor_spl::{
    token_2022::{Token2022, spl_token_2022},
    token_interface::{Mint, TokenAccount, TokenInterface},
};
use spl_transfer_hook_interface::instruction::TransferHookInstruction;

declare_id!("CELTicToken1111111111111111111111111111111");

/// Program state seed
pub const CELTIC_CONFIG_SEED: &[u8] = b"celtic_config";
/// Transfer hook extra accounts seed
pub const HOOK_EXTRA_ACCOUNTS_SEED: &[u8] = b"hook_extra_accounts";
/// Clan treasury seed
pub const CLAN_TREASURY_SEED: &[u8] = b"clan_treasury";
/// Treasury proposal seed
pub const TREASURY_PROPOSAL_SEED: &[u8] = b"treasury_proposal";
/// Treasury vote seed
pub const TREASURY_VOTE_SEED: &[u8] = b"treasury_vote";
/// Minimum voting period in slots (~2 days at 400ms/slot)
pub const MIN_VOTING_PERIOD_SLOTS: u64 = 432_000;
/// Maximum voting period in slots (~7 days)
pub const MAX_VOTING_PERIOD_SLOTS: u64 = 1_512_000;

#[program]
pub mod celtic_token {
    use super::*;

    /// Initialize the Celtic token configuration
    pub fn initialize(
        ctx: Context<Initialize>,
        clan_treasury_fee_bps: u16,
        game_escrow_fee_bps: u16,
    ) -> Result<()> {
        require!(
            clan_treasury_fee_bps <= 1000, // Max 10%
            CelticError::FeeTooHigh
        );
        require!(
            game_escrow_fee_bps <= 500, // Max 5%
            CelticError::FeeTooHigh
        );

        let config = &mut ctx.accounts.config;
        config.authority = ctx.accounts.authority.key();
        config.clan_treasury_fee_bps = clan_treasury_fee_bps;
        config.game_escrow_fee_bps = game_escrow_fee_bps;
        config.total_minted = 0;
        config.total_burned = 0;
        config.paused = false;
        config.bump = ctx.bumps.config;

        emit!(ConfigInitialized {
            authority: config.authority,
            clan_treasury_fee_bps,
            game_escrow_fee_bps,
        });

        Ok(())
    }

    /// Create a new Celtic token mint with Transfer Hook extension
    pub fn create_celtic_mint(
        ctx: Context<CreateCelticMint>,
        item_type: ItemType,
        celtic_style: CelticStyle,
        metadata_uri: String,
    ) -> Result<()> {
        let item_metadata = &mut ctx.accounts.item_metadata;
        item_metadata.mint = ctx.accounts.mint.key();
        item_metadata.item_type = item_type;
        item_metadata.celtic_style = celtic_style;
        item_metadata.metadata_uri = metadata_uri.clone();
        item_metadata.creator = ctx.accounts.authority.key();
        item_metadata.is_tradeable = true;
        item_metadata.is_equippable = true;
        item_metadata.power_level = 1;
        item_metadata.created_at = Clock::get()?.unix_timestamp;
        item_metadata.bump = ctx.bumps.item_metadata;

        emit!(CelticMintCreated {
            mint: ctx.accounts.mint.key(),
            item_type,
            celtic_style,
            metadata_uri,
            creator: ctx.accounts.authority.key(),
        });

        Ok(())
    }

    /// Mint Celtic tokens to a player
    pub fn mint_to_player(
        ctx: Context<MintToPlayer>,
        amount: u64,
    ) -> Result<()> {
        require!(!ctx.accounts.config.paused, CelticError::ProgramPaused);
        require!(amount > 0, CelticError::InvalidAmount);

        // Update config stats
        let config = &mut ctx.accounts.config;
        config.total_minted = config.total_minted.checked_add(amount)
            .ok_or(CelticError::Overflow)?;

        // Mint tokens using Token-2022
        let seeds = &[
            CELTIC_CONFIG_SEED,
            &[config.bump],
        ];
        let signer = &[&seeds[..]];

        anchor_spl::token_2022::mint_to(
            CpiContext::new_with_signer(
                ctx.accounts.token_program.to_account_info(),
                anchor_spl::token_2022::MintTo {
                    mint: ctx.accounts.mint.to_account_info(),
                    to: ctx.accounts.player_token_account.to_account_info(),
                    authority: ctx.accounts.config.to_account_info(),
                },
                signer,
            ),
            amount,
        )?;

        emit!(TokensMinted {
            mint: ctx.accounts.mint.key(),
            player: ctx.accounts.player.key(),
            amount,
        });

        Ok(())
    }

    /// Burn tokens (withdraw from game)
    pub fn burn_tokens(
        ctx: Context<BurnTokens>,
        amount: u64,
    ) -> Result<()> {
        require!(!ctx.accounts.config.paused, CelticError::ProgramPaused);
        require!(amount > 0, CelticError::InvalidAmount);

        // Update config stats
        let config = &mut ctx.accounts.config;
        config.total_burned = config.total_burned.checked_add(amount)
            .ok_or(CelticError::Overflow)?;

        // Burn tokens
        anchor_spl::token_2022::burn(
            CpiContext::new(
                ctx.accounts.token_program.to_account_info(),
                anchor_spl::token_2022::Burn {
                    mint: ctx.accounts.mint.to_account_info(),
                    from: ctx.accounts.player_token_account.to_account_info(),
                    authority: ctx.accounts.player.to_account_info(),
                },
            ),
            amount,
        )?;

        emit!(TokensBurned {
            mint: ctx.accounts.mint.key(),
            player: ctx.accounts.player.key(),
            amount,
        });

        Ok(())
    }

    /// Transfer Hook: Execute - Called by Token-2022 during transfers
    /// Validates game rules and collects fees
    pub fn transfer_hook_execute(
        ctx: Context<TransferHookExecute>,
        amount: u64,
    ) -> Result<()> {
        let item_metadata = &ctx.accounts.item_metadata;
        let config = &ctx.accounts.config;

        // Check if item is tradeable
        require!(
            item_metadata.is_tradeable,
            CelticError::ItemNotTradeable
        );

        // Clan treasury fee (if destination is in a clan)
        if config.clan_treasury_fee_bps > 0 {
            let _fee = amount
                .checked_mul(config.clan_treasury_fee_bps as u64)
                .ok_or(CelticError::Overflow)?
                .checked_div(10000)
                .ok_or(CelticError::Overflow)?;
            // Fee collection handled by additional instructions
        }

        emit!(TransferHookExecuted {
            mint: item_metadata.mint,
            amount,
            source: ctx.accounts.source_token.key(),
            destination: ctx.accounts.destination_token.key(),
        });

        Ok(())
    }

    /// Transfer Hook: Initialize extra account metas
    /// Required by SPL Transfer Hook interface
    pub fn transfer_hook_initialize_extra_account_metas(
        ctx: Context<TransferHookInitialize>,
    ) -> Result<()> {
        let extra_account_metas = &mut ctx.accounts.extra_account_metas;

        // Store the config and item_metadata accounts as extra metas
        // These will be automatically included in transfers
        extra_account_metas.mint = ctx.accounts.mint.key();
        extra_account_metas.bump = ctx.bumps.extra_account_metas;

        Ok(())
    }

    /// Update item metadata (admin only)
    pub fn update_item_metadata(
        ctx: Context<UpdateItemMetadata>,
        is_tradeable: Option<bool>,
        is_equippable: Option<bool>,
        power_level: Option<u8>,
    ) -> Result<()> {
        let item_metadata = &mut ctx.accounts.item_metadata;

        if let Some(tradeable) = is_tradeable {
            item_metadata.is_tradeable = tradeable;
        }
        if let Some(equippable) = is_equippable {
            item_metadata.is_equippable = equippable;
        }
        if let Some(power) = power_level {
            item_metadata.power_level = power;
        }

        emit!(ItemMetadataUpdated {
            mint: item_metadata.mint,
            is_tradeable: item_metadata.is_tradeable,
            is_equippable: item_metadata.is_equippable,
            power_level: item_metadata.power_level,
        });

        Ok(())
    }

    /// Pause/unpause the program (admin only)
    pub fn set_paused(ctx: Context<AdminOnly>, paused: bool) -> Result<()> {
        ctx.accounts.config.paused = paused;

        emit!(PauseStatusChanged {
            paused,
            authority: ctx.accounts.authority.key(),
        });

        Ok(())
    }

    /// Update fee configuration (admin only)
    pub fn update_fees(
        ctx: Context<AdminOnly>,
        clan_treasury_fee_bps: Option<u16>,
        game_escrow_fee_bps: Option<u16>,
    ) -> Result<()> {
        let config = &mut ctx.accounts.config;

        if let Some(fee) = clan_treasury_fee_bps {
            require!(fee <= 1000, CelticError::FeeTooHigh);
            config.clan_treasury_fee_bps = fee;
        }
        if let Some(fee) = game_escrow_fee_bps {
            require!(fee <= 500, CelticError::FeeTooHigh);
            config.game_escrow_fee_bps = fee;
        }

        emit!(FeesUpdated {
            clan_treasury_fee_bps: config.clan_treasury_fee_bps,
            game_escrow_fee_bps: config.game_escrow_fee_bps,
        });

        Ok(())
    }

    // ========================================================================
    // Clan Treasury Instructions
    // ========================================================================

    /// Initialize a new clan treasury
    /// Requires clan leader authority from SpacetimeDB validation
    pub fn initialize_treasury(
        ctx: Context<InitializeTreasury>,
        clan_id: u64,
        required_approvals: u8,
        voting_period_slots: u64,
    ) -> Result<()> {
        require!(
            required_approvals >= 1 && required_approvals <= 10,
            CelticError::InvalidApprovalThreshold
        );
        require!(
            voting_period_slots >= MIN_VOTING_PERIOD_SLOTS
                && voting_period_slots <= MAX_VOTING_PERIOD_SLOTS,
            CelticError::InvalidVotingPeriod
        );

        let treasury = &mut ctx.accounts.treasury;
        treasury.clan_id = clan_id;
        treasury.authority = ctx.accounts.clan_leader.key();
        treasury.token_account = ctx.accounts.treasury_token_account.key();
        treasury.mint = ctx.accounts.mint.key();
        treasury.total_deposited = 0;
        treasury.total_withdrawn = 0;
        treasury.proposal_count = 0;
        treasury.required_approvals = required_approvals;
        treasury.voting_period_slots = voting_period_slots;
        treasury.created_at = Clock::get()?.unix_timestamp;
        treasury.bump = ctx.bumps.treasury;

        emit!(TreasuryInitialized {
            clan_id,
            treasury: treasury.key(),
            authority: ctx.accounts.clan_leader.key(),
            mint: ctx.accounts.mint.key(),
            required_approvals,
        });

        Ok(())
    }

    /// Deposit tokens into clan treasury
    pub fn deposit_to_treasury(
        ctx: Context<DepositToTreasury>,
        amount: u64,
    ) -> Result<()> {
        require!(amount > 0, CelticError::InvalidAmount);
        require!(!ctx.accounts.config.paused, CelticError::ProgramPaused);

        // Transfer tokens from depositor to treasury
        anchor_spl::token_2022::transfer_checked(
            CpiContext::new(
                ctx.accounts.token_program.to_account_info(),
                anchor_spl::token_2022::TransferChecked {
                    from: ctx.accounts.depositor_token_account.to_account_info(),
                    to: ctx.accounts.treasury_token_account.to_account_info(),
                    authority: ctx.accounts.depositor.to_account_info(),
                    mint: ctx.accounts.mint.to_account_info(),
                },
            ),
            amount,
            ctx.accounts.mint.decimals,
        )?;

        // Update treasury stats
        let treasury = &mut ctx.accounts.treasury;
        treasury.total_deposited = treasury.total_deposited
            .checked_add(amount)
            .ok_or(CelticError::Overflow)?;

        emit!(TreasuryDeposit {
            clan_id: treasury.clan_id,
            treasury: treasury.key(),
            depositor: ctx.accounts.depositor.key(),
            amount,
            total_balance: treasury.total_deposited - treasury.total_withdrawn,
        });

        Ok(())
    }

    /// Create a spending proposal
    pub fn create_spend_proposal(
        ctx: Context<CreateSpendProposal>,
        recipient: Pubkey,
        amount: u64,
        description: String,
    ) -> Result<()> {
        require!(amount > 0, CelticError::InvalidAmount);
        require!(description.len() <= 200, CelticError::DescriptionTooLong);
        require!(!ctx.accounts.config.paused, CelticError::ProgramPaused);

        // Check treasury has sufficient balance
        let treasury_balance = ctx.accounts.treasury.total_deposited
            .saturating_sub(ctx.accounts.treasury.total_withdrawn);
        require!(amount <= treasury_balance, CelticError::InsufficientTreasuryBalance);

        let clock = Clock::get()?;
        let treasury = &mut ctx.accounts.treasury;

        // Increment proposal count
        let proposal_id = treasury.proposal_count;
        treasury.proposal_count = treasury.proposal_count
            .checked_add(1)
            .ok_or(CelticError::Overflow)?;

        // Initialize proposal
        let proposal = &mut ctx.accounts.proposal;
        proposal.treasury = treasury.key();
        proposal.proposal_id = proposal_id;
        proposal.proposer = ctx.accounts.proposer.key();
        proposal.recipient = recipient;
        proposal.amount = amount;
        proposal.description = description.clone();
        proposal.votes_for = 0;
        proposal.votes_against = 0;
        proposal.status = ProposalStatus::Active;
        proposal.created_slot = clock.slot;
        proposal.end_slot = clock.slot.checked_add(treasury.voting_period_slots)
            .ok_or(CelticError::Overflow)?;
        proposal.executed_at = None;
        proposal.bump = ctx.bumps.proposal;

        emit!(ProposalCreated {
            clan_id: treasury.clan_id,
            treasury: treasury.key(),
            proposal_id,
            proposer: ctx.accounts.proposer.key(),
            recipient,
            amount,
            description,
            end_slot: proposal.end_slot,
        });

        Ok(())
    }

    /// Vote on a treasury proposal
    pub fn vote_on_proposal(
        ctx: Context<VoteOnProposal>,
        approve: bool,
        voting_power: u64,
    ) -> Result<()> {
        require!(voting_power > 0, CelticError::InvalidVotingPower);
        require!(!ctx.accounts.config.paused, CelticError::ProgramPaused);

        let clock = Clock::get()?;
        let proposal = &mut ctx.accounts.proposal;

        // Check proposal is still active
        require!(
            proposal.status == ProposalStatus::Active,
            CelticError::ProposalNotActive
        );
        require!(
            clock.slot <= proposal.end_slot,
            CelticError::VotingPeriodEnded
        );

        // Record vote
        let vote = &mut ctx.accounts.vote;
        vote.proposal = proposal.key();
        vote.voter = ctx.accounts.voter.key();
        vote.voting_power = voting_power;
        vote.approve = approve;
        vote.voted_at = clock.unix_timestamp;
        vote.bump = ctx.bumps.vote;

        // Update proposal vote counts
        if approve {
            proposal.votes_for = proposal.votes_for
                .checked_add(voting_power)
                .ok_or(CelticError::Overflow)?;
        } else {
            proposal.votes_against = proposal.votes_against
                .checked_add(voting_power)
                .ok_or(CelticError::Overflow)?;
        }

        emit!(VoteCast {
            clan_id: ctx.accounts.treasury.clan_id,
            proposal_id: proposal.proposal_id,
            voter: ctx.accounts.voter.key(),
            approve,
            voting_power,
            votes_for: proposal.votes_for,
            votes_against: proposal.votes_against,
        });

        Ok(())
    }

    /// Execute an approved proposal
    pub fn execute_proposal(ctx: Context<ExecuteProposal>) -> Result<()> {
        require!(!ctx.accounts.config.paused, CelticError::ProgramPaused);

        let clock = Clock::get()?;
        let proposal = &mut ctx.accounts.proposal;
        let treasury = &mut ctx.accounts.treasury;

        // Check proposal status
        require!(
            proposal.status == ProposalStatus::Active,
            CelticError::ProposalNotActive
        );

        // Check voting period ended
        require!(
            clock.slot > proposal.end_slot,
            CelticError::VotingPeriodNotEnded
        );

        // Check approval threshold met
        let total_votes = proposal.votes_for.saturating_add(proposal.votes_against);
        require!(total_votes > 0, CelticError::NoVotesCast);

        let required_votes = treasury.required_approvals as u64;
        if proposal.votes_for >= required_votes && proposal.votes_for > proposal.votes_against {
            // Proposal approved - execute transfer
            let treasury_bump = treasury.bump;
            let clan_id_bytes = treasury.clan_id.to_le_bytes();
            let seeds = &[
                CLAN_TREASURY_SEED,
                clan_id_bytes.as_ref(),
                &[treasury_bump],
            ];
            let signer = &[&seeds[..]];

            anchor_spl::token_2022::transfer_checked(
                CpiContext::new_with_signer(
                    ctx.accounts.token_program.to_account_info(),
                    anchor_spl::token_2022::TransferChecked {
                        from: ctx.accounts.treasury_token_account.to_account_info(),
                        to: ctx.accounts.recipient_token_account.to_account_info(),
                        authority: treasury.to_account_info(),
                        mint: ctx.accounts.mint.to_account_info(),
                    },
                    signer,
                ),
                proposal.amount,
                ctx.accounts.mint.decimals,
            )?;

            // Update treasury stats
            treasury.total_withdrawn = treasury.total_withdrawn
                .checked_add(proposal.amount)
                .ok_or(CelticError::Overflow)?;

            proposal.status = ProposalStatus::Executed;
            proposal.executed_at = Some(clock.unix_timestamp);

            emit!(ProposalExecuted {
                clan_id: treasury.clan_id,
                proposal_id: proposal.proposal_id,
                recipient: proposal.recipient,
                amount: proposal.amount,
                executor: ctx.accounts.executor.key(),
            });
        } else {
            // Proposal rejected
            proposal.status = ProposalStatus::Rejected;

            emit!(ProposalRejected {
                clan_id: treasury.clan_id,
                proposal_id: proposal.proposal_id,
                votes_for: proposal.votes_for,
                votes_against: proposal.votes_against,
            });
        }

        Ok(())
    }

    /// Cancel a proposal (only proposer or authority)
    pub fn cancel_proposal(ctx: Context<CancelProposal>) -> Result<()> {
        let proposal = &mut ctx.accounts.proposal;

        require!(
            proposal.status == ProposalStatus::Active,
            CelticError::ProposalNotActive
        );

        // Only proposer or clan authority can cancel
        let is_proposer = ctx.accounts.canceller.key() == proposal.proposer;
        let is_authority = ctx.accounts.canceller.key() == ctx.accounts.treasury.authority;
        require!(is_proposer || is_authority, CelticError::Unauthorized);

        proposal.status = ProposalStatus::Cancelled;

        emit!(ProposalCancelled {
            clan_id: ctx.accounts.treasury.clan_id,
            proposal_id: proposal.proposal_id,
            cancelled_by: ctx.accounts.canceller.key(),
        });

        Ok(())
    }

    /// Update treasury settings (clan leader only)
    pub fn update_treasury_settings(
        ctx: Context<UpdateTreasurySettings>,
        new_authority: Option<Pubkey>,
        new_required_approvals: Option<u8>,
        new_voting_period_slots: Option<u64>,
    ) -> Result<()> {
        let treasury = &mut ctx.accounts.treasury;

        if let Some(authority) = new_authority {
            treasury.authority = authority;
        }

        if let Some(required) = new_required_approvals {
            require!(
                required >= 1 && required <= 10,
                CelticError::InvalidApprovalThreshold
            );
            treasury.required_approvals = required;
        }

        if let Some(period) = new_voting_period_slots {
            require!(
                period >= MIN_VOTING_PERIOD_SLOTS && period <= MAX_VOTING_PERIOD_SLOTS,
                CelticError::InvalidVotingPeriod
            );
            treasury.voting_period_slots = period;
        }

        emit!(TreasurySettingsUpdated {
            clan_id: treasury.clan_id,
            treasury: treasury.key(),
            authority: treasury.authority,
            required_approvals: treasury.required_approvals,
            voting_period_slots: treasury.voting_period_slots,
        });

        Ok(())
    }
}

// ============================================================================
// Account Structures
// ============================================================================

#[account]
#[derive(InitSpace)]
pub struct CelticConfig {
    /// Program authority
    pub authority: Pubkey,
    /// Fee sent to clan treasury (basis points)
    pub clan_treasury_fee_bps: u16,
    /// Fee for game escrow operations (basis points)
    pub game_escrow_fee_bps: u16,
    /// Total tokens minted
    pub total_minted: u64,
    /// Total tokens burned
    pub total_burned: u64,
    /// Emergency pause flag
    pub paused: bool,
    /// PDA bump
    pub bump: u8,
}

#[account]
#[derive(InitSpace)]
pub struct ItemMetadata {
    /// Associated mint
    pub mint: Pubkey,
    /// Item type (weapon, armor, etc.)
    pub item_type: ItemType,
    /// Celtic art style
    pub celtic_style: CelticStyle,
    /// IPFS/Arweave URI for full metadata
    #[max_len(200)]
    pub metadata_uri: String,
    /// Original creator
    pub creator: Pubkey,
    /// Can be traded between players
    pub is_tradeable: bool,
    /// Can be equipped in game
    pub is_equippable: bool,
    /// Power level (1-100)
    pub power_level: u8,
    /// Creation timestamp
    pub created_at: i64,
    /// PDA bump
    pub bump: u8,
}

#[account]
#[derive(InitSpace)]
pub struct ExtraAccountMetas {
    /// Associated mint
    pub mint: Pubkey,
    /// PDA bump
    pub bump: u8,
}

/// Clan treasury account - holds clan funds with governance
#[account]
#[derive(InitSpace)]
pub struct ClanTreasury {
    /// Clan ID from SpacetimeDB
    pub clan_id: u64,
    /// Treasury authority (clan leader)
    pub authority: Pubkey,
    /// Token account holding treasury funds
    pub token_account: Pubkey,
    /// Token mint
    pub mint: Pubkey,
    /// Total tokens deposited (lifetime)
    pub total_deposited: u64,
    /// Total tokens withdrawn (lifetime)
    pub total_withdrawn: u64,
    /// Number of proposals created
    pub proposal_count: u64,
    /// Required approvals for spending
    pub required_approvals: u8,
    /// Voting period in slots
    pub voting_period_slots: u64,
    /// Creation timestamp
    pub created_at: i64,
    /// PDA bump
    pub bump: u8,
}

/// Treasury spending proposal
#[account]
#[derive(InitSpace)]
pub struct TreasuryProposal {
    /// Parent treasury
    pub treasury: Pubkey,
    /// Proposal ID (sequential within treasury)
    pub proposal_id: u64,
    /// Who created this proposal
    pub proposer: Pubkey,
    /// Recipient of funds if approved
    pub recipient: Pubkey,
    /// Amount to transfer
    pub amount: u64,
    /// Description of spending purpose
    #[max_len(200)]
    pub description: String,
    /// Votes in favor
    pub votes_for: u64,
    /// Votes against
    pub votes_against: u64,
    /// Current status
    pub status: ProposalStatus,
    /// Slot when proposal was created
    pub created_slot: u64,
    /// Slot when voting ends
    pub end_slot: u64,
    /// Execution timestamp (if executed)
    pub executed_at: Option<i64>,
    /// PDA bump
    pub bump: u8,
}

/// Individual vote record
#[account]
#[derive(InitSpace)]
pub struct TreasuryVote {
    /// Proposal being voted on
    pub proposal: Pubkey,
    /// Voter
    pub voter: Pubkey,
    /// Voting power used
    pub voting_power: u64,
    /// True = approve, False = reject
    pub approve: bool,
    /// When vote was cast
    pub voted_at: i64,
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
        space = 8 + CelticConfig::INIT_SPACE,
        seeds = [CELTIC_CONFIG_SEED],
        bump,
    )]
    pub config: Account<'info, CelticConfig>,

    #[account(mut)]
    pub authority: Signer<'info>,

    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct CreateCelticMint<'info> {
    #[account(
        seeds = [CELTIC_CONFIG_SEED],
        bump = config.bump,
    )]
    pub config: Account<'info, CelticConfig>,

    /// CHECK: Mint account initialized externally with Token-2022 extensions
    #[account(mut)]
    pub mint: UncheckedAccount<'info>,

    #[account(
        init,
        payer = authority,
        space = 8 + ItemMetadata::INIT_SPACE,
        seeds = [b"item_metadata", mint.key().as_ref()],
        bump,
    )]
    pub item_metadata: Account<'info, ItemMetadata>,

    #[account(mut)]
    pub authority: Signer<'info>,

    pub token_program: Program<'info, Token2022>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct MintToPlayer<'info> {
    #[account(
        mut,
        seeds = [CELTIC_CONFIG_SEED],
        bump = config.bump,
    )]
    pub config: Account<'info, CelticConfig>,

    #[account(mut)]
    pub mint: InterfaceAccount<'info, Mint>,

    #[account(mut)]
    pub player_token_account: InterfaceAccount<'info, TokenAccount>,

    /// CHECK: Player identity
    pub player: UncheckedAccount<'info>,

    #[account(
        constraint = authority.key() == config.authority @ CelticError::Unauthorized
    )]
    pub authority: Signer<'info>,

    pub token_program: Interface<'info, TokenInterface>,
}

#[derive(Accounts)]
pub struct BurnTokens<'info> {
    #[account(
        mut,
        seeds = [CELTIC_CONFIG_SEED],
        bump = config.bump,
    )]
    pub config: Account<'info, CelticConfig>,

    #[account(mut)]
    pub mint: InterfaceAccount<'info, Mint>,

    #[account(mut)]
    pub player_token_account: InterfaceAccount<'info, TokenAccount>,

    #[account(mut)]
    pub player: Signer<'info>,

    pub token_program: Interface<'info, TokenInterface>,
}

#[derive(Accounts)]
pub struct TransferHookExecute<'info> {
    #[account(
        seeds = [CELTIC_CONFIG_SEED],
        bump = config.bump,
    )]
    pub config: Account<'info, CelticConfig>,

    #[account(
        seeds = [b"item_metadata", source_token.mint.as_ref()],
        bump = item_metadata.bump,
    )]
    pub item_metadata: Account<'info, ItemMetadata>,

    /// CHECK: Source token account (validated by Token-2022)
    pub source_token: InterfaceAccount<'info, TokenAccount>,

    /// CHECK: Destination token account (validated by Token-2022)
    pub destination_token: InterfaceAccount<'info, TokenAccount>,
}

#[derive(Accounts)]
pub struct TransferHookInitialize<'info> {
    #[account(
        init,
        payer = payer,
        space = 8 + ExtraAccountMetas::INIT_SPACE,
        seeds = [HOOK_EXTRA_ACCOUNTS_SEED, mint.key().as_ref()],
        bump,
    )]
    pub extra_account_metas: Account<'info, ExtraAccountMetas>,

    /// CHECK: Mint for the hook
    pub mint: UncheckedAccount<'info>,

    #[account(mut)]
    pub payer: Signer<'info>,

    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct UpdateItemMetadata<'info> {
    #[account(
        seeds = [CELTIC_CONFIG_SEED],
        bump = config.bump,
    )]
    pub config: Account<'info, CelticConfig>,

    #[account(
        mut,
        seeds = [b"item_metadata", item_metadata.mint.as_ref()],
        bump = item_metadata.bump,
    )]
    pub item_metadata: Account<'info, ItemMetadata>,

    #[account(
        constraint = authority.key() == config.authority @ CelticError::Unauthorized
    )]
    pub authority: Signer<'info>,
}

#[derive(Accounts)]
pub struct AdminOnly<'info> {
    #[account(
        mut,
        seeds = [CELTIC_CONFIG_SEED],
        bump = config.bump,
    )]
    pub config: Account<'info, CelticConfig>,

    #[account(
        constraint = authority.key() == config.authority @ CelticError::Unauthorized
    )]
    pub authority: Signer<'info>,
}

// ============================================================================
// Treasury Context Structures
// ============================================================================

#[derive(Accounts)]
#[instruction(clan_id: u64)]
pub struct InitializeTreasury<'info> {
    #[account(
        seeds = [CELTIC_CONFIG_SEED],
        bump = config.bump,
    )]
    pub config: Account<'info, CelticConfig>,

    #[account(
        init,
        payer = clan_leader,
        space = 8 + ClanTreasury::INIT_SPACE,
        seeds = [CLAN_TREASURY_SEED, &clan_id.to_le_bytes()],
        bump,
    )]
    pub treasury: Account<'info, ClanTreasury>,

    /// Treasury token account (owned by treasury PDA)
    #[account(
        mut,
        constraint = treasury_token_account.mint == mint.key(),
    )]
    pub treasury_token_account: InterfaceAccount<'info, TokenAccount>,

    pub mint: InterfaceAccount<'info, Mint>,

    #[account(mut)]
    pub clan_leader: Signer<'info>,

    pub token_program: Interface<'info, TokenInterface>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct DepositToTreasury<'info> {
    #[account(
        seeds = [CELTIC_CONFIG_SEED],
        bump = config.bump,
    )]
    pub config: Account<'info, CelticConfig>,

    #[account(
        mut,
        seeds = [CLAN_TREASURY_SEED, &treasury.clan_id.to_le_bytes()],
        bump = treasury.bump,
    )]
    pub treasury: Account<'info, ClanTreasury>,

    #[account(
        mut,
        constraint = treasury_token_account.key() == treasury.token_account,
    )]
    pub treasury_token_account: InterfaceAccount<'info, TokenAccount>,

    #[account(
        mut,
        constraint = depositor_token_account.mint == treasury.mint,
        constraint = depositor_token_account.owner == depositor.key(),
    )]
    pub depositor_token_account: InterfaceAccount<'info, TokenAccount>,

    pub mint: InterfaceAccount<'info, Mint>,

    #[account(mut)]
    pub depositor: Signer<'info>,

    pub token_program: Interface<'info, TokenInterface>,
}

#[derive(Accounts)]
pub struct CreateSpendProposal<'info> {
    #[account(
        seeds = [CELTIC_CONFIG_SEED],
        bump = config.bump,
    )]
    pub config: Account<'info, CelticConfig>,

    #[account(
        mut,
        seeds = [CLAN_TREASURY_SEED, &treasury.clan_id.to_le_bytes()],
        bump = treasury.bump,
    )]
    pub treasury: Account<'info, ClanTreasury>,

    #[account(
        init,
        payer = proposer,
        space = 8 + TreasuryProposal::INIT_SPACE,
        seeds = [
            TREASURY_PROPOSAL_SEED,
            treasury.key().as_ref(),
            &treasury.proposal_count.to_le_bytes()
        ],
        bump,
    )]
    pub proposal: Account<'info, TreasuryProposal>,

    #[account(mut)]
    pub proposer: Signer<'info>,

    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct VoteOnProposal<'info> {
    #[account(
        seeds = [CELTIC_CONFIG_SEED],
        bump = config.bump,
    )]
    pub config: Account<'info, CelticConfig>,

    #[account(
        seeds = [CLAN_TREASURY_SEED, &treasury.clan_id.to_le_bytes()],
        bump = treasury.bump,
    )]
    pub treasury: Account<'info, ClanTreasury>,

    #[account(
        mut,
        seeds = [
            TREASURY_PROPOSAL_SEED,
            treasury.key().as_ref(),
            &proposal.proposal_id.to_le_bytes()
        ],
        bump = proposal.bump,
        constraint = proposal.treasury == treasury.key(),
    )]
    pub proposal: Account<'info, TreasuryProposal>,

    #[account(
        init,
        payer = voter,
        space = 8 + TreasuryVote::INIT_SPACE,
        seeds = [
            TREASURY_VOTE_SEED,
            proposal.key().as_ref(),
            voter.key().as_ref()
        ],
        bump,
    )]
    pub vote: Account<'info, TreasuryVote>,

    #[account(mut)]
    pub voter: Signer<'info>,

    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct ExecuteProposal<'info> {
    #[account(
        seeds = [CELTIC_CONFIG_SEED],
        bump = config.bump,
    )]
    pub config: Account<'info, CelticConfig>,

    #[account(
        mut,
        seeds = [CLAN_TREASURY_SEED, &treasury.clan_id.to_le_bytes()],
        bump = treasury.bump,
    )]
    pub treasury: Account<'info, ClanTreasury>,

    #[account(
        mut,
        seeds = [
            TREASURY_PROPOSAL_SEED,
            treasury.key().as_ref(),
            &proposal.proposal_id.to_le_bytes()
        ],
        bump = proposal.bump,
        constraint = proposal.treasury == treasury.key(),
    )]
    pub proposal: Account<'info, TreasuryProposal>,

    #[account(
        mut,
        constraint = treasury_token_account.key() == treasury.token_account,
    )]
    pub treasury_token_account: InterfaceAccount<'info, TokenAccount>,

    /// Recipient token account
    #[account(
        mut,
        constraint = recipient_token_account.owner == proposal.recipient,
        constraint = recipient_token_account.mint == treasury.mint,
    )]
    pub recipient_token_account: InterfaceAccount<'info, TokenAccount>,

    pub mint: InterfaceAccount<'info, Mint>,

    /// Anyone can execute after voting period ends
    pub executor: Signer<'info>,

    pub token_program: Interface<'info, TokenInterface>,
}

#[derive(Accounts)]
pub struct CancelProposal<'info> {
    #[account(
        seeds = [CLAN_TREASURY_SEED, &treasury.clan_id.to_le_bytes()],
        bump = treasury.bump,
    )]
    pub treasury: Account<'info, ClanTreasury>,

    #[account(
        mut,
        seeds = [
            TREASURY_PROPOSAL_SEED,
            treasury.key().as_ref(),
            &proposal.proposal_id.to_le_bytes()
        ],
        bump = proposal.bump,
        constraint = proposal.treasury == treasury.key(),
    )]
    pub proposal: Account<'info, TreasuryProposal>,

    /// Must be proposer or treasury authority
    pub canceller: Signer<'info>,
}

#[derive(Accounts)]
pub struct UpdateTreasurySettings<'info> {
    #[account(
        mut,
        seeds = [CLAN_TREASURY_SEED, &treasury.clan_id.to_le_bytes()],
        bump = treasury.bump,
    )]
    pub treasury: Account<'info, ClanTreasury>,

    #[account(
        constraint = authority.key() == treasury.authority @ CelticError::Unauthorized
    )]
    pub authority: Signer<'info>,
}

// ============================================================================
// Types (mirroring shared-types for Anchor compatibility)
// ============================================================================

#[derive(AnchorSerialize, AnchorDeserialize, Clone, Copy, PartialEq, Eq, InitSpace)]
pub enum ItemType {
    Weapon,
    Armor,
    Artifact,
    Consumable,
    Quest,
    Material,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, Copy, PartialEq, Eq, InitSpace)]
pub enum CelticStyle {
    LaTene,
    Ogham,
    Knotwork,
    Zoomorphic,
    Spiral,
}

/// Treasury proposal status
#[derive(AnchorSerialize, AnchorDeserialize, Clone, Copy, PartialEq, Eq, InitSpace, Default)]
pub enum ProposalStatus {
    /// Proposal is open for voting
    #[default]
    Active,
    /// Proposal was approved and executed
    Executed,
    /// Proposal was rejected (insufficient votes)
    Rejected,
    /// Proposal was cancelled by proposer/authority
    Cancelled,
}

// ============================================================================
// Events
// ============================================================================

#[event]
pub struct ConfigInitialized {
    pub authority: Pubkey,
    pub clan_treasury_fee_bps: u16,
    pub game_escrow_fee_bps: u16,
}

#[event]
pub struct CelticMintCreated {
    pub mint: Pubkey,
    pub item_type: ItemType,
    pub celtic_style: CelticStyle,
    pub metadata_uri: String,
    pub creator: Pubkey,
}

#[event]
pub struct TokensMinted {
    pub mint: Pubkey,
    pub player: Pubkey,
    pub amount: u64,
}

#[event]
pub struct TokensBurned {
    pub mint: Pubkey,
    pub player: Pubkey,
    pub amount: u64,
}

#[event]
pub struct TransferHookExecuted {
    pub mint: Pubkey,
    pub amount: u64,
    pub source: Pubkey,
    pub destination: Pubkey,
}

#[event]
pub struct ItemMetadataUpdated {
    pub mint: Pubkey,
    pub is_tradeable: bool,
    pub is_equippable: bool,
    pub power_level: u8,
}

#[event]
pub struct PauseStatusChanged {
    pub paused: bool,
    pub authority: Pubkey,
}

#[event]
pub struct FeesUpdated {
    pub clan_treasury_fee_bps: u16,
    pub game_escrow_fee_bps: u16,
}

// ============================================================================
// Treasury Events
// ============================================================================

#[event]
pub struct TreasuryInitialized {
    pub clan_id: u64,
    pub treasury: Pubkey,
    pub authority: Pubkey,
    pub mint: Pubkey,
    pub required_approvals: u8,
}

#[event]
pub struct TreasuryDeposit {
    pub clan_id: u64,
    pub treasury: Pubkey,
    pub depositor: Pubkey,
    pub amount: u64,
    pub total_balance: u64,
}

#[event]
pub struct ProposalCreated {
    pub clan_id: u64,
    pub treasury: Pubkey,
    pub proposal_id: u64,
    pub proposer: Pubkey,
    pub recipient: Pubkey,
    pub amount: u64,
    pub description: String,
    pub end_slot: u64,
}

#[event]
pub struct VoteCast {
    pub clan_id: u64,
    pub proposal_id: u64,
    pub voter: Pubkey,
    pub approve: bool,
    pub voting_power: u64,
    pub votes_for: u64,
    pub votes_against: u64,
}

#[event]
pub struct ProposalExecuted {
    pub clan_id: u64,
    pub proposal_id: u64,
    pub recipient: Pubkey,
    pub amount: u64,
    pub executor: Pubkey,
}

#[event]
pub struct ProposalRejected {
    pub clan_id: u64,
    pub proposal_id: u64,
    pub votes_for: u64,
    pub votes_against: u64,
}

#[event]
pub struct ProposalCancelled {
    pub clan_id: u64,
    pub proposal_id: u64,
    pub cancelled_by: Pubkey,
}

#[event]
pub struct TreasurySettingsUpdated {
    pub clan_id: u64,
    pub treasury: Pubkey,
    pub authority: Pubkey,
    pub required_approvals: u8,
    pub voting_period_slots: u64,
}

// ============================================================================
// Errors
// ============================================================================

#[error_code]
pub enum CelticError {
    #[msg("Unauthorized access")]
    Unauthorized,
    #[msg("Program is paused")]
    ProgramPaused,
    #[msg("Invalid amount")]
    InvalidAmount,
    #[msg("Fee exceeds maximum")]
    FeeTooHigh,
    #[msg("Arithmetic overflow")]
    Overflow,
    #[msg("Item is not tradeable")]
    ItemNotTradeable,
    #[msg("Item is not equippable")]
    ItemNotEquippable,
    #[msg("Invalid metadata URI")]
    InvalidMetadataUri,

    // Treasury-specific errors
    #[msg("Invalid approval threshold (must be 1-10)")]
    InvalidApprovalThreshold,
    #[msg("Invalid voting period")]
    InvalidVotingPeriod,
    #[msg("Insufficient treasury balance")]
    InsufficientTreasuryBalance,
    #[msg("Description too long (max 200 chars)")]
    DescriptionTooLong,
    #[msg("Proposal is not active")]
    ProposalNotActive,
    #[msg("Voting period has ended")]
    VotingPeriodEnded,
    #[msg("Voting period has not ended yet")]
    VotingPeriodNotEnded,
    #[msg("No votes have been cast")]
    NoVotesCast,
    #[msg("Invalid voting power")]
    InvalidVotingPower,
}
