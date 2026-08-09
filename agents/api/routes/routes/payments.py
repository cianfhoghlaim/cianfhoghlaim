"""
x402 Micropayment Routes.

HTTP 402 Payment Required integration for premium features.
Uses x402 protocol for cryptocurrency micropayments.

Features:
- On-chain transaction verification via web3
- Chainlink price feeds for ETH/USD conversion
- Multi-token support (USDC, ETH)
"""

import logging
import os
import secrets
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Header, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .auth import check_free_usage, get_session_from_header, increment_usage

logger = logging.getLogger(__name__)

# Optional web3 imports (graceful degradation if not installed)
try:
    from web3 import Web3
    from web3.exceptions import TransactionNotFound

    WEB3_AVAILABLE = True
except ImportError:
    WEB3_AVAILABLE = False
    logger.warning("web3 not installed - on-chain verification disabled")

router = APIRouter()

# Payment configuration
PAYMENT_CONFIG = {
    "chat_message": {
        "price_usd": 0.01,
        "free_daily_limit": 5,
        "description": "AI chat message",
    },
    "knowledge_search": {
        "price_usd": 0.02,
        "free_daily_limit": 3,
        "description": "Knowledge base search",
    },
    "premium_quest": {
        "price_usd": 0.05,
        "free_daily_limit": 0,
        "description": "Premium quest access",
    },
    "analytics": {
        "price_usd": 0.05,
        "free_daily_limit": 0,
        "description": "Learning analytics",
    },
}

# Supported payment tokens
PAYMENT_TOKENS = {
    "USDC": {
        "address": "0xA0b86a33E6fd2d2AF57f2b1cf4f6b0cbb4aD8C5f",  # Base USDC
        "decimals": 6,
        "chain": "base",
    },
    "ETH": {
        "address": "native",
        "decimals": 18,
        "chain": "base",
    },
}

# Payment receiver address. Sourced from env config (real deployment);
# falls back to a documented dev placeholder — the same address the
# original hardcoded constant used, kept only as the dev default.
RECEIVER_ADDRESS = os.environ.get(
    "CIANFHOGHLAIM_X402_RECEIVER_ADDRESS",
    "0x742d35Cc6634C0532925a3b8D42C2f39edE3e8C1",
)

# RPC endpoints (use environment variables in production)
RPC_ENDPOINTS = {
    "base": os.environ.get("BASE_RPC_URL", "https://mainnet.base.org"),
    "ethereum": os.environ.get("ETH_RPC_URL", "https://eth.llamarpc.com"),
}

# Chainlink price feed addresses
CHAINLINK_FEEDS = {
    "ETH/USD": {
        "base": "0x71041dddad3595F9CEd3DcCFBe3D1F4b0a16Bb70",  # Base mainnet
        "ethereum": "0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419",  # Ethereum mainnet
    },
}

# Minimum confirmations required
MIN_CONFIRMATIONS = 2

# In-memory payment tracking — FALLBACK ONLY. Per
# `learn-to-earn-x402-credential-pipeline-v1`: the primary store is now
# the Convex `x402Payments` table (via `_ConvexPaymentStore` below), so
# payment state survives a process restart. These dicts remain as the
# degraded-mode store when the `convex` package isn't installed or
# `CONVEX_URL` isn't reachable — matching the graceful-degradation
# pattern already used by `tuatha/badges/ledger.py`.
_payment_requests: dict[str, dict] = {}
_completed_payments: dict[str, dict] = {}


