"""Data Profiling Benchmarks — Compare Migrion profiler against Great Expectations."""
import time
import pandas as pd
import numpy as np
from typing import Any, Dict, List
from src.utils.helpers import setup_logger, calculate_data_quality_score, detect_pii_columns
from src.modules.data_quality import DataQualityAnalyzer

logger = setup_logger("profiling_benchmarks")


class ProfilingBenchmark:
    """Benchmark Migrion's data profiler against Great Expectations."""

    def __init__(self, dataframe: pd.DataFrame, dataset_name: str = "Dataset"):
        self.df = dataframe
        self.dataset_name = dataset_name

    def run_migrion_profiler(self) -> Dict[str, Any]:
        """Run Migrion's built-in data profiler and measure performance."""
        start_time = time.time()

        analyzer = DataQualityAnalyzer(self.df, self.dataset_name)
        report = analyzer.analyze()

        elapsed = time.time() - start_time

        quality = report.get("quality_metrics", {})
        issues = report.get("data_issues", [])
        pii = report.get("pii_detection", {})

        return {
            "tool": "Migrion",
            "execution_time_seconds": round(elapsed, 4),
            "quality_score": quality.get("quality_score", 0),
            "completeness": quality.get("completeness_score", 0),
            "uniqueness": quality.get("uniqueness_score", 0),
            "missing_percentage": quality.get("missing_percentage", 0),
            "duplicate_percentage": quality.get("duplicate_percentage", 0),
            "issues_detected": len(issues),
            "pii_columns_detected": pii.get("pii_count", 0),
            "columns_profiled": len(report.get("column_analysis", [])),
        }

    def run_great_expectations(self) -> Dict[str, Any]:
        """Run Great Expectations profiler and measure performance."""
        start_time = time.time()

        results = {
            "tool": "Great Expectations",
            "execution_time_seconds": 0,
            "quality_score": 0,
            "completeness": 0,
            "uniqueness": 0,
            "missing_percentage": 0,
            "duplicate_percentage": 0,
            "issues_detected": 0,
            "pii_columns_detected": 0,
            "columns_profiled": 0,
            "expectations_evaluated": 0,
            "expectations_passed": 0,
            "expectations_failed": 0,
        }

        try:
            import great_expectations as gx
            from great_expectations.dataset import PandasDataset

            ge_df = PandasDataset(self.df)

            expectations_results = []
            issues_count = 0

            # Run common expectations per column
            for col in self.df.columns:
                # Completeness check
                result = ge_df.expect_column_values_to_not_be_null(col)
                expectations_results.append(result)
                if not result["success"]:
                    issues_count += 1

                # Unique check for ID-like columns
                if "id" in col.lower():
                    result = ge_df.expect_column_values_to_be_unique(col)
                    expectations_results.append(result)
                    if not result["success"]:
                        issues_count += 1

            elapsed = time.time() - start_time

            passed = sum(1 for r in expectations_results if r.get("success", False))
            failed = len(expectations_results) - passed

            # Calculate quality metrics from GE results
            total_cells = self.df.shape[0] * self.df.shape[1]
            missing_cells = self.df.isnull().sum().sum()
            missing_pct = (missing_cells / total_cells * 100) if total_cells > 0 else 0
            dup_count = self.df.duplicated().sum()
            dup_pct = (dup_count / len(self.df) * 100) if len(self.df) > 0 else 0

            completeness = 1 - (missing_pct / 100)
            uniqueness = 1 - (dup_pct / 100)
            quality_score = completeness * 0.6 + uniqueness * 0.4

            results.update({
                "execution_time_seconds": round(elapsed, 4),
                "quality_score": round(quality_score, 4),
                "completeness": round(completeness, 4),
                "uniqueness": round(uniqueness, 4),
                "missing_percentage": round(missing_pct, 2),
                "duplicate_percentage": round(dup_pct, 2),
                "issues_detected": issues_count,
                "columns_profiled": len(self.df.columns),
                "expectations_evaluated": len(expectations_results),
                "expectations_passed": passed,
                "expectations_failed": failed,
            })

        except ImportError:
            elapsed = time.time() - start_time
            results["error"] = "Great Expectations not installed"
            results["execution_time_seconds"] = round(elapsed, 4)
        except Exception as e:
            elapsed = time.time() - start_time
            results["error"] = str(e)
            results["execution_time_seconds"] = round(elapsed, 4)

        return results

    def compare_results(self) -> Dict[str, Any]:
        """Run both profilers and generate comparison report."""
        migrion_results = self.run_migrion_profiler()
        ge_results = self.run_great_expectations()

        # Calculate agreement on key metrics
        metrics_to_compare = [
            "quality_score", "completeness", "uniqueness",
            "missing_percentage", "duplicate_percentage"
        ]

        agreements = []
        for metric in metrics_to_compare:
            m_val = migrion_results.get(metric, 0)
            g_val = ge_results.get(metric, 0)
            diff = abs(m_val - g_val)
            agrees = diff < 0.05  # Within 5% tolerance
            agreements.append({
                "metric": metric,
                "migrion_value": round(m_val, 4),
                "great_expectations_value": round(g_val, 4),
                "difference": round(diff, 4),
                "agrees": agrees
            })

        agreement_count = sum(1 for a in agreements if a["agrees"])
        total_metrics = len(agreements)

        speed_comparison = "Migrion"
        m_time = migrion_results.get("execution_time_seconds", float('inf'))
        g_time = ge_results.get("execution_time_seconds", float('inf'))
        if g_time < m_time:
            speed_comparison = "Great Expectations"
        speedup = round(max(m_time, g_time) / max(min(m_time, g_time), 0.0001), 2)

        return {
            "dataset_name": self.dataset_name,
            "row_count": len(self.df),
            "column_count": len(self.df.columns),
            "migrion_results": migrion_results,
            "great_expectations_results": ge_results,
            "metric_comparisons": agreements,
            "summary": {
                "agreement_rate": round(agreement_count / total_metrics * 100, 1) if total_metrics > 0 else 0,
                "faster_tool": speed_comparison,
                "speedup_factor": speedup,
                "migrion_issues": migrion_results.get("issues_detected", 0),
                "ge_issues": ge_results.get("issues_detected", 0),
            }
        }
