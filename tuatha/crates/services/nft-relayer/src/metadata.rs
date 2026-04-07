//! NFT Metadata Generation and Upload
//!
//! Creates Metaplex-compatible JSON metadata and uploads to Arweave/IPFS

use serde::{Deserialize, Serialize};

/// Metaplex-compatible NFT metadata
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct NftMetadata {
    pub name: String,
    pub symbol: String,
    pub description: String,
    pub image: String,
    pub animation_url: Option<String>,
    pub external_url: Option<String>,
    pub attributes: Vec<MetadataAttribute>,
    pub properties: MetadataProperties,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MetadataAttribute {
    pub trait_type: String,
    pub value: serde_json::Value,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub display_type: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MetadataProperties {
    pub files: Vec<MetadataFile>,
    pub category: String,
    pub creators: Vec<MetadataCreator>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MetadataFile {
    pub uri: String,
    #[serde(rename = "type")]
    pub file_type: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub cdn: Option<bool>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MetadataCreator {
    pub address: String,
    pub share: u8,
}

/// Metadata uploader trait
#[async_trait::async_trait]
pub trait MetadataUploader: Send + Sync {
    /// Upload metadata JSON and return the URI
    async fn upload_metadata(&self, metadata: &NftMetadata) -> anyhow::Result<String>;

    /// Upload an image file and return the URI
    async fn upload_image(&self, data: &[u8], content_type: &str) -> anyhow::Result<String>;
}

/// Arweave metadata uploader
pub struct ArweaveUploader {
    gateway: String,
    client: reqwest::Client,
}

impl ArweaveUploader {
    pub fn new(gateway: String) -> Self {
        Self {
            gateway,
            client: reqwest::Client::new(),
        }
    }
}

#[async_trait::async_trait]
impl MetadataUploader for ArweaveUploader {
    async fn upload_metadata(&self, metadata: &NftMetadata) -> anyhow::Result<String> {
        let json = serde_json::to_string(metadata)?;

        // For production, this would use Bundlr/Irys or direct Arweave upload
        // For now, we'll use a placeholder that could be replaced with actual implementation
        tracing::info!("Uploading metadata to Arweave: {} bytes", json.len());

        // In production: upload to Arweave via Bundlr/Irys
        // let response = self.client
        //     .post(&format!("{}/tx", self.gateway))
        //     .body(json)
        //     .send()
        //     .await?;

        // Placeholder URI format for development
        let hash = format!("{:x}", md5::compute(json.as_bytes()));
        Ok(format!("{}/{}", self.gateway, hash))
    }

    async fn upload_image(&self, data: &[u8], content_type: &str) -> anyhow::Result<String> {
        tracing::info!(
            "Uploading image to Arweave: {} bytes, type: {}",
            data.len(),
            content_type
        );

        // Placeholder for development
        let hash = format!("{:x}", md5::compute(data));
        Ok(format!("{}/{}", self.gateway, hash))
    }
}

/// Character NFT metadata builder
pub struct CharacterMetadataBuilder {
    treasury_address: String,
}

impl CharacterMetadataBuilder {
    pub fn new(treasury_address: String) -> Self {
        Self { treasury_address }
    }

    pub fn build(
        &self,
        name: &str,
        clan: &str,
        character_class: &str,
        level: u8,
        image_uri: &str,
    ) -> NftMetadata {
        NftMetadata {
            name: name.to_string(),
            symbol: "CELT".to_string(),
            description: format!(
                "A {} {} of the {} clan in the Celtic MMO. Level {}.",
                character_class, name, clan, level
            ),
            image: image_uri.to_string(),
            animation_url: None,
            external_url: Some("https://tuath.ie".to_string()),
            attributes: vec![
                MetadataAttribute {
                    trait_type: "Clan".to_string(),
                    value: serde_json::Value::String(clan.to_string()),
                    display_type: None,
                },
                MetadataAttribute {
                    trait_type: "Class".to_string(),
                    value: serde_json::Value::String(character_class.to_string()),
                    display_type: None,
                },
                MetadataAttribute {
                    trait_type: "Level".to_string(),
                    value: serde_json::Value::Number(level.into()),
                    display_type: Some("number".to_string()),
                },
                MetadataAttribute {
                    trait_type: "Game".to_string(),
                    value: serde_json::Value::String("Tuath Celtic MMO".to_string()),
                    display_type: None,
                },
            ],
            properties: MetadataProperties {
                files: vec![MetadataFile {
                    uri: image_uri.to_string(),
                    file_type: "image/png".to_string(),
                    cdn: Some(true),
                }],
                category: "image".to_string(),
                creators: vec![MetadataCreator {
                    address: self.treasury_address.clone(),
                    share: 100,
                }],
            },
        }
    }
}

/// Territory NFT metadata builder
pub struct TerritoryMetadataBuilder {
    treasury_address: String,
}

impl TerritoryMetadataBuilder {
    pub fn new(treasury_address: String) -> Self {
        Self { treasury_address }
    }

    pub fn build(
        &self,
        name: &str,
        region_x: i32,
        region_z: i32,
        terrain_type: &str,
        image_uri: &str,
    ) -> NftMetadata {
        NftMetadata {
            name: name.to_string(),
            symbol: "CELT-LAND".to_string(),
            description: format!(
                "Territory deed for {} at coordinates ({}, {}). Terrain: {}.",
                name, region_x, region_z, terrain_type
            ),
            image: image_uri.to_string(),
            animation_url: None,
            external_url: Some("https://tuath.ie".to_string()),
            attributes: vec![
                MetadataAttribute {
                    trait_type: "Region X".to_string(),
                    value: serde_json::Value::Number(region_x.into()),
                    display_type: Some("number".to_string()),
                },
                MetadataAttribute {
                    trait_type: "Region Z".to_string(),
                    value: serde_json::Value::Number(region_z.into()),
                    display_type: Some("number".to_string()),
                },
                MetadataAttribute {
                    trait_type: "Terrain".to_string(),
                    value: serde_json::Value::String(terrain_type.to_string()),
                    display_type: None,
                },
                MetadataAttribute {
                    trait_type: "Type".to_string(),
                    value: serde_json::Value::String("Territory Deed".to_string()),
                    display_type: None,
                },
            ],
            properties: MetadataProperties {
                files: vec![MetadataFile {
                    uri: image_uri.to_string(),
                    file_type: "image/png".to_string(),
                    cdn: Some(true),
                }],
                category: "image".to_string(),
                creators: vec![MetadataCreator {
                    address: self.treasury_address.clone(),
                    share: 100,
                }],
            },
        }
    }
}

// Simple MD5 implementation for hashing (placeholder)
mod md5 {
    pub fn compute(data: &[u8]) -> [u8; 16] {
        use std::collections::hash_map::DefaultHasher;
        use std::hash::{Hash, Hasher};

        let mut hasher = DefaultHasher::new();
        data.hash(&mut hasher);
        let hash = hasher.finish();

        let mut result = [0u8; 16];
        result[0..8].copy_from_slice(&hash.to_le_bytes());
        result[8..16].copy_from_slice(&hash.to_be_bytes());
        result
    }
}
