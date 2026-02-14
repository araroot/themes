#!/usr/bin/env python3
import pandas as pd
from pathlib import Path

BASE = Path('/Users/raviaranke/Desktop/themes')
IN_FULL = BASE / 'stage22_reports_overlay_full.csv'
IN_ORDER = BASE / 'theme_order_reference.csv'

OUT_ADDITIONS = BASE / 'stage23_secondary_theme_additions.csv'
OUT_MULTI_FULL = BASE / 'stage23_multi_theme_membership_full.csv'
OUT_SUMMARY = BASE / 'stage23_multi_theme_summary.md'
OUT_FINAL_2COL = BASE / 'theme_park_codex_final_2col.csv'

SECONDARY = {
    # Ownership/causal overlays
    'ADANIENSOL': ('Power Utilities - Regulated / Transmission', 'Adani ownership + power transmission utility cycle'),
    'ADANIGREEN': ('Renewables & Energy Transition', 'Adani ownership + renewable generation cycle'),
    'ADANIPORTS': ('Infra Buildout - Ports & Maritime', 'Adani ownership + ports throughput cycle'),
    'ADANIPOWER': ('Power Utilities - Generation & Renewables', 'Adani ownership + power generation cycle'),
    'AWL': ('Consumer Staples Brands', 'Adani ownership + staples/FMCG cycle'),

    # India Digital Stack -> operator/infra/product mappings
    'BHARTIARTL': ('Telecom Operators & Tower Infra', 'Digital stack + telecom operator coverage'),
    'BHARTIHEXA': ('Telecom Operators & Tower Infra', 'Digital stack + telecom operator coverage'),
    'IDEA': ('Telecom Operators & Tower Infra', 'Digital stack + telecom operator coverage'),
    'RAILTEL': ('Telecom Operators & Tower Infra', 'Digital stack + telecom infra operator coverage'),
    'STLTECH': ('Electrical Cables, Wires & Conductors', 'Digital infra + fiber cable capex cycle'),
    'E2E': ('India Digital Stack - Data Center & Compute', 'Connectivity infra + cloud/data-center exposure'),
    'BBOX': ('IT Services - Enterprise / BFSI', 'Digital infra + enterprise network services'),
    'ANANTRAJ': ('Real Estate - Commercial / Leasing', 'Data center thesis + land/lease economics'),
    'NETWEB': ('IT Products', 'Data center thesis + server hardware exposure'),
    'TECHNOE': ('Power Equip - Grid & T&D', 'Data center thesis + power infra EPC exposure'),

    # Enterprise + consumer internet bridges
    'AFFLE': ('IT Products', 'Enterprise platform + ad-tech product model'),
    'INDIAMART': ('B2B Distribution Platforms', 'Enterprise platform + B2B commerce network effects'),
    'JUSTDIAL': ('India Digital Stack - Consumer Internet', 'Enterprise ad platform + consumer local search demand'),
    'MAPMYINDIA': ('IT Products', 'Enterprise platform + map/IP product economics'),
    'NAUKRI': ('India Digital Stack - Consumer Internet', 'Enterprise HR platform + consumer job marketplace'),
    'NAZARA': ('Media & Music', 'Enterprise platform + digital content/gaming monetization'),
    'ROUTE': ('IT Products', 'Enterprise platform + communication API product model'),
    'MPSLTD': ('IT Services - Enterprise / BFSI', 'Enterprise platform + outsourced digital workflow services'),
    'AMAGI': ('Media & Broadcasting Platforms', 'Enterprise platform + media tech monetization'),
    'CAPILLARY': ('IT Services - Enterprise / BFSI', 'Enterprise platform + enterprise SaaS implementation cycle'),
    'UNIECOM': ('B2B Distribution Platforms', 'Enterprise platform + merchant enablement/distribution'),
    'ETERNAL': ('Digital Marketplace & Logistics Platforms', 'Consumer internet + on-demand commerce/logistics flywheel'),
    'NYKAA': ('Organized Retail - Value & Fashion', 'Consumer internet + beauty retail merchandising cycle'),
    'SWIGGY': ('Digital Marketplace & Logistics Platforms', 'Consumer internet + logistics marketplace economics'),
    'FIRSTCRY': ('Organized Retail - Value & Fashion', 'Consumer internet + omni retail inventory cycle'),
    'MEESHO': ('Organized Retail - Value & Fashion', 'Consumer internet + value retail demand cycle'),
    'URBANCO': ('Digital Marketplace & Logistics Platforms', 'Consumer internet + service marketplace matching'),

    # Tourism ecosystem bridges
    'BRIGHOTEL': ('Hospitality Chains', 'Tourism ecosystem + hotel room cycle'),
    'ITCHOTELS': ('Hospitality Chains', 'Tourism ecosystem + hotel room cycle'),
    'JUNIPER': ('Hospitality Chains', 'Tourism ecosystem + hotel room cycle'),
    'THELEELA': ('Hospitality Chains', 'Tourism ecosystem + hotel room cycle'),
    'TRAVELFOOD': ('Quick Service Restaurants', 'Tourism ecosystem + airport F&B throughput'),
    'GMRAIRPORT': ('Infra Buildout - Logistics Networks', 'Tourism ecosystem + airport infra throughput'),
    'IRCTC': ('Infra Buildout - Rail Mobility', 'Travel discovery + rail network operating leverage'),
    'IXIGO': ('India Digital Stack - Consumer Internet', 'Travel discovery + consumer booking funnel'),
    'TBOTEK': ('India Digital Stack - Enterprise Platforms', 'Travel discovery + B2B travel distribution platform'),
    'THOMASCOOK': ('Tourism Ecosystem - Mobility & Hospitality', 'Travel booking + packaged travel operations'),
    'YATRA': ('India Digital Stack - Consumer Internet', 'Travel discovery + consumer booking funnel'),

    # EV stack bridges
    'BOSCHLTD': ('Auto Components - Precision, Systems & Harnesses', 'EV component thesis + auto systems engineering cycle'),
    'EXIDEIND': ('Auto Components - Electrical, Interiors & Lighting', 'EV component thesis + battery/electrical systems cycle'),
    'JTEKTINDIA': ('Auto Components - Driveline / Chassis', 'EV component thesis + steering/driveline content share'),
    'SCHAEFFLER': ('Auto Components - Driveline / Chassis', 'EV component thesis + drivetrain/bearing content share'),
    'SONACOMS': ('Auto Components - Driveline / Chassis', 'EV component thesis + drivetrain systems cycle'),
    'UNOMINDA': ('Auto Components - Electrical, Interiors & Lighting', 'EV component thesis + cockpit/electrical systems cycle'),
    'ZFCVINDIA': ('Auto Components - Driveline / Chassis', 'EV component thesis + CV axle/driveline cycle'),
    'ATHERENERG': ('2W/3W OEMs', 'EV thesis + 2W OEM volume/mix cycle'),
    'OLAELEC': ('2W/3W OEMs', 'EV thesis + 2W OEM volume/mix cycle'),

    # Renewables theme bridges
    'ACMESOLAR': ('Renewables - Solar', 'Energy transition + utility solar execution cycle'),
    'EMMVEE': ('Renewables - Solar', 'Energy transition + solar module manufacturing cycle'),
    'ENRIN': ('Power Equip - Grid & T&D', 'Energy transition + grid equipment capex cycle'),
    'NTPCGREEN': ('Power Utilities - Generation & Renewables', 'Energy transition + renewable utility generation cycle'),
    'QPOWER': ('Power Equip - Grid & T&D', 'Energy transition + electrical equipment order cycle'),
    'SAATVIKGL': ('Renewables - Solar', 'Energy transition + solar module manufacturing cycle'),
    'SUZLON': ('Renewables - Wind', 'Energy transition + wind turbine order cycle'),
    'TRUALT': ('Sugar & Bioenergy', 'Energy transition + ethanol/bioenergy economics'),

    # Marketplace / workspace bridges
    'BLACKBUCK': ('Infra Buildout - Logistics Networks', 'Marketplace model + freight network utilization'),
    'CARTRADE': ('India Digital Stack - Consumer Internet', 'Marketplace model + auto retail demand funnel'),
    'DELHIVERY': ('Infra Buildout - Logistics Networks', 'Marketplace model + logistics network density'),
    'AWFIS': ('Real Estate - Commercial / Leasing', 'Workspace model + office absorption cycle'),
    'INDIQUBE': ('Real Estate - Commercial / Leasing', 'Workspace model + office absorption cycle'),
    'SMARTWORKS': ('Real Estate - Commercial / Leasing', 'Workspace model + office absorption cycle'),
    'WEWORK': ('Real Estate - Commercial / Leasing', 'Workspace model + office absorption cycle'),

    # Distribution + healthcare service bridges
    'ENTERO': ('Healthcare Services Platforms', 'B2B distribution + pharma supply chain execution'),
    'OPTIEMUS': ('Consumer Durables & Electronics', 'B2B distribution + electronics channel cycle'),
    'REDINGTON': ('Consumer Durables & Electronics', 'B2B distribution + IT/electronics channel cycle'),
    'RPTECH': ('IT Products', 'B2B distribution + enterprise hardware cycle'),
    'BUILDPRO': ('Cement - Regional / Midcap', 'B2B distribution + building materials demand cycle'),
    'MEDIASSIST': ('Insurance', 'Healthcare services + insurance claims processing linkage'),
    'MEDPLUS': ('Organized Retail - Large Format', 'Healthcare services + pharmacy retail cycle'),
    'NEPHROPLUS': ('Hospitals - Mid Cap', 'Healthcare services + specialty care utilization cycle'),
    'AGARWALEYE': ('Hospitals - Mid Cap', 'Healthcare services + specialty care utilization cycle'),
    'LAXMIDENTL': ('Hospitals - Small Cap', 'Healthcare services + specialty care utilization cycle'),
    'IKS': ('IT Services - Enterprise / BFSI', 'Healthcare services + healthcare BPM/digital services'),
    'INDGN': ('IT Services - Enterprise / BFSI', 'Healthcare services + healthcare tech services'),

    # CDMO advanced bridge into pharma operating buckets
    'CONCORDBIO': ('Pharma API & Intermediates', 'CDMO platform + API fermentation demand cycle'),
    'DIVISLAB': ('Pharma API & Intermediates', 'CDMO platform + API/intermediates scale economics'),
    'GLAND': ('Pharma - Export Generics - Large Cap', 'CDMO platform + injectables export cycle'),
    'LAURUSLABS': ('Pharma API & Intermediates', 'CDMO platform + API/intermediates cycle'),
    'PPLPHARMA': ('Pharma - Specialty / Emerging', 'CDMO platform + niche portfolio cycle'),
    'RUBICON': ('Pharma CDMO - Core Contract Manufacturing', 'Advanced CDMO + core contract manufacturing overlap'),
    'ANTHEM': ('Pharma CDMO - Core Contract Manufacturing', 'Advanced CDMO + core contract manufacturing overlap'),

    # Fintech bridge
    'PAYTM': ('Financial Services', 'Fintech platform + digital payments/financialization cycle'),
    'POLICYBZR': ('Financial Services', 'Fintech platform + insurance distribution cycle'),
    'ZAGGLE': ('Financial Services', 'Fintech platform + corporate spends/payment rails cycle'),
    'GROWW': ('Financial Services', 'Fintech platform + retail participation cycle'),
    'PINELABS': ('Financial Services', 'Fintech platform + merchant acquiring cycle'),

    # Premium consumption bridge
    'ETHOSLTD': ('Niche Retail & Entertainment', 'Premium consumption + specialty retail demand'),
    'KALYANKJIL': ('Jewellery', 'Premium consumption + jewelry demand cycle'),
    'LENSKART': ('Organized Retail - Large Format', 'Premium consumption + organized retail unit economics'),
    'PHOENIXLTD': ('Real Estate - Commercial / Leasing', 'Premium consumption + mall leasing/footfall cycle'),
    'RAYMONDLSL': ('Organized Retail - Value & Fashion', 'Premium consumption + apparel retail cycle'),
    'SKYGOLD': ('Jewellery', 'Premium consumption + jewelry demand cycle'),
    'STYL': ('Organized Retail - Value & Fashion', 'Premium consumption + apparel retail cycle'),
    'THANGAMAYL': ('Jewellery', 'Premium consumption + jewelry demand cycle'),
    'TITAN': ('Jewellery', 'Premium consumption + jewelry demand cycle'),
}


