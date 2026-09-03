//! Celtic Hooks - Transfer Hook Program
//!
//! SPL Transfer Hook implementation for Celtic game mechanics:
//! - Validates transfers meet game rules
//! - Collects clan treasury fees
//! - Enforces cooldown periods
//! - Tracks transfer analytics
//!
//! This program is invoked automatically by Token-2022 during transfers.
//!
//! Build: anchor build
//! Deploy: anchor deploy --provider.cluster devnet

use anchor_lang::prelude::*;
use anchor_spl::token_interface::{Mint, TokenAccount};
use spl_transfer_hook_interface::instruction::{ExecuteInstruction, TransferHookInstruction};
use spl_tlv_account_resolution::{
    account::ExtraAccountMeta, seeds::Seed, state::ExtraAccountMetaList,
};

declare_id!("CELTicHook1111111111111111111111111111111");

/// Extra account metas seed
pub const EXTRA_ACCOUNT_METAS_SEED: &[u8] = b"extra-account-metas";
/// Hook config seed
pub const HOOK_CONFIG_SEED: &[u8] = b"hook_config";
/// Transfer record seed
pub const TRANSFER_RECORD_SEED: &[u8] = b"transfer_record";

#[program]
pub mod celtic_hooks {
    use super::*;

    /// Initialize hook configuration for a mint
    pub fn initialize_hook_config(
        ctx: Context<InitializeHookConfig>,
        cooldown_seconds: i64,
        min_transfer_amount: u64,
        max_transfer_amount: u64,
        fee_bps: u16,
    ) -> Result<()> {
        require!(cooldown_seconds >= 0, HookError::InvalidCooldown);
        require!(min_transfer_amount <= max_transfer_amount, HookError::InvalidAmountRange);
        require!(fee_bps <= 1000, HookError::FeeTooHigh);

        let config = &mut ctx.accounts.hook_config;
        config.mint = ctx.accounts.mint.key();
        config.authority = ctx.accounts.authority.key();
        config.cooldown_seconds = cooldown_seconds;
        config.min_transfer_amount = min_transfer_amount;
        config.max_transfer_amount = max_transfer_amount;
        config.fee_bps = fee_bps;
        config.fee_collector = ctx.accounts.fee_collector.key();
        config.total_transfers = 0;
        config.total_volume = 0;
        config.total_fees_collected = 0;
        config.is_active = true;
        config.bump = ctx.bumps.hook_config;

        emit!(HookConfigInitialized {
            mint: config.mint,
            cooldown_seconds,
            fee_bps,
        });

        Ok(())
    }

    /// Initialize extra account metas for transfer hook
    /// Required by the Transfer Hook interface
    pub fn initialize_extra_account_meta_list(
        ctx: Context<InitializeExtraAccountMetaList>,
    ) -> Result<()> {
        // Define the extra accounts needed during transfer execution
        let account_metas = vec![
            // Hook config account (for validation rules)
            ExtraAccountMeta::new_with_seeds(
                &[
                    Seed::Literal {
                        bytes: HOOK_CONFIG_SEED.to_vec(),
                    },
                    Seed::AccountKey { index: 1 }, // mint
                ],
                false, // is_signer
                true,  // is_writable
            )?,
            // Transfer record account (for tracking)
            ExtraAccountMeta::new_with_seeds(
                &[
                    Seed::Literal {
                        bytes: TRANSFER_RECORD_SEED.to_vec(),
                    },
                    Seed::AccountKey { index: 0 }, // source
                    Seed::AccountKey { index: 2 }, // destination
                ],
                false,
                true,
            )?,
        ];

        // Get the account length
        let account_size = ExtraAccountMetaList::size_of(account_metas.len())?;

        // Initialize the extra account list
        let extra_account_metas = &ctx.accounts.extra_account_metas;

        // Write the data
        let mut data = extra_account_metas.try_borrow_mut_data()?;
        ExtraAccountMetaList::init::<ExecuteInstruction>(&mut data, &account_metas)?;

        emit!(ExtraAccountMetasInitialized {
            mint: ctx.accounts.mint.key(),
        });

        Ok(())
    }

