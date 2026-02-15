#!/usr/bin/env python3
"""
Build interactive dashboard with dropdowns for GitHub Pages deployment
Generates static HTML + JSON data files
"""

from pathlib import Path
import pandas as pd
import json
import re
from datetime import datetime

from app import (
    build_theme_map,
    build_theme_map_codex,
    normalize_theme_name,
)

from export_static import (
    is_real_symbol,
)

from mf_processor import (
    get_all_bb_cols_sorted,
    get_symbol_bb_last_3,
)

from combined_processor import (
    build_combined_theme_table,
    render_combined_table,
)

# Directories
RANK_DIR = Path("/Users/raviaranke/Desktop/code2026/data/r_outputs/eom_price")
PIVOT_DIR = Path("/Users/raviaranke/Desktop/code2026/data/r_outputs/final")
PF_RANKS_PATH = Path("/Users/raviaranke/Downloads/PF_Ranks.xlsx")
if not PF_RANKS_PATH.exists():
    PF_RANKS_PATH = Path("/Users/raviaranke/Desktop/themes/PF_Ranks.xlsx")

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
        return (year, month, day)
    return (0, 0, 0)


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
        return (year, month)
    return (0, 0)


def match_pivot_to_rank(rank_date_tuple, available_pivots):
    """
    Match rank date to appropriate pivot file
    - End of month (day >= 25): same month pivot
    - Mid month (day < 25): previous month pivot
    """
    year, month, day = rank_date_tuple

    # Determine target pivot month
    if day >= 25:
        # End of month -> use same month pivot
        target_year, target_month = year, month
    else:
        # Mid month -> use previous month pivot
        target_month = month - 1
        target_year = year
        if target_month < 1:
            target_month = 12
            target_year -= 1

    # Find matching pivot
    for pivot_file, (py, pm) in available_pivots:
        if py == target_year and pm == target_month:
            return pivot_file

    # Fallback: return closest earlier pivot
    sorted_pivots = sorted(available_pivots, key=lambda x: (x[1][0], x[1][1]), reverse=True)
    for pivot_file, (py, pm) in sorted_pivots:
        if (py, pm) <= (target_year, target_month):
            return pivot_file

    # Last resort: return latest pivot
    if sorted_pivots:
        return sorted_pivots[0][0]
    return None


def get_available_rank_files():
    """Get all rank files sorted by date (newest first)"""
    files = list(RANK_DIR.glob("out_*.csv"))
    files_with_dates = [(f, parse_rank_date(f.name)) for f in files]
    files_with_dates = [(f, d) for f, d in files_with_dates if d != (0, 0, 0)]
    sorted_files = sorted(files_with_dates, key=lambda x: x[1], reverse=True)
    return sorted_files


def get_available_pivot_files():
    """Get all pivot files sorted by date (newest first)"""
    files = list(PIVOT_DIR.glob("*_pivot_features.xlsx"))
    files_with_dates = [(f, parse_pivot_date(f.name)) for f in files]
    files_with_dates = [(f, d) for f, d in files_with_dates if d != (0, 0)]
    sorted_files = sorted(files_with_dates, key=lambda x: x[1], reverse=True)
    return sorted_files


def format_rank_date_display(date_tuple):
    """Format (2026, 2, 13) -> '2026-02-13'"""
    year, month, day = date_tuple
    return f"{year:04d}-{month:02d}-{day:02d}"


def format_pivot_date_display(date_tuple):
    """Format (2026, 1) -> '2026-01'"""
    year, month = date_tuple
    return f"{year:04d}-{month:02d}"


def load_rank_data(rank_file: Path):
    """Load rank data from CSV and return as dict by symbol"""
    df = pd.read_csv(rank_file)
    df['symbol'] = df['symbol'].str.strip().str.upper()

    rank_dict = {}
    for _, row in df.iterrows():
        symbol = row['symbol']
        rank_dict[symbol] = {
            'ptile': int(row['ptile']) if pd.notna(row['ptile']) else None,
            'cmp': row.get('cmp'),
            'mcap': row.get('ff_mcap')
        }
    return rank_dict


