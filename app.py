"""
Migrion - Intelligent ERP Data Migration Platform
Main Streamlit Application
"""
import streamlit as st
from streamlit_option_menu import option_menu
from pathlib import Path

# Configure page
st.set_page_config(
    page_title="Migrion - ERP Data Migration",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import utilities
from src.utils.styling import apply_custom_css, create_header
from src.utils.helpers import init_session_state, get_session_state, set_session_state
from src.utils.config import APP_NAME, APP_SUBTITLE, APP_VERSION, EXAMPLE_COMPANIES

# Apply custom styling
apply_custom_css()

# Initialize session state variables
init_session_state("current_page", "home")
init_session_state("project_data", None)
init_session_state("migration_plan", None)
init_session_state("quality_reports", {})
init_session_state("mappings", {})
init_session_state("selected_dataset", None)


def main():
    """Main application entry point."""

    # Sidebar navigation
    with st.sidebar:
        st.markdown(f"""
        <div style='text-align: center; padding: 1rem 0;'>
            <h1 style='font-size: 2rem; margin: 0;'>🔄 {APP_NAME}</h1>
            <p style='color: #9CA3AF; font-size: 0.9rem; margin-top: 0.5rem;'>{APP_SUBTITLE}</p>
            <p style='color: #6B7280; font-size: 0.8rem;'>v{APP_VERSION}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        selected = option_menu(
            menu_title="Navigation",
            options=[
                "Home",
                "Project Intake",
                "Data Quality",
                "Schema Mapping",
                "Knowledge Graph",
                "Validation",
                "Optimizer",
                "Audit & Compliance",
                "Migration Execution",
                "Dashboard"
            ],
            icons=[
                "house-fill",
                "clipboard-check",
                "graph-up",
                "diagram-3",
                "diagram-2",
                "check-circle",
                "lightning",
                "shield-check",
                "play-circle",
                "speedometer2"
            ],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "transparent"},
                "icon": {"color": "#3B82F6", "font-size": "1.2rem"},
                "nav-link": {
                    "font-size": "0.95rem",
                    "text-align": "left",
                    "margin": "0.25rem",
                    "padding": "0.75rem 1rem",
                    "border-radius": "0.5rem",
                    "background-color": "transparent",
                    "color": "#FAFAFA"
                },
                "nav-link-selected": {
                    "background": "linear-gradient(135deg, #2E5EAA 0%, #3B82F6 100%)",
                    "color": "white",
                    "font-weight": "500"
                },
            }
        )

        st.markdown("---")

        # Quick Stats in Sidebar
        if get_session_state("project_data"):
            st.markdown("### 📊 Project Stats")
            project_data = get_session_state("project_data")
            st.metric("Company", project_data.get("company_name", "N/A"))
            st.metric("Target ERP", project_data.get("target_erp", "N/A"))

            if get_session_state("migration_plan"):
                plan = get_session_state("migration_plan")
                if "estimated_total_duration_days" in plan:
                    st.metric("Est. Duration", f"{plan['estimated_total_duration_days']} days")

    # Main content area
    page_map = {
        "Home": show_home,
        "Project Intake": show_project_intake,
        "Data Quality": show_data_quality,
        "Schema Mapping": show_schema_mapping,
        "Knowledge Graph": show_knowledge_graph,
        "Validation": show_validation,
        "Optimizer": show_optimizer,
        "Audit & Compliance": show_audit_compliance,
        "Migration Execution": show_migration_execution,
        "Dashboard": show_dashboard
    }

    # Display selected page
    if selected in page_map:
        page_map[selected]()


def show_home():
    """Home page."""
    st.markdown(create_header(
        "Welcome to Migrion",
        "Your Intelligent ERP Data Migration Platform"
    ), unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>🎯 Smart Planning</h3>
            <p style="color: #9CA3AF; margin-top: 0.5rem;">
                AI-powered migration planning with risk assessment and timeline optimization
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>🔍 Quality Analysis</h3>
            <p style="color: #9CA3AF; margin-top: 0.5rem;">
                Comprehensive data profiling and quality metrics with automated issue detection
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>🛡️ Compliance</h3>
            <p style="color: #9CA3AF; margin-top: 0.5rem;">
                Built-in GDPR, PCI, and audit trails with explainable transformation logs
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("## 🚀 Get Started")

    tab1, tab2 = st.tabs(["📝 New Project", "🎮 Try Demo"])

    with tab1:
        st.markdown("### Create a New Migration Project")
        st.info("Fill out the project intake form to start your migration journey. Our AI will analyze your requirements and generate a customized migration plan.")

        if st.button("Start New Project", type="primary", use_container_width=True, key="start_new_project_btn"):
            # Navigate to Project Intake page by rerunning with a query param
            st.session_state["navigate_to"] = "Project Intake"
            st.rerun()

    with tab2:
        st.markdown("### Try with Example Data")
        st.info("Explore Migrion's capabilities with pre-configured example datasets. Perfect for understanding the platform without setting up your own data.")

        for idx, company in enumerate(EXAMPLE_COMPANIES):
            with st.expander(f"🏢 {company['name']}", expanded=idx==0):
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.markdown(f"**Industry:** {company['industry']}")
                    st.markdown(f"**Description:** {company['description']}")
                    st.markdown(f"**Data Volume:** {company['data_volume']}")
                    st.markdown(f"**Legacy System:** {company['legacy_system']}")
                    st.markdown(f"**Target ERP:** {company['target_erp']}")

                with col2:
                    if st.button("Load Demo", key=f"demo_load_{idx}", use_container_width=True):
                        # Store demo data in session state
                        st.session_state["selected_dataset"] = company["name"]
                        st.session_state["project_data"] = company
                        st.session_state["project_info"] = {
                            "company_name": company["name"],
                            "industry": company["industry"],
                            "description": company["description"],
                            "legacy_system": company["legacy_system"],
                            "target_erp": company.get("target_erp", "Odoo ERP"),
                            "data_volume": company.get("data_volume", "100K - 500K records")
                        }
                        st.success(f"✅ Loaded {company['name']} demo data!")
                        st.balloons()
                        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Features Grid
    st.markdown("## ✨ Key Features")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        ### 📋 Comprehensive Workflow
        - Project intake & discovery
        - Data ingestion & profiling
        - Automated schema mapping
        - Knowledge graph visualization
        - Validation & transformation
        - Migration optimization
        """)

    with col2:
        st.markdown("""
        ### 🤖 AI-Powered Intelligence
        - Gemini-based multi-agent system
        - Smart mapping suggestions
        - Risk assessment & mitigation
        - Strategy recommendations
        - Explainable audit trails
        - Compliance checking
        """)


def show_project_intake():
    """Project intake page."""
    from src.pages import project_intake
    project_intake.render()


def show_data_quality():
    """Data quality analysis page."""
    from src.pages import data_quality_page
    data_quality_page.render()


def show_schema_mapping():
    """Schema mapping page."""
    from src.pages import schema_mapping
    schema_mapping.render()


def show_knowledge_graph():
    """Knowledge graph page."""
    from src.pages import knowledge_graph
    knowledge_graph.render()


def show_validation():
    """Validation page."""
    from src.pages import validation
    validation.render()


def show_optimizer():
    """Optimizer page."""
    from src.pages import optimizer
    optimizer.render()


def show_audit_compliance():
    """Audit & compliance page."""
    from src.pages import audit_compliance
    audit_compliance.render()


def show_migration_execution():
    """Migration execution page."""
    from src.pages import migration_execution
    migration_execution.render()


def show_dashboard():
    """Dashboard page."""
    from src.pages import dashboard
    dashboard.render()


if __name__ == "__main__":
    main()
