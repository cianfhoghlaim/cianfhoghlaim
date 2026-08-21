//! SpacetimeDB Client for NFT Relayer
//!
//! Subscribes to pending mint requests and updates status

use serde::{Deserialize, Serialize};

/// Pending mint request from SpacetimeDB
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PendingMint {
    /// Unique ID
    pub id: u64,
    /// Player ID who requested the mint
    pub player_id: u64,
    /// Type of NFT to mint
    pub nft_type: String,
    /// Type-specific data as JSON
    pub type_data: String,
    /// Solana wallet address (base58)
    pub wallet_address: String,
    /// Request timestamp
    pub created_at: i64,
    /// Number of retry attempts
    pub retry_count: u32,
    /// Last error message (if any)
    pub last_error: Option<String>,
    /// Status: pending, processing, completed, failed
    pub status: String,
}

/// Mint confirmation to send back to SpacetimeDB
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MintConfirmation {
    /// Pending mint ID
    pub pending_mint_id: u64,
    /// Solana transaction signature
    pub transaction_signature: String,
    /// Minted asset pubkey
    pub asset_pubkey: String,
    /// Metadata URI
    pub metadata_uri: String,
    /// Confirmation timestamp
    pub confirmed_at: i64,
}

/// SpacetimeDB client for the relayer
pub struct SpacetimeClient {
    url: String,
    module: String,
}

impl SpacetimeClient {
    pub fn new(url: String, module: String) -> Self {
        Self { url, module }
    }

    /// Connect to SpacetimeDB and subscribe to pending mints
    pub async fn connect(&self) -> anyhow::Result<()> {
        tracing::info!(
            "Connecting to SpacetimeDB at {} (module: {})",
            self.url,
            self.module
        );

        // In production, this would use the SpacetimeDB SDK to:
        // 1. Connect via WebSocket
        // 2. Subscribe to the PendingMint table
        // 3. Receive callbacks when new mints are requested

        Ok(())
    }

    /// Get pending mints that need processing
    pub async fn get_pending_mints(&self) -> anyhow::Result<Vec<PendingMint>> {
        // In production, this would query SpacetimeDB for pending mints
        // SELECT * FROM PendingMint WHERE status = 'pending' ORDER BY created_at LIMIT 10

        Ok(vec![])
    }

    /// Mark a mint as processing
    pub async fn mark_processing(&self, pending_mint_id: u64) -> anyhow::Result<()> {
        tracing::debug!("Marking mint {} as processing", pending_mint_id);
        // In production: UPDATE PendingMint SET status = 'processing' WHERE id = ?
        Ok(())
    }

    /// Confirm a successful mint
    pub async fn confirm_mint(&self, confirmation: MintConfirmation) -> anyhow::Result<()> {
        tracing::info!(
            "Confirming mint {} with signature {}",
            confirmation.pending_mint_id,
            confirmation.transaction_signature
        );

        // In production, this would call a SpacetimeDB reducer:
        // call confirm_nft_mint(pending_mint_id, transaction_signature, asset_pubkey, metadata_uri)

        Ok(())
    }

    /// Mark a mint as failed
    pub async fn mark_failed(
        &self,
        pending_mint_id: u64,
        error: &str,
        retry_count: u32,
    ) -> anyhow::Result<()> {
        tracing::warn!(
            "Marking mint {} as failed (attempt {}): {}",
            pending_mint_id,
            retry_count,
            error
        );

        // In production: UPDATE PendingMint SET status = 'failed', last_error = ?, retry_count = ?

        Ok(())
    }
}
