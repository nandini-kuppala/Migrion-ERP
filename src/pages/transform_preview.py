"""Transform Preview Page — Preview data transformations before migration."""
import streamlit as st
import pandas as pd
import json
from src.utils.styling import apply_custom_css, create_header
from src.utils.helpers import init_session_state, get_session_state, set_session_state


def render():
    """Render data transformation preview page."""
    apply_custom_css()

    st.markdown(create_header(
        "Data Transformation Preview",
        "Preview how your data will look after transformation — before migration"
    ), unsafe_allow_html=True)

    init_session_state("preview_source_df", None)
    init_session_state("preview_rules", [])
    init_session_state("preview_result_df", None)

    # --- Data Source ---
    st.markdown("### 1. Source Data")

    source_method = st.radio("Data Source", ["Upload CSV", "Use Sample"], horizontal=True,
                             key="tp_source_method")

    if source_method == "Upload CSV":
        uploaded = st.file_uploader("Upload source CSV", type=["csv"], key="tp_upload")
        if uploaded:
            df = pd.read_csv(uploaded)
            set_session_state("preview_source_df", df)
            st.success(f"Loaded {len(df)} rows × {len(df.columns)} columns")
    else:
        if st.button("Load Sample Data", key="tp_sample"):
            df = _get_sample_data()
            set_session_state("preview_source_df", df)
            st.success("Sample data loaded")
            st.rerun()

    source_df = get_session_state("preview_source_df")

    if source_df is not None:
        with st.expander("Source Data Preview", expanded=True):
            st.dataframe(source_df.head(20), use_container_width=True, height=250)

        # --- Transformation Rules ---
        st.markdown("---")
        st.markdown("### 2. Define Transformations")

        rules = []

        # Pre-populate from schema mapping if available
        mappings_data = get_session_state("mappings")

        tab1, tab2, tab3 = st.tabs(["Rename Fields", "Type Conversions", "Custom Transforms"])

        with tab1:
            st.markdown("**Rename Columns**")
            rename_rules = {}
            for col in source_df.columns:
                new_name = st.text_input(f"`{col}` →", value=col, key=f"rename_{col}")
                if new_name != col and new_name.strip():
                    rename_rules[col] = new_name.strip()
            if rename_rules:
                rules.append({"type": "rename", "mapping": rename_rules})

        with tab2:
            st.markdown("**Type Conversions**")
            type_conversions = {}
            for col in source_df.columns:
                current_type = str(source_df[col].dtype)
                target_type = st.selectbox(
                    f"`{col}` ({current_type})",
                    ["Keep", "string", "integer", "float", "datetime", "boolean"],
                    key=f"type_{col}"
                )
                if target_type != "Keep":
                    type_conversions[col] = target_type
            if type_conversions:
                rules.append({"type": "type_cast", "conversions": type_conversions})

        with tab3:
            st.markdown("**Custom Transformations**")
            st.info("Define custom transformations using column expressions")

            col1, col2 = st.columns(2)
            with col1:
                new_col_name = st.text_input("New Column Name", key="custom_col_name")
            with col2:
                source_cols = st.multiselect("Source Columns", source_df.columns.tolist(),
                                             key="custom_source_cols")

            operation = st.selectbox("Operation",
                                     ["Concatenate", "Uppercase", "Lowercase", "Strip Whitespace",
                                      "Fill Missing", "Drop Column"],
                                     key="custom_op")

            if operation == "Fill Missing":
                fill_value = st.text_input("Fill value", "N/A", key="fill_val")
            elif operation == "Concatenate":
                separator = st.text_input("Separator", " ", key="concat_sep")

            if st.button("Add Transformation", key="add_custom"):
                custom_rule = {
                    "type": "custom",
                    "operation": operation,
                    "source_columns": source_cols,
                    "new_column": new_col_name,
                }
                if operation == "Fill Missing":
                    custom_rule["fill_value"] = fill_value
                elif operation == "Concatenate":
                    custom_rule["separator"] = separator
                rules.append(custom_rule)
                st.success(f"Added: {operation} on {source_cols}")

        # --- Apply and Preview ---
        st.markdown("---")
        st.markdown("### 3. Preview Transformation")

        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            apply_btn = st.button("Apply & Preview", type="primary", use_container_width=True)

        if apply_btn:
            result_df = _apply_transformations(source_df.copy(), rules)
            set_session_state("preview_result_df", result_df)
            st.success("Transformations applied!")

        result_df = get_session_state("preview_result_df")

        if result_df is not None:
            st.markdown("### Side-by-Side Comparison")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Before (Source)**")
                st.dataframe(source_df.head(15), use_container_width=True, height=350)
                st.caption(f"{len(source_df)} rows × {len(source_df.columns)} cols")

            with col2:
                st.markdown("**After (Transformed)**")
                st.dataframe(result_df.head(15), use_container_width=True, height=350)
                st.caption(f"{len(result_df)} rows × {len(result_df.columns)} cols")

            # Change summary
            st.markdown("### Change Summary")

            changes = _compute_changes(source_df, result_df)

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Columns Renamed", changes["renamed"])
            with col2:
                st.metric("Types Changed", changes["type_changed"])
            with col3:
                st.metric("Columns Added", changes["added"])
            with col4:
                st.metric("Columns Removed", changes["removed"])

            # Export
            st.markdown("---")
            col1, col2, col3 = st.columns([2, 1, 2])
            with col2:
                csv_data = result_df.to_csv(index=False)
                st.download_button(
                    "Download Transformed CSV",
                    data=csv_data,
                    file_name="transformed_data.csv",
                    mime="text/csv",
                    use_container_width=True
                )


