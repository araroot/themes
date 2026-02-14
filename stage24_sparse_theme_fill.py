#!/usr/bin/env python3
import pandas as pd
from pathlib import Path

BASE = Path('/Users/raviaranke/Desktop/themes')
IN_MULTI = BASE / 'stage23_multi_theme_membership_full.csv'
IN_ORDER = BASE / 'theme_order_reference.csv'

OUT_ADDITIONS = BASE / 'stage24_sparse_theme_fill_additions.csv'
OUT_MULTI = BASE / 'stage24_multi_theme_membership_full.csv'
OUT_SUMMARY = BASE / 'stage24_sparse_theme_fill_summary.md'
OUT_FINAL_2COL = BASE / 'theme_park_codex_final_2col.csv'

ADDITIONS = {
    # Fill sparse themes (1-2 names) to >=3 using rough but related matches
    'GPPL': ('Shipping', 'Ports and coastal cargo throughput links to shipping cycle.'),
    'JSWINFRA': ('Shipping', 'Port operations are highly correlated with shipping throughput.'),

    'HINDCOPPER': ('Rare Earth', 'Critical minerals basket proxy alongside niche mineral names.'),
    'MOIL': ('Rare Earth', 'Critical mineral mining proxy for strategic-minerals bucket.'),

    'TATAPOWER': ('Power Utilities - Trading / Mixed', 'Integrated utility profile includes merchant/trading exposure.'),
    'JSWENERGY': ('Power Utilities - Trading / Mixed', 'Integrated power platform with mixed merchant dynamics.'),

    'KRSNAA': ('Medical Devices', 'Diagnostics/medtech adjacency used as rough medical-tech proxy.'),

    'GESHIP': ('Infra Buildout - Marine & Dredging', 'Marine fleet activity ties to dredging/marine capex cycle.'),

    'KSB': ('Water & Environmental Utilities', 'Water-pump and fluid handling exposure aligns with water utilities.'),
    'KIRLOSBROS': ('Water & Environmental Utilities', 'Pump/process equipment is core to water infra projects.'),

    'ELECON': ('Mine Supply', 'Mining conveyor/gearbox capex linkage to mine-supply cycle.'),

    'TORNTPOWER': ('Thermal Power', 'Conventional thermal mix provides rough fit for thermal basket.'),

    'JKPAPER': ('Stationery & Writing Instruments', 'Paper substrate demand is upstream-linked to stationery cycle.'),

    'TVSMOTOR': ('EV Mobility Stack - 2W OEMs', '2W OEM with EV product exposure; natural bridge candidate.'),

    'ESABINDIA': ('Electrodes', 'Welding/consumables adjacency to metal fabrication and electrode demand.'),
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
        syms = sorted(df.loc[df['Theme'] == theme, 'Symbol'].dropna().astype(str).unique().tolist())
        for sym in syms:
            out.append({'Symbol': sym, 'Theme': theme})
        out.append({'Symbol': pd.NA, 'Theme': pd.NA})
    return pd.DataFrame(out, columns=['Symbol', 'Theme'])


def main() -> None:
    multi = pd.read_csv(IN_MULTI)
    symbol_set = set(multi['Symbol'])
    theme_set = set(multi['Theme'])

    missing_symbols = sorted(set(ADDITIONS) - symbol_set)
    missing_themes = sorted({t for t, _ in ADDITIONS.values() if t not in theme_set})
    if missing_symbols:
        raise ValueError(f'Missing symbols: {missing_symbols}')
    if missing_themes:
        raise ValueError(f'Missing themes: {missing_themes}')

    primary_map = (
        multi[multi['membership_type'] == 'primary'][['Symbol', 'Theme']]
        .drop_duplicates('Symbol')
        .set_index('Symbol')['Theme']
        .to_dict()
    )

    rows = []
    for sym, (sec_theme, rationale) in ADDITIONS.items():
        pri = primary_map.get(sym)
        if pri is None:
            continue
        # skip if already mapped to this theme
        already = ((multi['Symbol'] == sym) & (multi['Theme'] == sec_theme)).any()
        if already:
            continue
        rows.append({
            'Symbol': sym,
            'Theme': sec_theme,
            'membership_type': 'secondary',
            'primary_theme': pri,
            'secondary_rationale': rationale,
        })

    add_df = pd.DataFrame(rows)
    add_df = add_df.sort_values(['Theme', 'Symbol'])
    add_df.to_csv(OUT_ADDITIONS, index=False)

    out = pd.concat([multi, add_df], ignore_index=True)
    out = out.drop_duplicates(['Symbol', 'Theme']).sort_values(['Theme', 'membership_type', 'Symbol'])
    out.to_csv(OUT_MULTI, index=False)

    final_2col = build_final_2col(out[['Symbol', 'Theme']])
    final_2col.to_csv(OUT_FINAL_2COL, index=False)

    # Diagnostics
    sizes = out.groupby('Theme')['Symbol'].nunique().sort_values()
    sym_counts = out.groupby('Symbol')['Theme'].nunique()
    sparse_before = multi.groupby('Theme')['Symbol'].nunique()
    sparse_before = sparse_before[sparse_before <= 2].sort_index()
    sparse_after = sizes[sizes.index.isin(sparse_before.index)].sort_index()

    lines = [
        '# Stage24 Sparse Theme Fill Summary',
        '',
        f'- Input rows: {len(multi)}',
        f'- Added secondary rows: {len(add_df)}',
        f'- Output rows: {len(out)}',
        f'- Symbols: {out["Symbol"].nunique()}',
        f'- Themes: {out["Theme"].nunique()}',
        f'- Themes with <=2 names after fill: {int((sizes <= 2).sum())}',
        f'- Minimum theme size after fill: {int(sizes.min())}',
        f'- Max themes per symbol: {int(sym_counts.max())}',
        '',
        '## Sparse Themes Before -> After',
    ]
    for theme in sparse_before.index:
        lines.append(f'- {theme}: {int(sparse_before[theme])} -> {int(sparse_after.get(theme, sparse_before[theme]))}')

    OUT_SUMMARY.write_text('\n'.join(lines), encoding='utf-8')

    print(f'Wrote: {OUT_ADDITIONS}')
    print(f'Wrote: {OUT_MULTI}')
    print(f'Wrote: {OUT_FINAL_2COL}')
    print(f'Wrote: {OUT_SUMMARY}')
    print(f'Added rows: {len(add_df)}')
    print(f'Themes <=2 after: {int((sizes <= 2).sum())}')
    print(f'Min theme size after: {int(sizes.min())}')
    print(f'Max themes per symbol: {int(sym_counts.max())}')


if __name__ == '__main__':
    main()
