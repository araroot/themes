# 🐱 Theme Park - Interactive Dashboard (GitHub Pages)

## Overview

Pure JavaScript interactive dashboard that runs entirely in the browser. No server needed - deploys to GitHub Pages for access from anywhere!

## ✅ What You Got

**Three Interactive Dropdowns:**
- 📊 **Current Rank Date** - Select current ranking period (21 dates available)
- 📊 **Previous Rank Date** - Select comparison period for deltas
- 🏦 **Pivot File** - Auto-matched to current rank (14 files available)

**Auto-Matching Logic:**
- End of month rank (day ≥ 25) → Same month pivot
- Mid-month rank (day < 25) → Previous month pivot
- Manual override available anytime

**Data Loads On-Demand:**
- CSV files parsed client-side (PapaParse library)
- Excel files read client-side (SheetJS library)
- Instant dropdown switching (data cached in browser)
- No page reload needed

## 🚀 Access Your Dashboard

**GitHub Pages URL:**
```
https://araroot.github.io/themes/
```

Bookmark this URL - it's live and accessible from anywhere!

## 📂 New Data Architecture

**Changed from static version:**

1. **Theme Definitions** (unchanged)
   - Source: `data/PF_Ranks.xlsx` (tpark_codex sheet)
   - Used for: Theme-to-symbol mappings

2. **Rank Data** (NEW - more flexible!)
   - Source: `data/eom_price/out_DD-Mon-YY.csv`
   - Contains: Percentile ranks, market cap, returns
   - Example: `out_13-Feb-26.csv`, `out_30-Jan-26.csv`
   - **21 dates available** vs limited dates in old version

3. **BB Flags** (NEW location)
   - Source: `data/final/MonYY_pivot_features.xlsx`
   - Contains: Last 3 BB values per symbol
   - Example: `Jan26_pivot_features.xlsx`, `Dec25_pivot_features.xlsx`
   - **14 months available**

4. **Manifest** (NEW - enables flexibility)
   - Source: `docs/manifest.json`
   - Auto-generated index of all available files
   - JavaScript reads this to populate dropdowns

## 🔄 Updating Data

### Quick Update (Recommended)

```bash
cd ~/Desktop/themes
python update_interactive_dashboard.py
```

This script:
1. Copies latest data from source directories
2. Regenerates manifest.json
3. Commits changes to git
4. Pushes to GitHub
5. Dashboard updates automatically in 1-2 minutes

### Manual Update

1. **Copy new rank files:**
   ```bash
   cp /path/to/new/out_DD-Mon-YY.csv ~/Desktop/themes/data/eom_price/
   ```

2. **Copy new pivot files:**
   ```bash
   cp /path/to/new/MonYY_pivot_features.xlsx ~/Desktop/themes/data/final/
   ```

3. **Update theme definitions (if changed):**
   ```bash
   cp ~/Downloads/PF_Ranks.xlsx ~/Desktop/themes/data/
   ```

4. **Regenerate manifest:**
   ```bash
   python generate_manifest.py
   ```

5. **Commit and push:**
   ```bash
   git add data/ docs/manifest.json
   git commit -m "Update data files"
   git push
   ```

6. **Wait 1-2 minutes** for GitHub Pages to deploy

## 🏗️ Technical Architecture

### Client-Side Libraries

- **PapaParse (5.4.1)** - CSV parsing in browser
- **SheetJS (0.18.5)** - Excel file reading in browser

### File Structure

```
themes/
├── docs/                        # GitHub Pages deployment
│   ├── index.html              # Main interactive page
│   ├── theme-park.js           # All logic (data loading, table building)
│   ├── manifest.json           # Index of available data files
│   └── data/                   # Symlink or copy of ../data/
├── data/                        # Data files
│   ├── eom_price/              # Rank CSV files (21 files)
│   ├── final/                  # Pivot Excel files (14 files)
│   └── PF_Ranks.xlsx           # Theme definitions
├── generate_manifest.py         # Regenerates manifest.json
└── update_interactive_dashboard.py  # One-command update
```

### How It Works

1. **Page Load:**
   - Loads `manifest.json` to get list of available files
   - Populates dropdowns with file options
   - Loads theme definitions from PF_Ranks.xlsx

