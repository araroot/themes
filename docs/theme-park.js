// Theme Park - Interactive Dashboard JavaScript
// Loads data files dynamically and builds tables client-side

// Global state
let manifest = null;
let themeMap = null;
let portfolioSymbols = new Set();
let allThemes = [];

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
    try {
        await loadManifest();
        await loadThemeDefinitions();
        populateDropdowns();
        setupEventListeners();
        await loadAndRenderData();
    } catch (error) {
        showError('Failed to initialize dashboard: ' + error.message);
        console.error(error);
    }
});

// Load manifest file
async function loadManifest() {
    const response = await fetch('manifest.json');
    if (!response.ok) throw new Error('Failed to load manifest');
    manifest = await response.json();
}

// Load theme definitions from PF_Ranks.xlsx
async function loadThemeDefinitions() {
    const response = await fetch(manifest.pf_ranks_path);
    if (!response.ok) throw new Error('Failed to load PF_Ranks.xlsx');

    const arrayBuffer = await response.arrayBuffer();
    const workbook = XLSX.read(arrayBuffer, { type: 'array' });

    // Load tpark_codex sheet
    const codexSheet = workbook.Sheets['tpark_codex'];
    const codexData = XLSX.utils.sheet_to_json(codexSheet);

    // Build theme map from tpark_codex
    themeMap = new Map();
    codexData.forEach(row => {
        if (row.Symbol && row.Theme) {
            const symbol = String(row.Symbol).trim().toUpperCase();
            const theme = normalizeThemeName(String(row.Theme));

            if (!themeMap.has(theme)) {
                themeMap.set(theme, []);
            }
            themeMap.get(theme).push(symbol);
        }
    });

    // Load PF_Ranks sheet for portfolio symbols
    const pfSheet = workbook.Sheets['PF_Ranks'];
    const pfData = XLSX.utils.sheet_to_json(pfSheet);

    portfolioSymbols = new Set();
    const portfolioSymbolsList = [];
    pfData.forEach(row => {
        const symbolCol = row['Symbol / Rank'] || row['Symbol'];
        if (symbolCol && isRealSymbol(symbolCol)) {
            const symbol = String(symbolCol).trim().toUpperCase();
            portfolioSymbols.add(symbol);
            portfolioSymbolsList.push(symbol);
        }
    });

    // Check if any portfolio symbols are missing from themeMap
    // If so, try loading from theme_park sheet as fallback
    const symbolsInThemeMap = new Set();
    themeMap.forEach(symbols => {
        symbols.forEach(s => symbolsInThemeMap.add(s));
    });

    const missingSymbols = portfolioSymbolsList.filter(s => !symbolsInThemeMap.has(s));

    if (missingSymbols.length > 0) {
        console.log(`Found ${missingSymbols.length} portfolio symbols not in tpark_codex, checking theme_park...`);
        // This is a placeholder - in practice GOODLUCK should be added to a theme
        // For now, add to "Other Portfolio Holdings" theme
        const otherTheme = "Other Portfolio Holdings";
        if (!themeMap.has(otherTheme)) {
            themeMap.set(otherTheme, []);
        }
        missingSymbols.forEach(s => {
            themeMap.get(otherTheme).push(s);
            console.log(`Added ${s} to ${otherTheme}`);
        });
    }

    // Get all themes sorted
    allThemes = Array.from(themeMap.keys()).sort();
}

// Normalize theme name
function normalizeThemeName(value) {
    const s = String(value).trim();
    if (!s || s.toLowerCase() === 'nan') return s;

    const keepUpper = new Set(['nbfc', 'psu', 'mnc', 'it', 'ai', 'ev', 'kpi', 'fmcg']);

    const normToken = (tok) => {
        if (/\d/.test(tok)) return tok;
        if (tok === tok.toUpperCase()) return tok;
        if (keepUpper.has(tok.toLowerCase())) return tok.toUpperCase();
        return tok.charAt(0).toUpperCase() + tok.slice(1).toLowerCase();
    };

    return s.split(/\s+/).map(normToken).join(' ');
}

// Check if symbol is real (not "Average Rank" etc.)
function isRealSymbol(val) {
    const s = String(val).trim().toLowerCase();
    if (!s || s === 'nan') return false;
    if (s.includes('avg rank') || s.includes('average rank')) return false;
    if (s.includes('kpi') && s.includes('rank')) return false;
    return true;
}

