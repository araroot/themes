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
    <title>Theme Constituents</title>
    <style>
      body {{ font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica, Arial, sans-serif; margin: 24px; }}
      h1 {{ font-size: 20px; margin: 0 0 8px 0; }}
    </style>
  </head>
  <body>
    <h1>Theme Constituents</h1>
    {html_body}
  </body>
</html>
"""

    docs = Path("/Users/raviaranke/Desktop/themes/docs")
    docs.mkdir(exist_ok=True)
    (docs / "index.html").write_text(full_html)
    print("Wrote", docs / "index.html")


if __name__ == "__main__":
    main()
