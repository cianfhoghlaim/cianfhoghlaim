"""
Challenge 6: Learning Tokens - tuath Education Economy

SpeedRunEthereum Challenge: https://speedrunethereum.com/challenge/stablecoins

Learning Objectives:
- Education-backed stablecoin mechanics
- Verified learning as minting collateral
- Curriculum milestone verification
- Redemption for courses/certifications

Tuath Integration:
- CelticUSD minted by verified achievements
- NCCA curriculum milestone backing
- Redeemable for educational resources
- SpacetimeDB achievement tracking
"""

import marimo

__generated_with = "0.10.0"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo

    mo.md("""
    # Challenge 6: Education-Backed Learning Tokens

    **SpeedRunEthereum Challenge 6** implements CDP-based stablecoins.

    For **tuath**, we create an **education-backed stablecoin** where:
    - **Learning achievements** serve as "collateral"
    - Completing **verified curriculum** mints tokens
    - Tokens are **redeemable** for courses and certifications
    - **NCCA milestones** provide backing value

    This creates a **learn-to-earn** economy where education has tangible value.
    """)
    return (mo,)


@app.cell
def _():
    """Core types for learning token system."""
    from dataclasses import dataclass, field
    from enum import Enum
    from typing import Optional
    from datetime import datetime
    import uuid

    class SubjectArea(Enum):
        IRISH = "irish"
        MATHEMATICS = "mathematics"
        ENGLISH = "english"
        HISTORY = "history"
        GEOGRAPHY = "geography"
        SCIENCE = "science"
        MUSIC = "music"
        ART = "art"
        CODING = "coding"

    class AchievementLevel(Enum):
        BRONZE = 1  # Basic understanding
        SILVER = 2  # Intermediate mastery
        GOLD = 3  # Advanced proficiency
        PLATINUM = 4  # Expert level

    class CurriculumStage(Enum):
        PRIMARY_JUNIOR = "primary_junior"  # 1st-2nd class
        PRIMARY_SENIOR = "primary_senior"  # 3rd-6th class
        JUNIOR_CYCLE = "junior_cycle"  # 1st-3rd year
        SENIOR_CYCLE = "senior_cycle"  # 5th-6th year
        LEAVING_CERT = "leaving_cert"  # Final exams

    @dataclass
    class LearningAchievement:
        """A verified learning achievement."""

        achievement_id: str
        student: str
        subject: SubjectArea
        topic: str
        topic_irish: str
        level: AchievementLevel
        stage: CurriculumStage
        verified_at: datetime
        verifier: str  # Teacher/system that verified
        token_value: float  # CUSD value of achievement

    @dataclass
    class LearningToken:
        """Education-backed stablecoin."""

        symbol: str = "LEDU"  # Learning EDU
        name: str = "Celtic Learning Token"
        name_irish: str = "Airgeadra Foghlama Ceilteach"
        peg_target: float = 1.0  # 1 LEDU = $1 of educational value
        total_minted: float = 0
        total_achievements: int = 0
        backing_ratio: float = 100  # 100% backed by verified achievements

    @dataclass
    class RedemptionOption:
        """What tokens can be redeemed for."""

        option_id: str
        name: str
        name_irish: str
        category: str  # course, certification, tutoring, materials
        cost_ledu: float
        provider: str
        description: str

    return (
        AchievementLevel,
        CurriculumStage,
        LearningAchievement,
        LearningToken,
        Optional,
        RedemptionOption,
        SubjectArea,
        dataclass,
        datetime,
        field,
        uuid,
    )


@app.cell
def _(mo):
    mo.md("""
    ## Learning Token Economics

    The **Celtic Learning Token (LEDU)** has a unique backing model:

    ### Minting (Earning)
    - Complete verified learning modules
    - Pass assessments with minimum score
    - Earn tokens proportional to difficulty
    - Harder subjects/levels = more tokens

    ### Backing Value
    - Each token represents verified educational work
    - Backed by NCCA curriculum standards
    - Auditable learning records on-chain
    - Cannot be "printed" without learning

    ### Redemption (Spending)
    - Exchange for online courses
    - Pay for tutoring sessions
    - Purchase educational materials
    - Earn certifications
    """)
    return ()


