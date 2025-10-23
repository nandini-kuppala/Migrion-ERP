"""Audit & Compliance Page - Display audit trail and compliance checks."""
import streamlit as st
import pandas as pd
from datetime import datetime
from src.utils.styling import apply_custom_css, create_header, create_status_badge
from src.utils.helpers import init_session_state, get_session_state, set_session_state
from src.agents.gemini_agent import AuditorAgent


def render():
    """Render audit and compliance page."""
    apply_custom_css()

    st.markdown(create_header(
        "Audit & Compliance",
        "Ensure migration compliance and maintain audit trail"
    ), unsafe_allow_html=True)

    # Initialize session state
    init_session_state("audit_report", None)
    init_session_state("transformations_log", None)

    # Tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs([
        "Audit Report",
        "PII Detection",
        "Compliance Check",
        "Audit Trail"
    ])

    with tab1:
        render_audit_report_tab()

    with tab2:
        render_pii_detection_tab()

    with tab3:
        render_compliance_tab()

    with tab4:
        render_audit_trail_tab()


def render_audit_report_tab():
    """Render audit report generation tab."""
    st.markdown("### Generate Audit Report")

    # Input options
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Transformations Log**")

        upload_transformations = st.file_uploader(
            "Upload Transformations Log (JSON/CSV)",
            type=['json', 'csv'],
            key="transformations_upload"
        )

        if upload_transformations:
            try:
                if upload_transformations.name.endswith('.json'):
                    import json
                    transformations = json.load(upload_transformations)
                else:
                    df = pd.read_csv(upload_transformations)
                    transformations = df.to_dict('records')

                set_session_state("transformations_log", transformations)
                st.success(f"Loaded {len(transformations)} transformation records")

            except Exception as e:
                st.error(f"Error loading file: {str(e)}")

        if st.button("Use Sample Transformations", use_container_width=True):
            transformations = get_sample_transformations()
            set_session_state("transformations_log", transformations)
            st.success("Sample transformations loaded")
            st.rerun()

    with col2:
        st.markdown("**Compliance Requirements**")

        compliance_reqs = st.multiselect(
            "Select Compliance Standards",
            ["GDPR", "HIPAA", "SOC 2", "PCI DSS", "ISO 27001", "CCPA"],
            default=["GDPR", "SOC 2"]
        )

        include_pii = st.checkbox("Include PII Analysis", value=True)
        include_audit_trail = st.checkbox("Include Audit Trail", value=True)

    # Generate report
    st.markdown("---")

    col1, col2, col3 = st.columns([2, 1, 2])

    with col2:
        generate_report = st.button(
            "Generate Audit Report",
            type="primary",
            use_container_width=True,
            disabled=not get_session_state("transformations_log")
        )

    if generate_report:
        transformations = get_session_state("transformations_log")

        with st.spinner("Generating comprehensive audit report..."):
            try:
                auditor = AuditorAgent()

                audit_report = auditor.generate_audit_report(
                    transformations=transformations,
                    compliance_requirements=compliance_reqs
                )

                if "error" not in audit_report:
                    set_session_state("audit_report", audit_report)
                    st.success("Audit report generated successfully!")
                else:
                    st.error(f"Error: {audit_report.get('error')}")
                    st.code(audit_report.get('raw_response', ''))

            except Exception as e:
                st.error(f"Failed to generate audit report: {str(e)}")

    # Display audit report
    audit_report = get_session_state("audit_report")

    if audit_report and "error" not in audit_report:
        display_audit_report(audit_report)


