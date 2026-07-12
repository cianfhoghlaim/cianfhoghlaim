"""
Challenge 2: Token Vendor - Tuath In-Game Shop Implementation

SpeedRunEthereum Challenge: https://speedrunethereum.com/challenge/token-vendor

Learning Objectives:
- ERC20 approve pattern for token spending
- Contract-to-contract interactions
- Simple AMM mechanics (constant price)
- In-game economy design

Project Integration:
- Celtic token shop for the tuath MMO
- Dynamic pricing based on player demand
- x402 micropayment integration
- SIWE authentication for premium features
- SpacetimeDB inventory sync
"""

import marimo

__generated_with = "0.10.14"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo

    mo.md(
        """
        # Challenge 2: Celtic Token Shop

        ## Tuath In-Game Economy

        This notebook implements the in-game shop for the tuath Celtic educational MMO,
        where players can buy items using CELTIC tokens.

        ### What We'll Build:
        1. **Token Exchange** - Buy/sell CELTIC tokens with ETH
        2. **Item Shop** - Purchase in-game items with tokens
        3. **Dynamic Pricing** - Demand-based price adjustments
        4. **Premium Features** - x402 micropayment integration
        """
    )
    return (mo,)


@app.cell
def _(mo):
    mo.md(
        """
        ## 1. The Token Vendor Pattern

        SpeedRunEthereum Challenge 2 teaches the token vendor pattern:
        a contract that buys and sells tokens at a fixed rate.

        ### Core Mechanics:

        ```solidity
        contract Vendor {
            IERC20 public token;
            uint256 public tokensPerEth = 100;

            // User sends ETH, receives tokens
            function buyTokens() public payable {
                uint256 tokenAmount = msg.value * tokensPerEth;
                token.transfer(msg.sender, tokenAmount);
            }

            // User sends tokens, receives ETH
            function sellTokens(uint256 amount) public {
                // Requires user to approve() first!
                token.transferFrom(msg.sender, address(this), amount);
                uint256 ethAmount = amount / tokensPerEth;
                payable(msg.sender).transfer(ethAmount);
            }
        }
        ```

        ### Key Concept: The Approve Pattern

        Unlike ETH (sent via `msg.value`), ERC20 tokens require:

        1. **User calls `approve(vendorAddress, amount)`** on token contract
        2. **Vendor calls `transferFrom(user, vendor, amount)`** to pull tokens

        This two-step process prevents unauthorized token transfers.
        """
    )
    return


@app.cell
def _():
    # Tuath game items
    game_items = {
        "weapons": [
            {
                "id": 1,
                "name": "Claíomh Solais",
                "name_en": "Sword of Light",
                "description": "Nuada's legendary sword that none could escape",
                "price_celtic": 500,
                "rarity": "legendary",
                "strength_bonus": 50,
                "tradition": "Irish",
            },
            {
                "id": 2,
                "name": "Gáe Bulg",
                "name_en": "Belly Spear",
                "description": "Cú Chulainn's deadly spear with barbed points",
                "price_celtic": 750,
                "rarity": "legendary",
                "strength_bonus": 75,
                "tradition": "Irish",
            },
            {
                "id": 3,
                "name": "Dyrnwyn",
                "name_en": "White Hilt",
                "description": "Welsh sword that flames when drawn by the worthy",
                "price_celtic": 400,
                "rarity": "epic",
                "strength_bonus": 40,
                "tradition": "Welsh",
            },
        ],
        "armor": [
            {
                "id": 4,
                "name": "Clóca Fionnachta",
                "name_en": "Cloak of Feathers",
                "description": "Allows transformation into a swan",
                "price_celtic": 300,
                "rarity": "rare",
                "wisdom_bonus": 25,
                "tradition": "Irish",
            },
            {
                "id": 5,
                "name": "Scíath Gheal",
                "name_en": "Bright Shield",
                "description": "Shield blessed by Brigid",
                "price_celtic": 200,
                "rarity": "uncommon",
                "defense_bonus": 30,
                "tradition": "Irish",
            },
        ],
        "consumables": [
            {
                "id": 6,
                "name": "Ubhla Óir",
                "name_en": "Golden Apples",
                "description": "Restores health and grants temporary invulnerability",
                "price_celtic": 50,
                "rarity": "common",
                "health_restore": 100,
                "tradition": "Irish",
            },
            {
                "id": 7,
                "name": "Deoch na hÓige",
                "name_en": "Drink of Youth",
                "description": "Restores XP multiplier to maximum",
                "price_celtic": 100,
                "rarity": "uncommon",
                "xp_multiplier": 2.0,
                "tradition": "Irish",
            },
        ],
        "learning": [
            {
                "id": 8,
                "name": "Leabhar Feasa",
                "name_en": "Book of Knowledge",
                "description": "Unlocks bonus Irish vocabulary lessons",
                "price_celtic": 150,
                "rarity": "rare",
                "bonus_lessons": 10,
                "tradition": "Irish",
            },
            {
                "id": 9,
                "name": "Focail Draíochta",
                "name_en": "Words of Magic",
                "description": "Grammar power-ups for difficult concepts",
                "price_celtic": 75,
                "rarity": "uncommon",
                "grammar_boost": 5,
                "tradition": "Irish",
            },
        ],
    }
    return (game_items,)


