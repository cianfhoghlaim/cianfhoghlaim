// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Permit.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title TuathToken
 * @notice ERC20 token for the Anam learn-to-earn platform
 * @dev Implements EIP-2612 for gasless approvals
 *
 * The five elemental utilities of Tuath:
 * - Spirit (Anam): Currency/Mentorship
 * - Water (Uisce): Liquidity pools
 * - Fire (Tine): Burn for NFT crafting
 * - Earth (Talamh): Stake for land
 * - Air (Aer): Governance/gas fees
 */
contract TuathToken is ERC20, ERC20Permit, Ownable {
    // Maximum supply: 1 billion tokens
    uint256 public constant MAX_SUPPLY = 1_000_000_000 * 10**18;

    // Minting authorities (learning validators)
    mapping(address => bool) public validators;

    // Events
    event ValidatorAdded(address indexed validator);
    event ValidatorRemoved(address indexed validator);
    event LearnToEarnMint(address indexed learner, uint256 amount, string reason);

    constructor()
        ERC20("Tuath", "TUATH")
        ERC20Permit("Tuath")
        Ownable(msg.sender)
    {}

    /**
     * @notice Add a validator who can mint tokens for learning achievements
     * @param validator Address of the validator contract/account
     */
    function addValidator(address validator) external onlyOwner {
        validators[validator] = true;
        emit ValidatorAdded(validator);
    }

    /**
     * @notice Remove a validator
     * @param validator Address to remove
     */
    function removeValidator(address validator) external onlyOwner {
        validators[validator] = false;
        emit ValidatorRemoved(validator);
    }

    /**
     * @notice Mint tokens for a learning achievement (Proof of Learn)
     * @param learner Address of the learner receiving tokens
     * @param amount Amount to mint (in wei)
     * @param reason Description of the learning achievement
     */
    function mintForLearning(
        address learner,
        uint256 amount,
        string calldata reason
    ) external {
        require(validators[msg.sender], "Not a validator");
        require(totalSupply() + amount <= MAX_SUPPLY, "Exceeds max supply");

        _mint(learner, amount);
        emit LearnToEarnMint(learner, amount, reason);
    }

    /**
     * @notice Burn tokens (Fire element - for crafting NFTs)
     * @param amount Amount to burn
     */
    function burn(uint256 amount) external {
        _burn(msg.sender, amount);
    }
}
