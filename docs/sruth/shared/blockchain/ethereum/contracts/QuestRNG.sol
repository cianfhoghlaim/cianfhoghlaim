// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

/**
 * @title QuestRNG
 * @author Cianfhoghlaim / tuath project
 * @notice Secure randomness for quest rewards and loot drops
 * @dev SpeedRunEthereum Challenge 3: Dice Game
 *
 * Features:
 * - Commit-reveal scheme for fair randomness
 * - VRF integration ready (Chainlink/Gelato)
 * - Quest reward distribution
 * - Loot drop tables
 * - MEV protection
 */
contract QuestRNG is Ownable, ReentrancyGuard {
    // ============================================================================
    // State Variables
    // ============================================================================

    /// @notice Commit-reveal timeout in blocks
    uint256 public revealTimeout = 256;

    /// @notice Minimum blocks before reveal (prevents front-running)
    uint256 public minRevealDelay = 2;

    /// @notice Quest counter
    uint256 public questCount;

    /// @notice Total rewards distributed
    uint256 public totalRewardsDistributed;

    // ============================================================================
    // Enums
    // ============================================================================

    /// @notice Quest difficulty levels
    enum Difficulty {
        Easy,       // 0
        Medium,     // 1
        Hard,       // 2
        Legendary   // 3
    }

    /// @notice Loot rarity tiers
    enum LootRarity {
        Common,     // 0 - 50%
        Uncommon,   // 1 - 30%
        Rare,       // 2 - 15%
        Epic,       // 3 - 4%
        Legendary   // 4 - 1%
    }

    /// @notice Quest states
    enum QuestState {
        None,
        Committed,
        Revealed,
        Completed,
        Expired
    }

    // ============================================================================
    // Structs
    // ============================================================================

    /// @notice Quest data
    struct Quest {
        address player;
        bytes32 commitHash;
        uint256 commitBlock;
        uint256 revealBlock;
        bytes32 playerSeed;
        bytes32 blockSeed;
        uint256 randomResult;
        Difficulty difficulty;
        QuestState state;
        uint256 rewardAmount;
        LootRarity lootRarity;
    }

    /// @notice Loot drop table entry
    struct LootEntry {
        string name;
        string category;
        uint256 minRoll;   // Inclusive
        uint256 maxRoll;   // Exclusive
        LootRarity rarity;
        uint256 itemId;    // Reference to item in CelticShop
    }

    // ============================================================================
    // Mappings
    // ============================================================================

    /// @notice Quest ID => Quest data
    mapping(uint256 => Quest) public quests;

    /// @notice Player => Active quest IDs
    mapping(address => uint256[]) public playerQuests;

    /// @notice Player => Total quests completed
    mapping(address => uint256) public playerCompletedQuests;

    /// @notice Difficulty => Base reward multiplier (basis points)
    mapping(Difficulty => uint256) public difficultyMultipliers;

    /// @notice Difficulty => Loot table
    mapping(Difficulty => LootEntry[]) public lootTables;

    // ============================================================================
    // Events
    // ============================================================================

    event QuestCommitted(
        uint256 indexed questId,
        address indexed player,
        Difficulty difficulty,
        bytes32 commitHash,
        uint256 commitBlock
    );

    event QuestRevealed(
        uint256 indexed questId,
        address indexed player,
        uint256 randomResult,
        LootRarity lootRarity,
        uint256 reward
    );

    event QuestExpired(
        uint256 indexed questId,
        address indexed player
    );

    event LootDropped(
        uint256 indexed questId,
        address indexed player,
        string itemName,
        LootRarity rarity,
        uint256 itemId
    );

    // ============================================================================
    // Constructor
    // ============================================================================

    constructor() Ownable(msg.sender) {
        // Set default difficulty multipliers
        difficultyMultipliers[Difficulty.Easy] = 100;      // 1x
        difficultyMultipliers[Difficulty.Medium] = 200;    // 2x
        difficultyMultipliers[Difficulty.Hard] = 500;      // 5x
        difficultyMultipliers[Difficulty.Legendary] = 1000; // 10x

        // Initialize default loot tables
        _initializeLootTables();
    }

    // ============================================================================
    // Core Functions - Commit Phase
    // ============================================================================

    /**
     * @notice Start a quest by committing to a secret seed
     * @param commitHash Hash of player's secret seed: keccak256(playerSeed)
     * @param difficulty Quest difficulty level
     * @return questId The ID of the new quest
     *
     * @dev The commit-reveal scheme works as follows:
     * 1. Player generates random seed off-chain
     * 2. Player commits hash of seed (can't change after)
     * 3. Wait for blocks to pass (randomness source)
     * 4. Player reveals original seed
     * 5. Final random = keccak256(playerSeed, blockHash)
     *
     * This prevents:
     * - Miners from manipulating block hash after seeing seed
     * - Players from choosing seed after seeing block hash
     */
    function commitQuest(
        bytes32 commitHash,
        Difficulty difficulty
    ) external nonReentrant returns (uint256) {
        require(commitHash != bytes32(0), "Invalid commit hash");

        uint256 questId = questCount++;

        quests[questId] = Quest({
            player: msg.sender,
            commitHash: commitHash,
            commitBlock: block.number,
            revealBlock: 0,
            playerSeed: bytes32(0),
            blockSeed: bytes32(0),
            randomResult: 0,
            difficulty: difficulty,
            state: QuestState.Committed,
            rewardAmount: 0,
            lootRarity: LootRarity.Common
        });

        playerQuests[msg.sender].push(questId);

        emit QuestCommitted(
            questId,
            msg.sender,
            difficulty,
            commitHash,
            block.number
        );

        return questId;
    }

    // ============================================================================
    // Core Functions - Reveal Phase
    // ============================================================================

    /**
     * @notice Complete a quest by revealing the original seed
     * @param questId The quest to complete
     * @param playerSeed The original seed that was hashed in commit
     */
    function revealQuest(
        uint256 questId,
        bytes32 playerSeed
    ) external nonReentrant {
        Quest storage quest = quests[questId];

        require(quest.player == msg.sender, "Not your quest");
        require(quest.state == QuestState.Committed, "Quest not in committed state");

        // Verify the commit hash
        require(
            keccak256(abi.encodePacked(playerSeed)) == quest.commitHash,
            "Invalid seed"
        );

        // Check timing constraints
        uint256 blocksPassed = block.number - quest.commitBlock;
        require(blocksPassed >= minRevealDelay, "Too early to reveal");
        require(blocksPassed < revealTimeout, "Quest expired");

        // Get block hash from commit block (for randomness)
        // Note: blockhash only works for last 256 blocks
        bytes32 blockSeed = blockhash(quest.commitBlock + 1);
        require(blockSeed != bytes32(0), "Block hash unavailable");

        // Combine seeds for final randomness
        uint256 randomResult = uint256(keccak256(abi.encodePacked(
            playerSeed,
            blockSeed,
            questId,
            msg.sender
        )));

        // Calculate reward and loot
        (uint256 reward, LootRarity rarity) = _calculateReward(
            randomResult,
            quest.difficulty
        );

        // Update quest
        quest.revealBlock = block.number;
        quest.playerSeed = playerSeed;
        quest.blockSeed = blockSeed;
        quest.randomResult = randomResult;
        quest.state = QuestState.Completed;
        quest.rewardAmount = reward;
        quest.lootRarity = rarity;

        playerCompletedQuests[msg.sender]++;
        totalRewardsDistributed += reward;

        // Determine loot drop
        _processLootDrop(questId, randomResult, quest.difficulty);

        emit QuestRevealed(
            questId,
            msg.sender,
            randomResult,
            rarity,
            reward
        );
    }

    /**
     * @notice Mark expired quests
     * @param questId The quest to check/expire
     */
    function expireQuest(uint256 questId) external {
        Quest storage quest = quests[questId];

        require(quest.state == QuestState.Committed, "Quest not committed");
        require(
            block.number - quest.commitBlock >= revealTimeout,
            "Quest not expired yet"
        );

        quest.state = QuestState.Expired;

        emit QuestExpired(questId, quest.player);
    }

    // ============================================================================
    // Reward Calculation
    // ============================================================================

    /**
     * @notice Calculate reward based on random result and difficulty
     * @param randomResult The random number from reveal
     * @param difficulty The quest difficulty
     * @return reward The reward amount (in CELTIC tokens * 1e18)
     * @return rarity The loot rarity tier
     */
    function _calculateReward(
        uint256 randomResult,
        Difficulty difficulty
    ) internal view returns (uint256 reward, LootRarity rarity) {
        // Extract different parts of random for different purposes
        uint256 rewardRoll = randomResult % 1000;  // 0-999
        uint256 rarityRoll = (randomResult >> 16) % 1000;  // 0-999

        // Base reward: 10-100 CELTIC based on roll
        uint256 baseReward = 10 ether + (rewardRoll * 90 ether / 1000);

        // Apply difficulty multiplier
        uint256 multiplier = difficultyMultipliers[difficulty];
        reward = (baseReward * multiplier) / 100;

        // Determine rarity based on roll
        if (rarityRoll >= 990) {
            rarity = LootRarity.Legendary;  // 1%
        } else if (rarityRoll >= 950) {
            rarity = LootRarity.Epic;       // 4%
        } else if (rarityRoll >= 800) {
            rarity = LootRarity.Rare;       // 15%
        } else if (rarityRoll >= 500) {
            rarity = LootRarity.Uncommon;   // 30%
        } else {
            rarity = LootRarity.Common;     // 50%
        }
    }

    /**
     * @notice Process loot drop from quest completion
     */
    function _processLootDrop(
        uint256 questId,
        uint256 randomResult,
        Difficulty difficulty
    ) internal {
        LootEntry[] storage table = lootTables[difficulty];
        if (table.length == 0) return;

        // Use different bits for loot table roll
        uint256 lootRoll = (randomResult >> 32) % 1000;

        // Find matching loot entry
        for (uint256 i = 0; i < table.length; i++) {
            if (lootRoll >= table[i].minRoll && lootRoll < table[i].maxRoll) {
                emit LootDropped(
                    questId,
                    msg.sender,
                    table[i].name,
                    table[i].rarity,
                    table[i].itemId
                );
                break;
            }
        }
    }

    // ============================================================================
    // Loot Table Management
    // ============================================================================

    /**
     * @notice Initialize default loot tables
     */
    function _initializeLootTables() internal {
        // Easy difficulty loot
        lootTables[Difficulty.Easy].push(LootEntry({
            name: "Health Potion",
            category: "consumable",
            minRoll: 0,
            maxRoll: 500,
            rarity: LootRarity.Common,
            itemId: 6
        }));
        lootTables[Difficulty.Easy].push(LootEntry({
            name: "XP Boost",
            category: "consumable",
            minRoll: 500,
            maxRoll: 800,
            rarity: LootRarity.Uncommon,
            itemId: 7
        }));
        lootTables[Difficulty.Easy].push(LootEntry({
            name: "Learning Scroll",
            category: "learning",
            minRoll: 800,
            maxRoll: 1000,
            rarity: LootRarity.Rare,
            itemId: 8
        }));

        // Medium difficulty loot
        lootTables[Difficulty.Medium].push(LootEntry({
            name: "Bronze Shield",
            category: "armor",
            minRoll: 0,
            maxRoll: 400,
            rarity: LootRarity.Common,
            itemId: 5
        }));
        lootTables[Difficulty.Medium].push(LootEntry({
            name: "Feather Cloak",
            category: "armor",
            minRoll: 400,
            maxRoll: 750,
            rarity: LootRarity.Rare,
            itemId: 4
        }));
        lootTables[Difficulty.Medium].push(LootEntry({
            name: "Welsh Sword",
            category: "weapon",
            minRoll: 750,
            maxRoll: 1000,
            rarity: LootRarity.Epic,
            itemId: 3
        }));

        // Hard difficulty loot
        lootTables[Difficulty.Hard].push(LootEntry({
            name: unicode"Gáe Bulg",
            category: "weapon",
            minRoll: 0,
            maxRoll: 600,
            rarity: LootRarity.Epic,
            itemId: 2
        }));
        lootTables[Difficulty.Hard].push(LootEntry({
            name: "Sword of Light",
            category: "weapon",
            minRoll: 600,
            maxRoll: 1000,
            rarity: LootRarity.Legendary,
            itemId: 1
        }));
    }

    /**
     * @notice Add a loot entry to a difficulty table
     */
    function addLootEntry(
        Difficulty difficulty,
        string calldata name,
        string calldata category,
        uint256 minRoll,
        uint256 maxRoll,
        LootRarity rarity,
        uint256 itemId
    ) external onlyOwner {
        require(maxRoll > minRoll, "Invalid roll range");
        require(maxRoll <= 1000, "Max roll exceeds 1000");

        lootTables[difficulty].push(LootEntry({
            name: name,
            category: category,
            minRoll: minRoll,
            maxRoll: maxRoll,
            rarity: rarity,
            itemId: itemId
        }));
    }

    /**
     * @notice Clear and reset a loot table
     */
    function clearLootTable(Difficulty difficulty) external onlyOwner {
        delete lootTables[difficulty];
    }

    // ============================================================================
    // Admin Functions
    // ============================================================================

    /**
     * @notice Update reveal timeout
     */
    function setRevealTimeout(uint256 blocks) external onlyOwner {
        require(blocks >= 10 && blocks <= 256, "Invalid timeout");
        revealTimeout = blocks;
    }

    /**
     * @notice Update minimum reveal delay
     */
    function setMinRevealDelay(uint256 blocks) external onlyOwner {
        require(blocks >= 1 && blocks <= 10, "Invalid delay");
        minRevealDelay = blocks;
    }

    /**
     * @notice Update difficulty multiplier
     */
    function setDifficultyMultiplier(
        Difficulty difficulty,
        uint256 multiplier
    ) external onlyOwner {
        require(multiplier >= 50 && multiplier <= 5000, "Invalid multiplier");
        difficultyMultipliers[difficulty] = multiplier;
    }

    // ============================================================================
    // View Functions
    // ============================================================================

    /**
     * @notice Get quest details
     */
    function getQuest(uint256 questId) external view returns (Quest memory) {
        return quests[questId];
    }

    /**
     * @notice Get player's quest IDs
     */
    function getPlayerQuests(address player) external view returns (uint256[] memory) {
        return playerQuests[player];
    }

    /**
     * @notice Get loot table for a difficulty
     */
    function getLootTable(Difficulty difficulty) external view returns (LootEntry[] memory) {
        return lootTables[difficulty];
    }

    /**
     * @notice Generate a commit hash from a seed (helper for frontend)
     * @param seed The secret seed to hash
     * @return The commit hash to submit
     */
    function generateCommitHash(bytes32 seed) external pure returns (bytes32) {
        return keccak256(abi.encodePacked(seed));
    }

    /**
     * @notice Check if a quest can be revealed
     */
    function canReveal(uint256 questId) external view returns (bool, string memory) {
        Quest storage quest = quests[questId];

        if (quest.state != QuestState.Committed) {
            return (false, "Quest not in committed state");
        }

        uint256 blocksPassed = block.number - quest.commitBlock;

        if (blocksPassed < minRevealDelay) {
            return (false, "Too early to reveal");
        }

        if (blocksPassed >= revealTimeout) {
            return (false, "Quest expired");
        }

        // Check if block hash is still available
        if (blockhash(quest.commitBlock + 1) == bytes32(0)) {
            return (false, "Block hash no longer available");
        }

        return (true, "Ready to reveal");
    }

    /**
     * @notice Simulate reward for a given random result (for testing)
     */
    function simulateReward(
        uint256 randomResult,
        Difficulty difficulty
    ) external view returns (uint256 reward, LootRarity rarity) {
        return _calculateReward(randomResult, difficulty);
    }
}
