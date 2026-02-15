# 🐱 Theme Park - Interactive Dashboard

## Overview

The interactive dashboard provides dropdown controls for selecting different rank dates and pivot files. Access it from anywhere via Streamlit Cloud or run it locally.

## Quick Start - Local

```bash
cd ~/Desktop/themes
streamlit run app_interactive.py
```

## Deploy to Streamlit Cloud (Access from Anywhere)

1. **Push to GitHub** (data files already included)

2. **Deploy to Streamlit Cloud:**
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Repository: `araroot/themes`
   - Main file: `app_interactive.py`
   - Click "Deploy"

3. **Access from anywhere:**
   - Get URL like: `https://araroot-themes.streamlit.app`
   - Bookmark and share the URL
   - Auto-updates when you push to GitHub

## Features

### Three Interactive Dropdowns

1. **📊 Current Rank Date**
   - Select the current ranking period
   - Default: Latest available (e.g., 2026-02-13)
   - Automatically matches appropriate pivot file

2. **📊 Previous Rank Date**
   - Select the comparison period for rank deltas
   - Default: Second latest (e.g., 2026-01-30)
   - Used to calculate ▲▼ changes

3. **🏦 Pivot File**
   - Select MF data period for BB flags
   - Auto-selected based on current rank date
   - Can manually override if needed

### Auto-Matching Logic

The pivot file automatically matches to the current rank date:

- **End of month** (day ≥ 25) → Same month pivot
  - Rank: 2026-01-30 → Pivot: 2026-01

- **Mid-month** (day < 25) → Previous month pivot
  - Rank: 2026-02-13 → Pivot: 2026-01

You can manually override the auto-selection if needed.

## Data Architecture

### New Data Sources (Changed from Previous Version)

1. **Theme Definitions** (theme mappings only)
   - Source: `PF_Ranks.xlsx` (tpark_codex sheet)
   - Purpose: Define which symbols belong to which themes

2. **Rank Data** (rank changes and deltas)
   - Source: `/data/eom_price/out_DD-Mon-YY.csv`
   - Contains: Percentile ranks (ptile column)
   - Example: `out_13-Feb-26.csv`, `out_30-Jan-26.csv`

3. **BB Flags** (mutual fund bucket band signals)
   - Source: `/data/final/MonYY_pivot_features.xlsx`
   - Contains: BB values for last 3 periods
   - Example: `Jan26_pivot_features.xlsx`

### What Changed

**Previously (Static Dashboard):**
- Used PF_Ranks.xlsx for both themes AND rank data
- Limited to dates available in PF_Ranks

**Now (Interactive Dashboard):**
- PF_Ranks.xlsx ONLY for theme definitions
- Rank data from eom_price CSV files (more dates available)
- Pivot files for BB flags
- Dropdowns to select any date combination

## Updating Data

### For Local Development

1. **Add new rank files:**
   ```bash
   cp /path/to/new/out_DD-Mon-YY.csv ~/Desktop/code2026/data/r_outputs/eom_price/
   ```

2. **Add new pivot files:**
   ```bash
   cp /path/to/new/MonYY_pivot_features.xlsx ~/Desktop/code2026/data/r_outputs/final/
   ```

3. **Update theme definitions:**
   ```bash
   cp ~/Downloads/PF_Ranks.xlsx ~/Desktop/themes/data/
   ```

4. **Refresh the app** (Streamlit auto-reloads)

### For Streamlit Cloud Deployment

1. **Copy new data to themes/data:**
   ```bash
   cd ~/Desktop/themes
   python copy_data_for_deployment.py
   ```

2. **Push to GitHub:**
   ```bash
   git add data/
   git commit -m "Update data files"
   git push
   ```

3. **Streamlit Cloud auto-deploys** (takes 1-2 minutes)

## File Structure

```
themes/
├── app_interactive.py          # Interactive Streamlit app
├── data/                        # Data files for deployment
│   ├── eom_price/              # Rank CSV files
│   │   ├── out_13-Feb-26.csv
│   │   ├── out_30-Jan-26.csv
│   │   └── ...
│   ├── final/                  # Pivot files
│   │   ├── Jan26_pivot_features.xlsx
│   │   ├── Dec25_pivot_features.xlsx
│   │   └── ...
│   └── PF_Ranks.xlsx           # Theme definitions
├── copy_data_for_deployment.py # Helper script
└── requirements.txt            # Python dependencies
```

## Comparison: Static vs Interactive

| Feature | Static (GitHub Pages) | Interactive (Streamlit) |
|---------|----------------------|-------------------------|
| **Deployment** | GitHub Pages | Streamlit Cloud |
| **Access** | URL, no login | URL, no login |
| **Data Selection** | Fixed (latest) | Dropdowns (any date) |
| **Updates** | Push to GitHub | Push to GitHub |
| **Load Time** | Instant | ~2 seconds |
| **Best For** | Quick view, mobile | Analysis, comparison |

## Troubleshooting

**App won't start:**
- Check data directories exist: `data/eom_price/`, `data/final/`
- Verify PF_Ranks.xlsx is present
- Check requirements: `pip install -r requirements.txt`

**No data showing:**
- Verify CSV files are in `data/eom_price/`
- Verify pivot files are in `data/final/`
- Check file naming: `out_DD-Mon-YY.csv` and `MonYY_pivot_features.xlsx`

**Streamlit Cloud deployment fails:**
- Ensure data files are committed to repo
- Check requirements.txt is present
- Verify file paths use relative paths (not absolute)

## Performance Tips

- **Caching enabled** - Data loads once then cached
- **Dropdown changes** are instant (cached data)
- **First load** may take 5-10 seconds (loading all files)
- **Subsequent loads** are ~1 second

## Support

For issues or questions:
1. Check this documentation
2. Review HOW_TO_UPDATE.md for static dashboard
3. Check GitHub Issues: `araroot/themes/issues`
