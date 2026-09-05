"""
Case Management API endpoints

Investigator workflow for reviewing and resolving fraud cases.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import List
import logging
import uuid

from app.core.database import get_db
from app.schemas.schemas import (
    CaseCreate,
    CaseUpdate,
    CaseResponse,
    CaseEventCreate,
    CaseEventResponse,
    CaseStateEnum,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
async def create_case(
    case: CaseCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new fraud case"""
    case_id = f"FM-{uuid.uuid4().hex[:6].upper()}"
    
    case_data = {
        "case_id": case_id,
        "transaction_id": case.transaction_id,
        "institution_id": case.institution_id,
        "risk_score": case.risk_score,
        "risk_level": case.risk_level,
        "state": "SUSPECTED",
        "assigned_investigator": case.assigned_investigator,
    }
    
    result = await db.execute(
        FraudCaseModel.__table__.insert().values(**case_data).returning(
            FraudCaseModel.__table__
        )
    )
    await db.commit()
    created_case = result.fetchone()
    
    logger.info(f"Created fraud case {case_id}")
    
    return created_case


@router.get("/", response_model=List[CaseResponse])
async def list_cases(
    skip: int = 0,
    limit: int = 100,
    state: str = None,
    db: AsyncSession = Depends(get_db)
):
    """List fraud cases with optional filtering"""
    query = FraudCaseModel.__table__.select().offset(skip).limit(limit)
    
    if state:
        query = query.where(FraudCaseModel.__table__.c.state == state)
    
    result = await db.execute(query)
    cases = result.fetchall()
    
    return cases


@router.get("/{case_id}", response_model=CaseResponse)
async def get_case(
    case_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific fraud case"""
    result = await db.execute(
        FraudCaseModel.__table__.select().where(
            FraudCaseModel.__table__.c.case_id == case_id
        )
    )
    case = result.fetchone()
    
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )
    
    return case


@router.patch("/{case_id}/status", response_model=CaseResponse)
async def update_case_status(
    case_id: str,
    update: CaseUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update case status (confirm/dispute/clear)"""
    # Get existing case
    result = await db.execute(
        FraudCaseModel.__table__.select().where(
            FraudCaseModel.__table__.c.case_id == case_id
        )
    )
    case = result.fetchone()
    
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )
    
    # Update case
    update_data = {}
    if update.state:
        update_data["state"] = update.state.value
    if update.resolution_reason:
        update_data["resolution_reason"] = update.resolution_reason
    if update.assigned_investigator:
        update_data["assigned_investigator"] = update.assigned_investigator
    
    await db.execute(
        FraudCaseModel.__table__.update()
        .where(FraudCaseModel.__table__.c.case_id == case_id)
        .values(**update_data)
    )
    await db.commit()
    
    # Refresh and return
    result = await db.execute(
        FraudCaseModel.__table__.select().where(
            FraudCaseModel.__table__.c.case_id == case_id
        )
    )
    updated_case = result.fetchone()
    
    logger.info(f"Updated case {case_id} to {update_data.get('state', 'unchanged')}")
    
    return updated_case


@router.post("/{case_id}/events", response_model=CaseEventResponse)
async def create_case_event(
    case_id: str,
    event: CaseEventCreate,
    db: AsyncSession = Depends(get_db)
):
    """Add an event to the case audit trail"""
    event_id = f"EV-{uuid.uuid4().hex[:8].upper()}"
    
    event_data = {
        "event_id": event_id,
        "case_id": case_id,
        "event_type": event.event_type,
        "actor": event.actor,
        "institution": event.institution,
        "reason": event.reason,
        "evidence_hash": event.evidence_hash,
    }
    
    result = await db.execute(
        CaseEventModel.__table__.insert().values(**event_data).returning(
            CaseEventModel.__table__
        )
    )
    await db.commit()
    created_event = result.fetchone()
    
    logger.info(f"Added event {event_id} to case {case_id}")
    
    return created_event


@router.get("/{case_id}/events", response_model=List[CaseEventResponse])
async def get_case_events(
    case_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get all events for a case (audit trail)"""
    result = await db.execute(
        CaseEventModel.__table__.select()
        .where(CaseEventModel.__table__.c.case_id == case_id)
        .order_by(CaseEventModel.__table__.c.timestamp)
    )
    events = result.fetchall()
    
    return events


# Import models
from app.models.customer import FraudCase as FraudCaseModel, CaseEvent as CaseEventModel
