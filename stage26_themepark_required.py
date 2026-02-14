#!/usr/bin/env python3
import pandas as pd
from pathlib import Path

BASE = Path('/Users/raviaranke/Desktop/themes')
IN_MULTI = BASE / 'stage24_multi_theme_membership_full.csv'
IN_BASE = BASE / 'stage22_reports_overlay_full.csv'
IN_JAN26 = BASE / 'Jan26_pivot_features.xlsx'
IN_THEMEPARK = BASE / 'PF_Ranks.xlsx'
IN_ORDER = BASE / 'theme_order_reference.csv'

OUT_MULTI = BASE / 'stage26_multi_theme_membership_mcap_filtered_themepark_required.csv'
OUT_BACKFILL = BASE / 'stage26_theme_park_backfilled_symbols.csv'
OUT_REMOVED = BASE / 'stage26_removed_below_1000_non_themepark.csv'
OUT_SUMMARY = BASE / 'stage26_themepark_required_summary.md'
OUT_FINAL_2COL = BASE / 'theme_park_codex_final_2col.csv'

MCAP_THRESHOLD = 1000.0

# Explicit mapping for symbols present in original theme_park but missing in modeled universe.
THEMEPARK_BACKFILL_THEME = {
    'AURIONPRO': 'IT Products',
    'AWHCL': 'Recyclers',
    'BIRET': 'Real Estate - Commercial / Leasing',
    'BLS': 'Workforce & Outsourced Services',
    'CANTABIL': 'Organized Retail - Value & Fashion',
    'DEEPINDS': 'Hydrocarbon Upstream & Gas Infrastructure',
    'EASEMYTRIP': 'Tourism Ecosystem - Discovery & Booking',
    'EMBASSY': 'Real Estate - Commercial / Leasing',
    'GOODLUCK': 'Steel - Pipes & Tubes',
    'HSCL': 'Specialty Chem - Materials & Formulations',
    'IOB': 'Banks - Public Sector',
    'JWL': 'Infra Buildout - Rail Mobility',
    'KSCL': 'Agri Inputs & Farm Value Chain',
    'LLOYDSME': 'Steel - Primary / Long Products',
    'MINDSPACE': 'Real Estate - Commercial / Leasing',
    'ORIENTCEM': 'Cement - Regional / Midcap',
    'PATANJALI': 'Consumer Staples Brands',
    'PCBL': 'Commodity Chemicals',
    'SMLMAH': 'Commercial Vehicles',
    'SOLARA': 'Pharma - Export Generics - Mid Cap',
    'UCOBANK': 'Banks - Public Sector',
}


def sort_themes(themes: list[str]) -> list[str]:
    if IN_ORDER.exists():
        order_df = pd.read_csv(IN_ORDER)
        order_map = {t: i for i, t in enumerate(order_df['Theme'].dropna().tolist())}
        return sorted(themes, key=lambda t: (order_map.get(t, 10_000), t))
    return sorted(themes)


def build_final_2col(df: pd.DataFrame) -> pd.DataFrame:
    out = []
    for theme in sort_themes(df['Theme'].dropna().unique().tolist()):
        sub = df[df['Theme'] == theme].copy()
        # sort by mcap descending, unknown mcap last
        sub = sub.sort_values(['mcap_cr', 'Symbol'], ascending=[False, True], na_position='last')
        for _, r in sub.iterrows():
            out.append({'Symbol': r['Symbol'], 'Theme': theme})
        out.append({'Symbol': pd.NA, 'Theme': pd.NA})
    return pd.DataFrame(out, columns=['Symbol', 'Theme'])


def load_themepark_symbols() -> pd.DataFrame:
    tp = pd.read_excel(IN_THEMEPARK, sheet_name='theme_park')
    sym_col = [c for c in tp.columns if str(c).strip().lower() in ['symbol / rank', 'symbol', 'symbol/rank']]
    theme_col = [c for c in tp.columns if str(c).strip().lower() == 'theme']
    sym_col = sym_col[0] if sym_col else tp.columns[0]
    theme_col = theme_col[0] if theme_col else tp.columns[1]

    d = tp[[sym_col, theme_col]].copy()
    d.columns = ['Symbol', 'ThemeRaw']
    d['Symbol'] = d['Symbol'].astype(str).str.strip().str.upper()
    d['ThemeRaw'] = d['ThemeRaw'].astype(str).str.strip()

    # Keep only actual symbol-theme rows
    d = d[(d['Symbol'] != '') & (d['ThemeRaw'] != '')]
    d = d[~d['Symbol'].str.lower().isin(['nan', 'none'])]
    d = d[~d['ThemeRaw'].str.lower().isin(['nan', 'none'])]
    d = d[~d['Symbol'].str.contains('average rank|kpi avg rank|avg rank', case=False, regex=True)]
    d = d[d['Symbol'].str.match(r'^[A-Z0-9&\-\.]+$')]

    return d.drop_duplicates(['Symbol'])


