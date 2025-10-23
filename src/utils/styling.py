"""Custom CSS and styling for Streamlit app."""
import streamlit as st

def apply_custom_css():
    """Apply custom CSS styling to the Streamlit app."""
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Global Styles */
    * {
        font-family: 'Inter', sans-serif;
    }

    /* Main container */
    .main {
        background: linear-gradient(135deg, #0E1117 0%, #1a1f2e 100%);
    }

    /* Headers */
    h1, h2, h3 {
        color: #FAFAFA !important;
        font-weight: 600 !important;
        letter-spacing: -0.5px;
    }

    h1 {
        font-size: 2.5rem !important;
        margin-bottom: 0.5rem !important;
        background: linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    /* Cards */
    .stCard {
        background: linear-gradient(135deg, #1C2333 0%, #2D3748 100%);
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid rgba(59, 130, 246, 0.2);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }

    .stCard:hover {
        border-color: rgba(59, 130, 246, 0.5);
        box-shadow: 0 8px 12px rgba(59, 130, 246, 0.2);
        transform: translateY(-2px);
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #2E5EAA 0%, #3B82F6 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.5rem;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(59, 130, 246, 0.3);
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #3B82F6 0%, #60A5FA 100%);
        box-shadow: 0 4px 8px rgba(59, 130, 246, 0.5);
        transform: translateY(-1px);
    }

    /* Input fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        background-color: #1C2333;
        color: #FAFAFA;
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 8px;
        padding: 0.6rem;
        transition: all 0.3s ease;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #3B82F6;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: #1C2333;
        border-radius: 8px;
        color: #FAFAFA;
        padding: 0.6rem 1.2rem;
        border: 1px solid rgba(59, 130, 246, 0.2);
        transition: all 0.3s ease;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(59, 130, 246, 0.1);
        border-color: rgba(59, 130, 246, 0.5);
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #2E5EAA 0%, #3B82F6 100%);
        border-color: #3B82F6;
    }

    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 600 !important;
        color: #3B82F6 !important;
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.9rem !important;
        color: #9CA3AF !important;
        font-weight: 500 !important;
    }

    /* Progress bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #2E5EAA 0%, #3B82F6 50%, #60A5FA 100%);
        border-radius: 4px;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1C2333 0%, #0E1117 100%);
        border-right: 1px solid rgba(59, 130, 246, 0.2);
    }

    [data-testid="stSidebar"] .stButton > button {
        width: 100%;
        margin-bottom: 0.5rem;
    }

    /* Expander */
    .streamlit-expanderHeader {
        background-color: #1C2333;
        border-radius: 8px;
        border: 1px solid rgba(59, 130, 246, 0.2);
        transition: all 0.3s ease;
    }

    .streamlit-expanderHeader:hover {
        background-color: rgba(59, 130, 246, 0.1);
        border-color: rgba(59, 130, 246, 0.5);
    }

    /* Success/Error/Warning/Info boxes */
    .stSuccess, .stError, .stWarning, .stInfo {
        border-radius: 8px;
        padding: 1rem;
        border-left: 4px solid;
    }

    .stSuccess {
        background-color: rgba(16, 185, 129, 0.1);
        border-left-color: #10B981;
    }

    .stError {
        background-color: rgba(239, 68, 68, 0.1);
        border-left-color: #EF4444;
    }

    .stWarning {
        background-color: rgba(245, 158, 11, 0.1);
        border-left-color: #F59E0B;
    }

    .stInfo {
        background-color: rgba(59, 130, 246, 0.1);
        border-left-color: #3B82F6;
    }

    /* Data tables */
    .dataframe {
        border: 1px solid rgba(59, 130, 246, 0.2) !important;
        border-radius: 8px;
    }

    .dataframe thead tr th {
        background: linear-gradient(135deg, #2E5EAA 0%, #3B82F6 100%) !important;
        color: white !important;
        font-weight: 600 !important;
        padding: 0.75rem !important;
    }

    .dataframe tbody tr:hover {
        background-color: rgba(59, 130, 246, 0.1) !important;
    }

    /* File uploader */
    [data-testid="stFileUploader"] {
        background-color: #1C2333;
        border: 2px dashed rgba(59, 130, 246, 0.3);
        border-radius: 8px;
        padding: 2rem;
        transition: all 0.3s ease;
    }

    [data-testid="stFileUploader"]:hover {
        border-color: rgba(59, 130, 246, 0.6);
        background-color: rgba(59, 130, 246, 0.05);
    }

    /* Spinner */
    .stSpinner > div {
        border-top-color: #3B82F6 !important;
    }

    /* Custom classes */
    .metric-card {
        background: linear-gradient(135deg, #1C2333 0%, #2D3748 100%);
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid rgba(59, 130, 246, 0.2);
        text-align: center;
        transition: all 0.3s ease;
    }

    .metric-card:hover {
        border-color: rgba(59, 130, 246, 0.5);
        transform: translateY(-2px);
        box-shadow: 0 8px 12px rgba(59, 130, 246, 0.2);
    }

    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.875rem;
        font-weight: 500;
    }

    .status-success {
        background-color: rgba(16, 185, 129, 0.2);
        color: #10B981;
    }

    .status-warning {
        background-color: rgba(245, 158, 11, 0.2);
        color: #F59E0B;
    }

    .status-error {
        background-color: rgba(239, 68, 68, 0.2);
        color: #EF4444;
    }

    .status-info {
        background-color: rgba(59, 130, 246, 0.2);
        color: #3B82F6;
    }

    /* Animation classes */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .fade-in {
        animation: fadeIn 0.5s ease-in;
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }

    .pulse {
        animation: pulse 2s ease-in-out infinite;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    </style>
    """, unsafe_allow_html=True)


def create_metric_card(label: str, value: str, delta: str = None, delta_color: str = "normal"):
    """Create a custom metric card."""
    delta_html = ""
    if delta:
        color = "#10B981" if delta_color == "normal" else "#EF4444" if delta_color == "inverse" else "#9CA3AF"
        delta_html = f'<div style="color: {color}; font-size: 0.9rem; margin-top: 0.5rem;">{delta}</div>'

    return f"""
    <div class="metric-card fade-in">
        <div style="color: #9CA3AF; font-size: 0.9rem; font-weight: 500; margin-bottom: 0.5rem;">{label}</div>
        <div style="color: #3B82F6; font-size: 2rem; font-weight: 600;">{value}</div>
        {delta_html}
    </div>
    """


def create_status_badge(status: str):
    """Create a status badge."""
    status_map = {
        "success": ("✓ Success", "status-success"),
        "completed": ("✓ Completed", "status-success"),
        "warning": ("⚠ Warning", "status-warning"),
        "pending": ("⏳ Pending", "status-info"),
        "error": ("✗ Error", "status-error"),
        "failed": ("✗ Failed", "status-error"),
        "in_progress": ("⟳ In Progress", "status-info"),
    }

    text, css_class = status_map.get(status.lower(), ("• " + status, "status-info"))
    return f'<span class="status-badge {css_class}">{text}</span>'


def create_header(title: str, subtitle: str = ""):
    """Create an animated header."""
    subtitle_html = f'<p style="color: #9CA3AF; font-size: 1.1rem; margin-top: 0.5rem;">{subtitle}</p>' if subtitle else ""

    return f"""
    <div class="fade-in" style="margin-bottom: 2rem;">
        <h1>{title}</h1>
        {subtitle_html}
    </div>
    """
