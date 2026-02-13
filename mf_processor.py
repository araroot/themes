"""
Mutual Fund Movement Processor
Processes latest *_pivot_features.xlsx to show mutual fund buy/sell movements BY THEME
"""

from pathlib import Path
import pandas as pd
import re
from datetime import datetime


def find_latest_pivot_file(base_dir: Path = None):
    """Find the latest pivot_features.xlsx file based on date prefix"""
    if base_dir is None:
        base_dir = Path("/Users/raviaranke/Desktop/themes")

    # Find all files matching pattern *_pivot_features.xlsx
    pivot_files = list(base_dir.glob("*_pivot_features.xlsx"))

    if not pivot_files:
        raise FileNotFoundError("No pivot_features.xlsx files found")

    # Parse dates from filenames (format: MonYY_pivot_features.xlsx)
    month_map = {
        'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
        'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
    }

    def parse_filename_date(filepath):
        """Extract date from filename like Dec25_pivot_features.xlsx"""
        match = re.match(r'([A-Za-z]+)(\d+)_pivot_features\.xlsx', filepath.name)
        if match:
            month_str = match.group(1)
            year = int('20' + match.group(2))  # Convert 25 to 2025
            month = month_map.get(month_str[:3], 0)
            return (year, month), match.group(1) + match.group(2)
        return (0, 0), None

    # Sort by date and get the latest
    files_with_dates = [(f, parse_filename_date(f)) for f in pivot_files]
    files_with_dates = [(f, date, label) for f, (date, label) in files_with_dates if label]

    if not files_with_dates:
        raise ValueError("Could not parse dates from pivot file names")

    latest_file, _, date_label = max(files_with_dates, key=lambda x: x[1])
    return latest_file, date_label


def load_mf_data(path: Path = None):
    """Load mutual fund data from latest pivot file"""
    if path is None:
        path, date_label = find_latest_pivot_file()
        print(f"Using pivot file: {path.name} ({date_label})")
    else:
        # Extract date label from provided path
        match = re.match(r'([A-Za-z]+\d+)_pivot_features\.xlsx', path.name)
        date_label = match.group(1) if match else "Unknown"

    df = pd.read_excel(path, sheet_name="Summary Data")
    return df, date_label


def get_latest_prev_bb_cols(df: pd.DataFrame):
    """Get latest and previous bb_ columns (chronologically)"""
    bb_cols = get_all_bb_cols_sorted(df)

    if len(bb_cols) >= 2:
        latest = bb_cols[-1]
        prev = bb_cols[-2]
        return latest, prev
    elif len(bb_cols) == 1:
        return bb_cols[0], None
    else:
        return None, None


def get_all_bb_cols_sorted(df: pd.DataFrame):
    """Get all bb_ columns sorted chronologically"""
    import re

    bb_cols = [c for c in df.columns if c.startswith('bb_') and c != 'bb_']

    # Sort chronologically by parsing month names
    month_map = {
        'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
        'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
    }

    def parse_date(col_name):
        # Extract month and year from column name like "bb_Dec25"
        match = re.match(r'bb_([A-Za-z]+)(\d+)', col_name)
        if match:
            month_str = match.group(1)
            year = int('20' + match.group(2))  # Convert 25 to 2025
            month = month_map.get(month_str[:3], 0)
            return (year, month)
        return (0, 0)

    return sorted(bb_cols, key=parse_date)


def get_symbol_bb_aggregated(df: pd.DataFrame, symbol: str, latest_col: str, prev_col: str):
    """Get BB value for a symbol (per-symbol, same across all fund families)"""
    symbol_df = df[df['Symbol'] == symbol]

    if len(symbol_df) == 0:
        return None, None

    # BB values are per-symbol (same across all fund families), so just take first value
    latest_val = symbol_df[latest_col].iloc[0] if latest_col in symbol_df.columns and len(symbol_df) > 0 else None
    prev_val = symbol_df[prev_col].iloc[0] if prev_col and prev_col in symbol_df.columns and len(symbol_df) > 0 else None

    return latest_val, prev_val


def get_symbol_bb_last_3(df: pd.DataFrame, symbol: str, bb_cols_sorted: list):
    """Get last 3 BB values for a symbol"""
    symbol_df = df[df['Symbol'] == symbol]

    if len(symbol_df) == 0:
        return []

    # Get last 3 columns
    last_3_cols = bb_cols_sorted[-3:] if len(bb_cols_sorted) >= 3 else bb_cols_sorted

    values = []
    for col in last_3_cols:
        if col in symbol_df.columns and len(symbol_df) > 0:
            val = symbol_df[col].iloc[0]
            if pd.notna(val):
                values.append(int(val))

    return values


def build_mf_theme_table(mf_df: pd.DataFrame, latest_col: str, prev_col: str,
                         selected_themes: list, theme_map: pd.DataFrame,
                         portfolio_symbols: set):
    """
    Build MF table matching the theme structure from Ranks tab
    Shows last 3 BB values by theme (comma-separated in brackets)
    """

    if latest_col is None:
        return []

    # Get all BB columns sorted chronologically
    bb_cols_sorted = get_all_bb_cols_sorted(mf_df)

    rows = []

    for theme in selected_themes:
        # Get all symbols for this theme
        theme_symbols = theme_map[theme_map['Theme'] == theme]['Symbol'].unique()

        portfolio_cells = []
        other_cells = []

        for symbol in theme_symbols:
            # Get last 3 BB values
            bb_last_3 = get_symbol_bb_last_3(mf_df, symbol, bb_cols_sorted)

            if bb_last_3:
                # Build display string: "SYMBOL(value1,value2,value3)"
                bb_text = f"{symbol}({','.join(map(str, bb_last_3))})"

                # Separate portfolio vs others
                if symbol in portfolio_symbols:
                    portfolio_cells.append(bb_text)
                else:
                    other_cells.append(bb_text)

        row = {
            "Theme": theme,
            "Portfolio": ", ".join(portfolio_cells),
            "Others": ", ".join(other_cells)
        }
        rows.append(row)

    return rows


def render_mf_theme_table(rows, latest_date_str: str = "Dec 2025"):
    """Render MF theme table as HTML - matching Ranks tab layout"""

    cols = ["Theme", "Portfolio", "Others"]

    colgroup = (
        "<colgroup>"
        "<col style='width:14%'>"
        "<col style='width:43%'>"
        "<col style='width:43%'>"
        "</colgroup>"
    )

    head_cells = "".join(f"<th>{c}</th>" for c in cols)
    body_rows = []

    for r in rows:
        theme = r.get("Theme", "")
        portfolio = r.get("Portfolio", "")
        others = r.get("Others", "")

        cells = [
            f"<td class='col-theme'>{theme}</td>",
            f"<td class='col-list'>{portfolio}</td>",
            f"<td class='col-list'>{others}</td>",
        ]
        body_rows.append("<tr>" + "".join(cells) + "</tr>")

    html = (
        f"<div style='margin:4px 0 8px 0;color:#666;font-size:12px;'>Mutual Fund BB Signals - {latest_date_str}</div>"
        "<table class='tp-table'>"
        f"{colgroup}"
        f"<thead><tr>{head_cells}</tr></thead>"
        f"<tbody>{''.join(body_rows)}</tbody>"
        "</table>"
    )
    return html
