# 🔄 Refresh Button Setup Guide

Your dashboard now has a **Refresh Data** button that automatically updates from Google Drive!

## 🎯 How It Works

1. Click the **🔄 Refresh Data** button on your site
2. It takes you to GitHub Actions
3. Click **Run workflow** → **Run workflow**
4. GitHub automatically:
   - Downloads latest Excel from Google Drive
   - Generates new HTML
   - Deploys to GitHub Pages
5. Refresh your site in 1-2 minutes to see updates!

---

## ⚙️ One-Time Setup (Required)

### Step 1: Make Your Google Drive File Public (Viewer Access)

1. Open `PF_Ranks.xlsx` in Google Drive
2. Click **Share** (top right)
3. Under "General access", select **Anyone with the link** → **Viewer**
4. Click **Copy link**
5. Your link looks like: `https://drive.google.com/file/d/1ABC...XYZ/view`
6. Extract the **File ID**: `1ABC...XYZ` (between `/d/` and `/view`)

### Step 2: Add File ID to GitHub Secrets

1. Go to your repository: https://github.com/araroot/themes
2. Click **Settings** (top menu)
3. Click **Secrets and variables** → **Actions** (left sidebar)
4. Click **New repository secret**
5. Name: `GDRIVE_FILE_ID`
6. Value: Paste your File ID (e.g., `1ABC...XYZ`)
7. Click **Add secret**

### Step 3: Test the Workflow

1. Go to https://github.com/araroot/themes/actions
2. Click **Update Dashboard from Google Drive** (left sidebar)
3. Click **Run workflow** → **Run workflow**
4. Watch it run (takes ~1 minute)
5. Check your site: https://araroot.github.io/themes/

---

## 🚀 Using the Refresh Button

### From Your Dashboard Site:

1. Visit https://araroot.github.io/themes/
2. Click **🔄 Refresh Data** (top right)
3. On GitHub Actions page, click **Run workflow** → **Run workflow**
4. Wait 1-2 minutes
5. Refresh your site to see updates

### Directly from GitHub:

1. Go to https://github.com/araroot/themes/actions/workflows/update-dashboard.yml
2. Click **Run workflow** → **Run workflow**
3. That's it!

---

## 🔐 Security Note

**Why make the file "Anyone with the link"?**
- GitHub Actions needs to download the file
- This is the simplest method that doesn't require OAuth setup
- The file ID is stored as a secret (not publicly visible)
- Only people who know the exact URL can access it

**If you need stricter security:**
- Use the `deploy_from_gdrive.py` script locally instead
- Or set up Google Service Account (more complex)

---

## 🤖 Bonus: Automate Daily Updates (Optional)

Want the dashboard to auto-update every day? Edit `.github/workflows/update-dashboard.yml`:

Add this after line 3:

```yaml
on:
  # Runs every day at 9 AM UTC (adjust to your timezone)
  schedule:
    - cron: '0 9 * * *'

  workflow_dispatch:
  repository_dispatch:
    types: [update-dashboard]
```

Now your dashboard will automatically refresh daily!

---

## 📊 Workflow Status

Check deployment status:
- **Actions**: https://github.com/araroot/themes/actions
- **Deployments**: https://github.com/araroot/themes/deployments
- **Live Site**: https://araroot.github.io/themes/

---

## ❓ Troubleshooting

### "Error: Failed to download file"
- Check that your Google Drive file is set to "Anyone with the link"
- Verify the File ID is correct in GitHub Secrets
- Make sure the secret is named exactly `GDRIVE_FILE_ID`

### Workflow fails with permission error
- Go to Settings → Actions → General
- Under "Workflow permissions", enable "Read and write permissions"
- Click Save

### Button doesn't appear on site
- Wait for GitHub Pages to rebuild (2-3 minutes)
- Clear your browser cache
- Check that the latest commit updated `docs/index.html`

### Site shows old data after refresh
- Check workflow completed successfully in Actions tab
- Wait 2-3 minutes for GitHub Pages to rebuild
- Do a hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)

---

## 🎉 You're All Set!

Your dashboard now has:
- ✅ Beautiful modern design
- ✅ One-click refresh from Google Drive
- ✅ Automatic deployment via GitHub Actions
- ✅ Mobile-responsive layout

Just update your Excel in Google Drive, click the refresh button, and you're done! 🚀
