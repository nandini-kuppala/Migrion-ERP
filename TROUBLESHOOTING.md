# Migrion - Troubleshooting Guide

## Common Issues and Solutions

### ✅ FIXED: "module has no attribute 'show'" Error

**Error Message:**
```
AttributeError: module 'src.pages.project_intake' has no attribute 'show'
```

**Solution:** This has been fixed! The page modules use `render()` instead of `show()`. The app.py file has been updated to call the correct function.

### ✅ FIXED: Buttons Not Working on Home Page

**Problem:** "Start New Project" and "Load Demo" buttons were not responding.

**Solution:** Button interactions have been fixed with proper session state management and unique keys.

### ✅ FIXED: CORS Warning on Startup

**Warning Message:**
```
Warning: the config option 'server.enableCORS=false' is not compatible with 'server.enableXsrfProtection=true'.
```

**Solution:** Streamlit config has been updated to remove the incompatible CORS setting.

---

## Current Setup Checklist

Before running the app, make sure:

1. ✅ **Dependencies Installed**
   ```bash
   pip install -r requirements.txt
   ```

2. ✅ **.env File Created**
   ```bash
   copy .env.example .env  # Windows
   cp .env.example .env    # Mac/Linux
   ```

3. ✅ **Gemini API Key Added to .env**
   ```
   GEMINI_API_KEY=your_actual_key_here
   ```
   Get it from: https://ai.google.dev/

4. ✅ **MongoDB Atlas URI Added to .env** (Optional)
   ```
   MONGODB_URI=mongodb+srv://user:password@cluster.mongodb.net/
   ```

5. ✅ **Synthetic Data Generated**
   ```bash
   python src/modules/data_generator.py
   ```

---

## MongoDB Atlas Setup (Recommended for Migration Execution)

If you want to use the Migration Execution feature, set up MongoDB Atlas (Free):

### Step-by-Step:

1. **Create Free Account**
   - Go to: https://www.mongodb.com/cloud/atlas/register
   - Sign up with Google or email

2. **Create Free Cluster**
   - Click "Build a Database"
   - Select "FREE" (M0 tier)
   - Choose any cloud provider/region
   - Click "Create Cluster" (takes 1-3 minutes)

3. **Create Database User**
   - Left menu: "Database Access"
   - Click "Add New Database User"
   - Authentication: "Password"
   - Username: `migrion_user` (or any name)
   - Password: Create a strong password (save it!)
   - Database User Privileges: "Read and write to any database"
   - Click "Add User"

4. **Whitelist Your IP**
   - Left menu: "Network Access"
   - Click "Add IP Address"
   - Click "Allow Access from Anywhere" (for development)
   - Or enter your specific IP address
   - Click "Confirm"

5. **Get Connection String**
   - Left menu: "Database"
   - Click "Connect" on your cluster
   - Choose "Connect your application"
   - Driver: Python, Version: 3.12 or later
   - Copy connection string
   - It looks like: `mongodb+srv://migrion_user:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority`

6. **Update .env File**
   - Replace `<password>` with your actual password
   - Add to `.env`:
   ```
   MONGODB_URI=mongodb+srv://migrion_user:YourActualPassword@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```

7. **Test Connection**
   - In the app, go to "Migration Execution" page
   - Click "Test Connection"
   - Should show: "✅ Connected to MongoDB successfully!"

---

## How to Use the Application

### 1. Start the Application

```bash
streamlit run app.py
```

Or use the launcher:
```bash
# Windows
run_migrion.bat

# Mac/Linux
chmod +x run_migrion.sh
./run_migrion.sh
```

### 2. Access the App

Open browser: **http://localhost:8501**

### 3. Try the Demo (Recommended First Step)

**On the Home page:**
1. Click the **"🎮 Try Demo"** tab
2. Expand **"Orange League Ventures Technologies"**
3. Click **"Load Demo"** button
4. You'll see: "✅ Loaded Orange League Ventures Technologies demo data!" with balloons!

**Now the demo data is loaded!** You can navigate to any page:
- **Project Intake**: See pre-filled company information
- **Data Quality**: Analyze the demo customer data
- **Schema Mapping**: Try auto-mapping features
- **And more...**

### 4. Or Create Your Own Project

**On the Home page:**
1. Click the **"📝 New Project"** tab
2. Click **"Start New Project"** button
3. This navigates you to the Project Intake page
4. Fill in your organization details
5. Click **"Generate Migration Plan"** to get AI recommendations

---

## Testing Each Feature

### Test Data Quality Analysis

1. Go to **"Data Quality"** page
2. Click **"Load Sample Data"** button
3. Select dataset: "Orange League - Customers"
4. Click **"Analyze Data"**
5. View quality metrics, charts, and AI insights

### Test Schema Mapping

1. Go to **"Schema Mapping"** page
2. Under Source Schema, select **"Use Sample Schema"**
3. Under Target Schema, select **"Use Sample Schema"**
4. Click **"Generate Mappings with AI"**
5. Review the AI-generated field mappings with confidence scores

### Test Migration Execution (Requires MongoDB Atlas)

1. Go to **"Migration Execution"** page
2. Source Configuration:
   - Click **"Load Sample Data"**
   - Select "Orange League - Customers"
