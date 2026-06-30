#!/usr/bin/env python3
"""
Nasdaq Chart Dashboard Generator (V5 - Tabbed Multi-Security Dashboard)
------------------------------------------------------------------------
Generates index.html at root workspace.
Loads all *_nasdaq_dataset.json files from the downloads/ directory,
injects them into the template, and renders a dynamic horizontal Tab Bar
at the top of the main dashboard area. Each tab preserves its own chart states.
Supports light/dark themes, stats KPIs, synchronized ApexCharts,
client-side CSV downloads, and dynamic technical analysis writeups.
"""

import os
import json
import sys

def generate_qmd(datasets_dict, qmd_output_path):
    if not datasets_dict:
        print("Error: No datasets found to inject.", file=sys.stderr)
        sys.exit(1)
        
    # Inject all datasets into JSON
    data_js = json.dumps(datasets_dict)
    
    # Grab first ticker as default
    default_ticker = "AAPL" if "AAPL" in datasets_dict else sorted(list(datasets_dict.keys()))[0]

    qmd_template = """---
title: "Asset Analytics Dashboard"
page-layout: custom
toc: false
---

```{=html}
<!-- Google Fonts -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">

<!-- ApexCharts -->
<script src="https://cdn.jsdelivr.net/npm/apexcharts"></script>
    
    <style>
        :root {
            --bg-primary: #0b0f19;
            --bg-secondary: #111827;
            --sidebar-bg: #0f172a;
            --panel-bg: rgba(30, 41, 59, 0.4);
            --panel-border: rgba(255, 255, 255, 0.08);
            
            --accent-blue: #3b82f6;
            --accent-blue-hover: #2563eb;
            --accent-green: #10b981;
            --accent-red: #ef4444;
            --accent-yellow: #f59e0b;
            --accent-pink: #ec4899;
            
            --text-primary: #f9fafb;
            --text-secondary: #9ca3af;
            --text-muted: #6b7280;
            
            --sidebar-width: 320px;
        }
        
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background-color: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
            display: flex;
            overflow-x: hidden;
            transition: background-color 0.3s ease, color 0.3s ease;
        }
        
        body.theme-light {
            --bg-primary: #f8fafc;
            --bg-secondary: #ffffff;
            --sidebar-bg: #f1f5f9;
            --panel-bg: rgba(241, 245, 249, 0.8);
            --panel-border: rgba(0, 0, 0, 0.08);
            --text-primary: #0f172a;
            --text-secondary: #475569;
            --text-muted: #94a3b8;
        }
        
        /* Sidebar Layout */
        .sidebar {
            width: var(--sidebar-width);
            background-color: var(--sidebar-bg);
            border-right: 1px solid var(--panel-border);
            padding: 2rem 1.5rem;
            display: flex;
            flex-direction: column;
            gap: 2rem;
            height: calc(100vh - 56px);
            position: fixed;
            top: 56px;
            left: 0;
            overflow-y: auto;
            z-index: 10;
            transition: background-color 0.3s ease, border-color 0.3s ease;
        }
        
        .brand {
            display: flex;
            flex-direction: column;
            gap: 0.25rem;
        }
        
        .brand h2 {
            font-size: 1.35rem;
            font-weight: 800;
            letter-spacing: -0.025em;
            background: linear-gradient(to right, #60a5fa, #a5b4fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .brand p {
            color: var(--text-muted);
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            font-weight: 700;
        }
        
        .sidebar-section {
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
        }
        
        .sidebar-section-title {
            font-size: 0.75rem;
            font-weight: 700;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 0.25rem;
        }
        
        /* Controls UI */
        .select-input {
            width: 100%;
            background-color: rgba(15, 23, 42, 0.1);
            border: 1px solid var(--panel-border);
            color: var(--text-primary);
            padding: 0.65rem 0.85rem;
            border-radius: 8px;
            font-size: 0.9rem;
            font-family: inherit;
            outline: none;
            cursor: pointer;
            transition: border-color 0.2s ease, background-color 0.2s ease;
        }
        
        body:not(.theme-light) .select-input {
            background-color: rgba(15, 23, 42, 0.6);
        }
        
        .select-input:focus {
            border-color: var(--accent-blue);
        }
        
        .radio-group {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }
        
        .radio-label {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            font-size: 0.9rem;
            color: var(--text-secondary);
            cursor: pointer;
            padding: 0.5rem 0.75rem;
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid transparent;
            transition: all 0.2s ease;
        }
        
        .radio-label:hover {
            background: rgba(255, 255, 255, 0.05);
            color: var(--text-primary);
        }
        
        .radio-label.active {
            background: rgba(59, 130, 246, 0.08);
            border-color: rgba(59, 130, 246, 0.3);
            color: #60a5fa;
            font-weight: 500;
        }
        
        .radio-label input {
            display: none;
        }
        
        .checkbox-group {
            display: flex;
            flex-direction: column;
            gap: 0.65rem;
        }
        
        .checkbox-label {
            display: flex;
            align-items: center;
            gap: 0.65rem;
            font-size: 0.9rem;
            color: var(--text-secondary);
            cursor: pointer;
            user-select: none;
        }
        
        .checkbox-label input {
            accent-color: var(--accent-blue);
            width: 1rem;
            height: 1rem;
        }
        
        /* Segmented Toggle Control */
        .toggle-pill-group {
            display: flex;
            background-color: rgba(15, 23, 42, 0.45);
            border: 1px solid var(--panel-border);
            border-radius: 8px;
            padding: 0.25rem;
            width: 100%;
            box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.25);
        }
        
        body.theme-light .toggle-pill-group {
            background-color: rgba(0, 0, 0, 0.05);
            box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.08);
        }
        
        .btn-toggle {
            flex: 1;
            background: transparent;
            border: none;
            color: var(--text-secondary);
            padding: 0.5rem;
            font-size: 0.85rem;
            font-weight: 600;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s ease;
            text-align: center;
        }
        
        .btn-toggle:hover {
            color: var(--text-primary);
        }
        
        .btn-toggle.active {
            background: linear-gradient(to bottom, #3b82f6, #2563eb);
            color: white;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.2);
        }
        
        /* Action Button */
        .btn-primary {
            background-color: var(--accent-blue);
            color: white;
            border: none;
            padding: 0.75rem 1rem;
            border-radius: 8px;
            font-size: 0.9rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.25);
        }
        
        .btn-primary:hover {
            background-color: var(--accent-blue-hover);
            box-shadow: 0 4px 16px rgba(59, 130, 246, 0.35);
        }
        
        /* Main Layout Content */
        .main-content {
            flex: 1;
            margin-left: var(--sidebar-width);
            padding: 2rem 2.5rem;
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
            min-width: 0;
            margin-top: 56px;
            min-height: calc(100vh - 56px);
        }
        
        /* Top Navigation Bar */
        .top-navbar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--panel-border);
            padding-bottom: 1rem;
        }
        
        .ticker-details {
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        
        .company-name {
            font-size: 1.4rem;
            font-weight: 700;
            letter-spacing: -0.02em;
        }
        
        /* Tab Bar Styling */
        .tab-bar {
            display: flex;
            gap: 0.75rem;
            border-bottom: 1px solid var(--panel-border);
            padding-bottom: 1rem;
            margin-bottom: 0.5rem;
            flex-wrap: wrap;
        }
        
        .tab-btn {
            background-color: rgba(255, 255, 255, 0.02);
            border: 1px solid var(--panel-border);
            color: var(--text-secondary);
            padding: 0.65rem 1.25rem;
            border-radius: 8px;
            font-size: 0.9rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .tab-btn:hover {
            background-color: rgba(255, 255, 255, 0.06);
            color: var(--text-primary);
        }
        
        .tab-btn.active {
            background: linear-gradient(to bottom, #3b82f6, #2563eb);
            border-color: #3b82f6;
            color: white;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
        }
        
        body.theme-light .tab-btn {
            background-color: rgba(0, 0, 0, 0.02);
        }
        
        body.theme-light .tab-btn:hover {
            background-color: rgba(0, 0, 0, 0.05);
        }
        
        .tab-badge {
            background-color: rgba(255, 255, 255, 0.15);
            padding: 0.15rem 0.4rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 800;
        }
        
        .tab-btn.active .tab-badge {
            background-color: rgba(255,255,255,0.25);
        }
        
        /* KPIs Grid */
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.25rem;
        }
        
        .kpi-card {
            background-color: var(--bg-secondary);
            border: 1px solid var(--panel-border);
            border-radius: 12px;
            padding: 1.25rem;
            display: flex;
            flex-direction: column;
            gap: 0.4rem;
            transition: background-color 0.3s ease, border-color 0.3s ease;
        }
        
        .kpi-label {
            font-size: 0.75rem;
            font-weight: 600;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        .kpi-value {
            font-size: 1.5rem;
            font-weight: 700;
            font-family: 'JetBrains Mono', monospace;
        }
        
        .kpi-sub {
            font-size: 0.8rem;
            font-weight: 500;
        }
        
        /* Dynamic HUD Bar style (Screenshot Replica) */
        .hud-bar {
            background-color: var(--bg-secondary);
            border: 1px solid var(--panel-border);
            border-radius: 12px;
            padding: 1rem 1.5rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.85rem;
            flex-wrap: wrap;
            gap: 1.5rem;
            transition: background-color 0.3s ease, border-color 0.3s ease;
        }
        
        .hud-symbol-block {
            display: flex;
            flex-direction: column;
            gap: 0.15rem;
            border-right: 1px solid var(--panel-border);
            padding-right: 1.5rem;
        }
        
        .hud-symbol {
            font-size: 1.35rem;
            font-weight: 800;
            color: var(--text-primary);
            letter-spacing: -0.01em;
        }
        
        .hud-company {
            font-size: 0.7rem;
            font-weight: 700;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        .hud-metrics {
            display: flex;
            gap: 2rem;
            flex: 1;
            flex-wrap: wrap;
        }
        
        .hud-metric-col {
            display: flex;
            flex-direction: column;
            gap: 0.25rem;
            color: var(--text-muted);
            min-width: 110px;
        }
        
        .hud-metric-col div {
            display: flex;
            justify-content: space-between;
            gap: 0.5rem;
        }
        
        .hud-value {
            font-weight: 700;
            color: var(--text-primary);
            font-family: 'JetBrains Mono', monospace;
        }
        
        .hud-value.gain {
            color: var(--accent-green);
        }
        
        .hud-value.loss {
            color: var(--accent-red);
        }
        
        /* Chart container */
        .chart-container {
            background-color: var(--bg-secondary);
            border: 1px solid var(--panel-border);
            border-radius: 16px;
            padding: 1.75rem;
            display: flex;
            flex-direction: column;
            gap: 1.25rem;
            box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.3);
            transition: background-color 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease;
        }
        
        body.theme-light .chart-container {
            box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.06);
        }
        
        .chart-panel-title {
            font-size: 1.05rem;
            font-weight: 700;
            color: var(--text-primary);
            border-left: 3px solid var(--accent-blue);
            padding-left: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.03em;
        }
        
        /* Quantitative Analysis Report Panel */
        .analysis-container {
            background-color: var(--bg-secondary);
            border: 1px solid var(--panel-border);
            border-radius: 16px;
            padding: 2rem;
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
            transition: background-color 0.3s ease, border-color 0.3s ease;
        }
        
        .analysis-header {
            border-bottom: 1px solid var(--panel-border);
            padding-bottom: 1rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        
        .analysis-header h3 {
            font-size: 1.15rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-primary);
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .analysis-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 2rem;
        }
        
        .analysis-card {
            background-color: rgba(15, 23, 42, 0.15);
            border: 1px solid var(--panel-border);
            border-radius: 12px;
            padding: 1.5rem;
        }
        
        body:not(.theme-light) .analysis-card {
            background-color: rgba(15, 23, 42, 0.4);
        }
        
        .analysis-card-title {
            font-size: 0.85rem;
            font-weight: 700;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .analysis-metric-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(255,255,255,0.03);
            padding: 0.65rem 0;
            font-size: 0.9rem;
        }
        
        body.theme-light .analysis-metric-row {
            border-bottom-color: rgba(0,0,0,0.03);
        }
        
        .analysis-metric-row:last-child {
            border-bottom: none;
        }
        
        .analysis-metric-label {
            color: var(--text-secondary);
        }
        
        .analysis-metric-value {
            font-weight: 600;
            font-family: 'JetBrains Mono', monospace;
        }
        
        .writeup {
            font-size: 0.95rem;
            color: var(--text-secondary);
            line-height: 1.7;
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }
        
        .writeup p strong {
            color: var(--text-primary);
        }
        
        .tag-pill {
            font-size: 0.75rem;
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            font-weight: 600;
            text-transform: uppercase;
        }
        
        .tag-bullish {
            background-color: rgba(16, 185, 129, 0.1);
            color: var(--accent-green);
        }
        
        .tag-bearish {
            background-color: rgba(239, 68, 68, 0.1);
            color: var(--accent-red);
        }
        
        .tag-neutral {
            background-color: rgba(245, 158, 11, 0.1);
            color: var(--accent-yellow);
        }
        
        .gain { color: var(--accent-green); }
        .loss { color: var(--accent-red); }
        .text-green { color: var(--accent-green) !important; }
        .text-red { color: var(--accent-red) !important; }
    </style>

    <!-- Sidebar controls -->
    <div class="sidebar">
        <div class="brand">
            <h2>MARKET ANALYTICS</h2>
            <p>Nasdaq Charting V5</p>
        </div>
        
        <!-- Setting: Color Theme -->
        <div class="sidebar-section">
            <div class="sidebar-section-title">Color Theme</div>
            <div class="toggle-pill-group">
                <button class="btn-toggle active" id="btn-theme-dark" onclick="setThemeStyle('dark')">Dark</button>
                <button class="btn-toggle" id="btn-theme-light" onclick="setThemeStyle('light')">Light</button>
            </div>
        </div>
        
        <!-- Setting: Date Range -->
        <div class="sidebar-section">
            <div class="sidebar-section-title">Timeframe Range</div>
            <div class="radio-group" id="range-picker">
                <label class="radio-label" id="lbl-5y">
                    <input type="radio" name="timeframe" value="5Y" checked> 5 Years (Full Data)
                </label>
                <label class="radio-label" id="lbl-3y">
                    <input type="radio" name="timeframe" value="3Y"> 3 Years
                </label>
                <label class="radio-label" id="lbl-1y">
                    <input type="radio" name="timeframe" value="1Y"> 1 Year
                </label>
                <label class="radio-label" id="lbl-6m">
                    <input type="radio" name="timeframe" value="6M"> 6 Months
                </label>
                <label class="radio-label" id="lbl-1m">
                    <input type="radio" name="timeframe" value="1M"> 1 Month
                </label>
            </div>
        </div>
        
        <!-- Setting: Chart Style -->
        <div class="sidebar-section">
            <div class="sidebar-section-title">Chart Representation</div>
            <div class="toggle-pill-group">
                <button class="btn-toggle active" id="btn-chart-line" onclick="setChartStyle('line')">Line</button>
                <button class="btn-toggle" id="btn-chart-candle" onclick="setChartStyle('candlestick')">Candle</button>
            </div>
        </div>
        
        <!-- Setting: Indicators -->
        <div class="sidebar-section">
            <div class="sidebar-section-title">Technical Overlays</div>
            <div class="checkbox-group">
                <label class="checkbox-label">
                    <input type="checkbox" id="chk-sma50" checked onchange="onOverlayChange()"> Show 50-day SMA
                </label>
                <label class="checkbox-label">
                    <input type="checkbox" id="chk-sma200" checked onchange="onOverlayChange()"> Show 200-day SMA
                </label>
            </div>
        </div>
        
        <!-- Actions: Download Data -->
        <div class="sidebar-section" style="margin-top: auto;">
            <button class="btn-primary" onclick="downloadCSV()">
                <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                    <path d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path>
                </svg>
                Export CSV Dataset
            </button>
        </div>
    </div>

    <!-- Main Content Area -->
    <div class="main-content">
        
        <!-- Navigation Header -->
        <div class="top-navbar">
            <div class="ticker-details">
                <span class="company-name">Financial Terminal</span>
            </div>
            <div style="font-size: 0.85rem; color: var(--text-muted);">
                Server Connection: <strong style="color: var(--accent-green)">Live Active</strong>
            </div>
        </div>
        
        <!-- Tab Bar for Stocks -->
        <div class="tab-bar" id="ticker-tab-bar">
            <!-- Populated dynamically via JS -->
        </div>
        
        <!-- Tab Layouts container -->
        <div id="tab-contents-wrapper">
            <!-- Dynamically populated stock layouts panels -->
        </div>
        
    </div>

    <script>
        // Injected raw stock data maps
        const stockDatasets = {data_js};
        let currentTicker = "{default_ticker}";
        let currentTheme = "dark";
        
        const companyNames = {
            "AAPL": "Apple Inc.",
            "TSLA": "Tesla Inc.",
            "NVDA": "NVIDIA Corp.",
            "AMZN": "Amazon.com Inc.",
            "DIS": "The Walt Disney Co.",
            "MSFT": "Microsoft Corp."
        };
        
        const companyShortNames = {
            "AAPL": "Apple",
            "TSLA": "Tesla",
            "NVDA": "NVIDIA",
            "AMZN": "Amazon",
            "DIS": "Disney",
            "MSFT": "Microsoft"
        };
        
        // Maps to hold data and calculated SMA indicators for each ticker
        const datasets = {};
        const sma50FullMaps = {};
        const sma200FullMaps = {};
        
        // Maps to hold active data for the current viewport for each ticker
        const activeDataMaps = {};
        const activeSma50Maps = {};
        const activeSma200Maps = {};
        
        // Maps to hold ApexCharts instances
        const priceCharts = {};
        const volumeCharts = {};
        
        const initializedStocks = new Set();
        const activeFilteredDataMaps = {};
        let activeZoomStart = null;
        let activeZoomEnd = null;
        
        // Active state variables
        let activeChartType = "line";
        let activeZoomCount = 90;
        let activeRangeCode = "5Y";

        // Initialize Webpage
        document.addEventListener("DOMContentLoaded", () => {
            const availableTickers = Object.keys(stockDatasets);
            if (availableTickers.length > 0) {
                currentTicker = availableTickers.includes("AAPL") ? "AAPL" : availableTickers[0];
            }
            
            // Build tab layouts first
            availableTickers.forEach(ticker => {
                createStockLayout(ticker);
                preprocessStockData(ticker);
            });
            
            buildTabBar();
            setupSidebarListeners();
            
            // Open default stock tab
            switchTab(currentTicker);
        });

        // Preprocess raw datasets and calculate SMAs
        function preprocessStockData(ticker) {
            const rawData = stockDatasets[ticker] || [];
            const sortedData = rawData.map(d => {
                const parts = d.Date.split('-');
                const timestamp = Date.UTC(parseInt(parts[0]), parseInt(parts[1]) - 1, parseInt(parts[2]));
                return {
                    date: d.Date,
                    timestamp: timestamp,
                    open: d.Open,
                    high: d.High,
                    low: d.Low,
                    close: d.Close,
                    volume: d.Volume,
                    price: d.Price || d.Close
                };
            }).sort((a, b) => a.timestamp - b.timestamp);
            
            datasets[ticker] = sortedData;
            sma50FullMaps[ticker] = calculateSMA(sortedData, 50);
            sma200FullMaps[ticker] = calculateSMA(sortedData, 200);
        }

        // Dynamically build tab header buttons
        function buildTabBar() {
            const tabBar = document.getElementById("ticker-tab-bar");
            tabBar.innerHTML = "";
            
            Object.keys(stockDatasets).sort().forEach(ticker => {
                const button = document.createElement("button");
                button.className = "tab-btn";
                button.id = `tab-btn-${ticker}`;
                button.onclick = () => switchTab(ticker);
                
                const spanBadge = document.createElement("span");
                spanBadge.className = "tab-badge";
                spanBadge.innerText = ticker;
                
                const textLabel = document.createTextNode(companyShortNames[ticker] || ticker);
                
                button.appendChild(spanBadge);
                button.appendChild(textLabel);
                tabBar.appendChild(button);
            });
        }

        // Dynamically generate individual content panels in HTML
        function createStockLayout(ticker) {
            const wrapper = document.getElementById("tab-contents-wrapper");
            
            const content = document.createElement("div");
            content.id = `content-${ticker}`;
            content.className = "stock-content-panel";
            content.style.display = "none";
            
            content.innerHTML = `
                <!-- KPI Row -->
                <div class="kpi-grid">
                    <div class="kpi-card">
                        <div class="kpi-label">Latest Close</div>
                        <div class="kpi-value" id="kpi-latest-${ticker}">-</div>
                        <div class="kpi-sub" id="kpi-change-${ticker}">-</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-label">Average Close</div>
                        <div class="kpi-value" id="kpi-avg-${ticker}">-</div>
                        <div class="kpi-sub" style="color: var(--text-muted);">Selected range</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-label">Period Peak</div>
                        <div class="kpi-value" id="kpi-high-${ticker}" style="color: var(--accent-green)">-</div>
                        <div class="kpi-sub" id="kpi-high-date-${ticker}" style="color: var(--text-muted);">-</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-label">Period Floor</div>
                        <div class="kpi-value" id="kpi-low-${ticker}" style="color: var(--accent-red)">-</div>
                        <div class="kpi-sub" id="kpi-low-date-${ticker}" style="color: var(--text-muted);">-</div>
                    </div>
                </div>
                
                <!-- Chart HUD & Chart Panel -->
                <div class="chart-container">
                    <div class="hud-bar">
                        <div class="hud-symbol-block">
                            <span class="hud-symbol">${ticker}</span>
                            <span class="hud-company">${companyNames[ticker] || ticker}</span>
                        </div>
                        <div class="hud-metrics">
                            <div class="hud-metric-col">
                                <div>LAST: <span id="hud-last-${ticker}" class="hud-value">-</span></div>
                                <div>VOLUME: <span id="hud-volume-${ticker}" class="hud-value">-</span></div>
                            </div>
                            <div class="hud-metric-col">
                                <div>CHANGE: <span id="hud-change-${ticker}" class="hud-value">-</span></div>
                            </div>
                            <div class="hud-metric-col">
                                <div>OPEN: <span id="hud-open-${ticker}" class="hud-value">-</span></div>
                                <div>CLOSE: <span id="hud-close-${ticker}" class="hud-value">-</span></div>
                            </div>
                            <div class="hud-metric-col">
                                <div>HIGH: <span id="hud-high-${ticker}" class="hud-value">-</span></div>
                                <div>LOW: <span id="hud-low-${ticker}" class="hud-value">-</span></div>
                            </div>
                            <div class="hud-metric-col">
                                <div>DATE: <span id="hud-date-${ticker}" class="hud-value">-</span></div>
                            </div>
                        </div>
                    </div>
                    
                    <div id="price-chart-${ticker}" style="min-height: 380px;"></div>
                    <div id="volume-chart-${ticker}" style="min-height: 150px;"></div>
                </div>
                
                <!-- Analysis Panel -->
                <div class="analysis-container">
                    <div class="analysis-header">
                        <h3>
                            <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24" style="color: var(--accent-blue);">
                                <path d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                            </svg>
                            Market Data Analysis Report
                        </h3>
                        <span id="analysis-trend-badge-${ticker}" class="tag-pill tag-neutral">Analyzing...</span>
                    </div>
                    
                    <div class="analysis-grid">
                        <!-- Quantitative Stats Table -->
                        <div class="analysis-card">
                            <div class="analysis-card-title">Quantitative Statistics</div>
                            <div class="analysis-metric-row">
                                <span class="analysis-metric-label">Total Sample Days</span>
                                <span class="analysis-metric-value" id="stat-days-${ticker}">-</span>
                            </div>
                            <div class="analysis-metric-row">
                                <span class="analysis-metric-label">Average Daily Returns</span>
                                <span class="analysis-metric-value" id="stat-avg-returns-${ticker}">-</span>
                            </div>
                            <div class="analysis-metric-row">
                                <span class="analysis-metric-label">Daily Price Volatility (Std Dev)</span>
                                <span class="analysis-metric-value" id="stat-volatility-${ticker}">-</span>
                            </div>
                            <div class="analysis-metric-row">
                                <span class="analysis-metric-label">Single-Day Maximum Gain</span>
                                <span class="analysis-metric-value text-green" id="stat-max-gain-${ticker}">-</span>
                            </div>
                            <div class="analysis-metric-row">
                                <span class="analysis-metric-label">Single-Day Maximum Loss</span>
                                <span class="analysis-metric-value text-red" id="stat-max-loss-${ticker}">-</span>
                            </div>
                            <div class="analysis-metric-row">
                                <span class="analysis-metric-label">Trading Volume Mean</span>
                                <span class="analysis-metric-value" id="stat-vol-mean-${ticker}">-</span>
                            </div>
                        </div>
                        
                        <!-- Historical Return Performance Table -->
                        <div class="analysis-card">
                            <div class="analysis-card-title">
                                <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24" style="color: var(--accent-green);">
                                    <path d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path>
                                </svg>
                                Historical Returns
                            </div>
                            <div class="analysis-metric-row">
                                <span class="analysis-metric-label">6 Months Return</span>
                                <span class="analysis-metric-value" id="perf-6m-${ticker}">-</span>
                            </div>
                            <div class="analysis-metric-row">
                                <span class="analysis-metric-label">3 Months Return</span>
                                <span class="analysis-metric-value" id="perf-3m-${ticker}">-</span>
                            </div>
                            <div class="analysis-metric-row">
                                <span class="analysis-metric-label">1 Month Return</span>
                                <span class="analysis-metric-value" id="perf-1m-${ticker}">-</span>
                            </div>
                            <div class="analysis-metric-row">
                                <span class="analysis-metric-label">2 Weeks Return</span>
                                <span class="analysis-metric-value" id="perf-2w-${ticker}">-</span>
                            </div>
                            <div class="analysis-metric-row">
                                <span class="analysis-metric-label">1 Week Return</span>
                                <span class="analysis-metric-value" id="perf-1w-${ticker}">-</span>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Formal Analysis Text Writeup (Full Width) -->
                    <div class="analysis-card writeup" id="analysis-text-writeup-${ticker}" style="margin-top: 1.5rem;"></div>
                </div>
            `;
            wrapper.appendChild(content);
        }

        function setupSidebarListeners() {
            const radioButtons = document.querySelectorAll('input[name="timeframe"]');
            radioButtons.forEach(btn => {
                btn.addEventListener("change", (e) => {
                    document.querySelectorAll(".radio-label").forEach(lbl => {
                        lbl.classList.remove("active");
                    });
                    document.getElementById(`lbl-${e.target.value.toLowerCase()}`).classList.add("active");
                    activeRangeCode = e.target.value;
                    updateViewport(activeRangeCode);
                });
            });
            
            document.getElementById("lbl-5y").classList.add("active");
        }

        // Switch Active Tab layout
        function switchTab(ticker) {
            // Hide previous tab content
            const prevContent = document.getElementById(`content-${currentTicker}`);
            if (prevContent) prevContent.style.display = "none";
            
            const prevBtn = document.getElementById(`tab-btn-${currentTicker}`);
            if (prevBtn) prevBtn.classList.remove("active");
            
            // Set active ticker
            currentTicker = ticker;
            
            // Show new tab content
            const activeContent = document.getElementById(`content-${currentTicker}`);
            if (activeContent) {
                activeContent.style.display = "flex";
                activeContent.style.flexDirection = "column";
                activeContent.style.gap = "2rem";
            }
            
            const activeBtn = document.getElementById(`tab-btn-${currentTicker}`);
            if (activeBtn) activeBtn.classList.add("active");
            
            // Lazy-load charts upon first viewing of tab
            if (!initializedStocks.has(currentTicker)) {
                initializedStocks.add(currentTicker);
                updateViewport(activeRangeCode); // Calculates viewport data and generates charts
            } else {
                // If already initialized, update viewport to sync with sidebar settings
                updateViewport(activeRangeCode);
                // Call ApexCharts handlers to recalculate container widths and redraw
                setTimeout(() => {
                    if (priceCharts[currentTicker]) priceCharts[currentTicker].windowResizeHandler();
                    if (volumeCharts[currentTicker]) volumeCharts[currentTicker].windowResizeHandler();
                }, 50);
            }
        }

        // Technical Indicator calculations
        function calculateSMA(data, period) {
            let sma = [];
            for (let i = 0; i < data.length; i++) {
                if (i < period - 1) {
                    sma.push({ x: data[i].timestamp, y: null });
                } else {
                    let sum = 0;
                    for (let j = 0; j < period; j++) {
                        sum += data[i - j].close;
                    }
                    sma.push({ x: data[i].timestamp, y: parseFloat((sum / period).toFixed(2)) });
                }
            }
            return sma;
        }

        // Helper: get UTC ISO week key or UTC Month key for grouping
        function getGroupKey(dateObj, type) {
            if (type === 'weekly') {
                const target = new Date(dateObj.getTime());
                const dayNr = (target.getUTCDay() + 6) % 7;
                target.setUTCDate(target.getUTCDate() - dayNr + 3);
                const firstThursday = target.getTime();
                target.setUTCMonth(0, 1);
                if (target.getUTCDay() !== 4) {
                    target.setUTCMonth(0, 1 + ((4 - target.getUTCDay()) + 7) % 7);
                }
                const weekNum = 1 + Math.ceil((firstThursday - target.getTime()) / 604800000);
                return `${target.getUTCFullYear()}-W${weekNum}`;
            } else if (type === 'monthly') {
                return `${dateObj.getUTCFullYear()}-${dateObj.getUTCMonth()}`;
            }
            return null;
        }

        // Helper: roll up daily array into a single candle/bar
        function rollupGroup(group) {
            group.sort((a, b) => a.timestamp - b.timestamp);
            const first = group[0];
            const last = group[group.length - 1];
            
            const highs = group.map(d => d.high).filter(v => v !== null);
            const lows = group.map(d => d.low).filter(v => v !== null);
            const volumes = group.map(d => d.volume).filter(v => v !== null);
            
            return {
                date: last.date,
                timestamp: last.timestamp,
                open: first.open,
                high: highs.length > 0 ? Math.max(...highs) : null,
                low: lows.length > 0 ? Math.min(...lows) : null,
                close: last.close,
                volume: volumes.reduce((sum, v) => sum + v, 0),
                price: last.price
            };
        }

        // Aggregate daily OHLCV data
        function aggregateData(dailyData, periodType) {
            if (periodType === 'daily') return dailyData;
            
            let aggregated = [];
            let tempGroup = [];
            let currentKey = null;
            
            for (let i = 0; i < dailyData.length; i++) {
                const item = dailyData[i];
                const dateObj = new Date(item.timestamp);
                const key = getGroupKey(dateObj, periodType);
                
                if (currentKey === null) {
                    currentKey = key;
                }
                
                if (key !== currentKey) {
                    if (tempGroup.length > 0) {
                        aggregated.push(rollupGroup(tempGroup));
                    }
                    tempGroup = [];
                    currentKey = key;
                }
                tempGroup.push(item);
            }
            
            if (tempGroup.length > 0) {
                aggregated.push(rollupGroup(tempGroup));
            }
            
            return aggregated;
        }

        // Helper: calculate price performance return over a calendar interval (in days)
        function getPerformanceChange(dataset, latestItem, daysBack) {
            const targetTime = latestItem.timestamp - daysBack * 24 * 60 * 60 * 1000;
            let closestItem = dataset[0];
            let minDiff = Math.abs(dataset[0].timestamp - targetTime);
            
            for (let i = 1; i < dataset.length; i++) {
                const diff = Math.abs(dataset[i].timestamp - targetTime);
                if (diff < minDiff && dataset[i].timestamp <= latestItem.timestamp) {
                    minDiff = diff;
                    closestItem = dataset[i];
                }
            }
            
            if (!closestItem || closestItem.timestamp >= latestItem.timestamp) return null;
            
            const change = latestItem.close - closestItem.close;
            const pct = (change / closestItem.close) * 100;
            return {
                pct: pct,
                priceChange: change,
                oldPrice: closestItem.close,
                date: closestItem.date
            };
        }

        // Filter and update variables based on timeframe selection
        function updateViewport(rangeCode) {
            activeRangeCode = rangeCode;
            const ticker = currentTicker;
            const dataset = datasets[ticker];
            
            if (!dataset || dataset.length === 0) return;
            
            const latestTimestamp = dataset[dataset.length - 1].timestamp;
            let cutOffTimestamp = 0;
            
            const oneMonthMs = 30 * 24 * 60 * 60 * 1000;
            const oneYearMs = 365 * 24 * 60 * 60 * 1000;
            
            if (rangeCode === "1M") cutOffTimestamp = latestTimestamp - oneMonthMs;
            else if (rangeCode === "6M") cutOffTimestamp = latestTimestamp - 6 * oneMonthMs;
            else if (rangeCode === "1Y") cutOffTimestamp = latestTimestamp - oneYearMs;
            else if (rangeCode === "3Y") cutOffTimestamp = latestTimestamp - 3 * oneYearMs;
            else cutOffTimestamp = 0; // 5Y / Full data
            
            // Generalize data (weekly) for large periods of time so bars show up clearly for every setting
            let aggregationType = "daily";
            if (rangeCode === "3Y" || rangeCode === "5Y") {
                aggregationType = "weekly";
            }
            
            // Feed the ENTIRE dataset (all 5 years) to the chart series to allow zooming out
            const activeData = aggregateData(dataset, aggregationType);
            activeDataMaps[ticker] = activeData;
            
            // Downsample SMA pre-calculations by matching the weekly/daily timestamps of activeData
            const sma50Full = sma50FullMaps[ticker];
            const sma200Full = sma200FullMaps[ticker];
            
            activeSma50Maps[ticker] = activeData.map(item => {
                const match = sma50Full.find(s => s.x === item.timestamp);
                return { x: item.timestamp, y: match ? match.y : null };
            });
            activeSma200Maps[ticker] = activeData.map(item => {
                const match = sma200Full.find(s => s.x === item.timestamp);
                return { x: item.timestamp, y: match ? match.y : null };
            });

            // Calculate KPIs and Narrative Report based on the FILTERED range
            const filteredData = dataset.filter(d => d.timestamp >= cutOffTimestamp);
            const activeFilteredData = aggregateData(filteredData, aggregationType);
            
            activeZoomStart = cutOffTimestamp;
            activeZoomEnd = latestTimestamp;
            activeFilteredDataMaps[ticker] = activeFilteredData;
            
            calculateKPIs(ticker, activeFilteredData);
            generateAnalysisReport(ticker, activeFilteredData);
            
            // Render the charts (which will draw the full series and zoom to the range)
            renderCharts(ticker, cutOffTimestamp, latestTimestamp);
            resetHUD(ticker);
        }

        // Calculate KPI summaries
        function calculateKPIs(ticker, activeData) {
            const dataset = datasets[ticker];
            const latest = activeData[activeData.length - 1];
            const prev = activeData[activeData.length - 2] || latest;
            
            const change = latest.close - prev.close;
            const pct = (change / prev.close) * 100;
            
            document.getElementById(`kpi-latest-${ticker}`).innerText = `$${latest.close.toFixed(2)}`;
            const changeEl = document.getElementById(`kpi-change-${ticker}`);
            changeEl.innerText = `${change >= 0 ? '+' : ''}${change.toFixed(2)} (${change >= 0 ? '+' : ''}${pct.toFixed(2)}%)`;
            changeEl.className = `kpi-sub ${change >= 0 ? 'gain' : 'loss'}`;
            
            // Period Stats
            const closes = activeData.map(d => d.close);
            const sumCloses = closes.reduce((a, b) => a + b, 0);
            const avg = sumCloses / closes.length;
            document.getElementById(`kpi-avg-${ticker}`).innerText = `$${avg.toFixed(2)}`;
            
            let maxObj = activeData[0];
            let minObj = activeData[0];
            
            activeData.forEach(d => {
                if (d.close > maxObj.close) maxObj = d;
                if (d.close < minObj.close) minObj = d;
            });
            
            document.getElementById(`kpi-high-${ticker}`).innerText = `$${maxObj.close.toFixed(2)}`;
            document.getElementById(`kpi-high-date-${ticker}`).innerText = maxObj.date;
            
            document.getElementById(`kpi-low-${ticker}`).innerText = `$${minObj.close.toFixed(2)}`;
            document.getElementById(`kpi-low-date-${ticker}`).innerText = minObj.date;
        }

        // Dynamic HUD updates (triggers on hover or details reset)
        function updateHUD(ticker, item) {
            if (!item) return;
            const dataset = datasets[ticker];
            document.getElementById(`hud-last-${ticker}`).innerText = `$${item.close.toFixed(2)}`;
            document.getElementById(`hud-volume-${ticker}`).innerText = item.volume.toLocaleString();
            document.getElementById(`hud-open-${ticker}`).innerText = `$${item.open.toFixed(2)}`;
            document.getElementById(`hud-close-${ticker}`).innerText = `$${item.close.toFixed(2)}`;
            document.getElementById(`hud-high-${ticker}`).innerText = `$${item.high.toFixed(2)}`;
            document.getElementById(`hud-low-${ticker}`).innerText = `$${item.low.toFixed(2)}`;
            document.getElementById(`hud-date-${ticker}`).innerText = item.date;
            
            // Calculate change from previous day
            const idx = dataset.findIndex(d => d.timestamp === item.timestamp);
            if (idx > 0) {
                const prev = dataset[idx - 1];
                const change = item.close - prev.close;
                const pct = (change / prev.close) * 100;
                const changeEl = document.getElementById(`hud-change-${ticker}`);
                changeEl.innerText = `${change >= 0 ? '▲' : '▼'} ${Math.abs(change).toFixed(2)} (${change >= 0 ? '+' : ''}${pct.toFixed(2)}%)`;
                changeEl.className = `hud-value ${change >= 0 ? 'gain' : 'loss'}`;
            } else {
                document.getElementById(`hud-change-${ticker}`).innerText = "N/A";
                document.getElementById(`hud-change-${ticker}`).className = "hud-value";
            }
        }

        function resetHUD(ticker) {
            const activeData = activeDataMaps[ticker];
            if (activeData && activeData.length > 0) {
                updateHUD(ticker, activeData[activeData.length - 1]);
            }
        }

        // Renders / Updates Stock Charts
        function renderCharts(ticker, zoomStart, zoomEnd) {
            const activeData = activeDataMaps[ticker];
            const activeSma50 = activeSma50Maps[ticker];
            const activeSma200 = activeSma200Maps[ticker];
            
            const ohlcSeries = activeData.map(d => ({ x: d.timestamp, y: [d.open, d.high, d.low, d.close] }));
            const lineSeries = activeData.map(d => ({ x: d.timestamp, y: d.close }));
            const volumeSeries = activeData.map(d => ({ x: d.timestamp, y: d.volume }));
            
            // Period Avg calculation for reference baseline
            const closes = activeData.map(d => d.close);
            const sumCloses = closes.reduce((a, b) => a + b, 0);
            const avgClose = sumCloses / closes.length;
            
            // Build series array and style lists dynamically to assign fixed properties
            let primarySeries = [];
            let chartColors = [];
            let chartWidths = [];
            let chartDashes = [];
            let chartOpacities = [];
            let chartFillTypes = [];
            
            if (activeChartType === "candlestick") {
                primarySeries.push({
                    name: 'Price (OHLC)',
                    type: 'candlestick',
                    data: ohlcSeries
                });
                chartColors.push('#3b82f6');
                chartWidths.push(1.5);
                chartDashes.push(0);
                chartOpacities.push(1.0);
                chartFillTypes.push('solid');
            } else {
                primarySeries.push({
                    name: 'Close Price',
                    type: 'area',
                    data: lineSeries
                });
                chartColors.push('#3b82f6');
                chartWidths.push(3.0);
                chartDashes.push(0);
                chartOpacities.push(1.0);
                chartFillTypes.push('gradient');
            }
            
            if (document.getElementById("chk-sma50").checked) {
                primarySeries.push({
                    name: '50-day SMA',
                    type: 'line',
                    data: activeSma50
                });
                chartColors.push('#ec4899'); // Vibrant pink
                chartWidths.push(3.0); // Reduced boldness to match price line
                chartDashes.push(0);
                chartOpacities.push(0.5); // Lower opacity for transparency
                chartFillTypes.push('solid');
            }
            
            if (document.getElementById("chk-sma200").checked) {
                primarySeries.push({
                    name: '200-day SMA',
                    type: 'line',
                    data: activeSma200
                });
                chartColors.push('#f97316'); // Vibrant orange
                chartWidths.push(3.0); // Reduced boldness to match price line
                chartDashes.push(0);
                chartOpacities.push(0.5); // Lower opacity for transparency
                chartFillTypes.push('solid');
            }
            
            const optionsPrice = {
                series: primarySeries,
                chart: {
                    id: `candles-${ticker}`,
                    group: `stock-group-${ticker}`, // Sync scrolling/zooming with volume chart
                    height: 380,
                    type: 'line',
                    toolbar: {
                        show: true,
                        autoSelected: 'zoom',
                        tools: {
                            download: true,
                            selection: false,
                            zoom: true,
                            zoomin: true,
                            zoomout: true,
                            pan: true,
                            reset: true
                        }
                    },
                    zoom: {
                        enabled: true,
                        type: 'x',
                        autoScaleYaxis: true
                    },
                    background: 'transparent',
                    foreColor: currentTheme === 'dark' ? '#9ca3af' : '#475569',
                    events: {
                        mounted: function(chartContext) {
                            const start = zoomStart || activeData[0].timestamp;
                            const end = zoomEnd || activeData[activeData.length - 1].timestamp;
                            chartContext.zoomX(start, end);
                        },
                        mouseMove: function(event, chartContext, config) {
                            const dataPointIndex = config.dataPointIndex;
                            if (dataPointIndex !== -1 && dataPointIndex !== undefined) {
                                updateHUD(ticker, activeData[dataPointIndex]);
                            }
                        },
                        mouseLeave: function() {
                            resetHUD(ticker);
                        }
                    }
                },
                theme: { mode: currentTheme },
                dataLabels: { enabled: false },
                colors: chartColors,
                stroke: {
                    width: chartWidths,
                    curve: 'smooth',
                    dashArray: chartDashes
                },
                plotOptions: {
                    candlestick: {
                        colors: { upward: '#10b981', downward: '#ef4444' },
                        wick: { useFillColor: true }
                    }
                },
                fill: {
                    type: chartFillTypes,
                    opacity: chartOpacities,
                    gradient: {
                        shade: currentTheme,
                        type: 'vertical',
                        shadeIntensity: 0.5,
                        inverseColors: false,
                        opacityFrom: 0.65,
                        opacityTo: 0.0,
                        stops: [0, 100]
                    }
                },
                // Dash Baseline (Screenshot style average reference line)
                annotations: {
                    yaxis: [{
                        y: avgClose,
                        borderColor: 'rgba(245, 158, 11, 0.45)',
                        strokeDashArray: 4,
                        label: {
                            borderColor: 'rgba(245, 158, 11, 0.7)',
                            style: {
                                color: '#fff',
                                background: '#f59e0b',
                                fontSize: '10px'
                            },
                            text: 'Baseline Avg'
                        }
                    }]
                },
                xaxis: {
                    type: 'datetime',
                    axisBorder: { show: false },
                    axisTicks: { color: 'rgba(255,255,255,0.08)' }
                },
                yaxis: {
                    labels: {
                        formatter: (val) => '$' + val.toFixed(2)
                    }
                },
                grid: {
                    borderColor: currentTheme === 'dark' ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)',
                    strokeDashArray: 3
                },
                tooltip: {
                    shared: true,
                    custom: function({ series, seriesIndex, dataPointIndex, w }) {
                        const o = w.globals.seriesCandleO[seriesIndex][dataPointIndex];
                        const h = w.globals.seriesCandleH[seriesIndex][dataPointIndex];
                        const l = w.globals.seriesCandleL[seriesIndex][dataPointIndex];
                        const c = w.globals.seriesCandleC[seriesIndex][dataPointIndex];
                        
                        const dateStr = new Date(w.globals.seriesX[seriesIndex][dataPointIndex]).toLocaleDateString();
                        
                        if (o !== undefined) {
                            return `<div style="padding: 10px; background: #111827; border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; color: #fff;">
                                <div style="font-weight:700; margin-bottom: 5px; color: #60a5fa">${dateStr}</div>
                                <div style="font-size: 0.8rem">Open: <span style="font-family:monospace; font-weight:600">$${o.toFixed(2)}</span></div>
                                <div style="font-size: 0.8rem">High: <span style="font-family:monospace; font-weight:600; color: #10b981">$${h.toFixed(2)}</span></div>
                                <div style="font-size: 0.8rem">Low: <span style="font-family:monospace; font-weight:600; color: #ef4444">$${l.toFixed(2)}</span></div>
                                <div style="font-size: 0.8rem">Close: <span style="font-family:monospace; font-weight:600">$${c.toFixed(2)}</span></div>
                            </div>`;
                        }
                        
                        let val = series[seriesIndex][dataPointIndex];
                        return `<div style="padding: 8px 12px; background: #111827; border: 1px solid rgba(255,255,255,0.1); border-radius: 6px; color: #fff;">
                            <span style="font-weight: 500">${w.config.series[seriesIndex].name}: </span>
                            <span style="font-family:monospace; font-weight: 700">$${val.toFixed(2)}</span>
                        </div>`;
                    }
                }
            };
            
            const optionsVolume = {
                series: [{
                    name: 'Volume',
                    data: volumeSeries
                }],
                chart: {
                    id: `volume-${ticker}`,
                    group: `stock-group-${ticker}`, // Sync scrolling/zooming with price chart
                    height: 150,
                    type: 'bar',
                    toolbar: { show: false },
                    background: 'transparent',
                    foreColor: currentTheme === 'dark' ? '#9ca3af' : '#475569'
                },
                theme: { mode: currentTheme },
                dataLabels: { enabled: false },
                colors: [
                    function({ value, seriesIndex, dataPointIndex }) {
                        const item = activeData[dataPointIndex];
                        if (item) {
                            return item.close >= item.open ? '#22c55e' : '#ef4444';
                        }
                        return '#3b82f6';
                    }
                ],
                fill: {
                    opacity: 1.0
                },
                plotOptions: {
                    bar: {
                        columnWidth: '90%'
                    }
                },
                grid: {
                    borderColor: currentTheme === 'dark' ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)',
                    strokeDashArray: 3
                },
                xaxis: {
                    type: 'datetime',
                    axisBorder: { show: false }
                },
                yaxis: {
                    labels: {
                        formatter: (val) => {
                            if (val >= 1e6) return (val / 1e6).toFixed(0) + 'M';
                            if (val >= 1e3) return (val / 1e3).toFixed(0) + 'K';
                            return val;
                        }
                    }
                }
            };

            const chartPriceEl = document.querySelector(`#price-chart-${ticker}`);
            const chartVolEl = document.querySelector(`#volume-chart-${ticker}`);
            
            if (priceCharts[ticker]) {
                priceCharts[ticker].destroy();
            }
            if (volumeCharts[ticker]) {
                volumeCharts[ticker].destroy();
            }

            priceCharts[ticker] = new ApexCharts(chartPriceEl, optionsPrice);
            priceCharts[ticker].render();

            volumeCharts[ticker] = new ApexCharts(chartVolEl, optionsVolume);
            volumeCharts[ticker].render();


        }

        // Style controls switches
        function setChartStyle(style) {
            if (activeChartType === style) return;
            activeChartType = style;
            
            document.querySelectorAll(".btn-toggle").forEach(btn => {
                if (btn.id.startsWith("btn-theme-")) return;
                btn.classList.remove("active");
            });
            if (style === "line") {
                document.getElementById("btn-chart-line").classList.add("active");
            } else {
                document.getElementById("btn-chart-candle").classList.add("active");
            }
            
            // Re-render only the currently active tab's charts
            renderCharts(currentTicker);
        }

        function onOverlayChange() {
            renderCharts(currentTicker);
            generateAnalysisReport(currentTicker, activeFilteredDataMaps[currentTicker]);
        }

        // Live/Classic theme controls
        function setThemeStyle(themeName) {
            if (currentTheme === themeName) return;
            currentTheme = themeName;
            
            document.querySelectorAll("[id^='btn-theme-']").forEach(btn => btn.classList.remove("active"));
            document.getElementById(`btn-theme-${themeName}`).classList.add("active");
            
            if (themeName === 'light') {
                document.body.classList.add('theme-light');
            } else {
                document.body.classList.remove('theme-light');
            }
            
            // Re-render the charts on the active tab
            renderCharts(currentTicker);
        }

        // Quant Stats & Dynamic Summary Report Generation
        function generateAnalysisReport(ticker, activeData) {
            const activeSma50 = activeSma50Maps[ticker];
            const activeSma200 = activeSma200Maps[ticker];
            
            const n = activeData.length;
            if (n === 0) return;
            
            // Calculate daily returns
            let returns = [];
            let maxGain = 0;
            let maxGainDate = "";
            let maxLoss = 0;
            let maxLossDate = "";
            
            for (let i = 1; i < n; i++) {
                const ret = (activeData[i].close - activeData[i-1].close) / activeData[i-1].close;
                returns.push(ret);
                
                if (ret > maxGain) {
                    maxGain = ret;
                    maxGainDate = activeData[i].date;
                }
                if (ret < maxLoss) {
                    maxLoss = ret;
                    maxLossDate = activeData[i].date;
                }
            }
            
            const avgReturn = returns.length > 0 ? (returns.reduce((a, b) => a + b, 0) / returns.length) : 0;
            
            // Volatility (std dev)
            const variance = returns.length > 0 ? (returns.map(x => Math.pow(x - avgReturn, 2)).reduce((a, b) => a + b, 0) / returns.length) : 0;
            const volatility = Math.sqrt(variance);
            
            // Avg Volume
            const vols = activeData.map(d => d.volume);
            const avgVol = vols.reduce((a, b) => a + b, 0) / vols.length;
            
            // Fill table fields
            document.getElementById(`stat-days-${ticker}`).innerText = n;
            document.getElementById(`stat-avg-returns-${ticker}`).innerText = `${avgReturn >= 0 ? '+' : ''}${(avgReturn * 100).toFixed(4)}% / day`;
            document.getElementById(`stat-volatility-${ticker}`).innerText = `${(volatility * 100).toFixed(4)}%`;
            document.getElementById(`stat-max-gain-${ticker}`).innerText = `+${(maxGain * 100).toFixed(2)}% (on ${maxGainDate})`;
            document.getElementById(`stat-max-loss-${ticker}`).innerText = `${(maxLoss * 100).toFixed(2)}% (on ${maxLossDate})`;
            document.getElementById(`stat-vol-mean-${ticker}`).innerText = avgVol.toLocaleString(undefined, {maximumFractionDigits: 0}) + " shares";

            // Calculate and display historical interval performance return percentages
            const fullDataset = datasets[ticker];
            if (fullDataset && fullDataset.length > 0) {
                const latestDay = fullDataset[fullDataset.length - 1];
                const intervals = [
                    { id: "6m", days: 182 },
                    { id: "3m", days: 91 },
                    { id: "1m", days: 30 },
                    { id: "2w", days: 14 },
                    { id: "1w", days: 7 }
                ];
                
                intervals.forEach(interval => {
                    const changeObj = getPerformanceChange(fullDataset, latestDay, interval.days);
                    const cell = document.getElementById(`perf-${interval.id}-${ticker}`);
                    if (cell) {
                        if (changeObj) {
                            const val = changeObj.pct;
                            cell.innerText = `${val >= 0 ? '+' : ''}${val.toFixed(2)}%`;
                            cell.className = `analysis-metric-value ${val >= 0 ? 'text-green' : 'text-red'}`;
                            cell.title = `Compared to $${changeObj.oldPrice.toFixed(2)} on ${changeObj.date}`;
                        } else {
                            cell.innerText = "N/A";
                            cell.className = "analysis-metric-value";
                        }
                    }
                });
            }

            // Determine Trend and writeup analysis
            const latest = activeData[n - 1];
            const sma50Obj = activeSma50[activeSma50.length - 1];
            const sma200Obj = activeSma200[activeSma200.length - 1];
            
            let trend = "Neutral";
            let trendClass = "tag-neutral";
            let smaText = "";
            
            if (sma50Obj && sma50Obj.y && sma200Obj && sma200Obj.y) {
                if (latest.close > sma50Obj.y && sma50Obj.y > sma200Obj.y) {
                    trend = "Bullish Outlook";
                    trendClass = "tag-bullish";
                    smaText = `Price ($${latest.close.toFixed(2)}) resides above the 50-day SMA ($${sma50Obj.y.toFixed(2)}) and the 200-day SMA ($${sma200Obj.y.toFixed(2)}). The short-term and long-term averages showcase a bullish structural alignment.`;
                } else if (latest.close < sma50Obj.y && sma50Obj.y < sma200Obj.y) {
                    trend = "Bearish Trend";
                    trendClass = "tag-bearish";
                    smaText = `Price ($${latest.close.toFixed(2)}) trades below the 50-day SMA ($${sma50Obj.y.toFixed(2)}) and 200-day SMA ($${sma200Obj.y.toFixed(2)}), highlighting a strong downward structural correction.`;
                } else {
                    trend = "Consolidating Range";
                    trendClass = "tag-neutral";
                    smaText = `Price is consolidating between the 50-day SMA ($${sma50Obj.y.toFixed(2)}) and the 200-day SMA ($${sma200Obj.y.toFixed(2)}). Moving averages signal short-term range-bound volatility.`;
                }
            } else {
                smaText = "Moving Average crossovers cannot be fully evaluated with current constraints (requires more history).";
            }
            
            document.getElementById(`analysis-trend-badge-${ticker}`).innerText = trend;
            document.getElementById(`analysis-trend-badge-${ticker}`).className = `tag-pill ${trendClass}`;
            
            // Build formal summary text writeup
            const avgValStr = (activeData.reduce((a,b)=>a+b.close,0)/n).toFixed(2);
            const minValStr = activeData.reduce((a,b)=>a.close<b.close?a:b).close.toFixed(2);
            const maxValStr = activeData.reduce((a,b)=>a.close>b.close?a:b).close.toFixed(2);

            const writeupHTML = `
                <p><strong>Executive Summary:</strong> Over the selected timeframe, ${ticker} has traded for a total of <strong>${n} sessions</strong>. The historical close price registers an average of <strong>$${avgValStr}</strong>, bounding inside a dynamic window between the period floor of <strong>$${minValStr}</strong> and the period ceiling of <strong>$${maxValStr}</strong>.</p>
                
                <p><strong>Moving Averages & Crossovers:</strong> ${smaText}</p>
                
                <p><strong>Risk & Volatility Parameters:</strong> The daily price volatility coefficient measures at <strong>${(volatility*100).toFixed(3)}%</strong>, indicating typical equity risk bounds. On a performance basis, the most extreme positive deviation was <strong>+${(maxGain*100).toFixed(2)}%</strong> on <strong>${maxGainDate}</strong>, while the maximum downward draw occurred on <strong>${maxLossDate}</strong> at <strong>${(maxLoss*100).toFixed(2)}%</strong>.</p>
            `;
            document.getElementById(`analysis-text-writeup-${ticker}`).innerHTML = writeupHTML;
        }

        // Client-side CSV generation and blob downloader
        function downloadCSV() {
            const ticker = currentTicker;
            const activeData = activeDataMaps[ticker];
            
            if (!activeData || activeData.length === 0) return;
            
            let csv = "Date,Open,High,Low,Close,Volume,Price\\n";
            activeData.forEach(d => {
                csv += `${d.date},${d.open},${d.high},${d.low},${d.close},${d.volume},${d.price}\\n`;
            });
            
            const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
            const url = URL.createObjectURL(blob);
            const link = document.createElement("a");
            link.setAttribute("href", url);
            link.setAttribute("download", `${ticker}_stock_dataset.csv`);
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    </script>
```
"""
    # Safe replacement of placeholders
    qmd_content = qmd_template.replace("{default_ticker}", default_ticker).replace("{data_js}", data_js)

    os.makedirs(os.path.dirname(qmd_output_path), exist_ok=True)
    with open(qmd_output_path, "w") as f:
        f.write(qmd_content)
    print(f"Generated tabbed dashboard entrypoint index.qmd at: {qmd_output_path}")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    downloads_dir = os.path.join(script_dir, "downloads")
    
    datasets_dict = {}
    
    # Dynamically scan and load all JSON datasets inside downloads/
    for filename in os.listdir(downloads_dir):
        if filename.endswith("_nasdaq_dataset.json"):
            ticker = filename.split("_")[0].upper()
            file_path = os.path.join(downloads_dir, filename)
            with open(file_path, "w" if False else "r") as f:
                datasets_dict[ticker] = json.load(f)
                
    output_qmd = os.path.join(script_dir, "index.qmd")
    generate_qmd(datasets_dict, output_qmd)
