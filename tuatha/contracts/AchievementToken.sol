// SPDX-License-Identifier: BUSL-1.1
pragma solidity ^0.8.20;

/**
 * @title AchievementToken
 * @notice Cianfhoghlaim Educational MMO — badge-gated learn-to-earn token
 * @dev Per `2026-08-08-learn-to-earn-x402-credential-pipeline-v1`: a
 *      concrete, non-speculative implementation of the "learn-to-earn"
 *      research (`docs/research/game/Learn-to-Earn Blockchain and AI.md`
 *      and related documents) — deliberately scoped narrower than the
 *      orphaned `notebooks/16_speedrun_mmo_*` prototype series and
 *      `sruth/shared/blockchain/ethereum/contracts/` Foundry project,
 *      which build a genuine fungible-currency economy (a "CelticUSD"
 *      stablecoin, staking, lending, a DEX, prediction markets). This
 *      contract does none of that.
 *
 *      Generically named (not Celtic-themed) per the operator's own
 *      stated sequencing — re-theming is deferred to a later, separate
 *      change once grounded in vetted history-syllabus content.
 *
 *      Educational, NOT financial — same framing as `CredAnchor.sol`:
 *
 *      1. NON-TRANSFERABLE. `transfer`/`transferFrom`/`approve` all
 *         revert. This is a soulbound achievement record, not a
 *         spendable or tradeable currency — there is no secondary
 *         market for this token, by design, not by omission.
 *      2. CAPPED SUPPLY. `mint()` reverts once `totalSupply` would
 *         exceed `MAX_SUPPLY`.
 *      3. SINGLE MINT PATH. The only way tokens enter existence is the
 *         `minter`-gated `mint()` function, called from
 *         `tuatha/badges/ledger.py::issue_badge()` on a real, verified
 *         quest completion (mirroring `CredAnchor.publish()`'s
 *         owner-gated, single-purpose design). There is no
 *         staking, lending, trading, or prediction-market function
 *         anywhere in this contract — that is a scope boundary, not an
 *         oversight.
 *
 *      Reference:
 *      - openspec/changes/2026-08-08-learn-to-earn-x402-credential-pipeline-v1/
 *      - tuatha/badges/ledger.py (the minting caller)
 *      - tuatha/contracts/CredAnchor.sol (the sibling credential-anchor contract)
 */
contract AchievementToken {
    string public constant name = "Cianfhoghlaim Achievement Token";
    string public constant symbol = "ACHV";
    uint8 public constant decimals = 0; // whole achievement points, not fractional currency

    /// @notice Hard cap on total supply. Chosen generously for a multi-year
    ///         rollout across 8+ subjects without needing a re-deploy;
    ///         revisit if genuinely approached.
    uint256 public constant MAX_SUPPLY = 100_000_000;

    /// @notice Amount minted per badge-triggered achievement.
    uint256 public constant MINT_AMOUNT_PER_BADGE = 10;

    uint256 public totalSupply;
    mapping(address => uint256) public balanceOf;

    /// @notice The contract owner (can rotate the minter).
    address public owner;

    /// @notice The address authorized to call `mint()` — the platform's
    ///         badge-issuance service wallet, invoked from
    ///         `issue_badge()` on real quest completion.
    address public minter;

    /// @dev evidenceHash -> whether it has already minted, so the same
    ///      badge evidence can never mint twice even if `issue_badge()`
    ///      is accidentally called more than once for the same evidence.
    mapping(bytes32 => bool) public mintedForEvidence;

    event AchievementMinted(
        address indexed student,
        uint256 amount,
        bytes32 indexed evidenceHash
    );
    event OwnerRotated(address indexed previousOwner, address indexed newOwner);
    event MinterRotated(address indexed previousMinter, address indexed newMinter);

    modifier onlyOwner() {
        require(msg.sender == owner, "AchievementToken: caller is not the owner");
        _;
    }

    modifier onlyMinter() {
        require(msg.sender == minter, "AchievementToken: caller is not the minter");
        _;
    }

    constructor(address initialMinter) {
        require(initialMinter != address(0), "AchievementToken: minter is zero address");
        owner = msg.sender;
        minter = initialMinter;
    }

    /**
     * @notice Mint achievement tokens to a student on a real, verified
     *         badge issuance. Reverts if this evidenceHash already
     *         minted (idempotent against retries), or if the mint would
     *         exceed MAX_SUPPLY.
     * @param student        The student's wallet address.
     * @param evidenceHash   The SkillTreeBadge's evidence_hash — the
     *                       same value used as the Merkle leaf in
     *                       CredAnchor, so a mint is always traceable
     *                       back to a specific, anchored badge.
     */
    function mint(address student, bytes32 evidenceHash) external onlyMinter {
        require(student != address(0), "AchievementToken: student is zero address");
        require(evidenceHash != bytes32(0), "AchievementToken: evidenceHash required");
        require(!mintedForEvidence[evidenceHash], "AchievementToken: already minted for this evidence");
        require(
            totalSupply + MINT_AMOUNT_PER_BADGE <= MAX_SUPPLY,
            "AchievementToken: exceeds MAX_SUPPLY"
        );

        mintedForEvidence[evidenceHash] = true;
        totalSupply += MINT_AMOUNT_PER_BADGE;
        balanceOf[student] += MINT_AMOUNT_PER_BADGE;

        emit AchievementMinted(student, MINT_AMOUNT_PER_BADGE, evidenceHash);
    }

    /**
     * @notice Non-transferable. Always reverts. Present so wallets/
     *         explorers that expect the standard ERC20 interface can
     *         at least read `name`/`symbol`/`decimals`/`balanceOf`/
     *         `totalSupply` without erroring — but no value ever moves
     *         through this function. This is the load-bearing design
     *         decision of this contract, not a bug.
     */
    function transfer(address, uint256) external pure returns (bool) {
        revert("AchievementToken: non-transferable - this is an educational achievement record, not a tradeable asset");
    }

    /// @notice Non-transferable. Always reverts. See `transfer()`.
    function transferFrom(address, address, uint256) external pure returns (bool) {
        revert("AchievementToken: non-transferable - this is an educational achievement record, not a tradeable asset");
    }

    /// @notice Non-transferable. Always reverts. See `transfer()`.
    function approve(address, uint256) external pure returns (bool) {
        revert("AchievementToken: non-transferable - this is an educational achievement record, not a tradeable asset");
    }

    /// @notice Always returns 0 — there is no allowance mechanism.
    function allowance(address, address) external pure returns (uint256) {
        return 0;
    }

    /**
     * @notice Rotate the minter address. Owner-only, mirrors
     *         `CredAnchor.rotateOwner()`'s key-rotation pattern.
     * @param newMinter  The new minter address.
     */
    function rotateMinter(address newMinter) external onlyOwner {
        require(newMinter != address(0), "AchievementToken: newMinter is zero address");
        emit MinterRotated(minter, newMinter);
        minter = newMinter;
    }

    /**
     * @notice Rotate the contract owner.
     * @param newOwner  The new owner address.
     */
    function rotateOwner(address newOwner) external onlyOwner {
        require(newOwner != address(0), "AchievementToken: newOwner is zero address");
        emit OwnerRotated(owner, newOwner);
        owner = newOwner;
    }
}
