//! Solana Client for Celtic NFT Program
//!
//! Handles interaction with the Celtic NFT Solana program

use solana_client::rpc_client::RpcClient;
use solana_sdk::{
    commitment_config::CommitmentConfig,
    pubkey::Pubkey,
    signature::{Keypair, Signature},
    signer::Signer,
    transaction::Transaction,
};
use std::str::FromStr;
use std::sync::Arc;

/// Celtic NFT Solana client
pub struct CelticNftClient {
    rpc_client: RpcClient,
    relayer_keypair: Arc<Keypair>,
    program_id: Pubkey,
}

impl CelticNftClient {
    /// Create a new Celtic NFT client
    pub fn new(
        rpc_url: &str,
        relayer_keypair: Keypair,
        program_id: &str,
    ) -> anyhow::Result<Self> {
        let rpc_client = RpcClient::new_with_commitment(
            rpc_url.to_string(),
            CommitmentConfig::confirmed(),
        );

        let program_id = Pubkey::from_str(program_id)?;

        Ok(Self {
            rpc_client,
            relayer_keypair: Arc::new(relayer_keypair),
            program_id,
        })
    }

    /// Get the config PDA
    pub fn get_config_pda(&self) -> (Pubkey, u8) {
        Pubkey::find_program_address(&[b"celtic_nft_config"], &self.program_id)
    }

    /// Get the collection info PDA
    pub fn get_collection_info_pda(&self, collection: &Pubkey) -> (Pubkey, u8) {
        Pubkey::find_program_address(
            &[b"collection_info", collection.as_ref()],
            &self.program_id,
        )
    }

    /// Get the NFT data PDA
    pub fn get_nft_data_pda(&self, asset: &Pubkey) -> (Pubkey, u8) {
        Pubkey::find_program_address(&[b"nft_data", asset.as_ref()], &self.program_id)
    }

    /// Get recent blockhash
    pub async fn get_recent_blockhash(&self) -> anyhow::Result<solana_sdk::hash::Hash> {
        Ok(self.rpc_client.get_latest_blockhash()?)
    }

    /// Send and confirm transaction
    pub async fn send_and_confirm_transaction(
        &self,
        transaction: &Transaction,
    ) -> anyhow::Result<Signature> {
        let signature = self.rpc_client.send_and_confirm_transaction(transaction)?;
        Ok(signature)
    }

    /// Get relayer public key
    pub fn relayer_pubkey(&self) -> Pubkey {
        self.relayer_keypair.pubkey()
    }

    /// Get the keypair for signing
    pub fn relayer_keypair(&self) -> &Keypair {
        &self.relayer_keypair
    }

    /// Get program ID
    pub fn program_id(&self) -> Pubkey {
        self.program_id
    }

    /// Check if an account exists
    pub async fn account_exists(&self, pubkey: &Pubkey) -> anyhow::Result<bool> {
        match self.rpc_client.get_account(pubkey) {
            Ok(_) => Ok(true),
            Err(_) => Ok(false),
        }
    }

    /// Get account balance
    pub async fn get_balance(&self, pubkey: &Pubkey) -> anyhow::Result<u64> {
        Ok(self.rpc_client.get_balance(pubkey)?)
    }
}

/// Mint request for the relayer
#[derive(Debug, Clone)]
pub struct RelayerMintRequest {
    /// SpacetimeDB pending mint ID
    pub pending_mint_id: u64,
    /// NFT type (character, territory, etc.)
    pub nft_type: NftMintType,
    /// Owner wallet address (Solana pubkey)
    pub owner: Pubkey,
    /// Collection to mint into
    pub collection: Pubkey,
    /// Metadata URI (after upload)
    pub metadata_uri: String,
    /// NFT name
    pub name: String,
}

/// NFT mint type with type-specific data
#[derive(Debug, Clone)]
pub enum NftMintType {
    Character {
        clan: String,
        character_class: String,
    },
    Territory {
        region_x: i32,
        region_z: i32,
        terrain_type: String,
    },
    Achievement {
        achievement_id: u32,
        rarity: String,
    },
}

/// Mint result
#[derive(Debug, Clone)]
pub struct MintResult {
    pub pending_mint_id: u64,
    pub signature: Signature,
    pub asset_pubkey: Pubkey,
}
