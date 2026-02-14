#!/usr/bin/env python3
import pandas as pd
from pathlib import Path

BASE = Path('/Users/raviaranke/Desktop/themes')
IN_MULTI = BASE / 'stage24_multi_theme_membership_full.csv'
IN_BASE = BASE / 'stage22_reports_overlay_full.csv'
IN_ORDER = BASE / 'theme_order_reference.csv'

OUT_MULTI = BASE / 'stage25_multi_theme_membership_full_mcap_filtered.csv'
OUT_REMOVED = BASE / 'stage25_removed_below_1000_mcap.csv'
OUT_SUMMARY = BASE / 'stage25_mcap_filter_sort_summary.md'
OUT_FINAL_2COL = BASE / 'theme_park_codex_final_2col.csv'

MCAP_THRESHOLD = 1000.0


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
        sub = sub.sort_values(['mcap_cr', 'Symbol'], ascending=[False, True])
        for _, r in sub.iterrows():
            out.append({'Symbol': r['Symbol'], 'Theme': theme})
        out.append({'Symbol': pd.NA, 'Theme': pd.NA})
    return pd.DataFrame(out, columns=['Symbol', 'Theme'])


def main() -> None:
    multi = pd.read_csv(IN_MULTI)
    base = pd.read_csv(IN_BASE)[['Symbol', 'ff_mcap_med_x']].drop_duplicates('Symbol').rename(columns={'ff_mcap_med_x': 'mcap_cr'})

    merged = multi.merge(base, on='Symbol', how='left')
    if merged['mcap_cr'].isna().any():
        missing = sorted(merged[merged['mcap_cr'].isna()]['Symbol'].unique().tolist())
        raise ValueError(f'Missing mcap for symbols: {missing[:20]}... total {len(missing)}')

    # Removed symbol list (< threshold) at symbol level
    symbol_mcap = merged[['Symbol', 'mcap_cr']].drop_duplicates('Symbol')
    removed_syms = symbol_mcap[symbol_mcap['mcap_cr'] < MCAP_THRESHOLD].sort_values(['mcap_cr', 'Symbol'])

    # Filter and sort
    kept = merged[merged['mcap_cr'] >= MCAP_THRESHOLD].copy()
    kept = kept.sort_values(['Theme', 'mcap_cr', 'Symbol'], ascending=[True, False, True])

    kept.to_csv(OUT_MULTI, index=False)
    removed_syms.to_csv(OUT_REMOVED, index=False)

    final_2col = build_final_2col(kept[['Symbol', 'Theme', 'mcap_cr']])
    final_2col.to_csv(OUT_FINAL_2COL, index=False)

    # Diagnostics
    theme_sizes_before = merged.groupby('Theme')['Symbol'].nunique()
    theme_sizes_after = kept.groupby('Theme')['Symbol'].nunique()

    dropped_themes = sorted(set(theme_sizes_before.index) - set(theme_sizes_after.index))
    shrunk = []
    for t in sorted(theme_sizes_after.index):
        b = int(theme_sizes_before.get(t, 0))
        a = int(theme_sizes_after.get(t, 0))
        if a != b:
            shrunk.append((t, b, a))

    lines = [
        '# Stage25 MCap Filter + Theme Order Summary',
        '',
        f'- MCap threshold applied: >= {MCAP_THRESHOLD:.0f} Cr',
        f'- Input rows: {len(merged)}',
        f'- Output rows: {len(kept)}',
        f'- Input symbols: {merged["Symbol"].nunique()}',
        f'- Output symbols: {kept["Symbol"].nunique()}',
        f'- Symbols removed (<{MCAP_THRESHOLD:.0f} Cr): {len(removed_syms)}',
        f'- Themes before: {merged["Theme"].nunique()}',
        f'- Themes after: {kept["Theme"].nunique()}',
        f'- Themes dropped entirely: {len(dropped_themes)}',
        '',
        '## Sorting Rule',
        '- Inside each theme, symbols are ordered by market cap descending (largest to smallest).',
        '',
        '## Themes That Shrank After Filter',
    ]

    if shrunk:
        for t, b, a in shrunk:
            lines.append(f'- {t}: {b} -> {a}')
    else:
        lines.append('- None')

    if dropped_themes:
        lines.append('')
        lines.append('## Themes Dropped (all symbols below threshold)')
        for t in dropped_themes:
            lines.append(f'- {t}')

    OUT_SUMMARY.write_text('\n'.join(lines), encoding='utf-8')

    print(f'Wrote: {OUT_MULTI}')
    print(f'Wrote: {OUT_REMOVED}')
    print(f'Wrote: {OUT_FINAL_2COL}')
    print(f'Wrote: {OUT_SUMMARY}')
    print(f'Removed symbols: {len(removed_syms)}')
    print(f'Output symbols: {kept["Symbol"].nunique()}')


if __name__ == '__main__':
    main()
