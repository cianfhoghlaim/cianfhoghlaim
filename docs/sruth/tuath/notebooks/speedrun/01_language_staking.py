"""
Challenge 1: Decentralized Staking - Tuath Learn-to-Earn Implementation

SpeedRunEthereum Challenge: https://speedrunethereum.com/challenge/staking

Learning Objectives:
- Implement time-based staking rewards
- Create learn-to-earn incentive mechanisms
- Design XP multipliers for long-term stakers
- Integrate with SpacetimeDB for progress tracking

Project Integration:
- CELTIC token staking for language learning
- Lesson completion verification
- Streak-based reward multipliers
- Integration with NCCA Irish curriculum milestones
"""

import marimo

__generated_with = "0.10.14"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo

    mo.md(
        """
        # Challenge 1: Learn-to-Earn Language Staking

        ## Tuath Celtic Educational MMO Integration

        This notebook implements the Learn-to-Earn staking system for the tuath
        Celtic educational MMO, where players stake CELTIC tokens to earn
        rewards by completing Irish language lessons.

        ### The Core Idea:
        > **"Stake to Learn, Learn to Earn"**
        >
        > Players stake CELTIC tokens and earn enhanced rewards by:
        > 1. Completing daily Irish lessons
        > 2. Maintaining learning streaks
        > 3. Achieving language milestones (A1, A2, B1, etc.)
        """
    )
    return (mo,)


@app.cell
def _(mo):
    mo.md(
        """
        ## 1. Learn-to-Earn Game Design

        ### Traditional Staking vs Learn-to-Earn

        | Aspect | Traditional | Learn-to-Earn |
        |--------|-------------|---------------|
        | Rewards | Time-based only | Time + Activity |
        | Engagement | Passive | Active learning |
        | Retention | Low | High (habit forming) |
        | Value | Speculative | Educational |

        ### Tuath Staking Mechanics

        ```
        ┌────────────────────────────────────────────────────┐
        │                TUATH STAKING FLOW                  │
        ├────────────────────────────────────────────────────┤
        │                                                    │
        │   1. STAKE CELTIC ──► Base APY (5%)               │
        │         │                                          │
        │         ▼                                          │
        │   2. COMPLETE LESSONS ──► Streak Bonus (+1%/day)  │
        │         │                                          │
        │         ▼                                          │
        │   3. ACHIEVE MILESTONES ──► Level Multiplier      │
        │         │         (Beginner: 1x, Fluent: 5x)      │
        │         ▼                                          │
        │   4. MAINTAIN STREAK ──► Loyalty Bonus (+2%/mo)   │
        │                                                    │
        └────────────────────────────────────────────────────┘
        ```
        """
    )
    return


@app.cell
def _(mo):
    mo.md(
        """
        ## 2. The LanguageStaking Contract

        Our `LanguageStaking.sol` contract extends traditional staking with
        learning verification:

        ```solidity
        // Core staking data structure
        struct Staker {
            uint256 balance;           // Amount staked
            uint256 stakedAt;          // When they first staked
            uint256 lastClaimAt;       // Last reward claim
            uint256 rewardDebt;        // Pending unclaimed rewards
            LearningLevel level;       // Current learning level
            Language language;         // Language being learned
            uint256 lessonsCompleted;  // Total lessons completed
            uint256 streakDays;        // Current learning streak
            bool isActive;             // Has active stake
        }

        // Learning levels (CEFR-inspired)
        enum LearningLevel {
            Beginner,      // Just started
            Elementary,    // A1 level
            Intermediate,  // A2-B1 level
            Advanced,      // B2 level
            Fluent         // C1+ level
        }

        // Supported Celtic languages
        enum Language {
            Irish,          // Gaeilge
            Welsh,          // Cymraeg
            ScottishGaelic, // Gàidhlig
            Manx,           // Gaelg
            Cornish,        // Kernewek
            Breton          // Brezhoneg
        }
        ```
        """
    )
    return