def render_pii_detection_tab():
    """Render PII detection tab."""
    st.markdown("### PII Detection & Protection")

    # Upload data for PII detection
    uploaded_file = st.file_uploader(
        "Upload Data for PII Detection",
        type=['csv'],
        key="pii_upload"
    )

    if uploaded_file or st.button("Use Sample Data", key="pii_sample"):
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
        else:
            df = get_sample_pii_data()

        # Detect PII
        from src.utils.helpers import detect_pii_columns

        pii_columns = detect_pii_columns(df)

        st.markdown("### PII Detection Results")

        if pii_columns:
            st.warning(f"Found {len(pii_columns)} columns with potential PII data")

            # Display PII columns
            pii_df = pd.DataFrame({
                "Column": pii_columns,
                "Sample Data": [df[col].head(3).tolist() for col in pii_columns],
                "Unique Values": [df[col].nunique() for col in pii_columns],
                "Protection Recommended": ["Encrypt/Mask" for _ in pii_columns]
            })

            st.dataframe(pii_df, use_container_width=True)

            # PII categories
            st.markdown("### PII Categories")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown("**Contact Information**")
                contact_pii = [col for col in pii_columns if any(k in col.lower() for k in ['email', 'phone', 'address'])]
                for col in contact_pii:
                    st.info(f"📧 {col}")

            with col2:
                st.markdown("**Personal Identifiers**")
                id_pii = [col for col in pii_columns if any(k in col.lower() for k in ['ssn', 'passport', 'license', 'name'])]
                for col in id_pii:
                    st.info(f"🆔 {col}")

            with col3:
                st.markdown("**Financial Data**")
                fin_pii = [col for col in pii_columns if any(k in col.lower() for k in ['card', 'account', 'credit'])]
                for col in fin_pii:
                    st.info(f"💳 {col}")

            # Recommendations
            st.markdown("### Protection Recommendations")

            st.markdown("""
            **Immediate Actions Required:**
            1. Apply encryption to all PII fields during migration
            2. Implement access controls for PII data
            3. Enable audit logging for PII access
            4. Consider data masking for non-production environments
            5. Implement data retention policies
            """)

        else:
            st.success("No PII columns detected in the dataset")


def render_compliance_tab():
    """Render compliance check tab."""
    st.markdown("### Compliance Status Check")

    audit_report = get_session_state("audit_report")

    if audit_report and "error" not in audit_report:
        # Overall compliance status
        compliance_status = audit_report.get("compliance_status", "Unknown")

        if compliance_status == "Compliant":
            st.success(f"Compliance Status: {compliance_status}")
        elif compliance_status == "Partial":
            st.warning(f"Compliance Status: {compliance_status}")
        else:
            st.error(f"Compliance Status: {compliance_status}")

        # GDPR Compliance
        if "gdpr_compliance" in audit_report:
            st.markdown("### GDPR Compliance")

            gdpr = audit_report["gdpr_compliance"]

            col1, col2 = st.columns(2)

            with col1:
                status = gdpr.get("status", "Unknown")
                if status == "Compliant":
                    st.success(f"Status: {status}")
                else:
                    st.error(f"Status: {status}")

                if gdpr.get("issues"):
                    st.markdown("**Issues:**")
                    for issue in gdpr["issues"]:
                        st.warning(f"- {issue}")

            with col2:
                if gdpr.get("required_actions"):
                    st.markdown("**Required Actions:**")
                    for action in gdpr["required_actions"]:
                        st.info(f"- {action}")

        # Compliance checklist
        st.markdown("### Compliance Checklist")

        checklist_items = [
            {"item": "Data encryption in transit", "status": "compliant"},
            {"item": "Data encryption at rest", "status": "compliant"},
            {"item": "Access control implementation", "status": "compliant"},
            {"item": "Audit logging enabled", "status": "compliant"},
            {"item": "Data retention policy", "status": "pending"},
            {"item": "Right to erasure capability", "status": "compliant"},
            {"item": "Data breach notification process", "status": "compliant"},
            {"item": "Privacy impact assessment", "status": "pending"}
        ]

        for item in checklist_items:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(item["item"])
            with col2:
                badge = create_status_badge(item["status"])
                st.markdown(badge, unsafe_allow_html=True)

    else:
        st.info("Generate an audit report to view compliance status")


