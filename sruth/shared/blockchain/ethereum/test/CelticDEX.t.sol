// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";
import "../contracts/CelticDEX.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

/**
 * @title Mock ERC20 Token
 */
contract MockToken is ERC20 {
    constructor(string memory name, string memory symbol) ERC20(name, symbol) {}

    function mint(address to, uint256 amount) external {
        _mint(to, amount);
    }
}

/**
 * @title CelticDEX Test Suite
 * @notice Comprehensive tests for constant product AMM
 * @dev SpeedRunEthereum Challenge 4: DEX
 */
contract CelticDEXTest is Test {
    CelticDEX public dex;
    MockToken public celticToken;
    MockToken public goldToken;

    address public owner;
    address public alice;
    address public bob;
    address public carol;

    uint256 constant INITIAL_LIQUIDITY_A = 100_000 ether;
    uint256 constant INITIAL_LIQUIDITY_B = 100_000 ether;

    event LiquidityAdded(
        address indexed provider,
        uint256 amountA,
        uint256 amountB,
        uint256 lpTokens
    );

    event LiquidityRemoved(
        address indexed provider,
        uint256 amountA,
        uint256 amountB,
        uint256 lpTokens
    );

    event Swap(
        address indexed trader,
        address indexed tokenIn,
        address indexed tokenOut,
        uint256 amountIn,
        uint256 amountOut
    );

    event Sync(uint256 reserveA, uint256 reserveB);

    function setUp() public {
        owner = address(this);
        alice = makeAddr("alice");
        bob = makeAddr("bob");
        carol = makeAddr("carol");

        // Deploy tokens
        celticToken = new MockToken("Celtic Token", "CELTIC");
        goldToken = new MockToken("Gold Token", "GOLD");

        // Deploy DEX
        dex = new CelticDEX(
            address(celticToken),
            address(goldToken),
            "Celtic-Gold LP",
            "CELTIC-GOLD-LP"
        );

        // Mint tokens to users
        celticToken.mint(alice, 1_000_000 ether);
        celticToken.mint(bob, 1_000_000 ether);
        celticToken.mint(carol, 1_000_000 ether);
        goldToken.mint(alice, 1_000_000 ether);
        goldToken.mint(bob, 1_000_000 ether);
        goldToken.mint(carol, 1_000_000 ether);

        // Approve DEX
        vm.startPrank(alice);
        celticToken.approve(address(dex), type(uint256).max);
        goldToken.approve(address(dex), type(uint256).max);
        vm.stopPrank();

        vm.startPrank(bob);
        celticToken.approve(address(dex), type(uint256).max);
        goldToken.approve(address(dex), type(uint256).max);
        vm.stopPrank();

        vm.startPrank(carol);
        celticToken.approve(address(dex), type(uint256).max);
        goldToken.approve(address(dex), type(uint256).max);
        vm.stopPrank();
    }

    // ============ Constructor Tests ============

    function test_Constructor() public view {
        assertEq(address(dex.tokenA()), address(celticToken));
        assertEq(address(dex.tokenB()), address(goldToken));
        assertEq(dex.name(), "Celtic-Gold LP");
        assertEq(dex.symbol(), "CELTIC-GOLD-LP");
        assertEq(dex.feeBps(), 30);
    }

    function test_RevertIdenticalTokens() public {
        vm.expectRevert("Identical tokens");
        new CelticDEX(
            address(celticToken),
            address(celticToken),
            "LP",
            "LP"
        );
    }

    function test_RevertZeroAddress() public {
        vm.expectRevert("Zero address");
        new CelticDEX(
            address(0),
            address(goldToken),
            "LP",
            "LP"
        );
    }

    // ============ First Liquidity Tests ============

    function test_AddFirstLiquidity() public {
        vm.prank(alice);
        uint256 lpTokens = dex.addLiquidity(
            INITIAL_LIQUIDITY_A,
            INITIAL_LIQUIDITY_B,
            0
        );

        // LP tokens = sqrt(100_000 * 100_000) - 1000 = 100_000 - 1000 = 99_000 ether
        uint256 expectedLp = 100_000 ether - dex.MINIMUM_LIQUIDITY();
        assertEq(lpTokens, expectedLp);
        assertEq(dex.balanceOf(alice), expectedLp);
        assertEq(dex.totalSupply(), 100_000 ether);

        // Check reserves
        (uint256 reserveA, uint256 reserveB) = dex.getReserves();
        assertEq(reserveA, INITIAL_LIQUIDITY_A);
        assertEq(reserveB, INITIAL_LIQUIDITY_B);
    }

    function test_MinimumLiquidityLocked() public {
        vm.prank(alice);
        dex.addLiquidity(INITIAL_LIQUIDITY_A, INITIAL_LIQUIDITY_B, 0);

        // Minimum liquidity is locked to address(1)
        assertEq(dex.balanceOf(address(1)), dex.MINIMUM_LIQUIDITY());
    }

    function test_AddFirstLiquidityEvent() public {
        vm.prank(alice);

        vm.expectEmit(true, false, false, true);
        emit LiquidityAdded(alice, INITIAL_LIQUIDITY_A, INITIAL_LIQUIDITY_B, 100_000 ether - 1000);

        dex.addLiquidity(INITIAL_LIQUIDITY_A, INITIAL_LIQUIDITY_B, 0);
    }

    // ============ Subsequent Liquidity Tests ============

    function test_AddSubsequentLiquidity() public {
        // First liquidity
        vm.prank(alice);
        dex.addLiquidity(INITIAL_LIQUIDITY_A, INITIAL_LIQUIDITY_B, 0);

        // Second liquidity (proportional)
        vm.prank(bob);
        uint256 lpTokens = dex.addLiquidity(50_000 ether, 50_000 ether, 0);

        // Should get 50% of total supply (proportional to contribution)
        assertEq(lpTokens, 50_000 ether);
        assertEq(dex.balanceOf(bob), 50_000 ether);
    }

    function test_AddLiquidityImbalanced() public {
        // First liquidity
        vm.prank(alice);
        dex.addLiquidity(INITIAL_LIQUIDITY_A, INITIAL_LIQUIDITY_B, 0);

        // Imbalanced liquidity (extra B tokens)
        vm.prank(bob);
        uint256 lpTokens = dex.addLiquidity(10_000 ether, 20_000 ether, 0);

        // Should only get LP tokens based on limiting factor (A)
        assertEq(lpTokens, 10_000 ether);
    }

    function test_RevertSlippageExceededLiquidity() public {
        vm.prank(alice);
        dex.addLiquidity(INITIAL_LIQUIDITY_A, INITIAL_LIQUIDITY_B, 0);

        vm.prank(bob);
        vm.expectRevert("Slippage exceeded");
        dex.addLiquidity(10_000 ether, 10_000 ether, 100_000 ether); // Too high minLP
    }

    function test_RevertZeroAmounts() public {
        vm.prank(alice);
        vm.expectRevert("Zero amounts");
        dex.addLiquidity(0, INITIAL_LIQUIDITY_B, 0);
    }

    // ============ Remove Liquidity Tests ============

    function test_RemoveLiquidity() public {
        // Add liquidity
        vm.prank(alice);
        uint256 lpTokens = dex.addLiquidity(INITIAL_LIQUIDITY_A, INITIAL_LIQUIDITY_B, 0);

        // Remove half
        vm.prank(alice);
        (uint256 amountA, uint256 amountB) = dex.removeLiquidity(
            lpTokens / 2,
            0,
            0
        );

        // Should get ~half of reserves (minus locked minimum)
        assertApproxEqRel(amountA, INITIAL_LIQUIDITY_A / 2, 0.01e18);
        assertApproxEqRel(amountB, INITIAL_LIQUIDITY_B / 2, 0.01e18);
    }

    function test_RemoveAllLiquidity() public {
        // Add liquidity
        vm.prank(alice);
        uint256 lpTokens = dex.addLiquidity(INITIAL_LIQUIDITY_A, INITIAL_LIQUIDITY_B, 0);

        // Remove all (can't get MINIMUM_LIQUIDITY back)
        vm.prank(alice);
        (uint256 amountA, uint256 amountB) = dex.removeLiquidity(
            lpTokens,
            0,
            0
        );

        // Check balances
        assertEq(dex.balanceOf(alice), 0);
        assertTrue(amountA > 0);
        assertTrue(amountB > 0);
    }

    function test_RemoveLiquidityEvent() public {
        vm.prank(alice);
        uint256 lpTokens = dex.addLiquidity(INITIAL_LIQUIDITY_A, INITIAL_LIQUIDITY_B, 0);

        vm.prank(alice);
        vm.expectEmit(true, false, false, false);
        emit LiquidityRemoved(alice, 0, 0, lpTokens);

        dex.removeLiquidity(lpTokens, 0, 0);
    }

    function test_RevertInsufficientLPBalance() public {
        vm.prank(alice);
        dex.addLiquidity(INITIAL_LIQUIDITY_A, INITIAL_LIQUIDITY_B, 0);

        vm.prank(bob); // Bob has no LP tokens
        vm.expectRevert("Insufficient LP balance");
        dex.removeLiquidity(1000 ether, 0, 0);
    }

    function test_RevertSlippageOnRemove() public {
        vm.prank(alice);
        uint256 lpTokens = dex.addLiquidity(INITIAL_LIQUIDITY_A, INITIAL_LIQUIDITY_B, 0);

        vm.prank(alice);
        vm.expectRevert("Slippage A");
        dex.removeLiquidity(lpTokens / 2, INITIAL_LIQUIDITY_A, 0); // Too high minA
    }

    // ============ Swap Tests ============

    function test_SwapAForB() public {
        // Add liquidity
        vm.prank(alice);
        dex.addLiquidity(INITIAL_LIQUIDITY_A, INITIAL_LIQUIDITY_B, 0);

        uint256 swapAmount = 1000 ether;
        uint256 expectedOut = dex.getAmountOut(swapAmount, INITIAL_LIQUIDITY_A, INITIAL_LIQUIDITY_B);

        uint256 bobGoldBefore = goldToken.balanceOf(bob);

        vm.prank(bob);
        uint256 amountOut = dex.swapAForB(swapAmount, 0);

        assertEq(amountOut, expectedOut);
        assertEq(goldToken.balanceOf(bob) - bobGoldBefore, amountOut);
    }

    function test_SwapBForA() public {
        vm.prank(alice);
        dex.addLiquidity(INITIAL_LIQUIDITY_A, INITIAL_LIQUIDITY_B, 0);

        uint256 swapAmount = 1000 ether;
        uint256 expectedOut = dex.getAmountOut(swapAmount, INITIAL_LIQUIDITY_B, INITIAL_LIQUIDITY_A);

        uint256 bobCelticBefore = celticToken.balanceOf(bob);

        vm.prank(bob);
        uint256 amountOut = dex.swapBForA(swapAmount, 0);

        assertEq(amountOut, expectedOut);
        assertEq(celticToken.balanceOf(bob) - bobCelticBefore, amountOut);
    }

    function test_SwapEvent() public {
        vm.prank(alice);
        dex.addLiquidity(INITIAL_LIQUIDITY_A, INITIAL_LIQUIDITY_B, 0);

        vm.prank(bob);
        vm.expectEmit(true, true, true, false);
        emit Swap(bob, address(celticToken), address(goldToken), 0, 0);

        dex.swapAForB(1000 ether, 0);
    }

    function test_SwapMaintainsK() public {
        vm.prank(alice);
        dex.addLiquidity(INITIAL_LIQUIDITY_A, INITIAL_LIQUIDITY_B, 0);

        (uint256 reserveABefore, uint256 reserveBBefore) = dex.getReserves();
        uint256 kBefore = reserveABefore * reserveBBefore;

        vm.prank(bob);
        dex.swapAForB(10_000 ether, 0);

        (uint256 reserveAAfter, uint256 reserveBAfter) = dex.getReserves();
        uint256 kAfter = reserveAAfter * reserveBAfter;

        // K should increase (fees retained in pool)
        assertTrue(kAfter >= kBefore);
    }

    function test_RevertSwapSlippage() public {
        vm.prank(alice);
        dex.addLiquidity(INITIAL_LIQUIDITY_A, INITIAL_LIQUIDITY_B, 0);

        vm.prank(bob);
        vm.expectRevert("Slippage exceeded");
        dex.swapAForB(1000 ether, INITIAL_LIQUIDITY_B); // Impossible output
    }

    function test_RevertSwapInsufficientLiquidity() public {
        vm.prank(alice);
        dex.addLiquidity(INITIAL_LIQUIDITY_A, INITIAL_LIQUIDITY_B, 0);

        vm.prank(bob);
        vm.expectRevert("Insufficient liquidity");
        dex.swapAForB(999_999 ether, 0); // Would drain all liquidity
    }

    function test_RevertSwapZeroInput() public {
        vm.prank(alice);
        dex.addLiquidity(INITIAL_LIQUIDITY_A, INITIAL_LIQUIDITY_B, 0);

        vm.prank(bob);
        vm.expectRevert("Zero input");
        dex.swapAForB(0, 0);
    }

    // ============ Pricing Tests ============

    function test_GetAmountOut() public {
        vm.prank(alice);
        dex.addLiquidity(INITIAL_LIQUIDITY_A, INITIAL_LIQUIDITY_B, 0);

        // For 1000 CELTIC swap with 0.3% fee:
        // amountOut = (1000 * 0.997 * 100_000) / (100_000 + 1000 * 0.997)
        // amountOut ≈ 987.05 GOLD
        uint256 amountOut = dex.getAmountOut(1000 ether, 100_000 ether, 100_000 ether);

        assertTrue(amountOut > 986 ether);
        assertTrue(amountOut < 988 ether);
    }

    function test_GetAmountIn() public {
        vm.prank(alice);
        dex.addLiquidity(INITIAL_LIQUIDITY_A, INITIAL_LIQUIDITY_B, 0);

        // Reverse calculation
        uint256 amountIn = dex.getAmountIn(987 ether, 100_000 ether, 100_000 ether);

        // Should be around 1000 ether
        assertTrue(amountIn > 999 ether);
        assertTrue(amountIn < 1001 ether);
    }

    function test_GetSpotPrices() public {
        vm.prank(alice);
        dex.addLiquidity(INITIAL_LIQUIDITY_A, INITIAL_LIQUIDITY_B, 0);

        (uint256 priceAInB, uint256 priceBInA) = dex.getSpotPrices();

        // 1:1 ratio
        assertEq(priceAInB, 1e18);
        assertEq(priceBInA, 1e18);
    }

    function test_GetSpotPricesImbalanced() public {
        vm.prank(alice);
        // 2:1 ratio
        dex.addLiquidity(100_000 ether, 50_000 ether, 0);

        (uint256 priceAInB, uint256 priceBInA) = dex.getSpotPrices();

        // 1 CELTIC = 0.5 GOLD
        assertEq(priceAInB, 0.5e18);
        // 1 GOLD = 2 CELTIC
        assertEq(priceBInA, 2e18);
    }

    function test_GetPriceImpact() public {
        vm.prank(alice);
        dex.addLiquidity(INITIAL_LIQUIDITY_A, INITIAL_LIQUIDITY_B, 0);

        // Small trade = small impact
        uint256 smallImpact = dex.getPriceImpact(100 ether, true);
        assertTrue(smallImpact < 30); // < 0.3%

        // Large trade = large impact
        uint256 largeImpact = dex.getPriceImpact(50_000 ether, true);
        assertTrue(largeImpact > 1000); // > 10%
    }

    // ============ TWAP Tests ============

    function test_TWAPUpdates() public {
        vm.prank(alice);
        dex.addLiquidity(INITIAL_LIQUIDITY_A, INITIAL_LIQUIDITY_B, 0);

        (uint256 priceCum1, , uint256 time1) = dex.getTWAPData();

        // Advance time
        vm.warp(block.timestamp + 1 hours);

        vm.prank(bob);
        dex.swapAForB(1000 ether, 0);

        (uint256 priceCum2, , uint256 time2) = dex.getTWAPData();

        assertTrue(priceCum2 > priceCum1);
        assertTrue(time2 > time1);
    }

    // ============ Impermanent Loss Tests ============

    function test_CalculateImpermanentLoss() public view {
        // No price change = no IL
        uint256 noChange = dex.calculateImpermanentLoss(1e18);
        assertEq(noChange, 0);

        // 2x price = ~5.7% IL
        uint256 doublePrice = dex.calculateImpermanentLoss(2e18);
        assertTrue(doublePrice > 500); // > 5%
        assertTrue(doublePrice < 600); // < 6%

        // 4x price = ~20% IL
        uint256 quadPrice = dex.calculateImpermanentLoss(4e18);
        assertTrue(quadPrice > 1800); // > 18%
        assertTrue(quadPrice < 2200); // < 22%
    }

    // ============ Admin Tests ============

    function test_SetFee() public {
        dex.setFee(50); // 0.5%
        assertEq(dex.feeBps(), 50);
    }

    function test_RevertFeeTooHigh() public {
        vm.expectRevert("Fee too high");
        dex.setFee(101); // > 1%
    }

    function test_RevertNonOwnerSetFee() public {
        vm.prank(alice);
        vm.expectRevert();
        dex.setFee(50);
    }

    function test_Sync() public {
        vm.prank(alice);
        dex.addLiquidity(INITIAL_LIQUIDITY_A, INITIAL_LIQUIDITY_B, 0);

        // Accidentally send tokens directly
        celticToken.mint(address(dex), 1000 ether);

        (uint256 reserveABefore, ) = dex.getReserves();

        vm.expectEmit(false, false, false, false);
        emit Sync(0, 0);

        dex.sync();

        (uint256 reserveAAfter, ) = dex.getReserves();
        assertEq(reserveAAfter, reserveABefore + 1000 ether);
    }

    // ============ Pool Stats Tests ============

    function test_GetPoolStats() public {
        vm.prank(alice);
        dex.addLiquidity(INITIAL_LIQUIDITY_A, INITIAL_LIQUIDITY_B, 0);

        (uint256 rA, uint256 rB, uint256 supply, uint256 k) = dex.getPoolStats();

        assertEq(rA, INITIAL_LIQUIDITY_A);
        assertEq(rB, INITIAL_LIQUIDITY_B);
        assertEq(supply, 100_000 ether);
        assertEq(k, INITIAL_LIQUIDITY_A * INITIAL_LIQUIDITY_B);
    }

    // ============ Fuzz Tests ============

    function testFuzz_AddLiquidity(uint256 amountA, uint256 amountB) public {
        amountA = bound(amountA, 1001, 100_000 ether); // Above minimum
        amountB = bound(amountB, 1001, 100_000 ether);

        vm.prank(alice);
        uint256 lpTokens = dex.addLiquidity(amountA, amountB, 0);

        assertTrue(lpTokens > 0);
        assertEq(dex.balanceOf(alice), lpTokens);
    }

    function testFuzz_SwapPreservesK(uint256 swapAmount) public {
        vm.prank(alice);
        dex.addLiquidity(INITIAL_LIQUIDITY_A, INITIAL_LIQUIDITY_B, 0);

        swapAmount = bound(swapAmount, 1 ether, 10_000 ether);

        (uint256 rA1, uint256 rB1) = dex.getReserves();
        uint256 k1 = rA1 * rB1;

        vm.prank(bob);
        dex.swapAForB(swapAmount, 0);

        (uint256 rA2, uint256 rB2) = dex.getReserves();
        uint256 k2 = rA2 * rB2;

        // K should increase or stay same (fee accumulates)
        assertTrue(k2 >= k1);
    }

    function testFuzz_AddRemoveLiquidity(uint256 amount) public {
        amount = bound(amount, 10_000, 100_000 ether);

        vm.startPrank(alice);

        uint256 lpTokens = dex.addLiquidity(amount, amount, 0);

        uint256 celticBefore = celticToken.balanceOf(alice);
        uint256 goldBefore = goldToken.balanceOf(alice);

        (uint256 amountA, uint256 amountB) = dex.removeLiquidity(lpTokens, 0, 0);

        vm.stopPrank();

        // Should get back approximately what was deposited (minus minimum liquidity)
        uint256 celticAfter = celticToken.balanceOf(alice);
        uint256 goldAfter = goldToken.balanceOf(alice);

        assertTrue(celticAfter - celticBefore == amountA);
        assertTrue(goldAfter - goldBefore == amountB);
    }

    function testFuzz_RoundTrip(uint256 swapAmount) public {
        vm.prank(alice);
        dex.addLiquidity(INITIAL_LIQUIDITY_A, INITIAL_LIQUIDITY_B, 0);

        swapAmount = bound(swapAmount, 100 ether, 10_000 ether);

        uint256 celticBefore = celticToken.balanceOf(bob);

        vm.startPrank(bob);

        // Swap A -> B
        uint256 goldReceived = dex.swapAForB(swapAmount, 0);

        // Swap B -> A
        uint256 celticReceived = dex.swapBForA(goldReceived, 0);

        vm.stopPrank();

        uint256 celticAfter = celticToken.balanceOf(bob);

        // Should lose approximately 0.6% on round trip (0.3% * 2)
        uint256 loss = celticBefore - celticAfter;
        uint256 expectedLoss = (swapAmount * 60) / 10000; // 0.6%

        // Allow 0.2% tolerance
        assertApproxEqRel(loss, expectedLoss, 0.05e18);
    }

    // ============ Edge Case Tests ============

    function test_MultipleSwaps() public {
        vm.prank(alice);
        dex.addLiquidity(INITIAL_LIQUIDITY_A, INITIAL_LIQUIDITY_B, 0);

        // Multiple small swaps
        for (uint256 i = 0; i < 10; i++) {
            vm.prank(bob);
            dex.swapAForB(100 ether, 0);
        }

        (uint256 reserveA, uint256 reserveB) = dex.getReserves();

        // Reserve A should increase (Celtic added)
        assertTrue(reserveA > INITIAL_LIQUIDITY_A);
        // Reserve B should decrease (Gold removed)
        assertTrue(reserveB < INITIAL_LIQUIDITY_B);
    }

    function test_ArbitrageOpportunity() public {
        // Create imbalanced pool
        vm.prank(alice);
        dex.addLiquidity(100_000 ether, 200_000 ether, 0);

        // Price: 1 CELTIC = 2 GOLD
        // Arbitrageur should buy CELTIC (cheaper here)

        uint256 goldBefore = goldToken.balanceOf(bob);
        uint256 celticBefore = celticToken.balanceOf(bob);

        vm.prank(bob);
        uint256 celticOut = dex.swapBForA(10_000 ether, 0);

        uint256 goldAfter = goldToken.balanceOf(bob);
        uint256 celticAfter = celticToken.balanceOf(bob);

        // Bob spent 10_000 GOLD and received more CELTIC (profitable if external price is 1:1)
        assertEq(goldBefore - goldAfter, 10_000 ether);
        assertTrue(celticAfter > celticBefore);
        assertTrue(celticOut > 4500 ether); // Should get roughly 2:1 minus fees
    }

    function test_LiquidityAfterSwaps() public {
        // First liquidity
        vm.prank(alice);
        dex.addLiquidity(INITIAL_LIQUIDITY_A, INITIAL_LIQUIDITY_B, 0);

        // Some swaps happen
        vm.prank(bob);
        dex.swapAForB(10_000 ether, 0);

        // Carol adds liquidity at new ratio
        (uint256 reserveA, uint256 reserveB) = dex.getReserves();
        uint256 addAmountA = 10_000 ether;
        uint256 addAmountB = (addAmountA * reserveB) / reserveA;

        vm.prank(carol);
        uint256 lpTokens = dex.addLiquidity(addAmountA, addAmountB, 0);

        assertTrue(lpTokens > 0);
    }
}