@app.cell
def _():
    # Simulate staking rewards calculation
    from dataclasses import dataclass
    from enum import IntEnum
    from typing import Optional

    class LearningLevel(IntEnum):
        BEGINNER = 0
        ELEMENTARY = 1
        INTERMEDIATE = 2
        ADVANCED = 3
        FLUENT = 4

    class Language(IntEnum):
        IRISH = 0
        WELSH = 1
        SCOTTISH_GAELIC = 2
        MANX = 3
        CORNISH = 4
        BRETON = 5

    @dataclass
    class Staker:
        balance: float
        staked_at: int  # timestamp
        last_claim_at: int
        reward_debt: float
        level: LearningLevel
        language: Language
        lessons_completed: int
        streak_days: int
        is_active: bool

    # Level multipliers (matching contract)
    LEVEL_MULTIPLIERS = {
        LearningLevel.BEGINNER: 1.0,
        LearningLevel.ELEMENTARY: 1.5,
        LearningLevel.INTERMEDIATE: 2.0,
        LearningLevel.ADVANCED: 3.0,
        LearningLevel.FLUENT: 5.0,
    }

    BASE_APY = 0.05  # 5%
    LOYALTY_BONUS_PER_MONTH = 0.02  # 2% per month
    MAX_LOYALTY_BONUS = 0.12  # 12% cap (6 months)
    MAX_STREAK_BONUS = 0.30  # 30% cap (30 days)

    print("Learn-to-Earn Staking Parameters")
    print("=" * 40)
    print(f"Base APY: {BASE_APY * 100}%")
    print(f"Loyalty Bonus: +{LOYALTY_BONUS_PER_MONTH * 100}% per month")
    print(f"Max Streak Bonus: +{MAX_STREAK_BONUS * 100}%")
    print("\nLevel Multipliers:")
    for level, mult in LEVEL_MULTIPLIERS.items():
        print(f"  {level.name}: {mult}x")
    return (
        BASE_APY,
        LEVEL_MULTIPLIERS,
        LOYALTY_BONUS_PER_MONTH,
        Language,
        LearningLevel,
        MAX_LOYALTY_BONUS,
        MAX_STREAK_BONUS,
        Optional,
        Staker,
        dataclass,
    )


@app.cell
def _(
    BASE_APY,
    LEVEL_MULTIPLIERS,
    LOYALTY_BONUS_PER_MONTH,
    LearningLevel,
    MAX_LOYALTY_BONUS,
    MAX_STREAK_BONUS,
):
    def calculate_effective_apy(
        level: LearningLevel, months_staked: int, streak_days: int
    ) -> float:
        """
        Calculate effective APY including all bonuses.

        Formula:
        Effective APY = (Base APY + Loyalty Bonus) * Level Multiplier * Streak Bonus
        """
        # Base APY
        apy = BASE_APY

        # Add loyalty bonus (capped)
        loyalty = min(months_staked * LOYALTY_BONUS_PER_MONTH, MAX_LOYALTY_BONUS)
        apy += loyalty

        # Apply level multiplier
        apy *= LEVEL_MULTIPLIERS[level]

        # Apply streak bonus (1% per day, max 30%)
        streak_bonus = min(streak_days * 0.01, MAX_STREAK_BONUS)
        apy *= 1 + streak_bonus

        return apy

    def calculate_rewards(
        stake_amount: float,
        level: LearningLevel,
        months_staked: int,
        streak_days: int,
        days_since_claim: int,
    ) -> dict:
        """Calculate pending rewards for a staker."""
        effective_apy = calculate_effective_apy(level, months_staked, streak_days)

        # Daily reward rate
        daily_rate = effective_apy / 365

        # Pending rewards
        pending = stake_amount * daily_rate * days_since_claim

        return {
            "stake_amount": stake_amount,
            "effective_apy": effective_apy,
            "daily_rate": daily_rate,
            "days_since_claim": days_since_claim,
            "pending_rewards": pending,
        }

    # Example: Beginner with no streak
    beginner = calculate_rewards(
        stake_amount=1000,
        level=LearningLevel.BEGINNER,
        months_staked=1,
        streak_days=0,
        days_since_claim=30,
    )

    # Example: Intermediate with 7-day streak
    intermediate = calculate_rewards(
        stake_amount=1000,
        level=LearningLevel.INTERMEDIATE,
        months_staked=3,
        streak_days=7,
        days_since_claim=30,
    )

    # Example: Fluent with max streak
    fluent = calculate_rewards(
        stake_amount=1000,
        level=LearningLevel.FLUENT,
        months_staked=6,
        streak_days=30,
        days_since_claim=30,
    )

    print("Reward Comparison (1000 CELTIC staked, 30 days)")
    print("=" * 50)
    print(f"{'Level':<15} {'APY':>10} {'Monthly Rewards':>20}")
    print("-" * 50)
    print(
        f"{'Beginner':<15} {beginner['effective_apy'] * 100:>9.1f}% {beginner['pending_rewards']:>19.2f}"
    )
    print(
        f"{'Intermediate':<15} {intermediate['effective_apy'] * 100:>9.1f}% {intermediate['pending_rewards']:>19.2f}"
    )
    print(
        f"{'Fluent':<15} {fluent['effective_apy'] * 100:>9.1f}% {fluent['pending_rewards']:>19.2f}"
    )
    return (
        beginner,
        calculate_effective_apy,
        calculate_rewards,
        fluent,
        intermediate,
    )


