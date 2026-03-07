"""Tests for schema generation utilities."""
import pytest
import pandas as pd
import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def generate_schema_from_df(df: pd.DataFrame, schema_name: str = "Test") -> list:
    """Standalone schema generator for testing (mirrors schema_mapping.py logic)."""
    fields = []
    for col in df.columns:
        dtype = str(df[col].dtype)
        if 'int' in dtype:
            field_type = 'integer'
        elif 'float' in dtype:
            field_type = 'float'
        elif 'datetime' in dtype:
            field_type = 'datetime'
        elif 'bool' in dtype:
            field_type = 'boolean'
        else:
            field_type = 'string'
        fields.append({
            "name": col,
            "type": field_type,
            "nullable": bool(df[col].isnull().any()),
        })
    return fields


class TestSchemaGeneration:
    """Test suite for generate_schema_from_df()."""

    def test_basic_schema(self, sample_clean_df):
        """Should generate schema with correct field names."""
        schema = generate_schema_from_df(sample_clean_df)
        assert isinstance(schema, list), "Schema should be a list"
        field_names = [f["name"] for f in schema]
        for col in sample_clean_df.columns:
            assert col in field_names, f"Column '{col}' should be in schema"

    def test_numeric_types(self):
        """Should correctly identify numeric types."""
        df = pd.DataFrame({
            "int_col": [1, 2, 3],
            "float_col": [1.1, 2.2, 3.3],
        })
        schema = generate_schema_from_df(df)
        schema_dict = {f["name"]: f for f in schema}
        assert schema_dict["int_col"]["type"] == "integer"
        assert schema_dict["float_col"]["type"] == "float"

    def test_string_types(self):
        """Should correctly identify string/object types."""
        df = pd.DataFrame({
            "text_col": ["hello", "world", "test"],
        })
        schema = generate_schema_from_df(df)
        schema_dict = {f["name"]: f for f in schema}
        assert schema_dict["text_col"]["type"] == "string"

    def test_empty_dataframe(self, empty_df):
        """Should handle empty DataFrames gracefully."""
        schema = generate_schema_from_df(empty_df)
        assert isinstance(schema, list), "Should return a list even for empty DF"
        assert len(schema) == 0, "Empty DF should produce empty schema"

    def test_schema_field_structure(self, sample_clean_df):
        """Each schema field should have at least 'name' and 'type'."""
        schema = generate_schema_from_df(sample_clean_df)
        for field in schema:
            assert "name" in field, "Each field should have a 'name'"
            assert "type" in field, "Each field should have a 'type'"

    def test_mixed_types(self):
        """Should handle mixed data types."""
        df = pd.DataFrame({
            "id": [1, 2, 3],
            "name": ["Alice", "Bob", "Charlie"],
            "score": [85.5, 90.0, 78.1],
            "active": [True, False, True],
        })
        schema = generate_schema_from_df(df)
        assert len(schema) == 4, "Should have 4 fields"

    def test_nullable_detection(self):
        """Should detect nullable columns."""
        df = pd.DataFrame({
            "complete": [1, 2, 3],
            "has_null": [1, None, 3],
        })
        schema = generate_schema_from_df(df)
        schema_dict = {f["name"]: f for f in schema}
        assert not schema_dict["complete"]["nullable"], "Complete column should not be nullable"
        assert schema_dict["has_null"]["nullable"], "Column with nulls should be nullable"
