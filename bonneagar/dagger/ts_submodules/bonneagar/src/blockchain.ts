/**
 * Blockchain CI Module
 *
 * Provides CI/CD functions for:
 * - SpacetimeDB WASM module builds and deployment
 * - Solana program builds and deployment (Anchor)
 * - Ethereum contract builds (Foundry/Alloy)
 * - Cross-chain integration testing
 */

import {
  dag,
  Container,
  Directory,
  Secret,
  object,
  func,
  field,
} from "@dagger.io/dagger";

@object()
export class SpacetimeDB {
  @field()
  rustVersion = "1.83";

  @field()
  spacetimeVersion = "1.0.0";

  /**
   * Get container with SpacetimeDB CLI and Rust WASM target
   */
  @func()
  baseContainer(): Container {
    return dag
      .container()
      .from(`rust:${this.rustVersion}-slim`)
      .withExec(["apt-get", "update"])
      .withExec(["apt-get", "install", "-y", "curl", "pkg-config", "libssl-dev"])
      .withExec(["rustup", "target", "add", "wasm32-unknown-unknown"])
      .withExec([
        "sh",
        "-c",
        "curl -sSf https://install.spacetimedb.com | sh",
      ]);
  }

  /**
   * Build SpacetimeDB WASM modules
   */
  @func()
  async build(
    source: Directory,
    modules: string[] = ["tuath-game", "crypteolas-sync"]
  ): Promise<Directory> {
    let container = this.baseContainer()
      .withDirectory("/src", source)
      .withWorkdir("/src");

    // Build each module
    for (const mod of modules) {
      container = container.withExec([
        "cargo",
        "build",
        "--target",
        "wasm32-unknown-unknown",
        "--release",
        "-p",
        mod,
      ]);
    }

    return container.directory("/src/target/wasm32-unknown-unknown/release");
  }

  /**
   * Generate TypeScript client bindings
   */
  @func()
  async generateBindings(
    source: Directory,
    module: string,
    outputPath: string = "bindings"
  ): Promise<Directory> {
    const wasmDir = await this.build(source, [module]);

    const container = this.baseContainer()
      .withDirectory("/wasm", wasmDir)
      .withExec([
        "spacetime",
        "generate",
        "--lang",
        "typescript",
        "--out-dir",
        `/out/${outputPath}`,
        `/wasm/${module}.wasm`,
      ]);

    return container.directory(`/out/${outputPath}`);
  }

  /**
   * Deploy module to SpacetimeDB instance
   */
  @func()
  async deploy(
    source: Directory,
    module: string,
    host: string,
    identityToken: Secret,
    databaseName?: string
  ): Promise<string> {
    const wasmDir = await this.build(source, [module]);
    const dbName = databaseName || module.replace("-", "_");

    const container = this.baseContainer()
      .withDirectory("/wasm", wasmDir)
      .withSecretVariable("SPACETIMEDB_TOKEN", identityToken)
      .withExec([
        "spacetime",
        "publish",
        "--host",
        host,
        "--database",
        dbName,
        `/wasm/${module}.wasm`,
      ]);

    return container.stdout();
  }

  /**
   * Run integration tests against local SpacetimeDB
   */
  @func()
  async test(source: Directory): Promise<string> {
    const container = this.baseContainer()
      .withDirectory("/src", source)
      .withWorkdir("/src")
      .withExec([
        "cargo",
        "test",
        "-p",
        "tuath-game",
        "-p",
        "crypteolas-sync",
      ]);

    return container.stdout();
  }
}

@object()
export class Solana {
  @field()
  anchorVersion = "0.31.0";

  @field()
  solanaVersion = "2.1.0";

  /**
   * Get container with Anchor and Solana CLI
   */
  @func()
  baseContainer(): Container {
    return dag
      .container()
      .from("backpackapp/build:v0.31.0")
      .withEnvVariable("ANCHOR_WALLET", "/root/.config/solana/id.json")
      .withExec(["solana", "config", "set", "--url", "devnet"]);
  }

  /**
   * Build all Solana programs
   */
  @func()
  async build(source: Directory): Promise<Directory> {
    const container = this.baseContainer()
      .withDirectory("/src", source)
      .withWorkdir("/src/crates/solana")
      .withExec(["anchor", "build"]);

    return container.directory("/src/target/deploy");
  }