def render_audit_trail_tab():
    """Render audit trail tab."""
    st.markdown("### Audit Trail Log")

    # Generate sample audit trail
    audit_trail = get_sample_audit_trail()

    # Filters
    col1, col2, col3 = st.columns(3)

    with col1:
        event_filter = st.multiselect(
            "Filter by Event Type",
            ["All", "CREATE", "UPDATE", "DELETE", "ACCESS", "EXPORT"],
            default=["All"]
        )

    with col2:
        user_filter = st.selectbox(
            "Filter by User",
            ["All Users", "system_admin", "data_engineer", "auditor"]
        )

    with col3:
        severity_filter = st.multiselect(
            "Filter by Severity",
            ["All", "INFO", "WARNING", "ERROR", "CRITICAL"],
            default=["All"]
        )

    # Display audit trail
    df = pd.DataFrame(audit_trail)

    # Apply filters
    if "All" not in event_filter:
        df = df[df["event_type"].isin(event_filter)]

    if user_filter != "All Users":
        df = df[df["user"] == user_filter]

    if "All" not in severity_filter:
        df = df[df["severity"].isin(severity_filter)]

    # Configure display
    st.dataframe(
        df,
        use_container_width=True,
        column_config={
            "timestamp": st.column_config.DatetimeColumn("Timestamp", format="YYYY-MM-DD HH:mm:ss"),
            "event_type": st.column_config.TextColumn("Event Type"),
            "user": st.column_config.TextColumn("User"),
            "resource": st.column_config.TextColumn("Resource"),
            "action": st.column_config.TextColumn("Action"),
            "severity": st.column_config.TextColumn("Severity"),
            "ip_address": st.column_config.TextColumn("IP Address")
        },
        height=400
    )

    # Audit statistics
    st.markdown("### Audit Statistics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Events", len(audit_trail))

    with col2:
        st.metric("Unique Users", len(df["user"].unique()))

    with col3:
        critical_count = len(df[df["severity"] == "CRITICAL"])
        st.metric("Critical Events", critical_count, delta="⚠️" if critical_count > 0 else "✓")

    with col4:
        error_count = len(df[df["severity"] == "ERROR"])
        st.metric("Errors", error_count, delta="⚠️" if error_count > 0 else "✓")

    # Export audit trail
    st.markdown("---")

    col1, col2, col3 = st.columns([2, 1, 2])

    with col2:
        if st.button("Export Audit Trail", use_container_width=True):
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"audit_trail_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )


def get_sample_transformations() -> list:
    """Get sample transformations for audit."""
    return [
        {
            "source_table": "customers",
            "target_table": "res_partner",
            "field_mapping": "customer_id -> id",
            "transformation": "direct",
            "timestamp": "2024-01-15T10:30:00",
            "records_affected": 1500
        },
        {
            "source_table": "customers",
            "target_table": "res_partner",
            "field_mapping": "email_address -> email",
            "transformation": "direct",
            "timestamp": "2024-01-15T10:30:05",
            "records_affected": 1500
        },
        {
            "source_table": "orders",
            "target_table": "sale_order",
            "field_mapping": "order_date -> date_order",
            "transformation": "format_date",
            "timestamp": "2024-01-15T10:35:00",
            "records_affected": 5200
        }
    ]


def get_sample_pii_data() -> pd.DataFrame:
    """Get sample data with PII."""
    return pd.DataFrame({
        "customer_id": ["C001", "C002", "C003"],
        "customer_name": ["John Doe", "Jane Smith", "Bob Johnson"],
        "email": ["john@example.com", "jane@example.com", "bob@example.com"],
        "phone": ["+1-555-0100", "+1-555-0101", "+1-555-0102"],
        "ssn": ["123-45-6789", "987-65-4321", "456-78-9012"],
        "address": ["123 Main St", "456 Oak Ave", "789 Pine Rd"],
        "credit_card": ["****1234", "****5678", "****9012"]
    })


