"""Optimizer Page - Recommend migration strategies."""
import streamlit as st
import plotly.graph_objects as go
from src.utils.styling import apply_custom_css, create_header, create_status_badge, create_metric_card
from src.utils.helpers import init_session_state, get_session_state, set_session_state
from src.agents.gemini_agent import OptimizerAgent


def render():
    """Render optimizer page."""
    apply_custom_css()

    st.markdown(create_header(
        "Migration Strategy Optimizer",
        "Get AI-powered recommendations for optimal migration strategy"
    ), unsafe_allow_html=True)

    # Initialize session state
    init_session_state("optimization_result", None)

    st.markdown("### Migration Parameters")

    # Input parameters
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Data & System Constraints**")

        data_size_gb = st.number_input(
            "Total Data Size (GB)",
            min_value=0.1,
            max_value=10000.0,
            value=100.0,
            step=10.0,
            help="Total size of data to migrate in gigabytes"
        )

        concurrent_users = st.number_input(
            "Concurrent Users",
            min_value=1,
            max_value=100000,
            value=500,
            step=50,
            help="Number of active users during migration"
        )

        current_system_age = st.slider(
            "Legacy System Age (years)",
            min_value=1,
            max_value=30,
            value=5,
            help="Age of the current system"
        )

    with col2:
        st.markdown("**Business Constraints**")

        acceptable_downtime = st.number_input(
            "Acceptable Downtime (hours)",
            min_value=0.0,
            max_value=168.0,
            value=8.0,
            step=0.5,
            help="Maximum acceptable system downtime"
        )

        budget_usd = st.number_input(
            "Budget (USD)",
            min_value=0.0,
            max_value=10000000.0,
            value=150000.0,
            step=10000.0,
            help="Total budget for migration project"
        )

        business_criticality = st.select_slider(
            "Business Criticality",
            options=["Low", "Medium", "High", "Critical"],
            value="High",
            help="How critical is this system to business operations"
        )

    # Additional parameters
    st.markdown("### Additional Considerations")

    col3, col4 = st.columns(2)

    with col3:
        data_complexity = st.select_slider(
            "Data Complexity",
            options=["Simple", "Moderate", "Complex", "Very Complex"],
            value="Moderate",
            help="Complexity of data structures and relationships"
        )

        integration_count = st.number_input(
            "Number of Integrations",
            min_value=0,
            max_value=100,
            value=5,
            help="Number of external system integrations"
        )

    with col4:
        compliance_requirements = st.multiselect(
            "Compliance Requirements",
            ["GDPR", "HIPAA", "SOC 2", "PCI DSS", "ISO 27001", "None"],
            default=["GDPR"]
        )

        rollback_capability = st.radio(
            "Rollback Capability Required",
            ["Yes", "No"],
            index=0,
            horizontal=True
        )

    # Get recommendation
    st.markdown("---")

    col1, col2, col3 = st.columns([2, 1, 2])

    with col2:
        get_recommendation = st.button(
            "Get Recommendation",
            type="primary",
            use_container_width=True
        )

    if get_recommendation:
        with st.spinner("Analyzing parameters and generating recommendations..."):
            try:
                optimizer = OptimizerAgent()

                recommendation = optimizer.recommend_strategy(
                    data_size_gb=data_size_gb,
                    acceptable_downtime_hours=acceptable_downtime,
                    concurrent_users=concurrent_users,
                    budget_usd=budget_usd
                )

                if "error" not in recommendation:
                    set_session_state("optimization_result", recommendation)
                    st.success("Recommendation generated successfully!")
                else:
                    st.error(f"Error: {recommendation.get('error')}")
                    st.code(recommendation.get('raw_response', ''))

            except Exception as e:
                st.error(f"Failed to generate recommendation: {str(e)}")

    # Display recommendation
    optimization_result = get_session_state("optimization_result")

    if optimization_result and "error" not in optimization_result:
        display_recommendation(optimization_result)


