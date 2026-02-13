"""
Combined View Processor
Merges Ranks and MF BB data into a single view by theme with separate columns
"""

from pathlib import Path
import pandas as pd
import re


def parse_symbols_from_html(html_str: str):
    """
    Parse HTML string to extract symbols in order with their data
    Returns: OrderedDict of {symbol: html_fragment}
    Example: "SBIN 4 <span...><br/>AXIS 3 <span...>" or "SBIN(8,4,4)<br/>AXIS(5,3,2)"
    Returns: {'SBIN': '4 <span...>', 'AXIS': '3 <span...>'} or {'SBIN': '(8,4,4)', 'AXIS': '(5,3,2)'}
    """
    from collections import OrderedDict

    if not html_str or not html_str.strip():
        return OrderedDict()

    symbols = OrderedDict()

    # Split by <br/> to get individual symbol entries (one per line)
    parts = re.split(r'<br\s*/?>', html_str, flags=re.IGNORECASE)

    for part in parts:
        part = part.strip()
        if not part:
            continue

        # Extract symbol - can be followed by space or opening parenthesis
        # Pattern 1: "SYMBOL(...)" - BB format
        match = re.match(r'^([A-Z0-9&\-]+)(\(.+?\))$', part)
        if match:
            symbol = match.group(1)
            value_html = match.group(2)
            symbols[symbol] = value_html
            continue

        # Pattern 2: "SYMBOL value..." - Rank format
        match = re.match(r'^([A-Z0-9&\-]+)\s+(.+)$', part)
        if match:
            symbol = match.group(1)
            value_html = match.group(2).strip()
            symbols[symbol] = value_html

    return symbols


def reorder_bb_to_match_rank(rank_html: str, bb_html: str):
    """
    Reorder BB HTML to match the symbol order in Rank HTML
    """
    if not rank_html or not rank_html.strip():
        return bb_html

    if not bb_html or not bb_html.strip():
        return ""

    # Parse both
    rank_symbols = parse_symbols_from_html(rank_html)
    bb_symbols = parse_symbols_from_html(bb_html)

    # Build BB in same order as Rank
    reordered_parts = []

    for symbol in rank_symbols.keys():
        if symbol in bb_symbols:
            # BB values are in format "(val1,val2,val3)" - include them with symbol
            reordered_parts.append(f"{symbol}{bb_symbols[symbol]}")

    # Add any BB symbols not in Rank (at the end)
    for symbol, value_html in bb_symbols.items():
        if symbol not in rank_symbols:
            reordered_parts.append(f"{symbol}{value_html}")

    return "<br/>".join(reordered_parts)


def build_combined_theme_table(
    theme_rows_data,  # Data from build_theme_table
    mf_rows_data,     # Data from build_mf_theme_table
    selected_themes
):
    """
    Build combined table showing Ranks and BB flags in separate columns

    Structure:
    - Theme
    - Median (Rank only)
    - Portfolio: Rank | BB (two sub-columns)
    - Others: Rank | BB (two sub-columns)
    """

    # Convert lists to dictionaries keyed by theme
    theme_dict = {row['Theme']: row for row in theme_rows_data}
    mf_dict = {row['Theme']: row for row in mf_rows_data}

    rows = []

    for theme in selected_themes:
        theme_data = theme_dict.get(theme, {})
        mf_data = mf_dict.get(theme, {})

        # Get rank median only
        rank_median = theme_data.get('Median (Latest Δ)', '')

        # Get rank HTML (this determines the order)
        portfolio_rank_html = theme_data.get('Portfolio', '')
        others_rank_html = theme_data.get('Others', '')

        # Get BB HTML
        portfolio_bb_html = mf_data.get('Portfolio', '')
        others_bb_html = mf_data.get('Others', '')

        # Reorder BB to match Rank symbol order
        portfolio_bb_reordered = reorder_bb_to_match_rank(portfolio_rank_html, portfolio_bb_html)
        others_bb_reordered = reorder_bb_to_match_rank(others_rank_html, others_bb_html)

        row = {
            'Theme': theme,
            'Rank_Median': rank_median,
            'Portfolio_Rank': portfolio_rank_html,
            'Portfolio_BB': portfolio_bb_reordered,
            'Others_Rank': others_rank_html,
            'Others_BB': others_bb_reordered
        }
        rows.append(row)

    return rows


def render_combined_table(rows, latest_date_str: str = "2026-01-31"):
    """Render combined table as HTML with separate Rank and BB columns"""

    html_parts = []

    html_parts.append(f"<div style='margin:4px 0 8px 0;color:#666;font-size:12px;'>Combined View: Ranks + MF BB Signals - As of {latest_date_str}</div>")
    html_parts.append("<table class='tp-table combined-table'>")

    # Column groups
    html_parts.append("""
        <colgroup>
            <col style='width:10%'>
            <col style='width:6%'>
            <col style='width:21%'>
            <col style='width:21%'>
            <col style='width:21%'>
            <col style='width:21%'>
        </colgroup>
    """)

    # Table header with grouped sub-columns
    html_parts.append("""
        <thead>
            <tr>
                <th rowspan="2">Theme</th>
                <th rowspan="2">Median<br/>(Rank Δ)</th>
                <th colspan="2">Portfolio</th>
                <th colspan="2">Others</th>
            </tr>
            <tr>
                <th class="sub-header">Rank</th>
                <th class="sub-header">BB</th>
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
        portfolio_rank = row.get('Portfolio_Rank', '')
        portfolio_bb = row.get('Portfolio_BB', '')
        others_rank = row.get('Others_Rank', '')
        others_bb = row.get('Others_BB', '')

        html_parts.append(f"""
            <tr>
                <td class='col-theme'>{theme}</td>
                <td class='col-median'>{rank_median}</td>
                <td class='col-list'>{portfolio_rank}</td>
                <td class='col-bb'>{portfolio_bb}</td>
                <td class='col-list'>{others_rank}</td>
                <td class='col-bb'>{others_bb}</td>
            </tr>
        """)

    html_parts.append("</tbody>")
    html_parts.append("</table>")

    return "".join(html_parts)
