//! Relayer Configuration

use std::env;

/// Configuration for the NFT Relayer service
#[derive(Debug, Clone)]
pub struct RelayerConfig {
    /// SpacetimeDB WebSocket URL
    pub spacetimedb_url: String,
    /// SpacetimeDB module name
    pub spacetimedb_module: String,
    /// Solana RPC URL
    pub solana_rpc_url: String,
    /// Path to relayer keypair file
    pub relayer_keypair_path: String,
    /// Celtic NFT program ID
    pub celtic_nft_program_id: String,
    /// Arweave gateway URL
    pub arweave_gateway: String,
    /// Arweave wallet path (for uploads)
    pub arweave_wallet_path: Option<String>,
    /// IPFS gateway URL (fallback)
    pub ipfs_gateway: Option<String>,
    /// Maximum retries for failed mints
    pub max_retries: u32,
    /// Retry delay in milliseconds
    pub retry_delay_ms: u64,
    /// Batch size for processing pending mints
    pub batch_size: usize,
}

impl RelayerConfig {
    /// Load configuration from environment variables
    pub fn from_env() -> anyhow::Result<Self> {
        Ok(Self {
            spacetimedb_url: env::var("SPACETIMEDB_URL")
                .unwrap_or_else(|_| "ws://localhost:3000".to_string()),
            spacetimedb_module: env::var("SPACETIMEDB_MODULE")
                .unwrap_or_else(|_| "tuath-game".to_string()),
            solana_rpc_url: env::var("SOLANA_RPC_URL")
                .unwrap_or_else(|_| "https://api.devnet.solana.com".to_string()),
            relayer_keypair_path: env::var("RELAYER_KEYPAIR_PATH")
                .map_err(|_| anyhow::anyhow!("RELAYER_KEYPAIR_PATH is required"))?,
            celtic_nft_program_id: env::var("CELTIC_NFT_PROGRAM_ID")
                .unwrap_or_else(|_| "CELTicNFT11111111111111111111111111111111".to_string()),
            arweave_gateway: env::var("ARWEAVE_GATEWAY")
                .unwrap_or_else(|_| "https://arweave.net".to_string()),
            arweave_wallet_path: env::var("ARWEAVE_WALLET_PATH").ok(),
            ipfs_gateway: env::var("IPFS_GATEWAY").ok(),
            max_retries: env::var("MAX_RETRIES")
                .ok()
                .and_then(|v| v.parse().ok())
                .unwrap_or(3),
            retry_delay_ms: env::var("RETRY_DELAY_MS")
                .ok()
                .and_then(|v| v.parse().ok())
                .unwrap_or(5000),
            batch_size: env::var("BATCH_SIZE")
                .ok()
                .and_then(|v| v.parse().ok())
                .unwrap_or(10),
        })
    }
}
