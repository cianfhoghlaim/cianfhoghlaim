// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/math/Math.sol";

/**
 * @title CelticUSD
 * @author Cianfhoghlaim / crypteolas project
 * @notice Education-backed stablecoin using CDP mechanism
 * @dev SpeedRunEthereum Challenge 6: Stablecoins
 *
 * Features:
 * - Collateralized Debt Position (CDP)
 * - Stability fee (interest on minted CUSD)
 * - Liquidation auctions
 * - Peg maintenance via arbitrage incentives
 *
 * Tuath Integration:
 * - Minted by verified learning achievements
 * - Redeemable for educational courses
 * - NCCA curriculum milestone verification
 */
contract CelticUSD is ERC20, Ownable, ReentrancyGuard {
    using SafeERC20 for IERC20;
    using Math for uint256;

    // ============================================================================
    // Types
    // ============================================================================

    struct CDP {
        uint256 collateral;      // Collateral deposited
        uint256 debt;            // CUSD minted
        uint256 lastAccrual;     // Last stability fee accrual
        bool isActive;           // CDP status
    }

    struct LiquidationAuction {
        uint256 cdpId;
        address borrower;
        uint256 collateralForSale;
        uint256 debtToCover;
        uint256 startTime;
        uint256 startPrice;      // Starting price per collateral unit
        uint256 endTime;
        bool isActive;
    }

    // ============================================================================
    // State Variables
    // ============================================================================

    /// @notice Collateral token (e.g., CELTIC, ETH)
    IERC20 public immutable collateralToken;

    /// @notice All CDPs by ID
    mapping(uint256 => CDP) public cdps;

    /// @notice User's CDP IDs
    mapping(address => uint256[]) public userCdps;

    /// @notice CDP counter
    uint256 public cdpCount;

    /// @notice Total collateral locked
    uint256 public totalCollateral;

    /// @notice Total debt (CUSD) minted
    uint256 public totalDebt;

    /// @notice Collateralization ratio (e.g., 15000 = 150%)
    uint256 public collateralRatio = 15000;

    /// @notice Liquidation threshold (e.g., 12000 = 120%)
    uint256 public liquidationThreshold = 12000;

    /// @notice Stability fee (annual, in basis points, e.g., 500 = 5%)
    uint256 public stabilityFeeBps = 500;

    /// @notice Liquidation penalty (e.g., 1300 = 13%)
    uint256 public liquidationPenaltyBps = 1300;

    /// @notice Price oracle (simplified: collateral per USD, scaled by 1e18)
    uint256 public collateralPrice = 1e18; // 1 collateral = $1

    /// @notice Debt ceiling
    uint256 public debtCeiling = 1_000_000 ether;

    /// @notice Active auctions
    mapping(uint256 => LiquidationAuction) public auctions;
    uint256 public auctionCount;

    /// @notice Auction duration
    uint256 public auctionDuration = 6 hours;

    /// @notice Surplus buffer (protocol revenue)
    uint256 public surplusBuffer;

    /// @notice Blocks per year for fee calculation
    uint256 public constant BLOCKS_PER_YEAR = 2_628_000;

    /// @notice Scale factor
    uint256 public constant SCALE = 1e18;

    /// @notice Basis points scale
    uint256 public constant BPS = 10000;

    // ============================================================================
    // Events
    // ============================================================================

    event CDPOpened(uint256 indexed cdpId, address indexed owner, uint256 collateral, uint256 debt);
    event CDPClosed(uint256 indexed cdpId, address indexed owner);
    event CollateralAdded(uint256 indexed cdpId, uint256 amount);
    event CollateralWithdrawn(uint256 indexed cdpId, uint256 amount);
    event DebtMinted(uint256 indexed cdpId, uint256 amount);
    event DebtRepaid(uint256 indexed cdpId, uint256 amount);
    event CDPLiquidated(uint256 indexed cdpId, address indexed liquidator, uint256 collateralSeized, uint256 debtCovered);
    event AuctionStarted(uint256 indexed auctionId, uint256 indexed cdpId, uint256 collateral, uint256 debt);
    event AuctionBid(uint256 indexed auctionId, address indexed bidder, uint256 price, uint256 amount);
    event PriceUpdated(uint256 newPrice);

    // ============================================================================
    // Constructor
    // ============================================================================

    constructor(
        address _collateralToken
    ) ERC20("Celtic USD", "CUSD") Ownable(msg.sender) {
        require(_collateralToken != address(0), "Invalid collateral");
        collateralToken = IERC20(_collateralToken);
    }

    // ============================================================================
    // CDP Management
    // ============================================================================

    /**
     * @notice Open a new CDP
     * @param collateralAmount Collateral to deposit
     * @param debtAmount CUSD to mint
     * @return cdpId The new CDP ID
     */
    function openCDP(
        uint256 collateralAmount,
        uint256 debtAmount
    ) external nonReentrant returns (uint256 cdpId) {
        require(collateralAmount > 0, "Zero collateral");
        require(totalDebt + debtAmount <= debtCeiling, "Debt ceiling reached");

        // Calculate minimum collateral required
        uint256 minCollateral = _getMinCollateral(debtAmount);
        require(collateralAmount >= minCollateral, "Insufficient collateral");

        // Transfer collateral
        collateralToken.safeTransferFrom(msg.sender, address(this), collateralAmount);

        // Create CDP
        cdpId = cdpCount++;
        cdps[cdpId] = CDP({
            collateral: collateralAmount,
            debt: debtAmount,
            lastAccrual: block.number,
            isActive: true
        });

        userCdps[msg.sender].push(cdpId);

        // Update totals
        totalCollateral += collateralAmount;
        totalDebt += debtAmount;

        // Mint CUSD
        _mint(msg.sender, debtAmount);

        emit CDPOpened(cdpId, msg.sender, collateralAmount, debtAmount);
    }

    /**
     * @notice Add collateral to existing CDP
     * @param cdpId CDP to add collateral to
     * @param amount Collateral amount to add
     */
    function addCollateral(uint256 cdpId, uint256 amount) external nonReentrant {
        CDP storage cdp = cdps[cdpId];
        require(cdp.isActive, "CDP not active");
        require(amount > 0, "Zero amount");

        // Accrue stability fee first
        _accrueStabilityFee(cdpId);

        collateralToken.safeTransferFrom(msg.sender, address(this), amount);

        cdp.collateral += amount;
        totalCollateral += amount;

        emit CollateralAdded(cdpId, amount);
    }

    /**
     * @notice Withdraw collateral from CDP (if safe)
     * @param cdpId CDP to withdraw from
     * @param amount Collateral amount to withdraw
     */
    function withdrawCollateral(uint256 cdpId, uint256 amount) external nonReentrant {
        CDP storage cdp = cdps[cdpId];
        require(cdp.isActive, "CDP not active");
        require(amount > 0 && amount <= cdp.collateral, "Invalid amount");

        _accrueStabilityFee(cdpId);

        // Check if withdrawal maintains health
        uint256 newCollateral = cdp.collateral - amount;
        uint256 minRequired = _getMinCollateral(cdp.debt);
        require(newCollateral >= minRequired, "Would be undercollateralized");

        cdp.collateral = newCollateral;
        totalCollateral -= amount;

        collateralToken.safeTransfer(msg.sender, amount);

        emit CollateralWithdrawn(cdpId, amount);
    }

    /**
     * @notice Mint additional CUSD from CDP
     * @param cdpId CDP to mint from
     * @param amount CUSD to mint
     */
    function mintDebt(uint256 cdpId, uint256 amount) external nonReentrant {
        CDP storage cdp = cdps[cdpId];
        require(cdp.isActive, "CDP not active");
        require(amount > 0, "Zero amount");
        require(totalDebt + amount <= debtCeiling, "Debt ceiling reached");

        _accrueStabilityFee(cdpId);

        uint256 newDebt = cdp.debt + amount;
        uint256 minCollateral = _getMinCollateral(newDebt);
        require(cdp.collateral >= minCollateral, "Insufficient collateral");

        cdp.debt = newDebt;
        totalDebt += amount;

        _mint(msg.sender, amount);

        emit DebtMinted(cdpId, amount);
    }

    /**
     * @notice Repay CUSD debt
     * @param cdpId CDP to repay
     * @param amount CUSD to repay
     */
    function repayDebt(uint256 cdpId, uint256 amount) external nonReentrant {
        CDP storage cdp = cdps[cdpId];
        require(cdp.isActive, "CDP not active");
        require(amount > 0, "Zero amount");

        _accrueStabilityFee(cdpId);

        uint256 repayAmount = amount > cdp.debt ? cdp.debt : amount;

        // Burn CUSD
        _burn(msg.sender, repayAmount);

        cdp.debt -= repayAmount;
        totalDebt -= repayAmount;

        emit DebtRepaid(cdpId, repayAmount);
    }

    /**
     * @notice Close CDP (repay all debt, withdraw all collateral)
     * @param cdpId CDP to close
     */
    function closeCDP(uint256 cdpId) external nonReentrant {
        CDP storage cdp = cdps[cdpId];
        require(cdp.isActive, "CDP not active");

        _accrueStabilityFee(cdpId);

        // Burn all debt
        if (cdp.debt > 0) {
            _burn(msg.sender, cdp.debt);
            totalDebt -= cdp.debt;
        }

        // Return all collateral
        uint256 collateralReturn = cdp.collateral;
        totalCollateral -= collateralReturn;

        // Close CDP
        cdp.isActive = false;
        cdp.collateral = 0;
        cdp.debt = 0;

        collateralToken.safeTransfer(msg.sender, collateralReturn);

        emit CDPClosed(cdpId, msg.sender);
    }

    // ============================================================================
    // Stability Fee
    // ============================================================================

    /**
     * @notice Accrue stability fee on a CDP
     * @param cdpId CDP to accrue fees for
     */
    function _accrueStabilityFee(uint256 cdpId) internal {
        CDP storage cdp = cdps[cdpId];
        if (cdp.debt == 0) {
            cdp.lastAccrual = block.number;
            return;
        }

        uint256 blocksElapsed = block.number - cdp.lastAccrual;
        if (blocksElapsed == 0) return;

        // Calculate fee: debt * rate * time
        uint256 annualFee = (cdp.debt * stabilityFeeBps) / BPS;
        uint256 fee = (annualFee * blocksElapsed) / BLOCKS_PER_YEAR;

        // Add fee to debt
        cdp.debt += fee;
        totalDebt += fee;

        // Fee goes to surplus buffer
        surplusBuffer += fee;

        cdp.lastAccrual = block.number;
    }

    /**
     * @notice Get pending stability fee for a CDP
     * @param cdpId CDP to check
     */
    function getPendingFee(uint256 cdpId) external view returns (uint256) {
        CDP storage cdp = cdps[cdpId];
        if (cdp.debt == 0) return 0;

        uint256 blocksElapsed = block.number - cdp.lastAccrual;
        uint256 annualFee = (cdp.debt * stabilityFeeBps) / BPS;
        return (annualFee * blocksElapsed) / BLOCKS_PER_YEAR;
    }

    // ============================================================================
    // Liquidation
    // ============================================================================

    /**
     * @notice Check if a CDP can be liquidated
     * @param cdpId CDP to check
     */
    function isLiquidatable(uint256 cdpId) public view returns (bool) {
        CDP storage cdp = cdps[cdpId];
        if (!cdp.isActive || cdp.debt == 0) return false;

        uint256 collateralValue = (cdp.collateral * collateralPrice) / SCALE;
        uint256 minCollateralValue = (cdp.debt * liquidationThreshold) / BPS;

        return collateralValue < minCollateralValue;
    }

    /**
     * @notice Start liquidation auction for undercollateralized CDP
     * @param cdpId CDP to liquidate
     * @return auctionId The auction ID
     */
    function startLiquidation(uint256 cdpId) external nonReentrant returns (uint256 auctionId) {
        require(isLiquidatable(cdpId), "CDP not liquidatable");

        CDP storage cdp = cdps[cdpId];
        _accrueStabilityFee(cdpId);

        // Calculate debt with liquidation penalty
        uint256 debtWithPenalty = (cdp.debt * liquidationPenaltyBps) / BPS;

        // Create auction
        auctionId = auctionCount++;
        auctions[auctionId] = LiquidationAuction({
            cdpId: cdpId,
            borrower: msg.sender,
            collateralForSale: cdp.collateral,
            debtToCover: debtWithPenalty,
            startTime: block.timestamp,
            startPrice: (debtWithPenalty * SCALE) / cdp.collateral, // Debt/collateral ratio
            endTime: block.timestamp + auctionDuration,
            isActive: true
        });

        // Mark CDP as in liquidation
        cdp.isActive = false;

        emit AuctionStarted(auctionId, cdpId, cdp.collateral, debtWithPenalty);
    }

    /**
     * @notice Bid on liquidation auction (Dutch auction - price decreases)
     * @param auctionId Auction to bid on
     * @param collateralAmount Amount of collateral to buy
     */
    function bidOnAuction(
        uint256 auctionId,
        uint256 collateralAmount
    ) external nonReentrant {
        LiquidationAuction storage auction = auctions[auctionId];
        require(auction.isActive, "Auction not active");
        require(block.timestamp <= auction.endTime, "Auction ended");
        require(collateralAmount <= auction.collateralForSale, "Too much collateral");

        // Calculate current price (Dutch auction: price decreases over time)
        uint256 currentPrice = _getCurrentAuctionPrice(auctionId);

        // Calculate CUSD needed
        uint256 cusdNeeded = (collateralAmount * currentPrice) / SCALE;

        // Burn CUSD from bidder
        _burn(msg.sender, cusdNeeded);

        // Transfer collateral to bidder
        collateralToken.safeTransfer(msg.sender, collateralAmount);

        // Update auction
        auction.collateralForSale -= collateralAmount;
        auction.debtToCover -= cusdNeeded;

        // Update global totals
        CDP storage cdp = cdps[auction.cdpId];
        cdp.collateral -= collateralAmount;
        cdp.debt -= cusdNeeded;
        totalCollateral -= collateralAmount;
        totalDebt -= cusdNeeded;

        // Close auction if fully liquidated
        if (auction.collateralForSale == 0 || auction.debtToCover == 0) {
            auction.isActive = false;
        }

        emit AuctionBid(auctionId, msg.sender, currentPrice, collateralAmount);
    }

    /**
     * @notice Get current auction price (decreases over time)
     * @param auctionId Auction to check
     */
    function _getCurrentAuctionPrice(uint256 auctionId) internal view returns (uint256) {
        LiquidationAuction storage auction = auctions[auctionId];

        uint256 elapsed = block.timestamp - auction.startTime;
        uint256 duration = auctionDuration;

        if (elapsed >= duration) {
            // Minimum price at end (50% of start)
            return auction.startPrice / 2;
        }

        // Linear decrease
        uint256 decrease = (auction.startPrice * elapsed) / (duration * 2);
        return auction.startPrice - decrease;
    }

    /**
     * @notice Get current auction price (public)
     */
    function getCurrentAuctionPrice(uint256 auctionId) external view returns (uint256) {
        return _getCurrentAuctionPrice(auctionId);
    }

    // ============================================================================
    // View Functions
    // ============================================================================

    /**
     * @notice Get minimum collateral for debt amount
     */
    function _getMinCollateral(uint256 debt) internal view returns (uint256) {
        // minCollateral = debt * collateralRatio / (price * BPS)
        return (debt * collateralRatio * SCALE) / (collateralPrice * BPS);
    }

    /**
     * @notice Get CDP health (collateralization ratio)
     * @param cdpId CDP to check
     * @return healthBps Current collateralization in basis points
     */
    function getCDPHealth(uint256 cdpId) external view returns (uint256 healthBps) {
        CDP storage cdp = cdps[cdpId];
        if (cdp.debt == 0) return type(uint256).max;

        uint256 collateralValue = (cdp.collateral * collateralPrice) / SCALE;
        return (collateralValue * BPS) / cdp.debt;
    }

    /**
     * @notice Get user's CDP IDs
     */
    function getUserCDPs(address user) external view returns (uint256[] memory) {
        return userCdps[user];
    }

    /**
     * @notice Get CDP details
     */
    function getCDP(uint256 cdpId) external view returns (
        uint256 collateral,
        uint256 debt,
        uint256 healthBps,
        bool isActive,
        bool canLiquidate
    ) {
        CDP storage cdp = cdps[cdpId];
        collateral = cdp.collateral;
        debt = cdp.debt;
        isActive = cdp.isActive;

        if (debt > 0) {
            uint256 collateralValue = (collateral * collateralPrice) / SCALE;
            healthBps = (collateralValue * BPS) / debt;
        } else {
            healthBps = type(uint256).max;
        }

        canLiquidate = isLiquidatable(cdpId);
    }

    /**
     * @notice Get protocol stats
     */
    function getProtocolStats() external view returns (
        uint256 _totalCollateral,
        uint256 _totalDebt,
        uint256 _collateralizationRatio,
        uint256 _surplusBuffer
    ) {
        _totalCollateral = totalCollateral;
        _totalDebt = totalDebt;
        _collateralizationRatio = totalDebt > 0
            ? ((totalCollateral * collateralPrice) * BPS) / (SCALE * totalDebt)
            : 0;
        _surplusBuffer = surplusBuffer;
    }

    // ============================================================================
    // Admin Functions
    // ============================================================================

    /**
     * @notice Update collateral price (oracle simulation)
     * @param newPrice New price (collateral per USD, scaled by 1e18)
     */
    function updatePrice(uint256 newPrice) external onlyOwner {
        require(newPrice > 0, "Invalid price");
        collateralPrice = newPrice;
        emit PriceUpdated(newPrice);
    }

    /**
     * @notice Update protocol parameters
     */
    function updateParameters(
        uint256 _collateralRatio,
        uint256 _liquidationThreshold,
        uint256 _stabilityFeeBps,
        uint256 _liquidationPenaltyBps
    ) external onlyOwner {
        require(_collateralRatio >= _liquidationThreshold, "Invalid ratios");
        require(_stabilityFeeBps <= 2000, "Fee too high"); // Max 20%
        require(_liquidationPenaltyBps <= 2000, "Penalty too high");

        collateralRatio = _collateralRatio;
        liquidationThreshold = _liquidationThreshold;
        stabilityFeeBps = _stabilityFeeBps;
        liquidationPenaltyBps = _liquidationPenaltyBps;
    }

    /**
     * @notice Update debt ceiling
     */
    function updateDebtCeiling(uint256 newCeiling) external onlyOwner {
        debtCeiling = newCeiling;
    }

    /**
     * @notice Withdraw surplus buffer (protocol revenue)
     */
    function withdrawSurplus(uint256 amount) external onlyOwner {
        require(amount <= surplusBuffer, "Insufficient surplus");
        surplusBuffer -= amount;
        _mint(msg.sender, amount);
    }
}
