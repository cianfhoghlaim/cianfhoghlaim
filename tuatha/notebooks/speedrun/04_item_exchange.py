"""
Challenge 4: DEX - Tuath Player Trading Exchange

SpeedRunEthereum Challenge: https://speedrunethereum.com/challenge/dex

Learning Objectives:
- Implement player-to-player trading
- Create AMM pools for game items
- Build guild treasury management
- Enable price discovery for rare items

Project Integration:
- Celtic token / item liquidity pools
- Guild treasury management
- Player-driven economy
- SpacetimeDB order book integration
"""

import marimo

__generated_with = "0.10.14"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo

    mo.md(
        """
        # Challenge 4: Player Item Exchange

        ## Tuath Trading Economy

        This notebook implements the player-to-player trading system for
        the tuath Celtic educational MMO.

        ### What We'll Build:
        1. **Item Trading Pools** - AMM for game items
        2. **Guild Treasury** - Collective resource management
        3. **Price Discovery** - Fair pricing for rare items
        4. **Order Book** - Traditional limit orders via SpacetimeDB
        """
    )
    return (mo,)


@app.cell
def _(mo):
    mo.md(
        """
        ## 1. Trading System Overview

        ### Two Trading Mechanisms:

        ```
        ┌─────────────────────────────────────────────────────────────────┐
        │                     TUATH TRADING SYSTEM                        │
        ├─────────────────────────────┬───────────────────────────────────┤
        │         AMM POOLS           │           ORDER BOOK              │
        │    (On-Chain/Hybrid)        │       (SpacetimeDB)               │
        ├─────────────────────────────┼───────────────────────────────────┤
        │ • Instant swaps             │ • Set your price                  │
        │ • Guaranteed liquidity      │ • No slippage at limit            │
        │ • Common items              │ • Rare/unique items               │
        │ • CELTIC/Item pairs         │ • Item/Item trades                │
        │ • 0.3% fee to LPs           │ • Auction support                 │
        └─────────────────────────────┴───────────────────────────────────┘
        ```

        ### When to Use Each:

        | Use Case | AMM | Order Book |
        |----------|-----|------------|
        | Quick sale of common items | ✓ | |
        | Buying specific quantity | ✓ | |
        | Rare/legendary items | | ✓ |
        | Auctions | | ✓ |
        | Guild bulk trades | | ✓ |
        | Passive income (LP) | ✓ | |
        """
    )
    return


@app.cell
def _():
    # Game items and their base values
    tradeable_items = {
        "consumables": [
            {"id": 1, "name": "Ubhla Óir", "name_en": "Golden Apple", "base_value": 50, "rarity": "common"},
            {"id": 2, "name": "Deoch na hÓige", "name_en": "Drink of Youth", "base_value": 100, "rarity": "uncommon"},
            {"id": 3, "name": "Focail Draíochta", "name_en": "Words of Magic", "base_value": 75, "rarity": "uncommon"},
        ],
        "weapons": [
            {"id": 4, "name": "Claíomh Umha", "name_en": "Bronze Sword", "base_value": 200, "rarity": "common"},
            {"id": 5, "name": "Dyrnwyn", "name_en": "White Hilt", "base_value": 400, "rarity": "epic"},
            {"id": 6, "name": "Gáe Bulg", "name_en": "Belly Spear", "base_value": 750, "rarity": "legendary"},
            {"id": 7, "name": "Claíomh Solais", "name_en": "Sword of Light", "base_value": 1500, "rarity": "legendary"},
        ],
        "armor": [
            {"id": 8, "name": "Scíath Gheal", "name_en": "Bright Shield", "base_value": 200, "rarity": "uncommon"},
            {"id": 9, "name": "Clóca Fionnachta", "name_en": "Feather Cloak", "base_value": 300, "rarity": "rare"},
        ],
        "learning": [
            {"id": 10, "name": "Leabhar Feasa", "name_en": "Book of Knowledge", "base_value": 150, "rarity": "rare"},
        ],
    }

    # Flatten for easy access
    all_items = {}
    for category, items in tradeable_items.items():
        for item in items:
            all_items[item["id"]] = {**item, "category": category}

    print("=== Tradeable Items ===\n")
    for category, items in tradeable_items.items():
        print(f"{category.upper()}:")
        for item in items:
            print(f"  [{item['rarity']:10}] {item['name']} ({item['base_value']} CELTIC)")
        print()
    return all_items, category, item, items, tradeable_items


