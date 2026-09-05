"""
SQLAlchemy models for FraudMesh
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Enum, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class RiskState(str, enum.Enum):
    """Account risk states"""
    NORMAL = "NORMAL"
    MONITORED = "MONITORED"
    SUSPECTED = "SUSPECTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    CONFIRMED = "CONFIRMED"
    DISPUTED = "DISPUTED"
    CLEARED = "CLEARED"


class CaseState(str, enum.Enum):
    """Fraud case states"""
    SIGNAL_RECEIVED = "SIGNAL_RECEIVED"
    SUSPECTED = "SUSPECTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    CONFIRMED = "CONFIRMED"
    CLEARED = "CLEARED"
    DISPUTED = "DISPUTED"


class TransactionChannel(str, enum.Enum):
    """Transaction channels"""
    UPI = "UPI"
    CARD = "CARD"
    BANK_TRANSFER = "BANK_TRANSFER"
    WALLET = "WALLET"


class Customer(Base):
    """Customer model"""
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String, unique=True, nullable=False, index=True)
    institution_id = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    age = Column(Integer)
    phone_hash = Column(String, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, default="ACTIVE")
    
    # Relationships
    accounts = relationship("Account", back_populates="customer")


class Account(Base):
    """Account model"""
    __tablename__ = "accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(String, unique=True, nullable=False, index=True)
    customer_id = Column(String, ForeignKey("customers.customer_id"), nullable=False)
    institution_id = Column(String, nullable=False, index=True)
    account_type = Column(String, default="SAVINGS")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, default="ACTIVE")
    risk_state = Column(Enum(RiskState), default=RiskState.NORMAL)
    
    # Relationships
    customer = relationship("Customer", back_populates="accounts")
    transactions_sent = relationship("Transaction", foreign_keys="Transaction.sender_account", back_populates="sender")
    transactions_received = relationship("Transaction", foreign_keys="Transaction.receiver_account", back_populates="receiver")


class Device(Base):
    """Device model"""
    __tablename__ = "devices"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, unique=True, nullable=False, index=True)
    device_type = Column(String, default="MOBILE")
    first_seen = Column(DateTime(timezone=True), server_default=func.now())
    last_seen = Column(DateTime(timezone=True), server_default=func.now())
    risk_score = Column(Float, default=0.0)


class Transaction(Base):
    """Transaction model"""
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String, unique=True, nullable=False, index=True)
    institution_id = Column(String, nullable=False, index=True)
    sender_account = Column(String, ForeignKey("accounts.account_id"), nullable=False)
    receiver_account = Column(String, ForeignKey("accounts.account_id"), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="INR")
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    device_id = Column(String, ForeignKey("devices.device_id"))
    ip_hash = Column(String)
    location = Column(String)
    channel = Column(Enum(TransactionChannel), default=TransactionChannel.UPI)
    beneficiary_new = Column(Boolean, default=False)
    status = Column(String, default="PENDING")
    
    # Relationships
    sender = relationship("Account", foreign_keys=[sender_account], back_populates="transactions_sent")
    receiver = relationship("Account", foreign_keys=[receiver_account], back_populates="transactions_received")


class FraudCase(Base):
    """Fraud case model"""
    __tablename__ = "fraud_cases"
    
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(String, unique=True, nullable=False, index=True)
    transaction_id = Column(String, ForeignKey("transactions.transaction_id"), nullable=False)
    institution_id = Column(String, nullable=False, index=True)
    risk_score = Column(Float, nullable=False)
    risk_level = Column(String, nullable=False)
    state = Column(Enum(CaseState), default=CaseState.SIGNAL_RECEIVED)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    assigned_investigator = Column(String)
    resolution_reason = Column(Text)
    
    # Relationships
    transaction = relationship("Transaction")


class CaseEvent(Base):
    """Case event audit trail"""
    __tablename__ = "case_events"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, unique=True, nullable=False, index=True)
    case_id = Column(String, ForeignKey("fraud_cases.case_id"), nullable=False, index=True)
    event_type = Column(String, nullable=False)
    actor = Column(String, nullable=False)
    institution = Column(String, nullable=False)
    reason = Column(Text)
    evidence_hash = Column(String)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    case = relationship("FraudCase")


class Evidence(Base):
    """Evidence package"""
    __tablename__ = "evidence"
    
    id = Column(Integer, primary_key=True, index=True)
    evidence_id = Column(String, unique=True, nullable=False, index=True)
    case_id = Column(String, ForeignKey("fraud_cases.case_id"), nullable=False, index=True)
    evidence_hash = Column(String, nullable=False)
    evidence_data = Column(Text)  # JSON string
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    verified = Column(Boolean, default=False)
    
    # Relationships
    case = relationship("FraudCase")
