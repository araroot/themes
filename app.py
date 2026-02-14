import datetime as dt
from pathlib import Path

import pandas as pd
import streamlit as st

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

DATA_PATH_DEFAULT = Path("/Users/raviaranke/Desktop/themes/PF_Ranks.xlsx")


def normalize_theme_name(value) -> str:
    s = str(value).strip()
    if not s or s.lower() == "nan":
        return s
    # Keep acronyms / code-like tokens uppercase
    keep_upper = {"nbfc", "psu", "mnc", "it", "ai", "ev", "kpi", "fmcg"}

    def norm_token(tok: str) -> str:
        if any(ch.isdigit() for ch in tok):
            return tok
        if tok.isupper():
            return tok
        if tok.lower() in keep_upper:
            return tok.upper()
        return tok[:1].upper() + tok[1:].lower() if tok else tok

    parts = s.split()
    return " ".join(norm_token(p) for p in parts)


def _date_cols(df: pd.DataFrame) -> list:
    return [
        c
        for c in df.columns
        if isinstance(c, (pd.Timestamp, dt.datetime, dt.date))
    ]


@st.cache_data
def load_data(path: str):
    pf = pd.read_excel(path, sheet_name="PF_Ranks")
    th = pd.read_excel(path, sheet_name="theme_park")
    return pf, th


@st.cache_data
def load_data_codex(path: str):
    pf = pd.read_excel(path, sheet_name="PF_Ranks")
    th_codex = pd.read_excel(path, sheet_name="tpark_codex")
    return pf, th_codex


def build_theme_map(th: pd.DataFrame) -> pd.DataFrame:
    th = th.rename(columns={"Symbol / Rank": "Symbol"})
    th["Symbol"] = th["Symbol"].astype(str).str.strip()

    current_theme = None
    rows = []
    for _, row in th.iterrows():
        sym = str(row["Symbol"]).strip() if pd.notna(row["Symbol"]) else None
        theme_cell = row["Theme"]
        if pd.isna(theme_cell) and sym:
            current_theme = normalize_theme_name(sym)
            continue
        if pd.notna(theme_cell):
            current_theme = normalize_theme_name(str(theme_cell).strip())
        if sym and current_theme and sym.lower() != "nan":
            rows.append((sym, current_theme))
    return pd.DataFrame(rows, columns=["Symbol", "Theme"])


def build_theme_map_codex(th_codex: pd.DataFrame) -> pd.DataFrame:
    """Build theme map from tpark_codex format (Symbol, Theme columns directly)"""
    df = th_codex[["Symbol", "Theme"]].copy()
    df = df[df["Symbol"].notna() & df["Theme"].notna()]
    df["Symbol"] = df["Symbol"].astype(str).str.strip()
    df["Theme"] = df["Theme"].apply(lambda v: normalize_theme_name(v) if pd.notna(v) else v)
    return df


def get_latest_prev_dates(pf: pd.DataFrame, th: pd.DataFrame):
    pf_dates = _date_cols(pf)
    th_dates = _date_cols(th)
    latest = min(max(pf_dates), max(th_dates))
    prev_dates = sorted([d for d in pf_dates if d < latest])
    prev = prev_dates[-1] if prev_dates else None
    return latest, prev


def theme_medians(th: pd.DataFrame, date_col) -> pd.Series:
    th = th.rename(columns={"Symbol / Rank": "Symbol"})
    th = th[["Symbol", "Theme", date_col]].copy()
    th["Theme"] = th["Theme"].apply(lambda v: normalize_theme_name(v) if pd.notna(v) else v)
    th = th[th["Theme"].notna()].rename(columns={date_col: "Rank"})
    th["Rank"] = pd.to_numeric(th["Rank"], errors="coerce")
    return th.groupby("Theme", dropna=True)["Rank"].median()


