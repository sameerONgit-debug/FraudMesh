# FraudMesh

**Detect the Network. Verify the Signal. Preserve the Evidence.**

Cross-institution financial fraud intelligence platform for hackathon MVP.

## Core Pipeline

```
Transaction → Local AI Risk → Entity Resolution → Fraud Graph → 
Network Risk → Cross-Institution Signal → Final Risk → Explainability → 
Investigator → Case Decision → Evidence Ledger
```

## Quick Start

```bash
# Setup all services
make setup

# Seed demo data
make seed

# Run everything with Docker Compose
docker compose up

# Or run individual services
docker compose up postgres neo4j redis
docker compose up api
docker compose up web
```

Access:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Neo4j Browser: http://localhost:7474

## Demo Scenario

The seeded demo shows:

1. **Bank A** receives ₹85,000 suspicious transaction
2. **Local AI** scores risk at 72/100 (HIGH)
3. **Graph enrichment** discovers shared device → 88/100 (CRITICAL)
4. **Bank B signal** confirms mule association → 97/100 (CRITICAL)
5. **Investigator** reviews evidence, graph, and external signals
6. **Decision**: Confirm/Dispute/Clear with full audit trail
7. **Evidence** hashed and recorded on permissioned ledger

## Architecture

- **Frontend**: Next.js + React + TypeScript + Tailwind
- **Backend**: FastAPI (Python)
- **ML**: scikit-learn + XGBoost
- **Graph**: Neo4j with APOC
- **Database**: PostgreSQL
- **Cache**: Redis
- **Blockchain**: Hyperledger Fabric (permissioned)
- **Visualization**: Cytoscape.js

## Repository Structure

```
fraudmesh/
├── apps/
│   ├── web/              # Next.js frontend
│   └── api/              # FastAPI backend
├── services/
│   ├── ml-training/      # Model training pipeline
│   ├── graph-service/    # Neo4j operations
│   ├── ledger-service/   # Blockchain integration
│   └── simulator/        # Synthetic data generator
├── blockchain/
│   ├── fabric-network/   # Hyperledger config
│   └── chaincode/        # Smart contracts
├── data/
│   ├── raw/              # SQL init scripts
│   ├── processed/        # Processed datasets
│   └── synthetic/        # Generated test data
├── scripts/
│   └── seed_demo.py      # Demo scenario seeder
├── docker-compose.yml
├── Makefile
└── README.md
```

## Key Features

### AI Risk Engine
- Transaction-level fraud scoring
- Feature engineering (amount, velocity, beneficiary, device, location)
- User behavior features (historical patterns, deviations)
- Graph-derived features (network risk, community risk)
- Explainable predictions with feature impacts

### Fraud Graph
- Entity resolution across institutions
- Account, device, customer, transaction nodes
- Weighted relationships with confidence scores
- Risk propagation through network
- Suspicious cluster detection

### Cross-Institution Signals
- Privacy-preserving entity tokens (no raw PII)
- Minimal disclosure fraud signals
- Institution-signed claims
- Claim expiry and lifecycle management
- Verification and dispute workflow

### Evidence Ledger
- SHA-256 evidence hashing
- Permissioned blockchain (Hyperledger Fabric)
- Immutable audit trail
- Case event provenance
- Signature verification

### Investigator Dashboard
- Risk visualization with breakdown
- Interactive fraud graph
- External signal panel
- Evidence verification
- Case decision workflow (Confirm/Dispute/Clear)
- Full audit timeline

## Make Commands

```bash
make setup      # Initialize all services
make seed       # Seed demo scenario
make train      # Train ML models
make demo       # Run complete demo
make test       # Run tests
make reset      # Reset all data
```

## API Endpoints

- `POST /api/transactions` - Create transaction
- `POST /api/risk/score` - Calculate risk score
- `GET /api/risk/{id}` - Get risk assessment
- `GET /api/graph/entity/{id}` - Get entity graph
- `POST /api/signals/query` - Query cross-bank signals
- `GET /api/cases` - List cases
- `PATCH /api/cases/{id}/status` - Update case status
- `GET /api/evidence/{id}/verify` - Verify evidence
- `GET /api/ledger/claims/{id}` - Get ledger claim

## Privacy & Security

✓ No raw PII stored on ledger
✓ Institution-signed claims
✓ Claim expiry enforcement
✓ Full audit trail
✓ Role-based access control
✓ Purpose-bound queries
✓ Evidence integrity verification
✓ Dispute lifecycle

## What This MVP Does NOT Do

❌ Live UPI/bank integration
❌ Real customer data
❌ Automatic account freezing
❌ Production-scale blockchain
❌ Actual money movement

This is a **working hackathon prototype** demonstrating the core fraud intelligence loop.

## License

MIT License - Hackathon Project