def display_recommendation(result: dict):
    """Display optimization recommendation."""
    st.markdown("---")
    st.markdown("## Recommended Strategy")

    # Main recommendation
    strategy = result.get("recommended_strategy", "Unknown")

    # Strategy icon and color
    strategy_info = {
        "Big Bang": {"icon": "🚀", "color": "#EF4444", "description": "Complete cutover in single event"},
        "Phased": {"icon": "📊", "color": "#3B82F6", "description": "Gradual migration in stages"},
        "Hybrid": {"icon": "🔄", "color": "#8B5CF6", "description": "Combination of approaches"},
        "Parallel Run": {"icon": "⚡", "color": "#10B981", "description": "Systems run simultaneously"}
    }

    info = strategy_info.get(strategy, {"icon": "📋", "color": "#6B7280", "description": "Custom approach"})

    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1C2333 0%, #2D3748 100%);
                border-radius: 12px; padding: 2rem; border: 2px solid {info['color']};
                margin-bottom: 2rem;">
        <div style="font-size: 3rem; text-align: center; margin-bottom: 1rem;">{info['icon']}</div>
        <h2 style="text-align: center; color: {info['color']}; margin-bottom: 0.5rem;">{strategy}</h2>
        <p style="text-align: center; color: #9CA3AF; font-size: 1.1rem;">{info['description']}</p>
    </div>
    """, unsafe_allow_html=True)

    # Key metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        downtime = result.get("expected_downtime_hours", 0)
        st.markdown(create_metric_card(
            "Expected Downtime",
            f"{downtime} hours"
        ), unsafe_allow_html=True)

    with col2:
        risk = result.get("risk_level", "Unknown")
        risk_colors = {"Low": "🟢", "Medium": "🟡", "High": "🔴"}
        st.markdown(create_metric_card(
            "Risk Level",
            f"{risk_colors.get(risk, '⚪')} {risk}"
        ), unsafe_allow_html=True)

    with col3:
        cost = result.get("estimated_cost_usd", 0)
        st.markdown(create_metric_card(
            "Estimated Cost",
            f"${cost:,.0f}"
        ), unsafe_allow_html=True)

    with col4:
        # Calculate complexity score
        complexity = len(result.get("implementation_steps", [])) / 10 * 100
        st.markdown(create_metric_card(
            "Complexity",
            f"{min(complexity, 100):.0f}/100"
        ), unsafe_allow_html=True)

    # Rationale
    st.markdown("### Rationale")
    st.info(result.get("rationale", "No rationale provided"))

    # Implementation steps
    if "implementation_steps" in result and result["implementation_steps"]:
        st.markdown("### Implementation Steps")

        for idx, step in enumerate(result["implementation_steps"], 1):
            st.markdown(f"{idx}. {step}")

    # Strategy comparison chart
    if "alternative_strategies" in result and result["alternative_strategies"]:
        st.markdown("### Strategy Comparison")

        create_comparison_chart(result)

    # Alternative strategies
    st.markdown("### Alternative Strategies")

    alternatives = result.get("alternative_strategies", [])

    if alternatives:
        for alt in alternatives:
            strategy_name = alt.get("strategy", "Unknown")

            with st.expander(f"Alternative: {strategy_name}"):
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**Pros:**")
                    for pro in alt.get("pros", []):
                        st.markdown(f"✅ {pro}")

                    st.markdown(f"\n**Expected Downtime:** {alt.get('estimated_downtime_hours', 'N/A')} hours")

                with col2:
                    st.markdown("**Cons:**")
                    for con in alt.get("cons", []):
                        st.markdown(f"❌ {con}")

                    risk = alt.get("risk_level", "Unknown")
                    st.markdown(f"\n**Risk Level:** {risk}")

    # Mitigation plan
    if "mitigation_plan" in result and result["mitigation_plan"]:
        st.markdown("### Risk Mitigation Plan")

        for idx, action in enumerate(result["mitigation_plan"], 1):
            st.markdown(f"{idx}. {action}")

    # Success metrics
    if "success_metrics" in result and result["success_metrics"]:
        st.markdown("### Success Metrics")

        metrics_cols = st.columns(len(result["success_metrics"]))

        for col, metric in zip(metrics_cols, result["success_metrics"]):
            with col:
                st.info(metric)

    # Timeline visualization
    st.markdown("### Estimated Timeline")
    create_timeline_chart(result)

    # Export recommendation
    st.markdown("---")

    col1, col2, col3 = st.columns([2, 1, 2])

    with col2:
        if st.button("Export Recommendation", use_container_width=True):
            import json
            st.download_button(
                label="Download JSON",
                data=json.dumps(result, indent=2),
                file_name="migration_strategy_recommendation.json",
                mime="application/json",
                use_container_width=True
            )


def create_comparison_chart(result: dict):
    """Create comparison chart for strategies."""
    # Prepare data
    strategies = [result.get("recommended_strategy", "Recommended")]
    downtimes = [result.get("expected_downtime_hours", 0)]
    risks = [result.get("risk_level", "Medium")]

    for alt in result.get("alternative_strategies", []):
        strategies.append(alt.get("strategy", "Unknown"))
        downtimes.append(alt.get("estimated_downtime_hours", 0))
        risks.append(alt.get("risk_level", "Medium"))

    # Map risk to numeric values
    risk_map = {"Low": 1, "Medium": 2, "High": 3}
    risk_values = [risk_map.get(r, 2) for r in risks]

    # Create figure
    fig = go.Figure()

    # Add downtime bars
    fig.add_trace(go.Bar(
        name='Expected Downtime (hours)',
        x=strategies,
        y=downtimes,
        marker_color='#3B82F6',
        yaxis='y',
        offsetgroup=1
    ))

    # Add risk bars
    fig.add_trace(go.Bar(
        name='Risk Level (1=Low, 3=High)',
        x=strategies,
        y=risk_values,
        marker_color='#EF4444',
        yaxis='y2',
        offsetgroup=2
    ))

    # Update layout
    fig.update_layout(
        template="plotly_dark",
        barmode='group',
        height=400,
        yaxis=dict(
            title='Downtime (hours)',
            side='left'
        ),
        yaxis2=dict(
            title='Risk Level',
            overlaying='y',
            side='right',
            range=[0, 4]
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    st.plotly_chart(fig, use_container_width=True)


def create_timeline_chart(result: dict):
    """Create timeline visualization."""
    # Estimate phases
    downtime = result.get("expected_downtime_hours", 8)
    strategy = result.get("recommended_strategy", "Phased")

    # Create sample timeline data
    if strategy == "Big Bang":
        phases = [
            {"phase": "Planning", "duration": 30},
            {"phase": "Preparation", "duration": 45},
            {"phase": "Migration", "duration": 5},
            {"phase": "Testing", "duration": 20}
        ]
    elif strategy == "Phased":
        phases = [
            {"phase": "Phase 1: Core Data", "duration": 40},
            {"phase": "Phase 2: Transactions", "duration": 35},
            {"phase": "Phase 3: Analytics", "duration": 25},
            {"phase": "Phase 4: Archive", "duration": 20}
        ]
    else:
        phases = [
            {"phase": "Setup", "duration": 25},
            {"phase": "Migration", "duration": 50},
            {"phase": "Validation", "duration": 25}
        ]

    # Create Gantt-like chart
    fig = go.Figure()

    colors = ['#3B82F6', '#10B981', '#F59E0B', '#8B5CF6', '#EC4899']
    y_pos = list(range(len(phases)))

    for i, phase in enumerate(phases):
        fig.add_trace(go.Bar(
            name=phase["phase"],
            y=[phase["phase"]],
            x=[phase["duration"]],
            orientation='h',
            marker=dict(color=colors[i % len(colors)]),
            text=f"{phase['duration']} days",
            textposition='inside'
        ))

    fig.update_layout(
        template="plotly_dark",
        height=300,
        barmode='stack',
        showlegend=False,
        xaxis_title="Duration (days)",
        yaxis_title=""
    )

    st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    render()