@app.cell
def _(game_items, mo):
    # Display shop inventory
    all_items = []
    for category, items in game_items.items():
        for item in items:
            all_items.append({
                "Category": category.title(),
                "Name (Irish)": item["name"],
                "Name (English)": item["name_en"],
                "Price": f"{item['price_celtic']} CELTIC",
                "Rarity": item["rarity"].title(),
                "Tradition": item.get("tradition", "Celtic"),
            })

    mo.md(
        f"""
        ## 2. Celtic Shop Inventory

        Items available for purchase with CELTIC tokens:

        {mo.ui.table(all_items)}

        ### Item Categories:
        - **Weapons** - Increase strength in quests
        - **Armor** - Boost defense and special abilities
        - **Consumables** - Temporary buffs and restoration
        - **Learning** - Educational bonuses for language study
        """
    )
    return all_items, category, item, items


@app.cell
def _(mo):
    mo.md(
        """
        ## 3. CelticShop Contract

        Our Ethereum implementation extends the basic vendor with:

        ### Features:
        1. **Token Exchange** - Buy/sell CELTIC for ETH
        2. **Spread** - 1% fee on trades
        3. **In-Game Items** - Purchase items with tokens
        4. **Inventory Tracking** - On-chain ownership records
        5. **Dynamic Pricing** - Bonding curve potential

        ### Contract Architecture:

        ```solidity
        contract CelticShop is Ownable, ReentrancyGuard {
            IERC20 public celticToken;

            // Exchange rate: tokens per ETH
            uint256 public tokensPerEth = 1000;
            uint256 public spreadBps = 100; // 1%

            struct GameItem {
                string name;
                string category;
                uint256 priceInCeltic;
                uint256 stock;
                bool isActive;
                string metadataUri;
            }

            mapping(uint256 => GameItem) public items;
            mapping(address => mapping(uint256 => uint256)) public playerInventory;

            function buyTokens() external payable;
            function sellTokens(uint256 amount) external;
            function purchaseItem(uint256 itemId, uint256 quantity) external;
        }
        ```

        The spread creates a sustainable revenue model:
        - **Buying**: User gets slightly fewer tokens
        - **Selling**: User gets slightly less ETH
        - **Difference**: Accumulates in shop treasury
        """
    )
    return