// Populate dropdown options
function populateDropdowns() {
    const currentSelect = document.getElementById('currentRankSelect');
    const prevSelect = document.getElementById('prevRankSelect');
    const pivotSelect = document.getElementById('pivotSelect');

    // Clear loading options
    currentSelect.innerHTML = '';
    prevSelect.innerHTML = '';
    pivotSelect.innerHTML = '';

    // Populate rank dropdowns
    manifest.rank_files.forEach((file, index) => {
        const option1 = document.createElement('option');
        option1.value = index;
        option1.textContent = file.display;
        currentSelect.appendChild(option1);

        const option2 = document.createElement('option');
        option2.value = index;
        option2.textContent = file.display;
        prevSelect.appendChild(option2);
    });

    // Populate pivot dropdown
    manifest.pivot_files.forEach((file, index) => {
        const option = document.createElement('option');
        option.value = index;
        option.textContent = file.display;
        pivotSelect.appendChild(option);
    });

    // Set defaults
    currentSelect.value = 0;

    // Auto-match pivot and previous rank to current rank
    updatePivotSelection();
    updatePrevRankSelection();
}

// Auto-match pivot file to current rank date
function updatePivotSelection() {
    const currentRankIndex = parseInt(document.getElementById('currentRankSelect').value);
    const currentRank = manifest.rank_files[currentRankIndex];

    if (!currentRank) return;

    const { year, month, day } = currentRank.date;

    // Determine target pivot month
    let targetYear = year;
    let targetMonth = month;

    if (day < 25) {
        // Mid-month: use previous month pivot
        targetMonth = month - 1;
        if (targetMonth < 1) {
            targetMonth = 12;
            targetYear -= 1;
        }
    }

    // Find matching pivot
    let matchedIndex = 0;
    for (let i = 0; i < manifest.pivot_files.length; i++) {
        const pivot = manifest.pivot_files[i];
        if (pivot.date.year === targetYear && pivot.date.month === targetMonth) {
            matchedIndex = i;
            break;
        }
    }

    // If no exact match, find closest earlier pivot
    if (matchedIndex === 0) {
        for (let i = 0; i < manifest.pivot_files.length; i++) {
            const pivot = manifest.pivot_files[i];
            if (pivot.date.year < targetYear ||
                (pivot.date.year === targetYear && pivot.date.month <= targetMonth)) {
                matchedIndex = i;
                break;
            }
        }
    }

    document.getElementById('pivotSelect').value = matchedIndex;
}

// Auto-populate previous rank to ~1 month before current rank
function updatePrevRankSelection() {
    const currentRankIndex = parseInt(document.getElementById('currentRankSelect').value);
    const currentRank = manifest.rank_files[currentRankIndex];
    if (!currentRank) return;

    const { year, month, day } = currentRank.date;

    // Calculate target date (1 month before)
    let targetYear = year;
    let targetMonth = month - 1;
    let targetDay = day;

    if (targetMonth < 1) {
        targetMonth = 12;
        targetYear -= 1;
    }

    // Find closest rank file to target date
    let bestIndex = currentRankIndex + 1; // Default to next in list (older)
    let minDiff = Infinity;

    for (let i = 0; i < manifest.rank_files.length; i++) {
        if (i === currentRankIndex) continue; // Skip current

        const rank = manifest.rank_files[i];
        const rankDate = new Date(rank.date.year, rank.date.month - 1, rank.date.day);
        const targetDate = new Date(targetYear, targetMonth - 1, targetDay);
        const diff = Math.abs(rankDate - targetDate);

        if (diff < minDiff) {
            minDiff = diff;
            bestIndex = i;
        }
    }

    document.getElementById('prevRankSelect').value = bestIndex;
}

// Setup event listeners
function setupEventListeners() {
    document.getElementById('currentRankSelect').addEventListener('change', () => {
        updatePivotSelection();
        updatePrevRankSelection();
        loadAndRenderData();
    });

    document.getElementById('prevRankSelect').addEventListener('change', loadAndRenderData);
    document.getElementById('pivotSelect').addEventListener('change', loadAndRenderData);
    document.getElementById('separatePortfolioToggle').addEventListener('change', loadAndRenderData);
    document.getElementById('highlightToggle').addEventListener('change', loadAndRenderData);
}

