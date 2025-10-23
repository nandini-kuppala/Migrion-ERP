# Migrion - Deployment Guide

## 🚀 Deploy to Streamlit Cloud (Recommended - FREE)

Streamlit Cloud provides free hosting for Streamlit apps directly from GitHub.

### Prerequisites

1. ✅ GitHub account
2. ✅ Gemini API Key (get from https://ai.google.dev/ - FREE)
3. ✅ MongoDB Atlas URI (optional, get from https://www.mongodb.com/cloud/atlas)

### Step 1: Push to GitHub

The project is already configured for Git deployment. Run these commands:

```bash
# Initialize git repository (if not already done)
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit - Migrion ERP Migration Platform"

# Set main branch
git branch -M main

# Add your GitHub repository
git remote add origin git@github.com:nandini-kuppala/Migrion-ERP.git

# Push to GitHub
git push -u origin main
```

### Step 2: Deploy on Streamlit Cloud

1. **Sign in to Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io/)
   - Click "Continue with GitHub"
   - Authorize Streamlit

2. **Create New App**
   - Click "New app" button
   - Repository: `nandini-kuppala/Migrion-ERP`
   - Branch: `main`
   - Main file path: `app.py`
   - Click "Deploy!"

3. **Configure Secrets**
   - Before the app starts, click "Advanced settings"
   - Or after deployment, click the app menu → "Settings" → "Secrets"
   - Add your secrets in TOML format:

   ```toml
   GEMINI_API_KEY = "your_actual_gemini_api_key"
   MONGODB_URI = "mongodb+srv://user:password@cluster.mongodb.net/"
   ```

4. **Wait for Deployment**
   - Streamlit Cloud will install dependencies
   - Initial deployment takes 2-5 minutes
   - Your app will be live at: `https://your-app-name.streamlit.app`

### Step 3: Configure MongoDB (Optional)

If you want to use the Migration Execution feature:

1. **Create MongoDB Atlas Cluster** (FREE)
   - Sign up at https://www.mongodb.com/cloud/atlas/register
   - Create free M0 cluster
   - Create database user
   - Whitelist IP: `0.0.0.0/0` (allow from anywhere)
   - Get connection string

2. **Add to Streamlit Secrets**
   - In Streamlit Cloud app settings → Secrets
   - Add `MONGODB_URI` with your connection string

### Step 4: Verify Deployment

1. **Test the App**
   - Visit your app URL
   - Try loading demo data
   - Navigate through pages
   - Test AI features

2. **Check Logs**
   - Click "Manage app" → "Logs"
   - Verify no errors
   - Check API connections

---

## 🔒 Managing Secrets

### Local Development (.env file)

For local development, use `.env` file:

```bash
# Create .env file
GEMINI_API_KEY=your_key_here
MONGODB_URI=mongodb+srv://user:password@cluster.mongodb.net/
```

### Streamlit Cloud (Secrets Management)

For production, use Streamlit secrets:

1. Go to app settings
2. Click "Secrets"
3. Add in TOML format:

```toml
GEMINI_API_KEY = "your_key"
MONGODB_URI = "your_uri"
```

### How It Works

The app automatically detects the environment:
- **Local**: Uses `.env` file
- **Streamlit Cloud**: Uses `st.secrets`

Code in `src/utils/config.py`:
```python
def get_secret(key: str, default: str = "") -> str:
    """Get secret from Streamlit secrets or environment variables."""
    if HAS_STREAMLIT_SECRETS:
        return st.secrets.get(key, default)
    return os.getenv(key, default)
```

---

## 📋 Deployment Checklist

Before deploying, verify:

- [ ] `.gitignore` excludes `.env`, `venv/`, `__pycache__/`
- [ ] `requirements.txt` is up to date
- [ ] All code is committed to Git
- [ ] Repository is pushed to GitHub
- [ ] Gemini API key is ready
- [ ] MongoDB URI is configured (if using migration feature)
- [ ] Demo data is included in repository

---

## 🎯 Post-Deployment

### Update Your App

```bash
# Make changes to your code
git add .
git commit -m "Your update message"
git push

# Streamlit Cloud auto-deploys on push!
```

### Monitor Usage

1. **Streamlit Cloud Dashboard**
   - View app analytics
   - Check resource usage
   - Monitor uptime

2. **Gemini API Usage**
   - Check usage at https://ai.google.dev/
   - Free tier: 15 req/min, 1,500 req/day

3. **MongoDB Atlas**
   - Monitor at https://cloud.mongodb.com/
   - Free tier: 512MB storage

---

## 🐛 Troubleshooting Deployment

### App Won't Start

**Check Logs:**
- Streamlit Cloud → Manage app → Logs
- Look for import errors or missing dependencies

**Common Issues:**
1. Missing secrets → Add in Streamlit settings
2. Dependency conflicts → Check `requirements.txt`
3. File path issues → Use relative paths

### Secrets Not Working

**Verify Format:**
- Must be valid TOML
- No quotes around keys
- Use quotes around values
- Example:
  ```toml
  KEY = "value"
  ```

**Check Access:**
- Secrets are case-sensitive
- Use exact key names
- Test with simple print (remove before production!)

### Performance Issues

**Optimize:**
1. Use `@st.cache_data` for data loading
2. Limit file sizes (< 200MB recommended)
3. Use batching for large datasets
4. Monitor Gemini API rate limits

---

## 📊 Resource Limits

### Streamlit Cloud (Free Tier)

- **Resources**: 1 GB RAM, shared CPU
- **Apps**: Up to 3 public apps
- **Storage**: 1 GB per app
- **Uptime**: Auto-sleeps after inactivity, wakes on visit

### Gemini API (Free Tier)

- **Rate Limit**: 15 requests/minute
- **Daily Limit**: 1,500 requests/day
- **Cost**: FREE forever
- **Token Limit**: 8K output tokens

### MongoDB Atlas (Free Tier)

- **Storage**: 512 MB
- **RAM**: Shared
- **Backups**: Not included
- **Regions**: Limited selection

---

## 🔐 Security Best Practices

1. **Never commit secrets**
   - Use `.gitignore` for `.env`
   - Use Streamlit secrets in cloud

2. **API Key Security**
   - Rotate keys periodically
   - Don't share publicly
   - Use environment-specific keys

3. **MongoDB Security**
   - Use strong passwords
   - Limit IP whitelist when possible
   - Use database-specific users

4. **Access Control**
   - Make app public or private
   - Configure in Streamlit settings
   - Add authentication if needed

---

## 🌐 Custom Domain (Optional)

Streamlit Cloud supports custom domains:

1. Go to app settings
2. Click "Custom domain"
3. Follow instructions to configure DNS
4. Example: `migrion.yourcompany.com`

---

## 📞 Support

### Streamlit Cloud Issues
- Docs: https://docs.streamlit.io/streamlit-community-cloud
- Forum: https://discuss.streamlit.io/
- Status: https://streamlitstatus.com/

### Gemini API Issues
- Docs: https://ai.google.dev/docs
- Support: Google AI Studio

### MongoDB Atlas Issues
- Docs: https://docs.mongodb.com/
- Support: https://support.mongodb.com/

---

## ✅ Production Checklist

Before going live:

- [ ] Test all features thoroughly
- [ ] Verify secrets are configured
- [ ] Check API rate limits
- [ ] Test demo data loading
- [ ] Verify MongoDB connection
- [ ] Review error handling
- [ ] Test on mobile devices
- [ ] Monitor logs for issues
- [ ] Set up custom domain (optional)
- [ ] Add analytics (optional)

---

**Your Migrion app is now live! 🎉**

Share your app URL:
`https://your-app-name.streamlit.app`

Enjoy automated ERP data migration! 🚀