@app.cell
def _():
    # Token economics simulation
    def simulate_token_exchange(
        tokens_per_eth: int = 1000,
        spread_bps: int = 100,  # 1%
        eth_amount: float = 1.0
    ) -> dict:
        """
        Simulate token purchase/sale with spread.

        Args:
            tokens_per_eth: Base exchange rate
            spread_bps: Spread in basis points (100 = 1%)
            eth_amount: Amount of ETH to exchange

        Returns:
            Dictionary with exchange details
        """
        # Buy: user pays slightly more (fewer tokens per ETH)
        buy_rate = tokens_per_eth * (10000 - spread_bps) / 10000
        tokens_received = eth_amount * buy_rate

        # Sell: user receives slightly less ETH
        sell_rate = tokens_per_eth * (10000 + spread_bps) / 10000
        eth_received = tokens_received / sell_rate

        # Spread captured by shop
        spread_captured = eth_amount - eth_received

        return {
            "eth_spent": eth_amount,
            "tokens_received": tokens_received,
            "buy_rate": buy_rate,
            "sell_rate": sell_rate,
            "eth_if_sold_back": eth_received,
            "spread_captured": spread_captured,
            "effective_fee_pct": (spread_captured / eth_amount) * 100,
        }

    # Demo exchange
    exchange = simulate_token_exchange(1000, 100, 1.0)

    print("Token Exchange Simulation (1 ETH)")
    print("-" * 40)
    print(f"Tokens Received:    {exchange['tokens_received']:.2f} CELTIC")
    print(f"Buy Rate:           {exchange['buy_rate']:.2f} tokens/ETH")
    print(f"Sell Rate:          {exchange['sell_rate']:.2f} tokens/ETH")
    print(f"ETH if Sold Back:   {exchange['eth_if_sold_back']:.4f} ETH")
    print(f"Spread Captured:    {exchange['spread_captured']:.4f} ETH")
    print(f"Effective Fee:      {exchange['effective_fee_pct']:.2f}%")
    return exchange, simulate_token_exchange


@app.cell
def _(mo):
    mo.md(
        """
        ## 4. Player Wallet Integration

        ### SIWE (Sign-In with Ethereum) Flow

        For web-based shop access, we use SIWE:

        ```python
        # SIWE authentication for shop access
        from siwe import SiweMessage

        async def authenticate_player(message: str, signature: str):
            '''
            Verify player's wallet ownership.
            '''
            siwe = SiweMessage(message=message)
            siwe.verify(signature)

            return {
                "address": siwe.address,
                "chain_id": siwe.chain_id,
                "authenticated": True
            }

        # After authentication, player can:
        # 1. View their token balance
        # 2. Access shop inventory
        # 3. Make purchases (signed transactions)
        # 4. Sync inventory to SpacetimeDB
        ```

        ### Transaction Flow:

        ```
        1. Player connects wallet (MetaMask, WalletConnect)
        2. SIWE authentication proves ownership
        3. Player browses shop inventory
        4. For purchase:
           a. Approve CELTIC spending if needed
           b. Call purchaseItem(itemId, quantity)
           c. Transaction confirmed on-chain
        5. SpacetimeDB updates player inventory
        6. Game UI reflects new items
        ```
        """
    )
    return


@app.cell
def _():
    # SpacetimeDB integration schema
    spacetimedb_schema = """
    // SpacetimeDB tables for shop integration

    #[spacetimedb::table(public)]
    pub struct PlayerWallet {
        #[primary_key]
        player_id: Identity,
        eth_address: String,
        celtic_balance: u64,  // Cached from chain
        last_sync: Timestamp,
    }

    #[spacetimedb::table(public)]
    pub struct PlayerInventory {
        #[primary_key]
        #[auto_inc]
        id: u64,
        #[index(btree)]
        player_id: Identity,
        item_id: u32,
        quantity: u32,
        acquired_at: Timestamp,
        tx_hash: Option<String>,  // On-chain proof
    }

    #[spacetimedb::table(public)]
    pub struct ShopItem {
        #[primary_key]
        item_id: u32,
        name_irish: String,
        name_english: String,
        category: ItemCategory,
        price_celtic: u64,
        rarity: Rarity,
        metadata_uri: String,
        is_active: bool,
    }

    #[spacetimedb::reducer]
    pub fn sync_purchase(
        ctx: &ReducerContext,
        item_id: u32,
        quantity: u32,
        tx_hash: String,
    ) -> Result<(), String> {
        // Verify tx_hash on-chain (via oracle or indexer)
        // Update player inventory
        // Emit event for game clients
    }
    """

    print(spacetimedb_schema)
    return (spacetimedb_schema,)


