"""
Combined View Processor
Merges Ranks and MF BB data into a single view by theme with separate columns
"""

from pathlib import Path
import pandas as pd
import re


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

        # Parse and split portfolio data
        portfolio_rank_html = theme_data.get('Portfolio', '')
        portfolio_bb_html = mf_data.get('Portfolio', '')

        # Parse and split others data
        others_rank_html = theme_data.get('Others', '')
        others_bb_html = mf_data.get('Others', '')

        row = {
            'Theme': theme,
            'Rank_Median': rank_median,
            'Portfolio_Rank': portfolio_rank_html,
            'Portfolio_BB': portfolio_bb_html,
            'Others_Rank': others_rank_html,
            'Others_BB': others_bb_html
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
                <td class='col-list'>{portfolio_bb}</td>
                <td class='col-list'>{others_rank}</td>
                <td class='col-list'>{others_bb}</td>
            </tr>
        """)

    html_parts.append("</tbody>")
    html_parts.append("</table>")

    return "".join(html_parts)
