"""Tests for ML schema matcher."""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestMLSchemaMatcher:
    """Test suite for ML-based schema matching."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Check if sentence-transformers is available."""
        try:
            from src.modules.ml_schema_matcher import MLSchemaMatcher
            self.matcher = MLSchemaMatcher()
            self.available = True
        except ImportError:
            self.available = False

    def test_field_matching_basic(self, sample_source_schema, sample_target_schema):
        """Basic field matching should produce valid results."""
        if not self.available:
            pytest.skip("sentence-transformers not installed")

        result = self.matcher.match_fields(sample_source_schema, sample_target_schema)

        assert "mappings" in result, "Result should have 'mappings'"
        assert isinstance(result["mappings"], list), "Mappings should be a list"
        assert len(result["mappings"]) > 0, "Should produce at least one mapping"

    def test_confidence_scores(self, sample_source_schema, sample_target_schema):
        """Confidence scores should be between 0 and 1."""
        if not self.available:
            pytest.skip("sentence-transformers not installed")

        result = self.matcher.match_fields(sample_source_schema, sample_target_schema)

        for mapping in result["mappings"]:
            assert "confidence" in mapping, "Each mapping should have 'confidence'"
            assert 0 <= mapping["confidence"] <= 1, \
                f"Confidence should be [0, 1], got {mapping['confidence']}"

    def test_obvious_matches(self, sample_source_schema, sample_target_schema):
        """Obviously similar fields should match with high confidence."""
        if not self.available:
            pytest.skip("sentence-transformers not installed")

        result = self.matcher.match_fields(sample_source_schema, sample_target_schema)

        # Build map for easy lookup
        mapping_map = {m["source_field"]: m for m in result["mappings"]}

        # email_address should map to email
        if "email_address" in mapping_map:
            assert mapping_map["email_address"]["target_field"] == "email", \
                "email_address should map to email"
            assert mapping_map["email_address"]["confidence"] > 0.5, \
                "email match should have high confidence"

    def test_unmapped_fields_tracked(self):
        """Unmapped fields should be tracked in the result."""
        if not self.available:
            pytest.skip("sentence-transformers not installed")

        source = [{"name": "zzz_obscure_field", "type": "string"}]
        target = [{"name": "aaa_different_field", "type": "string"}]

        result = self.matcher.match_fields(source, target, threshold=0.9)

        assert "unmapped_source_fields" in result
        assert "unmapped_target_fields" in result

    def test_comparison_with_llm(self):
        """Compare ML and LLM results should produce valid comparison."""
        if not self.available:
            pytest.skip("sentence-transformers not installed")

        from src.modules.ml_schema_matcher import MLSchemaMatcher

        ml_result = {
            "mappings": [
                {"source_field": "email_address", "target_field": "email", "confidence": 0.92},
                {"source_field": "customer_name", "target_field": "name", "confidence": 0.85},
            ]
        }
        llm_result = {
            "mappings": [
                {"source_field": "email_address", "target_field": "email", "confidence": 0.95},
                {"source_field": "customer_name", "target_field": "name", "confidence": 0.90},
            ]
        }

        comparison = MLSchemaMatcher.compare_with_llm(llm_result, ml_result)

        assert "comparisons" in comparison
        assert "summary" in comparison
        assert comparison["summary"]["agreements"] == 2
        assert comparison["summary"]["agreement_rate"] == 100.0