    /// Execute transfer hook - called automatically by Token-2022
    ///
    /// This is the main entry point invoked during every transfer
    pub fn transfer_hook(ctx: Context<TransferHook>, amount: u64) -> Result<()> {
        let hook_config = &mut ctx.accounts.hook_config;

        // Validate hook is active
        require!(hook_config.is_active, HookError::HookDisabled);

        // Validate amount range
        require!(
            amount >= hook_config.min_transfer_amount,
            HookError::AmountBelowMinimum
        );
        require!(
            amount <= hook_config.max_transfer_amount || hook_config.max_transfer_amount == 0,
            HookError::AmountAboveMaximum
        );

        // Check cooldown (using transfer record)
        let transfer_record = &mut ctx.accounts.transfer_record;
        let current_time = Clock::get()?.unix_timestamp;

        if transfer_record.last_transfer_time > 0 {
            let elapsed = current_time - transfer_record.last_transfer_time;
            require!(
                elapsed >= hook_config.cooldown_seconds,
                HookError::CooldownActive
            );
        }

        // Calculate fee
        let fee = if hook_config.fee_bps > 0 {
            amount
                .checked_mul(hook_config.fee_bps as u64)
                .ok_or(HookError::Overflow)?
                .checked_div(10000)
                .ok_or(HookError::Overflow)?
        } else {
            0
        };

        // Update statistics
        hook_config.total_transfers = hook_config.total_transfers
            .checked_add(1)
            .ok_or(HookError::Overflow)?;
        hook_config.total_volume = hook_config.total_volume
            .checked_add(amount)
            .ok_or(HookError::Overflow)?;
        hook_config.total_fees_collected = hook_config.total_fees_collected
            .checked_add(fee)
            .ok_or(HookError::Overflow)?;

        // Update transfer record
        transfer_record.source = ctx.accounts.source_token.key();
        transfer_record.destination = ctx.accounts.destination_token.key();
        transfer_record.amount = amount;
        transfer_record.fee = fee;
        transfer_record.last_transfer_time = current_time;
        transfer_record.transfer_count = transfer_record.transfer_count
            .checked_add(1)
            .ok_or(HookError::Overflow)?;

        emit!(TransferExecuted {
            mint: hook_config.mint,
            source: ctx.accounts.source_token.key(),
            destination: ctx.accounts.destination_token.key(),
            amount,
            fee,
        });

        Ok(())
    }