def theme_counts(th: pd.DataFrame, date_col) -> pd.Series:
    th = th.rename(columns={"Symbol / Rank": "Symbol"})
    th = th[["Symbol", "Theme", date_col]].copy()
    th["Theme"] = th["Theme"].apply(lambda v: normalize_theme_name(v) if pd.notna(v) else v)
    th = th[th["Theme"].notna()].rename(columns={date_col: "Rank"})
    th["Rank"] = pd.to_numeric(th["Rank"], errors="coerce")
    return th.dropna(subset=["Rank"])["Theme"].value_counts()


def portfolio_themes(pf: pd.DataFrame, theme_map: pd.DataFrame):
    pf = pf.rename(columns={"Symbol / Rank": "Symbol"})
    pf["Symbol"] = pf["Symbol"].astype(str).str.strip()
    symbols = set(pf["Symbol"].dropna())
    return sorted(theme_map[theme_map["Symbol"].isin(symbols)]["Theme"].unique())


def _rank_delta_text(prev_val, latest_val):
    if pd.isna(prev_val) or pd.isna(latest_val):
        return ""
    delta = latest_val - prev_val
    # Lower rank is better: use up arrow for improvement
    arrow = "▲" if delta < 0 else "▼" if delta > 0 else "•"
    return f"{arrow}{abs(delta):.0f}"


def build_theme_table(
    th: pd.DataFrame,
    latest,
    prev,
    selected_themes,
    portfolio_symbol_set,
    latest_median,
    show_non_portfolio: bool,
):
    th_latest = th.rename(columns={"Symbol / Rank": "Symbol"})
    th_latest = th_latest[["Symbol", "Theme", latest]].copy()
    th_latest["Theme"] = th_latest["Theme"].apply(lambda v: normalize_theme_name(v) if pd.notna(v) else v)
    th_latest = th_latest[th_latest["Theme"].notna()].rename(columns={latest: "Rank"})
    th_latest["Rank"] = pd.to_numeric(th_latest["Rank"], errors="coerce")
    th_latest["Symbol"] = th_latest["Symbol"].astype(str).str.strip()

    prev_ranks = None
    if prev is not None:
        prev_ranks = th.rename(columns={"Symbol / Rank": "Symbol"})
        prev_ranks = prev_ranks[["Symbol", "Theme", prev]].copy()
        prev_ranks["Theme"] = prev_ranks["Theme"].apply(lambda v: normalize_theme_name(v) if pd.notna(v) else v)
        prev_ranks = prev_ranks[prev_ranks["Theme"].notna()].rename(columns={prev: "Rank"})
        prev_ranks["Rank"] = pd.to_numeric(prev_ranks["Rank"], errors="coerce")
        prev_ranks["Symbol"] = prev_ranks["Symbol"].astype(str).str.strip()

    prev_median = theme_medians(th, prev) if prev is not None else pd.Series(dtype=float)

    rows = []
    for theme in selected_themes:
        latest_rows = th_latest[th_latest["Theme"] == theme].dropna(subset=["Rank"])
        latest_rows = latest_rows.sort_values("Rank", ascending=True)
        prev_rows = None
        if prev_ranks is not None:
            prev_rows = prev_ranks[prev_ranks["Theme"] == theme].dropna(subset=["Rank"])
            prev_rows = prev_rows.set_index("Symbol")["Rank"].to_dict()

        portfolio_cells = []
        other_cells = []
        for _, r in latest_rows.iterrows():
            sym = r["Symbol"]
            latest_rank = int(r["Rank"])
            prev_rank = None if prev_rows is None else prev_rows.get(sym)
            if pd.notna(prev_rank):
                delta = latest_rank - int(prev_rank)
                arrow = "▲" if delta < 0 else "▼" if delta > 0 else "•"
                klass = "delta-up" if delta < 0 else "delta-down" if delta > 0 else "delta-flat"
                delta_text = f"<span class='{klass}'>({arrow}{abs(delta)})</span>"
            else:
                delta_text = "<span class='delta-unk'>(?)</span>"
            label = f"{sym} {latest_rank} {delta_text}"
            if sym in portfolio_symbol_set:
                portfolio_cells.append(label)
            else:
                other_cells.append(label)

        latest_med = float(latest_median.get(theme, float("nan")))
        prev_med = float(prev_median.get(theme, float("nan"))) if prev is not None else float("nan")
        delta_text = _rank_delta_text(prev_med, latest_med)
        if pd.notna(latest_med) and pd.notna(prev_med):
            delta_val = latest_med - prev_med
            klass = "delta-up" if delta_val < 0 else "delta-down" if delta_val > 0 else "delta-flat"
            med_cell = f"{latest_med:.0f} <span class='{klass}'>({delta_text})</span>"
        else:
            med_cell = ""
        row = {
            "Theme": theme,
            "Median (Latest Δ)": med_cell,
            "Portfolio": "<br/>".join(portfolio_cells),
        }
        if show_non_portfolio:
            row["Others"] = "<br/>".join(other_cells)
        rows.append(row)
    return rows


