// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/math/Math.sol";

/**
 * @title CelticLending
 * @author Cianfhoghlaim / crypteolas project
 * @notice Over-collateralized lending protocol for Celtic tokens
 * @dev SpeedRunEthereum Challenge 5: Lending
 *
 * Features:
 * - Over-collateralized borrowing (150% collateral ratio)
 * - Interest rate model (utilization-based)
 * - Liquidation mechanism with incentives
 * - Oracle price feeds for collateral valuation
 * - Health factor monitoring
 *
 * Tuath Integration:
 * - XP as reputation collateral
 * - Guild loan guarantees
 * - Skill/item lending for quests
 */
contract CelticLending is Ownable, ReentrancyGuard {
    using SafeERC20 for IERC20;
    using Math for uint256;

    // ============================================================================
    // Types
    // ============================================================================

    struct Market {
        IERC20 token;
        uint256 totalSupplied;       // Total tokens supplied to market
        uint256 totalBorrowed;       // Total tokens borrowed
        uint256 supplyIndex;         // Accumulated interest for suppliers
        uint256 borrowIndex;         // Accumulated interest for borrowers
        uint256 lastAccrualBlock;    // Last block interest was accrued
        uint256 baseRateBps;         // Base interest rate (in basis points)
        uint256 multiplierBps;       // Interest rate multiplier
        bool isActive;               // Market active status
    }

    struct UserAccount {
        uint256 supplied;            // User's supply balance
        uint256 borrowed;            // User's borrow balance
        uint256 supplyPrincipal;     // Principal supplied
        uint256 borrowPrincipal;     // Principal borrowed
    }

    struct LiquidationParams {
        uint256 closeFactor;         // Max % of debt liquidatable (in bps)
        uint256 liquidationIncentive; // Bonus for liquidators (in bps)
        uint256 collateralFactor;    // Collateral value factor (in bps)
    }

    // ============================================================================
    // State Variables
    // ============================================================================

    /// @notice Collateral token (e.g., CELTIC)
    IERC20 public immutable collateralToken;

    /// @notice Borrow token (e.g., GOLD)
    IERC20 public immutable borrowToken;

    /// @notice Collateral market data
    Market public collateralMarket;

    /// @notice Borrow market data
    Market public borrowMarket;

    /// @notice User accounts for collateral
    mapping(address => UserAccount) public collateralAccounts;

    /// @notice User accounts for borrowing
    mapping(address => UserAccount) public borrowAccounts;

    /// @notice Liquidation parameters
    LiquidationParams public liquidationParams;

    /// @notice Price oracle (simplified: fixed price ratio)
    uint256 public priceRatio = 1e18; // 1 collateral = 1 borrow token

    /// @notice Minimum collateral ratio (150% = 15000 bps)
    uint256 public constant MIN_COLLATERAL_RATIO_BPS = 15000;

    /// @notice Blocks per year (for interest calculations)
    uint256 public constant BLOCKS_PER_YEAR = 2_628_000; // ~12s blocks

    /// @notice Scale for interest calculations
    uint256 public constant SCALE = 1e18;

    // ============================================================================
    // Events
    // ============================================================================

    event Supply(address indexed user, address indexed token, uint256 amount);
    event Withdraw(address indexed user, address indexed token, uint256 amount);
    event Borrow(address indexed user, uint256 amount, uint256 healthFactor);
    event Repay(address indexed user, uint256 amount);
    event Liquidate(
        address indexed liquidator,
        address indexed borrower,
        uint256 repayAmount,
        uint256 collateralSeized
    );
    event InterestAccrued(
        address indexed token,
        uint256 interestAccumulated,
        uint256 newIndex
    );
    event PriceUpdated(uint256 newPriceRatio);

    // ============================================================================
    // Constructor
    // ============================================================================

    constructor(
        address _collateralToken,
        address _borrowToken
    ) Ownable(msg.sender) {
        require(_collateralToken != address(0), "Invalid collateral");
        require(_borrowToken != address(0), "Invalid borrow token");
        require(_collateralToken != _borrowToken, "Same token");

        collateralToken = IERC20(_collateralToken);
        borrowToken = IERC20(_borrowToken);

        // Initialize collateral market
        collateralMarket = Market({
            token: IERC20(_collateralToken),
            totalSupplied: 0,
            totalBorrowed: 0,
            supplyIndex: SCALE,
            borrowIndex: SCALE,
            lastAccrualBlock: block.number,
            baseRateBps: 0,      // No interest on collateral
            multiplierBps: 0,
            isActive: true
        });

        // Initialize borrow market
        borrowMarket = Market({
            token: IERC20(_borrowToken),
            totalSupplied: 0,
            totalBorrowed: 0,
            supplyIndex: SCALE,
            borrowIndex: SCALE,
            lastAccrualBlock: block.number,
            baseRateBps: 200,    // 2% base rate
            multiplierBps: 2000, // 20% at 100% utilization
            isActive: true
        });

        // Initialize liquidation params
        liquidationParams = LiquidationParams({
            closeFactor: 5000,           // 50% max liquidation
            liquidationIncentive: 1000,  // 10% bonus
            collateralFactor: 8000       // 80% collateral value
        });
    }

    // ============================================================================
    // Supply Functions
    // ============================================================================

    /**
     * @notice Supply collateral to the protocol
     * @param amount Amount of collateral to supply
     */
    function supplyCollateral(uint256 amount) external nonReentrant {
        require(amount > 0, "Zero amount");
        require(collateralMarket.isActive, "Market not active");

        // Transfer collateral
        collateralToken.safeTransferFrom(msg.sender, address(this), amount);

        // Update user account
        collateralAccounts[msg.sender].supplied += amount;
        collateralAccounts[msg.sender].supplyPrincipal += amount;

        // Update market
        collateralMarket.totalSupplied += amount;

        emit Supply(msg.sender, address(collateralToken), amount);
    }

    /**
     * @notice Supply liquidity to the borrow pool (lenders)
     * @param amount Amount to supply for lending
     */
    function supplyLiquidity(uint256 amount) external nonReentrant {
        require(amount > 0, "Zero amount");
        require(borrowMarket.isActive, "Market not active");

        // Accrue interest first
        _accrueInterest();

        // Transfer tokens
        borrowToken.safeTransferFrom(msg.sender, address(this), amount);

        // Update user account with current index
        borrowAccounts[msg.sender].supplied += amount;
        borrowAccounts[msg.sender].supplyPrincipal += amount;

        // Update market
        borrowMarket.totalSupplied += amount;

        emit Supply(msg.sender, address(borrowToken), amount);
    }

    /**
     * @notice Withdraw collateral (if health factor allows)
     * @param amount Amount to withdraw
     */
    function withdrawCollateral(uint256 amount) external nonReentrant {
        require(amount > 0, "Zero amount");
        require(collateralAccounts[msg.sender].supplied >= amount, "Insufficient balance");

        // Check if withdrawal would maintain health factor
        uint256 newCollateral = collateralAccounts[msg.sender].supplied - amount;
        uint256 borrowed = borrowAccounts[msg.sender].borrowed;

        if (borrowed > 0) {
            uint256 newHealthFactor = _calculateHealthFactor(newCollateral, borrowed);
            require(newHealthFactor >= SCALE, "Unhealthy position");
        }

        // Update balances
        collateralAccounts[msg.sender].supplied -= amount;
        collateralMarket.totalSupplied -= amount;

        // Transfer
        collateralToken.safeTransfer(msg.sender, amount);

        emit Withdraw(msg.sender, address(collateralToken), amount);
    }

    /**
     * @notice Withdraw supplied liquidity
     * @param amount Amount to withdraw
     */
    function withdrawLiquidity(uint256 amount) external nonReentrant {
        require(amount > 0, "Zero amount");

        _accrueInterest();

        uint256 available = borrowMarket.totalSupplied - borrowMarket.totalBorrowed;
        require(amount <= available, "Insufficient liquidity");
        require(borrowAccounts[msg.sender].supplied >= amount, "Insufficient balance");

        // Update balances
        borrowAccounts[msg.sender].supplied -= amount;
        borrowMarket.totalSupplied -= amount;

        // Transfer
        borrowToken.safeTransfer(msg.sender, amount);

        emit Withdraw(msg.sender, address(borrowToken), amount);
    }

    // ============================================================================
    // Borrow Functions
    // ============================================================================

    /**
     * @notice Borrow tokens against collateral
     * @param amount Amount to borrow
     */
    function borrow(uint256 amount) external nonReentrant {
        require(amount > 0, "Zero amount");
        require(borrowMarket.isActive, "Market not active");

        _accrueInterest();

        // Check liquidity
        uint256 available = borrowMarket.totalSupplied - borrowMarket.totalBorrowed;
        require(amount <= available, "Insufficient liquidity");

        // Check collateral
        uint256 collateral = collateralAccounts[msg.sender].supplied;
        uint256 newBorrowed = borrowAccounts[msg.sender].borrowed + amount;

        uint256 healthFactor = _calculateHealthFactor(collateral, newBorrowed);
        require(healthFactor >= SCALE, "Insufficient collateral");

        // Update borrow account
        borrowAccounts[msg.sender].borrowed = newBorrowed;
        borrowAccounts[msg.sender].borrowPrincipal += amount;
        borrowMarket.totalBorrowed += amount;

        // Transfer
        borrowToken.safeTransfer(msg.sender, amount);

        emit Borrow(msg.sender, amount, healthFactor);
    }

    /**
     * @notice Repay borrowed tokens
     * @param amount Amount to repay
     */
    function repay(uint256 amount) external nonReentrant {
        require(amount > 0, "Zero amount");

        _accrueInterest();

        uint256 borrowed = borrowAccounts[msg.sender].borrowed;
        uint256 repayAmount = amount > borrowed ? borrowed : amount;

        // Transfer repayment
        borrowToken.safeTransferFrom(msg.sender, address(this), repayAmount);

        // Update balances
        borrowAccounts[msg.sender].borrowed -= repayAmount;
        borrowMarket.totalBorrowed -= repayAmount;

        emit Repay(msg.sender, repayAmount);
    }

    // ============================================================================
    // Liquidation Functions
    // ============================================================================

    /**
     * @notice Liquidate an unhealthy position
     * @param borrower Address of the borrower to liquidate
     * @param repayAmount Amount of debt to repay
     */
    function liquidate(
        address borrower,
        uint256 repayAmount
    ) external nonReentrant {
        require(borrower != msg.sender, "Cannot self-liquidate");
        require(repayAmount > 0, "Zero repay amount");

        _accrueInterest();

        // Check if position is liquidatable
        uint256 collateral = collateralAccounts[borrower].supplied;
        uint256 borrowed = borrowAccounts[borrower].borrowed;
        uint256 healthFactor = _calculateHealthFactor(collateral, borrowed);

        require(healthFactor < SCALE, "Position is healthy");

        // Limit repay amount to close factor
        uint256 maxRepay = (borrowed * liquidationParams.closeFactor) / 10000;
        repayAmount = repayAmount > maxRepay ? maxRepay : repayAmount;
        repayAmount = repayAmount > borrowed ? borrowed : repayAmount;

        // Calculate collateral to seize (with incentive)
        uint256 collateralToSeize = _calculateSeizeAmount(repayAmount);
        require(collateralToSeize <= collateral, "Insufficient collateral to seize");

        // Transfer repayment from liquidator
        borrowToken.safeTransferFrom(msg.sender, address(this), repayAmount);

        // Update borrower's balances
        borrowAccounts[borrower].borrowed -= repayAmount;
        borrowMarket.totalBorrowed -= repayAmount;
        collateralAccounts[borrower].supplied -= collateralToSeize;
        collateralMarket.totalSupplied -= collateralToSeize;

        // Transfer seized collateral to liquidator
        collateralToken.safeTransfer(msg.sender, collateralToSeize);

        emit Liquidate(msg.sender, borrower, repayAmount, collateralToSeize);
    }

    // ============================================================================
    // Interest Functions
    // ============================================================================

    /**
     * @notice Accrue interest on the borrow market
     */
    function _accrueInterest() internal {
        uint256 blockDelta = block.number - borrowMarket.lastAccrualBlock;
        if (blockDelta == 0) return;

        uint256 utilization = _getUtilization();
        uint256 borrowRate = _getBorrowRate(utilization);

        // Calculate interest accumulated
        uint256 interestFactor = (borrowRate * blockDelta) / BLOCKS_PER_YEAR;
        uint256 interestAccumulated = (borrowMarket.totalBorrowed * interestFactor) / SCALE;

        // Update indices
        if (borrowMarket.totalBorrowed > 0) {
            borrowMarket.borrowIndex += (interestFactor * borrowMarket.borrowIndex) / SCALE;
        }
        if (borrowMarket.totalSupplied > 0) {
            uint256 supplyInterest = (interestAccumulated * SCALE) / borrowMarket.totalSupplied;
            borrowMarket.supplyIndex += supplyInterest;
        }

        // Add interest to totals
        borrowMarket.totalBorrowed += interestAccumulated;
        borrowMarket.lastAccrualBlock = block.number;

        emit InterestAccrued(address(borrowToken), interestAccumulated, borrowMarket.borrowIndex);
    }

    /**
     * @notice Get current utilization rate
     * @return utilization Utilization in scale (0 to SCALE)
     */
    function _getUtilization() internal view returns (uint256) {
        if (borrowMarket.totalSupplied == 0) return 0;
        return (borrowMarket.totalBorrowed * SCALE) / borrowMarket.totalSupplied;
    }

    /**
     * @notice Calculate borrow rate based on utilization
     * @param utilization Current utilization rate
     * @return rate Borrow rate per block (scaled)
     */
    function _getBorrowRate(uint256 utilization) internal view returns (uint256) {
        // Linear rate: baseRate + (multiplier * utilization)
        uint256 baseRate = (borrowMarket.baseRateBps * SCALE) / 10000;
        uint256 multiplierRate = (borrowMarket.multiplierBps * utilization) / 10000;
        return baseRate + multiplierRate;
    }

    // ============================================================================
    // Health Factor Functions
    // ============================================================================

    /**
     * @notice Calculate health factor for a position
     * @param collateralAmount Collateral balance
     * @param borrowAmount Borrow balance
     * @return healthFactor Health factor (>= SCALE is healthy)
     */
    function _calculateHealthFactor(
        uint256 collateralAmount,
        uint256 borrowAmount
    ) internal view returns (uint256) {
        if (borrowAmount == 0) return type(uint256).max;

        // Collateral value in borrow token terms
        uint256 collateralValue = (collateralAmount * priceRatio) / SCALE;

        // Apply collateral factor
        uint256 adjustedCollateral = (collateralValue * liquidationParams.collateralFactor) / 10000;

        // Required collateral at min ratio
        uint256 requiredCollateral = (borrowAmount * MIN_COLLATERAL_RATIO_BPS) / 10000;

        // Health factor = adjusted collateral / required collateral
        return (adjustedCollateral * SCALE) / requiredCollateral;
    }

    /**
     * @notice Calculate collateral to seize during liquidation
     * @param repayAmount Amount being repaid
     * @return seizeAmount Collateral to seize
     */
    function _calculateSeizeAmount(uint256 repayAmount) internal view returns (uint256) {
        // Convert repay amount to collateral terms
        uint256 collateralValue = (repayAmount * SCALE) / priceRatio;

        // Add liquidation incentive
        uint256 incentive = (collateralValue * liquidationParams.liquidationIncentive) / 10000;

        return collateralValue + incentive;
    }

    // ============================================================================
    // View Functions
    // ============================================================================

    /**
     * @notice Get user's health factor
     * @param user User address
     * @return healthFactor Current health factor
     */
    function getHealthFactor(address user) external view returns (uint256) {
        return _calculateHealthFactor(
            collateralAccounts[user].supplied,
            borrowAccounts[user].borrowed
        );
    }

    /**
     * @notice Get maximum borrowable amount for user
     * @param user User address
     * @return maxBorrow Maximum additional amount user can borrow
     */
    function getMaxBorrow(address user) external view returns (uint256) {
        uint256 collateral = collateralAccounts[user].supplied;
        uint256 currentBorrow = borrowAccounts[user].borrowed;

        // Collateral value adjusted by collateral factor
        uint256 collateralValue = (collateral * priceRatio) / SCALE;
        uint256 adjustedCollateral = (collateralValue * liquidationParams.collateralFactor) / 10000;

        // Max borrow at minimum ratio
        uint256 maxTotalBorrow = (adjustedCollateral * 10000) / MIN_COLLATERAL_RATIO_BPS;

        if (maxTotalBorrow <= currentBorrow) return 0;
        return maxTotalBorrow - currentBorrow;
    }

    /**
     * @notice Get current borrow APY
     * @return apy Annual percentage yield (scaled by SCALE)
     */
    function getBorrowAPY() external view returns (uint256) {
        uint256 utilization = _getUtilization();
        uint256 ratePerBlock = _getBorrowRate(utilization);
        return ratePerBlock * BLOCKS_PER_YEAR;
    }

    /**
     * @notice Get current supply APY
     * @return apy Annual percentage yield (scaled by SCALE)
     */
    function getSupplyAPY() external view returns (uint256) {
        uint256 utilization = _getUtilization();
        if (utilization == 0) return 0;

        uint256 borrowRate = _getBorrowRate(utilization);
        // Supply APY = borrow rate * utilization (since suppliers share interest)
        return (borrowRate * utilization * BLOCKS_PER_YEAR) / SCALE;
    }

    /**
     * @notice Get market stats
     */
    function getMarketStats() external view returns (
        uint256 totalSupplied,
        uint256 totalBorrowed,
        uint256 utilization,
        uint256 borrowRate,
        uint256 supplyRate
    ) {
        totalSupplied = borrowMarket.totalSupplied;
        totalBorrowed = borrowMarket.totalBorrowed;
        utilization = _getUtilization();
        borrowRate = _getBorrowRate(utilization);
        supplyRate = totalSupplied > 0 ? (borrowRate * utilization) / SCALE : 0;
    }

    /**
     * @notice Get user account summary
     * @param user User address
     */
    function getUserAccount(address user) external view returns (
        uint256 collateralSupplied,
        uint256 liquiditySupplied,
        uint256 borrowed,
        uint256 healthFactor,
        uint256 maxBorrow
    ) {
        collateralSupplied = collateralAccounts[user].supplied;
        liquiditySupplied = borrowAccounts[user].supplied;
        borrowed = borrowAccounts[user].borrowed;
        healthFactor = _calculateHealthFactor(collateralSupplied, borrowed);

        // Calculate max borrow
        uint256 collateralValue = (collateralSupplied * priceRatio) / SCALE;
        uint256 adjustedCollateral = (collateralValue * liquidationParams.collateralFactor) / 10000;
        uint256 maxTotal = (adjustedCollateral * 10000) / MIN_COLLATERAL_RATIO_BPS;
        maxBorrow = maxTotal > borrowed ? maxTotal - borrowed : 0;
    }

    /**
     * @notice Check if a position can be liquidated
     * @param user User address
     */
    function isLiquidatable(address user) external view returns (bool) {
        uint256 healthFactor = _calculateHealthFactor(
            collateralAccounts[user].supplied,
            borrowAccounts[user].borrowed
        );
        return healthFactor < SCALE;
    }

    // ============================================================================
    // Admin Functions
    // ============================================================================

    /**
     * @notice Update price ratio (simplified oracle)
     * @param newRatio New price ratio (collateral per borrow token)
     */
    function updatePriceRatio(uint256 newRatio) external onlyOwner {
        require(newRatio > 0, "Invalid ratio");
        priceRatio = newRatio;
        emit PriceUpdated(newRatio);
    }

    /**
     * @notice Update interest rate parameters
     * @param baseRateBps New base rate in basis points
     * @param multiplierBps New multiplier in basis points
     */
    function updateInterestParams(
        uint256 baseRateBps,
        uint256 multiplierBps
    ) external onlyOwner {
        require(baseRateBps <= 5000, "Base rate too high");
        require(multiplierBps <= 10000, "Multiplier too high");

        _accrueInterest();

        borrowMarket.baseRateBps = baseRateBps;
        borrowMarket.multiplierBps = multiplierBps;
    }

    /**
     * @notice Update liquidation parameters
     * @param closeFactor New close factor in bps
     * @param liquidationIncentive New incentive in bps
     * @param collateralFactor New collateral factor in bps
     */
    function updateLiquidationParams(
        uint256 closeFactor,
        uint256 liquidationIncentive,
        uint256 collateralFactor
    ) external onlyOwner {
        require(closeFactor <= 10000, "Invalid close factor");
        require(liquidationIncentive <= 2000, "Incentive too high");
        require(collateralFactor <= 10000, "Invalid collateral factor");

        liquidationParams.closeFactor = closeFactor;
        liquidationParams.liquidationIncentive = liquidationIncentive;
        liquidationParams.collateralFactor = collateralFactor;
    }

    /**
     * @notice Pause/unpause markets
     */
    function setMarketActive(bool collateralActive, bool borrowActive) external onlyOwner {
        collateralMarket.isActive = collateralActive;
        borrowMarket.isActive = borrowActive;
    }
}
