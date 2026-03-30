"""
================================================
  Streamlit Frontend — Stock Return Predictor
  v3.0 — Dashboard + History + MySQL connected
================================================
"""

import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os
import yfinance as yf

FASTAPI_URL = os.getenv("FASTAPI_URL", "http://127.0.0.1:8000")

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Stock ROCE Predictor",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=IBM+Plex+Mono:wght@400;500;600&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}
.stApp { background: #080c14; color: #c8d6e8; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #0d1421 !important;
    border-right: 1px solid #1a2535;
}
section[data-testid="stSidebar"] .stMarkdown p {
    color: #6b82a0; font-family: 'IBM Plex Mono', monospace; font-size: 0.7rem;
    text-transform: uppercase; letter-spacing: 2px;
}

/* Hero */
.hero-wrap {
    background: linear-gradient(135deg, #0d1421 0%, #0a1628 40%, #0d1421 100%);
    border: 1px solid #1e3a5f40;
    border-radius: 16px; padding: 2.2rem 2.5rem; margin-bottom: 1.5rem;
    position: relative; overflow: hidden;
}
.hero-wrap::before {
    content: ''; position: absolute; top: -50%; right: -10%;
    width: 400px; height: 400px; border-radius: 50%;
    background: radial-gradient(circle, #1a4a8a15 0%, transparent 70%);
}
.hero-title {
    font-family: 'DM Serif Display', serif; font-size: 2.6rem;
    color: #e8f4ff; margin: 0; line-height: 1.1;
}
.hero-title span { color: #3b9eff; font-style: italic; }
.hero-sub {
    font-family: 'IBM Plex Mono', monospace; font-size: 0.65rem;
    color: #3b6ea0; letter-spacing: 3px; text-transform: uppercase;
    margin-top: 0.6rem;
}

/* Metric cards */
.metric-row { display: flex; gap: 1rem; margin-bottom: 1.5rem; flex-wrap: wrap; }
.metric-card {
    flex: 1; min-width: 140px; background: #0d1421;
    border: 1px solid #1a2c42; border-radius: 12px;
    padding: 1.2rem 1.4rem;
}
.metric-card .m-label {
    font-family: 'IBM Plex Mono', monospace; font-size: 0.6rem;
    color: #4a6a8a; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 0.4rem;
}
.metric-card .m-value {
    font-family: 'DM Serif Display', serif; font-size: 2rem; color: #e8f4ff; line-height: 1;
}
.metric-card .m-sub { font-size: 0.72rem; color: #4a6a8a; margin-top: 0.3rem; }

/* Section label */
.sec-label {
    font-family: 'IBM Plex Mono', monospace; font-size: 0.6rem;
    color: #3b6ea0; text-transform: uppercase; letter-spacing: 3px;
    padding-bottom: 0.5rem; border-bottom: 1px solid #1a2535; margin: 1.5rem 0 1rem;
}

/* Result card */
.result-card {
    border-radius: 14px; padding: 2rem; text-align: center; margin: 1rem 0;
}
.result-label {
    font-family: 'IBM Plex Mono', monospace; font-size: 0.6rem;
    color: #4a6a8a; text-transform: uppercase; letter-spacing: 2px;
}
.result-value {
    font-family: 'DM Serif Display', serif; font-size: 4.5rem; line-height: 1.05;
}
.result-badge {
    display: inline-block; padding: 0.35rem 1.3rem; border-radius: 20px;
    font-family: 'IBM Plex Mono', monospace; font-size: 0.75rem; margin-top: 0.8rem;
}

/* Input labels */
div[data-testid="stNumberInput"] label,
div[data-testid="stTextInput"] label {
    color: #5a7a9a !important; font-size: 0.7rem !important;
    font-family: 'IBM Plex Mono', monospace !important;
    text-transform: uppercase !important; letter-spacing: 1px !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #1a4a8a, #2563eb) !important;
    color: #e8f4ff !important; border: none !important;
    border-radius: 8px !important; font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important; letter-spacing: 0.5px !important;
    padding: 0.65rem 1.8rem !important; transition: all 0.2s !important;
}
.stButton > button:hover { opacity: 0.88 !important; transform: translateY(-1px) !important; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] { background: #0d1421; border-radius: 10px; padding: 4px; }
.stTabs [data-baseweb="tab"] {
    color: #4a6a8a !important; font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.72rem !important; border-radius: 8px !important;
}
.stTabs [aria-selected="true"] {
    background: #1a2c42 !important; color: #3b9eff !important;
}

/* Table */
div[data-testid="stDataFrame"] { background: #0d1421; border-radius: 10px; border: 1px solid #1a2535; }

/* Status badges */
.badge-green  { background: #052012; color: #4ade80; padding: 3px 10px; border-radius: 12px; font-size:0.72rem; font-family: 'IBM Plex Mono', monospace; }
.badge-blue   { background: #031520; color: #38bdf8; padding: 3px 10px; border-radius: 12px; font-size:0.72rem; font-family: 'IBM Plex Mono', monospace; }
.badge-yellow { background: #1c1200; color: #fbbf24; padding: 3px 10px; border-radius: 12px; font-size:0.72rem; font-family: 'IBM Plex Mono', monospace; }
.badge-red    { background: #1a0008; color: #f43f5e; padding: 3px 10px; border-radius: 12px; font-size:0.72rem; font-family: 'IBM Plex Mono', monospace; }

.stAlert { border-radius: 10px !important; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ System Status")
    try:
        r = requests.get(f"{FASTAPI_URL}/health", timeout=3)
        data = r.json()
        model_ok = data.get("model_ready", False)
        db_ok    = data.get("db_ready", False)
        
        # Status Badges
        if model_ok:
            st.success("✅ FastAPI Online")
        else:
            st.warning("⚠️ Model Not Loaded")
            
        if db_ok:
            st.success("✅ MySQL Connected")
        else:
            st.error("❌ MySQL Offline")

        # Detailed Info in Expander
        with st.expander("🔍 Detailed System Info"):
            st.markdown(f"**Model:** `{os.path.basename(data.get('model_path', 'pipeline.pkl'))}`")
            st.markdown(f"**DB Host:** `{data.get('db_host', 'localhost')}`")
            st.markdown(f"**DB Name:** `{data.get('db_name', 'stock_predictor')}`")
            st.markdown(f"**API URL:** `{FASTAPI_URL}`")
            if st.button("🔄 Force Refresh", use_container_width=True):
                st.rerun()
                
        api_online = True
    except Exception:
        st.error("❌ FastAPI Offline")
        st.info(f"💡 Expected API at: `{FASTAPI_URL}`")
        if st.button("🔄 Retry Connection", use_container_width=True):
            st.rerun()
        api_online = False
        model_ok = db_ok = False

    st.divider()
    st.markdown("**ABOUT**")
    st.markdown("ML model predicts ROCE from 8 financial metrics of Indian listed companies.")
    st.divider()
    st.markdown("**FEATURES**")
    for f in ["Live Tracker Fetch", "Manual Entry", "MySQL Storage", "History Dashboard"]:
        st.markdown(f"• {f}")
    st.divider()
    st.markdown("**RUN**")
    st.code("python run.py", language="bash")

# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-wrap">
    <div class="hero-sub">📊 ML-Powered · FastAPI + Streamlit + MySQL</div>
    <div class="hero-title">Stock <span>ROCE</span> Predictor</div>
    <div class="hero-sub" style="margin-top:0.8rem; color:#2a5a8a;">
        Predict Return on Capital Employed — powered by XGBoost · 5000+ Indian Companies
    </div>
</div>
""", unsafe_allow_html=True)

# ── Live stats from DB ─────────────────────────────────────────────────────────
if api_online and db_ok:
    try:
        stats_r = requests.get(f"{FASTAPI_URL}/stats", timeout=5)
        if stats_r.status_code == 200:
            stats_data = stats_r.json()
            col1, col2, col3, col4, col5 = st.columns(5)

            def mcard(col, label, value, sub=""):
                col.markdown(f"""
                <div class="metric-card">
                    <div class="m-label">{label}</div>
                    <div class="m-value">{value}</div>
                    <div class="m-sub">{sub}</div>
                </div>""", unsafe_allow_html=True)

            mcard(col1, "Total Predictions", stats_data.get("total_predictions", 0), "all time")
            mcard(col2, "Avg ROCE",  f"{stats_data.get('avg_roce', 0):.1f}%", "predicted")
            mcard(col3, "Best ROCE", f"{stats_data.get('max_roce', 0):.1f}%", "maximum")
            mcard(col4, "Excellent", stats_data.get("excellent_count", 0), "> 20% ROCE")
            mcard(col5, "Good",      stats_data.get("excellent_count", 0), "10–20% ROCE")
    except Exception:
        pass

# ── Helper: display result card + gauge ───────────────────────────────────────
def clean_ticker(symbol: str) -> str:
    """Clean and format ticker: remove spaces, add .NS if missing."""
    s = symbol.strip().upper().replace(" ", "")
    if s and "." not in s:
        return f"{s}.NS"
    return s

def display_result(val, interp, color, input_dict, record_id=None):
    themes = {
        "green":  ("#4ade80", "#052012", "#14532d"),
        "blue":   ("#38bdf8", "#031520", "#0c4a6e"),
        "yellow": ("#fbbf24", "#1c1200", "#78350f"),
        "red":    ("#f43f5e", "#1a0008", "#7f1d1d"),
    }
    hex_color, bg, badge_bg = themes.get(color, themes["blue"])

    saved_note = f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.6rem;color:#2a6a4a;margin-top:0.5rem;">✅ Saved to MySQL (ID #{record_id})</div>' if record_id else ""

    st.markdown(f"""
    <div class="result-card"
         style="background:linear-gradient(135deg,{bg},{bg}cc,#080c14);
                border:1px solid {hex_color}40;">
        <div class="result-label">Predicted Return on Capital Employed</div>
        <div class="result-value" style="color:{hex_color};">{val:.2f}%</div>
        <div class="result-badge" style="background:{badge_bg}; color:{hex_color};">{interp}</div>
        {saved_note}
    </div>
    """, unsafe_allow_html=True)

    # Gauge
    fig, ax = plt.subplots(figsize=(8, 1.0))
    fig.patch.set_facecolor("#080c14")
    ax.set_facecolor("#080c14")
    clamped = max(-10, min(val, 50))
    ax.barh(0, 60, left=-10, color="#0d1421", height=0.5)
    ax.barh(0, clamped + 10, left=-10, color=hex_color, height=0.5, alpha=0.85)
    for tick, lbl in [(-10,"-10%"),(0,"0%"),(5,"5%"),(10,"10%"),(20,"20%"),(30,"30%"),(50,"50%")]:
        ax.axvline(tick, color="#1a2535", linewidth=0.8)
        ax.text(tick, 0.32, lbl, ha="center", color="#3a5a7a", fontsize=7, fontfamily="monospace")
    ax.set_xlim(-10, 50); ax.set_yticks([])
    for sp in ax.spines.values(): sp.set_visible(False)
    ax.tick_params(bottom=False, labelbottom=False)
    plt.tight_layout(pad=0.3)
    st.pyplot(fig)

    # Input table
    st.markdown('<div class="sec-label">Input Metrics</div>', unsafe_allow_html=True)
    summary = pd.DataFrame({
        "Metric": ["Market Price (₹)", "P/E Ratio", "Market Cap (₹ Cr)", "Dividend Yield (%)",
                   "Net Profit Q (₹ Cr)", "YOY Profit Growth (%)", "Sales Q (₹ Cr)", "YOY Sales Growth (%)"],
        "Value": [
            input_dict.get("Current Market price(Rs)", ""),
            input_dict.get("Price to Earning", ""),
            input_dict.get("Market Capitilization", ""),
            input_dict.get("Dividend yield", ""),
            input_dict.get("Net Profit latest quarter", ""),
            input_dict.get("YOY Quarterly profit Growth", ""),
            input_dict.get("Sales latest quarter", ""),
            input_dict.get("YOY Quarter sales growth", ""),
        ],
    })
    st.dataframe(summary, use_container_width=True, hide_index=True)

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab_dynamic, tab_manual, tab_history, tab_dashboard = st.tabs([
    "🚀 Live Tracker", "📝 Manual Entry", "🗄️ Prediction History", "📊 Analytics Dashboard"
])

# ════════════════════════════════════════════════════════════════════════════════
# TAB 1: DYNAMIC / LIVE TICKER
# ════════════════════════════════════════════════════════════════════════════════
with tab_dynamic:
    st.markdown('<div class="sec-label">Predict using Live Yahoo Finance Data</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns([3, 1, 1])
    with c1:
        ticker_input = st.text_input("Ticker Symbol", placeholder="RELIANCE.NS   TCS.NS   INFY.NS", label_visibility="collapsed")
    with c2:
        company_name_dyn = st.text_input("Company Name (optional)", value="", label_visibility="visible")
    with c3:
        st.markdown("<br>", unsafe_allow_html=True)
        dyn_btn = st.button("🔮 Predict Live", use_container_width=True, key="dyn_btn")

    if dyn_btn:
        if not ticker_input.strip():
            st.warning("Please enter a ticker symbol.")
        else:
            with st.spinner(f"Fetching live data for **{ticker_input}**..."):
                try:
                    cleaned_ticker = clean_ticker(ticker_input)
                    ticker_obj = yf.Ticker(cleaned_ticker)
                    info = ticker_obj.info
                    
                    if not info or "currentPrice" not in info:
                        st.error(f"❌ Could not fetch data for '{ticker_input}'.")
                        st.info(f"💡 Try using the exact symbol like **M&M.NS** or **RELIANCE.NS**.")
                        st.stop()

                    d_price      = float(info.get("currentPrice", 0.0))
                    d_pe         = float(info.get("trailingPE", 0.0) or 0.0)
                    d_mktcap     = float(info.get("marketCap", 0.0) or 0.0) / 1e7
                    d_dividend   = float(info.get("dividendYield", 0.0) or 0.0) * 100.0
                    d_yoy_sales  = float(info.get("revenueGrowth", 0.0) or 0.0) * 100.0
                    d_yoy_profit = float(info.get("earningsGrowth", 0.0) or 0.0) * 100.0
                    d_sales      = float(info.get("totalRevenue", 0.0) or 0.0) / 4.0 / 1e7
                    d_net_profit = float(info.get("netIncomeToCommon", 0.0) or 0.0) / 4.0 / 1e7

                    cname = company_name_dyn.strip() or info.get("longName", ticker_input)

                    payload = {"inputs": [{
                        "company_name":                cname,
                        "ticker":                      cleaned_ticker,
                        "source":                      "live_ticker",
                        "Current Market price(Rs)":    d_price,
                        "Price to Earning":            d_pe,
                        "Market Capitilization":       d_mktcap,
                        "Dividend yield":              d_dividend,
                        "Net Profit latest quarter":   d_net_profit,
                        "YOY Quarterly profit Growth": d_yoy_profit,
                        "Sales latest quarter":        d_sales,
                        "YOY Quarter sales growth":    d_yoy_sales,
                    }]}

                    resp = requests.post(f"{FASTAPI_URL}/predict", json=payload, timeout=15)
                    if resp.status_code == 200:
                        pred = resp.json()["predictions"][0]
                        st.markdown(f"### 📡 {cname} (`{ticker_input.upper()}`)")
                        display_result(
                            pred["predicted_ROCE"], pred["interpretation"],
                            pred["color"], payload["inputs"][0],
                            record_id=pred.get("record_id"),
                        )
                    elif resp.status_code == 503:
                        st.error("Model not loaded. Ensure pipeline.pkl is present and restart FastAPI.")
                    else:
                        st.error(f"API Error {resp.status_code}: {resp.text}")

                except requests.ConnectionError:
                    st.error("❌ FastAPI is offline. Run: `python run.py`")
                except Exception as e:
                    st.error(f"Error: {e}")

# ════════════════════════════════════════════════════════════════════════════════
# TAB 2: MANUAL ENTRY
# ════════════════════════════════════════════════════════════════════════════════
with tab_manual:
    st.markdown('<div class="sec-label">Enter Financial Metrics Manually</div>', unsafe_allow_html=True)

    with st.form("manual_entry_form", clear_on_submit=False):
        name_col, ticker_col = st.columns([2, 1])
        with name_col:
            m_company = st.text_input("Company Name", value="My Company", key="m_company")
        with ticker_col:
            m_ticker = st.text_input("Ticker (optional)", value="", placeholder="TICKER.NS", key="m_ticker")

        c1, c2 = st.columns(2)
        with c1:
            price      = st.number_input("Current Market Price (₹)",        value=1441.30, min_value=0.0, step=1.0,   format="%.2f", key="m_price")
            pe         = st.number_input("Price to Earning Ratio",           value=25.43,  min_value=0.0, step=0.01,  format="%.2f", key="m_pe")
            mktcap     = st.number_input("Market Capitalization (₹ Cr)",     value=195138.0,min_value=0.0,step=100.0, format="%.2f", key="m_mktcap")
            dividend   = st.number_input("Dividend Yield (%)",               value=0.38,   min_value=0.0, step=0.01,  format="%.4f", key="m_dividend")
        with c2:
            net_profit = st.number_input("Net Profit Latest Quarter (₹ Cr)", value=22290.0,               step=10.0,  format="%.2f", key="m_net_profit")
            yoy_profit = st.number_input("YOY Quarterly Profit Growth (%)",  value=0.57,                  step=0.01,  format="%.2f", key="m_yoy_profit")
            sales      = st.number_input("Sales Latest Quarter (₹ Cr)",      value=264905.0,min_value=0.0,step=100.0, format="%.2f", key="m_sales")
            yoy_sales  = st.number_input("YOY Quarter Sales Growth (%)",     value=10.38,                 step=0.01,  format="%.2f", key="m_yoy_sales")

        st.markdown("<br>", unsafe_allow_html=True)
        man_btn = st.form_submit_button("⚡ Predict ROCE", use_container_width=True)

    if man_btn:
        with st.spinner("Connecting to backend and predicting..."):
            payload = {"inputs": [{
                "company_name":                m_company or "Manual Entry",
                "ticker":                      m_ticker.strip() or None,
                "source":                      "manual",
                "Current Market price(Rs)":    price,
                "Price to Earning":            pe,
                "Market Capitilization":       mktcap,
                "Dividend yield":              dividend,
                "Net Profit latest quarter":   net_profit,
                "YOY Quarterly profit Growth": yoy_profit,
                "Sales latest quarter":        sales,
                "YOY Quarter sales growth":    yoy_sales,
            }]}

            try:
                resp = requests.post(f"{FASTAPI_URL}/predict", json=payload, timeout=15)
                if resp.status_code == 200:
                    pred = resp.json()["predictions"][0]
                    st.markdown(f"### 📋 {m_company}")
                    display_result(
                        pred["predicted_ROCE"], pred["interpretation"],
                        pred["color"], payload["inputs"][0],
                        record_id=pred.get("record_id"),
                    )
                elif resp.status_code == 503:
                    st.error("Model not loaded. Ensure pipeline.pkl is present.")
                else:
                    st.error(f"API Error {resp.status_code}: {resp.text}")
            except requests.ConnectionError:
                st.error(f"❌ FastAPI is offline at {FASTAPI_URL}. Run: `python run.py`")
            except Exception as e:
                st.error(f"System Error: {e}")

# ════════════════════════════════════════════════════════════════════════════════
# TAB 3: HISTORY
# ════════════════════════════════════════════════════════════════════════════════
with tab_history:
    st.markdown('<div class="sec-label">All Predictions — Stored in MySQL</div>', unsafe_allow_html=True)

    col_limit, col_refresh, col_spacer = st.columns([1, 1, 3])
    with col_limit:
        limit = st.selectbox("Show last", [25, 50, 100, 250], index=1, key="hist_limit")
    with col_refresh:
        st.markdown("<br>", unsafe_allow_html=True)
        refresh_btn = st.button("🔄 Refresh", key="hist_refresh")

    if not db_ok:
        st.warning("⚠️ MySQL is not connected. Configure DB_CONFIG in main.py and restart.")
    else:
        try:
            h_resp = requests.get(f"{FASTAPI_URL}/history?limit={limit}", timeout=10)
            if h_resp.status_code == 200:
                history_data = h_resp.json()["history"]
                if not history_data:
                    st.info("No predictions stored yet. Make a prediction to see history here.")
                else:
                    df_hist = pd.DataFrame(history_data)

                    # Color-code the interpretation column
                    def color_interp(val):
                        if "Excellent" in str(val): return "color: #4ade80"
                        elif "Good" in str(val):    return "color: #38bdf8"
                        elif "Average" in str(val): return "color: #fbbf24"
                        else:                        return "color: #f43f5e"

                    display_cols = [
                        "id", "company_name", "ticker", "predicted_roce",
                        "interpretation", "source", "created_at"
                    ]
                    available = [c for c in display_cols if c in df_hist.columns]
                    df_show = df_hist[available].copy()
                    df_show.columns = [c.replace("_", " ").title() for c in df_show.columns]

                    st.dataframe(
                        df_show,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "Predicted Roce": st.column_config.NumberColumn("ROCE (%)", format="%.2f%%"),
                        }
                    )
                    st.markdown(f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.65rem;color:#3b6ea0;margin-top:0.5rem;">{len(history_data)} records loaded</div>', unsafe_allow_html=True)

                    # Delete by ID
                    st.markdown('<div class="sec-label" style="margin-top:2rem;">Delete a Record</div>', unsafe_allow_html=True)
                    del_col1, del_col2 = st.columns([1, 3])
                    with del_col1:
                        del_id = st.number_input("Record ID to delete", min_value=1, step=1, key="del_id")
                    with del_col2:
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button("🗑️ Delete", key="del_btn"):
                            del_r = requests.delete(f"{FASTAPI_URL}/history/{int(del_id)}", timeout=5)
                            if del_r.status_code == 200:
                                st.success(f"Record #{int(del_id)} deleted.")
                                st.rerun()
                            else:
                                st.error(f"Could not delete: {del_r.text}")
            else:
                st.error(f"Could not load history: {h_resp.text}")
        except Exception as e:
            st.error(f"Error loading history: {e}")

# ════════════════════════════════════════════════════════════════════════════════
# TAB 4: ANALYTICS DASHBOARD
# ════════════════════════════════════════════════════════════════════════════════
with tab_dashboard:
    st.markdown('<div class="sec-label">Analytics — Based on Stored Predictions</div>', unsafe_allow_html=True)

    if not db_ok:
        st.warning("⚠️ MySQL is not connected. Dashboard requires a live DB connection.")
    else:
        try:
            h_resp2 = requests.get(f"{FASTAPI_URL}/history?limit=250", timeout=10)
            if h_resp2.status_code != 200:
                st.error("Could not fetch data for dashboard.")
            else:
                hist = h_resp2.json()["history"]
                if len(hist) < 2:
                    st.info("Make at least 2 predictions to see analytics.")
                else:
                    df_d = pd.DataFrame(hist)
                    df_d["predicted_roce"] = pd.to_numeric(df_d["predicted_roce"], errors="coerce")
                    df_d["created_at"] = pd.to_datetime(df_d["created_at"], errors="coerce")

                    # ── Row 1: Distribution + Category breakdown ───────────────
                    ch1, ch2 = st.columns(2)

                    with ch1:
                        st.markdown('<div class="sec-label">ROCE Distribution</div>', unsafe_allow_html=True)
                        fig1, ax1 = plt.subplots(figsize=(6, 3.5))
                        fig1.patch.set_facecolor("#0d1421")
                        ax1.set_facecolor("#0d1421")
                        roce_vals = df_d["predicted_roce"].dropna()
                        ax1.hist(roce_vals, bins=20, color="#2563eb", alpha=0.85, edgecolor="#1a2c42")
                        ax1.axvline(roce_vals.mean(), color="#3b9eff", linewidth=1.5, linestyle="--", label=f"Mean: {roce_vals.mean():.1f}%")
                        ax1.set_xlabel("ROCE (%)", color="#4a6a8a", fontsize=9)
                        ax1.set_ylabel("Count", color="#4a6a8a", fontsize=9)
                        ax1.tick_params(colors="#4a6a8a")
                        ax1.spines["bottom"].set_color("#1a2535")
                        ax1.spines["left"].set_color("#1a2535")
                        ax1.spines["top"].set_visible(False)
                        ax1.spines["right"].set_visible(False)
                        ax1.legend(facecolor="#0d1421", labelcolor="#4a8aba", fontsize=8)
                        plt.tight_layout()
                        st.pyplot(fig1)

                    with ch2:
                        st.markdown('<div class="sec-label">Prediction Category Breakdown</div>', unsafe_allow_html=True)
                        cat_colors = {"green": "#4ade80", "blue": "#38bdf8", "yellow": "#fbbf24", "red": "#f43f5e"}
                        cat_labels = {"green": "Excellent (>20%)", "blue": "Good (10–20%)", "yellow": "Average (5–10%)", "red": "Below Avg (<5%)"}
                        color_counts = df_d["color"].value_counts() if "color" in df_d.columns else pd.Series()
                        cats = [k for k in cat_colors if k in color_counts.index]
                        vals = [color_counts[k] for k in cats]
                        clrs = [cat_colors[k] for k in cats]
                        lbls = [cat_labels[k] for k in cats]

                        fig2, ax2 = plt.subplots(figsize=(6, 3.5))
                        fig2.patch.set_facecolor("#0d1421")
                        ax2.set_facecolor("#0d1421")
                        if vals:
                            wedges, texts, autotexts = ax2.pie(
                                vals, labels=lbls, colors=clrs, autopct="%1.0f%%",
                                startangle=90, pctdistance=0.75,
                                wedgeprops={"edgecolor": "#0d1421", "linewidth": 2}
                            )
                            for t in texts: t.set_color("#4a6a8a"); t.set_fontsize(8)
                            for a in autotexts: a.set_color("#0d1421"); a.set_fontsize(8); a.set_fontweight("bold")
                        plt.tight_layout()
                        st.pyplot(fig2)

                    # ── Row 2: Time series + Top companies ────────────────────
                    ch3, ch4 = st.columns(2)

                    with ch3:
                        st.markdown('<div class="sec-label">ROCE Over Time</div>', unsafe_allow_html=True)
                        ts_df = df_d.dropna(subset=["created_at", "predicted_roce"]).sort_values("created_at")
                        fig3, ax3 = plt.subplots(figsize=(6, 3.5))
                        fig3.patch.set_facecolor("#0d1421")
                        ax3.set_facecolor("#0d1421")
                        ax3.plot(range(len(ts_df)), ts_df["predicted_roce"].values,
                                 color="#3b9eff", linewidth=1.5, marker="o", markersize=4, alpha=0.85)
                        ax3.fill_between(range(len(ts_df)), ts_df["predicted_roce"].values,
                                         alpha=0.15, color="#3b9eff")
                        ax3.set_xlabel("Prediction #", color="#4a6a8a", fontsize=9)
                        ax3.set_ylabel("ROCE (%)", color="#4a6a8a", fontsize=9)
                        ax3.tick_params(colors="#4a6a8a")
                        for sp in ["top","right"]: ax3.spines[sp].set_visible(False)
                        ax3.spines["bottom"].set_color("#1a2535")
                        ax3.spines["left"].set_color("#1a2535")
                        plt.tight_layout()
                        st.pyplot(fig3)

                    with ch4:
                        st.markdown('<div class="sec-label">Top 10 Companies by ROCE</div>', unsafe_allow_html=True)
                        if "company_name" in df_d.columns:
                            top10 = df_d.nlargest(10, "predicted_roce")[["company_name", "predicted_roce"]].copy()
                            top10["company_name"] = top10["company_name"].str[:20]
                            fig4, ax4 = plt.subplots(figsize=(6, 3.5))
                            fig4.patch.set_facecolor("#0d1421")
                            ax4.set_facecolor("#0d1421")
                            bars = ax4.barh(top10["company_name"], top10["predicted_roce"],
                                            color="#2563eb", alpha=0.85)
                            for bar, val in zip(bars, top10["predicted_roce"]):
                                ax4.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
                                         f"{val:.1f}%", va="center", color="#3b9eff", fontsize=8)
                            ax4.set_xlabel("ROCE (%)", color="#4a6a8a", fontsize=9)
                            ax4.tick_params(colors="#4a6a8a")
                            for sp in ["top","right"]: ax4.spines[sp].set_visible(False)
                            ax4.spines["bottom"].set_color("#1a2535")
                            ax4.spines["left"].set_color("#1a2535")
                            plt.tight_layout()
                            st.pyplot(fig4)

                    # ── Source breakdown ───────────────────────────────────────
                    if "source" in df_d.columns:
                        st.markdown('<div class="sec-label">Prediction Source Split</div>', unsafe_allow_html=True)
                        src_counts = df_d["source"].value_counts()
                        num_cols = min(len(src_counts), 3)
                        if num_cols > 0:
                            cols_sc = st.columns(num_cols)
                            for i, (src, cnt) in enumerate(src_counts.items()):
                                if i < num_cols:
                                    cols_sc[i].markdown(f"""
                                    <div class="metric-card">
                                        <div class="m-label">{src.replace("_"," ").title()}</div>
                                        <div class="m-value">{cnt}</div>
                                        <div class="m-sub">predictions</div>
                                    </div>""", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Dashboard error: {e}")
