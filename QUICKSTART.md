# 🚀 Migrion - Quick Start Guide

Get up and running with Migrion in 5 minutes!

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install all required packages including Streamlit, Gemini AI, Plotly, and MongoDB drivers.

## Step 2: Set Up Environment Variables

1. Copy the example environment file:
   ```bash
   copy .env.example .env
   ```

2. Edit `.env` and add your Gemini API key:
   ```
   GEMINI_API_KEY=your_actual_key_here
   MONGODB_URI=mongodb://localhost:27017/
   ```

### Getting a Gemini API Key (FREE)

1. Go to [https://ai.google.dev/](https://ai.google.dev/)
2. Click "Get API Key"
3. Sign in with your Google account
4. Create a new API key
5. Copy and paste it into your `.env` file

**Note**: The free tier includes 60 requests per minute, which is more than enough for this application!

## Step 3: Run the Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## Step 4: Try the Demo

1. On the **Home** page, go to the **"Try Demo"** tab
2. Click **"Load Demo"** for **Orange League Ventures Technologies**
3. This loads 250K+ records of realistic synthetic data

## Step 5: Explore the Features

### 📋 Project Intake
- Navigate to **Project Intake** from the sidebar
- View the pre-loaded demo company information
- Click **"Generate Migration Plan"** to see AI-powered planning

### 📊 Data Quality Analysis
- Go to **Data Quality** page
- Click **"Load Sample Data"** to analyze Orange League customer data
- View quality metrics, visualizations, and AI insights

### 🗺️ Schema Mapping
- Navigate to **Schema Mapping**
- Load sample source and target schemas
- Click **"Generate Mappings with AI"** to see intelligent field matching

### 🕸️ Knowledge Graph
- Visit **Knowledge Graph** page
- Select "ERP Entities" graph type
- View interactive relationship visualization

### ⚡ Migration Optimizer
- Go to **Optimizer** page
- Input your constraints (data size, downtime, users, budget)
- Get AI-recommended migration strategies

### 🚀 MongoDB Migration
- Navigate to **Migration Execution**
- Load sample source data
- Configure MongoDB connection (optional)
- Run a dry-run migration with progress tracking

### 📈 Dashboard
- View the **Dashboard** for overall project metrics
- See quality scores, progress charts, and activity feed

## Common Use Cases

### Use Case 1: Analyze Your Own Data

1. Go to **Data Quality** page
2. Click **"Upload CSV File"**
3. Select your CSV file
4. Click **"Analyze Data"**
5. Review quality metrics and recommendations

### Use Case 2: Map Custom Schemas

1. Navigate to **Schema Mapping**
2. Choose **"Manual JSON Input"**
3. Paste your source schema JSON
4. Paste your target schema JSON
5. Click **"Generate Mappings with AI"**
6. Review and edit mappings as needed
7. Export to JSON or SQL

### Use Case 3: Plan a Migration

1. Go to **Project Intake**
2. Click **"Create New Project"**
3. Fill in organization details:
   - Company name, industry, size
   - Legacy system (e.g., "MySQL Database")
   - Target ERP (e.g., "Odoo", "SAP", "Oracle")
   - Data volume estimate
   - Constraints (downtime, users, budget)
4. Click **"Generate Migration Plan"**
5. Review the AI-generated plan with phases, risks, and timeline

## Tips for Best Results

### 🎯 Gemini API Tips
- **Completely FREE** - Gemini 2.0 Flash never requires payment
- The free tier has rate limits (15 requests/minute, 1,500/day)
- If you see rate limit errors, wait a few seconds
- Prompts are optimized to use minimal tokens
- Flash model is faster than the old Pro model

### 📊 Data Quality Tips
- Upload CSV files with headers
- Recommended max size: 200MB
- For larger files, use sampling or batching

### 🗺️ Mapping Tips
- Provide sample data for better mapping accuracy
- Review AI-generated confidence scores
- Edit mappings before export

### 🚀 Migration Tips
- Always run a dry-run first
- Test with small batches (100-1000 records)
- Validate data before and after migration
- Keep backups of source data

## Example Workflow

**Complete Migration Planning in 10 Minutes:**

1. **Home** → Load "Orange League Ventures" demo (30 seconds)
2. **Project Intake** → Generate migration plan (1 minute)
3. **Data Quality** → Analyze customer data (2 minutes)
4. **Schema Mapping** → Generate and review mappings (2 minutes)
5. **Knowledge Graph** → Visualize relationships (1 minute)
6. **Optimizer** → Get strategy recommendations (1 minute)
7. **Audit & Compliance** → Review PII and GDPR (1 minute)
8. **Migration Execution** → Dry-run migration (2 minutes)
9. **Dashboard** → Review overall status (30 seconds)

## Troubleshooting

### "GEMINI_API_KEY is not set"
✅ **Solution**: Create `.env` file and add your API key

### "Module not found" errors
✅ **Solution**: Run `pip install -r requirements.txt`

### MongoDB connection fails
✅ **Solution**: MongoDB is optional! You can skip migration execution or use a cloud MongoDB (e.g., MongoDB Atlas free tier)

### Streamlit won't start
✅ **Solution**:
- Check Python version: `python --version` (must be 3.8+)
- Reinstall Streamlit: `pip install --upgrade streamlit`

### AI responses are slow
✅ **Solution**: This is normal for the free Gemini tier. Responses typically take 2-5 seconds.

## Next Steps

- ✅ Explore all 9 pages
- ✅ Try uploading your own CSV data
- ✅ Generate migration plans for your use case
- ✅ Export reports and mappings
- ✅ Customize the theme in `.streamlit/config.toml`

## Need Help?

- 📖 Read the full [README.md](README.md)
- 💬 Check the code comments
- 🐛 Report issues on GitHub

---

**You're all set! Happy migrating! 🎉**
