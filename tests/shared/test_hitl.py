"""
Tests for sruth.shared.hitl module.

Tests:
- ApprovalRequest model
- ApprovalStatus transitions
- HITLWorkflow request/response
- InMemoryApprovalStore
"""

from datetime import datetime, timedelta

import pytest


class TestApprovalModels:
    """Tests for HITL data models."""

    def test_approval_context_creation(self):
        """Test ApprovalContext creation."""
        from sruth.shared.hitl import ApprovalContext

        context = ApprovalContext(
            action="execute_trade",
            description="Buy 100 ETH",
            parameters={"symbol": "ETH", "amount": 100},
        )

        assert context.action == "execute_trade"
        assert context.parameters["amount"] == 100

    def test_approval_request_creation(self):
        """Test ApprovalRequest creation with defaults."""
        from sruth.shared.hitl import ApprovalRequest, ApprovalStatus

        request = ApprovalRequest()

        assert request.status == ApprovalStatus.PENDING
        assert request.id is not None
        assert request.expires_at is not None

    def test_approval_request_expiry(self):
        """Test ApprovalRequest expiry calculation."""
        from sruth.shared.hitl import ApprovalRequest

        request = ApprovalRequest(timeout_seconds=1)

        # Initially not expired
        assert not request.is_expired

        # Simulate expiry by backdating
        request.expires_at = datetime.now() - timedelta(seconds=1)
        assert request.is_expired

    def test_approval_request_approve(self):
        """Test approving a request."""
        from sruth.shared.hitl import ApprovalRequest, ApprovalStatus

        request = ApprovalRequest()
        request.approve(responder_id="user1", notes="LGTM")

        assert request.status == ApprovalStatus.APPROVED
        assert request.responder_id == "user1"
        assert request.response_notes == "LGTM"
        assert request.responded_at is not None

    def test_approval_request_reject(self):
        """Test rejecting a request."""
        from sruth.shared.hitl import ApprovalRequest, ApprovalStatus

        request = ApprovalRequest()
        request.reject(responder_id="user2", notes="Too risky")

        assert request.status == ApprovalStatus.REJECTED
        assert request.responder_id == "user2"

    def test_approval_request_cannot_approve_twice(self):
        """Test cannot approve already resolved request."""
        from sruth.shared.hitl import ApprovalRequest

        request = ApprovalRequest()
        request.approve(responder_id="user1")

        with pytest.raises(ValueError):
            request.approve(responder_id="user2")

    def test_approval_request_cancel(self):
        """Test cancelling a request."""
        from sruth.shared.hitl import ApprovalRequest, ApprovalStatus

        request = ApprovalRequest()
        request.cancel(reason="No longer needed")

        assert request.status == ApprovalStatus.CANCELLED

    def test_approval_request_serialization(self):
        """Test request serialization to dict."""
        from sruth.shared.hitl import ApprovalContext, ApprovalRequest

        context = ApprovalContext(action="test", description="Test action")
        request = ApprovalRequest(context=context)

        data = request.to_dict()

        assert data["id"] == request.id
        assert data["context"]["action"] == "test"
        assert data["status"] == "pending"

    def test_approval_request_deserialization(self):
        """Test request deserialization from dict."""
        from sruth.shared.hitl import ApprovalRequest

        data = {
            "id": "test-id",
            "context": {"action": "test", "description": "Test"},
            "status": "pending",
            "priority": "medium",
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(hours=1)).isoformat(),
            "timeout_seconds": 3600,
        }

        request = ApprovalRequest.from_dict(data)

        assert request.id == "test-id"
        assert request.context.action == "test"


class TestInMemoryApprovalStore:
    """Tests for InMemoryApprovalStore."""

    def test_save_and_get_request(self):
        """Test saving and retrieving a request."""
        from sruth.shared.hitl import ApprovalRequest, InMemoryApprovalStore

        store = InMemoryApprovalStore()
        request = ApprovalRequest()

        store.save_request(request)
        retrieved = store.get_request(request.id)

        assert retrieved is not None
        assert retrieved.id == request.id

    def test_list_pending(self):
        """Test listing pending requests."""
        from sruth.shared.hitl import ApprovalRequest, ApprovalStatus, InMemoryApprovalStore

        store = InMemoryApprovalStore()

        # Add some requests
        pending1 = ApprovalRequest()
        pending2 = ApprovalRequest()
        approved = ApprovalRequest()
        approved.approve("user")

        store.save_request(pending1)
        store.save_request(pending2)
        store.save_request(approved)

        pending = store.list_pending()

        assert len(pending) == 2
        assert all(r.status == ApprovalStatus.PENDING for r in pending)

    def test_priority_ordering(self):
        """Test pending requests are ordered by priority."""
        from sruth.shared.hitl import (
            ApprovalPriority,
            ApprovalRequest,
            InMemoryApprovalStore,
        )

        store = InMemoryApprovalStore()

        low = ApprovalRequest(priority=ApprovalPriority.LOW)
        high = ApprovalRequest(priority=ApprovalPriority.HIGH)
        critical = ApprovalRequest(priority=ApprovalPriority.CRITICAL)

        store.save_request(low)
        store.save_request(high)
        store.save_request(critical)

        pending = store.list_pending()

        # Critical should be first
        assert pending[0].priority == ApprovalPriority.CRITICAL
        assert pending[1].priority == ApprovalPriority.HIGH
        assert pending[2].priority == ApprovalPriority.LOW

    def test_audit_trail(self):
        """Test audit trail creation."""
        from sruth.shared.hitl import ApprovalRequest, AuditEntry, InMemoryApprovalStore

        store = InMemoryApprovalStore()
        request = ApprovalRequest()

        entry = AuditEntry(
            event_type="request_created",
            request_id=request.id,
            actor_id="agent1",
        )

        store.save_audit(entry)
        trail = store.get_audit_trail(request.id)

        assert len(trail) == 1
        assert trail[0].event_type == "request_created"

    def test_cleanup_expired(self):
        """Test cleanup of expired requests."""
        from sruth.shared.hitl import ApprovalRequest, ApprovalStatus, InMemoryApprovalStore

        store = InMemoryApprovalStore()

        # Create expired request
        expired = ApprovalRequest(timeout_seconds=1)
        expired.expires_at = datetime.now() - timedelta(seconds=1)

        store.save_request(expired)
        count = store.cleanup_expired()

        assert count == 1

        retrieved = store.get_request(expired.id)
        assert retrieved.status == ApprovalStatus.EXPIRED


