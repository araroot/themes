# Stage5 Deep Critique and Fixes

## Criticism of prior versions
- Previous min-size constraint (5+) forced unnatural merges across analyst coverage boundaries.
- STAR, AVL, and SENORES were in weak thematic homes relative to fundamentals.
- Telecom (domestic) and IT export services were blended, reducing specialist interpretability.

## Fixes implemented
- Relaxed minimum theme size to 3 (as requested).
- Explicit corrections: STAR -> Insurance; AVL -> Auto_Ancillaries_and_Components; SENORES -> Pharma_CDMO_and_Lifesciences.
- Split IT export/BPM from domestic telecom-digital consumer names.
- Kept TI/RADICO/ABDL together in dedicated Alcobev theme.

## Quality checks
- Coverage: candidates=82, assigned=82, uncovered=0, duplicates=0
- Cohesion mean Stage4 -> Stage5: 0.0949 -> 0.1344
- Worst-theme cohesion Stage4 -> Stage5: -0.0789 -> -0.0987

## Stage5 themes
- Banks_and_Regional_Lenders (n=9, cohesion=0.3039) | A: AXISBANK, FEDERALBNK, INDIANB | B: CANBK, IDFCFIRSTB, PNB | Top outliers: IDFCFIRSTB, CANBK, PNB
- NBFC_and_Credit_Platforms (n=8, cohesion=0.2508) | A: CHOLAFIN, MANAPPURAM | B: BAJFINANCE, SHRIRAMFIN | Top outliers: SHRIRAMFIN, BAJFINANCE, LTF
- Pharma_CDMO_and_Lifesciences (n=7, cohesion=0.2925) | A: ACUTAAS, NAVINFLUOR | B: LAURUSLABS, TORNTPHARM | Top outliers: TORNTPHARM, LAURUSLABS, SAILIFE
- Capital_Markets_and_Wealth (n=6, cohesion=0.1701) | A: BSE, MCX | B: IIFL, MFSL | Top outliers: IIFL, MFSL, 360ONE
- Auto_Ancillaries_and_Components (n=6, cohesion=-0.064) | A: FIEMIND, LUMAXTECH | B: AVL, MSUMI | Top outliers: MSUMI, AVL, CRAFTSMAN
- Steel_and_Engineering_Materials (n=6, cohesion=0.2076) | A: HEG, JSWSTEEL | B: AIAENG, PGIL | Top outliers: AIAENG, PGIL, TATASTEEL
- Power_and_Electrification (n=5, cohesion=0.0078) | A: WAAREEENER | B: MTARTECH | Top outliers: MTARTECH, POWERINDIA, ADANIPOWER
- Base_Metals_Mining_and_Commodities (n=5, cohesion=0.1323) | A: HINDALCO | B: VEDL | Top outliers: VEDL, GMDCLTD, HINDZINC
- Telecom_and_Digital_Consumer (n=4, cohesion=0.0224) | A: BHARTIARTL | B: IDEA | Top outliers: IDEA, PAYTM, ETERNAL
- Mobility_OEM_and_Platforms (n=4, cohesion=0.0158) | A: ASHOKLEY | B: CARTRADE | Top outliers: CARTRADE, IXIGO, EICHERMOT
- Luxury_and_Discretionary_Retail (n=4, cohesion=0.0897) | A: THANGAMAYL | B: V2RETAIL | Top outliers: V2RETAIL, ETHOSLTD, TITAN
- IT_Services_and_BPM (n=3, cohesion=0.1914) | A: ECLERX | B: SAGILITY | Top outliers: SAGILITY, COFORGE, ECLERX
- Industrials_EMS_and_Precision (n=3, cohesion=-0.0122) | A: SHAILY | B: SYRMA | Top outliers: SYRMA, AVALON, SHAILY
- Transport_Logistics_Infrastructure (n=3, cohesion=-0.0987) | A: ADANIPORTS | B: GESHIP | Top outliers: GESHIP, DELHIVERY, ADANIPORTS
- Insurance (n=3, cohesion=0.1486) | A: STAR | B: HDFCLIFE | Top outliers: HDFCLIFE, SBILIFE, STAR
- Healthcare_Services_and_Diagnostics (n=3, cohesion=0.1975) | A: THYROCARE | B: ASTERDM | Top outliers: ASTERDM, METROPOLIS, THYROCARE
- Alcobev (n=3, cohesion=0.4298) | A: RADICO | B: TI | Top outliers: TI, ABDL, RADICO