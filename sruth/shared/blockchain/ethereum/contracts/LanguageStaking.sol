// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

/**
 * @title LanguageStaking
 * @author Cianfhoghlaim / tuath project
 * @notice Learn-to-Earn staking contract for the tuath educational MMO
 * @dev SpeedRunEthereum Challenge 1: Decentralized Staking
 *
 * Features:
 * - Stake CELTIC tokens to earn learning rewards
 * - XP multipliers based on staking duration
 * - Learning milestone verification
 * - Time-based reward calculations
 * - Minimum staking periods with bonuses
 */
contract LanguageStaking is Ownable, ReentrancyGuard {
    using SafeERC20 for IERC20;

    // ============================================================================
    // State Variables
    // ============================================================================

    /// @notice The token used for staking
    IERC20 public immutable stakingToken;

    /// @notice Total tokens staked in the contract
    uint256 public totalStaked;

    /// @notice Base APY in basis points (e.g., 500 = 5%)
    uint256 public baseAPY = 500;

    /// @notice Minimum staking period for bonus (7 days)
    uint256 public constant MIN_STAKE_PERIOD = 7 days;

    /// @notice XP multiplier boost for long-term stakers (basis points)
    uint256 public loyaltyBonus = 200; // 2% extra APY per month staked

    /// @notice Maximum loyalty bonus cap (6 months = 12%)
    uint256 public maxLoyaltyBonus = 1200;

    // ============================================================================
    // Structs
    // ============================================================================

    /// @notice Learning milestone levels
    enum LearningLevel {
        Beginner,      // 0 - Just started
        Elementary,    // 1 - A1 level
        Intermediate,  // 2 - A2-B1 level
        Advanced,      // 3 - B2 level
        Fluent         // 4 - C1+ level
    }

    /// @notice Celtic language being learned
    enum Language {
        Irish,
        Welsh,
        ScottishGaelic,
        Manx,
        Cornish,
        Breton
    }

    /// @notice Individual staker information
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

    /// @notice Learning milestone completion record
    struct Milestone {
        uint256 completedAt;
        LearningLevel levelAchieved;
        uint256 bonusReward;
        string achievement;
    }

    // ============================================================================
    // Mappings
    // ============================================================================

    /// @notice Staker data by address
    mapping(address => Staker) public stakers;

    /// @notice Milestone history by address
    mapping(address => Milestone[]) public milestones;

    /// @notice Trusted verifiers who can confirm learning milestones
    mapping(address => bool) public verifiers;

    /// @notice Reward multiplier by learning level (basis points)
    mapping(LearningLevel => uint256) public levelMultipliers;

    // ============================================================================
    // Events
    // ============================================================================

    event Staked(
        address indexed staker,
        uint256 amount,
        Language language,
        uint256 timestamp
    );

    event Unstaked(
        address indexed staker,
        uint256 amount,
        uint256 rewards,
        uint256 timestamp
    );

    event RewardsClaimed(
        address indexed staker,
        uint256 amount,
        uint256 timestamp
    );

    event MilestoneCompleted(
        address indexed staker,
        LearningLevel level,
        uint256 bonusReward,
        string achievement
    );

    event LessonCompleted(
        address indexed staker,
        uint256 lessonId,
        uint256 streakDays,
        uint256 timestamp
    );

    event StreakMaintained(
        address indexed staker,
        uint256 streakDays,
        uint256 bonusMultiplier
    );

    event VerifierUpdated(address indexed verifier, bool status);

    // ============================================================================
    // Constructor
    // ============================================================================

    constructor(address _stakingToken) Ownable(msg.sender) {
        stakingToken = IERC20(_stakingToken);

        // Initialize level multipliers
        levelMultipliers[LearningLevel.Beginner] = 100;      // 1x
        levelMultipliers[LearningLevel.Elementary] = 150;    // 1.5x
        levelMultipliers[LearningLevel.Intermediate] = 200;  // 2x
        levelMultipliers[LearningLevel.Advanced] = 300;      // 3x
        levelMultipliers[LearningLevel.Fluent] = 500;        // 5x
    }

    // ============================================================================
    // Staking Functions
    // ============================================================================

    /**
     * @notice Stake tokens and begin earning learn-to-earn rewards
     * @param amount Amount of tokens to stake
     * @param language The Celtic language being learned
     */
    function stake(uint256 amount, Language language) external nonReentrant {
        require(amount > 0, "Cannot stake 0");

        Staker storage staker = stakers[msg.sender];

        // Claim any pending rewards first
        if (staker.isActive && staker.balance > 0) {
            _claimRewards(msg.sender);
        }

        // Transfer tokens to contract
        stakingToken.safeTransferFrom(msg.sender, address(this), amount);

        // Update staker data
        if (!staker.isActive) {
            staker.stakedAt = block.timestamp;
            staker.lastClaimAt = block.timestamp;
            staker.level = LearningLevel.Beginner;
            staker.language = language;
            staker.isActive = true;
        }

        staker.balance += amount;
        totalStaked += amount;

        emit Staked(msg.sender, amount, language, block.timestamp);
    }

    /**
     * @notice Unstake tokens and claim all rewards
     * @param amount Amount to unstake (0 = unstake all)
     */
    function unstake(uint256 amount) external nonReentrant {
        Staker storage staker = stakers[msg.sender];
        require(staker.isActive, "No active stake");
        require(staker.balance > 0, "Nothing staked");

        if (amount == 0) {
            amount = staker.balance;
        }
        require(amount <= staker.balance, "Insufficient balance");

        // Calculate and claim rewards
        uint256 rewards = _calculateRewards(msg.sender);
        staker.rewardDebt = 0;
        staker.lastClaimAt = block.timestamp;

        // Update balances
        staker.balance -= amount;
        totalStaked -= amount;

        if (staker.balance == 0) {
            staker.isActive = false;
        }

        // Transfer tokens and rewards
        stakingToken.safeTransfer(msg.sender, amount);

        // Note: In production, rewards would come from a separate reward pool
        // For this demo, we assume the contract has sufficient reward tokens

        emit Unstaked(msg.sender, amount, rewards, block.timestamp);
    }

    /**
     * @notice Claim pending rewards without unstaking
     */
    function claimRewards() external nonReentrant {
        _claimRewards(msg.sender);
    }

    // ============================================================================
    // Learning Verification (Verifier Only)
    // ============================================================================

    /**
     * @notice Record a completed lesson (called by verified learning platform)
     * @param learner Address of the learner
     * @param lessonId Unique lesson identifier
     */
    function recordLesson(address learner, uint256 lessonId) external {
        require(verifiers[msg.sender], "Not a verifier");
        require(stakers[learner].isActive, "Learner not staking");

        Staker storage staker = stakers[learner];
        staker.lessonsCompleted += 1;

        // Check for streak maintenance (simplified: lesson within 24h)
        if (block.timestamp - staker.lastClaimAt < 1 days) {
            staker.streakDays += 1;

            emit StreakMaintained(
                learner,
                staker.streakDays,
                _getStreakMultiplier(staker.streakDays)
            );
        } else if (block.timestamp - staker.lastClaimAt > 2 days) {
            // Streak broken if more than 48h without activity
            staker.streakDays = 1;
        }

        emit LessonCompleted(learner, lessonId, staker.streakDays, block.timestamp);
    }

    /**
     * @notice Verify a learning milestone achievement
     * @param learner Address of the learner
     * @param newLevel The level achieved
     * @param achievement Description of the achievement
     */
    function verifyMilestone(
        address learner,
        LearningLevel newLevel,
        string calldata achievement
    ) external {
        require(verifiers[msg.sender], "Not a verifier");
        require(stakers[learner].isActive, "Learner not staking");

        Staker storage staker = stakers[learner];
        require(uint8(newLevel) > uint8(staker.level), "Must be level up");

        // Calculate bonus reward for milestone
        uint256 bonusReward = _calculateMilestoneBonus(staker.balance, newLevel);

        // Update level
        staker.level = newLevel;

        // Record milestone
        milestones[learner].push(Milestone({
            completedAt: block.timestamp,
            levelAchieved: newLevel,
            bonusReward: bonusReward,
            achievement: achievement
        }));

        // Add bonus to pending rewards
        staker.rewardDebt += bonusReward;

        emit MilestoneCompleted(learner, newLevel, bonusReward, achievement);
    }

    // ============================================================================
    // View Functions
    // ============================================================================

    /**
     * @notice Get pending rewards for a staker
     */
    function pendingRewards(address account) external view returns (uint256) {
        return _calculateRewards(account);
    }

    /**
     * @notice Get current APY for a staker including all bonuses
     */
    function getEffectiveAPY(address account) external view returns (uint256) {
        Staker storage staker = stakers[account];
        if (!staker.isActive) return 0;

        uint256 effectiveAPY = baseAPY;

        // Add loyalty bonus
        uint256 stakingDuration = block.timestamp - staker.stakedAt;
        uint256 monthsStaked = stakingDuration / 30 days;
        uint256 loyalty = monthsStaked * loyaltyBonus;
        if (loyalty > maxLoyaltyBonus) loyalty = maxLoyaltyBonus;
        effectiveAPY += loyalty;

        // Apply level multiplier
        effectiveAPY = (effectiveAPY * levelMultipliers[staker.level]) / 100;

        // Apply streak bonus
        effectiveAPY = (effectiveAPY * _getStreakMultiplier(staker.streakDays)) / 100;

        return effectiveAPY;
    }

    /**
     * @notice Get staker's milestone history
     */
    function getMilestones(address account) external view returns (Milestone[] memory) {
        return milestones[account];
    }

    /**
     * @notice Get staker's full info
     */
    function getStakerInfo(address account) external view returns (Staker memory) {
        return stakers[account];
    }

    // ============================================================================
    // Admin Functions
    // ============================================================================

    /**
     * @notice Add or remove a verifier
     */
    function setVerifier(address verifier, bool status) external onlyOwner {
        verifiers[verifier] = status;
        emit VerifierUpdated(verifier, status);
    }

    /**
     * @notice Update base APY
     */
    function setBaseAPY(uint256 newAPY) external onlyOwner {
        require(newAPY <= 10000, "APY too high"); // Max 100%
        baseAPY = newAPY;
    }

    /**
     * @notice Update level multiplier
     */
    function setLevelMultiplier(LearningLevel level, uint256 multiplier) external onlyOwner {
        levelMultipliers[level] = multiplier;
    }

    // ============================================================================
    // Internal Functions
    // ============================================================================

    function _claimRewards(address account) internal {
        uint256 rewards = _calculateRewards(account);
        if (rewards == 0) return;

        Staker storage staker = stakers[account];
        staker.rewardDebt = 0;
        staker.lastClaimAt = block.timestamp;

        // In production, transfer from reward pool
        // stakingToken.safeTransfer(account, rewards);

        emit RewardsClaimed(account, rewards, block.timestamp);
    }

    function _calculateRewards(address account) internal view returns (uint256) {
        Staker storage staker = stakers[account];
        if (!staker.isActive || staker.balance == 0) return 0;

        uint256 stakingDuration = block.timestamp - staker.lastClaimAt;

        // Base reward: balance * APY * time / year
        uint256 baseReward = (staker.balance * baseAPY * stakingDuration) / (365 days * 10000);

        // Apply level multiplier
        baseReward = (baseReward * levelMultipliers[staker.level]) / 100;

        // Apply streak bonus
        baseReward = (baseReward * _getStreakMultiplier(staker.streakDays)) / 100;

        // Add loyalty bonus
        uint256 monthsStaked = (block.timestamp - staker.stakedAt) / 30 days;
        uint256 loyalty = monthsStaked * loyaltyBonus;
        if (loyalty > maxLoyaltyBonus) loyalty = maxLoyaltyBonus;
        uint256 loyaltyReward = (baseReward * loyalty) / 10000;

        // Add any pending milestone rewards
        return baseReward + loyaltyReward + staker.rewardDebt;
    }

    function _calculateMilestoneBonus(uint256 stakedAmount, LearningLevel level) internal pure returns (uint256) {
        // Bonus: 1% of staked amount per level achieved
        uint256 levelValue = uint256(level);
        return (stakedAmount * levelValue * 100) / 10000; // 1% per level
    }

    function _getStreakMultiplier(uint256 streakDays) internal pure returns (uint256) {
        // Streak multiplier: 100 base + 1 per streak day, max 130 (30% bonus)
        if (streakDays == 0) return 100;
        if (streakDays > 30) return 130;
        return 100 + streakDays;
    }
}

/**
 * @title CelticToken
 * @notice Simple ERC20 token for testing staking
 */
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract CelticToken is ERC20, Ownable {
    constructor() ERC20("Celtic Token", "CELTIC") Ownable(msg.sender) {
        // Mint initial supply to deployer
        _mint(msg.sender, 1_000_000_000 * 10**18);
    }

    function mint(address to, uint256 amount) external onlyOwner {
        _mint(to, amount);
    }
}
