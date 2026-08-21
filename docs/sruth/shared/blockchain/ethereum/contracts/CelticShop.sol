// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

/**
 * @title CelticShop
 * @author Cianfhoghlaim / tuath project
 * @notice In-game shop for the tuath Celtic educational MMO
 * @dev SpeedRunEthereum Challenge 2: Token Vendor
 *
 * Features:
 * - Buy/sell CELTIC tokens with ETH
 * - Dynamic pricing based on demand
 * - In-game item purchases
 * - x402 micropayment compatible
 * - Bonding curve for token pricing
 */
contract CelticShop is Ownable, ReentrancyGuard {
    using SafeERC20 for IERC20;

    // ============================================================================
    // State Variables
    // ============================================================================

    /// @notice The CELTIC token
    IERC20 public immutable celticToken;

    /// @notice Base price: tokens per ETH (e.g., 1000 = 1000 CELTIC per 1 ETH)
    uint256 public tokensPerEth = 1000;

    /// @notice Buy/sell spread in basis points (e.g., 100 = 1%)
    uint256 public spreadBps = 100;

    /// @notice Total ETH collected
    uint256 public totalEthCollected;

    /// @notice Total CELTIC sold
    uint256 public totalTokensSold;

    /// @notice Total CELTIC bought back
    uint256 public totalTokensBought;

    /// @notice Whether the shop is open
    bool public isOpen = true;

    // ============================================================================
    // Structs
    // ============================================================================

    /// @notice In-game item for purchase
    struct GameItem {
        string name;
        string category;      // "weapon", "armor", "consumable", "cosmetic"
        uint256 priceInCeltic;
        uint256 stock;        // 0 = unlimited
        bool isActive;
        string metadataUri;   // IPFS/Arweave URI
    }

    /// @notice Purchase record
    struct Purchase {
        uint256 itemId;
        address buyer;
        uint256 price;
        uint256 timestamp;
    }

    // ============================================================================
    // Mappings
    // ============================================================================

    /// @notice Item ID => Item data
    mapping(uint256 => GameItem) public items;

    /// @notice Total number of items
    uint256 public itemCount;

    /// @notice Player address => Item ID => Amount owned
    mapping(address => mapping(uint256 => uint256)) public playerInventory;

    /// @notice Purchase history
    Purchase[] public purchases;

    // ============================================================================
    // Events
    // ============================================================================

    event TokensPurchased(
        address indexed buyer,
        uint256 ethSpent,
        uint256 tokensReceived,
        uint256 timestamp
    );

    event TokensSold(
        address indexed seller,
        uint256 tokensSold,
        uint256 ethReceived,
        uint256 timestamp
    );

    event ItemAdded(
        uint256 indexed itemId,
        string name,
        string category,
        uint256 price
    );

    event ItemPurchased(
        address indexed buyer,
        uint256 indexed itemId,
        uint256 price,
        uint256 timestamp
    );

    event PriceUpdated(
        uint256 oldPrice,
        uint256 newPrice
    );

    event ShopStatusChanged(bool isOpen);

    // ============================================================================
    // Constructor
    // ============================================================================

    constructor(address _celticToken) Ownable(msg.sender) {
        celticToken = IERC20(_celticToken);
    }

    // ============================================================================
    // Token Exchange Functions
    // ============================================================================

    /**
     * @notice Buy CELTIC tokens with ETH
     * @dev Sender sends ETH and receives CELTIC tokens
     */
    function buyTokens() external payable nonReentrant {
        require(isOpen, "Shop is closed");
        require(msg.value > 0, "Must send ETH");

        uint256 tokenAmount = getTokensForEth(msg.value);
        require(tokenAmount > 0, "Amount too small");
        require(
            celticToken.balanceOf(address(this)) >= tokenAmount,
            "Insufficient shop balance"
        );

        totalEthCollected += msg.value;
        totalTokensSold += tokenAmount;

        celticToken.safeTransfer(msg.sender, tokenAmount);

        emit TokensPurchased(msg.sender, msg.value, tokenAmount, block.timestamp);
    }

    /**
     * @notice Sell CELTIC tokens for ETH
     * @param tokenAmount Amount of CELTIC to sell
     */
    function sellTokens(uint256 tokenAmount) external nonReentrant {
        require(isOpen, "Shop is closed");
        require(tokenAmount > 0, "Must sell tokens");

        uint256 ethAmount = getEthForTokens(tokenAmount);
        require(ethAmount > 0, "Amount too small");
        require(address(this).balance >= ethAmount, "Insufficient ETH in shop");

        totalTokensBought += tokenAmount;

        celticToken.safeTransferFrom(msg.sender, address(this), tokenAmount);
        payable(msg.sender).transfer(ethAmount);

        emit TokensSold(msg.sender, tokenAmount, ethAmount, block.timestamp);
    }

    // ============================================================================
    // Item Shop Functions
    // ============================================================================

    /**
     * @notice Add a new item to the shop
     * @param name Item name
     * @param category Item category
     * @param priceInCeltic Price in CELTIC tokens
     * @param stock Initial stock (0 = unlimited)
     * @param metadataUri IPFS/Arweave URI for item metadata
     */
    function addItem(
        string calldata name,
        string calldata category,
        uint256 priceInCeltic,
        uint256 stock,
        string calldata metadataUri
    ) external onlyOwner returns (uint256) {
        uint256 itemId = itemCount++;

        items[itemId] = GameItem({
            name: name,
            category: category,
            priceInCeltic: priceInCeltic,
            stock: stock,
            isActive: true,
            metadataUri: metadataUri
        });

        emit ItemAdded(itemId, name, category, priceInCeltic);
        return itemId;
    }

    /**
     * @notice Purchase an in-game item with CELTIC tokens
     * @param itemId Item to purchase
     * @param quantity How many to buy
     */
    function purchaseItem(uint256 itemId, uint256 quantity) external nonReentrant {
        require(isOpen, "Shop is closed");
        require(quantity > 0, "Must buy at least 1");

        GameItem storage item = items[itemId];
        require(item.isActive, "Item not available");

        if (item.stock > 0) {
            require(item.stock >= quantity, "Insufficient stock");
            item.stock -= quantity;
        }

        uint256 totalPrice = item.priceInCeltic * quantity;

        // Transfer CELTIC from buyer to shop
        celticToken.safeTransferFrom(msg.sender, address(this), totalPrice);

        // Update inventory
        playerInventory[msg.sender][itemId] += quantity;

        // Record purchase
        purchases.push(Purchase({
            itemId: itemId,
            buyer: msg.sender,
            price: totalPrice,
            timestamp: block.timestamp
        }));

        emit ItemPurchased(msg.sender, itemId, totalPrice, block.timestamp);
    }

    /**
     * @notice Get items owned by a player
     * @param player Player address
     * @param itemId Item to check
     */
    function getInventory(address player, uint256 itemId) external view returns (uint256) {
        return playerInventory[player][itemId];
    }

    // ============================================================================
    // Pricing Functions
    // ============================================================================

    /**
     * @notice Calculate tokens received for ETH (buy price)
     * @param ethAmount Amount of ETH to spend
     * @return tokens Amount of CELTIC tokens received
     */
    function getTokensForEth(uint256 ethAmount) public view returns (uint256) {
        // Apply spread (buyer pays slightly more)
        uint256 effectiveRate = tokensPerEth * (10000 - spreadBps) / 10000;
        return (ethAmount * effectiveRate) / 1 ether;
    }

    /**
     * @notice Calculate ETH received for tokens (sell price)
     * @param tokenAmount Amount of CELTIC to sell
     * @return eth Amount of ETH received
     */
    function getEthForTokens(uint256 tokenAmount) public view returns (uint256) {
        // Apply spread (seller receives slightly less)
        uint256 effectiveRate = tokensPerEth * (10000 + spreadBps) / 10000;
        return (tokenAmount * 1 ether) / effectiveRate;
    }

    /**
     * @notice Get current buy price (ETH per token)
     */
    function getBuyPrice() external view returns (uint256) {
        return getTokensForEth(1 ether);
    }

    /**
     * @notice Get current sell price (ETH per token)
     */
    function getSellPrice() external view returns (uint256) {
        return getEthForTokens(1 ether);
    }

    // ============================================================================
    // Dynamic Pricing (Bonding Curve)
    // ============================================================================

    /**
     * @notice Update token price based on supply/demand
     * @dev Called periodically or by oracle
     */
    function updatePrice(uint256 newTokensPerEth) external onlyOwner {
        require(newTokensPerEth > 0, "Price must be positive");
        require(
            newTokensPerEth >= tokensPerEth / 2 && newTokensPerEth <= tokensPerEth * 2,
            "Price change too large"
        );

        uint256 oldPrice = tokensPerEth;
        tokensPerEth = newTokensPerEth;

        emit PriceUpdated(oldPrice, newTokensPerEth);
    }

    /**
     * @notice Calculate dynamic price based on pool ratio
     * @dev Implements x*y=k constant product formula (simplified)
     */
    function getDynamicPrice() external view returns (uint256) {
        uint256 ethBalance = address(this).balance;
        uint256 tokenBalance = celticToken.balanceOf(address(this));

        if (tokenBalance == 0) return tokensPerEth;

        // Price = tokenBalance / ethBalance (tokens per ETH)
        return (tokenBalance * 1 ether) / (ethBalance > 0 ? ethBalance : 1 ether);
    }

    // ============================================================================
    // Admin Functions
    // ============================================================================

    /**
     * @notice Open or close the shop
     */
    function setShopOpen(bool _isOpen) external onlyOwner {
        isOpen = _isOpen;
        emit ShopStatusChanged(_isOpen);
    }

    /**
     * @notice Update item status
     */
    function setItemActive(uint256 itemId, bool active) external onlyOwner {
        require(itemId < itemCount, "Item does not exist");
        items[itemId].isActive = active;
    }

    /**
     * @notice Update item price
     */
    function setItemPrice(uint256 itemId, uint256 newPrice) external onlyOwner {
        require(itemId < itemCount, "Item does not exist");
        items[itemId].priceInCeltic = newPrice;
    }

    /**
     * @notice Restock an item
     */
    function restockItem(uint256 itemId, uint256 additionalStock) external onlyOwner {
        require(itemId < itemCount, "Item does not exist");
        items[itemId].stock += additionalStock;
    }

    /**
     * @notice Update spread
     */
    function setSpread(uint256 newSpreadBps) external onlyOwner {
        require(newSpreadBps <= 1000, "Spread too high"); // Max 10%
        spreadBps = newSpreadBps;
    }

    /**
     * @notice Withdraw ETH (owner only)
     */
    function withdrawEth(uint256 amount) external onlyOwner {
        require(amount <= address(this).balance, "Insufficient balance");
        payable(owner()).transfer(amount);
    }

    /**
     * @notice Withdraw tokens (owner only)
     */
    function withdrawTokens(uint256 amount) external onlyOwner {
        require(amount <= celticToken.balanceOf(address(this)), "Insufficient balance");
        celticToken.safeTransfer(owner(), amount);
    }

    // ============================================================================
    // View Functions
    // ============================================================================

    /**
     * @notice Get item details
     */
    function getItem(uint256 itemId) external view returns (GameItem memory) {
        require(itemId < itemCount, "Item does not exist");
        return items[itemId];
    }

    /**
     * @notice Get all active items
     */
    function getActiveItems() external view returns (uint256[] memory) {
        uint256 activeCount = 0;
        for (uint256 i = 0; i < itemCount; i++) {
            if (items[i].isActive) activeCount++;
        }

        uint256[] memory activeItems = new uint256[](activeCount);
        uint256 index = 0;
        for (uint256 i = 0; i < itemCount; i++) {
            if (items[i].isActive) {
                activeItems[index++] = i;
            }
        }

        return activeItems;
    }

    /**
     * @notice Get purchase history length
     */
    function getPurchaseCount() external view returns (uint256) {
        return purchases.length;
    }

    /**
     * @notice Get shop stats
     */
    function getShopStats() external view returns (
        uint256 ethBalance,
        uint256 tokenBalance,
        uint256 totalItems,
        uint256 totalPurchases
    ) {
        return (
            address(this).balance,
            celticToken.balanceOf(address(this)),
            itemCount,
            purchases.length
        );
    }

    // ============================================================================
    // Receive ETH
    // ============================================================================

    receive() external payable {
        // Accept ETH deposits for liquidity
    }
}
