# Theme Park - Deployment Guide

## Access From Anywhere via Streamlit Cloud

### Option 1: Deploy to Streamlit Cloud (Recommended)

1. **Push to GitHub** (already done when you push this repo)

2. **Deploy to Streamlit Cloud:**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Select your repository: `araroot/themes`
   - Main file path: `app_interactive.py`
   - Click "Deploy"

3. **Access from anywhere:**
   - Get a URL like: `https://araroot-themes.streamlit.app`
   - Share this URL to access from any device
   - Auto-updates when you push to GitHub

### Option 2: Run Locally

```bash
cd ~/Desktop/themes
streamlit run app_interactive.py
```

## Features

**Interactive Dropdowns:**
- 📊 Current Rank Date - Select current ranking period
- 📊 Previous Rank Date - Select comparison period
- 🏦 Pivot File - Auto-matched to current rank date

**Auto-Matching Logic:**
- End of month rank (day ≥ 25) → Same month pivot
- Mid-month rank (day < 25) → Previous month pivot
- Manual override available

**Data Sources:**
1. **Theme Definitions:** `PF_Ranks.xlsx` (theme_park/tpark_codex)
2. **Rank Data:** `/Users/raviaranke/Desktop/code2026/data/r_outputs/eom_price/*.csv`
3. **BB Flags:** `/Users/raviaranke/Desktop/code2026/data/r_outputs/final/*_pivot_features.xlsx`

## Note on Data Paths

The app currently uses local file paths. For Streamlit Cloud deployment, you'll need to either:
1. Upload data files to the repo
2. Connect to cloud storage (Google Drive, S3, etc.)
3. Use Streamlit secrets for API access

Contact me if you need help with cloud data access setup!