@app.cell
def _(mo):
    mo.md(
        """
        ## 3. SpacetimeDB Integration

        The tuath game uses SpacetimeDB for real-time state management.
        We sync learning progress to SpacetimeDB for the game client:

        ```rust
        // SpacetimeDB table for staking state
        #[spacetimedb::table(name = staking_state)]
        pub struct StakingState {
            #[primary_key]
            pub player_id: Identity,
            pub wallet_address: String,
            pub staked_amount: u64,
            pub learning_level: LearningLevel,
            pub language: Language,
            pub lessons_completed: u32,
            pub streak_days: u16,
            pub last_lesson_at: Timestamp,
            pub pending_rewards: u64,
        }

        // Reducer: Sync staking state from blockchain
        #[spacetimedb::reducer]
        pub fn sync_staking_state(
            ctx: &ReducerContext,
            wallet_address: String,
            staked_amount: u64,
            level: u8,
            streak_days: u16,
        ) -> Result<(), String> {
            let player_id = ctx.sender;

            // Update or insert staking state
            if let Some(mut state) = StakingState::filter_by_player_id(&player_id).first() {
                state.staked_amount = staked_amount;
                state.learning_level = LearningLevel::from(level);
                state.streak_days = streak_days;
                StakingState::update_by_player_id(&player_id, state);
            } else {
                StakingState::insert(StakingState {
                    player_id,
                    wallet_address,
                    staked_amount,
                    learning_level: LearningLevel::Beginner,
                    language: Language::Irish,
                    lessons_completed: 0,
                    streak_days,
                    last_lesson_at: ctx.timestamp,
                    pending_rewards: 0,
                })?;
            }

            Ok(())
        }
        ```
        """
    )
    return


@app.cell
def _(mo):
    mo.md(
        """
        ## 4. Lesson Verification Flow

        ```
        ┌─────────────────────────────────────────────────────────────┐
        │                  LESSON VERIFICATION FLOW                   │
        └─────────────────────────────────────────────────────────────┘

        ┌──────────┐    ┌──────────────┐    ┌───────────────┐
        │  Player  │───►│ Tuath Client │───►│  SpacetimeDB  │
        │ completes│    │  records     │    │  stores       │
        │  lesson  │    │  completion  │    │  progress     │
        └──────────┘    └──────────────┘    └───────────────┘
                                                    │
                                                    ▼
                        ┌──────────────┐    ┌───────────────┐
                        │   Relayer    │◄───│   Verifier    │
                        │   submits    │    │   validates   │
                        │   to chain   │    │   milestone   │
                        └──────────────┘    └───────────────┘
                                │
                                ▼
                        ┌──────────────────────────────────┐
                        │     LanguageStaking Contract     │
                        │  - recordLesson(learner, id)     │
                        │  - verifyMilestone(learner, lvl) │
                        │  - Update streak, rewards        │
                        └──────────────────────────────────┘
        ```

        ### Verifier Role

        Trusted verifiers (approved by the contract owner) can:
        1. Record completed lessons
        2. Verify milestone achievements
        3. Maintain learning streaks

        This prevents gaming the system while keeping lesson completion
        verification off-chain for gas efficiency.
        """
    )
    return


