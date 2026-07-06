"""
Challenge 5: Skill & Item Lending - tuath Game Economy

SpeedRunEthereum Challenge: https://speedrunethereum.com/challenge/lending

Learning Objectives:
- Reputation-based collateral (XP as collateral)
- Temporal lending (time-limited borrowing)
- Guild loan guarantees
- Item rental for quests

Tuath Integration:
- Skill/item lending for quests
- XP as reputation collateral
- Guild treasury backing
- SpacetimeDB lending records
"""

import marimo

__generated_with = "0.10.0"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo

    mo.md("""
    # Challenge 5: Skill & Item Lending System

    **SpeedRunEthereum Challenge 5** implements over-collateralized lending.

    For **tuath**, we adapt this to a **game economy** where:
    - Players can **borrow powerful items** for quests
    - **XP (reputation)** serves as collateral
    - **Guilds** can guarantee loans for members
    - Lending is **time-limited** (item returns after quest)

    This enables players to access high-tier content without permanently owning rare items.
    """)
    return (mo,)


@app.cell
def _():
    """Core types for skill lending system."""
    import uuid
    from dataclasses import dataclass, field
    from datetime import datetime, timedelta
    from enum import Enum
    from typing import Optional

    class ItemTier(Enum):
        COMMON = 1
        UNCOMMON = 2
        RARE = 3
        EPIC = 4
        LEGENDARY = 5

    class LoanStatus(Enum):
        ACTIVE = "active"
        RETURNED = "returned"
        DEFAULTED = "defaulted"
        GUARANTEED = "guaranteed"

    @dataclass
    class GameItem:
        """A borrowable game item."""
        item_id: str
        name: str
        name_irish: str
        tier: ItemTier
        power_level: int
        rental_cost_per_hour: float  # In CELTIC tokens
        min_xp_required: int  # Minimum XP to borrow
        owner: str
        is_available: bool = True

    @dataclass
    class ItemLoan:
        """An active item loan."""
        loan_id: str
        borrower: str
        item: GameItem
        xp_collateral: int
        celtic_deposit: float
        start_time: datetime
        duration_hours: int
        guild_guarantor: str | None = None
        status: LoanStatus = LoanStatus.ACTIVE
        quest_id: str | None = None

        @property
        def end_time(self) -> datetime:
            return self.start_time + timedelta(hours=self.duration_hours)

        @property
        def is_expired(self) -> bool:
            return datetime.now() > self.end_time

        @property
        def time_remaining(self) -> timedelta:
            remaining = self.end_time - datetime.now()
            return remaining if remaining.total_seconds() > 0 else timedelta(0)

    @dataclass
    class PlayerStats:
        """Player reputation and lending stats."""
        address: str
        total_xp: int
        available_xp: int  # Not locked as collateral
        completed_loans: int
        defaulted_loans: int
        guild_id: str | None = None

        @property
        def reputation_score(self) -> float:
            """Calculate reputation (0-1 scale)."""
            if self.completed_loans + self.defaulted_loans == 0:
                return 0.5  # Neutral for new players
            success_rate = self.completed_loans / (self.completed_loans + self.defaulted_loans)
            # Weight by total loans for confidence
            confidence = min(1.0, (self.completed_loans + self.defaulted_loans) / 10)
            return success_rate * confidence + 0.5 * (1 - confidence)

    @dataclass
    class Guild:
        """Guild with loan guarantee capability."""
        guild_id: str
        name: str
        name_irish: str
        treasury_celtic: float
        member_count: int
        total_guaranteed: float = 0
        active_guarantees: list = field(default_factory=list)

        @property
        def available_guarantee_capacity(self) -> float:
            """Max additional guarantees guild can provide."""
            # Can guarantee up to 50% of treasury
            max_capacity = self.treasury_celtic * 0.5
            return max(0, max_capacity - self.total_guaranteed)
    return (
        GameItem,
        Guild,
        ItemLoan,
        ItemTier,
        LoanStatus,
        PlayerStats,
        Optional,
        dataclass,
        datetime,
        field,
        timedelta,
        uuid,
    )