// Load CSV file
async function loadCSV(path) {
    return new Promise((resolve, reject) => {
        Papa.parse(path, {
            download: true,
            header: true,
            dynamicTyping: true,
            complete: (results) => resolve(results.data),
            error: (error) => reject(error)
        });
    });
}

// Load Excel file and return BB data and Impact data
async function loadPivotFile(path) {
    const response = await fetch(path);
    if (!response.ok) throw new Error('Failed to load pivot file');

    const arrayBuffer = await response.arrayBuffer();
    const workbook = XLSX.read(arrayBuffer, { type: 'array' });

    const sheet = workbook.Sheets['Summary Data'];
    const data = XLSX.utils.sheet_to_json(sheet);

    // Parse BB columns and sort chronologically (not alphabetically!)
    const bbData = new Map();
    const impactData = new Map();
    const fundQualityData = new Map();
    const bbColsRaw = Object.keys(data[0] || {}).filter(col => col.startsWith('bb_') && col !== 'bb_');

    // Sort BB columns chronologically
    const monthMap = {
        'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
        'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
    };

    const parseBBDate = (colName) => {
        // Extract month and year from column name like "bb_Dec25"
        const match = colName.match(/bb_([A-Za-z]+)(\d+)/);
        if (match) {
            const monthStr = match[1];
            const year = parseInt('20' + match[2]);
            const month = monthMap[monthStr.substring(0, 3)] || 0;
            return year * 12 + month; // Convert to sortable number
        }
        return 0;
    };

    const bbCols = bbColsRaw.sort((a, b) => parseBBDate(a) - parseBBDate(b));

    data.forEach(row => {
        const symbol = String(row.Symbol || '').trim().toUpperCase();
        if (!symbol) return;

        const last3 = bbCols.slice(-3).map(col => {
            const val = row[col];
            return (val !== null && val !== undefined && !isNaN(val)) ? parseInt(val) : null;
        }).filter(v => v !== null);

        if (last3.length > 0) {
            bbData.set(symbol, last3);
        }

        // Store impact value (keep highest impact for the symbol)
        const impact = row.Impact;
        if (impact !== null && impact !== undefined && !isNaN(impact)) {
            const currentImpact = impactData.get(symbol) || 0;
            impactData.set(symbol, Math.max(currentImpact, parseInt(impact)));
        }

        // Store fund quality value (keep highest FundQuality for the symbol)
        const fundQuality = row.FundQuality;
        if (fundQuality !== null && fundQuality !== undefined && !isNaN(fundQuality)) {
            const currentFQ = fundQualityData.get(symbol) || 0;
            fundQualityData.set(symbol, Math.max(currentFQ, parseInt(fundQuality)));
        }
    });

    return { bbData, impactData, fundQualityData };
}

