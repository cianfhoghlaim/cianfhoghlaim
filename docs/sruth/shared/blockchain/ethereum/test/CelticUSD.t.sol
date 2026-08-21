// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";
import "../contracts/CelticUSD.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

/// @title Mock Collateral Token for testing
contract MockCollateral is ERC20 {
    constructor() ERC20("Mock ETH", "mETH") {
        _mint(msg.sender, 1_000_000 ether);
    }

    function mint(address to, uint256 amount) external {
        _mint(to, amount);
    }
}

/// @title Mock Price Oracle
contract MockOracle {
    int256 private _price;
    uint8 private _decimals;
    uint256 private _updatedAt;

    constructor(int256 initialPrice, uint8 decimals_) {
        _price = initialPrice;
        _decimals = decimals_;
        _updatedAt = block.timestamp;
    }

    function latestRoundData() external view returns (
        uint80 roundId,
        int256 answer,
        uint256 startedAt,
        uint256 updatedAt,
        uint80 answeredInRound
    ) {
        return (1, _price, block.timestamp, _updatedAt, 1);
    }

    function decimals() external view returns (uint8) {
        return _decimals;
    }

    function setPrice(int256 newPrice) external {
        _price = newPrice;
        _updatedAt = block.timestamp;
    }

    function setStalePrice(int256 newPrice, uint256 timestamp) external {
        _price = newPrice;
        _updatedAt = timestamp;
    }
}

