// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {Test, console2} from "forge-std/Test.sol";
import {CredAnchor} from "../src/CredAnchor.sol";

/**
 * @title CredAnchorTest
 * @notice Foundry tests for the CredAnchor contract.
 */
contract CredAnchorTest is Test {
    CredAnchor public credAnchor;
    address public owner = address(this);
    address public newOwner = address(0xBEEF);

    event AnchorPublished(
        string indexed batchId,
        bytes32 merkleRoot,
        uint256 leafCount,
        uint256 timestamp
    );

    event OwnerRotated(address indexed previousOwner, address indexed newOwner);

    function setUp() public {
        credAnchor = new CredAnchor();
        assertEq(credAnchor.owner(), owner);
    }

    function test_publish_first_anchor() public {
        bytes32 merkleRoot = bytes32(uint256(0xdeadbeef) << 224);
        uint256 leafCount = 42;

        vm.expectEmit(true, false, false, true);
        emit AnchorPublished("2026-07-01", merkleRoot, leafCount, block.timestamp);

        credAnchor.publish("2026-07-01", merkleRoot, leafCount);

        (bytes32 returnedRoot, uint256 returnedTs, uint256 returnedCount) =
            credAnchor.getAnchor("2026-07-01");
        assertEq(returnedRoot, merkleRoot);
        assertEq(returnedCount, leafCount);
        assertEq(returnedTs, block.timestamp);
    }

    function test_publish_overwrites_existing_batch() public {
        bytes32 root1 = bytes32(uint256(0x1111) << 224);
        bytes32 root2 = bytes32(uint256(0x2222) << 224);

        credAnchor.publish("2026-07-01", root1, 10);
        credAnchor.publish("2026-07-01", root2, 20);

        (bytes32 returnedRoot,, uint256 returnedCount) =
            credAnchor.getAnchor("2026-07-01");
        assertEq(returnedRoot, root2);  // overwritten
        assertEq(returnedCount, 20);
    }

    function test_publish_rejects_empty_batch_id() public {
        bytes32 merkleRoot = bytes32(uint256(0xdeadbeef) << 224);
        vm.expectRevert(bytes("CredAnchor: batchId required"));
        credAnchor.publish("", merkleRoot, 42);
    }

    function test_publish_rejects_empty_merkle_root() public {
        vm.expectRevert(bytes("CredAnchor: merkleRoot required"));
        credAnchor.publish("2026-07-01", bytes32(0), 42);
    }

    function test_publish_rejects_zero_leaf_count() public {
        bytes32 merkleRoot = bytes32(uint256(0xdeadbeef) << 224);
        vm.expectRevert(bytes("CredAnchor: leafCount must be > 0"));
        credAnchor.publish("2026-07-01", merkleRoot, 0);
    }

    function test_publish_rejects_non_owner() public {
        bytes32 merkleRoot = bytes32(uint256(0xdeadbeef) << 224);
        vm.prank(address(0xCAFE));
        vm.expectRevert(bytes("CredAnchor: caller is not the owner"));
        credAnchor.publish("2026-07-01", merkleRoot, 42);
    }

    function test_rotate_owner() public {
        vm.expectEmit(true, true, false, false);
        emit OwnerRotated(owner, newOwner);

        credAnchor.rotateOwner(newOwner);
        assertEq(credAnchor.owner(), newOwner);
    }

    function test_rotate_owner_rejects_zero_address() public {
        vm.expectRevert(bytes("CredAnchor: newOwner is zero address"));
        credAnchor.rotateOwner(address(0));
    }

    function test_rotate_owner_rejects_non_owner() public {
        vm.prank(address(0xCAFE));
        vm.expectRevert(bytes("CredAnchor: caller is not the owner"));
        credAnchor.rotateOwner(newOwner);
    }

    function test_get_anchor_unknown_batch() public {
        (bytes32 root, uint256 ts, uint256 count) = credAnchor.getAnchor("nonexistent");
        assertEq(root, bytes32(0));
        assertEq(ts, 0);
        assertEq(count, 0);
    }

    function test_multiple_batches() public {
        credAnchor.publish("2026-07-01", bytes32(uint256(0x01) << 224), 10);
        credAnchor.publish("2026-07-02", bytes32(uint256(0x02) << 224), 20);
        credAnchor.publish("2026-07-03", bytes32(uint256(0x03) << 224), 30);

        (,, uint256 count1) = credAnchor.getAnchor("2026-07-01");
        (,, uint256 count2) = credAnchor.getAnchor("2026-07-02");
        (,, uint256 count3) = credAnchor.getAnchor("2026-07-03");
        assertEq(count1, 10);
        assertEq(count2, 20);
        assertEq(count3, 30);
    }
}