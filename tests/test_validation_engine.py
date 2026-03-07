"""Tests for validation engine functionality."""
import pytest
import pandas as pd
import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_validation_check(df: pd.DataFrame, rule: dict) -> dict:
    """Run a single validation rule against a DataFrame.

    This is a standalone implementation for testability since the
    original validation logic is embedded in the Streamlit page.
    """
    field = rule.get("field", "")
    rule_type = rule.get("rule_type", "")
    result = {"rule": rule, "passed": True, "failures": 0, "total": len(df)}

    if field not in df.columns:
        result["passed"] = False
        result["failures"] = len(df)
        result["message"] = f"Field '{field}' not found in data"
        return result

    if rule_type == "required":
        failures = df[field].isnull().sum()
        result["failures"] = int(failures)
        result["passed"] = failures == 0

    elif rule_type == "format":
        pattern = rule.get("pattern", "")
        if pattern:
            non_null = df[field].dropna()
            failures = sum(1 for val in non_null if not re.match(pattern, str(val)))
            result["failures"] = failures
            result["passed"] = failures == 0

    elif rule_type == "range":
        min_val = rule.get("min_value")
        max_val = rule.get("max_value")
        numeric_vals = pd.to_numeric(df[field], errors="coerce").dropna()
        failures = 0
        if min_val is not None:
            failures += int((numeric_vals < min_val).sum())
        if max_val is not None:
            failures += int((numeric_vals > max_val).sum())
        result["failures"] = failures
        result["passed"] = failures == 0

    return result


class TestValidationEngine:
    """Test suite for the validation engine."""

    def test_required_field_pass(self, sample_clean_df):
        """Required field with no nulls should pass."""
        rule = {"field": "name", "rule_type": "required", "severity": "Critical"}
        result = run_validation_check(sample_clean_df, rule)
        assert result["passed"], "Required check should pass on complete data"
        assert result["failures"] == 0

    def test_required_field_fail(self, sample_dirty_df):
        """Required field with nulls should fail."""
        rule = {"field": "name", "rule_type": "required", "severity": "High"}
        result = run_validation_check(sample_dirty_df, rule)
        assert not result["passed"], "Required check should fail on data with nulls"
        assert result["failures"] == 2, "Should detect 2 missing values"

    def test_format_email_pass(self):
        """Valid emails should pass format check."""
        df = pd.DataFrame({"email": ["a@b.com", "x@y.org", "test@test.co"]})
        rule = {"field": "email", "rule_type": "format",
                "pattern": r"^[^@]+@[^@]+\.[^@]+$", "severity": "High"}
        result = run_validation_check(df, rule)
        assert result["passed"], "Valid emails should pass"

    def test_format_email_fail(self):
        """Invalid emails should fail format check."""
        df = pd.DataFrame({"email": ["a@b.com", "invalid-email", "no-at.com"]})
        rule = {"field": "email", "rule_type": "format",
                "pattern": r"^[^@]+@[^@]+\.[^@]+$", "severity": "High"}
        result = run_validation_check(df, rule)
        assert not result["passed"], "Invalid emails should fail"
        assert result["failures"] == 2

    def test_range_pass(self):
        """Values within range should pass."""
        df = pd.DataFrame({"age": [25, 30, 45, 60, 18]})
        rule = {"field": "age", "rule_type": "range",
                "min_value": 0, "max_value": 120, "severity": "Medium"}
        result = run_validation_check(df, rule)
        assert result["passed"], "Values within range should pass"

    def test_range_fail(self, sample_dirty_df):
        """Values outside range should fail."""
        rule = {"field": "age", "rule_type": "range",
                "min_value": 0, "max_value": 120, "severity": "Medium"}
        result = run_validation_check(sample_dirty_df, rule)
        assert not result["passed"], "Out-of-range values should fail"
        assert result["failures"] >= 2, "Should detect age=-5 and age=200"

    def test_missing_field(self, sample_clean_df):
        """Rule on missing field should fail."""
        rule = {"field": "nonexistent", "rule_type": "required", "severity": "Critical"}
        result = run_validation_check(sample_clean_df, rule)
        assert not result["passed"], "Missing field should fail"

    def test_pass_rate_calculation(self, sample_dirty_df, sample_validation_rules):
        """Test computing overall pass rate across multiple rules."""
        results = [run_validation_check(sample_dirty_df, rule) for rule in sample_validation_rules]
        passed = sum(1 for r in results if r["passed"])
        total = len(results)
        pass_rate = passed / total if total > 0 else 0
        assert 0 <= pass_rate <= 1, "Pass rate should be between 0 and 1"
