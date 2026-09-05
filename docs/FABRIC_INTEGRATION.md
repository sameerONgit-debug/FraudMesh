# FraudMesh Phase 2: Hyperledger Fabric Permissioned Blockchain Integration

## Overview

This document describes the implementation of a real Hyperledger Fabric permissioned blockchain network for the FraudMesh multi-institution fraud detection system.

**IMPORTANT**: Blockchain is NOT in the real-time fraud decision path. It provides asynchronous evidence provenance and cross-institution trust layer.

---

## Architecture Summary

### Why Blockchain?

PostgreSQL alone is insufficient for multi-institution fraud sharing because:

1. **No shared truth**: Each bank has its own database - no single source of truth
2. **Trust deficit**: Bank A cannot verify that Bank B's records haven't been modified
3. **Audit limitations**: No cryptographic proof of when claims were recorded
4. **Dispute resolution**: No immutable audit trail for regulatory review

Hyperledger Fabric provides:
- **Permissioned access**: Only authorized institutions can write/read
- **Immutable ledger**: Records cannot be altered retroactively
- **Cryptographic signatures**: Each transaction is signed by the submitting institution
- **Audit trail**: Complete history of all state changes
- **Privacy**: Channel-based data isolation between organizations

### What's On-Chain vs Off-Chain

**ON-CHAIN (Fabric Ledger)** - Minimal metadata only:
- Tokenized entity identifiers (HMAC, not raw PII)
- Signal type (e.g., `CONFIRMED_MULE_ASSOCIATION`)
- Confidence score (0.0-1.0)
- Source institution ID
- Evidence hash (SHA-256)
- Claim status and timestamps
- Case events (audit trail)

**OFF-CHAIN (PostgreSQL/Neo4j)** - All sensitive data:
- Customer names, PAN, Aadhaar, account numbers
- Raw transaction details
- Device fingerprints, IP addresses
- Full investigation files
- Graph relationship details

---

## Network Topology

### Organizations

| Org | Identity | Role |
|-----|----------|------|
| Org1MSP | BANK_A | Participating bank |
| Org2MSP | BANK_B | Participating bank |
| Org3MSP | BANK_C | Participating bank |

### Services

```
┌─────────────────────────────────────────────────────────────┐
│                    FraudMesh Network                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐               │
│  │  CA_Org1 │    │  CA_Org2 │    │  CA_Org3 │               │
│  │ :7054    │    │ :8054    │    │ :9054    │               │
│  └──────────┘    └──────────┘    └──────────┘               │
│                                                              │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐               │
│  │ Peer0    │    │ Peer0    │    │ Peer0    │               │
│  │ Org1     │    │ Org2     │    │ Org3     │               │
│  │ :7051    │    │ :8051    │    │ :9051    │               │
│  │ CouchDB0 │    │ CouchDB1 │    │ CouchDB2 │               │
│  │ :5984    │    │ :6984    │    │ :7984    │               │
│  └──────────┘    └──────────┘    └──────────┘               │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Orderer Service                          │   │
│  │              :7050                                    │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              CLI Tool                                 │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Channel

- **Channel Name**: `fraudmesh-channel`
- **Consortium**: `FraudMeshConsortium`
- **Chaincode**: `fraud-claim` v1.0

---

## Claim Lifecycle

### States

```
SIGNAL_RECEIVED → SUSPECTED → UNDER_REVIEW → CONFIRMED
                                       ↓
                                   DISPUTED
                                       ↓
                                   CLEARED
                                       ↓
                                   EXPIRED