// Build theme rank table
function buildThemeRankTable(rankCurrent, rankPrev, separatePortfolio = true, impactData = new Map(), fundQualityData = new Map(), enableHighlight = true) {
    const rows = [];

    allThemes.forEach(theme => {
        const themeSymbols = themeMap.get(theme) || [];

        let portfolioCells = [];
        let otherCells = [];
        let allCells = [];

        // Calculate median (filter out NaN, null, undefined)
        const currentRanks = themeSymbols
            .map(s => rankCurrent.get(s))
            .filter(r => r !== undefined && r !== null && !isNaN(r));

        const prevRanks = themeSymbols
            .map(s => rankPrev.get(s))
            .filter(r => r !== undefined && r !== null && !isNaN(r));

        const medianCurrent = currentRanks.length > 0 ? median(currentRanks) : null;
        const medianPrev = prevRanks.length > 0 ? median(prevRanks) : null;

        // Format median with delta
        let medianStr = '';
        if (medianCurrent !== null) {
            medianStr = String(Math.round(medianCurrent));
            if (medianPrev !== null) {
                const delta = Math.round(medianCurrent - medianPrev);
                if (delta < 0) {
                    medianStr += ` <span class="delta-up">(▲${Math.abs(delta)})</span>`;
                } else if (delta > 0) {
                    medianStr += ` <span class="delta-down">(▼${delta})</span>`;
                } else {
                    medianStr += ` <span class="delta-flat">(0)</span>`;
                }
            }
        }

        // Build symbol lists sorted by current rank (lowest/best first)
        const symbolData = themeSymbols
            .map(symbol => {
                const currRank = rankCurrent.get(symbol);
                if (currRank === undefined || currRank === null || isNaN(currRank)) return null;
                return { symbol, currRank };
            })
            .filter(item => item !== null)
            .sort((a, b) => a.currRank - b.currRank);

        symbolData.forEach(({ symbol, currRank }) => {
            const prevRank = rankPrev.get(symbol);
            const impact = impactData.get(symbol) || 0;
            const fundQuality = fundQualityData.get(symbol) || 0;

            let rankStr = `${symbol} ${Math.round(currRank)}`;

            if (prevRank !== undefined && prevRank !== null && !isNaN(prevRank)) {
                const delta = Math.round(currRank - prevRank);
                if (delta < 0) {
                    rankStr += ` <span class="delta-up">(▲${Math.abs(delta)})</span>`;
                } else if (delta > 0) {
                    rankStr += ` <span class="delta-down">(▼${delta})</span>`;
                } else {
                    rankStr += ` <span class="delta-flat">(0)</span>`;
                }
            } else {
                // No previous rank - show as green ▲0
                rankStr += ` <span class="delta-up">(▲0)</span>`;
            }

            // Highlight if BOTH impact=2 AND fundQuality=2 (and highlighting is enabled)
            if (enableHighlight && impact === 2 && fundQuality === 2) {
                rankStr = `<span style="background-color:#FFD700;padding:2px 4px;border-radius:3px;font-weight:700;">${rankStr}</span>`;
            }

            if (separatePortfolio) {
                if (portfolioSymbols.has(symbol)) {
                    portfolioCells.push(rankStr);
                } else {
                    otherCells.push(rankStr);
                }
            } else {
                allCells.push(rankStr);
            }
        });

        const rowData = {
            theme,
            median: medianStr,
            medianValue: medianCurrent !== null ? Math.round(medianCurrent) : 999, // For sorting
        };

        if (separatePortfolio) {
            rowData.portfolio = portfolioCells.join('<br/>');
            rowData.others = otherCells.join('<br/>');
        } else {
            rowData.all = allCells.join('<br/>');
        }

        rows.push(rowData);
    });

    // Sort by median rank (ascending - lower rank is better)
    rows.sort((a, b) => a.medianValue - b.medianValue);

    return rows;
}

// Build MF theme table
function buildMFThemeTable(bbData, rankCurrent, separatePortfolio = true, fundQualityData = new Map(), impactData = new Map(), enableHighlight = true) {
    const rows = [];

    allThemes.forEach(theme => {
        const themeSymbols = themeMap.get(theme) || [];

        let portfolioCells = [];
        let otherCells = [];
        let allCells = [];

        // Sort stocks by current rank (same order as rank table)
        const symbolData = themeSymbols
            .map(symbol => {
                const currRank = rankCurrent.get(symbol);
                const bbValues = bbData.get(symbol);
                if (!bbValues || bbValues.length === 0) return null;
                return { symbol, currRank: currRank || 999 };
            })
            .filter(item => item !== null)
            .sort((a, b) => a.currRank - b.currRank);

        symbolData.forEach(({ symbol }) => {
            const bbValues = bbData.get(symbol);
            const fundQuality = fundQualityData.get(symbol) || 0;
            const impact = impactData.get(symbol) || 0;
            let bbText = `${symbol} (${bbValues.join(', ')})`;

            // Highlight if BOTH impact=2 AND fundQuality=2 (and highlighting is enabled)
            if (enableHighlight && impact === 2 && fundQuality === 2) {
                bbText = `<span style="background-color:#FFD700;padding:2px 4px;border-radius:3px;font-weight:700;">${bbText}</span>`;
            }

            if (separatePortfolio) {
                if (portfolioSymbols.has(symbol)) {
                    portfolioCells.push(bbText);
                } else {
                    otherCells.push(bbText);
                }
            } else {
                allCells.push(bbText);
            }
        });

        const rowData = { theme };

        if (separatePortfolio) {
            rowData.portfolio = portfolioCells.join('<br/>');
            rowData.others = otherCells.join('<br/>');
        } else {
            rowData.all = allCells.join('<br/>');
        }

        rows.push(rowData);
    });

    return rows;
}

