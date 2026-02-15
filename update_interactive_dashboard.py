#!/usr/bin/env python3
"""
Update interactive dashboard with new data files and deploy to GitHub
"""

import shutil
from pathlib import Path
import subprocess

# Source directories
RANK_SRC = Path("/Users/raviaranke/Desktop/code2026/data/r_outputs/eom_price")
PIVOT_SRC = Path("/Users/raviaranke/Desktop/code2026/data/r_outputs/final")
PF_RANKS_SRC = Path("/Users/raviaranke/Downloads/PF_Ranks.xlsx")

# Destination directory
THEMES_DIR = Path("/Users/raviaranke/Desktop/themes")
DATA_DIR = THEMES_DIR / "data"

def main():
    print("=" * 60)
    print("UPDATING INTERACTIVE DASHBOARD")
    print("=" * 60)

    # 1. Copy data files
    print("\n1. Copying data files to themes/data...")

    rank_dest = DATA_DIR / "eom_price"
    pivot_dest = DATA_DIR / "final"

    rank_dest.mkdir(parents=True, exist_ok=True)
    pivot_dest.mkdir(parents=True, exist_ok=True)

    # Copy rank files
    rank_files = list(RANK_SRC.glob("out_*.csv"))
    for f in rank_files:
        shutil.copy2(f, rank_dest / f.name)
    print(f"   ✓ Copied {len(rank_files)} rank files")

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
    subprocess.run(["git", "add", "data/", "docs/manifest.json"], cwd=THEMES_DIR)

    # Git commit
    commit_msg = """Update interactive dashboard data

Updated data files:
- Rank files (eom_price)
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
