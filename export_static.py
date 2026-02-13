from pathlib import Path

import pandas as pd

from app import (
    DATA_PATH_DEFAULT,
    build_theme_map,
    build_theme_table,
    get_latest_prev_dates,
    normalize_theme_name,
    render_table,
    theme_medians,
)

from mf_processor import (
    load_mf_data,
    get_latest_prev_bb_cols,
    build_mf_theme_table,
    render_mf_theme_table,
)

from combined_processor import (
    build_combined_theme_table,
    render_combined_table,
)


def is_real_symbol(val: str) -> bool:
    s = str(val).strip()
    if not s or s.lower() == "nan":
        return False
    s_lower = s.lower()
    if s_lower in {"average rank", "avg rank", "kpi avg rank", "kpi average rank"}:
        return False
    if "avg rank" in s_lower or "average rank" in s_lower:
        return False
    if "kpi" in s_lower and "rank" in s_lower:
        return False
    return True


def main():
    # ========== RANKS TAB DATA ==========
    path = Path(DATA_PATH_DEFAULT)
    pf = pd.read_excel(path, sheet_name="PF_Ranks")
    th = pd.read_excel(path, sheet_name="theme_park")

    latest, prev = get_latest_prev_dates(pf, th)

    theme_map = build_theme_map(th)
    pf = pf.rename(columns={"Symbol / Rank": "Symbol"})
    pf["Symbol"] = pf["Symbol"].astype(str).str.strip()
    pf_symbols = {s for s in pf["Symbol"].dropna() if is_real_symbol(s)}

    latest_median = theme_medians(th, latest).sort_values()
    all_themes = latest_median.index.tolist()

    # Include all themes when exporting (includes non-portfolio)
    selected = all_themes

    rows = build_theme_table(
        th,
        latest,
        prev,
        selected,
        pf_symbols,
        latest_median,
        show_non_portfolio=True,
    )

    ranks_html_body = render_table(rows, True, latest, font_size=12, date_font_size=12)

    # ========== MF MOVES TAB DATA ==========
    mf_pivot_date = None
    try:
        mf_df, mf_pivot_date = load_mf_data()
        latest_bb, prev_bb = get_latest_prev_bb_cols(mf_df)

        if latest_bb:
            # Use same theme structure as Ranks tab
            mf_rows = build_mf_theme_table(
                mf_df,
                latest_bb,
                prev_bb,
                selected,  # Same themes in same order as Ranks
                theme_map,
                pf_symbols
            )
            mf_html_body = render_mf_theme_table(mf_rows, latest_date_str=latest_bb.replace("bb_", "").replace("25", " 2025"))

            # ========== COMBINED TAB DATA ==========
            combined_rows = build_combined_theme_table(rows, mf_rows, selected)
            combined_html_body = render_combined_table(combined_rows, latest_date_str=f"{latest:%Y-%m-%d}")
        else:
            mf_html_body = "<p>No MF data available</p>"
            combined_html_body = "<p>No MF data available for combined view</p>"
    except Exception as e:
        print(f"Warning: Could not load MF data: {e}")
        mf_html_body = "<p>MF data not available</p>"
        combined_html_body = "<p>MF data not available for combined view</p>"

    # ========== GENERATE TABBED HTML ==========
    full_html = f"""<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Investment Dashboard</title>
    <style>
      * {{
        box-sizing: border-box;
      }}

      body {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        margin: 0;
        padding: 24px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
      }}

      .container {{
        max-width: 1400px;
        margin: 0 auto;
        background: white;
        border-radius: 12px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        overflow: hidden;
      }}

      .header {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 32px 40px 0 40px;
        border-bottom: 4px solid #5568d3;
      }}

      h1 {{
        font-size: 32px;
        margin: 0 0 8px 0;
        font-weight: 700;
        letter-spacing: -0.5px;
      }}

      .header-content {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 16px;
        margin-bottom: 24px;
      }}

      .header-left {{
        flex: 1;
      }}

      .header-right {{
        display: flex;
        gap: 12px;
        align-items: center;
      }}

      .date-badge {{
        display: inline-block;
        background: rgba(255,255,255,0.2);
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 500;
        backdrop-filter: blur(10px);
      }}

      .refresh-btn {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(255,255,255,0.9);
        color: #667eea;
        padding: 10px 20px;
        border-radius: 24px;
        text-decoration: none;
        font-size: 14px;
        font-weight: 600;
        transition: all 0.3s ease;
        border: 2px solid transparent;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
      }}

      .refresh-btn:hover {{
        background: white;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        border-color: rgba(255,255,255,0.3);
      }}

      .refresh-btn:active {{
        transform: translateY(0);
      }}

      /* Tabs */
      .tabs {{
        display: flex;
        gap: 4px;
        padding: 0;
        margin: 0;
      }}

      .tab {{
        padding: 12px 28px;
        background: rgba(255,255,255,0.1);
        color: rgba(255,255,255,0.7);
        border: none;
        cursor: pointer;
        font-size: 15px;
        font-weight: 600;
        transition: all 0.3s ease;
        border-radius: 8px 8px 0 0;
        position: relative;
      }}

      .tab:hover {{
        background: rgba(255,255,255,0.15);
        color: rgba(255,255,255,0.9);
      }}

      .tab.active {{
        background: white;
        color: #667eea;
      }}

      .tab-content {{
        display: none;
        padding: 24px 40px 40px 40px;
        overflow-x: auto;
      }}

      .tab-content.active {{
        display: block;
      }}

      .table-container {{
        padding: 0;
      }}

      .tp-table {{
        width: 100%;
        table-layout: fixed;
        border-collapse: collapse;
        font-size: 13px;
        line-height: 1.5;
      }}

      .tp-table thead {{
        position: sticky;
        top: 0;
        z-index: 10;
      }}

      .tp-table th {{
        text-align: left;
        padding: 14px 16px;
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
        font-weight: 700;
        color: #2c3e50;
        text-transform: uppercase;
        font-size: 11px;
        letter-spacing: 0.5px;
        border-bottom: 2px solid #667eea;
        border-top: 1px solid #dee2e6;
      }}

      .tp-table tbody tr {{
        transition: all 0.2s ease;
        border-bottom: 1px solid #e9ecef;
      }}

      .tp-table tbody tr:nth-child(odd) {{
        background: #ffffff;
      }}

      .tp-table tbody tr:nth-child(even) {{
        background: #f8f9fa;
      }}

      .tp-table tbody tr:hover {{
        background: #e7f3ff !important;
        transform: scale(1.01);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
        cursor: pointer;
      }}

      .tp-table tbody tr.portfolio-row {{
        background: #fff3cd !important;
      }}

      .tp-table tbody tr.portfolio-row:hover {{
        background: #ffe69c !important;
      }}

      .tp-table td {{
        vertical-align: top;
        padding: 14px 16px;
      }}

      .tp-table .col-median {{
        text-align: right;
        white-space: nowrap;
        color: #2c3e50;
        font-weight: 600;
        font-size: 14px;
      }}

      .tp-table .col-theme {{
        font-weight: 600;
        color: #2c3e50;
        font-size: 14px;
      }}

      .tp-table .col-list {{
        color: #495057;
        font-weight: 400;
        white-space: normal;
        word-break: break-word;
        line-height: 1.6;
      }}

      .tp-table .col-bb {{
        text-align: right;
        color: #495057;
        font-weight: 400;
        white-space: normal;
        word-break: break-word;
        line-height: 1.6;
        font-family: 'Courier New', Courier, monospace;
      }}

      .delta-up {{
        color: #28a745;
        font-weight: 700;
      }}

      .delta-down {{
        color: #dc3545;
        font-weight: 700;
      }}

      .delta-flat {{
        color: #6c757d;
        font-weight: 600;
      }}

      .delta-unk {{
        color: #6c757d;
        font-weight: 400;
      }}

      /* Combined table styles */
      .combined-table .sub-header {{
        font-size: 10px;
        padding: 8px 12px;
        background: linear-gradient(180deg, #e9ecef 0%, #dee2e6 100%);
        border-bottom: 1px solid #667eea;
      }}

      .combined-table strong {{
        color: #2c3e50;
        font-weight: 600;
      }}

      .combined-table .col-bb {{
        text-align: right;
        color: #495057;
        font-weight: 400;
        white-space: normal;
        word-break: break-word;
        line-height: 1.6;
        font-family: 'Courier New', Courier, monospace;
      }}

      @media (max-width: 768px) {{
        body {{
          padding: 12px;
        }}

        .header {{
          padding: 24px 20px 0 20px;
        }}

        .header-content {{
          flex-direction: column;
          align-items: flex-start;
        }}

        .header-right {{
          width: 100%;
        }}

        .refresh-btn {{
          width: 100%;
          justify-content: center;
        }}

        h1 {{
          font-size: 24px;
        }}

        .tabs {{
          flex-direction: column;
          gap: 8px;
        }}

        .tab {{
          width: 100%;
          border-radius: 8px;
        }}

        .tab-content {{
          padding: 16px 20px 24px 20px;
        }}

        .tp-table {{
          font-size: 11px;
        }}

        .tp-table th,
        .tp-table td {{
          padding: 10px 12px;
        }}
      }}
    </style>
  </head>
  <body>
    <div class="container">
      <div class="header">
        <div class="header-content">
          <div class="header-left">
            <h1>📊 Investment Dashboard</h1>
            <span class="date-badge">📅 As of {latest:%Y-%m-%d}</span>
            {f'<span class="date-badge">📊 Pivot File: {mf_pivot_date}</span>' if mf_pivot_date else ''}
          </div>
          <div class="header-right">
            <a href="https://github.com/araroot/themes/actions/workflows/update-dashboard.yml"
               target="_blank"
               class="refresh-btn"
               title="Click to refresh data from Google Drive">
              🔄 Refresh Data
            </a>
          </div>
        </div>

        <!-- Tabs -->
        <div class="tabs">
          <button class="tab active" onclick="switchTab(event, 'ranks')">📈 Ranks</button>
          <button class="tab" onclick="switchTab(event, 'mf-moves')">🏦 MF Moves</button>
          <button class="tab" onclick="switchTab(event, 'combined')">🔀 Combined</button>
        </div>
      </div>

      <!-- Ranks Tab Content -->
      <div id="ranks" class="tab-content active">
        {ranks_html_body}
      </div>

      <!-- MF Moves Tab Content -->
      <div id="mf-moves" class="tab-content">
        {mf_html_body}
      </div>

      <!-- Combined Tab Content -->
      <div id="combined" class="tab-content">
        {combined_html_body}
      </div>
    </div>

    <script>
      function switchTab(evt, tabName) {{
        // Hide all tab contents
        var tabContents = document.getElementsByClassName("tab-content");
        for (var i = 0; i < tabContents.length; i++) {{
          tabContents[i].classList.remove("active");
        }}

        // Remove active class from all tabs
        var tabs = document.getElementsByClassName("tab");
        for (var i = 0; i < tabs.length; i++) {{
          tabs[i].classList.remove("active");
        }}

        // Show current tab and mark button as active
        document.getElementById(tabName).classList.add("active");
        evt.currentTarget.classList.add("active");
      }}
    </script>
  </body>
</html>
"""

    docs = Path("/Users/raviaranke/Desktop/themes/docs")
    docs.mkdir(exist_ok=True)
    (docs / "index.html").write_text(full_html)
    print("Wrote", docs / "index.html")


if __name__ == "__main__":
    main()
