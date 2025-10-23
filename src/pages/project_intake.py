"""Project Intake Page - Collect organization information and generate migration plan."""
import streamlit as st
import time
from src.utils.styling import apply_custom_css, create_header, create_status_badge
from src.utils.helpers import init_session_state, set_session_state, get_session_state
from src.agents.gemini_agent import PlannerAgent
from src.utils.config import EXAMPLE_COMPANIES


def render():
    """Render project intake page."""
    apply_custom_css()

    st.markdown(create_header(
        "Project Intake",
        "Provide your organization details to generate a customized migration plan"
    ), unsafe_allow_html=True)

    # Initialize session state
    init_session_state("migration_plan", None)
    init_session_state("project_info", {})

    # Two-column layout for form
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Organization Details")

        # Organization information
        company_name = st.text_input(
            "Company Name",
            value=get_session_state("project_info", {}).get("company_name", ""),
            placeholder="Enter company name"
        )

        industry = st.selectbox(
            "Industry",
            options=[
                "Technology/SaaS",
                "E-commerce",
                "Manufacturing",
                "Healthcare",
                "Finance",
                "Retail",
                "Logistics",
                "Education",
                "Other"
            ],
            index=0
        )

        company_size = st.selectbox(
            "Company Size",
            options=[
                "1-50 employees",
                "51-200 employees",
                "201-500 employees",
                "501-1000 employees",
                "1000+ employees"
            ],
            index=1
        )

        description = st.text_area(
            "Business Description",
            value=get_session_state("project_info", {}).get("description", ""),
            placeholder="Brief description of your business operations",
            height=100
        )

    with col2:
        st.markdown("### Migration Parameters")

        # Migration details
        legacy_system = st.text_input(
            "Legacy System",
            value=get_session_state("project_info", {}).get("legacy_system", ""),
            placeholder="e.g., Custom MySQL Database, Oracle EBS, etc."
        )

        target_erp = st.selectbox(
            "Target ERP System",
            options=[
                "Odoo ERP",
                "SAP S/4HANA",
                "SAP Commerce Cloud",
                "Microsoft Dynamics 365",
                "Oracle NetSuite",
                "Salesforce",
                "Other"
            ],
            index=0
        )

        data_volume = st.selectbox(
            "Estimated Data Volume",
            options=[
                "< 10K records",
                "10K - 100K records",
                "100K - 500K records",
                "500K - 1M records",
                "> 1M records"
            ],
            index=1
        )

        timeline = st.selectbox(
            "Desired Timeline",
            options=[
                "1-3 months",
                "3-6 months",
                "6-12 months",
                "> 12 months"
            ],
            index=1
        )

    # Additional parameters
    st.markdown("### Additional Requirements")

    col3, col4 = st.columns(2)

    with col3:
        acceptable_downtime = st.number_input(
            "Acceptable Downtime (hours)",
            min_value=0.0,
            max_value=168.0,
            value=4.0,
            step=0.5,
            help="Maximum acceptable system downtime during migration"
        )

        concurrent_users = st.number_input(
            "Concurrent Users",
            min_value=1,
            max_value=10000,
            value=100,
            step=10,
            help="Number of concurrent users in the system"
        )

    with col4:
        budget_range = st.selectbox(
            "Budget Range (USD)",
            options=[
                "< $50K",
                "$50K - $100K",
                "$100K - $250K",
                "$250K - $500K",
                "> $500K"
            ],
            index=2
        )

        compliance_requirements = st.multiselect(
            "Compliance Requirements",
            options=["GDPR", "HIPAA", "SOC 2", "PCI DSS", "ISO 27001"],
            default=["GDPR"]
        )

    # Example companies
    st.markdown("---")
    st.markdown("### Quick Start Examples")

    example_cols = st.columns(len(EXAMPLE_COMPANIES))

    for idx, (col, company) in enumerate(zip(example_cols, EXAMPLE_COMPANIES)):
        with col:
            if st.button(
                f"Load {company['name'].split()[0]}",
                key=f"example_{idx}",
                use_container_width=True
            ):
                st.session_state.project_info = {
                    "company_name": company["name"],
                    "industry": company["industry"],
                    "description": company["description"],
                    "legacy_system": company["legacy_system"],
                    "target_erp": company.get("target_erp", "Odoo ERP"),
                    "data_volume": company.get("data_volume", "100K - 500K records")
                }
                st.rerun()

    # Generate plan button
    st.markdown("---")

    col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 2])

    with col_btn2:
        generate_button = st.button(
            "Generate Migration Plan",
            type="primary",
            use_container_width=True,
            disabled=not (company_name and legacy_system)
        )

    if generate_button:
        if not company_name or not legacy_system:
            st.error("Please fill in Company Name and Legacy System fields")
        else:
            # Store project information
            project_info = {
                "company_name": company_name,
                "industry": industry,
                "company_size": company_size,
                "description": description,
                "legacy_system": legacy_system,
                "target_erp": target_erp,
                "data_volume": data_volume,
                "timeline": timeline,
                "acceptable_downtime": acceptable_downtime,
                "concurrent_users": concurrent_users,
                "budget_range": budget_range,
                "compliance_requirements": compliance_requirements
            }
            set_session_state("project_info", project_info)

            # Generate migration plan using AI
            with st.spinner("Analyzing your requirements and generating migration plan..."):
                try:
                    planner = PlannerAgent()

                    # Simulate progress
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    status_text.text("Analyzing organization requirements...")
                    progress_bar.progress(25)
                    time.sleep(1)

                    status_text.text("Evaluating migration complexity...")
                    progress_bar.progress(50)

                    migration_plan = planner.generate_migration_plan(
                        org_info=project_info,
                        legacy_system=legacy_system,
                        target_erp=target_erp,
                        data_volume=data_volume
                    )

                    status_text.text("Generating detailed roadmap...")
                    progress_bar.progress(75)
                    time.sleep(0.5)

                    status_text.text("Finalizing recommendations...")
                    progress_bar.progress(100)
                    time.sleep(0.5)

                    progress_bar.empty()
                    status_text.empty()

                    if "error" not in migration_plan:
                        set_session_state("migration_plan", migration_plan)
                        st.success("Migration plan generated successfully!")
                    else:
                        st.error(f"Error generating plan: {migration_plan.get('error')}")
                        st.code(migration_plan.get('raw_response', ''))

                except Exception as e:
                    st.error(f"Failed to generate migration plan: {str(e)}")

    # Display migration plan if available
    if get_session_state("migration_plan"):
        display_migration_plan(get_session_state("migration_plan"))