3. Target Configuration:
   - MongoDB URI should auto-fill from .env
   - Database Name: `migrion`
   - Collection Name: `customers_demo`
4. Click **"Test Connection"**
5. If successful, click **"Start Migration"**
6. Watch real-time progress with batch processing!

---

## Verifying Your Setup

Run the verification script:

```bash
python verify_setup.py
```

**Expected Output:**
```
============================================================
Migrion - Setup Verification
============================================================

[1/5] Checking Python Version...
✅ Python version: 3.x.x

[2/5] Checking Dependencies...
✅ streamlit
✅ pandas
✅ google.generativeai
... (all packages)

[3/5] Checking Environment Variables...
✅ .env file exists
✅ GEMINI_API_KEY is set
✅ MONGODB_URI is set

[4/5] Checking Directory Structure...
✅ src/agents/
✅ src/modules/
✅ src/pages/
✅ src/utils/
... (all directories)

[5/5] Checking Data Files...
✅ Orange League data: 5 CSV files
✅ Olist data: 8 CSV files

============================================================
SUCCESS: All checks passed! You're ready to run Migrion.

Next steps:
   1. streamlit run app.py
   2. Open http://localhost:8501 in your browser
   3. Try the demo or create a new project
============================================================
```

---

## Gemini 2.0 Flash API - Rate Limits (FREE Forever)

**Free Tier Limits:**
- 15 requests per minute
- 1,500 requests per day
- **No credit card ever needed!**
- Completely free forever

**If you see rate limit errors:**
1. Wait 60 seconds
2. Try again
3. The free tier is more than sufficient for normal use

**Response Times (Flash is Fast!):**
- Typical: 1-3 seconds per AI call (faster than Pro!)
- Complex requests: 3-5 seconds
- Very responsive for a free tier

---

## Page-Specific Issues

### Home Page
- ✅ "Start New Project" button: Now working
- ✅ "Load Demo" buttons: Now working with proper feedback

### Project Intake
- Fill in at least Company Name and Legacy System before generating plan
- AI plan generation takes 5-10 seconds

### Data Quality
- Upload CSV files with headers
- Recommended max file size: 200MB
- For larger files, use sampling

### Schema Mapping
- Provide sample data for better AI mapping accuracy
- Review confidence scores (>0.8 is good)
- Edit mappings before export

### Migration Execution
- MongoDB URI must be valid
- Test connection before migration
- Use small batches (1000 records) for testing
- Check "Validate After Migration" option

---

## Performance Tips

1. **First Load is Slow**: Streamlit caches data after first load
2. **AI Responses**: 2-5 seconds is normal for free Gemini tier
3. **Large Datasets**: Use batching and sampling for files >100MB
4. **MongoDB**: Atlas free tier has 512MB storage limit

---

## Error Messages and Fixes

### "GEMINI_API_KEY is not set"
**Fix:**
1. Check `.env` file exists
2. Verify `GEMINI_API_KEY=your_key` is set
3. No quotes around the key
4. Restart Streamlit app

### "No module named 'src'"
**Fix:**
```bash
# Make sure you're in the project root directory
cd "C:\Users\knand\OneDrive\Desktop\Final Project"
streamlit run app.py
```

### MongoDB Connection Failed
**Fix:**
1. Check MONGODB_URI in .env
2. Verify IP is whitelisted in Atlas
3. Confirm database user credentials are correct
4. Test with: https://www.mongodb.com/docs/drivers/pymongo/

### "ImportError" or "ModuleNotFoundError"
**Fix:**
```bash
pip install -r requirements.txt --upgrade
```

---

## Still Having Issues?

1. **Check logs**: Look in `logs/` directory for error details
2. **Restart Streamlit**: Sometimes Ctrl+C and restart helps
3. **Clear cache**: In browser, clear site data for localhost:8501
4. **Fresh install**:
   ```bash
   pip uninstall -r requirements.txt -y
   pip install -r requirements.txt
   ```

---

## Success Indicators

**Application is working correctly when:**

1. ✅ Streamlit starts without errors
2. ✅ Home page loads with navigation menu
3. ✅ "Load Demo" buttons work and show success message
4. ✅ Project Intake page displays form
5. ✅ Data Quality analysis runs and shows charts
6. ✅ AI agents respond within 10 seconds
7. ✅ MongoDB test connection succeeds (if configured)

---

## Quick Test Workflow

**5-Minute Smoke Test:**

1. Start app: `streamlit run app.py`
2. Home → "Try Demo" → Load Orange League → See balloons ✅
3. Navigate to "Data Quality" → Load Sample → Analyze → See charts ✅
4. Navigate to "Schema Mapping" → Load Sample schemas → Generate → See mappings ✅
5. Navigate to "Dashboard" → See metrics and charts ✅

**If all 5 steps work, your installation is perfect!**

---

## Need More Help?

- 📖 Read [README.md](README.md) for full documentation
- 🚀 Check [QUICKSTART.md](QUICKSTART.md) for quick start
- 📥 Review [INSTALLATION.md](INSTALLATION.md) for detailed setup
- ✅ Run `python verify_setup.py` to diagnose issues

**The application is now fully functional! Enjoy using Migrion!** 🎉
