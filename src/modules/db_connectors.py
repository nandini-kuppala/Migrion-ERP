"""Database Connectors Module — SQLAlchemy-based connectors for multiple databases."""
import pandas as pd
from typing import Any, Dict, List, Optional, Tuple
from src.utils.helpers import setup_logger

logger = setup_logger("db_connectors")


class DatabaseConnector:
    """Base database connector using SQLAlchemy."""

    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.engine = None

    def connect(self) -> bool:
        """Establish database connection."""
        try:
            from sqlalchemy import create_engine
            self.engine = create_engine(self.connection_string, pool_pre_ping=True)
            # Test the connection
            with self.engine.connect() as conn:
                conn.execute(self.engine.dialect.statement_compiler(self.engine.dialect, None).__class__.__module__ and conn.connection)
            logger.info(f"Connected to database successfully")
            return True
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            self.engine = None
            return False

    def test_connection(self) -> Tuple[bool, str]:
        """Test database connection and return status message."""
        try:
            from sqlalchemy import create_engine, text
            engine = create_engine(self.connection_string, pool_pre_ping=True)
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.fetchone()
            engine.dispose()
            return True, "Connection successful!"
        except Exception as e:
            return False, f"Connection failed: {str(e)}"

    def get_tables(self) -> List[str]:
        """List all tables in the database."""
        try:
            from sqlalchemy import inspect
            if not self.engine:
                self.connect()
            inspector = inspect(self.engine)
            return inspector.get_table_names()
        except Exception as e:
            logger.error(f"Failed to list tables: {e}")
            return []

    def introspect_schema(self, table_name: str) -> Dict[str, Any]:
        """Extract schema metadata for a table."""
        try:
            from sqlalchemy import inspect
            if not self.engine:
                self.connect()
            inspector = inspect(self.engine)

            columns = inspector.get_columns(table_name)
            pk = inspector.get_pk_constraint(table_name)
            foreign_keys = inspector.get_foreign_keys(table_name)
            indexes = inspector.get_indexes(table_name)

            fields = []
            for col in columns:
                fields.append({
                    "name": col["name"],
                    "type": str(col["type"]),
                    "nullable": col.get("nullable", True),
                    "default": str(col.get("default", "")) if col.get("default") else None,
                    "primary_key": col["name"] in (pk.get("constrained_columns", []) if pk else [])
                })

            return {
                "schema_name": table_name,
                "fields": fields,
                "primary_key": pk.get("constrained_columns", []) if pk else [],
                "foreign_keys": [
                    {
                        "columns": fk["constrained_columns"],
                        "referred_table": fk["referred_table"],
                        "referred_columns": fk["referred_columns"]
                    }
                    for fk in foreign_keys
                ],
                "indexes": [
                    {"name": idx["name"], "columns": idx["column_names"], "unique": idx["unique"]}
                    for idx in indexes
                ]
            }
        except Exception as e:
            logger.error(f"Schema introspection failed: {e}")
            return {"error": str(e)}

    def read_table(self, table_name: str, limit: int = 1000) -> pd.DataFrame:
        """Read table data into a DataFrame."""
        try:
            if not self.engine:
                self.connect()
            query = f"SELECT * FROM {table_name} LIMIT {limit}"
            return pd.read_sql(query, self.engine)
        except Exception as e:
            logger.error(f"Failed to read table {table_name}: {e}")
            return pd.DataFrame()

    def get_row_count(self, table_name: str) -> int:
        """Get total row count for a table."""
        try:
            from sqlalchemy import text
            if not self.engine:
                self.connect()
            with self.engine.connect() as conn:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                return result.scalar()
        except Exception as e:
            logger.error(f"Failed to count rows: {e}")
            return 0

    def introspect_all_tables(self) -> Dict[str, Dict]:
        """Introspect schema for all tables."""
        tables = self.get_tables()
        schemas = {}
        for table in tables:
            schemas[table] = self.introspect_schema(table)
            schemas[table]["row_count"] = self.get_row_count(table)
        return schemas

    def close(self):
        """Close the database connection."""
        if self.engine:
            self.engine.dispose()
            self.engine = None


class PostgreSQLConnector(DatabaseConnector):
    """PostgreSQL-specific connector."""

    def __init__(self, host: str = "localhost", port: int = 5432,
                 database: str = "", user: str = "", password: str = ""):
        connection_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        super().__init__(connection_string)
        self.db_type = "PostgreSQL"


class MySQLConnector(DatabaseConnector):
    """MySQL-specific connector."""

    def __init__(self, host: str = "localhost", port: int = 3306,
                 database: str = "", user: str = "", password: str = ""):
        connection_string = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
        super().__init__(connection_string)
        self.db_type = "MySQL"


class SQLiteConnector(DatabaseConnector):
    """SQLite-specific connector."""

    def __init__(self, database_path: str = ""):
        connection_string = f"sqlite:///{database_path}"
        super().__init__(connection_string)
        self.db_type = "SQLite"


def get_connector(db_type: str, **kwargs) -> DatabaseConnector:
    """Factory function to get the appropriate connector."""
    connectors = {
        "PostgreSQL": PostgreSQLConnector,
        "MySQL": MySQLConnector,
        "SQLite": SQLiteConnector,
    }
    connector_class = connectors.get(db_type)
    if connector_class is None:
        raise ValueError(f"Unsupported database type: {db_type}")
    return connector_class(**kwargs)
