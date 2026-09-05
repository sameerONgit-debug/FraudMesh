"""
Pydantic schemas for FraudMesh API
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class RiskLevel(str, Enum):
    """Risk levels"""
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class CaseStateEnum(str, Enum):
    """Case states"""
    SIGNAL_RECEIVED = "SIGNAL_RECEIVED"
    SUSPECTED = "SUSPECTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    CONFIRMED = "CONFIRMED"
    CLEARED = "CLEARED"
    DISPUTED = "DISPUTED"


# Transaction Schemas
class TransactionBase(BaseModel):
    """Base transaction schema"""
    amount: float = Field(..., description="Transaction amount")
    currency: str = Field(default="INR", description="Currency code")
    receiver_account: str = Field(..., description="Receiver account ID")
    device_id: Optional[str] = Field(None, description="Device ID")
    location: Optional[str] = Field(None, description="Transaction location")
    channel: str = Field(default="UPI", description="Transaction channel")


class TransactionCreate(TransactionBase):
    """Schema for creating a transaction"""
    sender_account: str = Field(..., description="Sender account ID")
    institution_id: str = Field(..., description="Institution ID")


class TransactionResponse(TransactionBase):
    """Schema for transaction response"""
    id: int
    transaction_id: str
    institution_id: str
    sender_account: str
    timestamp: datetime
    status: str
    beneficiary_new: bool = False
    
    class Config:
        from_attributes = True


# Risk Scoring Schemas
class RiskScoreRequest(BaseModel):
    """Request schema for risk scoring"""
    transaction_id: str = Field(..., description="Transaction ID to score")


class RiskExplanation(BaseModel):
    """Risk explanation item"""
    feature: str
    impact: float
    description: Optional[str] = None


class RiskScoreResponse(BaseModel):
    """Response schema for risk scoring"""
    transaction_id: str
    fraud_probability: float = Field(..., ge=0, le=100)
    risk_level: RiskLevel
    local_ml_risk: float
    graph_risk: float = 0.0
    external_signal_risk: float = 0.0
    final_risk: float
    reasons: List[RiskExplanation] = []
    timestamp: datetime = Field(default_factory=datetime.now)


# Graph Schemas
class GraphNode(BaseModel):
    """Graph node representation"""
    id: str
    label: str
    type: str
    risk_score: float = 0.0
    properties: Dict[str, Any] = {}


class GraphEdge(BaseModel):
    """Graph edge representation"""
    source: str
    target: str
    relationship: str
    confidence: float = 1.0
    properties: Dict[str, Any] = {}


class GraphResponse(BaseModel):
    """Graph query response"""
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    risk_path: Optional[List[str]] = None


# Cross-Institution Signal Schemas
class SignalType(str, Enum):
    """Signal types for cross-institution sharing"""
    CONFIRMED_FRAUD = "CONFIRMED_FRAUD"
    CONFIRMED_MULE_ASSOCIATION = "CONFIRMED_MULE_ASSOCIATION"
    SUSPECTED_FRAUD = "SUSPECTED_FRAUD"
    HIGH_RISK_ENTITY = "HIGH_RISK_ENTITY"


class FraudSignalCreate(BaseModel):
    """Schema for creating a fraud signal"""
    entity_reference: str = Field(..., description="Tokenized entity identifier")
    signal_type: SignalType
    confidence: float = Field(..., ge=0, le=1)
    source_institution: str
    model_version: str = "fraud-v1.0"
    expires_at: Optional[datetime] = None


class FraudSignalResponse(FraudSignalCreate):
    """Response schema for fraud signal"""
    claim_id: str
    evidence_hash: str
    status: str = "ACTIVE"
    created_at: datetime
    
    class Config:
        from_attributes = True


class SignalQueryRequest(BaseModel):
    """Request schema for querying signals"""
    entity_token: str = Field(..., description="Tokenized entity to query")
    requesting_institution: str = Field(..., description="Requesting institution ID")


class SignalQueryResponse(BaseModel):
    """Response schema for signal query"""
    signal_available: bool
    claim_id: Optional[str] = None
    signal_type: Optional[SignalType] = None
    confidence: Optional[float] = None
    source_institution: Optional[str] = None
    status: Optional[str] = None


# Case Management Schemas
class CaseCreate(BaseModel):
    """Schema for creating a case"""
    transaction_id: str
    institution_id: str
    risk_score: float
    risk_level: str
    assigned_investigator: Optional[str] = None


class CaseUpdate(BaseModel):
    """Schema for updating a case"""
    state: Optional[CaseStateEnum] = None
    resolution_reason: Optional[str] = None
    assigned_investigator: Optional[str] = None


class CaseEventCreate(BaseModel):
    """Schema for creating a case event"""
    event_type: str
    actor: str
    institution: str
    reason: Optional[str] = None
    evidence_hash: Optional[str] = None


class CaseResponse(BaseModel):
    """Response schema for a case"""
    id: int
    case_id: str
    transaction_id: str
    institution_id: str
    risk_score: float
    risk_level: str
    state: CaseStateEnum
    created_at: datetime
    updated_at: datetime
    assigned_investigator: Optional[str] = None
    resolution_reason: Optional[str] = None
    
    class Config:
        from_attributes = True


class CaseEventResponse(BaseModel):
    """Response schema for case event"""
    id: int
    event_id: str
    case_id: str
    event_type: str
    actor: str
    institution: str
    reason: Optional[str] = None
    evidence_hash: Optional[str] = None
    timestamp: datetime
    
    class Config:
        from_attributes = True


# Evidence Schemas
class EvidenceCreate(BaseModel):
    """Schema for creating evidence"""
    case_id: str
    evidence_data: Dict[str, Any]


class EvidenceResponse(BaseModel):
    """Response schema for evidence"""
    id: int
    evidence_id: str
    case_id: str
    evidence_hash: str
    created_at: datetime
    verified: bool
    
    class Config:
        from_attributes = True


class EvidenceVerificationResponse(BaseModel):
    """Response schema for evidence verification"""
    evidence_id: str
    hash_verified: bool
    signature_verified: bool
    timestamp_verified: bool
    claim_history_intact: bool
    overall_valid: bool


# Ledger/Blockchain Schemas
class LedgerClaimCreate(BaseModel):
    """Schema for creating a ledger claim"""
    claim_id: str
    entity_token: str
    signal_type: SignalType
    confidence: float
    source_institution: str
    model_version: str
    evidence_hash: str


class LedgerClaimResponse(BaseModel):
    """Response schema for ledger claim"""
    claim_id: str
    entity_token: str
    signal_type: str
    confidence: float
    source_institution: str
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    transaction_id: Optional[str] = None
    
    class Config:
        from_attributes = True


class LedgerVerificationResponse(BaseModel):
    """Response schema for ledger verification"""
    claim_id: str
    ledger_verified: bool
    signature_valid: bool
    hash_matches: bool
    timestamp_valid: bool
    not_expired: bool
    status: str
    error: Optional[str] = None
    evidence_hash: Optional[str] = None
    source_institution: Optional[str] = None
    version: Optional[int] = None
    ledger_transaction_id: Optional[str] = None
    ledger_timestamp: Optional[int] = None
    
    class Config:
        from_attributes = True


# Authentication Schemas
class TokenData(BaseModel):
    """JWT token data"""
    sub: str
    institution_id: str
    role: str
    exp: datetime


class AuthRequest(BaseModel):
    """Authentication request"""
    username: str
    password: str
    institution_id: str


class AuthResponse(BaseModel):
    """Authentication response"""
    access_token: str
    token_type: str = "bearer"
    role: str
    institution_id: str


# Dashboard/Metrics Schemas
class DashboardMetrics(BaseModel):
    """Dashboard metrics response"""
    total_transactions: int
    high_risk_transactions: int
    open_investigations: int
    confirmed_fraud: int
    disputed_cases: int
    cleared_cases: int
    mule_networks_detected: int


class ModelComparisonResult(BaseModel):
    """Model comparison experiment result"""
    model_name: str
    precision: float
    recall: float
    f1_score: float
    pr_auc: float
    false_positive_rate: float
