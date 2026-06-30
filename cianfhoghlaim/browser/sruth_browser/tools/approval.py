"""Human-in-the-loop approval tools for browser automation.

Provides tools for:
- Requesting human approval for risky operations
- Handling approval responses from UI
- Timeout and expiration management
- Approval audit logging
"""

from datetime import datetime, timedelta
from typing import Any

import structlog
from google.adk.tools import FunctionTool
from pydantic import BaseModel, Field

from ..config import get_config
from ..core import get_restate_plugin

logger = structlog.get_logger()


class ApprovalRequest(BaseModel):
    """Model for an approval request."""

    id: str = Field(description="Unique approval request ID")
    session_id: str = Field(description="Browser session ID")
    action: str = Field(description="Description of the action requiring approval")
    details: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime | None = Field(default=None)
    status: str = Field(default="pending")  # pending, approved, rejected, expired
    decided_by: str | None = Field(default=None)
    decided_at: datetime | None = Field(default=None)


class ApprovalResponse(BaseModel):
    """Model for an approval response."""

    request_id: str
    approved: bool
    reason: str | None = None
    decided_by: str = "user"


# In-memory store for approval requests (would be Redis in production)
_pending_requests: dict[str, ApprovalRequest] = {}


async def request_approval(
    session_id: str,
    action: str,
    details: dict[str, Any] | None = None,
    timeout_minutes: int | None = None,
) -> dict:
    """Request human approval for an action.

    Creates an approval request that must be approved or rejected
    via the handle_approval tool or UI before proceeding.

    Args:
        session_id: Browser session ID for context
        action: Description of the action requiring approval
            e.g., "Extract data from 50 URLs on example.com"
        details: Additional context for the approval decision
        timeout_minutes: Override default timeout

    Returns:
        Approval request details with request_id

    Example:
        result = await request_approval(
            session_id="sess_123",
            action="Submit form with user data",
            details={"form_url": "https://...", "fields": ["name", "email"]},
        )
        # Wait for approval via handle_approval()
    """
    config = get_config()
    plugin = get_restate_plugin()

    # Calculate expiration
    timeout = timeout_minutes or config.approval_timeout_minutes
    expires_at = datetime.utcnow() + timedelta(minutes=timeout)

    # Create awakeable for async resolution
    awakeable = plugin.awakeable_manager.create(prefix=f"approval_{session_id}")

    # Create request
    request = ApprovalRequest(
        id=awakeable.id,
        session_id=session_id,
        action=action,
        details=details or {},
        expires_at=expires_at,
    )

    # Store request
    _pending_requests[request.id] = request

    logger.info(
        "approval_requested",
        request_id=request.id,
        session_id=session_id,
        action=action,
        expires_at=expires_at.isoformat(),
    )

    return {
        "request_id": request.id,
        "session_id": session_id,
        "action": action,
        "status": "pending",
        "expires_at": expires_at.isoformat(),
        "timeout_minutes": timeout,
    }


async def handle_approval(
    request_id: str,
    approved: bool,
    reason: str | None = None,
    decided_by: str = "user",
) -> dict:
    """Handle an approval response from the UI.

    Called when a human approves or rejects a pending request.

    Args:
        request_id: The approval request ID to respond to
        approved: True to approve, False to reject
        reason: Optional reason for the decision
        decided_by: Identifier for who made the decision

    Returns:
        Updated approval status

    Example:
        # From approval UI:
        await handle_approval(
            request_id="approval_sess_123_1",
            approved=True,
            reason="Looks safe",
            decided_by="admin@example.com",
        )
    """
    request = _pending_requests.get(request_id)

    if not request:
        return {
            "success": False,
            "error": f"Approval request {request_id} not found",
        }

    # Check expiration
    if request.expires_at and datetime.utcnow() > request.expires_at:
        request.status = "expired"
        return {
            "success": False,
            "error": f"Approval request {request_id} has expired",
        }

    # Update request
    request.status = "approved" if approved else "rejected"
    request.decided_by = decided_by
    request.decided_at = datetime.utcnow()

    # Resolve the awakeable
    plugin = get_restate_plugin()
    if approved:
        plugin.awakeable_manager.resolve(request_id, True)
    else:
        plugin.awakeable_manager.resolve(request_id, False)

    logger.info(
        "approval_handled",
        request_id=request_id,
        approved=approved,
        decided_by=decided_by,
        reason=reason,
    )

    return {
        "success": True,
        "request_id": request_id,
        "status": request.status,
        "decided_by": decided_by,
        "decided_at": request.decided_at.isoformat(),
    }


