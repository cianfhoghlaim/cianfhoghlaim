// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";
import "../contracts/CelticShop.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

/**
 * @title Mock CELTIC Token for testing
 */
contract MockCelticToken is ERC20 {
    constructor() ERC20("Celtic Token", "CELTIC") {
        _mint(msg.sender, 1_000_000 ether);
    }

    function mint(address to, uint256 amount) external {
        _mint(to, amount);
    }
}

/**
 * @title CelticShop Test Suite
 * @notice Comprehensive tests for the in-game token vendor
 * @dev SpeedRunEthereum Challenge 2: Token Vendor
 */
contract CelticShopTest is Test {
    CelticShop public shop;
    MockCelticToken public token;

    address public owner;
    address public alice;
    address public bob;

    uint256 constant INITIAL_SHOP_TOKENS = 100_000 ether;
    uint256 constant INITIAL_SHOP_ETH = 10 ether;

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

    function setUp() public {
        owner = address(this);
        alice = makeAddr("alice");
        bob = makeAddr("bob");

        // Deploy token
        token = new MockCelticToken();

        // Deploy shop
        shop = new CelticShop(address(token));

        // Fund shop with tokens and ETH
        token.transfer(address(shop), INITIAL_SHOP_TOKENS);
        vm.deal(address(shop), INITIAL_SHOP_ETH);

        // Fund users
        vm.deal(alice, 100 ether);
        vm.deal(bob, 100 ether);
        token.mint(alice, 10_000 ether);
        token.mint(bob, 10_000 ether);

        // Approve shop for token transfers
        vm.prank(alice);
        token.approve(address(shop), type(uint256).max);

        vm.prank(bob);
        token.approve(address(shop), type(uint256).max);
    }

    // ============ Token Exchange Tests ============

    function test_BuyTokens() public {
        uint256 ethAmount = 1 ether;
        uint256 expectedTokens = shop.getTokensForEth(ethAmount);

        vm.prank(alice);
        vm.expectEmit(true, false, false, true);
        emit TokensPurchased(alice, ethAmount, expectedTokens, block.timestamp);
        shop.buyTokens{value: ethAmount}();

        assertEq(token.balanceOf(alice), 10_000 ether + expectedTokens);
    }

    function test_BuyTokensWithSpread() public {
        // Default rate is 1000 tokens per ETH with 1% spread
        // So for 1 ETH: 1000 * 0.99 = 990 tokens
        uint256 expectedTokens = shop.getTokensForEth(1 ether);
        assertEq(expectedTokens, 990 ether);

        vm.prank(alice);
        shop.buyTokens{value: 1 ether}();

        assertEq(token.balanceOf(alice), 10_000 ether + 990 ether);
    }

    function test_SellTokens() public {
        uint256 tokenAmount = 1000 ether;
        uint256 expectedEth = shop.getEthForTokens(tokenAmount);

        uint256 ethBefore = alice.balance;

        vm.prank(alice);
        vm.expectEmit(true, false, false, true);
        emit TokensSold(alice, tokenAmount, expectedEth, block.timestamp);
        shop.sellTokens(tokenAmount);

        assertEq(alice.balance, ethBefore + expectedEth);
        assertEq(token.balanceOf(alice), 10_000 ether - tokenAmount);
    }

    function test_SellTokensWithSpread() public {
        // For 1000 tokens at 1000/ETH with 1% spread:
        // sell_rate = 1000 * 1.01 = 1010
        // eth = 1000 tokens / 1010 = ~0.99 ETH
        uint256 expectedEth = shop.getEthForTokens(1000 ether);

        vm.prank(alice);
        uint256 ethBefore = alice.balance;
        shop.sellTokens(1000 ether);

        assertEq(alice.balance - ethBefore, expectedEth);
        assertTrue(expectedEth < 1 ether); // Less due to spread
    }

    function test_RevertBuyWithZeroEth() public {
        vm.prank(alice);
        vm.expectRevert("Must send ETH");
        shop.buyTokens{value: 0}();
    }

    function test_RevertSellZeroTokens() public {
        vm.prank(alice);
        vm.expectRevert("Must sell tokens");
        shop.sellTokens(0);
    }

    function test_RevertBuyWhenShopClosed() public {
        shop.setShopOpen(false);

        vm.prank(alice);
        vm.expectRevert("Shop is closed");
        shop.buyTokens{value: 1 ether}();
    }

    function test_RevertSellWhenShopClosed() public {
        shop.setShopOpen(false);

        vm.prank(alice);
        vm.expectRevert("Shop is closed");
        shop.sellTokens(100 ether);
    }

    function test_RevertBuyInsufficientShopBalance() public {
        // Try to buy more tokens than shop has
        uint256 shopBalance = token.balanceOf(address(shop));
        uint256 tokensPerEth = shop.tokensPerEth();
        uint256 hugeEthAmount = (shopBalance / tokensPerEth) * 2;

        vm.deal(alice, hugeEthAmount);
        vm.prank(alice);
        vm.expectRevert("Insufficient shop balance");
        shop.buyTokens{value: hugeEthAmount}();
    }

    function test_RevertSellInsufficientEthInShop() public {
        // Try to sell more tokens than shop can pay for
        uint256 shopEth = address(shop).balance;
        uint256 tokensPerEth = shop.tokensPerEth();
        uint256 hugeTokenAmount = shopEth * tokensPerEth * 2;

        token.mint(alice, hugeTokenAmount);
        vm.prank(alice);
        token.approve(address(shop), hugeTokenAmount);

        vm.prank(alice);
        vm.expectRevert("Insufficient ETH in shop");
        shop.sellTokens(hugeTokenAmount);
    }

    // ============ Item Shop Tests ============

    function test_AddItem() public {
        vm.expectEmit(true, false, false, true);
        emit ItemAdded(0, unicode"Claíomh Solais", "weapon", 500 ether);

        uint256 itemId = shop.addItem(
            unicode"Claíomh Solais",
            "weapon",
            500 ether,
            10,
            "ipfs://..."
        );

        assertEq(itemId, 0);
        assertEq(shop.itemCount(), 1);

        CelticShop.GameItem memory item = shop.getItem(0);
        assertEq(item.name, unicode"Claíomh Solais");
        assertEq(item.category, "weapon");
        assertEq(item.priceInCeltic, 500 ether);
        assertEq(item.stock, 10);
        assertTrue(item.isActive);
    }

    function test_PurchaseItem() public {
        // Add item
        shop.addItem("Sword", "weapon", 100 ether, 10, "ipfs://...");

        uint256 tokensBefore = token.balanceOf(alice);

        vm.prank(alice);
        vm.expectEmit(true, true, false, true);
        emit ItemPurchased(alice, 0, 100 ether, block.timestamp);
        shop.purchaseItem(0, 1);

        // Check token spent
        assertEq(token.balanceOf(alice), tokensBefore - 100 ether);

        // Check inventory
        assertEq(shop.getInventory(alice, 0), 1);

        // Check stock decreased
        CelticShop.GameItem memory item = shop.getItem(0);
        assertEq(item.stock, 9);
    }

    function test_PurchaseMultipleItems() public {
        shop.addItem("Potion", "consumable", 10 ether, 100, "ipfs://...");

        vm.prank(alice);
        shop.purchaseItem(0, 5);

        assertEq(shop.getInventory(alice, 0), 5);

        CelticShop.GameItem memory item = shop.getItem(0);
        assertEq(item.stock, 95);
    }

    function test_PurchaseUnlimitedStockItem() public {
        // Stock = 0 means unlimited
        shop.addItem("Digital Badge", "cosmetic", 50 ether, 0, "ipfs://...");

        vm.prank(alice);
        shop.purchaseItem(0, 100);

        assertEq(shop.getInventory(alice, 0), 100);
    }

    function test_RevertPurchaseInactiveItem() public {
        shop.addItem("Old Item", "weapon", 100 ether, 10, "ipfs://...");
        shop.setItemActive(0, false);

        vm.prank(alice);
        vm.expectRevert("Item not available");
        shop.purchaseItem(0, 1);
    }

    function test_RevertPurchaseInsufficientStock() public {
        shop.addItem("Rare Item", "weapon", 100 ether, 2, "ipfs://...");

        vm.prank(alice);
        vm.expectRevert("Insufficient stock");
        shop.purchaseItem(0, 5);
    }

    function test_RevertPurchaseZeroQuantity() public {
        shop.addItem("Item", "weapon", 100 ether, 10, "ipfs://...");

        vm.prank(alice);
        vm.expectRevert("Must buy at least 1");
        shop.purchaseItem(0, 0);
    }

    function test_PurchaseHistory() public {
        shop.addItem("Item1", "weapon", 100 ether, 10, "ipfs://1");
        shop.addItem("Item2", "armor", 200 ether, 10, "ipfs://2");

        vm.startPrank(alice);
        shop.purchaseItem(0, 1);
        shop.purchaseItem(1, 2);
        vm.stopPrank();

        assertEq(shop.getPurchaseCount(), 2);

        (uint256 itemId, address buyer, uint256 price, ) = shop.purchases(0);
        assertEq(itemId, 0);
        assertEq(buyer, alice);
        assertEq(price, 100 ether);
    }

    // ============ Pricing Tests ============

    function test_GetBuyPrice() public view {
        uint256 buyPrice = shop.getBuyPrice();
        // With 1% spread, buyer gets 990 tokens per ETH
        assertEq(buyPrice, 990 ether);
    }

    function test_GetSellPrice() public view {
        uint256 sellPrice = shop.getSellPrice();
        // With 1% spread, seller gets ~0.99 ETH per 1000 tokens
        assertTrue(sellPrice < 1 ether);
    }

    function test_GetDynamicPrice() public view {
        uint256 dynamicPrice = shop.getDynamicPrice();
        // Should reflect current pool ratio
        assertTrue(dynamicPrice > 0);
    }

    // ============ Admin Tests ============

    function test_UpdatePrice() public {
        uint256 oldPrice = shop.tokensPerEth();
        uint256 newPrice = 1500;

        shop.updatePrice(newPrice);

        assertEq(shop.tokensPerEth(), newPrice);
    }

    function test_RevertPriceChangeTooLarge() public {
        uint256 oldPrice = shop.tokensPerEth(); // 1000

        // Try to set price > 2x
        vm.expectRevert("Price change too large");
        shop.updatePrice(oldPrice * 3);

        // Try to set price < 0.5x
        vm.expectRevert("Price change too large");
        shop.updatePrice(oldPrice / 3);
    }

    function test_SetSpread() public {
        shop.setSpread(200); // 2%
        assertEq(shop.spreadBps(), 200);
    }

    function test_RevertSpreadTooHigh() public {
        vm.expectRevert("Spread too high");
        shop.setSpread(1001); // > 10%
    }

    function test_SetShopOpen() public {
        shop.setShopOpen(false);
        assertFalse(shop.isOpen());

        shop.setShopOpen(true);
        assertTrue(shop.isOpen());
    }

    function test_SetItemPrice() public {
        shop.addItem("Item", "weapon", 100 ether, 10, "ipfs://...");

        shop.setItemPrice(0, 200 ether);

        CelticShop.GameItem memory item = shop.getItem(0);
        assertEq(item.priceInCeltic, 200 ether);
    }

    function test_RestockItem() public {
        shop.addItem("Item", "weapon", 100 ether, 10, "ipfs://...");

        shop.restockItem(0, 5);

        CelticShop.GameItem memory item = shop.getItem(0);
        assertEq(item.stock, 15);
    }

    function test_WithdrawEth() public {
        uint256 ownerBalanceBefore = owner.balance;
        uint256 withdrawAmount = 5 ether;

        shop.withdrawEth(withdrawAmount);

        assertEq(owner.balance, ownerBalanceBefore + withdrawAmount);
        assertEq(address(shop).balance, INITIAL_SHOP_ETH - withdrawAmount);
    }

    function test_WithdrawTokens() public {
        uint256 ownerBalanceBefore = token.balanceOf(owner);
        uint256 withdrawAmount = 1000 ether;

        shop.withdrawTokens(withdrawAmount);

        assertEq(token.balanceOf(owner), ownerBalanceBefore + withdrawAmount);
    }

    function test_RevertNonOwnerAdmin() public {
        vm.prank(alice);
        vm.expectRevert();
        shop.setShopOpen(false);

        vm.prank(alice);
        vm.expectRevert();
        shop.addItem("Item", "weapon", 100 ether, 10, "ipfs://...");
    }

    // ============ View Function Tests ============

    function test_GetActiveItems() public {
        shop.addItem("Item1", "weapon", 100 ether, 10, "ipfs://1");
        shop.addItem("Item2", "armor", 200 ether, 10, "ipfs://2");
        shop.addItem("Item3", "consumable", 50 ether, 10, "ipfs://3");

        // Deactivate middle item
        shop.setItemActive(1, false);

        uint256[] memory activeItems = shop.getActiveItems();

        assertEq(activeItems.length, 2);
        assertEq(activeItems[0], 0);
        assertEq(activeItems[1], 2);
    }

    function test_GetShopStats() public {
        shop.addItem("Item", "weapon", 100 ether, 10, "ipfs://...");

        vm.prank(alice);
        shop.purchaseItem(0, 2);

        (
            uint256 ethBalance,
            uint256 tokenBalance,
            uint256 totalItems,
            uint256 totalPurchases
        ) = shop.getShopStats();

        assertEq(ethBalance, INITIAL_SHOP_ETH);
        assertEq(tokenBalance, INITIAL_SHOP_TOKENS + 200 ether); // Received from purchase
        assertEq(totalItems, 1);
        assertEq(totalPurchases, 1);
    }

    // ============ Receive ETH Tests ============

    function test_ReceiveEth() public {
        uint256 balanceBefore = address(shop).balance;

        (bool success,) = address(shop).call{value: 1 ether}("");
        assertTrue(success);

        assertEq(address(shop).balance, balanceBefore + 1 ether);
    }

    // ============ Fuzz Tests ============

    function testFuzz_BuyTokens(uint256 ethAmount) public {
        ethAmount = bound(ethAmount, 0.001 ether, 10 ether);

        uint256 expectedTokens = shop.getTokensForEth(ethAmount);

        vm.prank(alice);
        shop.buyTokens{value: ethAmount}();

        assertEq(token.balanceOf(alice), 10_000 ether + expectedTokens);
    }

    function testFuzz_SellTokens(uint256 tokenAmount) public {
        tokenAmount = bound(tokenAmount, 1 ether, 5_000 ether);

        uint256 expectedEth = shop.getEthForTokens(tokenAmount);

        // Skip if not enough ETH in shop
        vm.assume(expectedEth <= address(shop).balance);

        vm.prank(alice);
        uint256 ethBefore = alice.balance;
        shop.sellTokens(tokenAmount);

        assertEq(alice.balance - ethBefore, expectedEth);
    }

    function testFuzz_SpreadConsistency(uint256 ethAmount) public {
        ethAmount = bound(ethAmount, 0.1 ether, 1 ether);

        // Buy tokens
        vm.prank(alice);
        shop.buyTokens{value: ethAmount}();

        uint256 tokensReceived = token.balanceOf(alice) - 10_000 ether;

        // Sell tokens back
        vm.prank(alice);
        uint256 ethBefore = alice.balance;
        shop.sellTokens(tokensReceived);
        uint256 ethReceived = alice.balance - ethBefore;

        // Should receive less ETH due to double spread
        assertTrue(ethReceived < ethAmount);

        // Loss should be approximately 2% (spread applied twice)
        uint256 loss = ethAmount - ethReceived;
        uint256 expectedLoss = ethAmount * 200 / 10000; // ~2%
        assertApproxEqRel(loss, expectedLoss, 0.1e18); // 10% tolerance
    }

    function testFuzz_ItemPurchase(uint256 quantity) public {
        quantity = bound(quantity, 1, 50);

        shop.addItem("Item", "weapon", 10 ether, 100, "ipfs://...");

        uint256 totalCost = 10 ether * quantity;
        vm.assume(token.balanceOf(alice) >= totalCost);

        vm.prank(alice);
        shop.purchaseItem(0, uint256(quantity));

        assertEq(shop.getInventory(alice, 0), quantity);
    }
}