```

### State Transitions

| From | To | Trigger |
|------|-----|---------|
| SIGNAL_RECEIVED | SUSPECTED | Initial risk threshold exceeded |
| SUSPECTED | UNDER_REVIEW | Investigator assigned |
| UNDER_REVIEW | CONFIRMED | Investigation confirms fraud |
| UNDER_REVIEW | CLEARED | Investigation clears suspicion |
| ANY_ACTIVE | DISPUTED | Institution disputes claim |
| ACTIVE | EXPIRED | Time-based expiry (90 days default) |

---

## Chaincode Functions

### FraudClaim Asset

```go
type FraudClaim struct {
    ClaimID           string  // Unique identifier
    EntityToken       string  // HMAC(tokenized_id)
    SignalType        string  // e.g., "CONFIRMED_MULE_ASSOCIATION"
    Confidence        float64 // 0.0 to 1.0
    SourceInstitution string  // e.g., "BANK_B"
    EvidenceHash      string  // SHA-256 of off-chain evidence
    ModelVersion      string  // e.g., "fraud-v1.3"
    Status            string  // ACTIVE, DISPUTED, etc.
    CreatedAt         int64   // Unix timestamp
    UpdatedAt         int64   // Unix timestamp
    ExpiresAt         int64   // Unix timestamp
    Version           int     // Incrementing version
}
```

### Smart Contract APIs

| Function | Description |
|----------|-------------|
| `CreateClaim` | Create new fraud claim (idempotent) |
| `GetClaim` | Retrieve claim by ID |
| `QueryClaimsByEntityToken` | Find claims for entity |
| `UpdateClaimState` | Update claim status |
| `DisputeClaim` | Mark claim as disputed |
| `ConfirmClaim` | Confirm claim validity |
| `ClearClaim` | Clear claim (false positive) |
| `ExpireClaim` | Mark claim expired |
| `AddCaseEvent` | Add audit event |
| `GetCaseHistory` | Get full case timeline |
| `VerifyClaim` | Verify claim integrity |

---

## REST API Endpoints

### Claims

```
POST   /api/ledger/claims          # Create new claim
GET    /api/ledger/claims/{id}     # Get claim
GET    /api/ledger/verify/{id}     # Verify claim
POST   /api/ledger/claims/{id}/dispute   # Dispute claim
POST   /api/ledger/claims/{id}/confirm   # Confirm claim
POST   /api/ledger/claims/{id}/clear     # Clear claim
GET    /api/ledger/events/{caseId} # Get case history
POST   /api/ledger/claims/{id}/query-by-entity  # Query by token
GET    /api/ledger/health          # Health check
```

### Example: Create Claim

```json
POST /api/ledger/claims
{
  "claimId": "CLM-1092",
  "entityToken": "ENT_B781_TOKENIZED",
  "signalType": "CONFIRMED_MULE_ASSOCIATION",
  "confidence": 0.91,
  "sourceInstitution": "BANK_B",
  "evidenceHash": "sha256_abc123...",
  "modelVersion": "fraud-v1.3"
}
```

### Example: Cross-Institution Query

```json
POST /api/ledger/claims/CLM-1092/query-by-entity?entityToken=ENT_B781
{
  "entity_token": "ENT_B781",
  "signal_found": true,
  "claims_count": 1,
  "claims": [
    {
      "claim_id": "CLM-1092",
      "signal_type": "CONFIRMED_MULE_ASSOCIATION",
      "confidence": 0.91,
      "source_institution": "BANK_B",
      "status": "ACTIVE",
      "expires_at": "2025-04-15T10:30:00Z"
    }
  ]
}
```

**Note**: Only minimal signal metadata is returned - NO raw transaction data from Bank B.

---

## Evidence Verification

### Process

1. Backend assembles canonical evidence package
2. Calculates SHA-256 hash
3. Stores full evidence off-chain (PostgreSQL)
4. Writes hash to Fabric ledger
5. Returns transaction ID

### Verification Endpoint

```
GET /api/ledger/verify/{claim_id}
```

Response:
```json
{
  "claim_id": "CLM-1092",
  "ledger_verified": true,
  "signature_valid": true,
  "hash_matches": true,
  "timestamp_valid": true,
  "not_expired": true,
  "status": "VALID",
  "evidence_hash": "sha256_abc123...",
  "source_institution": "BANK_B",
  "version": 1,
  "ledger_transaction_id": "TXN-CLM-1092-20250115103045",
  "ledger_timestamp": 1736938245
}
```

### Integrity Check

```python
async def verify_evidence(case_id: str) -> dict:
    """
    1. Retrieve current off-chain evidence
    2. Recreate canonical representation
    3. Calculate SHA-256
    4. Retrieve ledger hash
    5. Compare values
    6. Return VERIFIED or INTEGRITY_MISMATCH
    """
```

---

## Failure Handling

### Blockchain Unavailable

The system MUST NOT fail if Fabric is unavailable:

```
Transaction Risk Decision Path:
┌────────────┐    ┌──────────┐    ┌──────────┐    ┌───────────┐
│ Transaction│ →  │ ML Risk  │ →  │ Graph    │ →  │ Final     │
│            │    │ Engine   │    │ Enrich   │    │ Decision  │
└────────────┘    └──────────┘    └──────────┘    └───────────┘
                                             │
                                             ↓ (async)
                                      ┌──────────────┐
                                      │ Ledger Anchor│
                                      │ (retry queue)│
                                      └──────────────┘
```

### Retry Mechanism

```python
class LedgerSyncWorker:
    """Background worker for ledger operations"""
    
    async def process_pending_claims():
        # Identify PENDING claims
        # Retry with exponential backoff
        # Update status on success/failure
        # Log all attempts