@app.cell
def _(mo):
    mo.md(
        """
        ## 2. AMM Item Pools

        ### Pool Structure:

        Each pool pairs CELTIC tokens with a game item:

        ```
        Pool: CELTIC / Golden Apple
        ├── Reserve CELTIC: 10,000
        ├── Reserve Apples: 200
        ├── k = 2,000,000
        └── Price: 50 CELTIC per Apple
        ```

        ### Creating a Pool:

        ```solidity
        // CelticItemPool.sol

        contract CelticItemPool is ERC20 {
            IERC20 public celtic;
            uint256 public itemId;

            uint256 public reserveCeltic;
            uint256 public reserveItems;

            // Item inventory is tracked off-chain (SpacetimeDB)
            // Only pool ownership tokens are on-chain

            function addLiquidity(uint256 celticAmount, uint256 itemAmount)
                external returns (uint256 lpTokens);

            function swapCelticForItem(uint256 celticIn, uint256 minItemsOut)
                external returns (uint256 itemsOut);

            function swapItemForCeltic(uint256 itemsIn, uint256 minCelticOut)
                external returns (uint256 celticOut);
        }
        ```
        """
    )
    return


@app.cell
def _():
    import math

    class ItemPool:
        """Simulated AMM pool for CELTIC/Item trading."""

        def __init__(self, item_id: int, item_name: str, initial_celtic: float, initial_items: int):
            self.item_id = item_id
            self.item_name = item_name
            self.reserve_celtic = initial_celtic
            self.reserve_items = float(initial_items)
            self.total_lp = math.sqrt(initial_celtic * initial_items)
            self.lp_holders = {}
            self.fee_rate = 0.003  # 0.3%
            self.trades = []

        @property
        def k(self) -> float:
            return self.reserve_celtic * self.reserve_items

        @property
        def spot_price(self) -> float:
            """Price of 1 item in CELTIC."""
            return self.reserve_celtic / self.reserve_items if self.reserve_items > 0 else 0

        def add_liquidity(self, provider: str, celtic: float, items: int) -> float:
            """Add liquidity to the pool."""
            if self.total_lp == 0:
                lp_tokens = math.sqrt(celtic * items)
            else:
                lp_from_celtic = celtic / self.reserve_celtic * self.total_lp
                lp_from_items = items / self.reserve_items * self.total_lp
                lp_tokens = min(lp_from_celtic, lp_from_items)

            self.reserve_celtic += celtic
            self.reserve_items += items
            self.total_lp += lp_tokens
            self.lp_holders[provider] = self.lp_holders.get(provider, 0) + lp_tokens

            return lp_tokens

        def swap_celtic_for_item(self, celtic_in: float) -> tuple:
            """Swap CELTIC for items."""
            celtic_with_fee = celtic_in * (1 - self.fee_rate)
            items_out = self.reserve_items - (self.k / (self.reserve_celtic + celtic_with_fee))
            items_out = int(items_out)  # Items are whole numbers

            self.reserve_celtic += celtic_in
            self.reserve_items -= items_out

            self.trades.append({
                "type": "buy",
                "celtic_in": celtic_in,
                "items_out": items_out,
                "price": celtic_in / items_out if items_out > 0 else 0,
            })

            return items_out, celtic_in / items_out if items_out > 0 else 0

        def swap_item_for_celtic(self, items_in: int) -> tuple:
            """Swap items for CELTIC."""
            items_with_fee = items_in * (1 - self.fee_rate)
            celtic_out = self.reserve_celtic - (self.k / (self.reserve_items + items_with_fee))

            self.reserve_items += items_in
            self.reserve_celtic -= celtic_out

            self.trades.append({
                "type": "sell",
                "items_in": items_in,
                "celtic_out": celtic_out,
                "price": celtic_out / items_in,
            })

            return celtic_out, celtic_out / items_in

        def get_stats(self) -> dict:
            return {
                "item_name": self.item_name,
                "reserve_celtic": self.reserve_celtic,
                "reserve_items": self.reserve_items,
                "spot_price": self.spot_price,
                "k": self.k,
                "total_lp": self.total_lp,
                "num_lps": len(self.lp_holders),
                "num_trades": len(self.trades),
            }

    # Create sample pools
    pools = {
        "apple_pool": ItemPool(1, "Ubhla Óir (Golden Apple)", 10000, 200),
        "sword_pool": ItemPool(4, "Claíomh Umha (Bronze Sword)", 20000, 100),
        "cloak_pool": ItemPool(9, "Clóca Fionnachta (Feather Cloak)", 30000, 100),
    }

    print("=== Item Trading Pools ===\n")
    for name, pool in pools.items():
        stats = pool.get_stats()
        print(f"{stats['item_name']}")
        print(f"  Reserves: {stats['reserve_celtic']:,.0f} CELTIC / {stats['reserve_items']:.0f} items")
        print(f"  Price: {stats['spot_price']:.2f} CELTIC per item")
        print()
    return ItemPool, math, name, pool, pools, stats