def _get_sample_data() -> pd.DataFrame:
    """Get sample data for transformation preview."""
    return pd.DataFrame({
        "customer_id": ["C001", "C002", "C003", "C004", "C005"],
        "customer_name": ["Acme Corp", "beta industries", "  Gamma LLC  ", "DELTA INC", "Epsilon Co"],
        "email_address": ["acme@test.com", "beta@test.com", None, "delta@test.com", "epsilon@test.com"],
        "phone_num": ["+1-555-0100", "+1-555-0101", "+1-555-0102", None, "+1-555-0104"],
        "registration_date": ["2023-01-15", "01-20-2023", "2023/03/10", "2023-04-05", "2023-05-20"],
        "total_purchases": [45, 12, 78, 3, 156],
        "lifetime_value": [125000.50, 8500.00, 340000.00, 1200.00, 890000.00],
        "status": ["active", "Active", "ACTIVE", "inactive", "Active"],
    })


def _apply_transformations(df: pd.DataFrame, rules: list) -> pd.DataFrame:
    """Apply transformation rules to a DataFrame."""
    for rule in rules:
        rule_type = rule.get("type", "")

        if rule_type == "rename":
            mapping = rule.get("mapping", {})
            df = df.rename(columns=mapping)

        elif rule_type == "type_cast":
            for col, target_type in rule.get("conversions", {}).items():
                if col in df.columns:
                    try:
                        if target_type == "string":
                            df[col] = df[col].astype(str)
                        elif target_type == "integer":
                            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
                        elif target_type == "float":
                            df[col] = pd.to_numeric(df[col], errors="coerce")
                        elif target_type == "datetime":
                            df[col] = pd.to_datetime(df[col], errors="coerce")
                        elif target_type == "boolean":
                            df[col] = df[col].astype(bool)
                    except Exception:
                        pass

        elif rule_type == "custom":
            operation = rule.get("operation", "")
            source_cols = rule.get("source_columns", [])
            new_col = rule.get("new_column", "")

            if operation == "Concatenate" and source_cols and new_col:
                sep = rule.get("separator", " ")
                df[new_col] = df[source_cols].astype(str).agg(sep.join, axis=1)

            elif operation == "Uppercase":
                for col in source_cols:
                    if col in df.columns:
                        df[col] = df[col].astype(str).str.upper()

            elif operation == "Lowercase":
                for col in source_cols:
                    if col in df.columns:
                        df[col] = df[col].astype(str).str.lower()

            elif operation == "Strip Whitespace":
                for col in source_cols:
                    if col in df.columns:
                        df[col] = df[col].astype(str).str.strip()

            elif operation == "Fill Missing":
                fill_value = rule.get("fill_value", "N/A")
                for col in source_cols:
                    if col in df.columns:
                        df[col] = df[col].fillna(fill_value)

            elif operation == "Drop Column":
                for col in source_cols:
                    if col in df.columns:
                        df = df.drop(columns=[col])

    return df


def _compute_changes(before: pd.DataFrame, after: pd.DataFrame) -> dict:
    """Compute summary of changes between before and after DataFrames."""
    before_cols = set(before.columns)
    after_cols = set(after.columns)

    renamed = len(after_cols - before_cols)
    removed = len(before_cols - after_cols)
    added = len(after_cols - before_cols)

    type_changed = 0
    for col in before_cols & after_cols:
        if str(before[col].dtype) != str(after[col].dtype):
            type_changed += 1

    return {
        "renamed": renamed,
        "type_changed": type_changed,
        "added": added,
        "removed": removed,
    }


if __name__ == "__main__":
    render()
