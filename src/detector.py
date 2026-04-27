"""
Rule‑based anomaly detection and risk scoring.
"""
import pandas as pd
import numpy as np
from typing import Tuple

def calculate_user_patterns(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Compute average login hour per user and merge with original data.
    Returns:
        user_patterns: aggregated user stats
        login_data: original df with additional columns (avg_hour, login_count, device_history)
    """
    # Group by user_id
    user_group = df.groupby('user_id').agg(
        avg_hour=('hour', 'mean'),
        total_logins=('login_time', 'count'),
        failed_attempts=('is_failed', 'sum'),
    ).reset_index()

    # Add success rate
    user_group['success_rate'] = 1 - (user_group['failed_attempts'] / user_group['total_logins'])

    # Merge back
    login_data = df.merge(user_group, on='user_id', how='left')

    # Device history: determine if device is new for each user
    login_data = login_data.sort_values(['user_id', 'login_time'])
    
    # A device is new if it's not the first login for the user AND
    # this specific (user_id, device) pair hasn't appeared before in previous rows.
    
    # 1. Identify which row is the first login for each user
    login_data['is_first_login'] = login_data.groupby('user_id').cumcount() == 0
    
    # 2. Identify if this device has been seen before for this user
    # duplicated() returns True for all occurrences except the first (within the group)
    login_data['device_seen_before'] = login_data.duplicated(subset=['user_id', 'device'], keep='first')
    
    # 3. A device is "new" if it's NOT the first login AND it hasn't been seen before
    login_data['new_device'] = (~login_data['is_first_login']) & (~login_data['device_seen_before'])
    
    # Clean up temporary columns
    login_data = login_data.drop(columns=['is_first_login', 'device_seen_before'])


    return user_group, login_data

def detect_rule_based(login_data: pd.DataFrame, user_patterns: pd.DataFrame, failed_threshold: int) -> pd.DataFrame:
    """
    Apply detection rules to each login event.
    Adds columns: is_anomaly, reasons.
    """
    df = login_data.copy()
    df['is_anomaly'] = False
    df['reason'] = ''

    # Rule 1: Suspicious time (3 AM)
    mask1 = df['hour'] == 3
    df.loc[mask1, 'is_anomaly'] = True
    df.loc[mask1, 'reason'] += "Suspicious time (3 AM); "

    # Rule 2: Time deviation > 4 hours from user's average
    df['time_deviation'] = (df['hour'] - df['avg_hour']).abs()
    mask2 = df['time_deviation'] > 4
    df.loc[mask2, 'is_anomaly'] = True
    df.loc[mask2, 'reason'] += "Time deviation > 4h; "

    # Rule 3: Too many failed attempts (count per user > threshold)
    df['too_many_fails'] = df['failed_attempts'] > failed_threshold
    # This is a per‑user condition; we flag all logins of a user with too many fails
    # Using user_patterns
    fail_users = user_patterns.loc[user_patterns['failed_attempts'] > failed_threshold, 'user_id'].tolist()
    mask3 = df['user_id'].isin(fail_users)
    df.loc[mask3, 'is_anomaly'] = True
    df.loc[mask3, 'reason'] += f"Failed attempts > {failed_threshold}; "

    # Rule 4: Frequency spike (not implemented in detail; placeholder)
    # For simplicity we check if a user has more than 5 logins in the dataset (as a spike indicator)
    df['high_freq'] = df['total_logins'] > 10
    mask4 = df['high_freq']
    df.loc[mask4, 'is_anomaly'] = True
    df.loc[mask4, 'reason'] += "High login frequency; "

    # Rule 5: New device
    mask5 = df['new_device']
    df.loc[mask5, 'is_anomaly'] = True
    df.loc[mask5, 'reason'] += "New device; "

    return df

def calculate_risk(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute risk score (0‑100) and risk level.
    """
    df = df.copy()
    df['risk_score'] = 0

    # Rule weights
    df.loc[df['hour'] == 3, 'risk_score'] += 40
    df.loc[(df['hour'] - df['avg_hour']).abs() > 4, 'risk_score'] += 25
    df.loc[df['is_failed'] == 1, 'risk_score'] += 20  # per failed event (cumulative effect)
    # For new device only if flagged
    df.loc[df['new_device'], 'risk_score'] += 15

    # Cap score at 100
    df['risk_score'] = df['risk_score'].clip(upper=100)

    # Classify risk
    bins = [0, 31, 61, 81, 101]
    labels = ['Low', 'Medium', 'High', 'Critical']
    df['risk_level'] = pd.cut(df['risk_score'], bins=bins, labels=labels, right=False)
    return df