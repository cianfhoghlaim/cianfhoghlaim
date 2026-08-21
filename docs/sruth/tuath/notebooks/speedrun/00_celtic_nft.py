"""
Challenge 0: Tokenization - Tuath Celtic Creature NFT Implementation

SpeedRunEthereum Challenge: https://speedrunethereum.com/challenge/tokenization

Learning Objectives:
- Implement ERC721 NFTs for Celtic mythology creatures
- Extend Metaplex Core with creature attributes
- Generate on-chain SVG artwork
- Sync NFT inventory with SpacetimeDB game state

Project Integration:
- Extends existing celtic-nft Solana program
- Integrates with tuath game client (Babylon.js/Godot)
- Uses mythology database from dlt_sources/mythology/
- WGPU shaders for creature visualization

Usage:
    marimo edit 00_celtic_nft.py
    marimo run 00_celtic_nft.py
"""

import marimo

__generated_with = "0.10.14"
app = marimo.App(width="full")


@app.cell
def _():
    """Setup and imports."""
    import marimo as mo

    mo.md("""
    # Challenge 0: Celtic Creature NFTs

    > Build NFTs that represent Celtic mythology characters for the tuath educational MMO

    ## Overview

    This notebook implements NFTs for the **tuath** Celtic educational game:

    **Creatures from Celtic Mythology:**
    - **Irish**: Cú Chulainn, Fionn mac Cumhaill, Tuatha Dé Danann
    - **Welsh**: Pwyll, Rhiannon, Mabinogi characters
    - **Scottish**: Cailleach, Selkies, Highland spirits

    **What you'll build:**
    - ERC721 Celtic Creature contract (Ethereum)
    - Metaplex Core extension (Solana)
    - On-chain SVG generation
    - SpacetimeDB inventory sync
    """)
    return (mo,)


@app.cell
def _(mo):
    """Celtic Creature Types."""
    mo.md("""
    ## Part 1: Celtic Creature Design

    ### Creature Categories

    | Type | Examples | Rarity Distribution |
    |------|----------|---------------------|
    | **Gods** | Lugh, Danu, Manannán | 5% Legendary |
    | **Heroes** | Cú Chulainn, Fionn | 15% Rare |
    | **Creatures** | Selkies, Púca | 30% Uncommon |
    | **Spirits** | Banshee, Will-o'-wisp | 50% Common |

    ### Attributes

    ```python
    @dataclass
    class CelticCreature:
        name: str                    # "Cú Chulainn"
        tradition: Tradition         # IRISH | WELSH | SCOTTISH
        creature_type: CreatureType  # GOD | HERO | CREATURE | SPIRIT
        attributes: Attributes       # strength, wisdom, magic (0-100)
        rarity: Rarity              # COMMON | UNCOMMON | RARE | LEGENDARY
        special_ability: str         # "Ríastrad" (warp spasm)
    ```
    """)
    return ()


@app.cell
def _(mo):
    """Mythology Database Preview."""
    # Sample creatures from Irish mythology
    irish_creatures = [
        {
            "name": "Cú Chulainn",
            "type": "Hero",
            "tradition": "Irish",
            "cycle": "Ulster Cycle",
            "strength": 95,
            "wisdom": 70,
            "magic": 80,
            "rarity": "Legendary",
            "ability": "Ríastrad (Warp Spasm)",
        },
        {
            "name": "Fionn mac Cumhaill",
            "type": "Hero",
            "tradition": "Irish",
            "cycle": "Fenian Cycle",
            "strength": 85,
            "wisdom": 90,
            "magic": 75,
            "rarity": "Legendary",
            "ability": "Salmon of Knowledge",
        },
        {
            "name": "Lugh Lámhfhada",
            "type": "God",
            "tradition": "Irish",
            "cycle": "Mythological Cycle",
            "strength": 90,
            "wisdom": 95,
            "magic": 100,
            "rarity": "Legendary",
            "ability": "Master of All Arts",
        },
        {
            "name": "Púca",
            "type": "Creature",
            "tradition": "Irish",
            "cycle": "Folklore",
            "strength": 40,
            "wisdom": 60,
            "magic": 70,
            "rarity": "Uncommon",
            "ability": "Shapeshifting",
        },
        {
            "name": "Banshee",
            "type": "Spirit",
            "tradition": "Irish",
            "cycle": "Folklore",
            "strength": 20,
            "wisdom": 80,
            "magic": 90,
            "rarity": "Rare",
            "ability": "Death Wail",
        },
    ]

    import pandas as pd

    df = pd.DataFrame(irish_creatures)

    mo.vstack(
        [
            mo.md("### Irish Mythology Database (Sample)"),
            mo.ui.table(df),
            mo.md(
                "*Full database available in `sruth/tuath/dlt_sources/mythology/celtic_mythology.py`*"
            ),
        ]
    )
    return df, irish_creatures, pd