  /**
   * Run Anchor tests
   */
  @func()
  async test(source: Directory): Promise<string> {
    const container = this.baseContainer()
      .withDirectory("/src", source)
      .withWorkdir("/src/crates/solana")
      .withExec(["anchor", "test"]);

    return container.stdout();
  }

  /**
   * Deploy program to Solana devnet
   */
  @func()
  async deploy(
    source: Directory,
    program: string,
    keypair: Secret
  ): Promise<string> {
    const buildDir = await this.build(source);

    const container = this.baseContainer()
      .withDirectory("/deploy", buildDir)
      .withMountedSecret("/root/.config/solana/id.json", keypair)
      .withExec([
        "solana",
        "program",
        "deploy",
        `/deploy/${program}.so`,
        "--url",
        "devnet",
      ]);

    return container.stdout();
  }

  /**
   * Upgrade existing program
   */
  @func()
  async upgrade(
    source: Directory,
    program: string,
    programId: string,
    keypair: Secret
  ): Promise<string> {
    const buildDir = await this.build(source);

    const container = this.baseContainer()
      .withDirectory("/deploy", buildDir)
      .withMountedSecret("/root/.config/solana/id.json", keypair)
      .withExec([
        "solana",
        "program",
        "deploy",
        `/deploy/${program}.so`,
        "--program-id",
        programId,
        "--url",
        "devnet",
      ]);

    return container.stdout();
  }

  /**
   * Generate IDL and TypeScript client
   */
  @func()
  async generateClient(
    source: Directory,
    program: string
  ): Promise<Directory> {
    const container = this.baseContainer()
      .withDirectory("/src", source)
      .withWorkdir("/src/crates/solana")
      .withExec(["anchor", "build"])
      .withExec([
        "anchor",
        "idl",
        "build",
        "-p",
        program,
        "-o",
        `/out/${program}.json`,
      ]);

    return container.directory("/out");
  }
}

@object()
export class Ethereum {
  @field()
  foundryVersion = "nightly";

  /**
   * Get container with Foundry tools
   */
  @func()
  baseContainer(): Container {
    return dag
      .container()
      .from("ghcr.io/foundry-rs/foundry:latest")
      .withExec(["forge", "--version"]);
  }

  /**
   * Build Alloy contract bindings
   */
  @func()
  async buildBindings(source: Directory): Promise<string> {
    const container = dag
      .container()
      .from("rust:1.83-slim")
      .withDirectory("/src", source)
      .withWorkdir("/src")
      .withExec([
        "cargo",
        "build",
        "--release",
        "-p",
        "celtic-eth-contracts",
        "-p",
        "celtic-bridge",
      ]);

    return container.stdout();
  }

  /**
   * Run Rust tests for Ethereum bindings
   */
  @func()
  async test(source: Directory): Promise<string> {
    const container = dag
      .container()
      .from("rust:1.83-slim")
      .withDirectory("/src", source)
      .withWorkdir("/src")
      .withExec([
        "cargo",
        "test",
        "-p",
        "celtic-eth-contracts",
        "-p",
        "celtic-bridge",
      ]);

    return container.stdout();
  }

  /**
   * Deploy contract using Forge (if Solidity contracts exist)
   */
  @func()
  async deploy(
    source: Directory,
    contractPath: string,
    rpcUrl: string,
    privateKey: Secret
  ): Promise<string> {
    const container = this.baseContainer()
      .withDirectory("/src", source)
      .withWorkdir("/src")
      .withSecretVariable("PRIVATE_KEY", privateKey)
      .withExec([
        "forge",
        "create",
        contractPath,
        "--rpc-url",
        rpcUrl,
        "--private-key",
        "$PRIVATE_KEY",
      ]);

    return container.stdout();
  }

  /**
   * Verify contract on block explorer
   */
  @func()
  async verify(
    contractAddress: string,
    contractPath: string,
    rpcUrl: string,
    etherscanApiKey: Secret
  ): Promise<string> {
    const container = this.baseContainer()
      .withSecretVariable("ETHERSCAN_API_KEY", etherscanApiKey)
      .withExec([
        "forge",
        "verify-contract",
        contractAddress,
        contractPath,
        "--etherscan-api-key",
        "$ETHERSCAN_API_KEY",
        "--rpc-url",
        rpcUrl,
      ]);

    return container.stdout();
  }
}