@app.cell
def _(mo):
    mo.md("""
    ## Lending Mechanics

    The skill lending system uses a **hybrid collateral model**:

    ### 1. XP Collateral (Reputation)
    - Players lock XP as "reputation stake"
    - Defaulting loses XP (reputation damage)
    - Higher XP = lower deposit requirements

    ### 2. Token Deposit
    - CELTIC tokens locked during loan
    - Returned on successful item return
    - Covers item value if player defaults

    ### 3. Guild Guarantees
    - Guild treasury can back member loans
    - Reduces individual deposit requirements
    - Guild reputation affected by member defaults
    """)
    return ()


@app.cell
def _(
    GameItem,
    Guild,
    ItemLoan,
    ItemTier,
    LoanStatus,
    PlayerStats,
    datetime,
    uuid,
):
    """Skill lending protocol implementation."""

    class SkillLendingProtocol:
        """
        Game item lending protocol for tuath.

        Features:
        - XP-based reputation collateral
        - Time-limited borrowing
        - Guild guarantees
        - Quest-linked lending
        """

        def __init__(self):
            self.items: dict[str, GameItem] = {}
            self.loans: dict[str, ItemLoan] = {}
            self.players: dict[str, PlayerStats] = {}
            self.guilds: dict[str, Guild] = {}

            # Collateral requirements by tier
            self.tier_collateral_multipliers = {
                ItemTier.COMMON: 1.0,
                ItemTier.UNCOMMON: 1.5,
                ItemTier.RARE: 2.0,
                ItemTier.EPIC: 3.0,
                ItemTier.LEGENDARY: 5.0
            }

            # XP discount rates (higher reputation = lower deposit)
            self.xp_discount_tiers = [
                (10000, 0.20),  # 20% discount at 10k+ XP
                (5000, 0.15),
                (2500, 0.10),
                (1000, 0.05),
                (0, 0.0)
            ]

        def register_player(self, address: str, xp: int, guild_id: str | None = None) -> PlayerStats:
            """Register a new player."""
            player = PlayerStats(
                address=address,
                total_xp=xp,
                available_xp=xp,
                completed_loans=0,
                defaulted_loans=0,
                guild_id=guild_id
            )
            self.players[address] = player
            return player

        def register_guild(self, name: str, name_irish: str, treasury: float) -> Guild:
            """Register a new guild."""
            guild = Guild(
                guild_id=str(uuid.uuid4())[:8],
                name=name,
                name_irish=name_irish,
                treasury_celtic=treasury,
                member_count=0
            )
            self.guilds[guild.guild_id] = guild
            return guild

        def list_item(
            self,
            owner: str,
            name: str,
            name_irish: str,
            tier: ItemTier,
            power_level: int,
            hourly_rate: float,
            min_xp: int
        ) -> GameItem:
            """List an item for lending."""
            item = GameItem(
                item_id=str(uuid.uuid4())[:8],
                name=name,
                name_irish=name_irish,
                tier=tier,
                power_level=power_level,
                rental_cost_per_hour=hourly_rate,
                min_xp_required=min_xp,
                owner=owner
            )
            self.items[item.item_id] = item
            return item

        def calculate_deposit(
            self,
            item: GameItem,
            borrower: PlayerStats,
            hours: int,
            guild_guarantee: float = 0
        ) -> dict:
            """
            Calculate required deposit for borrowing.

            Factors:
            - Item tier and power level
            - Borrower XP (reputation discount)
            - Guild guarantee (reduces deposit)
            - Rental duration
            """
            # Base deposit: item value estimate (power_level * tier multiplier)
            base_value = item.power_level * self.tier_collateral_multipliers[item.tier] * 100
            base_deposit = base_value * 1.5  # 150% collateral ratio

            # Rental cost
            rental_cost = item.rental_cost_per_hour * hours

            # XP discount
            xp_discount = 0
            for xp_threshold, discount in self.xp_discount_tiers:
                if borrower.total_xp >= xp_threshold:
                    xp_discount = discount
                    break

            # Reputation modifier
            rep_modifier = 1.0 - (borrower.reputation_score * 0.3)  # Up to 30% reduction

            adjusted_deposit = base_deposit * (1 - xp_discount) * rep_modifier

            # Subtract guild guarantee
            final_deposit = max(0, adjusted_deposit - guild_guarantee)

            # XP collateral (10% of deposit value equivalent in XP)
            xp_collateral = int(adjusted_deposit * 0.1)

            return {
                "base_deposit": base_deposit,
                "rental_cost": rental_cost,
                "xp_discount_percent": xp_discount * 100,
                "reputation_modifier": rep_modifier,
                "guild_guarantee": guild_guarantee,
                "final_deposit": final_deposit,
                "xp_collateral": xp_collateral,
                "total_cost": final_deposit + rental_cost
            }

        def borrow_item(
            self,
            borrower_address: str,
            item_id: str,
            hours: int,
            quest_id: str | None = None,
            guild_guarantee: float = 0
        ) -> dict:
            """Borrow an item for a quest."""
            item = self.items.get(item_id)
            if not item:
                return {"success": False, "error": "Item not found"}

            if not item.is_available:
                return {"success": False, "error": "Item not available"}

            borrower = self.players.get(borrower_address)
            if not borrower:
                return {"success": False, "error": "Player not registered"}

            if borrower.total_xp < item.min_xp_required:
                return {"success": False, "error": f"Minimum {item.min_xp_required} XP required"}

            # Calculate deposit
            deposit_info = self.calculate_deposit(item, borrower, hours, guild_guarantee)

            # Check XP collateral
            if borrower.available_xp < deposit_info["xp_collateral"]:
                return {"success": False, "error": "Insufficient XP for collateral"}

            # Create loan
            loan = ItemLoan(
                loan_id=str(uuid.uuid4())[:8],
                borrower=borrower_address,
                item=item,
                xp_collateral=deposit_info["xp_collateral"],
                celtic_deposit=deposit_info["final_deposit"],
                start_time=datetime.now(),
                duration_hours=hours,
                guild_guarantor=borrower.guild_id if guild_guarantee > 0 else None,
                status=LoanStatus.GUARANTEED if guild_guarantee > 0 else LoanStatus.ACTIVE,
                quest_id=quest_id
            )

            # Update state
            item.is_available = False
            borrower.available_xp -= deposit_info["xp_collateral"]
            self.loans[loan.loan_id] = loan

            return {
                "success": True,
                "loan_id": loan.loan_id,
                "item": item.name,
                "duration_hours": hours,
                "deposit_paid": deposit_info["final_deposit"],
                "xp_locked": deposit_info["xp_collateral"],
                "return_deadline": loan.end_time.isoformat()
            }

        def return_item(self, loan_id: str) -> dict:
            """Return a borrowed item."""
            loan = self.loans.get(loan_id)
            if not loan:
                return {"success": False, "error": "Loan not found"}

            if loan.status != LoanStatus.ACTIVE and loan.status != LoanStatus.GUARANTEED:
                return {"success": False, "error": "Loan not active"}

            borrower = self.players[loan.borrower]

            # Check if late
            is_late = loan.is_expired
            late_penalty = 0
            xp_penalty = 0

            if is_late:
                # Late fee: 10% of deposit per hour late
                hours_late = (datetime.now() - loan.end_time).total_seconds() / 3600
                late_penalty = loan.celtic_deposit * 0.1 * min(hours_late, 10)  # Cap at 100%
                xp_penalty = int(loan.xp_collateral * 0.1 * min(hours_late, 5))  # Cap at 50%

            # Return item
            loan.item.is_available = True
            loan.status = LoanStatus.RETURNED

            # Return collateral (minus penalties)
            returned_xp = loan.xp_collateral - xp_penalty
            returned_deposit = loan.celtic_deposit - late_penalty

            borrower.available_xp += returned_xp
            borrower.completed_loans += 1

            return {
                "success": True,
                "was_late": is_late,
                "late_penalty": late_penalty,
                "xp_penalty": xp_penalty,
                "deposit_returned": returned_deposit,
                "xp_returned": returned_xp,
                "reputation_score": borrower.reputation_score
            }

        def default_loan(self, loan_id: str) -> dict:
            """Process a defaulted loan (item not returned)."""
            loan = self.loans.get(loan_id)
            if not loan:
                return {"success": False, "error": "Loan not found"}

            borrower = self.players[loan.borrower]

            # Borrower loses all collateral
            loan.status = LoanStatus.DEFAULTED
            borrower.defaulted_loans += 1
            # XP already locked - now permanently lost
            borrower.total_xp -= loan.xp_collateral

            # Item owner compensated from deposit
            owner_compensation = loan.celtic_deposit

            # If guild guaranteed, they cover the difference
            guild_penalty = 0
            if loan.guild_guarantor:
                guild = self.guilds.get(loan.guild_guarantor)
                if guild:
                    guild_penalty = owner_compensation * 0.5  # Guild covers 50%
                    guild.treasury_celtic -= guild_penalty

            return {
                "success": True,
                "xp_forfeited": loan.xp_collateral,
                "deposit_forfeited": loan.celtic_deposit,
                "owner_compensation": owner_compensation,
                "guild_penalty": guild_penalty,
                "new_reputation": borrower.reputation_score
            }

    # Initialize protocol
    protocol = SkillLendingProtocol()
    print("Skill Lending Protocol Initialized")
    return SkillLendingProtocol, protocol


