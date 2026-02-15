#!/usr/bin/env python3
"""
Extract only theme definition sheets from PF_Ranks.xlsx
Creates a lightweight file for GitHub Pages
"""

import pandas as pd
from pathlib import Path

SOURCE = Path("/Users/raviaranke/Desktop/themes/data/PF_Ranks.xlsx")
DEST = Path("/Users/raviaranke/Desktop/themes/docs/data/PF_Ranks_lite.xlsx")

def main():
    print("Extracting theme definitions...")

    # Read only the sheets we need
    pf_ranks = pd.read_excel(SOURCE, sheet_name="PF_Ranks")
    tpark_codex = pd.read_excel(SOURCE, sheet_name="tpark_codex")

    # Create destination directory
    DEST.parent.mkdir(parents=True, exist_ok=True)

    # Write to new file
    with pd.ExcelWriter(DEST, engine='openpyxl') as writer:
        pf_ranks.to_excel(writer, sheet_name='PF_Ranks', index=False)
        tpark_codex.to_excel(writer, sheet_name='tpark_codex', index=False)

    # Check file sizes
    orig_size = SOURCE.stat().st_size / (1024 * 1024)
    new_size = DEST.stat().st_size / (1024 * 1024)

    print(f"✓ Original: {orig_size:.1f}MB")
    print(f"✓ Lite version: {new_size:.1f}MB")
    print(f"✓ Saved: {orig_size - new_size:.1f}MB ({(1 - new_size/orig_size)*100:.0f}% reduction)")
    print(f"✓ Wrote to: {DEST}")

if __name__ == "__main__":
    main()