@app.cell
def _(
    AchievementLevel,
    CurriculumStage,
    LearningAchievement,
    SubjectArea,
    datetime,
    uuid,
):
    """Learning token protocol implementation."""

    class LearningTokenProtocol:
        """
        Education-backed stablecoin protocol.

        Key concepts:
        - Achievements as collateral
        - Verified learning = minting rights
        - Redeemable for educational value
        """

        def __init__(self):
            self.achievements = {}
            self.student_balances = {}
            self.total_supply = 0
            self.redemption_options = []

            # Token values by level and stage
            self.level_multipliers = {
                AchievementLevel.BRONZE: 1.0,
                AchievementLevel.SILVER: 2.0,
                AchievementLevel.GOLD: 4.0,
                AchievementLevel.PLATINUM: 8.0,
            }

            self.stage_multipliers = {
                CurriculumStage.PRIMARY_JUNIOR: 0.5,
                CurriculumStage.PRIMARY_SENIOR: 1.0,
                CurriculumStage.JUNIOR_CYCLE: 2.0,
                CurriculumStage.SENIOR_CYCLE: 3.0,
                CurriculumStage.LEAVING_CERT: 5.0,
            }

            # Subject bonuses (Irish language gets bonus)
            self.subject_bonuses = {
                SubjectArea.IRISH: 1.5,  # 50% bonus for Irish
                SubjectArea.MATHEMATICS: 1.2,  # 20% bonus for STEM
                SubjectArea.SCIENCE: 1.2,
                SubjectArea.CODING: 1.3,
            }

            # Base token value for a single achievement
            self.base_token_value = 10.0  # 10 LEDU base

        def calculate_token_value(
            self, level: AchievementLevel, stage: CurriculumStage, subject: SubjectArea
        ) -> float:
            """Calculate LEDU token value for an achievement."""
            value = self.base_token_value
            value *= self.level_multipliers[level]
            value *= self.stage_multipliers[stage]
            value *= self.subject_bonuses.get(subject, 1.0)
            return round(value, 2)

        def verify_and_mint(
            self,
            student: str,
            subject: SubjectArea,
            topic: str,
            topic_irish: str,
            level: AchievementLevel,
            stage: CurriculumStage,
            verifier: str,
        ) -> dict:
            """
            Verify a learning achievement and mint tokens.

            In production, this would:
            1. Verify assessment completion
            2. Check minimum score requirements
            3. Validate verifier credentials
            4. Record on-chain
            """
            # Calculate token value
            token_value = self.calculate_token_value(level, stage, subject)

            # Create achievement record
            achievement = LearningAchievement(
                achievement_id=str(uuid.uuid4())[:8],
                student=student,
                subject=subject,
                topic=topic,
                topic_irish=topic_irish,
                level=level,
                stage=stage,
                verified_at=datetime.now(),
                verifier=verifier,
                token_value=token_value,
            )

            # Store achievement
            self.achievements[achievement.achievement_id] = achievement

            # Mint tokens to student
            self.student_balances[student] = self.student_balances.get(student, 0) + token_value
            self.total_supply += token_value

            return {
                "success": True,
                "achievement_id": achievement.achievement_id,
                "tokens_minted": token_value,
                "new_balance": self.student_balances[student],
                "subject": subject.value,
                "level": level.name,
            }

        def get_student_achievements(self, student: str) -> list:
            """Get all achievements for a student."""
            return [ach for ach in self.achievements.values() if ach.student == student]

        def get_balance(self, student: str) -> float:
            """Get student's LEDU balance."""
            return self.student_balances.get(student, 0)

        def redeem_tokens(self, student: str, amount: float, option_id: str) -> dict:
            """Redeem tokens for educational resources."""
            balance = self.student_balances.get(student, 0)

            if balance < amount:
                return {"success": False, "error": "Insufficient balance"}

            # Find redemption option
            option = next((o for o in self.redemption_options if o.option_id == option_id), None)

            if not option:
                return {"success": False, "error": "Invalid redemption option"}

            if amount < option.cost_ledu:
                return {"success": False, "error": f"Requires {option.cost_ledu} LEDU"}

            # Burn tokens
            self.student_balances[student] -= option.cost_ledu
            self.total_supply -= option.cost_ledu

            return {
                "success": True,
                "redeemed_for": option.name,
                "tokens_spent": option.cost_ledu,
                "remaining_balance": self.student_balances[student],
            }

    # Initialize protocol
    protocol = LearningTokenProtocol()
    print("Learning Token Protocol Initialized")
    return LearningTokenProtocol, protocol


