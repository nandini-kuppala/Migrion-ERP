"""Schema Mapping Page - Display and edit schema mappings."""
import streamlit as st
import pandas as pd
import json
from src.utils.styling import apply_custom_css, create_header, create_status_badge
from src.utils.helpers import init_session_state, get_session_state, set_session_state
from src.agents.gemini_agent import MapperAgent


def render():
    """Render schema mapping page."""
    apply_custom_css()

    st.markdown(create_header(
        "Schema Mapping",
        "Map source fields to target schema with AI-powered suggestions"
    ), unsafe_allow_html=True)

    # Initialize session state
    init_session_state("source_schema", None)
    init_session_state("target_schema", None)
    init_session_state("mappings", None)
    init_session_state("sample_data", None)

    # Two-column layout for schema input
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Source Schema")

        # Source schema input method
        source_method = st.radio(
            "Input Method",
            ["Upload CSV", "Manual JSON", "Use Sample"],
            key="source_method",
            horizontal=True
        )

        if source_method == "Upload CSV":
            source_file = st.file_uploader("Upload Source Data (CSV)", type=['csv'], key="source_csv")
            if source_file:
                try:
                    df = pd.read_csv(source_file)
                    # Generate schema from CSV
                    source_schema = generate_schema_from_df(df, "Source")
                    set_session_state("source_schema", source_schema)
                    set_session_state("sample_data", df.head(10).to_dict('records'))
                    st.success(f"Schema generated from {len(df.columns)} columns")

                    with st.expander("Preview Schema"):
                        st.json(source_schema)
                except Exception as e:
                    st.error(f"Error reading CSV: {str(e)}")

        elif source_method == "Manual JSON":
            source_json = st.text_area(
                "Source Schema (JSON)",
                height=250,
                placeholder='{"fields": [{"name": "customer_id", "type": "string", "nullable": false}]}'
            )
            if source_json:
                try:
                    source_schema = json.loads(source_json)
                    set_session_state("source_schema", source_schema)
                    st.success("Schema loaded successfully")
                except json.JSONDecodeError as e:
                    st.error(f"Invalid JSON: {str(e)}")

        else:  # Use Sample
            if st.button("Load Sample Source Schema", use_container_width=True):
                source_schema = get_sample_source_schema()
                set_session_state("source_schema", source_schema)
                set_session_state("sample_data", get_sample_data())
                st.success("Sample schema loaded")
                st.rerun()

        # Display current source schema
        if get_session_state("source_schema"):
            with st.expander("Current Source Schema", expanded=False):
                st.json(get_session_state("source_schema"))

    with col2:
        st.markdown("### Target Schema")

        # Target schema input method
        target_method = st.radio(
            "Input Method",
            ["Manual JSON", "Use Sample"],
            key="target_method",
            horizontal=True
        )

        if target_method == "Manual JSON":
            target_json = st.text_area(
                "Target Schema (JSON)",
                height=250,
                placeholder='{"fields": [{"name": "client_id", "type": "varchar", "nullable": false}]}'
            )
            if target_json:
                try:
                    target_schema = json.loads(target_json)
                    set_session_state("target_schema", target_schema)
                    st.success("Schema loaded successfully")
                except json.JSONDecodeError as e:
                    st.error(f"Invalid JSON: {str(e)}")

        else:  # Use Sample
            if st.button("Load Sample Target Schema", use_container_width=True):
                target_schema = get_sample_target_schema()
                set_session_state("target_schema", target_schema)
                st.success("Sample schema loaded")
                st.rerun()

        # Display current target schema
        if get_session_state("target_schema"):
            with st.expander("Current Target Schema", expanded=False):
                st.json(get_session_state("target_schema"))

    # Generate mappings button
    st.markdown("---")

    col1, col2, col3 = st.columns([2, 1, 2])

    with col2:
        generate_mappings = st.button(
            "Generate Mappings",
            type="primary",
            use_container_width=True,
            disabled=not (get_session_state("source_schema") and get_session_state("target_schema"))
        )

    if generate_mappings:
        source_schema = get_session_state("source_schema")
        target_schema = get_session_state("target_schema")
        sample_data = get_session_state("sample_data")

        with st.spinner("Analyzing schemas and generating mappings..."):
            try:
                mapper = MapperAgent()
                mappings = mapper.generate_mappings(
                    source_schema=source_schema,
                    target_schema=target_schema,
                    sample_data=sample_data
                )

                if "error" not in mappings:
                    set_session_state("mappings", mappings)
                    st.success("Mappings generated successfully!")
                else:
                    st.error(f"Error generating mappings: {mappings.get('error')}")
                    st.code(mappings.get('raw_response', ''))

            except Exception as e:
                st.error(f"Failed to generate mappings: {str(e)}")

    # Display mappings if available
    mappings = get_session_state("mappings")

    if mappings and "error" not in mappings:
        display_mappings(mappings)


