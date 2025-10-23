"""Migration Execution Page - Execute MongoDB migration with real-time progress."""
import streamlit as st
import pandas as pd
import time
from datetime import datetime
from pymongo import MongoClient
from src.utils.styling import apply_custom_css, create_header, create_status_badge
from src.utils.helpers import init_session_state, get_session_state, set_session_state
from src.utils.config import MONGODB_URI, OLIST_DATA_DIR


def render():
    """Render migration execution page."""
    apply_custom_css()

    st.markdown(create_header(
        "Migration Execution",
        "Execute data migration to MongoDB with real-time monitoring"
    ), unsafe_allow_html=True)

    # Initialize session state
    init_session_state("migration_status", "not_started")
    init_session_state("migration_logs", [])
    init_session_state("migration_stats", {})

    # Configuration section
    st.markdown("### Migration Configuration")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Source Configuration**")

        source_type = st.selectbox(
            "Source Type",
            ["Local CSV Files", "Database Connection", "Sample Data"]
        )

        if source_type == "Local CSV Files":
            uploaded_files = st.file_uploader(
                "Upload CSV Files",
                type=['csv'],
                accept_multiple_files=True
            )
        elif source_type == "Sample Data":
            st.info("Using Olist e-commerce sample dataset")
            uploaded_files = None
        else:
            st.text_input("Database Connection String", type="password")
            uploaded_files = None

    with col2:
        st.markdown("**Target Configuration**")

        # MongoDB configuration
        mongo_uri = st.text_input(
            "MongoDB URI",
            value=MONGODB_URI if MONGODB_URI else "mongodb://localhost:27017/",
            type="password",
            help="MongoDB connection string"
        )

        database_name = st.text_input(
            "Database Name",
            value="migrion",
            help="Target MongoDB database name"
        )

        collection_prefix = st.text_input(
            "Collection Prefix",
            value="erp_",
            help="Prefix for collection names"
        )

    # Migration options
    st.markdown("### Migration Options")

    col3, col4, col5 = st.columns(3)

    with col3:
        batch_size = st.number_input(
            "Batch Size",
            min_value=100,
            max_value=10000,
            value=1000,
            step=100,
            help="Number of records per batch"
        )

    with col4:
        enable_validation = st.checkbox("Enable Validation", value=True)
        create_indexes = st.checkbox("Create Indexes", value=True)

    with col5:
        drop_existing = st.checkbox("Drop Existing Collections", value=False)
        enable_logging = st.checkbox("Enable Detailed Logging", value=True)

    # Test connection button
    st.markdown("---")

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        test_connection = st.button("Test Connection", use_container_width=True)

    with col2:
        preview_data = st.button("Preview Data", use_container_width=True)

    with col3:
        start_migration = st.button(
            "Start Migration",
            type="primary",
            use_container_width=True,
            disabled=get_session_state("migration_status") == "in_progress"
        )

    # Test connection
    if test_connection:
        with st.spinner("Testing MongoDB connection..."):
            success, message = test_mongo_connection(mongo_uri, database_name)
            if success:
                st.success(message)
            else:
                st.error(message)

    # Preview data
    if preview_data:
        if source_type == "Sample Data":
            preview_sample_data()
        elif uploaded_files:
            preview_uploaded_data(uploaded_files)
        else:
            st.warning("Please upload files or select sample data")

    # Start migration
    if start_migration:
        if source_type == "Sample Data":
            execute_migration(
                source_type="sample",
                mongo_uri=mongo_uri,
                database_name=database_name,
                collection_prefix=collection_prefix,
                batch_size=batch_size,
                drop_existing=drop_existing,
                enable_validation=enable_validation,
                create_indexes=create_indexes
            )
        elif uploaded_files:
            execute_migration(
                source_type="uploaded",
                uploaded_files=uploaded_files,
                mongo_uri=mongo_uri,
                database_name=database_name,
                collection_prefix=collection_prefix,
                batch_size=batch_size,
                drop_existing=drop_existing,
                enable_validation=enable_validation,
                create_indexes=create_indexes
            )
        else:
            st.error("Please select a data source")

    # Display migration progress and logs
    display_migration_status()


def test_mongo_connection(uri: str, database: str) -> tuple:
    """Test MongoDB connection."""
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        db = client[database]
        collections = db.list_collection_names()
        client.close()
        return True, f"Connection successful! Database '{database}' is accessible."
    except Exception as e:
        return False, f"Connection failed: {str(e)}"


