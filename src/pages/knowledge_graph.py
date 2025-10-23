"""Knowledge Graph Page - Visualize entity relationships."""
import streamlit as st
import networkx as nx
from pyvis.network import Network
import tempfile
import json
from pathlib import Path
from src.utils.styling import apply_custom_css, create_header
from src.utils.helpers import init_session_state, get_session_state, set_session_state


def render():
    """Render knowledge graph visualization page."""
    apply_custom_css()

    st.markdown(create_header(
        "Knowledge Graph",
        "Visualize entity relationships and data dependencies"
    ), unsafe_allow_html=True)

    # Initialize session state
    init_session_state("graph_data", None)
    init_session_state("selected_entity", None)

    # Options
    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        graph_type = st.selectbox(
            "Graph Type",
            ["ERP Entities", "Data Flow", "Custom"]
        )

    with col2:
        layout = st.selectbox(
            "Layout Algorithm",
            ["force_atlas", "hierarchical", "barnes_hut"]
        )

    with col3:
        if st.button("Generate Graph", type="primary", use_container_width=True):
            set_session_state("regenerate_graph", True)

    # Load or generate graph data
    if get_session_state("regenerate_graph") or get_session_state("graph_data") is None:
        if graph_type == "ERP Entities":
            graph_data = get_erp_entities_graph()
        elif graph_type == "Data Flow":
            graph_data = get_data_flow_graph()
        else:
            graph_data = get_custom_graph()

        set_session_state("graph_data", graph_data)
        set_session_state("regenerate_graph", False)

    graph_data = get_session_state("graph_data")

    # Display graph
    if graph_data:
        st.markdown("### Entity Relationship Visualization")

        # Create and display network graph
        html_file = create_network_graph(graph_data, layout)

        # Display the graph
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
            st.components.v1.html(html_content, height=600, scrolling=False)

        # Graph statistics
        st.markdown("---")
        st.markdown("### Graph Statistics")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Entities", len(graph_data.get("nodes", [])))

        with col2:
            st.metric("Relationships", len(graph_data.get("edges", [])))

        with col3:
            # Calculate average connections
            G = nx.Graph()
            for edge in graph_data.get("edges", []):
                G.add_edge(edge["from"], edge["to"])
            avg_degree = sum(dict(G.degree()).values()) / len(G.nodes()) if len(G.nodes()) > 0 else 0
            st.metric("Avg Connections", f"{avg_degree:.1f}")

        with col4:
            # Find most connected entity
            if G.nodes():
                most_connected = max(dict(G.degree()).items(), key=lambda x: x[1])
                st.metric("Hub Entity", most_connected[0][:15])

        # Entity details
        st.markdown("### Entity Details")

        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs(["Entities", "Relationships", "Graph Data"])

        with tab1:
            display_entities(graph_data.get("nodes", []))

        with tab2:
            display_relationships(graph_data.get("edges", []))

        with tab3:
            st.json(graph_data)

        # Export options
        st.markdown("---")
        st.markdown("### Export Options")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("Export as JSON", use_container_width=True):
                st.download_button(
                    label="Download Graph JSON",
                    data=json.dumps(graph_data, indent=2),
                    file_name="knowledge_graph.json",
                    mime="application/json",
                    use_container_width=True
                )

        with col2:
            if st.button("Export as GraphML", use_container_width=True):
                graphml_data = convert_to_graphml(graph_data)
                st.download_button(
                    label="Download GraphML",
                    data=graphml_data,
                    file_name="knowledge_graph.graphml",
                    mime="application/xml",
                    use_container_width=True
                )

        with col3:
            if st.button("Export HTML", use_container_width=True):
                with open(html_file, 'r', encoding='utf-8') as f:
                    html_data = f.read()
                st.download_button(
                    label="Download Interactive HTML",
                    data=html_data,
                    file_name="knowledge_graph.html",
                    mime="text/html",
                    use_container_width=True
                )


