"""
Data loading and validation module.
"""
import pandas as pd
from typing import Union, List
import os

def load_file(source: Union[str, "UploadedFile"]) -> pd.DataFrame:
    """
    Load CSV file from file path or Streamlit UploadedFile object.
    """
    try:
        if isinstance(source, str):
            df = pd.read_csv(source)
        else:
            df = pd.read_csv(source)
        return df
    except Exception as e:
        raise ValueError(f"Failed to load CSV: {e}")

def validate_columns(df: pd.DataFrame, required: List[str]) -> bool:
    """
    Check if the DataFrame contains all required columns.
    """
    return all(col in df.columns for col in required)