/**
 * SpeedRunEthereum Challenge Builder
 *
 * Manages build, test, and deployment for SpeedRunEthereum challenges
 * integrated with crypteolas (DeFi analytics) and tuath (Celtic MMO)
 */
@object()
export class SpeedRunEthereum {
  @field()
  challengeNames: string[] = [
    "tokenization",        // Challenge 0: NFT
    "staking",             // Challenge 1: Decentralized Staking
    "token-vendor",        // Challenge 2: Token Vendor
    "dice-game",           // Challenge 3: Randomness
    "dex",                 // Challenge 4: DEX/AMM
    "lending",             // Challenge 5: Over-Collateralized Lending
    "stablecoins",         // Challenge 6: Stablecoins
    "prediction-markets",  // Challenge 7: Prediction Markets
    "zk-voting",           // Challenge 8: ZK Voting
  ];

  /**
   * Get Foundry container for Solidity development
   */
  @func()
  foundryContainer(): Container {
    return dag
      .container()
      .from("ghcr.io/foundry-rs/foundry:latest")
      .withExec(["forge", "--version"])
      .withExec(["cast", "--version"]);
  }

  /**
   * Build SpeedRunEthereum Solidity contracts
   */
  @func()
  async buildContracts(source: Directory): Promise<Directory> {
    const container = this.foundryContainer()
      .withDirectory("/src", source)
      .withWorkdir("/src/sruth/shared/blockchain/ethereum")
      .withExec(["forge", "install", "OpenZeppelin/openzeppelin-contracts"])
      .withExec(["forge", "build"]);

    return container.directory("/src/sruth/shared/blockchain/ethereum/out");
  }

  /**
   * Run Foundry tests for all contracts
   */
  @func()
  async testContracts(source: Directory): Promise<string> {
    const container = this.foundryContainer()
      .withDirectory("/src", source)
      .withWorkdir("/src/sruth/shared/blockchain/ethereum")
      .withExec(["forge", "install", "OpenZeppelin/openzeppelin-contracts"])
      .withExec(["forge", "test", "-vvv"]);

    return container.stdout();
  }

  /**
   * Deploy a specific challenge contract
   */
  @func()
  async deployChallenge(
    source: Directory,
    challengeId: number,
    chain: string = "base_sepolia",
    privateKey: Secret
  ): Promise<string> {
    const contracts: Record<number, string> = {
      0: "contracts/CelticCreatureNFT.sol:CelticCreatureNFT",
      1: "contracts/LanguageStaking.sol:LanguageStaking",
      2: "contracts/CelticShop.sol:CelticShop",
      3: "contracts/QuestRNG.sol:QuestRNG",
      4: "contracts/CelticDEX.sol:CelticDEX",
      5: "contracts/CelticLending.sol:CelticLending",
      6: "contracts/CelticUSD.sol:CelticUSD",
      7: "contracts/CelticPredictions.sol:CelticPredictions",
      8: "contracts/CelticZKVoting.sol:CelticZKVoting",
    };

    const rpcUrls: Record<string, string> = {
      localhost: "http://localhost:8545",
      anvil: "http://localhost:8545",
      sepolia: "${SEPOLIA_RPC_URL}",
      base_sepolia: "https://sepolia.base.org",
      optimism_sepolia: "https://sepolia.optimism.io",
    };

    const contractPath = contracts[challengeId];
    if (!contractPath) {
      return `Error: Unknown challenge ID ${challengeId}`;
    }

    const rpcUrl = rpcUrls[chain] || rpcUrls["base_sepolia"];

    const container = this.foundryContainer()
      .withDirectory("/src", source)
      .withWorkdir("/src/sruth/shared/blockchain/ethereum")
      .withExec(["forge", "install", "OpenZeppelin/openzeppelin-contracts"])
      .withSecretVariable("PRIVATE_KEY", privateKey)
      .withExec([
        "forge",
        "create",
        contractPath,
        "--rpc-url",
        rpcUrl,
        "--private-key",
        "$PRIVATE_KEY",
      ]);

    return container.stdout();
  }

