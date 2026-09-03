// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Base64.sol";
import "@openzeppelin/contracts/utils/Strings.sol";

/**
 * @title CelticCreatureNFT
 * @author Cianfhoghlaim / tuath project
 * @notice Celtic mythology-themed NFT for the tuath educational MMO
 * @dev SpeedRunEthereum Challenge 0: Tokenization
 *
 * Features:
 * - On-chain SVG generation
 * - Creature attributes (strength, wisdom, magic)
 * - Three Celtic traditions (Irish, Welsh, Scottish)
 * - Four creature types (God, Hero, Creature, Spirit)
 */
contract CelticCreatureNFT is ERC721URIStorage, Ownable {
    using Strings for uint256;
    using Strings for uint8;

    uint256 private _nextTokenId;

    // Celtic traditions
    enum Tradition {
        Irish,    // 0
        Welsh,    // 1
        Scottish  // 2
    }

    // Creature categories
    enum CreatureType {
        God,      // 0 - Tuatha Dé Danann, etc.
        Hero,     // 1 - Cú Chulainn, Fionn, etc.
        Creature, // 2 - Púca, Selkie, etc.
        Spirit    // 3 - Banshee, Will-o'-wisp, etc.
    }

    // Rarity levels
    enum Rarity {
        Common,    // 0
        Uncommon,  // 1
        Rare,      // 2
        Legendary  // 3
    }

    // Creature attributes stored on-chain
    struct Creature {
        string name;           // Mythological name
        Tradition tradition;   // Celtic tradition
        CreatureType creatureType;
        uint8 strength;        // 0-100
        uint8 wisdom;          // 0-100
        uint8 magic;           // 0-100
        Rarity rarity;
        string specialAbility; // e.g., "Ríastrad"
    }

    // Token ID => Creature data
    mapping(uint256 => Creature) public creatures;

    // Events
    event CreatureMinted(
        uint256 indexed tokenId,
        address indexed owner,
        string name,
        Tradition tradition,
        CreatureType creatureType,
        Rarity rarity
    );

    event CreatureAttributesUpdated(
        uint256 indexed tokenId,
        uint8 strength,
        uint8 wisdom,
        uint8 magic
    );

    constructor() ERC721("Celtic Creatures", "CELTIC") Ownable(msg.sender) {}

    /**
     * @notice Mint a new Celtic creature NFT
     * @param to Recipient address
     * @param name Creature's mythological name
     * @param tradition Celtic tradition (Irish, Welsh, Scottish)
     * @param creatureType Category (God, Hero, Creature, Spirit)
     * @param strength Strength attribute (0-100)
     * @param wisdom Wisdom attribute (0-100)
     * @param magic Magic attribute (0-100)
     * @param rarity Rarity level
     * @param specialAbility Special ability name
     */
    function mint(
        address to,
        string memory name,
        Tradition tradition,
        CreatureType creatureType,
        uint8 strength,
        uint8 wisdom,
        uint8 magic,
        Rarity rarity,
        string memory specialAbility
    ) public onlyOwner returns (uint256) {
        require(strength <= 100, "Strength max 100");
        require(wisdom <= 100, "Wisdom max 100");
        require(magic <= 100, "Magic max 100");

        uint256 tokenId = _nextTokenId++;

        creatures[tokenId] = Creature({
            name: name,
            tradition: tradition,
            creatureType: creatureType,
            strength: strength,
            wisdom: wisdom,
            magic: magic,
            rarity: rarity,
            specialAbility: specialAbility
        });

        _safeMint(to, tokenId);

        emit CreatureMinted(
            tokenId,
            to,
            name,
            tradition,
            creatureType,
            rarity
        );

        return tokenId;
    }

    /**
     * @notice Public mint with default rarity calculation
     */
    function publicMint(
        string memory name,
        Tradition tradition,
        CreatureType creatureType,
        uint8 strength,
        uint8 wisdom,
        uint8 magic,
        string memory specialAbility
    ) public returns (uint256) {
        // Calculate rarity based on total attributes
        uint16 total = uint16(strength) + uint16(wisdom) + uint16(magic);
        Rarity rarity;

        if (total >= 270) {
            rarity = Rarity.Legendary;
        } else if (total >= 220) {
            rarity = Rarity.Rare;
        } else if (total >= 150) {
            rarity = Rarity.Uncommon;
        } else {
            rarity = Rarity.Common;
        }

        return mint(
            msg.sender,
            name,
            tradition,
            creatureType,
            strength,
            wisdom,
            magic,
            rarity,
            specialAbility
        );
    }

    /**
     * @notice Get fully on-chain token URI with SVG
     */
    function tokenURI(uint256 tokenId) public view override returns (string memory) {
        require(_ownerOf(tokenId) != address(0), "Token does not exist");

        Creature memory c = creatures[tokenId];
        string memory svg = _generateSVG(c);

        string memory json = Base64.encode(bytes(string(abi.encodePacked(
            '{"name":"', c.name, '",',
            '"description":"Celtic Creature from the tuath educational MMO. A ', _typeName(c.creatureType), ' from ', _traditionName(c.tradition), ' mythology.",',
            '"attributes":[',
                '{"trait_type":"Tradition","value":"', _traditionName(c.tradition), '"},',
                '{"trait_type":"Type","value":"', _typeName(c.creatureType), '"},',
                '{"trait_type":"Rarity","value":"', _rarityName(c.rarity), '"},',
                '{"trait_type":"Strength","value":', c.strength.toString(), '},',
                '{"trait_type":"Wisdom","value":', c.wisdom.toString(), '},',
                '{"trait_type":"Magic","value":', c.magic.toString(), '},',
                '{"trait_type":"Special Ability","value":"', c.specialAbility, '"}',
            '],',
            '"image":"data:image/svg+xml;base64,', Base64.encode(bytes(svg)), '"}'
        ))));

        return string(abi.encodePacked("data:application/json;base64,", json));
    }

    /**
     * @dev Generate on-chain SVG artwork for creature
     */
    function _generateSVG(Creature memory c) internal pure returns (string memory) {
        // Color schemes by tradition
        string memory primaryColor;
        string memory secondaryColor;

        if (c.tradition == Tradition.Irish) {
            primaryColor = "#228B22"; // Forest green
            secondaryColor = "#FFD700"; // Gold
        } else if (c.tradition == Tradition.Welsh) {
            primaryColor = "#C41E3A"; // Cardinal red
            secondaryColor = "#FFFFFF"; // White
        } else {
            primaryColor = "#0065BF"; // Scottish blue
            secondaryColor = "#FFFFFF"; // White
        }

        // Type symbols
        string memory symbol;
        if (c.creatureType == CreatureType.God) {
            symbol = '<path d="M50,15 L55,35 L75,35 L60,48 L67,68 L50,55 L33,68 L40,48 L25,35 L45,35 Z" fill="none" stroke-width="2"/>';
        } else if (c.creatureType == CreatureType.Hero) {
            symbol = '<path d="M50,15 L50,65 M35,30 L65,30 M30,45 L70,45" fill="none" stroke-width="3"/>';
        } else if (c.creatureType == CreatureType.Creature) {
            symbol = '<ellipse cx="50" cy="40" rx="25" ry="20" fill="none" stroke-width="2"/>';
        } else {
            symbol = '<path d="M50,15 Q35,30 50,45 Q65,30 50,15 M50,45 Q40,60 50,70 Q60,60 50,45" fill="none" stroke-width="2"/>';
        }

        // Attribute bar widths (scaled to 80px max)
        string memory strWidth = uint256(c.strength * 80 / 100).toString();
        string memory wisWidth = uint256(c.wisdom * 80 / 100).toString();
        string memory magWidth = uint256(c.magic * 80 / 100).toString();

        return string(abi.encodePacked(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 120">',
            '<defs>',
                '<linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">',
                    '<stop offset="0%" style="stop-color:#1a1a2e"/>',
                    '<stop offset="100%" style="stop-color:#16213e"/>',
                '</linearGradient>',
            '</defs>',
            '<rect width="100" height="120" fill="url(#bg)"/>',
            '<rect x="3" y="3" width="94" height="114" fill="none" stroke="', primaryColor, '" stroke-width="2"/>',
            '<rect x="6" y="6" width="88" height="108" fill="none" stroke="', secondaryColor, '" stroke-width="1" opacity="0.5"/>',
            '<g stroke="', secondaryColor, '" transform="translate(0,5)">', symbol, '</g>',
            '<text x="50" y="82" text-anchor="middle" fill="', secondaryColor, '" font-family="Georgia,serif" font-size="7" font-weight="bold">', c.name, '</text>',
            '<text x="50" y="92" text-anchor="middle" fill="', primaryColor, '" font-family="Arial,sans-serif" font-size="5">', _typeName(c.creatureType), ' - ', _traditionName(c.tradition), '</text>',
            '<g transform="translate(10,100)">',
                '<rect x="0" y="0" width="', strWidth, '" height="4" fill="#FF6B6B" rx="1"/>',
                '<rect x="0" y="5" width="', wisWidth, '" height="4" fill="#4ECDC4" rx="1"/>',
                '<rect x="0" y="10" width="', magWidth, '" height="4" fill="#A855F7" rx="1"/>',
            '</g>',
            '</svg>'
        ));
    }

    function _traditionName(Tradition t) internal pure returns (string memory) {
        if (t == Tradition.Irish) return "Irish";
        if (t == Tradition.Welsh) return "Welsh";
        return "Scottish";
    }

    function _typeName(CreatureType t) internal pure returns (string memory) {
        if (t == CreatureType.God) return "God";
        if (t == CreatureType.Hero) return "Hero";
        if (t == CreatureType.Creature) return "Creature";
        return "Spirit";
    }

    function _rarityName(Rarity r) internal pure returns (string memory) {
        if (r == Rarity.Common) return "Common";
        if (r == Rarity.Uncommon) return "Uncommon";
        if (r == Rarity.Rare) return "Rare";
        return "Legendary";
    }

    /**
     * @notice Get creature data
     */
    function getCreature(uint256 tokenId) public view returns (Creature memory) {
        require(_ownerOf(tokenId) != address(0), "Token does not exist");
        return creatures[tokenId];
    }

    /**
     * @notice Total supply of minted tokens
     */
    function totalSupply() public view returns (uint256) {
        return _nextTokenId;
    }
}
