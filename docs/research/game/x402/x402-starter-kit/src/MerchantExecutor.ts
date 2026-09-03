import type {
  Network,
  PaymentPayload,
  PaymentRequirements,
} from 'x402/types';
import { ethers } from 'ethers';

const DEFAULT_FACILITATOR_URL = 'https://x402.org/facilitator';

const TRANSFER_AUTH_TYPES = {
  TransferWithAuthorization: [
    { name: 'from', type: 'address' },
    { name: 'to', type: 'address' },
    { name: 'value', type: 'uint256' },
    { name: 'validAfter', type: 'uint256' },
    { name: 'validBefore', type: 'uint256' },
    { name: 'nonce', type: 'bytes32' },
  ],
};

export type SettlementMode = 'facilitator' | 'direct';

type BuiltInNetwork =
  | 'base'
  | 'base-sepolia'
  | 'polygon'
  | 'polygon-amoy'
  | 'avalanche-fuji'
  | 'avalanche'
  | 'iotex'
  | 'sei'
  | 'sei-testnet'
  | 'peaq'
  | 'solana-devnet'
  | 'solana';

const BUILT_IN_NETWORKS: Record<
  BuiltInNetwork,
  {
    chainId?: number;
    assetAddress: string;
    assetName: string;
    explorer?: string;
  }
> = {
  base: {
    chainId: 8453,
    assetAddress: '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913',
    assetName: 'USD Coin',
    explorer: 'https://basescan.org',
  },
  'base-sepolia': {
    chainId: 84532,
    assetAddress: '0x036CbD53842c5426634e7929541eC2318f3dCF7e',
    assetName: 'USDC',
    explorer: 'https://sepolia.basescan.org',
  },
  polygon: {
    chainId: 137,
    assetAddress: '0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359',
    assetName: 'USD Coin',
    explorer: 'https://polygonscan.com',
  },
  'polygon-amoy': {
    chainId: 80002,
    assetAddress: '0x41E94Eb019C0762f9Bfcf9Fb1E58725BfB0e7582',
    assetName: 'USDC',
    explorer: 'https://amoy.polygonscan.com',
  },
  'avalanche-fuji': {
    chainId: 43113,
    assetAddress: '0x5425890298aed601595a70AB815c96711a31Bc65',
    assetName: 'USD Coin',
    explorer: 'https://testnet.snowtrace.io',
  },
  avalanche: {
    chainId: 43114,
    assetAddress: '0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E',
    assetName: 'USD Coin',
    explorer: 'https://snowtrace.io',
  },
  iotex: {
    chainId: 4689,
    assetAddress: '0xcdf79194c6c285077a58da47641d4dbe51f63542',
    assetName: 'Bridged USDC',
    explorer: 'https://iotexscan.io',
  },
  sei: {
    chainId: 1329,
    assetAddress: '0xe15fc38f6d8c56af07bbcbe3baf5708a2bf42392',
    assetName: 'USDC',
    explorer: 'https://sei.explorers.guru',
  },
  'sei-testnet': {
    chainId: 1328,
    assetAddress: '0x4fcf1784b31630811181f670aea7a7bef803eaed',
    assetName: 'USDC',
    explorer: 'https://testnet.sei.explorers.guru',
  },
  peaq: {
    chainId: 3338,
    assetAddress: '0xbbA60da06c2c5424f03f7434542280FCAd453d10',
    assetName: 'USDC',
    explorer: 'https://scan.peaq.network',
  },
  'solana-devnet': {
    assetAddress: '4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU',
    assetName: 'USDC',
    explorer: 'https://explorer.solana.com/?cluster=devnet',
  },
  solana: {
    assetAddress: 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
    assetName: 'USDC',
    explorer: 'https://explorer.solana.com',
  },
};

export interface MerchantExecutorOptions {
  payToAddress: string;
  network: Network;
  price: number;
  facilitatorUrl?: string;
  facilitatorApiKey?: string;
  resourceUrl?: string;
  settlementMode?: SettlementMode;
  rpcUrl?: string;
  privateKey?: string;
  assetAddress?: string;
  assetName?: string;
  explorerUrl?: string;
  chainId?: number;
}

export interface VerifyResult {
  isValid: boolean;
  payer?: string;
  invalidReason?: string;
}

export interface SettlementResult {
  success: boolean;
  transaction?: string;
  network: string;
  payer?: string;
  errorReason?: string;
}

