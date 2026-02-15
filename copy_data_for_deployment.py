#!/usr/bin/env python3
"""
Copy data files to themes/data directory for deployment
"""

from pathlib import Path
import shutil

# Source directories
RANK_SRC = Path("/Users/raviaranke/Desktop/code2026/data/r_outputs/eom_price")
PIVOT_SRC = Path("/Users/raviaranke/Desktop/code2026/data/r_outputs/final")
PF_RANKS_SRC = Path("/Users/raviaranke/Downloads/PF_Ranks.xlsx")

# Destination directory
DEST = Path("/Users/raviaranke/Desktop/themes/data")

def main():
    print("=" * 60)
    print("COPYING DATA FOR DEPLOYMENT")
    print("=" * 60)

    # Create destination directories
    rank_dest = DEST / "eom_price"
    pivot_dest = DEST / "final"

    rank_dest.mkdir(parents=True, exist_ok=True)
    pivot_dest.mkdir(parents=True, exist_ok=True)

    # Copy rank files
    print("\n1. Copying rank files...")
    rank_files = list(RANK_SRC.glob("out_*.csv"))
    for f in rank_files:
        shutil.copy2(f, rank_dest / f.name)
    print(f"   ✓ Copied {len(rank_files)} rank files")

    # Copy pivot files
    print("\n2. Copying pivot files...")
    pivot_files = list(PIVOT_SRC.glob("*_pivot_features.xlsx"))
    for f in pivot_files:
        # Skip temp files
        if f.name.startswith("~$"):
            continue
        shutil.copy2(f, pivot_dest / f.name)
    print(f"   ✓ Copied {len([f for f in pivot_files if not f.name.startswith('~$')])} pivot files")

    # Copy PF_Ranks
    print("\n3. Copying PF_Ranks.xlsx...")
    if PF_RANKS_SRC.exists():
        shutil.copy2(PF_RANKS_SRC, DEST / "PF_Ranks.xlsx")
        print("   ✓ Copied PF_Ranks.xlsx")
    else:
        print("   ⚠ PF_Ranks.xlsx not found in Downloads")

    print("\n" + "=" * 60)
    print("✓ COPY COMPLETE")
    print("=" * 60)
    print(f"\nData copied to: {DEST}")
    print("\nNext steps:")
    print("1. Run: git add data/")
    print("2. Run: git commit -m 'Add data files for deployment'")
    print("3. Run: git push")
    print("4. Deploy to Streamlit Cloud")


if __name__ == "__main__":
    main()