def get_erp_entities_graph() -> dict:
    """Get ERP entities graph data."""
    return {
        "nodes": [
            {"id": "Customer", "label": "Customer", "group": "core", "title": "Customer/Partner entity"},
            {"id": "Order", "label": "Sales Order", "group": "core", "title": "Sales order records"},
            {"id": "Invoice", "label": "Invoice", "group": "finance", "title": "Invoice documents"},
            {"id": "Payment", "label": "Payment", "group": "finance", "title": "Payment transactions"},
            {"id": "Product", "label": "Product", "group": "inventory", "title": "Product catalog"},
            {"id": "Inventory", "label": "Inventory", "group": "inventory", "title": "Stock levels"},
            {"id": "Supplier", "label": "Supplier", "group": "procurement", "title": "Supplier/Vendor data"},
            {"id": "Purchase", "label": "Purchase Order", "group": "procurement", "title": "Purchase orders"},
            {"id": "Employee", "label": "Employee", "group": "hr", "title": "Employee records"},
            {"id": "Project", "label": "Project", "group": "operations", "title": "Project management"},
            {"id": "Contract", "label": "Contract", "group": "operations", "title": "Contract management"},
            {"id": "Delivery", "label": "Delivery", "group": "logistics", "title": "Delivery/Shipping"},
            {"id": "Warehouse", "label": "Warehouse", "group": "logistics", "title": "Warehouse locations"},
        ],
        "edges": [
            {"from": "Customer", "to": "Order", "label": "places", "title": "Customer places orders"},
            {"from": "Order", "to": "Invoice", "label": "generates", "title": "Order generates invoice"},
            {"from": "Invoice", "to": "Payment", "label": "receives", "title": "Invoice receives payment"},
            {"from": "Order", "to": "Product", "label": "contains", "title": "Order contains products"},
            {"from": "Product", "to": "Inventory", "label": "tracked_in", "title": "Product tracked in inventory"},
            {"from": "Supplier", "to": "Purchase", "label": "fulfills", "title": "Supplier fulfills purchase"},
            {"from": "Purchase", "to": "Product", "label": "orders", "title": "Purchase orders products"},
            {"from": "Employee", "to": "Order", "label": "manages", "title": "Employee manages orders"},
            {"from": "Customer", "to": "Project", "label": "sponsors", "title": "Customer sponsors projects"},
            {"from": "Project", "to": "Contract", "label": "governed_by", "title": "Project governed by contract"},
            {"from": "Order", "to": "Delivery", "label": "ships_via", "title": "Order ships via delivery"},
            {"from": "Warehouse", "to": "Inventory", "label": "stores", "title": "Warehouse stores inventory"},
            {"from": "Delivery", "to": "Warehouse", "label": "from", "title": "Delivery from warehouse"},
            {"from": "Employee", "to": "Project", "label": "assigned_to", "title": "Employee assigned to project"},
            {"from": "Customer", "to": "Contract", "label": "signs", "title": "Customer signs contract"},
        ]
    }


def get_data_flow_graph() -> dict:
    """Get data flow graph."""
    return {
        "nodes": [
            {"id": "Source_DB", "label": "Legacy Database", "group": "source", "title": "Source MySQL database"},
            {"id": "Extract", "label": "Data Extract", "group": "etl", "title": "Extract process"},
            {"id": "Transform", "label": "Transform", "group": "etl", "title": "Data transformation"},
            {"id": "Validate", "label": "Validation", "group": "etl", "title": "Data validation"},
            {"id": "Staging", "label": "Staging Area", "group": "intermediate", "title": "Staging database"},
            {"id": "Load", "label": "Data Load", "group": "etl", "title": "Load process"},
            {"id": "Target_DB", "label": "Target ERP", "group": "target", "title": "Target ERP system"},
            {"id": "Audit", "label": "Audit Log", "group": "support", "title": "Audit trail"},
            {"id": "Error", "label": "Error Queue", "group": "support", "title": "Error handling"},
            {"id": "Monitor", "label": "Monitoring", "group": "support", "title": "Process monitoring"},
        ],
        "edges": [
            {"from": "Source_DB", "to": "Extract", "label": "read", "title": "Read data from source"},
            {"from": "Extract", "to": "Transform", "label": "process", "title": "Process extracted data"},
            {"from": "Transform", "to": "Validate", "label": "check", "title": "Validate transformations"},
            {"from": "Validate", "to": "Staging", "label": "stage", "title": "Stage validated data"},
            {"from": "Staging", "to": "Load", "label": "prepare", "title": "Prepare for loading"},
            {"from": "Load", "to": "Target_DB", "label": "write", "title": "Write to target"},
            {"from": "Extract", "to": "Audit", "label": "log", "title": "Log extraction"},
            {"from": "Transform", "to": "Audit", "label": "log", "title": "Log transformations"},
            {"from": "Load", "to": "Audit", "label": "log", "title": "Log loading"},
            {"from": "Validate", "to": "Error", "label": "reject", "title": "Handle validation errors"},
            {"from": "Load", "to": "Error", "label": "fail", "title": "Handle load errors"},
            {"from": "Extract", "to": "Monitor", "label": "track", "title": "Track extraction"},
            {"from": "Transform", "to": "Monitor", "label": "track", "title": "Track transformation"},
            {"from": "Load", "to": "Monitor", "label": "track", "title": "Track loading"},
        ]
    }


