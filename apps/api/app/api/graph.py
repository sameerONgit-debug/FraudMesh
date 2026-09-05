"""
Graph Analytics API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.schemas.schemas import GraphResponse, GraphNode, GraphEdge

router = APIRouter()


@router.get("/entity/{entity_id}", response_model=GraphResponse)
async def get_entity_graph(
    entity_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get graph relationships for an entity
    
    Returns connected nodes and edges with confidence scores.
    In production, this queries Neo4j.
    """
    # Simulated graph data for demo
    # In production: query Neo4j with Cypher
    
    nodes = [
        GraphNode(
            id=entity_id,
            label=entity_id,
            type="Account",
            risk_score=72.0,
            properties={"institution": "BANK_A"}
        ),
        GraphNode(
            id="DEV_442",
            label="Device DEV_442",
            type="Device",
            risk_score=65.0,
            properties={"first_seen": "2026-09-05T08:00:00", "device_type": "MOBILE"}
        ),
        GraphNode(
            id="ACC_B781",
            label="Account B781",
            type="Account",
            risk_score=88.0,
            properties={"institution": "BANK_B", "risk_state": "SUSPECTED"}
        ),
        GraphNode(
            id="ACC_B552",
            label="Account B552",
            type="Account",
            risk_score=95.0,
            properties={"institution": "BANK_B", "risk_state": "CONFIRMED_FRAUD"}
        ),
    ]
    
    edges = [
        GraphEdge(
            source=entity_id,
            target="DEV_442",
            relationship="USED",
            confidence=1.0,
            properties={"first_seen": "2026-09-05T09:30:00"}
        ),
        GraphEdge(
            source="ACC_B781",
            target="DEV_442",
            relationship="USED",
            confidence=0.95,
            properties={"first_seen": "2026-09-04T14:20:00"}
        ),
        GraphEdge(
            source="ACC_B781",
            target="ACC_B552",
            relationship="ASSOCIATED_WITH",
            confidence=0.85,
            properties={"reason": "shared_device", "case_id": "CLM-1092"}
        ),
    ]
    
    return GraphResponse(
        nodes=nodes,
        edges=edges,
        risk_path=[entity_id, "DEV_442", "ACC_B781", "ACC_B552"]
    )


@router.get("/case/{case_id}", response_model=GraphResponse)
async def get_case_graph(
    case_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get graph visualization for a fraud case"""
    # Simulated for demo
    nodes = [
        GraphNode(id="CASE_" + case_id, label=case_id, type="FraudCase", risk_score=97.0),
        GraphNode(id="TX_9822", label="₹85,000", type="Transaction", risk_score=97.0),
        GraphNode(id="ACC_A101", label="Victim A101", type="Account", risk_score=30.0),
        GraphNode(id="ACC_B781", label="Mule B781", type="Account", risk_score=88.0),
        GraphNode(id="DEV_442", label="Shared Device", type="Device", risk_score=65.0),
    ]
    
    edges = [
        GraphEdge(source="ACC_A101", target="TX_9822", relationship="SENT", confidence=1.0),
        GraphEdge(source="TX_9822", target="ACC_B781", relationship="RECEIVED", confidence=1.0),
        GraphEdge(source="ACC_B781", target="DEV_442", relationship="USED", confidence=0.95),
        GraphEdge(source="CASE_" + case_id, target="TX_9822", relationship="FLAGGED_BY", confidence=1.0),
    ]
    
    return GraphResponse(nodes=nodes, edges=edges)


@router.get("/path", response_model=GraphResponse)
async def get_risk_path(
    source: str,
    target: str,
    db: AsyncSession = Depends(get_db)
):
    """Find risk path between two entities"""
    # Simulated shortest path with risk explanation
    nodes = [
        GraphNode(id=source, label=source, type="Account", risk_score=72.0),
        GraphNode(id="INTERMEDIATE_1", label="Intermediate Node", type="Device", risk_score=65.0),
        GraphNode(id=target, label=target, type="Account", risk_score=88.0),
    ]
    
    edges = [
        GraphEdge(source=source, target="INTERMEDIATE_1", relationship="SHARED_DEVICE", confidence=0.71),
        GraphEdge(source="INTERMEDIATE_1", target=target, relationship="LINKED_TO", confidence=0.85),
    ]
    
    return GraphResponse(
        nodes=nodes,
        edges=edges,
        risk_path=[source, "INTERMEDIATE_1", target]
    )
