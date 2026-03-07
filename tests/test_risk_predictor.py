"""Tests for migration risk predictor."""
import pytest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.modules.risk_predictor import RiskPredictor


class TestRiskPredictor:
    """Test suite for the ML risk predictor."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Initialize and train predictor."""
        self.predictor = RiskPredictor()
        self.training_metrics = self.predictor.train()

    def test_training_produces_metrics(self):
        """Training should return performance metrics."""
        assert "cv_accuracy_mean" in self.training_metrics
        assert "n_samples" in self.training_metrics
        assert "feature_importance" in self.training_metrics

    def test_training_accuracy(self):
        """Cross-validation accuracy should be reasonable (>70%)."""
        assert self.training_metrics["cv_accuracy_mean"] > 0.70, \
            f"CV accuracy should be > 0.70, got {self.training_metrics['cv_accuracy_mean']}"

    def test_low_risk_prediction(self):
        """High quality data should predict Low risk."""
        prediction = self.predictor.predict({
            "quality_score": 0.95,
            "completeness_score": 0.98,
            "uniqueness_score": 0.99,
            "missing_percentage": 1.0,
            "duplicate_percentage": 0.5,
            "pii_count": 1,
            "total_rows": 5000,
            "total_columns": 10,
            "numeric_columns": 4,
        })
        assert prediction["risk_level"] == "Low", \
            f"High quality data should predict Low risk, got {prediction['risk_level']}"

    def test_high_risk_prediction(self):
        """Low quality data should predict High risk."""
        prediction = self.predictor.predict({
            "quality_score": 0.25,
            "completeness_score": 0.35,
            "uniqueness_score": 0.45,
            "missing_percentage": 50,
            "duplicate_percentage": 30,
            "pii_count": 12,
            "total_rows": 100000,
            "total_columns": 60,
            "numeric_columns": 5,
        })
        assert prediction["risk_level"] == "High", \
            f"Low quality data should predict High risk, got {prediction['risk_level']}"

    def test_prediction_has_probabilities(self):
        """Prediction should include probabilities for all risk levels."""
        prediction = self.predictor.predict({
            "quality_score": 0.7,
            "completeness_score": 0.75,
            "uniqueness_score": 0.8,
            "missing_percentage": 10,
            "duplicate_percentage": 5,
            "pii_count": 3,
            "total_rows": 10000,
            "total_columns": 20,
            "numeric_columns": 7,
        })
        assert "probabilities" in prediction
        assert "Low" in prediction["probabilities"]
        assert "Medium" in prediction["probabilities"]
        assert "High" in prediction["probabilities"]
        total_prob = sum(prediction["probabilities"].values())
        assert abs(total_prob - 100.0) < 1.0, f"Probabilities should sum to ~100, got {total_prob}"

    def test_feature_importance(self):
        """Feature importance should be available after training."""
        importance = self.predictor.get_feature_importance()
        assert isinstance(importance, dict), "Should return a dict"
        assert len(importance) > 0, "Should have features"
        for name, value in importance.items():
            assert 0 <= value <= 1, f"Importance should be [0,1], got {value} for {name}"

    def test_prediction_has_contributions(self):
        """Prediction should include feature contributions."""
        prediction = self.predictor.predict({
            "quality_score": 0.5,
            "completeness_score": 0.6,
            "uniqueness_score": 0.7,
            "missing_percentage": 20,
            "duplicate_percentage": 10,
            "pii_count": 5,
            "total_rows": 50000,
            "total_columns": 30,
            "numeric_columns": 10,
        })
        assert "feature_contributions" in prediction
        assert len(prediction["feature_contributions"]) > 0
        for contrib in prediction["feature_contributions"]:
            assert "feature" in contrib
            assert "value" in contrib
            assert "importance" in contrib
