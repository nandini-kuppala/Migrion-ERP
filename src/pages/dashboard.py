"""Dashboard Page - Overview of migration project status."""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd
from src.utils.styling import apply_custom_css, create_header, create_metric_card, create_status_badge
from src.utils.helpers import init_session_state, get_session_state, format_number, format_percentage


def render():
    """Render dashboard page."""
    apply_custom_css()

    st.markdown(create_header(
        "Migration Dashboard",
        "Real-time overview of your ERP migration project"
    ), unsafe_allow_html=True)

    # Initialize session state
    init_session_state("dashboard_data", None)

    # Get or generate dashboard data
    dashboard_data = get_dashboard_data()

    # Key Metrics Section
    st.markdown("### Project Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        completion = dashboard_data["project"]["completion_percentage"]
        st.markdown(create_metric_card(
            "Overall Progress",
            f"{completion}%",
            delta=f"+{dashboard_data['project']['weekly_progress']}% this week"
        ), unsafe_allow_html=True)

    with col2:
        quality_score = dashboard_data["quality"]["overall_score"]
        st.markdown(create_metric_card(
            "Data Quality",
            f"{quality_score}%",
            delta="Above target" if quality_score >= 70 else "Below target",
            delta_color="normal" if quality_score >= 70 else "inverse"
        ), unsafe_allow_html=True)

    with col3:
        st.markdown(create_metric_card(
            "Total Records",
            format_number(dashboard_data["data"]["total_records"], 0)
        ), unsafe_allow_html=True)

    with col4:
        days_remaining = dashboard_data["project"]["days_remaining"]
        st.markdown(create_metric_card(
            "Days Remaining",
            str(days_remaining),
            delta=f"On schedule" if days_remaining > 0 else "Overdue"
        ), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Status Cards
    col5, col6, col7, col8 = st.columns(4)

    with col5:
        status = dashboard_data["project"]["status"]
        badge = create_status_badge(status.lower())
        st.markdown(f"**Project Status:** {badge}", unsafe_allow_html=True)

    with col6:
        risk = dashboard_data["risk"]["level"]
        risk_badge = create_status_badge("success" if risk == "Low" else "warning" if risk == "Medium" else "error")
        st.markdown(f"**Risk Level:** {risk_badge}", unsafe_allow_html=True)

    with col7:
        compliance = dashboard_data["compliance"]["status"]
        comp_badge = create_status_badge("success" if compliance == "Compliant" else "warning")
        st.markdown(f"**Compliance:** {comp_badge}", unsafe_allow_html=True)

    with col8:
        migration_status = dashboard_data["migration"]["status"]
        mig_badge = create_status_badge(migration_status.lower())
        st.markdown(f"**Migration:** {mig_badge}", unsafe_allow_html=True)

    # Charts Section
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Project Timeline")
        create_timeline_chart(dashboard_data)

        st.markdown("### Data Quality Breakdown")
        create_quality_breakdown_chart(dashboard_data)

    with col2:
        st.markdown("### Phase Progress")
        create_phase_progress_chart(dashboard_data)

        st.markdown("### Migration Volume")
        create_volume_chart(dashboard_data)

    # Detailed Metrics
    st.markdown("---")
    st.markdown("### Detailed Metrics")

    tab1, tab2, tab3, tab4 = st.tabs([
        "Data Quality",
        "Migration Progress",
        "Risk Assessment",
        "Team Activity"
    ])

    with tab1:
        render_quality_metrics(dashboard_data)

    with tab2:
        render_migration_metrics(dashboard_data)

    with tab3:
        render_risk_metrics(dashboard_data)

    with tab4:
        render_activity_metrics(dashboard_data)

    # Recent Activity
    st.markdown("---")
    st.markdown("### Recent Activity")

    render_recent_activity(dashboard_data)

    # Alerts and Notifications
    if dashboard_data.get("alerts"):
        st.markdown("---")
        st.markdown("### Alerts & Notifications")

        for alert in dashboard_data["alerts"]:
            if alert["severity"] == "critical":
                st.error(f"🚨 {alert['message']}")
            elif alert["severity"] == "warning":
                st.warning(f"⚠️ {alert['message']}")
            else:
                st.info(f"ℹ️ {alert['message']}")


def get_dashboard_data() -> dict:
    """Get or generate dashboard data."""
    # Try to get data from session state or generate sample data
    data = get_session_state("dashboard_data")

    if data is None:
        data = generate_sample_dashboard_data()
        st.session_state["dashboard_data"] = data

    return data


def generate_sample_dashboard_data() -> dict:
    """Generate sample dashboard data."""
    return {
        "project": {
            "name": "ERP Migration - Orange League",
            "status": "In Progress",
            "completion_percentage": 65,
            "weekly_progress": 12,
            "start_date": "2024-01-01",
            "target_date": "2024-04-30",
            "days_remaining": 45
        },
        "quality": {
            "overall_score": 78,
            "completeness": 85,
            "accuracy": 82,
            "consistency": 75,
            "uniqueness": 90,
            "issues_count": 23
        },
        "data": {
            "total_records": 250000,
            "migrated_records": 162500,
            "pending_records": 87500,
            "failed_records": 150,
            "total_size_gb": 45.2
        },
        "risk": {
            "level": "Medium",
            "score": 42,
            "active_risks": 5,
            "mitigated_risks": 8
        },
        "compliance": {
            "status": "Compliant",
            "pii_protected": True,
            "audit_enabled": True,
            "gdpr_compliant": True
        },
        "migration": {
            "status": "In Progress",
            "current_phase": "Data Transformation",
            "phases_completed": 2,
            "total_phases": 5
        },
        "phases": [
            {"name": "Planning", "progress": 100, "status": "completed"},
            {"name": "Analysis", "progress": 100, "status": "completed"},
            {"name": "Transformation", "progress": 65, "status": "in_progress"},
            {"name": "Testing", "progress": 0, "status": "pending"},
            {"name": "Deployment", "progress": 0, "status": "pending"}
        ],
        "alerts": [
            {
                "severity": "warning",
                "message": "23 data quality issues require attention",
                "timestamp": "2024-01-15 14:30"
            },
            {
                "severity": "info",
                "message": "Schema mapping completed for Customer module",
                "timestamp": "2024-01-15 12:15"
            }
        ],
        "activity": [
            {"user": "John Doe", "action": "Updated schema mappings", "timestamp": "2 hours ago"},
            {"user": "Jane Smith", "action": "Ran data quality analysis", "timestamp": "3 hours ago"},
            {"user": "System", "action": "Completed batch migration (5000 records)", "timestamp": "5 hours ago"},
            {"user": "Bob Johnson", "action": "Generated audit report", "timestamp": "1 day ago"}
        ]
    }


def create_timeline_chart(data: dict):
    """Create project timeline chart."""
    # Calculate timeline
    start_date = datetime.strptime(data["project"]["start_date"], "%Y-%m-%d")
    target_date = datetime.strptime(data["project"]["target_date"], "%Y-%m-%d")
    current_date = datetime.now()

    total_days = (target_date - start_date).days
    elapsed_days = (current_date - start_date).days
    progress_percentage = (elapsed_days / total_days * 100) if total_days > 0 else 0

    fig = go.Figure()

    # Progress bar
    fig.add_trace(go.Bar(
        x=[data["project"]["completion_percentage"]],
        y=["Actual Progress"],
        orientation='h',
        marker=dict(color='#3B82F6'),
        name='Actual'
    ))

    fig.add_trace(go.Bar(
        x=[progress_percentage],
        y=["Expected Progress"],
        orientation='h',
        marker=dict(color='#10B981'),
        name='Expected'
    ))

    fig.update_layout(
        barmode='group',
        template="plotly_dark",
        height=200,
        xaxis=dict(range=[0, 100], title="Progress (%)"),
        showlegend=True,
        margin=dict(l=20, r=20, t=20, b=20)
    )

    st.plotly_chart(fig, use_container_width=True)


def create_phase_progress_chart(data: dict):
    """Create phase progress chart."""
    phases = data["phases"]

    fig = go.Figure()

    for phase in phases:
        color = "#10B981" if phase["status"] == "completed" else "#3B82F6" if phase["status"] == "in_progress" else "#6B7280"

        fig.add_trace(go.Bar(
            name=phase["name"],
            x=[phase["name"]],
            y=[phase["progress"]],
            marker_color=color,
            text=f"{phase['progress']}%",
            textposition='inside'
        ))

    fig.update_layout(
        template="plotly_dark",
        height=300,
        showlegend=False,
        yaxis=dict(range=[0, 100], title="Progress (%)"),
        xaxis_title=""
    )

    st.plotly_chart(fig, use_container_width=True)


def create_quality_breakdown_chart(data: dict):
    """Create quality breakdown chart."""
    quality = data["quality"]

    categories = ["Completeness", "Accuracy", "Consistency", "Uniqueness"]
    values = [
        quality["completeness"],
        quality["accuracy"],
        quality["consistency"],
        quality["uniqueness"]
    ]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        marker=dict(color='#3B82F6'),
        line=dict(color='#3B82F6')
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        template="plotly_dark",
        height=300,
        margin=dict(l=80, r=80, t=20, b=20)
    )

    st.plotly_chart(fig, use_container_width=True)


def create_volume_chart(data: dict):
    """Create migration volume chart."""
    migration_data = data["data"]

    labels = ['Migrated', 'Pending', 'Failed']
    values = [
        migration_data["migrated_records"],
        migration_data["pending_records"],
        migration_data["failed_records"]
    ]
    colors = ['#10B981', '#F59E0B', '#EF4444']

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        marker=dict(colors=colors)
    )])

    fig.update_layout(
        template="plotly_dark",
        height=300,
        margin=dict(l=20, r=20, t=20, b=20)
    )

    st.plotly_chart(fig, use_container_width=True)