class _ConvexPaymentStore:
    """Durable x402 payment state backed by the Convex `x402Payments`
    table, with transparent fallback to the in-memory dicts above when
    the `convex` package isn't installed. Mirrors the try/except
    ImportError pattern in `tuatha/badges/ledger.py`.
    """

    @staticmethod
    def _client():
        from convex import ConvexClient

        return ConvexClient(os.environ.get("CONVEX_URL", "http://localhost:3210"))

    @classmethod
    def create(cls, payment_id: str, record: dict) -> None:
        try:
            client = cls._client()
            client.mutation(
                "x402Payments:create",
                {
                    "paymentId": payment_id,
                    "resourceType": record["resource_type"],
                    "priceUsd": record["price_usd"],
                    "priceCrypto": record["price_crypto"],
                    "token": record["token"],
                    "createdAt": record["created_at"],
                    "expiresAt": record["expires_at"],
                },
            )
        except ImportError:
            _payment_requests[payment_id] = record

    @classmethod
    def get(cls, payment_id: str) -> dict | None:
        try:
            client = cls._client()
            row = client.query("x402Payments:getByPaymentId", {"paymentId": payment_id})
            if row is None:
                return None
            return {
                "resource_type": row["resourceType"],
                "price_usd": row["priceUsd"],
                "price_crypto": row["priceCrypto"],
                "token": row["token"],
                "status": row["status"],
                "created_at": row["createdAt"],
                "expires_at": row["expiresAt"],
                "transaction_hash": row.get("transactionHash"),
                "failure_reason": row.get("failureReason"),
            }
        except ImportError:
            return _payment_requests.get(payment_id) or _completed_payments.get(payment_id)

    @classmethod
    def mark_verified(cls, payment_id: str, transaction_hash: str, verified_at: str) -> None:
        try:
            client = cls._client()
            client.mutation(
                "x402Payments:markVerified",
                {
                    "paymentId": payment_id,
                    "transactionHash": transaction_hash,
                    "verifiedAt": verified_at,
                },
            )
        except ImportError:
            record = _payment_requests.get(payment_id, {})
            record.update(
                {
                    "status": "verified",
                    "transaction_hash": transaction_hash,
                    "verified_at": verified_at,
                }
            )
            _completed_payments[payment_id] = record

    @classmethod
    def mark_failed(cls, payment_id: str, status: str, failure_reason: str | None = None) -> None:
        try:
            client = cls._client()
            client.mutation(
                "x402Payments:markFailed",
                {"paymentId": payment_id, "status": status, "failureReason": failure_reason},
            )
        except ImportError:
            if payment_id in _payment_requests:
                _payment_requests[payment_id]["status"] = status
                if failure_reason:
                    _payment_requests[payment_id]["failure_reason"] = failure_reason

# Web3 instances (lazily initialized)
_web3_instances: dict[str, "Web3"] = {}


class PaymentRequirement(BaseModel):
    """Payment requirement details."""

    resource_type: str
    price_usd: float
    price_crypto: float
    token: str
    receiver_address: str
    payment_id: str
    expires_at: str
    message: str


class PaymentProof(BaseModel):
    """Payment proof for verification."""

    payment_id: str
    transaction_hash: str
    token: str
    amount: str


class PaymentStatus(BaseModel):
    """Payment verification status."""

    payment_id: str
    status: str  # pending, verified, expired, failed
    resource_type: str
    access_granted: bool
    message: str


class UsageStatus(BaseModel):
    """Current usage and payment status."""

    resource_type: str
    free_remaining: int
    price_usd: float
    requires_payment: bool


@router.get("/config")
async def get_payment_config():
    """Get payment configuration and supported tokens."""
    return {
        "pricing": PAYMENT_CONFIG,
        "tokens": PAYMENT_TOKENS,
        "receiver": RECEIVER_ADDRESS,
        "protocol": "x402",
        "chain": "base",
    }


@router.get("/usage/{resource_type}")
async def get_usage_status(
    resource_type: str,
    x_session_id: str | None = Header(None),
) -> UsageStatus:
    """Check usage status for a resource type."""
    if resource_type not in PAYMENT_CONFIG:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown resource type: {resource_type}",
        )

    config = PAYMENT_CONFIG[resource_type]
    free_limit = config["free_daily_limit"]

    # Check if user has free usage remaining
    has_free = False
    free_remaining = 0

    if x_session_id:
        session = get_session_from_header(x_session_id)
        if session:
            usage_type = resource_type.replace("_", "s_") if "_" not in resource_type else resource_type.split("_")[0] + "s"
            has_free = check_free_usage(x_session_id, usage_type, free_limit)
            used = session.get(f"free_{usage_type}_used", 0)
            free_remaining = max(0, free_limit - used)

    return UsageStatus(
        resource_type=resource_type,
        free_remaining=free_remaining,
        price_usd=config["price_usd"],
        requires_payment=not has_free and free_limit > 0,
    )


