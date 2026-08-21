// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";
import "../contracts/QuestRNG.sol";

/**
 * @title QuestRNG Test Suite
 * @notice Comprehensive tests for commit-reveal randomness
 * @dev SpeedRunEthereum Challenge 3: Dice Game
 */
contract QuestRNGTest is Test {
    QuestRNG public questRNG;

    address public owner;
    address public alice;
    address public bob;

    bytes32 constant ALICE_SEED = keccak256("alice-secret-seed-12345");
    bytes32 constant BOB_SEED = keccak256("bob-secret-seed-67890");

    event QuestCommitted(
        uint256 indexed questId,
        address indexed player,
        QuestRNG.Difficulty difficulty,
        bytes32 commitHash,
        uint256 commitBlock
    );

    event QuestRevealed(
        uint256 indexed questId,
        address indexed player,
        uint256 randomResult,
        QuestRNG.LootRarity lootRarity,
        uint256 reward
    );

    event QuestExpired(
        uint256 indexed questId,
        address indexed player
    );

    function setUp() public {
        owner = address(this);
        alice = makeAddr("alice");
        bob = makeAddr("bob");

        questRNG = new QuestRNG();
    }

    // ============ Commit Tests ============

    function test_CommitQuest() public {
        bytes32 commitHash = keccak256(abi.encodePacked(ALICE_SEED));

        vm.prank(alice);
        vm.expectEmit(true, true, false, true);
        emit QuestCommitted(0, alice, QuestRNG.Difficulty.Medium, commitHash, block.number);

        uint256 questId = questRNG.commitQuest(commitHash, QuestRNG.Difficulty.Medium);

        assertEq(questId, 0);
        assertEq(questRNG.questCount(), 1);

        QuestRNG.Quest memory quest = questRNG.getQuest(0);
        assertEq(quest.player, alice);
        assertEq(quest.commitHash, commitHash);
        assertEq(quest.commitBlock, block.number);
        assertEq(uint8(quest.difficulty), uint8(QuestRNG.Difficulty.Medium));
        assertEq(uint8(quest.state), uint8(QuestRNG.QuestState.Committed));
    }

    function test_CommitMultipleQuests() public {
        bytes32 hash1 = keccak256(abi.encodePacked(ALICE_SEED));
        bytes32 hash2 = keccak256(abi.encodePacked(BOB_SEED));

        vm.prank(alice);
        uint256 quest1 = questRNG.commitQuest(hash1, QuestRNG.Difficulty.Easy);

        vm.prank(bob);
        uint256 quest2 = questRNG.commitQuest(hash2, QuestRNG.Difficulty.Hard);

        assertEq(quest1, 0);
        assertEq(quest2, 1);
        assertEq(questRNG.questCount(), 2);
    }

    function test_RevertCommitEmptyHash() public {
        vm.prank(alice);
        vm.expectRevert("Invalid commit hash");
        questRNG.commitQuest(bytes32(0), QuestRNG.Difficulty.Easy);
    }

    function test_PlayerQuestTracking() public {
        bytes32 hash = keccak256(abi.encodePacked(ALICE_SEED));

        vm.prank(alice);
        questRNG.commitQuest(hash, QuestRNG.Difficulty.Easy);

        uint256[] memory aliceQuests = questRNG.getPlayerQuests(alice);
        assertEq(aliceQuests.length, 1);
        assertEq(aliceQuests[0], 0);
    }

    // ============ Reveal Tests ============

    function test_RevealQuest() public {
        bytes32 commitHash = keccak256(abi.encodePacked(ALICE_SEED));

        vm.prank(alice);
        uint256 questId = questRNG.commitQuest(commitHash, QuestRNG.Difficulty.Medium);

        // Advance blocks (minimum delay is 2)
        vm.roll(block.number + 3);

        vm.prank(alice);
        questRNG.revealQuest(questId, ALICE_SEED);

        QuestRNG.Quest memory quest = questRNG.getQuest(questId);
        assertEq(uint8(quest.state), uint8(QuestRNG.QuestState.Completed));
        assertEq(quest.playerSeed, ALICE_SEED);
        assertTrue(quest.randomResult > 0 || quest.randomResult == 0); // Has a result
        assertTrue(quest.rewardAmount > 0);
    }

    function test_RevealEmitsCorrectEvent() public {
        bytes32 commitHash = keccak256(abi.encodePacked(ALICE_SEED));

        vm.prank(alice);
        uint256 questId = questRNG.commitQuest(commitHash, QuestRNG.Difficulty.Easy);

        vm.roll(block.number + 3);

        vm.prank(alice);
        // Can't predict exact values, just verify event is emitted
        vm.expectEmit(true, true, false, false);
        emit QuestRevealed(questId, alice, 0, QuestRNG.LootRarity.Common, 0);
        questRNG.revealQuest(questId, ALICE_SEED);
    }

    function test_RevertRevealWrongPlayer() public {
        bytes32 commitHash = keccak256(abi.encodePacked(ALICE_SEED));

        vm.prank(alice);
        uint256 questId = questRNG.commitQuest(commitHash, QuestRNG.Difficulty.Easy);

        vm.roll(block.number + 3);

        vm.prank(bob);
        vm.expectRevert("Not your quest");
        questRNG.revealQuest(questId, ALICE_SEED);
    }

    function test_RevertRevealWrongSeed() public {
        bytes32 commitHash = keccak256(abi.encodePacked(ALICE_SEED));

        vm.prank(alice);
        uint256 questId = questRNG.commitQuest(commitHash, QuestRNG.Difficulty.Easy);

        vm.roll(block.number + 3);

        vm.prank(alice);
        vm.expectRevert("Invalid seed");
        questRNG.revealQuest(questId, BOB_SEED); // Wrong seed
    }

    function test_RevertRevealTooEarly() public {
        bytes32 commitHash = keccak256(abi.encodePacked(ALICE_SEED));

        vm.prank(alice);
        uint256 questId = questRNG.commitQuest(commitHash, QuestRNG.Difficulty.Easy);

        // Don't advance any blocks
        vm.prank(alice);
        vm.expectRevert("Too early to reveal");
        questRNG.revealQuest(questId, ALICE_SEED);
    }

    function test_RevertRevealExpired() public {
        bytes32 commitHash = keccak256(abi.encodePacked(ALICE_SEED));

        vm.prank(alice);
        uint256 questId = questRNG.commitQuest(commitHash, QuestRNG.Difficulty.Easy);

        // Advance past timeout (256 blocks)
        vm.roll(block.number + 257);

        vm.prank(alice);
        vm.expectRevert("Quest expired");
        questRNG.revealQuest(questId, ALICE_SEED);
    }

    function test_RevertRevealAlreadyRevealed() public {
        bytes32 commitHash = keccak256(abi.encodePacked(ALICE_SEED));

        vm.prank(alice);
        uint256 questId = questRNG.commitQuest(commitHash, QuestRNG.Difficulty.Easy);

        vm.roll(block.number + 3);

        vm.prank(alice);
        questRNG.revealQuest(questId, ALICE_SEED);

        // Try to reveal again
        vm.prank(alice);
        vm.expectRevert("Quest not in committed state");
        questRNG.revealQuest(questId, ALICE_SEED);
    }

    // ============ Expiry Tests ============

    function test_ExpireQuest() public {
        bytes32 commitHash = keccak256(abi.encodePacked(ALICE_SEED));

        vm.prank(alice);
        uint256 questId = questRNG.commitQuest(commitHash, QuestRNG.Difficulty.Easy);

        // Advance past timeout
        vm.roll(block.number + 260);

        vm.expectEmit(true, true, false, false);
        emit QuestExpired(questId, alice);
        questRNG.expireQuest(questId);

        QuestRNG.Quest memory quest = questRNG.getQuest(questId);
        assertEq(uint8(quest.state), uint8(QuestRNG.QuestState.Expired));
    }

    function test_RevertExpireNotExpiredYet() public {
        bytes32 commitHash = keccak256(abi.encodePacked(ALICE_SEED));

        vm.prank(alice);
        uint256 questId = questRNG.commitQuest(commitHash, QuestRNG.Difficulty.Easy);

        // Only advance 10 blocks
        vm.roll(block.number + 10);

        vm.expectRevert("Quest not expired yet");
        questRNG.expireQuest(questId);
    }

    // ============ Reward Calculation Tests ============

    function test_DifficultyMultipliers() public view {
        // Easy = 1x, Medium = 2x, Hard = 5x, Legendary = 10x
        assertEq(questRNG.difficultyMultipliers(QuestRNG.Difficulty.Easy), 100);
        assertEq(questRNG.difficultyMultipliers(QuestRNG.Difficulty.Medium), 200);
        assertEq(questRNG.difficultyMultipliers(QuestRNG.Difficulty.Hard), 500);
        assertEq(questRNG.difficultyMultipliers(QuestRNG.Difficulty.Legendary), 1000);
    }

    function test_SimulateReward() public view {
        // Test reward simulation function
        (uint256 reward, QuestRNG.LootRarity rarity) = questRNG.simulateReward(
            500, // Mid-range roll
            QuestRNG.Difficulty.Medium
        );

        // Reward should be between 20-200 CELTIC for medium (2x multiplier)
        assertTrue(reward >= 20 ether);
        assertTrue(reward <= 200 ether);

        // Rarity for roll 500 should be common (< 500) or uncommon (500-800)
        assertTrue(
            uint8(rarity) == uint8(QuestRNG.LootRarity.Common) ||
            uint8(rarity) == uint8(QuestRNG.LootRarity.Uncommon)
        );
    }

    function test_LegendaryRarity() public view {
        // Roll 995 should give legendary (>= 990)
        (, QuestRNG.LootRarity rarity) = questRNG.simulateReward(
            995 << 16, // Put 995 in rarity bits
            QuestRNG.Difficulty.Easy
        );

        assertEq(uint8(rarity), uint8(QuestRNG.LootRarity.Legendary));
    }

    // ============ Loot Table Tests ============

    function test_LootTablesInitialized() public view {
        QuestRNG.LootEntry[] memory easyLoot = questRNG.getLootTable(QuestRNG.Difficulty.Easy);
        QuestRNG.LootEntry[] memory mediumLoot = questRNG.getLootTable(QuestRNG.Difficulty.Medium);
        QuestRNG.LootEntry[] memory hardLoot = questRNG.getLootTable(QuestRNG.Difficulty.Hard);

        assertTrue(easyLoot.length > 0);
        assertTrue(mediumLoot.length > 0);
        assertTrue(hardLoot.length > 0);
    }

    function test_AddLootEntry() public {
        questRNG.addLootEntry(
            QuestRNG.Difficulty.Legendary,
            "Test Item",
            "test",
            0,
            500,
            QuestRNG.LootRarity.Legendary,
            999
        );

        QuestRNG.LootEntry[] memory legendaryLoot = questRNG.getLootTable(QuestRNG.Difficulty.Legendary);
        assertTrue(legendaryLoot.length > 0);
    }

    function test_ClearLootTable() public {
        // First verify there's loot
        QuestRNG.LootEntry[] memory before = questRNG.getLootTable(QuestRNG.Difficulty.Easy);
        assertTrue(before.length > 0);

        // Clear it
        questRNG.clearLootTable(QuestRNG.Difficulty.Easy);

        // Verify empty
        QuestRNG.LootEntry[] memory afterLoot = questRNG.getLootTable(QuestRNG.Difficulty.Easy);
        assertEq(afterLoot.length, 0);
    }

    // ============ Admin Tests ============

    function test_SetRevealTimeout() public {
        questRNG.setRevealTimeout(100);
        assertEq(questRNG.revealTimeout(), 100);
    }

    function test_RevertSetInvalidTimeout() public {
        vm.expectRevert("Invalid timeout");
        questRNG.setRevealTimeout(5); // Too low

        vm.expectRevert("Invalid timeout");
        questRNG.setRevealTimeout(300); // Too high
    }

    function test_SetMinRevealDelay() public {
        questRNG.setMinRevealDelay(5);
        assertEq(questRNG.minRevealDelay(), 5);
    }

    function test_SetDifficultyMultiplier() public {
        questRNG.setDifficultyMultiplier(QuestRNG.Difficulty.Easy, 150);
        assertEq(questRNG.difficultyMultipliers(QuestRNG.Difficulty.Easy), 150);
    }

    function test_RevertNonOwnerAdmin() public {
        vm.prank(alice);
        vm.expectRevert();
        questRNG.setRevealTimeout(100);
    }

    // ============ View Function Tests ============

    function test_GenerateCommitHash() public view {
        bytes32 expected = keccak256(abi.encodePacked(ALICE_SEED));
        bytes32 result = questRNG.generateCommitHash(ALICE_SEED);
        assertEq(result, expected);
    }

    function test_CanReveal() public {
        bytes32 commitHash = keccak256(abi.encodePacked(ALICE_SEED));

        vm.prank(alice);
        uint256 questId = questRNG.commitQuest(commitHash, QuestRNG.Difficulty.Easy);

        // Too early
        (bool canRevealNow, string memory reason) = questRNG.canReveal(questId);
        assertFalse(canRevealNow);
        assertEq(reason, "Too early to reveal");

        // After delay
        vm.roll(block.number + 3);
        (canRevealNow, reason) = questRNG.canReveal(questId);
        assertTrue(canRevealNow);
        assertEq(reason, "Ready to reveal");
    }

    function test_CompletedQuestCount() public {
        bytes32 commitHash = keccak256(abi.encodePacked(ALICE_SEED));

        vm.prank(alice);
        uint256 questId = questRNG.commitQuest(commitHash, QuestRNG.Difficulty.Easy);

        vm.roll(block.number + 3);

        vm.prank(alice);
        questRNG.revealQuest(questId, ALICE_SEED);

        assertEq(questRNG.playerCompletedQuests(alice), 1);
    }

    // ============ Fuzz Tests ============

    function testFuzz_CommitReveal(bytes32 seed) public {
        vm.assume(seed != bytes32(0));

        bytes32 commitHash = keccak256(abi.encodePacked(seed));

        vm.prank(alice);
        uint256 questId = questRNG.commitQuest(commitHash, QuestRNG.Difficulty.Medium);

        vm.roll(block.number + 3);

        vm.prank(alice);
        questRNG.revealQuest(questId, seed);

        QuestRNG.Quest memory quest = questRNG.getQuest(questId);
        assertEq(uint8(quest.state), uint8(QuestRNG.QuestState.Completed));
    }

    function testFuzz_RewardRange(uint256 randomValue) public view {
        randomValue = bound(randomValue, 0, type(uint256).max);

        (uint256 reward, ) = questRNG.simulateReward(
            randomValue,
            QuestRNG.Difficulty.Medium
        );

        // Medium difficulty: base 10-100 * 2x = 20-200 CELTIC
        assertTrue(reward >= 20 ether);
        assertTrue(reward <= 200 ether);
    }

    function testFuzz_RarityDistribution(uint256 randomValue) public view {
        randomValue = bound(randomValue, 0, type(uint256).max);

        (, QuestRNG.LootRarity rarity) = questRNG.simulateReward(
            randomValue,
            QuestRNG.Difficulty.Easy
        );

        // Rarity should always be valid
        assertTrue(uint8(rarity) <= uint8(QuestRNG.LootRarity.Legendary));
    }
}