@app.cell
def _(mo):
    """Creature Selector."""
    traditions = ["Irish", "Welsh", "Scottish"]
    tradition_select = mo.ui.dropdown(
        options=traditions,
        value="Irish",
        label="Tradition",
    )

    creature_types = ["God", "Hero", "Creature", "Spirit"]
    type_select = mo.ui.dropdown(
        options=creature_types,
        value="Hero",
        label="Type",
    )

    mo.hstack(
        [
            mo.md("**Create New Creature:**"),
            tradition_select,
            type_select,
        ],
        gap=2,
    )
    return creature_types, tradition_select, traditions, type_select


@app.cell
def _(mo, tradition_select, type_select):
    """Creature attribute sliders."""
    strength = mo.ui.slider(start=0, stop=100, value=50, label="Strength")
    wisdom = mo.ui.slider(start=0, stop=100, value=50, label="Wisdom")
    magic = mo.ui.slider(start=0, stop=100, value=50, label="Magic")

    creature_name = mo.ui.text(
        value="",
        label="Creature Name",
        placeholder="Enter mythological name...",
    )

    mo.vstack(
        [
            mo.md(f"### Design Your {type_select.value} ({tradition_select.value})"),
            creature_name,
            mo.hstack([strength, wisdom, magic], gap=2),
        ]
    )
    return creature_name, magic, strength, wisdom


@app.cell
def _(creature_name, magic, mo, strength, tradition_select, type_select, wisdom):
    """SVG Preview."""

    # Generate SVG based on attributes
    def generate_creature_svg(
        name: str, tradition: str, ctype: str, str_val: int, wis_val: int, mag_val: int
    ) -> str:
        """Generate on-chain SVG for creature NFT."""

        # Color schemes by tradition
        colors = {
            "Irish": {"primary": "#228B22", "secondary": "#FFD700", "bg": "#1a1a2e"},
            "Welsh": {"primary": "#C41E3A", "secondary": "#FFFFFF", "bg": "#1a1a2e"},
            "Scottish": {"primary": "#0065BF", "secondary": "#FFFFFF", "bg": "#1a1a2e"},
        }

        # Type symbols
        symbols = {
            "God": "M50,20 L60,45 L85,45 L65,60 L75,85 L50,70 L25,85 L35,60 L15,45 L40,45 Z",  # Star
            "Hero": "M50,15 L50,85 M30,35 L70,35 M25,50 L75,50",  # Sword
            "Creature": "M50,20 Q80,50 50,80 Q20,50 50,20",  # Beast shape
            "Spirit": "M50,20 Q30,40 50,50 Q70,40 50,20 M50,50 Q40,70 50,80 Q60,70 50,50",  # Ghost
        }

        c = colors.get(tradition, colors["Irish"])
        symbol = symbols.get(ctype, symbols["Spirit"])

        # Attribute bars
        str_width = str_val * 0.8
        wis_width = wis_val * 0.8
        mag_width = mag_val * 0.8

        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 120">
  <!-- Background -->
  <rect width="100" height="120" fill="{c["bg"]}"/>

  <!-- Celtic knotwork border -->
  <rect x="2" y="2" width="96" height="116" fill="none"
        stroke="{c["primary"]}" stroke-width="2"/>
  <rect x="5" y="5" width="90" height="110" fill="none"
        stroke="{c["secondary"]}" stroke-width="1"/>

  <!-- Type symbol -->
  <g transform="translate(0,5)">
    <path d="{symbol}" fill="none" stroke="{c["secondary"]}"
          stroke-width="2" opacity="0.8"/>
  </g>

  <!-- Creature name -->
  <text x="50" y="95" text-anchor="middle" fill="{c["secondary"]}"
        font-family="serif" font-size="8" font-weight="bold">
    {name or "Unnamed"}
  </text>

  <!-- Attribute bars -->
  <g transform="translate(10,102)">
    <!-- Strength (red) -->
    <rect x="0" y="0" width="{str_width}" height="4" fill="#FF4444"/>
    <!-- Wisdom (blue) -->
    <rect x="0" y="5" width="{wis_width}" height="4" fill="#4444FF"/>
    <!-- Magic (purple) -->
    <rect x="0" y="10" width="{mag_width}" height="4" fill="#AA44FF"/>
  </g>
