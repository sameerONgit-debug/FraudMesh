#!/usr/bin/env python3
"""
ML Model Training Script for FraudMesh

Trains the fraud detection model with synthetic data and saves it.
Run this before starting the API to have a trained model available.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml_training.risk_engine import train_model
import logging

def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("=" * 60)
    print("FraudMesh ML Model Training")
    print("=" * 60)
    
    # Train with 10,000 synthetic samples
    n_samples = 10000
    print(f"\nGenerating {n_samples} synthetic training samples...")
    print("This includes:")
    print("  - Normal transactions (85%)")
    print("  - Fraud patterns: amount anomaly, new beneficiary, device anomaly,")
    print("    location anomaly, velocity attacks, mule accounts")
    
    metrics = train_model(n_samples=n_samples)
    
    print("\n" + "=" * 60)
    print("Training Complete!")
    print("=" * 60)
    print(f"\nModel Metrics:")
    print(f"  Precision:  {metrics['precision']:.3f}")
    print(f"  Recall:     {metrics['recall']:.3f}")
    print(f"  F1 Score:   {metrics['f1']:.3f}")
    print(f"  PR-AUC:     {metrics['pr_auc']:.3f}")
    print(f"  Model Type: {metrics['model_type']}")
    print(f"  Features:   {metrics['n_features']}")
    
    print(f"\nModel saved to: apps/api/app/ml/model.pkl")
    print("\nYou can now start the API server.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
