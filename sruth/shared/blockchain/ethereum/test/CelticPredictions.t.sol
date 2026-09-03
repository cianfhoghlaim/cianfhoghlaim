// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";
import "../contracts/CelticPredictions.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

/// @title Mock Collateral Token for testing
contract MockToken is ERC20 {
    constructor() ERC20("Mock USDC", "mUSDC") {
        _mint(msg.sender, 10_000_000e18);
    }

    function mint(address to, uint256 amount) external {
        _mint(to, amount);
    }
}

/// @title CelticPredictions Test Suite
/// @notice Comprehensive tests for prediction market functionality
contract CelticPredictionsTest is Test {
    CelticPredictions public predictions;
    MockToken public usdc;

    address public alice = makeAddr("alice");
    address public bob = makeAddr("bob");
    address public charlie = makeAddr("charlie");
    address public oracle = makeAddr("oracle");
    address public treasury = makeAddr("treasury");

    uint256 constant INITIAL_LIQUIDITY = 10000e18;
    uint256 constant RESOLUTION_TIME = 1735689600; // Dec 31, 2025

    event MarketCreated(
        uint256 indexed marketId,
        string question,
        uint256 resolutionTime,
        address creator
    );
    event SharesPurchased(
        uint256 indexed marketId,
        address indexed buyer,
        bool isYes,
        uint256 shares,
        uint256 cost
    );
    event MarketResolved(
        uint256 indexed marketId,
        int256 outcome,
        address resolver
    );
    event WinningsClaimed(
        uint256 indexed marketId,
        address indexed claimer,
        uint256 amount
    );
    event DisputeRaised(
        uint256 indexed marketId,
        address indexed disputer,
        string reason
    );

    function setUp() public {
        usdc = new MockToken();

        predictions = new CelticPredictions(address(usdc));

        // Setup oracle
        predictions.setAuthorizedOracle(oracle, true);

        // Setup users with tokens
        usdc.mint(alice, 100000e18);
        usdc.mint(bob, 100000e18);
        usdc.mint(charlie, 100000e18);

        // Approve predictions contract
        vm.prank(alice);
        usdc.approve(address(predictions), type(uint256).max);

        vm.prank(bob);
        usdc.approve(address(predictions), type(uint256).max);

        vm.prank(charlie);
        usdc.approve(address(predictions), type(uint256).max);
    }

    // ============ Market Creation Tests ============

    function test_CreateMarket() public {
        vm.startPrank(alice);

        vm.expectEmit(true, false, false, true);
        emit MarketCreated(0, "Will ETH reach $5000?", RESOLUTION_TIME, alice);

        uint256 marketId = predictions.createMarket(
            "Will ETH reach $5000?",
            RESOLUTION_TIME,
            INITIAL_LIQUIDITY,
            100 // 1% creator fee
        );

        assertEq(marketId, 0);

        (
            string memory question,
            uint256 resolutionTime,
            uint256 totalYesShares,
            uint256 totalNoShares,
            uint256 liquidity,
            int256 resolvedOutcome,
            bool resolved,
            bool disputed
        ) = predictions.getMarket(marketId);

        assertEq(question, "Will ETH reach $5000?");
        assertEq(resolutionTime, RESOLUTION_TIME);
        assertEq(totalYesShares, 0);
        assertEq(totalNoShares, 0);
        assertEq(liquidity, INITIAL_LIQUIDITY);
        assertEq(resolvedOutcome, -1);
        assertFalse(resolved);
        assertFalse(disputed);

        vm.stopPrank();
    }

    function test_CreateMarket_MultipleMarkets() public {
        vm.startPrank(alice);

        uint256 market1 = predictions.createMarket(
            "Question 1",
            RESOLUTION_TIME,
            INITIAL_LIQUIDITY,
            100
        );

        uint256 market2 = predictions.createMarket(
            "Question 2",
            RESOLUTION_TIME + 1000,
            INITIAL_LIQUIDITY * 2,
            200
        );

        assertEq(market1, 0);
        assertEq(market2, 1);
        assertEq(predictions.marketCount(), 2);

        vm.stopPrank();
    }

    function test_RevertWhen_CreateMarket_PastResolution() public {
        vm.startPrank(alice);

        vm.expectRevert("Resolution must be future");
        predictions.createMarket(
            "Question",
            block.timestamp - 1,
            INITIAL_LIQUIDITY,
            100
        );

        vm.stopPrank();
    }

    function test_RevertWhen_CreateMarket_InsufficientLiquidity() public {
        vm.startPrank(alice);

        vm.expectRevert("Insufficient initial liquidity");
        predictions.createMarket(
            "Question",
            RESOLUTION_TIME,
            10e18, // Below minimum
            100
        );

        vm.stopPrank();
    }

    function test_RevertWhen_CreateMarket_HighCreatorFee() public {
        vm.startPrank(alice);

        vm.expectRevert("Creator fee too high");
        predictions.createMarket(
            "Question",
            RESOLUTION_TIME,
            INITIAL_LIQUIDITY,
            600 // 6% exceeds max
        );

        vm.stopPrank();
    }

    // ============ Share Trading Tests ============

    function test_BuyShares_Yes() public {
        vm.prank(alice);
        uint256 marketId = predictions.createMarket(
            "Test Market",
            RESOLUTION_TIME,
            INITIAL_LIQUIDITY,
            100
        );

        uint256 shares = 100e18;
        uint256 cost = predictions.calculateBuyCost(marketId, true, shares);

        vm.startPrank(bob);

        vm.expectEmit(true, true, false, false);
        emit SharesPurchased(marketId, bob, true, shares, cost);

        predictions.buyShares(marketId, true, shares, cost * 2);

        (uint256 yesShares, uint256 noShares,) = predictions.getPosition(marketId, bob);
        assertEq(yesShares, shares);
        assertEq(noShares, 0);

        vm.stopPrank();
    }

    function test_BuyShares_No() public {
        vm.prank(alice);
        uint256 marketId = predictions.createMarket(
            "Test Market",
            RESOLUTION_TIME,
            INITIAL_LIQUIDITY,
            100
        );

        uint256 shares = 150e18;

        vm.startPrank(bob);
        predictions.buyShares(marketId, false, shares, 1000e18);

        (uint256 yesShares, uint256 noShares,) = predictions.getPosition(marketId, bob);
        assertEq(yesShares, 0);
        assertEq(noShares, shares);

        vm.stopPrank();
    }

    function test_BuyShares_MultipleTrades() public {
        vm.prank(alice);
        uint256 marketId = predictions.createMarket(
            "Test Market",
            RESOLUTION_TIME,
            INITIAL_LIQUIDITY,
            100
        );

        // Bob buys YES
        vm.prank(bob);
        predictions.buyShares(marketId, true, 100e18, 1000e18);

        // Charlie buys NO
        vm.prank(charlie);
        predictions.buyShares(marketId, false, 200e18, 1000e18);

        // Bob buys more YES
        vm.prank(bob);
        predictions.buyShares(marketId, true, 50e18, 1000e18);

        (uint256 bobYes,,) = predictions.getPosition(marketId, bob);
        (uint256 charlieYes, uint256 charlieNo,) = predictions.getPosition(marketId, charlie);

        assertEq(bobYes, 150e18);
        assertEq(charlieYes, 0);
        assertEq(charlieNo, 200e18);
    }

    function test_RevertWhen_BuyShares_ExceedsMaxCost() public {
        vm.prank(alice);
        uint256 marketId = predictions.createMarket(
            "Test Market",
            RESOLUTION_TIME,
            INITIAL_LIQUIDITY,
            100
        );

        vm.prank(bob);
        vm.expectRevert("Cost exceeds max");
        predictions.buyShares(marketId, true, 100e18, 1); // Max cost too low
    }

    function test_RevertWhen_BuyShares_MarketResolved() public {
        vm.prank(alice);
        uint256 marketId = predictions.createMarket(
            "Test Market",
            RESOLUTION_TIME,
            INITIAL_LIQUIDITY,
            100
        );

        // Resolve market
        vm.warp(RESOLUTION_TIME + 1);
        vm.prank(oracle);
        predictions.resolveMarket(marketId, 1);

        // Try to buy
        vm.prank(bob);
        vm.expectRevert(CelticPredictions.MarketAlreadyResolved.selector);
        predictions.buyShares(marketId, true, 100e18, 1000e18);
    }

    function test_RevertWhen_BuyShares_MarketExpired() public {
        vm.prank(alice);
        uint256 marketId = predictions.createMarket(
            "Test Market",
            RESOLUTION_TIME,
            INITIAL_LIQUIDITY,
            100
        );

        vm.warp(RESOLUTION_TIME + 1);

        vm.prank(bob);
        vm.expectRevert(CelticPredictions.MarketExpired.selector);
        predictions.buyShares(marketId, true, 100e18, 1000e18);
    }

    function test_SellShares() public {
        vm.prank(alice);
        uint256 marketId = predictions.createMarket(
            "Test Market",
            RESOLUTION_TIME,
            INITIAL_LIQUIDITY,
            100
        );

        // Buy shares
        vm.startPrank(bob);
        predictions.buyShares(marketId, true, 100e18, 1000e18);

        uint256 balanceBefore = usdc.balanceOf(bob);

        // Sell shares
        predictions.sellShares(marketId, true, 50e18, 0);

        uint256 balanceAfter = usdc.balanceOf(bob);
        assertGt(balanceAfter, balanceBefore);

        (uint256 yesShares,,) = predictions.getPosition(marketId, bob);
        assertEq(yesShares, 50e18);

        vm.stopPrank();
    }

    function test_RevertWhen_SellShares_InsufficientShares() public {
        vm.prank(alice);
        uint256 marketId = predictions.createMarket(
            "Test Market",
            RESOLUTION_TIME,
            INITIAL_LIQUIDITY,
            100
        );

        vm.prank(bob);
        predictions.buyShares(marketId, true, 100e18, 1000e18);

        vm.prank(bob);
        vm.expectRevert(CelticPredictions.InsufficientShares.selector);
        predictions.sellShares(marketId, true, 200e18, 0);
    }

    // ============ Probability Tests ============

    function test_GetProbability_Initial() public {
        vm.prank(alice);
        uint256 marketId = predictions.createMarket(
            "Test Market",
            RESOLUTION_TIME,
            INITIAL_LIQUIDITY,
            100
        );

        uint256 prob = predictions.getProbability(marketId);
        // Initial should be ~50%
        assertApproxEqRel(prob, 0.5e18, 0.01e18);
    }

    function test_GetProbability_AfterYesBuy() public {
        vm.prank(alice);
        uint256 marketId = predictions.createMarket(
            "Test Market",
            RESOLUTION_TIME,
            INITIAL_LIQUIDITY,
            100
        );

        vm.prank(bob);
        predictions.buyShares(marketId, true, 500e18, 10000e18);

        uint256 prob = predictions.getProbability(marketId);
        // Should be higher than 50%
        assertGt(prob, 0.5e18);
    }

    function test_GetProbability_AfterNoBuy() public {
        vm.prank(alice);
        uint256 marketId = predictions.createMarket(
            "Test Market",
            RESOLUTION_TIME,
            INITIAL_LIQUIDITY,
            100
        );

        vm.prank(bob);
        predictions.buyShares(marketId, false, 500e18, 10000e18);

        uint256 prob = predictions.getProbability(marketId);
        // Should be lower than 50%
        assertLt(prob, 0.5e18);
    }

    // ============ Resolution Tests ============

    function test_ResolveMarket_Yes() public {
        vm.prank(alice);
        uint256 marketId = predictions.createMarket(
            "Test Market",
            RESOLUTION_TIME,
            INITIAL_LIQUIDITY,
            100
        );

        vm.warp(RESOLUTION_TIME + 1);

        vm.expectEmit(true, false, false, true);
        emit MarketResolved(marketId, 1, oracle);

        vm.prank(oracle);
        predictions.resolveMarket(marketId, 1);

        (,,,,,int256 outcome, bool resolved,) = predictions.getMarket(marketId);
        assertEq(outcome, 1);
        assertTrue(resolved);
    }

    function test_ResolveMarket_No() public {
        vm.prank(alice);
        uint256 marketId = predictions.createMarket(
            "Test Market",
            RESOLUTION_TIME,
            INITIAL_LIQUIDITY,
            100
        );

        vm.warp(RESOLUTION_TIME + 1);

        vm.prank(oracle);
        predictions.resolveMarket(marketId, 0);

        (,,,,,int256 outcome, bool resolved,) = predictions.getMarket(marketId);
        assertEq(outcome, 0);
        assertTrue(resolved);
    }

    function test_RevertWhen_ResolveMarket_NotOracle() public {
        vm.prank(alice);
        uint256 marketId = predictions.createMarket(
            "Test Market",
            RESOLUTION_TIME,
            INITIAL_LIQUIDITY,
            100
        );

        vm.warp(RESOLUTION_TIME + 1);

        vm.prank(bob);
        vm.expectRevert(CelticPredictions.NotAuthorizedOracle.selector);
        predictions.resolveMarket(marketId, 1);
    }

    function test_RevertWhen_ResolveMarket_TooEarly() public {
        vm.prank(alice);
        uint256 marketId = predictions.createMarket(
            "Test Market",
            RESOLUTION_TIME,
            INITIAL_LIQUIDITY,
            100
        );

        vm.prank(oracle);
        vm.expectRevert(CelticPredictions.MarketNotExpired.selector);
        predictions.resolveMarket(marketId, 1);
    }

    function test_RevertWhen_ResolveMarket_InvalidOutcome() public {
        vm.prank(alice);
        uint256 marketId = predictions.createMarket(
            "Test Market",
            RESOLUTION_TIME,
            INITIAL_LIQUIDITY,
            100
        );

        vm.warp(RESOLUTION_TIME + 1);

        vm.prank(oracle);
        vm.expectRevert(CelticPredictions.InvalidOutcome.selector);
        predictions.resolveMarket(marketId, 2);
    }

    // ============ Claim Winnings Tests ============

    function test_ClaimWinnings_YesWins() public {
        vm.prank(alice);
        uint256 marketId = predictions.createMarket(
            "Test Market",
            RESOLUTION_TIME,
            INITIAL_LIQUIDITY,
            100
        );

        // Bob buys YES shares
        vm.prank(bob);
        predictions.buyShares(marketId, true, 100e18, 1000e18);

        // Resolve as YES
        vm.warp(RESOLUTION_TIME + 1);
        vm.prank(oracle);
        predictions.resolveMarket(marketId, 1);

        // Wait for dispute period
        vm.warp(RESOLUTION_TIME + 2 days);

        uint256 balanceBefore = usdc.balanceOf(bob);

        vm.prank(bob);
        predictions.claimWinnings(marketId);

        uint256 balanceAfter = usdc.balanceOf(bob);
        assertGt(balanceAfter, balanceBefore);
    }

    function test_ClaimWinnings_NoWins() public {
        vm.prank(alice);
        uint256 marketId = predictions.createMarket(
            "Test Market",
            RESOLUTION_TIME,
            INITIAL_LIQUIDITY,
            100
        );

        // Bob buys NO shares
        vm.prank(bob);
        predictions.buyShares(marketId, false, 100e18, 1000e18);

        // Resolve as NO
        vm.warp(RESOLUTION_TIME + 1);
        vm.prank(oracle);
        predictions.resolveMarket(marketId, 0);

        vm.warp(RESOLUTION_TIME + 2 days);

        uint256 balanceBefore = usdc.balanceOf(bob);

        vm.prank(bob);
        predictions.claimWinnings(marketId);

        assertGt(usdc.balanceOf(bob), balanceBefore);
    }

    function test_RevertWhen_ClaimWinnings_NotResolved() public {
        vm.prank(alice);
        uint256 marketId = predictions.createMarket(
            "Test Market",
            RESOLUTION_TIME,
            INITIAL_LIQUIDITY,
            100
        );

        vm.prank(bob);
        predictions.buyShares(marketId, true, 100e18, 1000e18);

        vm.prank(bob);
        vm.expectRevert(CelticPredictions.MarketNotExpired.selector);
        predictions.claimWinnings(marketId);
    }

    function test_RevertWhen_ClaimWinnings_DisputePeriod() public {
        vm.prank(alice);
        uint256 marketId = predictions.createMarket(
            "Test Market",
            RESOLUTION_TIME,
            INITIAL_LIQUIDITY,
            100
        );

        vm.prank(bob);
        predictions.buyShares(marketId, true, 100e18, 1000e18);

        vm.warp(RESOLUTION_TIME + 1);
        vm.prank(oracle);
        predictions.resolveMarket(marketId, 1);

        // Try to claim before dispute period ends
        vm.prank(bob);
        vm.expectRevert(CelticPredictions.DisputePeriodActive.selector);
        predictions.claimWinnings(marketId);
    }

    function test_RevertWhen_ClaimWinnings_AlreadyClaimed() public {
        vm.prank(alice);
        uint256 marketId = predictions.createMarket(
            "Test Market",
            RESOLUTION_TIME,
            INITIAL_LIQUIDITY,
            100
        );

        vm.prank(bob);
        predictions.buyShares(marketId, true, 100e18, 1000e18);

        vm.warp(RESOLUTION_TIME + 1);
        vm.prank(oracle);
        predictions.resolveMarket(marketId, 1);

        vm.warp(RESOLUTION_TIME + 2 days);

        vm.prank(bob);
        predictions.claimWinnings(marketId);

        vm.prank(bob);
        vm.expectRevert(CelticPredictions.AlreadyRedeemed.selector);
        predictions.claimWinnings(marketId);
    }

    // ============ Dispute Tests ============

    function test_RaiseDispute() public {
        vm.prank(alice);
        uint256 marketId = predictions.createMarket(
            "Test Market",
            RESOLUTION_TIME,
            INITIAL_LIQUIDITY,
            100
        );

        vm.warp(RESOLUTION_TIME + 1);
        vm.prank(oracle);
        predictions.resolveMarket(marketId, 1);

        vm.expectEmit(true, true, false, true);
        emit DisputeRaised(marketId, bob, "Incorrect resolution");

        vm.prank(bob);
        predictions.raiseDispute(marketId, "Incorrect resolution");

        (,,,,,,, bool disputed) = predictions.getMarket(marketId);
        assertTrue(disputed);
    }

    function test_ResolveDispute_Accept() public {
        vm.prank(alice);
        uint256 marketId = predictions.createMarket(
            "Test Market",
            RESOLUTION_TIME,
            INITIAL_LIQUIDITY,
            100
        );

        vm.warp(RESOLUTION_TIME + 1);
        vm.prank(oracle);
        predictions.resolveMarket(marketId, 1);

        vm.prank(bob);
        predictions.raiseDispute(marketId, "Should be NO");

        uint256 bobBalanceBefore = usdc.balanceOf(bob);

        // Owner resolves dispute in favor of disputer
        predictions.resolveDispute(marketId, true, 0);

        // Bob should get bond back
        assertGt(usdc.balanceOf(bob), bobBalanceBefore);

        (,,,,,int256 outcome,,) = predictions.getMarket(marketId);
        assertEq(outcome, 0);
    }

    function test_ResolveDispute_Reject() public {
        vm.prank(alice);
        uint256 marketId = predictions.createMarket(
            "Test Market",
            RESOLUTION_TIME,
            INITIAL_LIQUIDITY,
            100
        );

        vm.warp(RESOLUTION_TIME + 1);
        vm.prank(oracle);
        predictions.resolveMarket(marketId, 1);

        vm.prank(bob);
        predictions.raiseDispute(marketId, "Wrong");

        uint256 bobBalanceBefore = usdc.balanceOf(bob);

        // Owner rejects dispute
        predictions.resolveDispute(marketId, false, 1);

        // Bob loses bond
        assertEq(usdc.balanceOf(bob), bobBalanceBefore);

        (,,,,,int256 outcome,,) = predictions.getMarket(marketId);
        assertEq(outcome, 1); // Unchanged
    }

    function test_RevertWhen_RaiseDispute_AfterPeriod() public {
        vm.prank(alice);
        uint256 marketId = predictions.createMarket(
            "Test Market",
            RESOLUTION_TIME,
            INITIAL_LIQUIDITY,
            100
        );

        vm.warp(RESOLUTION_TIME + 1);
        vm.prank(oracle);
        predictions.resolveMarket(marketId, 1);

        vm.warp(RESOLUTION_TIME + 2 days); // After dispute period

        vm.prank(bob);
        vm.expectRevert("Dispute period ended");
        predictions.raiseDispute(marketId, "Too late");
    }

    // ============ Liquidity Tests ============

    function test_AddLiquidity() public {
        vm.prank(alice);
        uint256 marketId = predictions.createMarket(
            "Test Market",
            RESOLUTION_TIME,
            INITIAL_LIQUIDITY,
            100
        );

        (,,,, uint256 liquidityBefore,,,) = predictions.getMarket(marketId);

        vm.prank(bob);
        predictions.addLiquidity(marketId, 5000e18);

        (,,,, uint256 liquidityAfter,,,) = predictions.getMarket(marketId);
        assertEq(liquidityAfter, liquidityBefore + 5000e18);
    }

    // ============ Admin Tests ============

    function test_SetAuthorizedOracle() public {
        address newOracle = makeAddr("newOracle");

        predictions.setAuthorizedOracle(newOracle, true);
        assertTrue(predictions.authorizedOracles(newOracle));

        predictions.setAuthorizedOracle(newOracle, false);
        assertFalse(predictions.authorizedOracles(newOracle));
    }

    function test_SetPlatformFee() public {
        predictions.setPlatformFee(200);
        assertEq(predictions.platformFee(), 200);
    }

    function test_RevertWhen_SetPlatformFee_TooHigh() public {
        vm.expectRevert("Fee too high");
        predictions.setPlatformFee(600);
    }

    function test_SetMinLiquidity() public {
        predictions.setMinLiquidity(500e18);
        assertEq(predictions.minLiquidity(), 500e18);
    }

    function test_SetDisputeBond() public {
        predictions.setDisputeBond(100e18);
        assertEq(predictions.disputeBond(), 100e18);
    }

    function test_SetDisputePeriod() public {
        predictions.setDisputePeriod(2 days);
        assertEq(predictions.disputePeriod(), 2 days);
    }

    // ============ View Functions Tests ============

    function test_GetPosition() public {
        vm.prank(alice);
        uint256 marketId = predictions.createMarket(
            "Test Market",
            RESOLUTION_TIME,
            INITIAL_LIQUIDITY,
            100
        );

        vm.startPrank(bob);
        predictions.buyShares(marketId, true, 100e18, 1000e18);
        predictions.buyShares(marketId, false, 50e18, 1000e18);
        vm.stopPrank();

        (uint256 yes, uint256 no, uint256 cost) = predictions.getPosition(marketId, bob);
        assertEq(yes, 100e18);
        assertEq(no, 50e18);
        assertGt(cost, 0);
    }

    function test_CalculatePotentialPayout() public {
        vm.prank(alice);
        uint256 marketId = predictions.createMarket(
            "Test Market",
            RESOLUTION_TIME,
            INITIAL_LIQUIDITY,
            100
        );

        vm.prank(bob);
        predictions.buyShares(marketId, true, 100e18, 1000e18);

        uint256 yesPayout = predictions.calculatePotentialPayout(marketId, bob, 1);
        uint256 noPayout = predictions.calculatePotentialPayout(marketId, bob, 0);

        assertEq(yesPayout, 100e18);
        assertEq(noPayout, 0);
    }

    // ============ Fuzz Tests ============

    function testFuzz_BuyShares(uint256 shares) public {
        shares = bound(shares, 1e18, 1000e18);

        vm.prank(alice);
        uint256 marketId = predictions.createMarket(
            "Test Market",
            RESOLUTION_TIME,
            INITIAL_LIQUIDITY,
            100
        );

        uint256 cost = predictions.calculateBuyCost(marketId, true, shares);

        vm.prank(bob);
        predictions.buyShares(marketId, true, shares, cost * 2);

        (uint256 yesShares,,) = predictions.getPosition(marketId, bob);
        assertEq(yesShares, shares);
    }

    function testFuzz_ProbabilityRange(uint256 yesAmount, uint256 noAmount) public {
        yesAmount = bound(yesAmount, 1e18, 1000e18);
        noAmount = bound(noAmount, 1e18, 1000e18);

        vm.prank(alice);
        uint256 marketId = predictions.createMarket(
            "Test Market",
            RESOLUTION_TIME,
            INITIAL_LIQUIDITY,
            100
        );

        vm.prank(bob);
        predictions.buyShares(marketId, true, yesAmount, 100000e18);

        vm.prank(charlie);
        predictions.buyShares(marketId, false, noAmount, 100000e18);

        uint256 prob = predictions.getProbability(marketId);

        // Probability should always be between 0 and 1
        assertGe(prob, 0);
        assertLe(prob, 1e18);
    }

    // ============ Integration Tests ============

    function test_FullMarketLifecycle() public {
        // 1. Create market
        vm.prank(alice);
        uint256 marketId = predictions.createMarket(
            "Will Ireland win Six Nations 2025?",
            RESOLUTION_TIME,
            INITIAL_LIQUIDITY,
            100
        );

        // 2. Users trade
        vm.prank(bob);
        predictions.buyShares(marketId, true, 200e18, 5000e18);

        vm.prank(charlie);
        predictions.buyShares(marketId, false, 300e18, 5000e18);

        // 3. Check probability shifted
        uint256 prob = predictions.getProbability(marketId);
        assertLt(prob, 0.5e18); // More NO shares

        // 4. Time passes, resolve market
        vm.warp(RESOLUTION_TIME + 1);
        vm.prank(oracle);
        predictions.resolveMarket(marketId, 1); // Ireland wins!

        // 5. Wait for dispute period
        vm.warp(RESOLUTION_TIME + 2 days);

        // 6. Winners claim
        uint256 bobBefore = usdc.balanceOf(bob);
        vm.prank(bob);
        predictions.claimWinnings(marketId);
        assertGt(usdc.balanceOf(bob), bobBefore);

        // 7. Losers get nothing
        vm.prank(charlie);
        vm.expectRevert(CelticPredictions.InsufficientShares.selector);
        predictions.claimWinnings(marketId);
    }

    function test_DisputeResolutionFlow() public {
        vm.prank(alice);
        uint256 marketId = predictions.createMarket(
            "Test Market",
            RESOLUTION_TIME,
            INITIAL_LIQUIDITY,
            100
        );

        // Buy shares
        vm.prank(bob);
        predictions.buyShares(marketId, true, 100e18, 1000e18);

        vm.prank(charlie);
        predictions.buyShares(marketId, false, 100e18, 1000e18);

        // Resolve incorrectly
        vm.warp(RESOLUTION_TIME + 1);
        vm.prank(oracle);
        predictions.resolveMarket(marketId, 1);

        // Charlie disputes
        uint256 charlieBefore = usdc.balanceOf(charlie);
        vm.prank(charlie);
        predictions.raiseDispute(marketId, "Should be NO - evidence shows otherwise");

        // Owner accepts dispute
        predictions.resolveDispute(marketId, true, 0);

        // Charlie gets bond back
        assertEq(usdc.balanceOf(charlie), charlieBefore);

        // Wait and claim
        vm.warp(RESOLUTION_TIME + 2 days);

        vm.prank(charlie);
        predictions.claimWinnings(marketId);
    }
}