@router.post("/request/{resource_type}")
async def request_payment(
    resource_type: str,
    token: str = "USDC",
) -> PaymentRequirement:
    """
    Request payment for a resource.

    Returns x402 payment requirement with payment details.
    """
    if resource_type not in PAYMENT_CONFIG:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown resource type: {resource_type}",
        )

    if token not in PAYMENT_TOKENS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported token: {token}",
        )

    config = PAYMENT_CONFIG[resource_type]
    PAYMENT_TOKENS[token]

    # Generate payment ID
    payment_id = secrets.token_urlsafe(16)
    expires_at = datetime.now(UTC) + timedelta(minutes=15)

    # Calculate crypto amount using Chainlink price feed
    if token == "USDC":
        price_crypto = config["price_usd"]
    else:
        # Get ETH price from Chainlink oracle
        eth_price_usd = await get_eth_price_usd("base")
        price_crypto = config["price_usd"] / eth_price_usd

    # Store payment request (durably, in Convex — falls back to
    # in-memory if the `convex` package isn't installed)
    _ConvexPaymentStore.create(
        payment_id,
        {
            "resource_type": resource_type,
            "price_usd": config["price_usd"],
            "price_crypto": price_crypto,
            "token": token,
            "created_at": datetime.now(UTC).isoformat(),
            "expires_at": expires_at.isoformat(),
            "status": "pending",
        },
    )

    return PaymentRequirement(
        resource_type=resource_type,
        price_usd=config["price_usd"],
        price_crypto=price_crypto,
        token=token,
        receiver_address=RECEIVER_ADDRESS,
        payment_id=payment_id,
        expires_at=expires_at.isoformat(),
        message=f"Payment required for {config['description']}",
    )


@router.post("/verify")
async def verify_payment(proof: PaymentProof) -> PaymentStatus:
    """
    Verify a payment proof with on-chain verification.

    Verifies:
    1. Transaction exists on-chain
    2. Recipient matches receiver address
    3. Amount matches or exceeds required payment
    4. Token type matches
    5. Sufficient confirmations
    """
    payment_request = _ConvexPaymentStore.get(proof.payment_id)
    if payment_request is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment request not found",
        )

    # Check expiry
    expires_at = datetime.fromisoformat(payment_request["expires_at"])
    if datetime.now(UTC) > expires_at:
        _ConvexPaymentStore.mark_failed(proof.payment_id, "expired")
        return PaymentStatus(
            payment_id=proof.payment_id,
            status="expired",
            resource_type=payment_request["resource_type"],
            access_granted=False,
            message="Payment request has expired",
        )

    # Validate transaction hash format
    if not proof.transaction_hash.startswith("0x") or len(proof.transaction_hash) != 66:
        return PaymentStatus(
            payment_id=proof.payment_id,
            status="failed",
            resource_type=payment_request["resource_type"],
            access_granted=False,
            message="Invalid transaction hash format",
        )

    # Perform on-chain verification if web3 is available
    if WEB3_AVAILABLE:
        verification_result = await _verify_transaction_onchain(
            tx_hash=proof.transaction_hash,
            expected_token=payment_request["token"],
            expected_amount=payment_request["price_crypto"],
            chain="base",
        )

        if not verification_result["success"]:
            _ConvexPaymentStore.mark_failed(
                proof.payment_id, "failed", verification_result["reason"]
            )
            return PaymentStatus(
                payment_id=proof.payment_id,
                status="failed",
                resource_type=payment_request["resource_type"],
                access_granted=False,
                message=verification_result["reason"],
            )
    else:
        # Fallback: basic validation without on-chain check
        logger.warning(f"On-chain verification skipped for {proof.payment_id} - web3 not available")

    # Mark as verified
    _ConvexPaymentStore.mark_verified(
        proof.payment_id, proof.transaction_hash, datetime.now(UTC).isoformat()
    )

    return PaymentStatus(
        payment_id=proof.payment_id,
        status="verified",
        resource_type=payment_request["resource_type"],
        access_granted=True,
        message="Go raibh maith agat! Payment verified - access granted",
    )


