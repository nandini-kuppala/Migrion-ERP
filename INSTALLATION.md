# Migrion - Installation Guide

## System Requirements

- **Operating System**: Windows 10/11, macOS 10.14+, or Linux
- **Python**: 3.8 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Disk Space**: 500MB for application + dependencies
- **Internet**: Required for Gemini API calls

## Step-by-Step Installation

### 1. Verify Python Installation

```bash
python --version
```

Should show Python 3.8 or higher. If not installed:
- **Windows**: Download from [python.org](https://www.python.org/downloads/)
- **macOS**: `brew install python3`
- **Linux**: `sudo apt-get install python3.8`

### 2. Navigate to Project Directory

```bash
cd "C:\Users\knand\OneDrive\Desktop\Final Project"
```

Or on macOS/Linux:
```bash
cd "/path/to/Final Project"
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install approximately 20 packages including:
- Streamlit (web framework)
- Google Generative AI (Gemini)
- Pandas, NumPy (data processing)
- Plotly (visualization)
- PyMongo (database)
- And many more...

**Installation time**: 2-5 minutes depending on internet speed

**Troubleshooting**:
- If `pip` is not found, try `python -m pip install -r requirements.txt`
- On macOS/Linux, you might need `pip3` instead of `pip`
- If permission errors occur on Linux, use `sudo pip install -r requirements.txt`

### 4. Configure Environment Variables

#### Create .env file:

**Windows**:
```bash
copy .env.example .env
notepad .env
```

**macOS/Linux**:
```bash
cp .env.example .env
nano .env
```

#### Add your API keys:

```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
MONGODB_URI=mongodb://localhost:27017/
```

### 5. Get a Gemini API Key (FREE)

1. Visit [https://ai.google.dev/](https://ai.google.dev/)
2. Click **"Get API Key"** button
3. Sign in with your Google account
4. Click **"Create API Key"**
5. Copy the generated key
6. Paste it into your `.env` file

**Note**: The free tier includes:
- 60 requests per minute
- No credit card required
- Perfect for this application

### 6. (Optional) Set Up MongoDB

MongoDB is only needed if you want to test the migration execution feature.

**Option A: Local MongoDB**
1. Download from [mongodb.com/download-center/community](https://www.mongodb.com/try/download/community)
2. Install and start the MongoDB service
3. Use default URI: `mongodb://localhost:27017/`

**Option B: MongoDB Atlas (Cloud - FREE) - RECOMMENDED**
1. Sign up at [mongodb.com/cloud/atlas/register](https://www.mongodb.com/cloud/atlas/register)
2. Click "Build a Database" and select "Free" tier (M0)
3. Choose your cloud provider and region (any will work)
4. Create cluster (takes 1-3 minutes)
5. Create a database user:
   - Click "Database Access" in left menu
   - Click "Add New Database User"
   - Choose "Password" authentication
   - Enter username and password (remember these!)
   - Set role to "Read and write to any database"
6. Add your IP to whitelist:
   - Click "Network Access" in left menu
   - Click "Add IP Address"
   - Click "Allow Access from Anywhere" (for development)
   - Click "Confirm"
7. Get connection string:
   - Click "Database" in left menu
   - Click "Connect" on your cluster
   - Choose "Connect your application"
   - Copy the connection string
   - Replace `<password>` with your actual password
   - Example: `mongodb+srv://user:password@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority`
8. Add it to `.env` as `MONGODB_URI`

**Option C: Skip MongoDB**
- You can use all features except migration execution
- Great for testing and exploration

### 7. Generate Example Data

```bash
python src/modules/data_generator.py
```

This creates synthetic data for Orange League Ventures Technologies:
- 5,000 customer records
- 1,200 projects
- 3,500 invoices
- 250 users
- 150 products

**Generation time**: ~5-10 seconds

### 8. Verify Installation

```bash
python verify_setup.py
```

This checks:
- Python version
- All dependencies
- Environment variables
- Directory structure
- Example data

**Expected output**:
```
Migrion - Setup Verification
[1/5] Checking Python Version...
✅ Python version: 3.x.x
[2/5] Checking Dependencies...
✅ streamlit
✅ pandas
... (all packages)
[3/5] Checking Environment Variables...
✅ .env file exists
✅ GEMINI_API_KEY is set
[4/5] Checking Directory Structure...
✅ src/agents/
... (all directories)
[5/5] Checking Data Files...
✅ Orange League data: 5 CSV files
SUCCESS: All checks passed!
```

### 9. Run the Application

**Option A: Using launcher script**

Windows:
```bash
run_migrion.bat
```

macOS/Linux:
```bash
chmod +x run_migrion.sh
./run_migrion.sh
```

**Option B: Direct command**
```bash
streamlit run app.py
```

**Expected output**:
```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
Network URL: http://192.168.x.x:8501
```

### 10. Access the Application

Open your browser and navigate to:
```
http://localhost:8501
```

## Post-Installation

### First-Time Setup

1. **Try the Demo**:
   - Go to Home page
   - Click "Try Demo" tab
   - Load "Orange League Ventures Technologies"
   - Explore all features

2. **Configure Your Project**:
   - Go to "Project Intake"
   - Fill in your organization details
   - Generate a migration plan

3. **Upload Your Data**:
   - Go to "Data Quality"
   - Upload your CSV files
   - Analyze data quality

## Troubleshooting

### Common Issues

#### 1. "streamlit: command not found"

**Solution**:
```bash
python -m streamlit run app.py
```

Or reinstall Streamlit:
```bash
pip install --upgrade streamlit
```

#### 2. "ModuleNotFoundError: No module named 'src'"

**Solution**: Make sure you're in the correct directory
```bash
cd "C:\Users\knand\OneDrive\Desktop\Final Project"
```

#### 3. "GEMINI_API_KEY is not set"

**Solution**: Check that:
1. `.env` file exists in project root
2. `GEMINI_API_KEY=...` is set correctly
3. No quotes around the key
4. No spaces before/after the `=`

#### 4. Import errors or "No module named..."

**Solution**:
```bash
pip install -r requirements.txt --upgrade
```

#### 5. Port 8501 already in use

**Solution**: Use a different port
```bash
streamlit run app.py --server.port 8502
```

#### 6. Slow AI responses

**Solution**: This is normal for the free Gemini tier
- Responses typically take 2-5 seconds
- If timeout occurs, try again
- Check your internet connection

### Advanced Configuration

#### Custom Port

Edit `.streamlit/config.toml`:
```toml
[server]
port = 8502  # Change to your desired port
```

#### Custom Theme

Edit `.streamlit/config.toml` to change colors:
```toml
[theme]
primaryColor="#2E5EAA"  # Change this
backgroundColor="#0E1117"  # And this
```

#### Increase Gemini Timeout

Edit `src/agents/gemini_agent.py`:
```python
GEMINI_TIMEOUT = 30  # Increase from default
```

## Updating

To update Migrion to the latest version:

```bash
git pull  # If using git
pip install -r requirements.txt --upgrade
```

## Uninstallation

To completely remove Migrion:

```bash
# Remove virtual environment (if using one)
deactivate
rm -rf venv

# Remove project directory
rm -rf "Final Project"

# Uninstall packages (optional)
pip uninstall -r requirements.txt -y
```

## Getting Help

If you encounter issues:

1. Check the [README.md](README.md) for detailed documentation
2. Review [QUICKSTART.md](QUICKSTART.md) for quick tips
3. Run `python verify_setup.py` to diagnose issues
4. Check the `logs/` directory for error logs

## Next Steps

After successful installation:

1. Read the [QUICKSTART.md](QUICKSTART.md)
2. Try the demo datasets
3. Explore all 9 pages
4. Upload your own data
5. Generate migration plans

**You're all set! Enjoy Migrion!**
