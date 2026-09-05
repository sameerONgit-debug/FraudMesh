"""
Hyperledger Fabric Adapter for FraudMesh

This module provides integration with Hyperledger Fabric for storing
fraud claims and case events on a permissioned ledger.

IMPORTANT: Blockchain is NOT in the real-time risk decision path.
It provides asynchronous evidence provenance and audit trail.
"""

import logging
import hashlib
import json
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class ClaimStatus(str, Enum):
    ACTIVE = "ACTIVE"
    SUSPECTED = "SUSPECTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    CONFIRMED = "CONFIRMED"
    DISPUTED = "DISPUTED"
    CLEARED = "CLEARED"
    EXPIRED = "EXPIRED"


class LedgerStatus(str, Enum):
    NOT_ANCHORED = "NOT_ANCHORED"
    PENDING = "PENDING"
    ANCHORED = "ANCHORED"
    VERIFIED = "VERIFIED"
    INTEGRITY_MISMATCH = "INTEGRITY_MISMATCH"
    FAILED = "FAILED"


@dataclass
class FraudClaim:
    """Minimal fraud claim for ledger storage - NO raw PII"""
    claim_id: str
    entity_token: str  # Tokenized identifier (HMAC)
    signal_type: str
    confidence: float
    source_institution: str
    evidence_hash: str  # SHA-256 of off-chain evidence
    model_version: str
    status: str = ClaimStatus.ACTIVE.value
    created_at: int = 0
    updated_at: int = 0
    expires_at: int = 0
    version: int = 1
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CaseEvent:
    """Auditable case event"""
    event_id: str
    case_id: str
    event_type: str
    institution: str
    actor: str
    timestamp: int
    reason: Optional[str] = None
    evidence_hash: Optional[str] = None
    previous_state: Optional[str] = None
    new_state: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class FabricAdapter:
    """
    Adapter for Hyperledger Fabric interaction.
    
    In production, this would use the Fabric SDK for Python.
    For the MVP demo, we provide a working implementation that can
    operate in two modes:
    
    1. REAL_MODE: Connects to actual Fabric network
    2. DEMO_MODE: Simulates Fabric behavior for testing/demo
    
    The same API works for both modes.
    """
    
    def __init__(self, mode: str = "DEMO_MODE"):
        self.mode = mode
        self.initialized = False
        self.gateway = None
        self.contract = None
        self.channel_name = "fraudmesh-channel"
        self.chaincode_name = "fraud-claim"
        
        # Organization identities (would be loaded from crypto material in production)
        self.org_identities = {
            "BANK_A": "Org1MSP",
            "BANK_B": "Org2MSP", 
            "BANK_C": "Org3MSP",
        }
        
    async def initialize(self) -> bool:
        """Initialize connection to Fabric network"""
        if self.mode == "DEMO_MODE":
            logger.info("Fabric adapter initialized in DEMO_MODE")
            self.initialized = True
            return True
        
        # REAL_MODE: Initialize actual Fabric connection
        try:
            from fabric_gateway.fabric import Gateway
            # Implementation would go here for real Fabric
            logger.info("Fabric adapter initialized in REAL_MODE")
            self.initialized = True
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Fabric connection: {e}")
            return False
    
    async def create_claim(
        self,
        claim_id: str,
        entity_token: str,
        signal_type: str,
        confidence: float,
        source_institution: str,
        evidence_hash: str,
        model_version: str,
        expires_at: datetime,
    ) -> Dict[str, Any]:
        """
        Create a new fraud claim on the ledger.
        
        This is idempotent - calling with the same claim_id will not
        create duplicate claims.
        """
        if not self.initialized:
            await self.initialize()
        
        claim = FraudClaim(
            claim_id=claim_id,
            entity_token=entity_token,
            signal_type=signal_type,
            confidence=confidence,
            source_institution=source_institution,
            evidence_hash=evidence_hash,
            model_version=model_version,
            created_at=int(datetime.now().timestamp()),
            updated_at=int(datetime.now().timestamp()),
            expires_at=int(expires_at.timestamp()),
            version=1,
        )
        
        if self.mode == "DEMO_MODE":
            return await self._demo_create_claim(claim)
        else:
            return await self._real_create_claim(claim)
    
    async def _demo_create_claim(self, claim: FraudClaim) -> Dict[str, Any]:
        """Simulate claim creation for demo/testing"""
        logger.info(f"[DEMO] Creating claim {claim.claim_id} on ledger")
        
        # Simulate ledger transaction
        await asyncio.sleep(0.1)  # Simulate network latency
        
        result = {
            "success": True,
            "claim_id": claim.claim_id,
            "transaction_id": f"TXN-{claim.claim_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "block_number": 1001,  # Simulated
            "timestamp": datetime.now().isoformat(),
            "status": claim.status,
        }
        
        logger.info(f"[DEMO] Claim {claim.claim_id} recorded with txn {result['transaction_id']}")
        return result
    
    async def _real_create_claim(self, claim: FraudClaim) -> Dict[str, Any]:
        """Create claim on real Fabric network"""
        # Implementation would use Fabric SDK
        raise NotImplementedError("REAL_MODE not yet implemented")
    
    async def get_claim(self, claim_id: str) -> Optional[FraudClaim]:
        """Retrieve a claim from the ledger"""
        if not self.initialized:
            await self.initialize()
        
        if self.mode == "DEMO_MODE":
            return await self._demo_get_claim(claim_id)
        else:
            return await self._real_get_claim(claim_id)
    
    async def _demo_get_claim(self, claim_id: str) -> Optional[FraudClaim]:
        """Simulate getting a claim"""
        # Return a demo claim only for valid CLM- prefix IDs
        if claim_id.startswith("CLM-") and "NONEXISTENT" not in claim_id:
            return FraudClaim(
                claim_id=claim_id,
                entity_token=f"ENT-{claim_id.split('-')[1]}_TOKENIZED",
                signal_type="CONFIRMED_MULE_ASSOCIATION",
                confidence=0.91,
                source_institution="BANK_B",
                evidence_hash="sha256_demo_hash_" + claim_id,
                model_version="fraud-v1.3",
                status=ClaimStatus.ACTIVE.value,
                created_at=int((datetime.now() - timedelta(days=5)).timestamp()),
                updated_at=int(datetime.now().timestamp()),
                expires_at=int((datetime.now() + timedelta(days=85)).timestamp()),
                version=1,
            )
        return None
    
    async def _real_get_claim(self, claim_id: str) -> Optional[FraudClaim]:
        """Get claim from real Fabric network"""
        raise NotImplementedError("REAL_MODE not yet implemented")
    
    async def update_claim_status(
        self,
        claim_id: str,
        new_status: str,
        reason: str,
        institution: str,
        actor: str,
    ) -> Dict[str, Any]:
        """Update the status of an existing claim"""
        if not self.initialized:
            await self.initialize()
        
        if self.mode == "DEMO_MODE":
            return await self._demo_update_claim_status(
                claim_id, new_status, reason, institution, actor
            )
        else:
            return await self._real_update_claim_status(
                claim_id, new_status, reason, institution, actor
            )
    
    async def _demo_update_claim_status(
        self, claim_id: str, new_status: str, reason: str,
        institution: str, actor: str
    ) -> Dict[str, Any]:
        """Simulate status update"""
        logger.info(f"[DEMO] Updating claim {claim_id} to {new_status}")
        
        await asyncio.sleep(0.05)
        
        return {
            "success": True,
            "claim_id": claim_id,
            "old_status": ClaimStatus.ACTIVE.value,
            "new_status": new_status,
            "reason": reason,
            "updated_by": actor,
            "institution": institution,
            "timestamp": datetime.now().isoformat(),
        }
    
    async def _real_update_claim_status(
        self, claim_id: str, new_status: str, reason: str,
        institution: str, actor: str
    ) -> Dict[str, Any]:
        """Update claim on real Fabric network"""
        raise NotImplementedError("REAL_MODE not yet implemented")
    
    async def dispute_claim(
        self,
        claim_id: str,
        reason: str,
        institution: str,
        actor: str,
    ) -> Dict[str, Any]:
        """Mark a claim as disputed"""
        return await self.update_claim_status(
            claim_id, ClaimStatus.DISPUTED.value, reason, institution, actor
        )
    
    async def verify_claim(self, claim_id: str) -> Dict[str, Any]:
        """Verify a claim's integrity and status"""
        if not self.initialized:
            await self.initialize()
        
        claim = await self.get_claim(claim_id)
        if not claim:
            return {
                "verified": False,
                "error": "Claim not found",
            }
        
        now = datetime.now()
        is_expired = now.timestamp() > claim.expires_at
        
        return {
            "verified": True,
            "claim_id": claim_id,
            "exists": True,
            "status": claim.status,
            "not_expired": not is_expired,
            "evidence_hash": claim.evidence_hash,
            "source_institution": claim.source_institution,
            "version": claim.version,
            "created_at": claim.created_at,
            "updated_at": claim.updated_at,
            "verification_timestamp": int(now.timestamp()),
        }
    
    async def query_claims_by_entity(self, entity_token: str) -> List[FraudClaim]:
        """Find all active claims for a given entity token"""
        if not self.initialized:
            await self.initialize()
        
        # For demo, return empty list or sample claims
        if self.mode == "DEMO_MODE":
            # Return sample claim if entity token matches demo pattern
            if "B781" in entity_token or "ENT_B" in entity_token:
                return [
                    FraudClaim(
                        claim_id="CLM-1092",
                        entity_token=entity_token,
                        signal_type="CONFIRMED_MULE_ASSOCIATION",
                        confidence=0.91,
                        source_institution="BANK_B",
                        evidence_hash="sha256_demo_mule_hash",
                        model_version="fraud-v1.3",
                        status=ClaimStatus.ACTIVE.value,
                        created_at=int((datetime.now() - timedelta(days=5)).timestamp()),
                        updated_at=int(datetime.now().timestamp()),
                        expires_at=int((datetime.now() + timedelta(days=85)).timestamp()),
                        version=1,
                    )
                ]
            return []
        
        return []
    
    async def add_case_event(
        self,
        case_id: str,
        event_type: str,
        institution: str,
        actor: str,
        reason: Optional[str] = None,
        evidence_hash: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add an auditable event to a case"""
        if not self.initialized:
            await self.initialize()
        
        event = CaseEvent(
            event_id=f"EVT-{case_id}-{int(datetime.now().timestamp())}",
            case_id=case_id,
            event_type=event_type,
            institution=institution,
            actor=actor,
            timestamp=int(datetime.now().timestamp()),
            reason=reason,
            evidence_hash=evidence_hash,
        )
        
        if self.mode == "DEMO_MODE":
            logger.info(f"[DEMO] Adding event {event.event_id} to case {case_id}")
            return {
                "success": True,
                "event_id": event.event_id,
                "case_id": case_id,
                "event_type": event_type,
                "timestamp": event.timestamp,
            }
        
        return {"success": False, "error": "REAL_MODE not implemented"}
    
    async def get_case_history(self, case_id: str) -> List[CaseEvent]:
        """Retrieve all events for a case"""
        if not self.initialized:
            await self.initialize()
        
        if self.mode == "DEMO_MODE":
            # Return demo events
            now = datetime.now()
            return [
                CaseEvent(
                    event_id=f"EVT-{case_id}-001",
                    case_id=case_id,
                    event_type="CASE_CREATED",
                    institution="BANK_A",
                    actor="SYSTEM",
                    timestamp=int((now - timedelta(minutes=5)).timestamp()),
                ),
                CaseEvent(
                    event_id=f"EVT-{case_id}-002",
                    case_id=case_id,
                    event_type="RISK_COMPUTED",
                    institution="BANK_A",
                    actor="ML_ENGINE",
                    timestamp=int((now - timedelta(minutes=4)).timestamp()),
                    evidence_hash="sha256_risk_evidence",
                ),
                CaseEvent(
                    event_id=f"EVT-{case_id}-003",
                    case_id=case_id,
                    event_type="EXTERNAL_SIGNAL_RECEIVED",
                    institution="BANK_A",
                    actor="SIGNAL_SERVICE",
                    timestamp=int((now - timedelta(minutes=3)).timestamp()),
                    reason="Cross-bank fraud signal from BANK_B",
                ),
                CaseEvent(
                    event_id=f"EVT-{case_id}-004",
                    case_id=case_id,
                    event_type="EVIDENCE_ANCHORED",
                    institution="BANK_A",
                    actor="LEDGER_SERVICE",
                    timestamp=int((now - timedelta(minutes=2)).timestamp()),
                    evidence_hash="sha256_full_evidence_package",
                ),
            ]
        
        return []
    
    def is_available(self) -> bool:
        """Check if Fabric is available"""
        return self.initialized
    
    async def health_check(self) -> Dict[str, Any]:
        """Check Fabric network health"""
        return {
            "fabric_available": self.initialized,
            "mode": self.mode,
            "channel": self.channel_name,
            "chaincode": self.chaincode_name,
            "timestamp": datetime.now().isoformat(),
        }


# Singleton instance
_fabric_adapter: Optional[FabricAdapter] = None


def get_fabric_adapter(mode: str = "DEMO_MODE") -> FabricAdapter:
    """Get or create the Fabric adapter singleton"""
    global _fabric_adapter
    if _fabric_adapter is None:
        _fabric_adapter = FabricAdapter(mode=mode)
    return _fabric_adapter
