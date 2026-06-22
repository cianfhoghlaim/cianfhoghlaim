// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/access/Ownable.sol";
import "./TuathToken.sol";

/**
 * @title AnamCaraDAO
 * @notice Soul Friend mentorship system for the Anam platform
 * @dev Implements the Celtic "Anam Cara" concept where mentors guide acolytes
 *
 * Mentorship Mechanics:
 * - Mentors bond with Acolytes (new learners)
 * - Acolytes share a "Soul Tithe" (% of earnings) with their Mentor
 * - Both gain reputation from successful mentorship
 */
contract AnamCaraDAO is Ownable {
    // Soul Bond structure
    struct SoulBond {
        address mentor;
        address acolyte;
        uint256 bondTime;
        uint256 soulTitheRate;    // Basis points (100 = 1%)
        uint256 totalTithePaid;
        bool active;
    }

    // Mentor profile
    struct MentorProfile {
        uint256 soulLevel;         // Reputation score
        uint256 totalAcolytes;     // Lifetime acolytes mentored
        uint256 activeAcolytes;    // Current acolytes
        uint256 totalTitheEarned;  // Lifetime earnings from mentorship
        bool isActive;             // Available for new bonds
    }

    // Reference to Tuath token
    TuathToken public tuathToken;

    // Default tithe rate (5%)
    uint256 public constant DEFAULT_TITHE_RATE = 500;
    uint256 public constant MAX_TITHE_RATE = 2000; // 20% max
    uint256 public constant MIN_SOUL_LEVEL_FOR_MENTOR = 100;

    // Bond ID counter
    uint256 private _bondIdCounter;

    // Mappings
    mapping(uint256 => SoulBond) public bonds;
    mapping(address => MentorProfile) public mentorProfiles;
    mapping(address => uint256) public acolyteBondId; // Current bond for acolyte
    mapping(address => uint256[]) public mentorBondIds; // All bonds for mentor

    // Events
    event BondCreated(uint256 indexed bondId, address indexed mentor, address indexed acolyte, uint256 titheRate);
    event BondDissolved(uint256 indexed bondId, address indexed mentor, address indexed acolyte);
    event TithePaid(uint256 indexed bondId, address indexed acolyte, address indexed mentor, uint256 amount);
    event MentorRegistered(address indexed mentor);
    event SoulLevelUpdated(address indexed user, uint256 newLevel);

    constructor(address _tuathToken) Ownable(msg.sender) {
        tuathToken = TuathToken(_tuathToken);
    }

    /**
     * @notice Register as a mentor
     * @dev Requires minimum soul level
     */
    function registerAsMentor() external {
        require(mentorProfiles[msg.sender].soulLevel >= MIN_SOUL_LEVEL_FOR_MENTOR, "Insufficient soul level");
        require(!mentorProfiles[msg.sender].isActive, "Already registered");

        mentorProfiles[msg.sender].isActive = true;
        emit MentorRegistered(msg.sender);
    }

    /**
     * @notice Create a soul bond between mentor and acolyte
     * @param acolyte Address of the new learner
     * @param titheRate Custom tithe rate (basis points)
     */
    function createBond(address acolyte, uint256 titheRate) external returns (uint256) {
        require(mentorProfiles[msg.sender].isActive, "Not a registered mentor");
        require(acolyteBondId[acolyte] == 0, "Acolyte already has mentor");
        require(acolyte != msg.sender, "Cannot mentor yourself");
        require(titheRate <= MAX_TITHE_RATE, "Tithe rate too high");

        uint256 bondId = ++_bondIdCounter;

        bonds[bondId] = SoulBond({
            mentor: msg.sender,
            acolyte: acolyte,
            bondTime: block.timestamp,
            soulTitheRate: titheRate > 0 ? titheRate : DEFAULT_TITHE_RATE,
            totalTithePaid: 0,
            active: true
        });

        acolyteBondId[acolyte] = bondId;
        mentorBondIds[msg.sender].push(bondId);
        mentorProfiles[msg.sender].totalAcolytes++;
        mentorProfiles[msg.sender].activeAcolytes++;

        emit BondCreated(bondId, msg.sender, acolyte, bonds[bondId].soulTitheRate);
        return bondId;
    }

    /**
     * @notice Dissolve a soul bond
     * @dev Can be called by either mentor or acolyte
     */
    function dissolveBond(uint256 bondId) external {
        SoulBond storage bond = bonds[bondId];
        require(bond.active, "Bond not active");
        require(msg.sender == bond.mentor || msg.sender == bond.acolyte, "Not authorized");

        bond.active = false;
        acolyteBondId[bond.acolyte] = 0;
        mentorProfiles[bond.mentor].activeAcolytes--;

        emit BondDissolved(bondId, bond.mentor, bond.acolyte);
    }

    /**
     * @notice Pay tithe from acolyte earnings to mentor
     * @dev Called by learning validators when acolyte earns tokens
     * @param acolyte Address of the earning acolyte
     * @param grossAmount Total amount earned before tithe
     */
    function payTithe(address acolyte, uint256 grossAmount) external returns (uint256 titheAmount) {
        uint256 bondId = acolyteBondId[acolyte];
        if (bondId == 0) return 0; // No active bond

        SoulBond storage bond = bonds[bondId];
        if (!bond.active) return 0;

        titheAmount = (grossAmount * bond.soulTitheRate) / 10000;
        if (titheAmount == 0) return 0;

        bond.totalTithePaid += titheAmount;
        mentorProfiles[bond.mentor].totalTitheEarned += titheAmount;

        // Transfer tithe from caller (validator) to mentor
        require(tuathToken.transferFrom(msg.sender, bond.mentor, titheAmount), "Tithe transfer failed");

        emit TithePaid(bondId, acolyte, bond.mentor, titheAmount);

        // Update soul levels based on mentorship success
        _updateSoulLevel(bond.mentor, titheAmount / 10); // Mentor gains
        _updateSoulLevel(acolyte, titheAmount / 20);     // Acolyte gains less

        return titheAmount;
    }

    /**
     * @notice Update soul level (reputation)
     */
    function _updateSoulLevel(address user, uint256 increase) internal {
        mentorProfiles[user].soulLevel += increase;
        emit SoulLevelUpdated(user, mentorProfiles[user].soulLevel);
    }

    /**
     * @notice Grant soul level (admin/validator function)
     */
    function grantSoulLevel(address user, uint256 amount) external onlyOwner {
        _updateSoulLevel(user, amount);
    }

    /**
     * @notice Get mentor's active bond IDs
     */
    function getMentorBonds(address mentor) external view returns (uint256[] memory) {
        return mentorBondIds[mentor];
    }

    /**
     * @notice Check if address is eligible to be mentor
     */
    function canBeMentor(address user) external view returns (bool) {
        return mentorProfiles[user].soulLevel >= MIN_SOUL_LEVEL_FOR_MENTOR;
    }
}
