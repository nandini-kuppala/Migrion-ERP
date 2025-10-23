"""Data Quality Analysis Page - Display quality metrics and visualizations."""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from src.utils.styling import apply_custom_css, create_header, create_status_badge, create_metric_card
from src.utils.helpers import (
    init_session_state,
    get_session_state,
    set_session_state,
    format_percentage,
    format_number
)
from src.modules.data_quality import DataQualityAnalyzer
from src.agents.gemini_agent import QualityAgent


def render():
    """Render data quality analysis page."""
    apply_custom_css()

    st.markdown(create_header(
        "Data Quality Analysis",
        "Analyze your data quality and identify issues before migration"
    ), unsafe_allow_html=True)

    # Initialize session state
    init_session_state("quality_report", None)
    init_session_state("ai_insights", None)

    # File uploader
    st.markdown("### Upload Data for Analysis")

    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=['csv'],
        help="Upload your dataset for quality analysis"
    )

    # Sample data option
    col1, col2 = st.columns([3, 1])
    with col2:
        use_sample = st.button("Use Sample Data", use_container_width=True)

    if use_sample:
        # Load sample data
        try:
            from src.utils.config import OLIST_DATA_DIR
            sample_file = OLIST_DATA_DIR / "olist_orders_dataset.csv"
            if sample_file.exists():
                df = pd.read_csv(sample_file)
                set_session_state("uploaded_data", df)
                st.success("Sample data loaded successfully!")
            else:
                st.error("Sample data file not found")
        except Exception as e:
            st.error(f"Error loading sample data: {str(e)}")

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            set_session_state("uploaded_data", df)
            st.success(f"File uploaded successfully! ({len(df)} rows, {len(df.columns)} columns)")
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")

    # Check if data is available
    df = get_session_state("uploaded_data")

    if df is not None:
        # Data preview
        st.markdown("### Data Preview")
        with st.expander("View first 10 rows", expanded=False):
            st.dataframe(df.head(10), use_container_width=True)

        # Analyze button
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            analyze_button = st.button("Analyze Quality", type="primary", use_container_width=True)

        if analyze_button:
            with st.spinner("Analyzing data quality..."):
                try:
                    # Perform quality analysis
                    analyzer = DataQualityAnalyzer(df, dataset_name=uploaded_file.name if uploaded_file else "Sample Data")
                    quality_report = analyzer.analyze()
                    set_session_state("quality_report", quality_report)

                    # Generate plots
                    plots = analyzer.create_quality_dashboard_plots()
                    set_session_state("quality_plots", plots)

                    # Get AI insights
                    with st.spinner("Generating AI insights..."):
                        quality_agent = QualityAgent()
                        ai_insights = quality_agent.analyze_quality_report(quality_report["quality_metrics"])
                        set_session_state("ai_insights", ai_insights)

                    st.success("Analysis complete!")

                except Exception as e:
                    st.error(f"Error during analysis: {str(e)}")

        # Display results if available
        quality_report = get_session_state("quality_report")
        ai_insights = get_session_state("ai_insights")

        if quality_report:
            display_quality_results(quality_report, ai_insights)

    else:
        st.info("Please upload a CSV file or use sample data to begin analysis")


