# Tuatha (The Edge)

`Tuatha` manages the distributed node states, real-time MMO mechanics, and Web3 integrations for the "Anam" educational platform.

## Core Architecture

### 1. SpacetimeDB
We utilize SpacetimeDB as both the application server and the database. It allows us to synchronize Entity-Component-System (ECS) updates in real-time across players.
*   **Modules**: Located in `crates/stdb-modules/tuath-game/`. Contains `#[table]` and `#[reducer]` components for spatial indexing (`EntityPosition`) and spaced-repetition logic for Celtic language learning.

### 2. x402 Micropayments
The educational RPG relies on a "Learn-to-Earn" token economy. To avoid heavy, expensive smart contract deployments for every in-game action, we utilize the HTTP 402 (**x402**) protocol.
*   **Function**: Facilitates cryptographic, decentralized micropayments natively over HTTP using the `Pinginn` and `Screpall` tokens.

### 3. Blockchain Synchronization
The repository includes a relayer queue (`PendingMint` / `confirm_mint`) for asynchronous synchronization with Solana and Ethereum wallets, bridging the low-latency SpacetimeDB state with on-chain NFT inventories.
