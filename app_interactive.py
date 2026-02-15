"""
Theme Park - Interactive Dashboard with Dropdowns
Deploy to Streamlit Cloud for access from anywhere
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import re

from app import build_theme_map_codex, normalize_theme_name
from export_static import is_real_symbol
from mf_processor import get_all_bb_cols_sorted, get_symbol_bb_last_3
from combined_processor import build_combined_theme_table, render_combined_table

# Configure page
st.set_page_config(
    page_title="🐱 Theme Park",
    page_icon="🐱",
    layout="wide"
)

# Data directories - use environment variables if available, otherwise use local paths
import os

RANK_DIR = Path(os.getenv("RANK_DIR", "/Users/raviaranke/Desktop/code2026/data/r_outputs/eom_price"))
PIVOT_DIR = Path(os.getenv("PIVOT_DIR", "/Users/raviaranke/Desktop/code2026/data/r_outputs/final"))
PF_RANKS_PATH = Path(os.getenv("PF_RANKS_PATH", "/Users/raviaranke/Downloads/PF_Ranks.xlsx"))

if not PF_RANKS_PATH.exists():
    PF_RANKS_PATH = Path("/Users/raviaranke/Desktop/themes/PF_Ranks.xlsx")

# Fallback: try data subdirectory in app folder (for deployment)
if not RANK_DIR.exists():
    RANK_DIR = Path(__file__).parent / "data" / "eom_price"
if not PIVOT_DIR.exists():
    PIVOT_DIR = Path(__file__).parent / "data" / "final"
if not PF_RANKS_PATH.exists():
    PF_RANKS_PATH = Path(__file__).parent / "data" / "PF_Ranks.xlsx"


def parse_rank_date(filename: str):
    """Parse date from rank filename"""
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
    """Parse date from pivot filename"""
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


def match_pivot_to_rank(rank_date_tuple, available_pivots_dict):
    """Match rank date to appropriate pivot file"""
    year, month, day = rank_date_tuple

    # End of month (day >= 25): same month pivot
    # Mid month (day < 25): previous month pivot
    if day >= 25:
        target_year, target_month = year, month
    else:
        target_month = month - 1
        target_year = year
        if target_month < 1:
            target_month = 12
            target_year -= 1

    # Find matching pivot
    for pivot_name, (py, pm) in available_pivots_dict.items():
        if py == target_year and pm == target_month:
            return pivot_name

    # Fallback: return closest earlier pivot
    sorted_pivots = sorted(available_pivots_dict.items(), key=lambda x: (x[1][0], x[1][1]), reverse=True)
    for pivot_name, (py, pm) in sorted_pivots:
        if (py, pm) <= (target_year, target_month):
            return pivot_name

    # Last resort: return latest pivot
    if sorted_pivots:
        return sorted_pivots[0][0]
    return None


@st.cache_data
def load_theme_data():
    """Load theme definitions and portfolio symbols"""
    pf = pd.read_excel(PF_RANKS_PATH, sheet_name="PF_Ranks")
    th_codex = pd.read_excel(PF_RANKS_PATH, sheet_name="tpark_codex")

    theme_map = build_theme_map_codex(th_codex)

    pf = pf.rename(columns={"Symbol / Rank": "Symbol"})
    pf["Symbol"] = pf["Symbol"].astype(str).str.strip().str.upper()
    pf_symbols = {s for s in pf["Symbol"].dropna() if is_real_symbol(s)}

    all_themes = sorted(theme_map['Theme'].unique())

    return theme_map, pf_symbols, all_themes


@st.cache_data
def get_available_files():
    """Get available rank and pivot files"""
    # Rank files
    rank_files = list(RANK_DIR.glob("out_*.csv"))
    rank_dict = {}
    for f in rank_files:
        date = parse_rank_date(f.name)
        if date != (0, 0, 0):
            rank_dict[f.name] = date

    # Pivot files
    pivot_files = list(PIVOT_DIR.glob("*_pivot_features.xlsx"))
    pivot_dict = {}
    for f in pivot_files:
        date = parse_pivot_date(f.name)
        if date != (0, 0):
            pivot_dict[f.name] = date

    return rank_dict, pivot_dict


@st.cache_data
def load_rank_data(rank_filename):
    """Load rank data from CSV"""
    df = pd.read_csv(RANK_DIR / rank_filename)
    df['symbol'] = df['symbol'].str.strip().str.upper()

    rank_dict = {}
    for _, row in df.iterrows():
        symbol = row['symbol']
        rank_dict[symbol] = {
            'ptile': int(row['ptile']) if pd.notna(row['ptile']) else None
        }
    return rank_dict


def build_theme_rank_table(theme_map, rank_current, rank_prev, pf_symbols, selected_themes):
    """Build theme table using rank data"""
    rows = []

    for theme in selected_themes:
        theme_symbols = theme_map[theme_map['Theme'] == theme]['Symbol'].unique()

        portfolio_cells = []
        other_cells = []

        # Calculate median
        theme_ranks = [rank_current[s]['ptile'] for s in theme_symbols
                      if s in rank_current and rank_current[s]['ptile'] is not None]
        median_current = int(pd.Series(theme_ranks).median()) if theme_ranks else None

        theme_ranks_prev = [rank_prev[s]['ptile'] for s in theme_symbols
                           if s in rank_prev and rank_prev[s]['ptile'] is not None]
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


@st.cache_data
def build_mf_theme_table_from_pivot(pivot_filename, theme_map, pf_symbols, selected_themes):
    """Build MF theme table from pivot file"""
    df = pd.read_excel(PIVOT_DIR / pivot_filename, sheet_name="Summary Data")
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


# Main app
def main():
    st.title("🐱 Theme Park")

    # Load data
    theme_map, pf_symbols, all_themes = load_theme_data()
    rank_dict, pivot_dict = get_available_files()

    # Sort files by date (newest first)
    sorted_ranks = sorted(rank_dict.items(), key=lambda x: x[1], reverse=True)
    sorted_pivots = sorted(pivot_dict.items(), key=lambda x: x[1], reverse=True)

    # Format display names
    rank_display = {name: f"{date[0]:04d}-{date[1]:02d}-{date[2]:02d}"
                   for name, date in rank_dict.items()}
    pivot_display = {name: f"{date[0]:04d}-{date[1]:02d}"
                    for name, date in pivot_dict.items()}

    # Dropdowns
    col1, col2, col3 = st.columns(3)

    with col1:
        current_rank_file = st.selectbox(
            "📊 Current Rank Date",
            options=[name for name, _ in sorted_ranks],
            format_func=lambda x: rank_display[x],
            index=0
        )

    with col2:
        prev_rank_file = st.selectbox(
            "📊 Previous Rank Date",
            options=[name for name, _ in sorted_ranks],
            format_func=lambda x: rank_display[x],
            index=1 if len(sorted_ranks) > 1 else 0
        )

    # Auto-match pivot to current rank
    current_rank_date = rank_dict[current_rank_file]
    matched_pivot = match_pivot_to_rank(current_rank_date, pivot_dict)
    default_pivot_index = [name for name, _ in sorted_pivots].index(matched_pivot) if matched_pivot else 0

    with col3:
        pivot_file = st.selectbox(
            "🏦 Pivot File",
            options=[name for name, _ in sorted_pivots],
            format_func=lambda x: pivot_display[x],
            index=default_pivot_index
        )

    # Display selected dates
    st.info(f"**PF Rank:** {rank_display[current_rank_file]} | **Pivot File:** {pivot_display[pivot_file]}")

    # Load selected data
    rank_current = load_rank_data(current_rank_file)
    rank_prev = load_rank_data(prev_rank_file)

    # Build tables
    with st.spinner("Loading data..."):
        rank_rows = build_theme_rank_table(theme_map, rank_current, rank_prev, pf_symbols, all_themes)
        mf_rows = build_mf_theme_table_from_pivot(pivot_file, theme_map, pf_symbols, all_themes)
        combined_rows = build_combined_theme_table(rank_rows, mf_rows, all_themes)

    # Render combined table
    combined_html = render_combined_table(combined_rows, latest_date_str=rank_display[current_rank_file])

    # Add CSS
    st.markdown("""
    <style>
    .tp-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 13px;
    }
    .tp-table th {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 12px;
        text-align: left;
        font-weight: 700;
        border-bottom: 2px solid #667eea;
    }
    .tp-table td {
        padding: 12px;
        border-bottom: 1px solid #e9ecef;
    }
    .tp-table tr:nth-child(even) {
        background: #f8f9fa;
    }
    .tp-table tr:hover {
        background: #e7f3ff !important;
    }
    .col-theme {
        font-weight: 600;
        color: #2c3e50;
    }
    .col-median {
        text-align: right;
        font-weight: 600;
    }
    .col-list {
        color: #495057;
    }
    .col-bb {
        text-align: right;
        color: #495057;
    }
    .delta-up {
        color: #28a745;
        font-weight: 700;
    }
    .delta-down {
        color: #dc3545;
        font-weight: 700;
    }
    .delta-flat {
        color: #6c757d;
        font-weight: 600;
    }
    .sub-header {
        font-size: 10px;
        padding: 8px 12px;
        background: linear-gradient(180deg, #e9ecef 0%, #dee2e6 100%);
    }
    </style>
    """, unsafe_allow_html=True)

    # Display table
    st.markdown(combined_html, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