def build_theme_rank_table(theme_map, rank_current, rank_prev, pf_symbols, selected_themes):
    """Build theme table using rank data instead of PF_Ranks"""
    rows = []

    for theme in selected_themes:
        # Get symbols for this theme
        theme_symbols = theme_map[theme_map['Theme'] == theme]['Symbol'].unique()

        portfolio_cells = []
        other_cells = []

        # Calculate median for theme
        theme_ranks = []
        for symbol in theme_symbols:
            if symbol in rank_current and rank_current[symbol]['ptile'] is not None:
                theme_ranks.append(rank_current[symbol]['ptile'])

        median_current = int(pd.Series(theme_ranks).median()) if theme_ranks else None

        # Calculate previous median for delta
        theme_ranks_prev = []
        for symbol in theme_symbols:
            if symbol in rank_prev and rank_prev[symbol]['ptile'] is not None:
                theme_ranks_prev.append(rank_prev[symbol]['ptile'])

        median_prev = int(pd.Series(theme_ranks_prev).median()) if theme_ranks_prev else None

        # Format median with delta
        if median_current is not None:
            median_str = str(median_current)
            if median_prev is not None:
                delta = median_current - median_prev
                if delta < 0:
                    median_str += f" <span class='delta-up'>(▲{abs(delta)})</span>"
                elif delta > 0:
                    median_str += f" <span class='delta-down'>(▼{delta})</span>"
                else:
                    median_str += f" <span class='delta-flat'>(—)</span>"
        else:
            median_str = ""

        # Build symbol lists
        for symbol in theme_symbols:
            if symbol not in rank_current:
                continue

            curr_rank = rank_current[symbol]['ptile']
            if curr_rank is None:
                continue

            prev_rank = rank_prev.get(symbol, {}).get('ptile')

            # Format: SYMBOL rank (delta)
            rank_str = f"{symbol} {curr_rank}"

            if prev_rank is not None:
                delta = curr_rank - prev_rank
                if delta < 0:
                    rank_str += f" <span class='delta-up'>(▲{abs(delta)})</span>"
                elif delta > 0:
                    rank_str += f" <span class='delta-down'>(▼{delta})</span>"
                else:
                    rank_str += f" <span class='delta-flat'>(—)</span>"

            if symbol in pf_symbols:
                portfolio_cells.append(rank_str)
            else:
                other_cells.append(rank_str)

        row = {
            "Theme": theme,
            "Median (Latest Δ)": median_str,
            "Portfolio": "<br/>".join(portfolio_cells),
            "Others": "<br/>".join(other_cells)
        }
        rows.append(row)

    return rows


def build_mf_theme_table_from_pivot(pivot_file, theme_map, pf_symbols, selected_themes):
    """Build MF theme table from pivot file"""
    df = pd.read_excel(pivot_file, sheet_name="Summary Data")
    df['Symbol'] = df['Symbol'].str.strip().str.upper()

    bb_cols_sorted = get_all_bb_cols_sorted(df)

    rows = []
    for theme in selected_themes:
        theme_symbols = theme_map[theme_map['Theme'] == theme]['Symbol'].unique()

        portfolio_cells = []
        other_cells = []

        for symbol in theme_symbols:
            bb_last_3 = get_symbol_bb_last_3(df, symbol, bb_cols_sorted)

            if bb_last_3:
                bb_text = f"{symbol} ({', '.join(map(str, bb_last_3))})"

                if symbol in pf_symbols:
                    portfolio_cells.append(bb_text)
                else:
                    other_cells.append(bb_text)

        row = {
            "Theme": theme,
            "Portfolio": "<br/>".join(portfolio_cells),
            "Others": "<br/>".join(other_cells)
        }
        rows.append(row)

    return rows


