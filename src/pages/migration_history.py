"""Migration History Page — View and compare historical migration runs."""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import json
from pathlib import Path
from datetime import datetime
from src.utils.styling import apply_custom_css, create_header, create_metric_card
from src.utils.helpers import init_session_state, get_session_state, set_session_state
from src.utils.config import HISTORY_DIR


def render():
    """Render migration history analytics page."""
    apply_custom_css()

    st.markdown(create_header(
        "Migration History & Analytics",
        "Track, compare, and analyze past migration runs"
    ), unsafe_allow_html=True)

    # Load history
    runs = _load_all_runs()

    if not runs:
        st.info("No migration history found. Run a migration to see historical analytics here.")
        st.markdown("---")

        if st.button("Generate Sample History", type="primary"):
            _generate_sample_history()
            st.success("Sample history generated!")
            st.rerun()
        return

    # --- Summary Metrics ---
    st.markdown("### Overall Statistics")

    col1, col2, col3, col4 = st.columns(4)

    total_records = sum(r.get("total_records", 0) for r in runs)
    total_migrated = sum(r.get("migrated_records", 0) for r in runs)
    avg_success = (total_migrated / total_records * 100) if total_records > 0 else 0
    avg_duration = sum(r.get("duration_seconds", 0) for r in runs) / len(runs)

    with col1:
        st.markdown(create_metric_card("Total Runs", str(len(runs))), unsafe_allow_html=True)
    with col2:
        st.markdown(create_metric_card("Total Records", f"{total_records:,}"), unsafe_allow_html=True)
    with col3:
        st.markdown(create_metric_card("Avg Success Rate", f"{avg_success:.1f}%"), unsafe_allow_html=True)
    with col4:
        st.markdown(create_metric_card("Avg Duration", f"{avg_duration:.1f}s"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Charts ---
    tab1, tab2, tab3 = st.tabs(["Trends", "Run Details", "Compare Runs"])

    with tab1:
        _render_trends(runs)

    with tab2:
        _render_run_details(runs)

    with tab3:
        _render_comparison(runs)


def _load_all_runs() -> list:
    """Load all migration run histories from disk."""
    runs = []
    history_dir = HISTORY_DIR
    if not history_dir.exists():
        return runs

    for filepath in sorted(history_dir.glob("run_*.json"), reverse=True):
        try:
            with open(filepath, 'r') as f:
                run = json.load(f)
                run["_filename"] = filepath.name
                runs.append(run)
        except Exception:
            continue
    return runs


def _render_trends(runs: list):
    """Render historical trend charts."""
    st.markdown("### Migration Trends")

    df = pd.DataFrame([{
        "Run": r.get("_filename", "").replace("run_", "").replace(".json", ""),
        "Date": r.get("start_time", "")[:10] if r.get("start_time") else "Unknown",
        "Records": r.get("total_records", 0),
        "Migrated": r.get("migrated_records", 0),
        "Failed": r.get("failed_records", 0),
        "Duration (s)": r.get("duration_seconds", 0),
        "Success Rate": (r.get("migrated_records", 0) / max(r.get("total_records", 1), 1)) * 100,
        "Throughput": r.get("migrated_records", 0) / max(r.get("duration_seconds", 1), 0.1),
    } for r in runs])

    if df.empty:
        st.info("No data to display")
        return

    col1, col2 = st.columns(2)

    with col1:
        # Success rate over time
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["Date"], y=df["Success Rate"],
            mode="lines+markers", name="Success Rate",
            line=dict(color="#10B981", width=3),
            marker=dict(size=8)
        ))
        fig.update_layout(title="Success Rate Over Time", template="plotly_dark",
                          yaxis_title="Success Rate (%)", height=300)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Throughput over time
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["Date"], y=df["Throughput"],
            mode="lines+markers", name="Throughput",
            line=dict(color="#3B82F6", width=3),
            marker=dict(size=8)
        ))
        fig.update_layout(title="Throughput (records/sec)", template="plotly_dark",
                          yaxis_title="Records/sec", height=300)
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        # Records per run
        fig = go.Figure(data=[
            go.Bar(name="Migrated", x=df["Run"], y=df["Migrated"], marker_color="#3B82F6"),
            go.Bar(name="Failed", x=df["Run"], y=df["Failed"], marker_color="#EF4444"),
        ])
        fig.update_layout(title="Records Per Run", template="plotly_dark",
                          barmode="stack", height=300)
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        # Duration per run
        fig = go.Figure(data=[
            go.Bar(x=df["Run"], y=df["Duration (s)"], marker_color="#F59E0B")
        ])
        fig.update_layout(title="Duration Per Run (seconds)", template="plotly_dark", height=300)
        st.plotly_chart(fig, use_container_width=True)