```

### Status Values

| Status | Meaning |
|--------|---------|
| NOT_ANCHORED | Not yet submitted |
| PENDING | Submitted, awaiting confirmation |
| ANCHORED | Successfully recorded |
| VERIFIED | Hash verified against ledger |
| INTEGRITY_MISMATCH | Hash mismatch detected |
| FAILED | Ledger operation failed |

---

## Security Considerations

### Organization Identities

Each institution has separate credentials:

```
BANK_A_SERVICE → Org1MSP certificate
BANK_B_SERVICE → Org2MSP certificate
BANK_C_SERVICE → Org3MSP certificate
```

### Access Control

Application-level roles:
- `BANK_ANALYST`: View signals, create cases
- `INVESTIGATOR`: Update claim states, dispute
- `AUDITOR`: Read-only audit access
- `ADMIN`: Full access

### Key Management

**DO NOT hardcode private keys in source code.**

Use environment variables or mounted secrets:
```bash
export FABRIC_ORG1_KEY_PATH=/secrets/org1/msp/keystore
export FABRIC_ORG2_KEY_PATH=/secrets/org2/msp/keystore
```

---

## Demo Scenario

### Flow

1. **BANK_A** submits ₹85,000 transaction
2. **ML Risk Engine** scores: 72 (MEDIUM-HIGH)
3. **Fraud Graph** enrichment: +16 points → 88 (HIGH)
4. **Cross-institution query**: BANK_B claim found
   - Signal: `CONFIRMED_MULE_ASSOCIATION`
   - Confidence: 0.91
   - Adds: +9 points → 97 (CRITICAL)
5. **Final risk**: 97 → Case FM-DEMO-001 created
6. **Evidence package** generated, SHA-256 calculated
7. **Claim CLM-DEMO-001** anchored to Fabric
8. **Investigator** reviews case
   - Sees graph visualization
   - Reviews BANK_B signal
   - Verifies blockchain evidence ✓
9. **Dispute workflow**
   - Investigator disputes relationship
   - Reason: "Shared device may be legitimate"
   - Claim updated to DISPUTED
   - Event recorded on ledger
10. **Audit trail** shows complete history

---

## Commands

### Start Fabric Network

```bash
make fabric-up
```

### Check Status

```bash
make fabric-status
```

### Run Demo

```bash
make demo           # Full demo with real Fabric
make demo-simple    # Simplified demo (DEMO_MODE)
```

### Stop Network

```bash
make fabric-down
```

### Reset Everything

```bash
make fabric-reset
```

---

## Testing

### Ledger Tests

```bash
make test-ledger
```

Tests:
- Create claim
- Duplicate claim (idempotency)
- Get claim
- Update state
- Dispute flow
- Clear flow
- Expiry handling
- Case history
- Unauthorized mutation

### Evidence Tests

- Deterministic hashing
- Successful verification
- Modified evidence detection
- Mismatched ledger hash

### Cross-Institution Tests

- BANK_B creates claim
- BANK_A queries claim
- BANK_A receives minimal signal
- BANK_A cannot retrieve Bank B raw data

### End-to-End Test

```bash
make test-e2e
```

Reproduces full demo scenario programmatically.

---

## Known Limitations

### Prototype/Demo Network

This is a **development/demo network**, NOT production-ready:

1. **TLS certificates** are self-signed for demo purposes
2. **Single orderer** - production needs Raft consensus
3. **Simplified crypto** - use `cryptogen` or Fabric-CA in production
4. **No HSM** - keys stored on filesystem
5. **Demo mode** - API can simulate Fabric for testing

### Production Requirements

For actual deployment:

1. Proper CA infrastructure
2. Hardware Security Modules (HSM) for key storage
3. Raft ordering service (3+ nodes)
4. Production TLS certificates
5. Private channels for sensitive data
6. Regular key rotation
7. Comprehensive monitoring
8. Disaster recovery procedures

---

## File Structure

```
/workspace
├── blockchain/
│   ├── fabric-network/
│   │   ├── docker-compose-fabric.yml
│   │   ├── configtx.yaml
│   │   ├── scripts/
│   │   │   ├── generate-crypto.sh
│   │   │   └── create-channel-artifacts.sh
│   │   ├── crypto-config/
│   │   └── channel-artifacts/
│   └── chaincode/
│       └── go/fraud-claim/main.go
├── apps/api/app/
│   ├── ledger/
│   │   └── __init__.py      # Fabric adapter
│   └── api/
│       └── ledger.py         # REST endpoints
├── Makefile.fabric
└── docs/
    └── FABRIC_INTEGRATION.md
```

---

## Troubleshooting

### Fabric Network Won't Start

```bash
# Check Docker
docker ps

# View logs
docker logs fraudmesh-peer0-org1 -f

# Reset and try again
make fabric-reset
make fabric-up
```

### Crypto Material Issues

```bash
# Regenerate
rm -rf blockchain/fabric-network/crypto-config/*
make fabric-generate
```

### Channel Creation Fails

Ensure network is fully started:
```bash
sleep 30  # Wait for peers to initialize
make fabric-create-channel
```

---

## Additional Resources

- [Hyperledger Fabric Docs](https://hyperledger-fabric.readthedocs.io/)
- [Fabric Gateway SDK](https://github.com/hyperledger/fabric-gateway)
- [Fabric Samples](https://github.com/hyperledger/fabric-samples)

---

## Compliance Note

This implementation provides technical capabilities for multi-institution fraud signal sharing. Actual deployment requires:

1. Legal agreements between participating institutions
2. Regulatory compliance review (RBI, NPCI guidelines)
3. Data privacy impact assessment
4. Information sharing agreements
5. Audit procedures
6. Incident response plans

**Blockchain establishes provenance/integrity of claims and events. It does not establish that a fraud claim is objectively true.**
