// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Script.sol";
import "../contracts/CelticCreatureNFT.sol";

/**
 * @title DeployCelticNFT
 * @notice Deployment script for Celtic Creature NFT
 * @dev SpeedRunEthereum Challenge 0: Tokenization
 *
 * Usage:
 *   # Deploy to Anvil (local)
 *   forge script script/DeployCelticNFT.s.sol --rpc-url anvil --broadcast
 *
 *   # Deploy to Base Sepolia testnet
 *   forge script script/DeployCelticNFT.s.sol --rpc-url base_sepolia --broadcast --verify
 *
 *   # Deploy to Sepolia testnet
 *   forge script script/DeployCelticNFT.s.sol --rpc-url sepolia --broadcast --verify
 */
contract DeployCelticNFT is Script {
    // Starter creatures to mint upon deployment
    struct StarterCreature {
        string name;
        CelticCreatureNFT.Tradition tradition;
        CelticCreatureNFT.CreatureType creatureType;
        uint8 strength;
        uint8 wisdom;
        uint8 magic;
        CelticCreatureNFT.Rarity rarity;
        string specialAbility;
    }

    function run() external {
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        address deployer = vm.addr(deployerPrivateKey);

        console.log("Deploying CelticCreatureNFT...");
        console.log("Deployer:", deployer);

        vm.startBroadcast(deployerPrivateKey);

        // Deploy the NFT contract
        CelticCreatureNFT nft = new CelticCreatureNFT();
        console.log("CelticCreatureNFT deployed at:", address(nft));

        // Mint starter creatures for the deployer (game initialization)
        _mintStarterCreatures(nft, deployer);

        vm.stopBroadcast();

        console.log("Deployment complete!");
        console.log("Total supply:", nft.totalSupply());
    }

    function _mintStarterCreatures(CelticCreatureNFT nft, address to) internal {
        // Irish God: The Dagda
        nft.mint(
            to,
            "The Dagda",
            CelticCreatureNFT.Tradition.Irish,
            CelticCreatureNFT.CreatureType.God,
            90, 85, 95,
            CelticCreatureNFT.Rarity.Legendary,
            "Club of Life and Death"
        );
        console.log("Minted: The Dagda (Irish God)");

        // Irish Hero: Cu Chulainn
        nft.mint(
            to,
            "Cu Chulainn",
            CelticCreatureNFT.Tradition.Irish,
            CelticCreatureNFT.CreatureType.Hero,
            100, 70, 60,
            CelticCreatureNFT.Rarity.Legendary,
            "Riastrad"
        );
        console.log("Minted: Cu Chulainn (Irish Hero)");

        // Welsh Hero: Taliesin
        nft.mint(
            to,
            "Taliesin",
            CelticCreatureNFT.Tradition.Welsh,
            CelticCreatureNFT.CreatureType.Hero,
            50, 95, 90,
            CelticCreatureNFT.Rarity.Legendary,
            "Prophetic Poetry"
        );
        console.log("Minted: Taliesin (Welsh Hero)");

        // Scottish Creature: Selkie
        nft.mint(
            to,
            "Selkie",
            CelticCreatureNFT.Tradition.Scottish,
            CelticCreatureNFT.CreatureType.Creature,
            60, 70, 65,
            CelticCreatureNFT.Rarity.Uncommon,
            "Seal Transformation"
        );
        console.log("Minted: Selkie (Scottish Creature)");

        // Irish Spirit: Banshee
        nft.mint(
            to,
            "Banshee",
            CelticCreatureNFT.Tradition.Irish,
            CelticCreatureNFT.CreatureType.Spirit,
            40, 80, 90,
            CelticCreatureNFT.Rarity.Rare,
            "Death Wail"
        );
        console.log("Minted: Banshee (Irish Spirit)");

        // Irish Creature: Puca
        nft.mint(
            to,
            "Puca",
            CelticCreatureNFT.Tradition.Irish,
            CelticCreatureNFT.CreatureType.Creature,
            70, 60, 75,
            CelticCreatureNFT.Rarity.Uncommon,
            "Shapeshifting"
        );
        console.log("Minted: Puca (Irish Creature)");
    }
}

/**
 * @title MintCreature
 * @notice Script to mint a single creature (for game operations)
 */
contract MintCreature is Script {
    function run() external {
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        address nftAddress = vm.envAddress("NFT_ADDRESS");
        address recipient = vm.envAddress("RECIPIENT");
        string memory name = vm.envString("CREATURE_NAME");

        CelticCreatureNFT nft = CelticCreatureNFT(nftAddress);

        vm.startBroadcast(deployerPrivateKey);

        // Default creature for quick testing
        uint256 tokenId = nft.mint(
            recipient,
            name,
            CelticCreatureNFT.Tradition.Irish,
            CelticCreatureNFT.CreatureType.Creature,
            50, 50, 50,
            CelticCreatureNFT.Rarity.Common,
            "Test Ability"
        );

        vm.stopBroadcast();

        console.log("Minted token ID:", tokenId);
        console.log("To:", recipient);
    }
}
