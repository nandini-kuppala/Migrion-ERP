"""Helper utility functions."""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List
import pandas as pd
import streamlit as st

from .config import LOGS_DIR


def setup_logger(name: str) -> logging.Logger:
    """Set up and configure logger."""
    logger = logging.Logger(name)

    # Create logs directory if it doesn't exist
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    # File handler
    log_file = LOGS_DIR / f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def save_json(data: Dict[str, Any], filepath: Path) -> None:
    """Save data to JSON file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)


def load_json(filepath: Path) -> Dict[str, Any]:
    """Load data from JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def init_session_state(key: str, default_value: Any) -> None:
    """Initialize session state variable if not exists."""
    if key not in st.session_state:
        st.session_state[key] = default_value


def get_session_state(key: str, default_value: Any = None) -> Any:
    """Get session state variable with default."""
    return st.session_state.get(key, default_value)


def set_session_state(key: str, value: Any) -> None:
    """Set session state variable."""
    st.session_state[key] = value


def clear_session_state() -> None:
    """Clear all session state."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]


def format_number(num: float, decimals: int = 2) -> str:
    """Format number with thousands separator."""
    if num >= 1_000_000:
        return f"{num/1_000_000:.{decimals}f}M"
    elif num >= 1_000:
        return f"{num/1_000:.{decimals}f}K"
    else:
        return f"{num:.{decimals}f}"


def format_percentage(value: float, decimals: int = 1) -> str:
    """Format value as percentage."""
    return f"{value:.{decimals}f}%"


def format_bytes(bytes_size: int) -> str:
    """Format bytes to human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} PB"


def calculate_data_quality_score(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate data quality metrics for a DataFrame."""
    total_cells = df.shape[0] * df.shape[1]
    missing_cells = df.isnull().sum().sum()
    missing_percentage = (missing_cells / total_cells * 100) if total_cells > 0 else 0

    duplicate_rows = df.duplicated().sum()
    duplicate_percentage = (duplicate_rows / len(df) * 100) if len(df) > 0 else 0

    # Calculate completeness score (0-1)
    completeness_score = 1 - (missing_percentage / 100)

    # Calculate uniqueness score (0-1)
    uniqueness_score = 1 - (duplicate_percentage / 100)

    # Overall quality score (weighted average)
    quality_score = (completeness_score * 0.6 + uniqueness_score * 0.4)

    return {
        "quality_score": quality_score,
        "completeness_score": completeness_score,
        "uniqueness_score": uniqueness_score,
        "missing_percentage": missing_percentage,
        "duplicate_percentage": duplicate_percentage,
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "total_cells": total_cells,
        "missing_cells": int(missing_cells),
        "duplicate_rows": int(duplicate_rows)
    }


def get_column_stats(df: pd.DataFrame, column: str) -> Dict[str, Any]:
    """Get statistics for a specific column."""
    stats = {
        "column": column,
        "dtype": str(df[column].dtype),
        "missing_count": int(df[column].isnull().sum()),
        "missing_percentage": float(df[column].isnull().sum() / len(df) * 100),
        "unique_count": int(df[column].nunique()),
        "unique_percentage": float(df[column].nunique() / len(df) * 100)
    }

    # Add numeric stats if applicable
    if pd.api.types.is_numeric_dtype(df[column]):
        stats.update({
            "mean": float(df[column].mean()) if not df[column].isnull().all() else None,
            "median": float(df[column].median()) if not df[column].isnull().all() else None,
            "std": float(df[column].std()) if not df[column].isnull().all() else None,
            "min": float(df[column].min()) if not df[column].isnull().all() else None,
            "max": float(df[column].max()) if not df[column].isnull().all() else None
        })

    return stats


def detect_pii_columns(df: pd.DataFrame) -> List[str]:
    """Detect potential PII columns based on column names and content."""
    pii_keywords = [
        'email', 'phone', 'ssn', 'social', 'passport', 'license',
        'credit', 'card', 'account', 'password', 'secret', 'token',
        'name', 'address', 'zip', 'postal', 'birth', 'dob', 'age'
    ]

    pii_columns = []
    for col in df.columns:
        col_lower = col.lower()
        if any(keyword in col_lower for keyword in pii_keywords):
            pii_columns.append(col)

    return pii_columns


def create_data_profile(df: pd.DataFrame) -> Dict[str, Any]:
    """Create comprehensive data profile."""
    profile = {
        "timestamp": datetime.now().isoformat(),
        "shape": {
            "rows": len(df),
            "columns": len(df.columns)
        },
        "quality_metrics": calculate_data_quality_score(df),
        "columns": {},
        "pii_columns": detect_pii_columns(df),
        "memory_usage_bytes": int(df.memory_usage(deep=True).sum())
    }

    # Add column-level stats
    for col in df.columns:
        profile["columns"][col] = get_column_stats(df, col)

    return profile


def generate_unique_id(prefix: str = "") -> str:
    """Generate unique ID with timestamp."""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
    return f"{prefix}_{timestamp}" if prefix else timestamp


def export_dataframe(df: pd.DataFrame, filename: str, format: str = "csv") -> Path:
    """Export DataFrame to file."""
    from .config import OUTPUT_DIR

    filepath = OUTPUT_DIR / filename

    if format.lower() == "csv":
        df.to_csv(filepath, index=False)
    elif format.lower() == "excel":
        df.to_excel(filepath, index=False)
    elif format.lower() == "json":
        df.to_json(filepath, orient='records', indent=2)
    else:
        raise ValueError(f"Unsupported format: {format}")

    return filepath


def validate_dataframe(df: pd.DataFrame, required_columns: List[str] = None) -> Dict[str, Any]:
    """Validate DataFrame structure and content."""
    validation_result = {
        "is_valid": True,
        "errors": [],
        "warnings": []
    }

    # Check if DataFrame is empty
    if df.empty:
        validation_result["is_valid"] = False
        validation_result["errors"].append("DataFrame is empty")
        return validation_result

    # Check required columns
    if required_columns:
        missing_columns = set(required_columns) - set(df.columns)
        if missing_columns:
            validation_result["is_valid"] = False
            validation_result["errors"].append(f"Missing required columns: {missing_columns}")

    # Check for excessive missing data
    quality_metrics = calculate_data_quality_score(df)
    if quality_metrics["missing_percentage"] > 50:
        validation_result["warnings"].append(
            f"High missing data percentage: {quality_metrics['missing_percentage']:.1f}%"
        )

    # Check for excessive duplicates
    if quality_metrics["duplicate_percentage"] > 20:
        validation_result["warnings"].append(
            f"High duplicate percentage: {quality_metrics['duplicate_percentage']:.1f}%"
        )

    return validation_result
