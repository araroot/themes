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
    """Get latest and previous bb_ columns"""
    bb_cols = [c for c in df.columns if c.startswith('bb_') and c != 'bb_']
    bb_cols_sorted = sorted(bb_cols)

    if len(bb_cols_sorted) >= 2:
        latest = bb_cols_sorted[-1]
        prev = bb_cols_sorted[-2]
        return latest, prev
    elif len(bb_cols_sorted) == 1:
        return bb_cols_sorted[0], None
    else:
        return None, None


def get_symbol_bb_aggregated(df: pd.DataFrame, symbol: str, latest_col: str, prev_col: str):
    """Get aggregated BB value for a symbol (median across all fund families)"""
    symbol_df = df[df['Symbol'] == symbol]

    if len(symbol_df) == 0:
        return None, None

    # Take median BB value across all fund families
    latest_val = symbol_df[latest_col].median() if latest_col in symbol_df.columns else None
    prev_val = symbol_df[prev_col].median() if prev_col and prev_col in symbol_df.columns else None

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

                # Build display string
                if pd.notna(prev_bb):
                    delta = latest_bb - prev_bb
                    arrow = "▲" if delta > 0 else "▼" if delta < 0 else "•"
                    klass = "delta-up" if delta > 0 else "delta-down" if delta < 0 else "delta-flat"
                    bb_text = f"{symbol} {latest_bb:.0f} <span class='{klass}'>({arrow}{abs(delta):.0f})</span>"
                else:
                    bb_text = f"{symbol} {latest_bb:.0f}"

                # Separate portfolio vs others
                if symbol in portfolio_symbols:
                    portfolio_cells.append(bb_text)
                else:
                    other_cells.append(bb_text)

        # Calculate median BB for the theme
        if bb_values:
            median_bb = pd.Series(bb_values).median()

            # Get previous median for delta calculation
            prev_bb_values = []
            for symbol in theme_symbols:
                _, prev_bb = get_symbol_bb_aggregated(mf_df, symbol, latest_col, prev_col)
                if pd.notna(prev_bb):
                    prev_bb_values.append(prev_bb)

            if prev_bb_values:
                prev_median = pd.Series(prev_bb_values).median()
                delta = median_bb - prev_median
                arrow = "▲" if delta > 0 else "▼" if delta < 0 else "•"
                klass = "delta-up" if delta > 0 else "delta-down" if delta < 0 else "delta-flat"
                median_cell = f"{median_bb:.1f} <span class='{klass}'>({arrow}{abs(delta):.1f})</span>"
            else:
                median_cell = f"{median_bb:.1f}"
        else:
            median_cell = ""

        row = {
            "Theme": theme,
            "Median BB (Latest Δ)": median_cell,
            "Portfolio": ", ".join(portfolio_cells),
            "Others": ", ".join(other_cells)
        }
        rows.append(row)

    return rows


def render_mf_theme_table(rows, latest_date_str: str = "Dec 2025"):
    """Render MF theme table as HTML - matching Ranks tab layout"""

    cols = ["Theme", "Median BB (Latest Δ)", "Portfolio", "Others"]

    colgroup = (
        "<colgroup>"
        "<col style='width:14%'>"
        "<col style='width:8%'>"
        "<col style='width:39%'>"
        "<col style='width:39%'>"
        "</colgroup>"
    )

    head_cells = "".join(f"<th>{c}</th>" for c in cols)
    body_rows = []

    for r in rows:
        theme = r.get("Theme", "")
        median = r.get("Median BB (Latest Δ)", "")
        portfolio = r.get("Portfolio", "")
        others = r.get("Others", "")

        cells = [
            f"<td class='col-theme'>{theme}</td>",
            f"<td class='col-median'>{median}</td>",
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