// Build combined table
function buildCombinedTable(rankRows, mfRows, separatePortfolio = true) {
    const combined = [];

    // Create a map of MF rows by theme for quick lookup
    const mfRowsByTheme = new Map();
    mfRows.forEach(row => {
        mfRowsByTheme.set(row.theme, row);
    });

    // Iterate over rankRows (already sorted by median)
    rankRows.forEach(rankRow => {
        const combinedRow = {
            theme: rankRow.theme,
            median: rankRow.median,
            separatePortfolio: separatePortfolio
        };

        if (separatePortfolio) {
            const mfRow = mfRowsByTheme.get(rankRow.theme) || { portfolio: '', others: '' };
            combinedRow.portfolioRank = rankRow.portfolio;
            combinedRow.portfolioBB = mfRow.portfolio;
            combinedRow.othersRank = rankRow.others;
            combinedRow.othersBB = mfRow.others;
        } else {
            const mfRow = mfRowsByTheme.get(rankRow.theme) || { all: '' };
            combinedRow.allRank = rankRow.all;
            combinedRow.allBB = mfRow.all;
        }

        combined.push(combinedRow);
    });

    return combined;
}

// Render combined table as HTML
function renderCombinedTable(rows, dateStr) {
    if (rows.length === 0) return '<div>No data</div>';

    const separatePortfolio = rows[0].separatePortfolio;

    let html = `
        <div style="margin:4px 0 8px 0;color:#666;font-size:12px;">
            Combined View: Ranks + MF Fund Signals - As of ${dateStr}
        </div>
        <table class="tp-table">
    `;

    if (separatePortfolio) {
        html += `
            <colgroup>
                <col style="width:10%">
                <col style="width:6%">
                <col style="width:21%">
                <col style="width:21%">
                <col style="width:21%">
                <col style="width:21%">
            </colgroup>
            <thead>
                <tr>
                    <th rowspan="2">Theme</th>
                    <th rowspan="2">Median<br/>(Rank Δ)</th>
                    <th colspan="2">Portfolio</th>
                    <th colspan="2">Others</th>
                </tr>
                <tr>
                    <th class="sub-header">Rank</th>
                    <th class="sub-header">Funds</th>
                    <th class="sub-header">Rank</th>
                    <th class="sub-header">Funds</th>
                </tr>
            </thead>
            <tbody>
        `;

        rows.forEach(row => {
            html += `
                <tr>
                    <td class="col-theme">${row.theme}</td>
                    <td class="col-median">${row.median}</td>
                    <td class="col-list">${row.portfolioRank}</td>
                    <td class="col-bb">${row.portfolioBB}</td>
                    <td class="col-list">${row.othersRank}</td>
                    <td class="col-bb">${row.othersBB}</td>
                </tr>
            `;
        });
    } else {
        html += `
            <colgroup>
                <col style="width:16%">
                <col style="width:8%">
                <col style="width:38%">
                <col style="width:38%">
            </colgroup>
            <thead>
                <tr>
                    <th rowspan="2">Theme</th>
                    <th rowspan="2">Median<br/>(Rank Δ)</th>
                    <th colspan="2">All Stocks</th>
                </tr>
                <tr>
                    <th class="sub-header">Rank</th>
                    <th class="sub-header">Funds</th>
                </tr>
            </thead>
            <tbody>
        `;

        rows.forEach(row => {
            html += `
                <tr>
                    <td class="col-theme">${row.theme}</td>
                    <td class="col-median">${row.median}</td>
                    <td class="col-list">${row.allRank}</td>
                    <td class="col-bb">${row.allBB}</td>
                </tr>
            `;
        });
    }

    html += `
            </tbody>
        </table>
    `;

    return html;
}

// Calculate median
function median(values) {
    if (values.length === 0) return null;
    const sorted = values.slice().sort((a, b) => a - b);
    const mid = Math.floor(sorted.length / 2);
    return sorted.length % 2 === 0 ? (sorted[mid - 1] + sorted[mid]) / 2 : sorted[mid];
}

