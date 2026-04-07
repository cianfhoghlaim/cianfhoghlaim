//! Main NFT Relayer Logic
//!
//! Orchestrates the minting process:
//! 1. Listen for pending mints from SpacetimeDB
//! 2. Upload metadata to Arweave
//! 3. Call Solana program to mint
//! 4. Update SpacetimeDB with confirmation

use std::sync::Arc;
use std::time::Duration;
use solana_sdk::signature::read_keypair_file;

use crate::config::RelayerConfig;
use crate::metadata::{ArweaveUploader, CharacterMetadataBuilder, MetadataUploader, TerritoryMetadataBuilder};
use crate::solana_client::{CelticNftClient, NftMintType, RelayerMintRequest};
use crate::spacetime_client::{MintConfirmation, SpacetimeClient};

/// NFT Relayer service
pub struct NftRelayer {
    config: RelayerConfig,
    spacetime_client: SpacetimeClient,
    solana_client: CelticNftClient,
    metadata_uploader: Arc<dyn MetadataUploader>,
    character_metadata: CharacterMetadataBuilder,
    territory_metadata: TerritoryMetadataBuilder,
}

impl NftRelayer {
    /// Create a new NFT relayer
    pub async fn new(config: RelayerConfig) -> anyhow::Result<Self> {
        // Load relayer keypair
        let relayer_keypair = read_keypair_file(&config.relayer_keypair_path)
            .map_err(|e| anyhow::anyhow!("Failed to load relayer keypair: {}", e))?;

        // Create SpacetimeDB client
        let spacetime_client = SpacetimeClient::new(
            config.spacetimedb_url.clone(),
            config.spacetimedb_module.clone(),
        );

        // Create Solana client
        let solana_client = CelticNftClient::new(
            &config.solana_rpc_url,
            relayer_keypair,
            &config.celtic_nft_program_id,
        )?;

        // Create metadata uploader
        let metadata_uploader: Arc<dyn MetadataUploader> = Arc::new(ArweaveUploader::new(
            config.arweave_gateway.clone(),
        ));

        // Treasury address for NFT creators
        let treasury_address = solana_client.relayer_pubkey().to_string();
        let character_metadata = CharacterMetadataBuilder::new(treasury_address.clone());
        let territory_metadata = TerritoryMetadataBuilder::new(treasury_address);

        Ok(Self {
            config,
            spacetime_client,
            solana_client,
            metadata_uploader,
            character_metadata,
            territory_metadata,
        })
    }

    /// Run the relayer loop
    pub async fn run(&self) -> anyhow::Result<()> {
        // Connect to SpacetimeDB
        self.spacetime_client.connect().await?;

        tracing::info!("Relayer running, polling for pending mints...");

        loop {
            // Process pending mints
            match self.process_pending_mints().await {
                Ok(processed) => {
                    if processed > 0 {
                        tracing::info!("Processed {} pending mints", processed);
                    }
                }
                Err(e) => {
                    tracing::error!("Error processing pending mints: {}", e);
                }
            }

            // Wait before next poll
            tokio::time::sleep(Duration::from_secs(5)).await;
        }
    }

    /// Process all pending mints
    async fn process_pending_mints(&self) -> anyhow::Result<usize> {
        let pending = self.spacetime_client.get_pending_mints().await?;

        if pending.is_empty() {
            return Ok(0);
        }

        tracing::info!("Found {} pending mints to process", pending.len());

        let mut processed = 0;

        for mint in pending.iter().take(self.config.batch_size) {
            match self.process_single_mint(mint.id, &mint.nft_type, &mint.type_data, &mint.wallet_address).await {
                Ok(_) => {
                    processed += 1;
                }
                Err(e) => {
                    tracing::error!("Failed to process mint {}: {}", mint.id, e);
                    self.spacetime_client
                        .mark_failed(mint.id, &e.to_string(), mint.retry_count + 1)
                        .await?;
                }
            }
        }

        Ok(processed)
    }

    /// Process a single mint request
    async fn process_single_mint(
        &self,
        pending_mint_id: u64,
        nft_type: &str,
        type_data: &str,
        wallet_address: &str,
    ) -> anyhow::Result<()> {
        tracing::info!(
            "Processing mint {}: type={}, wallet={}",
            pending_mint_id,
            nft_type,
            wallet_address
        );

        // Mark as processing
        self.spacetime_client.mark_processing(pending_mint_id).await?;

        // Parse type data
        let type_data: serde_json::Value = serde_json::from_str(type_data)?;

        // Generate and upload metadata based on NFT type
        let (metadata_uri, mint_type) = match nft_type {
            "character" => {
                let clan = type_data["clan"].as_str().unwrap_or("unknown");
                let character_class = type_data["class"].as_str().unwrap_or("warrior");
                let level = type_data["level"].as_u64().unwrap_or(1) as u8;
                let name = type_data["name"].as_str().unwrap_or("Celtic Hero");
                let image_uri = type_data["image_uri"].as_str().unwrap_or("");

                let metadata = self.character_metadata.build(
                    name,
                    clan,
                    character_class,
                    level,
                    image_uri,
                );

                let uri = self.metadata_uploader.upload_metadata(&metadata).await?;

                (uri, NftMintType::Character {
                    clan: clan.to_string(),
                    character_class: character_class.to_string(),
                })
            }
            "territory" => {
                let region_x = type_data["region_x"].as_i64().unwrap_or(0) as i32;
                let region_z = type_data["region_z"].as_i64().unwrap_or(0) as i32;
                let terrain = type_data["terrain"].as_str().unwrap_or("plains");
                let name = type_data["name"].as_str().unwrap_or("Celtic Territory");
                let image_uri = type_data["image_uri"].as_str().unwrap_or("");

                let metadata = self.territory_metadata.build(
                    name,
                    region_x,
                    region_z,
                    terrain,
                    image_uri,
                );

                let uri = self.metadata_uploader.upload_metadata(&metadata).await?;

                (uri, NftMintType::Territory {
                    region_x,
                    region_z,
                    terrain_type: terrain.to_string(),
                })
            }
            _ => {
                return Err(anyhow::anyhow!("Unknown NFT type: {}", nft_type));
            }
        };

        tracing::info!("Metadata uploaded to: {}", metadata_uri);

        // Parse owner wallet
        let owner = wallet_address.parse()
            .map_err(|_| anyhow::anyhow!("Invalid wallet address: {}", wallet_address))?;

        // TODO: In production, this would:
        // 1. Build the Solana transaction for mint_with_relayer instruction
        // 2. Sign with the relayer keypair
        // 3. Send and confirm transaction
        // 4. Return the signature and asset pubkey

        // Placeholder for the actual mint transaction
        let signature = "placeholder_signature";
        let asset_pubkey = "placeholder_asset";

        tracing::info!(
            "Mint {} completed: signature={}, asset={}",
            pending_mint_id,
            signature,
            asset_pubkey
        );

        // Confirm the mint in SpacetimeDB
        self.spacetime_client
            .confirm_mint(MintConfirmation {
                pending_mint_id,
                transaction_signature: signature.to_string(),
                asset_pubkey: asset_pubkey.to_string(),
                metadata_uri,
                confirmed_at: chrono::Utc::now().timestamp(),
            })
            .await?;

        Ok(())
    }
}