@app.cell
def _(AchievementLevel, CurriculumStage, SubjectArea, protocol):
    """Demo the learning token system."""

    print("Learning Token System Demo")
    print("=" * 60)

    # Show token value table
    print("\nToken Value Matrix (LEDU per achievement):")
    print("-" * 60)
    print(
        f"{'Level':<12} {'Primary Jr':<12} {'Primary Sr':<12} {'Junior Cyc':<12} {'Senior Cyc':<12}"
    )
    print("-" * 60)

    for level in AchievementLevel:
        row = f"{level.name:<12}"
        for stage in [
            CurriculumStage.PRIMARY_JUNIOR,
            CurriculumStage.PRIMARY_SENIOR,
            CurriculumStage.JUNIOR_CYCLE,
            CurriculumStage.SENIOR_CYCLE,
        ]:
            value = protocol.calculate_token_value(level, stage, SubjectArea.ENGLISH)
            row += f"{value:<12.0f}"
        print(row)

    print("\n--- Student Earns Achievements ---")

    # Student completes Irish module
    result1 = protocol.verify_and_mint(
        student="student_001",
        subject=SubjectArea.IRISH,
        topic="Verb Conjugation",
        topic_irish="Réimniú na mBriathra",
        level=AchievementLevel.SILVER,
        stage=CurriculumStage.JUNIOR_CYCLE,
        verifier="teacher_001",
    )
    print(f"1. Irish (Silver, Junior Cycle): +{result1['tokens_minted']} LEDU")

    # Mathematics achievement
    result2 = protocol.verify_and_mint(
        student="student_001",
        subject=SubjectArea.MATHEMATICS,
        topic="Quadratic Equations",
        topic_irish="Cothromóidí Cearnógacha",
        level=AchievementLevel.GOLD,
        stage=CurriculumStage.SENIOR_CYCLE,
        verifier="teacher_002",
    )
    print(f"2. Mathematics (Gold, Senior Cycle): +{result2['tokens_minted']} LEDU")

    # Coding achievement
    result3 = protocol.verify_and_mint(
        student="student_001",
        subject=SubjectArea.CODING,
        topic="Python Basics",
        topic_irish="Bunúsacha Python",
        level=AchievementLevel.BRONZE,
        stage=CurriculumStage.PRIMARY_SENIOR,
        verifier="system",
    )
    print(f"3. Coding (Bronze, Primary Senior): +{result3['tokens_minted']} LEDU")

    balance = protocol.get_balance("student_001")
    print(f"\nTotal Balance: {balance} LEDU")

    # Show achievements
    achievements = protocol.get_student_achievements("student_001")
    print(f"\nAchievements Earned: {len(achievements)}")
    for ach in achievements:
        print(f"  - {ach.topic} ({ach.subject.value}, {ach.level.name})")
    return achievements, balance, result1, result2, result3