@app.cell
def _(ItemTier, protocol):
    """Demo the lending system."""

    print("Skill Lending System Demo")
    print("=" * 60)

    # Register players
    player_a = protocol.register_player("player_a", xp=5000)
    player_b = protocol.register_player("player_b", xp=15000)

    print("\nRegistered Players:")
    print(f"  Player A: {player_a.total_xp} XP, Reputation: {player_a.reputation_score:.2f}")
    print(f"  Player B: {player_b.total_xp} XP, Reputation: {player_b.reputation_score:.2f}")

    # Register a guild
    guild = protocol.register_guild(
        "Fianna Warriors",
        "Laochra na Fianna",
        treasury=50000
    )
    player_b.guild_id = guild.guild_id
    print(f"\nGuild: {guild.name} (Treasury: {guild.treasury_celtic:,.0f} CELTIC)")

    # List items
    sword = protocol.list_item(
        owner="npc_blacksmith",
        name="Sword of Lugh",
        name_irish="Claíomh Lugh",
        tier=ItemTier.LEGENDARY,
        power_level=100,
        hourly_rate=50,
        min_xp=1000
    )

    staff = protocol.list_item(
        owner="npc_druid",
        name="Staff of Brigid",
        name_irish="Bata Bhríd",
        tier=ItemTier.EPIC,
        power_level=75,
        hourly_rate=35,
        min_xp=500
    )

    print("\nAvailable Items:")
    print(f"  {sword.name} ({sword.name_irish}) - {sword.tier.name}, Power: {sword.power_level}")
    print(f"  {staff.name} ({staff.name_irish}) - {staff.tier.name}, Power: {staff.power_level}")

    # Calculate deposits for different scenarios
    print("\n" + "=" * 60)
    print("Deposit Calculations (4-hour rental)")
    print("-" * 60)

    # Player A (lower XP, no guild)
    deposit_a = protocol.calculate_deposit(sword, player_a, hours=4)
    print(f"\nPlayer A borrowing {sword.name}:")
    print(f"  Base Deposit: {deposit_a['base_deposit']:,.0f} CELTIC")
    print(f"  XP Discount: {deposit_a['xp_discount_percent']:.0f}%")
    print(f"  Rep Modifier: {deposit_a['reputation_modifier']:.2f}x")
    print(f"  Final Deposit: {deposit_a['final_deposit']:,.0f} CELTIC")
    print(f"  XP Collateral: {deposit_a['xp_collateral']:,} XP")

    # Player B (higher XP, guild guarantee)
    deposit_b = protocol.calculate_deposit(sword, player_b, hours=4, guild_guarantee=20000)
    print(f"\nPlayer B borrowing {sword.name} (with guild guarantee):")
    print(f"  Base Deposit: {deposit_b['base_deposit']:,.0f} CELTIC")
    print(f"  XP Discount: {deposit_b['xp_discount_percent']:.0f}%")
    print(f"  Rep Modifier: {deposit_b['reputation_modifier']:.2f}x")
    print(f"  Guild Guarantee: {deposit_b['guild_guarantee']:,.0f} CELTIC")
    print(f"  Final Deposit: {deposit_b['final_deposit']:,.0f} CELTIC")
    print(f"  XP Collateral: {deposit_b['xp_collateral']:,} XP")
    return deposit_a, deposit_b, guild, player_a, player_b, staff, sword