def generate_schema_from_df(df: pd.DataFrame, schema_name: str) -> dict:
    """Generate schema dictionary from DataFrame."""
    fields = []

    for col in df.columns:
        dtype = str(df[col].dtype)

        # Map pandas dtypes to generic types
        if 'int' in dtype:
            field_type = 'integer'
        elif 'float' in dtype:
            field_type = 'float'
        elif 'datetime' in dtype:
            field_type = 'datetime'
        elif 'bool' in dtype:
            field_type = 'boolean'
        else:
            field_type = 'string'

        fields.append({
            "name": col,
            "type": field_type,
            "nullable": bool(df[col].isnull().any()),
            "unique_count": int(df[col].nunique()),
            "sample_values": df[col].dropna().head(3).tolist()
        })

    return {
        "schema_name": schema_name,
        "fields": fields
    }


def get_sample_source_schema() -> dict:
    """Get sample source schema."""
    return {
        "schema_name": "Legacy CRM System",
        "fields": [
            {"name": "customer_id", "type": "string", "nullable": False},
            {"name": "customer_name", "type": "string", "nullable": False},
            {"name": "email_address", "type": "string", "nullable": True},
            {"name": "phone_num", "type": "string", "nullable": True},
            {"name": "registration_date", "type": "datetime", "nullable": False},
            {"name": "account_status", "type": "string", "nullable": False},
            {"name": "total_purchases", "type": "integer", "nullable": False},
            {"name": "lifetime_value", "type": "float", "nullable": False},
            {"name": "street_address", "type": "string", "nullable": True},
            {"name": "city_name", "type": "string", "nullable": True},
            {"name": "state_code", "type": "string", "nullable": True},
            {"name": "zip_code", "type": "string", "nullable": True}
        ]
    }


def get_sample_target_schema() -> dict:
    """Get sample target schema."""
    return {
        "schema_name": "Odoo ERP - Partner Model",
        "fields": [
            {"name": "id", "type": "integer", "nullable": False, "primary_key": True},
            {"name": "name", "type": "varchar", "nullable": False},
            {"name": "email", "type": "varchar", "nullable": True},
            {"name": "phone", "type": "varchar", "nullable": True},
            {"name": "create_date", "type": "timestamp", "nullable": False},
            {"name": "active", "type": "boolean", "nullable": False},
            {"name": "customer_rank", "type": "integer", "nullable": False},
            {"name": "total_invoiced", "type": "numeric", "nullable": False},
            {"name": "street", "type": "varchar", "nullable": True},
            {"name": "city", "type": "varchar", "nullable": True},
            {"name": "state_id", "type": "integer", "nullable": True},
            {"name": "zip", "type": "varchar", "nullable": True},
            {"name": "country_id", "type": "integer", "nullable": True}
        ]
    }


def get_sample_data() -> list:
    """Get sample data."""
    return [
        {
            "customer_id": "C001",
            "customer_name": "Acme Corporation",
            "email_address": "contact@acme.com",
            "phone_num": "+1-555-0100",
            "registration_date": "2023-01-15",
            "account_status": "active",
            "total_purchases": 45,
            "lifetime_value": 125000.50,
            "street_address": "123 Main St",
            "city_name": "New York",
            "state_code": "NY",
            "zip_code": "10001"
        }
    ]