@app.cell
def _(mo):
    mo.md("""
    ## Redemption System

    LEDU tokens can be **redeemed** for real educational value:

    | Category | Examples | Typical Cost |
    |----------|----------|--------------|
    | **Courses** | Online lessons, video tutorials | 50-200 LEDU |
    | **Tutoring** | 1-on-1 sessions with teachers | 100-500 LEDU |
    | **Materials** | Textbooks, workbooks, flashcards | 20-100 LEDU |
    | **Certifications** | Skill certificates, badges | 200-1000 LEDU |
    | **Events** | Workshops, camps, competitions | 100-500 LEDU |

    This creates a **circular economy**:
    1. Students learn → earn tokens
    2. Tokens spent on more learning
    3. Providers earn tokens for teaching
    4. System grows with participation
    """)
    return ()


@app.cell
def _(RedemptionOption, protocol, uuid):
    """Redemption options and marketplace."""

    # Add redemption options
    redemption_catalog = [
        RedemptionOption(
            option_id=str(uuid.uuid4())[:8],
            name="Irish Conversation Practice (1 hour)",
            name_irish="Cleachtadh Comhrá Gaeilge (1 uair)",
            category="tutoring",
            cost_ledu=100,
            provider="tuath_tutors",
            description="One-on-one Irish conversation practice with native speaker",
        ),
        RedemptionOption(
            option_id=str(uuid.uuid4())[:8],
            name="Leaving Cert Math Masterclass",
            name_irish="Máistir-rang Mata na hArdteiste",
            category="course",
            cost_ledu=200,
            provider="tuath_academy",
            description="Complete video course covering Leaving Cert mathematics",
        ),
        RedemptionOption(
            option_id=str(uuid.uuid4())[:8],
            name="NCCA Curriculum Workbook",
            name_irish="Leabhar Oibre CNCM",
            category="materials",
            cost_ledu=50,
            provider="tuath_press",
            description="Digital workbook aligned with NCCA curriculum",
        ),
        RedemptionOption(
            option_id=str(uuid.uuid4())[:8],
            name="Irish Language Proficiency Certificate",
            name_irish="Teastas Inniúlachta Gaeilge",
            category="certification",
            cost_ledu=500,
            provider="tuath_certs",
            description="Official certificate of Irish language proficiency",
        ),
        RedemptionOption(
            option_id=str(uuid.uuid4())[:8],
            name="Gaeltacht Summer Camp Discount",
            name_irish="Lascaine Champa Samhraidh Gaeltachta",
            category="events",
            cost_ledu=300,
            provider="gaeltacht_camps",
            description="25% discount voucher for Gaeltacht summer camp",
        ),
    ]

    protocol.redemption_options = redemption_catalog

    print("Redemption Marketplace")
    print("=" * 70)
    print(f"{'Name':<40} {'Category':<15} {'Cost':<10}")
    print("-" * 70)

    for option in redemption_catalog:
        print(f"{option.name[:38]:<40} {option.category:<15} {option.cost_ledu:<10} LEDU")

    # Student redeems tokens
    print("\n--- Student Redemption ---")
    balance_before = protocol.get_balance("student_001")
    print(f"Balance before: {balance_before} LEDU")

    redemption = protocol.redeem_tokens(
        "student_001",
        redemption_catalog[2].cost_ledu,  # Workbook
        redemption_catalog[2].option_id,
    )

    if redemption["success"]:
        print(f"Redeemed: {redemption['redeemed_for']}")
        print(f"Tokens spent: {redemption['tokens_spent']} LEDU")
        print(f"Balance after: {redemption['remaining_balance']} LEDU")
    return balance_before, option, redemption, redemption_catalog


