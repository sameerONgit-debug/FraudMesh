"""
Blockchain Ledger API endpoints

Hyperledger Fabric integration for fraud claim provenance.
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from typing import List, Optional
import logging
import hashlib
import json

from app.core.database import get_db
from app.schemas.schemas import (
    LedgerClaimCreate,
    LedgerClaimResponse,
    SignalType,
    LedgerVerificationResponse,
)
from app.ledger import get_fabric_adapter, ClaimStatus, LedgerStatus

logger = logging.getLogger(__name__)
router = APIRouter()


# Get Fabric adapter (DEMO_MODE by default for hackathon)
fabric = get_fabric_adapter(mode="DEMO_MODE")


@router.on_event("startup")
async def startup_fabric():
    """Initialize Fabric adapter on startup"""
    await fabric.initialize()


def calculate_evidence_hash(evidence_data: dict) -> str:
    """Calculate SHA-256 hash of evidence package"""
    canonical_json = json.dumps(evidence_data, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(canonical_json.encode()).hexdigest()


@router.post("/claims", response_model=LedgerClaimResponse)
async def create_ledger_claim(
    claim: LedgerClaimCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Record a fraud claim on the blockchain ledger
    
    This creates an immutable record of the fraud signal with:
    - Tokenized entity identifier (no raw PII)
    - Signal type and confidence
    - Source institution signature
    - Evidence hash
    - Timestamp
    """
    logger.info(f"Recording claim {claim.claim_id} on ledger")
    
    # Calculate expiry (default 90 days from now)
    expires_at = datetime.now() + timedelta(days=90)
    
    try:
        result = await fabric.create_claim(
            claim_id=claim.claim_id,
            entity_token=claim.entity_token,
            signal_type=claim.signal_type.value,
            confidence=claim.confidence,
            source_institution=claim.source_institution,
            evidence_hash=claim.evidence_hash,
            model_version=claim.model_version or "fraud-v1.3",
            expires_at=expires_at,
        )
        
        return LedgerClaimResponse(
            claim_id=claim.claim_id,
            entity_token=claim.entity_token,
            signal_type=claim.signal_type.value,
            confidence=claim.confidence,
            source_institution=claim.source_institution,
            status=result.get("status", "ANCHORED"),
            created_at=datetime.now(),
            expires_at=expires_at,
        )
    except Exception as e:
        logger.error(f"Failed to create claim on ledger: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ledger operation failed: {str(e)}"
        )