def render_quality_metrics(data: dict):
    """Render detailed quality metrics."""
    quality = data["quality"]

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Overall Score", f"{quality['overall_score']}%")

    with col2:
        st.metric("Completeness", f"{quality['completeness']}%")

    with col3:
        st.metric("Accuracy", f"{quality['accuracy']}%")

    with col4:
        st.metric("Issues", quality["issues_count"], delta="🔍 Review required" if quality["issues_count"] > 0 else "✓")

    # Quality issues table
    st.markdown("**Quality Issues**")

    issues_df = pd.DataFrame([
        {"Severity": "High", "Category": "Missing Data", "Count": 12, "Status": "In Review"},
        {"Severity": "Medium", "Category": "Duplicate Records", "Count": 8, "Status": "Resolved"},
        {"Severity": "Low", "Category": "Format Issues", "Count": 3, "Status": "Pending"}
    ])

    st.dataframe(issues_df, use_container_width=True, hide_index=True)


def render_migration_metrics(data: dict):
    """Render migration progress metrics."""
    migration_data = data["data"]

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Records", format_number(migration_data["total_records"], 0))

    with col2:
        st.metric("Migrated", format_number(migration_data["migrated_records"], 0))

    with col3:
        st.metric("Pending", format_number(migration_data["pending_records"], 0))

    with col4:
        success_rate = (migration_data["migrated_records"] / migration_data["total_records"] * 100)
        st.metric("Success Rate", f"{success_rate:.1f}%")

    # Migration timeline
    st.markdown("**Migration Timeline**")

    # Generate sample timeline data
    dates = pd.date_range(start='2024-01-01', periods=14, freq='D')
    records = [5000, 8000, 12000, 15000, 18000, 22000, 25000, 28000,
               30000, 32000, 34000, 36000, 38000, 40000]

    timeline_df = pd.DataFrame({
        'Date': dates,
        'Records Migrated': records
    })

    fig = px.line(timeline_df, x='Date', y='Records Migrated',
                  markers=True, template='plotly_dark')

    fig.update_traces(line_color='#3B82F6', marker=dict(size=8))

    st.plotly_chart(fig, use_container_width=True)


