#!/usr/bin/env python3
"""
Aggregate MF data by Theme + FundFamily
Sums tv_ columns for all stocks within each theme
Calculates bb_ (bucket bands) from tv_ values
"""

from pathlib import Path
import pandas as pd
import numpy as np
from app import build_theme_map, DATA_PATH_DEFAULT


def tv_to_bb(tv):
    """
    Convert total value (tv) to bucket band (bb)

    Bucketing logic from code2026/r/pivot.R:
    - tv >= 100:    bb = 3   (strong buying)
    - tv >= 10:     bb = 2   (moderate buying)
    - tv > 0:       bb = 1   (light buying)
    - tv == 0:      bb = 0   (neutral)
    - tv >= -10:    bb = -1  (light selling)
    - tv >= -100:   bb = -2  (moderate selling)
    - tv < -100:    bb = -3  (strong selling)
    """
    if pd.isna(tv):
        return np.nan

    if tv >= 100:
        return 3
    elif tv >= 10:
        return 2
    elif tv > 0:
        return 1
    elif tv == 0:
        return 0
    elif tv >= -10:
        return -1
    elif tv >= -100:
        return -2
    else:
        return -3


def aggregate_by_theme_and_fund():
    """
    Aggregate MF data by Theme + FundFamily
    """

    # Load theme mapping
    print("Loading theme map...")
    th = pd.read_excel(DATA_PATH_DEFAULT, sheet_name="theme_park")
    theme_map = build_theme_map(th)

    # Load portfolio symbols to identify portfolio themes
    pf = pd.read_excel(DATA_PATH_DEFAULT, sheet_name="PF_Ranks")
    pf = pf.rename(columns={"Symbol / Rank": "Symbol"})
    pf["Symbol"] = pf["Symbol"].astype(str).str.strip()
    portfolio_symbols = set(pf["Symbol"].dropna())

    # Identify portfolio themes
    portfolio_themes = sorted(theme_map[theme_map['Symbol'].isin(portfolio_symbols)]['Theme'].unique())

    # Load MF data
    print("Loading MF data...")
    mf_file = Path("/Users/raviaranke/Desktop/themes/Dec25_pivot_features.xlsx")
    mf_df = pd.read_excel(mf_file, sheet_name="Summary Data")

    # Merge with theme map
    print("Merging with theme map...")
    mf_with_theme = mf_df.merge(theme_map, on='Symbol', how='left')

    # Filter only rows with theme mapping
    mf_with_theme = mf_with_theme[mf_with_theme['Theme'].notna()]

    # Get all tv_ columns
    tv_cols = [c for c in mf_with_theme.columns if c.startswith('tv_')]

    print(f"Aggregating {len(tv_cols)} tv_ columns: {tv_cols}")

    # Group by Theme + FundFamily and sum tv_ columns
    print("Aggregating by Theme + FundFamily...")
    agg_dict = {col: 'sum' for col in tv_cols}

    theme_fund_agg = mf_with_theme.groupby(['Theme', 'FundFamily'], as_index=False).agg(agg_dict)

    # Sort: Portfolio themes first, then others (alphabetically within each group)
    print("Sorting themes (portfolio first)...")
    theme_fund_agg['IsPortfolio'] = theme_fund_agg['Theme'].isin(portfolio_themes)
    theme_fund_agg = theme_fund_agg.sort_values(
        by=['IsPortfolio', 'Theme', 'FundFamily'],
        ascending=[False, True, True]
    )

    # Add Total rows for each theme
    print("Adding Total rows for each theme...")
    result_rows = []

    for theme in theme_fund_agg['Theme'].unique():
        theme_data = theme_fund_agg[theme_fund_agg['Theme'] == theme]

        # Add all fund family rows for this theme
        for _, row in theme_data.iterrows():
            result_rows.append(row.to_dict())

        # Add Total row
        total_row = {'Theme': theme, 'FundFamily': 'TOTAL', 'IsPortfolio': theme in portfolio_themes}
        for col in tv_cols:
            total_row[col] = theme_data[col].sum()
        result_rows.append(total_row)

    # Create final dataframe
    result_df = pd.DataFrame(result_rows)

    # Drop IsPortfolio helper column
    result_df = result_df.drop(columns=['IsPortfolio'])

    # Calculate bb_ columns from tv_ columns
    print("Calculating bb_ (bucket bands) from tv_ values...")
    bb_cols = []
    for tv_col in tv_cols:
        bb_col = tv_col.replace('tv_', 'bb_')
        result_df[bb_col] = result_df[tv_col].apply(tv_to_bb).astype('Int64')  # Use Int64 for nullable integers
        bb_cols.append(bb_col)

    # Reorder columns: Theme, FundFamily, then alternating tv_ and bb_ columns
    cols = ['Theme', 'FundFamily']
    for tv_col, bb_col in zip(tv_cols, bb_cols):
        cols.append(tv_col)
        cols.append(bb_col)

    result_df = result_df[cols]

    # Save to Excel
    output_file = Path("/Users/raviaranke/Desktop/themes/Dec25_theme_aggregated.xlsx")
    print(f"\nSaving to {output_file}...")
    result_df.to_excel(output_file, index=False, sheet_name="Theme Aggregated")

    print(f"✅ Done! Created {output_file}")
    print(f"   - {len(result_df)} rows")
    print(f"   - {len(result_df['Theme'].unique())} unique themes")
    print(f"   - {len(portfolio_themes)} portfolio themes")
    print(f"   - {len(tv_cols)} months of data (tv_ and bb_ columns)")
    print(f"   - Total columns: {len(cols)}")

    return result_df


if __name__ == "__main__":
    df = aggregate_by_theme_and_fund()

    # Show sample
    print("\n" + "="*80)
    print("SAMPLE OUTPUT (first 10 rows, showing Nov and Dec columns):")
    print("="*80)
    sample_cols = ['Theme', 'FundFamily', 'tv_Nov25', 'bb_Nov25', 'tv_Dec25', 'bb_Dec25']
    print(df[sample_cols].head(10).to_string(index=False))
