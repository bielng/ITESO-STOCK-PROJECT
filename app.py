
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

from data_loader import AlpacaAPI
from config import STOCK_DATA, TIMEFRAME_MAP

# ---------- Page ----------
st.set_page_config(page_title="Stock Dashboard", layout="wide")

# ---------- Custom CSS (AdventureWorks Style) ----------
st.markdown(
    """
    <style>
    .reportview-container {background: #0E1117;}
    .sidebar .sidebar-content {background: #161B22;}
    .kpi-card {
        background: #1A1F2E;
        padding: 18px;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,212,170,0.15);
        border: 1px solid #2A2F3E;
    }
    .kpi-value {
        font-size: 36px;
        font-weight: bold;
        color: #00D4AA;
        margin: 0;
    }
    .kpi-label {
        font-size: 14px;
        color: #B0B8C4;
        margin-top: 6px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .big-title {
        font-size: 42px !important;
        font-weight: bold;
        color: #00D4AA;
        text-align: center;
        margin-bottom: 10px;
    }
    .stSelectbox > div > div {background-color: #1A1F2E; color: white;}
    .stTextInput > div > div > input {background-color: #1A1F2E; color: white; border: 1px solid #00D4AA;}
    </style>
    """,
    unsafe_allow_html=True
)

# ---------- Title ----------
st.markdown('<p class="big-title">STOCK DASHBOARD</p>', unsafe_allow_html=True)

# ---------- Hard-coded Keys ----------
API_KEY    = "PKWE76NAVGFRCDGOPHQA2RH33F"
API_SECRET = "FpX7LTMiUtJGCNTrW83cEz4J1PG2XhYA2J1Ls3HfzBwf"

# ---------- Group by Sector ----------
SECTORS = {}
for sym, info in STOCK_DATA.items():
    SECTORS.setdefault(info["sector"], []).append(sym)

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("### Stock Selector")

    # Search
    search = st.text_input("Search company...", "")
    filtered = {
        sym: info for sym, info in STOCK_DATA.items()
        if search.lower() in info["name"].lower() or search.upper() in sym
    }

    # Sector Filter
    sector_filter = st.selectbox("Sector", options=["All"] + list(SECTORS.keys()))
    if sector_filter != "All":
        filtered = {sym: info for sym, info in filtered.items() if info["sector"] == sector_filter}

    # Symbol Select
    symbol = st.selectbox(
        "Select Stock",
        options=list(filtered.keys()),
        format_func=lambda x: f"{x} – {filtered[x]['name']}"
    )
    sector = filtered[symbol]["sector"]

    period = st.selectbox("Period", options=list(TIMEFRAME_MAP.keys()))
    chart_type = st.radio("Chart Type", ["Candlestick", "Line"])

    st.markdown("### Indicators")
    sma = st.checkbox("SMA 20", True)
    ema = st.checkbox("EMA 20", True)
    bb  = st.checkbox("Bollinger Bands", True)

    st.markdown(f"**{symbol}** – {STOCK_DATA[symbol]['name']}\n*Sector: {sector}*")

# ---------- Choose Feed ----------
cfg = TIMEFRAME_MAP[period]
feed = "sip" if cfg["days"] > 35 else "iex"
alpaca = AlpacaAPI(API_KEY, API_SECRET, feed=feed)

# ---------- Fetch ----------
start_iso, end_iso = alpaca.get_market_range(cfg["days"])

with st.spinner(f"Fetching {symbol} {period} ({feed.upper()})…"):
    df = alpaca.get_bars(symbol, cfg["alpaca"], start_iso, end_iso)

if df.empty:
    if feed == "iex":
        st.error("No data – IEX free tier only gives ~30 days. Try 1d/1wk/1mo.")
    else:
        st.error("No data – SIP access required. Upgrade to AlgoTrader Plus.")
    st.stop()

# ---------- KPIs (Top Row) ----------
latest = df.iloc[-1]
prev   = df.iloc[-2] if len(df) > 1 else latest
delta  = latest["Close"] - prev["Close"]
delta_pct = (delta / prev["Close"]) * 100

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-value">${latest['Close']:.2f}</div>
            <div class="kpi-label">Last Close</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-value" style="color: {'#00ff85' if delta >= 0 else '#ff4d4d'}">
                {delta:+.2f}
            </div>
            <div class="kpi-label">Change ($)</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-value" style="color: {'#00ff85' if delta_pct >= 0 else '#ff4d4d'}">
                {delta_pct:+.2f}%
            </div>
            <div class="kpi-label">Change (%)</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col4:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-value">{latest['Volume']:,.0f}</div>
            <div class="kpi-label">Volume</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col5:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-value">${df['High'].max():.2f}</div>
            <div class="kpi-label">Period High</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# ---------- Chart ----------
fig = go.Figure()
if chart_type == "Candlestick":
    fig.add_trace(go.Candlestick(
        x=df.index, open=df["Open"], high=df["High"],
        low=df["Low"], close=df["Close"], name=symbol,
        increasing_line_color='#00D4AA', decreasing_line_color='#ff4d4d'
    ))
else:
    fig.add_trace(go.Scatter(x=df.index, y=df["Close"], mode="lines", line=dict(color="#00D4AA"), name="Close"))

# Indicators
if sma:
    df["SMA20"] = df["Close"].rolling(20).mean()
    fig.add_trace(go.Scatter(x=df.index, y=df["SMA20"], name="SMA 20", line=dict(color="#FFA500", dash="dash")))
if ema:
    df["EMA20"] = df["Close"].ewm(span=20).mean()
    fig.add_trace(go.Scatter(x=df.index, y=df["EMA20"], name="EMA 20", line=dict(color="#00D4AA", dash="dot")))
if bb:
    df["BB_Mid"] = df["Close"].rolling(20).mean()
    df["BB_Std"] = df["Close"].rolling(20).std()
    df["BB_Upper"] = df["BB_Mid"] + 2 * df["BB_Std"]
    df["BB_Lower"] = df["BB_Mid"] - 2 * df["BB_Std"]
    fig.add_trace(go.Scatter(x=df.index, y=df["BB_Upper"], name="BB Upper", line=dict(color="#666", width=1)))
    fig.add_trace(go.Scatter(x=df.index, y=df["BB_Lower"], name="BB Lower", line=dict(color="#666", width=1)))
    fig.add_trace(go.Scatter(x=df.index, y=df["BB_Mid"], fill='tonexty', fillcolor='rgba(0,212,170,0.1)', name="BB Fill"))

fig.update_layout(
    title=f"{symbol} – {period.upper()} ({feed.upper()})",
    xaxis_title="Date", yaxis_title="Price ($)",
    height=600,
    plot_bgcolor='#0E1117',
    paper_bgcolor='#0E1117',
    font=dict(color="#B0B8C4"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, bgcolor="#161B22"),
    xaxis=dict(gridcolor="#2A2F3E"),
    yaxis=dict(gridcolor="#2A2F3E")
)
st.plotly_chart(fig, use_container_width=True)

# ---------- Table ----------
st.subheader("Historical Data")
disp = df.copy()
disp.index = disp.index.strftime("%Y-%m-%d")
disp = disp.round(2)
st.dataframe(disp, use_container_width=True)

# ---------- CSV ----------
csv = df.to_csv().encode()
st.download_button("Download CSV", csv, f"{symbol}_{period}.csv", "text/csv")