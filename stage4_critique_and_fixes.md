# Stage4 Critique and Fixes

## Criticism of previous work (Stage3)
- Logistics theme had very poor cohesion and mixed internet platforms with freight/shipping behaviors.
- Auto theme mixed OEM cycle and component cycle, reducing internal co-movement.
- Industrials theme mixed EMS/export engineering with power/electrification cyclicality.
- Some allocations were mathematically convenient but not specialist-coverage coherent.

## Top fixes implemented
- Split Auto into component-focused bucket and moved OEM names to mobility/logistics bucket.
- Split Industrials from Power/Electrification into separate analyst-style themes.
- Moved AIAENG to materials/mining-linked bucket; kept TI/RADICO/ABDL together in alcobev bucket.

## Quant impact
- Mean cohesion: Stage3 0.1002 -> Stage4 0.0949
- Worst-theme cohesion: Stage3 -0.1139 -> Stage4 -0.0789
- Coverage: 82 candidates, 82 covered, uncovered=0
- Duplicate assignments: 0

## Stage4 themes
- Healthcare_Pharma_Diagnostics_and_Lifesciences (n=10, cohesion=0.1556) | A: LAURUSLABS, SAILIFE, TORNTPHARM | B: ACUTAAS, METROPOLIS, SAGILITY | Top outliers: METROPOLIS, ACUTAAS, SAGILITY
- Banks_and_Regional_Lenders (n=9, cohesion=0.3039) | A: AXISBANK, FEDERALBNK, INDIANB | B: CANBK, IDFCFIRSTB, PNB | Top outliers: IDFCFIRSTB, CANBK, PNB
- Insurance_Wealth_and_Exchanges (n=9, cohesion=0.1553) | A: BSE, NUVAMA, SBILIFE | B: HDFCLIFE, IIFL, STAR | Top outliers: IIFL, STAR, HDFCLIFE
- Metals_Mining_and_Commodity_Materials (n=9, cohesion=0.138) | A: HINDALCO, JSWSTEEL, TATASTEEL | B: AIAENG, GMDCLTD, VEDL | Top outliers: AIAENG, GMDCLTD, VEDL
- NBFC_and_Credit_Platforms (n=8, cohesion=0.2508) | A: CHOLAFIN, MANAPPURAM | B: BAJFINANCE, SHRIRAMFIN | Top outliers: SHRIRAMFIN, BAJFINANCE, LTF
- Alcobev_Luxury_and_Discretionary_Retail (n=7, cohesion=0.1492) | A: RADICO, TITAN | B: ETHOSLTD, THANGAMAYL | Top outliers: ETHOSLTD, THANGAMAYL, ABDL
- Logistics_Travel_and_Mobility (n=7, cohesion=-0.0789) | A: ASHOKLEY, EICHERMOT | B: DELHIVERY, GESHIP | Top outliers: GESHIP, DELHIVERY, ADANIPORTS
- Auto_Ancillaries_and_Components (n=6, cohesion=-0.064) | A: FIEMIND, LUMAXTECH | B: AVL, MSUMI | Top outliers: MSUMI, AVL, CRAFTSMAN
- Industrials_EMS_and_Exports (n=6, cohesion=0.01) | A: AVALON, SENORES | B: APLAPOLLO, SYRMA | Top outliers: SYRMA, APLAPOLLO, SHAILY
- Tech_Telecom_and_Digital_Platforms (n=6, cohesion=0.0162) | A: BHARTIARTL, COFORGE | B: IDEA, PAYTM | Top outliers: IDEA, PAYTM, ETERNAL
- Power_and_Electrification (n=5, cohesion=0.0078) | A: GVT&D, WAAREEENER | B: MTARTECH, POWERINDIA | Top outliers: MTARTECH, POWERINDIA, ADANIPOWER