def load_mcap_map() -> pd.DataFrame:
    # Primary mcap source from stage22 base
    base = pd.read_csv(IN_BASE)[['Symbol', 'ff_mcap_med_x']].drop_duplicates('Symbol')
    base.columns = ['Symbol', 'mcap_primary']
    base['Symbol'] = base['Symbol'].astype(str).str.upper().str.strip()

    # Fallback mcap source from Jan26 features
    j = pd.read_excel(IN_JAN26)
    j['Symbol'] = j['Symbol'].astype(str).str.upper().str.strip()
    j_m = j.groupby('Symbol', as_index=False)['ff_mcap'].median().rename(columns={'ff_mcap': 'mcap_jan26'})

    m = base.merge(j_m, on='Symbol', how='outer')
    m['mcap_cr'] = m['mcap_primary']
    m['mcap_cr'] = m['mcap_cr'].fillna(m['mcap_jan26'])
    return m[['Symbol', 'mcap_cr']].drop_duplicates('Symbol')


def main() -> None:
    multi = pd.read_csv(IN_MULTI)
    multi['Symbol'] = multi['Symbol'].astype(str).str.upper().str.strip()

    themepark = load_themepark_symbols()
    required_symbols = set(themepark['Symbol'])

    mcap_map = load_mcap_map()

    # Backfill symbols that are present in theme_park but missing from modeled universe.
    existing_symbols = set(multi['Symbol'])
    missing_required = sorted(required_symbols - existing_symbols)

    backfill_rows = []
    for sym in missing_required:
        if sym not in THEMEPARK_BACKFILL_THEME:
            continue
        th = THEMEPARK_BACKFILL_THEME[sym]
        backfill_rows.append({
            'Symbol': sym,
            'Theme': th,
            'membership_type': 'theme_park_backfill',
            'primary_theme': th,
            'secondary_rationale': 'Backfilled because symbol exists in original theme_park.',
        })

    backfill = pd.DataFrame(backfill_rows)
    if not backfill.empty:
        backfill.to_csv(OUT_BACKFILL, index=False)
    else:
        pd.DataFrame(columns=['Symbol', 'Theme', 'membership_type', 'primary_theme', 'secondary_rationale']).to_csv(OUT_BACKFILL, index=False)

    combined = pd.concat([multi, backfill], ignore_index=True)
    combined = combined.drop_duplicates(['Symbol', 'Theme'])

    # Attach mcap and apply threshold, except forced keep for original theme_park symbols.
    combined = combined.merge(mcap_map, on='Symbol', how='left')

    keep_mask = (combined['mcap_cr'] >= MCAP_THRESHOLD) | (combined['Symbol'].isin(required_symbols))
    kept = combined[keep_mask].copy()
    removed = combined[~keep_mask].copy()

    # Guarantee rule: all original theme_park symbols must exist.
    final_symbols = set(kept['Symbol'])
    still_missing = sorted(required_symbols - final_symbols)
    if still_missing:
        raise ValueError(f'Symbols from theme_park still missing after processing: {still_missing}')

    # Sort within theme by mcap desc.
    kept = kept.sort_values(['Theme', 'mcap_cr', 'Symbol'], ascending=[True, False, True], na_position='last')
    kept.to_csv(OUT_MULTI, index=False)

    removed_symbols = removed[['Symbol', 'mcap_cr']].drop_duplicates().sort_values(['mcap_cr', 'Symbol'], na_position='first')
    removed_symbols.to_csv(OUT_REMOVED, index=False)

    final_2col = build_final_2col(kept[['Symbol', 'Theme', 'mcap_cr']])
    final_2col.to_csv(OUT_FINAL_2COL, index=False)

    # Summary
    lines = [
        '# Stage26 ThemePark Mandatory Inclusion Summary',
        '',
        f'- MCap threshold: >= {MCAP_THRESHOLD:.0f} Cr (with exception for symbols present in original theme_park)',
        f'- Input rows: {len(multi)}',
        f'- Theme_park required symbols: {len(required_symbols)}',
        f'- Required symbols missing from modeled universe: {len(missing_required)}',
        f'- Backfilled rows added: {len(backfill)}',
        f'- Output rows: {len(kept)}',
        f'- Output symbols: {kept["Symbol"].nunique()}',
        f'- Removed non-theme_park symbols below threshold: {removed_symbols["Symbol"].nunique()}',
        f'- Required symbols still missing after output: {len(still_missing)}',
        '',
        '## Specific Fix',
        '- DREDGECORP is now retained (forced by theme_park membership despite sub-1000 Cr mcap).',
    ]

    OUT_SUMMARY.write_text('\n'.join(lines), encoding='utf-8')

    print(f'Wrote: {OUT_MULTI}')
    print(f'Wrote: {OUT_BACKFILL}')
    print(f'Wrote: {OUT_REMOVED}')
    print(f'Wrote: {OUT_FINAL_2COL}')
    print(f'Wrote: {OUT_SUMMARY}')
    print(f'Required symbols: {len(required_symbols)} | Missing pre-backfill: {len(missing_required)} | Backfilled: {len(backfill)}')


if __name__ == '__main__':
    main()