def display_mappings(mappings: dict):
    """Display the generated mappings in an editable table."""
    st.markdown("---")
    st.markdown("## Generated Mappings")

    # Summary metrics
    mapping_list = mappings.get("mappings", [])
    unmapped_source = mappings.get("unmapped_source_fields", [])
    unmapped_target = mappings.get("unmapped_target_fields", [])

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Mappings", len(mapping_list))

    with col2:
        high_confidence = len([m for m in mapping_list if m.get("confidence", 0) >= 0.8])
        st.metric("High Confidence", high_confidence)

    with col3:
        st.metric("Unmapped Source", len(unmapped_source))

    with col4:
        st.metric("Unmapped Target", len(unmapped_target))

    # Mappings table
    st.markdown("### Field Mappings")

    if mapping_list:
        # Convert to DataFrame for editing
        mappings_df = pd.DataFrame(mapping_list)

        # Configure column display
        column_config = {
            "source_field": st.column_config.TextColumn("Source Field", width="medium"),
            "target_field": st.column_config.TextColumn("Target Field", width="medium"),
            "transform": st.column_config.TextColumn("Transformation", width="large"),
            "confidence": st.column_config.ProgressColumn(
                "Confidence",
                format="%.0f%%",
                min_value=0,
                max_value=1,
                width="small"
            ),
            "data_type_source": st.column_config.TextColumn("Source Type", width="small"),
            "data_type_target": st.column_config.TextColumn("Target Type", width="small"),
            "requires_validation": st.column_config.CheckboxColumn("Needs Validation", width="small")
        }

        # Display editable dataframe
        edited_df = st.data_editor(
            mappings_df,
            column_config=column_config,
            use_container_width=True,
            num_rows="dynamic",
            height=400
        )

        # Save edited mappings
        if st.button("Save Mappings", type="primary"):
            updated_mappings = edited_df.to_dict('records')
            mappings["mappings"] = updated_mappings
            set_session_state("mappings", mappings)
            st.success("Mappings saved successfully!")

        # Show details for each mapping
        st.markdown("### Mapping Details")

        for idx, mapping in enumerate(mapping_list):
            confidence = mapping.get("confidence", 0)
            confidence_color = "success" if confidence >= 0.8 else "warning" if confidence >= 0.5 else "error"

            with st.expander(
                f"{mapping.get('source_field', 'N/A')} → {mapping.get('target_field', 'N/A')} "
                f"(Confidence: {confidence*100:.0f}%)"
            ):
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**Source Field:**")
                    st.write(f"Name: `{mapping.get('source_field', 'N/A')}`")
                    st.write(f"Type: `{mapping.get('data_type_source', 'N/A')}`")

                with col2:
                    st.markdown("**Target Field:**")
                    st.write(f"Name: `{mapping.get('target_field', 'N/A')}`")
                    st.write(f"Type: `{mapping.get('data_type_target', 'N/A')}`")

                st.markdown("**Transformation:**")
                st.code(mapping.get('transform', 'direct'), language='python')

                st.markdown("**Explanation:**")
                st.info(mapping.get('explanation', 'No explanation provided'))

                if mapping.get('requires_validation'):
                    st.warning("This mapping requires validation before migration")

    # Unmapped fields
    if unmapped_source or unmapped_target:
        st.markdown("### Unmapped Fields")

        col1, col2 = st.columns(2)

        with col1:
            if unmapped_source:
                st.markdown("**Unmapped Source Fields:**")
                for field in unmapped_source:
                    st.warning(f"- {field}")
                st.info("These source fields have no corresponding target field")

        with col2:
            if unmapped_target:
                st.markdown("**Unmapped Target Fields:**")
                for field in unmapped_target:
                    st.warning(f"- {field}")
                st.info("These target fields will not receive data from source")

    # Suggested transformations
    if "suggested_transformations" in mappings and mappings["suggested_transformations"]:
        st.markdown("### Suggested Transformations")

        for transform in mappings["suggested_transformations"]:
            with st.expander(f"Transform: {transform.get('field', 'N/A')}"):
                st.markdown(f"**Field:** `{transform.get('field', 'N/A')}`")
                st.markdown(f"**Transformation:** {transform.get('transformation', 'N/A')}")
                st.info(f"**Reason:** {transform.get('reason', 'N/A')}")

    # Export mappings
    st.markdown("---")

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("Export as JSON", use_container_width=True):
            st.download_button(
                label="Download Mappings JSON",
                data=json.dumps(mappings, indent=2),
                file_name="schema_mappings.json",
                mime="application/json",
                use_container_width=True
            )

    with col2:
        if st.button("Export as CSV", use_container_width=True):
            mappings_df = pd.DataFrame(mapping_list)
            csv = mappings_df.to_csv(index=False)
            st.download_button(
                label="Download Mappings CSV",
                data=csv,
                file_name="schema_mappings.csv",
                mime="text/csv",
                use_container_width=True
            )

    with col3:
        if st.button("Generate SQL Script", use_container_width=True):
            sql_script = generate_mapping_sql(mapping_list)
            st.download_button(
                label="Download SQL Script",
                data=sql_script,
                file_name="mapping_transform.sql",
                mime="text/plain",
                use_container_width=True
            )


def generate_mapping_sql(mappings: list) -> str:
    """Generate SQL transformation script from mappings."""
    sql_lines = [
        "-- Auto-generated SQL transformation script",
        "-- Generated by Migrion Schema Mapper",
        "",
        "INSERT INTO target_table (",
    ]

    # Target fields
    target_fields = [m.get("target_field") for m in mappings]
    sql_lines.append("  " + ",\n  ".join(target_fields))
    sql_lines.append(")")
    sql_lines.append("SELECT")

    # Transformations
    transforms = []
    for mapping in mappings:
        source = mapping.get("source_field")
        transform = mapping.get("transform", "direct")

        if transform == "direct":
            transforms.append(f"  {source}")
        else:
            transforms.append(f"  {transform} -- {source}")

    sql_lines.append(",\n".join(transforms))
    sql_lines.append("FROM source_table;")

    return "\n".join(sql_lines)


if __name__ == "__main__":
    render()
