"""
Machine learning module using Isolation Forest.
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import LabelEncoder
import joblib
import os

def train_model(login_data: pd.DataFrame):
    """
    Train an Isolation Forest on engineered features.
    Returns the model and the feature matrix used.
    """
    # Copy and create features
    df = login_data.copy()
    # Encode device
    le = LabelEncoder()
    df['device_encoded'] = le.fit_transform(df['device'].astype(str))

    features = df[['hour', 'is_failed', 'total_logins', 'weekday', 'device_encoded']].copy()
    # Handle missing if any
    features = features.fillna(0)

    model = IsolationForest(contamination=0.1, random_state=42)
    model.fit(features)

    # Save model (optional for reuse)
    os.makedirs("models", exist_ok=True)
    joblib.dump(model, "models/isolation_forest.pkl")
    joblib.dump(le, "models/device_encoder.pkl")

    return model, features

def predict_anomalies(model, features: pd.DataFrame) -> pd.Series:
    """
    Predict anomalies using trained model.
    Returns a Series with 'Normal' or 'Suspicious'.
    """
    preds = model.predict(features)
    result = pd.Series(np.where(preds == -1, 'Suspicious', 'Normal'))
    return result