# Anam Contracts

Smart contracts for the Anam learn-to-earn platform.

## Setup

```bash
# Install Foundry
curl -L https://foundry.paradigm.xyz | bash
foundryup

# Install dependencies
forge install

# Build contracts
forge build

# Run tests
forge test
```

## Networks

| Network | Chain ID | RPC |
|---------|----------|-----|
| Arbitrum Sepolia | 421614 | https://sepolia-rollup.arbitrum.io/rpc |
| Base Sepolia | 84532 | https://sepolia.base.org |

## Contracts

- `TuathToken.sol` - ERC20 utility token
- `CuchulainnNFT.sol` - Dynamic avatar NFT
- `SovereigntyStaking.sol` - Land staking
- `TuathVendor.sol` - Token marketplace
- `AnamCaraDAO.sol` - Mentorship system