class TestHITLWorkflow:
    """Tests for HITLWorkflow."""

    @pytest.mark.asyncio
    async def test_workflow_creation(self):
        """Test HITLWorkflow creation."""
        from sruth.shared.hitl import HITLWorkflow

        workflow = HITLWorkflow()

        assert workflow.store is not None
        assert workflow.handler is not None

    @pytest.mark.asyncio
    async def test_get_pending(self):
        """Test getting pending requests from workflow."""
        from sruth.shared.hitl import ApprovalRequest, HITLWorkflow

        workflow = HITLWorkflow()

        # Add a request directly to store
        request = ApprovalRequest()
        workflow.store.save_request(request)

        pending = workflow.get_pending()

        assert len(pending) == 1
        assert pending[0].id == request.id

    @pytest.mark.asyncio
    async def test_respond_approve(self):
        """Test responding to approve a request."""
        from sruth.shared.hitl import (
            ApprovalRequest,
            ApprovalResponse,
            ApprovalStatus,
            HITLWorkflow,
        )

        workflow = HITLWorkflow()

        # Add request
        request = ApprovalRequest()
        workflow.store.save_request(request)

        # Respond
        response = ApprovalResponse(
            request_id=request.id,
            approved=True,
            responder_id="reviewer1",
        )

        updated = await workflow.respond(response)

        assert updated.status == ApprovalStatus.APPROVED
        assert updated.responder_id == "reviewer1"

    @pytest.mark.asyncio
    async def test_respond_reject(self):
        """Test responding to reject a request."""
        from sruth.shared.hitl import (
            ApprovalRequest,
            ApprovalResponse,
            ApprovalStatus,
            HITLWorkflow,
        )

        workflow = HITLWorkflow()

        request = ApprovalRequest()
        workflow.store.save_request(request)

        response = ApprovalResponse(
            request_id=request.id,
            approved=False,
            responder_id="reviewer1",
            notes="Too risky",
        )

        updated = await workflow.respond(response)

        assert updated.status == ApprovalStatus.REJECTED
        assert updated.response_notes == "Too risky"

    @pytest.mark.asyncio
    async def test_cancel_request(self):
        """Test cancelling a request."""
        from sruth.shared.hitl import ApprovalRequest, ApprovalStatus, HITLWorkflow

        workflow = HITLWorkflow()

        request = ApprovalRequest()
        workflow.store.save_request(request)

        cancelled = await workflow.cancel(request.id, reason="Changed mind")

        assert cancelled.status == ApprovalStatus.CANCELLED

    @pytest.mark.asyncio
    async def test_audit_trail_created(self):
        """Test audit trail is created during workflow."""
        from sruth.shared.hitl import (
            ApprovalRequest,
            ApprovalResponse,
            HITLWorkflow,
        )

        workflow = HITLWorkflow()

        # Add and respond to request
        request = ApprovalRequest()
        workflow.store.save_request(request)

        # Add initial audit entry (normally done by request_approval)
        from sruth.shared.hitl import AuditEntry
        workflow.store.save_audit(AuditEntry(
            event_type="request_created",
            request_id=request.id,
        ))

        response = ApprovalResponse(
            request_id=request.id,
            approved=True,
            responder_id="reviewer1",
        )
        await workflow.respond(response)

        trail = workflow.get_audit_trail(request.id)

        # Should have at least 2 entries: created and approved
        assert len(trail) >= 2
        events = [e.event_type for e in trail]
        assert "request_created" in events
        assert "approved" in events


class TestApprovalResult:
    """Tests for ApprovalResult."""

    def test_approval_result_approved(self):
        """Test ApprovalResult for approved request."""
        from sruth.shared.hitl import ApprovalRequest
        from sruth.shared.hitl.workflow import ApprovalResult

        request = ApprovalRequest()
        request.approve("user1")

        result = ApprovalResult(
            request=request,
            approved=True,
            responder_id="user1",
        )

        assert result.approved
        assert not result.rejected
        assert not result.expired

    def test_approval_result_rejected(self):
        """Test ApprovalResult for rejected request."""
        from sruth.shared.hitl import ApprovalRequest
        from sruth.shared.hitl.workflow import ApprovalResult

        request = ApprovalRequest()
        request.reject("user1", "Denied")

        result = ApprovalResult(
            request=request,
            approved=False,
            responder_id="user1",
            notes="Denied",
        )

        assert not result.approved
        assert result.rejected

    def test_approval_result_expired(self):
        """Test ApprovalResult for expired request."""
        from sruth.shared.hitl import ApprovalRequest, ApprovalStatus
        from sruth.shared.hitl.workflow import ApprovalResult

        request = ApprovalRequest()
        request.status = ApprovalStatus.EXPIRED

        result = ApprovalResult(
            request=request,
            approved=False,
            error="Request expired",
        )

        assert not result.approved
        assert result.expired
        assert not result.rejected  # Expired is different from rejected


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