def render_risk_metrics(data: dict):
    """Render risk assessment metrics."""
    risk = data["risk"]

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Risk Score", f"{risk['score']}/100")

    with col2:
        risk_level = risk["level"]
        color = "🟢" if risk_level == "Low" else "🟡" if risk_level == "Medium" else "🔴"
        st.metric("Risk Level", f"{color} {risk_level}")

    with col3:
        st.metric("Active Risks", risk["active_risks"])

    with col4:
        st.metric("Mitigated", risk["mitigated_risks"])

    # Risk breakdown
    st.markdown("**Active Risks**")

    risks_df = pd.DataFrame([
        {"Risk": "Data Loss", "Probability": "Low", "Impact": "High", "Mitigation": "Daily backups"},
        {"Risk": "Downtime Overrun", "Probability": "Medium", "Impact": "Medium", "Mitigation": "Phased approach"},
        {"Risk": "Integration Issues", "Probability": "Medium", "Impact": "High", "Mitigation": "Pre-testing"},
        {"Risk": "Resource Shortage", "Probability": "Low", "Impact": "Medium", "Mitigation": "Contingency team"},
        {"Risk": "Compliance Violation", "Probability": "Low", "Impact": "Critical", "Mitigation": "Audit reviews"}
    ])

    st.dataframe(risks_df, use_container_width=True, hide_index=True)


def render_activity_metrics(data: dict):
    """Render team activity metrics."""
    st.markdown("**Team Activity Summary**")

    # Team metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Team Members", "8")

    with col2:
        st.metric("Tasks Completed", "42")

    with col3:
        st.metric("Tasks In Progress", "15")

    with col4:
        st.metric("Tasks Pending", "23")

    # Activity by team member
    st.markdown("**Activity by Team Member**")

    activity_df = pd.DataFrame([
        {"Team Member": "John Doe", "Role": "Data Engineer", "Tasks": 15, "Hours": 120},
        {"Team Member": "Jane Smith", "Role": "Data Analyst", "Tasks": 12, "Hours": 95},
        {"Team Member": "Bob Johnson", "Role": "QA Engineer", "Tasks": 8, "Hours": 65},
        {"Team Member": "Alice Williams", "Role": "Project Manager", "Tasks": 7, "Hours": 80}
    ])

    st.dataframe(activity_df, use_container_width=True, hide_index=True)


def render_recent_activity(data: dict):
    """Render recent activity feed."""
    activities = data["activity"]

    for activity in activities:
        col1, col2, col3 = st.columns([2, 4, 2])

        with col1:
            st.markdown(f"**{activity['user']}**")

        with col2:
            st.markdown(activity['action'])

        with col3:
            st.markdown(f"*{activity['timestamp']}*")

        st.markdown("---")


if __name__ == "__main__":
    render()
