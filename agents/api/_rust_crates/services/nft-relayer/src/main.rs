//! Celtic NFT Relayer Service
//!
//! Bridges SpacetimeDB game state to Solana NFTs:
//! 1. Subscribes to PendingMint table in SpacetimeDB
//! 2. Uploads metadata to Arweave/IPFS
//! 3. Calls Celtic-NFT Solana program to mint
//! 4. Updates SpacetimeDB with transaction confirmation

use dotenvy::dotenv;
use std::env;
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};

mod config;
mod metadata;
mod relayer;
mod solana_client;
mod spacetime_client;

use config::RelayerConfig;
use relayer::NftRelayer;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    dotenv().ok();

    // Initialize tracing
    tracing_subscriber::registry()
        .with(tracing_subscriber::fmt::layer())
        .with(
            tracing_subscriber::EnvFilter::try_from_default_env()
                .unwrap_or_else(|_| "celtic_nft_relayer=debug,spacetimedb_sdk=info".into()),
        )
        .init();

    tracing::info!("Starting Celtic NFT Relayer Service");

    // Load configuration
    let config = RelayerConfig::from_env()?;

    tracing::info!("SpacetimeDB: {}", config.spacetimedb_url);
    tracing::info!("Solana RPC: {}", config.solana_rpc_url);
    tracing::info!("Relayer Authority: {}", config.relayer_keypair_path);

    // Create and start relayer
    let relayer = NftRelayer::new(config).await?;

    tracing::info!("Relayer initialized, starting subscription loop...");

    // Run the relayer (blocks until shutdown)
    relayer.run().await?;

    Ok(())
}