@app.cell
def _(protocol, staff):
    """Simulate a full lending cycle."""

    print("\nLending Cycle Simulation")
    print("=" * 60)

    # Player A borrows the staff
    print("\n1. Player A borrows Staff of Brigid for a quest:")
    borrow_result = protocol.borrow_item(
        "player_a",
        staff.item_id,
        hours=2,
        quest_id="quest_dungeon_001"
    )

    if borrow_result["success"]:
        print(f"   Loan ID: {borrow_result['loan_id']}")
        print(f"   Item: {borrow_result['item']}")
        print(f"   Deposit Paid: {borrow_result['deposit_paid']:,.0f} CELTIC")
        print(f"   XP Locked: {borrow_result['xp_locked']:,}")
        print(f"   Return By: {borrow_result['return_deadline']}")

        loan_id = borrow_result['loan_id']

        # Complete quest and return
        print("\n2. Player A completes quest and returns item:")
        return_result = protocol.return_item(loan_id)

        if return_result["success"]:
            print(f"   Was Late: {return_result['was_late']}")
            print(f"   Deposit Returned: {return_result['deposit_returned']:,.0f} CELTIC")
            print(f"   XP Returned: {return_result['xp_returned']:,}")
            print(f"   New Reputation: {return_result['reputation_score']:.3f}")
    else:
        print(f"   Error: {borrow_result['error']}")
        loan_id = None
    return borrow_result, loan_id, return_result


