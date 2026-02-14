# How to Update Dashboard

## Quick Update Process

1. **Download new files** to `~/Downloads/`:
   - `PF_Ranks.xlsx` (latest portfolio ranks)
   - `MonYY_pivot_features.xlsx` (e.g., `Feb26_pivot_features.xlsx`)

2. **Run the update script:**
   ```bash
   cd ~/Desktop/themes
   python update_and_push.py
   ```

3. **Done!** The script will:
   - Copy files from Downloads to themes folder
   - Regenerate static HTML dashboard
   - Commit changes to git
   - Push to GitHub
   - Deploy automatically via GitHub Pages

## What the Script Does

The `update_and_push.py` script automates everything:

```
UPDATING DASHBOARD FILES
✓ Copied PF_Ranks.xlsx from Downloads
✓ Copied Feb26_pivot_features.xlsx from Downloads

FILES BEING USED:
PF_Ranks: PF_Ranks.xlsx
Pivot File: Feb26_pivot_features.xlsx

REGENERATING STATIC HTML
✓ Static HTML regenerated successfully
  Using pivot file: Feb26_pivot_features.xlsx (Feb26)

COMMITTING AND PUSHING TO GITHUB
✓ Changes committed
✓ Pushed to GitHub successfully

✓ DASHBOARD UPDATE COMPLETE!
```

## File Locations

### Input Files (Downloads)
- `~/Downloads/PF_Ranks.xlsx` - Portfolio ranks data
- `~/Downloads/MonYY_pivot_features.xlsx` - Mutual fund BB signals

### Working Directory
- `~/Desktop/themes/` - Main dashboard directory
- `~/Desktop/themes/docs/index.html` - Generated static dashboard

### GitHub Repository
- Repository: `araroot/themes`
- Live Dashboard: GitHub Pages (auto-deploys on push)

## Manual Steps (if needed)

If you prefer to do it manually:

1. **Copy files:**
   ```bash
   cp ~/Downloads/PF_Ranks.xlsx ~/Desktop/themes/
   cp ~/Downloads/Feb26_pivot_features.xlsx ~/Desktop/themes/
   ```

2. **Regenerate HTML:**
   ```bash
   cd ~/Desktop/themes
   python export_static.py
   ```

3. **Commit and push:**
   ```bash
   git add -A
   git commit -m "Update dashboard data: Feb26"
   git push
   ```

## Dashboard Tabs

The dashboard has 4 tabs:

1. **📈 Ranks** - Portfolio rank data by theme
2. **🏦 MF Moves** - Mutual fund BB signals by theme
3. **🔀 Combined** - Ranks + BB signals (using theme_park)
4. **🎯 Combined (Codex)** - Ranks + BB signals (using tpark_codex)

## Troubleshooting

**Problem:** Pivot file not in Downloads
- Script will use existing pivot file in themes directory
- Warning shown: `⚠ No pivot file in Downloads, using existing: Jan26_pivot_features.xlsx`

**Problem:** PF_Ranks.xlsx not in Downloads
- Script will exit with error
- Download the file and run again

**Problem:** Script fails to push
- Check git credentials
- Ensure you have push access to repository
- Run `git status` to check for issues

## Data Sources

- **PF_Ranks.xlsx** sheets used:
  - `PF_Ranks` - Portfolio symbols
  - `theme_park` - Theme mappings (regular Combined tab)
  - `tpark_codex` - Theme mappings (Codex Combined tab)

- **MonYY_pivot_features.xlsx** sheets used:
  - `Summary Data` - Mutual fund BB values by symbol

## Key Features

- **Auto-detection** of latest pivot file by date
- **Case-insensitive** symbol matching (all uppercase internally)
- **Theme normalization** for consistent display
- **Symbol ordering** - Portfolio symbols shown first, then others
- **BB format** - Shows last 3 values: `SYMBOL (val1, val2, val3)`
- **Delta arrows** - Rank changes shown with ▲▼ indicators