@app.cell
def _(mo):
    mo.md("""
    ## NCCA Curriculum Integration

    Token minting is tied to **NCCA (National Council for Curriculum and Assessment)** standards:

    ### Primary School (Bunscoil)
    - Junior/Senior Infants through 6th Class
    - Subjects: Gaeilge, English, Mathematics, SESE, SPHE, etc.
    - Achievement levels mapped to curriculum outcomes

    ### Post-Primary (Iar-Bhunscoil)
    - Junior Cycle (1st-3rd Year)
    - Senior Cycle (5th-6th Year)
    - Leaving Certificate examinations

    ### Verification Methods
    1. **Teacher Verification** - Classroom assessments
    2. **System Verification** - Online quiz completion
    3. **Exam Results** - State examination scores
    4. **Peer Review** - Community validation (language practice)
    """)
    return ()


@app.cell
def _(AchievementLevel, CurriculumStage, SubjectArea):
    """NCCA curriculum mapping."""

    # NCCA curriculum structure for token system
    CURRICULUM_MAPPING = {
        SubjectArea.IRISH: {
            CurriculumStage.PRIMARY_JUNIOR: {
                "topics": [
                    ("Mé Féin", "Myself", AchievementLevel.BRONZE),
                    ("Mo Chlann", "My Family", AchievementLevel.BRONZE),
                    ("Bia", "Food", AchievementLevel.BRONZE),
                    ("Éadaí", "Clothes", AchievementLevel.SILVER),
                ],
                "outcomes": "Communicating in Irish at basic level",
            },
            CurriculumStage.PRIMARY_SENIOR: {
                "topics": [
                    ("An Aimsir", "Weather", AchievementLevel.BRONZE),
                    ("An Scoil", "School", AchievementLevel.SILVER),
                    ("Caitheamh Aimsire", "Hobbies", AchievementLevel.SILVER),
                    ("Scéalta Traidisiúnta", "Traditional Stories", AchievementLevel.GOLD),
                ],
                "outcomes": "Reading and writing simple Irish texts",
            },
            CurriculumStage.JUNIOR_CYCLE: {
                "topics": [
                    ("Gramadach Bhunúsach", "Basic Grammar", AchievementLevel.SILVER),
                    ("Filíocht", "Poetry", AchievementLevel.SILVER),
                    ("Comhrá", "Conversation", AchievementLevel.GOLD),
                    ("Litríocht", "Literature", AchievementLevel.GOLD),
                ],
                "outcomes": "Intermediate Irish communication and comprehension",
            },
            CurriculumStage.LEAVING_CERT: {
                "topics": [
                    ("Prós Liteartha", "Literary Prose", AchievementLevel.GOLD),
                    ("Díospóireacht", "Debate", AchievementLevel.GOLD),
                    ("Aiste", "Essay Writing", AchievementLevel.PLATINUM),
                    ("Ardleibhéal Teanga", "Higher Level Language", AchievementLevel.PLATINUM),
                ],
                "outcomes": "Advanced Irish fluency and literary analysis",
            },
        },
        SubjectArea.MATHEMATICS: {
            CurriculumStage.JUNIOR_CYCLE: {
                "topics": [
                    ("Uimhríocht", "Arithmetic", AchievementLevel.BRONZE),
                    ("Ailgéabar", "Algebra", AchievementLevel.SILVER),
                    ("Geoiméadracht", "Geometry", AchievementLevel.SILVER),
                    ("Staitisticí", "Statistics", AchievementLevel.GOLD),
                ],
                "outcomes": "Fundamental mathematical reasoning",
            },
            CurriculumStage.LEAVING_CERT: {
                "topics": [
                    ("Calcalas", "Calculus", AchievementLevel.GOLD),
                    ("Triantánacht", "Trigonometry", AchievementLevel.GOLD),
                    ("Dóchúlacht", "Probability", AchievementLevel.PLATINUM),
                    ("Uimhirtheoraic", "Number Theory", AchievementLevel.PLATINUM),
                ],
                "outcomes": "Advanced mathematical problem-solving",
            },
        },
    }

    print("NCCA Curriculum Token Mapping")
    print("=" * 70)

    for subject, stages in CURRICULUM_MAPPING.items():
        print(f"\n{subject.value.upper()}")
        print("-" * 50)
        for stage, data in stages.items():
            print(f"\n  {stage.value}:")
            for topic_irish, topic_en, level in data["topics"]:
                print(f"    [{level.name:<8}] {topic_irish} ({topic_en})")
    return (CURRICULUM_MAPPING,)