@app.cell
def _(mo):
    mo.md(
        """
        ## 5. Irish Curriculum Milestones

        ### NCCA Curriculum Integration

        The tuath game aligns with the Irish National Council for Curriculum
        and Assessment (NCCA) learning outcomes:

        | Level | CEFR | Irish Name | Curriculum Alignment |
        |-------|------|------------|---------------------|
        | Beginner | Pre-A1 | Tosaitheoir | Junior Cycle L1 |
        | Elementary | A1 | Bunrang | Junior Cycle L2 |
        | Intermediate | A2-B1 | Meánrang | Leaving Cert OL |
        | Advanced | B2 | Ardrang | Leaving Cert HL |
        | Fluent | C1+ | Líofa | Gaeltacht immersion |

        ### Milestone Achievements

        When players reach a new level, they earn:

        1. **One-time bonus** - 1% of staked amount per level
        2. **Permanent multiplier increase** - See level multipliers
        3. **Achievement NFT** - Celtic Creature for the level
        4. **In-game perks** - Access to new quests, areas, items
        """
    )
    return


@app.cell
def _():
    # Milestone bonus calculation
    def calculate_milestone_bonus(stake_amount: float, new_level: int) -> float:
        """
        Calculate bonus for achieving a new level.
        Bonus: 1% of staked amount per level achieved
        """
        return stake_amount * new_level * 0.01

    # Example milestones
    stake = 1000  # CELTIC tokens

    print("Milestone Bonuses (1000 CELTIC staked)")
    print("=" * 40)
    for level in range(1, 5):
        level_names = ["", "Elementary", "Intermediate", "Advanced", "Fluent"]
        bonus = calculate_milestone_bonus(stake, level)
        print(f"{level_names[level]:<15} +{bonus:.2f} CELTIC")
    return calculate_milestone_bonus, level, level_names, stake


@app.cell
def _(mo):
    mo.md(
        """
        ## 6. Solana Program Extension

        ### Extending celtic-token Program

        For the Solana implementation, we extend the existing `celtic-token`
        program with staking functionality:

        ```rust
        // programs/celtic-token/src/staking.rs

        #[account]
        #[derive(InitSpace)]
        pub struct StakeAccount {
            pub owner: Pubkey,
            pub amount: u64,
            pub staked_at: i64,
            pub last_claim_at: i64,
            pub learning_level: u8,
            pub language: u8,
            pub lessons_completed: u32,
            pub streak_days: u16,
            pub pending_rewards: u64,
            pub bump: u8,
        }

        pub fn stake(ctx: Context<Stake>, amount: u64, language: u8) -> Result<()> {
            let stake_account = &mut ctx.accounts.stake_account;
            let clock = Clock::get()?;

            // Transfer tokens to stake vault
            token::transfer(
                ctx.accounts.transfer_context(),
                amount,
            )?;

            stake_account.owner = ctx.accounts.owner.key();
            stake_account.amount = stake_account.amount.checked_add(amount)
                .ok_or(StakingError::Overflow)?;
            stake_account.staked_at = clock.unix_timestamp;
            stake_account.last_claim_at = clock.unix_timestamp;
            stake_account.language = language;

            emit!(Staked {
                owner: ctx.accounts.owner.key(),
                amount,
                language,
                timestamp: clock.unix_timestamp,
            });

            Ok(())
        }
        ```

        ### Token-2022 Transfer Hooks

        We use Token-2022 transfer hooks to verify learning milestones:

        ```rust
        // Transfer hook: verify learner status before reward transfer
        pub fn transfer_hook(ctx: Context<TransferHook>) -> Result<()> {
            // Check if recipient has active stake
            let stake_account = &ctx.accounts.stake_account;
            require!(stake_account.amount > 0, StakingError::NoActiveStake);

            // Verify milestone if this is a milestone reward
            if ctx.accounts.is_milestone_reward {
                require!(
                    stake_account.learning_level > ctx.accounts.required_level,
                    StakingError::LevelNotAchieved
                );
            }

            Ok(())
        }
        ```
        """
    )
    return