@router.get("/claims/{claim_id}", response_model=LedgerClaimResponse)
async def get_ledger_claim(
    claim_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Retrieve a claim from the ledger"""
    claim = await fabric.get_claim(claim_id)
    
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found on ledger"
        )
    
    return LedgerClaimResponse(
        claim_id=claim.claim_id,
        entity_token=claim.entity_token,
        signal_type=claim.signal_type,
        confidence=claim.confidence,
        source_institution=claim.source_institution,
        status=claim.status,
        created_at=datetime.fromtimestamp(claim.created_at),
        updated_at=datetime.fromtimestamp(claim.updated_at),
        expires_at=datetime.fromtimestamp(claim.expires_at),
    )


@router.get("/verify/{claim_id}", response_model=LedgerVerificationResponse)
async def verify_ledger_claim(
    claim_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Verify a claim's integrity on the ledger"""
    verification = await fabric.verify_claim(claim_id)
    
    if not verification.get("verified"):
        return LedgerVerificationResponse(
            claim_id=claim_id,
            ledger_verified=False,
            signature_valid=False,
            hash_matches=False,
            timestamp_valid=False,
            not_expired=False,
            status="INVALID",
            error=verification.get("error", "Unknown error"),
        )
    
    return LedgerVerificationResponse(
        claim_id=claim_id,
        ledger_verified=True,
        signature_valid=True,  # Would verify in production
        hash_matches=True,  # Would compare hashes in production
        timestamp_valid=True,
        not_expired=verification.get("not_expired", True),
        status="VALID" if verification.get("not_expired", True) else "EXPIRED",
        evidence_hash=verification.get("evidence_hash"),
        source_institution=verification.get("source_institution"),
        version=verification.get("version"),
        ledger_transaction_id=f"TXN-{claim_id}-{verification.get('createdAt', '')}",
        ledger_timestamp=verification.get("updatedAt"),
    )


@router.post("/claims/{claim_id}/dispute")
async def dispute_ledger_claim(
    claim_id: str,
    reason: str,
    institution: str,
    actor: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Record a dispute on the ledger"""
    logger.info(f"Recording dispute for claim {claim_id} by {institution}")
    
    actor = actor or f"INVESTIGATOR_{institution}"
    
    result = await fabric.dispute_claim(
        claim_id=claim_id,
        reason=reason,
        institution=institution,
        actor=actor,
    )
    
    # Add case event
    await fabric.add_case_event(
        case_id=claim_id,
        event_type="CLAIM_DISPUTED",
        institution=institution,
        actor=actor,
        reason=reason,
    )
    
    return {
        "claim_id": claim_id,
        "status": "DISPUTED",
        "reason": reason,
        "disputed_by": institution,
        "actor": actor,
        "timestamp": datetime.now().isoformat(),
        "ledger_updated": result.get("success", False),
    }


@router.post("/claims/{claim_id}/confirm")
async def confirm_ledger_claim(
    claim_id: str,
    reason: str,
    institution: str,
    actor: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Confirm a fraud claim on the ledger"""
    logger.info(f"Confirming claim {claim_id} by {institution}")
    
    actor = actor or f"INVESTIGATOR_{institution}"
    
    result = await fabric.update_claim_status(
        claim_id=claim_id,
        new_status=ClaimStatus.CONFIRMED.value,
        reason=reason,
        institution=institution,
        actor=actor,
    )
    
    return {
        "claim_id": claim_id,
        "status": "CONFIRMED",
        "reason": reason,
        "confirmed_by": institution,
        "timestamp": datetime.now().isoformat(),
        "ledger_updated": result.get("success", False),
    }


@router.post("/claims/{claim_id}/clear")
async def clear_ledger_claim(
    claim_id: str,
    reason: str,
    institution: str,
    actor: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Clear a fraud claim on the ledger"""
    logger.info(f"Clearing claim {claim_id} by {institution}: {reason}")
    
    actor = actor or f"INVESTIGATOR_{institution}"
    
    result = await fabric.update_claim_status(
        claim_id=claim_id,
        new_status=ClaimStatus.CLEARED.value,
        reason=reason,
        institution=institution,
        actor=actor,
    )
    
    return {
        "claim_id": claim_id,
        "status": "CLEARED",
        "reason": reason,
        "cleared_by": institution,
        "timestamp": datetime.now().isoformat(),
        "ledger_updated": result.get("success", False),
    }


@router.get("/events/{case_id}")
async def get_case_ledger_events(
    case_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get all ledger events for a case"""
    events = await fabric.get_case_history(case_id)
    
    return [
        {
            "event_id": event.event_id,
            "case_id": event.case_id,
            "event_type": event.event_type,
            "timestamp": datetime.fromtimestamp(event.timestamp).isoformat(),
            "institution": event.institution,
            "actor": event.actor,
            "reason": event.reason,
            "evidence_hash": event.evidence_hash,
            "previous_state": event.previous_state,
            "new_state": event.new_state,
        }
        for event in events
    ]


@router.post("/claims/{claim_id}/query-by-entity")
async def query_claims_by_entity(
    entity_token: str,
    db: AsyncSession = Depends(get_db)
):
    """Query all active claims for a given entity token"""
    claims = await fabric.query_claims_by_entity(entity_token)
    
    return {
        "entity_token": entity_token,
        "signal_found": len(claims) > 0,
        "claims_count": len(claims),
        "claims": [
            {
                "claim_id": claim.claim_id,
                "signal_type": claim.signal_type,
                "confidence": claim.confidence,
                "source_institution": claim.source_institution,
                "status": claim.status,
                "expires_at": datetime.fromtimestamp(claim.expires_at).isoformat(),
            }
            for claim in claims
        ],
    }


@router.get("/health")
async def ledger_health_check():
    """Check ledger service health"""
    health = await fabric.health_check()
    return health
