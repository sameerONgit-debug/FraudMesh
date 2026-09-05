#!/usr/bin/env python3
"""
Seed Demo Data Script for FraudMesh

This script creates the exact fraud scenario needed for the MVP demo:

Bank A receives a suspicious ₹85,000 transaction → AI flags it → 
graph discovers suspicious relationships → Bank B has a related fraud signal → 
risk increases → investigator sees the evidence → case is reviewed.
"""

import asyncio
import sys
from datetime import datetime, timedelta
import random

# Add parent directory to path
sys.path.insert(0, '/workspace/apps/api')

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text


async def seed_demo_data():
    """Seed the database with demo data"""
    
    # Database URL
    DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/fraudmesh"
    
    print("🏦 Seeding FraudMesh Demo Data...")
    print("=" * 60)
    
    # Create engine
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session_maker = async_sessionmaker(engine, class_=AsyncSession)
    
    async with async_session_maker() as session:
        # Clear existing data
        print("🧹 Clearing existing data...")
        await session.execute(text("TRUNCATE fraud_cases, case_events, evidence, transactions, devices, accounts, customers CASCADE"))
        await session.commit()
        
        # =====================================================
        # STEP 1: Create Customers
        # =====================================================
        print("\n👥 Creating customers...")
        
        customers = [
            {
                "customer_id": "CUS_001",
                "institution_id": "BANK_A",
                "name": "Rajesh Kumar (Victim)",
                "age": 42,
                "phone_hash": "PH_A001",
            },
            {
                "customer_id": "CUS_002",
                "institution_id": "BANK_B",
                "name": "Amit Sharma (Mule)",
                "age": 28,
                "phone_hash": "PH_B002",
            },
            {
                "customer_id": "CUS_003",
                "institution_id": "BANK_B",
                "name": "Vikram Singh (Fraudster)",
                "age": 35,
                "phone_hash": "PH_B003",
            },
        ]
        
        for customer in customers:
            await session.execute(text("""
                INSERT INTO customers (customer_id, institution_id, name, age, phone_hash, created_at, status)
                VALUES (:customer_id, :institution_id, :name, :age, :phone_hash, :created_at, :status)
            """), customer)
        
        await session.commit()
        print(f"   ✓ Created {len(customers)} customers")
        
        # =====================================================
        # STEP 2: Create Accounts
        # =====================================================
        print("\n💳 Creating accounts...")
        
        accounts = [
            {
                "account_id": "ACC_A101",
                "customer_id": "CUS_001",
                "institution_id": "BANK_A",
                "account_type": "SAVINGS",
                "risk_state": "NORMAL",
            },
            {
                "account_id": "ACC_B781",
                "customer_id": "CUS_002",
                "institution_id": "BANK_B",
                "account_type": "SAVINGS",
                "risk_state": "SUSPECTED",
            },
            {
                "account_id": "ACC_B552",
                "customer_id": "CUS_003",
                "institution_id": "BANK_B",
                "account_type": "CURRENT",
                "risk_state": "CONFIRMED",
            },
        ]
        
        for account in accounts:
            await session.execute(text("""
                INSERT INTO accounts (account_id, customer_id, institution_id, account_type, created_at, status, risk_state)
                VALUES (:account_id, :customer_id, :institution_id, :account_type, :created_at, :status, :risk_state)
            """), account)
        
        await session.commit()
        print(f"   ✓ Created {len(accounts)} accounts")
        
        # =====================================================
        # STEP 3: Create Devices
        # =====================================================
        print("\n📱 Creating devices...")
        
        devices = [
            {
                "device_id": "DEV_442",
                "device_type": "MOBILE",
                "first_seen": datetime.now() - timedelta(days=2),
                "last_seen": datetime.now(),
                "risk_score": 65.0,
            },
            {
                "device_id": "DEV_001",
                "device_type": "MOBILE",
                "first_seen": datetime.now() - timedelta(days=365),
                "last_seen": datetime.now(),
                "risk_score": 10.0,
            },
        ]
        
        for device in devices:
            await session.execute(text("""
                INSERT INTO devices (device_id, device_type, first_seen, last_seen, risk_score)
                VALUES (:device_id, :device_type, :first_seen, :last_seen, :risk_score)
            """), device)
        
        await session.commit()
        print(f"   ✓ Created {len(devices)} devices")
        
        # =====================================================
        # STEP 4: Create THE Suspicious Transaction (₹85,000)
        # =====================================================
        print("\n💰 Creating suspicious transaction...")
        
        suspicious_transaction = {
            "transaction_id": "TX_9822",
            "institution_id": "BANK_A",
            "sender_account": "ACC_A101",
            "receiver_account": "ACC_B781",
            "amount": 85000.0,
            "currency": "INR",
            "timestamp": datetime.now(),
            "device_id": "DEV_442",
            "ip_hash": "IP_HASH_9822",
            "location": "Bengaluru",
            "channel": "UPI",
            "beneficiary_new": True,
            "status": "PENDING",
        }
        
        await session.execute(text("""
            INSERT INTO transactions (
                transaction_id, institution_id, sender_account, receiver_account,
                amount, currency, timestamp, device_id, ip_hash, location,
                channel, beneficiary_new, status
            )
            VALUES (
                :transaction_id, :institution_id, :sender_account, :receiver_account,
                :amount, :currency, :timestamp, :device_id, :ip_hash, :location,
                :channel, :beneficiary_new, :status
            )
        """), suspicious_transaction)
        
        await session.commit()
        print(f"   ✓ Created suspicious transaction TX_9822: ₹85,000 from ACC_A101 to ACC_B781")
        
        # =====================================================
        # STEP 5: Create Normal Transactions (for comparison)
        # =====================================================
        print("\n📊 Creating normal transactions...")
        
        normal_transactions = [
            {
                "transaction_id": f"TX_{1000 + i}",
                "institution_id": "BANK_A",
                "sender_account": "ACC_A101",
                "receiver_account": "ACC_MERCHANT_" + str(i),
                "amount": random.uniform(200, 3000),
                "currency": "INR",
                "timestamp": datetime.now() - timedelta(days=random.randint(1, 30)),
                "device_id": "DEV_001",
                "location": "Bengaluru",
                "channel": "UPI",
                "beneficiary_new": False,
                "status": "COMPLETED",
            }
            for i in range(10)
        ]
        
        for tx in normal_transactions:
            await session.execute(text("""
                INSERT INTO transactions (
                    transaction_id, institution_id, sender_account, receiver_account,
                    amount, currency, timestamp, device_id, location, channel,
                    beneficiary_new, status
                )
                VALUES (
                    :transaction_id, :institution_id, :sender_account, :receiver_account,
                    :amount, :currency, :timestamp, :device_id, :location, :channel,
                    :beneficiary_new, :status
                )
            """), tx)
        
        await session.commit()
        print(f"   ✓ Created {len(normal_transactions)} normal transactions")
        
        # =====================================================
        # STEP 6: Create Fraud Case
        # =====================================================
        print("\n🚨 Creating fraud case...")
        
        fraud_case = {
            "case_id": "FM-DEMO-001",
            "transaction_id": "TX_9822",
            "institution_id": "BANK_A",
            "risk_score": 97.0,
            "risk_level": "CRITICAL",
            "state": "UNDER_REVIEW",
            "assigned_investigator": "INV_BANK_A_01",
            "resolution_reason": None,
        }
        
        await session.execute(text("""
            INSERT INTO fraud_cases (
                case_id, transaction_id, institution_id, risk_score,
                risk_level, state, assigned_investigator, resolution_reason,
                created_at, updated_at
            )
            VALUES (
                :case_id, :transaction_id, :institution_id, :risk_score,
                :risk_level, :state, :assigned_investigator, :resolution_reason,
                :created_at, :updated_at
            )
        """), {**fraud_case, "created_at": datetime.now(), "updated_at": datetime.now()})
        
        await session.commit()
        print(f"   ✓ Created fraud case FM-DEMO-001 with risk score 97/100 (CRITICAL)")
        
        # =====================================================
        # STEP 7: Create Case Events (Audit Trail)
        # =====================================================
        print("\n📝 Creating audit trail events...")
        
        events = [
            {
                "event_id": "EV_001",
                "case_id": "FM-DEMO-001",
                "event_type": "CASE_CREATED",
                "actor": "SYSTEM",
                "institution": "BANK_A",
                "reason": "High-risk transaction detected automatically",
                "evidence_hash": "hash_001",
            },
            {
                "event_id": "EV_002",
                "case_id": "FM-DEMO-001",
                "event_type": "RISK_COMPUTED",
                "actor": "ML_ENGINE",
                "institution": "BANK_A",
                "reason": "Local ML risk: 72, Graph risk: +21, External signal: +19",
                "evidence_hash": "hash_002",
            },
            {
                "event_id": "EV_003",
                "case_id": "FM-DEMO-001",
                "event_type": "GRAPH_ENRICHED",
                "actor": "GRAPH_SERVICE",
                "institution": "BANK_A",
                "reason": "Found shared device DEV_442 connecting to confirmed fraud account",
                "evidence_hash": "hash_003",
            },
            {
                "event_id": "EV_004",
                "case_id": "FM-DEMO-001",
                "event_type": "EXTERNAL_SIGNAL_RECEIVED",
                "actor": "SIGNAL_SERVICE",
                "institution": "BANK_A",
                "reason": "BANK_B confirmed mule association (Claim: CLM-1092)",
                "evidence_hash": "hash_004",
            },
            {
                "event_id": "EV_005",
                "case_id": "FM-DEMO-001",
                "event_type": "EVIDENCE_ANCHORED",
                "actor": "LEDGER_SERVICE",
                "institution": "BANK_A",
                "reason": "Evidence package hashed and recorded on blockchain",
                "evidence_hash": "sha256_e4f9a8b2c1d3e5f6...",
            },
            {
                "event_id": "EV_006",
                "case_id": "FM-DEMO-001",
                "event_type": "INVESTIGATION_STARTED",
                "actor": "INV_BANK_A_01",
                "institution": "BANK_A",
                "reason": "Case assigned to investigator for review",
                "evidence_hash": None,
            },
        ]
        
        for event in events:
            await session.execute(text("""
                INSERT INTO case_events (
                    event_id, case_id, event_type, actor, institution,
                    reason, evidence_hash, timestamp
                )
                VALUES (
                    :event_id, :case_id, :event_type, :actor, :institution,
                    :reason, :evidence_hash, :timestamp
                )
            """), {**event, "timestamp": datetime.now() - timedelta(minutes=len(events) - events.index(event))})
        
        await session.commit()
        print(f"   ✓ Created {len(events)} audit trail events")
        
        # =====================================================
        # SUMMARY
        # =====================================================
        print("\n" + "=" * 60)
        print("✅ Demo Data Seeding Complete!")
        print("=" * 60)
        print("\n📋 Demo Scenario Summary:")
        print("   • Victim Account: ACC_A101 (BANK_A)")
        print("   • Mule Account: ACC_B781 (BANK_B)")
        print("   • Fraudster Account: ACC_B552 (BANK_B)")
        print("   • Shared Device: DEV_442")
        print("   • Suspicious Transaction: TX_9822 (₹85,000)")
        print("   • Fraud Case: FM-DEMO-001")
        print("   • Risk Score: 97/100 (CRITICAL)")
        print("   • External Signal: CLM-1092 from BANK_B")
        print("\n🎯 Ready for Demo!")
        print("\n   To run the demo:")
        print("   1. Start services: docker compose up -d")
        print("   2. Open http://localhost:3000")
        print("   3. Navigate to Investigator Dashboard")
        print("   4. View case FM-DEMO-001")
        print("\n" + "=" * 60)


if __name__ == "__main__":
    try:
        asyncio.run(seed_demo_data())
    except Exception as e:
        print(f"❌ Error seeding demo data: {e}")
        sys.exit(1)