def get_custom_graph() -> dict:
    """Get custom sample graph."""
    return {
        "nodes": [
            {"id": "A", "label": "Entity A", "group": "group1", "title": "Sample entity A"},
            {"id": "B", "label": "Entity B", "group": "group1", "title": "Sample entity B"},
            {"id": "C", "label": "Entity C", "group": "group2", "title": "Sample entity C"},
            {"id": "D", "label": "Entity D", "group": "group2", "title": "Sample entity D"},
        ],
        "edges": [
            {"from": "A", "to": "B", "label": "relates", "title": "A relates to B"},
            {"from": "B", "to": "C", "label": "connects", "title": "B connects to C"},
            {"from": "C", "to": "D", "label": "links", "title": "C links to D"},
            {"from": "D", "to": "A", "label": "cycles", "title": "D cycles back to A"},
        ]
    }


def create_network_graph(graph_data: dict, layout: str) -> str:
    """Create interactive network graph using pyvis."""
    # Create network
    net = Network(
        height="550px",
        width="100%",
        bgcolor="#1C2333",
        font_color="#FAFAFA",
        directed=True
    )

    # Set physics layout
    if layout == "force_atlas":
        net.force_atlas_2based()
    elif layout == "hierarchical":
        net.set_options("""
        {
            "layout": {
                "hierarchical": {
                    "enabled": true,
                    "direction": "UD",
                    "sortMethod": "directed"
                }
            }
        }
        """)
    else:  # barnes_hut
        net.barnes_hut()

    # Color scheme for groups
    group_colors = {
        "core": "#3B82F6",
        "finance": "#10B981",
        "inventory": "#F59E0B",
        "procurement": "#8B5CF6",
        "hr": "#EC4899",
        "operations": "#06B6D4",
        "logistics": "#F97316",
        "source": "#EF4444",
        "target": "#22C55E",
        "etl": "#3B82F6",
        "intermediate": "#F59E0B",
        "support": "#8B5CF6",
        "group1": "#3B82F6",
        "group2": "#10B981"
    }

    # Add nodes
    for node in graph_data.get("nodes", []):
        color = group_colors.get(node.get("group", "default"), "#6B7280")
        net.add_node(
            node["id"],
            label=node.get("label", node["id"]),
            title=node.get("title", node["id"]),
            color=color,
            size=25,
            font={"color": "#FAFAFA", "size": 14}
        )

    # Add edges
    for edge in graph_data.get("edges", []):
        net.add_edge(
            edge["from"],
            edge["to"],
            label=edge.get("label", ""),
            title=edge.get("title", ""),
            color={"color": "#6B7280", "opacity": 0.5},
            arrows="to"
        )

    # Save to temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode='w', encoding='utf-8')
    net.save_graph(temp_file.name)
    temp_file.close()

    return temp_file.name


def display_entities(nodes: list):
    """Display entity information in a table."""
    if not nodes:
        st.info("No entities to display")
        return

    # Create DataFrame
    import pandas as pd
    df = pd.DataFrame(nodes)

    # Display with filters
    if "group" in df.columns:
        groups = ["All"] + sorted(df["group"].unique().tolist())
        selected_group = st.selectbox("Filter by Group", groups)

        if selected_group != "All":
            df = df[df["group"] == selected_group]

    st.dataframe(
        df,
        use_container_width=True,
        column_config={
            "id": "Entity ID",
            "label": "Label",
            "group": "Group",
            "title": "Description"
        }
    )


def display_relationships(edges: list):
    """Display relationship information in a table."""
    if not edges:
        st.info("No relationships to display")
        return

    # Create DataFrame
    import pandas as pd
    df = pd.DataFrame(edges)

    st.dataframe(
        df,
        use_container_width=True,
        column_config={
            "from": "From Entity",
            "to": "To Entity",
            "label": "Relationship Type",
            "title": "Description"
        }
    )


def convert_to_graphml(graph_data: dict) -> str:
    """Convert graph data to GraphML format."""
    G = nx.DiGraph()

    # Add nodes
    for node in graph_data.get("nodes", []):
        G.add_node(
            node["id"],
            label=node.get("label", ""),
            group=node.get("group", ""),
            title=node.get("title", "")
        )

    # Add edges
    for edge in graph_data.get("edges", []):
        G.add_edge(
            edge["from"],
            edge["to"],
            label=edge.get("label", ""),
            title=edge.get("title", "")
        )

    # Convert to GraphML
    import io
    output = io.BytesIO()
    nx.write_graphml(G, output)
    return output.getvalue().decode('utf-8')


if __name__ == "__main__":
    render()
