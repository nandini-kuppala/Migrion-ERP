"""Streamlit page modules for Migrion ERP Migration Platform."""

# Import all page modules for easy access
from . import (
    dashboard,
    project_intake,
    data_quality_page,
    schema_mapping,
    knowledge_graph,
    validation,
    optimizer,
    audit_compliance,
    migration_execution
)

__all__ = [
    'dashboard',
    'project_intake',
    'data_quality_page',
    'schema_mapping',
    'knowledge_graph',
    'validation',
    'optimizer',
    'audit_compliance',
    'migration_execution'
]