  /**
   * Verify a deployed challenge contract
   */
  @func()
  async verifyChallenge(
    source: Directory,
    challengeId: number,
    contractAddress: string,
    chain: string = "base_sepolia",
    apiKey: Secret
  ): Promise<string> {
    const contracts: Record<number, string> = {
      0: "contracts/CelticCreatureNFT.sol:CelticCreatureNFT",
      1: "contracts/LanguageStaking.sol:LanguageStaking",
      2: "contracts/CelticShop.sol:CelticShop",
      3: "contracts/QuestRNG.sol:QuestRNG",
      4: "contracts/CelticDEX.sol:CelticDEX",
      5: "contracts/CelticLending.sol:CelticLending",
      6: "contracts/CelticUSD.sol:CelticUSD",
      7: "contracts/CelticPredictions.sol:CelticPredictions",
      8: "contracts/CelticZKVoting.sol:CelticZKVoting",
    };

    const rpcUrls: Record<string, string> = {
      base_sepolia: "https://sepolia.base.org",
      optimism_sepolia: "https://sepolia.optimism.io",
      sepolia: "${SEPOLIA_RPC_URL}",
    };

    const contractPath = contracts[challengeId];
    const rpcUrl = rpcUrls[chain] || rpcUrls["base_sepolia"];

    const container = this.foundryContainer()
      .withDirectory("/src", source)
      .withWorkdir("/src/sruth/shared/blockchain/ethereum")
      .withSecretVariable("ETHERSCAN_API_KEY", apiKey)
      .withExec([
        "forge",
        "verify-contract",
        contractAddress,
        contractPath,
        "--etherscan-api-key",
        "$ETHERSCAN_API_KEY",
        "--rpc-url",
        rpcUrl,
      ]);

    return container.stdout();
  }

  /**
   * Run gas snapshot for optimization analysis
   */
  @func()
  async gasSnapshot(source: Directory): Promise<string> {
    const container = this.foundryContainer()
      .withDirectory("/src", source)
      .withWorkdir("/src/sruth/shared/blockchain/ethereum")
      .withExec(["forge", "install", "OpenZeppelin/openzeppelin-contracts"])
      .withExec(["forge", "snapshot"]);

    return container.stdout();
  }

  /**
   * Format all Solidity contracts
   */
  @func()
  async formatContracts(source: Directory): Promise<Directory> {
    const container = this.foundryContainer()
      .withDirectory("/src", source)
      .withWorkdir("/src/sruth/shared/blockchain/ethereum")
      .withExec(["forge", "fmt"]);

    return container.directory("/src/sruth/shared/blockchain/ethereum/contracts");
  }

  /**
   * Start local Anvil chain for testing
   */
  @func()
  startAnvil(): Container {
    return this.foundryContainer()
      .withExposedPort(8545)
      .withExec(["anvil", "--host", "0.0.0.0"]);
  }
}

@object()
export class BlockchainCI {
  spacetimedb = new SpacetimeDB();
  solana = new Solana();
  ethereum = new Ethereum();
  speedrun = new SpeedRunEthereum();

  /**
   * Run full blockchain CI pipeline
   */
  @func()
  async fullPipeline(source: Directory): Promise<string> {
    const results: string[] = [];

    // SpacetimeDB
    results.push("=== SpacetimeDB Build ===");
    try {
      await this.spacetimedb.build(source);
      results.push("SpacetimeDB build: SUCCESS");
    } catch (e) {
      results.push(`SpacetimeDB build: FAILED - ${e}`);
    }

    // Solana
    results.push("\n=== Solana Build ===");
    try {
      await this.solana.build(source);
      results.push("Solana build: SUCCESS");
    } catch (e) {
      results.push(`Solana build: FAILED - ${e}`);
    }

    // Ethereum bindings
    results.push("\n=== Ethereum Bindings ===");
    try {
      await this.ethereum.buildBindings(source);
      results.push("Ethereum bindings: SUCCESS");
    } catch (e) {
      results.push(`Ethereum bindings: FAILED - ${e}`);
    }

    // Tests
    results.push("\n=== SpacetimeDB Tests ===");
    try {
      const stdbTests = await this.spacetimedb.test(source);
      results.push(stdbTests);
    } catch (e) {
      results.push(`SpacetimeDB tests: FAILED - ${e}`);
    }

    results.push("\n=== Ethereum Tests ===");
    try {
      const ethTests = await this.ethereum.test(source);
      results.push(ethTests);
    } catch (e) {
      results.push(`Ethereum tests: FAILED - ${e}`);
    }

    return results.join("\n");
  }
}
