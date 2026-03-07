"""Shared test fixtures for Migrion test suite."""
import pytest
import pandas as pd
import numpy as np


@pytest.fixture
def sample_clean_df():
    """A clean DataFrame with no issues."""
    return pd.DataFrame({
        "id": [1, 2, 3, 4, 5],
        "name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
        "age": [25, 30, 35, 40, 45],
        "score": [85.5, 90.2, 78.1, 92.3, 88.7],
    })


@pytest.fixture
def sample_dirty_df():
    """A DataFrame with intentional quality issues."""
    return pd.DataFrame({
        "id": [1, 2, 2, 4, 5],  # duplicate ID
        "name": ["Alice", None, "Charlie", "Diana", None],  # 2 missing
        "email": ["alice@test.com", None, "charlie@test.com", None, "eve@test.com"],  # 2 missing
        "phone": ["+1-555-0100", "+1-555-0101", None, "+1-555-0103", None],  # 2 missing
        "age": [25, 30, -5, 40, 200],  # invalid ages
        "score": [85.5, 90.2, 78.1, np.nan, 88.7],  # 1 missing
    })


@pytest.fixture
def sample_pii_df():
    """A DataFrame with PII columns."""
    return pd.DataFrame({
        "customer_id": ["C001", "C002", "C003"],
        "customer_name": ["John Doe", "Jane Smith", "Bob Johnson"],
        "email": ["john@example.com", "jane@example.com", "bob@example.com"],
        "phone": ["+1-555-0100", "+1-555-0101", "+1-555-0102"],
        "ssn": ["123-45-6789", "987-65-4321", "456-78-9012"],
        "date_of_birth": ["1990-01-15", "1985-06-20", "1978-11-30"],
        "address": ["123 Main St", "456 Oak Ave", "789 Pine Rd"],
        "total_orders": [15, 8, 22],
        "revenue": [5000.0, 3200.0, 12000.0],
    })


@pytest.fixture
def sample_no_pii_df():
    """A DataFrame without PII columns."""
    return pd.DataFrame({
        "product_id": ["P001", "P002", "P003"],
        "category": ["Electronics", "Clothing", "Food"],
        "price": [99.99, 29.99, 5.49],
        "quantity": [100, 250, 500],
    })


@pytest.fixture
def sample_source_schema():
    """Source schema for mapping tests."""
    return [
        {"name": "customer_id", "type": "integer"},
        {"name": "customer_name", "type": "string"},
        {"name": "email_address", "type": "string"},
        {"name": "phone_number", "type": "string"},
        {"name": "registration_date", "type": "date"},
        {"name": "total_purchases", "type": "integer"},
        {"name": "account_status", "type": "string"},
    ]


@pytest.fixture
def sample_target_schema():
    """Target schema for mapping tests."""
    return [
        {"name": "id", "type": "integer"},
        {"name": "name", "type": "string"},
        {"name": "email", "type": "string"},
        {"name": "phone", "type": "string"},
        {"name": "date_registered", "type": "datetime"},
        {"name": "purchase_count", "type": "integer"},
        {"name": "status", "type": "string"},
    ]


@pytest.fixture
def sample_validation_rules():
    """Sample validation rules for testing."""
    return [
        {"field": "email", "rule_type": "required", "severity": "Critical"},
        {"field": "email", "rule_type": "format", "pattern": r"^[^@]+@[^@]+\.[^@]+$", "severity": "High"},
        {"field": "age", "rule_type": "range", "min_value": 0, "max_value": 120, "severity": "Medium"},
        {"field": "name", "rule_type": "required", "severity": "High"},
    ]


@pytest.fixture
def empty_df():
    """An empty DataFrame."""
    return pd.DataFrame()


@pytest.fixture
def all_null_df():
    """A DataFrame with all null values."""
    return pd.DataFrame({
        "a": [None, None, None],
        "b": [np.nan, np.nan, np.nan],
        "c": [None, np.nan, None],
    })