@app.cell
def _(mo):
    mo.md(
        """
        ## 5. x402 Micropayment Integration

        For premium features without gas costs, we use x402:

        ### HTTP 402 Payment Required Flow:

        ```
        Client                   Server                  Blockchain
           |                        |                        |
           | --- GET /premium-lesson -->                     |
           |                        |                        |
           | <-- 402 Payment Required                        |
           |     X-Payment: x402://...                       |
           |                        |                        |
           | (User approves payment in wallet)               |
           |                        |                        |
           | --- GET /premium-lesson -->                     |
           |     Authorization: x402 <signed-receipt>        |
           |                        |                        |
           |                    (Verify receipt)             |
           |                        | --- Submit to chain -->|
           |                        |                        |
           | <-- 200 OK (lesson content)                     |
        ```

        ### x402 Use Cases in Tuath:

        | Feature | Price | Description |
        |---------|-------|-------------|
        | Premium Lesson | 10 CELTIC | Access advanced content |
        | Hint System | 5 CELTIC | Get hints during quests |
        | Fast Travel | 2 CELTIC | Instant teleportation |
        | Name Change | 50 CELTIC | Update character name |
        | Guild Creation | 200 CELTIC | Create new guild |
        """
    )
    return


@app.cell
def _():
    # x402 payment verification
    def verify_x402_payment(
        receipt: str,
        expected_amount: int,
        expected_recipient: str
    ) -> dict:
        """
        Verify an x402 payment receipt.

        In production, this would:
        1. Decode the signed receipt
        2. Verify signature against payer's wallet
        3. Check amount and recipient
        4. Optionally submit to chain
        """
        # Simulated verification
        return {
            "valid": True,
            "payer": "0x742d35Cc6634C0532925a3b844Bc9e7595f1234a",
            "amount": expected_amount,
            "token": "CELTIC",
            "recipient": expected_recipient,
            "nonce": 12345,
            "expiry": 1735689600,  # Unix timestamp
        }

    # Demo x402 verification
    payment = verify_x402_payment(
        receipt="x402://...",
        expected_amount=10,
        expected_recipient="0xShopContract..."
    )

    print("x402 Payment Verification")
    print("-" * 40)
    for key, value in payment.items():
        print(f"{key}: {value}")
    return payment, verify_x402_payment


@app.cell
def _(mo):
    mo.md(
        """
        ## 6. Dynamic Pricing

        ### Demand-Based Pricing Algorithm

        Items can have dynamic prices based on:

        1. **Purchase velocity** - High demand = higher prices
        2. **Stock levels** - Limited stock = premium pricing
        3. **Time of day** - Peak hours adjustment
        4. **Player level** - Discounts for new players

        ```python
        def calculate_dynamic_price(
            base_price: int,
            daily_purchases: int,
            stock: int,
            player_level: int
        ) -> int:
            '''
            Calculate dynamic item price.

            Formula:
            price = base_price * demand_mult * scarcity_mult * level_discount

            Where:
            - demand_mult = 1 + (daily_purchases / 100) * 0.5  (max 2x)
            - scarcity_mult = 1 + (1 / stock) * 10 if stock < 10 else 1
            - level_discount = 0.9 if player_level < 5 else 1.0
            '''
            # Demand multiplier (caps at 2x)
            demand_mult = min(1 + (daily_purchases / 100) * 0.5, 2.0)

            # Scarcity multiplier (kicks in below 10 stock)
            if stock > 0 and stock < 10:
                scarcity_mult = 1 + (1 / stock) * 10
            else:
                scarcity_mult = 1.0

            # New player discount
            level_discount = 0.9 if player_level < 5 else 1.0

            return int(base_price * demand_mult * scarcity_mult * level_discount)
        ```
        """
    )
    return


@app.cell
def _():
    def calculate_dynamic_price(
        base_price: int,
        daily_purchases: int,
        stock: int,
        player_level: int
    ) -> dict:
        """
        Calculate dynamic item price with breakdown.
        """
        # Demand multiplier (caps at 2x)
        demand_mult = min(1 + (daily_purchases / 100) * 0.5, 2.0)

        # Scarcity multiplier (kicks in below 10 stock)
        scarcity_mult = 1 + 1 / stock * 10 if stock > 0 and stock < 10 else 1.0

        # New player discount
        level_discount = 0.9 if player_level < 5 else 1.0

        final_price = int(base_price * demand_mult * scarcity_mult * level_discount)

        return {
            "base_price": base_price,
            "demand_multiplier": demand_mult,
            "scarcity_multiplier": scarcity_mult,
            "level_discount": level_discount,
            "final_price": final_price,
            "change_pct": ((final_price - base_price) / base_price) * 100,
        }

    # Scenarios
    scenarios = [
        ("Normal conditions", 100, 10, 50, 10),
        ("High demand", 100, 150, 50, 10),
        ("Low stock", 100, 10, 3, 10),
        ("New player", 100, 10, 50, 2),
        ("All factors", 100, 200, 2, 3),
    ]

    print("Dynamic Pricing Scenarios")
    print("=" * 60)

    for name, base, purchases, stock, level in scenarios:
        result = calculate_dynamic_price(base, purchases, stock, level)
        print(f"\n{name}:")
        print(f"  Base Price: {result['base_price']} CELTIC")
        print(f"  Demand: x{result['demand_multiplier']:.2f}")
        print(f"  Scarcity: x{result['scarcity_multiplier']:.2f}")
        print(f"  Level Discount: x{result['level_discount']:.2f}")
        print(f"  Final Price: {result['final_price']} CELTIC ({result['change_pct']:+.1f}%)")
    return (
        base,
        calculate_dynamic_price,
        level,
        name,
        purchases,
        result,
        scenarios,
        stock,
    )


