"""
Challenge 3: Dice Game - Tuath Quest Randomness Implementation

SpeedRunEthereum Challenge: https://speedrunethereum.com/challenge/dice-game

Learning Objectives:
- Implement secure randomness for game mechanics
- Design loot drop tables with weighted probabilities
- Integrate commit-reveal for fair quest outcomes
- Connect to SpacetimeDB for real-time game state

Project Integration:
- Quest reward randomness in the Celtic MMO
- Loot drop tables for Celtic mythology items
- WGPU particle effects for dice animations
- Switchboard VRF for Solana integration
"""

import marimo

__generated_with = "0.10.14"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo

    mo.md(
        """
        # Challenge 3: Quest Randomness System

        ## Tuath Game Mechanics

        This notebook implements the randomness system for quests and loot
        drops in the tuath Celtic educational MMO.

        ### What We'll Build:
        1. **Commit-Reveal Quests** - Fair quest outcome determination
        2. **Loot Tables** - Weighted Celtic mythology items
        3. **Difficulty Scaling** - Harder quests = better rewards
        4. **VRF Integration** - Chainlink/Switchboard for high-stakes
        """
    )
    return (mo,)


@app.cell
def _(mo):
    mo.md(
        """
        ## 1. Quest System Overview

        ### Quest Flow:

        ```
        ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
        │   SELECT    │     │   COMMIT    │     │   REVEAL    │
        │   QUEST     │ --> │   SEED      │ --> │   OUTCOME   │
        │             │     │   (Wait)    │     │             │
        └─────────────┘     └─────────────┘     └─────────────┘
              │                   │                   │
              ▼                   ▼                   ▼
        Player chooses      Player submits      Random combined
        difficulty &        hash(secret)        with block hash
        quest type          to blockchain       for fair result
        ```

        ### Quest Difficulties:

        | Difficulty | Reward Multiplier | Rarity Boost | Time Limit |
        |------------|-------------------|--------------|------------|
        | Easy       | 1x                | None         | No limit   |
        | Medium     | 2x                | +5%          | 24 hours   |
        | Hard       | 5x                | +15%         | 6 hours    |
        | Legendary  | 10x               | +30%         | 1 hour     |

        ### Quest Types:

        - **Language Quests**: Complete Irish lessons for rewards
        - **Combat Quests**: Defeat Celtic creatures
        - **Exploration Quests**: Discover mythological locations
        - **Social Quests**: Teach other players
        """
    )
    return


@app.cell
def _():
    # Celtic mythology loot tables
    loot_tables = {
        "easy": {
            "common": [
                {"name": "Ubhla Óir", "name_en": "Golden Apple", "type": "consumable", "effect": "Restore 50 HP"},
                {"name": "Deoch Uisce", "name_en": "Water Drink", "type": "consumable", "effect": "Restore 25 MP"},
                {"name": "Cloch Bheag", "name_en": "Small Stone", "type": "crafting", "effect": "Crafting material"},
            ],
            "uncommon": [
                {"name": "Focail Nua", "name_en": "New Words", "type": "learning", "effect": "+10 vocabulary"},
                {"name": "Briathra", "name_en": "Verbs", "type": "learning", "effect": "+5 grammar"},
            ],
            "rare": [
                {"name": "Leabhar Beag", "name_en": "Small Book", "type": "learning", "effect": "Unlock bonus lesson"},
            ],
        },
        "medium": {
            "common": [
                {"name": "Sciath Umha", "name_en": "Bronze Shield", "type": "armor", "effect": "+10 defense"},
            ],
            "uncommon": [
                {"name": "Clóca Féileacáin", "name_en": "Butterfly Cloak", "type": "armor", "effect": "+5 agility"},
                {"name": "Bróga Reatha", "name_en": "Running Shoes", "type": "armor", "effect": "+15% speed"},
            ],
            "rare": [
                {"name": "Clóca Fionnachta", "name_en": "Feather Cloak", "type": "legendary_armor", "effect": "Transform to swan"},
            ],
            "epic": [
                {"name": "Dyrnwyn", "name_en": "White Hilt", "type": "weapon", "effect": "Fire damage, +40 strength"},
            ],
        },
        "hard": {
            "uncommon": [
                {"name": "Deoch na hÓige", "name_en": "Drink of Youth", "type": "consumable", "effect": "2x XP for 1 hour"},
            ],
            "rare": [
                {"name": "Leabhar Feasa", "name_en": "Book of Knowledge", "type": "learning", "effect": "10 bonus lessons"},
            ],
            "epic": [
                {"name": "Gáe Bulg", "name_en": "Belly Spear", "type": "weapon", "effect": "+75 strength, barbed"},
            ],
            "legendary": [
                {"name": "Claíomh Solais", "name_en": "Sword of Light", "type": "weapon", "effect": "+50 all stats, glows"},
            ],
        },
        "legendary": {
            "epic": [
                {"name": "Coire Dagdae", "name_en": "Dagda's Cauldron", "type": "artifact", "effect": "Infinite food"},
                {"name": "Lia Fáil", "name_en": "Stone of Destiny", "type": "artifact", "effect": "Reveals true kings"},
            ],
            "legendary": [
                {"name": "Claiomh Solais", "name_en": "Sword of Light", "type": "artifact", "effect": "Nuada's blade"},
                {"name": "Sleá Lúgh", "name_en": "Spear of Lugh", "type": "artifact", "effect": "Never misses"},
                {"name": "Coire Goibhniu", "name_en": "Cauldron of Goibhniu", "type": "artifact", "effect": "Heals all wounds"},
            ],
        },
    }

    print("=== Celtic Loot Tables ===\n")
    for difficulty, rarities in loot_tables.items():
        print(f"{difficulty.upper()}:")
        for rarity, items in rarities.items():
            print(f"  {rarity}: {len(items)} items")
    return difficulty, items, loot_tables, rarities


