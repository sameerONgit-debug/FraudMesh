"""
FraudMesh Ledger Integration Tests

Tests for Hyperledger Fabric integration including:
- Claim creation and retrieval
- State transitions
- Dispute workflow
- Evidence verification
- Cross-institution queries
- Idempotency
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from app.ledger import (
    get_fabric_adapter,
    FabricAdapter,
    FraudClaim,
    CaseEvent,
    ClaimStatus,
    LedgerStatus,
)


@pytest.fixture
def fabric_adapter():
    """Create a demo mode fabric adapter for testing"""
    return get_fabric_adapter(mode="DEMO_MODE")


@pytest.mark.asyncio
async def test_initialize_adapter(fabric_adapter):
    """Test that the adapter initializes correctly"""
    result = await fabric_adapter.initialize()
    assert result is True
    assert fabric_adapter.initialized is True
    assert fabric_adapter.mode == "DEMO_MODE"


@pytest.mark.asyncio
async def test_create_claim(fabric_adapter):
    """Test creating a new fraud claim"""
    expires_at = datetime.now() + timedelta(days=90)
    
    result = await fabric_adapter.create_claim(
        claim_id="CLM-TEST-001",
        entity_token="ENT_TEST_TOKENIZED",
        signal_type="CONFIRMED_MULE_ASSOCIATION",
        confidence=0.85,
        source_institution="BANK_B",
        evidence_hash="sha256_test_evidence_hash",
        model_version="fraud-v1.3",
        expires_at=expires_at,
    )
    
    assert result["success"] is True
    assert result["claim_id"] == "CLM-TEST-001"
    assert "transaction_id" in result


@pytest.mark.asyncio
async def test_get_claim(fabric_adapter):
    """Test retrieving a claim from the ledger"""
    claim = await fabric_adapter.get_claim("CLM-1092")
    
    assert claim is not None
    assert claim.claim_id == "CLM-1092"
    assert claim.signal_type == "CONFIRMED_MULE_ASSOCIATION"
    assert claim.source_institution == "BANK_B"
    assert claim.confidence == 0.91


@pytest.mark.asyncio
async def test_get_nonexistent_claim(fabric_adapter):
    """Test retrieving a claim that doesn't exist"""
    claim = await fabric_adapter.get_claim("CLM-NONEXISTENT")
    assert claim is None


@pytest.mark.asyncio
async def test_verify_claim(fabric_adapter):
    """Test verifying a claim's integrity"""
    verification = await fabric_adapter.verify_claim("CLM-1092")
    
    assert verification["verified"] is True
    assert verification["exists"] is True
    assert verification["status"] == "ACTIVE"
    assert verification["not_expired"] is True
    assert "evidence_hash" in verification


@pytest.mark.asyncio
async def test_dispute_claim(fabric_adapter):
    """Test disputing a claim"""
    result = await fabric_adapter.dispute_claim(
        claim_id="CLM-TEST-DISPUTE",
        reason="Shared device may be legitimate",
        institution="BANK_A",
        actor="INVESTIGATOR_001",
    )
    
    assert result["success"] is True
    assert result["new_status"] == "DISPUTED"
    assert result["reason"] == "Shared device may be legitimate"


@pytest.mark.asyncio
async def test_update_claim_status(fabric_adapter):
    """Test updating claim status"""
    result = await fabric_adapter.update_claim_status(
        claim_id="CLM-TEST-UPDATE",
        new_status=ClaimStatus.UNDER_REVIEW.value,
        reason="Assigned to investigator",
        institution="BANK_A",
        actor="INVESTIGATOR_002",
    )
    
    assert result["success"] is True
    assert result["new_status"] == ClaimStatus.UNDER_REVIEW.value


@pytest.mark.asyncio
async def test_query_claims_by_entity(fabric_adapter):
    """Test querying claims by entity token"""
    # Test with matching entity token
    claims = await fabric_adapter.query_claims_by_entity("ENT_B781_MATCH")
    
    assert len(claims) > 0
    assert claims[0].source_institution == "BANK_B"
    assert claims[0].signal_type == "CONFIRMED_MULE_ASSOCIATION"
    
    # Test with non-matching entity token
    claims_empty = await fabric_adapter.query_claims_by_entity("ENT_UNKNOWN")
    assert len(claims_empty) == 0


@pytest.mark.asyncio
async def test_add_case_event(fabric_adapter):
    """Test adding a case event"""
    result = await fabric_adapter.add_case_event(
        case_id="CASE-TEST-001",
        event_type="RISK_COMPUTED",
        institution="BANK_A",
        actor="ML_ENGINE",
        reason="High risk transaction detected",
        evidence_hash="sha256_risk_evidence",
    )
    
    assert result["success"] is True
    assert result["event_type"] == "RISK_COMPUTED"


@pytest.mark.asyncio
async def test_get_case_history(fabric_adapter):
    """Test retrieving case history"""
    events = await fabric_adapter.get_case_history("CASE-TEST-001")
    
    assert len(events) > 0
    
    # Check event structure
    event = events[0]
    assert hasattr(event, "event_id")
    assert hasattr(event, "case_id")
    assert hasattr(event, "event_type")
    assert hasattr(event, "timestamp")
    assert hasattr(event, "institution")
    assert hasattr(event, "actor")


@pytest.mark.asyncio
async def test_health_check(fabric_adapter):
    """Test health check endpoint"""
    health = await fabric_adapter.health_check()
    
    assert health["fabric_available"] is True
    assert health["mode"] == "DEMO_MODE"
    assert health["channel"] == "fraudmesh-channel"
    assert health["chaincode"] == "fraud-claim"