export class MerchantExecutor {
  private readonly requirements: PaymentRequirements;
  private readonly explorerUrl?: string;
  private readonly mode: SettlementMode;
  private readonly facilitatorUrl?: string;
  private readonly facilitatorApiKey?: string;
  private settlementProvider?: ethers.JsonRpcProvider;
  private settlementWallet?: ethers.Wallet;
  private readonly network: Network;
  private readonly assetName: string;
  private readonly chainId?: number;

  constructor(options: MerchantExecutorOptions) {
    const builtinConfig = BUILT_IN_NETWORKS[
      options.network as BuiltInNetwork
    ] as (typeof BUILT_IN_NETWORKS)[BuiltInNetwork] | undefined;

    const assetAddress =
      options.assetAddress ?? builtinConfig?.assetAddress;
    const assetName = options.assetName ?? builtinConfig?.assetName;
    const chainId = options.chainId ?? builtinConfig?.chainId;
    const explorerUrl = options.explorerUrl ?? builtinConfig?.explorer;

    if (!assetAddress) {
      throw new Error(
        `Asset address must be provided for network "${options.network}". Set ASSET_ADDRESS in the environment.`
      );
    }

    if (!assetName) {
      throw new Error(
        `Asset name must be provided for network "${options.network}". Set ASSET_NAME in the environment.`
      );
    }

    this.network = options.network;
    this.assetName = assetName;
    this.chainId = chainId;
    this.explorerUrl = explorerUrl;

    this.requirements = {
      scheme: 'exact',
      network: options.network,
      asset: assetAddress,
      payTo: options.payToAddress,
      maxAmountRequired: this.getAtomicAmount(options.price),
      resource: options.resourceUrl || 'https://merchant.local/process',
      description: 'AI request processing service',
      mimeType: 'application/json',
      maxTimeoutSeconds: 600,
      extra: {
        name: assetName,
        version: '2',
      },
    };

    this.mode =
      options.settlementMode ??
      (options.facilitatorUrl || !options.privateKey ? 'facilitator' : 'direct');

    if (this.mode === 'direct') {
      if (options.network === 'solana' || options.network === 'solana-devnet') {
        throw new Error(
          'Direct settlement is only supported on EVM networks.'
        );
      }

      if (!options.privateKey) {
        throw new Error(
          'Direct settlement requires PRIVATE_KEY to be configured.'
        );
      }

      const normalizedKey = options.privateKey.startsWith('0x')
        ? options.privateKey
        : `0x${options.privateKey}`;

      const rpcUrl = options.rpcUrl || this.getDefaultRpcUrl(options.network);

      if (!rpcUrl) {
        throw new Error(
          `Direct settlement requires an RPC URL for network "${options.network}".`
        );
      }

       if (typeof chainId !== 'number') {
        throw new Error(
          `Direct settlement requires a numeric CHAIN_ID for network "${options.network}".`
        );
      }

      try {
        this.settlementProvider = new ethers.JsonRpcProvider(rpcUrl);
        this.settlementWallet = new ethers.Wallet(
          normalizedKey,
          this.settlementProvider
        );
        console.log('⚡ Local settlement enabled via RPC provider');
      } catch (error) {
        throw new Error(
          `Failed to initialize direct settlement: ${
            error instanceof Error ? error.message : String(error)
          }`
        );
      }
    } else {
      this.facilitatorUrl = options.facilitatorUrl || DEFAULT_FACILITATOR_URL;
      this.facilitatorApiKey = options.facilitatorApiKey;
    }
  }

  getPaymentRequirements(): PaymentRequirements {
    return this.requirements;
  }

  createPaymentRequiredResponse() {
    return {
      x402Version: 1,
      accepts: [this.requirements],
      error: 'Payment required for service: /process-request',
    };
  }

