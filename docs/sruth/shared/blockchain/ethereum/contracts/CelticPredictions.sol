// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

/// @title CelticPredictions
/// @notice Binary outcome prediction market with CPMM pricing
/// @dev SpeedRunEthereum Challenge 7 - Prediction Markets
///
/// Learning Objectives:
/// - Binary outcome markets (YES/NO)
/// - Cost Function Market Maker (LMSR/CPMM)
/// - Oracle-based resolution
/// - Dispute mechanisms
///
/// Integration:
/// - crypteolas: DeFi prediction market analytics
/// - tuath: Exam result prediction markets for Irish education
contract CelticPredictions is Ownable, ReentrancyGuard {
    using SafeERC20 for IERC20;

    // ============ Structs ============

    struct Market {
        string question;
        string[] outcomes;
        uint256 resolutionTime;
        uint256 totalYesShares;
        uint256 totalNoShares;
        uint256 liquidity;
        int256 resolvedOutcome; // -1 = unresolved, 0 = NO, 1 = YES
        bool resolved;
        bool disputed;
        address creator;
        uint256 creatorFee; // in basis points
    }

    struct Position {
        uint256 yesShares;
        uint256 noShares;
        uint256 totalCost;
    }

    struct DisputeInfo {
        address disputer;
        uint256 bond;
        string reason;
        uint256 disputeTime;
        bool resolved;
    }

    // ============ State Variables ============

    IERC20 public immutable collateralToken;

    uint256 public marketCount;
    mapping(uint256 => Market) public markets;
    mapping(uint256 => mapping(address => Position)) public positions;
    mapping(uint256 => DisputeInfo) public disputes;
    mapping(uint256 => mapping(address => bool)) public hasRedeemed;

    // Platform parameters
    uint256 public platformFee = 100; // 1% in basis points
    uint256 public minLiquidity = 100e18;
    uint256 public disputeBond = 50e18;
    uint256 public disputePeriod = 1 days;

    // Oracle addresses (could be Chainlink, UMA, or custom)
    mapping(address => bool) public authorizedOracles;

    // CPMM constant (controls price sensitivity)
    uint256 public constant CPMM_B = 100e18; // Liquidity depth

    // ============ Events ============

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
    event SharesSold(
        uint256 indexed marketId,
        address indexed seller,
        bool isYes,
        uint256 shares,
        uint256 payout
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
    event DisputeResolved(
        uint256 indexed marketId,
        bool accepted,
        int256 newOutcome
    );
    event LiquidityAdded(
        uint256 indexed marketId,
        address indexed provider,
        uint256 amount
    );

    // ============ Errors ============

    error MarketNotFound();
    error MarketAlreadyResolved();
    error MarketNotExpired();
    error MarketExpired();
    error InsufficientLiquidity();
    error InsufficientShares();
    error NotAuthorizedOracle();
    error DisputeAlreadyActive();
    error NoActiveDispute();
    error DisputePeriodActive();
    error AlreadyRedeemed();
    error InvalidOutcome();

    // ============ Constructor ============

    constructor(address _collateralToken) Ownable(msg.sender) {
        collateralToken = IERC20(_collateralToken);
    }

    // ============ Market Creation ============

    /// @notice Create a new prediction market
    /// @param question The question being predicted
    /// @param resolutionTime When the market can be resolved
    /// @param initialLiquidity Initial liquidity for CPMM
    /// @param creatorFee Fee for market creator (max 5%)
    function createMarket(
        string calldata question,
        uint256 resolutionTime,
        uint256 initialLiquidity,
        uint256 creatorFee
    ) external nonReentrant returns (uint256 marketId) {
        require(resolutionTime > block.timestamp, "Resolution must be future");
        require(initialLiquidity >= minLiquidity, "Insufficient initial liquidity");
        require(creatorFee <= 500, "Creator fee too high"); // Max 5%

        collateralToken.safeTransferFrom(msg.sender, address(this), initialLiquidity);

        marketId = marketCount++;

        string[] memory outcomes = new string[](2);
        outcomes[0] = "NO";
        outcomes[1] = "YES";

        markets[marketId] = Market({
            question: question,
            outcomes: outcomes,
            resolutionTime: resolutionTime,
            totalYesShares: 0,
            totalNoShares: 0,
            liquidity: initialLiquidity,
            resolvedOutcome: -1,
            resolved: false,
            disputed: false,
            creator: msg.sender,
            creatorFee: creatorFee
        });

        emit MarketCreated(marketId, question, resolutionTime, msg.sender);
    }

    // ============ Trading Functions ============

    /// @notice Buy outcome shares using CPMM pricing
    /// @param marketId The market to trade in
    /// @param isYes Whether buying YES or NO shares
    /// @param shares Number of shares to buy
    /// @param maxCost Maximum cost willing to pay (slippage protection)
    function buyShares(
        uint256 marketId,
        bool isYes,
        uint256 shares,
        uint256 maxCost
    ) external nonReentrant {
        Market storage market = markets[marketId];
        if (market.resolutionTime == 0) revert MarketNotFound();
        if (market.resolved) revert MarketAlreadyResolved();
        if (block.timestamp >= market.resolutionTime) revert MarketExpired();

        uint256 cost = calculateBuyCost(marketId, isYes, shares);
        require(cost <= maxCost, "Cost exceeds max");

        // Apply fees
        uint256 platformAmount = (cost * platformFee) / 10000;
        uint256 creatorAmount = (cost * market.creatorFee) / 10000;
        uint256 netCost = cost + platformAmount + creatorAmount;

        collateralToken.safeTransferFrom(msg.sender, address(this), netCost);

        // Update market state
        if (isYes) {
            market.totalYesShares += shares;
        } else {
            market.totalNoShares += shares;
        }
        market.liquidity += cost;

        // Update user position
        Position storage pos = positions[marketId][msg.sender];
        if (isYes) {
            pos.yesShares += shares;
        } else {
            pos.noShares += shares;
        }
        pos.totalCost += netCost;

        emit SharesPurchased(marketId, msg.sender, isYes, shares, netCost);
    }

    /// @notice Sell outcome shares back to the market
    /// @param marketId The market to trade in
    /// @param isYes Whether selling YES or NO shares
    /// @param shares Number of shares to sell
    /// @param minPayout Minimum payout expected (slippage protection)
    function sellShares(
        uint256 marketId,
        bool isYes,
        uint256 shares,
        uint256 minPayout
    ) external nonReentrant {
        Market storage market = markets[marketId];
        if (market.resolutionTime == 0) revert MarketNotFound();
        if (market.resolved) revert MarketAlreadyResolved();

        Position storage pos = positions[marketId][msg.sender];

        if (isYes) {
            if (pos.yesShares < shares) revert InsufficientShares();
            pos.yesShares -= shares;
            market.totalYesShares -= shares;
        } else {
            if (pos.noShares < shares) revert InsufficientShares();
            pos.noShares -= shares;
            market.totalNoShares -= shares;
        }

        uint256 payout = calculateSellPayout(marketId, isYes, shares);
        require(payout >= minPayout, "Payout below minimum");

        market.liquidity -= payout;
        collateralToken.safeTransfer(msg.sender, payout);

        emit SharesSold(marketId, msg.sender, isYes, shares, payout);
    }

    // ============ CPMM Pricing ============

    /// @notice Calculate cost to buy shares using LMSR
    /// @dev Cost = b * ln((e^(q_yes/b) + e^(q_no/b)) / (e^(q_yes'/b) + e^(q_no'/b)))
    function calculateBuyCost(
        uint256 marketId,
        bool isYes,
        uint256 shares
    ) public view returns (uint256) {
        Market storage market = markets[marketId];

        // Simplified CPMM formula for gas efficiency
        // Uses constant product approximation: price = yes_shares / (yes_shares + no_shares)
        uint256 yesShares = market.totalYesShares + 1e18; // Add 1 to avoid division by zero
        uint256 noShares = market.totalNoShares + 1e18;
        uint256 totalShares = yesShares + noShares;

        uint256 currentPrice;
        if (isYes) {
            currentPrice = (noShares * 1e18) / totalShares;
        } else {
            currentPrice = (yesShares * 1e18) / totalShares;
        }

        // Average cost accounting for price impact
        uint256 newYesShares = isYes ? yesShares + shares : yesShares;
        uint256 newNoShares = isYes ? noShares : noShares + shares;
        uint256 newTotal = newYesShares + newNoShares;

        uint256 newPrice;
        if (isYes) {
            newPrice = (newNoShares * 1e18) / newTotal;
        } else {
            newPrice = (newYesShares * 1e18) / newTotal;
        }

        // Average price * shares (simplified)
        uint256 avgPrice = (currentPrice + newPrice) / 2;
        return (avgPrice * shares) / 1e18;
    }

    /// @notice Calculate payout for selling shares
    function calculateSellPayout(
        uint256 marketId,
        bool isYes,
        uint256 shares
    ) public view returns (uint256) {
        Market storage market = markets[marketId];

        uint256 yesShares = market.totalYesShares + 1e18;
        uint256 noShares = market.totalNoShares + 1e18;
        uint256 totalShares = yesShares + noShares;

        uint256 currentPrice;
        if (isYes) {
            currentPrice = (noShares * 1e18) / totalShares;
        } else {
            currentPrice = (yesShares * 1e18) / totalShares;
        }

        // Apply small sell penalty for liquidity protection
        return (currentPrice * shares * 95) / (1e18 * 100);
    }

    /// @notice Get current probability implied by the market
    function getProbability(uint256 marketId) external view returns (uint256 yesProbability) {
        Market storage market = markets[marketId];

        uint256 yesShares = market.totalYesShares + 1e18;
        uint256 noShares = market.totalNoShares + 1e18;

        yesProbability = (yesShares * 1e18) / (yesShares + noShares);
    }

    // ============ Resolution ============

    /// @notice Resolve market with final outcome (oracle-based)
    /// @param marketId The market to resolve
    /// @param outcome The winning outcome (0 = NO, 1 = YES)
    function resolveMarket(uint256 marketId, int256 outcome) external {
        if (!authorizedOracles[msg.sender] && msg.sender != owner()) {
            revert NotAuthorizedOracle();
        }

        Market storage market = markets[marketId];
        if (market.resolutionTime == 0) revert MarketNotFound();
        if (market.resolved) revert MarketAlreadyResolved();
        if (block.timestamp < market.resolutionTime) revert MarketNotExpired();
        if (outcome != 0 && outcome != 1) revert InvalidOutcome();

        market.resolvedOutcome = outcome;
        market.resolved = true;

        emit MarketResolved(marketId, outcome, msg.sender);
    }

    /// @notice Claim winnings after market resolution
    function claimWinnings(uint256 marketId) external nonReentrant {
        Market storage market = markets[marketId];
        if (!market.resolved) revert MarketNotExpired();
        if (market.disputed) revert DisputeAlreadyActive();
        if (block.timestamp < market.resolutionTime + disputePeriod) {
            revert DisputePeriodActive();
        }
        if (hasRedeemed[marketId][msg.sender]) revert AlreadyRedeemed();

        Position storage pos = positions[marketId][msg.sender];

        uint256 winningShares;
        if (market.resolvedOutcome == 1) {
            winningShares = pos.yesShares;
        } else {
            winningShares = pos.noShares;
        }

        if (winningShares == 0) revert InsufficientShares();

        hasRedeemed[marketId][msg.sender] = true;

        // Each winning share worth 1 token
        uint256 payout = winningShares;

        // Check liquidity
        if (payout > market.liquidity) {
            payout = market.liquidity;
        }
        market.liquidity -= payout;

        collateralToken.safeTransfer(msg.sender, payout);

        emit WinningsClaimed(marketId, msg.sender, payout);
    }

    // ============ Dispute Mechanism ============

    /// @notice Raise dispute on market resolution
    /// @param marketId The resolved market to dispute
    /// @param reason Reason for the dispute
    function raiseDispute(uint256 marketId, string calldata reason) external nonReentrant {
        Market storage market = markets[marketId];
        if (!market.resolved) revert MarketNotExpired();
        if (market.disputed) revert DisputeAlreadyActive();
        if (block.timestamp >= market.resolutionTime + disputePeriod) {
            revert("Dispute period ended");
        }

        collateralToken.safeTransferFrom(msg.sender, address(this), disputeBond);

        market.disputed = true;
        disputes[marketId] = DisputeInfo({
            disputer: msg.sender,
            bond: disputeBond,
            reason: reason,
            disputeTime: block.timestamp,
            resolved: false
        });

        emit DisputeRaised(marketId, msg.sender, reason);
    }

    /// @notice Resolve dispute (admin/oracle only)
    /// @param marketId The disputed market
    /// @param accept Whether to accept the dispute
    /// @param newOutcome New outcome if dispute accepted
    function resolveDispute(
        uint256 marketId,
        bool accept,
        int256 newOutcome
    ) external onlyOwner {
        Market storage market = markets[marketId];
        DisputeInfo storage dispute = disputes[marketId];

        if (!market.disputed) revert NoActiveDispute();
        if (dispute.resolved) revert("Dispute already resolved");

        dispute.resolved = true;

        if (accept) {
            market.resolvedOutcome = newOutcome;
            // Return bond to disputer
            collateralToken.safeTransfer(dispute.disputer, dispute.bond);
        }
        // If rejected, bond is kept by protocol

        market.disputed = false;

        emit DisputeResolved(marketId, accept, newOutcome);
    }

    // ============ Liquidity Functions ============

    /// @notice Add liquidity to a market
    function addLiquidity(uint256 marketId, uint256 amount) external nonReentrant {
        Market storage market = markets[marketId];
        if (market.resolutionTime == 0) revert MarketNotFound();
        if (market.resolved) revert MarketAlreadyResolved();

        collateralToken.safeTransferFrom(msg.sender, address(this), amount);
        market.liquidity += amount;

        emit LiquidityAdded(marketId, msg.sender, amount);
    }

    // ============ View Functions ============

    /// @notice Get market details
    function getMarket(uint256 marketId) external view returns (
        string memory question,
        uint256 resolutionTime,
        uint256 totalYesShares,
        uint256 totalNoShares,
        uint256 liquidity,
        int256 resolvedOutcome,
        bool resolved,
        bool disputed
    ) {
        Market storage market = markets[marketId];
        return (
            market.question,
            market.resolutionTime,
            market.totalYesShares,
            market.totalNoShares,
            market.liquidity,
            market.resolvedOutcome,
            market.resolved,
            market.disputed
        );
    }

    /// @notice Get user position in a market
    function getPosition(uint256 marketId, address user) external view returns (
        uint256 yesShares,
        uint256 noShares,
        uint256 totalCost
    ) {
        Position storage pos = positions[marketId][user];
        return (pos.yesShares, pos.noShares, pos.totalCost);
    }

    /// @notice Calculate potential payout
    function calculatePotentialPayout(
        uint256 marketId,
        address user,
        int256 outcome
    ) external view returns (uint256) {
        Position storage pos = positions[marketId][user];

        if (outcome == 1) {
            return pos.yesShares;
        } else if (outcome == 0) {
            return pos.noShares;
        }
        return 0;
    }

    // ============ Admin Functions ============

    function setAuthorizedOracle(address oracle, bool authorized) external onlyOwner {
        authorizedOracles[oracle] = authorized;
    }

    function setPlatformFee(uint256 _fee) external onlyOwner {
        require(_fee <= 500, "Fee too high"); // Max 5%
        platformFee = _fee;
    }

    function setMinLiquidity(uint256 _minLiquidity) external onlyOwner {
        minLiquidity = _minLiquidity;
    }

    function setDisputeBond(uint256 _bond) external onlyOwner {
        disputeBond = _bond;
    }

    function setDisputePeriod(uint256 _period) external onlyOwner {
        disputePeriod = _period;
    }

    /// @notice Emergency withdraw for stuck funds
    function emergencyWithdraw(address token, uint256 amount) external onlyOwner {
        IERC20(token).safeTransfer(owner(), amount);
    }
}
