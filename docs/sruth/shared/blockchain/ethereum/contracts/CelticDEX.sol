// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/math/Math.sol";

/**
 * @title CelticDEX
 * @author Cianfhoghlaim / tuath project
 * @notice Automated Market Maker for Celtic token trading
 * @dev SpeedRunEthereum Challenge 4: DEX
 *
 * Features:
 * - Constant product AMM (x * y = k)
 * - LP token minting/burning
 * - Fee collection (0.3%)
 * - Player-to-player item trading pools
 * - Multi-token support
 */
contract CelticDEX is ERC20, Ownable, ReentrancyGuard {
    using SafeERC20 for IERC20;
    using Math for uint256;

    // ============================================================================
    // State Variables
    // ============================================================================

    /// @notice Token A in the pair
    IERC20 public immutable tokenA;

    /// @notice Token B in the pair
    IERC20 public immutable tokenB;

    /// @notice Reserve of token A
    uint256 public reserveA;

    /// @notice Reserve of token B
    uint256 public reserveB;

    /// @notice Trading fee in basis points (30 = 0.3%)
    uint256 public feeBps = 30;

    /// @notice Accumulated fees for token A
    uint256 public feesA;

    /// @notice Accumulated fees for token B
    uint256 public feesB;

    /// @notice Minimum liquidity locked forever (prevents division by zero)
    uint256 public constant MINIMUM_LIQUIDITY = 1000;

    /// @notice Last update block for TWAP
    uint256 public blockTimestampLast;

    /// @notice Cumulative price for TWAP (tokenA per tokenB)
    uint256 public priceACumulativeLast;

    /// @notice Cumulative price for TWAP (tokenB per tokenA)
    uint256 public priceBCumulativeLast;

    // ============================================================================
    // Events
    // ============================================================================

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

    event FeesCollected(
        address indexed collector,
        uint256 feesA,
        uint256 feesB
    );

    event Sync(uint256 reserveA, uint256 reserveB);

    // ============================================================================
    // Constructor
    // ============================================================================

    constructor(
        address _tokenA,
        address _tokenB,
        string memory lpName,
        string memory lpSymbol
    ) ERC20(lpName, lpSymbol) Ownable(msg.sender) {
        require(_tokenA != _tokenB, "Identical tokens");
        require(_tokenA != address(0) && _tokenB != address(0), "Zero address");

        tokenA = IERC20(_tokenA);
        tokenB = IERC20(_tokenB);
    }

    // ============================================================================
    // Liquidity Functions
    // ============================================================================

    /**
     * @notice Add liquidity to the pool
     * @param amountA Amount of token A to add
     * @param amountB Amount of token B to add
     * @param minLpTokens Minimum LP tokens to receive (slippage protection)
     * @return lpTokens Amount of LP tokens minted
     *
     * @dev First depositor sets the initial ratio.
     * Subsequent depositors must maintain the ratio.
     */
    function addLiquidity(
        uint256 amountA,
        uint256 amountB,
        uint256 minLpTokens
    ) external nonReentrant returns (uint256 lpTokens) {
        require(amountA > 0 && amountB > 0, "Zero amounts");

        // Update TWAP
        _updateCumulativePrices();

        uint256 _totalSupply = totalSupply();

        if (_totalSupply == 0) {
            // First deposit: LP tokens = sqrt(amountA * amountB) - MINIMUM_LIQUIDITY
            lpTokens = Math.sqrt(amountA * amountB) - MINIMUM_LIQUIDITY;

            // Lock minimum liquidity forever to prevent division by zero
            _mint(address(1), MINIMUM_LIQUIDITY);
        } else {
            // Calculate LP tokens based on smaller ratio to prevent manipulation
            uint256 lpFromA = (amountA * _totalSupply) / reserveA;
            uint256 lpFromB = (amountB * _totalSupply) / reserveB;
            lpTokens = lpFromA < lpFromB ? lpFromA : lpFromB;
        }

        require(lpTokens >= minLpTokens, "Slippage exceeded");

        // Transfer tokens to pool
        tokenA.safeTransferFrom(msg.sender, address(this), amountA);
        tokenB.safeTransferFrom(msg.sender, address(this), amountB);

        // Update reserves
        reserveA += amountA;
        reserveB += amountB;

        // Mint LP tokens
        _mint(msg.sender, lpTokens);

        emit LiquidityAdded(msg.sender, amountA, amountB, lpTokens);
        emit Sync(reserveA, reserveB);
    }

    /**
     * @notice Remove liquidity from the pool
     * @param lpTokens Amount of LP tokens to burn
     * @param minAmountA Minimum token A to receive
     * @param minAmountB Minimum token B to receive
     * @return amountA Amount of token A returned
     * @return amountB Amount of token B returned
     */
    function removeLiquidity(
        uint256 lpTokens,
        uint256 minAmountA,
        uint256 minAmountB
    ) external nonReentrant returns (uint256 amountA, uint256 amountB) {
        require(lpTokens > 0, "Zero LP tokens");
        require(balanceOf(msg.sender) >= lpTokens, "Insufficient LP balance");

        // Update TWAP
        _updateCumulativePrices();

        uint256 _totalSupply = totalSupply();

        // Calculate proportional share
        amountA = (lpTokens * reserveA) / _totalSupply;
        amountB = (lpTokens * reserveB) / _totalSupply;

        require(amountA >= minAmountA, "Slippage A");
        require(amountB >= minAmountB, "Slippage B");

        // Burn LP tokens
        _burn(msg.sender, lpTokens);

        // Update reserves
        reserveA -= amountA;
        reserveB -= amountB;

        // Transfer tokens
        tokenA.safeTransfer(msg.sender, amountA);
        tokenB.safeTransfer(msg.sender, amountB);

        emit LiquidityRemoved(msg.sender, amountA, amountB, lpTokens);
        emit Sync(reserveA, reserveB);
    }

    // ============================================================================
    // Swap Functions
    // ============================================================================

    /**
     * @notice Swap token A for token B
     * @param amountIn Amount of token A to swap
     * @param minAmountOut Minimum token B to receive
     * @return amountOut Amount of token B received
     */
    function swapAForB(
        uint256 amountIn,
        uint256 minAmountOut
    ) external nonReentrant returns (uint256 amountOut) {
        require(amountIn > 0, "Zero input");

        // Update TWAP
        _updateCumulativePrices();

        // Calculate output using constant product formula
        amountOut = getAmountOut(amountIn, reserveA, reserveB);
        require(amountOut >= minAmountOut, "Slippage exceeded");
        require(amountOut < reserveB, "Insufficient liquidity");

        // Transfer tokens
        tokenA.safeTransferFrom(msg.sender, address(this), amountIn);
        tokenB.safeTransfer(msg.sender, amountOut);

        // Update reserves (fee is kept in pool)
        reserveA += amountIn;
        reserveB -= amountOut;

        emit Swap(msg.sender, address(tokenA), address(tokenB), amountIn, amountOut);
        emit Sync(reserveA, reserveB);
    }

    /**
     * @notice Swap token B for token A
     * @param amountIn Amount of token B to swap
     * @param minAmountOut Minimum token A to receive
     * @return amountOut Amount of token A received
     */
    function swapBForA(
        uint256 amountIn,
        uint256 minAmountOut
    ) external nonReentrant returns (uint256 amountOut) {
        require(amountIn > 0, "Zero input");

        // Update TWAP
        _updateCumulativePrices();

        amountOut = getAmountOut(amountIn, reserveB, reserveA);
        require(amountOut >= minAmountOut, "Slippage exceeded");
        require(amountOut < reserveA, "Insufficient liquidity");

        tokenB.safeTransferFrom(msg.sender, address(this), amountIn);
        tokenA.safeTransfer(msg.sender, amountOut);

        reserveB += amountIn;
        reserveA -= amountOut;

        emit Swap(msg.sender, address(tokenB), address(tokenA), amountIn, amountOut);
        emit Sync(reserveA, reserveB);
    }

    // ============================================================================
    // Pricing Functions
    // ============================================================================

    /**
     * @notice Calculate output amount using constant product formula
     * @param amountIn Amount of input token
     * @param reserveIn Reserve of input token
     * @param reserveOut Reserve of output token
     * @return amountOut Amount of output token
     *
     * @dev Formula: amountOut = (amountIn * (1 - fee) * reserveOut) / (reserveIn + amountIn * (1 - fee))
     * With fee = 0.3%: amountOut = (amountIn * 997 * reserveOut) / (reserveIn * 1000 + amountIn * 997)
     */
    function getAmountOut(
        uint256 amountIn,
        uint256 reserveIn,
        uint256 reserveOut
    ) public view returns (uint256 amountOut) {
        require(amountIn > 0, "Zero input");
        require(reserveIn > 0 && reserveOut > 0, "No liquidity");

        uint256 amountInWithFee = amountIn * (10000 - feeBps);
        uint256 numerator = amountInWithFee * reserveOut;
        uint256 denominator = (reserveIn * 10000) + amountInWithFee;

        amountOut = numerator / denominator;
    }

    /**
     * @notice Calculate input amount for desired output
     * @param amountOut Desired output amount
     * @param reserveIn Reserve of input token
     * @param reserveOut Reserve of output token
     * @return amountIn Required input amount
     */
    function getAmountIn(
        uint256 amountOut,
        uint256 reserveIn,
        uint256 reserveOut
    ) public view returns (uint256 amountIn) {
        require(amountOut > 0, "Zero output");
        require(reserveIn > 0 && reserveOut > 0, "No liquidity");
        require(amountOut < reserveOut, "Insufficient liquidity");

        uint256 numerator = reserveIn * amountOut * 10000;
        uint256 denominator = (reserveOut - amountOut) * (10000 - feeBps);

        amountIn = (numerator / denominator) + 1; // Round up
    }

    /**
     * @notice Get current spot prices
     * @return priceAInB Price of 1 token A in terms of token B (scaled by 1e18)
     * @return priceBInA Price of 1 token B in terms of token A (scaled by 1e18)
     */
    function getSpotPrices() external view returns (uint256 priceAInB, uint256 priceBInA) {
        if (reserveA == 0 || reserveB == 0) {
            return (0, 0);
        }

        priceAInB = (reserveB * 1e18) / reserveA;
        priceBInA = (reserveA * 1e18) / reserveB;
    }

    /**
     * @notice Calculate price impact of a trade
     * @param amountIn Amount to trade
     * @param isAToB Direction of trade
     * @return impactBps Price impact in basis points
     */
    function getPriceImpact(
        uint256 amountIn,
        bool isAToB
    ) external view returns (uint256 impactBps) {
        if (reserveA == 0 || reserveB == 0) return 0;

        uint256 spotPrice;
        uint256 executionPrice;

        if (isAToB) {
            spotPrice = (reserveB * 1e18) / reserveA;
            uint256 amountOut = getAmountOut(amountIn, reserveA, reserveB);
            executionPrice = (amountOut * 1e18) / amountIn;
        } else {
            spotPrice = (reserveA * 1e18) / reserveB;
            uint256 amountOut = getAmountOut(amountIn, reserveB, reserveA);
            executionPrice = (amountOut * 1e18) / amountIn;
        }

        if (executionPrice >= spotPrice) {
            impactBps = 0;
        } else {
            impactBps = ((spotPrice - executionPrice) * 10000) / spotPrice;
        }
    }

    // ============================================================================
    // TWAP Functions
    // ============================================================================

    /**
     * @notice Update cumulative prices for TWAP
     */
    function _updateCumulativePrices() internal {
        uint256 blockTimestamp = block.timestamp;
        uint256 timeElapsed = blockTimestamp - blockTimestampLast;

        if (timeElapsed > 0 && reserveA > 0 && reserveB > 0) {
            // Accumulate price * time
            priceACumulativeLast += (reserveB * 1e18 / reserveA) * timeElapsed;
            priceBCumulativeLast += (reserveA * 1e18 / reserveB) * timeElapsed;
            blockTimestampLast = blockTimestamp;
        }
    }

    /**
     * @notice Get current TWAP data for external calculation
     */
    function getTWAPData() external view returns (
        uint256 priceACumulative,
        uint256 priceBCumulative,
        uint256 lastTimestamp
    ) {
        return (priceACumulativeLast, priceBCumulativeLast, blockTimestampLast);
    }

    // ============================================================================
    // Admin Functions
    // ============================================================================

    /**
     * @notice Update trading fee
     * @param newFeeBps New fee in basis points (max 100 = 1%)
     */
    function setFee(uint256 newFeeBps) external onlyOwner {
        require(newFeeBps <= 100, "Fee too high");
        feeBps = newFeeBps;
    }

    /**
     * @notice Collect accumulated fees
     */
    function collectFees() external onlyOwner {
        // Fees accumulate naturally as the k value increases relative to LP tokens
        // This simple implementation just tracks actual vs expected balances
        uint256 balanceA = tokenA.balanceOf(address(this));
        uint256 balanceB = tokenB.balanceOf(address(this));

        uint256 feeA = balanceA > reserveA ? balanceA - reserveA : 0;
        uint256 feeB = balanceB > reserveB ? balanceB - reserveB : 0;

        if (feeA > 0) {
            tokenA.safeTransfer(owner(), feeA);
            feesA += feeA;
        }
        if (feeB > 0) {
            tokenB.safeTransfer(owner(), feeB);
            feesB += feeB;
        }

        emit FeesCollected(msg.sender, feeA, feeB);
    }

    /**
     * @notice Sync reserves with actual balances
     * @dev Use if tokens are accidentally sent to the contract
     */
    function sync() external {
        reserveA = tokenA.balanceOf(address(this));
        reserveB = tokenB.balanceOf(address(this));
        emit Sync(reserveA, reserveB);
    }

    // ============================================================================
    // View Functions
    // ============================================================================

    /**
     * @notice Get pool reserves
     */
    function getReserves() external view returns (uint256, uint256) {
        return (reserveA, reserveB);
    }

    /**
     * @notice Get pool stats
     */
    function getPoolStats() external view returns (
        uint256 _reserveA,
        uint256 _reserveB,
        uint256 _totalSupply,
        uint256 _k
    ) {
        _reserveA = reserveA;
        _reserveB = reserveB;
        _totalSupply = totalSupply();
        _k = reserveA * reserveB;
    }

    /**
     * @notice Calculate impermanent loss for a given price change
     * @param priceRatio New price / initial price (scaled by 1e18)
     * @return lossBps Impermanent loss in basis points
     */
    function calculateImpermanentLoss(
        uint256 priceRatio
    ) external pure returns (uint256 lossBps) {
        // IL = 2 * sqrt(r) / (1 + r) - 1
        // Where r = new_price / initial_price

        // Simplify: for small changes, IL ≈ (r - 1)^2 / (4 * r)
        if (priceRatio == 1e18) return 0;

        // Using the approximation for the formula
        uint256 sqrtR = Math.sqrt(priceRatio * 1e18);
        uint256 numerator = 2 * sqrtR;
        uint256 denominator = 1e18 + priceRatio;

        uint256 holdValue = 1e18; // Normalized
        uint256 lpValue = (numerator * 1e18) / denominator;

        if (lpValue >= holdValue) {
            lossBps = 0;
        } else {
            lossBps = ((holdValue - lpValue) * 10000) / holdValue;
        }
    }
}
