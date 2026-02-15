#!/usr/bin/env python3
"""
Generate manifest.json listing all available data files for JavaScript to load
"""

from pathlib import Path
import json
import re

# Data directories
DATA_DIR = Path("/Users/raviaranke/Desktop/themes/data")
RANK_DIR = DATA_DIR / "eom_price"
PIVOT_DIR = DATA_DIR / "final"
OUTPUT_DIR = Path("/Users/raviaranke/Desktop/themes/docs")


def parse_rank_date(filename: str):
    """Parse date from rank filename: out_13-Feb-26.csv -> (2026, 2, 13)"""
    match = re.match(r'out_(\d+)-([A-Za-z]+)-(\d+)\.csv', filename)
    if match:
        day = int(match.group(1))
        month_str = match.group(2)
        year = int('20' + match.group(3))

        month_map = {
            'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
            'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
        }
        month = month_map.get(month_str, 1)
        return {"year": year, "month": month, "day": day}
    return None


def parse_pivot_date(filename: str):
    """Parse date from pivot filename: Jan26_pivot_features.xlsx -> (2026, 1)"""
    match = re.match(r'([A-Za-z]+)(\d+)_pivot_features\.xlsx', filename)
    if match:
        month_str = match.group(1)
        year = int('20' + match.group(2))

        month_map = {
            'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
            'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
        }
        month = month_map.get(month_str[:3], 1)
        return {"year": year, "month": month}
    return None


def main():
    print("=" * 60)
    print("GENERATING DATA MANIFEST")
    print("=" * 60)

    # Scan rank files
    print("\n1. Scanning rank files...")
    rank_files = []
    for f in sorted(RANK_DIR.glob("out_*.csv")):
        date = parse_rank_date(f.name)
        if date:
            rank_files.append({
                "filename": f.name,
                "path": f"data/eom_price/{f.name}",
                "date": date,
                "display": f"{date['year']:04d}-{date['month']:02d}-{date['day']:02d}"
            })

    # Sort by date (newest first)
    rank_files.sort(key=lambda x: (x['date']['year'], x['date']['month'], x['date']['day']), reverse=True)
    print(f"   Found {len(rank_files)} rank files")

    # Scan pivot files
    print("\n2. Scanning pivot files...")
    pivot_files = []
    for f in sorted(PIVOT_DIR.glob("*_pivot_features.xlsx")):
        # Skip temp files
        if f.name.startswith("~$"):
            continue
        date = parse_pivot_date(f.name)
        if date:
            pivot_files.append({
                "filename": f.name,
                "path": f"data/final/{f.name}",
                "date": date,
                "display": f"{date['year']:04d}-{date['month']:02d}"
            })

    # Sort by date (newest first)
    pivot_files.sort(key=lambda x: (x['date']['year'], x['date']['month']), reverse=True)
    print(f"   Found {len(pivot_files)} pivot files")

    # Create manifest
    manifest = {
        "rank_files": rank_files,
        "pivot_files": pivot_files,
        "pf_ranks_path": "data/PF_Ranks.xlsx",
        "defaults": {
            "current_rank": rank_files[0] if rank_files else None,
            "prev_rank": rank_files[1] if len(rank_files) > 1 else rank_files[0] if rank_files else None
        }
    }

    # Write manifest
    print("\n3. Writing manifest.json...")
    manifest_file = OUTPUT_DIR / "manifest.json"
    with open(manifest_file, 'w') as f:
        json.dump(manifest, f, indent=2)

    print(f"   ✓ Wrote {manifest_file}")

    print("\n" + "=" * 60)
    print("✓ MANIFEST GENERATION COMPLETE")
    print("=" * 60)
    print(f"\nManifest contains:")
    print(f"  - {len(rank_files)} rank files")
    print(f"  - {len(pivot_files)} pivot files")
    print(f"\nDefaults:")
    if manifest['defaults']['current_rank']:
        print(f"  - Current: {manifest['defaults']['current_rank']['display']}")
    if manifest['defaults']['prev_rank']:
        print(f"  - Previous: {manifest['defaults']['prev_rank']['display']}")


if __name__ == "__main__":
    main()
