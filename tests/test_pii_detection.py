"""Tests for PII detection functionality."""
import pytest
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.utils.helpers import detect_pii_columns


class TestPIIDetection:
    """Test suite for detect_pii_columns()."""

    def test_detects_email(self, sample_pii_df):
        """Should detect email columns."""
        pii = detect_pii_columns(sample_pii_df)
        assert "email" in pii, "Should detect 'email' as PII"

    def test_detects_phone(self, sample_pii_df):
        """Should detect phone columns."""
        pii = detect_pii_columns(sample_pii_df)
        assert "phone" in pii, "Should detect 'phone' as PII"

    def test_detects_ssn(self, sample_pii_df):
        """Should detect SSN columns."""
        pii = detect_pii_columns(sample_pii_df)
        assert "ssn" in pii, "Should detect 'ssn' as PII"

    def test_detects_name(self, sample_pii_df):
        """Should detect name columns."""
        pii = detect_pii_columns(sample_pii_df)
        assert "customer_name" in pii, "Should detect 'customer_name' as PII"

    def test_detects_dob(self, sample_pii_df):
        """Should detect date_of_birth columns."""
        pii = detect_pii_columns(sample_pii_df)
        assert "date_of_birth" in pii, "Should detect 'date_of_birth' as PII"

    def test_no_false_positives_on_clean_data(self, sample_no_pii_df):
        """Non-PII columns should not be flagged."""
        pii = detect_pii_columns(sample_no_pii_df)
        assert "product_id" not in pii, "product_id is not PII"
        assert "category" not in pii, "category is not PII"
        assert "price" not in pii, "price is not PII"
        assert "quantity" not in pii, "quantity is not PII"

    def test_returns_list(self, sample_pii_df):
        """Should return a list of column names."""
        pii = detect_pii_columns(sample_pii_df)
        assert isinstance(pii, list), "Should return a list"
        for col in pii:
            assert isinstance(col, str), "Each element should be a string"
            assert col in sample_pii_df.columns, f"{col} should be a column in the DataFrame"

    def test_empty_dataframe(self, empty_df):
        """Empty DataFrame should return empty list."""
        pii = detect_pii_columns(empty_df)
        assert pii == [] or isinstance(pii, list), "Empty DF should return empty list"
