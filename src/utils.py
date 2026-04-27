"""
Utility functions for saving reports and exporting CSV.
"""
import pandas as pd
import os

def save_report(df: pd.DataFrame, filepath: str):
    """
    Save DataFrame to CSV, create directory if needed.
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    df.to_csv(filepath, index=False)

def export_csv(df: pd.DataFrame) -> str:
    """
    Convert DataFrame to CSV string for download.
    """
    return df.to_csv(index=False).encode('utf-8')