def render_table(rows, show_non_portfolio: bool, latest_date, font_size=14, date_font_size=13) -> str:
    cols = ["Theme", "Median (Latest Δ)", "Portfolio"]
    if show_non_portfolio:
        cols.append("Others")

    colgroup = (
        "<colgroup>"
        "<col style='width:14%'>"
        "<col style='width:8%'>"
        "<col style='width:78%'>"
        "</colgroup>"
    )
    if show_non_portfolio:
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
        t = r.get("Theme", "")
        med = r.get("Median (Latest Δ)", "")
        port = r.get("Portfolio", "")
        oth = r.get("Others", "")
        cells = [
            f"<td class='col-theme'>{t}</td>",
            f"<td class='col-median'>{med}</td>",
            f"<td class='col-list'>{port}</td>",
        ]
        if show_non_portfolio:
            cells.append(f"<td class='col-list'>{oth}</td>")
        body_rows.append("<tr>" + "".join(cells) + "</tr>")

    html = (
        "<style>"
        f".tp-table{{width:100%;table-layout:fixed;border-collapse:collapse;font-size:{font_size}px;line-height:1.35;}}"
        ".tp-table th{text-align:left;padding:8px 10px;border-bottom:1px solid #e6e6e6;font-weight:600;color:#333;}"
        ".tp-table td{vertical-align:top;padding:8px 10px;border-bottom:1px solid #f0f0f0;}"
        ".tp-table .col-median{text-align:right;white-space:nowrap;color:#222;}"
        ".tp-table .col-theme{font-weight:500;color:#222;}"
        ".tp-table .col-list{color:#222;font-weight:400;white-space:normal;word-break:break-word;}"
        ".delta-up{color:#28a745;font-weight:700;}"
        ".delta-down{color:#dc3545;font-weight:700;}"
        ".delta-flat{color:#6c757d;font-weight:600;}"
        ".delta-unk{color:#6c757d;font-weight:400;}"
        "</style>"
        f"<div style='margin:4px 0 8px 0;color:#666;font-size:{date_font_size}px;'>As of {latest_date:%Y-%m-%d}</div>"
        "<table class='tp-table'>"
        f"{colgroup}"
        f"<thead><tr>{head_cells}</tr></thead>"
        f"<tbody>{''.join(body_rows)}</tbody>"
        "</table>"
    )
    return html