@app.cell
def _(mo):
    mo.md(
        """
        ## 7. Frontend Integration

        ### Staking UI Components

        For the tuath game client (TanStack Start + Cloudflare):

        ```tsx
        // components/StakingPanel.tsx
        import { useStaking } from '@/hooks/useStaking'
        import { useLearningProgress } from '@/hooks/useLearningProgress'

        export function StakingPanel() {
          const { stake, unstake, claimRewards, stakerInfo } = useStaking()
          const { level, streakDays, lessonsCompleted } = useLearningProgress()

          const effectiveAPY = calculateEffectiveAPY(level, streakDays)

          return (
            <div className="staking-panel">
              <h2>Learn-to-Earn Staking</h2>

              <div className="stats-grid">
                <Stat label="Staked" value={`${stakerInfo.balance} CELTIC`} />
                <Stat label="Level" value={levelNames[level]} />
                <Stat label="Streak" value={`${streakDays} days 🔥`} />
                <Stat label="APY" value={`${(effectiveAPY * 100).toFixed(1)}%`} />
              </div>

              <div className="progress-bar">
                <LessonProgress completed={lessonsCompleted} />
              </div>

              <div className="actions">
                <StakeButton onStake={stake} />
                <ClaimButton
                  onClaim={claimRewards}
                  pending={stakerInfo.pendingRewards}
                />
                <UnstakeButton onUnstake={unstake} />
              </div>
            </div>
          )
        }
        ```
        """
    )
    return


@app.cell
def _(mo):
    mo.md(
        """
        ## 8. Testing & Deployment

        ### Foundry Tests

        ```bash
        # Run all staking tests
        cd sruth/shared/blockchain/ethereum
        forge test --match-contract LanguageStakingTest -vvv

        # Specific test scenarios
        forge test --match-test test_StreakMaintained -vvv
        forge test --match-test test_MilestoneIncreaseRewards -vvv
        ```

        ### Deployment Commands

        ```bash
        # Deploy to Base Sepolia
        forge script script/DeployStaking.s.sol \\
            --rpc-url base_sepolia \\
            --broadcast \\
            --verify

        # Set up verifiers
        cast send $STAKING_ADDRESS "setVerifier(address,bool)" \\
            $VERIFIER_ADDRESS true \\
            --rpc-url base_sepolia \\
            --private-key $PRIVATE_KEY
        ```

        ### Anchor Tests (Solana)

        ```bash
        # Build and test
        cd sruth/tuath/crates/solana
        anchor build
        anchor test

        # Deploy to devnet
        anchor deploy --provider.cluster devnet
        ```
        """
    )
    return


@app.cell
def _(mo):
    mo.md(
        """
        ## 9. Next Steps

        ### For SpeedRunEthereum:
        1. ✅ Implement LanguageStaking contract
        2. ✅ Add learning verification system
        3. 🔲 Deploy to Base Sepolia testnet
        4. 🔲 Complete challenge verification
        5. 🔲 Submit for SpeedRunEthereum badge

        ### For Tuath Integration:
        1. 🔲 Extend celtic-token Solana program
        2. 🔲 Implement SpacetimeDB sync
        3. 🔲 Build staking UI components
        4. 🔲 Create lesson verification backend
        5. 🔲 Integrate with NCCA curriculum data

        ### Related Notebooks:
        - `00_celtic_nft.py` - Celtic Creature NFTs (Challenge 0)
        - `02_token_shop.py` - In-game shop (Challenge 2)
        - `03_quest_randomness.py` - Quest RNG (Challenge 3)
        """
    )
    return


if __name__ == "__main__":
    app.run()