def generate_data_json(rank_current_file, rank_prev_file, pivot_file, theme_map, pf_symbols, selected_themes, output_name):
    """Generate JSON data for a specific combination"""
    # Load rank data
    rank_current = load_rank_data(rank_current_file)
    rank_prev = load_rank_data(rank_prev_file)

    # Build rank table
    rank_rows = build_theme_rank_table(theme_map, rank_current, rank_prev, pf_symbols, selected_themes)

    # Build MF table
    mf_rows = build_mf_theme_table_from_pivot(pivot_file, theme_map, pf_symbols, selected_themes)

    # Build combined
    combined_rows = build_combined_theme_table(rank_rows, mf_rows, selected_themes)

    # Convert to JSON-serializable format
    json_data = {
        "themes": selected_themes,
        "combined": combined_rows
    }

    # Write to file
    output_file = OUTPUT_DIR / "data" / f"{output_name}.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(json_data, f)

    return json_data


def main():
    print("=" * 60)
    print("BUILDING INTERACTIVE DASHBOARD")
    print("=" * 60)

    # Load theme definitions
    print("\n1. Loading theme definitions from PF_Ranks.xlsx...")
    pf = pd.read_excel(PF_RANKS_PATH, sheet_name="PF_Ranks")
    th_codex = pd.read_excel(PF_RANKS_PATH, sheet_name="tpark_codex")

    theme_map_codex = build_theme_map_codex(th_codex)

    # Get portfolio symbols
    pf = pf.rename(columns={"Symbol / Rank": "Symbol"})
    pf["Symbol"] = pf["Symbol"].astype(str).str.strip().str.upper()
    pf_symbols = {s for s in pf["Symbol"].dropna() if is_real_symbol(s)}

    # Get all themes
    all_themes = sorted(theme_map_codex['Theme'].unique())

    print(f"   Found {len(all_themes)} themes")
    print(f"   Found {len(pf_symbols)} portfolio symbols")

    # Get available files
    print("\n2. Scanning available data files...")
    rank_files = get_available_rank_files()
    pivot_files = get_available_pivot_files()

    print(f"   Found {len(rank_files)} rank files")
    print(f"   Found {len(pivot_files)} pivot files")

    # Determine defaults
    latest_rank = rank_files[0]
    prev_rank = rank_files[1] if len(rank_files) > 1 else rank_files[0]

    # Match pivot to latest rank
    matched_pivot = match_pivot_to_rank(latest_rank[1], pivot_files)

    print(f"\n3. Default selections:")
    print(f"   Current Rank: {latest_rank[0].name} ({format_rank_date_display(latest_rank[1])})")
    print(f"   Previous Rank: {prev_rank[0].name} ({format_rank_date_display(prev_rank[1])})")
    print(f"   Pivot File: {matched_pivot.name if matched_pivot else 'None'} ({format_pivot_date_display(parse_pivot_date(matched_pivot.name)) if matched_pivot else 'N/A'})")

    # Generate default data
    print("\n4. Generating default data JSON...")
    default_data = generate_data_json(
        latest_rank[0],
        prev_rank[0],
        matched_pivot,
        theme_map_codex,
        pf_symbols,
        all_themes,
        "default"
    )

    # Build dropdown options
    rank_options = []
    for f, date in rank_files:
        rank_options.append({
            "file": f.name,
            "display": format_rank_date_display(date),
            "date": date
        })

    pivot_options = []
    for f, date in pivot_files:
        pivot_options.append({
            "file": f.name,
            "display": format_pivot_date_display(date),
            "date": date
        })

    # Create mapping JSON for auto-matching
    mapping = {
        "rank_files": rank_options,
        "pivot_files": pivot_options,
        "defaults": {
            "current_rank": latest_rank[0].name,
            "prev_rank": prev_rank[0].name,
            "pivot": matched_pivot.name if matched_pivot else None
        }
    }

    mapping_file = OUTPUT_DIR / "data" / "file_mapping.json"
    with open(mapping_file, 'w') as f:
        json.dump(mapping, f, indent=2)

    print(f"   ✓ Generated {mapping_file}")
    print(f"   ✓ Generated default data JSON")

    print("\n5. Generating interactive HTML...")
    # Will create the HTML in next step

    print("\n" + "=" * 60)
    print("✓ BUILD COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