def main():
    st.set_page_config(page_title="Investment Dashboard", layout="wide")
    st.title("📊 Investment Dashboard")

    with st.expander("Data source", expanded=False):
        data_path = st.text_input("Excel path", str(DATA_PATH_DEFAULT))
        st.caption("Uses PF_Ranks and theme_park tabs.")

    pf, th = load_data(data_path)
    latest, prev = get_latest_prev_dates(pf, th)

    theme_map = build_theme_map(th)
    pf = pf.rename(columns={"Symbol / Rank": "Symbol"})
    pf["Symbol"] = pf["Symbol"].astype(str).str.strip()

    # Ignore non-portfolio summary rows
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

    pf_symbols = {s for s in pf["Symbol"].dropna() if is_real_symbol(s)}
    mapped_symbols = set(theme_map["Symbol"].dropna())
    missing_in_theme = sorted(s for s in pf_symbols if s not in mapped_symbols)
    if missing_in_theme:
        msg = "Portfolio symbols missing in theme_park: " + ", ".join(missing_in_theme)
        print("WARNING:", msg)
        st.warning(msg, icon="⚠️")
    pf_themes = portfolio_themes(pf, theme_map)
    pf_theme_set = set(pf_themes)

    latest_median = theme_medians(th, latest).sort_values()
    counts = theme_counts(th, latest)

    top20 = latest_median.head(20).index.tolist()
    bottom20 = latest_median.tail(20).index.tolist()
    all_themes = latest_median.index.tolist()

    # Load MF data
    mf_pivot_date = None
    mf_df = None
    try:
        mf_df, mf_pivot_date = load_mf_data()
        st.info(f"📊 Using Pivot File: {mf_pivot_date}")
    except Exception as e:
        st.warning(f"Could not load MF data: {e}")

    prev_text = prev.strftime("%Y-%m-%d") if prev else "N/A"
    st.caption(f"📅 Latest date: {latest:%Y-%m-%d} | Previous date: {prev_text}")

    st.subheader("Theme Selection")
    mode = st.radio(
        "Pick a theme set",
        ["Portfolio themes", "All themes", "Custom"],
        horizontal=True,
    )

    if mode == "Portfolio themes":
        selected = pf_themes
    elif mode == "All themes":
        selected = all_themes
    else:
        selected = st.multiselect("Choose themes", all_themes, default=pf_themes)

    # Sort selected themes by latest median rank (best to worst), NaNs last
    selected_series = pd.Series(selected).drop_duplicates()
    sort_key = latest_median.reindex(selected_series).astype(float)
    selected = (
        pd.DataFrame({"Theme": selected_series, "Median": sort_key.values})
        .sort_values(by="Median", ascending=True, na_position="last")
        ["Theme"]
        .tolist()
    )

    controls_left, controls_right = st.columns([1, 1])
    with controls_left:
        show_non_portfolio = st.checkbox("Show non-portfolio stocks", value=True)
    with controls_right:
        st.caption("Format: `SYM latest→prev` (lower is better)")

    # If showing non-portfolio stocks, include themes without portfolio holdings
    if show_non_portfolio and mode == "Portfolio themes":
        selected = all_themes

    # Load codex data
    try:
        _, th_codex = load_data_codex(data_path)
        theme_map_codex = build_theme_map_codex(th_codex)
        has_codex = True
    except Exception as e:
        print(f"Could not load codex data: {e}")
        has_codex = False

    # Create tabs
    if has_codex:
        tab1, tab2, tab3, tab4 = st.tabs(["📈 Ranks", "🏦 MF Moves", "🔀 Combined", "🎯 Combined (Codex)"])
    else:
        tab1, tab2, tab3 = st.tabs(["📈 Ranks", "🏦 MF Moves", "🔀 Combined"])

    # TAB 1: RANKS
    with tab1:
        st.subheader("Theme Constituents (Compact)")
        rows = build_theme_table(
            th,
            latest,
            prev,
            selected,
            pf_symbols,
            latest_median,
            show_non_portfolio,
        )
        html_display = render_table(rows, show_non_portfolio, latest, font_size=14, date_font_size=13)
        html_download = render_table(rows, show_non_portfolio, latest, font_size=12, date_font_size=12)
        st.download_button(
            label="Download HTML",
            data=html_download,
            file_name=f"theme_constituents_{latest:%Y-%m-%d}.html",
            mime="text/html",
        )
        st.markdown(html_display, unsafe_allow_html=True)

    # TAB 2: MF MOVES
    with tab2:
        if mf_df is not None:
            latest_bb, prev_bb = get_latest_prev_bb_cols(mf_df)
            if latest_bb:
                st.subheader("Mutual Fund Movement by Theme")
                mf_rows = build_mf_theme_table(
                    mf_df,
                    latest_bb,
                    prev_bb,
                    selected,
                    theme_map,
                    pf_symbols
                )
                mf_html = render_mf_theme_table(mf_rows, latest_date_str=latest_bb.replace("bb_", "").replace("25", " 2025").replace("26", " 2026"))
                st.markdown(mf_html, unsafe_allow_html=True)
            else:
                st.warning("No MF data columns found")
        else:
            st.warning("MF data not available")

    # TAB 3: COMBINED
    with tab3:
        if mf_df is not None:
            latest_bb, prev_bb = get_latest_prev_bb_cols(mf_df)
            if latest_bb:
                st.subheader("Combined View: Ranks + MF Moves")
                mf_rows = build_mf_theme_table(
                    mf_df,
                    latest_bb,
                    prev_bb,
                    selected,
                    theme_map,
                    pf_symbols
                )
                combined_rows = build_combined_theme_table(rows, mf_rows, selected)
                combined_html = render_combined_table(combined_rows, latest_date_str=f"{latest:%Y-%m-%d}")
                st.markdown(combined_html, unsafe_allow_html=True)
            else:
                st.warning("No MF data available for combined view")
        else:
            st.warning("MF data not available for combined view")

    # TAB 4: COMBINED (CODEX)
    if has_codex:
        with tab4:
            if mf_df is not None:
                latest_bb, prev_bb = get_latest_prev_bb_cols(mf_df)
                if latest_bb:
                    st.subheader("Combined View (Codex): Ranks + MF Moves")

                    # Get codex latest median and selected themes
                    latest_codex, prev_codex = get_latest_prev_dates(pf, th_codex)
                    latest_median_codex = theme_medians(th_codex, latest_codex).sort_values()
                    all_themes_codex = latest_median_codex.index.tolist()
                    pf_themes_codex = portfolio_themes(pf, theme_map_codex)

                    # Use same selection mode
                    if mode == "Portfolio themes":
                        selected_codex = pf_themes_codex
                    elif mode == "All themes":
                        selected_codex = all_themes_codex
                    else:
                        selected_codex = [t for t in selected if t in all_themes_codex]

                    # Sort by median rank
                    selected_series_codex = pd.Series(selected_codex).drop_duplicates()
                    sort_key_codex = latest_median_codex.reindex(selected_series_codex).astype(float)
                    selected_codex = (
                        pd.DataFrame({"Theme": selected_series_codex, "Median": sort_key_codex.values})
                        .sort_values(by="Median", ascending=True, na_position="last")
                        ["Theme"]
                        .tolist()
                    )

                    # Build tables using codex
                    rows_codex = build_theme_table(
                        th_codex,
                        latest_codex,
                        prev_codex,
                        selected_codex,
                        pf_symbols,
                        latest_median_codex,
                        show_non_portfolio,
                    )

                    mf_rows_codex = build_mf_theme_table(
                        mf_df,
                        latest_bb,
                        prev_bb,
                        selected_codex,
                        theme_map_codex,
                        pf_symbols
                    )

                    combined_rows_codex = build_combined_theme_table(rows_codex, mf_rows_codex, selected_codex)
                    combined_html_codex = render_combined_table(combined_rows_codex, latest_date_str=f"{latest_codex:%Y-%m-%d}")
                    st.markdown(combined_html_codex, unsafe_allow_html=True)
                else:
                    st.warning("No MF data available for codex combined view")
            else:
                st.warning("MF data not available for codex combined view")


if __name__ == "__main__":
    main()