  async verifyPayment(payload: PaymentPayload): Promise<VerifyResult> {
    console.log('\n🔍 Verifying payment...');
    console.log(`   Network: ${payload.network}`);
    console.log(`   Scheme: ${payload.scheme}`);
    console.log(`   From: ${(payload.payload as any).authorization?.from}`);
    console.log(`   To: ${this.requirements.payTo}`);
    console.log(`   Amount: ${this.requirements.maxAmountRequired}`);

    try {
      const result =
        this.mode === 'direct'
          ? this.verifyPaymentLocally(payload, this.requirements)
          : await this.callFacilitator<VerifyResult>('verify', payload);

      console.log('\n📋 Verification result:');
      console.log(`   Valid: ${result.isValid}`);
      if (!result.isValid) {
        console.log(`   ❌ Reason: ${result.invalidReason}`);
      }

      return result;
    } catch (error) {
      const message =
        error instanceof Error ? error.message : 'Unknown verification error';
      console.error(`   ❌ Verification failed: ${message}`);
      return {
        isValid: false,
        invalidReason: message,
      };
    }
  }

  async settlePayment(payload: PaymentPayload): Promise<SettlementResult> {
    console.log('\n💰 Settling payment...');
    console.log(`   Network: ${this.requirements.network}`);
    console.log(
      `   Amount: ${this.requirements.maxAmountRequired} (micro units)`
    );
    console.log(`   Pay to: ${this.requirements.payTo}`);

    try {
      const result =
        this.mode === 'direct'
          ? await this.settleOnChain(payload, this.requirements)
          : await this.callFacilitator<SettlementResult>('settle', payload);

      console.log('\n✅ Payment settlement result:');
      console.log(`   Success: ${result.success}`);
      console.log(`   Network: ${result.network}`);
      if (result.transaction) {
        console.log(`   Transaction: ${result.transaction}`);
        if (this.explorerUrl) {
          console.log(
            `   Explorer: ${this.explorerUrl}/tx/${result.transaction}`
          );
        }
      }
      if (result.payer) {
        console.log(`   Payer: ${result.payer}`);
      }
      if (result.errorReason) {
        console.log(`   Error: ${result.errorReason}`);
      }

      return result;
    } catch (error) {
      const message =
        error instanceof Error ? error.message : 'Unknown settlement error';
      console.error(`   ❌ Settlement failed: ${message}`);
      return {
        success: false,
        network: this.requirements.network,
        errorReason: message,
      };
    }
  }

  private verifyPaymentLocally(
    payload: PaymentPayload,
    requirements: PaymentRequirements
  ): VerifyResult {
    const exactPayload = payload.payload as any;
    const authorization = exactPayload?.authorization;
    const signature = exactPayload?.signature;

    if (!authorization || !signature) {
      return {
        isValid: false,
        invalidReason: 'Missing payment authorization data',
      };
    }

    if (payload.network !== requirements.network) {
      return {
        isValid: false,
        invalidReason: `Network mismatch: ${payload.network} vs ${requirements.network}`,
      };
    }

    if (
      authorization.to?.toLowerCase() !== requirements.payTo.toLowerCase()
    ) {
      return {
        isValid: false,
        invalidReason: 'Authorization recipient does not match payment requirement',
      };
    }

    try {
      const requiredAmount = BigInt(requirements.maxAmountRequired);
      const authorizedAmount = BigInt(authorization.value);
      if (authorizedAmount < requiredAmount) {
        return {
          isValid: false,
          invalidReason: 'Authorized amount is less than required amount',
        };
      }
    } catch {
      return {
        isValid: false,
        invalidReason: 'Invalid payment amount provided',
      };
    }

    const validAfterNum = Number(authorization.validAfter ?? 0);
    const validBeforeNum = Number(authorization.validBefore ?? 0);
    if (Number.isNaN(validAfterNum) || Number.isNaN(validBeforeNum)) {
      return {
        isValid: false,
        invalidReason: 'Invalid authorization timing fields',
      };
    }

    const now = Math.floor(Date.now() / 1000);
    if (validAfterNum > now) {
      return {
        isValid: false,
        invalidReason: 'Payment authorization is not yet valid',
      };
    }
    if (validBeforeNum <= now) {
      return {
        isValid: false,
        invalidReason: 'Payment authorization has expired',
      };
    }

    try {
      const domain = this.buildEip712Domain(requirements);
      const recovered = ethers.verifyTypedData(
        domain,
        TRANSFER_AUTH_TYPES,
        {
          from: authorization.from,
          to: authorization.to,
          value: authorization.value,
          validAfter: authorization.validAfter,
          validBefore: authorization.validBefore,
          nonce: authorization.nonce,
        },
        signature
      );

      if (recovered.toLowerCase() !== authorization.from.toLowerCase()) {
        return {
          isValid: false,
          invalidReason: 'Signature does not match payer address',
        };
      }

      return {
        isValid: true,
        payer: recovered,
      };
    } catch (error) {
      return {
        isValid: false,
        invalidReason: `Signature verification failed: ${
          error instanceof Error ? error.message : String(error)
        }`,
      };
    }
  }