def _render_run_details(runs: list):
    """Render detailed info for each run."""
    st.markdown("### Run Details")

    run_names = [r.get("_filename", f"Run {i}") for i, r in enumerate(runs)]
    selected = st.selectbox("Select Run", run_names)

    run = next((r for r in runs if r.get("_filename") == selected), None)

    if run:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Records", f"{run.get('total_records', 0):,}")
        with col2:
            st.metric("Migrated", f"{run.get('migrated_records', 0):,}")
        with col3:
            st.metric("Failed", run.get("failed_records", 0))
        with col4:
            dur = run.get("duration_seconds", 0)
            st.metric("Duration", f"{dur:.2f}s")

        col5, col6, col7, col8 = st.columns(4)
        success = (run.get('migrated_records', 0) / max(run.get('total_records', 1), 1)) * 100
        with col5:
            st.metric("Success Rate", f"{success:.1f}%")
        with col6:
            st.metric("Collections", run.get("collections_created", 0))
        with col7:
            st.metric("Start Time", run.get("start_time", "N/A")[:19])
        with col8:
            throughput = run.get("migrated_records", 0) / max(dur, 0.1)
            st.metric("Throughput", f"{throughput:.0f} rec/s")

        with st.expander("Full Run Data (JSON)"):
            display_run = {k: v for k, v in run.items() if not k.startswith("_")}
            st.json(display_run)


def _render_comparison(runs: list):
    """Compare two migration runs side by side."""
    st.markdown("### Compare Runs")

    if len(runs) < 2:
        st.info("Need at least 2 runs to compare")
        return

    run_names = [r.get("_filename", f"Run {i}") for i, r in enumerate(runs)]

    col1, col2 = st.columns(2)
    with col1:
        run_a_name = st.selectbox("Run A", run_names, index=0, key="cmp_a")
    with col2:
        run_b_name = st.selectbox("Run B", run_names,
                                  index=min(1, len(run_names) - 1), key="cmp_b")

    run_a = next((r for r in runs if r.get("_filename") == run_a_name), {})
    run_b = next((r for r in runs if r.get("_filename") == run_b_name), {})

    metrics = ["total_records", "migrated_records", "failed_records",
               "duration_seconds", "collections_created"]

    comparison_data = []
    for m in metrics:
        a_val = run_a.get(m, 0)
        b_val = run_b.get(m, 0)
        diff = b_val - a_val
        comparison_data.append({
            "Metric": m.replace("_", " ").title(),
            "Run A": a_val,
            "Run B": b_val,
            "Difference": diff,
            "Change": f"+{diff}" if diff > 0 else str(diff)
        })

    st.dataframe(pd.DataFrame(comparison_data), use_container_width=True, hide_index=True)

    # Visual comparison
    fig = go.Figure(data=[
        go.Bar(name=run_a_name[:20], x=[d["Metric"] for d in comparison_data],
               y=[d["Run A"] for d in comparison_data], marker_color="#3B82F6"),
        go.Bar(name=run_b_name[:20], x=[d["Metric"] for d in comparison_data],
               y=[d["Run B"] for d in comparison_data], marker_color="#10B981"),
    ])
    fig.update_layout(title="Run Comparison", template="plotly_dark",
                      barmode="group", height=350)
    st.plotly_chart(fig, use_container_width=True)


def _generate_sample_history():
    """Generate sample migration history for demo purposes."""
    import random
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)

    for i in range(6):
        run = {
            "start_time": f"2024-01-{10+i*3:02d}T{8+i}:00:00",
            "end_time": f"2024-01-{10+i*3:02d}T{8+i}:05:00",
            "total_files": random.randint(3, 8),
            "total_records": random.randint(10000, 100000),
            "migrated_records": 0,
            "failed_records": 0,
            "collections_created": random.randint(3, 8),
            "duration_seconds": random.uniform(5, 60),
        }
        run["migrated_records"] = int(run["total_records"] * random.uniform(0.92, 1.0))
        run["failed_records"] = run["total_records"] - run["migrated_records"]

        filepath = HISTORY_DIR / f"run_2024{10+i*3:02d}{random.randint(100000, 999999)}.json"
        with open(filepath, 'w') as f:
            json.dump(run, f, indent=2)


def save_migration_run(stats: dict):
    """Save a completed migration run to history. Called from migration_execution.py."""
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = HISTORY_DIR / f"run_{timestamp}.json"

    run_data = {}
    for key in ["start_time", "end_time", "total_files", "total_records",
                "migrated_records", "failed_records", "collections_created",
                "duration_seconds"]:
        val = stats.get(key)
        if hasattr(val, 'isoformat'):
            run_data[key] = val.isoformat()
        else:
            run_data[key] = val

    with open(filepath, 'w') as f:
        json.dump(run_data, f, indent=2, default=str)


if __name__ == "__main__":
    render()
