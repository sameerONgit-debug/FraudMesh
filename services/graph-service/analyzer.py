"""
Graph Analytics Service for FraudMesh

This module provides graph-based fraud detection using Neo4j.
Features:
- Entity resolution
- Risk propagation
- Community detection
- Path explanation
"""

from typing import Dict, List, Optional, Tuple, Set
from datetime import datetime, timedelta
import logging
import hashlib

logger = logging.getLogger(__name__)


class FraudGraphAnalyzer:
    """
    Graph analytics for fraud detection
    
    Uses Neo4j to find suspicious patterns:
    - Shared devices between accounts
    - Fan-in/fan-out structures
    - Distance to confirmed fraud
    - Suspicious communities
    """
    
    def __init__(self, neo4j_uri: Optional[str] = None, 
                 neo4j_user: Optional[str] = None,
                 neo4j_password: Optional[str] = None):
        self.neo4j_uri = neo4j_uri
        self.neo4j_user = neo4j_user
        self.neo4j_password = neo4j_password
        self.driver = None
        self.is_connected = False
        
        # Relationship confidence weights (from spec section 59)
        self.relationship_weights = {
            'confirmed_fraud': 1.0,
            'confirmed_mule': 1.0,
            'suspected_fraud': 0.5,
            'shared_device': 0.6,
            'shared_phone': 0.8,
            'shared_ip': 0.2,
            'same_beneficiary': 0.5,
            'rapid_succession': 0.4,
        }
        
        # Temporal decay parameter (lambda from spec section 60)
        self.decay_lambda = 0.01  # ~70 day half-life
    
    def connect(self):
        """Establish Neo4j connection"""
        try:
            from neo4j import GraphDatabase
            
            if not all([self.neo4j_uri, self.neo4j_user, self.neo4j_password]):
                logger.warning("Neo4j credentials not provided, using simulated mode")
                return False
            
            self.driver = GraphDatabase.driver(
                self.neo4j_uri,
                auth=(self.neo4j_user, self.neo4j_password)
            )
            
            # Test connection
            with self.driver.session() as session:
                session.run("MATCH (n) RETURN count(n) LIMIT 1")
            
            self.is_connected = True
            logger.info(f"Connected to Neo4j at {self.neo4j_uri}")
            return True
            
        except ImportError:
            logger.warning("Neo4j driver not installed, using simulated mode")
            return False
        except Exception as e:
            logger.warning(f"Failed to connect to Neo4j: {e}. Using simulated mode.")
            return False
    
    def close(self):
        """Close Neo4j connection"""
        if self.driver:
            self.driver.close()
            self.is_connected = False
    
    def resolve_entity(self, entity_type: str, identifier: str) -> Dict:
        """
        Resolve an entity to a canonical graph node
        
        Implements deterministic matching from spec section 15:
        - same device_id → confidence 1.0
        - same phone_hash → confidence 1.0
        - shared IP → confidence 0.3
        - same address → confidence 0.2
        
        Args:
            entity_type: Type of entity (device, phone, account, etc.)
            identifier: Unique identifier
        
        Returns:
            Resolved entity information
        """
        if not self.is_connected:
            # Simulated entity resolution
            return self._simulate_entity_resolution(entity_type, identifier)
        
        # In production, this would query Neo4j for existing entities
        # and merge/return the canonical node
        
        cypher = """
        MATCH (n:%s {identifier: $identifier})
        RETURN n
        """ % entity_type.upper()
        
        with self.driver.session() as session:
            result = session.run(cypher, identifier=identifier)
            existing = result.single()
            
            if existing:
                return {
                    'entity_id': existing['n'].id,
                    'confidence': 1.0,
                    'merged': False
                }
        
        # No existing entity found
        return {
            'entity_id': None,
            'confidence': 0.0,
            'merged': False
        }
    
    def _simulate_entity_resolution(self, entity_type: str, identifier: str) -> Dict:
        """Simulate entity resolution for demo mode"""
        # Generate deterministic entity ID
        entity_hash = hashlib.sha256(f"{entity_type}:{identifier}".encode()).hexdigest()[:12]
        
        return {
            'entity_id': f"{entity_type.upper()}_{entity_hash}",
            'confidence': 1.0 if entity_type in ['device', 'phone'] else 0.7,
            'merged': False
        }
    
    def calculate_graph_risk(self, account_id: str, 
                            relationships: Optional[List[Dict]] = None) -> Tuple[float, List[Dict]]:
        """
        Calculate graph-derived risk score for an account
        
        Implements risk propagation from spec section 18 & 59:
        GraphRisk(E) = Σ [neighbor_risk × edge_confidence × relationship_weight × time_decay]
        
        Args:
            account_id: Account to analyze
            relationships: Optional pre-fetched relationships
        
        Returns:
            Tuple of (risk_score, explanation_reasons)
        """
        if not self.is_connected:
            return self._simulate_graph_risk(account_id, relationships)
        
        # Query Neo4j for neighboring nodes and their risk levels
        cypher = """
        MATCH (acc:Account {account_id: $account_id})
        OPTIONAL MATCH (acc)-[r]-(neighbor)
        WHERE r.confidence IS NOT NULL
        RETURN 
            neighbor.risk_score as neighbor_risk,
            type(r) as relationship_type,
            r.confidence as confidence,
            r.first_seen as first_seen,
            r.source as source
        """
        
        risk_score = 0.0
        reasons = []
        
        with self.driver.session() as session:
            result = session.run(cypher, account_id=account_id)
            
            for record in result:
                neighbor_risk = record['neighbor_risk'] or 0
                rel_type = record['relationship_type']
                confidence = record['confidence'] or 0.5
                first_seen = record['first_seen']
                
                # Get relationship weight
                weight = self.relationship_weights.get(rel_type.lower(), 0.3)
                
                # Apply temporal decay
                if first_seen:
                    age_days = (datetime.now() - first_seen).days
                    decay = self._temporal_decay(age_days)
                else:
                    decay = 1.0
                
                # Calculate contribution
                contribution = neighbor_risk * confidence * weight * decay
                risk_score += contribution
                
                # Add explanation
                if contribution > 5:
                    reasons.append({
                        'feature': 'network_risk',
                        'impact': round(contribution, 1),
                        'description': f"Connected via {rel_type} to high-risk entity (confidence: {confidence:.2f})"
                    })
        
        return min(50.0, risk_score), reasons
    
    def _simulate_graph_risk(self, account_id: str, 
                            relationships: Optional[List[Dict]] = None) -> Tuple[float, List[Dict]]:
        """Simulate graph risk calculation for demo mode"""
        
        risk_score = 0.0
        reasons = []
        
        # Simulate: Check if account is connected to known mule
        if "B781" in account_id or "MULE" in account_id.upper():
            risk_score += 21.0
            reasons.append({
                'feature': 'network_risk',
                'impact': 21.0,
                'description': "The beneficiary has connections to accounts associated with unresolved fraud cases"
            })
            
            risk_score += 15.0
            reasons.append({
                'feature': 'suspicious_neighbor_count',
                'impact': 15.0,
                'description': "Multiple accounts have sent funds to this beneficiary in short timeframe"
            })
        
        # Simulate: Check for fan-in pattern
        if "B781" in account_id:
            risk_score += 12.0
            reasons.append({
                'feature': 'fan_in_pattern',
                'impact': 12.0,
                'description': "Fan-in pattern detected: multiple sources sending to single receiver"
            })
        
        return risk_score, reasons
    
    def _temporal_decay(self, age_days: int) -> float:
        """
        Calculate temporal decay factor
        
        Implements exponential decay from spec section 60:
        decay = exp(-λ × age_days)
        """
        import math
        return math.exp(-self.decay_lambda * age_days)
    
    def find_suspicious_paths(self, start_account: str, end_account: str, 
                             max_depth: int = 3) -> List[Dict]:
        """
        Find suspicious paths between two accounts
        
        Implements path explanation from spec section 18
        
        Args:
            start_account: Starting account ID
            end_account: Target account ID
            max_depth: Maximum path length
        
        Returns:
            List of paths with risk explanations
        """
        if not self.is_connected:
            return self._simulate_suspicious_paths(start_account, end_account)
        
        cypher = """
        MATCH path = (start:Account {account_id: $start})
                     -[*1..%d]-(end:Account {account_id: $end})
        WHERE ALL(rel IN relationships(path) WHERE rel.confidence > 0.3)
        RETURN path, 
               [rel IN relationships(path) | type(rel)] as rel_types,
               [rel IN relationships(path) | rel.confidence] as confidences
        """ % max_depth
        
        paths = []
        
        with self.driver.session() as session:
            result = session.run(cypher, start=start_account, end=end_account)
            
            for record in result:
                path_nodes = [node.id for node in record['path'].nodes]
                rel_types = record['rel_types']
                confidences = record['confidences']
                
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0
                
                paths.append({
                    'nodes': path_nodes,
                    'relationships': rel_types,
                    'avg_confidence': avg_confidence,
                    'length': len(path_nodes) - 1
                })
        
        # Sort by confidence and length
        paths.sort(key=lambda p: (-p['avg_confidence'], p['length']))
        
        return paths[:5]  # Return top 5 paths
    
    def _simulate_suspicious_paths(self, start_account: str, end_account: str) -> List[Dict]:
        """Simulate path finding for demo mode"""
        
        # Create demo path for the seed scenario
        if "A101" in start_account and "B781" in end_account:
            return [{
                'nodes': ['ACC_A101', 'DEV_442', 'ACC_B781', 'ACC_B552'],
                'relationships': ['USED', 'SHARED_DEVICE', 'FLAGGED_BY'],
                'avg_confidence': 0.85,
                'length': 3,
                'explanation': "Observed risk path through shared device"
            }]
        
        return []
    
    def detect_communities(self) -> List[Dict]:
        """
        Detect suspicious communities/clusters using Louvain algorithm
        
        Implements community detection from spec section 18
        
        Returns:
            List of detected communities with risk metrics
        """
        if not self.is_connected:
            return self._simulate_community_detection()
        
        # Use Neo4j Graph Data Science library
        cypher = """
        CALL gds.louvain.stream({
            nodeProjection: ['Account', 'Device', 'Phone'],
            relationshipProjection: {
                SHARED_DEVICE: {type: 'SHARED_DEVICE', orientation: 'UNDIRECTED'},
                SHARED_PHONE: {type: 'SHARED_PHONE', orientation: 'UNDIRECTED'},
                SENT_TO: {type: 'SENT_TO', orientation: 'DIRECTED'}
            },
            relationshipWeightProperty: 'confidence'
        })
        YIELD nodeId, communityId
        RETURN communityId, count(*) as size
        ORDER BY size DESC
        LIMIT 10
        """
        
        communities = []
        
        try:
            with self.driver.session() as session:
                result = session.run(cypher)
                
                for record in result:
                    communities.append({
                        'community_id': record['communityId'],
                        'size': record['size']
                    })
        except Exception as e:
            logger.warning(f"Community detection failed: {e}")
            return self._simulate_community_detection()
        
        return communities
    
    def _simulate_community_detection(self) -> List[Dict]:
        """Simulate community detection for demo mode"""
        return [
            {
                'community_id': 'COMM_001',
                'size': 12,
                'avg_risk': 0.78,
                'description': 'Suspected mule network with fan-in pattern'
            },
            {
                'community_id': 'COMM_002',
                'size': 7,
                'avg_risk': 0.65,
                'description': 'Cluster of accounts with shared devices'
            }
        ]
    
    def get_entity_details(self, entity_id: str) -> Dict:
        """
        Get detailed information about a graph entity
        
        Args:
            entity_id: Entity identifier
        
        Returns:
            Entity details including risk, relationships, metadata
        """
        if not self.is_connected:
            return self._simulate_entity_details(entity_id)
        
        cypher = """
        MATCH (n) WHERE id(n) = $entity_id OR n.account_id = $entity_id
        OPTIONAL MATCH (n)-[r]-(neighbor)
        RETURN 
            n,
            collect(DISTINCT {
                relationship: type(r),
                neighbor_id: neighbor.account_id,
                confidence: r.confidence
            }) as relationships
        """
        
        with self.driver.session() as session:
            result = session.run(cypher, entity_id=entity_id)
            record = result.single()
            
            if not record:
                return {'error': 'Entity not found'}
            
            return {
                'entity_id': entity_id,
                'risk_score': record['n'].get('risk_score', 0),
                'relationships': record['relationships'],
                'metadata': dict(record['n'])
            }
    
    def _simulate_entity_details(self, entity_id: str) -> Dict:
        """Simulate entity details for demo mode"""
        return {
            'entity_id': entity_id,
            'risk_score': 0.85 if "B781" in entity_id else 0.3,
            'relationships': [
                {
                    'relationship': 'SHARED_DEVICE',
                    'neighbor_id': 'ACC_B552',
                    'confidence': 0.91
                }
            ],
            'metadata': {
                'first_seen': (datetime.now() - timedelta(days=5)).isoformat(),
                'last_seen': datetime.now().isoformat(),
                'source': 'BANK_B'
            }
        }


# Singleton instance
_graph_instance = None


def get_graph_analyzer(neo4j_uri: Optional[str] = None,
                       neo4j_user: Optional[str] = None,
                       neo4j_password: Optional[str] = None) -> FraudGraphAnalyzer:
    """Get or create the graph analyzer singleton"""
    global _graph_instance
    if _graph_instance is None:
        _graph_instance = FraudGraphAnalyzer(neo4j_uri, neo4j_user, neo4j_password)
        _graph_instance.connect()
    return _graph_instance


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    analyzer = get_graph_analyzer()
    
    # Test graph risk calculation
    risk, reasons = analyzer.calculate_graph_risk("ACC_B781")
    print(f"Graph risk: {risk}")
    print(f"Reasons: {reasons}")
    
    # Test path finding
    paths = analyzer.find_suspicious_paths("ACC_A101", "ACC_B781")
    print(f"\nSuspicious paths: {len(paths)}")
    for path in paths:
        print(f"  Path: {path['nodes']}")
    
    analyzer.close()
