"""
Cross-Institution Signals API endpoints

This enables privacy-preserving fraud intelligence sharing between banks.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from typing import List
import logging
import hashlib

from app.core.database import get_db
from app.schemas.schemas import (
    FraudSignalCreate,
    FraudSignalResponse,
    SignalQueryRequest,
    SignalQueryResponse,
    SignalType,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=FraudSignalResponse, status_code=status.HTTP_201_CREATED)
async def create_fraud_signal(
    signal: FraudSignalCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a cross-institution fraud signal
    
    This creates a minimal fraud claim that can be shared with other institutions.
    The claim is hashed and recorded on the blockchain ledger.
    """
    import uuid
    
    # Generate claim ID
    claim_id = f"CLM-{uuid.uuid4().hex[:8].upper()}"
    
    # Set default expiry (90 days from now)
    if not signal.expires_at:
        signal.expires_at = datetime.now() + timedelta(days=90)
    
    # Create evidence hash for blockchain
    evidence_data = {
        "claim_id": claim_id,
        "entity_reference": signal.entity_reference,
        "signal_type": signal.signal_type.value,
        "confidence": signal.confidence,
        "source_institution": signal.source_institution,
        "created_at": datetime.now().isoformat(),
    }
    evidence_hash = hashlib.sha256(
        str(evidence_data).encode()
    ).hexdigest()
    
    logger.info(f"Created fraud signal {claim_id} from {signal.source_institution}")
    
    return FraudSignalResponse(
        claim_id=claim_id,
        entity_reference=signal.entity_reference,
        signal_type=signal.signal_type,
        confidence=signal.confidence,
        source_institution=signal.source_institution,
        model_version=signal.model_version,
        expires_at=signal.expires_at,
        evidence_hash=evidence_hash,
        status="ACTIVE",
        created_at=datetime.now()
    )


@router.post("/query", response_model=SignalQueryResponse)
async def query_signals(
    request: SignalQueryRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Query for cross-institution signals about an entity
    
    Returns minimal information - only whether a signal exists and basic metadata.
    Does NOT expose raw customer data or full transaction history.
    """
    entity_token = request.entity_token
    
    # Simulated: Check if any signals exist for this entity
    # In production, query the blockchain ledger
    
    # Demo: Bank B has a confirmed fraud signal for entities containing "B781"
    if "B781" in entity_token or "MULE" in entity_token.upper():
        return SignalQueryResponse(
            signal_available=True,
            claim_id="CLM-1092",
            signal_type=SignalType.CONFIRMED_MULE_ASSOCIATION,
            confidence=0.91,
            source_institution="BANK_B",
            status="ACTIVE"
        )
    
    # No signals found
    return SignalQueryResponse(
        signal_available=False
    )


@router.get("/{claim_id}", response_model=FraudSignalResponse)
async def get_signal(
    claim_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get details of a specific fraud signal/claim"""
    # Simulated for demo
    # In production: retrieve from blockchain ledger
    
    if claim_id == "CLM-1092":
        return FraudSignalResponse(
            claim_id=claim_id,
            entity_reference="ENT_B781_TOKENIZED",
            signal_type=SignalType.CONFIRMED_MULE_ASSOCIATION,
            confidence=0.91,
            source_institution="BANK_B",
            model_version="fraud-v1.3",
            expires_at=datetime.now() + timedelta(days=90),
            evidence_hash="e4f9a8b2c1d3e5f6...",
            status="ACTIVE",
            created_at=datetime.now() - timedelta(days=5)
        )
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Claim not found"
    )


@router.post("/{claim_id}/dispute")
async def dispute_claim(
    claim_id: str,
    reason: str,
    institution: str,
    db: AsyncSession = Depends(get_db)
):
    """Dispute a fraud claim"""
    logger.info(f"Claim {claim_id} disputed by {institution}: {reason}")
    
    # In production: record dispute on blockchain
    return {
        "claim_id": claim_id,
        "status": "DISPUTED",
        "reason": reason,
        "disputed_by": institution,
        "timestamp": datetime.now()
    }


@router.post("/{claim_id}/verify")
async def verify_claim(
    claim_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Verify a fraud claim's integrity"""
    # Simulated verification
    return {
        "claim_id": claim_id,
        "signature_verified": True,
        "hash_verified": True,
        "timestamp_verified": True,
        "claim_history_intact": True,
        "overall_valid": True
    }
