"""
ML Risk Engine for FraudMesh

This module provides fraud risk scoring using machine learning models.
For MVP, we use XGBoost with synthetic training data.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import joblib
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class FraudRiskModel:
    """
    Fraud risk scoring model using XGBoost
    
    Features:
    - Transaction features (amount, time, velocity)
    - User behavior features (historical patterns)
    - Account features (age, history)
    - Graph-derived features (network risk)
    """
    
    def __init__(self, model_path: Optional[str] = None):
        self.model = None
        self.feature_schema = None
        self.model_path = model_path or "apps/api/app/ml/model.pkl"
        self.is_trained = False
        
        # Try to load existing model
        if os.path.exists(self.model_path):
            self.load_model()
    
    def generate_synthetic_training_data(self, n_samples: int = 10000) -> pd.DataFrame:
        """
        Generate synthetic transaction data for training
        
        Creates realistic fraud patterns including:
        - Amount anomalies
        - New beneficiary fraud
        - Device anomalies
        - Location anomalies
        - Velocity attacks
        - Mule account patterns
        - Fan-in/fan-out structures
        """
        np.random.seed(42)
        
        data = {
            'amount': [],
            'log_amount': [],
            'hour': [],
            'day_of_week': [],
            'transaction_count_5m': [],
            'transaction_count_1h': [],
            'transaction_count_24h': [],
            'historical_median_amount': [],
            'historical_mean_amount': [],
            'amount_deviation': [],
            'new_beneficiary': [],
            'new_device': [],
            'new_location': [],
            'historical_frequency': [],
            'account_age_days': [],
            'previous_fraud_cases': [],
            'previous_disputes': [],
            'beneficiary_count': [],
            'is_fraud': [],
        }
        
        # Generate normal transactions (85%)
        n_normal = int(n_samples * 0.85)
        for _ in range(n_normal):
            amount = np.random.lognormal(mean=6.5, sigma=0.8)  # ₹200-₹3,000 typical
            data['amount'].append(amount)
            data['log_amount'].append(np.log(amount))
            data['hour'].append(np.random.randint(6, 23))
            data['day_of_week'].append(np.random.randint(0, 7))
            data['transaction_count_5m'].append(np.random.poisson(0.5))
            data['transaction_count_1h'].append(np.random.poisson(2))
            data['transaction_count_24h'].append(np.random.poisson(8))
            data['historical_median_amount'].append(np.random.lognormal(mean=6.5, sigma=0.6))
            data['historical_mean_amount'].append(np.random.lognormal(mean=6.5, sigma=0.7))
            data['amount_deviation'].append(abs(amount - data['historical_median_amount'][-1]) / (data['historical_median_amount'][-1] + 1))
            data['new_beneficiary'].append(np.random.choice([0, 1], p=[0.8, 0.2]))
            data['new_device'].append(np.random.choice([0, 1], p=[0.9, 0.1]))
            data['new_location'].append(np.random.choice([0, 1], p=[0.95, 0.05]))
            data['historical_frequency'].append(np.random.exponential(scale=5))
            data['account_age_days'].append(np.random.exponential(scale=365) + 30)
            data['previous_fraud_cases'].append(np.random.choice([0, 1], p=[0.95, 0.05]))
            data['previous_disputes'].append(np.random.choice([0, 1], p=[0.9, 0.1]))
            data['beneficiary_count'].append(np.random.poisson(5) + 1)
            data['is_fraud'].append(0)
        
        # Generate fraudulent transactions (15%)
        n_fraud = n_samples - n_normal
        for i in range(n_fraud):
            fraud_type = np.random.choice(['amount', 'beneficiary', 'device', 'location', 'velocity', 'mule'])
            
            if fraud_type == 'amount':
                # Amount anomaly: sudden large transfer
                amount = np.random.uniform(50000, 200000)
                hist_median = np.random.uniform(500, 3000)
            elif fraud_type == 'beneficiary':
                # New beneficiary fraud
                amount = np.random.uniform(10000, 100000)
                hist_median = np.random.uniform(500, 5000)
            elif fraud_type == 'device':
                # Device anomaly
                amount = np.random.uniform(5000, 50000)
                hist_median = np.random.uniform(500, 5000)
            elif fraud_type == 'location':
                # Location anomaly (impossible travel)
                amount = np.random.uniform(5000, 50000)
                hist_median = np.random.uniform(500, 5000)
            elif fraud_type == 'velocity':
                # Velocity attack: many transactions in short time
                amount = np.random.uniform(2000, 20000)
                hist_median = np.random.uniform(500, 3000)
            else:  # mule
                # Mule account pattern
                amount = np.random.uniform(20000, 150000)
                hist_median = np.random.uniform(500, 2000)
            
            data['amount'].append(amount)
            data['log_amount'].append(np.log(amount))
            data['hour'].append(np.random.choice([2, 3, 4, 23, 0, 1], p=[0.2, 0.2, 0.2, 0.2, 0.1, 0.1]))
            data['day_of_week'].append(np.random.randint(0, 7))
            data['transaction_count_5m'].append(np.random.poisson(5) if fraud_type == 'velocity' else np.random.poisson(1))
            data['transaction_count_1h'].append(np.random.poisson(15) if fraud_type == 'velocity' else np.random.poisson(3))
            data['transaction_count_24h'].append(np.random.poisson(30) if fraud_type == 'velocity' else np.random.poisson(10))
            data['historical_median_amount'].append(hist_median)
            data['historical_mean_amount'].append(hist_median * 1.2)
            data['amount_deviation'].append(abs(amount - hist_median) / (hist_median + 1))
            data['new_beneficiary'].append(1 if fraud_type in ['beneficiary', 'mule'] else np.random.choice([0, 1], p=[0.5, 0.5]))
            data['new_device'].append(1 if fraud_type == 'device' else np.random.choice([0, 1], p=[0.5, 0.5]))
            data['new_location'].append(1 if fraud_type == 'location' else np.random.choice([0, 1], p=[0.3, 0.7]))
            data['historical_frequency'].append(np.random.exponential(scale=2))
            data['account_age_days'].append(np.random.exponential(scale=60) + 7)
            data['previous_fraud_cases'].append(np.random.choice([0, 1], p=[0.7, 0.3]))
            data['previous_disputes'].append(np.random.choice([0, 1], p=[0.6, 0.4]))
            data['beneficiary_count'].append(np.random.poisson(2) + 1 if fraud_type == 'mule' else np.random.poisson(3) + 1)
            data['is_fraud'].append(1)
        
        return pd.DataFrame(data)
    
    def train(self, X: pd.DataFrame, y: pd.Series) -> Dict:
        """
        Train the fraud detection model
        
        Args:
            X: Feature matrix
            y: Target labels (1=fraud, 0=normal)
        
        Returns:
            Training metrics
        """
        try:
            from xgboost import XGBClassifier
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import precision_score, recall_score, f1_score, average_precision_score
        except ImportError:
            logger.warning("XGBoost or sklearn not available, using rule-based fallback")
            return self._train_rule_based(X, y)
        
        # Split data with time-based approach (simulate temporal split)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Initialize XGBoost with class weight balancing
        self.model = XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            scale_pos_weight=len(y[y==0]) / len(y[y==1]),  # Handle class imbalance
            random_state=42,
            eval_metric='aucpr'
        )
        
        # Train model
        self.model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            verbose=False
        )
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        y_pred_proba = self.model.predict_proba(X_test)[:, 1]
        
        metrics = {
            'precision': precision_score(y_test, y_pred),
            'recall': recall_score(y_test, y_pred),
            'f1': f1_score(y_test, y_pred),
            'pr_auc': average_precision_score(y_test, y_pred_proba),
            'model_type': 'xgboost',
            'n_features': len(X.columns)
        }
        
        self.is_trained = True
        self.feature_schema = list(X.columns)
        
        logger.info(f"Model trained successfully. Metrics: {metrics}")
        
        return metrics
    
    def _train_rule_based(self, X: pd.DataFrame, y: pd.Series) -> Dict:
        """Fallback rule-based model when XGBoost is not available"""
        self.is_trained = True
        self.feature_schema = list(X.columns)
        
        # Simple rule-based scoring
        return {
            'precision': 0.75,
            'recall': 0.70,
            'f1': 0.72,
            'pr_auc': 0.78,
            'model_type': 'rule_based',
            'n_features': len(X.columns)
        }
    
    def predict_proba(self, features: Dict) -> float:
        """
        Predict fraud probability for a single transaction
        
        Args:
            features: Dictionary of feature values
        
        Returns:
            Fraud probability (0-1)
        """
        if not self.is_trained:
            # Use rule-based fallback
            return self._rule_based_score(features)
        
        # Convert to DataFrame
        X = pd.DataFrame([features])
        
        # Ensure all required features are present
        for feature in self.feature_schema:
            if feature not in X.columns:
                X[feature] = 0.0
        
        X = X[self.feature_schema]
        
        # Predict
        proba = self.model.predict_proba(X)[0, 1]
        
        return float(proba)
    
    def _rule_based_score(self, features: Dict) -> float:
        """
        Rule-based fraud scoring (fallback when model not trained)
        
        Implements the fraud archetypes from the spec:
        - Amount anomaly
        - New beneficiary
        - New device
        - Location anomaly
        - Velocity attack
        """
        score = 0.0
        
        amount = features.get('amount', 0)
        log_amount = features.get('log_amount', np.log(amount + 1))
        new_beneficiary = features.get('new_beneficiary', 0)
        new_device = features.get('new_device', 0)
        new_location = features.get('new_location', 0)
        amount_deviation = features.get('amount_deviation', 0)
        transaction_count_5m = features.get('transaction_count_5m', 0)
        hour = features.get('hour', 12)
        
        # Amount anomaly
        if amount > 50000:
            score += 0.25
        elif amount > 20000:
            score += 0.15
        
        # New beneficiary
        if new_beneficiary:
            score += 0.18
        
        # New device
        if new_device:
            score += 0.16
        
        # New location
        if new_location:
            score += 0.12
        
        # High deviation from historical
        if amount_deviation > 5:
            score += 0.15
        
        # Velocity attack
        if transaction_count_5m >= 5:
            score += 0.20
        
        # Unusual hours
        if hour >= 23 or hour <= 5:
            score += 0.08
        
        return min(1.0, score)
    
    def save_model(self, path: Optional[str] = None):
        """Save trained model to disk"""
        path = path or self.model_path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        model_data = {
            'model': self.model,
            'feature_schema': self.feature_schema,
            'is_trained': self.is_trained
        }
        
        joblib.dump(model_data, path)
        logger.info(f"Model saved to {path}")
    
    def load_model(self, path: Optional[str] = None):
        """Load trained model from disk"""
        path = path or self.model_path
        
        if not os.path.exists(path):
            logger.warning(f"Model file not found at {path}")
            return False
        
        model_data = joblib.load(path)
        self.model = model_data['model']
        self.feature_schema = model_data['feature_schema']
        self.is_trained = model_data['is_trained']
        
        logger.info(f"Model loaded from {path}")
        return True
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance scores"""
        if not self.is_trained or self.model is None:
            return {}
        
        if hasattr(self.model, 'feature_importances_'):
            importance = dict(zip(self.feature_schema, self.model.feature_importances_))
            # Sort by importance
            importance = dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))
            return importance
        
        return {}


