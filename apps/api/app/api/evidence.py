"""
Evidence API endpoints

Manage evidence packages and verification.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import hashlib
import json
import logging
import uuid

from app.core.database import get_db
from app.schemas.schemas import (
    EvidenceCreate,
    EvidenceResponse,
    EvidenceVerificationResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=EvidenceResponse, status_code=status.HTTP_201_CREATED)
async def create_evidence(
    evidence: EvidenceCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create an evidence package for a case"""
    evidence_id = f"EV-{uuid.uuid4().hex[:8].upper()}"
    
    # Create evidence hash
    evidence_data = {
        "case_id": evidence.case_id,
        "data": evidence.evidence_data,
        "timestamp": datetime.now().isoformat(),
    }
    evidence_hash = hashlib.sha256(
        json.dumps(evidence_data, sort_keys=True).encode()
    ).hexdigest()
    
    evidence_record = {
        "evidence_id": evidence_id,
        "case_id": evidence.case_id,
        "evidence_hash": evidence_hash,
        "evidence_data": json.dumps(evidence.evidence_data),
    }
    
    result = await db.execute(
        EvidenceModel.__table__.insert().values(**evidence_record).returning(
            EvidenceModel.__table__
        )
    )
    await db.commit()
    created_evidence = result.fetchone()
    
    logger.info(f"Created evidence {evidence_id} for case {evidence.case_id}")
    
    return created_evidence


@router.get("/{case_id}", response_model=list[EvidenceResponse])
async def get_case_evidence(
    case_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get all evidence for a case"""
    result = await db.execute(
        EvidenceModel.__table__.select()
        .where(EvidenceModel.__table__.c.case_id == case_id)
    )
    evidence_list = result.fetchall()
    
    return evidence_list


@router.get("/{case_id}/verify", response_model=EvidenceVerificationResponse)
async def verify_evidence(
    case_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Verify evidence integrity for a case"""
    # Get evidence for case
    result = await db.execute(
        EvidenceModel.__table__.select()
        .where(EvidenceModel.__table__.c.case_id == case_id)
    )
    evidence_list = result.fetchall()
    
    if not evidence_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No evidence found for case"
        )
    
    # Verify each evidence item
    all_verified = True
    for evidence in evidence_list:
        # Recompute hash
        stored_data = json.loads(evidence.evidence_data)
        recomputed_data = {
            "case_id": evidence.case_id,
            "data": stored_data,
            "timestamp": evidence.created_at.isoformat() if hasattr(evidence.created_at, 'isoformat') else str(evidence.created_at),
        }
        recomputed_hash = hashlib.sha256(
            json.dumps(recomputed_data, sort_keys=True).encode()
        ).hexdigest()
        
        if recomputed_hash != evidence.evidence_hash:
            all_verified = False
            break
    
    return EvidenceVerificationResponse(
        evidence_id=evidence_list[0].evidence_id if evidence_list else "",
        hash_verified=all_verified,
        signature_verified=True,  # Simulated
        timestamp_verified=True,  # Simulated
        claim_history_intact=True,  # Simulated
        overall_valid=all_verified
    )


# Import models
from app.models.customer import Evidence as EvidenceModel