</svg>'''
        return svg

    svg_content = generate_creature_svg(
        creature_name.value or "Unnamed Creature",
        tradition_select.value,
        type_select.value,
        strength.value,
        wisdom.value,
        magic.value,
    )

    mo.vstack(
        [
            mo.md("### NFT Preview"),
            mo.Html(f'<div style="width: 200px; height: 240px;">{svg_content}</div>'),
            mo.md(f"""
        **Attributes:**
        - Strength: {strength.value}
        - Wisdom: {wisdom.value}
        - Magic: {magic.value}
        - Tradition: {tradition_select.value}
        - Type: {type_select.value}
        """),
        ]
    )
    return generate_creature_svg, svg_content


@app.cell
def _(mo):
    """Solana Program Extension."""
    mo.md("""
    ## Part 2: Solana Implementation (Metaplex Core)

    ### Extending celtic-nft Program

    The existing `celtic-nft` program in `sruth/tuath/crates/solana/programs/celtic-nft/`
    will be extended with creature-specific attributes:

    ```rust
    // lib.rs - Celtic Creature NFT Program
    use anchor_lang::prelude::*;
    use mpl_core::{
        instructions::CreateV2CpiBuilder,
        types::{Attribute, Plugin, PluginAuthorityPair},
    };

    declare_id!("CeLtIcNFTDevnetAddress11111111111111111111");

    #[program]
    pub mod celtic_nft {
        use super::*;

        pub fn create_creature(
            ctx: Context<CreateCreature>,
            name: String,
            uri: String,
            tradition: Tradition,
            creature_type: CreatureType,
            strength: u8,
            wisdom: u8,
            magic: u8,
        ) -> Result<()> {
            // Create Metaplex Core asset with creature attributes
            let attributes = vec![
                Attribute { key: "tradition".to_string(), value: tradition.to_string() },
                Attribute { key: "type".to_string(), value: creature_type.to_string() },
                Attribute { key: "strength".to_string(), value: strength.to_string() },
                Attribute { key: "wisdom".to_string(), value: wisdom.to_string() },
                Attribute { key: "magic".to_string(), value: magic.to_string() },
            ];

            CreateV2CpiBuilder::new(&ctx.accounts.mpl_core_program)
                .asset(&ctx.accounts.asset)
                .collection(Some(&ctx.accounts.collection))
                .payer(&ctx.accounts.payer)
                .owner(Some(&ctx.accounts.owner))
                .system_program(&ctx.accounts.system_program)
                .name(name)
                .uri(uri)
                .plugins(vec![
                    PluginAuthorityPair {
                        plugin: Plugin::Attributes(mpl_core::types::Attributes {
                            attribute_list: attributes,
                        }),
                        authority: None,
                    },
                ])
                .invoke()?;

            Ok(())
        }
    }

    #[derive(AnchorSerialize, AnchorDeserialize, Clone, Copy)]
    pub enum Tradition {
        Irish,
        Welsh,
        Scottish,
    }

    #[derive(AnchorSerialize, AnchorDeserialize, Clone, Copy)]
    pub enum CreatureType {
        God,
        Hero,
        Creature,
        Spirit,
    }
    ```
    """)
    return ()


@app.cell
def _(mo):
    """Ethereum Contract."""
    mo.md("""
    ## Part 3: Ethereum Implementation (ERC721)

    ### CelticCreatureNFT.sol

    ```solidity
    // SPDX-License-Identifier: MIT
    pragma solidity ^0.8.20;

    import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
    import "@openzeppelin/contracts/utils/Base64.sol";
    import "@openzeppelin/contracts/utils/Strings.sol";

    contract CelticCreatureNFT is ERC721URIStorage {
        using Strings for uint256;
        using Strings for uint8;

        uint256 private _nextTokenId;

        enum Tradition { Irish, Welsh, Scottish }
        enum CreatureType { God, Hero, Creature, Spirit }

        struct Creature {
            string name;
            Tradition tradition;
            CreatureType creatureType;
            uint8 strength;
            uint8 wisdom;
            uint8 magic;
        }

        mapping(uint256 => Creature) public creatures;

        constructor() ERC721("Celtic Creatures", "CELTIC") {}

        function mint(
            address to,
            string memory name,
            Tradition tradition,
            CreatureType creatureType,
            uint8 strength,
            uint8 wisdom,
            uint8 magic
        ) public returns (uint256) {
            uint256 tokenId = _nextTokenId++;

            creatures[tokenId] = Creature({
                name: name,
                tradition: tradition,
                creatureType: creatureType,
                strength: strength,
                wisdom: wisdom,
                magic: magic
            });

            _safeMint(to, tokenId);
            return tokenId;
        }

        function tokenURI(uint256 tokenId) public view override returns (string memory) {
            Creature memory c = creatures[tokenId];

            // Generate on-chain SVG
            string memory svg = _generateSVG(c);

            // Build metadata JSON
            string memory json = Base64.encode(bytes(string(abi.encodePacked(
                '{"name":"', c.name, '",',
                '"description":"Celtic Creature from tuath MMO",',
                '"attributes":[',
                    '{"trait_type":"Tradition","value":"', _traditionName(c.tradition), '"},',
                    '{"trait_type":"Type","value":"', _typeName(c.creatureType), '"},',
                    '{"trait_type":"Strength","value":', c.strength.toString(), '},',
                    '{"trait_type":"Wisdom","value":', c.wisdom.toString(), '},',
                    '{"trait_type":"Magic","value":', c.magic.toString(), '}',
                '],',
                '"image":"data:image/svg+xml;base64,', Base64.encode(bytes(svg)), '"}'
            ))));

            return string(abi.encodePacked("data:application/json;base64,", json));
        }

        function _generateSVG(Creature memory c) internal pure returns (string memory) {
            // SVG generation logic (simplified)
            return string(abi.encodePacked(
                '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">',
                '<rect width="100" height="100" fill="#1a1a2e"/>',
                '<text x="50" y="50" text-anchor="middle" fill="gold">',
                c.name,
                '</text></svg>'
            ));
        }

        function _traditionName(Tradition t) internal pure returns (string memory) {
            if (t == Tradition.Irish) return "Irish";
            if (t == Tradition.Welsh) return "Welsh";
            return "Scottish";
        }

        function _typeName(CreatureType t) internal pure returns (string memory) {
            if (t == CreatureType.God) return "God";
            if (t == CreatureType.Hero) return "Hero";
            if (t == CreatureType.Creature) return "Creature";
            return "Spirit";
        }
    }
    ```
    """)
    return ()


@app.cell
def _(mo):
    """SpacetimeDB Integration."""
    mo.md("""
    ## Part 4: SpacetimeDB Game State Sync

    ### Inventory Table

    The NFT inventory syncs with SpacetimeDB for real-time game state:

    ```rust
    // sruth/tuath/crates/stdb-modules/tuath-game/src/lib.rs

    use spacetimedb::{spacetimedb, Identity, ReducerContext};

    #[spacetimedb(table)]
    pub struct PlayerInventory {
        #[primarykey]
        pub player_id: Identity,
        pub creature_ids: Vec<String>,  // NFT token IDs
        pub equipped_creature: Option<String>,
    }

    #[spacetimedb(table)]
    pub struct CreatureCache {
        #[primarykey]
        pub token_id: String,
        pub name: String,
        pub tradition: u8,
        pub creature_type: u8,
        pub strength: u8,
        pub wisdom: u8,
        pub magic: u8,
        pub owner: Identity,
        pub chain: String,  // "ethereum" or "solana"
    }

    #[spacetimedb(reducer)]
    pub fn sync_creature(
        ctx: ReducerContext,
        token_id: String,
        name: String,
        tradition: u8,
        creature_type: u8,
        strength: u8,
        wisdom: u8,
        magic: u8,
        chain: String,
    ) {
        CreatureCache::insert(CreatureCache {
            token_id: token_id.clone(),
            name,
            tradition,
            creature_type,
            strength,
            wisdom,
            magic,
            owner: ctx.sender,
            chain,
        });

        // Update player inventory
        if let Some(mut inv) = PlayerInventory::filter_by_player_id(&ctx.sender).next() {
            inv.creature_ids.push(token_id);
            PlayerInventory::update_by_player_id(&ctx.sender, inv);
        }
    }

    #[spacetimedb(reducer)]
    pub fn equip_creature(ctx: ReducerContext, token_id: String) {
        if let Some(mut inv) = PlayerInventory::filter_by_player_id(&ctx.sender).next() {
            // Verify ownership
            if inv.creature_ids.contains(&token_id) {
                inv.equipped_creature = Some(token_id);
                PlayerInventory::update_by_player_id(&ctx.sender, inv);
            }
        }
    }
    ```

    ### NFT Relayer Service

    The `nft-relayer` service bridges blockchain NFTs to SpacetimeDB:

    ```
    sruth/tuath/crates/services/nft-relayer/
    ├── src/
    │   ├── main.rs           # Service entrypoint
    │   ├── ethereum.rs       # ERC721 event listener
    │   ├── solana.rs         # Metaplex event listener
    │   └── spacetimedb.rs    # STDB sync client
    ```
    """)
    return ()


@app.cell
def _(mo):
    """Deployment Instructions."""
    mo.md("""
    ## Part 5: Deployment

    ### Local Development

    ```bash
    # 1. Start local Ethereum chain (Anvil)
    cd sruth/shared/blockchain/ethereum
    anvil

    # 2. Deploy Celtic NFT contract
    forge create --rpc-url http://localhost:8545 \\
        --private-key 0xac0974... \\
        src/CelticCreatureNFT.sol:CelticCreatureNFT

    # 3. Start local Solana validator
    solana-test-validator

    # 4. Deploy Anchor program
    cd sruth/tuath/crates/solana
    anchor deploy

    # 5. Start SpacetimeDB
    spacetime start

    # 6. Publish game module
    spacetime publish tuath-game
    ```

    ### Testnet Deployment

    ```bash
    # Ethereum (Base Sepolia)
    forge create --rpc-url https://sepolia.base.org \\
        --private-key $PRIVATE_KEY \\
        --etherscan-api-key $BASESCAN_API_KEY \\
        --verify \\
        src/CelticCreatureNFT.sol:CelticCreatureNFT

    # Solana (Devnet)
    anchor deploy --provider.cluster devnet
    ```
    """)
    return ()


@app.cell
def _(mo):
    """Testing."""
    mo.md("""
    ## Part 6: Testing

    ### Ethereum Tests (Foundry)

    ```solidity
    // test/CelticCreatureNFT.t.sol
    pragma solidity ^0.8.20;

    import "forge-std/Test.sol";
    import "../src/CelticCreatureNFT.sol";

    contract CelticCreatureNFTTest is Test {
        CelticCreatureNFT nft;
        address owner = address(1);

        function setUp() public {
            nft = new CelticCreatureNFT();
        }

        function testMint() public {
            uint256 tokenId = nft.mint(
                owner,
                "Cu Chulainn",
                CelticCreatureNFT.Tradition.Irish,
                CelticCreatureNFT.CreatureType.Hero,
                95,  // strength
                70,  // wisdom
                80   // magic
            );

            assertEq(nft.ownerOf(tokenId), owner);

            CelticCreatureNFT.Creature memory c = nft.creatures(tokenId);
            assertEq(c.name, "Cu Chulainn");
            assertEq(c.strength, 95);
        }

        function testTokenURI() public {
            uint256 tokenId = nft.mint(owner, "Test", ...);
            string memory uri = nft.tokenURI(tokenId);

            // Should be base64-encoded JSON with SVG
            assertTrue(bytes(uri).length > 0);
        }
    }
    ```

    ### Solana Tests (Anchor)

    ```rust
    // tests/celtic_nft.rs
    #[tokio::test]
    async fn test_create_creature() {
        let program = Program::new(...);

        let (asset, _) = find_asset_pda(&collection, &name);

        program
            .request()
            .accounts(CreateCreature { ... })
            .args(celtic_nft::instruction::CreateCreature {
                name: "Cú Chulainn".to_string(),
                uri: "https://...".to_string(),
                tradition: Tradition::Irish,
                creature_type: CreatureType::Hero,
                strength: 95,
                wisdom: 70,
                magic: 80,
            })
            .send()
            .await
            .unwrap();

        let asset_account = program.account::<Asset>(asset).await.unwrap();
        assert_eq!(asset_account.name, "Cú Chulainn");
    }
    ```
    """)
    return ()


@app.cell
def _(mo):
    """Challenge Completion."""
    tasks = [
        ("Design creature attribute system", True),
        ("Create SVG generator", True),
        ("Review Solana program extension", False),
        ("Review Ethereum contract", False),
        ("Deploy to local testnet", False),
        ("Sync with SpacetimeDB", False),
        ("Test in game client", False),
    ]

    checklist = mo.ui.array([mo.ui.checkbox(label=task, value=done) for task, done in tasks])

    completed = sum(1 for cb in checklist.value if cb)
    total = len(tasks)

    mo.vstack(
        [
            mo.md("## Challenge Completion"),
            checklist,
            mo.md(f"**Progress: {completed}/{total}**"),
            mo.md("**Next:** [Challenge 1: Language Staking](./01_language_staking.py)")
            if completed == total
            else None,
        ]
    )
    return checklist, completed, tasks, total


@app.cell
def _(mo):
    """Resources."""
    mo.md("""
    ---

    ## Resources

    ### SpeedRunEthereum
    - [Challenge 0: Tokenization](https://speedrunethereum.com/challenge/tokenization)

    ### Celtic Mythology
    - [CELT: Corpus of Electronic Texts](https://celt.ucc.ie/)
    - [Dúchas.ie](https://www.duchas.ie/) - Irish Folklore Collection

    ### Technical
    - [Metaplex Core](https://developers.metaplex.com/core)
    - [OpenZeppelin ERC721](https://docs.openzeppelin.com/contracts/5.x/erc721)
    - [SpacetimeDB](https://spacetimedb.com/docs)
    - [On-chain SVG NFTs](https://www.paradigm.xyz/2021/10/a-guide-to-designing-effective-nft-launches)
    """)
    return ()


if __name__ == "__main__":
    app.run()