// Load and render data based on current dropdown selections
async function loadAndRenderData() {
    const container = document.getElementById('tableContainer');
    container.innerHTML = '<div class="loading">Loading data</div>';

    try {
        const currentRankIndex = parseInt(document.getElementById('currentRankSelect').value);
        const prevRankIndex = parseInt(document.getElementById('prevRankSelect').value);
        const pivotIndex = parseInt(document.getElementById('pivotSelect').value);

        const currentRankFile = manifest.rank_files[currentRankIndex];
        const prevRankFile = manifest.rank_files[prevRankIndex];
        const pivotFile = manifest.pivot_files[pivotIndex];

        // Update info bar
        document.getElementById('currentRankDisplay').textContent = currentRankFile.display;
        document.getElementById('pivotDisplay').textContent = pivotFile.display;

        // Load data files
        const [currentRankData, prevRankData, pivotData] = await Promise.all([
            loadCSV(currentRankFile.path),
            loadCSV(prevRankFile.path),
            loadPivotFile(pivotFile.path)
        ]);

        const { bbData, impactData, fundQualityData } = pivotData;

        // Convert to maps
        const rankCurrent = new Map();
        const rankPrev = new Map();

        currentRankData.forEach(row => {
            if (row.symbol) {
                rankCurrent.set(String(row.symbol).trim().toUpperCase(), row.ptile);
            }
        });

        prevRankData.forEach(row => {
            if (row.symbol) {
                rankPrev.set(String(row.symbol).trim().toUpperCase(), row.ptile);
            }
        });

        // Get flags from checkboxes
        const separatePortfolio = document.getElementById('separatePortfolioToggle').checked;
        const enableHighlight = document.getElementById('highlightToggle').checked;

        // Build tables
        const rankRows = buildThemeRankTable(rankCurrent, rankPrev, separatePortfolio, impactData, fundQualityData, enableHighlight);
        const mfRows = buildMFThemeTable(bbData, rankCurrent, separatePortfolio, fundQualityData, impactData, enableHighlight);
        const combinedRows = buildCombinedTable(rankRows, mfRows, separatePortfolio);

        // IMPORTANT CHECK: Verify all portfolio symbols are in the dashboard
        checkMissingPortfolioSymbols(combinedRows, rankCurrent);

        // Render
        const html = renderCombinedTable(combinedRows, currentRankFile.display);
        container.innerHTML = html;

    } catch (error) {
        showError('Failed to load data: ' + error.message);
        console.error(error);
    }
}

// Check if any portfolio symbols are missing from dashboard
function checkMissingPortfolioSymbols(combinedRows, rankCurrent) {
    // Get all symbols shown in dashboard
    const displayedSymbols = new Set();

    themeMap.forEach((symbols, theme) => {
        symbols.forEach(symbol => {
            // Only count symbols that have current rank data (actually displayed)
            if (rankCurrent.has(symbol) && !isNaN(rankCurrent.get(symbol))) {
                displayedSymbols.add(symbol);
            }
        });
    });

    // Find missing portfolio symbols
    const missingSymbols = Array.from(portfolioSymbols).filter(symbol => {
        // Symbol is missing if it's NOT displayed AND has rank data available
        return !displayedSymbols.has(symbol) && rankCurrent.has(symbol);
    });

    const alertDiv = document.getElementById('missingSymbolsAlert');
    const listDiv = document.getElementById('missingSymbolsList');

    if (missingSymbols.length > 0) {
        // Show warning
        alertDiv.style.display = 'block';
        listDiv.innerHTML = missingSymbols.sort().map(s => `<span style="display:inline-block;margin:0 8px 4px 0;">${s}</span>`).join('');
        console.error(`⚠️ MISSING PORTFOLIO SYMBOLS (${missingSymbols.length}):`, missingSymbols);
    } else {
        // Hide warning
        alertDiv.style.display = 'none';
        console.log('✓ All portfolio symbols accounted for in dashboard');
    }
}

// Show error message
function showError(message) {
    const container = document.getElementById('tableContainer');
    container.innerHTML = `
        <div class="error">
            <strong>Error:</strong> ${message}
        </div>
    `;
}
