#!/usr/bin/env python3
"""
Update interactive dashboard with new data files and deploy to GitHub
Only keeps the latest file from each month (Option B)
"""

import shutil
from pathlib import Path
import subprocess
import re
from collections import defaultdict

# Source directories
RANK_SRC = Path("/Users/raviaranke/Desktop/code2026/data/r_outputs/eom_price")
PIVOT_SRC = Path("/Users/raviaranke/Desktop/code2026/data/r_outputs/final")
PF_RANKS_SRC = Path("/Users/raviaranke/Downloads/PF_Ranks.xlsx")

# Destination directory
THEMES_DIR = Path("/Users/raviaranke/Desktop/themes")
DATA_DIR = THEMES_DIR / "docs" / "data"


def parse_rank_filename(filename):
    """Parse rank filename: out_20-Feb-26.csv -> (2026, 2, 20)"""
    match = re.match(r'out_(\d+)-([A-Za-z]+)-(\d+)\.csv', filename)
    if match:
        day = int(match.group(1))
        month_str = match.group(2)
        year = int('20' + match.group(3))

        month_map = {
            'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
            'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
        }
        month = month_map.get(month_str, 0)
        return (year, month, day)
    return None


def select_latest_per_month(files):
    """Keep only the latest file (highest day) from each month"""
    # Group files by (year, month)
    by_month = defaultdict(list)

    for f in files:
        parsed = parse_rank_filename(f.name)
        if parsed:
            year, month, day = parsed
            by_month[(year, month)].append((day, f))

    # For each month, keep only the file with max day
    selected = []
    for (year, month), file_list in by_month.items():
        max_day_file = max(file_list, key=lambda x: x[0])[1]
        selected.append(max_day_file)

    return selected


def main():
    print("=" * 60)
    print("UPDATING INTERACTIVE DASHBOARD")
    print("=" * 60)

    # 1. Copy data files (with smart selection)
    print("\n1. Smart-copying data files to themes/data...")

    rank_dest = DATA_DIR / "eom_price"
    pivot_dest = DATA_DIR / "final"

    rank_dest.mkdir(parents=True, exist_ok=True)
    pivot_dest.mkdir(parents=True, exist_ok=True)

    # Select only latest file per month from rank files
    all_rank_files = list(RANK_SRC.glob("out_*.csv"))
    selected_rank_files = select_latest_per_month(all_rank_files)

    # Get list of files that should exist in destination
    selected_names = {f.name for f in selected_rank_files}

    # Remove old files from destination that are not in selected set
    for existing_file in rank_dest.glob("out_*.csv"):
        if existing_file.name not in selected_names:
            existing_file.unlink()
            print(f"   🗑️  Removed outdated: {existing_file.name}")

    # Copy selected files
    for f in selected_rank_files:
        shutil.copy2(f, rank_dest / f.name)
    print(f"   ✓ Copied {len(selected_rank_files)} rank files (latest per month)")

    # Copy pivot files
    pivot_files = [f for f in PIVOT_SRC.glob("*_pivot_features.xlsx") if not f.name.startswith("~$")]
    for f in pivot_files:
        shutil.copy2(f, pivot_dest / f.name)
    print(f"   ✓ Copied {len(pivot_files)} pivot files")

    # Copy PF_Ranks
    if PF_RANKS_SRC.exists():
        shutil.copy2(PF_RANKS_SRC, DATA_DIR / "PF_Ranks.xlsx")
        print("   ✓ Copied PF_Ranks.xlsx")
    else:
        print("   ⚠ PF_Ranks.xlsx not found in Downloads")

    # 2. Generate manifest
    print("\n2. Generating manifest.json...")
    result = subprocess.run(
        ["python", "generate_manifest.py"],
        cwd=THEMES_DIR,
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print("   ✓ Manifest generated successfully")
    else:
        print(f"   ✗ Error generating manifest: {result.stderr}")
        return

    # 3. Commit and push
    print("\n3. Committing and pushing to GitHub...")

    # Git add
    subprocess.run(["git", "add", "docs/data/", "docs/manifest.json"], cwd=THEMES_DIR)

    # Git commit
    commit_msg = """Update interactive dashboard data (auto-cleaned)

Updated data files:
- Rank files (latest per month only)
- Pivot files (final)
- PF_Ranks.xlsx
- manifest.json

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"""

    commit_result = subprocess.run(
        ["git", "commit", "-m", commit_msg],
        cwd=THEMES_DIR,
        capture_output=True,
        text=True
    )

    if commit_result.returncode == 0:
        print("   ✓ Changes committed")
    else:
        if "nothing to commit" in commit_result.stdout:
            print("   ✓ No changes to commit")
        else:
            print(f"   ✗ Commit failed: {commit_result.stderr}")
            return

    # Git push
    push_result = subprocess.run(
        ["git", "push"],
        cwd=THEMES_DIR,
        capture_output=True,
        text=True
    )

    if push_result.returncode == 0:
        print("   ✓ Pushed to GitHub successfully")
    else:
        print(f"   ✗ Push failed: {push_result.stderr}")
        return

    print("\n" + "=" * 60)
    print("✓ DASHBOARD UPDATE COMPLETE!")
    print("=" * 60)
    print("\nInteractive dashboard updated and deployed to GitHub Pages")
    print("Changes will be live in 1-2 minutes")


if __name__ == "__main__":
    main()
