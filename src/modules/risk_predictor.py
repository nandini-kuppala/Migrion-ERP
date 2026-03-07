"""Migration Risk Predictor — ML-based risk prediction from data quality metrics."""
import numpy as np
import pandas as pd
from typing import Any, Dict, List, Tuple
from pathlib import Path
from src.utils.helpers import setup_logger

logger = setup_logger("risk_predictor")


class RiskPredictor:
    """Predict migration risk level using a trained Random Forest classifier."""

    FEATURE_NAMES = [
        "quality_score", "completeness_score", "uniqueness_score",
        "missing_percentage", "duplicate_percentage", "pii_count",
        "record_count_log", "column_count", "numeric_ratio"
    ]

    RISK_LABELS = {0: "Low", 1: "Medium", 2: "High"}

    def __init__(self, model_path: str = None):
        self.model = None
        self.model_path = model_path
        if model_path and Path(model_path).exists():
            self.load_model(model_path)

    def _generate_training_data(self, n_samples: int = 300) -> Tuple[np.ndarray, np.ndarray]:
        """Generate synthetic labeled training data for risk prediction.

        Encodes domain knowledge:
        - Low risk: high quality score, low missing/duplicate %, low PII
        - Medium risk: moderate metrics
        - High risk: low quality score, high missing/duplicate %, high PII count
        """
        np.random.seed(42)
        X = []
        y = []

        for _ in range(n_samples // 3):
            # Low risk samples
            quality_score = np.random.uniform(0.8, 1.0)
            completeness = np.random.uniform(0.85, 1.0)
            uniqueness = np.random.uniform(0.9, 1.0)
            missing_pct = np.random.uniform(0, 5)
            dup_pct = np.random.uniform(0, 3)
            pii = np.random.randint(0, 3)
            records_log = np.random.uniform(2, 6)
            cols = np.random.randint(5, 30)
            numeric_ratio = np.random.uniform(0.2, 0.8)
            X.append([quality_score, completeness, uniqueness, missing_pct,
                      dup_pct, pii, records_log, cols, numeric_ratio])
            y.append(0)

        for _ in range(n_samples // 3):
            # Medium risk samples
            quality_score = np.random.uniform(0.55, 0.82)
            completeness = np.random.uniform(0.6, 0.88)
            uniqueness = np.random.uniform(0.7, 0.92)
            missing_pct = np.random.uniform(4, 20)
            dup_pct = np.random.uniform(2, 12)
            pii = np.random.randint(2, 8)
            records_log = np.random.uniform(3, 7)
            cols = np.random.randint(10, 50)
            numeric_ratio = np.random.uniform(0.1, 0.7)
            X.append([quality_score, completeness, uniqueness, missing_pct,
                      dup_pct, pii, records_log, cols, numeric_ratio])
            y.append(1)

        for _ in range(n_samples // 3):
            # High risk samples
            quality_score = np.random.uniform(0.2, 0.58)
            completeness = np.random.uniform(0.3, 0.65)
            uniqueness = np.random.uniform(0.4, 0.72)
            missing_pct = np.random.uniform(15, 60)
            dup_pct = np.random.uniform(8, 40)
            pii = np.random.randint(5, 15)
            records_log = np.random.uniform(4, 8)
            cols = np.random.randint(15, 80)
            numeric_ratio = np.random.uniform(0.05, 0.5)
            X.append([quality_score, completeness, uniqueness, missing_pct,
                      dup_pct, pii, records_log, cols, numeric_ratio])
            y.append(2)

        return np.array(X), np.array(y)

    def train(self, X: np.ndarray = None, y: np.ndarray = None) -> Dict[str, Any]:
        """Train the risk prediction model.

        If X, y are not provided, uses synthetic training data.
        Returns training metrics.
        """
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.model_selection import cross_val_score

        if X is None or y is None:
            X, y = self._generate_training_data()

        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            class_weight="balanced"
        )

        # Cross-validation
        cv_scores = cross_val_score(self.model, X, y, cv=5, scoring="accuracy")

        # Train on full data
        self.model.fit(X, y)

        training_metrics = {
            "cv_accuracy_mean": round(float(cv_scores.mean()), 4),
            "cv_accuracy_std": round(float(cv_scores.std()), 4),
            "n_samples": len(X),
            "n_features": len(self.FEATURE_NAMES),
            "feature_importance": dict(zip(
                self.FEATURE_NAMES,
                [round(float(fi), 4) for fi in self.model.feature_importances_]
            ))
        }

        logger.info(f"Model trained. CV Accuracy: {training_metrics['cv_accuracy_mean']:.4f}")
        return training_metrics

    def predict(self, data_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Predict migration risk level from data quality metrics.

        Args:
            data_metrics: dict with keys matching quality metrics (quality_score,
                          missing_percentage, duplicate_percentage, etc.)

        Returns:
            dict with risk_level, probability, feature_contributions
        """
        if self.model is None:
            logger.info("No model loaded, training with synthetic data...")
            self.train()

        # Extract features
        features = self._extract_features(data_metrics)
        features_array = np.array([features])

        # Predict
        prediction = self.model.predict(features_array)[0]
        probabilities = self.model.predict_proba(features_array)[0]

        risk_level = self.RISK_LABELS.get(prediction, "Unknown")

        # Feature contributions (approximate using importance * deviation from mean)
        importance = self.model.feature_importances_
        contributions = []
        for i, name in enumerate(self.FEATURE_NAMES):
            contributions.append({
                "feature": name,
                "value": round(features[i], 4),
                "importance": round(float(importance[i]), 4),
            })
        contributions.sort(key=lambda x: x["importance"], reverse=True)

        return {
            "risk_level": risk_level,
            "risk_score": round(float(probabilities[prediction]) * 100, 1),
            "probabilities": {
                "Low": round(float(probabilities[0]) * 100, 1),
                "Medium": round(float(probabilities[1]) * 100, 1),
                "High": round(float(probabilities[2]) * 100, 1),
            },
            "feature_contributions": contributions,
        }

    def _extract_features(self, metrics: Dict[str, Any]) -> List[float]:
        """Extract feature vector from data quality metrics."""
        quality_score = metrics.get("quality_score", 0.5)
        completeness = metrics.get("completeness_score", 0.5)
        uniqueness = metrics.get("uniqueness_score", 0.5)
        missing_pct = metrics.get("missing_percentage", 10)
        dup_pct = metrics.get("duplicate_percentage", 5)
        pii_count = metrics.get("pii_count", 0)
        record_count = metrics.get("total_rows", 1000)
        col_count = metrics.get("total_columns", 10)
        numeric_cols = metrics.get("numeric_columns", 3)

        record_count_log = np.log10(max(record_count, 1))
        numeric_ratio = numeric_cols / max(col_count, 1)

        return [
            quality_score, completeness, uniqueness,
            missing_pct, dup_pct, pii_count,
            record_count_log, col_count, numeric_ratio
        ]

    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance ranking."""
        if self.model is None:
            return {}
        return dict(zip(
            self.FEATURE_NAMES,
            [round(float(fi), 4) for fi in self.model.feature_importances_]
        ))

    def save_model(self, path: str):
        """Save trained model to disk."""
        if self.model is not None:
            import joblib
            joblib.dump(self.model, path)
            logger.info(f"Model saved to {path}")

    def load_model(self, path: str):
        """Load trained model from disk."""
        try:
            import joblib
            self.model = joblib.load(path)
            logger.info(f"Model loaded from {path}")
        except Exception as e:
            logger.warning(f"Could not load model: {e}")
            self.model = None
