"""
Risk Scoring API endpoints

This is the core of FraudMesh - combining local ML risk, graph analytics,
and cross-institution signals to produce explainable fraud risk scores.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import List
import logging

from app.core.database import get_db
from app.schemas.schemas import (
    RiskScoreRequest,
    RiskScoreResponse,
    RiskLevel,
    RiskExplanation,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/score", response_model=RiskScoreResponse)
async def score_transaction(
    request: RiskScoreRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Score a transaction for fraud risk
    
    This endpoint calculates the final risk score by combining:
    1. Local ML model prediction
    2. Graph-derived risk from entity relationships
    3. Cross-institution trusted signals
    
    Returns an explainable risk score with feature contributions.
    """
    transaction_id = request.transaction_id
    
    # Step 1: Get transaction from database
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
    
    # Step 2: Calculate local ML risk
    local_ml_risk, ml_reasons = calculate_local_ml_risk(transaction)
    
    # Step 3: Calculate graph-derived risk
    graph_risk, graph_reasons = await calculate_graph_risk(transaction, db)
    
    # Step 4: Check for cross-institution signals
    external_risk, signal_reasons = await check_external_signals(transaction, db)
    
    # Step 5: Combine risks
    final_risk = min(100.0, local_ml_risk + graph_risk + external_risk)
    
    # Step 6: Determine risk level
    risk_level = determine_risk_level(final_risk)
    
    # Step 7: Compile all reasons
    all_reasons = ml_reasons + graph_reasons + signal_reasons
    
    # Step 8: Create case if risk is high
    if final_risk >= 60:
        await create_fraud_case_if_needed(transaction, final_risk, risk_level, db)
    
    logger.info(
        f"Risk scored for {transaction_id}: {final_risk:.1f} ({risk_level.value})"
    )
    
    return RiskScoreResponse(
        transaction_id=transaction_id,
        fraud_probability=final_risk,
        risk_level=risk_level,
        local_ml_risk=local_ml_risk,
        graph_risk=graph_risk,
        external_signal_risk=external_risk,
        final_risk=final_risk,
        reasons=all_reasons,
        timestamp=datetime.now()
    )


def calculate_local_ml_risk(transaction) -> tuple[float, List[RiskExplanation]]:
    """
    Calculate local ML-based risk score
    
    In production, this would use a trained XGBoost/LightGBM model.
    For MVP, we use rule-based heuristics that simulate ML behavior.
    """
    risk_score = 0.0
    reasons = []
    
    amount = transaction.amount
    hour = transaction.timestamp.hour if hasattr(transaction.timestamp, 'hour') else 12
    
    # Amount anomaly detection (simulating ML model)
    # Normal transactions are typically ₹200-₹3,000
    if amount > 50000:
        risk_score += 25.0
        reasons.append(RiskExplanation(
            feature="amount_deviation",
            impact=25.0,
            description=f"₹{amount:,.0f} is significantly higher than customer's normal transfer amount"
        ))
    elif amount > 20000:
        risk_score += 15.0
        reasons.append(RiskExplanation(
            feature="amount_deviation",
            impact=15.0,
            description=f"₹{amount:,.0f} is higher than typical transaction"
        ))
    
    # Time-based risk (late night transactions slightly riskier)
    if hour >= 23 or hour <= 5:
        risk_score += 8.0
        reasons.append(RiskExplanation(
            feature="unusual_hour",
            impact=8.0,
            description="Transaction occurred during unusual hours (11 PM - 5 AM)"
        ))
    
    # New beneficiary flag
    if getattr(transaction, 'beneficiary_new', False):
        risk_score += 18.0
        reasons.append(RiskExplanation(
            feature="new_beneficiary",
            impact=18.0,
            description="The beneficiary has never been used before"
        ))
    
    # Base risk for any transaction
    base_risk = 10.0
    risk_score += base_risk
    
    return min(70.0, risk_score), reasons


async def calculate_graph_risk(transaction, db) -> tuple[float, List[RiskExplanation]]:
    """
    Calculate graph-derived risk from entity relationships
    
    This uses Neo4j to find suspicious connections.
    For MVP, we simulate graph analytics.
    """
    risk_score = 0.0
    reasons = []
    
    # Simulate graph analysis
    # In production, this queries Neo4j for:
    # - Shared devices with known fraud accounts
    # - Shared phone numbers
    # - Distance to confirmed fraud nodes
    # - Suspicious community membership
    
    # Check if receiver account has suspicious connections
    receiver_account = transaction.receiver_account
    
    # Simulated: Check if receiver shares device with known fraud
    # This would be a Cypher query in production
    if "B781" in receiver_account or "MULE" in receiver_account.upper():
        risk_score += 21.0
        reasons.append(RiskExplanation(
            feature="network_risk",
            impact=21.0,
            description="The beneficiary has connections to accounts associated with unresolved fraud cases"
        ))
    
    # Simulated: Check for fan-in/fan-out patterns
    # Multiple accounts sending to same receiver
    if "B781" in receiver_account:
        risk_score += 15.0
        reasons.append(RiskExplanation(
            feature="suspicious_neighbor_count",
            impact=15.0,
            description="Multiple accounts have sent funds to this beneficiary in short timeframe"
        ))
    
    return risk_score, reasons


async def check_external_signals(transaction, db) -> tuple[float, List[RiskExplanation]]:
    """
    Check for cross-institution fraud signals
    
    This queries the network for trusted signals from other banks.
    For MVP demo, we simulate Bank B having a confirmed fraud signal.
    """
    risk_score = 0.0
    reasons = []
    
    receiver_account = transaction.receiver_account
    
    # Simulated: Check if Bank B has a confirmed fraud signal for this entity
    # In production, this would query the blockchain ledger
    if "B781" in receiver_account:
        risk_score += 19.0
        reasons.append(RiskExplanation(
            feature="external_signal",
            impact=19.0,
            description="Cross-institution signal: BANK_B has confirmed mule association (Claim: CLM-1092)"
        ))
    
    return risk_score, reasons


def determine_risk_level(risk_score: float) -> RiskLevel:
    """Determine risk level from score"""
    if risk_score >= 85:
        return RiskLevel.CRITICAL
    elif risk_score >= 60:
        return RiskLevel.HIGH
    elif risk_score >= 30:
        return RiskLevel.MODERATE
    else:
        return RiskLevel.LOW


async def create_fraud_case_if_needed(transaction, risk_score: float, risk_level: RiskLevel, db):
    """Create a fraud case for high-risk transactions"""
    import uuid
    
    # Check if case already exists
    result = await db.execute(
        FraudCaseModel.__table__.select().where(
            FraudCaseModel.__table__.c.transaction_id == transaction.transaction_id
        )
    )
    existing_case = result.fetchone()
    
    if existing_case:
        return  # Case already exists
    
    # Create new case
    case_id = f"FM-{uuid.uuid4().hex[:6].upper()}"
    
    case_data = {
        "case_id": case_id,
        "transaction_id": transaction.transaction_id,
        "institution_id": transaction.institution_id,
        "risk_score": risk_score,
        "risk_level": risk_level.value,
        "state": "SUSPECTED",
    }
    
    await db.execute(FraudCaseModel.__table__.insert().values(**case_data))
    await db.commit()
    
    logger.info(f"Created fraud case {case_id} for transaction {transaction.transaction_id}")


# Import models here to avoid circular imports
from app.models.customer import Transaction as TransactionModel, FraudCase as FraudCaseModel