@app.cell
def _(mo):
    mo.md("""
    ## Guild Guarantee System

    Guilds can **back loans for members**, reducing individual deposit requirements:

    ```
    Guild Guarantee Benefits:
    - Reduces player deposit by guarantee amount
    - Guild treasury locked as backing
    - If player defaults, guild covers 50% loss

    Guild Guarantee Limits:
    - Max 50% of treasury as active guarantees
    - Members must be in good standing
    - Guild reputation affects guarantee power
    ```

    This creates **social accountability** - guilds vet members and members protect guild reputation.
    """)
    return ()


@app.cell
def _():
    """Guild guarantee system."""

    class GuildGuaranteeSystem:
        """
        Guild-backed loan guarantees.

        Enables:
        - Lower deposits for guild members
        - Social accountability
        - Guild treasury as collective insurance
        """

        def __init__(self):
            self.guarantee_limits = {
                "new_member": 0.1,      # 10% of treasury
                "active_member": 0.2,   # 20% of treasury
                "veteran": 0.3,         # 30% of treasury
                "officer": 0.4,         # 40% of treasury
                "leader": 0.5           # 50% of treasury
            }

        def calculate_member_limit(
            self,
            guild_treasury: float,
            member_rank: str,
            member_completed_loans: int,
            member_defaults: int
        ) -> float:
            """Calculate max guarantee for a member."""
            base_limit = guild_treasury * self.guarantee_limits.get(member_rank, 0.1)

            # Reduce if member has defaults
            if member_defaults > 0:
                penalty = min(0.5, member_defaults * 0.1)
                base_limit *= (1 - penalty)

            # Bonus for proven track record
            if member_completed_loans >= 10 and member_defaults == 0:
                base_limit *= 1.2

            return base_limit

        def request_guarantee(
            self,
            guild_treasury: float,
            guild_available: float,
            member_rank: str,
            requested_amount: float,
            loan_item_tier: str
        ) -> dict:
            """Process a guarantee request."""
            max_guarantee = self.calculate_member_limit(
                guild_treasury,
                member_rank,
                0, 0  # Would check actual member stats
            )

            # Cap at available capacity
            approved_amount = min(requested_amount, max_guarantee, guild_available)

            if approved_amount < requested_amount:
                partial = True
                message = f"Partial guarantee approved: {approved_amount:,.0f} of {requested_amount:,.0f}"
            else:
                partial = False
                message = f"Full guarantee approved: {approved_amount:,.0f}"

            return {
                "approved": approved_amount > 0,
                "amount": approved_amount,
                "partial": partial,
                "message": message,
                "remaining_capacity": guild_available - approved_amount
            }

    guarantee_system = GuildGuaranteeSystem()

    # Demo
    print("Guild Guarantee System")
    print("=" * 50)

    # Simulate guarantee requests
    scenarios = [
        ("new_member", 5000, "Uncommon item"),
        ("active_member", 15000, "Rare item"),
        ("veteran", 30000, "Epic item"),
        ("officer", 50000, "Legendary item"),
    ]

    guild_treasury = 100000
    guild_available = 50000  # 50% capacity

    print(f"\nGuild Treasury: {guild_treasury:,} CELTIC")
    print(f"Available for Guarantees: {guild_available:,} CELTIC")
    print("\nGuarantee Requests:")
    print("-" * 50)

    for rank, amount, item in scenarios:
        result = guarantee_system.request_guarantee(
            guild_treasury,
            guild_available,
            rank,
            amount,
            item
        )
        print(f"\n{rank.title()} requesting {amount:,} for {item}:")
        print(f"  {result['message']}")
        if result['approved']:
            guild_available = result['remaining_capacity']
    return GuildGuaranteeSystem, amount, guild_available, guild_treasury, guarantee_system, item, rank, result, scenarios