@app.cell
def _(mo):
    mo.md(
        """
        ## 7. Solana Token Shop

        On Solana, we implement an equivalent program:

        ```rust
        // programs/celtic-vendor/src/lib.rs

        use anchor_lang::prelude::*;
        use anchor_spl::token::{self, Token, TokenAccount, Transfer};

        declare_id!("VendXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX");

        #[program]
        pub mod celtic_vendor {
            use super::*;

            pub fn initialize(
                ctx: Context<Initialize>,
                tokens_per_sol: u64,
                spread_bps: u16,
            ) -> Result<()> {
                let shop = &mut ctx.accounts.shop;
                shop.authority = ctx.accounts.authority.key();
                shop.celtic_mint = ctx.accounts.celtic_mint.key();
                shop.tokens_per_sol = tokens_per_sol;
                shop.spread_bps = spread_bps;
                shop.total_sol_collected = 0;
                shop.total_tokens_sold = 0;
                Ok(())
            }

            pub fn buy_tokens(ctx: Context<BuyTokens>, sol_amount: u64) -> Result<()> {
                let shop = &ctx.accounts.shop;

                // Calculate tokens with spread
                let effective_rate = shop.tokens_per_sol
                    .checked_mul(10000 - shop.spread_bps as u64)
                    .unwrap()
                    .checked_div(10000)
                    .unwrap();

                let token_amount = sol_amount
                    .checked_mul(effective_rate)
                    .unwrap();

                // Transfer SOL from buyer to shop
                anchor_lang::system_program::transfer(
                    CpiContext::new(
                        ctx.accounts.system_program.to_account_info(),
                        anchor_lang::system_program::Transfer {
                            from: ctx.accounts.buyer.to_account_info(),
                            to: ctx.accounts.shop_sol_vault.to_account_info(),
                        },
                    ),
                    sol_amount,
                )?;

                // Transfer tokens to buyer
                let seeds = &[b"shop", &[shop.bump]];
                let signer = &[&seeds[..]];

                token::transfer(
                    CpiContext::new_with_signer(
                        ctx.accounts.token_program.to_account_info(),
                        Transfer {
                            from: ctx.accounts.shop_token_vault.to_account_info(),
                            to: ctx.accounts.buyer_token_account.to_account_info(),
                            authority: ctx.accounts.shop.to_account_info(),
                        },
                        signer,
                    ),
                    token_amount,
                )?;

                Ok(())
            }

            pub fn purchase_item(
                ctx: Context<PurchaseItem>,
                item_id: u32,
                quantity: u32,
            ) -> Result<()> {
                // Verify item exists and has stock
                // Transfer tokens from buyer
                // Update inventory
                // Emit event
                Ok(())
            }
        }

        #[account]
        pub struct Shop {
            pub authority: Pubkey,
            pub celtic_mint: Pubkey,
            pub tokens_per_sol: u64,
            pub spread_bps: u16,
            pub total_sol_collected: u64,
            pub total_tokens_sold: u64,
            pub bump: u8,
        }
        ```
        """
    )
    return


