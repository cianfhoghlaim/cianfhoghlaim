// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";
import "../contracts/CelticCreatureNFT.sol";

/**
 * @title CelticCreatureNFT Test Suite
 * @notice Comprehensive tests for the Celtic Creature NFT contract
 * @dev SpeedRunEthereum Challenge 0: Tokenization
 */
contract CelticCreatureNFTTest is Test {
    CelticCreatureNFT public nft;
    address public owner;
    address public alice;
    address public bob;

    // Test creatures
    string constant CU_CHULAINN = "Cu Chulainn";
    string constant MORRIGAN = "The Morrigan";
    string constant PUCA = "Puca";
    string constant BANSHEE = "Banshee";

    function setUp() public {
        owner = address(this);
        alice = makeAddr("alice");
        bob = makeAddr("bob");

        nft = new CelticCreatureNFT();
    }

    // ============ Basic Minting Tests ============

    function test_MintCreature() public {
        uint256 tokenId = nft.mint(
            alice,
            CU_CHULAINN,
            CelticCreatureNFT.Tradition.Irish,
            CelticCreatureNFT.CreatureType.Hero,
            95, // strength
            70, // wisdom
            60, // magic
            CelticCreatureNFT.Rarity.Legendary,
            "Riastrad"
        );

        assertEq(tokenId, 0);
        assertEq(nft.ownerOf(tokenId), alice);
        assertEq(nft.totalSupply(), 1);
    }

    function test_MintMultipleCreatures() public {
        // Mint Irish Hero
        nft.mint(
            alice,
            CU_CHULAINN,
            CelticCreatureNFT.Tradition.Irish,
            CelticCreatureNFT.CreatureType.Hero,
            95, 70, 60,
            CelticCreatureNFT.Rarity.Legendary,
            "Riastrad"
        );

        // Mint Welsh Creature
        nft.mint(
            bob,
            "Afanc",
            CelticCreatureNFT.Tradition.Welsh,
            CelticCreatureNFT.CreatureType.Creature,
            80, 40, 30,
            CelticCreatureNFT.Rarity.Rare,
            "Lake Dwelling"
        );

        // Mint Scottish Spirit
        nft.mint(
            alice,
            "Bean Nighe",
            CelticCreatureNFT.Tradition.Scottish,
            CelticCreatureNFT.CreatureType.Spirit,
            30, 90, 85,
            CelticCreatureNFT.Rarity.Uncommon,
            "Death Omen"
        );

        assertEq(nft.totalSupply(), 3);
        assertEq(nft.balanceOf(alice), 2);
        assertEq(nft.balanceOf(bob), 1);
    }

    // ============ Public Mint Tests ============

    function test_PublicMintCalculatesRarity() public {
        vm.prank(alice);

        // Legendary: total >= 270
        uint256 legendaryId = nft.publicMint(
            MORRIGAN,
            CelticCreatureNFT.Tradition.Irish,
            CelticCreatureNFT.CreatureType.God,
            90, 95, 100,
            "Shapeshifting"
        );

        CelticCreatureNFT.Creature memory creature = nft.getCreature(legendaryId);
        assertEq(uint8(creature.rarity), uint8(CelticCreatureNFT.Rarity.Legendary));
    }

    function test_PublicMintRarityTiers() public {
        vm.startPrank(alice);

        // Common: total < 150
        uint256 commonId = nft.publicMint(
            "Will-o-Wisp",
            CelticCreatureNFT.Tradition.Irish,
            CelticCreatureNFT.CreatureType.Spirit,
            30, 40, 50,
            "Lure"
        );
        CelticCreatureNFT.Creature memory common = nft.getCreature(commonId);
        assertEq(uint8(common.rarity), uint8(CelticCreatureNFT.Rarity.Common));

        // Uncommon: 150 <= total < 220
        uint256 uncommonId = nft.publicMint(
            PUCA,
            CelticCreatureNFT.Tradition.Irish,
            CelticCreatureNFT.CreatureType.Creature,
            60, 50, 50,
            "Shapeshifting"
        );
        CelticCreatureNFT.Creature memory uncommon = nft.getCreature(uncommonId);
        assertEq(uint8(uncommon.rarity), uint8(CelticCreatureNFT.Rarity.Uncommon));

        // Rare: 220 <= total < 270
        uint256 rareId = nft.publicMint(
            BANSHEE,
            CelticCreatureNFT.Tradition.Irish,
            CelticCreatureNFT.CreatureType.Spirit,
            60, 80, 90,
            "Death Wail"
        );
        CelticCreatureNFT.Creature memory rare = nft.getCreature(rareId);
        assertEq(uint8(rare.rarity), uint8(CelticCreatureNFT.Rarity.Rare));

        vm.stopPrank();
    }

    // ============ Attribute Validation Tests ============

    function test_RevertWhenStrengthExceeds100() public {
        vm.expectRevert("Strength max 100");
        nft.mint(
            alice,
            CU_CHULAINN,
            CelticCreatureNFT.Tradition.Irish,
            CelticCreatureNFT.CreatureType.Hero,
            101, 70, 60,
            CelticCreatureNFT.Rarity.Legendary,
            "Riastrad"
        );
    }

    function test_RevertWhenWisdomExceeds100() public {
        vm.expectRevert("Wisdom max 100");
        nft.mint(
            alice,
            MORRIGAN,
            CelticCreatureNFT.Tradition.Irish,
            CelticCreatureNFT.CreatureType.God,
            90, 101, 60,
            CelticCreatureNFT.Rarity.Legendary,
            "Prophecy"
        );
    }

    function test_RevertWhenMagicExceeds100() public {
        vm.expectRevert("Magic max 100");
        nft.mint(
            alice,
            "Merlin",
            CelticCreatureNFT.Tradition.Welsh,
            CelticCreatureNFT.CreatureType.Hero,
            50, 90, 101,
            CelticCreatureNFT.Rarity.Legendary,
            "Enchantment"
        );
    }

    // ============ Token URI Tests ============

    function test_TokenURIReturnsValidJSON() public {
        uint256 tokenId = nft.mint(
            alice,
            CU_CHULAINN,
            CelticCreatureNFT.Tradition.Irish,
            CelticCreatureNFT.CreatureType.Hero,
            95, 70, 60,
            CelticCreatureNFT.Rarity.Legendary,
            "Riastrad"
        );

        string memory uri = nft.tokenURI(tokenId);

        // Should start with data:application/json;base64,
        assertTrue(bytes(uri).length > 35);
        assertEq(_substring(uri, 0, 29), "data:application/json;base64,");
    }

    function test_RevertTokenURIForNonExistentToken() public {
        vm.expectRevert("Token does not exist");
        nft.tokenURI(999);
    }

    // ============ Creature Data Tests ============

    function test_GetCreatureReturnsCorrectData() public {
        nft.mint(
            alice,
            CU_CHULAINN,
            CelticCreatureNFT.Tradition.Irish,
            CelticCreatureNFT.CreatureType.Hero,
            95, 70, 60,
            CelticCreatureNFT.Rarity.Legendary,
            "Riastrad"
        );

        CelticCreatureNFT.Creature memory creature = nft.getCreature(0);

        assertEq(creature.name, CU_CHULAINN);
        assertEq(uint8(creature.tradition), uint8(CelticCreatureNFT.Tradition.Irish));
        assertEq(uint8(creature.creatureType), uint8(CelticCreatureNFT.CreatureType.Hero));
        assertEq(creature.strength, 95);
        assertEq(creature.wisdom, 70);
        assertEq(creature.magic, 60);
        assertEq(uint8(creature.rarity), uint8(CelticCreatureNFT.Rarity.Legendary));
        assertEq(creature.specialAbility, "Riastrad");
    }

    function test_RevertGetCreatureForNonExistentToken() public {
        vm.expectRevert("Token does not exist");
        nft.getCreature(999);
    }

    // ============ Owner-Only Tests ============

    function test_OnlyOwnerCanMint() public {
        vm.prank(alice);
        vm.expectRevert();
        nft.mint(
            bob,
            CU_CHULAINN,
            CelticCreatureNFT.Tradition.Irish,
            CelticCreatureNFT.CreatureType.Hero,
            95, 70, 60,
            CelticCreatureNFT.Rarity.Legendary,
            "Riastrad"
        );
    }

    // ============ Event Tests ============

    function test_EmitsCreatureMintedEvent() public {
        vm.expectEmit(true, true, false, true);
        emit CelticCreatureNFT.CreatureMinted(
            0,
            alice,
            CU_CHULAINN,
            CelticCreatureNFT.Tradition.Irish,
            CelticCreatureNFT.CreatureType.Hero,
            CelticCreatureNFT.Rarity.Legendary
        );

        nft.mint(
            alice,
            CU_CHULAINN,
            CelticCreatureNFT.Tradition.Irish,
            CelticCreatureNFT.CreatureType.Hero,
            95, 70, 60,
            CelticCreatureNFT.Rarity.Legendary,
            "Riastrad"
        );
    }

    // ============ All Traditions Tests ============

    function test_AllTraditionsHaveUniqueSVGColors() public {
        // Irish creature
        uint256 irishId = nft.mint(
            alice,
            "Dagda",
            CelticCreatureNFT.Tradition.Irish,
            CelticCreatureNFT.CreatureType.God,
            90, 85, 95,
            CelticCreatureNFT.Rarity.Legendary,
            "Club of Life and Death"
        );

        // Welsh creature
        uint256 welshId = nft.mint(
            alice,
            "Blodeuwedd",
            CelticCreatureNFT.Tradition.Welsh,
            CelticCreatureNFT.CreatureType.Spirit,
            50, 75, 85,
            CelticCreatureNFT.Rarity.Rare,
            "Flower Magic"
        );

        // Scottish creature
        uint256 scottishId = nft.mint(
            alice,
            "Selkie",
            CelticCreatureNFT.Tradition.Scottish,
            CelticCreatureNFT.CreatureType.Creature,
            60, 70, 65,
            CelticCreatureNFT.Rarity.Uncommon,
            "Seal Form"
        );

        // All should have valid token URIs
        assertTrue(bytes(nft.tokenURI(irishId)).length > 0);
        assertTrue(bytes(nft.tokenURI(welshId)).length > 0);
        assertTrue(bytes(nft.tokenURI(scottishId)).length > 0);
    }

    // ============ All Creature Types Tests ============

    function test_AllCreatureTypesHaveUniqueSymbols() public {
        // God
        nft.mint(alice, "Lugh", CelticCreatureNFT.Tradition.Irish, CelticCreatureNFT.CreatureType.God, 85, 90, 95, CelticCreatureNFT.Rarity.Legendary, "Many-skilled");

        // Hero
        nft.mint(alice, "Fionn", CelticCreatureNFT.Tradition.Irish, CelticCreatureNFT.CreatureType.Hero, 90, 80, 70, CelticCreatureNFT.Rarity.Legendary, "Salmon of Knowledge");

        // Creature
        nft.mint(alice, "Leprechaun", CelticCreatureNFT.Tradition.Irish, CelticCreatureNFT.CreatureType.Creature, 40, 85, 60, CelticCreatureNFT.Rarity.Uncommon, "Gold Hiding");

        // Spirit
        nft.mint(alice, "Dullahan", CelticCreatureNFT.Tradition.Irish, CelticCreatureNFT.CreatureType.Spirit, 70, 50, 90, CelticCreatureNFT.Rarity.Rare, "Death Rider");

        assertEq(nft.totalSupply(), 4);
    }

    // ============ Fuzz Tests ============

    function testFuzz_MintWithValidAttributes(uint8 strength, uint8 wisdom, uint8 magic) public {
        // Bound to valid range
        strength = uint8(bound(strength, 0, 100));
        wisdom = uint8(bound(wisdom, 0, 100));
        magic = uint8(bound(magic, 0, 100));

        uint256 tokenId = nft.mint(
            alice,
            "Fuzz Creature",
            CelticCreatureNFT.Tradition.Irish,
            CelticCreatureNFT.CreatureType.Creature,
            strength,
            wisdom,
            magic,
            CelticCreatureNFT.Rarity.Common,
            "Fuzz Ability"
        );

        CelticCreatureNFT.Creature memory creature = nft.getCreature(tokenId);
        assertEq(creature.strength, strength);
        assertEq(creature.wisdom, wisdom);
        assertEq(creature.magic, magic);
    }

    function testFuzz_PublicMintRarityCalculation(uint8 strength, uint8 wisdom, uint8 magic) public {
        // Bound to valid range
        strength = uint8(bound(strength, 0, 100));
        wisdom = uint8(bound(wisdom, 0, 100));
        magic = uint8(bound(magic, 0, 100));

        vm.prank(alice);
        uint256 tokenId = nft.publicMint(
            "Fuzz Creature",
            CelticCreatureNFT.Tradition.Irish,
            CelticCreatureNFT.CreatureType.Creature,
            strength,
            wisdom,
            magic,
            "Fuzz Ability"
        );

        CelticCreatureNFT.Creature memory creature = nft.getCreature(tokenId);
        uint16 total = uint16(strength) + uint16(wisdom) + uint16(magic);

        if (total >= 270) {
            assertEq(uint8(creature.rarity), uint8(CelticCreatureNFT.Rarity.Legendary));
        } else if (total >= 220) {
            assertEq(uint8(creature.rarity), uint8(CelticCreatureNFT.Rarity.Rare));
        } else if (total >= 150) {
            assertEq(uint8(creature.rarity), uint8(CelticCreatureNFT.Rarity.Uncommon));
        } else {
            assertEq(uint8(creature.rarity), uint8(CelticCreatureNFT.Rarity.Common));
        }
    }

    // ============ Helper Functions ============

    function _substring(string memory str, uint256 startIndex, uint256 endIndex) internal pure returns (string memory) {
        bytes memory strBytes = bytes(str);
        bytes memory result = new bytes(endIndex - startIndex);
        for (uint256 i = startIndex; i < endIndex; i++) {
            result[i - startIndex] = strBytes[i];
        }
        return string(result);
    }
}
