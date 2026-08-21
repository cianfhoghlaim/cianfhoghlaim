// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/cryptography/MerkleProof.sol";

/// @title CelticZKVoting
/// @notice Privacy-preserving voting using zero-knowledge proofs
/// @dev SpeedRunEthereum Challenge 8 - ZK Voting
///
/// Learning Objectives:
/// - Zero-knowledge proofs (Noir/Circom concepts)
/// - Merkle tree membership proofs
/// - Privacy-preserving verification
/// - Anonymous credential systems
///
/// Integration:
/// - crypteolas: ZK proof generation and governance analytics
/// - tuath: Anonymous guild voting and peer reviews
///
/// This implementation uses a simplified ZK approach with Merkle proofs
/// for eligibility and nullifiers for double-vote prevention.
/// Production would use Noir or Circom for full ZK circuits.
contract CelticZKVoting is Ownable, ReentrancyGuard {

    // ============ Structs ============

    struct Proposal {
        string title;
        string description;
        uint256 startTime;
        uint256 endTime;
        bytes32 voterMerkleRoot;  // Merkle root of eligible voters
        uint256 yesVotes;
        uint256 noVotes;
        uint256 abstainVotes;
        bool executed;
        ProposalStatus status;
    }

    struct VoteCommitment {
        bytes32 commitment;  // Hash of (vote, salt)
        uint256 timestamp;
        bool revealed;
    }

    enum ProposalStatus {
        Pending,
        Active,
        Succeeded,
        Defeated,
        Executed,
        Cancelled
    }

    enum VoteOption {
        Against,  // 0
        For,      // 1
        Abstain   // 2
    }

    // ============ State Variables ============

    uint256 public proposalCount;
    mapping(uint256 => Proposal) public proposals;

    // Nullifier tracking to prevent double voting
    // proposalId => nullifier => used
    mapping(uint256 => mapping(bytes32 => bool)) public nullifiers;

    // Commit-reveal for additional privacy
    // proposalId => voter commitment hash => VoteCommitment
    mapping(uint256 => mapping(bytes32 => VoteCommitment)) public commitments;

    // Voting parameters
    uint256 public votingDelay = 1 days;     // Time before voting starts
    uint256 public votingPeriod = 7 days;    // Voting duration
    uint256 public quorumNumerator = 400;    // 4% quorum (in basis points)
    uint256 public totalVoters;              // Total eligible voters

    // ZK Verifier contract (would be generated from Noir/Circom)
    address public zkVerifier;

    // ============ Events ============

    event ProposalCreated(
        uint256 indexed proposalId,
        string title,
        bytes32 voterMerkleRoot,
        uint256 startTime,
        uint256 endTime
    );
    event VoteCast(
        uint256 indexed proposalId,
        bytes32 indexed nullifier,
        VoteOption vote
    );
    event VoteCommitted(
        uint256 indexed proposalId,
        bytes32 indexed commitmentHash
    );
    event VoteRevealed(
        uint256 indexed proposalId,
        bytes32 indexed commitmentHash,
        VoteOption vote
    );
    event ProposalExecuted(uint256 indexed proposalId);
    event ProposalCancelled(uint256 indexed proposalId);

    // ============ Errors ============

    error ProposalNotFound();
    error VotingNotActive();
    error VotingEnded();
    error VotingNotEnded();
    error AlreadyVoted();
    error InvalidProof();
    error InvalidNullifier();
    error QuorumNotReached();
    error ProposalNotSucceeded();
    error AlreadyExecuted();
    error CommitmentNotFound();
    error AlreadyRevealed();
    error InvalidReveal();

    // ============ Constructor ============

    constructor(uint256 _totalVoters) Ownable(msg.sender) {
        totalVoters = _totalVoters;
    }

    // ============ Proposal Management ============

    /// @notice Create a new proposal
    /// @param title Short title for the proposal
    /// @param description Detailed description (could be IPFS hash)
    /// @param voterMerkleRoot Merkle root of eligible voter addresses
    function createProposal(
        string calldata title,
        string calldata description,
        bytes32 voterMerkleRoot
    ) external returns (uint256 proposalId) {
        proposalId = proposalCount++;

        uint256 startTime = block.timestamp + votingDelay;
        uint256 endTime = startTime + votingPeriod;

        proposals[proposalId] = Proposal({
            title: title,
            description: description,
            startTime: startTime,
            endTime: endTime,
            voterMerkleRoot: voterMerkleRoot,
            yesVotes: 0,
            noVotes: 0,
            abstainVotes: 0,
            executed: false,
            status: ProposalStatus.Pending
        });

        emit ProposalCreated(proposalId, title, voterMerkleRoot, startTime, endTime);
    }

    // ============ Anonymous Voting ============

    /// @notice Cast an anonymous vote using ZK proof
    /// @param proposalId The proposal to vote on
    /// @param vote The vote option (0=Against, 1=For, 2=Abstain)
    /// @param nullifier Unique nullifier derived from voter's secret
    /// @param merkleProof Proof of membership in voter set
    /// @param voterLeaf The leaf value for the voter in the Merkle tree
    function castAnonymousVote(
        uint256 proposalId,
        VoteOption vote,
        bytes32 nullifier,
        bytes32[] calldata merkleProof,
        bytes32 voterLeaf
    ) external nonReentrant {
        Proposal storage proposal = proposals[proposalId];

        if (proposal.startTime == 0) revert ProposalNotFound();
        if (block.timestamp < proposal.startTime) revert VotingNotActive();
        if (block.timestamp > proposal.endTime) revert VotingEnded();
        if (nullifiers[proposalId][nullifier]) revert AlreadyVoted();

        // Verify Merkle proof of voter eligibility
        bool validProof = MerkleProof.verify(
            merkleProof,
            proposal.voterMerkleRoot,
            voterLeaf
        );
        if (!validProof) revert InvalidProof();

        // Verify nullifier is derived correctly
        // In a real ZK implementation, this would be verified by the ZK proof
        // Here we just check that nullifier matches expected format
        if (!_verifyNullifier(nullifier, voterLeaf)) revert InvalidNullifier();

        // Mark nullifier as used
        nullifiers[proposalId][nullifier] = true;

        // Record vote
        if (vote == VoteOption.For) {
            proposal.yesVotes++;
        } else if (vote == VoteOption.Against) {
            proposal.noVotes++;
        } else {
            proposal.abstainVotes++;
        }

        // Update status if needed
        _updateProposalStatus(proposalId);

        emit VoteCast(proposalId, nullifier, vote);
    }

    /// @notice Simplified nullifier verification
    /// @dev In production, this would be part of the ZK circuit verification
    function _verifyNullifier(
        bytes32 nullifier,
        bytes32 voterLeaf
    ) internal pure returns (bool) {
        // Simple check: nullifier should be derived from voter leaf
        // Real implementation would verify ZK proof
        return nullifier != bytes32(0) && voterLeaf != bytes32(0);
    }

    // ============ Commit-Reveal Voting ============

    /// @notice Commit a vote hash (for commit-reveal scheme)
    /// @param proposalId The proposal to vote on
    /// @param commitment Hash of (vote, salt)
    function commitVote(
        uint256 proposalId,
        bytes32 commitment
    ) external {
        Proposal storage proposal = proposals[proposalId];

        if (proposal.startTime == 0) revert ProposalNotFound();
        if (block.timestamp < proposal.startTime) revert VotingNotActive();
        if (block.timestamp > proposal.endTime) revert VotingEnded();

        bytes32 commitmentHash = keccak256(abi.encodePacked(msg.sender, commitment));

        commitments[proposalId][commitmentHash] = VoteCommitment({
            commitment: commitment,
            timestamp: block.timestamp,
            revealed: false
        });

        emit VoteCommitted(proposalId, commitmentHash);
    }

    /// @notice Reveal a committed vote
    /// @param proposalId The proposal voted on
    /// @param vote The actual vote
    /// @param salt The salt used in commitment
    function revealVote(
        uint256 proposalId,
        VoteOption vote,
        bytes32 salt
    ) external {
        Proposal storage proposal = proposals[proposalId];

        if (proposal.startTime == 0) revert ProposalNotFound();
        if (block.timestamp <= proposal.endTime) revert VotingNotEnded();

        bytes32 commitment = keccak256(abi.encodePacked(vote, salt));
        bytes32 commitmentHash = keccak256(abi.encodePacked(msg.sender, commitment));

        VoteCommitment storage vc = commitments[proposalId][commitmentHash];

        if (vc.commitment == bytes32(0)) revert CommitmentNotFound();
        if (vc.revealed) revert AlreadyRevealed();
        if (vc.commitment != commitment) revert InvalidReveal();

        vc.revealed = true;

        // Record vote
        if (vote == VoteOption.For) {
            proposal.yesVotes++;
        } else if (vote == VoteOption.Against) {
            proposal.noVotes++;
        } else {
            proposal.abstainVotes++;
        }

        _updateProposalStatus(proposalId);

        emit VoteRevealed(proposalId, commitmentHash, vote);
    }

    // ============ Full ZK Vote (Placeholder) ============

    /// @notice Cast vote with full ZK proof
    /// @dev This would call an external ZK verifier contract
    /// @param proposalId The proposal to vote on
    /// @param vote The vote option
    /// @param zkProof The serialized ZK proof
    function castZKVote(
        uint256 proposalId,
        VoteOption vote,
        bytes calldata zkProof
    ) external nonReentrant {
        Proposal storage proposal = proposals[proposalId];

        if (proposal.startTime == 0) revert ProposalNotFound();
        if (block.timestamp < proposal.startTime) revert VotingNotActive();
        if (block.timestamp > proposal.endTime) revert VotingEnded();

        // In production, verify ZK proof via external verifier
        // bool valid = IZKVerifier(zkVerifier).verify(zkProof);
        // require(valid, "Invalid ZK proof");

        // Extract nullifier from proof
        bytes32 nullifier = _extractNullifierFromProof(zkProof);
        if (nullifiers[proposalId][nullifier]) revert AlreadyVoted();

        nullifiers[proposalId][nullifier] = true;

        // Record vote
        if (vote == VoteOption.For) {
            proposal.yesVotes++;
        } else if (vote == VoteOption.Against) {
            proposal.noVotes++;
        } else {
            proposal.abstainVotes++;
        }

        _updateProposalStatus(proposalId);

        emit VoteCast(proposalId, nullifier, vote);
    }

    /// @notice Extract nullifier from ZK proof
    /// @dev Placeholder - actual implementation depends on proof format
    function _extractNullifierFromProof(
        bytes calldata zkProof
    ) internal pure returns (bytes32) {
        require(zkProof.length >= 32, "Invalid proof length");
        return bytes32(zkProof[:32]);
    }

    // ============ Proposal Execution ============

    /// @notice Execute a successful proposal
    /// @param proposalId The proposal to execute
    function executeProposal(uint256 proposalId) external nonReentrant {
        Proposal storage proposal = proposals[proposalId];

        if (proposal.startTime == 0) revert ProposalNotFound();
        if (block.timestamp <= proposal.endTime) revert VotingNotEnded();
        if (proposal.executed) revert AlreadyExecuted();

        _updateProposalStatus(proposalId);

        if (proposal.status != ProposalStatus.Succeeded) revert ProposalNotSucceeded();

        proposal.executed = true;
        proposal.status = ProposalStatus.Executed;

        // Execute proposal actions here
        // Could call target contract with calldata

        emit ProposalExecuted(proposalId);
    }

    /// @notice Cancel a proposal (admin only)
    function cancelProposal(uint256 proposalId) external onlyOwner {
        Proposal storage proposal = proposals[proposalId];

        if (proposal.startTime == 0) revert ProposalNotFound();
        if (proposal.executed) revert AlreadyExecuted();

        proposal.status = ProposalStatus.Cancelled;

        emit ProposalCancelled(proposalId);
    }

    // ============ Internal Functions ============

    function _updateProposalStatus(uint256 proposalId) internal {
        Proposal storage proposal = proposals[proposalId];

        if (proposal.status == ProposalStatus.Cancelled ||
            proposal.status == ProposalStatus.Executed) {
            return;
        }

        if (block.timestamp < proposal.startTime) {
            proposal.status = ProposalStatus.Pending;
        } else if (block.timestamp <= proposal.endTime) {
            proposal.status = ProposalStatus.Active;
        } else {
            // Voting ended - determine outcome
            uint256 totalVotes = proposal.yesVotes + proposal.noVotes + proposal.abstainVotes;
            uint256 requiredQuorum = (totalVoters * quorumNumerator) / 10000;

            if (totalVotes >= requiredQuorum && proposal.yesVotes > proposal.noVotes) {
                proposal.status = ProposalStatus.Succeeded;
            } else {
                proposal.status = ProposalStatus.Defeated;
            }
        }
    }

    // ============ View Functions ============

    /// @notice Get proposal details
    function getProposal(uint256 proposalId) external view returns (
        string memory title,
        string memory description,
        uint256 startTime,
        uint256 endTime,
        uint256 yesVotes,
        uint256 noVotes,
        uint256 abstainVotes,
        ProposalStatus status
    ) {
        Proposal storage p = proposals[proposalId];
        return (
            p.title,
            p.description,
            p.startTime,
            p.endTime,
            p.yesVotes,
            p.noVotes,
            p.abstainVotes,
            p.status
        );
    }

    /// @notice Check if nullifier has been used
    function isNullifierUsed(
        uint256 proposalId,
        bytes32 nullifier
    ) external view returns (bool) {
        return nullifiers[proposalId][nullifier];
    }

    /// @notice Get current quorum requirement
    function quorum() external view returns (uint256) {
        return (totalVoters * quorumNumerator) / 10000;
    }

    /// @notice Check if proposal reached quorum
    function hasReachedQuorum(uint256 proposalId) external view returns (bool) {
        Proposal storage p = proposals[proposalId];
        uint256 totalVotes = p.yesVotes + p.noVotes + p.abstainVotes;
        return totalVotes >= (totalVoters * quorumNumerator) / 10000;
    }

    /// @notice Get vote counts for a proposal
    function getVotes(uint256 proposalId) external view returns (
        uint256 forVotes,
        uint256 againstVotes,
        uint256 abstainVotes
    ) {
        Proposal storage p = proposals[proposalId];
        return (p.yesVotes, p.noVotes, p.abstainVotes);
    }

    /// @notice Verify if a voter is eligible using Merkle proof
    function verifyVoterEligibility(
        uint256 proposalId,
        bytes32[] calldata merkleProof,
        bytes32 voterLeaf
    ) external view returns (bool) {
        Proposal storage p = proposals[proposalId];
        return MerkleProof.verify(merkleProof, p.voterMerkleRoot, voterLeaf);
    }

    // ============ Admin Functions ============

    function setVotingDelay(uint256 _delay) external onlyOwner {
        votingDelay = _delay;
    }

    function setVotingPeriod(uint256 _period) external onlyOwner {
        require(_period >= 1 days, "Period too short");
        votingPeriod = _period;
    }

    function setQuorumNumerator(uint256 _numerator) external onlyOwner {
        require(_numerator <= 10000, "Invalid quorum");
        quorumNumerator = _numerator;
    }

    function setTotalVoters(uint256 _totalVoters) external onlyOwner {
        totalVoters = _totalVoters;
    }

    function setZKVerifier(address _verifier) external onlyOwner {
        zkVerifier = _verifier;
    }

    // ============ Helper Functions ============

    /// @notice Generate a commitment hash for commit-reveal
    /// @param vote The vote option
    /// @param salt Random salt for hiding vote
    function generateCommitment(
        VoteOption vote,
        bytes32 salt
    ) external pure returns (bytes32) {
        return keccak256(abi.encodePacked(vote, salt));
    }

    /// @notice Generate a voter leaf for Merkle tree
    /// @param voter Voter address
    /// @param weight Voting weight (if applicable)
    function generateVoterLeaf(
        address voter,
        uint256 weight
    ) external pure returns (bytes32) {
        return keccak256(abi.encodePacked(voter, weight));
    }
}