@app.cell
def _():
    import random as py_random

    # Rarity weights (must sum to 1000)
    rarity_weights = {
        "easy": {"common": 600, "uncommon": 300, "rare": 100},
        "medium": {"common": 400, "uncommon": 350, "rare": 200, "epic": 50},
        "hard": {"uncommon": 300, "rare": 400, "epic": 250, "legendary": 50},
        "legendary": {"epic": 500, "legendary": 500},
    }

    def roll_loot(difficulty: str, random_value: int) -> dict:
        """
        Determine loot drop based on difficulty and random value.

        Args:
            difficulty: Quest difficulty level
            random_value: Random number 0-999

        Returns:
            Selected loot item
        """
        weights = rarity_weights[difficulty]
        table = loot_tables[difficulty]

        # Find rarity tier
        cumulative = 0
        selected_rarity = None
        for rarity, weight in weights.items():
            cumulative += weight
            if random_value < cumulative:
                selected_rarity = rarity
                break

        # Select random item from tier
        items = table[selected_rarity]
        item_index = (random_value // 100) % len(items)

        return {
            "item": items[item_index],
            "rarity": selected_rarity,
            "roll": random_value,
        }

    # Simulate loot drops
    print("=== Loot Drop Simulation ===\n")

    for diff in ["easy", "medium", "hard", "legendary"]:
        print(f"\n{diff.upper()} QUEST (10 drops):")
        for _ in range(10):
            roll = py_random.randint(0, 999)
            loot = roll_loot(diff, roll)
            print(f"  [{loot['rarity']:10}] {loot['item']['name']} ({loot['item']['name_en']})")
    return diff, loot, loot_tables, py_random, rarity_weights, roll, roll_loot


@app.cell
def _(mo):
    mo.md(
        """
        ## 2. Commit-Reveal Implementation

        ### Smart Contract Integration:

        ```solidity
        // QuestRNG.sol - Core quest mechanics
        contract QuestRNG {
            function commitQuest(
                bytes32 commitHash,
                Difficulty difficulty
            ) external returns (uint256 questId);

            function revealQuest(
                uint256 questId,
                bytes32 playerSeed
            ) external;
        }
        ```

        ### Client-Side Flow:

        ```typescript
        // Frontend quest initiation
        async function startQuest(difficulty: Difficulty) {
          // 1. Generate random seed locally
          const seed = crypto.getRandomValues(new Uint8Array(32));
          const seedHex = bytesToHex(seed);

          // 2. Create commit hash
          const commitHash = keccak256(seedHex);

          // 3. Store seed securely (for reveal)
          localStorage.setItem('questSeed', seedHex);

          // 4. Submit commit to blockchain
          const tx = await questContract.commitQuest(commitHash, difficulty);
          await tx.wait();

          // 5. Wait for next block(s)...
          // 6. Reveal when ready
        }
        ```
        """
    )
    return


@app.cell
def _():
    import hashlib
    import secrets
    import time

    class QuestSimulator:
        """Simulate the commit-reveal quest system."""

        def __init__(self):
            self.quests = {}
            self.current_block = 1000

        def commit_quest(self, player: str, difficulty: str) -> dict:
            """Start a quest by committing a seed."""
            # Generate seed
            seed = secrets.token_hex(32)
            commit_hash = hashlib.sha256(seed.encode()).hexdigest()

            quest_id = len(self.quests)
            self.quests[quest_id] = {
                "player": player,
                "difficulty": difficulty,
                "seed": seed,
                "commit_hash": commit_hash,
                "commit_block": self.current_block,
                "state": "committed",
            }

            return {
                "quest_id": quest_id,
                "commit_hash": commit_hash[:16] + "...",
                "message": "Quest committed! Wait for next block to reveal.",
            }

        def advance_blocks(self, n: int = 2):
            """Simulate block progression."""
            self.current_block += n

        def reveal_quest(self, quest_id: int, player_seed: str) -> dict:
            """Reveal seed and determine outcome."""
            quest = self.quests.get(quest_id)
            if not quest:
                return {"error": "Quest not found"}

            if quest["state"] != "committed":
                return {"error": "Quest already revealed or expired"}

            # Verify seed matches commit
            verify_hash = hashlib.sha256(player_seed.encode()).hexdigest()
            if verify_hash != quest["commit_hash"]:
                return {"error": "Invalid seed - doesn't match commit"}

            # Check block timing
            blocks_passed = self.current_block - quest["commit_block"]
            if blocks_passed < 2:
                return {"error": "Too early - wait for more blocks"}
            if blocks_passed > 256:
                return {"error": "Quest expired - block hash unavailable"}

            # Generate "block hash" (simulated)
            block_seed = secrets.token_hex(32)

            # Combine for final random
            combined = player_seed + block_seed
            final_hash = hashlib.sha256(combined.encode()).hexdigest()
            random_value = int(final_hash[:8], 16) % 1000

            # Calculate reward
            difficulty_mult = {"easy": 1, "medium": 2, "hard": 5, "legendary": 10}
            base_reward = 10 + (random_value % 90)
            reward = base_reward * difficulty_mult[quest["difficulty"]]

            # Roll loot
            loot = roll_loot(quest["difficulty"], random_value)

            # Update quest state
            quest["state"] = "completed"
            quest["random_value"] = random_value
            quest["reward"] = reward
            quest["loot"] = loot

            return {
                "quest_id": quest_id,
                "random_value": random_value,
                "reward": f"{reward} CELTIC",
                "loot": loot["item"]["name"],
                "loot_en": loot["item"]["name_en"],
                "rarity": loot["rarity"],
            }

    # Demo the quest system
    print("=== Quest System Demo ===\n")

    sim = QuestSimulator()

    # Player commits a quest
    commit_result = sim.commit_quest("player1", "hard")
    print(f"1. COMMIT: {commit_result}")

    # Wait for blocks
    print("\n2. Waiting for blocks...")
    sim.advance_blocks(3)

    # Reveal with correct seed
    seed = sim.quests[0]["seed"]  # In real system, player stores this
    reveal_result = sim.reveal_quest(0, seed)
    print(f"\n3. REVEAL: {reveal_result}")
    return QuestSimulator, commit_result, hashlib, reveal_result, secrets, seed, sim, time


@app.cell
def _(mo):
    mo.md(
        """
        ## 3. SpacetimeDB Integration

        ### Real-Time Inventory Updates:

        ```rust
        // SpacetimeDB schema for quest system

        #[spacetimedb::table(public)]
        pub struct ActiveQuest {
            #[primary_key]
            quest_id: u64,
            #[index(btree)]
            player_id: Identity,
            difficulty: Difficulty,
            commit_hash: String,
            commit_block: u64,
            state: QuestState,
            created_at: Timestamp,
        }

        #[spacetimedb::table(public)]
        pub struct QuestResult {
            #[primary_key]
            #[auto_inc]
            id: u64,
            quest_id: u64,
            player_id: Identity,
            random_value: u32,
            reward_amount: u64,
            loot_item_id: Option<u32>,
            loot_rarity: Option<Rarity>,
            completed_at: Timestamp,
            tx_hash: String,
        }

        #[spacetimedb::reducer]
        pub fn sync_quest_result(
            ctx: &ReducerContext,
            quest_id: u64,
            random_value: u32,
            reward: u64,
            loot_item_id: Option<u32>,
            tx_hash: String,
        ) -> Result<(), String> {
            // Verify tx_hash on-chain
            // Update player inventory
            // Broadcast to connected clients
            Ok(())
        }
        ```

        ### Real-Time Client Updates:

        ```typescript
        // React hook for quest updates
        function useQuestUpdates(playerId: string) {
          const [quests, setQuests] = useState<Quest[]>([]);

          useEffect(() => {
            // Subscribe to SpacetimeDB updates
            const sub = SpacetimeDB.subscribe(
              'ActiveQuest',
              { player_id: playerId }
            );

            sub.on('insert', (quest) => setQuests(prev => [...prev, quest]));
            sub.on('update', (quest) => {
              setQuests(prev => prev.map(q =>
                q.quest_id === quest.quest_id ? quest : q
              ));
            });

            return () => sub.unsubscribe();
          }, [playerId]);

          return quests;
        }
        ```
        """
    )
    return


@app.cell
def _(mo):
    mo.md(
        """
        ## 4. WGPU Visual Effects

        ### Dice Animation System:

        For the quest reveal animation, we use WGPU particle systems:

        ```rust
        // wgpu/particle-system for quest dice

        pub struct DiceParticleSystem {
            particles: Vec<Particle>,
            dice_mesh: Mesh,
            result_glow: GlowEffect,
        }

        impl DiceParticleSystem {
            pub fn roll_animation(&mut self, result: u32, rarity: Rarity) {
                // Start dice tumbling
                self.dice_mesh.apply_physics(Physics::Dice);

                // Add Celtic swirl particles
                for _ in 0..100 {
                    self.particles.push(Particle::celtic_swirl());
                }

                // Set glow color based on rarity
                self.result_glow.color = match rarity {
                    Rarity::Common => Color::WHITE,
                    Rarity::Uncommon => Color::GREEN,
                    Rarity::Rare => Color::BLUE,
                    Rarity::Epic => Color::PURPLE,
                    Rarity::Legendary => Color::GOLD,
                };
            }

            pub fn render(&self, encoder: &mut wgpu::CommandEncoder) {
                // Render dice mesh
                // Render particles
                // Apply post-processing glow
            }
        }
        ```

        ### Visual Feedback by Rarity:

        | Rarity | Color | Effects |
        |--------|-------|---------|
        | Common | White | Simple glow |
        | Uncommon | Green | Leaf particles |
        | Rare | Blue | Water ripples |
        | Epic | Purple | Magic spirals |
        | Legendary | Gold | Celtic knot explosion |
        """
    )
    return


@app.cell
def _(mo):
    mo.md(
        """
        ## 5. Solana VRF Integration

        For high-stakes quests (tournaments, rare drops), we use Switchboard VRF:

        ```rust
        // Anchor program for VRF quests

        use anchor_lang::prelude::*;
        use switchboard_solana::prelude::*;

        #[program]
        pub mod quest_vrf {
            use super::*;

            pub fn request_vrf_quest(
                ctx: Context<RequestQuest>,
                difficulty: Difficulty,
            ) -> Result<()> {
                // Request VRF from Switchboard
                let vrf_request = VrfRequestRandomness {
                    vrf: ctx.accounts.vrf.to_account_info(),
                    oracle_queue: ctx.accounts.oracle_queue.to_account_info(),
                    queue_authority: ctx.accounts.queue_authority.to_account_info(),
                    data_buffer: ctx.accounts.data_buffer.to_account_info(),
                    permission: ctx.accounts.permission.to_account_info(),
                    escrow: ctx.accounts.escrow.to_account_info(),
                    payer_wallet: ctx.accounts.payer_wallet.to_account_info(),
                    payer_authority: ctx.accounts.payer.to_account_info(),
                    recent_blockhashes: ctx.accounts.recent_blockhashes.to_account_info(),
                    program_state: ctx.accounts.program_state.to_account_info(),
                    token_program: ctx.accounts.token_program.to_account_info(),
                };

                vrf_request.invoke_signed(&[&[/* seeds */]])?;

                // Store pending quest
                let quest = &mut ctx.accounts.quest;
                quest.player = ctx.accounts.player.key();
                quest.difficulty = difficulty;
                quest.state = QuestState::Pending;

                Ok(())
            }

            // Called by Switchboard when VRF is ready
            pub fn consume_vrf_result(
                ctx: Context<ConsumeVrf>,
            ) -> Result<()> {
                let vrf = ctx.accounts.vrf.load()?;

                // VRF result is cryptographically verified
                let result = vrf.get_result()?;
                let random_value = result[0..4].try_into().map(u32::from_le_bytes)?;

                // Calculate rewards and loot
                let quest = &mut ctx.accounts.quest;
                quest.random_value = random_value;
                quest.state = QuestState::Completed;

                // Emit event for SpacetimeDB sync
                emit!(QuestCompleted {
                    quest_id: quest.id,
                    player: quest.player,
                    random_value,
                });

                Ok(())
            }
        }
        ```

        ### VRF vs Commit-Reveal Trade-offs:

        | Aspect | Commit-Reveal | VRF |
        |--------|---------------|-----|
        | Cost | Gas only | ~0.002 SOL |
        | Speed | 2+ blocks | ~1 slot |
        | Trust | Self-sovereign | Oracle network |
        | Best for | Regular quests | Tournaments |
        """
    )
    return


@app.cell
def _(mo):
    mo.md(
        """
        ## 6. Anti-Cheat Measures

        ### Preventing Quest Manipulation:

        ```python
        # Server-side validation before accepting quest results

        def validate_quest_result(
            quest_id: int,
            player: str,
            claimed_result: int,
            tx_hash: str
        ) -> bool:
            '''
            Validate a quest result before syncing to SpacetimeDB.
            '''
            # 1. Verify transaction on-chain
            tx = fetch_transaction(tx_hash)
            if not tx or tx.status != 'success':
                return False

            # 2. Verify correct contract was called
            if tx.to != QUEST_CONTRACT_ADDRESS:
                return False

            # 3. Verify player was the sender
            if tx.from_ != player:
                return False

            # 4. Verify result matches emitted event
            events = parse_events(tx)
            quest_revealed = find_event(events, 'QuestRevealed')
            if quest_revealed.random_value != claimed_result:
                return False

            # 5. Check timing constraints
            commit_block = get_quest_commit_block(quest_id)
            reveal_block = tx.block_number
            if reveal_block - commit_block < 2:
                return False  # Too fast

            return True
        ```

        ### Rate Limiting:

        ```rust
        // Prevent quest spam
        #[spacetimedb::table(public)]
        pub struct PlayerQuestCooldown {
            #[primary_key]
            player_id: Identity,
            last_quest_time: Timestamp,
            quests_today: u32,
        }

        const MAX_QUESTS_PER_DAY: u32 = 50;
        const MIN_QUEST_INTERVAL: Duration = Duration::from_secs(60);
        ```
        """
    )
    return


@app.cell
def _(mo):
    mo.md(
        """
        ## 7. Testing the Quest System

        ### Local Testing:

        ```bash
        # Start Anvil for local Ethereum testing
        anvil --fork-url $BASE_SEPOLIA_RPC

        # Deploy QuestRNG contract
        forge script script/DeployQuestRNG.s.sol --rpc-url anvil --broadcast

        # Run Foundry tests
        forge test --match-contract QuestRNGTest -vvv

        # Test commit-reveal flow manually
        cast send $QUEST_ADDRESS "commitQuest(bytes32,uint8)" \\
            $(cast keccak "my-secret-seed") \\
            2  # Hard difficulty

        # Wait for blocks...
        sleep 15

        # Reveal
        cast send $QUEST_ADDRESS "revealQuest(uint256,bytes32)" \\
            0 \\
            $(cast --from-utf8 "my-secret-seed")
        ```

        ### Integration Testing:

        ```python
        # Python integration test
        async def test_quest_flow():
            # 1. Commit quest
            seed = os.urandom(32)
            commit_hash = keccak256(seed)
            tx = await quest_contract.commit_quest(commit_hash, Difficulty.MEDIUM)

            # 2. Wait for blocks
            await wait_for_blocks(3)

            # 3. Reveal
            tx = await quest_contract.reveal_quest(quest_id, seed)
            receipt = await tx.wait()

            # 4. Verify event
            event = find_event(receipt, 'QuestRevealed')
            assert event.player == player_address
            assert event.lootRarity in [0, 1, 2, 3, 4]

            # 5. Sync to SpacetimeDB
            await spacetimedb.call('sync_quest_result', {
                'quest_id': quest_id,
                'random_value': event.randomResult,
                'tx_hash': tx.hash,
            })
        ```
        """
    )
    return


@app.cell
def _(mo):
    mo.md(
        """
        ## 8. Next Steps

        ### For SpeedRunEthereum:
        1. Deploy QuestRNG.sol to testnet
        2. Complete full commit-reveal cycle
        3. Test edge cases (expiry, invalid seed)
        4. Submit for verification

        ### For Tuath Integration:
        1. Connect to SpacetimeDB for inventory sync
        2. Implement WGPU dice animations
        3. Add Switchboard VRF for Solana
        4. Build React quest UI component
        5. Add Celtic particle effects

        ### Related Notebooks:
        - `00_celtic_nft.py` - NFT for loot items
        - `01_language_staking.py` - XP staking affects quest rewards
        - `02_token_shop.py` - Buy quest boosters
        - `04_item_exchange.py` - Trade loot drops
        """
    )
    return


if __name__ == "__main__":
    app.run()