def display_migration_plan(plan: dict):
    """Display the generated migration plan."""
    st.markdown("---")
    st.markdown("## Generated Migration Plan")

    # Overview section
    st.markdown("### Executive Summary")
    if "overview" in plan:
        st.info(plan["overview"])

    # Key metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Duration",
            f"{plan.get('estimated_total_duration_days', 'N/A')} days"
        )

    with col2:
        st.metric(
            "Expected Downtime",
            f"{plan.get('estimated_downtime_hours', 'N/A')} hours"
        )

    with col3:
        risk_level = plan.get('risk_assessment', {}).get('overall_risk_level', 'Unknown')
        risk_color = {
            "Low": "🟢",
            "Medium": "🟡",
            "High": "🔴"
        }.get(risk_level, "⚪")
        st.metric(
            "Risk Level",
            f"{risk_color} {risk_level}"
        )

    with col4:
        team_size = plan.get('resource_requirements', {}).get('team_size', 'N/A')
        st.metric(
            "Team Size",
            f"{team_size} members"
        )

    # Migration phases
    if "phases" in plan and plan["phases"]:
        st.markdown("### Migration Phases")

        for idx, phase in enumerate(plan["phases"], 1):
            with st.expander(f"Phase {idx}: {phase.get('phase_name', 'Unknown')} ({phase.get('duration_days', 0)} days)", expanded=idx == 1):
                st.markdown(f"**Description:** {phase.get('description', 'N/A')}")

                col_a, col_b = st.columns(2)

                with col_a:
                    st.markdown("**Critical Steps:**")
                    for step in phase.get('critical_steps', []):
                        st.markdown(f"- {step}")

                with col_b:
                    st.markdown("**Success Criteria:**")
                    for criteria in phase.get('success_criteria', []):
                        st.markdown(f"- {criteria}")

                st.markdown("**Risks:**")
                for risk in phase.get('risks', []):
                    st.warning(risk)

    # Risk assessment
    if "risk_assessment" in plan:
        st.markdown("### Risk Assessment")

        risk_data = plan["risk_assessment"]

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Major Risks:**")
            for risk in risk_data.get('major_risks', []):
                st.markdown(f"- {risk}")

        with col2:
            st.markdown("**Mitigation Strategies:**")
            for strategy in risk_data.get('mitigation_strategies', []):
                st.markdown(f"- {strategy}")

    # Resource requirements
    if "resource_requirements" in plan:
        st.markdown("### Resource Requirements")

        resources = plan["resource_requirements"]

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Required Skillsets:**")
            for skill in resources.get('skillsets_needed', []):
                st.markdown(f"- {skill}")

        with col2:
            st.markdown("**Tools Required:**")
            for tool in resources.get('tools_required', []):
                st.markdown(f"- {tool}")

    # Validation checkpoints
    if "validation_checkpoints" in plan and plan["validation_checkpoints"]:
        st.markdown("### Validation Checkpoints")
        for checkpoint in plan["validation_checkpoints"]:
            st.markdown(f"- {checkpoint}")

    # Rollback strategy
    if "rollback_strategy" in plan:
        st.markdown("### Rollback Strategy")
        st.info(plan["rollback_strategy"])

    # Export plan
    st.markdown("---")
    col1, col2, col3 = st.columns([2, 1, 2])

    with col2:
        if st.button("Export Plan as JSON", use_container_width=True):
            import json
            st.download_button(
                label="Download JSON",
                data=json.dumps(plan, indent=2),
                file_name="migration_plan.json",
                mime="application/json",
                use_container_width=True
            )


if __name__ == "__main__":
    render()
