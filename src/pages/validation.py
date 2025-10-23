"""Validation Page - Define and run validation rules."""
import streamlit as st
import pandas as pd
import time
from datetime import datetime
from src.utils.styling import apply_custom_css, create_header, create_status_badge
from src.utils.helpers import init_session_state, get_session_state, set_session_state
from src.agents.gemini_agent import ValidationAgent


def render():
    """Render validation page."""
    apply_custom_css()

    st.markdown(create_header(
        "Data Validation",
        "Define validation rules and verify data integrity"
    ), unsafe_allow_html=True)

    # Initialize session state
    init_session_state("validation_rules", None)
    init_session_state("validation_results", None)
    init_session_state("sample_data_for_validation", None)

    # Two-column layout
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### Data Source")

        # Upload or use sample data
        data_source = st.radio(
            "Select Data Source",
            ["Upload CSV", "Use Sample Data", "Use Uploaded Data"],
            horizontal=True
        )

        if data_source == "Upload CSV":
            uploaded_file = st.file_uploader("Upload CSV for validation", type=['csv'])
            if uploaded_file:
                try:
                    df = pd.read_csv(uploaded_file)
                    set_session_state("sample_data_for_validation", df)
                    st.success(f"Loaded {len(df)} rows, {len(df.columns)} columns")
                except Exception as e:
                    st.error(f"Error loading file: {str(e)}")

        elif data_source == "Use Sample Data":
            if st.button("Load Sample Data", use_container_width=True):
                df = get_sample_validation_data()
                set_session_state("sample_data_for_validation", df)
                st.success("Sample data loaded")
                st.rerun()

        elif data_source == "Use Uploaded Data":
            uploaded_data = get_session_state("uploaded_data")
            if uploaded_data is not None:
                set_session_state("sample_data_for_validation", uploaded_data)
                st.success(f"Using previously uploaded data ({len(uploaded_data)} rows)")
            else:
                st.warning("No data found. Please upload data in Data Quality page first.")

    with col2:
        st.markdown("### Schema Definition")

        # Schema input
        schema_input = st.text_area(
            "Enter Schema (JSON)",
            height=200,
            placeholder='{"fields": [{"name": "id", "type": "integer"}]}',
            help="Define your data schema for validation"
        )

        if st.button("Load Sample Schema", use_container_width=True):
            sample_schema = get_sample_schema()
            st.session_state["schema_text"] = sample_schema
            st.rerun()

        if "schema_text" in st.session_state:
            schema_input = st.session_state["schema_text"]

    # Generate validation rules
    st.markdown("---")
    st.markdown("### Generate Validation Rules")

    col1, col2, col3 = st.columns([2, 1, 2])

    with col2:
        generate_rules = st.button(
            "Generate Rules with AI",
            type="primary",
            use_container_width=True,
            disabled=not schema_input
        )

    if generate_rules:
        try:
            import json
            schema = json.loads(schema_input)
            sample_data = get_session_state("sample_data_for_validation")

            with st.spinner("Generating validation rules with AI..."):
                validation_agent = ValidationAgent()

                sample_records = None
                if sample_data is not None and not sample_data.empty:
                    sample_records = sample_data.head(5).to_dict('records')

                rules = validation_agent.suggest_validation_rules(
                    schema=schema,
                    sample_data=sample_records
                )

                if "error" not in rules:
                    set_session_state("validation_rules", rules)
                    st.success("Validation rules generated successfully!")
                else:
                    st.error(f"Error: {rules.get('error')}")
                    st.code(rules.get('raw_response', ''))

        except json.JSONDecodeError as e:
            st.error(f"Invalid JSON schema: {str(e)}")
        except Exception as e:
            st.error(f"Error generating rules: {str(e)}")

    # Display validation rules
    validation_rules = get_session_state("validation_rules")

    if validation_rules and "error" not in validation_rules:
        display_validation_rules(validation_rules)

        # Run validation
        st.markdown("---")
        st.markdown("### Run Validation")

        sample_data = get_session_state("sample_data_for_validation")

        if sample_data is not None and not sample_data.empty:
            col1, col2, col3 = st.columns([2, 1, 2])

            with col2:
                run_validation = st.button(
                    "Run Validation",
                    type="primary",
                    use_container_width=True
                )

            if run_validation:
                with st.spinner("Running validation checks..."):
                    results = run_validation_checks(validation_rules, sample_data)
                    set_session_state("validation_results", results)
                    st.success("Validation complete!")

        else:
            st.info("Upload data to run validation checks")

    # Display validation results
    validation_results = get_session_state("validation_results")

    if validation_results:
        display_validation_results(validation_results)