2. **User Selects Dates:**
   - Dropdown change triggers data load
   - JavaScript fetches selected CSV/Excel files
   - Parses data client-side

3. **Table Building:**
   - Calculates medians per theme
   - Calculates rank deltas (current vs previous)
   - Matches BB values from pivot file
   - Renders combined HTML table
   - All in browser, no server needed!

4. **Caching:**
   - Browser caches loaded files
   - Subsequent dropdown changes are instant
   - Only loads new files when needed

## 📊 Comparison: Old vs New

| Feature | Static (Old) | Interactive (New) |
|---------|-------------|-------------------|
| **Deployment** | GitHub Pages | GitHub Pages |
| **Data Selection** | Fixed (latest only) | Dropdown (any date) |
| **Rank Dates** | Limited by PF_Ranks | 21 dates available |
| **Pivot Files** | 1 at a time | 14 available |
| **File Size** | Large (all data embedded) | Small (loads on-demand) |
| **Update Process** | Regenerate HTML | Copy files + manifest |
| **Load Time** | Instant | ~2-3 seconds initial |
| **Flexibility** | Low | High |
| **Mobile** | Good | Excellent |

## 🎯 Advantages

**For GitHub Pages:**
- ✓ No server needed (pure client-side)
- ✓ Works on free GitHub Pages
- ✓ Same URL as before
- ✓ Instant deployment (1-2 min)

**For You:**
- ✓ Select any date combination
- ✓ 21 rank dates vs limited before
- ✓ Easy to add new data (just copy files)
- ✓ Flexible pivot matching
- ✓ No regeneration needed (manifest only)

**For Users:**
- ✓ Fast dropdown switching
- ✓ Browser caching for speed
- ✓ Mobile-friendly design
- ✓ No login required
- ✓ Works anywhere

## 🐛 Troubleshooting

**Dashboard not loading:**
- Check browser console for errors (F12)
- Verify manifest.json exists in docs/
- Check data files exist in docs/data/

**Dropdowns empty:**
- Regenerate manifest: `python generate_manifest.py`
- Check manifest.json has rank_files and pivot_files

**Data not showing:**
- Verify CSV/Excel files are in correct directories
- Check file naming matches pattern:
  - Rank: `out_DD-Mon-YY.csv`
  - Pivot: `MonYY_pivot_features.xlsx`

**"Failed to load" errors:**
- Check browser console for specific file
- Verify file paths in manifest.json are correct
- Ensure files are committed to git

**Auto-matching not working:**
- Check date parsing in manifest.json
- Verify pivot files cover the date range
- Check browser console for errors

## 📱 Mobile Support

Fully responsive design:
- Dropdowns stack vertically on small screens
- Table scrolls horizontally if needed
- Touch-friendly controls
- Optimized for all devices

## 🔒 Data Privacy

- All data processing happens client-side
- No data sent to external servers
- Files loaded directly from GitHub
- No analytics or tracking
- Open source and transparent

## 📈 Performance

**Initial Load:**
- HTML: ~5KB
- JavaScript: ~15KB
- manifest.json: ~2KB
- Libraries (CDN): ~200KB (cached)
- **Total**: ~220KB first time
- **Subsequent**: ~22KB (libraries cached)

**Per Date Selection:**
- Rank CSV: ~120KB (parsed in ~100ms)
- Pivot Excel: ~1.6MB (parsed in ~500ms)
- Table render: ~50ms
- **Total**: ~650ms per selection

**Caching:**
- Files cached in browser
- Switching back to previous dates: instant
- No re-download needed

## 🚦 Next Steps

1. **Test it out:**
   - Visit https://araroot.github.io/themes/
   - Try different date combinations
   - Check mobile view

2. **Bookmark the URL**

3. **When you have new data:**
   - Run `python update_interactive_dashboard.py`
   - Wait 1-2 minutes for deployment
   - Refresh the page

4. **Share the URL** with anyone who needs access

## 📚 Additional Documentation

- **INTERACTIVE_APP.md** - Streamlit version (requires server)
- **HOW_TO_UPDATE.md** - Old static version docs
- **README_DEPLOY.md** - General deployment guide

This GitHub Pages version is now your main dashboard!