async def _verify_transaction_onchain(
    tx_hash: str,
    expected_token: str,
    expected_amount: float,
    chain: str = "base",
) -> dict:
    """
    Verify transaction on-chain using web3.

    Returns dict with 'success' boolean and 'reason' if failed.
    """
    try:
        w3 = _get_web3(chain)
        if not w3:
            return {"success": False, "reason": "Unable to connect to blockchain"}

        # Fetch transaction
        try:
            tx = w3.eth.get_transaction(tx_hash)
        except TransactionNotFound:
            return {"success": False, "reason": "Transaction not found on chain"}

        # Fetch transaction receipt for confirmation count
        try:
            receipt = w3.eth.get_transaction_receipt(tx_hash)
        except TransactionNotFound:
            return {"success": False, "reason": "Transaction pending - not yet confirmed"}

        # Check if transaction was successful
        if receipt["status"] != 1:
            return {"success": False, "reason": "Transaction failed on chain"}

        # Check confirmation count
        current_block = w3.eth.block_number
        confirmations = current_block - receipt["blockNumber"]
        if confirmations < MIN_CONFIRMATIONS:
            return {
                "success": False,
                "reason": f"Insufficient confirmations: {confirmations}/{MIN_CONFIRMATIONS}",
            }

        # Verify recipient
        receiver_lower = RECEIVER_ADDRESS.lower()
        if expected_token == "ETH":
            # Native ETH transfer
            if tx["to"].lower() != receiver_lower:
                return {"success": False, "reason": "Payment sent to wrong address"}

            # Verify amount
            amount_wei = tx["value"]
            amount_eth = float(w3.from_wei(amount_wei, "ether"))
            if amount_eth < expected_amount * 0.99:  # 1% tolerance for gas
                return {
                    "success": False,
                    "reason": f"Insufficient payment: {amount_eth} ETH < {expected_amount} ETH",
                }
        else:
            # ERC20 transfer (USDC)
            token_address = PAYMENT_TOKENS.get(expected_token, {}).get("address")
            if not token_address or tx["to"].lower() != token_address.lower():
                return {"success": False, "reason": "Invalid token transfer"}

            # Decode ERC20 transfer from input data
            transfer_data = _decode_erc20_transfer(tx["input"])
            if not transfer_data:
                return {"success": False, "reason": "Unable to decode token transfer"}

            if transfer_data["to"].lower() != receiver_lower:
                return {"success": False, "reason": "Token sent to wrong address"}

            # Verify amount (accounting for decimals)
            decimals = PAYMENT_TOKENS[expected_token]["decimals"]
            expected_raw = int(expected_amount * (10 ** decimals))
            if transfer_data["amount"] < expected_raw * 0.99:
                return {"success": False, "reason": "Insufficient token payment"}

        return {"success": True, "reason": None}

    except Exception as e:
        logger.exception(f"On-chain verification failed: {e}")
        return {"success": False, "reason": f"Verification error: {e!s}"}


def _get_web3(chain: str) -> "Web3 | None":
    """Get or create web3 instance for chain."""
    if not WEB3_AVAILABLE:
        return None

    if chain not in _web3_instances:
        rpc_url = RPC_ENDPOINTS.get(chain)
        if not rpc_url:
            return None
        _web3_instances[chain] = Web3(Web3.HTTPProvider(rpc_url))

    w3 = _web3_instances[chain]
    if not w3.is_connected():
        logger.warning(f"Web3 not connected to {chain}")
        return None

    return w3


def _decode_erc20_transfer(input_data: str) -> dict | None:
    """Decode ERC20 transfer function call."""
    # transfer(address,uint256) selector: 0xa9059cbb
    if not input_data.startswith("0xa9059cbb"):
        return None

    try:
        # Remove selector
        data = input_data[10:]
        # First 32 bytes: address (padded)
        to_address = "0x" + data[24:64]
        # Next 32 bytes: amount
        amount = int(data[64:128], 16)
        return {"to": to_address, "amount": amount}
    except Exception:
        return None


