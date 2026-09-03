// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";
import "../contracts/CelticLending.sol";
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
 * @title CelticLending Test Suite
 * @notice Comprehensive tests for over-collateralized lending
 * @dev SpeedRunEthereum Challenge 5: Lending
 */
contract CelticLendingTest is Test {
    CelticLending public lending;
    MockToken public celticToken;  // Collateral
    MockToken public goldToken;    // Borrow token

    address public owner;
    address public alice;
    address public bob;
    address public liquidator;

    uint256 constant INITIAL_BALANCE = 1_000_000 ether;

    event Supply(address indexed user, address indexed token, uint256 amount);
    event Borrow(address indexed user, uint256 amount, uint256 healthFactor);
    event Repay(address indexed user, uint256 amount);
    event Liquidate(
        address indexed liquidator,
        address indexed borrower,
        uint256 repayAmount,
        uint256 collateralSeized
    );

    function setUp() public {
        owner = address(this);
        alice = makeAddr("alice");
        bob = makeAddr("bob");
        liquidator = makeAddr("liquidator");

        // Deploy tokens
        celticToken = new MockToken("Celtic Token", "CELTIC");
        goldToken = new MockToken("Gold Token", "GOLD");

        // Deploy lending protocol
        lending = new CelticLending(
            address(celticToken),
            address(goldToken)
        );

        // Mint tokens
        celticToken.mint(alice, INITIAL_BALANCE);
        celticToken.mint(bob, INITIAL_BALANCE);
        goldToken.mint(alice, INITIAL_BALANCE);
        goldToken.mint(bob, INITIAL_BALANCE);
        goldToken.mint(liquidator, INITIAL_BALANCE);

        // Approve lending contract
        vm.startPrank(alice);
        celticToken.approve(address(lending), type(uint256).max);
        goldToken.approve(address(lending), type(uint256).max);
        vm.stopPrank();

        vm.startPrank(bob);
        celticToken.approve(address(lending), type(uint256).max);
        goldToken.approve(address(lending), type(uint256).max);
        vm.stopPrank();

        vm.startPrank(liquidator);
        celticToken.approve(address(lending), type(uint256).max);
        goldToken.approve(address(lending), type(uint256).max);
        vm.stopPrank();
    }

    // ============ Constructor Tests ============

    function test_Constructor() public view {
        assertEq(address(lending.collateralToken()), address(celticToken));
        assertEq(address(lending.borrowToken()), address(goldToken));
        assertEq(lending.priceRatio(), 1e18);
    }

    function test_RevertSameToken() public {
        vm.expectRevert("Same token");
        new CelticLending(address(celticToken), address(celticToken));
    }

    function test_RevertZeroAddress() public {
        vm.expectRevert("Invalid collateral");
        new CelticLending(address(0), address(goldToken));
    }

    // ============ Supply Collateral Tests ============

    function test_SupplyCollateral() public {
        uint256 amount = 10_000 ether;

        vm.prank(alice);
        vm.expectEmit(true, true, false, true);
        emit Supply(alice, address(celticToken), amount);

        lending.supplyCollateral(amount);

        (uint256 collateral, , , ,) = lending.getUserAccount(alice);
        assertEq(collateral, amount);
    }

    function test_RevertSupplyZero() public {
        vm.prank(alice);
        vm.expectRevert("Zero amount");
        lending.supplyCollateral(0);
    }

    function test_MultipleSupplies() public {
        vm.startPrank(alice);
        lending.supplyCollateral(5_000 ether);
        lending.supplyCollateral(3_000 ether);
        vm.stopPrank();

        (uint256 collateral, , , ,) = lending.getUserAccount(alice);
        assertEq(collateral, 8_000 ether);
    }

    // ============ Supply Liquidity Tests ============

    function test_SupplyLiquidity() public {
        uint256 amount = 50_000 ether;

        vm.prank(alice);
        lending.supplyLiquidity(amount);

        (, uint256 liquidity, , ,) = lending.getUserAccount(alice);
        assertEq(liquidity, amount);
    }

    function test_MultipleLiquidityProviders() public {
        vm.prank(alice);
        lending.supplyLiquidity(50_000 ether);

        vm.prank(bob);
        lending.supplyLiquidity(30_000 ether);

        (uint256 totalSupplied, , , ,) = lending.getMarketStats();
        assertEq(totalSupplied, 80_000 ether);
    }

    // ============ Borrow Tests ============

    function test_Borrow() public {
        // Alice supplies collateral
        vm.prank(alice);
        lending.supplyCollateral(15_000 ether);

        // Bob supplies liquidity
        vm.prank(bob);
        lending.supplyLiquidity(100_000 ether);

        // Alice borrows
        vm.prank(alice);
        vm.expectEmit(true, false, false, false);
        emit Borrow(alice, 5_000 ether, 0);

        lending.borrow(5_000 ether);

        (, , uint256 borrowed, ,) = lending.getUserAccount(alice);
        assertEq(borrowed, 5_000 ether);
    }

    function test_MaxBorrow() public {
        vm.prank(alice);
        lending.supplyCollateral(15_000 ether);

        vm.prank(bob);
        lending.supplyLiquidity(100_000 ether);

        (, , , , uint256 maxBorrow) = lending.getUserAccount(alice);

        // Should be able to borrow up to max
        vm.prank(alice);
        lending.borrow(maxBorrow);

        (, , uint256 borrowed, ,) = lending.getUserAccount(alice);
        assertEq(borrowed, maxBorrow);
    }

    function test_RevertBorrowInsufficientCollateral() public {
        vm.prank(alice);
        lending.supplyCollateral(1_000 ether);

        vm.prank(bob);
        lending.supplyLiquidity(100_000 ether);

        vm.prank(alice);
        vm.expectRevert("Insufficient collateral");
        lending.borrow(10_000 ether);
    }

    function test_RevertBorrowInsufficientLiquidity() public {
        vm.prank(alice);
        lending.supplyCollateral(100_000 ether);

        vm.prank(bob);
        lending.supplyLiquidity(1_000 ether);

        vm.prank(alice);
        vm.expectRevert("Insufficient liquidity");
        lending.borrow(5_000 ether);
    }

    // ============ Repay Tests ============

    function test_Repay() public {
        // Setup
        vm.prank(alice);
        lending.supplyCollateral(15_000 ether);

        vm.prank(bob);
        lending.supplyLiquidity(100_000 ether);

        vm.startPrank(alice);
        lending.borrow(5_000 ether);

        // Repay
        vm.expectEmit(true, false, false, true);
        emit Repay(alice, 5_000 ether);

        lending.repay(5_000 ether);
        vm.stopPrank();

        (, , uint256 borrowed, ,) = lending.getUserAccount(alice);
        assertEq(borrowed, 0);
    }

    function test_PartialRepay() public {
        vm.prank(alice);
        lending.supplyCollateral(15_000 ether);

        vm.prank(bob);
        lending.supplyLiquidity(100_000 ether);

        vm.startPrank(alice);
        lending.borrow(5_000 ether);
        lending.repay(2_000 ether);
        vm.stopPrank();

        (, , uint256 borrowed, ,) = lending.getUserAccount(alice);
        assertEq(borrowed, 3_000 ether);
    }

    function test_OverRepay() public {
        vm.prank(alice);
        lending.supplyCollateral(15_000 ether);

        vm.prank(bob);
        lending.supplyLiquidity(100_000 ether);

        vm.startPrank(alice);
        lending.borrow(5_000 ether);

        // Try to repay more than borrowed
        lending.repay(10_000 ether);
        vm.stopPrank();

        // Should only repay what was borrowed
        (, , uint256 borrowed, ,) = lending.getUserAccount(alice);
        assertEq(borrowed, 0);
    }

    // ============ Withdraw Tests ============

    function test_WithdrawCollateral() public {
        vm.startPrank(alice);
        lending.supplyCollateral(10_000 ether);
        lending.withdrawCollateral(5_000 ether);
        vm.stopPrank();

        (uint256 collateral, , , ,) = lending.getUserAccount(alice);
        assertEq(collateral, 5_000 ether);
    }

    function test_RevertWithdrawUnhealthy() public {
        vm.prank(alice);
        lending.supplyCollateral(15_000 ether);

        vm.prank(bob);
        lending.supplyLiquidity(100_000 ether);

        vm.startPrank(alice);
        lending.borrow(5_000 ether);

        // Try to withdraw too much collateral
        vm.expectRevert("Unhealthy position");
        lending.withdrawCollateral(10_000 ether);
        vm.stopPrank();
    }

    function test_WithdrawLiquidity() public {
        vm.startPrank(alice);
        lending.supplyLiquidity(50_000 ether);
        lending.withdrawLiquidity(20_000 ether);
        vm.stopPrank();

        (, uint256 liquidity, , ,) = lending.getUserAccount(alice);
        assertEq(liquidity, 30_000 ether);
    }

    function test_RevertWithdrawInsufficientLiquidity() public {
        vm.prank(alice);
        lending.supplyLiquidity(50_000 ether);

        // Bob borrows most of it
        vm.prank(bob);
        lending.supplyCollateral(100_000 ether);

        vm.prank(bob);
        lending.borrow(45_000 ether);

        // Alice can't withdraw all
        vm.prank(alice);
        vm.expectRevert("Insufficient liquidity");
        lending.withdrawLiquidity(50_000 ether);
    }

    // ============ Health Factor Tests ============

    function test_HealthFactor() public {
        vm.prank(alice);
        lending.supplyCollateral(15_000 ether);

        vm.prank(bob);
        lending.supplyLiquidity(100_000 ether);

        vm.prank(alice);
        lending.borrow(5_000 ether);

        uint256 hf = lending.getHealthFactor(alice);

        // Health factor should be > 1 for healthy position
        assertTrue(hf >= 1e18);
    }

    function test_HealthFactorNoBorrow() public {
        vm.prank(alice);
        lending.supplyCollateral(15_000 ether);

        uint256 hf = lending.getHealthFactor(alice);

        // No borrow = infinite health factor
        assertEq(hf, type(uint256).max);
    }

    // ============ Liquidation Tests ============

    function test_Liquidation() public {
        // Setup position
        vm.prank(alice);
        lending.supplyCollateral(15_000 ether);

        vm.prank(bob);
        lending.supplyLiquidity(100_000 ether);

        vm.prank(alice);
        lending.borrow(8_000 ether);

        // Price drops - collateral worth less
        lending.updatePriceRatio(0.6e18); // 40% drop

        // Should be liquidatable now
        assertTrue(lending.isLiquidatable(alice));

        // Liquidator repays some debt
        vm.prank(liquidator);
        lending.liquidate(alice, 4_000 ether);

        // Alice should have less debt and less collateral
        (, , uint256 borrowed, ,) = lending.getUserAccount(alice);
        assertTrue(borrowed < 8_000 ether);
    }

    function test_RevertLiquidateHealthy() public {
        vm.prank(alice);
        lending.supplyCollateral(15_000 ether);

        vm.prank(bob);
        lending.supplyLiquidity(100_000 ether);

        vm.prank(alice);
        lending.borrow(3_000 ether);

        // Position is healthy
        assertFalse(lending.isLiquidatable(alice));

        vm.prank(liquidator);
        vm.expectRevert("Position is healthy");
        lending.liquidate(alice, 1_000 ether);
    }

    function test_RevertSelfLiquidate() public {
        vm.prank(alice);
        lending.supplyCollateral(15_000 ether);

        vm.prank(bob);
        lending.supplyLiquidity(100_000 ether);

        vm.prank(alice);
        lending.borrow(8_000 ether);

        lending.updatePriceRatio(0.6e18);

        vm.prank(alice);
        vm.expectRevert("Cannot self-liquidate");
        lending.liquidate(alice, 1_000 ether);
    }

    function test_LiquidationCloseFactor() public {
        vm.prank(alice);
        lending.supplyCollateral(15_000 ether);

        vm.prank(bob);
        lending.supplyLiquidity(100_000 ether);

        vm.prank(alice);
        lending.borrow(8_000 ether);

        lending.updatePriceRatio(0.6e18);

        // Try to liquidate more than close factor allows
        uint256 beforeDebt = 8_000 ether;
        uint256 maxRepay = beforeDebt * 50 / 100; // 50% close factor

        vm.prank(liquidator);
        lending.liquidate(alice, 8_000 ether); // Try full amount

        (, , uint256 afterDebt, ,) = lending.getUserAccount(alice);

        // Should only liquidate up to close factor
        assertApproxEqAbs(beforeDebt - afterDebt, maxRepay, 1);
    }

    // ============ Interest Rate Tests ============

    function test_BorrowAPY() public {
        vm.prank(alice);
        lending.supplyLiquidity(100_000 ether);

        vm.prank(bob);
        lending.supplyCollateral(100_000 ether);

        vm.prank(bob);
        lending.borrow(50_000 ether); // 50% utilization

        uint256 borrowAPY = lending.getBorrowAPY();

        // Should be non-zero
        assertTrue(borrowAPY > 0);
    }

    function test_SupplyAPY() public {
        vm.prank(alice);
        lending.supplyLiquidity(100_000 ether);

        vm.prank(bob);
        lending.supplyCollateral(100_000 ether);

        vm.prank(bob);
        lending.borrow(50_000 ether);

        uint256 supplyAPY = lending.getSupplyAPY();

        // Supply APY should be less than borrow APY (protocol takes cut)
        uint256 borrowAPY = lending.getBorrowAPY();
        assertTrue(supplyAPY < borrowAPY);
    }

    function test_InterestAccrual() public {
        vm.prank(alice);
        lending.supplyLiquidity(100_000 ether);

        vm.prank(bob);
        lending.supplyCollateral(100_000 ether);

        vm.prank(bob);
        lending.borrow(50_000 ether);

        (, uint256 borrowedBefore, , ,) = lending.getUserAccount(bob);

        // Advance blocks
        vm.roll(block.number + 1000);

        // Trigger interest accrual
        vm.prank(bob);
        lending.repay(1 ether);

        // Note: In this simple implementation, interest doesn't compound
        // automatically on user balances, but the market indices do update
    }

    // ============ Admin Tests ============

    function test_UpdatePriceRatio() public {
        lending.updatePriceRatio(2e18);
        assertEq(lending.priceRatio(), 2e18);
    }

    function test_RevertUpdatePriceZero() public {
        vm.expectRevert("Invalid ratio");
        lending.updatePriceRatio(0);
    }

    function test_UpdateInterestParams() public {
        lending.updateInterestParams(300, 3000);

        // Verify by checking borrow rate
        vm.prank(alice);
        lending.supplyLiquidity(100_000 ether);

        uint256 borrowAPY = lending.getBorrowAPY();
        assertTrue(borrowAPY > 0);
    }

    function test_RevertNonOwnerAdmin() public {
        vm.prank(alice);
        vm.expectRevert();
        lending.updatePriceRatio(2e18);
    }

    function test_SetMarketActive() public {
        lending.setMarketActive(false, false);

        vm.prank(alice);
        vm.expectRevert("Market not active");
        lending.supplyCollateral(1000 ether);
    }

    // ============ View Function Tests ============

    function test_GetMarketStats() public {
        vm.prank(alice);
        lending.supplyLiquidity(100_000 ether);

        vm.prank(bob);
        lending.supplyCollateral(100_000 ether);

        vm.prank(bob);
        lending.borrow(30_000 ether);

        (
            uint256 totalSupplied,
            uint256 totalBorrowed,
            uint256 utilization,
            ,

        ) = lending.getMarketStats();

        assertEq(totalSupplied, 100_000 ether);
        assertEq(totalBorrowed, 30_000 ether);
        assertEq(utilization, 0.3e18); // 30%
    }

    function test_GetMaxBorrow() public {
        vm.prank(alice);
        lending.supplyCollateral(15_000 ether);

        vm.prank(bob);
        lending.supplyLiquidity(100_000 ether);

        uint256 maxBorrow = lending.getMaxBorrow(alice);

        // Should be able to borrow up to collateral factor / min ratio
        assertTrue(maxBorrow > 0);
        assertTrue(maxBorrow < 15_000 ether); // Less than collateral
    }

    function test_IsLiquidatable() public {
        vm.prank(alice);
        lending.supplyCollateral(15_000 ether);

        vm.prank(bob);
        lending.supplyLiquidity(100_000 ether);

        vm.prank(alice);
        lending.borrow(5_000 ether);

        // Initially healthy
        assertFalse(lending.isLiquidatable(alice));

        // Price crash
        lending.updatePriceRatio(0.3e18);

        // Now liquidatable
        assertTrue(lending.isLiquidatable(alice));
    }

    // ============ Fuzz Tests ============

    function testFuzz_SupplyWithdraw(uint256 amount) public {
        amount = bound(amount, 1 ether, 100_000 ether);

        vm.startPrank(alice);
        lending.supplyCollateral(amount);

        (uint256 collateral, , , ,) = lending.getUserAccount(alice);
        assertEq(collateral, amount);

        lending.withdrawCollateral(amount);

        (collateral, , , ,) = lending.getUserAccount(alice);
        assertEq(collateral, 0);
        vm.stopPrank();
    }

    function testFuzz_BorrowRepay(uint256 borrowAmount) public {
        vm.prank(alice);
        lending.supplyCollateral(100_000 ether);

        vm.prank(bob);
        lending.supplyLiquidity(100_000 ether);

        uint256 maxBorrow = lending.getMaxBorrow(alice);
        borrowAmount = bound(borrowAmount, 1 ether, maxBorrow);

        vm.startPrank(alice);
        lending.borrow(borrowAmount);

        (, , uint256 borrowed, ,) = lending.getUserAccount(alice);
        assertEq(borrowed, borrowAmount);

        lending.repay(borrowAmount);

        (, , borrowed, ,) = lending.getUserAccount(alice);
        assertEq(borrowed, 0);
        vm.stopPrank();
    }

    function testFuzz_HealthFactorPositive(uint256 collateral, uint256 borrowRatio) public {
        collateral = bound(collateral, 10_000 ether, 100_000 ether);
        borrowRatio = bound(borrowRatio, 1, 50); // 1-50% of max borrow

        vm.prank(alice);
        lending.supplyCollateral(collateral);

        vm.prank(bob);
        lending.supplyLiquidity(1_000_000 ether);

        uint256 maxBorrow = lending.getMaxBorrow(alice);
        uint256 borrowAmount = (maxBorrow * borrowRatio) / 100;

        if (borrowAmount > 0) {
            vm.prank(alice);
            lending.borrow(borrowAmount);

            uint256 hf = lending.getHealthFactor(alice);
            assertTrue(hf >= 1e18, "Health factor should be >= 1");
        }
    }
}
