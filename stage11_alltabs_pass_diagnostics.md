# Stage11 Multi-Theme Build (Up to 3 Themes per Stock)

Design:
1) Keep Stage10 primary assignment for full coverage.
2) Add up to 2 secondary themes using fundamental-first routing (family/industry/sector).
3) Secondary gating by rank-fit vs theme centroid: corr>=0.30, resid<=0.20, score>=0.12.
4) Standardize labels to clean analyst-friendly names.

- Universe symbols: 818
- Theme count: 104
- Membership rows: 1192
- Symbols with 1 theme: 544
- Symbols with 2 themes: 174
- Symbols with 3 themes: 100
- Max themes per symbol: 3

Top themes by total size:
- Banks · Group 2 [IND::Banks::A]: primary=12, total=25, sec_add=13, coh_primary=0.2890, coh_total=0.2555
- Banks · Group 1 [IND::Banks::B::B]: primary=14, total=24, sec_add=10, coh_primary=0.3432, coh_total=0.2652
- Finance (including Nbfcs) · Group 2 [IND::Finance (including NBFCs)::B::B]: primary=8, total=24, sec_add=16, coh_primary=0.2809, coh_total=0.2763
- Iron & Steel / Interm.products [IND::Iron & Steel/Interm.Products]: primary=14, total=22, sec_add=8, coh_primary=0.0715, coh_total=0.1505
- Personal Products [IND::Personal Products]: primary=13, total=20, sec_add=7, coh_primary=0.2037, coh_total=0.2514
- Agrochemicals [IND::Agrochemicals]: primary=11, total=19, sec_add=8, coh_primary=0.1317, coh_total=0.1452
- Industrial Machinery · Group 2 [IND::Industrial Machinery::B]: primary=9, total=19, sec_add=10, coh_primary=0.0629, coh_total=0.1593
- Auto Parts & Equipment · Group 2 [IND::Auto Parts & Equipment::B::B::A]: primary=11, total=18, sec_add=7, coh_primary=0.2311, coh_total=0.1977
- Healthcare Facilities [IND::Healthcare Facilities]: primary=14, total=18, sec_add=4, coh_primary=0.0856, coh_total=0.1053
- Packaged Foods [IND::Packaged Foods]: primary=9, total=18, sec_add=9, coh_primary=0.1049, coh_total=0.2186
- Specialty Chemicals · Group 1 [IND::Specialty Chemicals::A]: primary=14, total=18, sec_add=4, coh_primary=0.0959, coh_total=0.1289
- Auto Parts & Equipment · Group 1 [IND::Auto Parts & Equipment::B::A]: primary=14, total=17, sec_add=3, coh_primary=0.1463, coh_total=0.1465
- Cross-sector · Group 1 [UNCLASSIFIED::B::A::B]: primary=14, total=17, sec_add=3, coh_primary=0.2809, coh_total=0.2725
- Heavy Electrical Equipment · Group 1 [IND::Heavy Electrical Equipment::A]: primary=8, total=17, sec_add=9, coh_primary=0.0864, coh_total=0.1753
- Other Industrial Products [IND::Other Industrial Products]: primary=12, total=17, sec_add=5, coh_primary=0.1465, coh_total=0.1877
- Banks · Group 3 [IND::Banks::B::A]: primary=4, total=16, sec_add=12, coh_primary=0.3996, coh_total=0.3016
- Breweries & Distilleries [IND::Breweries & Distilleries]: primary=14, total=16, sec_add=2, coh_primary=0.1412, coh_total=0.1541
- Cross-sector · Group 3 [UNCLASSIFIED::B::B::A::B::B]: primary=12, total=16, sec_add=4, coh_primary=nan, coh_total=0.2349
- Finance (including Nbfcs) · Group 1 [IND::Finance (including NBFCs)::B::A]: primary=8, total=16, sec_add=8, coh_primary=0.1368, coh_total=0.2077
- Other Electrical Equipment / Products · Group 1 [IND::Other Electrical Equipment/Products::B]: primary=12, total=16, sec_add=4, coh_primary=0.1715, coh_total=0.1565