def preview_sample_data():
    """Preview sample data from Olist dataset."""
    st.markdown("### Sample Data Preview")

    try:
        # Try to load sample data
        sample_files = [
            "olist_orders_dataset.csv",
            "olist_customers_dataset.csv",
            "olist_products_dataset.csv"
        ]

        for filename in sample_files:
            filepath = OLIST_DATA_DIR / filename
            if filepath.exists():
                df = pd.read_csv(filepath)
                with st.expander(f"{filename} ({len(df)} rows)", expanded=False):
                    st.dataframe(df.head(10), use_container_width=True)
            else:
                st.warning(f"File not found: {filename}")

    except Exception as e:
        st.error(f"Error loading sample data: {str(e)}")


def preview_uploaded_data(files):
    """Preview uploaded CSV files."""
    st.markdown("### Uploaded Data Preview")

    for file in files:
        try:
            df = pd.read_csv(file)
            with st.expander(f"{file.name} ({len(df)} rows)", expanded=False):
                st.dataframe(df.head(10), use_container_width=True)
            # Reset file pointer
            file.seek(0)
        except Exception as e:
            st.error(f"Error reading {file.name}: {str(e)}")


def execute_migration(source_type: str, mongo_uri: str, database_name: str,
                      collection_prefix: str, batch_size: int, drop_existing: bool,
                      enable_validation: bool, create_indexes: bool, uploaded_files=None):
    """Execute the migration process."""
    set_session_state("migration_status", "in_progress")
    set_session_state("migration_logs", [])

    # Create placeholders for dynamic updates
    progress_bar = st.progress(0)
    status_text = st.empty()
    metrics_placeholder = st.empty()
    logs_placeholder = st.empty()

    try:
        # Connect to MongoDB
        add_log("Connecting to MongoDB...", "info")
        status_text.text("Connecting to MongoDB...")

        client = MongoClient(mongo_uri)
        db = client[database_name]

        add_log(f"Connected to database: {database_name}", "success")
        progress_bar.progress(10)

        # Get source files
        if source_type == "sample":
            files_to_migrate = get_sample_files()
        else:
            files_to_migrate = [(f.name, pd.read_csv(f)) for f in uploaded_files]

        total_files = len(files_to_migrate)
        total_records = 0
        migrated_records = 0

        # Initialize stats
        stats = {
            "start_time": datetime.now(),
            "total_files": total_files,
            "total_records": 0,
            "migrated_records": 0,
            "failed_records": 0,
            "collections_created": 0
        }

        # Process each file
        for idx, (filename, df) in enumerate(files_to_migrate):
            collection_name = f"{collection_prefix}{filename.replace('.csv', '').replace('_dataset', '')}"

            add_log(f"Processing {filename} ({len(df)} records)...", "info")
            status_text.text(f"Processing {filename}...")

            # Drop existing collection if requested
            if drop_existing and collection_name in db.list_collection_names():
                db[collection_name].drop()
                add_log(f"Dropped existing collection: {collection_name}", "warning")

            collection = db[collection_name]

            # Convert DataFrame to records
            records = df.to_dict('records')
            total_records += len(records)
            stats["total_records"] = total_records

            # Insert in batches
            for i in range(0, len(records), batch_size):
                batch = records[i:i + batch_size]

                try:
                    collection.insert_many(batch)
                    migrated_records += len(batch)
                    stats["migrated_records"] = migrated_records

                    # Update progress
                    overall_progress = 10 + int((idx / total_files) * 80) + int((i / len(records)) * (80 / total_files))
                    progress_bar.progress(min(overall_progress, 90))

                    # Update metrics
                    update_metrics(metrics_placeholder, stats)

                    time.sleep(0.1)  # Small delay for visualization

                except Exception as e:
                    stats["failed_records"] += len(batch)
                    add_log(f"Error inserting batch: {str(e)}", "error")

            # Create indexes if requested
            if create_indexes:
                create_collection_indexes(collection, df.columns.tolist())
                add_log(f"Created indexes for {collection_name}", "info")

            stats["collections_created"] += 1
            add_log(f"Completed {collection_name}: {len(records)} records", "success")

        # Final steps
        progress_bar.progress(95)
        status_text.text("Finalizing migration...")

        # Validation
        if enable_validation:
            add_log("Running post-migration validation...", "info")
            validation_results = validate_migration(db, collection_prefix, stats)
            add_log(f"Validation complete: {validation_results}", "success")

        progress_bar.progress(100)
        status_text.text("Migration completed successfully!")

        stats["end_time"] = datetime.now()
        stats["duration_seconds"] = (stats["end_time"] - stats["start_time"]).total_seconds()

        set_session_state("migration_status", "completed")
        set_session_state("migration_stats", stats)

        add_log(f"Migration completed in {stats['duration_seconds']:.2f} seconds", "success")

        client.close()

    except Exception as e:
        add_log(f"Migration failed: {str(e)}", "error")
        status_text.text(f"Migration failed: {str(e)}")
        set_session_state("migration_status", "failed")