async def get_pending_approvals(
    session_id: str | None = None,
) -> dict:
    """Get all pending approval requests.

    Args:
        session_id: Optional filter by session ID

    Returns:
        List of pending approval requests

    Example:
        # Get all pending for a session
        pending = await get_pending_approvals(session_id="sess_123")
    """
    # Clean expired requests
    now = datetime.utcnow()
    expired = [
        req_id
        for req_id, req in _pending_requests.items()
        if req.status == "pending" and req.expires_at and now > req.expires_at
    ]

    for req_id in expired:
        _pending_requests[req_id].status = "expired"
        # Also reject the awakeable
        plugin = get_restate_plugin()
        plugin.awakeable_manager.resolve(req_id, False)

    # Filter and return
    pending = [
        {
            "request_id": req.id,
            "session_id": req.session_id,
            "action": req.action,
            "details": req.details,
            "created_at": req.created_at.isoformat(),
            "expires_at": req.expires_at.isoformat() if req.expires_at else None,
            "status": req.status,
        }
        for req in _pending_requests.values()
        if req.status == "pending"
        and (session_id is None or req.session_id == session_id)
    ]

    return {
        "pending_count": len(pending),
        "requests": pending,
    }


async def cancel_approval(
    request_id: str,
    reason: str = "Cancelled by system",
) -> dict:
    """Cancel a pending approval request.

    Args:
        request_id: The request to cancel
        reason: Reason for cancellation

    Returns:
        Cancellation result
    """
    request = _pending_requests.get(request_id)

    if not request:
        return {
            "success": False,
            "error": f"Approval request {request_id} not found",
        }

    if request.status != "pending":
        return {
            "success": False,
            "error": f"Request {request_id} is already {request.status}",
        }

    request.status = "cancelled"
    request.decided_at = datetime.utcnow()

    # Reject the awakeable
    plugin = get_restate_plugin()
    plugin.awakeable_manager.resolve(request_id, False)

    logger.info(
        "approval_cancelled",
        request_id=request_id,
        reason=reason,
    )

    return {
        "success": True,
        "request_id": request_id,
        "status": "cancelled",
        "reason": reason,
    }


async def wait_for_approval(
    request_id: str,
    timeout_seconds: float | None = None,
) -> dict:
    """Wait for an approval request to be resolved.

    Blocks until the request is approved, rejected, or times out.

    Args:
        request_id: The request to wait for
        timeout_seconds: Override timeout (defaults to request expiration)

    Returns:
        Final approval status
    """
    request = _pending_requests.get(request_id)

    if not request:
        return {
            "success": False,
            "approved": False,
            "error": f"Approval request {request_id} not found",
        }

    plugin = get_restate_plugin()
    awakeable = plugin.awakeable_manager.get(request_id)

    if not awakeable:
        return {
            "success": False,
            "approved": False,
            "error": f"Awakeable for {request_id} not found",
        }

    # Calculate timeout
    if timeout_seconds:
        timeout = timedelta(seconds=timeout_seconds)
    elif request.expires_at:
        timeout = request.expires_at - datetime.utcnow()
        if timeout.total_seconds() <= 0:
            return {
                "success": False,
                "approved": False,
                "error": "Request already expired",
            }
    else:
        timeout = timedelta(minutes=get_config().approval_timeout_minutes)

    try:
        approved = await awakeable.wait(timeout=timeout)

        return {
            "success": True,
            "approved": approved,
            "request_id": request_id,
            "status": request.status,
        }

    except TimeoutError:
        request.status = "expired"
        return {
            "success": False,
            "approved": False,
            "error": "Approval request timed out",
        }


# Create ADK function tools
request_approval_tool = FunctionTool(request_approval)
handle_approval_tool = FunctionTool(handle_approval)
get_pending_tool = FunctionTool(get_pending_approvals)
cancel_approval_tool = FunctionTool(cancel_approval)
wait_approval_tool = FunctionTool(wait_for_approval)

# Export all tools
approval_tools = [
    request_approval_tool,
    handle_approval_tool,
    get_pending_tool,
    cancel_approval_tool,
    wait_approval_tool,
]
