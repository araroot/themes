#!/usr/bin/env python3
"""
Simple script to update dashboard with latest files from Downloads and push to GitHub
"""

import shutil
from pathlib import Path
import subprocess
import re

def find_latest_pivot_in_downloads():
    """Find the latest pivot_features.xlsx file in Downloads"""
    downloads = Path("/Users/raviaranke/Downloads")
    pivot_files = list(downloads.glob("*_pivot_features.xlsx"))

    if not pivot_files:
        raise FileNotFoundError("No pivot_features.xlsx files found in Downloads")

    # Parse dates from filenames (format: MonYY_pivot_features.xlsx)
    month_map = {
        'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
        'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
    }

    def parse_date(filepath):
        match = re.match(r'([A-Za-z]+)(\d+)_pivot_features\.xlsx', filepath.name)
        if match:
            month_str = match.group(1)
            year = int('20' + match.group(2))
            month = month_map.get(month_str[:3], 0)
            return (year, month)
        return (0, 0)

    latest = max(pivot_files, key=parse_date)
    return latest

def main():
    downloads = Path("/Users/raviaranke/Downloads")
    themes_dir = Path("/Users/raviaranke/Desktop/themes")

    print("=" * 60)
    print("UPDATING DASHBOARD FILES")
    print("=" * 60)

    # 1. Copy PF_Ranks.xlsx
    pf_ranks_src = downloads / "PF_Ranks.xlsx"
    pf_ranks_dst = themes_dir / "PF_Ranks.xlsx"

    if pf_ranks_src.exists():
        shutil.copy2(pf_ranks_src, pf_ranks_dst)
        print(f"✓ Copied PF_Ranks.xlsx from Downloads")
    else:
        print(f"✗ PF_Ranks.xlsx not found in Downloads")
        return

    # 2. Find and copy latest pivot file (check Downloads first, then themes_dir)
    pivot_dst = None
    try:
        pivot_src = find_latest_pivot_in_downloads()
        pivot_dst = themes_dir / pivot_src.name
        shutil.copy2(pivot_src, pivot_dst)
        print(f"✓ Copied {pivot_src.name} from Downloads")
    except FileNotFoundError:
        # Check if pivot file already exists in themes_dir
        pivot_files = list(themes_dir.glob("*_pivot_features.xlsx"))
        if pivot_files:
            month_map = {
                'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
                'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
            }
            def parse_date(filepath):
                match = re.match(r'([A-Za-z]+)(\d+)_pivot_features\.xlsx', filepath.name)
                if match:
                    month_str = match.group(1)
                    year = int('20' + match.group(2))
                    month = month_map.get(month_str[:3], 0)
                    return (year, month)
                return (0, 0)
            pivot_dst = max(pivot_files, key=parse_date)
            print(f"⚠ No pivot file in Downloads, using existing: {pivot_dst.name}")
        else:
            print(f"✗ No pivot_features.xlsx files found in Downloads or themes directory")
            return

    print("\n" + "=" * 60)
    print("FILES BEING USED:")
    print("=" * 60)
    print(f"PF_Ranks: {pf_ranks_dst.name}")
    print(f"Pivot File: {pivot_dst.name}")

    # 3. Regenerate static HTML
    print("\n" + "=" * 60)
    print("REGENERATING STATIC HTML")
    print("=" * 60)

    result = subprocess.run(
        ["python", "export_static.py"],
        cwd=themes_dir,
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print("✓ Static HTML regenerated successfully")
        # Print any output that shows pivot file being used
        for line in result.stdout.split('\n'):
            if 'pivot' in line.lower():
                print(f"  {line}")
    else:
        print(f"✗ Error regenerating HTML: {result.stderr}")
        return

    # 4. Git commit and push
    print("\n" + "=" * 60)
    print("COMMITTING AND PUSHING TO GITHUB")
    print("=" * 60)

    # Git add
    subprocess.run(["git", "add", "-A"], cwd=themes_dir)

    # Git commit
    commit_msg = f"""Update dashboard data: {pivot_dst.stem}

Files updated:
- PF_Ranks.xlsx
- {pivot_dst.name}
- Regenerated static HTML

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"""

    commit_result = subprocess.run(
        ["git", "commit", "-m", commit_msg],
        cwd=themes_dir,
        capture_output=True,
        text=True
    )

    if commit_result.returncode == 0:
        print("✓ Changes committed")
    else:
        if "nothing to commit" in commit_result.stdout:
            print("✓ No changes to commit")
        else:
            print(f"✗ Commit failed: {commit_result.stderr}")
            return

    # Git push
    push_result = subprocess.run(
        ["git", "push"],
        cwd=themes_dir,
        capture_output=True,
        text=True
    )

    if push_result.returncode == 0:
        print("✓ Pushed to GitHub successfully")
    else:
        print(f"✗ Push failed: {push_result.stderr}")
        return

    print("\n" + "=" * 60)
    print("✓ DASHBOARD UPDATE COMPLETE!")
    print("=" * 60)

if __name__ == "__main__":
    main()