@app.cell
def _(pools):
    # Simulate trading activity
    apple_pool = pools["apple_pool"]

    print("=== Trading Simulation: Golden Apples ===\n")
    print(f"Initial: {apple_pool.reserve_celtic:,.0f} CELTIC / {apple_pool.reserve_items:.0f} Apples")
    print(f"Initial Price: {apple_pool.spot_price:.2f} CELTIC\n")

    # Player buys apples
    items_received, price = apple_pool.swap_celtic_for_item(500)
    print(f"Trade 1: Buy with 500 CELTIC")
    print(f"  Received: {items_received} Apples at {price:.2f} CELTIC each")
    print(f"  New Price: {apple_pool.spot_price:.2f} CELTIC\n")

    # Another player buys (higher price due to previous trade)
    items_received2, price2 = apple_pool.swap_celtic_for_item(500)
    print(f"Trade 2: Buy with 500 CELTIC")
    print(f"  Received: {items_received2} Apples at {price2:.2f} CELTIC each")
    print(f"  New Price: {apple_pool.spot_price:.2f} CELTIC\n")

    # Player sells apples (brings price back down)
    celtic_received, sell_price = apple_pool.swap_item_for_celtic(15)
    print(f"Trade 3: Sell 15 Apples")
    print(f"  Received: {celtic_received:.2f} CELTIC at {sell_price:.2f} CELTIC each")
    print(f"  New Price: {apple_pool.spot_price:.2f} CELTIC\n")

    print(f"Final State: {apple_pool.reserve_celtic:,.2f} CELTIC / {apple_pool.reserve_items:.0f} Apples")
    return (
        apple_pool,
        celtic_received,
        items_received,
        items_received2,
        price,
        price2,
        sell_price,
    )


