# Stage6 Deep Critique and Fixes (Final)

## Explicit criticism of prior work
- Over-constrained min size caused forced mixes across specialist coverage lines.
- STAR, AVL, SENORES were mis-slotted in earlier drafts.
- Domestic telecom and IT exporters were mixed; this was analytically wrong for coverage ownership.
- Splitting transport too aggressively into tiny sub-buckets created unstable rank-cohesion.

## Top issues fixed
- Min theme size relaxed to 3.
- STAR -> Insurance; AVL -> Auto_Ancillaries_and_Components; SENORES -> Pharma_CDMO_and_Lifesciences.
- IT_Services_and_BPM separated from Telecom_and_Digital_Consumer.
- Transport and mobility merged into a single specialist transport theme to avoid unstable micro-buckets.

## Validation
- Coverage: candidates=82, assigned=82, uncovered=0, duplicates=0
- Cohesion mean: Stage4 0.0949 | Stage5 0.1344 | Stage6 0.1431
- Worst-theme cohesion: Stage4 -0.0789 | Stage5 -0.0987 | Stage6 -0.0789

## Stage6 themes
- Banks_and_Regional_Lenders (n=9, cohesion=0.3039) | A: AXISBANK, FEDERALBNK, INDIANB | B: CANBK, IDFCFIRSTB, PNB | Top outliers: IDFCFIRSTB, CANBK, PNB
- NBFC_and_Credit_Platforms (n=8, cohesion=0.2508) | A: CHOLAFIN, MANAPPURAM | B: BAJFINANCE, SHRIRAMFIN | Top outliers: SHRIRAMFIN, BAJFINANCE, LTF
- Transport_and_Mobility (n=7, cohesion=-0.0789) | A: ASHOKLEY, EICHERMOT | B: DELHIVERY, GESHIP | Top outliers: GESHIP, DELHIVERY, ADANIPORTS
- Pharma_CDMO_and_Lifesciences (n=7, cohesion=0.2925) | A: ACUTAAS, NAVINFLUOR | B: LAURUSLABS, TORNTPHARM | Top outliers: TORNTPHARM, LAURUSLABS, SAILIFE
- Capital_Markets_and_Wealth (n=6, cohesion=0.1701) | A: BSE, MCX | B: IIFL, MFSL | Top outliers: IIFL, MFSL, 360ONE
- Auto_Ancillaries_and_Components (n=6, cohesion=-0.064) | A: FIEMIND, LUMAXTECH | B: AVL, MSUMI | Top outliers: MSUMI, AVL, CRAFTSMAN
- Steel_and_Engineering_Materials (n=6, cohesion=0.2076) | A: HEG, JSWSTEEL | B: AIAENG, PGIL | Top outliers: AIAENG, PGIL, TATASTEEL
- Base_Metals_Mining_and_Commodities (n=5, cohesion=0.1323) | A: HINDALCO | B: VEDL | Top outliers: VEDL, GMDCLTD, HINDZINC
- Power_and_Electrification (n=5, cohesion=0.0078) | A: WAAREEENER | B: MTARTECH | Top outliers: MTARTECH, POWERINDIA, ADANIPOWER
- Telecom_and_Digital_Consumer (n=4, cohesion=0.0224) | A: BHARTIARTL | B: IDEA | Top outliers: IDEA, PAYTM, ETERNAL
- Luxury_and_Discretionary_Retail (n=4, cohesion=0.0897) | A: THANGAMAYL | B: V2RETAIL | Top outliers: V2RETAIL, ETHOSLTD, TITAN
- Insurance (n=3, cohesion=0.1486) | A: STAR | B: HDFCLIFE | Top outliers: HDFCLIFE, SBILIFE, STAR
- IT_Services_and_BPM (n=3, cohesion=0.1914) | A: ECLERX | B: SAGILITY | Top outliers: SAGILITY, COFORGE, ECLERX
- Industrials_EMS_and_Precision (n=3, cohesion=-0.0122) | A: SHAILY | B: SYRMA | Top outliers: SYRMA, AVALON, SHAILY
- Healthcare_Services_and_Diagnostics (n=3, cohesion=0.1975) | A: THYROCARE | B: ASTERDM | Top outliers: ASTERDM, METROPOLIS, THYROCARE
- Alcobev (n=3, cohesion=0.4298) | A: RADICO | B: TI | Top outliers: TI, ABDL, RADICO