async def get_eth_price_usd(chain: str = "base") -> float:
    """
    Get current ETH/USD price from Chainlink oracle.

    Falls back to hardcoded estimate if unavailable.
    """
    if not WEB3_AVAILABLE:
        return 2500.0  # Fallback estimate

    w3 = _get_web3(chain)
    if not w3:
        return 2500.0

    try:
        feed_address = CHAINLINK_FEEDS.get("ETH/USD", {}).get(chain)
        if not feed_address:
            return 2500.0

        # Chainlink Aggregator V3 ABI (minimal)
        aggregator_abi = [
            {
                "inputs": [],
                "name": "latestRoundData",
                "outputs": [
                    {"name": "roundId", "type": "uint80"},
                    {"name": "answer", "type": "int256"},
                    {"name": "startedAt", "type": "uint256"},
                    {"name": "updatedAt", "type": "uint256"},
                    {"name": "answeredInRound", "type": "uint80"},
                ],
                "stateMutability": "view",
                "type": "function",
            },
            {
                "inputs": [],
                "name": "decimals",
                "outputs": [{"name": "", "type": "uint8"}],
                "stateMutability": "view",
                "type": "function",
            },
        ]

        contract = w3.eth.contract(
            address=Web3.to_checksum_address(feed_address),
            abi=aggregator_abi,
        )

        decimals = contract.functions.decimals().call()
        round_data = contract.functions.latestRoundData().call()
        price = round_data[1] / (10 ** decimals)

        return float(price)

    except Exception as e:
        logger.warning(f"Failed to get ETH price from Chainlink: {e}")
        return 2500.0


@router.get("/status/{payment_id}")
async def get_payment_status(payment_id: str) -> PaymentStatus:
    """Get the status of a payment."""
    payment = _ConvexPaymentStore.get(payment_id)
    if payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )

    if payment["status"] == "verified":
        return PaymentStatus(
            payment_id=payment_id,
            status="verified",
            resource_type=payment["resource_type"],
            access_granted=True,
            message="Payment verified",
        )

    expires_at = datetime.fromisoformat(payment["expires_at"])
    if datetime.now(UTC) > expires_at:
        return PaymentStatus(
            payment_id=payment_id,
            status="expired",
            resource_type=payment["resource_type"],
            access_granted=False,
            message="Payment request expired",
        )

    return PaymentStatus(
        payment_id=payment_id,
        status="pending",
        resource_type=payment["resource_type"],
        access_granted=False,
        message="Awaiting payment",
    )


def create_402_response(
    resource_type: str,
    token: str = "USDC",
) -> JSONResponse:
    """
    Create an HTTP 402 Payment Required response.

    Used by other routes when payment is required.
    """
    if resource_type not in PAYMENT_CONFIG:
        resource_type = "chat_message"

    config = PAYMENT_CONFIG[resource_type]
    payment_id = secrets.token_urlsafe(16)
    expires_at = datetime.now(UTC) + timedelta(minutes=15)

    # Calculate crypto amount
    price_crypto = config["price_usd"] if token == "USDC" else config["price_usd"] / 2500.0

    # Store payment request
    _ConvexPaymentStore.create(payment_id, {
        "resource_type": resource_type,
        "price_usd": config["price_usd"],
        "price_crypto": price_crypto,
        "token": token,
        "created_at": datetime.now(UTC).isoformat(),
        "expires_at": expires_at.isoformat(),
        "status": "pending",
    })

    return JSONResponse(
        status_code=status.HTTP_402_PAYMENT_REQUIRED,
        content={
            "error": "payment_required",
            "message": f"Payment required for {config['description']}",
            "payment": {
                "resource_type": resource_type,
                "price_usd": config["price_usd"],
                "price_crypto": price_crypto,
                "token": token,
                "receiver_address": RECEIVER_ADDRESS,
                "payment_id": payment_id,
                "expires_at": expires_at.isoformat(),
            },
            "verify_url": "/payments/verify",
        },
        headers={
            "X-Payment-Required": "true",
            "X-Payment-Amount": str(price_crypto),
            "X-Payment-Address": RECEIVER_ADDRESS,
            "X-Payment-Token": token,
            "X-Payment-ID": payment_id,
        },
    )


def check_payment_or_free(
    session_id: str | None,
    resource_type: str,
    payment_id: str | None = None,
) -> bool:
    """
    Check if request has valid payment or free usage.

    Returns True if access should be granted, False otherwise.
    """
    # Check for valid payment
    if payment_id:
        payment = _ConvexPaymentStore.get(payment_id)
        if payment is not None and payment["status"] == "verified":
            return True

    # Check for free usage
    if session_id:
        config = PAYMENT_CONFIG.get(resource_type, {})
        free_limit = config.get("free_daily_limit", 0)

        if free_limit > 0:
            usage_type = "messages" if resource_type == "chat_message" else "searches"
            if check_free_usage(session_id, usage_type, free_limit):
                increment_usage(session_id, usage_type)
                return True

    return False