@app.cell
def _(mo):
    mo.md("""
    ## SpacetimeDB Integration

    Achievement and token data stored in SpacetimeDB:

    ```rust
    #[spacetimedb::table(public)]
    pub struct LearningAchievement {
        #[primarykey]
        pub achievement_id: String,
        pub student: Identity,
        pub subject: SubjectArea,
        pub topic: String,
        pub topic_irish: String,
        pub level: AchievementLevel,
        pub stage: CurriculumStage,
        pub verified_at: Timestamp,
        pub verifier: Identity,
        pub token_value: u64,
    }

    #[spacetimedb::table(public)]
    pub struct TokenBalance {
        #[primarykey]
        pub student: Identity,
        pub balance: u64,
        pub total_earned: u64,
        pub total_redeemed: u64,
    }

    #[spacetimedb::reducer]
    pub fn verify_achievement(
        ctx: ReducerContext,
        student: Identity,
        subject: SubjectArea,
        topic: String,
        level: AchievementLevel,
    ) -> Result<u64, String>;
    ```
    """)
    return ()


@app.cell
def _():
    """SpacetimeDB schema for learning tokens."""

    STDB_LEARNING_SCHEMA = """
    // SpacetimeDB schema for Celtic Learning Tokens

    use spacetimedb::{Identity, Timestamp};

    #[derive(Debug, Clone, PartialEq)]
    pub enum SubjectArea {
        Irish,
        Mathematics,
        English,
        History,
        Geography,
        Science,
        Music,
        Art,
        Coding,
    }

    #[derive(Debug, Clone, PartialEq)]
    pub enum AchievementLevel {
        Bronze,   // 1x base
        Silver,   // 2x base
        Gold,     // 4x base
        Platinum, // 8x base
    }

    #[derive(Debug, Clone, PartialEq)]
    pub enum CurriculumStage {
        PrimaryJunior,  // 0.5x
        PrimarySenior,  // 1x
        JuniorCycle,    // 2x
        SeniorCycle,    // 3x
        LeavingCert,    // 5x
    }

    #[spacetimedb::table(public)]
    pub struct LearningAchievement {
        #[primarykey]
        pub achievement_id: String,
        pub student: Identity,
        pub subject: SubjectArea,
        pub topic: String,
        pub topic_irish: String,
        pub level: AchievementLevel,
        pub stage: CurriculumStage,
        pub verified_at: Timestamp,
        pub verifier: Identity,
        pub token_value: u64, // In smallest unit (like wei)
    }

    #[spacetimedb::table(public)]
    pub struct TokenBalance {
        #[primarykey]
        pub student: Identity,
        pub balance: u64,
        pub total_earned: u64,
        pub total_redeemed: u64,
        pub achievement_count: u32,
    }

    #[spacetimedb::table(public)]
    pub struct RedemptionRecord {
        #[primarykey]
        pub redemption_id: String,
        pub student: Identity,
        pub option_id: String,
        pub amount: u64,
        pub redeemed_at: Timestamp,
    }

    #[spacetimedb::table(public)]
    pub struct RedemptionOption {
        #[primarykey]
        pub option_id: String,
        pub name: String,
        pub name_irish: String,
        pub category: String,
        pub cost_ledu: u64,
        pub provider: String,
        pub is_active: bool,
    }

    // Reducers
    #[spacetimedb::reducer]
    pub fn verify_achievement(
        ctx: ReducerContext,
        student: Identity,
        subject: SubjectArea,
        topic: String,
        topic_irish: String,
        level: AchievementLevel,
        stage: CurriculumStage,
    ) -> Result<String, String> {
        // Verify caller is authorized verifier
        // Calculate token value
        // Mint tokens to student
        // Create achievement record
        // Return achievement_id
    }

    #[spacetimedb::reducer]
    pub fn redeem_tokens(
        ctx: ReducerContext,
        option_id: String,
    ) -> Result<String, String> {
        // Check student has sufficient balance
        // Burn tokens from balance
        // Create redemption record
        // Trigger fulfillment (off-chain)
    }

    // Subscriptions for real-time updates
    #[spacetimedb::subscription]
    pub fn on_achievement_earned(achievement: &LearningAchievement) {
        // Notify student of new achievement
        // Update leaderboards
    }

    #[spacetimedb::subscription]
    pub fn on_balance_change(balance: &TokenBalance) {
        // Real-time balance updates in UI
    }
    """

    print("SpacetimeDB Learning Token Schema")
    print("=" * 50)
    print("\nTables:")
    print("  - LearningAchievement: Verified learning records")
    print("  - TokenBalance: Student LEDU balances")
    print("  - RedemptionRecord: Token redemption history")
    print("  - RedemptionOption: Available redemption options")
    print("\nReducers:")
    print("  - verify_achievement: Mint tokens for learning")
    print("  - redeem_tokens: Spend tokens on resources")
    print("\nFeatures:")
    print("  - Real-time balance updates")
    print("  - Leaderboard integration")
    print("  - Achievement notifications")
    return (STDB_LEARNING_SCHEMA,)


