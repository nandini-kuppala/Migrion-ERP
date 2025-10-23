"""Data Quality Analyzer module."""
import pandas as pd
import numpy as np
from typing import Dict, Any, List
import plotly.graph_objects as go
import plotly.express as px
from src.utils.helpers import calculate_data_quality_score, get_column_stats, detect_pii_columns


class DataQualityAnalyzer:
    """Analyze data quality and generate reports."""

    def __init__(self, dataframe: pd.DataFrame, dataset_name: str = "Dataset"):
        self.df = dataframe
        self.dataset_name = dataset_name
        self.quality_report = None

    def analyze(self) -> Dict[str, Any]:
        """Perform comprehensive quality analysis."""
        self.quality_report = {
            "dataset_name": self.dataset_name,
            "overview": self._get_overview(),
            "quality_metrics": calculate_data_quality_score(self.df),
            "column_analysis": self._analyze_columns(),
            "pii_detection": self._detect_pii(),
            "data_issues": self._detect_issues(),
            "recommendations": self._generate_recommendations()
        }
        return self.quality_report

    def _get_overview(self) -> Dict[str, Any]:
        """Get dataset overview."""
        return {
            "total_rows": len(self.df),
            "total_columns": len(self.df.columns),
            "memory_usage_mb": self.df.memory_usage(deep=True).sum() / (1024 * 1024),
            "numeric_columns": len(self.df.select_dtypes(include=[np.number]).columns),
            "categorical_columns": len(self.df.select_dtypes(include=['object']).columns),
            "datetime_columns": len(self.df.select_dtypes(include=['datetime64']).columns)
        }

    def _analyze_columns(self) -> List[Dict[str, Any]]:
        """Analyze each column."""
        column_analysis = []
        for col in self.df.columns:
            stats = get_column_stats(self.df, col)
            column_analysis.append(stats)
        return column_analysis

    def _detect_pii(self) -> Dict[str, Any]:
        """Detect PII columns."""
        pii_columns = detect_pii_columns(self.df)
        return {
            "has_pii": len(pii_columns) > 0,
            "pii_columns": pii_columns,
            "pii_count": len(pii_columns)
        }

    def _detect_issues(self) -> List[Dict[str, Any]]:
        """Detect data quality issues."""
        issues = []

        # Check for high missing data
        for col in self.df.columns:
            missing_pct = (self.df[col].isnull().sum() / len(self.df)) * 100
            if missing_pct > 20:
                issues.append({
                    "type": "high_missing_data",
                    "severity": "high" if missing_pct > 50 else "medium",
                    "column": col,
                    "description": f"{col} has {missing_pct:.1f}% missing values",
                    "affected_rows": int(self.df[col].isnull().sum())
                })

        # Check for duplicates
        dup_count = self.df.duplicated().sum()
        if dup_count > 0:
            dup_pct = (dup_count / len(self.df)) * 100
            issues.append({
                "type": "duplicate_rows",
                "severity": "high" if dup_pct > 10 else "medium" if dup_pct > 5 else "low",
                "column": "all",
                "description": f"Found {dup_count} duplicate rows ({dup_pct:.1f}%)",
                "affected_rows": int(dup_count)
            })

        # Check for low cardinality in what might be ID fields
        for col in self.df.columns:
            if 'id' in col.lower() and self.df[col].nunique() < len(self.df) * 0.9:
                issues.append({
                    "type": "low_cardinality_id",
                    "severity": "medium",
                    "column": col,
                    "description": f"{col} appears to be an ID but has low uniqueness",
                    "affected_rows": len(self.df) - self.df[col].nunique()
                })

        return issues

    def _generate_recommendations(self) -> List[Dict[str, Any]]:
        """Generate recommendations based on analysis."""
        recommendations = []

        quality_metrics = calculate_data_quality_score(self.df)

        if quality_metrics["missing_percentage"] > 10:
            recommendations.append({
                "category": "Data Completeness",
                "priority": "High",
                "recommendation": "Address missing data before migration",
                "action": "Review columns with high missing percentages and decide on imputation strategy or removal"
            })

        if quality_metrics["duplicate_percentage"] > 5:
            recommendations.append({
                "category": "Data Uniqueness",
                "priority": "High",
                "recommendation": "Remove or merge duplicate records",
                "action": "Investigate duplicate rows and establish deduplication rules"
            })

        pii_cols = detect_pii_columns(self.df)
        if pii_cols:
            recommendations.append({
                "category": "Data Privacy",
                "priority": "Critical",
                "recommendation": "Implement PII protection measures",
                "action": f"Apply encryption/masking to PII fields: {', '.join(pii_cols)}"
            })

        if quality_metrics["quality_score"] < 0.7:
            recommendations.append({
                "category": "Overall Quality",
                "priority": "High",
                "recommendation": "Improve overall data quality before migration",
                "action": "Address identified issues to reach minimum quality threshold of 70%"
            })

        return recommendations

    def create_quality_dashboard_plots(self) -> Dict[str, go.Figure]:
        """Create visualization plots for quality dashboard."""
        plots = {}

        # Missing data heatmap
        missing_data = self.df.isnull().sum()
        if missing_data.sum() > 0:
            fig_missing = go.Figure(data=[
                go.Bar(
                    x=missing_data[missing_data > 0].index,
                    y=missing_data[missing_data > 0].values,
                    marker_color='#EF4444'
                )
            ])
            fig_missing.update_layout(
                title="Missing Values by Column",
                xaxis_title="Column",
                yaxis_title="Missing Count",
                template="plotly_dark"
            )
            plots["missing_data"] = fig_missing

        # Data types distribution
        dtype_counts = self.df.dtypes.value_counts()
        fig_dtypes = go.Figure(data=[
            go.Pie(
                labels=[str(dt) for dt in dtype_counts.index],
                values=dtype_counts.values,
                hole=0.4
            )
        ])
        fig_dtypes.update_layout(
            title="Data Types Distribution",
            template="plotly_dark"
        )
        plots["data_types"] = fig_dtypes

        # Quality score gauge
        quality_score = calculate_data_quality_score(self.df)["quality_score"]
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=quality_score * 100,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Overall Quality Score"},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "#3B82F6"},
                'steps': [
                    {'range': [0, 50], 'color': "#EF4444"},
                    {'range': [50, 75], 'color': "#F59E0B"},
                    {'range': [75, 100], 'color': "#10B981"}
                ],
                'threshold': {
                    'line': {'color': "white", 'width': 4},
                    'thickness': 0.75,
                    'value': 70
                }
            }
        ))
        fig_gauge.update_layout(template="plotly_dark")
        plots["quality_gauge"] = fig_gauge

        return plots