@app.cell
def _(mo):
    mo.md(
        """
        ## 3. Order Book for Rare Items

        ### SpacetimeDB Order Book:

        ```rust
        #[spacetimedb::table(public)]
        pub struct TradeOrder {
            #[primary_key]
            #[auto_inc]
            order_id: u64,

            #[index(btree)]
            seller: Identity,

            item_id: u32,
            quantity: u32,
            price_per_item: u64,  // In CELTIC
            order_type: OrderType,  // Buy or Sell
            status: OrderStatus,
            created_at: Timestamp,
            expires_at: Option<Timestamp>,
        }

        #[derive(Debug, Clone)]
        pub enum OrderType { Buy, Sell }

        #[derive(Debug, Clone)]
        pub enum OrderStatus { Open, Filled, Cancelled, Expired }

        #[spacetimedb::reducer]
        pub fn place_order(
            ctx: &ReducerContext,
            item_id: u32,
            quantity: u32,
            price_per_item: u64,
            order_type: OrderType,
            expires_in_hours: Option<u32>,
        ) -> Result<u64, String> {
            // Validate seller has items (for sell) or CELTIC (for buy)
            // Create order
            // Try to match with existing orders
            // Emit order placed event
        }

        #[spacetimedb::reducer]
        pub fn cancel_order(
            ctx: &ReducerContext,
            order_id: u64,
        ) -> Result<(), String> {
            // Only order owner can cancel
            // Return locked items/CELTIC
        }

        #[spacetimedb::reducer]
        pub fn fill_order(
            ctx: &ReducerContext,
            order_id: u64,
            quantity: u32,
        ) -> Result<(), String> {
            // Transfer items and CELTIC
            // Update order status
            // Emit trade completed event
        }
        ```
        """
    )
    return