@app.cell
def _(mo):
    mo.md("""
    ## Solana Integration

    On Solana, LEDU is implemented as an **SPL Token** with:
    - **Token-2022 Extensions** for transfer hooks
    - **Metaplex** for achievement NFT metadata
    - **PDA accounts** for achievement verification

    ```rust
    // Mint LEDU tokens for verified achievement
    pub fn mint_learning_tokens(
        ctx: Context<MintLearning>,
        subject: SubjectArea,
        level: AchievementLevel,
        stage: CurriculumStage,
    ) -> Result<()>
    ```
    """)
    return ()


@app.cell
def _():
    """Anchor program structure for learning tokens."""

    ANCHOR_LEARNING_PROGRAM = """
    use anchor_lang::prelude::*;
    use anchor_spl::token_2022::{self, Token2022, MintTo};

    declare_id!("LEDU...your_program_id");

    #[program]
    pub mod celtic_learning {
        use super::*;

        pub fn initialize_mint(ctx: Context<InitializeMint>) -> Result<()> {
            // Initialize LEDU token mint with metadata
            // Set up transfer hook for tracking
            Ok(())
        }

        pub fn verify_and_mint(
            ctx: Context<VerifyAndMint>,
            subject: SubjectArea,
            topic: String,
            level: AchievementLevel,
            stage: CurriculumStage,
        ) -> Result<()> {
            let verifier = &ctx.accounts.verifier;

            // Verify the verifier is authorized
            require!(
                ctx.accounts.verifier_registry.is_authorized(verifier.key()),
                LearningError::UnauthorizedVerifier
            );

            // Calculate token amount
            let amount = calculate_token_value(level, stage, subject);

            // Create achievement record (PDA)
            let achievement = &mut ctx.accounts.achievement;
            achievement.student = ctx.accounts.student.key();
            achievement.subject = subject;
            achievement.topic = topic;
            achievement.level = level;
            achievement.stage = stage;
            achievement.verified_at = Clock::get()?.unix_timestamp;
            achievement.verifier = verifier.key();
            achievement.token_value = amount;

            // Mint tokens to student
            let cpi_accounts = MintTo {
                mint: ctx.accounts.ledu_mint.to_account_info(),
                to: ctx.accounts.student_token_account.to_account_info(),
                authority: ctx.accounts.mint_authority.to_account_info(),
            };

            let cpi_ctx = CpiContext::new(
                ctx.accounts.token_program.to_account_info(),
                cpi_accounts,
            );

            token_2022::mint_to(cpi_ctx, amount)?;

            emit!(AchievementVerified {
                student: ctx.accounts.student.key(),
                subject,
                level,
                tokens_minted: amount,
            });

            Ok(())
        }

        pub fn redeem_tokens(
            ctx: Context<RedeemTokens>,
            option_id: String,
            amount: u64,
        ) -> Result<()> {
            // Burn tokens from student
            // Record redemption
            // Trigger off-chain fulfillment
            Ok(())
        }
    }

    fn calculate_token_value(
        level: AchievementLevel,
        stage: CurriculumStage,
        subject: SubjectArea,
    ) -> u64 {
        let base: u64 = 10_000_000; // 10 LEDU in smallest unit

        let level_mult = match level {
            AchievementLevel::Bronze => 100,
            AchievementLevel::Silver => 200,
            AchievementLevel::Gold => 400,
            AchievementLevel::Platinum => 800,
        };

        let stage_mult = match stage {
            CurriculumStage::PrimaryJunior => 50,
            CurriculumStage::PrimarySenior => 100,
            CurriculumStage::JuniorCycle => 200,
            CurriculumStage::SeniorCycle => 300,
            CurriculumStage::LeavingCert => 500,
        };

        let subject_mult = match subject {
            SubjectArea::Irish => 150,
            SubjectArea::Mathematics => 120,
            SubjectArea::Coding => 130,
            _ => 100,
        };

        (base * level_mult * stage_mult * subject_mult) / 1_000_000
    }

    #[account]
    pub struct Achievement {
        pub student: Pubkey,
        pub subject: SubjectArea,
        pub topic: String,
        pub level: AchievementLevel,
        pub stage: CurriculumStage,
        pub verified_at: i64,
        pub verifier: Pubkey,
        pub token_value: u64,
    }

    #[event]
    pub struct AchievementVerified {
        pub student: Pubkey,
        pub subject: SubjectArea,
        pub level: AchievementLevel,
        pub tokens_minted: u64,
    }
    """

    print("Anchor Learning Token Program")
    print("=" * 50)
    print("\nInstructions:")
    print("  - initialize_mint: Create LEDU token with metadata")
    print("  - verify_and_mint: Verify achievement & mint tokens")
    print("  - redeem_tokens: Burn tokens for educational resources")
    print("\nFeatures:")
    print("  - Token-2022 for transfer hooks")
    print("  - Achievement PDA for on-chain records")
    print("  - Subject/level/stage multipliers")
    print("  - Irish language bonus (1.5x)")
    return (ANCHOR_LEARNING_PROGRAM,)


@app.cell
def _(mo):
    mo.md("""
    ## Summary

    **Challenge 6 Key Learnings:**

    1. **Education-Backed Value**
       - Learning achievements as "collateral"
       - Token value tied to curriculum standards
       - Cannot inflate without actual learning

    2. **Earning Mechanics**
       - Subject, level, stage multipliers
       - Irish language bonus (cultural priority)
       - Verified by teachers/system

    3. **Spending Mechanics**
       - Redeemable for courses, tutoring, materials
       - Creates circular education economy
       - Providers earn by teaching

    4. **Technical Implementation**
       - Ethereum: CelticUSD.sol (CDP-style)
       - Solana: SPL Token-2022 with metadata
       - SpacetimeDB: Real-time achievement tracking

    **Tuath Integration:**
    - Players earn LEDU through in-game learning
    - Tokens usable across education ecosystem
    - Creates tangible value for learning Irish
    - Connects game progress to real education
    """)
    return ()


if __name__ == "__main__":
    app.run()
