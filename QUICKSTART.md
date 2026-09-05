# FraudMesh Quick Start Guide

## Detect the Network. Verify the Signal. Preserve the Evidence.

FraudMesh is a cross-institution financial fraud intelligence platform that connects fragmented fraud signals while maintaining verifiable evidence provenance.

---

## 🚀 Quick Start (5 minutes)

### 1. Install Dependencies

```bash
cd /workspace
pip install -r requirements.txt
cd apps/web && npm install
```

### 2. Start Databases (Docker)

```bash
docker compose up -d postgres neo4j redis
```

### 3. Train ML Model

```bash
cd services/ml-training
python -c "from risk_engine import train_model, get_model; train_model(5000); get_model().save_model('../../apps/api/app/ml/model.pkl')"
```

### 4. Seed Demo Data

```bash
PYTHONPATH=/workspace python scripts/seed_demo.py
```

### 5. Start Services

**Terminal 1 - API:**
```bash
cd apps/api
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Web UI:**
```bash
cd apps/web
npm run dev
```

### 6. Open in Browser

- **API Docs:** http://localhost:8000/docs
- **Web UI:** http://localhost:3000

---

## 📋 Demo Scenario

The seeded demo includes:

| Component | Details |
|-----------|---------|
| **Transaction** | ₹85,000 from A-101 → B-781 |
| **Case ID** | FM-DEMO-001 |
| **Risk Progression** | 72 (ML) → 88 (+Graph) → 97 (+External Signal) |
| **Network Path** | A-101 → Device-442 → B-781 → B-552 (previous fraud) |
| **External Signal** | BANK_B confirmed mule association (CLM-1092) |

---

## 🎯 Live Demo Flow

1. **Transaction Received** → Bank A gets ₹85k transaction
2. **AI Risk Score** → Local ML flags as HIGH (72/100)
3. **Graph Enrichment** → Discovers shared device pattern (88/100)
4. **Cross-Bank Signal** → Bank B confirms mule association (97/100)
5. **Explainability** → Shows all risk factors with impact scores
6. **Evidence Verification** → Verify blockchain hash & signatures
7. **Investigator Review** → Confirm, dispute, or clear case
8. **Audit Trail** → Full timeline of all actions

---

## 🛠️ Makefile Commands

```bash
make setup     # Full setup (install + databases + train + seed)
make train     # Train ML model only
make seed      # Seed demo data only
make demo      # Run complete demo setup
make test      # Run tests
make reset     # Reset everything
make db-up     # Start databases
make api-up    # Start API server
make web-up    # Start web frontend
```

---

## 📁 Project Structure

```
fraudmesh/
├── apps/
│   ├── api/           # FastAPI backend
│   └── web/           # Next.js frontend
├── services/
│   ├── ml-training/   # ML model training
│   ├── graph-service/ # Neo4j analytics
│   ├── ledger-service/# Blockchain integration
│   └── simulator/     # Transaction generator
├── scripts/
│   └── seed_demo.py   # Demo scenario seeder
├── docker-compose.yml
├── requirements.txt
├── Makefile
└── README.md
```

---

## 🔑 Key Features

### ✅ Implemented (MVP)
- [x] Synthetic multi-bank transaction generation
- [x] Local ML fraud risk scoring (XGBoost)
- [x] Explainable risk reasons
- [x] Entity resolution
- [x] Neo4j-based fraud graph
- [x] Graph-derived fraud risk
- [x] Three simulated institutions (Bank A, B, C)
- [x] Minimal cross-institution fraud signals
- [x] Permissioned blockchain evidence layer
- [x] Signed fraud claims with expiry
- [x] Investigator case workflow
- [x] Claim dispute/clear/confirm
- [x] Full audit timeline
- [x] Privacy-preserving identifiers
- [x] No raw PII on-chain

### 🚧 Future Enhancements
- [ ] SHAP explanations
- [ ] Graph neural networks
- [ ] Real Hyperledger Fabric network
- [ ] Advanced fraud ring detection
- [ ] Model drift monitoring

---

## 🧪 Testing

```bash
# Run all tests
pytest apps/api/tests -v

# Test specific module
pytest apps/api/tests/test_risk.py -v
```

---

## 📊 Architecture

```
Transaction → Local AI Risk → Entity Resolution → Fraud Graph
                                                      ↓
                                              Network Risk
                                                      ↓
                                        Cross-Institution Signal
                                                      ↓
                                            Final Risk + Explanation
                                                      ↓
                           ┌──────────────────────────┴──────────────────────────┐
                           ↓                                                     ↓
                    Customer Action                                     Investigator
                                                                           ↓
                                                                    Case Decision
                                                                           ↓
                                                              Evidence Package
                                                                           ↓
                                                              Permissioned Ledger
                                                                           ↓
                                                               Audit History
```

---

## 🔒 Security & Privacy

- ✓ No raw PII stored on ledger
- ✓ Institution-signed claims
- ✓ Claim expiry (90 days default)
- ✓ Dispute lifecycle
- ✓ Full audit trail
- ✓ Role-based access control
- ✓ Purpose-bound queries
- ✓ Evidence integrity verification

---

## 🤝 What Makes FraudMesh Different

Unlike OneRadar-style systems that focus on individual transaction decisions, **FraudMesh's core contribution is:**

> **Connecting fragmented fraud intelligence across institutions and maintaining verifiable provenance for resulting claims and investigation history.**

Key differentiators:
1. **Cross-institution network effects** - Banks share minimal trusted signals
2. **Evidence provenance** - Blockchain provides tamper-evident audit trail
3. **Dispute mechanism** - Institutions can challenge claims
4. **Privacy-first design** - Tokenized identifiers, no raw PII sharing

---

## 📞 Support

For issues or questions:
1. Check API docs: http://localhost:8000/docs
2. Review logs in `apps/api/logs/`
3. See full documentation in `docs/`

---

**Built for hackathon MVP demonstration. Not for production use.**
