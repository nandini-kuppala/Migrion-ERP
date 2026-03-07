"""Tests for data quality scoring functionality."""
import pytest
import pandas as pd
import numpy as np
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.utils.helpers import calculate_data_quality_score


def _get_score(df):
    """Helper to extract quality_score float from the dict returned by calculate_data_quality_score."""
    result = calculate_data_quality_score(df)
    return result["quality_score"]


class TestDataQualityScore:
    """Test suite for calculate_data_quality_score()."""

    def test_perfect_data(self, sample_clean_df):
        """Clean data should have quality score close to 1.0."""
        score = _get_score(sample_clean_df)
        assert score >= 0.9, f"Clean data should score >= 0.9, got {score}"

    def test_dirty_data_lower_score(self, sample_dirty_df):
        """Dirty data should have a lower quality score."""
        clean_score = _get_score(
            pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
        )
        dirty_score = _get_score(sample_dirty_df)
        assert dirty_score < clean_score, "Dirty data should score lower than clean data"

    def test_empty_dataframe(self, empty_df):
        """Empty DataFrame should return 0 or handle gracefully."""
        result = calculate_data_quality_score(empty_df)
        score = result["quality_score"]
        assert isinstance(score, (int, float)), "Should return a numeric value"

    def test_all_null_dataframe(self, all_null_df):
        """All-null DataFrame should have very low quality score."""
        score = _get_score(all_null_df)
        assert score < 0.5, f"All-null data should score < 0.5, got {score}"

    def test_score_range(self, sample_clean_df):
        """Quality score should be between 0 and 1."""
        score = _get_score(sample_clean_df)
        assert 0 <= score <= 1, f"Score should be between 0 and 1, got {score}"

    def test_more_missing_lowers_score(self):
        """More missing values should result in a lower score."""
        score_few = _get_score(pd.DataFrame({
            "a": [1, 2, 3, None, 5], "b": ["x", "y", "z", "w", "v"],
        }))
        score_many = _get_score(pd.DataFrame({
            "a": [1, None, None, None, 5], "b": [None, None, "z", None, None],
        }))
        assert score_many <= score_few, "More missing values should not increase score"

    def test_duplicates_lower_score(self):
        """Duplicate rows should reduce the quality score."""
        score_no_dup = _get_score(pd.DataFrame({"a": [1, 2, 3, 4, 5], "b": ["a", "b", "c", "d", "e"]}))
        score_all_dup = _get_score(pd.DataFrame({"a": [1, 1, 1, 1, 1], "b": ["a", "a", "a", "a", "a"]}))
        assert score_all_dup <= score_no_dup, "All duplicates should not score higher"

    def test_returns_complete_dict(self, sample_clean_df):
        """Result should contain all expected keys."""
        result = calculate_data_quality_score(sample_clean_df)
        expected_keys = [
            "quality_score", "completeness_score", "uniqueness_score",
            "missing_percentage", "duplicate_percentage",
            "total_rows", "total_columns"
        ]
        for key in expected_keys:
            assert key in result, f"Missing key '{key}' in result"