@app.cell
def _(mo):
    mo.md("""
    ## SpacetimeDB Integration

    Lending data stored in SpacetimeDB for real-time sync:

    ```rust
    #[spacetimedb::table]
    pub struct ItemLoan {
        #[primarykey]
        loan_id: String,
        borrower: Identity,
        item_id: String,
        xp_collateral: u64,
        celtic_deposit: u128,
        start_time: Timestamp,
        end_time: Timestamp,
        status: LoanStatus,
        guild_guarantor: Option<String>,
    }

    #[spacetimedb::reducer]
    pub fn borrow_item(
        ctx: ReducerContext,
        item_id: String,
        duration_hours: u32,
        guild_guarantee: Option<u128>
    ) -> Result<String, String> {
        // Verify player XP and collateral
        // Create loan record
        // Lock item and collateral
        // Return loan_id
    }
    ```
    """)
    return ()


@app.cell
def _():
    """SpacetimeDB schema for lending."""

    STDB_LENDING_SCHEMA = """
    // SpacetimeDB schema for tuath skill lending

    use spacetimedb::{Identity, Timestamp};

    #[derive(Debug, Clone, PartialEq)]
    pub enum LoanStatus {
        Active,
        Returned,
        Defaulted,
        Guaranteed,
    }

    #[derive(Debug, Clone, PartialEq)]
    pub enum ItemTier {
        Common,
        Uncommon,
        Rare,
        Epic,
        Legendary,
    }

    #[spacetimedb::table(public)]
    pub struct LendableItem {
        #[primarykey]
        pub item_id: String,
        pub owner: Identity,
        pub name: String,
        pub name_irish: String,
        pub tier: ItemTier,
        pub power_level: u32,
        pub hourly_rate: u64,  // In CELTIC wei
        pub min_xp_required: u64,
        pub is_available: bool,
    }

    #[spacetimedb::table(public)]
    pub struct ItemLoan {
        #[primarykey]
        pub loan_id: String,
        pub borrower: Identity,
        pub item_id: String,
        pub xp_collateral: u64,
        pub celtic_deposit: u128,
        pub start_time: Timestamp,
        pub end_time: Timestamp,
        pub status: LoanStatus,
        pub guild_guarantor: Option<String>,
        pub quest_id: Option<String>,
    }

    #[spacetimedb::table(public)]
    pub struct GuildGuarantee {
        #[primarykey]
        pub guarantee_id: String,
        pub guild_id: String,
        pub loan_id: String,
        pub amount: u128,
        pub is_active: bool,
    }

    #[spacetimedb::table(public)]
    pub struct LendingStats {
        #[primarykey]
        pub player: Identity,
        pub total_borrowed: u64,
        pub total_lent: u64,
        pub completed_loans: u32,
        pub defaulted_loans: u32,
        pub total_xp_earned: u64,  // From successful lending
    }

    // Reducers
    #[spacetimedb::reducer]
    pub fn list_item_for_lending(
        ctx: ReducerContext,
        item_id: String,
        hourly_rate: u64,
        min_xp: u64,
    ) -> Result<(), String>;

    #[spacetimedb::reducer]
    pub fn borrow_item(
        ctx: ReducerContext,
        item_id: String,
        duration_hours: u32,
        quest_id: Option<String>,
    ) -> Result<String, String>;

    #[spacetimedb::reducer]
    pub fn return_item(
        ctx: ReducerContext,
        loan_id: String,
    ) -> Result<(), String>;

    #[spacetimedb::reducer]
    pub fn request_guild_guarantee(
        ctx: ReducerContext,
        loan_id: String,
        amount: u128,
    ) -> Result<String, String>;

    // Subscriptions for real-time updates
    #[spacetimedb::subscription]
    pub fn on_loan_status_change(loan: &ItemLoan) {
        // Notify borrower and lender of status changes
    }

    #[spacetimedb::subscription]
    pub fn on_item_available(item: &LendableItem) {
        // Notify watchers when item becomes available
    }
    """

    print("SpacetimeDB Lending Schema")
    print("=" * 50)
    print("\nTables:")
    print("  - LendableItem: Items available for borrowing")
    print("  - ItemLoan: Active and historical loans")
    print("  - GuildGuarantee: Guild-backed loan guarantees")
    print("  - LendingStats: Player lending statistics")
    print("\nReducers:")
    print("  - list_item_for_lending: Make item available")
    print("  - borrow_item: Create a new loan")
    print("  - return_item: Complete a loan")
    print("  - request_guild_guarantee: Get guild backing")
    print("\nSubscriptions:")
    print("  - on_loan_status_change: Real-time loan updates")
    print("  - on_item_available: Item availability alerts")
    return (STDB_LENDING_SCHEMA,)


