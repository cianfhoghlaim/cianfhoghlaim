// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Enumerable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Base64.sol";
import "@openzeppelin/contracts/utils/Strings.sol";

/**
 * @title CuchulainnNFT
 * @notice Dynamic NFT avatars for the Anam learn-to-earn platform
 * @dev On-chain SVG generation with evolving attributes based on learning progress
 *
 * Character Evolution:
 * - Level 1-5: Sétanta (Young warrior)
 * - Level 6-10: Cúchulainn (The Hound)
 * - Level 11+: Ríastrad (Warp Spasm unlocked)
 *
 * Elements: Fire, Water, Earth, Air, Spirit
 */
contract CuchulainnNFT is ERC721, ERC721Enumerable, Ownable {
    using Strings for uint256;

    // Warrior stats structure
    struct Warrior {
        uint256 level;
        uint256 xp;
        uint256 totalXpEarned;
        Element element;
        bool warpSpasm;      // Unlocked at level 11
        uint256 geisCount;   // Active taboos
        uint256 mintTime;
        string language;     // Primary language (ga, gd, gv, cy, en)
    }

    // Elements aligned with pent-elemental cosmology
    enum Element {
        Fire,    // Tine - Combat/Forge (Brigid)
        Water,   // Uisce - Travel/Inventory (Manannán)
        Earth,   // Talamh - Territory/Defense (Dagda)
        Air,     // Aer - Magic/Governance (Morrígan)
        Spirit   // Anam - Currency/Mentorship (Danu)
    }

    // XP required per level (exponential curve)
    uint256 public constant XP_PER_LEVEL = 1000;
    uint256 public constant XP_MULTIPLIER = 150; // 1.5x per level

    // Counter for token IDs
    uint256 private _tokenIdCounter;

    // Mapping from token ID to warrior data
    mapping(uint256 => Warrior) public warriors;

    // Addresses authorized to grant XP (learning validators)
    mapping(address => bool) public xpGranters;

    // Events
    event WarriorMinted(uint256 indexed tokenId, address indexed owner, Element element, string language);
    event XPGained(uint256 indexed tokenId, uint256 amount, string reason);
    event LevelUp(uint256 indexed tokenId, uint256 newLevel);
    event WarpSpasmUnlocked(uint256 indexed tokenId);
    event GeisAccepted(uint256 indexed tokenId, uint256 geisId);

    constructor() ERC721("Cuchulainn", "CUCH") Ownable(msg.sender) {}

    /**
     * @notice Mint a new warrior NFT
     * @param to Recipient address
     * @param element Chosen element alignment
     * @param language Primary language code
     */
    function mint(address to, Element element, string calldata language) external returns (uint256) {
        uint256 tokenId = _tokenIdCounter++;
        _safeMint(to, tokenId);

        warriors[tokenId] = Warrior({
            level: 1,
            xp: 0,
            totalXpEarned: 0,
            element: element,
            warpSpasm: false,
            geisCount: 0,
            mintTime: block.timestamp,
            language: language
        });

        emit WarriorMinted(tokenId, to, element, language);
        return tokenId;
    }

    /**
     * @notice Grant XP for learning achievements (Proof of Learn)
     * @param tokenId The warrior token
     * @param amount XP amount to grant
     * @param reason Description of achievement
     */
    function grantXP(uint256 tokenId, uint256 amount, string calldata reason) external {
        require(xpGranters[msg.sender] || msg.sender == owner(), "Not authorized");
        require(_ownerOf(tokenId) != address(0), "Token does not exist");

        Warrior storage warrior = warriors[tokenId];
        warrior.xp += amount;
        warrior.totalXpEarned += amount;

        emit XPGained(tokenId, amount, reason);

        // Check for level up
        uint256 xpRequired = _xpForLevel(warrior.level + 1);
        while (warrior.xp >= xpRequired) {
            warrior.xp -= xpRequired;
            warrior.level++;
            emit LevelUp(tokenId, warrior.level);

            // Unlock warp spasm at level 11
            if (warrior.level >= 11 && !warrior.warpSpasm) {
                warrior.warpSpasm = true;
                emit WarpSpasmUnlocked(tokenId);
            }

            xpRequired = _xpForLevel(warrior.level + 1);
        }
    }

    /**
     * @notice Calculate XP required for a specific level
     */
    function _xpForLevel(uint256 level) internal pure returns (uint256) {
        if (level <= 1) return XP_PER_LEVEL;
        // Exponential: base * 1.5^(level-1)
        uint256 xp = XP_PER_LEVEL;
        for (uint256 i = 1; i < level; i++) {
            xp = (xp * XP_MULTIPLIER) / 100;
        }
        return xp;
    }

    /**
     * @notice Get warrior stage name based on level
     */
    function _getStageName(uint256 level) internal pure returns (string memory) {
        if (level >= 11) return "Riastrad";
        if (level >= 6) return "Cuchulainn";
        return "Setanta";
    }

    /**
     * @notice Get element name
     */
    function _getElementName(Element element) internal pure returns (string memory) {
        if (element == Element.Fire) return "Tine";
        if (element == Element.Water) return "Uisce";
        if (element == Element.Earth) return "Talamh";
        if (element == Element.Air) return "Aer";
        return "Anam";
    }

    /**
     * @notice Get element color for SVG
     */
    function _getElementColor(Element element) internal pure returns (string memory) {
        if (element == Element.Fire) return "#FF6B35";
        if (element == Element.Water) return "#4ECDC4";
        if (element == Element.Earth) return "#8B4513";
        if (element == Element.Air) return "#E8E8E8";
        return "#9B59B6"; // Spirit - purple
    }

    /**
     * @notice Generate on-chain SVG for the warrior
     */
    function _generateSVG(uint256 tokenId) internal view returns (string memory) {
        Warrior memory w = warriors[tokenId];
        string memory color = _getElementColor(w.element);
        string memory stage = _getStageName(w.level);

        // Celtic knot pattern complexity increases with level
        string memory knotComplexity = w.level >= 11 ? "complex" : (w.level >= 6 ? "medium" : "simple");

        return string(abi.encodePacked(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400">',
            '<defs>',
            '<linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">',
            '<stop offset="0%" style="stop-color:#1a1a2e"/>',
            '<stop offset="100%" style="stop-color:#16213e"/>',
            '</linearGradient>',
            '</defs>',
            '<rect width="400" height="400" fill="url(#bg)"/>',
            // Celtic border
            '<rect x="10" y="10" width="380" height="380" fill="none" stroke="', color, '" stroke-width="3"/>',
            '<rect x="20" y="20" width="360" height="360" fill="none" stroke="', color, '" stroke-width="1" opacity="0.5"/>',
            // Warrior silhouette
            '<circle cx="200" cy="150" r="50" fill="', color, '" opacity="0.8"/>',
            '<ellipse cx="200" cy="280" rx="60" ry="80" fill="', color, '" opacity="0.6"/>',
            // Level indicator
            '<text x="200" y="380" text-anchor="middle" fill="', color, '" font-family="serif" font-size="24">', stage, '</text>',
            '<text x="200" y="50" text-anchor="middle" fill="#gold" font-family="serif" font-size="18">Level ', w.level.toString(), '</text>',
            // Warp spasm glow effect
            w.warpSpasm ? '<circle cx="200" cy="200" r="150" fill="none" stroke="#FF0000" stroke-width="2" opacity="0.5"><animate attributeName="r" values="150;170;150" dur="2s" repeatCount="indefinite"/></circle>' : '',
            '</svg>'
        ));
    }

    /**
     * @notice Generate token URI with on-chain metadata
     */
    function tokenURI(uint256 tokenId) public view override returns (string memory) {
        require(_ownerOf(tokenId) != address(0), "Token does not exist");

        Warrior memory w = warriors[tokenId];
        string memory svg = _generateSVG(tokenId);
        string memory stage = _getStageName(w.level);
        string memory elementName = _getElementName(w.element);

        string memory json = Base64.encode(bytes(string(abi.encodePacked(
            '{"name":"', stage, ' #', tokenId.toString(), '",',
            '"description":"A warrior of the Anam realm, aligned with ', elementName, '",',
            '"attributes":[',
            '{"trait_type":"Level","value":', w.level.toString(), '},',
            '{"trait_type":"Element","value":"', elementName, '"},',
            '{"trait_type":"Stage","value":"', stage, '"},',
            '{"trait_type":"Language","value":"', w.language, '"},',
            '{"trait_type":"Warp Spasm","value":"', w.warpSpasm ? "Unlocked" : "Locked", '"},',
            '{"trait_type":"Total XP","value":', w.totalXpEarned.toString(), '}',
            '],',
            '"image":"data:image/svg+xml;base64,', Base64.encode(bytes(svg)), '"}'
        ))));

        return string(abi.encodePacked("data:application/json;base64,", json));
    }

    // Admin functions
    function addXPGranter(address granter) external onlyOwner {
        xpGranters[granter] = true;
    }

    function removeXPGranter(address granter) external onlyOwner {
        xpGranters[granter] = false;
    }

    // Required overrides
    function _update(address to, uint256 tokenId, address auth)
        internal
        override(ERC721, ERC721Enumerable)
        returns (address)
    {
        return super._update(to, tokenId, auth);
    }

    function _increaseBalance(address account, uint128 value)
        internal
        override(ERC721, ERC721Enumerable)
    {
        super._increaseBalance(account, value);
    }

    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(ERC721, ERC721Enumerable)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }
}
