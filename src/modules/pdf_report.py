"""PDF Report Generation Module — Generate comprehensive migration assessment PDFs."""
from datetime import datetime
from typing import Any, Dict, List, Optional
from src.utils.helpers import setup_logger

logger = setup_logger("pdf_report")


class MigrationReportGenerator:
    """Generate professional PDF migration assessment reports using fpdf2."""

    def __init__(self):
        self.pdf = None

    def _init_pdf(self):
        """Initialize FPDF object with styling."""
        from fpdf import FPDF

        class MigrionPDF(FPDF):
            def header(self):
                self.set_font("Helvetica", "B", 10)
                self.set_text_color(59, 130, 246)
                self.cell(0, 8, "Migrion — ERP Data Migration Report", align="L")
                self.set_text_color(156, 163, 175)
                self.set_font("Helvetica", "", 8)
                self.cell(0, 8, datetime.now().strftime("%Y-%m-%d %H:%M"), align="R", new_x="LMARGIN", new_y="NEXT")
                self.set_draw_color(59, 130, 246)
                self.line(10, self.get_y(), 200, self.get_y())
                self.ln(4)

            def footer(self):
                self.set_y(-15)
                self.set_font("Helvetica", "I", 8)
                self.set_text_color(156, 163, 175)
                self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

        self.pdf = MigrionPDF()
        self.pdf.alias_nb_pages()
        self.pdf.set_auto_page_break(auto=True, margin=20)

    def _add_title(self, text: str):
        self.pdf.set_font("Helvetica", "B", 18)
        self.pdf.set_text_color(30, 30, 30)
        self.pdf.cell(0, 12, text, new_x="LMARGIN", new_y="NEXT")
        self.pdf.ln(2)

    def _add_section(self, text: str):
        self.pdf.set_font("Helvetica", "B", 13)
        self.pdf.set_text_color(59, 130, 246)
        self.pdf.cell(0, 10, text, new_x="LMARGIN", new_y="NEXT")
        self.pdf.set_draw_color(59, 130, 246)
        self.pdf.line(10, self.pdf.get_y(), 100, self.pdf.get_y())
        self.pdf.ln(4)

    def _add_subsection(self, text: str):
        self.pdf.set_font("Helvetica", "B", 11)
        self.pdf.set_text_color(50, 50, 50)
        self.pdf.cell(0, 8, text, new_x="LMARGIN", new_y="NEXT")
        self.pdf.ln(2)

    def _add_text(self, text: str):
        self.pdf.set_font("Helvetica", "", 10)
        self.pdf.set_text_color(60, 60, 60)
        self.pdf.multi_cell(0, 6, text)
        self.pdf.ln(2)

    def _add_key_value(self, key: str, value: str):
        self.pdf.set_font("Helvetica", "B", 10)
        self.pdf.set_text_color(80, 80, 80)
        self.pdf.cell(60, 7, f"{key}:", align="L")
        self.pdf.set_font("Helvetica", "", 10)
        self.pdf.set_text_color(30, 30, 30)
        self.pdf.cell(0, 7, str(value), new_x="LMARGIN", new_y="NEXT")

    def _add_table(self, headers: List[str], rows: List[List[str]],
                   col_widths: List[int] = None):
        """Add a simple table to the PDF."""
        if col_widths is None:
            total_width = 190
            col_widths = [total_width // len(headers)] * len(headers)

        # Header
        self.pdf.set_font("Helvetica", "B", 9)
        self.pdf.set_fill_color(59, 130, 246)
        self.pdf.set_text_color(255, 255, 255)
        for i, header in enumerate(headers):
            self.pdf.cell(col_widths[i], 8, header, border=1, fill=True, align="C")
        self.pdf.ln()

        # Rows
        self.pdf.set_font("Helvetica", "", 9)
        self.pdf.set_text_color(60, 60, 60)
        for row_idx, row in enumerate(rows):
            if row_idx % 2 == 0:
                self.pdf.set_fill_color(245, 247, 250)
            else:
                self.pdf.set_fill_color(255, 255, 255)
            for i, cell in enumerate(row):
                self.pdf.cell(col_widths[i], 7, str(cell)[:40], border=1,
                              fill=True, align="C")
            self.pdf.ln()
        self.pdf.ln(4)

    def _add_metric_row(self, metrics: Dict[str, str]):
        """Add a row of metrics as colored boxes."""
        n = len(metrics)
        if n == 0:
            return
        box_width = min(45, 190 // n)
        start_x = self.pdf.get_x()

        for label, value in metrics.items():
            x = self.pdf.get_x()
            y = self.pdf.get_y()
            self.pdf.set_fill_color(240, 245, 255)
            self.pdf.set_draw_color(59, 130, 246)
            self.pdf.rect(x, y, box_width, 18, style="DF")
            self.pdf.set_font("Helvetica", "", 8)
            self.pdf.set_text_color(120, 120, 120)
            self.pdf.set_xy(x, y + 2)
            self.pdf.cell(box_width, 5, label, align="C")
            self.pdf.set_font("Helvetica", "B", 12)
            self.pdf.set_text_color(59, 130, 246)
            self.pdf.set_xy(x, y + 8)
            self.pdf.cell(box_width, 8, str(value), align="C")
            self.pdf.set_xy(x + box_width + 3, y)
        self.pdf.ln(24)

    def generate_full_report(
        self,
        project_data: Dict[str, Any] = None,
        quality_metrics: Dict[str, Any] = None,
        mappings: Dict[str, Any] = None,
        validation_results: Dict[str, Any] = None,
        compliance_status: Dict[str, Any] = None,
        risk_prediction: Dict[str, Any] = None,
    ) -> bytes:
        """Generate a complete multi-page PDF migration assessment report.

        Returns PDF as bytes for download.
        """
        self._init_pdf()

        # --- Cover Page ---
        self.pdf.add_page()
        self.pdf.ln(30)
        self.pdf.set_font("Helvetica", "B", 28)
        self.pdf.set_text_color(59, 130, 246)
        self.pdf.cell(0, 15, "Migration Assessment Report", align="C", new_x="LMARGIN", new_y="NEXT")
        self.pdf.ln(5)
        self.pdf.set_font("Helvetica", "", 14)
        self.pdf.set_text_color(120, 120, 120)
        company = (project_data or {}).get("company_name", "ERP Migration Project")
        self.pdf.cell(0, 10, company, align="C", new_x="LMARGIN", new_y="NEXT")
        self.pdf.ln(3)
        self.pdf.set_font("Helvetica", "", 11)
        self.pdf.cell(0, 10, f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}", align="C", new_x="LMARGIN", new_y="NEXT")
        self.pdf.cell(0, 10, "Powered by Migrion — Intelligent ERP Data Migration Platform", align="C", new_x="LMARGIN", new_y="NEXT")

        # --- Executive Summary ---
        self.pdf.add_page()
        self._add_title("Executive Summary")

        if project_data:
            self._add_key_value("Company", project_data.get("company_name", "N/A"))
            self._add_key_value("Industry", project_data.get("industry", "N/A"))
            self._add_key_value("Legacy System", project_data.get("legacy_system", "N/A"))
            self._add_key_value("Target ERP", project_data.get("target_erp", "N/A"))
            self._add_key_value("Data Volume", project_data.get("data_volume", "N/A"))
            self.pdf.ln(4)

        # Summary metrics
        summary_metrics = {}
        if quality_metrics:
            qs = quality_metrics.get("quality_score", 0)
            summary_metrics["Quality Score"] = f"{qs*100:.0f}%" if qs <= 1 else f"{qs:.0f}%"
        if validation_results:
            pr = validation_results.get("pass_rate", 0)
            summary_metrics["Validation"] = f"{pr*100:.0f}%" if pr <= 1 else f"{pr:.0f}%"
        if risk_prediction:
            summary_metrics["Risk Level"] = risk_prediction.get("risk_level", "N/A")
        if compliance_status:
            summary_metrics["Compliance"] = compliance_status.get("compliance_status", "N/A")
        if summary_metrics:
            self._add_metric_row(summary_metrics)

        # --- Data Quality Section ---
        if quality_metrics:
            self._add_section("Data Quality Analysis")
            self._add_table(
                ["Metric", "Value"],
                [
                    ["Quality Score", f"{quality_metrics.get('quality_score', 0)*100:.1f}%"],
                    ["Completeness", f"{quality_metrics.get('completeness_score', 0)*100:.1f}%"],
                    ["Uniqueness", f"{quality_metrics.get('uniqueness_score', 0)*100:.1f}%"],
                    ["Missing Data", f"{quality_metrics.get('missing_percentage', 0):.1f}%"],
                    ["Duplicates", f"{quality_metrics.get('duplicate_percentage', 0):.1f}%"],
                    ["Total Rows", str(quality_metrics.get("total_rows", 0))],
                    ["Total Columns", str(quality_metrics.get("total_columns", 0))],
                ],
                [95, 95]
            )

        # --- Schema Mapping Section ---
        if mappings:
            self._add_section("Schema Mapping Summary")
            mapping_list = mappings.get("mappings", [])
            if mapping_list:
                rows = []
                for m in mapping_list[:20]:  # Limit to 20 for space
                    conf = m.get("confidence", 0)
                    conf_str = f"{conf*100:.0f}%" if conf <= 1 else f"{conf:.0f}%"
                    rows.append([
                        m.get("source_field", ""),
                        m.get("target_field", ""),
                        conf_str,
                    ])
                self._add_table(
                    ["Source Field", "Target Field", "Confidence"],
                    rows,
                    [70, 70, 50]
                )
            unmapped = mappings.get("unmapped_source_fields", [])
            if unmapped:
                self._add_text(f"Unmapped source fields: {', '.join(unmapped[:10])}")

        # --- Validation Section ---
        if validation_results:
            self._add_section("Validation Results")
            self._add_metric_row({
                "Total Checks": str(validation_results.get("total_checks", 0)),
                "Passed": str(validation_results.get("passed_checks", 0)),
                "Failed": str(validation_results.get("failed_checks", 0)),
                "Pass Rate": f"{validation_results.get('pass_rate', 0)*100:.1f}%"
            })

        # --- Risk Assessment Section ---
        if risk_prediction:
            self._add_section("Risk Assessment")
            self._add_key_value("Risk Level", risk_prediction.get("risk_level", "N/A"))
            self._add_key_value("Risk Score", f"{risk_prediction.get('risk_score', 0):.1f}%")
            self.pdf.ln(2)

            probs = risk_prediction.get("probabilities", {})
            if probs:
                self._add_table(
                    ["Risk Level", "Probability"],
                    [[level, f"{prob:.1f}%"] for level, prob in probs.items()],
                    [95, 95]
                )

            contribs = risk_prediction.get("feature_contributions", [])
            if contribs:
                self._add_subsection("Top Risk Factors")
                rows = [[c["feature"], str(c["value"]), str(c["importance"])] for c in contribs[:6]]
                self._add_table(["Feature", "Value", "Importance"], rows, [70, 60, 60])

        # --- Compliance Section ---
        if compliance_status:
            self._add_section("Compliance Status")
            self._add_key_value("Status", compliance_status.get("compliance_status", "N/A"))
            self._add_key_value("Approval", compliance_status.get("approval_status", "N/A"))

            findings = compliance_status.get("findings", [])
            if findings:
                self._add_subsection("Findings")
                rows = [
                    [f.get("category", ""), f.get("severity", ""), f.get("description", "")[:50]]
                    for f in findings[:10]
                ]
                self._add_table(["Category", "Severity", "Description"], rows, [50, 40, 100])

        # --- Generate PDF bytes ---
        return bytes(self.pdf.output())