def get_sample_schema() -> str:
    """Get sample schema as JSON string."""
    import json
    schema = {
        "schema_name": "Customer Data",
        "fields": [
            {"name": "customer_id", "type": "string", "nullable": False},
            {"name": "email", "type": "string", "nullable": False},
            {"name": "age", "type": "integer", "nullable": True},
            {"name": "purchase_amount", "type": "float", "nullable": False},
            {"name": "registration_date", "type": "datetime", "nullable": False}
        ]
    }
    return json.dumps(schema, indent=2)


def get_sample_validation_data() -> pd.DataFrame:
    """Get sample data for validation."""
    data = {
        "customer_id": ["C001", "C002", "C003", "", "C005", "C006", "C007", "C008"],
        "email": ["user1@example.com", "user2@example.com", "invalid-email", "user4@example.com",
                  "user5@example.com", "", "user7@example.com", "user8@example.com"],
        "age": [25, 35, 150, 28, -5, 45, 30, 22],
        "purchase_amount": [100.50, 250.00, 75.25, 0, 1000.00, 50.00, 300.00, -10.00],
        "registration_date": ["2023-01-15", "2023-02-20", "2023-03-10", "2023-04-05",
                              "invalid-date", "2023-06-15", "2023-07-20", "2023-08-25"]
    }
    return pd.DataFrame(data)


def display_validation_rules(rules: dict):
    """Display generated validation rules."""
    st.markdown("---")
    st.markdown("## Validation Rules")

    # Validation rules table
    if "validation_rules" in rules and rules["validation_rules"]:
        st.markdown("### Field Validation Rules")

        rules_list = rules["validation_rules"]

        # Create DataFrame
        rules_df = pd.DataFrame(rules_list)

        # Configure display
        column_config = {
            "field": st.column_config.TextColumn("Field", width="medium"),
            "rule_type": st.column_config.TextColumn("Rule Type", width="small"),
            "rule": st.column_config.TextColumn("Rule", width="large"),
            "severity": st.column_config.TextColumn("Severity", width="small"),
            "error_message": st.column_config.TextColumn("Error Message", width="medium")
        }

        st.dataframe(
            rules_df,
            column_config=column_config,
            use_container_width=True,
            hide_index=True,
            height=300
        )

        # Detailed view
        st.markdown("### Rule Details")

        for idx, rule in enumerate(rules_list):
            severity = rule.get("severity", "Medium")
            severity_color = {
                "Critical": "🔴",
                "High": "🟠",
                "Medium": "🟡",
                "Low": "🟢"
            }.get(severity, "⚪")

            with st.expander(f"{severity_color} {rule.get('field', 'N/A')} - {rule.get('rule_type', 'N/A')}"):
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown(f"**Field:** `{rule.get('field', 'N/A')}`")
                    st.markdown(f"**Rule Type:** {rule.get('rule_type', 'N/A')}")
                    st.markdown(f"**Severity:** {severity}")

                with col2:
                    st.markdown(f"**Rule:** {rule.get('rule', 'N/A')}")
                    st.markdown(f"**Error Message:** {rule.get('error_message', 'N/A')}")

    # Data quality checks
    if "data_quality_checks" in rules and rules["data_quality_checks"]:
        st.markdown("### Data Quality Checks")

        for check in rules["data_quality_checks"]:
            with st.expander(check.get("check_name", "Check")):
                st.write(f"**Description:** {check.get('description', 'N/A')}")
                st.info(f"**Expected Result:** {check.get('expected_result', 'N/A')}")

    # Transformation validations
    if "transformation_validations" in rules and rules["transformation_validations"]:
        st.markdown("### Transformation Validations")

        for validation in rules["transformation_validations"]:
            st.info(validation)


