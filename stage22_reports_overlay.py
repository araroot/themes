#!/usr/bin/env python3
import pandas as pd
from pathlib import Path

BASE = Path('/Users/raviaranke/Desktop/themes')
IN_FULL = BASE / 'stage21_source_informed_first_principles_full.csv'
IN_META = BASE / 'stage22_trendlyne_review_metadata.csv'
IN_ORDER = BASE / 'theme_order_reference.csv'

OUT_FULL = BASE / 'stage22_reports_overlay_full.csv'
OUT_CHANGES = BASE / 'stage22_reports_overlay_changes.csv'
OUT_EVIDENCE = BASE / 'stage22_report_source_evidence.csv'
OUT_SUMMARY = BASE / 'stage22_reports_overlay_summary.md'
OUT_FINAL_2COL = BASE / 'theme_park_codex_final_2col.csv'
OUT_HIGH_CONF = BASE / 'theme_park_codex_high_confidence_2col.csv'
OUT_REVIEW = BASE / 'theme_park_codex_review_queue.csv'

OVERRIDES = {
    # Low-confidence finance buckets
    'CRAMC': 'Capital Markets Ecosystem - Asset Managers',
    'DAMCAPITAL': 'Capital Markets Ecosystem - Wealth & Broking',
    'GROWW': 'Capital Markets Ecosystem - Digital Finance Platforms',
    'ICICIAMC': 'Capital Markets Ecosystem - Asset Managers',
    'IIFLCAPS': 'Capital Markets Ecosystem - Wealth & Broking',
    'JSWHL': 'Holding Companies',
    'PINELABS': 'Capital Markets Ecosystem - Digital Finance Platforms',
    'SKFINDUS': 'Other Industrial Goods',
    'BAJAJHFL': 'Housing Finance',
    'HDBFS': 'NBFC - Diversified Credit',
    'NORTHARC': 'NBFC - Diversified Credit',
    'PWL': 'India Digital Stack - Consumer Internet',
    'TATACAP': 'NBFC - Diversified Credit',
    'CANHLIFE': 'Insurance',
    'NIVABUPA': 'General Insurance',

    # Consumer and platform cleanup
    'CPPLUS': 'Consumer Durables & Electronics',
    'EPACK': 'Consumer Durables & Electronics',
    'EUREKAFORB': 'Household Appliances',
    'KRN': 'Cooling & Air-Conditioning',
    'LGEINDIA': 'Consumer Durables & Electronics',
    'MBEL': 'Industrial Engineering',
    'OSWALPUMPS': 'Agri Inputs & Farm Value Chain',
    'SHAKTIPUMP': 'Agri Inputs & Farm Value Chain',
    'WAKEFIT': 'Furniture-Furnishing-Paints - Mid Cap',
    'AMAGI': 'India Digital Stack - Enterprise Platforms',
    'CAPILLARY': 'India Digital Stack - Enterprise Platforms',
    'CRIZAC': 'India Digital Stack - Consumer Internet',
    'FIRSTCRY': 'India Digital Stack - Consumer Internet',
    'MEESHO': 'India Digital Stack - Consumer Internet',
    'PACEDIGITK': 'India Digital Stack - Connectivity & Infra',
    'PFOCUS': 'Media & Broadcasting Platforms',
    'UNIECOM': 'India Digital Stack - Enterprise Platforms',
    'URBANCO': 'India Digital Stack - Consumer Internet',
    'IGIL': 'Jewellery',

    # Healthcare and industrial cleanup
    'AGARWALEYE': 'Healthcare Services Platforms',
    'ELLEN': 'Process Inputs & Industrial Chemicals',
    'LAXMIDENTL': 'Healthcare Services Platforms',
    'LOTUSDEV': 'Real Estate - Residential Developers - Mid Cap',
    'FOSECOIND': 'Process Inputs & Industrial Chemicals',
    'HEXT': 'IT Services - Midcap',
    'IKS': 'Healthcare Services Platforms',
    'INDGN': 'Healthcare Services Platforms',
    'SOTL': 'Refineries/Petro-Products',
    'JSWCEMENT': 'Cement - Large Integrated',

    # Metals, mobility and infrastructure cleanup
    'ASHAPURMIN': 'Mining',
    'BHARATCOAL': 'Mining',
    'GALLANTT': 'Steel - Primary / Long Products',
    'JAINREC': 'Recyclers',
    'MIDWESTLTD': 'Mining',
    'CARRARO': 'Auto Components - Driveline / Chassis',
    'DYNAMATECH': 'Defence, Aerospace & Strategic Manufacturing',
    'SHARDAMOTR': 'Auto Components - Body / Thermal / Interior - Mid Cap',
    'STUDDS': 'Auto Components - Body / Thermal / Interior - Mid Cap',
    'SUNDRMFAST': 'Auto Components - Driveline / Chassis',
    'TMCV': 'Commercial Vehicles',
    'TMPV': 'Passenger Vehicles',
    'KRBL': 'Packaged Foods',
    'ORKLAINDIA': 'Packaged Foods',
    'VINCOFE': 'Packaged Foods',
    'CORONA': 'Pharma - Domestic Formulations - Mid Cap',
    'EMCURE': 'Pharma - Domestic Formulations - Mid Cap',
    'RUBICON': 'Pharma CDMO - Advanced Platforms',
    'SANOFICONR': 'Consumer Staples Brands',
    'SUDEEPPHRM': 'Pharma API & Intermediates',
    'ZOTA': 'Pharma - Domestic Formulations - Small Cap',
    'MARATHON': 'Real Estate - Residential Developers - Mid Cap',
    'RAYMONDREL': 'Real Estate - Residential Developers - Mid Cap',
    'SURAKSHA': 'Diagnostics & Pathology Chains',
    'SWANCORP': 'Real Estate - Commercial / Leasing',
    'TARC': 'Real Estate - Residential Developers - Mid Cap',
    'AEGISVOPAK': 'Infra Buildout - Logistics Networks',
    'CEMPRO': 'Cement - Regional / Midcap',
    'EUROPRATIK': 'Houseware',
    'KINGFA': 'Plastic Products',
    'PENIND': 'Steel - Pipes & Tubes',
    'POCL': 'Recyclers',
    'SAMBHV': 'Steel - Pipes & Tubes',
    'SANATHAN': 'Textiles',
    'XPROINDIA': 'Plastic Products',
    'ABLBL': 'Organized Retail - Value & Fashion',
    'AEQUS': 'Defence, Aerospace & Strategic Manufacturing',
    'AIIL': 'NBFC - Diversified Credit',
    'ANTHEM': 'Pharma CDMO - Advanced Platforms',
    'ATLANTAELE': 'Electrical Equipment',
    'EBGNG': 'Consumer Durables & Electronics',
    'FILATEX': 'Textiles',
    'KSHINTL': 'Electrical Cables, Wires & Conductors',
    'TENNIND': 'Auto Components - Body / Thermal / Interior - Mid Cap',
    'UNIMECH': 'Defence, Aerospace & Strategic Manufacturing',
    'AFCONS': 'Infra Buildout - EPC Contractors',
    'AJAXENGG': 'Industrial Machinery - Capital Goods',
    'BUILDPRO': 'B2B Distribution Platforms',
    'CEIGALL': 'Infra Buildout - Roads & Expressways',
    'EPACKPEB': 'Industrial Engineering',
    'INTERARCH': 'Industrial Engineering',
    'PATELENG': 'Infra Buildout - EPC Contractors',
    'SKIPPER': 'Power Equip - Grid & T&D',
    'TRANSRAILL': 'Power Equip - Grid & T&D',

    # Non-LO fixes after report cross-check
    'RAILTEL': 'India Digital Stack - Connectivity & Infra',
    'MPSLTD': 'India Digital Stack - Enterprise Platforms',
    'COHANCE': 'Pharma CDMO - Core Contract Manufacturing',
}

