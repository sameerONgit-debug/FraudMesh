"""
Transaction API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.models.customer import Transaction as TransactionModel
from app.schemas.schemas import TransactionCreate, TransactionResponse

router = APIRouter()


@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction: TransactionCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new transaction
    
    This endpoint simulates receiving a transaction from a participating institution.
    The transaction will be scored for fraud risk automatically.
    """
    # Generate transaction ID
    import uuid
    transaction_id = f"TX_{uuid.uuid4().hex[:8].upper()}"
    
    # Create transaction record
    db_transaction = TransactionModel(
        transaction_id=transaction_id,
        **transaction.model_dump()
    )
    
    db.add(db_transaction)
    await db.commit()
    await db.refresh(db_transaction)
    
    return db_transaction


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a transaction by ID"""
    result = await db.execute(
        TransactionModel.__table__.select().where(
            TransactionModel.__table__.c.transaction_id == transaction_id
        )
    )
    transaction = result.fetchone()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    return transaction


@router.get("/", response_model=List[TransactionResponse])
async def list_transactions(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """List transactions with pagination"""
    result = await db.execute(
        TransactionModel.__table__.select()
        .offset(skip)
        .limit(limit)
    )
    transactions = result.fetchall()
    
    return transactions
