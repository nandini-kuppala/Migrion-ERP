"""Configuration and environment variables management."""
import os
from pathlib import Path

# Try to load from .env file (for local development)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not required in production

# Try to import streamlit for secrets management (for Streamlit Cloud)
try:
    import streamlit as st
    HAS_STREAMLIT_SECRETS = hasattr(st, 'secrets') and len(st.secrets) > 0
except (ImportError, FileNotFoundError):
    HAS_STREAMLIT_SECRETS = False

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OLIST_DATA_DIR = PROJECT_ROOT / "Olist ecommerce dataset (Brazil)"
SYNTHETIC_DATA_DIR = DATA_DIR / "synthetic"
EXAMPLES_DATA_DIR = DATA_DIR / "examples"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
LOGS_DIR = PROJECT_ROOT / "logs"

# Create directories if they don't exist
for directory in [DATA_DIR, SYNTHETIC_DATA_DIR, EXAMPLES_DATA_DIR, OUTPUT_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# API Keys - Load from Streamlit secrets (production) or .env (local development)
def get_secret(key: str, default: str = "") -> str:
    """Get secret from Streamlit secrets or environment variables."""
    if HAS_STREAMLIT_SECRETS:
        try:
            import streamlit as st
            return st.secrets.get(key, default)
        except Exception:
            pass
    return os.getenv(key, default)

GEMINI_API_KEY = get_secret("GEMINI_API_KEY", "")
MONGODB_URI = get_secret("MONGODB_URI", "")

# Gemini Configuration
GEMINI_MODEL = "gemini-2.0-flash-exp"  # Free tier model
GEMINI_TEMPERATURE = 0.7
GEMINI_MAX_OUTPUT_TOKENS = 8192  # Flash model supports more tokens

# Application Settings
APP_NAME = "Migrion"
APP_SUBTITLE = "Intelligent ERP Data Migration Platform"
APP_VERSION = "1.0.0"

# Migration Settings
MAX_DATA_PREVIEW_ROWS = 100
DEFAULT_BATCH_SIZE = 1000
MAX_RETRY_ATTEMPTS = 3

# Quality Thresholds
MIN_DATA_QUALITY_SCORE = 0.7
MAX_MISSING_PERCENTAGE = 10.0
MAX_DUPLICATE_PERCENTAGE = 5.0

# Example Companies
EXAMPLE_COMPANIES = [
    {
        "name": "Orange League Ventures Technologies",
        "industry": "Technology/SaaS",
        "description": "Mid-sized B2B SaaS company specializing in project management solutions",
        "data_volume": "~250K records",
        "legacy_system": "Custom MySQL Database",
        "target_erp": "Odoo ERP"
    },
    {
        "name": "Olist E-commerce",
        "industry": "E-commerce Marketplace",
        "description": "Brazilian e-commerce platform connecting sellers to marketplaces",
        "data_volume": "~100K orders",
        "legacy_system": "Distributed MySQL",
        "target_erp": "SAP Commerce Cloud"
    }
]