@app.cell
def _():
    from dataclasses import dataclass
    from enum import Enum
    from typing import Optional
    import time as time_module

    class OrderType(Enum):
        BUY = "buy"
        SELL = "sell"

    class OrderStatus(Enum):
        OPEN = "open"
        FILLED = "filled"
        PARTIAL = "partial"
        CANCELLED = "cancelled"

    @dataclass
    class TradeOrder:
        order_id: int
        player: str
        item_id: int
        item_name: str
        quantity: int
        price_per_item: float
        order_type: OrderType
        status: OrderStatus
        filled_qty: int = 0

    class OrderBook:
        """Simulated order book for rare items."""

        def __init__(self):
            self.orders = {}
            self.next_id = 1
            self.trade_history = []

        def place_order(
            self,
            player: str,
            item_id: int,
            item_name: str,
            quantity: int,
            price: float,
            order_type: OrderType
        ) -> TradeOrder:
            order = TradeOrder(
                order_id=self.next_id,
                player=player,
                item_id=item_id,
                item_name=item_name,
                quantity=quantity,
                price_per_item=price,
                order_type=order_type,
                status=OrderStatus.OPEN,
            )
            self.orders[self.next_id] = order
            self.next_id += 1

            # Try to match
            self._match_orders(order)

            return order

        def _match_orders(self, new_order: TradeOrder):
            """Try to match new order with existing orders."""
            opposite_type = OrderType.SELL if new_order.order_type == OrderType.BUY else OrderType.BUY

            matching_orders = [
                o for o in self.orders.values()
                if o.order_id != new_order.order_id
                and o.item_id == new_order.item_id
                and o.order_type == opposite_type
                and o.status == OrderStatus.OPEN
            ]

            # Sort by price (best first)
            if new_order.order_type == OrderType.BUY:
                # For buy order, match with lowest sell prices
                matching_orders.sort(key=lambda x: x.price_per_item)
                matching_orders = [o for o in matching_orders if o.price_per_item <= new_order.price_per_item]
            else:
                # For sell order, match with highest buy prices
                matching_orders.sort(key=lambda x: -x.price_per_item)
                matching_orders = [o for o in matching_orders if o.price_per_item >= new_order.price_per_item]

            remaining = new_order.quantity - new_order.filled_qty

            for match in matching_orders:
                if remaining <= 0:
                    break

                available = match.quantity - match.filled_qty
                fill_qty = min(remaining, available)

                # Execute trade
                match.filled_qty += fill_qty
                new_order.filled_qty += fill_qty
                remaining -= fill_qty

                # Update statuses
                if match.filled_qty >= match.quantity:
                    match.status = OrderStatus.FILLED
                else:
                    match.status = OrderStatus.PARTIAL

                self.trade_history.append({
                    "buyer": new_order.player if new_order.order_type == OrderType.BUY else match.player,
                    "seller": match.player if new_order.order_type == OrderType.BUY else new_order.player,
                    "item_name": new_order.item_name,
                    "quantity": fill_qty,
                    "price": match.price_per_item,
                    "total": fill_qty * match.price_per_item,
                })

            if new_order.filled_qty >= new_order.quantity:
                new_order.status = OrderStatus.FILLED
            elif new_order.filled_qty > 0:
                new_order.status = OrderStatus.PARTIAL

        def get_order_book(self, item_id: int) -> dict:
            """Get buy/sell orders for an item."""
            buys = [o for o in self.orders.values()
                    if o.item_id == item_id and o.order_type == OrderType.BUY and o.status == OrderStatus.OPEN]
            sells = [o for o in self.orders.values()
                     if o.item_id == item_id and o.order_type == OrderType.SELL and o.status == OrderStatus.OPEN]

            buys.sort(key=lambda x: -x.price_per_item)  # Highest first
            sells.sort(key=lambda x: x.price_per_item)   # Lowest first

            return {"buys": buys, "sells": sells}

    # Demo order book
    book = OrderBook()

    # Legendary sword trading
    sword_id = 7
    sword_name = "Claíomh Solais (Sword of Light)"

    print("=== Legendary Item Order Book ===\n")
    print(f"Item: {sword_name}\n")

    # Place some sell orders
    book.place_order("seller1", sword_id, sword_name, 1, 1600, OrderType.SELL)
    book.place_order("seller2", sword_id, sword_name, 1, 1550, OrderType.SELL)
    book.place_order("seller3", sword_id, sword_name, 2, 1700, OrderType.SELL)

    # Place some buy orders
    book.place_order("buyer1", sword_id, sword_name, 1, 1400, OrderType.BUY)
    book.place_order("buyer2", sword_id, sword_name, 1, 1450, OrderType.BUY)

    # Show order book
    ob = book.get_order_book(sword_id)

    print("SELL ORDERS (Asks):")
    for order in ob["sells"]:
        remaining = order.quantity - order.filled_qty
        print(f"  {remaining}x @ {order.price_per_item:.0f} CELTIC (by {order.player})")

    print("\nBUY ORDERS (Bids):")
    for order in ob["buys"]:
        remaining = order.quantity - order.filled_qty
        print(f"  {remaining}x @ {order.price_per_item:.0f} CELTIC (by {order.player})")

    # Now a buyer matches!
    print("\n--- New Order: buyer3 buys 1 @ 1550 CELTIC ---\n")
    new_order = book.place_order("buyer3", sword_id, sword_name, 1, 1550, OrderType.BUY)

    print(f"Order Status: {new_order.status.value}")
    if book.trade_history:
        trade = book.trade_history[-1]
        print(f"Trade Executed: {trade['buyer']} bought {trade['quantity']}x from {trade['seller']} @ {trade['price']:.0f} CELTIC")
    return (
        OrderBook,
        OrderStatus,
        OrderType,
        TradeOrder,
        book,
        dataclass,
        new_order,
        ob,
        order,
        remaining,
        sword_id,
        sword_name,
        time_module,
        trade,
    )


@app.cell
def _(mo):
    mo.md(
        """
        ## 4. Guild Treasury

        ### Collective Resource Management:

        ```rust
        #[spacetimedb::table(public)]
        pub struct GuildTreasury {
            #[primary_key]
            guild_id: u64,
            celtic_balance: u64,
            lp_positions: Vec<LPPosition>,
            pending_proposals: Vec<ProposalId>,
        }

        #[spacetimedb::table(public)]
        pub struct TreasuryProposal {
            #[primary_key]
            proposal_id: u64,
            guild_id: u64,
            proposer: Identity,
            action: TreasuryAction,
            votes_for: u32,
            votes_against: u32,
            status: ProposalStatus,
            expires_at: Timestamp,
        }

        #[derive(Debug, Clone)]
        pub enum TreasuryAction {
            AddLiquidity { pool_id: u64, celtic: u64, items: u32 },
            RemoveLiquidity { pool_id: u64, lp_tokens: u64 },
            BuyItem { item_id: u32, max_price: u64 },
            SellItem { item_id: u32, quantity: u32, min_price: u64 },
            Transfer { recipient: Identity, celtic: u64 },
        }
        ```

        ### Governance Flow:

        ```
        1. Member proposes action (e.g., "Provide 10k CELTIC to Apple pool")
        2. Guild votes (majority required)
        3. If passed, action executes automatically
        4. LP tokens held in treasury
        5. Yields distributed to members proportionally
        ```
        """
    )
    return