def get_sample_files() -> list:
    """Get sample files for migration."""
    files = []

    sample_files = [
        "olist_orders_dataset.csv",
        "olist_customers_dataset.csv",
        "olist_order_items_dataset.csv"
    ]

    for filename in sample_files:
        filepath = OLIST_DATA_DIR / filename
        if filepath.exists():
            df = pd.read_csv(filepath)
            files.append((filename, df))

    return files


def create_collection_indexes(collection, columns: list):
    """Create indexes for collection."""
    # Create index on id-like fields
    for col in columns:
        if 'id' in col.lower():
            try:
                collection.create_index(col)
            except:
                pass


def validate_migration(db, collection_prefix: str, stats: dict) -> str:
    """Validate migration results."""
    collections = [c for c in db.list_collection_names() if c.startswith(collection_prefix)]

    total_docs = sum(db[col].count_documents({}) for col in collections)

    if total_docs == stats["migrated_records"]:
        return f"All {total_docs} records validated successfully"
    else:
        return f"Warning: Expected {stats['migrated_records']}, found {total_docs}"


def add_log(message: str, level: str = "info"):
    """Add log message to session state."""
    logs = get_session_state("migration_logs", [])
    logs.append({
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "level": level,
        "message": message
    })
    set_session_state("migration_logs", logs)


def update_metrics(placeholder, stats: dict):
    """Update migration metrics display."""
    with placeholder.container():
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Files Processed", stats.get("collections_created", 0))

        with col2:
            st.metric("Records Migrated", f"{stats.get('migrated_records', 0):,}")

        with col3:
            st.metric("Failed Records", stats.get("failed_records", 0))

        with col4:
            if "start_time" in stats:
                elapsed = (datetime.now() - stats["start_time"]).total_seconds()
                st.metric("Elapsed Time", f"{elapsed:.1f}s")


def display_migration_status():
    """Display current migration status and logs."""
    status = get_session_state("migration_status")

    if status == "not_started":
        return

    st.markdown("---")
    st.markdown("### Migration Status")

    # Status badge
    if status == "completed":
        st.success("Migration completed successfully!")
    elif status == "in_progress":
        st.info("Migration in progress...")
    elif status == "failed":
        st.error("Migration failed!")

    # Statistics
    stats = get_session_state("migration_stats", {})

    if stats:
        st.markdown("### Migration Statistics")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Files", stats.get("total_files", 0))

        with col2:
            st.metric("Total Records", f"{stats.get('total_records', 0):,}")

        with col3:
            st.metric("Migrated", f"{stats.get('migrated_records', 0):,}")

        with col4:
            st.metric("Failed", stats.get("failed_records", 0))

        if "duration_seconds" in stats:
            col5, col6, col7, col8 = st.columns(4)

            with col5:
                st.metric("Duration", f"{stats['duration_seconds']:.2f}s")

            with col6:
                records_per_sec = stats["migrated_records"] / stats["duration_seconds"] if stats["duration_seconds"] > 0 else 0
                st.metric("Records/sec", f"{records_per_sec:.1f}")

            with col7:
                success_rate = (stats["migrated_records"] / stats["total_records"] * 100) if stats["total_records"] > 0 else 0
                st.metric("Success Rate", f"{success_rate:.1f}%")

            with col8:
                st.metric("Collections", stats.get("collections_created", 0))

    # Logs
    logs = get_session_state("migration_logs", [])

    if logs:
        st.markdown("### Migration Logs")

        log_container = st.container()

        with log_container:
            for log in reversed(logs[-20:]):  # Show last 20 logs
                level = log.get("level", "info")

                if level == "error":
                    st.error(f"[{log['timestamp']}] {log['message']}")
                elif level == "warning":
                    st.warning(f"[{log['timestamp']}] {log['message']}")
                elif level == "success":
                    st.success(f"[{log['timestamp']}] {log['message']}")
                else:
                    st.info(f"[{log['timestamp']}] {log['message']}")


if __name__ == "__main__":
    render()
