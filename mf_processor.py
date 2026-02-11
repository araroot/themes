"""
Mutual Fund Movement Processor
Processes Dec25_pivot_features.xlsx to show mutual fund buy/sell movements BY THEME
"""

from pathlib import Path
import pandas as pd


MF_DATA_PATH = Path("/Users/raviaranke/Desktop/themes/Dec25_pivot_features.xlsx")


def load_mf_data(path: Path = MF_DATA_PATH):
    """Load mutual fund data"""
    df = pd.read_excel(path, sheet_name="Summary Data")
    return df


def get_latest_prev_bb_cols(df: pd.DataFrame):
    """Get latest and previous bb_ columns (chronologically)"""
    import re
    from datetime import datetime

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

    bb_cols_sorted = sorted(bb_cols, key=parse_date)

    if len(bb_cols_sorted) >= 2:
        latest = bb_cols_sorted[-1]
        prev = bb_cols_sorted[-2]
        return latest, prev
    elif len(bb_cols_sorted) == 1:
        return bb_cols_sorted[0], None
    else:
        return None, None


def get_symbol_bb_aggregated(df: pd.DataFrame, symbol: str, latest_col: str, prev_col: str):
    """Get BB value for a symbol (per-symbol, same across all fund families)"""
    symbol_df = df[df['Symbol'] == symbol]

    if len(symbol_df) == 0:
        return None, None

    # BB values are per-symbol (same across all fund families), so just take first value
    latest_val = symbol_df[latest_col].iloc[0] if latest_col in symbol_df.columns and len(symbol_df) > 0 else None
    prev_val = symbol_df[prev_col].iloc[0] if prev_col and prev_col in symbol_df.columns and len(symbol_df) > 0 else None

    return latest_val, prev_val


def build_mf_theme_table(mf_df: pd.DataFrame, latest_col: str, prev_col: str,
                         selected_themes: list, theme_map: pd.DataFrame,
                         portfolio_symbols: set):
    """
    Build MF table matching the theme structure from Ranks tab
    Shows BB flags by theme instead of ranks
    """

    if latest_col is None:
        return []

    rows = []

    for theme in selected_themes:
        # Get all symbols for this theme
        theme_symbols = theme_map[theme_map['Theme'] == theme]['Symbol'].unique()

        portfolio_cells = []
        other_cells = []
        bb_values = []  # For calculating median

        for symbol in theme_symbols:
            latest_bb, prev_bb = get_symbol_bb_aggregated(mf_df, symbol, latest_col, prev_col)

            if pd.notna(latest_bb):
                bb_values.append(latest_bb)

                # Build display string (all integers)
                if pd.notna(prev_bb):
                    delta = int(latest_bb - prev_bb)
                    arrow = "▲" if delta > 0 else "▼" if delta < 0 else "•"
                    klass = "delta-up" if delta > 0 else "delta-down" if delta < 0 else "delta-flat"
                    bb_text = f"{symbol} {int(latest_bb)} <span class='{klass}'>({arrow}{abs(delta)})</span>"
                else:
                    bb_text = f"{symbol} {int(latest_bb)}"

                # Separate portfolio vs others
                if symbol in portfolio_symbols:
                    portfolio_cells.append(bb_text)
                else:
                    other_cells.append(bb_text)

        # No median BB calculation - not needed

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
