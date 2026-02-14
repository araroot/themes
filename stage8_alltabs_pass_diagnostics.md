# Stage8 Multi-pass Theme Build (All Tabs)

Method order:
1. Fundamental seed groups from Sector/Industry (mode across date tabs) + Debug theme fallback
2. Merge tiny groups (<3) using rank-history centroid similarity, sector-aware first
3. Split oversized groups by rank-history clustering to reach 100-200 themes
4. Compute A/Core/B and outlier scores inside each final theme

Universe:
- Jan26 MF-active symbols (non Index/ETF/Arbitrage, tv_Jan26!=0): 818
- Usable with rank history from all date tabs: 773
- Missing rank history in workbook: 45
- Missing examples: AEQUS, AMAGI, ATLANTAELE, BHARATCOAL, BLUESTONE, BUILDPRO, CANHLIFE, CAPILLARY, CORONA, CPPLUS, CRAMC, EMMVEE, EPACKPEB, EUROPRATIK, GROWW, ICICIAMC, JAINREC, JSWCEMENT, KSHINTL, LENSKART

Pass stats:
- Initial seed groups: 127
- Tiny-group merges applied: 57
- Splits applied: 49
- Final themes: 119
- Theme size min/max: 3 / 35
- Mean cohesion: 0.2256
- Worst cohesion: -0.0979

Top 20 largest themes:
- Unclassified - Cluster A (UNCLASSIFIED::B::B::A) n=35, cohesion=0.2126
- IT Consulting & Software - Cluster A (IND::IT Consulting & Software::B::B::A) n=19, cohesion=0.2845
- Unclassified - Cluster B (UNCLASSIFIED::B::B::B) n=18, cohesion=0.2096
- Finance (including NBFCs) - Cluster B (IND::Finance (including NBFCs)::B) n=16, cohesion=0.1729
- Heavy Electrical Equipment - Cluster t (IND::Heavy Electrical Equipment) n=16, cohesion=0.0913
- Banks - Cluster B (IND::Banks::B::B) n=14, cohesion=0.3511
- Unclassified - Cluster B (UNCLASSIFIED::B::A::B) n=14, cohesion=0.28
- Specialty Chemicals - Cluster A (IND::Specialty Chemicals::A) n=14, cohesion=0.1158
- Healthcare Facilities - Cluster s (IND::Healthcare Facilities) n=14, cohesion=0.1095
- Other Financial Services - Cluster s (IND::Other Financial Services) n=14, cohesion=0.0849
- Iron & Steel/Interm.Products - Cluster s (IND::Iron & Steel/Interm.Products) n=14, cohesion=0.0602
- Pharmaceuticals - Cluster B (IND::Pharmaceuticals::B::A::B::B) n=13, cohesion=0.2369
- Personal Products - Cluster s (IND::Personal Products) n=13, cohesion=0.1672
- Other Electrical Equipment/Products - Cluster B (IND::Other Electrical Equipment/Products::B) n=12, cohesion=0.165
- Other Industrial Products - Cluster s (IND::Other Industrial Products) n=12, cohesion=0.1066
- Agrochemicals - Cluster s (IND::Agrochemicals) n=11, cohesion=0.1254
- Unclassified - Cluster B (UNCLASSIFIED::A::B) n=9, cohesion=0.267
- Auto Parts & Equipment - Cluster B (IND::Auto Parts & Equipment::B::B::B) n=9, cohesion=0.1732
- Packaged Foods - Cluster s (IND::Packaged Foods) n=9, cohesion=0.0804
- Industrial Machinery - Cluster B (IND::Industrial Machinery::B) n=9, cohesion=0.0739