def run_validation_checks(rules: dict, data: pd.DataFrame) -> dict:
    """Run validation checks on data."""
    validation_results = {
        "timestamp": datetime.now().isoformat(),
        "total_rows": len(data),
        "total_checks": 0,
        "passed_checks": 0,
        "failed_checks": 0,
        "errors": [],
        "warnings": [],
        "field_results": {}
    }

    rules_list = rules.get("validation_rules", [])

    for rule in rules_list:
        field = rule.get("field")
        rule_type = rule.get("rule_type")
        severity = rule.get("severity", "Medium")

        validation_results["total_checks"] += 1

        if field not in data.columns:
            validation_results["errors"].append({
                "field": field,
                "error": f"Field '{field}' not found in data",
                "severity": "Critical"
            })
            validation_results["failed_checks"] += 1
            continue

        # Initialize field results
        if field not in validation_results["field_results"]:
            validation_results["field_results"][field] = {
                "total_checks": 0,
                "passed": 0,
                "failed": 0,
                "issues": []
            }

        validation_results["field_results"][field]["total_checks"] += 1

        # Run different validation types
        passed = True

        if rule_type == "required":
            # Check for null values
            null_count = data[field].isnull().sum()
            if null_count > 0:
                passed = False
                validation_results["field_results"][field]["issues"].append({
                    "type": "required",
                    "message": f"Found {null_count} null values",
                    "severity": severity,
                    "affected_rows": int(null_count)
                })

        elif rule_type == "format":
            # Check email format example
            if "email" in field.lower():
                import re
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                invalid_emails = data[~data[field].astype(str).str.match(email_pattern, na=False)]
                if len(invalid_emails) > 0:
                    passed = False
                    validation_results["field_results"][field]["issues"].append({
                        "type": "format",
                        "message": f"Found {len(invalid_emails)} invalid email formats",
                        "severity": severity,
                        "affected_rows": len(invalid_emails)
                    })

        elif rule_type == "range":
            # Check numeric ranges
            if pd.api.types.is_numeric_dtype(data[field]):
                # Check for negative values (example)
                if "age" in field.lower() or "amount" in field.lower():
                    negative_count = (data[field] < 0).sum()
                    if negative_count > 0:
                        passed = False
                        validation_results["field_results"][field]["issues"].append({
                            "type": "range",
                            "message": f"Found {negative_count} negative values",
                            "severity": severity,
                            "affected_rows": int(negative_count)
                        })

                # Check for unrealistic values
                if "age" in field.lower():
                    invalid_age = ((data[field] > 120) | (data[field] < 0)).sum()
                    if invalid_age > 0:
                        passed = False
                        validation_results["field_results"][field]["issues"].append({
                            "type": "range",
                            "message": f"Found {invalid_age} unrealistic age values",
                            "severity": severity,
                            "affected_rows": int(invalid_age)
                        })

        if passed:
            validation_results["passed_checks"] += 1
            validation_results["field_results"][field]["passed"] += 1
        else:
            validation_results["failed_checks"] += 1
            validation_results["field_results"][field]["failed"] += 1

    # Calculate pass rate
    if validation_results["total_checks"] > 0:
        validation_results["pass_rate"] = (
            validation_results["passed_checks"] / validation_results["total_checks"]
        )
    else:
        validation_results["pass_rate"] = 0

    return validation_results


def display_validation_results(results: dict):
    """Display validation results."""
    st.markdown("---")
    st.markdown("## Validation Results")

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Checks", results.get("total_checks", 0))

    with col2:
        passed = results.get("passed_checks", 0)
        st.metric("Passed", passed, delta="✓", delta_color="normal")

    with col3:
        failed = results.get("failed_checks", 0)
        st.metric("Failed", failed, delta="✗" if failed > 0 else "✓", delta_color="inverse" if failed > 0 else "normal")

    with col4:
        pass_rate = results.get("pass_rate", 0) * 100
        st.metric("Pass Rate", f"{pass_rate:.1f}%")

    # Overall status
    if pass_rate >= 90:
        st.success("Excellent! Data passed most validation checks.")
    elif pass_rate >= 70:
        st.warning("Good, but some issues need attention.")
    else:
        st.error("Critical! Multiple validation failures detected.")

    # Field-level results
    st.markdown("### Field-Level Results")

    field_results = results.get("field_results", {})

    for field, field_data in field_results.items():
        passed = field_data.get("passed", 0)
        failed = field_data.get("failed", 0)
        total = field_data.get("total_checks", 0)

        field_pass_rate = (passed / total * 100) if total > 0 else 0

        status_icon = "✅" if failed == 0 else "⚠️" if failed < passed else "❌"

        with st.expander(f"{status_icon} {field} - {field_pass_rate:.0f}% passed"):
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Total Checks", total)
            with col2:
                st.metric("Passed", passed)
            with col3:
                st.metric("Failed", failed)

            # Display issues
            issues = field_data.get("issues", [])
            if issues:
                st.markdown("**Issues Found:**")
                for issue in issues:
                    severity = issue.get("severity", "Medium")
                    severity_color = {
                        "Critical": "error",
                        "High": "warning",
                        "Medium": "info",
                        "Low": "info"
                    }.get(severity, "info")

                    message = f"**{issue.get('type', 'Issue').upper()}:** {issue.get('message', 'N/A')}"
                    message += f" (Affected rows: {issue.get('affected_rows', 0)})"

                    if severity_color == "error":
                        st.error(message)
                    elif severity_color == "warning":
                        st.warning(message)
                    else:
                        st.info(message)
            else:
                st.success("All validation checks passed for this field!")

    # Export results
    st.markdown("---")

    col1, col2, col3 = st.columns([2, 1, 2])

    with col2:
        if st.button("Export Results", use_container_width=True):
            import json
            st.download_button(
                label="Download Validation Report",
                data=json.dumps(results, indent=2, default=str),
                file_name=f"validation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )


if __name__ == "__main__":
    render()