def sort_themes(present_themes: list[str]) -> list[str]:
    if IN_ORDER.exists():
        order_df = pd.read_csv(IN_ORDER)
        order_map = {t: i for i, t in enumerate(order_df['Theme'].dropna().tolist())}
        return sorted(present_themes, key=lambda t: (order_map.get(t, 10_000), t))
    return sorted(present_themes)


def build_final_2col(theme_rows: pd.DataFrame) -> pd.DataFrame:
    out = []
    for theme in sort_themes(theme_rows['Theme'].dropna().unique().tolist()):
        syms = sorted(theme_rows.loc[theme_rows['Theme'] == theme, 'Symbol'].dropna().astype(str).unique().tolist())
        for sym in syms:
            out.append({'Symbol': sym, 'Theme': theme})
        out.append({'Symbol': pd.NA, 'Theme': pd.NA})
    return pd.DataFrame(out, columns=['Symbol', 'Theme'])


def main() -> None:
    base = pd.read_csv(IN_FULL)
    symbol_to_theme = dict(zip(base['Symbol'], base['Theme']))
    all_themes = set(base['Theme'])

    # Validate mapping
    missing_symbols = sorted(set(SECONDARY) - set(base['Symbol']))
    missing_themes = sorted({t for t, _ in SECONDARY.values() if t not in all_themes})
    if missing_symbols:
        raise ValueError(f'Missing symbols in base file: {missing_symbols}')
    if missing_themes:
        raise ValueError(f'Secondary themes not found in base taxonomy: {missing_themes}')

    additions = []
    for sym, (sec_theme, rationale) in SECONDARY.items():
        pri_theme = symbol_to_theme[sym]
        if pri_theme == sec_theme:
            continue
        additions.append({
            'Symbol': sym,
            'PrimaryTheme': pri_theme,
            'SecondaryTheme': sec_theme,
            'Rationale': rationale,
        })

    add_df = pd.DataFrame(additions).sort_values(['SecondaryTheme', 'Symbol'])
    add_df.to_csv(OUT_ADDITIONS, index=False)

    primary_rows = base[['Symbol', 'Theme']].copy()
    primary_rows['membership_type'] = 'primary'
    primary_rows['primary_theme'] = primary_rows['Theme']
    primary_rows['secondary_rationale'] = pd.NA

    secondary_rows = add_df.rename(columns={'SecondaryTheme': 'Theme', 'Rationale': 'secondary_rationale'})[['Symbol', 'Theme', 'secondary_rationale']].copy()
    secondary_rows['membership_type'] = 'secondary'
    secondary_rows['primary_theme'] = secondary_rows['Symbol'].map(symbol_to_theme)

    multi = pd.concat([primary_rows, secondary_rows], ignore_index=True)
    multi = multi.drop_duplicates(['Symbol', 'Theme']).sort_values(['Theme', 'membership_type', 'Symbol'])
    multi.to_csv(OUT_MULTI_FULL, index=False)

    final_2col = build_final_2col(multi[['Symbol', 'Theme']])
    final_2col.to_csv(OUT_FINAL_2COL, index=False)

    memberships = multi.groupby('Symbol')['Theme'].nunique()
    theme_sizes = multi.groupby('Theme')['Symbol'].nunique().sort_values(ascending=False)

    summary = [
        '# Stage23 Multi-Theme Overlay Summary',
        '',
        f'- Base symbols: {base["Symbol"].nunique()}',
        f'- Primary mappings: {len(primary_rows)}',
        f'- Secondary mappings added: {len(secondary_rows)}',
        f'- Multi-theme rows (unique Symbol-Theme): {len(multi)}',
        f'- Symbols with 2 themes: {int((memberships >= 2).sum())}',
        f'- Max themes per symbol: {int(memberships.max())}',
        f'- Total themes in output: {multi["Theme"].nunique()}',
        f'- Max theme size after secondary overlay: {int(theme_sizes.max())}',
        f'- Themes with >15 symbols: {int((theme_sizes > 15).sum())}',
        '',
        '## Rule Used',
        '- Secondary theme added only when a distinct causal/coverage lens exists beyond the primary theme.',
        '- Kept max two themes per symbol in this pass.',
    ]
    OUT_SUMMARY.write_text('\n'.join(summary), encoding='utf-8')

    print(f'Wrote: {OUT_ADDITIONS}')
    print(f'Wrote: {OUT_MULTI_FULL}')
    print(f'Wrote: {OUT_FINAL_2COL}')
    print(f'Wrote: {OUT_SUMMARY}')
    print(f'Secondary rows: {len(secondary_rows)}')
    print(f'Symbols with 2 themes: {int((memberships >= 2).sum())}')
    print(f'Max theme size: {int(theme_sizes.max())}')


if __name__ == '__main__':
    main()
