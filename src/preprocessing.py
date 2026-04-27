"""
Data cleaning and feature extraction.
"""
import pandas as pd
import numpy as np

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Drop rows with missing critical values, parse login_time to datetime.
    """
    # Remove rows with null in user_id or login_time
    df = df.dropna(subset=['user_id', 'login_time'])
    # Parse datetime
    df['login_time'] = pd.to_datetime(df['login_time'], errors='coerce')
    df = df.dropna(subset=['login_time'])
    # Ensure status is string
    df['status'] = df['status'].astype(str).str.strip().str.capitalize()
    # Ensure device and location are strings
    df['device'] = df['device'].astype(str).str.strip()
    df['location'] = df['location'].astype(str).str.strip()
    return df.reset_index(drop=True)

def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add temporal features: hour, day, weekday, month.
    """
    df = df.copy()
    df['hour'] = df['login_time'].dt.hour
    df['day'] = df['login_time'].dt.day
    df['weekday'] = df['login_time'].dt.weekday  # 0=Monday, 6=Sunday
    df['month'] = df['login_time'].dt.month
    # Binary failed flag
    df['is_failed'] = (df['status'] == 'Failed').astype(int)
    return df