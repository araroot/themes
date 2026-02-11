"""
Mutual Fund Movement Processor
Processes Dec25_pivot_features.xlsx to show mutual fund buy/sell movements
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


def get_top_movers(df: pd.DataFrame, latest_col: str, prev_col: str, top_n: int = 50):
    """Get stocks with biggest changes in bb_ values"""
    if prev_col is None:
        return []

    # Calculate aggregate change per symbol across all fund families
    df['bb_delta'] = df[latest_col] - df[prev_col]

    # Group by symbol and get median bb values and max delta
    symbol_summary = df.groupby('Symbol').agg({
        latest_col: 'median',
        prev_col: 'median',
        'bb_delta': 'median',
        'cmp': 'first',
        'FundFamily': 'count'  # Count how many funds hold it
    }).reset_index()

    symbol_summary.columns = ['Symbol', 'bb_latest', 'bb_prev', 'bb_delta', 'cmp', 'fund_count']

    # Sort by absolute delta (biggest movers)
    symbol_summary['abs_delta'] = symbol_summary['bb_delta'].abs()
    symbol_summary = symbol_summary.sort_values('abs_delta', ascending=False)

    return symbol_summary.head(top_n)


def build_mf_table(df: pd.DataFrame, latest_col: str, prev_col: str, portfolio_symbols: set, top_n: int = 50):
    """Build mutual fund movement table showing top movers"""

    if latest_col is None:
        return []

    # Get top movers
    top_movers = get_top_movers(df, latest_col, prev_col, top_n)

    rows = []
    for _, stock in top_movers.iterrows():
        symbol = stock['Symbol']
        bb_latest = stock['bb_latest']
        bb_prev = stock['bb_prev']
        bb_delta = stock['bb_delta']
        fund_count = int(stock['fund_count'])
        cmp = stock['cmp']

        # Get fund family details for this symbol
        symbol_df = df[df['Symbol'] == symbol]

        # Group by fund family and show their bb values
        fund_details = []
        for _, row in symbol_df.iterrows():
            fund = row['FundFamily']
            latest_val = row[latest_col]
            prev_val = row[prev_col] if prev_col else None

            if pd.notna(latest_val) and latest_val != 0:
                if pd.notna(prev_val):
                    delta = latest_val - prev_val
                    if delta != 0:
                        arrow = "▲" if delta > 0 else "▼"
                        klass = "delta-up" if delta > 0 else "delta-down"
                        fund_details.append(f"{fund} {latest_val:.0f} <span class='{klass}'>({arrow}{abs(delta):.0f})</span>")
                    else:
                        fund_details.append(f"{fund} {latest_val:.0f} <span class='delta-flat'>(•0)</span>")
                else:
                    fund_details.append(f"{fund} {latest_val:.0f}")

        # Median bb value with delta
        if pd.notna(bb_prev):
            arrow = "▲" if bb_delta > 0 else "▼" if bb_delta < 0 else "•"
            klass = "delta-up" if bb_delta > 0 else "delta-down" if bb_delta < 0 else "delta-flat"
            median_cell = f"{bb_latest:.1f} <span class='{klass}'>({arrow}{abs(bb_delta):.1f})</span>"
        else:
            median_cell = f"{bb_latest:.1f}"

        is_portfolio = symbol in portfolio_symbols
        row_data = {
            "Symbol": symbol,
            "Median BB (Δ)": median_cell,
            "Funds": fund_count,
            "Price": f"₹{cmp:.1f}" if pd.notna(cmp) else "—",
            "Fund Details": ", ".join(fund_details[:10]),  # Limit to top 10 funds
            "IsPortfolio": is_portfolio
        }
        rows.append(row_data)

    return rows


def render_mf_table(rows, latest_date_str: str = "Dec 2025"):
    """Render MF table as HTML"""

    cols = ["Symbol", "Median BB (Δ)", "Funds", "Price", "Fund Details"]

    colgroup = (
        "<colgroup>"
        "<col style='width:10%'>"
        "<col style='width:12%'>"
        "<col style='width:8%'>"
        "<col style='width:10%'>"
        "<col style='width:60%'>"
        "</colgroup>"
    )

    head_cells = "".join(f"<th>{c}</th>" for c in cols)
    body_rows = []

    for r in rows:
        symbol = r.get("Symbol", "")
        median = r.get("Median BB (Δ)", "")
        funds = r.get("Funds", "")
        price = r.get("Price", "")
        details = r.get("Fund Details", "")
        is_portfolio = r.get("IsPortfolio", False)

        # Highlight portfolio stocks
        row_class = " class='portfolio-row'" if is_portfolio else ""

        cells = [
            f"<td class='col-theme'>{symbol}</td>",
            f"<td class='col-median'>{median}</td>",
            f"<td class='col-median'>{funds}</td>",
            f"<td class='col-median'>{price}</td>",
            f"<td class='col-list'>{details}</td>",
        ]
        body_rows.append(f"<tr{row_class}>" + "".join(cells) + "</tr>")

    html = (
        f"<div style='margin:4px 0 8px 0;color:#666;font-size:12px;'>Mutual Fund Buy/Sell Signals - {latest_date_str}</div>"
        "<table class='tp-table'>"
        f"{colgroup}"
        f"<thead><tr>{head_cells}</tr></thead>"
        f"<tbody>{''.join(body_rows)}</tbody>"
        "</table>"
    )
    return html