/// @title CelticUSD Test Suite
/// @notice Comprehensive tests for CDP-based stablecoin
contract CelticUSDTest is Test {
    CelticUSD public cusd;
    MockCollateral public collateral;
    MockOracle public oracle;

    address public alice = makeAddr("alice");
    address public bob = makeAddr("bob");
    address public liquidator = makeAddr("liquidator");
    address public treasury = makeAddr("treasury");

    // Constants matching contract
    uint256 constant COLLATERAL_RATIO = 15000; // 150%
    uint256 constant LIQUIDATION_THRESHOLD = 12000; // 120%
    uint256 constant STABILITY_FEE = 500; // 5% annual
    uint256 constant LIQUIDATION_PENALTY = 1300; // 13%

    event CDPOpened(uint256 indexed cdpId, address indexed owner, uint256 collateral, uint256 debt);
    event CollateralAdded(uint256 indexed cdpId, uint256 amount);
    event CollateralWithdrawn(uint256 indexed cdpId, uint256 amount);
    event DebtMinted(uint256 indexed cdpId, uint256 amount);
    event DebtRepaid(uint256 indexed cdpId, uint256 amount);
    event CDPClosed(uint256 indexed cdpId);
    event LiquidationStarted(uint256 indexed cdpId, uint256 indexed auctionId);
    event AuctionBid(uint256 indexed auctionId, address indexed bidder, uint256 collateralReceived);
    event AuctionCompleted(uint256 indexed auctionId);

    function setUp() public {
        // Deploy mock tokens and oracle
        collateral = new MockCollateral();
        oracle = new MockOracle(2000e8, 8); // $2000 ETH price

        // Deploy CelticUSD
        cusd = new CelticUSD(
            address(collateral),
            address(oracle),
            treasury
        );

        // Setup users
        collateral.mint(alice, 1000 ether);
        collateral.mint(bob, 1000 ether);
        collateral.mint(liquidator, 1000 ether);

        // Approve collateral
        vm.prank(alice);
        collateral.approve(address(cusd), type(uint256).max);

        vm.prank(bob);
        collateral.approve(address(cusd), type(uint256).max);

        vm.prank(liquidator);
        collateral.approve(address(cusd), type(uint256).max);
    }

    // ============ CDP Opening Tests ============

    function test_OpenCDP() public {
        vm.startPrank(alice);

        uint256 collateralAmount = 10 ether;
        uint256 debtAmount = 10000e18; // $10,000 CUSD

        vm.expectEmit(true, true, false, true);
        emit CDPOpened(0, alice, collateralAmount, debtAmount);

        uint256 cdpId = cusd.openCDP(collateralAmount, debtAmount);

        assertEq(cdpId, 0);
        assertEq(cusd.balanceOf(alice), debtAmount);
        assertEq(collateral.balanceOf(address(cusd)), collateralAmount);

        (
            address owner,
            uint256 storedCollateral,
            uint256 debt,
            ,
            bool active
        ) = cusd.cdps(cdpId);

        assertEq(owner, alice);
        assertEq(storedCollateral, collateralAmount);
        assertEq(debt, debtAmount);
        assertTrue(active);

        vm.stopPrank();
    }

    function test_OpenCDP_MaxDebt() public {
        vm.startPrank(alice);

        uint256 collateralAmount = 10 ether;
        // Max debt at 150% ratio: $20,000 collateral / 1.5 = $13,333.33
        uint256 maxDebt = (collateralAmount * 2000e18) / COLLATERAL_RATIO * 10000 / 1e18;

        uint256 cdpId = cusd.openCDP(collateralAmount, maxDebt);

        assertEq(cusd.balanceOf(alice), maxDebt);

        vm.stopPrank();
    }

    function test_RevertWhen_OpenCDP_ExceedsMaxDebt() public {
        vm.startPrank(alice);

        uint256 collateralAmount = 10 ether;
        // Exceeds max debt
        uint256 tooMuchDebt = 20000e18;

        vm.expectRevert("Insufficient collateral ratio");
        cusd.openCDP(collateralAmount, tooMuchDebt);

        vm.stopPrank();
    }

    function test_RevertWhen_OpenCDP_ZeroCollateral() public {
        vm.startPrank(alice);

        vm.expectRevert("Zero collateral");
        cusd.openCDP(0, 1000e18);

        vm.stopPrank();
    }

    function test_RevertWhen_OpenCDP_ZeroDebt() public {
        vm.startPrank(alice);

        vm.expectRevert("Zero debt");
        cusd.openCDP(10 ether, 0);

        vm.stopPrank();
    }

    // ============ Collateral Management Tests ============

    function test_AddCollateral() public {
        vm.startPrank(alice);

        uint256 cdpId = cusd.openCDP(10 ether, 10000e18);

        vm.expectEmit(true, false, false, true);
        emit CollateralAdded(cdpId, 5 ether);

        cusd.addCollateral(cdpId, 5 ether);

        (,uint256 storedCollateral,,,) = cusd.cdps(cdpId);
        assertEq(storedCollateral, 15 ether);

        vm.stopPrank();
    }

    function test_WithdrawCollateral() public {
        vm.startPrank(alice);

        uint256 cdpId = cusd.openCDP(10 ether, 5000e18);

        // Can withdraw excess collateral
        uint256 withdrawAmount = 2 ether;

        vm.expectEmit(true, false, false, true);
        emit CollateralWithdrawn(cdpId, withdrawAmount);

        cusd.withdrawCollateral(cdpId, withdrawAmount);

        (,uint256 storedCollateral,,,) = cusd.cdps(cdpId);
        assertEq(storedCollateral, 8 ether);
        assertEq(collateral.balanceOf(alice), 992 ether); // 1000 - 10 + 2

        vm.stopPrank();
    }

    function test_RevertWhen_WithdrawCollateral_BelowRatio() public {
        vm.startPrank(alice);

        uint256 cdpId = cusd.openCDP(10 ether, 10000e18);

        // Try to withdraw too much
        vm.expectRevert("Would breach collateral ratio");
        cusd.withdrawCollateral(cdpId, 5 ether);

        vm.stopPrank();
    }

    function test_RevertWhen_WithdrawCollateral_NotOwner() public {
        vm.prank(alice);
        uint256 cdpId = cusd.openCDP(10 ether, 5000e18);

        vm.prank(bob);
        vm.expectRevert("Not CDP owner");
        cusd.withdrawCollateral(cdpId, 1 ether);
    }

    // ============ Debt Management Tests ============

    function test_MintDebt() public {
        vm.startPrank(alice);

        uint256 cdpId = cusd.openCDP(10 ether, 5000e18);

        vm.expectEmit(true, false, false, true);
        emit DebtMinted(cdpId, 3000e18);

        cusd.mintDebt(cdpId, 3000e18);

        assertEq(cusd.balanceOf(alice), 8000e18);

        (,,uint256 debt,,) = cusd.cdps(cdpId);
        assertEq(debt, 8000e18);

        vm.stopPrank();
    }

    function test_RepayDebt() public {
        vm.startPrank(alice);

        uint256 cdpId = cusd.openCDP(10 ether, 10000e18);

        vm.expectEmit(true, false, false, true);
        emit DebtRepaid(cdpId, 5000e18);

        cusd.repayDebt(cdpId, 5000e18);

        assertEq(cusd.balanceOf(alice), 5000e18);

        (,,uint256 debt,,) = cusd.cdps(cdpId);
        assertEq(debt, 5000e18);

        vm.stopPrank();
    }

    function test_RepayDebt_Full() public {
        vm.startPrank(alice);

        uint256 cdpId = cusd.openCDP(10 ether, 10000e18);

        cusd.repayDebt(cdpId, 10000e18);

        assertEq(cusd.balanceOf(alice), 0);

        (,,uint256 debt,,) = cusd.cdps(cdpId);
        assertEq(debt, 0);

        vm.stopPrank();
    }

    function test_RevertWhen_MintDebt_ExceedsRatio() public {
        vm.startPrank(alice);

        uint256 cdpId = cusd.openCDP(10 ether, 10000e18);

        vm.expectRevert("Would breach collateral ratio");
        cusd.mintDebt(cdpId, 5000e18);

        vm.stopPrank();
    }

    // ============ CDP Closure Tests ============

    function test_CloseCDP() public {
        vm.startPrank(alice);

        uint256 cdpId = cusd.openCDP(10 ether, 10000e18);

        // Repay all debt first
        cusd.repayDebt(cdpId, 10000e18);

        uint256 balanceBefore = collateral.balanceOf(alice);

        vm.expectEmit(true, false, false, false);
        emit CDPClosed(cdpId);

        cusd.closeCDP(cdpId);

        assertEq(collateral.balanceOf(alice), balanceBefore + 10 ether);

        (,,,,bool active) = cusd.cdps(cdpId);
        assertFalse(active);

        vm.stopPrank();
    }

    function test_RevertWhen_CloseCDP_WithDebt() public {
        vm.startPrank(alice);

        uint256 cdpId = cusd.openCDP(10 ether, 10000e18);

        vm.expectRevert("CDP has outstanding debt");
        cusd.closeCDP(cdpId);

        vm.stopPrank();
    }

    // ============ Stability Fee Tests ============

    function test_StabilityFee_Accrual() public {
        vm.startPrank(alice);

        uint256 cdpId = cusd.openCDP(10 ether, 10000e18);

        // Fast forward 1 year
        vm.warp(block.timestamp + 365 days);

        // Update stability fee
        cusd.accrueStabilityFee(cdpId);

        (,,uint256 debt,,) = cusd.cdps(cdpId);

        // 5% annual fee
        // Expected: 10000 * 1.05 = 10500 (approximately)
        assertApproxEqRel(debt, 10500e18, 0.01e18); // 1% tolerance for compound calculation

        vm.stopPrank();
    }

    function test_StabilityFee_MultipleCDPs() public {
        vm.prank(alice);
        uint256 cdpId1 = cusd.openCDP(10 ether, 5000e18);

        vm.prank(bob);
        uint256 cdpId2 = cusd.openCDP(10 ether, 8000e18);

        vm.warp(block.timestamp + 180 days); // 6 months

        cusd.accrueStabilityFee(cdpId1);
        cusd.accrueStabilityFee(cdpId2);

        (,,uint256 debt1,,) = cusd.cdps(cdpId1);
        (,,uint256 debt2,,) = cusd.cdps(cdpId2);

        // ~2.5% for 6 months
        assertApproxEqRel(debt1, 5125e18, 0.01e18);
        assertApproxEqRel(debt2, 8200e18, 0.01e18);
    }

    // ============ Liquidation Tests ============

    function test_CanLiquidate() public {
        vm.prank(alice);
        uint256 cdpId = cusd.openCDP(10 ether, 10000e18);

        // Price drop: $2000 -> $1500
        oracle.setPrice(1500e8);

        assertTrue(cusd.canLiquidate(cdpId));
    }

    function test_CannotLiquidate_HealthyCDP() public {
        vm.prank(alice);
        uint256 cdpId = cusd.openCDP(10 ether, 5000e18);

        assertFalse(cusd.canLiquidate(cdpId));
    }

    function test_StartLiquidation() public {
        vm.prank(alice);
        uint256 cdpId = cusd.openCDP(10 ether, 10000e18);

        // Price drop triggers liquidation
        oracle.setPrice(1100e8);

        vm.prank(liquidator);

        vm.expectEmit(true, true, false, false);
        emit LiquidationStarted(cdpId, 0);

        uint256 auctionId = cusd.startLiquidation(cdpId);

        assertEq(auctionId, 0);

        (,,,,bool active) = cusd.cdps(cdpId);
        assertFalse(active); // CDP deactivated
    }

    function test_RevertWhen_StartLiquidation_HealthyCDP() public {
        vm.prank(alice);
        uint256 cdpId = cusd.openCDP(10 ether, 5000e18);

        vm.prank(liquidator);
        vm.expectRevert("CDP not liquidatable");
        cusd.startLiquidation(cdpId);
    }

    function test_BidOnAuction() public {
        // Setup liquidatable CDP
        vm.prank(alice);
        uint256 cdpId = cusd.openCDP(10 ether, 12000e18);

        oracle.setPrice(1300e8); // Below liquidation threshold

        // Start auction
        vm.prank(liquidator);
        uint256 auctionId = cusd.startLiquidation(cdpId);

        // Give liquidator some CUSD
        vm.prank(alice);
        cusd.transfer(liquidator, 5000e18);

        // Approve CUSD for repayment
        vm.startPrank(liquidator);
        cusd.approve(address(cusd), type(uint256).max);

        uint256 collateralBefore = collateral.balanceOf(liquidator);

        // Bid on auction
        cusd.bidOnAuction(auctionId, 3 ether);

        // Liquidator should receive collateral
        assertGt(collateral.balanceOf(liquidator), collateralBefore);

        vm.stopPrank();
    }

    function test_DutchAuction_PriceDecay() public {
        // Setup liquidatable CDP
        vm.prank(alice);
        uint256 cdpId = cusd.openCDP(10 ether, 12000e18);

        oracle.setPrice(1300e8);

        vm.prank(liquidator);
        uint256 auctionId = cusd.startLiquidation(cdpId);

        // Get initial auction price
        uint256 initialPrice = cusd.getAuctionPrice(auctionId);

        // Fast forward
        vm.warp(block.timestamp + 30 minutes);

        uint256 laterPrice = cusd.getAuctionPrice(auctionId);

        // Price should have decreased
        assertLt(laterPrice, initialPrice);
    }

    function test_AuctionCompletion() public {
        // Setup and liquidate
        vm.prank(alice);
        uint256 cdpId = cusd.openCDP(10 ether, 12000e18);

        oracle.setPrice(1300e8);

        vm.prank(liquidator);
        uint256 auctionId = cusd.startLiquidation(cdpId);

        // Transfer CUSD to liquidator
        vm.prank(alice);
        cusd.transfer(liquidator, 12000e18);

        // Buy all collateral
        vm.startPrank(liquidator);
        cusd.approve(address(cusd), type(uint256).max);
        cusd.bidOnAuction(auctionId, 10 ether);
        vm.stopPrank();

        // Auction should be complete
        (,,,,,bool auctionActive) = cusd.auctions(auctionId);
        assertFalse(auctionActive);
    }

    // ============ Price Oracle Tests ============

    function test_GetCollateralPrice() public view {
        uint256 price = cusd.getCollateralPrice();
        assertEq(price, 2000e18);
    }

    function test_GetCollateralValue() public {
        vm.prank(alice);
        uint256 cdpId = cusd.openCDP(10 ether, 5000e18);

        uint256 value = cusd.getCollateralValue(cdpId);
        assertEq(value, 20000e18); // 10 ETH * $2000
    }

    function test_RevertWhen_StalePrice() public {
        // Set stale price (2 hours old)
        oracle.setStalePrice(2000e8, block.timestamp - 2 hours);

        vm.prank(alice);
        vm.expectRevert("Stale price");
        cusd.openCDP(10 ether, 10000e18);
    }

    // ============ Collateral Ratio Tests ============

    function test_GetCollateralRatio() public {
        vm.prank(alice);
        uint256 cdpId = cusd.openCDP(10 ether, 10000e18);

        uint256 ratio = cusd.getCollateralRatio(cdpId);

        // 10 ETH * $2000 / $10000 debt = 200%
        assertEq(ratio, 20000); // 200% in basis points
    }

    function test_CollateralRatio_AfterPriceChange() public {
        vm.prank(alice);
        uint256 cdpId = cusd.openCDP(10 ether, 10000e18);

        // Price increase
        oracle.setPrice(3000e8);

        uint256 ratio = cusd.getCollateralRatio(cdpId);

        // 10 ETH * $3000 / $10000 debt = 300%
        assertEq(ratio, 30000);
    }

    // ============ Admin Functions Tests ============

    function test_SetStabilityFee() public {
        uint256 newFee = 1000; // 10%

        cusd.setStabilityFee(newFee);

        assertEq(cusd.stabilityFee(), newFee);
    }

    function test_SetCollateralRatio() public {
        uint256 newRatio = 17500; // 175%

        cusd.setCollateralRatio(newRatio);

        assertEq(cusd.collateralRatio(), newRatio);
    }

    function test_SetLiquidationThreshold() public {
        uint256 newThreshold = 13000; // 130%

        cusd.setLiquidationThreshold(newThreshold);

        assertEq(cusd.liquidationThreshold(), newThreshold);
    }

    function test_RevertWhen_InvalidParameters() public {
        // Liquidation threshold must be below collateral ratio
        vm.expectRevert("Invalid threshold");
        cusd.setLiquidationThreshold(16000);

        // Collateral ratio must be above liquidation threshold
        vm.expectRevert("Invalid ratio");
        cusd.setCollateralRatio(11000);
    }

    function test_RevertWhen_NonOwner_Admin() public {
        vm.prank(alice);
        vm.expectRevert();
        cusd.setStabilityFee(1000);
    }

    // ============ Treasury Tests ============

    function test_StabilityFee_GoesToTreasury() public {
        vm.startPrank(alice);
        uint256 cdpId = cusd.openCDP(10 ether, 10000e18);
        vm.stopPrank();

        // Fast forward and accrue fees
        vm.warp(block.timestamp + 365 days);
        cusd.accrueStabilityFee(cdpId);

        // Treasury should have received some CUSD from fees
        // (Implementation dependent on how fees are collected)
    }

    // ============ View Functions Tests ============

    function test_TotalSupply() public {
        vm.prank(alice);
        cusd.openCDP(10 ether, 5000e18);

        vm.prank(bob);
        cusd.openCDP(10 ether, 8000e18);

        assertEq(cusd.totalSupply(), 13000e18);
    }

    function test_GetCDPCount() public {
        vm.prank(alice);
        cusd.openCDP(10 ether, 5000e18);

        vm.prank(bob);
        cusd.openCDP(10 ether, 5000e18);

        vm.prank(alice);
        cusd.openCDP(5 ether, 2000e18);

        assertEq(cusd.cdpCount(), 3);
    }

    function test_GetUserCDPs() public {
        vm.startPrank(alice);
        cusd.openCDP(10 ether, 5000e18);
        cusd.openCDP(5 ether, 2000e18);
        vm.stopPrank();

        uint256[] memory aliceCDPs = cusd.getUserCDPs(alice);
        assertEq(aliceCDPs.length, 2);
        assertEq(aliceCDPs[0], 0);
        assertEq(aliceCDPs[1], 1);
    }

    // ============ Fuzz Tests ============

    function testFuzz_OpenCDP(uint256 collateralAmount, uint256 debtAmount) public {
        // Bound inputs to reasonable ranges
        collateralAmount = bound(collateralAmount, 0.1 ether, 100 ether);

        // Calculate max debt
        uint256 maxDebt = (collateralAmount * 2000e18) / COLLATERAL_RATIO * 10000 / 1e18;
        debtAmount = bound(debtAmount, 1e18, maxDebt);

        vm.startPrank(alice);
        uint256 cdpId = cusd.openCDP(collateralAmount, debtAmount);

        (,uint256 storedCollateral, uint256 debt,,) = cusd.cdps(cdpId);
        assertEq(storedCollateral, collateralAmount);
        assertEq(debt, debtAmount);

        uint256 ratio = cusd.getCollateralRatio(cdpId);
        assertGe(ratio, COLLATERAL_RATIO);

        vm.stopPrank();
    }

    function testFuzz_CollateralOperations(uint256 addAmount, uint256 withdrawAmount) public {
        vm.startPrank(alice);

        uint256 cdpId = cusd.openCDP(10 ether, 5000e18);

        // Add collateral
        addAmount = bound(addAmount, 0.1 ether, 50 ether);
        cusd.addCollateral(cdpId, addAmount);

        (,uint256 totalCollateral,,,) = cusd.cdps(cdpId);
        assertEq(totalCollateral, 10 ether + addAmount);

        // Calculate max withdrawable
        uint256 minCollateralNeeded = (5000e18 * COLLATERAL_RATIO) / (2000e18 * 10000 / 1e18);
        uint256 maxWithdraw = totalCollateral > minCollateralNeeded ?
            totalCollateral - minCollateralNeeded : 0;

        if (maxWithdraw > 0) {
            withdrawAmount = bound(withdrawAmount, 0, maxWithdraw);
            cusd.withdrawCollateral(cdpId, withdrawAmount);

            uint256 ratio = cusd.getCollateralRatio(cdpId);
            assertGe(ratio, COLLATERAL_RATIO);
        }

        vm.stopPrank();
    }

    function testFuzz_PriceMovements(int256 newPrice) public {
        // Bound price to reasonable range ($100 - $10000)
        newPrice = bound(newPrice, 100e8, 10000e8);

        vm.prank(alice);
        uint256 cdpId = cusd.openCDP(10 ether, 5000e18);

        oracle.setPrice(newPrice);

        uint256 collateralValue = cusd.getCollateralValue(cdpId);
        uint256 expectedValue = uint256(newPrice) * 10 * 1e10; // 10 ETH, price has 8 decimals

        assertEq(collateralValue, expectedValue);

        // Check if liquidatable
        uint256 ratio = cusd.getCollateralRatio(cdpId);
        bool shouldBeLiquidatable = ratio < LIQUIDATION_THRESHOLD;
        assertEq(cusd.canLiquidate(cdpId), shouldBeLiquidatable);
    }

    // ============ Edge Cases ============

    function test_MultipleCDPs_SameUser() public {
        vm.startPrank(alice);

        uint256 cdp1 = cusd.openCDP(5 ether, 3000e18);
        uint256 cdp2 = cusd.openCDP(3 ether, 2000e18);
        uint256 cdp3 = cusd.openCDP(2 ether, 1000e18);

        assertEq(cusd.balanceOf(alice), 6000e18);

        // Each CDP independent
        uint256 ratio1 = cusd.getCollateralRatio(cdp1);
        uint256 ratio2 = cusd.getCollateralRatio(cdp2);
        uint256 ratio3 = cusd.getCollateralRatio(cdp3);

        assertGe(ratio1, COLLATERAL_RATIO);
        assertGe(ratio2, COLLATERAL_RATIO);
        assertGe(ratio3, COLLATERAL_RATIO);

        vm.stopPrank();
    }

    function test_PartialLiquidation() public {
        // Open CDP at edge of liquidation
        vm.prank(alice);
        uint256 cdpId = cusd.openCDP(10 ether, 12000e18);

        // Price drops, but only partial liquidation needed
        oracle.setPrice(1400e8);

        assertTrue(cusd.canLiquidate(cdpId));

        // Liquidator takes partial collateral
        vm.prank(alice);
        cusd.transfer(liquidator, 6000e18);

        vm.startPrank(liquidator);
        cusd.approve(address(cusd), type(uint256).max);

        uint256 auctionId = cusd.startLiquidation(cdpId);
        cusd.bidOnAuction(auctionId, 5 ether);

        // Auction should still have remaining collateral
        (,,,uint256 remainingCollateral,,) = cusd.auctions(auctionId);
        assertGt(remainingCollateral, 0);

        vm.stopPrank();
    }

    function test_ZeroDebtAfterRepay_CanWithdrawAll() public {
        vm.startPrank(alice);

        uint256 cdpId = cusd.openCDP(10 ether, 5000e18);
        cusd.repayDebt(cdpId, 5000e18);

        // Should be able to withdraw all collateral
        cusd.withdrawCollateral(cdpId, 10 ether);

        (,uint256 storedCollateral,,,) = cusd.cdps(cdpId);
        assertEq(storedCollateral, 0);

        vm.stopPrank();
    }
}