    /// Fallback for transfer hook interface compatibility
    /// This ensures the program ID is recognized as a transfer hook
    pub fn fallback<'info>(
        program_id: &Pubkey,
        accounts: &'info [AccountInfo<'info>],
        data: &[u8],
    ) -> Result<()> {
        let instruction = TransferHookInstruction::unpack(data)?;

        match instruction {
            TransferHookInstruction::Execute { amount } => {
                let account_info_iter = &mut accounts.iter();

                // Parse accounts according to transfer hook interface
                let source_token = next_account_info(account_info_iter)?;
                let mint = next_account_info(account_info_iter)?;
                let destination_token = next_account_info(account_info_iter)?;
                let _owner = next_account_info(account_info_iter)?;
                let extra_account_metas = next_account_info(account_info_iter)?;

                // Additional accounts from extra_account_metas
                let hook_config = next_account_info(account_info_iter)?;
                let transfer_record = next_account_info(account_info_iter)?;

                // Invoke our transfer_hook instruction
                __private::__global::transfer_hook(
                    *program_id,
                    &[
                        source_token.clone(),
                        mint.clone(),
                        destination_token.clone(),
                        hook_config.clone(),
                        transfer_record.clone(),
                        extra_account_metas.clone(),
                    ],
                    amount,
                )
            }
            _ => Err(ProgramError::InvalidInstructionData.into()),
        }
    }

    /// Update hook configuration (admin only)
    pub fn update_hook_config(
        ctx: Context<UpdateHookConfig>,
        cooldown_seconds: Option<i64>,
        min_transfer_amount: Option<u64>,
        max_transfer_amount: Option<u64>,
        fee_bps: Option<u16>,
    ) -> Result<()> {
        let config = &mut ctx.accounts.hook_config;

        if let Some(cooldown) = cooldown_seconds {
            require!(cooldown >= 0, HookError::InvalidCooldown);
            config.cooldown_seconds = cooldown;
        }
        if let Some(min_amt) = min_transfer_amount {
            config.min_transfer_amount = min_amt;
        }
        if let Some(max_amt) = max_transfer_amount {
            config.max_transfer_amount = max_amt;
        }
        if let Some(fee) = fee_bps {
            require!(fee <= 1000, HookError::FeeTooHigh);
            config.fee_bps = fee;
        }

        require!(
            config.min_transfer_amount <= config.max_transfer_amount,
            HookError::InvalidAmountRange
        );

        emit!(HookConfigUpdated {
            mint: config.mint,
            cooldown_seconds: config.cooldown_seconds,
            fee_bps: config.fee_bps,
        });

        Ok(())
    }

    /// Enable or disable the hook (admin only)
    pub fn set_hook_active(ctx: Context<UpdateHookConfig>, is_active: bool) -> Result<()> {
        ctx.accounts.hook_config.is_active = is_active;

        emit!(HookActiveStatusChanged {
            mint: ctx.accounts.hook_config.mint,
            is_active,
        });

        Ok(())
    }

    /// Withdraw collected fees to fee collector (admin only)
    pub fn withdraw_fees(ctx: Context<WithdrawFees>) -> Result<()> {
        let config = &ctx.accounts.hook_config;
        let fees_to_withdraw = config.total_fees_collected;

        require!(fees_to_withdraw > 0, HookError::NoFeesToWithdraw);

        // Note: Actual token transfer would require additional accounts
        // This is a placeholder for the fee withdrawal logic

        emit!(FeesWithdrawn {
            mint: config.mint,
            amount: fees_to_withdraw,
            collector: config.fee_collector,
        });

        Ok(())
    }
}

// ============================================================================
// Account Structures
// ============================================================================

#[account]
#[derive(InitSpace)]
pub struct HookConfig {
    /// Associated mint
    pub mint: Pubkey,
    /// Admin authority
    pub authority: Pubkey,
    /// Cooldown between transfers (seconds)
    pub cooldown_seconds: i64,
    /// Minimum transfer amount
    pub min_transfer_amount: u64,
    /// Maximum transfer amount (0 = unlimited)
    pub max_transfer_amount: u64,
    /// Fee in basis points
    pub fee_bps: u16,
    /// Fee collector address
    pub fee_collector: Pubkey,
    /// Total number of transfers
    pub total_transfers: u64,
    /// Total volume transferred
    pub total_volume: u64,
    /// Total fees collected
    pub total_fees_collected: u64,
    /// Whether the hook is active
    pub is_active: bool,
    /// PDA bump
    pub bump: u8,
}

#[account]
#[derive(InitSpace)]
pub struct TransferRecord {
    /// Source token account
    pub source: Pubkey,
    /// Destination token account
    pub destination: Pubkey,
    /// Last transfer amount
    pub amount: u64,
    /// Last fee amount
    pub fee: u64,
    /// Timestamp of last transfer
    pub last_transfer_time: i64,
    /// Number of transfers for this pair
    pub transfer_count: u64,
    /// PDA bump
    pub bump: u8,
}

// ============================================================================
// Context Structures
// ============================================================================

#[derive(Accounts)]
pub struct InitializeHookConfig<'info> {
    #[account(
        init,
        payer = authority,
        space = 8 + HookConfig::INIT_SPACE,
        seeds = [HOOK_CONFIG_SEED, mint.key().as_ref()],
        bump,
    )]
    pub hook_config: Account<'info, HookConfig>,

    pub mint: InterfaceAccount<'info, Mint>,

    /// CHECK: Fee collector address
    pub fee_collector: UncheckedAccount<'info>,

    #[account(mut)]
    pub authority: Signer<'info>,

    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct InitializeExtraAccountMetaList<'info> {
    /// CHECK: Extra account metas PDA
    #[account(
        init,
        payer = payer,
        space = ExtraAccountMetaList::size_of(2)?, // 2 extra accounts
        seeds = [EXTRA_ACCOUNT_METAS_SEED, mint.key().as_ref()],
        bump,
    )]
    pub extra_account_metas: UncheckedAccount<'info>,

    pub mint: InterfaceAccount<'info, Mint>,

    #[account(mut)]
    pub payer: Signer<'info>,

    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