@app.cell
def _(mo):
    mo.md(
        """
        ## 8. Frontend Integration

        ### React Component for Shop

        ```tsx
        // components/CelticShop.tsx
        import { useAccount, useWriteContract } from 'wagmi';
        import { parseEther } from 'viem';

        export function CelticShop({ items }) {
          const { address } = useAccount();
          const { writeContract } = useWriteContract();

          const buyItem = async (itemId: number, quantity: number) => {
            // First approve CELTIC spending
            await writeContract({
              address: CELTIC_TOKEN_ADDRESS,
              abi: erc20Abi,
              functionName: 'approve',
              args: [SHOP_ADDRESS, parseEther('1000')],
            });

            // Then purchase
            await writeContract({
              address: SHOP_ADDRESS,
              abi: celticShopAbi,
              functionName: 'purchaseItem',
              args: [itemId, quantity],
            });
          };

          return (
            <div className="shop-grid">
              {items.map(item => (
                <ItemCard
                  key={item.id}
                  item={item}
                  onPurchase={() => buyItem(item.id, 1)}
                />
              ))}
            </div>
          );
        }
        ```

        ### TanStack Start Integration

        ```typescript
        // routes/shop.tsx
        import { createFileRoute } from '@tanstack/react-router';
        import { CelticShop } from '../components/CelticShop';

        export const Route = createFileRoute('/shop')({
          loader: async () => {
            // Fetch items from contract or SpacetimeDB
            const items = await fetchShopItems();
            return { items };
          },
          component: ShopPage,
        });

        function ShopPage() {
          const { items } = Route.useLoaderData();
          return <CelticShop items={items} />;
        }
        ```
        """
    )
    return


@app.cell
def _(mo):
    mo.md(
        """
        ## 9. Testing the Shop

        ### Foundry Tests

        ```bash
        # Navigate to contracts directory
        cd sruth/shared/blockchain/ethereum

        # Run shop tests
        forge test --match-contract CelticShopTest -vvv

        # Test specific functions
        forge test --match-test test_BuyTokens -vvv
        forge test --match-test test_PurchaseItem -vvv

        # Gas snapshots
        forge snapshot --match-contract CelticShopTest
        ```

        ### Local Anvil Testing

        ```bash
        # Start Anvil
        anvil --fork-url $BASE_SEPOLIA_RPC

        # Deploy contracts
        forge script script/DeployCelticShop.s.sol --rpc-url anvil --broadcast

        # Interact via cast
        cast send $SHOP_ADDRESS "buyTokens()" --value 0.1ether
        cast call $SHOP_ADDRESS "getItem(uint256)" 0
        ```

        ### Integration Testing

        ```python
        # Python integration test
        from web3 import Web3

        def test_shop_integration():
            w3 = Web3(Web3.HTTPProvider('http://localhost:8545'))

            # Load contracts
            shop = w3.eth.contract(address=SHOP_ADDRESS, abi=SHOP_ABI)
            token = w3.eth.contract(address=TOKEN_ADDRESS, abi=ERC20_ABI)

            # Buy tokens
            tx = shop.functions.buyTokens().transact({
                'from': user_address,
                'value': w3.to_wei(0.1, 'ether')
            })
            w3.eth.wait_for_transaction_receipt(tx)

            # Check balance
            balance = token.functions.balanceOf(user_address).call()
            assert balance > 0

            # Approve and purchase item
            token.functions.approve(SHOP_ADDRESS, balance).transact({
                'from': user_address
            })

            shop.functions.purchaseItem(0, 1).transact({
                'from': user_address
            })

            # Verify inventory
            inventory = shop.functions.getInventory(user_address, 0).call()
            assert inventory == 1
        ```
        """
    )
    return


@app.cell
def _(mo):
    mo.md(
        """
        ## 10. Next Steps

        ### For SpeedRunEthereum:
        1. Deploy CelticShop.sol to testnet
        2. Complete challenge verification
        3. Get NFT badge

        ### For Tuath Integration:
        1. Connect to SpacetimeDB for inventory sync
        2. Implement x402 payment verification
        3. Add dynamic pricing to contract
        4. Build React shop component
        5. Integrate with game UI

        ### Related Notebooks:
        - `00_celtic_nft.py` - Celtic creature NFTs
        - `01_language_staking.py` - Learn-to-Earn staking
        - `04_item_exchange.py` - Player-to-player trading (DEX)
        """
    )
    return


if __name__ == "__main__":
    app.run()
