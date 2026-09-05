"""
Configuration settings for FraudMesh API
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "FraudMesh"
    APP_ENV: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    FRONTEND_URL: str = "http://localhost:3000"
    
    # Database - use asyncpg driver
    DATABASE_URL: str = "postgresql+asyncpg://fraudmesh:fraudmesh@localhost:5432/fraudmesh"
    
    # Neo4j
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "neo4j_password"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # JWT
    JWT_SECRET: str = "dev-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 60
    
    # Bank Institution Keys (for demo)
    BANK_A_PRIVATE_KEY: str = "bank_a_private_key_demo"
    BANK_B_PRIVATE_KEY: str = "bank_b_private_key_demo"
    BANK_C_PRIVATE_KEY: str = "bank_c_private_key_demo"
    
    # Hyperledger Fabric
    FABRIC_NETWORK: str = "fraudmesh-network"
    FABRIC_CHANNEL: str = "fraudchannel"
    FABRIC_CHAINCODE: str = "fraudcc"
    
    # ML Model
    MODEL_PATH: str = "./services/ml-training/models"
    FEATURE_SCHEMA_PATH: str = "./services/ml-training/feature_schema.json"
    
    # Risk thresholds
    RISK_THRESHOLD_LOW: int = 29
    RISK_THRESHOLD_MODERATE: int = 59
    RISK_THRESHOLD_HIGH: int = 84
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