#[instruction(amount: u64)]
pub struct TransferHook<'info> {
    pub source_token: InterfaceAccount<'info, TokenAccount>,

    pub mint: InterfaceAccount<'info, Mint>,

    pub destination_token: InterfaceAccount<'info, TokenAccount>,

    #[account(
        mut,
        seeds = [HOOK_CONFIG_SEED, mint.key().as_ref()],
        bump = hook_config.bump,
    )]
    pub hook_config: Account<'info, HookConfig>,

    #[account(
        init_if_needed,
        payer = payer,
        space = 8 + TransferRecord::INIT_SPACE,
        seeds = [
            TRANSFER_RECORD_SEED,
            source_token.key().as_ref(),
            destination_token.key().as_ref()
        ],
        bump,
    )]
    pub transfer_record: Account<'info, TransferRecord>,

    /// CHECK: Extra account metas
    pub extra_account_metas: UncheckedAccount<'info>,

    #[account(mut)]
    pub payer: Signer<'info>,

    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct UpdateHookConfig<'info> {
    #[account(
        mut,
        seeds = [HOOK_CONFIG_SEED, hook_config.mint.as_ref()],
        bump = hook_config.bump,
        has_one = authority @ HookError::Unauthorized,
    )]
    pub hook_config: Account<'info, HookConfig>,

    pub authority: Signer<'info>,
}

#[derive(Accounts)]
pub struct WithdrawFees<'info> {
    #[account(
        seeds = [HOOK_CONFIG_SEED, hook_config.mint.as_ref()],
        bump = hook_config.bump,
        has_one = authority @ HookError::Unauthorized,
    )]
    pub hook_config: Account<'info, HookConfig>,

    /// CHECK: Fee collector
    #[account(mut)]
    pub fee_collector: UncheckedAccount<'info>,

    pub authority: Signer<'info>,
}

// ============================================================================
// Events
// ============================================================================

#[event]
pub struct HookConfigInitialized {
    pub mint: Pubkey,
    pub cooldown_seconds: i64,
    pub fee_bps: u16,
}

#[event]
pub struct ExtraAccountMetasInitialized {
    pub mint: Pubkey,
}

#[event]
pub struct TransferExecuted {
    pub mint: Pubkey,
    pub source: Pubkey,
    pub destination: Pubkey,
    pub amount: u64,
    pub fee: u64,
}

#[event]
pub struct HookConfigUpdated {
    pub mint: Pubkey,
    pub cooldown_seconds: i64,
    pub fee_bps: u16,
}

#[event]
pub struct HookActiveStatusChanged {
    pub mint: Pubkey,
    pub is_active: bool,
}

#[event]
pub struct FeesWithdrawn {
    pub mint: Pubkey,
    pub amount: u64,
    pub collector: Pubkey,
}

// ============================================================================
// Errors
// ============================================================================

#[error_code]
pub enum HookError {
    #[msg("Unauthorized access")]
    Unauthorized,
    #[msg("Transfer hook is disabled")]
    HookDisabled,
    #[msg("Invalid cooldown period")]
    InvalidCooldown,
    #[msg("Invalid amount range")]
    InvalidAmountRange,
    #[msg("Fee exceeds maximum (10%)")]
    FeeTooHigh,
    #[msg("Amount below minimum")]
    AmountBelowMinimum,
    #[msg("Amount above maximum")]
    AmountAboveMaximum,
    #[msg("Cooldown period active")]
    CooldownActive,
    #[msg("No fees to withdraw")]
    NoFeesToWithdraw,
    #[msg("Arithmetic overflow")]
    Overflow,
}
