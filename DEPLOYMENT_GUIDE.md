# 📊 Theme Dashboard - Deployment Guide

This guide explains how to update and deploy your Theme Constituents Dashboard to GitHub Pages.

## 🌐 Live Site

Your dashboard is published at: **https://araroot.github.io/themes/**

---

## 🎯 Quick Start - Which Method Should I Use?

### **Option 1: Manual Download (Simplest)** ⭐ RECOMMENDED FOR GETTING STARTED
- **Best for**: Quick updates, learning the workflow
- **Time**: ~2 minutes
- **Steps**: Download Excel → Run script → Done

### **Option 2: Google Drive Automation (Advanced)**
- **Best for**: Frequent updates, full automation
- **Time**: ~30 min setup, then 30 seconds per update
- **Steps**: One-time Google API setup → Run script → Done

---

## 📋 Prerequisites

1. **Python 3.8+** installed on your machine
2. **Git** configured with your GitHub account

### Install Dependencies

```bash
cd /Users/raviaranke/Desktop/themes
pip install -r requirements.txt
```

---

## 🚀 Option 1: Manual Download Workflow

This is the **simplest and recommended** approach.

### Steps:

1. **Download your Excel file** from Google Drive
   - Go to Google Drive
   - Download `PF_Ranks.xlsx`
   - Save it to: `/Users/raviaranke/Desktop/themes/PF_Ranks.xlsx`

2. **Run the deployment script**
   ```bash
   cd /Users/raviaranke/Desktop/themes
   ./deploy.sh
   ```

3. **Wait for GitHub Pages** (1-2 minutes)
   - Visit https://araroot.github.io/themes/
   - Refresh to see your updates

### What the script does:
- ✅ Checks if Excel file exists
- ✅ Generates beautiful HTML from your data
- ✅ Commits changes to git
- ✅ Pushes to GitHub
- ✅ GitHub Pages automatically rebuilds your site

---

## 🤖 Option 2: Google Drive Automation

Automatically downloads from Google Drive and deploys.

### One-Time Setup:

#### Step 1: Get Google Drive API Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Enable **Google Drive API**:
   - Click "Enable APIs and Services"
   - Search for "Google Drive API"
   - Click "Enable"
4. Create **OAuth 2.0 Credentials**:
   - Go to "Credentials" → "Create Credentials" → "OAuth client ID"
   - Application type: **Desktop app**
   - Name: "Theme Dashboard Deployer"
   - Click "Create"
5. **Download the credentials**:
   - Click the download icon next to your OAuth client
   - Save as `credentials.json` in `/Users/raviaranke/Desktop/themes/`

#### Step 2: Get Your File ID

1. Open your Excel file in Google Drive
2. Click "Share" → "Copy link"
3. Your link looks like: `https://drive.google.com/file/d/1ABC...XYZ/view`
4. Extract the ID: `1ABC...XYZ` (the part between `/d/` and `/view`)

#### Step 3: Configure the Script

Edit `deploy_from_gdrive.py` and update line 21:

```python
GDRIVE_FILE_ID = "1ABC...XYZ"  # Paste your file ID here
```

#### Step 4: First Run (Authentication)

```bash
cd /Users/raviaranke/Desktop/themes
python deploy_from_gdrive.py
```

- A browser window will open
- Sign in to your Google account
- Grant permissions
- A `token.json` file will be saved (keeps you logged in)

### Future Updates:

Just run:
```bash
cd /Users/raviaranke/Desktop/themes
python deploy_from_gdrive.py
```

That's it! The script will:
1. ✅ Download latest Excel from Google Drive
2. ✅ Generate HTML
3. ✅ Commit and push to GitHub
4. ✅ Deploy to GitHub Pages

---

## 🛠️ Manual Workflow (No Scripts)

If you prefer to run commands manually:

```bash
cd /Users/raviaranke/Desktop/themes

# 1. Download Excel file to this directory (manual step)

# 2. Generate HTML
python export_static.py

# 3. Commit and push
git add docs/index.html PF_Ranks.xlsx
git commit -m "Update theme dashboard - $(date '+%Y-%m-%d')"
git push
```

---

## 📁 File Structure

```
themes/
├── PF_Ranks.xlsx              # Your Excel data (not in git due to .gitignore)
├── app.py                     # Streamlit app for local viewing
├── export_static.py           # Generates static HTML
├── deploy.sh                  # Simple deployment script
├── deploy_from_gdrive.py      # Google Drive automated deployment
├── requirements.txt           # Python dependencies
├── credentials.json           # Google API credentials (not in git)
├── token.json                 # Google auth token (not in git)
└── docs/
    └── index.html            # Published to GitHub Pages
```

---

## 🎨 Customization

### Update Styling

Edit the CSS in `export_static.py` (lines 60-190) to customize:
- Colors
- Fonts
- Layout
- Responsive breakpoints

### Change Data Source

Edit line 7 in `app.py` and line 31 in `export_static.py`:
```python
DATA_PATH_DEFAULT = Path("/your/new/path/to/file.xlsx")
```

---

## ❓ Troubleshooting

### "PF_Ranks.xlsx not found"
- Make sure the Excel file is in the correct directory
- Check the filename matches exactly (case-sensitive)

### "Permission denied" when running scripts
```bash
chmod +x deploy.sh
chmod +x deploy_from_gdrive.py
```

### Google Drive authentication fails
- Delete `token.json` and try again
- Make sure `credentials.json` is in the correct directory
- Check that Google Drive API is enabled

### HTML looks broken
- Clear your browser cache
- Wait 2-3 minutes for GitHub Pages to rebuild
- Check that `docs/index.html` was generated correctly

### Git push fails
- Make sure you're authenticated with GitHub
- Check: `git remote -v` shows correct repository
- Try: `git pull` before pushing

---

## 💡 Tips

1. **Test locally first**: Run `streamlit run app.py` to view your data interactively
2. **Automate with cron**: Set up a cron job to run `deploy_from_gdrive.py` daily
3. **Check the data**: Always verify your Excel file has the correct sheets: `PF_Ranks` and `theme_park`
4. **Monitor deployments**: Visit https://github.com/araroot/themes/deployments

---

## 🎯 Recommended Workflow

**For most users, I recommend:**

1. **Start with Option 1** (Manual Download) to learn the process
2. **Switch to Option 2** (Google Drive) once you're comfortable
3. **Set up automation** (cron job) if you update frequently

---

## 📞 Need Help?

- Check GitHub Pages deployment status: https://github.com/araroot/themes/deployments
- Review git history: `git log --oneline -10`
- View recent changes: `git diff HEAD~1`

---

**Happy deploying! 🚀**