def display_quality_results(quality_report: dict, ai_insights: dict = None):
    """Display quality analysis results."""
    st.markdown("---")
    st.markdown("## Quality Analysis Results")

    # AI Insights Section (if available)
    if ai_insights and "error" not in ai_insights:
        st.markdown("### AI Insights")

        # Overall assessment
        assessment = ai_insights.get("overall_assessment", "Unknown")
        data_readiness = ai_insights.get("data_readiness", "Unknown")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Overall Assessment:** {create_status_badge(assessment.lower())}", unsafe_allow_html=True)
        with col2:
            readiness_status = "success" if "Ready" in data_readiness else "warning" if "Needs Work" in data_readiness else "error"
            st.markdown(f"**Data Readiness:** {create_status_badge(readiness_status)}", unsafe_allow_html=True)

        # Key findings
        if ai_insights.get("key_findings"):
            st.markdown("**Key Findings:**")
            for finding in ai_insights["key_findings"]:
                st.info(finding)

        # Critical issues
        if ai_insights.get("critical_issues"):
            st.markdown("**Critical Issues:**")
            for issue in ai_insights["critical_issues"]:
                st.error(issue)

    # Quality Score Metrics
    st.markdown("### Quality Metrics")

    metrics = quality_report.get("quality_metrics", {})

    # Create metric cards
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        quality_score = metrics.get("quality_score", 0) * 100
        st.markdown(create_metric_card(
            "Overall Quality",
            f"{quality_score:.1f}%",
            delta="Target: 70%" if quality_score >= 70 else "Below Target",
            delta_color="normal" if quality_score >= 70 else "inverse"
        ), unsafe_allow_html=True)

    with col2:
        completeness = metrics.get("completeness_score", 0) * 100
        st.markdown(create_metric_card(
            "Completeness",
            f"{completeness:.1f}%"
        ), unsafe_allow_html=True)

    with col3:
        uniqueness = metrics.get("uniqueness_score", 0) * 100
        st.markdown(create_metric_card(
            "Uniqueness",
            f"{uniqueness:.1f}%"
        ), unsafe_allow_html=True)

    with col4:
        total_rows = metrics.get("total_rows", 0)
        st.markdown(create_metric_card(
            "Total Records",
            format_number(total_rows, 0)
        ), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col5, col6, col7, col8 = st.columns(4)

    with col5:
        missing_pct = metrics.get("missing_percentage", 0)
        st.metric("Missing Data", format_percentage(missing_pct))

    with col6:
        duplicate_pct = metrics.get("duplicate_percentage", 0)
        st.metric("Duplicate Rows", format_percentage(duplicate_pct))

    with col7:
        total_cols = metrics.get("total_columns", 0)
        st.metric("Total Columns", total_cols)

    with col8:
        missing_cells = metrics.get("missing_cells", 0)
        st.metric("Missing Cells", format_number(missing_cells, 0))

    # Visualizations
    st.markdown("### Quality Visualizations")

    plots = get_session_state("quality_plots")

    if plots:
        col1, col2 = st.columns(2)

        with col1:
            if "quality_gauge" in plots:
                st.plotly_chart(plots["quality_gauge"], use_container_width=True)

            if "missing_data" in plots:
                st.plotly_chart(plots["missing_data"], use_container_width=True)

        with col2:
            if "data_types" in plots:
                st.plotly_chart(plots["data_types"], use_container_width=True)

    # Data Overview
    st.markdown("### Dataset Overview")

    overview = quality_report.get("overview", {})

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Data Dimensions:**")
        st.write(f"- Total Rows: {overview.get('total_rows', 0):,}")
        st.write(f"- Total Columns: {overview.get('total_columns', 0)}")
        st.write(f"- Memory Usage: {overview.get('memory_usage_mb', 0):.2f} MB")

    with col2:
        st.markdown("**Column Types:**")
        st.write(f"- Numeric: {overview.get('numeric_columns', 0)}")
        st.write(f"- Categorical: {overview.get('categorical_columns', 0)}")
        st.write(f"- DateTime: {overview.get('datetime_columns', 0)}")

    # PII Detection
    pii_detection = quality_report.get("pii_detection", {})
    if pii_detection.get("has_pii"):
        st.markdown("### PII Detection")
        st.warning(f"Found {pii_detection.get('pii_count', 0)} columns with potential PII data")

        pii_cols = pii_detection.get("pii_columns", [])
        st.write(f"**PII Columns:** {', '.join(pii_cols)}")
        st.info("Recommendation: Apply encryption or masking to these fields before migration")

    # Data Issues
    issues = quality_report.get("data_issues", [])
    if issues:
        st.markdown("### Identified Issues")

        for issue in issues:
            severity = issue.get("severity", "medium")
            icon = "🔴" if severity == "high" else "🟡" if severity == "medium" else "🟢"

            with st.expander(f"{icon} {issue.get('type', 'Unknown').replace('_', ' ').title()} - {issue.get('column', 'N/A')}"):
                st.write(f"**Description:** {issue.get('description', 'N/A')}")
                st.write(f"**Severity:** {severity.upper()}")
                st.write(f"**Affected Rows:** {issue.get('affected_rows', 0):,}")

    # AI Recommendations
    if ai_insights and "recommendations" in ai_insights and ai_insights["recommendations"]:
        st.markdown("### AI Recommendations")

        for rec in ai_insights["recommendations"]:
            priority = rec.get("priority", "Medium")
            priority_color = "error" if priority == "High" else "warning" if priority == "Medium" else "info"

            with st.expander(f"{rec.get('issue', 'Issue')} - Priority: {priority}"):
                st.markdown(f"**Recommendation:** {rec.get('recommendation', 'N/A')}")
                st.info(f"**Estimated Effort:** {rec.get('estimated_effort', 'Unknown')}")

    # Manual Recommendations
    recommendations = quality_report.get("recommendations", [])
    if recommendations:
        st.markdown("### Quality Recommendations")

        for rec in recommendations:
            with st.expander(f"{rec.get('category', 'Unknown')} - {rec.get('priority', 'Medium')} Priority"):
                st.write(f"**Recommendation:** {rec.get('recommendation', 'N/A')}")
                st.info(f"**Action:** {rec.get('action', 'N/A')}")

    # Column Analysis
    st.markdown("### Column-Level Analysis")

    column_analysis = quality_report.get("column_analysis", [])

    if column_analysis:
        # Create DataFrame for display
        columns_df = pd.DataFrame(column_analysis)

        # Select relevant columns
        display_cols = ["column", "dtype", "missing_count", "missing_percentage", "unique_count", "unique_percentage"]
        available_cols = [col for col in display_cols if col in columns_df.columns]

        st.dataframe(
            columns_df[available_cols].style.format({
                "missing_percentage": "{:.2f}%",
                "unique_percentage": "{:.2f}%"
            }),
            use_container_width=True,
            height=400
        )

    # Export report
    st.markdown("---")
    col1, col2, col3 = st.columns([2, 1, 2])

    with col2:
        if st.button("Export Report", use_container_width=True):
            import json
            report_data = {
                "quality_report": quality_report,
                "ai_insights": ai_insights
            }
            st.download_button(
                label="Download JSON Report",
                data=json.dumps(report_data, indent=2, default=str),
                file_name="quality_report.json",
                mime="application/json",
                use_container_width=True
            )


if __name__ == "__main__":
    render()