@app.cell
def _():
    class Guild:
        """Simulated guild with treasury."""

        def __init__(self, guild_id: int, name: str, members: list):
            self.guild_id = guild_id
            self.name = name
            self.members = members
            self.celtic_balance = 0
            self.lp_positions = {}  # pool_name -> lp_tokens
            self.item_inventory = {}  # item_id -> quantity

        def deposit_celtic(self, member: str, amount: float):
            if member not in self.members:
                raise ValueError("Not a member")
            self.celtic_balance += amount

        def get_member_share(self, member: str) -> float:
            if member not in self.members:
                return 0
            return 1.0 / len(self.members)  # Equal shares for demo

        def add_liquidity(self, pool, celtic: float, items: int):
            if celtic > self.celtic_balance:
                raise ValueError("Insufficient CELTIC")
            if items > self.item_inventory.get(pool.item_id, 0):
                raise ValueError("Insufficient items")

            lp_tokens = pool.add_liquidity(f"guild_{self.guild_id}", celtic, items)
            self.celtic_balance -= celtic
            self.item_inventory[pool.item_id] = self.item_inventory.get(pool.item_id, 0) - items
            self.lp_positions[pool.item_name] = self.lp_positions.get(pool.item_name, 0) + lp_tokens

            return lp_tokens

    # Demo guild treasury
    guild = Guild(
        guild_id=1,
        name="Clann na Gaeilge",
        members=["player1", "player2", "player3", "player4"]
    )

    # Fund the guild
    guild.celtic_balance = 50000
    guild.item_inventory = {1: 500, 4: 50, 9: 20}  # Apples, swords, cloaks

    print("=== Guild Treasury: Clann na Gaeilge ===\n")
    print(f"Members: {len(guild.members)}")
    print(f"CELTIC Balance: {guild.celtic_balance:,.0f}")
    print(f"Items:")
    print(f"  Golden Apples: {guild.item_inventory.get(1, 0)}")
    print(f"  Bronze Swords: {guild.item_inventory.get(4, 0)}")
    print(f"  Feather Cloaks: {guild.item_inventory.get(9, 0)}")

    # Simulate LP provision
    print("\n--- Guild Action: Provide Liquidity to Apple Pool ---\n")
    from sruth.tuath.notebooks.speedrun import _

    # Recreate pool for demo
    class SimplePool:
        def __init__(self):
            self.item_id = 1
            self.item_name = "Ubhla Óir (Golden Apple)"
            self.reserve_celtic = 10000
            self.reserve_items = 200
            self.total_lp = 1414
            self.lp_holders = {}

        def add_liquidity(self, provider, celtic, items):
            lp_tokens = min(
                celtic / self.reserve_celtic * self.total_lp,
                items / self.reserve_items * self.total_lp
            )
            self.lp_holders[provider] = self.lp_holders.get(provider, 0) + lp_tokens
            self.reserve_celtic += celtic
            self.reserve_items += items
            self.total_lp += lp_tokens
            return lp_tokens

    pool = SimplePool()
    lp_received = guild.add_liquidity(pool, 5000, 100)

    print(f"Deposited: 5,000 CELTIC + 100 Apples")
    print(f"Received: {lp_received:.2f} LP tokens")
    print(f"\nGuild LP Positions: {guild.lp_positions}")
    print(f"Remaining CELTIC: {guild.celtic_balance:,.0f}")
    print(f"Remaining Apples: {guild.item_inventory.get(1, 0)}")
    return Guild, SimplePool, guild, lp_received, pool