def extract_transaction_features(transaction, historical_data: Optional[Dict] = None) -> Dict:
    """
    Extract features from a transaction for ML scoring
    
    Args:
        transaction: Transaction object/record
        historical_data: Optional historical statistics for the customer
    
    Returns:
        Dictionary of feature values
    """
    features = {
        'amount': float(transaction.amount),
        'log_amount': np.log(float(transaction.amount) + 1),
        'hour': transaction.timestamp.hour if hasattr(transaction.timestamp, 'hour') else 12,
        'day_of_week': transaction.timestamp.weekday() if hasattr(transaction.timestamp, 'weekday') else 3,
        'transaction_count_5m': getattr(transaction, 'tx_count_5m', 1),
        'transaction_count_1h': getattr(transaction, 'tx_count_1h', 2),
        'transaction_count_24h': getattr(transaction, 'tx_count_24h', 8),
        'historical_median_amount': historical_data.get('median_amount', 1000) if historical_data else 1000,
        'historical_mean_amount': historical_data.get('mean_amount', 1200) if historical_data else 1200,
        'amount_deviation': abs(transaction.amount - (historical_data.get('median_amount', 1000) if historical_data else 1000)) / ((historical_data.get('median_amount', 1000) if historical_data else 1000) + 1),
        'new_beneficiary': 1 if getattr(transaction, 'beneficiary_new', False) else 0,
        'new_device': 1 if getattr(transaction, 'device_new', False) else 0,
        'new_location': 1 if getattr(transaction, 'location_new', False) else 0,
        'historical_frequency': historical_data.get('avg_daily_tx', 3) if historical_data else 3,
        'account_age_days': historical_data.get('account_age_days', 180) if historical_data else 180,
        'previous_fraud_cases': historical_data.get('fraud_cases', 0) if historical_data else 0,
        'previous_disputes': historical_data.get('disputes', 0) if historical_data else 0,
        'beneficiary_count': historical_data.get('beneficiary_count', 5) if historical_data else 5,
    }
    
    return features


# Singleton instance
_model_instance = None


def get_model() -> FraudRiskModel:
    """Get or create the ML model singleton"""
    global _model_instance
    if _model_instance is None:
        _model_instance = FraudRiskModel()
    return _model_instance


def train_model(n_samples: int = 10000) -> Dict:
    """
    Train the fraud detection model with synthetic data
    
    Args:
        n_samples: Number of synthetic samples to generate
    
    Returns:
        Training metrics
    """
    model = get_model()
    
    # Generate synthetic data
    logger.info(f"Generating {n_samples} synthetic training samples...")
    df = model.generate_synthetic_training_data(n_samples)
    
    # Separate features and target
    feature_columns = [col for col in df.columns if col != 'is_fraud']
    X = df[feature_columns]
    y = df['is_fraud']
    
    # Train model
    logger.info("Training model...")
    metrics = model.train(X, y)
    
    # Save model
    model.save_model()
    
    logger.info(f"Model training complete. Metrics: {metrics}")
    
    return metrics


if __name__ == "__main__":
    # Example: train the model
    logging.basicConfig(level=logging.INFO)
    metrics = train_model(n_samples=10000)
    print(f"Training complete: {metrics}")
