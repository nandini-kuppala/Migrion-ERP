# 🔄 Migrion - Intelligent ERP Data Migration Platform

**Version 1.0.0**

Migrion is a comprehensive Streamlit-based multi-agent system powered by Google Gemini AI that streamlines ERP data migration from planning through execution. It provides end-to-end migration assistance with AI-powered schema mapping, data quality analysis, knowledge graph visualization, validation, optimization, and compliance checking.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32.0-FF4B4B.svg)
![Gemini](https://img.shields.io/badge/Google-Gemini-4285F4.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 🌟 Features

### Core Capabilities

- **🎯 AI-Powered Migration Planning** - Generate comprehensive migration plans with phases, timelines, risk assessments, and resource requirements
- **📊 Data Quality Analysis** - Profile datasets with quality metrics, identify issues, detect PII, and generate recommendations
- **🗺️ Smart Schema Mapping** - Auto-generate field mappings between source and target schemas with confidence scores and transformation logic
- **🕸️ Knowledge Graph Visualization** - Build and visualize entity relationships across ERP systems with interactive network graphs
- **✅ Validation Engine** - AI-suggested validation rules with real-time execution and issue reporting
- **⚡ Migration Optimizer** - Recommend optimal strategies (Big Bang, Phased, Hybrid) based on constraints
- **🛡️ Audit & Compliance** - GDPR/PCI compliance checking, PII detection, and explainable audit trails
- **🚀 MongoDB Migration Simulation** - Real-time migration execution with progress tracking and validation
- **📈 Interactive Dashboard** - Comprehensive overview with metrics, charts, and real-time project status

### AI Agents (Powered by Gemini 2.0 Flash - FREE)

- **PlannerAgent** - Migration plan generation
- **MapperAgent** - Schema mapping and field transformations
- **QualityAgent** - Data quality insights and recommendations
- **ValidationAgent** - Validation rule suggestions
- **OptimizerAgent** - Strategy optimization
- **AuditorAgent** - Compliance and audit analysis

**Using Gemini 2.0 Flash (Experimental)** - The latest free model with:
- ✅ Completely FREE (no credit card required)
- ✅ Faster response times than Gemini Pro
- ✅ Higher token limits (8K output)
- ✅ Better performance on complex tasks

## 🏗️ Architecture

```
Migrion/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variables template
├── .streamlit/
│   └── config.toml                # Streamlit theme configuration
├── src/
│   ├── agents/
│   │   └── gemini_agent.py        # Gemini AI agent implementations
│   ├── modules/
│   │   ├── data_generator.py      # Synthetic data generation
│   │   └── data_quality.py        # Data quality analyzer
│   ├── pages/
│   │   ├── project_intake.py      # Project intake form
│   │   ├── data_quality_page.py   # Quality analysis UI
│   │   ├── schema_mapping.py      # Schema mapping interface
│   │   ├── knowledge_graph.py     # Graph visualization
│   │   ├── validation.py          # Validation UI
│   │   ├── optimizer.py           # Strategy optimizer UI
│   │   ├── audit_compliance.py    # Audit & compliance UI
│   │   ├── migration_execution.py # MongoDB migration UI
│   │   └── dashboard.py           # Overview dashboard
│   └── utils/
│       ├── config.py              # Configuration management
│       ├── helpers.py             # Helper functions
│       └── styling.py             # Custom CSS and UI components
├── data/
│   ├── examples/
│   │   └── orange_league/         # Orange League synthetic data
│   └── synthetic/                 # Generated datasets
├── Olist ecommerce dataset (Brazil)/  # Sample e-commerce data
├── outputs/                       # Exported reports and files
└── logs/                         # Application logs
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Google Gemini API key (free tier available at [ai.google.dev](https://ai.google.dev))
- MongoDB instance (optional, for migration simulation)

### Installation

1. **Clone or download the project**
   ```bash
   cd "Final Project"
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**

   Create a `.env` file in the project root:
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your credentials:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   MONGODB_URI=mongodb://localhost:27017/  # Optional
   ```

   **Get a FREE Gemini API Key:**
   - Visit [Google AI Studio](https://ai.google.dev/)
   - Sign in with your Google account
   - Click "Get API Key" and create a new key
   - Copy the key to your `.env` file
   - **No credit card required!** Completely free to use

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Access the application**

   Open your browser and navigate to `http://localhost:8501`

## 📖 Usage Guide

### Option 1: New Project

1. Navigate to **Home** page
2. Click **"Start New Project"** in the "New Project" tab
3. Fill out the project intake form with your organization details:
   - Company name, industry, size
   - Legacy system and target ERP
   - Data volume estimates
   - Migration constraints (downtime, users, budget)
4. Click **"Generate Migration Plan"** to get AI-powered recommendations
5. Proceed through the workflow:
   - **Data Quality** - Upload and analyze your data
   - **Schema Mapping** - Review and edit AI-generated mappings
   - **Knowledge Graph** - Visualize entity relationships
   - **Validation** - Configure validation rules
   - **Optimizer** - Get strategy recommendations
   - **Audit & Compliance** - Review compliance status
   - **Migration Execution** - Execute migration to MongoDB
   - **Dashboard** - Monitor overall progress

### Option 2: Try Demo

1. Navigate to **Home** page
2. In the "Try Demo" tab, select an example company:
   - **Orange League Ventures Technologies** - SaaS company (250K records)
   - **Olist E-commerce** - Brazilian marketplace (100K orders)
3. Click **"Load Demo"** to pre-populate with realistic data
4. Explore all features with pre-configured datasets

## 🎨 UI Theme

Migrion features a modern, professional dark theme with:
- **Primary Color**: Blue gradient (#2E5EAA → #3B82F6)
- **Background**: Dark gradient (#0E1117 → #1a1f2e)
- **Accent Colors**: Blue shades for emphasis
- **Animations**: Smooth transitions and fade-in effects
- **Interactive Components**: Hover effects and state indicators

## 📊 Example Datasets

### Orange League Ventures Technologies (Synthetic)

Realistic B2B SaaS company data with controlled anomalies:
- **5,000 customers** (10% missing emails, 5% duplicates)
- **1,200 projects** (various statuses and types)
- **3,500 invoices** (payment tracking)
- **250 users** (with PII for compliance testing)
- **150 products/services**

**Location**: `data/examples/orange_league/`

### Olist E-commerce Dataset (Real, Anonymized)

Brazilian e-commerce public dataset:
- **100K orders** from 2016-2018
- Customer, product, seller data
- Payment and shipping information
- Customer reviews

**Location**: `Olist ecommerce dataset (Brazil)/`

## 🤖 AI Agent Examples

### Migration Plan Generation
```python
from src.agents.gemini_agent import PlannerAgent

planner = PlannerAgent()
plan = planner.generate_migration_plan(
    org_info={"company_name": "Acme Corp", "industry": "Technology"},
    legacy_system="MySQL Database",
    target_erp="Odoo ERP",
    data_volume="2.5M rows"
)
```

### Schema Mapping
```python
from src.agents.gemini_agent import MapperAgent

mapper = MapperAgent()
mappings = mapper.generate_mappings(
    source_schema={"fields": [...]},
    target_schema={"fields": [...]},
    sample_data=[{...}, {...}]
)
```

### Quality Analysis
```python
from src.modules.data_quality import DataQualityAnalyzer
from src.agents.gemini_agent import QualityAgent

# Analyze data
analyzer = DataQualityAnalyzer(dataframe, "Customers")
quality_report = analyzer.analyze()

# Get AI insights
quality_agent = QualityAgent()
insights = quality_agent.analyze_quality_report(quality_report)
```

## 🔒 Security & Compliance

### PII Detection
Migrion automatically detects potential PII fields:
- Email addresses
- Phone numbers
- Social Security Numbers
- Dates of birth
- Credit card numbers
- Addresses

### GDPR Compliance
- Right to erasure validation
- Data minimization checks
- Consent tracking recommendations
- Data protection impact assessments

### Audit Trail
Every transformation is logged with:
- Timestamp
- Source and target fields
- Transformation logic
- User/agent responsible
- Compliance flags

## 📦 Dependencies

**Core Framework**
- `streamlit` - Web UI framework
- `pandas` - Data manipulation
- `numpy` - Numerical operations

**AI & ML**
- `google-generativeai` - Gemini 2.0 Flash AI integration (FREE)
- `scikit-learn` - Data validation

**Visualization**
- `plotly` - Interactive charts
- `networkx` - Graph algorithms
- `pyvis` - Network visualization
- `seaborn` - Statistical plots

**Database**
- `pymongo` - MongoDB driver

**Utilities**
- `faker` - Synthetic data generation
- `python-dotenv` - Environment management
- `great-expectations` - Data validation
- `streamlit-option-menu` - Navigation menu

## 🛠️ Development

### Project Structure
- **`src/agents/`** - AI agent implementations
- **`src/modules/`** - Core business logic
- **`src/pages/`** - Streamlit page components
- **`src/utils/`** - Shared utilities and helpers

### Adding New Features

1. **New AI Agent**: Extend `GeminiAgent` class in `src/agents/gemini_agent.py`
2. **New Module**: Create in `src/modules/` and import in pages
3. **New Page**: Create in `src/pages/` and add to `app.py` navigation

### Custom Styling

Modify `src/utils/styling.py` to customize:
- Color schemes
- Component styles
- Animations
- Layouts

## 📈 Performance

- **Gemini 2.0 Flash API**:
  - Completely FREE (no credit card needed)
  - 15 requests per minute (free tier)
  - 1,500 requests per day
  - Faster than previous Gemini Pro model
  - 8K output token limit (2x more than Pro)
- **Data Processing**: Handles datasets up to 10M rows (with proper batching)
- **MongoDB Migration**: Configurable batch sizes (default: 1000 records)
- **UI Responsiveness**: Optimized with caching and session state

## 🐛 Troubleshooting

### "GEMINI_API_KEY is not set"
- Ensure `.env` file exists in project root
- Verify `GEMINI_API_KEY` is properly set
- Restart the Streamlit app

### Import Errors
- Run `pip install -r requirements.txt`
- Check Python version (3.8+ required)

### MongoDB Connection Issues
- Verify MongoDB is running
- Check `MONGODB_URI` in `.env`
- Test connection with MongoDB Compass

### Data Upload Failures
- Check file format (CSV required)
- Verify column headers exist
- Check file size (< 200MB recommended)

## 🗺️ Roadmap

- [ ] Support for additional databases (PostgreSQL, Oracle)
- [ ] Real-time collaboration features
- [ ] Advanced transformation templates
- [ ] CI/CD pipeline integration
- [ ] API endpoints for programmatic access
- [ ] Multi-tenant support
- [ ] Enhanced security with SSO

## 📄 License

MIT License - see LICENSE file for details

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📞 Support

For issues, questions, or feature requests:
- Open an issue on GitHub
- Contact: support@migrion.example.com

## 🙏 Acknowledgments

- **Google Gemini** - AI capabilities
- **Olist** - Sample e-commerce dataset
- **Streamlit** - Web framework
- **Open Source Community** - Various libraries and tools

---

**Built with ❤️ for seamless ERP migrations**

*Migrion - Transform Your Data Migration Journey*
