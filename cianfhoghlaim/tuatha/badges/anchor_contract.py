"""badges.anchor_contract — CredAnchor.sol ABI + helper.

The CredAnchor smart contract is a minimal Solidity contract deployed
to Base L2. It stores `(timestamp, merkleRoot, batchId)` for each
daily anchor batch.

Solidity source (for reference; the actual contract is at
`infrastructure/contracts/CredAnchor.sol`):

    // SPDX-License-Identifier: BUSL-1.1
    pragma solidity ^0.8.20;

    contract CredAnchor {
        struct Anchor {
            bytes32 merkleRoot;
            uint256 timestamp;
            string batchId;
        }

        mapping(string => Anchor) public anchors;
        address public owner;

        event AnchorPublished(string indexed batchId, bytes32 merkleRoot, uint256 timestamp);

        constructor() {
            owner = msg.sender;
        }

        modifier onlyOwner() {
            require(msg.sender == owner, "CredAnchor: not owner");
            _;
        }

        function publish(string memory batchId, bytes32 merkleRoot) external onlyOwner {
            anchors[batchId] = Anchor(merkleRoot, block.timestamp, batchId);
            emit AnchorPublished(batchId, merkleRoot, block.timestamp);
        }

        function getAnchor(string memory batchId) external view returns (Anchor memory) {
            return anchors[batchId];
        }
    }
"""

CREEDANCHOR_ABI = [
    {
        "inputs": [{"internalType": "string", "name": "batchId", "type": "string"}],
        "name": "getAnchor",
        "outputs": [
            {
                "components": [
                    {"internalType": "bytes32", "name": "merkleRoot", "type": "bytes32"},
                    {"internalType": "uint256", "name": "timestamp", "type": "uint256"},
                    {"internalType": "string", "name": "batchId", "type": "string"},
                ],
                "internalType": "struct CredAnchor.Anchor",
                "name": "",
                "type": "tuple",
            }
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "string", "name": "batchId", "type": "string"},
            {"internalType": "bytes32", "name": "merkleRoot", "type": "bytes32"},
        ],
        "name": "publish",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "internalType": "string", "name": "batchId", "type": "string"},
            {"indexed": False, "internalType": "bytes32", "name": "merkleRoot", "type": "bytes32"},
            {"indexed": False, "internalType": "uint256", "name": "timestamp", "type": "uint256"},
        ],
        "name": "AnchorPublished",
        "type": "event",
    },
    {
        "inputs": [],
        "name": "owner",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function",
    },
]