LOW_CONFIDENCE_KEEP_REVIEW = {
    'SWANCORP', 'KSHINTL'
}


def append_source_tag(src: str, tag: str) -> str:
    src = '' if pd.isna(src) else str(src)
    parts = [p for p in src.split('|') if p]
    if tag not in parts:
        parts.append(tag)
    return '|'.join(parts)


def sort_themes(df: pd.DataFrame) -> list[str]:
    present = sorted(df['Theme'].dropna().unique().tolist())
    if IN_ORDER.exists():
        order_df = pd.read_csv(IN_ORDER)
        order_map = {t: i for i, t in enumerate(order_df['Theme'].dropna().tolist())}
        return sorted(present, key=lambda t: (order_map.get(t, 10_000), t))
    return present


def build_final_2col(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for theme in sort_themes(df):
        syms = sorted(df.loc[df['Theme'] == theme, 'Symbol'].dropna().astype(str).unique().tolist())
        for sym in syms:
            rows.append({'Symbol': sym, 'Theme': theme})
        rows.append({'Symbol': pd.NA, 'Theme': pd.NA})
    return pd.DataFrame(rows, columns=['Symbol', 'Theme'])


def main() -> None:
    df = pd.read_csv(IN_FULL)
    meta = pd.read_csv(IN_META)

    meta_cols = ['Symbol', 'company_name', 'sector', 'industry', 'brokers', 'motilal_present', 'trendlyne_post_url', 'trendlyne_stock_url', 'descriptions']
    meta = meta[meta_cols].drop_duplicates('Symbol')
    meta_map = meta.set_index('Symbol').to_dict(orient='index')

    change_rows = []

    for symbol, new_theme in OVERRIDES.items():
        idx = df.index[df['Symbol'] == symbol]
        if len(idx) == 0:
            continue

        i = idx[0]
        old_theme = df.at[i, 'Theme']
        old_conf = float(df.at[i, 'confidence']) if not pd.isna(df.at[i, 'confidence']) else 0.0
        m = meta_map.get(symbol, {})
        mot = bool(m.get('motilal_present', False))

        df.at[i, 'Theme'] = new_theme
        df.at[i, 'source'] = append_source_tag(df.at[i, 'source'], 'reports_overlay')
        if mot:
            df.at[i, 'source'] = append_source_tag(df.at[i, 'source'], 'motilal_oswal_report')

        if symbol in LOW_CONFIDENCE_KEEP_REVIEW:
            df.at[i, 'confidence'] = max(old_conf, 0.82)
            df.at[i, 'needs_review'] = True
            df.at[i, 'review_reasons'] = 'reports_overlay_low_confidence'
            if 'review_priority' in df.columns:
                df.at[i, 'review_priority'] = max(float(df.at[i, 'review_priority']) if not pd.isna(df.at[i, 'review_priority']) else 0.0, 35.0)
        else:
            target_conf = 0.94 if mot else 0.90
            df.at[i, 'confidence'] = max(old_conf, target_conf)
            df.at[i, 'needs_review'] = False
            df.at[i, 'review_reasons'] = pd.NA
            if 'review_priority' in df.columns:
                df.at[i, 'review_priority'] = 5.0

        if pd.isna(df.at[i, 'sector_mode']) and m.get('sector'):
            df.at[i, 'sector_mode'] = m.get('sector')
        if pd.isna(df.at[i, 'industry_mode']) and m.get('industry'):
            df.at[i, 'industry_mode'] = m.get('industry')

        change_rows.append({
            'Symbol': symbol,
            'old_theme': old_theme,
            'new_theme': new_theme,
            'old_confidence': old_conf,
            'new_confidence': float(df.at[i, 'confidence']),
            'needs_review': bool(df.at[i, 'needs_review']),
            'company_name': m.get('company_name', ''),
            'sector': m.get('sector', ''),
            'industry': m.get('industry', ''),
            'brokers': m.get('brokers', ''),
            'motilal_present': mot,
            'trendlyne_post_url': m.get('trendlyne_post_url', ''),
            'trendlyne_stock_url': m.get('trendlyne_stock_url', ''),
            'descriptions': m.get('descriptions', ''),
        })

    # Keep types clean
    if 'needs_review' in df.columns:
        df['needs_review'] = df['needs_review'].fillna(False).astype(bool)

    # Save full output
    df.to_csv(OUT_FULL, index=False)

    # Save change logs
    changes = pd.DataFrame(change_rows).sort_values(['new_theme', 'Symbol'])
    changes.to_csv(OUT_CHANGES, index=False)
    changes.to_csv(OUT_EVIDENCE, index=False)

    # Save 2-col final with blank separator rows after each theme
    final_2col = build_final_2col(df)
    final_2col.to_csv(OUT_FINAL_2COL, index=False)

    # Save high-confidence and review-queue files
    high_conf = df[~df['needs_review']][['Symbol', 'Theme']].sort_values(['Theme', 'Symbol'])
    high_conf.to_csv(OUT_HIGH_CONF, index=False)

    review = df[df['needs_review']].copy()
    if 'review_priority' in review.columns:
        review = review.sort_values(['review_priority', 'Symbol'], ascending=[False, True])
    else:
        review = review.sort_values(['Symbol'])
    review.to_csv(OUT_REVIEW, index=False)

    # Summary
    theme_sizes = df.groupby('Theme')['Symbol'].nunique().sort_values(ascending=False)
    lo_count = int(df['Theme'].astype(str).str.startswith('LO-').sum())
    summary = []
    summary.append('# Stage22 Reports Overlay Summary')
    summary.append('')
    summary.append(f'- Input rows: {len(pd.read_csv(IN_FULL))}')
    summary.append(f'- Output rows: {len(df)}')
    summary.append(f'- Symbols changed: {len(changes)}')
    summary.append(f'- Themes in output: {df["Theme"].nunique()}')
    summary.append(f'- LO-theme symbols remaining: {lo_count}')
    summary.append(f'- Max theme size: {int(theme_sizes.max()) if len(theme_sizes) else 0}')
    summary.append(f'- Themes with >15 symbols: {int((theme_sizes > 15).sum())}')
    summary.append(f'- High-confidence symbols: {len(high_conf)}')
    summary.append(f'- Review queue symbols: {len(review)}')
    summary.append('')
    summary.append('## Report Sources Used')
    summary.append('- Trendlyne stock/report pages for review set (sector/industry + broker coverage).')
    summary.append('- Motilal Oswal signal via Trendlyne broker attribution (`motilal_present=True`).')
    summary.append('- Moneycontrol direct scraping was not available in this runtime due access-denied responses; trendlyne-based broker report aggregation was used for this pass.')

    OUT_SUMMARY.write_text('\n'.join(summary), encoding='utf-8')

    print(f'Wrote: {OUT_FULL}')
    print(f'Wrote: {OUT_CHANGES}')
    print(f'Wrote: {OUT_EVIDENCE}')
    print(f'Wrote: {OUT_FINAL_2COL}')
    print(f'Wrote: {OUT_HIGH_CONF}')
    print(f'Wrote: {OUT_REVIEW}')
    print(f'Wrote: {OUT_SUMMARY}')
    print(f'Changed symbols: {len(changes)}')
    print(f'LO remaining: {lo_count}')
    print(f'Max theme size: {int(theme_sizes.max()) if len(theme_sizes) else 0}')


if __name__ == '__main__':
    main()