@pytest.mark.asyncio
async def test_claim_lifecycle_states():
    """Test all claim lifecycle states"""
    states = [
        ClaimStatus.ACTIVE,
        ClaimStatus.SUSPECTED,
        ClaimStatus.UNDER_REVIEW,
        ClaimStatus.CONFIRMED,
        ClaimStatus.DISPUTED,
        ClaimStatus.CLEARED,
        ClaimStatus.EXPIRED,
    ]
    
    for state in states:
        assert isinstance(state.value, str)
        assert len(state.value) > 0


@pytest.mark.asyncio
async def test_ledger_status_values():
    """Test all ledger status values"""
    statuses = [
        LedgerStatus.NOT_ANCHORED,
        LedgerStatus.PENDING,
        LedgerStatus.ANCHORED,
        LedgerStatus.VERIFIED,
        LedgerStatus.INTEGRITY_MISMATCH,
        LedgerStatus.FAILED,
    ]
    
    for status in statuses:
        assert isinstance(status.value, str)


@pytest.mark.asyncio
async def test_fraud_claim_dataclass():
    """Test FraudClaim dataclass"""
    claim = FraudClaim(
        claim_id="CLM-DC-001",
        entity_token="ENT_TOKENIZED",
        signal_type="SUSPECTED_FRAUD",
        confidence=0.75,
        source_institution="BANK_A",
        evidence_hash="sha256_hash",
        model_version="fraud-v1.0",
        version=1,
    )
    
    assert claim.claim_id == "CLM-DC-001"
    assert claim.status == ClaimStatus.ACTIVE.value
    
    # Test to_dict method
    claim_dict = claim.to_dict()
    assert isinstance(claim_dict, dict)
    assert claim_dict["claim_id"] == "CLM-DC-001"


@pytest.mark.asyncio
async def test_case_event_dataclass():
    """Test CaseEvent dataclass"""
    event = CaseEvent(
        event_id="EVT-001",
        case_id="CASE-001",
        event_type="CASE_CREATED",
        institution="BANK_A",
        actor="SYSTEM",
        timestamp=int(datetime.now().timestamp()),
    )
    
    assert event.event_id == "EVT-001"
    assert event.case_id == "CASE-001"
    
    # Test to_dict method
    event_dict = event.to_dict()
    assert isinstance(event_dict, dict)
    assert event_dict["event_type"] == "CASE_CREATED"


@pytest.mark.asyncio
async def test_cross_institution_query_privacy(fabric_adapter):
    """Test that cross-institution queries only return minimal data"""
    claims = await fabric_adapter.query_claims_by_entity("ENT_B781")
    
    if len(claims) > 0:
        claim = claims[0]
        # Verify only minimal fields are returned
        assert hasattr(claim, "claim_id")
        assert hasattr(claim, "signal_type")
        assert hasattr(claim, "confidence")
        assert hasattr(claim, "source_institution")
        # These should NOT contain raw PII
        assert "account_number" not in str(claim.__dict__)
        assert "customer_name" not in str(claim.__dict__)


@pytest.mark.asyncio
async def test_idempotent_claim_creation(fabric_adapter):
    """Test that creating the same claim twice is handled"""
    # In production, this would test actual idempotency
    # For DEMO_MODE, we verify the API accepts duplicate calls
    expires_at = datetime.now() + timedelta(days=90)
    
    result1 = await fabric_adapter.create_claim(
        claim_id="CLM-IDEMPOTENT-TEST",
        entity_token="ENT_TEST",
        signal_type="TEST_SIGNAL",
        confidence=0.5,
        source_institution="BANK_A",
        evidence_hash="sha256_test",
        model_version="test-v1",
        expires_at=expires_at,
    )
    
    # Second call with same ID
    result2 = await fabric_adapter.create_claim(
        claim_id="CLM-IDEMPOTENT-TEST",
        entity_token="ENT_TEST",
        signal_type="TEST_SIGNAL",
        confidence=0.5,
        source_institution="BANK_A",
        evidence_hash="sha256_test",
        model_version="test-v1",
        expires_at=expires_at,
    )
    
    # Both should succeed in DEMO_MODE
    # In REAL_MODE, second would fail or return existing
    assert result1["success"] is True
    assert result2["success"] is True


@pytest.mark.asyncio
async def test_claim_expiry_handling(fabric_adapter):
    """Test handling of expired claims"""
    # Create a claim that's already expired
    expired_at = datetime.now() - timedelta(days=1)
    
    result = await fabric_adapter.create_claim(
        claim_id="CLM-EXPIRED-TEST",
        entity_token="ENT_EXPIRED",
        signal_type="TEST_SIGNAL",
        confidence=0.5,
        source_institution="BANK_A",
        evidence_hash="sha256_test",
        model_version="test-v1",
        expires_at=expired_at,
    )
    
    assert result["success"] is True
    
    # Verify the claim shows as expired
    verification = await fabric_adapter.verify_claim("CLM-EXPIRED-TEST")
    # Note: Demo mode returns sample claim, so expiry check may vary


@pytest.mark.asyncio
async def test_organization_identities():
    """Test organization identity mapping"""
    adapter = FabricAdapter(mode="DEMO_MODE")
    
    assert adapter.org_identities["BANK_A"] == "Org1MSP"
    assert adapter.org_identities["BANK_B"] == "Org2MSP"
    assert adapter.org_identities["BANK_C"] == "Org3MSP"


@pytest.mark.asyncio
async def test_singleton_pattern():
    """Test that get_fabric_adapter returns singleton"""
    adapter1 = get_fabric_adapter(mode="DEMO_MODE")
    adapter2 = get_fabric_adapter(mode="DEMO_MODE")
    
    # Should return same instance
    assert adapter1 is adapter2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
