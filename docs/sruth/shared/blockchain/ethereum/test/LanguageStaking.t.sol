// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";
import "../contracts/LanguageStaking.sol";

/**
 * @title LanguageStaking Test Suite
 * @notice Comprehensive tests for the Learn-to-Earn staking contract
 * @dev SpeedRunEthereum Challenge 1: Decentralized Staking
 */
contract LanguageStakingTest is Test {
    LanguageStaking public staking;
    CelticToken public token;

    address public owner;
    address public alice;
    address public bob;
    address public verifier;

    uint256 constant STAKE_AMOUNT = 1000 ether;
    uint256 constant INITIAL_BALANCE = 10000 ether;

    function setUp() public {
        owner = address(this);
        alice = makeAddr("alice");
        bob = makeAddr("bob");
        verifier = makeAddr("verifier");

        // Deploy token
        token = new CelticToken();

        // Deploy staking contract
        staking = new LanguageStaking(address(token));

        // Setup verifier
        staking.setVerifier(verifier, true);

        // Distribute tokens
        token.transfer(alice, INITIAL_BALANCE);
        token.transfer(bob, INITIAL_BALANCE);

        // Approve staking contract
        vm.prank(alice);
        token.approve(address(staking), type(uint256).max);

        vm.prank(bob);
        token.approve(address(staking), type(uint256).max);
    }

    // ============ Basic Staking Tests ============

    function test_Stake() public {
        vm.prank(alice);
        staking.stake(STAKE_AMOUNT, LanguageStaking.Language.Irish);

        LanguageStaking.Staker memory info = staking.getStakerInfo(alice);

        assertEq(info.balance, STAKE_AMOUNT);
        assertEq(info.isActive, true);
        assertEq(uint8(info.language), uint8(LanguageStaking.Language.Irish));
        assertEq(uint8(info.level), uint8(LanguageStaking.LearningLevel.Beginner));
        assertEq(staking.totalStaked(), STAKE_AMOUNT);
    }

    function test_StakeMultipleTimes() public {
        vm.startPrank(alice);

        staking.stake(STAKE_AMOUNT, LanguageStaking.Language.Irish);
        staking.stake(STAKE_AMOUNT, LanguageStaking.Language.Irish);

        vm.stopPrank();

        LanguageStaking.Staker memory info = staking.getStakerInfo(alice);
        assertEq(info.balance, STAKE_AMOUNT * 2);
    }

    function test_RevertStakeZero() public {
        vm.prank(alice);
        vm.expectRevert("Cannot stake 0");
        staking.stake(0, LanguageStaking.Language.Irish);
    }

    // ============ Unstaking Tests ============

    function test_Unstake() public {
        vm.startPrank(alice);

        staking.stake(STAKE_AMOUNT, LanguageStaking.Language.Irish);

        // Fast forward time for rewards
        vm.warp(block.timestamp + 30 days);

        uint256 balanceBefore = token.balanceOf(alice);
        staking.unstake(STAKE_AMOUNT);
        uint256 balanceAfter = token.balanceOf(alice);

        assertEq(balanceAfter - balanceBefore, STAKE_AMOUNT);
        assertEq(staking.totalStaked(), 0);

        vm.stopPrank();
    }

    function test_UnstakeAll() public {
        vm.startPrank(alice);

        staking.stake(STAKE_AMOUNT, LanguageStaking.Language.Irish);
        staking.unstake(0); // 0 means unstake all

        LanguageStaking.Staker memory info = staking.getStakerInfo(alice);
        assertEq(info.balance, 0);
        assertEq(info.isActive, false);

        vm.stopPrank();
    }

    function test_PartialUnstake() public {
        vm.startPrank(alice);

        staking.stake(STAKE_AMOUNT, LanguageStaking.Language.Irish);
        staking.unstake(STAKE_AMOUNT / 2);

        LanguageStaking.Staker memory info = staking.getStakerInfo(alice);
        assertEq(info.balance, STAKE_AMOUNT / 2);
        assertEq(info.isActive, true);

        vm.stopPrank();
    }

    function test_RevertUnstakeWithoutStake() public {
        vm.prank(alice);
        vm.expectRevert("No active stake");
        staking.unstake(STAKE_AMOUNT);
    }

    // ============ Reward Calculation Tests ============

    function test_RewardsAccrue() public {
        vm.prank(alice);
        staking.stake(STAKE_AMOUNT, LanguageStaking.Language.Irish);

        // Fast forward 365 days
        vm.warp(block.timestamp + 365 days);

        uint256 rewards = staking.pendingRewards(alice);

        // Base APY is 500 basis points (5%)
        // Expected: STAKE_AMOUNT * 5% = 50 ether (approximate)
        // With beginner level multiplier (100), rewards should be around 50 ether
        assertTrue(rewards > 0);
        assertTrue(rewards < STAKE_AMOUNT / 10); // Less than 10% for beginners
    }

    function test_ClaimRewards() public {
        vm.prank(alice);
        staking.stake(STAKE_AMOUNT, LanguageStaking.Language.Irish);

        vm.warp(block.timestamp + 30 days);

        uint256 rewardsBefore = staking.pendingRewards(alice);
        assertTrue(rewardsBefore > 0);

        vm.prank(alice);
        staking.claimRewards();

        uint256 rewardsAfter = staking.pendingRewards(alice);
        assertEq(rewardsAfter, 0);
    }

    // ============ Learning Verification Tests ============

    function test_RecordLesson() public {
        vm.prank(alice);
        staking.stake(STAKE_AMOUNT, LanguageStaking.Language.Irish);

        vm.prank(verifier);
        staking.recordLesson(alice, 1);

        LanguageStaking.Staker memory info = staking.getStakerInfo(alice);
        assertEq(info.lessonsCompleted, 1);
    }

    function test_StreakMaintained() public {
        vm.prank(alice);
        staking.stake(STAKE_AMOUNT, LanguageStaking.Language.Irish);

        // Complete lessons on consecutive days
        for (uint i = 0; i < 5; i++) {
            vm.warp(block.timestamp + 12 hours); // Within 24h
            vm.prank(verifier);
            staking.recordLesson(alice, i + 1);
        }

        LanguageStaking.Staker memory info = staking.getStakerInfo(alice);
        assertEq(info.lessonsCompleted, 5);
        assertEq(info.streakDays, 5);
    }

    function test_StreakBroken() public {
        vm.prank(alice);
        staking.stake(STAKE_AMOUNT, LanguageStaking.Language.Irish);

        vm.prank(verifier);
        staking.recordLesson(alice, 1);

        // Skip 3 days
        vm.warp(block.timestamp + 3 days);

        vm.prank(verifier);
        staking.recordLesson(alice, 2);

        LanguageStaking.Staker memory info = staking.getStakerInfo(alice);
        assertEq(info.streakDays, 1); // Reset to 1
    }

    function test_RevertRecordLessonNonVerifier() public {
        vm.prank(alice);
        staking.stake(STAKE_AMOUNT, LanguageStaking.Language.Irish);

        vm.prank(bob);
        vm.expectRevert("Not a verifier");
        staking.recordLesson(alice, 1);
    }

    // ============ Milestone Tests ============

    function test_VerifyMilestone() public {
        vm.prank(alice);
        staking.stake(STAKE_AMOUNT, LanguageStaking.Language.Irish);

        vm.prank(verifier);
        staking.verifyMilestone(
            alice,
            LanguageStaking.LearningLevel.Elementary,
            "Completed A1 Irish course"
        );

        LanguageStaking.Staker memory info = staking.getStakerInfo(alice);
        assertEq(uint8(info.level), uint8(LanguageStaking.LearningLevel.Elementary));

        LanguageStaking.Milestone[] memory m = staking.getMilestones(alice);
        assertEq(m.length, 1);
        assertEq(m[0].achievement, "Completed A1 Irish course");
    }

    function test_MilestoneIncreaseRewards() public {
        vm.prank(alice);
        staking.stake(STAKE_AMOUNT, LanguageStaking.Language.Irish);

        // Get baseline APY
        uint256 beginnerAPY = staking.getEffectiveAPY(alice);

        // Level up
        vm.prank(verifier);
        staking.verifyMilestone(
            alice,
            LanguageStaking.LearningLevel.Intermediate,
            "Completed B1 Irish course"
        );

        uint256 intermediateAPY = staking.getEffectiveAPY(alice);

        // Intermediate multiplier (200) should double the APY
        assertTrue(intermediateAPY > beginnerAPY);
    }

    function test_RevertMilestoneDowngrade() public {
        vm.prank(alice);
        staking.stake(STAKE_AMOUNT, LanguageStaking.Language.Irish);

        vm.prank(verifier);
        staking.verifyMilestone(alice, LanguageStaking.LearningLevel.Advanced, "B2 achieved");

        vm.prank(verifier);
        vm.expectRevert("Must be level up");
        staking.verifyMilestone(alice, LanguageStaking.LearningLevel.Elementary, "Downgrade");
    }

    // ============ APY Calculation Tests ============

    function test_EffectiveAPY() public {
        vm.prank(alice);
        staking.stake(STAKE_AMOUNT, LanguageStaking.Language.Irish);

        uint256 initialAPY = staking.getEffectiveAPY(alice);
        assertEq(initialAPY, 500); // Base APY for beginner

        // Fast forward 30 days for loyalty bonus
        vm.warp(block.timestamp + 30 days);

        uint256 loyaltyAPY = staking.getEffectiveAPY(alice);
        assertTrue(loyaltyAPY > initialAPY); // Should have loyalty bonus
    }

    function test_LoyaltyBonusCapped() public {
        vm.prank(alice);
        staking.stake(STAKE_AMOUNT, LanguageStaking.Language.Irish);

        // Fast forward 12 months (more than 6 month cap)
        vm.warp(block.timestamp + 365 days);

        uint256 cappedAPY = staking.getEffectiveAPY(alice);

        // Base (500) + max loyalty (1200) = 1700 for beginner (100 multiplier)
        // 1700 * 100 / 100 = 1700
        assertEq(cappedAPY, 1700);
    }

    // ============ Admin Tests ============

    function test_SetVerifier() public {
        address newVerifier = makeAddr("newVerifier");

        staking.setVerifier(newVerifier, true);
        assertTrue(staking.verifiers(newVerifier));

        staking.setVerifier(newVerifier, false);
        assertFalse(staking.verifiers(newVerifier));
    }

    function test_SetBaseAPY() public {
        staking.setBaseAPY(1000); // 10%
        assertEq(staking.baseAPY(), 1000);
    }

    function test_RevertSetAPYTooHigh() public {
        vm.expectRevert("APY too high");
        staking.setBaseAPY(10001);
    }

    function test_RevertNonOwnerAdmin() public {
        vm.prank(alice);
        vm.expectRevert();
        staking.setVerifier(bob, true);
    }

    // ============ Multi-Language Tests ============

    function test_DifferentLanguages() public {
        vm.prank(alice);
        staking.stake(STAKE_AMOUNT, LanguageStaking.Language.Irish);

        vm.prank(bob);
        staking.stake(STAKE_AMOUNT, LanguageStaking.Language.Welsh);

        LanguageStaking.Staker memory aliceInfo = staking.getStakerInfo(alice);
        LanguageStaking.Staker memory bobInfo = staking.getStakerInfo(bob);

        assertEq(uint8(aliceInfo.language), uint8(LanguageStaking.Language.Irish));
        assertEq(uint8(bobInfo.language), uint8(LanguageStaking.Language.Welsh));
    }

    // ============ Fuzz Tests ============

    function testFuzz_Stake(uint256 amount) public {
        amount = bound(amount, 1, INITIAL_BALANCE);

        vm.prank(alice);
        staking.stake(amount, LanguageStaking.Language.Irish);

        assertEq(staking.totalStaked(), amount);
    }

    function testFuzz_RewardsProportional(uint256 amount, uint256 timeElapsed) public {
        amount = bound(amount, 1 ether, INITIAL_BALANCE);
        timeElapsed = bound(timeElapsed, 1 days, 365 days);

        vm.prank(alice);
        staking.stake(amount, LanguageStaking.Language.Irish);

        vm.warp(block.timestamp + timeElapsed);

        uint256 rewards = staking.pendingRewards(alice);

        // Rewards should scale with time
        assertTrue(rewards > 0);
    }
}
