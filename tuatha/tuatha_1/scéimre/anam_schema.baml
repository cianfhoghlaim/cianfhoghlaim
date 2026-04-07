// Anam Learn-to-Earn Schema
// BAML types for learning outcomes, token rewards, and NFT evolution

// =============================================================================
// Core Learning Types
// =============================================================================

/// Languages supported by the Anam platform
enum Language {
    Irish       @alias("ga")    @description("Irish (Gaeilge)")
    ScottishGaelic @alias("gd") @description("Scottish Gaelic (Gàidhlig)")
    Manx        @alias("gv")    @description("Manx (Gaelg)")
    Welsh       @alias("cy")    @description("Welsh (Cymraeg)")
    English     @alias("en")    @description("English")
}

/// Subject domains aligned with Irish Leaving Certificate
enum Subject {
    Irish
    Chemistry
    Biology
    Geography
    Mathematics
    History
    Welsh       @description("For Welsh medium schools")
    ScottishGaelic @description("For Scottish Gaelic medium schools")
}

/// Types of learning activities that earn rewards
enum ActivityType {
    QuizCompletion      @description("Completed a quiz or assessment")
    TranslationMining   @description("Contributed a verified translation")
    OracyMining         @description("Voice recording for ASR training")
    HandwritingOCR      @description("Handwriting sample for OCR training")
    PeerReview          @description("Reviewed another learner's work")
    ContentCreation     @description("Created educational content")
    MentorSession       @description("Completed a mentorship session")
}

/// Elements from the pent-elemental cosmology
enum Element {
    Spirit  @alias("Anam")    @description("Currency/Mentorship")
    Water   @alias("Uisce")   @description("Travel/Inventory")
    Fire    @alias("Tine")    @description("Combat/Forge")
    Earth   @alias("Talamh")  @description("Territory/Defense")
    Air     @alias("Aer")     @description("Magic/Governance")
}

// =============================================================================
// Learning Outcome Types
// =============================================================================

/// A single learning activity that may earn rewards
class LearningActivity {
    user_address    string      @description("Ethereum address of the learner")
    activity_type   ActivityType
    subject         Subject
    language        Language
    score           float       @description("Score from 0.0 to 1.0")
    duration_seconds int        @description("Time spent on activity")
    challenge_id    string      @description("ID of the specific challenge/quiz")
    timestamp       string      @description("ISO 8601 timestamp")
    metadata        map<string, string>? @description("Additional activity data")
}

/// Computed XP and token reward for an activity
class LearningReward {
    user_address    string
    xp_amount       int         @description("XP earned (used for NFT leveling)")
    tuath_amount    int         @description("Tuath tokens to mint")
    reason          string      @description("Human-readable reward reason")
    activity_ref    string      @description("Reference to original activity")
    language_bonus  float       @description("Multiplier for endangered languages")
    mentor_tithe    int?        @description("Amount to pay to mentor if bonded")
}

/// Batch of rewards ready for on-chain execution
class RewardBatch {
    batch_id        string      @description("Unique batch identifier")
    rewards         LearningReward[]
    total_xp        int
    total_tuath     int
    total_tithe     int
    created_at      string
}

// =============================================================================
// NFT Evolution Types
// =============================================================================

/// Current state of a Cúchulainn NFT warrior
class WarriorState {
    token_id        int
    owner_address   string
    level           int
    current_xp      int
    total_xp_earned int
    element         Element
    stage           string      @description("Sétanta, Cúchulainn, or Ríastrad")
    warp_spasm      bool        @description("True if level >= 11")
    active_geasa    int         @description("Number of active taboos")
    language        Language    @description("Primary language")
}

/// NFT evolution event triggered by XP gain
class NFTEvolution {
    token_id        int
    from_level      int
    to_level        int
    new_stage       string?     @description("New stage name if changed")
    new_abilities   string[]    @description("Abilities unlocked at new level")
    visual_changes  string[]    @description("SVG/metadata changes")
    warp_spasm_unlocked bool
}

// =============================================================================
// Mentorship (Anam Cara) Types
// =============================================================================

/// Soul bond between mentor and acolyte
class SoulBond {
    bond_id         int
    mentor_address  string
    acolyte_address string
    tithe_rate_bps  int         @description("Basis points (100 = 1%)")
    bond_timestamp  string
    total_tithe_paid int
    is_active       bool
}

/// Mentor profile with reputation
class MentorProfile {
    address         string
    soul_level      int         @description("Reputation score")
    total_acolytes  int
    active_acolytes int
    total_tithe_earned int
    is_active       bool        @description("Available for new bonds")
}

// =============================================================================
// BAML Functions
// =============================================================================

/// Compute XP and token rewards for a learning activity
function ComputeReward(activity: LearningActivity) -> LearningReward {
    client GeminiFlash
    prompt #"
        Calculate the XP and Tuath token reward for this learning activity.

        Activity: {{ activity }}

        Rules:
        - Base XP: 100 per activity
        - Score multiplier: score * 2.0
        - Language bonuses: Manx (2.0x), Irish/Scottish (1.5x), Welsh (1.3x), English (1.0x)
        - Tuath tokens: XP / 10

        Formula: base_xp * score * score_multiplier * language_bonus

        Return the computed reward with a clear reason string.
        {{ ctx.output_format }}
    "#
}

/// Generate NFT metadata JSON for a warrior at a given state
function GenerateNFTMetadata(warrior: WarriorState) -> string {
    client GeminiFlash
    prompt #"
        Generate the JSON metadata for this Cúchulainn NFT warrior.

        Warrior State: {{ warrior }}

        Include:
        - name: "{stage} #{token_id}"
        - description: Celtic warrior lore based on stage and element
        - attributes: level, element (Celtic name), stage, language, warp_spasm status
        - image: Placeholder SVG data URI

        Stage names:
        - Level 1-5: Sétanta (young warrior)
        - Level 6-10: Cúchulainn (The Hound)
        - Level 11+: Ríastrad (Warp Spasm form)

        Return valid JSON.
    "#
}

/// Determine if a learner qualifies for mentor status
function EvaluateMentorEligibility(
    activities: LearningActivity[],
    current_soul_level: int
) -> bool {
    client GeminiFlash
    prompt #"
        Determine if this learner qualifies to become a mentor.

        Recent Activities: {{ activities }}
        Current Soul Level: {{ current_soul_level }}

        Requirements:
        - Minimum soul level: 100
        - Consistent high scores (average > 0.8)
        - Activity in at least 2 languages
        - No recent geis violations

        Return true or false.
        {{ ctx.output_format }}
    "#
}

/// Extract learning achievement from free-form text (for crowdsourced validation)
function ExtractLearningAchievement(
    text: string,
    expected_language: Language
) -> LearningActivity {
    client GeminiFlash
    prompt #"
        Extract a structured learning activity from this text submission.

        Text: {{ text }}
        Expected Language: {{ expected_language }}

        Determine:
        - What type of activity (translation, quiz, etc.)
        - The subject if identifiable
        - Estimate a quality score (0.0-1.0)

        {{ ctx.output_format }}
    "#
}