@app.cell
def _(mo):
    mo.md("""
    ## Solana Integration: celtic-lending Program

    For Solana, we use:
    - **SPL Token** for CELTIC deposits
    - **PDA accounts** for loan state
    - **Clockwork** for loan expiry automation

    Key differences from Ethereum:
    - Rent-exempt accounts for loan state
    - Atomic CPI calls for multi-token transfers
    - Program-derived addresses for escrow
    """)
    return ()


@app.cell
def _():
    """Anchor program structure for celtic-lending."""

    ANCHOR_LENDING_PROGRAM = """
    // Anchor program for tuath skill lending on Solana

    use anchor_lang::prelude::*;
    use anchor_spl::token::{self, Token, TokenAccount, Transfer};

    declare_id!("LEND...your_program_id");

    #[program]
    pub mod celtic_lending {
        use super::*;

        pub fn list_item(
            ctx: Context<ListItem>,
            item_id: String,
            name: String,
            tier: u8,
            power_level: u32,
            hourly_rate: u64,
            min_xp: u64,
        ) -> Result<()> {
            let item = &mut ctx.accounts.item;
            item.owner = ctx.accounts.owner.key();
            item.item_id = item_id;
            item.name = name;
            item.tier = tier;
            item.power_level = power_level;
            item.hourly_rate = hourly_rate;
            item.min_xp_required = min_xp;
            item.is_available = true;
            Ok(())
        }

        pub fn borrow_item(
            ctx: Context<BorrowItem>,
            duration_hours: u32,
        ) -> Result<()> {
            let item = &mut ctx.accounts.item;
            let loan = &mut ctx.accounts.loan;
            let borrower = &ctx.accounts.borrower;

            require!(item.is_available, LendingError::ItemNotAvailable);

            // Calculate deposit
            let deposit = calculate_deposit(
                item.power_level,
                item.tier,
                duration_hours,
            );

            // Transfer deposit to escrow
            let cpi_accounts = Transfer {
                from: ctx.accounts.borrower_token.to_account_info(),
                to: ctx.accounts.escrow_token.to_account_info(),
                authority: borrower.to_account_info(),
            };
            let cpi_ctx = CpiContext::new(
                ctx.accounts.token_program.to_account_info(),
                cpi_accounts,
            );
            token::transfer(cpi_ctx, deposit)?;

            // Create loan record
            loan.borrower = borrower.key();
            loan.item = item.key();
            loan.deposit = deposit;
            loan.start_time = Clock::get()?.unix_timestamp;
            loan.end_time = loan.start_time + (duration_hours as i64 * 3600);
            loan.status = LoanStatus::Active;

            // Mark item unavailable
            item.is_available = false;

            emit!(LoanCreated {
                loan: loan.key(),
                borrower: borrower.key(),
                item: item.key(),
                deposit,
            });

            Ok(())
        }

        pub fn return_item(ctx: Context<ReturnItem>) -> Result<()> {
            let loan = &mut ctx.accounts.loan;
            let item = &mut ctx.accounts.item;

            require!(
                loan.status == LoanStatus::Active,
                LendingError::LoanNotActive
            );

            let clock = Clock::get()?;
            let is_late = clock.unix_timestamp > loan.end_time;

            // Calculate return amount (minus late fees if applicable)
            let mut return_amount = loan.deposit;
            if is_late {
                let hours_late = (clock.unix_timestamp - loan.end_time) / 3600;
                let penalty = (loan.deposit * hours_late as u64 * 10) / 100;
                return_amount = return_amount.saturating_sub(penalty);
            }

            // Return deposit from escrow
            // ... (escrow PDA transfer logic)

            loan.status = LoanStatus::Returned;
            item.is_available = true;

            Ok(())
        }
    }

    #[derive(Accounts)]
    pub struct BorrowItem<'info> {
        #[account(mut)]
        pub borrower: Signer<'info>,
        #[account(mut)]
        pub item: Account<'info, LendableItem>,
        #[account(
            init,
            payer = borrower,
            space = 8 + Loan::SIZE,
            seeds = [b"loan", item.key().as_ref(), borrower.key().as_ref()],
            bump
        )]
        pub loan: Account<'info, Loan>,
        #[account(mut)]
        pub borrower_token: Account<'info, TokenAccount>,
        #[account(mut)]
        pub escrow_token: Account<'info, TokenAccount>,
        pub token_program: Program<'info, Token>,
        pub system_program: Program<'info, System>,
    }

    #[account]
    pub struct LendableItem {
        pub owner: Pubkey,
        pub item_id: String,
        pub name: String,
        pub tier: u8,
        pub power_level: u32,
        pub hourly_rate: u64,
        pub min_xp_required: u64,
        pub is_available: bool,
    }

    #[account]
    pub struct Loan {
        pub borrower: Pubkey,
        pub item: Pubkey,
        pub deposit: u64,
        pub start_time: i64,
        pub end_time: i64,
        pub status: LoanStatus,
        pub guild_guarantee: Option<Pubkey>,
    }

    #[derive(AnchorSerialize, AnchorDeserialize, Clone, PartialEq)]
    pub enum LoanStatus {
        Active,
        Returned,
        Defaulted,
    }

    #[error_code]
    pub enum LendingError {
        #[msg("Item is not available for borrowing")]
        ItemNotAvailable,
        #[msg("Loan is not in active state")]
        LoanNotActive,
        #[msg("Insufficient XP for this item")]
        InsufficientXP,
    }

    #[event]
    pub struct LoanCreated {
        pub loan: Pubkey,
        pub borrower: Pubkey,
        pub item: Pubkey,
        pub deposit: u64,
    }
    """

    print("Anchor Lending Program Structure")
    print("=" * 50)
    print("\nInstructions:")
    print("  - list_item: Owner lists item for lending")
    print("  - borrow_item: Player borrows with deposit")
    print("  - return_item: Player returns and gets deposit back")
    print("\nAccounts:")
    print("  - LendableItem: Item metadata and availability")
    print("  - Loan: Active loan state with escrow")
    print("\nFeatures:")
    print("  - PDA-based escrow for deposits")
    print("  - Late fee calculation on return")
    print("  - Event emission for off-chain indexing")
    return (ANCHOR_LENDING_PROGRAM,)


@app.cell
def _(mo):
    mo.md("""
    ## Summary

    **Challenge 5 Key Learnings:**

    1. **Collateralization**
       - Over-collateralization protects lenders
       - XP as reputation-based collateral
       - Dynamic ratios based on player history

    2. **Temporal Lending**
       - Time-limited borrowing for quests
       - Late fees incentivize timely returns
       - Automatic expiry handling

    3. **Guild Guarantees**
       - Social accountability layer
       - Treasury-backed member loans
       - Collective reputation system

    4. **Cross-Chain Implementation**
       - Ethereum: CelticLending.sol
       - Solana: celtic-lending Anchor program
       - SpacetimeDB: Real-time state sync

    **Tuath Integration:**
    - Players borrow powerful items for hard quests
    - XP reputation unlocks better borrowing terms
    - Guilds support members with guarantees
    - Creates economic activity beyond token trading
    """)
    return ()


if __name__ == "__main__":
    app.run()
