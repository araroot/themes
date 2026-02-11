#!/usr/bin/env python3
"""
Aggregate MF data by Theme + FundFamily
Sums tv_ columns for all stocks within each theme
"""

from pathlib import Path
import pandas as pd
from app import build_theme_map, DATA_PATH_DEFAULT


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

    # Reorder columns: Theme, FundFamily, then all tv_ columns
    cols = ['Theme', 'FundFamily'] + tv_cols
    result_df = result_df[cols]

    # Save to Excel
    output_file = Path("/Users/raviaranke/Desktop/themes/Dec25_theme_aggregated.xlsx")
    print(f"\nSaving to {output_file}...")
    result_df.to_excel(output_file, index=False, sheet_name="Theme Aggregated")

    print(f"✅ Done! Created {output_file}")
    print(f"   - {len(result_df)} rows")
    print(f"   - {len(result_df['Theme'].unique())} unique themes")
    print(f"   - {len(portfolio_themes)} portfolio themes")
    print(f"   - Columns: {', '.join(cols)}")

    return result_df


if __name__ == "__main__":
    df = aggregate_by_theme_and_fund()

    # Show sample
    print("\n" + "="*80)
    print("SAMPLE OUTPUT (first 20 rows):")
    print("="*80)
    print(df.head(20).to_string(index=False))