def get_sample_audit_trail() -> list:
    """Get sample audit trail."""
    return [
        {
            "timestamp": "2024-01-15T10:00:00",
            "event_type": "CREATE",
            "user": "system_admin",
            "resource": "migration_project",
            "action": "Created new migration project",
            "severity": "INFO",
            "ip_address": "192.168.1.100"
        },
        {
            "timestamp": "2024-01-15T10:05:00",
            "event_type": "ACCESS",
            "user": "data_engineer",
            "resource": "customer_data",
            "action": "Accessed customer data for mapping",
            "severity": "INFO",
            "ip_address": "192.168.1.101"
        },
        {
            "timestamp": "2024-01-15T10:10:00",
            "event_type": "UPDATE",
            "user": "data_engineer",
            "resource": "schema_mapping",
            "action": "Updated schema mappings",
            "severity": "INFO",
            "ip_address": "192.168.1.101"
        },
        {
            "timestamp": "2024-01-15T10:15:00",
            "event_type": "WARNING",
            "user": "system",
            "resource": "validation",
            "action": "Data quality check found issues",
            "severity": "WARNING",
            "ip_address": "127.0.0.1"
        },
        {
            "timestamp": "2024-01-15T10:20:00",
            "event_type": "EXPORT",
            "user": "auditor",
            "resource": "audit_report",
            "action": "Exported audit report",
            "severity": "INFO",
            "ip_address": "192.168.1.102"
        }
    ]


def display_audit_report(report: dict):
    """Display comprehensive audit report."""
    st.markdown("---")
    st.markdown("## Audit Report")

    # Summary
    st.markdown("### Executive Summary")
    st.info(report.get("audit_summary", "No summary available"))

    # Overall compliance status
    compliance_status = report.get("compliance_status", "Unknown")

    col1, col2, col3 = st.columns(3)

    with col1:
        badge = create_status_badge(
            "success" if compliance_status == "Compliant" else
            "warning" if compliance_status == "Partial" else "error"
        )
        st.markdown(f"**Compliance Status:** {badge}", unsafe_allow_html=True)

    with col2:
        approval = report.get("approval_status", "Unknown")
        badge = create_status_badge(
            "success" if approval == "Approved" else
            "warning" if approval == "Conditional" else "error"
        )
        st.markdown(f"**Approval Status:** {badge}", unsafe_allow_html=True)

    # Findings
    if "findings" in report and report["findings"]:
        st.markdown("### Findings")

        for finding in report["findings"]:
            severity = finding.get("severity", "Medium")
            severity_icon = {
                "Critical": "🔴",
                "High": "🟠",
                "Medium": "🟡",
                "Low": "🟢"
            }.get(severity, "⚪")

            with st.expander(f"{severity_icon} {finding.get('category', 'Finding')} - {severity}"):
                st.markdown(f"**Description:** {finding.get('description', 'N/A')}")

                if finding.get("affected_fields"):
                    st.markdown(f"**Affected Fields:** {', '.join(finding['affected_fields'])}")

                st.info(f"**Recommendation:** {finding.get('recommendation', 'N/A')}")

    # PII Concerns
    if "pii_concerns" in report and report["pii_concerns"]:
        st.markdown("### PII Concerns")

        for concern in report["pii_concerns"]:
            with st.expander(f"PII: {concern.get('field', 'N/A')}"):
                st.warning(f"**Concern:** {concern.get('concern', 'N/A')}")
                st.info(f"**Mitigation:** {concern.get('mitigation', 'N/A')}")

    # Recommendations
    if "recommendations" in report and report["recommendations"]:
        st.markdown("### Recommendations")

        for rec in report["recommendations"]:
            st.markdown(f"- {rec}")

    # Export report
    st.markdown("---")

    col1, col2, col3 = st.columns([2, 1, 2])

    with col2:
        if st.button("Export Report", use_container_width=True, key="export_audit"):
            import json
            st.download_button(
                label="Download Audit Report",
                data=json.dumps(report, indent=2),
                file_name=f"audit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )


if __name__ == "__main__":
    render()