  private async settleOnChain(
    payload: PaymentPayload,
    requirements: PaymentRequirements
  ): Promise<SettlementResult> {
    if (!this.settlementWallet) {
      return {
        success: false,
        network: requirements.network,
        errorReason: 'Settlement wallet not configured',
      };
    }

    const exactPayload = payload.payload as any;
    const authorization = exactPayload?.authorization;
    const signature = exactPayload?.signature;

    if (!authorization || !signature) {
      return {
        success: false,
        network: requirements.network,
        errorReason: 'Missing payment authorization data',
      };
    }

    try {
      const usdcContract = new ethers.Contract(
        requirements.asset,
        [
          'function transferWithAuthorization(' +
            'address from,' +
            'address to,' +
            'uint256 value,' +
            'uint256 validAfter,' +
            'uint256 validBefore,' +
            'bytes32 nonce,' +
            'uint8 v,' +
            'bytes32 r,' +
            'bytes32 s' +
          ') external returns (bool)',
        ],
        this.settlementWallet
      );

      const parsedSignature = ethers.Signature.from(signature);
      const tx = await usdcContract.transferWithAuthorization(
        authorization.from,
        authorization.to,
        authorization.value,
        authorization.validAfter,
        authorization.validBefore,
        authorization.nonce,
        parsedSignature.v,
        parsedSignature.r,
        parsedSignature.s
      );

      const receipt = await tx.wait();
      const success = receipt?.status === 1;

      return {
        success,
        transaction: receipt?.hash,
        network: requirements.network,
        payer: authorization.from,
        errorReason: success ? undefined : 'Transaction reverted',
      };
    } catch (error) {
      return {
        success: false,
        network: requirements.network,
        payer: authorization.from,
        errorReason:
          error instanceof Error ? error.message : String(error),
      };
    }
  }

  private getAtomicAmount(priceUsd: number): string {
    const atomicUnits = Math.floor(priceUsd * 1_000_000);
    return atomicUnits.toString();
  }

  private buildHeaders() {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    if (this.facilitatorApiKey) {
      headers.Authorization = `Bearer ${this.facilitatorApiKey}`;
    }

    return headers;
  }

  private async callFacilitator<T>(
    endpoint: 'verify' | 'settle',
    payload: PaymentPayload
  ): Promise<T> {
    if (!this.facilitatorUrl) {
      throw new Error('Facilitator URL is not configured.');
    }

    const response = await fetch(`${this.facilitatorUrl}/${endpoint}`, {
      method: 'POST',
      headers: this.buildHeaders(),
      body: JSON.stringify({
        x402Version: payload.x402Version ?? 1,
        paymentPayload: payload,
        paymentRequirements: this.requirements,
      }),
    });

    if (!response.ok) {
      const text = await response.text();
      throw new Error(
        `Facilitator ${endpoint} failed (${response.status}): ${
          text || response.statusText
        }`
      );
    }

    return (await response.json()) as T;
  }

  private buildEip712Domain(requirements: PaymentRequirements) {
    return {
      name: requirements.extra?.name || this.assetName,
      version: requirements.extra?.version || '2',
      chainId: this.chainId,
      verifyingContract: requirements.asset,
    };
  }

  private getDefaultRpcUrl(network: Network): string | undefined {
    switch (network) {
      case 'base':
        return 'https://mainnet.base.org';
      case 'base-sepolia':
        return 'https://sepolia.base.org';
      case 'polygon':
        return 'https://polygon-rpc.com';
      case 'polygon-amoy':
        return 'https://rpc-amoy.polygon.technology';
      case 'avalanche':
        return 'https://api.avax.network/ext/bc/C/rpc';
      case 'avalanche-fuji':
        return 'https://api.avax-test.network/ext/bc/C/rpc';
      case 'iotex':
        return 'https://rpc.ankr.com/iotex';
      case 'sei':
        return 'https://sei-rpc.publicnode.com';
      case 'sei-testnet':
        return 'https://sei-testnet-rpc.publicnode.com';
      case 'peaq':
        return 'https://erpc.peaq.network';
      default:
        return undefined;
    }
  }
}