@app.cell
def _(mo):
    mo.md(
        """
        ## 5. Frontend Integration

        ### Trade UI Component:

        ```tsx
        // components/ItemExchange.tsx
        import { useState } from 'react';
        import { useItemPools, useOrderBook } from '../hooks/trading';

        export function ItemExchange({ itemId }: { itemId: number }) {
          const [mode, setMode] = useState<'swap' | 'limit'>('swap');
          const pool = useItemPools(itemId);
          const orderBook = useOrderBook(itemId);

          return (
            <div className="exchange-container">
              <div className="mode-toggle">
                <button onClick={() => setMode('swap')}>Instant Swap</button>
                <button onClick={() => setMode('limit')}>Limit Order</button>
              </div>

              {mode === 'swap' ? (
                <SwapPanel pool={pool} />
              ) : (
                <OrderBookPanel
                  bids={orderBook.buys}
                  asks={orderBook.sells}
                  onPlaceOrder={handlePlaceOrder}
                />
              )}

              <PriceChart itemId={itemId} />
            </div>
          );
        }

        function SwapPanel({ pool }) {
          const [celticAmount, setCelticAmount] = useState(0);
          const expectedItems = pool.getAmountOut(celticAmount);
          const priceImpact = pool.getPriceImpact(celticAmount);

          return (
            <div>
              <input
                type="number"
                value={celticAmount}
                onChange={e => setCelticAmount(Number(e.target.value))}
                placeholder="CELTIC amount"
              />
              <div>Expected: {expectedItems} items</div>
              <div>Price Impact: {priceImpact.toFixed(2)}%</div>
              <button onClick={() => pool.swap(celticAmount)}>
                Swap
              </button>
            </div>
          );
        }
        ```
        """
    )
    return


@app.cell
def _(mo):
    mo.md(
        """
        ## 6. Price Discovery Mechanics

        ### How Rare Item Prices Are Discovered:

        ```
        1. FLOOR PRICE (Order Book)
           └── Lowest active sell order

        2. LAST TRADE PRICE
           └── Most recent executed trade

        3. AVERAGE PRICE (TWAP)
           └── Time-weighted average from AMM

        4. FAIR VALUE ESTIMATE
           └── Based on rarity, stats, and comparable items
        ```

        ### Price Factors for Celtic Items:

        | Factor | Weight | Example |
        |--------|--------|---------|
        | Base Rarity | 40% | Legendary = 10x common |
        | Stat Bonuses | 30% | +50 strength = +25% |
        | Supply | 20% | Only 100 exist = +50% |
        | Demand | 10% | High trade volume = +10% |

        ### Example Calculation:

        ```
        Claíomh Solais (Sword of Light):
        - Base Value: 100 CELTIC (common sword)
        - Rarity Mult: x10 (legendary)
        - Stat Bonus: +50 all stats = +50%
        - Supply: ~50 in circulation = +30%
        - Demand: High = +20%

        Estimated Value: 100 * 10 * 1.5 * 1.3 * 1.2 = 2,340 CELTIC
        ```
        """
    )
    return


@app.cell
def _(mo):
    mo.md(
        """
        ## 7. Next Steps

        ### For SpeedRunEthereum:
        1. Deploy CelticDEX.sol to testnet
        2. Create CELTIC/ETH pool
        3. Test swap mechanics
        4. Submit for verification

        ### For Tuath Integration:
        1. Build SpacetimeDB order book
        2. Create item pool factory contract
        3. Implement guild treasury governance
        4. Build React trading UI
        5. Add price charts and history

        ### Related Notebooks:
        - `02_token_shop.py` - Basic buying/selling
        - `03_quest_randomness.py` - Loot drops create supply
        - `05_skill_lending.py` - Borrow items for quests
        """
    )
    return


if __name__ == "__main__":
    app.run()
