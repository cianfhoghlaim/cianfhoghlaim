// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {Script, console2} from "forge-std/Script.sol";
import {CredAnchor} from "./CredAnchor.sol";

/**
 * @title DeployCredAnchor
 * @notice Deployment script for the CredAnchor contract.
 * @dev Run with:
 *      forge script script/DeployCredAnchor.s.sol:DeployCredAnchor \
 *           --rpc-url $BASE_L2_RPC_URL \
 *           --private-key $DEPLOYER_PRIVATE_KEY \
 *           --broadcast
 *
 *      Required env vars:
 *        BASE_L2_RPC_URL     — Base L2 RPC endpoint
 *        DEPLOYER_PRIVATE_KEY — hex private key for the deployer
 */
contract DeployCredAnchor is Script {
    function run() external {
        uint256 deployerPrivateKey = vm.envUint("DEPLOYER_PRIVATE_KEY");

        vm.startBroadcast(deployerPrivateKey);

        CredAnchor credAnchor = new CredAnchor();
        address deployedAt = address(credAnchor);

        console2.log("CredAnchor deployed at:", deployedAt);
        console2.log("Owner:", credAnchor.owner());
        console2.log("Block number:", block.number);

        vm.stopBroadcast();

        // Write the deployed address to a file for downstream tooling
        vm.writeFile(
            string.concat("./out/CredAnchor-", vm.toString(block.chainid), ".address"),
            vm.toString(deployedAt)
        );
    }
}

/**
 * @title PublishTestAnchor
 * @notice Manual test script to publish a single anchor (for Base L2 testnet).
 * @dev Run with:
 *      forge script script/DeployCredAnchor.s.sol:PublishTestAnchor \
 *           --rpc-url $BASE_L2_RPC_URL \
 *           --private-key $OWNER_PRIVATE_KEY \
 *           --broadcast
 */
contract PublishTestAnchor is Script {
    function run() external {
        uint256 ownerPrivateKey = vm.envUint("OWNER_PRIVATE_KEY");
        address credAnchorAddress = vm.envAddress("CIANFHOGHLAIM_CREDANCHOR_ADDRESS");
        string memory batchId = "2026-07-01";
        bytes32 merkleRoot = bytes32(uint256(0xdeadbeef) << 224);
        uint256 leafCount = 42;

        vm.startBroadcast(ownerPrivateKey);

        CredAnchor credAnchor = CredAnchor(credAnchorAddress);
        credAnchor.publish(batchId, merkleRoot, leafCount);

        (bytes32 returnedRoot, uint256 returnedTs, uint256 returnedCount) =
            credAnchor.getAnchor(batchId);
        console2.log("Published anchor for batchId:", batchId);
        console2.log("Merkle root:", vm.toString(returnedRoot));
        console2.log("Timestamp:", returnedTs);
        console2.log("Leaf count:", returnedCount);

        vm.stopBroadcast();
    }
}