// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";
import "../contracts/CelticZKVoting.sol";
import "@openzeppelin/contracts/utils/cryptography/MerkleProof.sol";

/// @title CelticZKVoting Test Suite
/// @notice Comprehensive tests for ZK voting functionality
contract CelticZKVotingTest is Test {
    CelticZKVoting public voting;

    address public alice = makeAddr("alice");
    address public bob = makeAddr("bob");
    address public charlie = makeAddr("charlie");
    address public dave = makeAddr("dave");

    // Merkle tree setup for eligible voters
    bytes32[] public leaves;
    bytes32 public merkleRoot;

    uint256 constant TOTAL_VOTERS = 100;
    uint256 constant VOTING_DELAY = 1 days;
    uint256 constant VOTING_PERIOD = 7 days;

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
        CelticZKVoting.VoteOption vote
    );
    event VoteCommitted(
        uint256 indexed proposalId,
        bytes32 indexed commitmentHash
    );
    event VoteRevealed(
        uint256 indexed proposalId,
        bytes32 indexed commitmentHash,
        CelticZKVoting.VoteOption vote
    );
    event ProposalExecuted(uint256 indexed proposalId);
    event DisputeRaised(
        uint256 indexed proposalId,
        address indexed disputer,
        string reason
    );

    function setUp() public {
        voting = new CelticZKVoting(TOTAL_VOTERS);

        // Build Merkle tree with 4 voters
        leaves.push(voting.generateVoterLeaf(alice, 1));
        leaves.push(voting.generateVoterLeaf(bob, 1));
        leaves.push(voting.generateVoterLeaf(charlie, 1));
        leaves.push(voting.generateVoterLeaf(dave, 1));

        // Calculate Merkle root (simplified 4-leaf tree)
        bytes32 hash01 = keccak256(abi.encodePacked(leaves[0], leaves[1]));
        bytes32 hash23 = keccak256(abi.encodePacked(leaves[2], leaves[3]));
        merkleRoot = keccak256(abi.encodePacked(hash01, hash23));
    }

    // ============ Helper Functions ============

    function _createProposal() internal returns (uint256) {
        return voting.createProposal(
            "Test Proposal",
            "Description of test proposal",
            merkleRoot
        );
    }

    function _getMerkleProof(uint256 index) internal view returns (bytes32[] memory) {
        bytes32[] memory proof = new bytes32[](2);

        if (index == 0) {
            proof[0] = leaves[1];
            proof[1] = keccak256(abi.encodePacked(leaves[2], leaves[3]));
        } else if (index == 1) {
            proof[0] = leaves[0];
            proof[1] = keccak256(abi.encodePacked(leaves[2], leaves[3]));
        } else if (index == 2) {
            proof[0] = leaves[3];
            proof[1] = keccak256(abi.encodePacked(leaves[0], leaves[1]));
        } else {
            proof[0] = leaves[2];
            proof[1] = keccak256(abi.encodePacked(leaves[0], leaves[1]));
        }

        return proof;
    }

    function _generateNullifier(address voter, uint256 proposalId) internal pure returns (bytes32) {
        return keccak256(abi.encodePacked(voter, proposalId, "secret"));
    }

    // ============ Proposal Creation Tests ============

    function test_CreateProposal() public {
        vm.expectEmit(true, false, false, false);
        emit ProposalCreated(0, "Test Proposal", merkleRoot, 0, 0);

        uint256 proposalId = _createProposal();

        assertEq(proposalId, 0);

        (
            string memory title,
            string memory description,
            uint256 startTime,
            uint256 endTime,
            uint256 yesVotes,
            uint256 noVotes,
            uint256 abstainVotes,
            CelticZKVoting.ProposalStatus status
        ) = voting.getProposal(proposalId);

        assertEq(title, "Test Proposal");
        assertEq(description, "Description of test proposal");
        assertEq(startTime, block.timestamp + VOTING_DELAY);
        assertEq(endTime, block.timestamp + VOTING_DELAY + VOTING_PERIOD);
        assertEq(yesVotes, 0);
        assertEq(noVotes, 0);
        assertEq(abstainVotes, 0);
        assertEq(uint(status), uint(CelticZKVoting.ProposalStatus.Pending));
    }

    function test_CreateMultipleProposals() public {
        uint256 prop1 = _createProposal();
        uint256 prop2 = _createProposal();
        uint256 prop3 = _createProposal();

        assertEq(prop1, 0);
        assertEq(prop2, 1);
        assertEq(prop3, 2);
        assertEq(voting.proposalCount(), 3);
    }

    // ============ Anonymous Voting Tests ============

    function test_CastAnonymousVote_For() public {
        uint256 proposalId = _createProposal();

        // Skip to voting period
        vm.warp(block.timestamp + VOTING_DELAY + 1);

        bytes32 nullifier = _generateNullifier(alice, proposalId);
        bytes32[] memory proof = _getMerkleProof(0);
        bytes32 voterLeaf = leaves[0];

        vm.expectEmit(true, true, false, true);
        emit VoteCast(proposalId, nullifier, CelticZKVoting.VoteOption.For);

        voting.castAnonymousVote(
            proposalId,
            CelticZKVoting.VoteOption.For,
            nullifier,
            proof,
            voterLeaf
        );

        (,,,,uint256 yesVotes,,, ) = voting.getProposal(proposalId);
        assertEq(yesVotes, 1);
    }

    function test_CastAnonymousVote_Against() public {
        uint256 proposalId = _createProposal();
        vm.warp(block.timestamp + VOTING_DELAY + 1);

        bytes32 nullifier = _generateNullifier(bob, proposalId);
        bytes32[] memory proof = _getMerkleProof(1);
        bytes32 voterLeaf = leaves[1];

        voting.castAnonymousVote(
            proposalId,
            CelticZKVoting.VoteOption.Against,
            nullifier,
            proof,
            voterLeaf
        );

        (,,,,,uint256 noVotes,,) = voting.getProposal(proposalId);
        assertEq(noVotes, 1);
    }

    function test_CastAnonymousVote_Abstain() public {
        uint256 proposalId = _createProposal();
        vm.warp(block.timestamp + VOTING_DELAY + 1);

        bytes32 nullifier = _generateNullifier(charlie, proposalId);
        bytes32[] memory proof = _getMerkleProof(2);
        bytes32 voterLeaf = leaves[2];

        voting.castAnonymousVote(
            proposalId,
            CelticZKVoting.VoteOption.Abstain,
            nullifier,
            proof,
            voterLeaf
        );

        (,,,,,,uint256 abstainVotes,) = voting.getProposal(proposalId);
        assertEq(abstainVotes, 1);
    }

    function test_RevertWhen_VoteBeforeStart() public {
        uint256 proposalId = _createProposal();

        bytes32 nullifier = _generateNullifier(alice, proposalId);
        bytes32[] memory proof = _getMerkleProof(0);
        bytes32 voterLeaf = leaves[0];

        vm.expectRevert(CelticZKVoting.VotingNotActive.selector);
        voting.castAnonymousVote(
            proposalId,
            CelticZKVoting.VoteOption.For,
            nullifier,
            proof,
            voterLeaf
        );
    }

    function test_RevertWhen_VoteAfterEnd() public {
        uint256 proposalId = _createProposal();
        vm.warp(block.timestamp + VOTING_DELAY + VOTING_PERIOD + 1);

        bytes32 nullifier = _generateNullifier(alice, proposalId);
        bytes32[] memory proof = _getMerkleProof(0);
        bytes32 voterLeaf = leaves[0];

        vm.expectRevert(CelticZKVoting.VotingEnded.selector);
        voting.castAnonymousVote(
            proposalId,
            CelticZKVoting.VoteOption.For,
            nullifier,
            proof,
            voterLeaf
        );
    }

    function test_RevertWhen_DoubleVote() public {
        uint256 proposalId = _createProposal();
        vm.warp(block.timestamp + VOTING_DELAY + 1);

        bytes32 nullifier = _generateNullifier(alice, proposalId);
        bytes32[] memory proof = _getMerkleProof(0);
        bytes32 voterLeaf = leaves[0];

        // First vote
        voting.castAnonymousVote(
            proposalId,
            CelticZKVoting.VoteOption.For,
            nullifier,
            proof,
            voterLeaf
        );

        // Try to vote again with same nullifier
        vm.expectRevert(CelticZKVoting.AlreadyVoted.selector);
        voting.castAnonymousVote(
            proposalId,
            CelticZKVoting.VoteOption.Against,
            nullifier,
            proof,
            voterLeaf
        );
    }

    function test_MultipleVoters() public {
        uint256 proposalId = _createProposal();
        vm.warp(block.timestamp + VOTING_DELAY + 1);

        // Alice votes For
        voting.castAnonymousVote(
            proposalId,
            CelticZKVoting.VoteOption.For,
            _generateNullifier(alice, proposalId),
            _getMerkleProof(0),
            leaves[0]
        );

        // Bob votes Against
        voting.castAnonymousVote(
            proposalId,
            CelticZKVoting.VoteOption.Against,
            _generateNullifier(bob, proposalId),
            _getMerkleProof(1),
            leaves[1]
        );

        // Charlie votes For
        voting.castAnonymousVote(
            proposalId,
            CelticZKVoting.VoteOption.For,
            _generateNullifier(charlie, proposalId),
            _getMerkleProof(2),
            leaves[2]
        );

        (,,,,uint256 yesVotes, uint256 noVotes,,) = voting.getProposal(proposalId);
        assertEq(yesVotes, 2);
        assertEq(noVotes, 1);
    }

    // ============ Commit-Reveal Tests ============

    function test_CommitVote() public {
        uint256 proposalId = _createProposal();
        vm.warp(block.timestamp + VOTING_DELAY + 1);

        bytes32 salt = bytes32(uint256(12345));
        bytes32 commitment = voting.generateCommitment(
            CelticZKVoting.VoteOption.For,
            salt
        );

        vm.prank(alice);
        voting.commitVote(proposalId, commitment);

        // Commitment recorded (verified by reveal)
    }

    function test_RevealVote() public {
        uint256 proposalId = _createProposal();
        vm.warp(block.timestamp + VOTING_DELAY + 1);

        bytes32 salt = bytes32(uint256(12345));
        bytes32 commitment = voting.generateCommitment(
            CelticZKVoting.VoteOption.For,
            salt
        );

        vm.prank(alice);
        voting.commitVote(proposalId, commitment);

        // End voting period
        vm.warp(block.timestamp + VOTING_PERIOD + 1);

        vm.prank(alice);
        voting.revealVote(proposalId, CelticZKVoting.VoteOption.For, salt);

        (,,,,uint256 yesVotes,,,) = voting.getProposal(proposalId);
        assertEq(yesVotes, 1);
    }

    function test_RevertWhen_RevealDuringVoting() public {
        uint256 proposalId = _createProposal();
        vm.warp(block.timestamp + VOTING_DELAY + 1);

        bytes32 salt = bytes32(uint256(12345));
        bytes32 commitment = voting.generateCommitment(
            CelticZKVoting.VoteOption.For,
            salt
        );

        vm.prank(alice);
        voting.commitVote(proposalId, commitment);

        // Try to reveal during voting
        vm.prank(alice);
        vm.expectRevert(CelticZKVoting.VotingNotEnded.selector);
        voting.revealVote(proposalId, CelticZKVoting.VoteOption.For, salt);
    }

    function test_RevertWhen_RevealWrongVote() public {
        uint256 proposalId = _createProposal();
        vm.warp(block.timestamp + VOTING_DELAY + 1);

        bytes32 salt = bytes32(uint256(12345));
        bytes32 commitment = voting.generateCommitment(
            CelticZKVoting.VoteOption.For,
            salt
        );

        vm.prank(alice);
        voting.commitVote(proposalId, commitment);

        vm.warp(block.timestamp + VOTING_PERIOD + 1);

        // Try to reveal different vote
        vm.prank(alice);
        vm.expectRevert(CelticZKVoting.CommitmentNotFound.selector);
        voting.revealVote(proposalId, CelticZKVoting.VoteOption.Against, salt);
    }

    // ============ Proposal Execution Tests ============

    function test_ExecuteProposal_Succeeded() public {
        uint256 proposalId = _createProposal();
        vm.warp(block.timestamp + VOTING_DELAY + 1);

        // Vote to meet quorum and pass
        // Need 4% of 100 = 4 votes for quorum
        for (uint i = 0; i < 4; i++) {
            bytes32 nullifier = keccak256(abi.encodePacked("voter", i, proposalId));

            // Generate a simple valid proof for testing
            // In production, would use actual Merkle proof
            voting.castAnonymousVote(
                proposalId,
                CelticZKVoting.VoteOption.For,
                nullifier,
                _getMerkleProof(i % 4),
                leaves[i % 4]
            );
        }

        // End voting
        vm.warp(block.timestamp + VOTING_PERIOD + 1);

        vm.expectEmit(true, false, false, false);
        emit ProposalExecuted(proposalId);

        voting.executeProposal(proposalId);

        (,,,,,,,CelticZKVoting.ProposalStatus status) = voting.getProposal(proposalId);
        assertEq(uint(status), uint(CelticZKVoting.ProposalStatus.Executed));
    }

    function test_RevertWhen_ExecuteNotEnded() public {
        uint256 proposalId = _createProposal();
        vm.warp(block.timestamp + VOTING_DELAY + 1);

        vm.expectRevert(CelticZKVoting.VotingNotEnded.selector);
        voting.executeProposal(proposalId);
    }

    function test_RevertWhen_ExecuteDefeated() public {
        uint256 proposalId = _createProposal();
        vm.warp(block.timestamp + VOTING_DELAY + 1);

        // Vote against
        voting.castAnonymousVote(
            proposalId,
            CelticZKVoting.VoteOption.Against,
            _generateNullifier(alice, proposalId),
            _getMerkleProof(0),
            leaves[0]
        );

        vm.warp(block.timestamp + VOTING_PERIOD + 1);

        vm.expectRevert(CelticZKVoting.ProposalNotSucceeded.selector);
        voting.executeProposal(proposalId);
    }

    function test_CancelProposal() public {
        uint256 proposalId = _createProposal();

        voting.cancelProposal(proposalId);

        (,,,,,,,CelticZKVoting.ProposalStatus status) = voting.getProposal(proposalId);
        assertEq(uint(status), uint(CelticZKVoting.ProposalStatus.Cancelled));
    }

    function test_RevertWhen_CancelNonOwner() public {
        uint256 proposalId = _createProposal();

        vm.prank(alice);
        vm.expectRevert();
        voting.cancelProposal(proposalId);
    }

    // ============ View Functions Tests ============

    function test_IsNullifierUsed() public {
        uint256 proposalId = _createProposal();
        vm.warp(block.timestamp + VOTING_DELAY + 1);

        bytes32 nullifier = _generateNullifier(alice, proposalId);

        assertFalse(voting.isNullifierUsed(proposalId, nullifier));

        voting.castAnonymousVote(
            proposalId,
            CelticZKVoting.VoteOption.For,
            nullifier,
            _getMerkleProof(0),
            leaves[0]
        );

        assertTrue(voting.isNullifierUsed(proposalId, nullifier));
    }

    function test_GetQuorum() public view {
        uint256 quorum = voting.quorum();
        assertEq(quorum, 4); // 4% of 100
    }

    function test_HasReachedQuorum() public {
        uint256 proposalId = _createProposal();
        vm.warp(block.timestamp + VOTING_DELAY + 1);

        assertFalse(voting.hasReachedQuorum(proposalId));

        // Vote to reach quorum
        for (uint i = 0; i < 4; i++) {
            voting.castAnonymousVote(
                proposalId,
                CelticZKVoting.VoteOption.For,
                keccak256(abi.encodePacked("voter", i)),
                _getMerkleProof(i % 4),
                leaves[i % 4]
            );
        }

        assertTrue(voting.hasReachedQuorum(proposalId));
    }

    function test_GetVotes() public {
        uint256 proposalId = _createProposal();
        vm.warp(block.timestamp + VOTING_DELAY + 1);

        voting.castAnonymousVote(
            proposalId,
            CelticZKVoting.VoteOption.For,
            _generateNullifier(alice, proposalId),
            _getMerkleProof(0),
            leaves[0]
        );

        voting.castAnonymousVote(
            proposalId,
            CelticZKVoting.VoteOption.Against,
            _generateNullifier(bob, proposalId),
            _getMerkleProof(1),
            leaves[1]
        );

        voting.castAnonymousVote(
            proposalId,
            CelticZKVoting.VoteOption.Abstain,
            _generateNullifier(charlie, proposalId),
            _getMerkleProof(2),
            leaves[2]
        );

        (uint256 forVotes, uint256 againstVotes, uint256 abstainVotes) =
            voting.getVotes(proposalId);

        assertEq(forVotes, 1);
        assertEq(againstVotes, 1);
        assertEq(abstainVotes, 1);
    }

    function test_VerifyVoterEligibility() public {
        uint256 proposalId = _createProposal();

        bool isEligible = voting.verifyVoterEligibility(
            proposalId,
            _getMerkleProof(0),
            leaves[0]
        );

        assertTrue(isEligible);
    }

    // ============ Admin Functions Tests ============

    function test_SetVotingDelay() public {
        voting.setVotingDelay(2 days);
        assertEq(voting.votingDelay(), 2 days);
    }

    function test_SetVotingPeriod() public {
        voting.setVotingPeriod(14 days);
        assertEq(voting.votingPeriod(), 14 days);
    }

    function test_RevertWhen_SetVotingPeriodTooShort() public {
        vm.expectRevert("Period too short");
        voting.setVotingPeriod(12 hours);
    }

    function test_SetQuorumNumerator() public {
        voting.setQuorumNumerator(1000); // 10%
        assertEq(voting.quorumNumerator(), 1000);
    }

    function test_RevertWhen_SetQuorumTooHigh() public {
        vm.expectRevert("Invalid quorum");
        voting.setQuorumNumerator(10001);
    }

    function test_SetTotalVoters() public {
        voting.setTotalVoters(500);
        assertEq(voting.totalVoters(), 500);
    }

    function test_SetZKVerifier() public {
        address verifier = makeAddr("verifier");
        voting.setZKVerifier(verifier);
        assertEq(voting.zkVerifier(), verifier);
    }

    // ============ Helper Function Tests ============

    function test_GenerateCommitment() public view {
        bytes32 salt = bytes32(uint256(12345));

        bytes32 commitment = voting.generateCommitment(
            CelticZKVoting.VoteOption.For,
            salt
        );

        bytes32 expected = keccak256(abi.encodePacked(
            CelticZKVoting.VoteOption.For,
            salt
        ));

        assertEq(commitment, expected);
    }

    function test_GenerateVoterLeaf() public view {
        bytes32 leaf = voting.generateVoterLeaf(alice, 100);
        bytes32 expected = keccak256(abi.encodePacked(alice, uint256(100)));
        assertEq(leaf, expected);
    }

    // ============ Fuzz Tests ============

    function testFuzz_VotingParameters(
        uint256 delay,
        uint256 period,
        uint256 quorumNum
    ) public {
        delay = bound(delay, 0, 30 days);
        period = bound(period, 1 days, 60 days);
        quorumNum = bound(quorumNum, 100, 10000);

        voting.setVotingDelay(delay);
        voting.setVotingPeriod(period);
        voting.setQuorumNumerator(quorumNum);

        assertEq(voting.votingDelay(), delay);
        assertEq(voting.votingPeriod(), period);
        assertEq(voting.quorumNumerator(), quorumNum);
    }

    function testFuzz_MultipleProposals(uint8 numProposals) public {
        numProposals = uint8(bound(numProposals, 1, 20));

        for (uint i = 0; i < numProposals; i++) {
            _createProposal();
        }

        assertEq(voting.proposalCount(), numProposals);
    }

    // ============ Integration Tests ============

    function test_FullVotingLifecycle() public {
        // 1. Create proposal
        uint256 proposalId = _createProposal();

        // 2. Wait for voting to start
        vm.warp(block.timestamp + VOTING_DELAY + 1);

        // 3. Multiple voters cast anonymous votes
        voting.castAnonymousVote(
            proposalId,
            CelticZKVoting.VoteOption.For,
            _generateNullifier(alice, proposalId),
            _getMerkleProof(0),
            leaves[0]
        );

        voting.castAnonymousVote(
            proposalId,
            CelticZKVoting.VoteOption.For,
            _generateNullifier(bob, proposalId),
            _getMerkleProof(1),
            leaves[1]
        );

        voting.castAnonymousVote(
            proposalId,
            CelticZKVoting.VoteOption.Against,
            _generateNullifier(charlie, proposalId),
            _getMerkleProof(2),
            leaves[2]
        );

        voting.castAnonymousVote(
            proposalId,
            CelticZKVoting.VoteOption.For,
            _generateNullifier(dave, proposalId),
            _getMerkleProof(3),
            leaves[3]
        );

        // 4. Verify votes recorded
        (,,,,uint256 yesVotes, uint256 noVotes,,) = voting.getProposal(proposalId);
        assertEq(yesVotes, 3);
        assertEq(noVotes, 1);

        // 5. Wait for voting to end
        vm.warp(block.timestamp + VOTING_PERIOD + 1);

        // 6. Check proposal succeeded
        assertTrue(voting.hasReachedQuorum(proposalId));

        // 7. Execute proposal
        voting.executeProposal(proposalId);

        // 8. Verify final state
        (,,,,,,,CelticZKVoting.ProposalStatus status) = voting.getProposal(proposalId);
        assertEq(uint(status), uint(CelticZKVoting.ProposalStatus.Executed));
    }

    function test_CommitRevealLifecycle() public {
        uint256 proposalId = _createProposal();
        vm.warp(block.timestamp + VOTING_DELAY + 1);

        // Voters commit
        bytes32 salt1 = bytes32(uint256(1));
        bytes32 salt2 = bytes32(uint256(2));

        vm.prank(alice);
        voting.commitVote(
            proposalId,
            voting.generateCommitment(CelticZKVoting.VoteOption.For, salt1)
        );

        vm.prank(bob);
        voting.commitVote(
            proposalId,
            voting.generateCommitment(CelticZKVoting.VoteOption.Against, salt2)
        );

        // End voting period
        vm.warp(block.timestamp + VOTING_PERIOD + 1);

        // Reveal votes
        vm.prank(alice);
        voting.revealVote(proposalId, CelticZKVoting.VoteOption.For, salt1);

        vm.prank(bob);
        voting.revealVote(proposalId, CelticZKVoting.VoteOption.Against, salt2);

        // Verify
        (,,,,uint256 yesVotes, uint256 noVotes,,) = voting.getProposal(proposalId);
        assertEq(yesVotes, 1);
        assertEq(noVotes, 1);
    }
}
