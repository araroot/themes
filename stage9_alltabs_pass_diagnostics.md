# Stage9 Multi-pass Theme Build (All Tabs, Full 800+ Universe)

Method passes:
1) Fundamental seeding from Sector/Industry mode + Debug theme fallback
2) Tiny-theme merge (<3) using rank-centroid similarity
3) Recursive split of oversized themes (>15) using rank-history clustering
4) No-rank symbols assigned to fundamental no-rank buckets (size controlled)
5) A/Core/B + outlier scoring for rank-available themes

- Jan26 universe: 818
- Rank-available symbols: 773
- No-rank symbols assigned: 45
- Final themes: 104
- Theme size min/max: 3/15
- Coverage: 818/818 (uncovered=0)
- Multi-assigned symbols: 0
- Mean cohesion (rank themes only): 0.1735
- Worst cohesion (rank themes only): -0.0979

Top 25 largest themes:
- Internet Software & Services [IND::Internet Software & Services] n=15, rank_cov=rank_available, cohesion=0.0185
- Banks - Cluster B [IND::Banks::B::B] n=14, rank_cov=rank_available, cohesion=0.3511
- Unclassified - Cluster B [UNCLASSIFIED::B::A::B] n=14, rank_cov=rank_available, cohesion=0.28
- Auto Parts & Equipment - Cluster A [IND::Auto Parts & Equipment::B::A] n=14, rank_cov=rank_available, cohesion=0.1576
- Pharmaceuticals - Cluster B [IND::Pharmaceuticals::B::B] n=14, rank_cov=rank_available, cohesion=0.1519
- Specialty Chemicals - Cluster A [IND::Specialty Chemicals::A] n=14, rank_cov=rank_available, cohesion=0.1158
- Healthcare Facilities [IND::Healthcare Facilities] n=14, rank_cov=rank_available, cohesion=0.1095
- Other Financial Services [IND::Other Financial Services] n=14, rank_cov=rank_available, cohesion=0.0849
- Iron & Steel/Interm.Products [IND::Iron & Steel/Interm.Products] n=14, rank_cov=rank_available, cohesion=0.0602
- No-Rank Unclassified [UNCLASSIFIED::B::A::B::NoRank::1] n=14, rank_cov=no_rank_history, cohesion=nan
- No-Rank Unclassified [UNCLASSIFIED::B::A::B::NoRank::2] n=14, rank_cov=no_rank_history, cohesion=nan
- No-Rank Unclassified [UNCLASSIFIED::B::A::B::NoRank::3] n=14, rank_cov=no_rank_history, cohesion=nan
- Unclassified - Cluster A [UNCLASSIFIED::A::A] n=13, rank_cov=rank_available, cohesion=0.3213
- Realty - Cluster B [IND::Realty::B] n=13, rank_cov=rank_available, cohesion=0.2436
- Pharmaceuticals - Cluster B [IND::Pharmaceuticals::B::A::B::B] n=13, rank_cov=rank_available, cohesion=0.2369
- Personal Products [IND::Personal Products] n=13, rank_cov=rank_available, cohesion=0.1672
- Cement & Cement Products [IND::Cement & Cement Products] n=13, rank_cov=rank_available, cohesion=0.1375
- Breweries & Distilleries [IND::Breweries & Distilleries] n=13, rank_cov=rank_available, cohesion=0.1297
- Banks - Cluster A [IND::Banks::A] n=12, rank_cov=rank_available, cohesion=0.2964
- Electric Utilities - Cluster A [IND::Electric Utilities::A] n=12, rank_cov=rank_available, cohesion=0.2545
- Other Electrical Equipment/Products - Cluster B [IND::Other Electrical Equipment/Products::B] n=12, rank_cov=rank_available, cohesion=0.165
- Other Industrial Products [IND::Other Industrial Products] n=12, rank_cov=rank_available, cohesion=0.1066
- Consumer Electronics [IND::Consumer Electronics] n=12, rank_cov=rank_available, cohesion=0.0877
- Unclassified - Cluster B [UNCLASSIFIED::B::B::A::B::B] n=12, rank_cov=rank_available, cohesion=nan
- Auto Parts & Equipment - Cluster A [IND::Auto Parts & Equipment::B::B::A] n=11, rank_cov=rank_available, cohesion=0.1792