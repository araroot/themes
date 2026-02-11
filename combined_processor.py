"""
Combined View Processor
Merges Ranks and MF BB data into a single view by theme
"""

from pathlib import Path
import pandas as pd


def build_combined_theme_table(
    theme_rows_data,  # Data from build_theme_table
    mf_rows_data,     # Data from build_mf_theme_table
    selected_themes
):
    """
    Build combined table showing both Ranks and BB flags for each stock

    Structure:
    - Theme
    - Median: Rank (Δ) | BB (Δ)
    - Portfolio: Shows both Rank and BB for each stock
    - Others: Shows both Rank and BB for each stock
    """

    # Convert lists to dictionaries keyed by theme
    theme_dict = {row['Theme']: row for row in theme_rows_data}
    mf_dict = {row['Theme']: row for row in mf_rows_data}

    rows = []

    for theme in selected_themes:
        theme_data = theme_dict.get(theme, {})
        mf_data = mf_dict.get(theme, {})

        # Combine median values
        rank_median = theme_data.get('Median (Latest Δ)', '')
        bb_median = mf_data.get('Median BB (Latest Δ)', '')

        # Parse portfolio and others data to combine rank and BB
        portfolio_combined = merge_rank_and_bb(
            theme_data.get('Portfolio', ''),
            mf_data.get('Portfolio', '')
        )

        others_combined = merge_rank_and_bb(
            theme_data.get('Others', ''),
            mf_data.get('Others', '')
        )

        row = {
            'Theme': theme,
            'Rank_Median': rank_median,
            'BB_Median': bb_median,
            'Portfolio': portfolio_combined,
            'Others': others_combined
        }
        rows.append(row)

    return rows


def merge_rank_and_bb(rank_html: str, bb_html: str):
    """
    Merge rank and BB HTML strings by extracting symbols and combining
    Returns HTML with format: SYMBOL Rank:X(ΔY) BB:Z(ΔW)
    """
    if not rank_html and not bb_html:
        return ""

    # Parse symbols from both HTML strings
    rank_symbols = parse_symbols_from_html(rank_html)
    bb_symbols = parse_symbols_from_html(bb_html)

    # Get all unique symbols
    all_symbols = set(rank_symbols.keys()) | set(bb_symbols.keys())

    combined_parts = []
    for symbol in sorted(all_symbols):
        rank_part = rank_symbols.get(symbol, '')
        bb_part = bb_symbols.get(symbol, '')

        if rank_part and bb_part:
            # Both rank and BB available
            combined = f"<strong>{symbol}</strong> R:{rank_part} BB:{bb_part}"
        elif rank_part:
            # Only rank available
            combined = f"<strong>{symbol}</strong> R:{rank_part} BB:—"
        else:
            # Only BB available
            combined = f"<strong>{symbol}</strong> R:— BB:{bb_part}"

        combined_parts.append(combined)

    return ", ".join(combined_parts)


def parse_symbols_from_html(html_str: str):
    """
    Parse HTML string to extract symbol -> value mapping
    Example: "SBIN 4 <span class='delta-up'>(▲5)</span>, AXISBANK 3 <span...>"
    Returns: {'SBIN': "4 <span class='delta-up'>(▲5)</span>", 'AXISBANK': ...}
    """
    if not html_str:
        return {}

    import re

    symbols = {}

    # Split by comma
    parts = html_str.split(', ')

    for part in parts:
        # Extract symbol (first word before space and number)
        match = re.match(r'([A-Z&\-]+)\s+(.+)', part.strip())
        if match:
            symbol = match.group(1)
            value_and_delta = match.group(2)
            symbols[symbol] = value_and_delta

    return symbols


def render_combined_table(rows, latest_date_str: str = "2026-01-31"):
    """Render combined table as HTML"""

    html_parts = []

    html_parts.append(f"<div style='margin:4px 0 8px 0;color:#666;font-size:12px;'>Combined View: Ranks + MF BB Signals - As of {latest_date_str}</div>")
    html_parts.append("<table class='tp-table combined-table'>")

    # Column groups
    html_parts.append("""
        <colgroup>
            <col style='width:12%'>
            <col style='width:8%'>
            <col style='width:8%'>
            <col style='width:36%'>
            <col style='width:36%'>
        </colgroup>
    """)

    # Table header with sub-columns
    html_parts.append("""
        <thead>
            <tr>
                <th rowspan="2">Theme</th>
                <th colspan="2">Median (Latest Δ)</th>
                <th rowspan="2">Portfolio</th>
                <th rowspan="2">Others</th>
            </tr>
            <tr>
                <th class="sub-header">Rank</th>
                <th class="sub-header">BB</th>
            </tr>
        </thead>
    """)

    # Table body
    html_parts.append("<tbody>")

    for row in rows:
        theme = row.get('Theme', '')
        rank_median = row.get('Rank_Median', '')
        bb_median = row.get('BB_Median', '')
        portfolio = row.get('Portfolio', '')
        others = row.get('Others', '')

        html_parts.append(f"""
            <tr>
                <td class='col-theme'>{theme}</td>
                <td class='col-median'>{rank_median}</td>
                <td class='col-median'>{bb_median}</td>
                <td class='col-list'>{portfolio}</td>
                <td class='col-list'>{others}</td>
            </tr>
        """)

    html_parts.append("</tbody>")
    html_parts.append("</table>")

    return "".join(html_parts)
