// SPDX-License-Identifier: BUSL-1.1
pragma solidity ^0.8.20;

/**
 * @title CredAnchor
 * @notice Cianfhoghlaim Educational MMO — daily Merkle root anchor
 * @dev Stores `(timestamp, merkleRoot, batchId)` for each daily
 *      anchor batch of SkillTreeBadge credentials.
 *
 *      The Cianfhoghlaim Educational MMO issues off-chain
 *      SkillTreeBadge records (Convex + FalkorDB + LanceDB) and
 *      publishes a daily Merkle root to this contract on Base L2
 *      for third-party verifiability.
 *
 *      Educational, NOT financial. Students do not buy anything with
 *      real money. The gas for the daily Merkle anchor is paid from
 *      the platform's treasury (Base L2 ≈ $0.01/anchor;
 *      1 anchor/day ≈ $3.65/year).
 *
 *      Reference:
 *      - openspec/changes/cianfhoghlaim-educational-mmo-v1/proposal.md (D4)
 *      - cianfhoghlaim/badges/anchor.py (the publishing logic)
 *      - cianfhoghlaim/badges/anchor_contract.py (the Python ABI wrapper)
 *
 *      Verification flow:
 *      1. Third party (employer, university) navigates to
 *         https://cianfhoghlaim-mmo.cianfhoghlaim.ie/anchor/<date>
 *      2. Page reads `anchors(batchId)` → returns (merkleRoot, timestamp)
 *      3. Third party recomputes the Merkle path from
 *         `(badge_id, evidence_hash)` against `merkleRoot`
 *      4. If the recomputed path matches, the badge is authentic.
 */
contract CredAnchor {
    /**
     * @notice One Merkle root anchor batch.
     * @param merkleRoot  The 32-byte Merkle root of the badge batch.
     * @param timestamp   The block timestamp at which the batch was published.
     * @param batchId     The canonical batch ID (e.g. "2026-07-01").
     * @param leafCount   The number of badge evidence_hashes included in this batch.
     */
    struct Anchor {
        bytes32 merkleRoot;
        uint256 timestamp;
        string batchId;
        uint256 leafCount;
    }

    /// @notice Mapping from batchId (e.g. "2026-07-01") to the Anchor record.
    mapping(string => Anchor) public anchors;

    /// @notice The contract owner (the platform's hot wallet). Only the owner may publish.
    address public owner;

    /// @notice Emitted when a new daily Merkle root is published.
    /// @param batchId     The canonical batch ID.
    /// @param merkleRoot  The 32-byte Merkle root.
    /// @param leafCount   The number of badges in this batch.
    /// @param timestamp   The block timestamp.
    event AnchorPublished(
        string indexed batchId,
        bytes32 merkleRoot,
        uint256 leafCount,
        uint256 timestamp
    );

    /// @notice Emitted when the contract owner is rotated.
    /// @param previousOwner  The previous owner address.
    /// @param newOwner       The new owner address.
    event OwnerRotated(address indexed previousOwner, address indexed newOwner);

    modifier onlyOwner() {
        require(msg.sender == owner, "CredAnchor: caller is not the owner");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    /**
     * @notice Publish a new daily Merkle root anchor.
     * @dev Overwrites any existing anchor for the same batchId. The
     *      daily_credential_anchor Dagster asset publishes one
     *      batchId per UTC day.
     * @param batchId     The canonical batch ID (e.g. "2026-07-01").
     * @param merkleRoot  The 32-byte Merkle root of the batch.
     * @param leafCount   The number of badges in this batch.
     */
    function publish(
        string calldata batchId,
        bytes32 merkleRoot,
        uint256 leafCount
    ) external onlyOwner {
        require(bytes(batchId).length > 0, "CredAnchor: batchId required");
        require(merkleRoot != bytes32(0), "CredAnchor: merkleRoot required");
        require(leafCount > 0, "CredAnchor: leafCount must be > 0");

        anchors[batchId] = Anchor({
            merkleRoot: merkleRoot,
            timestamp: block.timestamp,
            batchId: batchId,
            leafCount: leafCount
        });

        emit AnchorPublished(batchId, merkleRoot, leafCount, block.timestamp);
    }

    /**
     * @notice Look up an anchor by batchId.
     * @param batchId  The canonical batch ID.
     * @return merkleRoot  The 32-byte Merkle root.
     * @return timestamp   The block timestamp.
     * @return leafCount   The number of badges in the batch.
     */
    function getAnchor(string calldata batchId)
        external
        view
        returns (bytes32 merkleRoot, uint256 timestamp, uint256 leafCount)
    {
        Anchor storage a = anchors[batchId];
        return (a.merkleRoot, a.timestamp, a.leafCount);
    }

    /**
     * @notice Rotate the contract owner. Useful for key rotation
     *         without re-deploying the contract.
     * @param newOwner  The new owner address.
     */
    function rotateOwner(address newOwner) external onlyOwner {
        require(newOwner != address(0), "CredAnchor: newOwner is zero address");
        emit OwnerRotated(owner, newOwner);
        owner = newOwner;
    }

    /**
     * @notice Transfer ownership to a new address (alias for rotateOwner
     *         for compatibility with OpenZeppelin Ownable convention).
     * @param newOwner  The new owner address.
     */
    function transferOwnership(address newOwner) external onlyOwner {
        this.rotateOwner(newOwner);
    }
}