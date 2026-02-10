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

    html_body = render_table(rows, True, latest, font_size=12, date_font_size=12)
    full_html = f"""<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Theme Constituents Dashboard</title>
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
        padding: 32px 40px;
        border-bottom: 4px solid #5568d3;
      }}

      h1 {{
        font-size: 32px;
        margin: 0 0 8px 0;
        font-weight: 700;
        letter-spacing: -0.5px;
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

      .table-container {{
        padding: 24px 40px 40px 40px;
        overflow-x: auto;
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

      .delta-up {{
        color: #28a745;
        font-weight: 700;
        background: #d4edda;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 11px;
      }}

      .delta-down {{
        color: #dc3545;
        font-weight: 700;
        background: #f8d7da;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 11px;
      }}

      .delta-flat {{
        color: #6c757d;
        font-weight: 600;
        background: #e2e3e5;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 11px;
      }}

      .delta-unk {{
        color: #6c757d;
        font-weight: 400;
      }}

      @media (max-width: 768px) {{
        body {{
          padding: 12px;
        }}

        .header {{
          padding: 24px 20px;
        }}

        h1 {{
          font-size: 24px;
        }}

        .table-container {{
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
        <h1>📊 Theme Constituents Dashboard</h1>
        <span class="date-badge">📅 As of {latest:%Y-%m-%d}</span>
      </div>
      <div class="table-container">
        {html_body}
      </div>
    </div>
  </body>
</html>
"""

    docs = Path("/Users/raviaranke/Desktop/themes/docs")
    docs.mkdir(exist_ok=True)
    (docs / "index.html").write_text(full_html)
    print("Wrote", docs / "index.html")


if __name__ == "__main__":
    main()
