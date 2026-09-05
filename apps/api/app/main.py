"""
FastAPI Backend for FraudMesh

Detect the Network. Verify the Signal. Preserve the Evidence.
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.core.database import get_db, init_db
from app.api import transactions, risk, graph, signals, cases, evidence, ledger, auth

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting FraudMesh API...")
    await init_db()
    logger.info("Database initialized")
    yield
    # Shutdown
    logger.info("Shutting down FraudMesh API...")


app = FastAPI(
    title="FraudMesh API",
    description="""
## FraudMesh - Cross-Institution Financial Fraud Intelligence
    
**Detect the Network. Verify the Signal. Preserve the Evidence.**
    
### Core Features
    
- **Transaction Risk Scoring**: AI-powered fraud detection
- **Graph Analytics**: Entity relationship mapping with Neo4j
- **Cross-Institution Signals**: Privacy-preserving fraud intelligence sharing
- **Evidence Ledger**: Blockchain-based provenance tracking
- **Case Management**: Investigator workflow with dispute resolution
    
### Demo Scenario
    
The MVP demonstrates:
1. Bank A receives suspicious ₹85,000 transaction
2. AI flags it (risk: 72/100)
3. Graph discovers relationships (risk: 88/100)
4. Bank B signal received (risk: 97/100)
5. Investigator reviews with full explainability
6. Case confirmed/disputed/cleared with audit trail
    """,
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(transactions.router, prefix="/transactions", tags=["Transactions"])
app.include_router(risk.router, prefix="/risk", tags=["Risk Scoring"])
app.include_router(graph.router, prefix="/graph", tags=["Graph Analytics"])
app.include_router(signals.router, prefix="/signals", tags=["Cross-Institution Signals"])
app.include_router(cases.router, prefix="/cases", tags=["Case Management"])
app.include_router(evidence.router, prefix="/evidence", tags=["Evidence"])
app.include_router(ledger.router, prefix="/ledger", tags=["Blockchain Ledger"])


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint"""
    return {
        "name": "FraudMesh API",
        "tagline": "Detect the Network. Verify the Signal. Preserve the Evidence.",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "fraudmesh-api"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True
    )
